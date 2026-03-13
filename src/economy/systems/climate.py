"""
Climate / Weather System — seasonal rainfall, droughts, floods, desertification.

Runs once per structural tick (monthly). Determines rainfall modifiers that
feed into agricultural production, triggers disaster events, and advances
long-term desertification in the Sahel belt.
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np

from src.economy.core.types import (
    ClimateMutations,
    DisasterEvent,
    EconomicState,
    SimConfig,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config constants
# ---------------------------------------------------------------------------

RAINY_SEASON_START_MONTH: int = 4
RAINY_SEASON_END_MONTH: int = 10

DROUGHT_PROBABILITY: float = 0.15
FLOOD_PROBABILITY: float = 0.10

DESERTIFICATION_ANNUAL_RATE: float = 0.036
RAINFALL_VARIANCE: float = 0.20

# Derived
_DESERTIFICATION_MONTHLY_RATE: float = DESERTIFICATION_ANNUAL_RATE / 12.0

# Rainfall baseline by season
_RAINY_SEASON_BASELINE: float = 1.25
_DRY_SEASON_BASELINE: float = 0.60

# Drought / flood severity
_DROUGHT_RAINFALL_FACTOR: float = 0.30   # rainfall drops to 30% of baseline
_FLOOD_INVENTORY_DAMAGE: float = 0.08    # 8% inventory loss in affected LGAs
_FLOOD_INFRA_DAMAGE: float = 0.03        # 3% infrastructure quality loss

# Farmland is index 0 in land_area (774, 4)
_FARMLAND_IDX: int = 0


# ---------------------------------------------------------------------------
# Main tick
# ---------------------------------------------------------------------------

def tick_climate(state: EconomicState, config: SimConfig) -> ClimateMutations:
    """
    Execute one climate tick (monthly).

    Returns a ClimateMutations with the new rainfall modifier, season flag,
    any disaster events, and per-LGA desertification deltas.
    """
    N = config.N_LGAS
    rng = state.rng

    # --- Advance month (1-indexed, wraps 12 -> 1) ---
    month = (state.current_month_of_year % 12) + 1

    # --- Determine season ---
    is_rainy = RAINY_SEASON_START_MONTH <= month <= RAINY_SEASON_END_MONTH

    # --- Baseline rainfall ---
    baseline = _RAINY_SEASON_BASELINE if is_rainy else _DRY_SEASON_BASELINE

    # --- Random variation around baseline ---
    variation = rng.normal(loc=0.0, scale=RAINFALL_VARIANCE)
    rainfall_modifier = baseline + variation
    rainfall_modifier = max(rainfall_modifier, 0.05)  # floor: never truly zero

    # --- Disaster events ---
    disaster_events: List[DisasterEvent] = []

    # Drought check (dry season only)
    if not is_rainy and rng.random() < DROUGHT_PROBABILITY:
        rainfall_modifier *= _DROUGHT_RAINFALL_FACTOR

        # Drought affects northern / Sahel LGAs (those with existing
        # desertification loss > 0) plus a random sample of other dry-belt LGAs.
        sahel_mask = _sahel_mask(state, N)
        affected = np.flatnonzero(sahel_mask).tolist()

        if affected:
            severity = 1.0 - rainfall_modifier  # higher when rainfall is lower
            disaster_events.append(DisasterEvent(
                disaster_type="drought",
                affected_lgas=affected,
                severity=float(np.clip(severity, 0.0, 1.0)),
                duration_months=rng.integers(2, 5),  # 2-4 months
                effects={
                    "rainfall_modifier": float(rainfall_modifier),
                    "agricultural_output_penalty": 0.40,
                },
            ))
            logger.info(
                "Drought triggered in month %d affecting %d LGAs (severity %.2f)",
                month, len(affected), severity,
            )

    # Flood check (rainy season only)
    if is_rainy and rng.random() < FLOOD_PROBABILITY:
        # Floods hit a random subset of LGAs (10-25% of total)
        n_affected = rng.integers(N // 10, N // 4 + 1)
        affected = rng.choice(N, size=int(n_affected), replace=False).tolist()

        severity = min(1.0, rainfall_modifier / _RAINY_SEASON_BASELINE)
        disaster_events.append(DisasterEvent(
            disaster_type="flood",
            affected_lgas=affected,
            severity=float(np.clip(severity, 0.0, 1.0)),
            duration_months=1,
            effects={
                "inventory_damage_fraction": _FLOOD_INVENTORY_DAMAGE,
                "infra_damage_fraction": _FLOOD_INFRA_DAMAGE,
            },
        ))
        logger.info(
            "Flood triggered in month %d affecting %d LGAs (severity %.2f)",
            month, len(affected), severity,
        )

    # --- Desertification (Sahel belt only) ---
    desertification_delta = np.zeros(N, dtype=np.float64)
    sahel_mask = _sahel_mask(state, N)

    if np.any(sahel_mask) and state.land_area is not None:
        farmland = state.land_area[sahel_mask, _FARMLAND_IDX]
        loss = farmland * _DESERTIFICATION_MONTHLY_RATE
        desertification_delta[sahel_mask] = loss

    return ClimateMutations(
        rainfall_modifier_new=float(rainfall_modifier),
        is_rainy_season_new=is_rainy,
        disaster_events=disaster_events,
        desertification_delta=desertification_delta,
    )


# ---------------------------------------------------------------------------
# Apply mutations back to state
# ---------------------------------------------------------------------------

def apply_climate_mutations(state: EconomicState, mutations: ClimateMutations) -> None:
    """Write climate mutations back into the economic state."""

    # --- Season and rainfall ---
    state.current_month_of_year = (state.current_month_of_year % 12) + 1
    state.is_rainy_season = mutations.is_rainy_season_new
    state.rainfall_modifier = mutations.rainfall_modifier_new

    # --- Desertification: reduce farmland, accumulate loss tracker ---
    if state.land_area is not None and mutations.desertification_delta is not None:
        delta = mutations.desertification_delta
        state.land_area[:, _FARMLAND_IDX] -= delta
        # Farmland cannot go negative
        np.clip(state.land_area[:, _FARMLAND_IDX], 0.0, None,
                out=state.land_area[:, _FARMLAND_IDX])

    if state.desertification_loss is not None and mutations.desertification_delta is not None:
        state.desertification_loss += mutations.desertification_delta

    # --- Flood inventory / infra damage ---
    for event in mutations.disaster_events:
        if event.disaster_type == "flood":
            _apply_flood_damage(state, event)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sahel_mask(state: EconomicState, n_lgas: int) -> np.ndarray:
    """
    Return a boolean mask (n_lgas,) identifying Sahel / northern dry-belt LGAs.

    Heuristic: LGAs with any accumulated desertification loss are in the
    Sahel belt (this is seeded from LGA initialization data).
    """
    if state.desertification_loss is not None:
        return state.desertification_loss > 0.0
    return np.zeros(n_lgas, dtype=bool)


def _apply_flood_damage(state: EconomicState, event: DisasterEvent) -> None:
    """Apply inventory and infrastructure damage from a flood event."""
    affected = np.array(event.affected_lgas, dtype=np.intp)
    effects = event.effects

    inv_dmg = effects.get("inventory_damage_fraction", _FLOOD_INVENTORY_DAMAGE)
    infra_dmg = effects.get("infra_damage_fraction", _FLOOD_INFRA_DAMAGE)

    # Inventory loss
    if state.inventories is not None and len(affected) > 0:
        state.inventories[affected] *= (1.0 - inv_dmg)

    # Infrastructure degradation
    if state.infra_road_quality is not None and len(affected) > 0:
        state.infra_road_quality[affected] *= (1.0 - infra_dmg)

    if state.infra_power_reliability is not None and len(affected) > 0:
        state.infra_power_reliability[affected] *= (1.0 - infra_dmg)
