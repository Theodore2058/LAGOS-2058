"""
Order-book market clearing system.

Replaces simple Walrasian tatonnement with an iterative order-matching system
where pops post buy orders and buildings post sell orders. Prices adjust based
on unfilled orders rather than aggregate excess demand.

Market clearing flow per tick:
  1. Buildings post sell orders (output available at their LGA)
  2. Pops post buy orders (consumption demand at their LGA)
  3. Traders post arbitrage orders (buy cheap, sell dear across LGAs)
  4. Orders are matched iteratively with price adjustment
  5. Actual consumption and inventory changes applied
  6. Unfilled orders tracked for next tick's price signal
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import EconomicState, MarketMutations, SimConfig
from src.economy.data.commodities import BASE_PRICES, SPOILAGE_RATES, DEMAND_ELASTICITIES
from src.economy.data.buildings import BUILDING_TYPE_BY_ID

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sell orders from buildings
# ---------------------------------------------------------------------------

def compute_building_sell_orders(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute aggregate sell orders per LGA per commodity from all buildings.

    Each operational building offers its output at the local market.
    Output depends on throughput, technology level, input availability,
    labor, and infrastructure.

    Returns: (N, C) array of units offered for sale.
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES
    sell = np.zeros((N, C), dtype=np.float64)

    if state.building_type_ids is None or state.n_buildings == 0:
        return sell

    B = state.n_buildings

    for i in range(B):
        if not state.building_operational[i]:
            continue

        bt = BUILDING_TYPE_BY_ID.get(int(state.building_type_ids[i]))
        if bt is None:
            continue

        lga = int(state.building_lga_ids[i])
        throughput = state.building_throughput[i]
        tech = state.building_tech_level[i]

        # Technology bonus: 0.3 tech -> 0.85x, 1.0 tech -> 1.15x
        tech_mult = 0.7 + 0.45 * tech

        # Infrastructure check
        if bt.requires_power and state.infra_power_reliability is not None:
            power = state.infra_power_reliability[lga]
            if power < bt.min_power_reliability:
                state.building_operational[i] = False
                continue
            # Power reliability scales output
            tech_mult *= max(power, 0.3)

        # Input bottleneck: check if inputs are available in LGA inventory
        bottleneck = 1.0
        if bt.inputs and state.inventories is not None:
            for inp_id, inp_per_unit in bt.inputs.items():
                if 0 <= inp_id < C:
                    available = state.inventories[lga, inp_id]
                    needed = throughput * inp_per_unit
                    if needed > 0:
                        ratio = available / needed
                        bottleneck = min(bottleneck, max(ratio, 0.0))

        # Labor bottleneck: check employee availability
        labor_bottleneck = 1.0
        if bt.labor:
            total_needed = sum(bt.labor.values())
            total_employed = state.building_employees[i].sum()
            if total_needed > 0:
                labor_bottleneck = min(total_employed / total_needed, 1.0)

        # Zaibatsu efficiency bonus
        zaibatsu_mult = 1.0
        if state.building_owners[i] >= 0:
            from src.economy.data.zaibatsu import ZAIBATSU_BY_ID
            z = ZAIBATSU_BY_ID.get(int(state.building_owners[i]))
            if z:
                zaibatsu_mult = 1.0 + z.efficiency_bonus

        # Rainfall for agricultural buildings
        rain_mult = 1.0
        if bt.rainfall_sensitive:
            rain_mult = max(state.rainfall_modifier, 0.1)

        # Al-Shahid disruption
        alsahid_mult = 1.0
        if state.alsahid_control is not None:
            control = state.alsahid_control[lga]
            # High control disrupts production (10-40% penalty)
            alsahid_mult = 1.0 - control * 0.4

        # Enhancement bonus
        enh_mult = 1.0
        if state.enhancement_adoption is not None:
            enh_mult = 1.0 + state.enhancement_adoption[lga] * config.ENHANCEMENT_PRODUCTIVITY_BONUS

        # Strikes check
        if state.strikes_active is not None and state.strikes_active[lga] > 0:
            bottleneck = 0.0  # no production during strikes

        # Final output
        output = (
            throughput
            * tech_mult
            * bottleneck
            * labor_bottleneck
            * zaibatsu_mult
            * rain_mult
            * alsahid_mult
            * enh_mult
        )
        output = max(output, 0.0)

        # Consume inputs from inventory
        if bt.inputs and state.inventories is not None and output > 0:
            for inp_id, inp_per_unit in bt.inputs.items():
                if 0 <= inp_id < C:
                    consumed = output * inp_per_unit * bottleneck
                    consumed = min(consumed, state.inventories[lga, inp_id])
                    state.inventories[lga, inp_id] -= consumed

        # Add output to LGA sell orders
        sell[lga, bt.output_commodity] += output

    return sell


# ---------------------------------------------------------------------------
# Order matching and price clearing
# ---------------------------------------------------------------------------

def clear_order_book(
    state: EconomicState,
    config: SimConfig,
    buy_orders: np.ndarray,      # (N, C) from pops
    sell_orders: np.ndarray,     # (N, C) from buildings
    trader_supply: np.ndarray | None = None,  # (N, C) from traders
    n_rounds: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Iterative order-book clearing with price adjustment.

    For each commodity in each LGA:
      1. Match buy and sell orders
      2. Record unfilled orders
      3. Adjust prices based on order imbalance
      4. Apply mean reversion

    Parameters
    ----------
    buy_orders : (N, C) total buy orders
    sell_orders : (N, C) total sell orders (from buildings + inventory)
    trader_supply : (N, C) net trader supply/demand
    n_rounds : number of clearing iterations

    Returns
    -------
    demand : (N, C) original demand
    fulfilled : (N, C) actual consumption
    """
    N, C = config.N_LGAS, config.N_COMMODITIES

    if trader_supply is None:
        trader_supply = np.zeros((N, C), dtype=np.float64)

    # Total available supply = building output + existing inventory + trader supply - hoarded
    total_supply = (
        sell_orders
        + np.maximum(state.inventories - state.hoarded, 0.0)
        + trader_supply
    )
    total_supply = np.maximum(total_supply, 0.0)

    # Iterative clearing
    remaining_demand = buy_orders.copy()
    remaining_supply = total_supply.copy()
    fulfilled = np.zeros((N, C), dtype=np.float64)

    for round_idx in range(n_rounds):
        # Match: consume min(demand, supply)
        matched = np.minimum(remaining_demand, remaining_supply)
        fulfilled += matched
        remaining_demand -= matched
        remaining_supply -= matched

        if round_idx < n_rounds - 1:
            # Price adjustment between rounds
            # Unfilled buy orders push prices up
            # Unfilled sell orders push prices down
            safe_total = np.maximum(buy_orders + sell_orders, 1.0)
            imbalance = (remaining_demand - remaining_supply) / safe_total

            # Small intra-round adjustment
            adj_speed = config.PRICE_ADJUSTMENT_SPEED * 0.15
            price_adj = adj_speed * imbalance
            price_adj = np.clip(price_adj, -0.015, 0.015)

            state.prices *= (1.0 + price_adj)
            state.prices[:] = np.maximum(state.prices, 0.01)

    # Final price adjustment based on unfilled orders
    unfilled_buy = remaining_demand
    unfilled_sell = remaining_supply

    safe_demand = np.maximum(buy_orders + sell_orders, 1.0)
    excess_demand_ratio = (unfilled_buy - unfilled_sell) / safe_demand

    # Price movement — damped to prevent runaway inflation
    price_change_ratio = config.PRICE_ADJUSTMENT_SPEED * 0.5 * excess_demand_ratio
    price_change_ratio = np.clip(price_change_ratio, -0.05, 0.05)

    # Sticky downward
    price_change_ratio = np.where(
        price_change_ratio < 0,
        price_change_ratio * 0.5,
        price_change_ratio,
    )

    state.prices *= (1.0 + price_change_ratio)

    # Mean reversion toward base prices (5% per tick — stronger anchor)
    log_ratio = np.log(np.maximum(state.prices, 1.0) / BASE_PRICES[np.newaxis, :])
    mean_reversion = -0.05 * log_ratio
    state.prices *= np.exp(mean_reversion)
    state.prices[:] = np.maximum(state.prices, 0.01)

    # Update inventory: add building output, subtract consumption
    state.inventories += sell_orders
    state.inventories -= fulfilled
    state.inventories[:] = np.maximum(state.inventories, 0.0)

    # Store order book state
    state.buy_orders = buy_orders
    state.sell_orders = sell_orders
    state.unfilled_buy = unfilled_buy
    state.unfilled_sell = unfilled_sell

    return buy_orders, fulfilled


# ---------------------------------------------------------------------------
# Full market tick using order book
# ---------------------------------------------------------------------------

def tick_market_orderbook(
    state: EconomicState,
    config: SimConfig,
    trader_net_supply: np.ndarray | None = None,
) -> MarketMutations:
    """
    Execute one market tick using the order-book system.

    Replaces the old Walrasian tatonnement when buildings and pops are
    initialized. Falls back to legacy if they're not.
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES

    # 1. Spoilage
    spoilage = state.inventories * SPOILAGE_RATES[np.newaxis, :]
    state.inventories -= spoilage
    state.inventories = np.maximum(state.inventories, 0.0)

    # 2. Building sell orders
    sell_orders = compute_building_sell_orders(state, config)

    # 3. Pop buy orders
    from src.economy.systems.pops import compute_pop_buy_orders
    buy_orders = compute_pop_buy_orders(state, config)

    # 4. Clear order book
    demand, fulfilled = clear_order_book(
        state, config, buy_orders, sell_orders,
        trader_supply=trader_net_supply,
        n_rounds=3,
    )

    # 5. Update pop consumption fulfillment
    from src.economy.systems.pops import update_consumption_fulfillment
    update_consumption_fulfillment(state, config, demand, fulfilled)

    # 6. Update price history ring buffer
    H = state.price_history.shape[2]
    cursor = state.price_history_cursor
    prev_idx = (cursor - 1) % H
    price_changes = state.prices - state.price_history[:, :, prev_idx]
    state.price_history[:, :, cursor] = state.prices
    state.price_history_cursor = (cursor + 1) % H

    return MarketMutations(
        price_changes=price_changes,
        inventory_changes=sell_orders - fulfilled - spoilage,
        trade_volumes=np.zeros((N, N), dtype=np.float64),
        excess_demand=state.unfilled_buy if state.unfilled_buy is not None else np.zeros((N, C)),
        hoarding_changes=np.zeros((N, C), dtype=np.float64),
    )
