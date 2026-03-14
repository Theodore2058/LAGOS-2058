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
from src.economy.data.buildings import (
    BUILDING_TYPE_BY_ID,
    BT_OUTPUT_COMMODITY,
    BT_REQUIRES_POWER,
    BT_MIN_POWER,
    BT_RAINFALL_SENSITIVE,
    BT_INPUT_MATRIX,
    BT_LABOR_MATRIX,
    BT_ZAIBATSU_BONUS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sell orders from buildings
# ---------------------------------------------------------------------------

def compute_building_sell_orders(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute aggregate sell orders per LGA per commodity from all buildings.

    Vectorized: computes all building outputs simultaneously using precomputed
    building-type arrays, then aggregates to LGA level.

    Returns: (N, C) array of units offered for sale.
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES
    sell = np.zeros((N, C), dtype=np.float64)

    if state.building_type_ids is None or state.n_buildings == 0:
        return sell

    B = state.n_buildings
    bt_ids = state.building_type_ids.astype(np.intp)
    lga_ids = state.building_lga_ids.astype(np.intp)

    # --- Vectorized operational check ---
    operational = state.building_operational.copy()

    # Power check: buildings requiring power in LGAs with low reliability
    if state.infra_power_reliability is not None:
        needs_power = BT_REQUIRES_POWER[bt_ids]  # (B,)
        min_power = BT_MIN_POWER[bt_ids]  # (B,)
        lga_power = state.infra_power_reliability[lga_ids]  # (B,)
        power_fail = needs_power & (lga_power < min_power)
        operational[power_fail] = False

    # Strike check
    if state.strikes_active is not None:
        on_strike = state.strikes_active[lga_ids] > 0
        operational[on_strike] = False

    state.building_operational[:] = operational

    # Only process operational buildings
    op_mask = operational
    if not op_mask.any():
        return sell

    # --- Vectorized modifier computation for all operational buildings ---
    throughput = state.building_throughput  # (B,)
    tech = state.building_tech_level  # (B,)

    # Tech multiplier
    tech_mult = 0.7 + 0.45 * tech  # (B,)

    # Power reliability factor (for powered buildings)
    if state.infra_power_reliability is not None:
        needs_power = BT_REQUIRES_POWER[bt_ids]
        lga_power = state.infra_power_reliability[lga_ids]
        power_factor = np.where(needs_power, np.maximum(lga_power, 0.3), 1.0)
        tech_mult *= power_factor

    # Zaibatsu bonus (from precomputed per-type array)
    zaibatsu_mult = BT_ZAIBATSU_BONUS[bt_ids]  # (B,)
    # Only apply if building has an owner
    no_owner = state.building_owners < 0
    zaibatsu_mult = np.where(no_owner, 1.0, zaibatsu_mult)

    # Rainfall
    rain_sensitive = BT_RAINFALL_SENSITIVE[bt_ids]
    rain_mult = np.where(rain_sensitive, max(state.rainfall_modifier, 0.1), 1.0)

    # Al-Shahid disruption
    alsahid_mult = np.ones(B, dtype=np.float64)
    if state.alsahid_control is not None:
        alsahid_mult = 1.0 - state.alsahid_control[lga_ids] * 0.4

    # Enhancement
    enh_mult = np.ones(B, dtype=np.float64)
    if state.enhancement_adoption is not None:
        enh_mult = 1.0 + state.enhancement_adoption[lga_ids] * config.ENHANCEMENT_PRODUCTIVITY_BONUS

    # --- Input bottleneck (vectorized per building) ---
    # For each building, compute min(available / needed) across its inputs
    # Using the precomputed input matrix: BT_INPUT_MATRIX[bt_id, commodity] = per_unit
    input_recipes = BT_INPUT_MATRIX[bt_ids]  # (B, C) input requirements per unit
    needed = throughput[:, np.newaxis] * input_recipes  # (B, C) total needed
    has_inputs = needed > 0  # (B, C)

    if state.inventories is not None and has_inputs.any():
        available = state.inventories[lga_ids]  # (B, C) available in each building's LGA
        safe_needed = np.where(has_inputs, needed, 1.0)
        ratios = np.where(has_inputs, available / safe_needed, 999.0)  # (B, C)
        bottleneck = np.minimum(ratios.min(axis=1), 1.0)  # (B,)
        bottleneck = np.maximum(bottleneck, 0.0)
    else:
        bottleneck = np.ones(B, dtype=np.float64)

    # --- Labor bottleneck (vectorized) ---
    labor_needed = BT_LABOR_MATRIX[bt_ids]  # (B, 4)
    total_labor_needed = labor_needed.sum(axis=1)  # (B,)
    total_employed = state.building_employees.sum(axis=1)  # (B,)
    safe_labor = np.maximum(total_labor_needed, 1.0)
    labor_bottleneck = np.minimum(total_employed / safe_labor, 1.0)
    labor_bottleneck = np.where(total_labor_needed > 0, labor_bottleneck, 1.0)

    # --- Final output per building ---
    output = (
        throughput * tech_mult * bottleneck * labor_bottleneck
        * zaibatsu_mult * rain_mult * alsahid_mult * enh_mult
    )
    output = np.maximum(output, 0.0)
    output *= op_mask  # zero out non-operational

    # --- Consume inputs from inventory ---
    if state.inventories is not None:
        consumed = output[:, np.newaxis] * input_recipes * bottleneck[:, np.newaxis]  # (B, C)
        consumed = np.minimum(consumed, state.inventories[lga_ids])
        consumed *= op_mask[:, np.newaxis]
        # Aggregate consumption per LGA and subtract
        for c in range(C):
            col = consumed[:, c]
            if col.any():
                np.add.at(state.inventories[:, c], lga_ids, -col)
        state.inventories[:] = np.maximum(state.inventories, 0.0)

    # --- Aggregate output to LGA sell orders ---
    out_commodities = BT_OUTPUT_COMMODITY[bt_ids]  # (B,)
    np.add.at(sell, (lga_ids, out_commodities), output)

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
