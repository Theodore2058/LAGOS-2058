"""
Government System — policy queue processing, budget allocation, and corruption.

Runs once per structural tick (monthly). Processes enacted policies after their
implementation delay, advances construction projects, computes tax revenue,
allocates budget across 12 ministries with corruption leakage, and handles
infrastructure decay and repair.
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np

from src.economy.core.types import (
    ConstructionProject,
    EconomicState,
    PolicyAction,
    SimConfig,
)
from src.economy.data.ministries import MINISTRIES, N_MINISTRIES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ministry indices for infrastructure repair
# ---------------------------------------------------------------------------

MINISTRY_INFRASTRUCTURE: int = 1   # Roads, bridges, transport
MINISTRY_ENERGY: int = 10          # Power generation & grid

# Infrastructure repair budget-to-quality conversion factor
# 1 billion naira of effective spend restores ~0.01 quality points per LGA
_ROAD_REPAIR_EFFICIENCY: float = 1e-11
_POWER_REPAIR_EFFICIENCY: float = 1e-11


# ---------------------------------------------------------------------------
# tick_government
# ---------------------------------------------------------------------------

def tick_government(state: EconomicState, config: SimConfig) -> None:
    """Run all government sub-systems for one structural tick (month)."""

    # 1. Process matured policies
    _process_policy_queue(state, config)

    # 2. Advance construction projects
    _tick_construction(state, config)

    # 3. Compute total tax revenue
    revenue = compute_tax_revenue(state, config)
    logger.info("Monthly tax revenue: %.2f naira", revenue)

    # 4. Allocate budget across ministries
    _allocate_budget(state, config, revenue)

    # 5. Infrastructure decay
    _decay_infrastructure(state, config)

    # 6. Infrastructure repair from released budget
    _repair_infrastructure(state, config)


# ---------------------------------------------------------------------------
# Policy queue processing
# ---------------------------------------------------------------------------

def _process_policy_queue(state: EconomicState, config: SimConfig) -> None:
    """Apply policies whose implementation delay has elapsed."""

    remaining: List[PolicyAction] = []
    for policy in state.policy_queue:
        days_elapsed = state.game_day - policy.enacted_game_day
        if days_elapsed >= policy.implementation_delay:
            process_policy(state, policy, config)
        else:
            remaining.append(policy)
    state.policy_queue = remaining


def process_policy(
    state: EconomicState,
    policy: PolicyAction,
    config: SimConfig,
) -> None:
    """Apply a single policy action to economic state."""

    action = policy.action_type
    params = policy.parameters

    if action == "set_tax_rate":
        tax_field = params.get("tax_field")
        new_rate = float(params["rate"])
        if tax_field == "income":
            old = state.tax_rate_income
            state.tax_rate_income = np.clip(new_rate, 0.0, 0.50)
            logger.info("Income tax: %.2f -> %.2f", old, state.tax_rate_income)
        elif tax_field == "corporate":
            old = state.tax_rate_corporate
            state.tax_rate_corporate = np.clip(new_rate, 0.0, 0.50)
            logger.info("Corporate tax: %.2f -> %.2f", old, state.tax_rate_corporate)
        elif tax_field == "vat":
            old = state.tax_rate_vat
            state.tax_rate_vat = np.clip(new_rate, 0.0, 0.30)
            logger.info("VAT: %.2f -> %.2f", old, state.tax_rate_vat)
        elif tax_field == "import_tariff":
            old = state.tax_rate_import_tariff
            state.tax_rate_import_tariff = np.clip(new_rate, 0.0, 0.60)
            logger.info(
                "Import tariff: %.2f -> %.2f", old, state.tax_rate_import_tariff,
            )
        else:
            logger.warning("Unknown tax_field: %s", tax_field)

    elif action == "set_minimum_wage":
        old = state.minimum_wage
        state.minimum_wage = max(0.0, float(params["wage"]))
        logger.info("Minimum wage: %.0f -> %.0f", old, state.minimum_wage)

    elif action == "start_construction":
        project = ConstructionProject(
            project_type=params["project_type"],
            lga_id=int(params["lga_id"]),
            commodity_id=params.get("commodity_id"),
            months_remaining=int(params["months"]),
            monthly_cost_naira=float(params["monthly_cost"]),
            monthly_labor_demand=params.get("labor_demand", {}),
            completion_effect=params.get("completion_effect", {}),
        )
        state.construction_projects.append(project)
        logger.info(
            "Construction started: %s in LGA %d (%d months)",
            project.project_type, project.lga_id, project.months_remaining,
        )

    elif action == "set_bic_enforcement":
        old = state.bic_enforcement_intensity
        state.bic_enforcement_intensity = np.clip(
            float(params["intensity"]), 0.0, 1.0,
        )
        logger.info(
            "BIC enforcement: %.2f -> %.2f", old, state.bic_enforcement_intensity,
        )
        # BIC enforcement reduces corruption leakage across all ministries
        _update_corruption_leakage(state, config)

    elif action == "set_zoning":
        lga_id = int(params["lga_id"])
        restriction = float(params["restriction"])
        if state.zoning_restriction is not None and 0 <= lga_id < config.N_LGAS:
            state.zoning_restriction[lga_id] = np.clip(restriction, 0.0, 1.0)
            logger.info(
                "Zoning restriction LGA %d set to %.2f", lga_id, restriction,
            )

    else:
        logger.warning("Unknown policy action: %s", action)


# ---------------------------------------------------------------------------
# Construction projects
# ---------------------------------------------------------------------------

def _tick_construction(state: EconomicState, config: SimConfig) -> None:
    """Decrement construction timers and apply completion effects."""

    remaining: List[ConstructionProject] = []
    for project in state.construction_projects:
        project.months_remaining -= 1

        if project.months_remaining <= 0:
            _apply_completion_effect(state, project, config)
            logger.info(
                "Construction complete: %s in LGA %d",
                project.project_type, project.lga_id,
            )
        else:
            remaining.append(project)

    state.construction_projects = remaining


def _apply_completion_effect(
    state: EconomicState,
    project: ConstructionProject,
    config: SimConfig,
) -> None:
    """Apply a completed construction project's effects to the state."""

    effect = project.completion_effect
    lga = project.lga_id

    # Production capacity boost
    if "production_capacity" in effect and state.production_capacity is not None:
        commodity_id = effect["production_capacity"]["commodity_id"]
        amount = effect["production_capacity"]["amount"]
        state.production_capacity[lga, commodity_id] += amount

    # Road quality improvement
    if "road_quality" in effect and state.infra_road_quality is not None:
        state.infra_road_quality[lga] = min(
            1.0, state.infra_road_quality[lga] + effect["road_quality"],
        )

    # Power reliability improvement
    if "power_reliability" in effect and state.infra_power_reliability is not None:
        state.infra_power_reliability[lga] = min(
            1.0, state.infra_power_reliability[lga] + effect["power_reliability"],
        )

    # Housing supply
    if "housing_supply" in effect and state.land_area is not None:
        state.land_area[lga, 1] += effect["housing_supply"]  # residential


# ---------------------------------------------------------------------------
# Tax revenue
# ---------------------------------------------------------------------------

def compute_tax_revenue(state: EconomicState, config: SimConfig) -> float:
    """
    Compute total monthly tax revenue in naira.

    Components: income tax, corporate tax, VAT, import tariffs.
    """

    revenue = 0.0

    # Income tax: sum(wages * employment) * tax_rate_income
    if state.wages is not None and state.labor_employed is not None:
        total_wage_bill = float(np.sum(state.wages * state.labor_employed))
        revenue += total_wage_bill * state.tax_rate_income

    # Corporate tax: sum(production_capacity * prices) * tax_rate_corporate
    if state.production_capacity is not None and state.prices is not None:
        gross_output_value = float(
            np.sum(state.production_capacity * state.prices),
        )
        revenue += gross_output_value * state.tax_rate_corporate

    # VAT: consumer spending proxy from wages * employment * consumption share
    if state.wages is not None and state.labor_employed is not None:
        consumer_spending = float(np.sum(state.wages * state.labor_employed)) * 0.65
        revenue += consumer_spending * state.tax_rate_vat

    # Import tariff: monthly import bill in USD * parallel rate * tariff rate
    import_bill_naira = state.monthly_import_bill_usd * state.parallel_exchange_rate
    revenue += import_bill_naira * state.tax_rate_import_tariff

    return revenue


# ---------------------------------------------------------------------------
# Budget allocation & corruption
# ---------------------------------------------------------------------------

def _allocate_budget(
    state: EconomicState,
    config: SimConfig,
    total_revenue: float,
) -> None:
    """Distribute revenue across ministries, apply corruption leakage."""

    if state.budget_allocation is None:
        return

    # Normalise allocation weights to sum to 1
    alloc = state.budget_allocation.copy()
    alloc_sum = alloc.sum()
    if alloc_sum > 0:
        alloc /= alloc_sum
    else:
        alloc[:] = 1.0 / N_MINISTRIES

    # Raw allocation per ministry
    allocated = alloc * total_revenue  # (12,)

    # Ensure corruption leakage and state capacity are current
    _update_corruption_leakage(state, config)

    if state.corruption_leakage is None or state.state_capacity is None:
        return

    # Released budget = allocated * state_capacity * (1 - leakage)
    released = allocated * state.state_capacity * (1.0 - state.corruption_leakage)

    if state.budget_released is not None:
        state.budget_released[:] = released

    leaked = float(np.sum(allocated - released))
    logger.debug(
        "Budget: %.2f allocated, %.2f released, %.2f leaked",
        total_revenue, float(np.sum(released)), leaked,
    )


def _update_corruption_leakage(
    state: EconomicState,
    config: SimConfig,
) -> None:
    """
    Recompute per-ministry corruption leakage and state capacity,
    accounting for BIC enforcement.
    """

    if state.corruption_leakage is None:
        state.corruption_leakage = np.zeros(N_MINISTRIES, dtype=np.float64)
    if state.state_capacity is None:
        state.state_capacity = np.zeros(N_MINISTRIES, dtype=np.float64)

    bic_reduction = state.bic_enforcement_intensity * config.BIC_ENFORCEMENT_LEAKAGE_REDUCTION

    for mid in range(N_MINISTRIES):
        mdef = MINISTRIES[mid]
        raw_leakage = mdef["base_leakage"] - bic_reduction
        state.corruption_leakage[mid] = np.clip(
            raw_leakage,
            config.CORRUPTION_LEAKAGE_MIN,
            config.CORRUPTION_LEAKAGE_MAX,
        )
        state.state_capacity[mid] = np.clip(
            mdef["base_capacity"] + bic_reduction * 0.5,
            config.STATE_CAPACITY_MIN,
            config.STATE_CAPACITY_MAX,
        )


# ---------------------------------------------------------------------------
# Infrastructure decay & repair
# ---------------------------------------------------------------------------

def _decay_infrastructure(state: EconomicState, config: SimConfig) -> None:
    """Apply monthly infrastructure quality decay."""

    monthly_decay = config.INFRASTRUCTURE_DECAY_RATE / 12.0

    if state.infra_road_quality is not None:
        state.infra_road_quality *= (1.0 - monthly_decay)
        np.clip(state.infra_road_quality, 0.0, 1.0, out=state.infra_road_quality)

    if state.infra_power_reliability is not None:
        state.infra_power_reliability *= (1.0 - monthly_decay)
        np.clip(
            state.infra_power_reliability, 0.0, 1.0,
            out=state.infra_power_reliability,
        )


def _repair_infrastructure(state: EconomicState, config: SimConfig) -> None:
    """
    Convert released ministry budgets into infrastructure quality repair.

    Transport ministry (ID 1) repairs roads.
    Energy ministry (ID 10) repairs power.
    """

    if state.budget_released is None:
        return

    # Road repair from Infrastructure ministry
    if state.infra_road_quality is not None:
        road_budget = state.budget_released[MINISTRY_INFRASTRUCTURE]
        if road_budget > 0:
            n_lgas = state.infra_road_quality.shape[0]
            per_lga = road_budget / n_lgas
            repair = per_lga * _ROAD_REPAIR_EFFICIENCY
            state.infra_road_quality += repair
            np.clip(state.infra_road_quality, 0.0, 1.0, out=state.infra_road_quality)

    # Power repair from Energy ministry
    if state.infra_power_reliability is not None:
        power_budget = state.budget_released[MINISTRY_ENERGY]
        if power_budget > 0:
            n_lgas = state.infra_power_reliability.shape[0]
            per_lga = power_budget / n_lgas
            repair = per_lga * _POWER_REPAIR_EFFICIENCY
            state.infra_power_reliability += repair
            np.clip(
                state.infra_power_reliability, 0.0, 1.0,
                out=state.infra_power_reliability,
            )
