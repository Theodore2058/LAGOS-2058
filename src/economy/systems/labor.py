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

    1. Compute labor demand from production capacity
    2. Match workers to jobs (highest-wage first)
    3. Adjust wages based on supply/demand
    4. Check strike conditions
    5. Process automation
    6. Compute informal sector
    """
    N = config.N_LGAS
    S = config.N_SKILL_TIERS

    # 1. Compute labor demand
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


def _compute_labor_demand(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute total labor demand from production capacity and utilization.
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

    # Compute cost of living: mean food price × Q1 food weight
    # This represents the minimum food cost for the poorest quintile
    food_ids = [6, 7, 8, 13, 18, 21]
    food_weight = CONSUMPTION_WEIGHTS_BY_QUINTILE[0, 0]  # Q1 food weight (0.55)

    # Average price across food commodities in each LGA
    mean_food_price = np.zeros(N, dtype=np.float64)
    for c_id in food_ids:
        mean_food_price += state.prices[:, c_id]
    mean_food_price /= len(food_ids)

    # Cost of living = food spending share × average food price
    # This gives a monthly cost proxy that scales with local food prices
    cost_of_living = mean_food_price * food_weight
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
    state.labor_employed = mutations.employment_new
    state.labor_informal = mutations.informal_new
    if strikes_active is not None:
        state.strikes_active = strikes_active
    state.automation_level = mutations.automation_changes
