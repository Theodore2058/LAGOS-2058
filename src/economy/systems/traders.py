"""
Trader agents — vectorized inter-LGA trade based on price differentials.

Uses the trade graph to move goods from low-price to high-price regions,
with transport costs factored in. Includes speculation/hoarding.
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import EconomicState, SimConfig, TraderAgent
from src.economy.data.commodities import BASE_PRICES
from src.economy.systems.trade import get_recent_prices
from src.economy.systems.trade_graph import TradeGraph, compute_visibility, get_best_visible_prices

logger = logging.getLogger(__name__)


def initialize_traders(
    state: EconomicState, config: SimConfig,
) -> list[TraderAgent]:
    """Create 774 aggregate traders. Mostly for state tracking."""
    N = config.N_LGAS
    traders = []
    for i in range(N):
        inv = np.zeros(config.N_COMMODITIES, dtype=np.float64)
        cash = float(state.population[i] * 100.0)
        aggressiveness = float(state.rng.uniform(0.2, 0.8))
        traders.append(TraderAgent(
            home_lga=i, inventory=inv, cash=cash,
            info_radius=config.TRADER_INFO_RADIUS_HOPS,
            speculation_aggressiveness=aggressiveness,
        ))
    return traders


def tick_traders(
    state: EconomicState,
    config: SimConfig,
    traders: list[TraderAgent],
    graph: TradeGraph,
) -> np.ndarray:
    """
    Vectorized trade tick: for each route, move goods from cheap to expensive end.

    Operates on all routes simultaneously rather than per-trader per-commodity.

    Returns: trader_net_supply (N, C) — net goods moved into each LGA
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES
    net_supply = np.zeros((N, C), dtype=np.float64)

    # Compute BFS visibility (cached on graph)
    visibility = compute_visibility(graph, config.TRADER_INFO_RADIUS_HOPS)

    # Best visible prices: traders respond to the highest price they can see
    best_visible = get_best_visible_prices(graph, state.prices, visibility)

    sources = graph.edges[:, 0]  # (R,)
    dests = graph.edges[:, 1]    # (R,)

    # Transport cost multiplier per route (commodity-independent part)
    base_tcost = graph.distances * config.TRANSPORT_COST_PER_KM
    route_mult = np.where(
        graph.route_types == 0,
        1.0 / np.maximum(graph.qualities, 0.1),
        np.where(
            graph.route_types == 1, config.RAIL_COST_MULTIPLIER,
            np.where(graph.route_types == 2, 0.5, 0.4),
        ),
    )
    route_cost_factor = base_tcost * route_mult * (1.0 + graph.surcharges)  # (R,)

    for c in range(C):
        price_src = state.prices[sources, c]  # (R,)
        price_dst = state.prices[dests, c]    # (R,)

        # Use best visible price as the signal: trade toward destination
        # only if it's in the direction of higher visible prices
        best_src = best_visible[sources, c]
        best_dst = best_visible[dests, c]

        # Forward: source → dest (trade when dest direction has higher visible prices)
        transport_cost = price_src * route_cost_factor
        # Profit uses actual dest price, but urgency is boosted by best visible
        profit_fwd = price_dst - price_src - transport_cost
        # Scale urgency: if best visible price beyond dest is even higher, trade harder
        signal_boost_fwd = np.clip(best_dst / np.maximum(price_dst, 1.0), 1.0, 2.0)

        fwd_mask = profit_fwd > 0
        if fwd_mask.any():
            fwd_sources = sources[fwd_mask]
            fwd_dests = dests[fwd_mask]
            avail = state.inventories[fwd_sources, c]
            margin = np.clip(profit_fwd[fwd_mask] / np.maximum(price_src[fwd_mask], 1.0), 0, 0.5)
            boost = signal_boost_fwd[fwd_mask]
            quantity = avail * 0.03 * margin * boost
            quantity = np.minimum(quantity, avail * 0.10)
            np.add.at(net_supply[:, c], fwd_sources, -quantity)
            np.add.at(net_supply[:, c], fwd_dests, quantity)

        # Reverse: dest → source
        transport_cost_rev = price_dst * route_cost_factor
        profit_rev = price_src - price_dst - transport_cost_rev
        signal_boost_rev = np.clip(best_src / np.maximum(price_src, 1.0), 1.0, 2.0)

        rev_mask = profit_rev > 0
        if rev_mask.any():
            rev_sources = dests[rev_mask]
            rev_dests = sources[rev_mask]
            avail = state.inventories[rev_sources, c]
            margin = np.clip(profit_rev[rev_mask] / np.maximum(price_dst[rev_mask], 1.0), 0, 0.5)
            boost = signal_boost_rev[rev_mask]
            quantity = avail * 0.03 * margin * boost
            quantity = np.minimum(quantity, avail * 0.10)
            np.add.at(net_supply[:, c], rev_sources, -quantity)
            np.add.at(net_supply[:, c], rev_dests, quantity)

    # Speculation/hoarding
    _process_speculation_vec(state, config, traders, net_supply)

    # Clamp: can't remove more than available
    for c in range(C):
        outflow = np.maximum(-net_supply[:, c], 0)
        avail = state.inventories[:, c]
        excess_mask = outflow > avail
        if excess_mask.any():
            scale = np.where(outflow > 0, avail / np.maximum(outflow, 1.0), 1.0)
            net_supply[excess_mask, c] *= scale[excess_mask]

    return net_supply


def _process_speculation_vec(
    state: EconomicState,
    config: SimConfig,
    traders: list[TraderAgent],
    net_supply: np.ndarray,
) -> None:
    """Vectorized speculation: hoard on rising trends, release on price spikes."""
    C = config.N_COMMODITIES
    lookback = min(config.SPECULATION_LOOKBACK_DAYS, state.price_history.shape[2])
    if lookback < 2:
        return

    recent = get_recent_prices(state, lookback)
    safe_start = np.maximum(recent[:, :, 0], 1.0)
    price_trends = (recent[:, :, -1] - recent[:, :, 0]) / safe_start / lookback

    aggressiveness = np.array([t.speculation_aggressiveness for t in traders])

    for c in range(C):
        trend = price_trends[:, c]

        # Hoard where trend > threshold
        hoard_mask = trend > config.SPECULATION_THRESHOLD
        if hoard_mask.any():
            hoard_frac = aggressiveness[hoard_mask] * (
                trend[hoard_mask] / config.SPECULATION_THRESHOLD
            )
            hoard_frac = np.clip(hoard_frac, 0, 0.8)
            hoard_amount = state.inventories[hoard_mask, c] * hoard_frac * 0.01
            state.hoarded[hoard_mask, c] += hoard_amount
            # Cap: hoarded cannot exceed inventory
            np.minimum(
                state.hoarded[hoard_mask, c],
                state.inventories[hoard_mask, c],
                out=state.hoarded[hoard_mask, c],
            )

        # Release where price > threshold * base
        release_mask = state.prices[:, c] > config.HOARD_RELEASE_THRESHOLD * BASE_PRICES[c]
        if release_mask.any():
            release = state.hoarded[release_mask, c]
            state.hoarded[release_mask, c] = 0.0
            net_supply[release_mask, c] += release
