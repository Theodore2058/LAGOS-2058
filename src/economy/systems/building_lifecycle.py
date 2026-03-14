"""
Building construction and destruction lifecycle.

Runs at the structural tick (1/month):
  1. Age all buildings by 1 month
  2. Evaluate building closures (unprofitable, damaged, obsolete)
  3. Process construction projects completing into new buildings
  4. Zaibatsu/government investment decisions (start new construction)

Buildings can be destroyed by:
  - Al-Shahid attacks (in high-control areas)
  - Extended unprofitability (no output for 6+ months)
  - Infrastructure collapse (power/road below minimum for 3+ months)
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import (
    ConstructionProject,
    EconomicState,
    SimConfig,
)
from src.economy.data.buildings import (
    BUILDING_TYPE_BY_ID,
    BUILDING_TYPES,
    BT_OUTPUT_COMMODITY,
    BT_REQUIRES_POWER,
    BT_MIN_POWER,
)
from src.economy.data.zaibatsu import ZAIBATSU_BY_ID

logger = logging.getLogger(__name__)


def tick_building_lifecycle(state: EconomicState, config: SimConfig) -> None:
    """
    Monthly building lifecycle update.

    Modifies state in-place: ages buildings, removes closures, completes
    construction projects, starts new investments, and upgrades tech levels.
    """
    if state.building_type_ids is None or state.n_buildings == 0:
        return

    # 1. Age all buildings
    if state.building_age is not None:
        state.building_age += 1

    # 2. Tech level upgrades (learning by doing + enhancement)
    _upgrade_tech_levels(state, config)

    # 3. Evaluate closures
    _process_closures(state, config)

    # 4. Complete construction projects → new buildings
    _complete_construction(state, config)

    # 5. Investment decisions (zaibatsu + government)
    _zaibatsu_investment(state, config)
    _government_investment(state, config)


# ---------------------------------------------------------------------------
# Tech level upgrades
# ---------------------------------------------------------------------------

def _upgrade_tech_levels(state: EconomicState, config: SimConfig) -> None:
    """
    Buildings improve tech level over time through:
    1. Learning-by-doing: operational buildings gain +0.005/month (capped at 1.0)
    2. Enhancement adoption: local enhancement boosts tech growth
    3. Zaibatsu-owned buildings have faster learning (+50%)
    """
    if state.building_tech_level is None:
        return

    B = state.n_buildings
    lga_ids = state.building_lga_ids.astype(np.intp)

    # Base learning rate for operational buildings
    base_rate = 0.005  # +0.5% per month
    learning = np.where(state.building_operational, base_rate, 0.0)

    # Zaibatsu bonus: 50% faster learning
    owned = state.building_owners >= 0
    learning = np.where(owned, learning * 1.5, learning)

    # Enhancement adoption bonus
    if state.enhancement_adoption is not None:
        enh = state.enhancement_adoption[lga_ids]
        learning *= (1.0 + enh * 0.5)  # up to 50% faster with full enhancement

    state.building_tech_level = np.minimum(
        state.building_tech_level + learning, 1.0,
    )


# ---------------------------------------------------------------------------
# Closures
# ---------------------------------------------------------------------------

def _process_closures(state: EconomicState, config: SimConfig) -> None:
    """Remove buildings that have been non-operational too long or destroyed."""
    B = state.n_buildings
    if B == 0:
        return

    keep_mask = np.ones(B, dtype=bool)

    bt_ids = state.building_type_ids.astype(np.intp)
    lga_ids = state.building_lga_ids.astype(np.intp)

    # Al-Shahid destruction: 2% monthly chance per building in areas with >0.5 control
    if state.alsahid_control is not None:
        control = state.alsahid_control[lga_ids]
        high_control = control > 0.5
        if high_control.any():
            destroy_roll = state.rng.random(B)
            destroy_prob = control * 0.02  # up to 2% per month
            destroyed = high_control & (destroy_roll < destroy_prob)
            keep_mask &= ~destroyed
            n_destroyed = destroyed.sum()
            if n_destroyed > 0:
                logger.info("Al-Shahid destroyed %d buildings", n_destroyed)

    # Extended non-operation: buildings non-operational for 6+ months close
    # Track via building_age: if operational is False and age > 6 months, close
    # Simplified: if building has near-zero employees and is old, close
    if state.building_employees is not None and state.building_age is not None:
        total_employed = state.building_employees.sum(axis=1)
        idle = (total_employed < 0.1) & (~state.building_operational) & (state.building_age > 6)
        keep_mask &= ~idle
        n_idle = idle.sum()
        if n_idle > 0:
            logger.info("Closed %d idle buildings", n_idle)

    # Apply closures
    if not keep_mask.all():
        _remove_buildings(state, keep_mask)


def _remove_buildings(state: EconomicState, keep_mask: np.ndarray) -> None:
    """Remove buildings where keep_mask is False."""
    state.building_type_ids = state.building_type_ids[keep_mask]
    state.building_lga_ids = state.building_lga_ids[keep_mask]
    state.building_owners = state.building_owners[keep_mask]
    state.building_throughput = state.building_throughput[keep_mask]
    state.building_tech_level = state.building_tech_level[keep_mask]
    state.building_employees = state.building_employees[keep_mask]
    state.building_operational = state.building_operational[keep_mask]
    state.building_age = state.building_age[keep_mask]
    state.n_buildings = int(keep_mask.sum())


# ---------------------------------------------------------------------------
# Construction completion
# ---------------------------------------------------------------------------

def _complete_construction(state: EconomicState, config: SimConfig) -> None:
    """Check construction projects; complete any that are finished."""
    remaining = []
    new_buildings = []

    for project in state.construction_projects:
        project.months_remaining -= 1

        if project.months_remaining <= 0 and project.funded:
            # Complete: create the building
            bt_id = project.completion_effect.get("building_type_id")
            if bt_id is not None and bt_id in BUILDING_TYPE_BY_ID:
                bt = BUILDING_TYPE_BY_ID[bt_id]
                owner = project.completion_effect.get("owner", -1)
                new_buildings.append((bt_id, project.lga_id, owner, bt.base_throughput))
                logger.info(
                    "Construction complete: %s in LGA %d",
                    bt.display_name, project.lga_id,
                )
        else:
            remaining.append(project)

    state.construction_projects = remaining

    # Add new buildings to arrays
    if new_buildings:
        _add_buildings(state, new_buildings)


def _add_buildings(
    state: EconomicState,
    new_buildings: list[tuple[int, int, int, float]],
) -> None:
    """Append new buildings to the structure-of-arrays."""
    n_new = len(new_buildings)
    if n_new == 0:
        return

    bt_ids = np.array([b[0] for b in new_buildings], dtype=np.int16)
    lga_ids = np.array([b[1] for b in new_buildings], dtype=np.int16)
    owners = np.array([b[2] for b in new_buildings], dtype=np.int8)
    throughputs = np.array([b[3] for b in new_buildings], dtype=np.float64)

    S = state.building_employees.shape[1] if state.building_employees is not None else 4

    state.building_type_ids = np.concatenate([state.building_type_ids, bt_ids])
    state.building_lga_ids = np.concatenate([state.building_lga_ids, lga_ids])
    state.building_owners = np.concatenate([state.building_owners, owners])
    state.building_throughput = np.concatenate([state.building_throughput, throughputs])
    state.building_tech_level = np.concatenate([
        state.building_tech_level, np.full(n_new, 0.7, dtype=np.float64),
    ])
    state.building_employees = np.concatenate([
        state.building_employees, np.zeros((n_new, S), dtype=np.float64),
    ])
    state.building_operational = np.concatenate([
        state.building_operational, np.ones(n_new, dtype=bool),
    ])
    state.building_age = np.concatenate([
        state.building_age, np.zeros(n_new, dtype=np.int32),
    ])
    state.n_buildings += n_new


# ---------------------------------------------------------------------------
# Zaibatsu investment
# ---------------------------------------------------------------------------

def _zaibatsu_investment(state: EconomicState, config: SimConfig) -> None:
    """
    Zaibatsu invest in new buildings based on profitability signals.

    Each zaibatsu checks demand vs supply for their affiliated commodities
    and starts construction if there's sustained unfilled demand.
    """
    if state.unfilled_buy is None or state.prices is None:
        return

    N = config.N_LGAS

    for z_id, z in ZAIBATSU_BY_ID.items():
        # Find building types this zaibatsu builds
        affiliated_types = [
            bt for bt in BUILDING_TYPES if bt.zaibatsu_affinity == z_id
        ]
        if not affiliated_types:
            continue

        for bt in affiliated_types:
            c_id = bt.output_commodity

            # Check if there's sustained unfilled demand for this commodity
            unfilled = state.unfilled_buy[:, c_id]  # (N,)
            total_unfilled = unfilled.sum()

            # Investment threshold: unfilled demand > 5% of prices suggest opportunity
            if total_unfilled < bt.base_throughput * 2:
                continue

            # Find best LGA for investment: high unfilled demand + good infrastructure
            score = unfilled.copy()

            # Penalize areas with poor infrastructure
            if bt.requires_power and state.infra_power_reliability is not None:
                power_ok = state.infra_power_reliability >= bt.min_power_reliability
                score *= power_ok.astype(np.float64)

            # Penalize al-Shahid controlled areas
            if state.alsahid_control is not None:
                score *= (1.0 - state.alsahid_control)

            # Cap at 1 new project per zaibatsu per building type per month
            best_lga = int(np.argmax(score))
            if score[best_lga] < bt.base_throughput:
                continue

            # Check if already building same type in this LGA
            already_building = any(
                p.completion_effect.get("building_type_id") == bt.id
                and p.lga_id == best_lga
                for p in state.construction_projects
            )
            if already_building:
                continue

            # Start construction
            project = ConstructionProject(
                project_type="zaibatsu_expansion",
                lga_id=best_lga,
                commodity_id=c_id,
                months_remaining=bt.construction_months,
                monthly_cost_naira=bt.construction_cost_naira / bt.construction_months,
                monthly_labor_demand={0: 20, 1: 5},
                completion_effect={
                    "building_type_id": bt.id,
                    "owner": z_id,
                },
                funded=True,
            )
            state.construction_projects.append(project)
            logger.info(
                "Zaibatsu %s starting %s in LGA %d (%d months)",
                z.name, bt.display_name, best_lga, bt.construction_months,
            )


# ---------------------------------------------------------------------------
# Government investment
# ---------------------------------------------------------------------------

# Building types the government invests in (IDs for power, food processing, housing)
_GOV_INFRASTRUCTURE_BT_IDS = [20, 18, 34]  # power_plant, food_processor, housing_developer


def _government_investment(state: EconomicState, config: SimConfig) -> None:
    """
    Government invests in infrastructure buildings in underserved areas.

    Priorities:
    1. Power plants in LGAs with low power reliability
    2. Food processing in LGAs with high food prices
    3. Housing in LGAs with high population and few housing buildings

    Funded by government budget (budget_released). Limited to 2 projects/month.
    """
    if state.budget_released is None or state.prices is None:
        return

    N = config.N_LGAS
    bt_ids = state.building_type_ids.astype(np.intp) if state.building_type_ids is not None else np.array([], dtype=np.intp)

    # Available government infrastructure budget (10% of released budget)
    total_released = state.budget_released.sum() if state.budget_released is not None else 0
    infra_budget = total_released * 0.10
    if infra_budget < 1e9:  # minimum 1 billion naira
        return

    projects_started = 0
    max_projects = 2  # cap per month

    # 1. Power plants in low-reliability areas
    if state.infra_power_reliability is not None and projects_started < max_projects:
        bt = BUILDING_TYPE_BY_ID[20]  # power_plant
        low_power = state.infra_power_reliability < 0.4
        # Count existing power plants per LGA
        power_plants = np.zeros(N, dtype=np.int32)
        if len(bt_ids) > 0:
            pp_mask = state.building_type_ids == 20
            if pp_mask.any():
                pp_lgas = state.building_lga_ids[pp_mask].astype(np.intp)
                np.add.at(power_plants, pp_lgas, 1)

        # Score: low power + population - existing plants
        score = np.where(low_power, 1.0, 0.0)
        if state.population is not None:
            score *= state.population / np.maximum(state.population.max(), 1.0)
        score -= power_plants * 0.5
        score = np.maximum(score, 0.0)

        # Penalize al-Shahid areas
        if state.alsahid_control is not None:
            score *= (1.0 - state.alsahid_control * 0.8)

        best_lga = int(np.argmax(score))
        if score[best_lga] > 0.1:
            already = any(
                p.completion_effect.get("building_type_id") == 20 and p.lga_id == best_lga
                for p in state.construction_projects
            )
            if not already:
                project = ConstructionProject(
                    project_type="government_infrastructure",
                    lga_id=best_lga,
                    commodity_id=bt.output_commodity,
                    months_remaining=bt.construction_months,
                    monthly_cost_naira=bt.construction_cost_naira / bt.construction_months,
                    monthly_labor_demand={0: 30, 1: 10},
                    completion_effect={"building_type_id": 20, "owner": -1},
                    funded=True,
                )
                state.construction_projects.append(project)
                projects_started += 1
                logger.info(
                    "Government starting Power Plant in LGA %d (%d months)",
                    best_lga, bt.construction_months,
                )

    # 2. Food processing in high food price areas
    if projects_started < max_projects:
        bt = BUILDING_TYPE_BY_ID[18]  # food_processor
        food_ids = [6, 7, 8, 13]
        mean_food = state.prices[:, food_ids].mean(axis=1)
        median_food = np.median(mean_food)

        high_price = mean_food > median_food * 1.5
        score = np.where(high_price, mean_food / np.maximum(median_food, 1.0), 0.0)

        if state.population is not None:
            score *= state.population / np.maximum(state.population.max(), 1.0)

        if state.alsahid_control is not None:
            score *= (1.0 - state.alsahid_control * 0.8)

        best_lga = int(np.argmax(score))
        if score[best_lga] > 0.1:
            already = any(
                p.completion_effect.get("building_type_id") == 18 and p.lga_id == best_lga
                for p in state.construction_projects
            )
            if not already:
                project = ConstructionProject(
                    project_type="government_infrastructure",
                    lga_id=best_lga,
                    commodity_id=bt.output_commodity,
                    months_remaining=bt.construction_months,
                    monthly_cost_naira=bt.construction_cost_naira / bt.construction_months,
                    monthly_labor_demand={0: 15, 1: 5},
                    completion_effect={"building_type_id": 18, "owner": -1},
                    funded=True,
                )
                state.construction_projects.append(project)
                projects_started += 1
                logger.info(
                    "Government starting Food Processor in LGA %d (%d months)",
                    best_lga, bt.construction_months,
                )
