"""
Labor market system — wages, employment, strikes, automation, informal sector.

Called once per production tick (every game-week).
"""

from __future__ import annotations

import logging
from typing import List, Tuple

import numpy as np

from src.economy.core.types import EconomicState, LaborMutations, SimConfig, SkillTier
from src.economy.data.commodities import BASE_PRICES, COMMODITIES
from src.economy.core.types import CONSUMPTION_BASKET_COMMODITY_MAP, CONSUMPTION_WEIGHTS_BY_QUINTILE

logger = logging.getLogger(__name__)


def tick_labor(state: EconomicState, config: SimConfig) -> LaborMutations:
    """
    Full labor market tick.

    1. Compute labor demand from production capacity (or macro conditions in V3)
    2. Match workers to jobs
    3. Adjust wages based on supply/demand
    4. Check strike conditions
    5. Process automation
    6. Compute informal sector
    """
    N = config.N_LGAS
    S = config.N_SKILL_TIERS

    # Detect V3 (order-book) mode
    use_v3 = (
        state.n_buildings > 0
        and state.building_type_ids is not None
        and state.pop_income is not None
    )

    if use_v3:
        labor_demand, employment = _compute_v3_employment(state, config)
    else:
        # 1. Compute labor demand from legacy production capacity
        labor_demand = _compute_labor_demand(state, config)
        # 2. Match workers
        employment = np.minimum(labor_demand, state.labor_pool)

    # 3. Adjust wages
    wages_new = adjust_wages(
        state.wages, labor_demand, state.labor_pool,
        config.BASE_WAGES[0], config.WAGE_ADJUSTMENT_SPEED,
    )

    # 4. Check strikes
    strikes_active, strikes_triggered = evaluate_strikes(state, config)

    # 5. Automation
    automation_new = process_automation(state, config)

    # 6. Informal sector
    unemployment = np.maximum(state.labor_pool - employment, 0.0)
    informal, informal_income = compute_informal_sector(unemployment, config)

    return LaborMutations(
        wages_new=wages_new,
        employment_new=employment,
        informal_new=informal,
        unemployment=unemployment,
        strikes_triggered=strikes_triggered,
        automation_changes=automation_new,
    )


def _compute_v3_employment(
    state: EconomicState, config: SimConfig,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute labor demand and employment for V3 (order-book) mode.

    In V3, buildings represent specific enterprises (~2K) employing ~70K workers,
    but the macro economy has 84M+ workers. Employment adjusts gradually based
    on economic conditions rather than snapping to building-level demand.

    Returns: (labor_demand, employment) both (N, S).
    """
    N = config.N_LGAS
    S = config.N_SKILL_TIERS

    # --- Aggregate building labor demand to LGA level ---
    building_demand = np.zeros((N, S), dtype=np.float64)
    if state.building_employees is not None and state.n_buildings > 0:
        from src.economy.data.buildings import BT_LABOR_MATRIX
        bt_ids = state.building_type_ids.astype(np.intp)
        lga_ids = state.building_lga_ids.astype(np.intp)
        labor_needed = BT_LABOR_MATRIX[bt_ids]  # (B, 4)
        for s in range(min(S, labor_needed.shape[1])):
            np.add.at(building_demand[:, s], lga_ids, labor_needed[:, s])

    # --- Macro labor demand based on economic conditions ---
    # Target employment rate adjusts based on:
    # 1. Consumption fulfillment (proxy for economic activity)
    # 2. Building operational rate (proxy for industrial health)
    # 3. Al-Shahid control (security disruption)

    # Base target: current employment rate (maintains continuity)
    safe_pool = np.maximum(state.labor_pool, 1.0)
    current_emp_rate = np.clip(state.labor_employed / safe_pool, 0.0, 1.0)  # (N, S)

    # Economic signal: average consumption fulfillment in each LGA
    econ_signal = np.zeros(N, dtype=np.float64)
    if state.pop_consumption_fulfilled is not None:
        pop_lga = getattr(state, "_pop_lga_ids", None)
        if pop_lga is not None:
            # Mean fulfillment per LGA
            fulfill_sum = np.bincount(pop_lga, weights=state.pop_consumption_fulfilled,
                                       minlength=N)
            pop_count = np.bincount(pop_lga, minlength=N).astype(np.float64)
            safe_count = np.maximum(pop_count, 1.0)
            econ_signal = np.clip(fulfill_sum / safe_count, 0.0, 1.0)
        else:
            econ_signal[:] = 0.7
    else:
        econ_signal[:] = 0.7  # default

    # Building health signal
    bldg_signal = np.ones(N, dtype=np.float64)
    if state.building_operational is not None and state.n_buildings > 0:
        lga_ids = state.building_lga_ids.astype(np.intp)
        op_count = np.bincount(lga_ids, weights=state.building_operational.astype(float),
                                minlength=N)
        total_count = np.bincount(lga_ids, minlength=N).astype(np.float64)
        safe_total = np.maximum(total_count, 1.0)
        bldg_signal = np.where(total_count > 0, op_count / safe_total, 1.0)

    # Security signal
    security_signal = np.ones(N, dtype=np.float64)
    if state.alsahid_control is not None:
        security_signal = 1.0 - state.alsahid_control * 0.3

    # Target employment rate: gradual adjustment
    # econ_signal (0-1) maps to employment target (0.3-0.85)
    target_emp_rate = (0.3 + 0.55 * econ_signal) * bldg_signal * security_signal
    target_emp_rate = np.clip(target_emp_rate, 0.15, 0.90)

    # Gradual convergence toward target (10% per production tick)
    adjustment_speed = 0.10
    new_emp_rate = current_emp_rate + adjustment_speed * (
        target_emp_rate[:, np.newaxis] - current_emp_rate
    )
    new_emp_rate = np.clip(new_emp_rate, 0.0, 1.0)

    # Macro demand and employment
    macro_demand = state.labor_pool * target_emp_rate[:, np.newaxis]
    employment = state.labor_pool * new_emp_rate

    # Total demand = macro + building (building is a subset, already counted)
    labor_demand = np.maximum(macro_demand, building_demand)
    employment = np.minimum(employment, state.labor_pool)

    return labor_demand, employment


def _compute_labor_demand(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute total labor demand from production capacity and utilization (legacy).
    Returns: (N, S) workers demanded.
    """
    N = config.N_LGAS
    S = config.N_SKILL_TIERS
    demand = np.zeros((N, S), dtype=np.float64)

    for cdef in COMMODITIES:
        c = cdef.id
        cap = state.production_capacity[:, c]
        auto = state.automation_level[:, c]

        for skill_int, amount in cdef.labor_requirements.items():
            s = int(skill_int)
            # Automation reduces labor needed
            effective_req = amount * (1.0 - auto * 0.5)
            demand[:, s] += cap * effective_req

    return demand


def adjust_wages(
    current_wages: np.ndarray,  # (N, S)
    labor_demand: np.ndarray,   # (N, S)
    labor_supply: np.ndarray,   # (N, S)
    minimum_wage: float,
    adjustment_speed: float,
) -> np.ndarray:
    """
    Adjust wages toward market-clearing levels.

    Excess demand → wages rise. Excess supply → wages fall (sticky downward).
    """
    safe_supply = np.maximum(labor_supply, 1.0)
    excess_demand_ratio = (labor_demand - labor_supply) / safe_supply
    wage_change = adjustment_speed * excess_demand_ratio

    # Sticky downward: negative adjustments halved
    wage_change = np.where(wage_change < 0, wage_change * 0.5, wage_change)

    # Clamp changes
    wage_change = np.clip(wage_change, -0.10, 0.15)

    new_wages = current_wages * (1.0 + wage_change)
    new_wages = np.maximum(new_wages, minimum_wage)
    return new_wages


def evaluate_strikes(
    state: EconomicState, config: SimConfig,
) -> Tuple[np.ndarray, List[int]]:
    """
    Determine which LGAs experience strikes.

    Strike when unskilled wage / cost_of_living < STRIKE_THRESHOLD.
    """
    N = config.N_LGAS
    strikes = state.strikes_active.copy()
    triggered = []

    # Decrement active strikes
    strikes = np.maximum(strikes - 1, 0)

    # Compute cost of living: weighted food basket for the poorest quintile
    # Weights reflect actual consumption patterns — poor households eat
    # mainly grains, cassava, and some processed food; not much fish/meat
    # IDs: 6=grains, 7=rice, 8=cassava, 13=fish, 18=processed_food, 21=meat
    food_ids =     [6,    7,    8,     13,   18,   21]
    food_weights = [0.30, 0.20, 0.25,  0.05, 0.15, 0.05]  # sum=1.0
    q1_food_share = CONSUMPTION_WEIGHTS_BY_QUINTILE[0, 0]  # Q1 food weight (0.55)

    # Weighted average food price — emphasizes staples over proteins
    weighted_food_price = np.zeros(N, dtype=np.float64)
    for c_id, w in zip(food_ids, food_weights):
        weighted_food_price += state.prices[:, c_id] * w

    # Cost of living = food spending share × weighted food price
    cost_of_living = weighted_food_price * q1_food_share
    cost_of_living = np.maximum(cost_of_living, 1.0)

    # Wage adequacy
    unskilled_wage = state.wages[:, SkillTier.UNSKILLED]
    wage_adequacy = unskilled_wage / cost_of_living

    # Strike probability
    below_threshold = wage_adequacy < config.STRIKE_THRESHOLD
    strike_prob = np.where(
        below_threshold,
        config.STRIKE_BASE_PROBABILITY * (config.STRIKE_THRESHOLD - wage_adequacy) / config.STRIKE_THRESHOLD,
        0.0,
    )

    # Don't strike if already striking
    strike_prob[strikes > 0] = 0.0

    # Roll for strikes
    rolls = state.rng.random(N)
    new_strikes = rolls < strike_prob
    if new_strikes.any():
        duration_min, duration_max = config.STRIKE_DURATION_RANGE
        durations = state.rng.integers(duration_min, duration_max + 1, size=N)
        strikes[new_strikes] = durations[new_strikes]
        triggered = list(np.where(new_strikes)[0])

    if triggered:
        logger.info("Strikes triggered in %d LGAs", len(triggered))

    return strikes, triggered


def process_automation(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Firms automate when labor is expensive. Automation is irreversible.

    automation_level increases by AUTOMATION_DISPLACEMENT_RATE when
    wages exceed AUTOMATION_INVESTMENT_THRESHOLD * BASE_WAGES.
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES
    auto = state.automation_level.copy()

    for cdef in COMMODITIES:
        c = cdef.id
        if not cdef.labor_requirements:
            continue

        # Check if wages for required tiers exceed threshold
        for skill_int, amount in cdef.labor_requirements.items():
            s = int(skill_int)
            threshold = config.AUTOMATION_INVESTMENT_THRESHOLD * config.BASE_WAGES[s]
            expensive = state.wages[:, s] > threshold

            # Only automate where there's production capacity
            has_cap = state.production_capacity[:, c] > 0
            should_automate = expensive & has_cap

            if should_automate.any():
                auto[should_automate, c] += config.AUTOMATION_DISPLACEMENT_RATE
                break  # one trigger per commodity

    # Cap at 0.80
    auto = np.clip(auto, 0.0, 0.80)
    return auto


def compute_informal_sector(
    unemployment: np.ndarray,  # (N, S)
    config: SimConfig,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Unemployed workers enter informal economy.

    70% of unemployed go informal.
    Earn INFORMAL_WAGE_FRACTION of formal wages.
    """
    informal = unemployment * 0.70
    informal_income = informal * config.INFORMAL_WAGE_FRACTION * config.BASE_WAGES[np.newaxis, :]
    return informal, informal_income


def apply_labor_mutations(
    state: EconomicState, mutations: LaborMutations,
    strikes_active: np.ndarray | None = None,
) -> None:
    """Apply labor tick results to state."""
    state.wages = mutations.wages_new
    state.labor_employed = np.minimum(mutations.employment_new, state.labor_pool)
    state.labor_informal = mutations.informal_new
    if strikes_active is not None:
        state.strikes_active = strikes_active
    state.automation_level = mutations.automation_changes
