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
    bt_ids = np.clip(state.building_type_ids.astype(np.intp), 0, len(BT_OUTPUT_COMMODITY) - 1)
    lga_ids = np.clip(state.building_lga_ids.astype(np.intp), 0, config.N_LGAS - 1)

    # --- Vectorized operational check ---
    # Start from all-True each tick; previous non-operational status doesn't persist
    operational = np.ones(B, dtype=bool)

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
    rain_mult = np.where(rain_sensitive, np.clip(state.rainfall_modifier, 0.1, 1.5), 1.0)

    # Al-Shahid disruption
    alsahid_mult = np.ones(B, dtype=np.float64)
    if state.alsahid_control is not None:
        alsahid_mult = 1.0 - state.alsahid_control[lga_ids] * 0.4

    # Enhancement
    enh_mult = np.ones(B, dtype=np.float64)
    if state.enhancement_adoption is not None:
        enh_mult = 1.0 + state.enhancement_adoption[lga_ids] * config.ENHANCEMENT_PRODUCTIVITY_BONUS

    # Import fulfillment constraint
    import_mult = np.ones(B, dtype=np.float64)
    if state.import_fulfillment:
        from src.economy.core.types import IMPORT_DEPENDENCIES
        out_commodities = BT_OUTPUT_COMMODITY[bt_ids]
        for dep_name, dep in IMPORT_DEPENDENCIES.items():
            fulfillment = state.import_fulfillment.get(dep_name, 1.0)
            if fulfillment < 1.0:
                required_by = dep.get("required_by", [])
                for c_id in required_by:
                    affected = out_commodities == c_id
                    import_mult[affected] = np.minimum(import_mult[affected], fulfillment)

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
        * import_mult
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

    # --- Update building employees based on utilization ---
    # Cap ratio = min(input bottleneck, labor bottleneck)
    cap_ratio = np.minimum(bottleneck, labor_bottleneck)
    cap_ratio *= op_mask  # zero for non-operational
    # Employees = labor_needed * cap_ratio, capped at available labor
    new_employees = labor_needed * cap_ratio[:, np.newaxis]
    state.building_employees[:] = new_employees

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

    # --- Inter-LGA trade equalization ---
    # Pool a fraction of supply nationally and redistribute to deficit LGAs.
    # This represents Nigeria's internal trade network (roads, markets).
    # Trade fraction scales with road quality: better roads → more trade
    base_trade_fraction = 0.25
    if state.infra_road_quality is not None:
        road_q = np.clip(state.infra_road_quality, 0.1, 1.0)
        # Roads range 0.1-1.0 → trade fraction 0.10-0.30
        trade_fraction = (base_trade_fraction * road_q)[:, np.newaxis]  # (N, 1)
    else:
        trade_fraction = base_trade_fraction
    trade_pool = total_supply * trade_fraction  # (N, C) contributed to pool
    local_supply = total_supply - trade_pool     # (N, C) kept locally

    # National pool per commodity
    national_pool = trade_pool.sum(axis=0)  # (C,) total available for trade

    # Distribute pool proportional to unmet demand after local clearing
    local_matched = np.minimum(buy_orders, local_supply)
    local_unmet = np.maximum(buy_orders - local_matched, 0.0)  # (N, C)
    unmet_total = local_unmet.sum(axis=0)  # (C,)
    safe_unmet = np.maximum(unmet_total, 1.0)

    # Each LGA gets pool share proportional to its unmet demand
    trade_received = local_unmet * (national_pool / safe_unmet)[np.newaxis, :]
    # Can't receive more than what's in the pool
    trade_received = np.minimum(trade_received, local_unmet)

    # Reconstructed supply: local + trade received
    total_supply = local_supply + trade_received
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
# Background economy production
# ---------------------------------------------------------------------------

def compute_background_supply(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute background economy supply — the vast majority of production that
    isn't modeled as explicit buildings.

    This represents smallholder farming, informal manufacturing, services,
    and other economic activity by the ~225M population. Buildings only model
    ~2K tracked enterprises; background supply fills the gap.

    Scale: population-based (per-capita production), stable over time.
    Distribution: blend of capacity structure + demand-weighted allocation.
    Zero-capacity constraint: LGAs can't produce what they lack capacity for.

    Returns: (N, C) units produced per tick.
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES

    cap = state.production_capacity  # (N, C)

    # --- Scale: population-based, calibrated to ~85% of demand ---
    # Per-capita monthly production factor (units per person per month)
    # Calibrated: 295M people × 1.2 / 56 ticks × modifiers ≈ 85% of demand
    # Demand ≈ 5.8M units/tick, need ~5M supply/tick → ~280M/month
    # 295M × 1.2 = 354M × modifiers(~0.76) = ~269M → 269M/56 = ~4.8M/tick
    PER_CAPITA_PROD = 1.2

    if state.population is not None:
        pop = state.population  # (N,)
    else:
        pop = np.full(N, 300000.0, dtype=np.float64)  # fallback ~300K per LGA

    # Total production budget per LGA per tick
    lga_budget = pop * PER_CAPITA_PROD / config.MARKET_TICKS_PER_MONTH  # (N,)

    # --- Distribution: blend capacity structure + demand weights ---
    # Capacity share: production_capacity normalized per LGA
    cap_total = np.maximum(cap.sum(axis=1, keepdims=True), 1.0)
    cap_share = cap / cap_total  # (N, C) — how LGA's economy is structured

    # Demand share: from previous tick's buy orders
    if state.buy_orders is not None and state.buy_orders.sum() > 0:
        lga_demand_total = np.maximum(state.buy_orders.sum(axis=1, keepdims=True), 1.0)
        demand_share = state.buy_orders / lga_demand_total  # (N, C)
    else:
        demand_share = np.ones((N, C), dtype=np.float64) / C

    # Constrain demand path: LGAs can only produce where they have capacity.
    # Exception: for widely-demanded consumer goods (food, clothing, housing),
    # allow partial production even without local capacity — this represents
    # implicit inter-LGA trade (coastal LGAs ship fish inland, etc.)
    has_capacity = (cap > 0).astype(np.float64)
    # Allow 30% production of demanded goods even without local capacity
    # (representing trade flows from producing regions)
    if state.buy_orders is not None:
        global_demand = state.buy_orders.sum(axis=0)
        demand_frac = global_demand / max(global_demand.sum(), 1.0)
        # High-demand commodities get trade allowance proportional to demand share
        trade_allowance = np.clip(demand_frac * 5.0, 0.0, 0.3)  # up to 30%
        effective_capacity = np.maximum(has_capacity, trade_allowance[np.newaxis, :])
    else:
        effective_capacity = has_capacity
    constrained_demand = demand_share * effective_capacity
    row_sum = np.maximum(constrained_demand.sum(axis=1, keepdims=True), 1.0)
    constrained_demand /= row_sum

    # Suppress capacity path for zero-demand commodities
    has_demand = np.ones(C, dtype=np.float64)
    if state.buy_orders is not None:
        global_demand = state.buy_orders.sum(axis=0)
        has_demand = np.where(global_demand > 0, 1.0, 0.01)
    cap_share_adj = cap_share * has_demand[np.newaxis, :]
    adj_sum = np.maximum(cap_share_adj.sum(axis=1, keepdims=True), 1.0)
    cap_share_adj /= adj_sum

    # Blend: 30% capacity-based + 70% demand-weighted
    commodity_share = 0.30 * cap_share_adj + 0.70 * constrained_demand

    bg_output = lga_budget[:, np.newaxis] * commodity_share  # (N, C)

    # --- Modifiers ---
    # Inventory-to-demand ratio: cut production when warehouses are full.
    # If inventory >> demand, firms scale back (realistic supply response).
    # Only dampen commodities with no unfilled demand — commodities with
    # shortfalls should maintain full production.
    if state.buy_orders is not None:
        global_buy = state.buy_orders.sum(axis=0)  # (C,)
        safe_demand = np.maximum(state.buy_orders, 1.0)
        inv_ratio = state.inventories / safe_demand  # ticks of stock (N, C)
        # Scale: 1.0 when ratio<=4, tapering to 0.3 when ratio>=24
        inv_damper = np.clip(1.0 - (inv_ratio - 4.0) / 28.0, 0.3, 1.0)
        # Zero-demand goods: fully suppress (nobody buys them)
        no_demand = global_buy <= 0
        inv_damper[:, no_demand] = 0.0
        # Don't dampen commodities that have unfilled demand anywhere
        if state.unfilled_buy is not None:
            has_shortage = state.unfilled_buy.sum(axis=0) > 0  # (C,)
            inv_damper[:, has_shortage] = 1.0
        bg_output *= inv_damper

    # Employment (gentle — informal economy resilient)
    if state.labor_employed is not None and state.labor_pool is not None:
        safe_pool = np.maximum(state.labor_pool.sum(axis=1), 1.0)
        emp_rate = np.clip(state.labor_employed.sum(axis=1) / safe_pool, 0.2, 1.0)
        bg_output *= np.sqrt(emp_rate[:, np.newaxis])

    # Infrastructure (gentle — most background production is low-tech)
    if state.infra_power_reliability is not None:
        power = np.clip(state.infra_power_reliability, 0.5, 1.0)
        power_factor = 0.7 + 0.3 * power
        bg_output *= power_factor[:, np.newaxis]

    # Rainfall: agricultural commodities scale with rainfall
    # IDs: 5=timber, 6=grains, 7=rice, 8=cassava, 9=cocoa, 10=palm,
    #       11=cotton, 12=livestock, 13=fish
    _AGRI_IDS = [5, 6, 7, 8, 9, 10, 11, 12, 13]
    rain = np.clip(state.rainfall_modifier, 0.1, 1.5)  # floor 10%, cap 150%
    bg_output[:, _AGRI_IDS] *= rain

    # Al-Shahid disruption
    if state.alsahid_control is not None:
        disruption = 1.0 - state.alsahid_control * 0.3
        bg_output *= disruption[:, np.newaxis]

    # Import fulfillment: reduce background supply for import-dependent goods
    # when forex reserves are low or WAFTA is cancelled
    if state.import_fulfillment:
        from src.economy.core.types import IMPORT_DEPENDENCIES
        for dep_name, dep in IMPORT_DEPENDENCIES.items():
            fulfillment = state.import_fulfillment.get(dep_name, 1.0)
            if fulfillment < 1.0:
                for c_id in dep.get("required_by", []):
                    bg_output[:, c_id] *= fulfillment

    return np.maximum(bg_output, 0.0)


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

    # 1. Spoilage — commodity-specific rates + universal storage depreciation
    # The universal rate (0.1%/tick ≈ 5.5%/month) prevents unbounded inventory
    # accumulation for zero-spoilage goods (steel, cement, ore, etc.)
    effective_spoilage = np.maximum(SPOILAGE_RATES, 0.002)  # min 0.2% per tick
    spoilage = state.inventories * effective_spoilage[np.newaxis, :]
    state.inventories -= spoilage
    state.inventories = np.maximum(state.inventories, 0.0)

    # 2. Building sell orders
    sell_orders = compute_building_sell_orders(state, config)

    # 2b. Background economy supply (non-building production)
    bg_supply = compute_background_supply(state, config)
    sell_orders += bg_supply

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
