"""
Market clearing and consumer demand.

Handles price adjustment via Walrasian tatonnement, spoilage,
and consumer demand computation. Trade routes and trader agents
will be added in Phase 2.
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import EconomicState, MarketMutations, SimConfig
from src.economy.data.commodities import (
    BASE_PRICES,
    COMMODITIES,
    DEMAND_ELASTICITIES,
    SPOILAGE_RATES,
)
from src.economy.core.types import (
    CONSUMPTION_BASKET_COMMODITY_MAP,
    CONSUMPTION_WEIGHTS_BY_QUINTILE,
)

logger = logging.getLogger(__name__)


def tick_market(
    state: EconomicState,
    config: SimConfig,
    trader_net_supply: np.ndarray | None = None,
) -> MarketMutations:
    """
    Execute one market tick: spoilage, demand computation, price clearing.

    If trader_net_supply is provided (from trader agents), it is included
    in the supply/demand balance.
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES

    # 1. Apply spoilage
    spoilage = state.inventories * SPOILAGE_RATES[np.newaxis, :]
    state.inventories -= spoilage
    state.inventories = np.maximum(state.inventories, 0.0)

    # 2. Compute consumer demand
    consumer_demand = compute_consumer_demand(state, config)

    # 3. Clear markets
    if trader_net_supply is None:
        trader_net_supply = np.zeros((N, C), dtype=np.float64)
    excess_demand = clear_market(
        prices=state.prices,
        inventories=state.inventories,
        hoarded=state.hoarded,
        consumer_demand=consumer_demand,
        trader_net_supply=trader_net_supply,
        price_adjustment_speed=config.PRICE_ADJUSTMENT_SPEED,
    )

    # 4. Update price history ring buffer
    state.price_history = np.roll(state.price_history, -1, axis=2)
    state.price_history[:, :, -1] = state.prices

    # Compute mutations for diagnostics
    price_changes = state.prices - state.price_history[:, :, -2]

    return MarketMutations(
        price_changes=price_changes,
        inventory_changes=-spoilage,  # net change from this tick
        trade_volumes=np.zeros((N, N), dtype=np.float64),
        excess_demand=excess_demand,
        hoarding_changes=np.zeros((N, C), dtype=np.float64),
    )


def compute_consumer_demand(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute consumer demand per LGA per commodity for one market tick.

    For each LGA:
    1. Total household income from wages
    2. Distribute across income quintiles
    3. Apply consumption basket weights
    4. Convert spending to quantity at local prices
    5. Apply price elasticity

    Returns: shape (N, C) units demanded
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES

    # Total household income per LGA = wages * employment + informal income
    formal_income = (state.wages * state.labor_employed).sum(axis=1)
    informal_income = (
        state.wages * config.INFORMAL_WAGE_FRACTION
        * state.labor_informal
    ).sum(axis=1)
    total_income = formal_income + informal_income
    total_income = np.maximum(total_income, 1.0)

    # Per-market-tick income (monthly income / 56 ticks per month)
    tick_income = total_income / config.MARKET_TICKS_PER_MONTH

    # For simplicity, use Q3 (median) consumption weights
    weights = CONSUMPTION_WEIGHTS_BY_QUINTILE[2]  # Q3

    demand = np.zeros((N, C), dtype=np.float64)

    # Map consumption categories to commodities
    categories = list(CONSUMPTION_BASKET_COMMODITY_MAP.keys())
    for cat_idx, cat_name in enumerate(categories):
        commodity_ids = CONSUMPTION_BASKET_COMMODITY_MAP[cat_name]
        if not commodity_ids:
            continue

        # Total spending on this category
        spending = tick_income * weights[cat_idx]

        # Split equally among commodities in category
        per_commodity_spending = spending / len(commodity_ids)

        for c_id in commodity_ids:
            # Convert naira spending to quantity
            local_price = state.prices[:, c_id]
            safe_price = np.maximum(local_price, 1.0)
            base_demand = per_commodity_spending / safe_price

            # Apply price elasticity
            elasticity = DEMAND_ELASTICITIES[c_id]
            price_ratio = local_price / BASE_PRICES[c_id]
            safe_ratio = np.maximum(price_ratio, 0.01)
            elastic_factor = safe_ratio ** elasticity

            demand[:, c_id] += base_demand * elastic_factor

    demand = np.maximum(demand, 0.0)
    return demand


def clear_market(
    prices: np.ndarray,              # (N, C) MUTATED
    inventories: np.ndarray,         # (N, C) MUTATED
    hoarded: np.ndarray,             # (N, C)
    consumer_demand: np.ndarray,     # (N, C)
    trader_net_supply: np.ndarray,   # (N, C)
    price_adjustment_speed: float,
    price_floor: float = 0.01,
) -> np.ndarray:
    """
    Walrasian tatonnement: adjust prices toward clearing levels.

    Prices rise when demand > supply, fall when supply > demand.
    Actual consumption is min(demand, available supply).
    """
    N, C = prices.shape

    # Available supply
    total_supply = inventories - hoarded + trader_net_supply
    total_supply = np.maximum(total_supply, 0.0)

    # Excess demand
    excess_demand = consumer_demand - total_supply

    # Price adjustment
    safe_demand = np.maximum(consumer_demand, 1.0)
    price_change_ratio = price_adjustment_speed * (excess_demand / safe_demand)

    # Clamp price changes to ±10% per tick to prevent instability
    price_change_ratio = np.clip(price_change_ratio, -0.10, 0.10)

    # Sticky downward: negative adjustments halved
    price_change_ratio = np.where(
        price_change_ratio < 0,
        price_change_ratio * 0.5,
        price_change_ratio,
    )

    prices *= (1.0 + price_change_ratio)

    # Mean reversion: gently pull prices toward base prices to prevent drift
    from src.economy.data.commodities import BASE_PRICES as _BP
    log_ratio = np.log(np.maximum(prices, 1.0) / _BP[np.newaxis, :])
    mean_reversion = -0.05 * log_ratio  # 5% pull toward base per tick
    prices *= np.exp(mean_reversion)
    prices[:] = np.maximum(prices, price_floor)

    # Actual consumption
    actual_consumption = np.minimum(consumer_demand, total_supply)
    inventories -= actual_consumption
    inventories[:] = np.maximum(inventories, 0.0)

    return excess_demand


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

def assert_market_valid(
    state: EconomicState, mutations: MarketMutations,
) -> None:
    """Run after every market tick."""
    assert np.all(state.prices > 0), "Zero or negative price detected"
    assert np.all(state.inventories >= -1e-6), "Negative inventory detected"

    # Price changes bounded
    if mutations.price_changes is not None:
        safe_prices = np.maximum(state.prices, 1.0)
        max_change = np.max(np.abs(mutations.price_changes / safe_prices))
        if max_change > 0.50:
            logger.warning("Large price change: %.0f%%", max_change * 100)
