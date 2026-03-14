"""
Per-pop economic behavior system.

Each of the 174,960 voter types acts as an economic agent with:
  - Income from employment (formal wages, informal work, government transfers)
  - Savings that accumulate and can be drawn down
  - Consumption budget split across commodity baskets by income quintile
  - Standard of living tracking based on consumption fulfillment
  - Investment decisions (savings rate adjustment)

Called once per production tick (7/month) for income/savings updates.
Pop buy orders are computed every market tick (56/month) for the order book.
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import numpy as np

from src.economy.core.types import (
    EconomicState,
    SimConfig,
    CONSUMPTION_BASKET_COMMODITY_MAP,
    CONSUMPTION_WEIGHTS_BY_QUINTILE,
)
from src.economy.data.commodities import BASE_PRICES, DEMAND_ELASTICITIES

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Livelihood constants
# ---------------------------------------------------------------------------

# Livelihood IDs: 0=Smallholder, 1=Commercial_ag, 2=Trade_informal,
#                 3=Formal_private, 4=Public_sector, 5=Unemployed

# Map livelihood to primary skill tier for wage lookup
LIVELIHOOD_TO_SKILL = np.array([0, 1, 0, 1, 2, 0], dtype=np.int32)

# Income multiplier by livelihood (relative to base wage of their skill tier)
LIVELIHOOD_INCOME_MULT = np.array([0.6, 0.9, 0.4, 1.0, 1.2, 0.1], dtype=np.float64)

# Income multiplier by income bracket (Bottom 40%, Middle 40%, Top 20%)
INCOME_BRACKET_MULT = np.array([0.5, 1.0, 2.5], dtype=np.float64)

# Map income bracket to consumption quintile
# Bottom 40% -> Q1/Q2 (average), Middle 40% -> Q3, Top 20% -> Q4/Q5 (average)
INCOME_TO_QUINTILE_WEIGHTS = np.array([
    [0.5, 0.5, 0.0, 0.0, 0.0],  # Bottom 40% -> 50% Q1 + 50% Q2
    [0.0, 0.0, 1.0, 0.0, 0.0],  # Middle 40% -> 100% Q3
    [0.0, 0.0, 0.0, 0.5, 0.5],  # Top 20% -> 50% Q4 + 50% Q5
], dtype=np.float64)

# Savings rate by income bracket (poor save less)
SAVINGS_RATE = np.array([0.02, 0.08, 0.18], dtype=np.float64)


# ---------------------------------------------------------------------------
# Pop income update (production tick)
# ---------------------------------------------------------------------------

def tick_pop_income(state: EconomicState, config: SimConfig) -> None:
    """
    Update per-pop income based on current wages, employment, and transfers.

    Called once per production tick (7/month).
    """
    NVT = config.N_VOTER_TYPES
    N = config.N_LGAS

    if state.pop_income is None or state.wages is None:
        return

    pop_lga = getattr(state, "_pop_lga_ids", None)
    pop_livelihood = getattr(state, "_pop_livelihood_ids", None)
    pop_income_bracket = getattr(state, "_pop_income_ids", None)

    if pop_lga is None or pop_livelihood is None or pop_income_bracket is None:
        return

    # Compute income for each pop type
    skills = LIVELIHOOD_TO_SKILL[pop_livelihood]  # (NVT,)
    base_wages = state.wages[pop_lga, skills]  # (NVT,)
    liv_mult = LIVELIHOOD_INCOME_MULT[pop_livelihood]  # (NVT,)
    inc_mult = INCOME_BRACKET_MULT[pop_income_bracket]  # (NVT,)

    # Formal income
    formal_income = base_wages * liv_mult * inc_mult * state.pop_employed_formal

    # Informal income (40% of formal wage)
    informal_income = (
        base_wages * config.INFORMAL_WAGE_FRACTION
        * state.pop_employed_informal
    )

    # Government transfers for unemployed (minimum wage * 10%)
    unemployed_frac = np.maximum(
        1.0 - state.pop_employed_formal - state.pop_employed_informal, 0.0,
    )
    transfers = config.BASE_WAGES[0] * 0.10 * unemployed_frac

    # Al-Shahid service provision: adds income equivalent in controlled areas
    alsahid_income = np.zeros(NVT, dtype=np.float64)
    if state.alsahid_control is not None and state.alsahid_service_provision is not None:
        control = state.alsahid_control[pop_lga]
        service = state.alsahid_service_provision[pop_lga]
        # Al-Shahid provides services equivalent to some income
        alsahid_income = control * service * config.BASE_WAGES[0] * 0.15

    # Enhancement bonus to income
    enh_bonus = np.ones(NVT, dtype=np.float64)
    if state.enhancement_adoption is not None:
        enh = state.enhancement_adoption[pop_lga]
        enh_bonus = 1.0 + enh * config.ENHANCEMENT_PRODUCTIVITY_BONUS

    total_income = (formal_income + informal_income + transfers + alsahid_income) * enh_bonus
    state.pop_income = np.maximum(total_income, 0.0)

    # Update savings
    savings_rate = SAVINGS_RATE[pop_income_bracket]
    monthly_saving = state.pop_income * savings_rate / config.PRODUCTION_TICKS_PER_MONTH
    state.pop_savings = np.maximum(state.pop_savings + monthly_saving, 0.0)

    # Cap savings at 24 months of income (prevent runaway accumulation)
    max_savings = state.pop_income * 24.0
    state.pop_savings = np.minimum(state.pop_savings, np.maximum(max_savings, 1.0))


# ---------------------------------------------------------------------------
# Pop buy orders (market tick)
# ---------------------------------------------------------------------------

def compute_pop_buy_orders(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute aggregate buy orders per LGA per commodity from all pop types.

    Optimized: aggregates pop budgets to (LGA, income_bracket) groups first
    (774 × 3 = 2,322 groups) before computing commodity demand, avoiding
    per-pop operations on 174,960 elements in the inner loop.

    Returns: (N, C) array of total units demanded per LGA per commodity.
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES
    NVT = config.N_VOTER_TYPES
    N_INC = 3  # income brackets

    if state.pop_income is None or state.prices is None:
        return np.zeros((N, C), dtype=np.float64)

    pop_lga = getattr(state, "_pop_lga_ids", None)
    pop_income_bracket = getattr(state, "_pop_income_ids", None)
    if pop_lga is None or pop_income_bracket is None:
        return np.zeros((N, C), dtype=np.float64)

    # Per-tick spending budget = (income * (1 - savings_rate)) / 56 ticks
    savings_rate = SAVINGS_RATE[pop_income_bracket]
    consumption_budget = (
        state.pop_income * (1.0 - savings_rate)
        / config.MARKET_TICKS_PER_MONTH
    )  # (NVT,) per-capita per-tick budget

    # Scale by population count to get total spending
    total_budget = consumption_budget * state.pop_count  # (NVT,)

    # Desperation spending: if SoL is low, dip into savings
    if state.pop_standard_of_living is not None:
        low_sol = state.pop_standard_of_living < 3.0
        desperation_mult = np.where(low_sol, 1.3, 1.0)
        total_budget *= desperation_mult

    # --- Aggregate total_budget to (LGA, income_bracket) groups ---
    # Composite key: lga * 3 + income_bracket
    group_key = pop_lga * N_INC + pop_income_bracket  # (NVT,)
    n_groups = N * N_INC

    # Precompute consumption weights per income bracket (only 3 unique sets)
    # INCOME_TO_QUINTILE_WEIGHTS is (3, 5), CONSUMPTION_WEIGHTS_BY_QUINTILE is (5, 9)
    bracket_cat_weights = INCOME_TO_QUINTILE_WEIGHTS @ CONSUMPTION_WEIGHTS_BY_QUINTILE  # (3, 9)

    # Aggregate budget per group
    group_budget = np.bincount(group_key, weights=total_budget, minlength=n_groups)  # (N*3,)
    group_budget = group_budget.reshape(N, N_INC)  # (N, 3)

    # --- Compute demand per commodity using groups ---
    categories = list(CONSUMPTION_BASKET_COMMODITY_MAP.keys())
    demand = np.zeros((N, C), dtype=np.float64)

    for cat_idx, cat_name in enumerate(categories):
        commodity_ids = CONSUMPTION_BASKET_COMMODITY_MAP[cat_name]
        if not commodity_ids:
            continue

        # Per-bracket category spending at each LGA: (N, 3)
        cat_spending = group_budget * bracket_cat_weights[np.newaxis, :, cat_idx]  # (N, 3)
        per_commodity_spending = cat_spending / len(commodity_ids)  # (N, 3)

        for c_id in commodity_ids:
            # Local price at each LGA
            local_price = state.prices[:, c_id]  # (N,)
            safe_price = np.maximum(local_price, 1.0)  # (N,)

            # Price elasticity
            price_ratio = local_price / BASE_PRICES[c_id]
            safe_ratio = np.maximum(price_ratio, 0.01)
            elastic_factor = safe_ratio ** DEMAND_ELASTICITIES[c_id]  # (N,)

            # Quantity demand per LGA = sum across income brackets
            qty_per_bracket = per_commodity_spending / safe_price[:, np.newaxis]  # (N, 3)
            qty_demand = (qty_per_bracket * elastic_factor[:, np.newaxis]).sum(axis=1)  # (N,)

            demand[:, c_id] += qty_demand

    demand = np.maximum(demand, 0.0)
    return demand


# ---------------------------------------------------------------------------
# Standard of living update (production tick)
# ---------------------------------------------------------------------------

def update_standard_of_living(state: EconomicState, config: SimConfig) -> None:
    """
    Update per-pop standard of living based on consumption fulfillment,
    income, and local conditions.

    SoL is a 0-10 scale:
      0-2: extreme poverty (unable to meet basic needs)
      3-4: subsistence (food and shelter barely met)
      5-6: moderate (comfortable but not affluent)
      7-8: prosperous (most needs well met)
      9-10: elite (luxury lifestyle)
    """
    NVT = config.N_VOTER_TYPES
    if state.pop_income is None or state.pop_consumption_fulfilled is None:
        return

    pop_lga = getattr(state, "_pop_lga_ids", None)
    if pop_lga is None:
        return

    # Income component: log-scaled relative to median
    income = state.pop_income
    median_inc = max(np.median(income[income > 0]), 1.0)
    income_ratio = income / median_inc
    income_sol = 5.0 + 2.0 * np.log(np.maximum(income_ratio, 0.01))

    # Consumption fulfillment component (0-1 -> 0-10)
    fulfill_sol = state.pop_consumption_fulfilled * 10.0

    # Infrastructure component
    infra_sol = np.full(NVT, 5.0, dtype=np.float64)
    if state.infra_power_reliability is not None:
        power = state.infra_power_reliability[pop_lga]
        infra_sol = power * 7.0 + 1.5  # range ~1.5-8.5

    # Al-Shahid penalty: living under insurgent control reduces SoL
    security_penalty = np.zeros(NVT, dtype=np.float64)
    if state.alsahid_control is not None:
        control = state.alsahid_control[pop_lga]
        security_penalty = control * 2.0  # up to -2 SoL in fully controlled areas

    # Weighted combination
    new_sol = (
        0.40 * income_sol
        + 0.35 * fulfill_sol
        + 0.15 * infra_sol
        - 0.10 * security_penalty * 10.0
    )

    # EMA smoothing: SoL changes slowly (inertia)
    alpha = 0.15  # 15% weight to new value per production tick
    state.pop_standard_of_living = np.clip(
        (1.0 - alpha) * state.pop_standard_of_living + alpha * new_sol,
        0.0, 10.0,
    )


# ---------------------------------------------------------------------------
# Pop employment update (production tick)
# ---------------------------------------------------------------------------

def update_pop_employment(state: EconomicState, config: SimConfig) -> None:
    """
    Update per-pop formal/informal employment rates based on LGA labor market.

    Maps aggregate LGA employment rates to individual pop types based on
    their livelihood and skill tier.
    """
    NVT = config.N_VOTER_TYPES
    if state.labor_employed is None or state.labor_pool is None:
        return

    pop_lga = getattr(state, "_pop_lga_ids", None)
    pop_livelihood = getattr(state, "_pop_livelihood_ids", None)
    if pop_lga is None or pop_livelihood is None:
        return

    # LGA-level employment rate by skill tier
    safe_pool = np.maximum(state.labor_pool, 1.0)
    emp_rate = state.labor_employed / safe_pool  # (N, 4)
    emp_rate = np.clip(emp_rate, 0.0, 1.0)

    # Map to pop types
    skills = LIVELIHOOD_TO_SKILL[pop_livelihood]
    lga_emp_rate = emp_rate[pop_lga, skills]  # (NVT,)

    # Base formal/informal rates from livelihood
    base_formal = np.array([0.30, 0.70, 0.10, 0.85, 0.95, 0.0], dtype=np.float64)
    base_informal = np.array([0.50, 0.20, 0.80, 0.10, 0.03, 0.20], dtype=np.float64)

    formal_base = base_formal[pop_livelihood]
    informal_base = base_informal[pop_livelihood]

    # Scale by actual LGA employment rate
    state.pop_employed_formal = formal_base * lga_emp_rate
    state.pop_employed_informal = informal_base * np.minimum(1.0 - lga_emp_rate + 0.3, 1.0)

    # Ensure total employment <= 1.0
    total = state.pop_employed_formal + state.pop_employed_informal
    excess = np.maximum(total - 1.0, 0.0)
    state.pop_employed_informal = np.maximum(state.pop_employed_informal - excess, 0.0)


# ---------------------------------------------------------------------------
# Pop consumption fulfillment (market tick, called after order book clearing)
# ---------------------------------------------------------------------------

def update_consumption_fulfillment(
    state: EconomicState, config: SimConfig,
    demand: np.ndarray, fulfilled: np.ndarray,
) -> None:
    """
    Update per-pop consumption fulfillment after market clearing.

    Parameters
    ----------
    demand : (N, C) total demanded per LGA per commodity
    fulfilled : (N, C) total actually consumed per LGA per commodity
    """
    N = config.N_LGAS
    NVT = config.N_VOTER_TYPES

    pop_lga = getattr(state, "_pop_lga_ids", None)
    if pop_lga is None or state.pop_consumption_fulfilled is None:
        return

    # Per-LGA fulfillment ratio
    safe_demand = np.maximum(demand.sum(axis=1), 1.0)  # (N,)
    lga_fulfillment = np.clip(fulfilled.sum(axis=1) / safe_demand, 0.0, 1.0)

    # Map to pop types
    pop_fulfill = lga_fulfillment[pop_lga]  # (NVT,)

    # EMA smoothing
    alpha = 0.3
    state.pop_consumption_fulfilled = np.clip(
        (1.0 - alpha) * state.pop_consumption_fulfilled + alpha * pop_fulfill,
        0.0, 1.0,
    )
