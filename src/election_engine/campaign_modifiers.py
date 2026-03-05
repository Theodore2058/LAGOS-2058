"""
Campaign modifier compiler for the LAGOS-2058 election engine.

Aggregates all active effects in CampaignState into CampaignModifiers
arrays that can be injected into the election engine.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .campaign_state import CampaignModifiers, CampaignState, ActiveEffect


# ---------------------------------------------------------------------------
# Cohesion multiplier
# ---------------------------------------------------------------------------

def cohesion_multiplier(cohesion: float) -> float:
    """Scale campaign effect magnitude by party cohesion (0-10)."""
    if cohesion >= 8:
        return 1.0
    elif cohesion >= 6:
        return 0.7 + 0.3 * (cohesion - 6) / 2
    elif cohesion >= 4:
        return 0.4 + 0.3 * (cohesion - 4) / 2
    elif cohesion >= 2:
        return 0.15 + 0.25 * (cohesion - 2) / 2
    else:
        return 0.15


# ---------------------------------------------------------------------------
# ETO category → modifier channel mapping
# ---------------------------------------------------------------------------

# AZ number → boolean LGA mask (computed lazily)
_az_mask_cache: dict[tuple[int, int], np.ndarray] = {}


def _get_az_mask(az: int, lga_data: pd.DataFrame) -> np.ndarray:
    """Get boolean mask for LGAs in a given Administrative Zone."""
    key = (id(lga_data), az)
    if key not in _az_mask_cache:
        _az_mask_cache[key] = (
            lga_data["Administrative Zone"].values.astype(int) == az
        )
    return _az_mask_cache[key]


def _apply_eto_effects(
    modifiers: CampaignModifiers,
    state: CampaignState,
    lga_data: pd.DataFrame,
) -> None:
    """
    Convert ETO scores into modifier arrays.

    ETO categories:
    - Mobilization → ceiling_boost in ETO's AZ
    - Elite → valence bonus in ETO's AZ
    - Economic → awareness boost in ETO's AZ
    - Legitimacy → tau_modifier decrease in ETO's AZ
    """
    for (party_name, eto_cat, az), score in state.eto_scores.items():
        if score <= 0:
            continue
        party_idx = state.party_names.index(party_name) if party_name in state.party_names else -1
        if party_idx < 0:
            continue

        az_mask = _get_az_mask(az, lga_data)
        normalized = score / 10.0  # 0-1 scale

        if eto_cat == "mobilization":
            if modifiers.ceiling_boost is not None:
                modifiers.ceiling_boost[az_mask] += 0.10 * normalized
        elif eto_cat == "elite":
            if modifiers.valence is not None:
                modifiers.valence[az_mask, party_idx] += 0.15 * normalized
        elif eto_cat == "economic":
            if modifiers.awareness is not None:
                modifiers.awareness[az_mask, party_idx] += 0.12 * normalized
                np.clip(
                    modifiers.awareness[az_mask, party_idx], 0.60, 1.0,
                    out=modifiers.awareness[az_mask, party_idx],
                )
        elif eto_cat == "legitimacy":
            if modifiers.tau_modifier is not None:
                modifiers.tau_modifier[az_mask] -= 0.15 * normalized


def _apply_momentum_valence(
    modifiers: CampaignModifiers,
    state: CampaignState,
) -> None:
    """
    Convert momentum counter into national valence modifier.

    Rising 1/2/3 turns: +0.02/+0.04/+0.06
    Falling 1/2/3 turns: -0.02/-0.04/-0.06
    """
    if modifiers.valence is None:
        return
    for party_name in state.party_names:
        turns = state.momentum.get(party_name, 0)
        direction = state.momentum_direction.get(party_name, "")
        if turns <= 0:
            continue
        capped = min(turns, 3)
        bonus = 0.02 * capped
        if direction == "falling":
            bonus = -bonus
        party_idx = state.party_names.index(party_name)
        modifiers.valence[:, party_idx] += bonus


# ---------------------------------------------------------------------------
# Main compiler
# ---------------------------------------------------------------------------

def compile_modifiers(
    state: CampaignState,
    lga_data: pd.DataFrame,
) -> CampaignModifiers:
    """
    Aggregate all active effects into modifier arrays for the engine.

    Awareness comes directly from state.awareness (monotonically accumulated).
    Salience, valence, ceiling, tau are summed from active effects.
    ETO contributions and momentum valence are added here.
    """
    modifiers = CampaignModifiers.zeros(state.n_lga, state.n_parties)

    # Awareness: directly from accumulated state
    if state.awareness is not None:
        modifiers.awareness = state.awareness.copy()

    # Aggregate effects by channel
    for effect in state.effects.values():
        if effect.channel == "salience":
            _apply_salience_effect(modifiers, effect, state)
        elif effect.channel == "valence":
            _apply_valence_effect(modifiers, effect, state)
        elif effect.channel == "ceiling":
            _apply_ceiling_effect(modifiers, effect, state)
        elif effect.channel == "tau":
            _apply_tau_effect(modifiers, effect, state)

    # ETO contributions
    _apply_eto_effects(modifiers, state, lga_data)

    # Momentum → valence
    _apply_momentum_valence(modifiers, state)

    # Exposure → valence penalty (patronage, ethnic mobilization accumulate risk)
    _apply_exposure_penalty(modifiers, state)

    return modifiers


def _apply_exposure_penalty(
    modifiers: CampaignModifiers,
    state: CampaignState,
) -> None:
    """
    Apply valence penalty for accumulated exposure from risky actions.

    Exposure accumulates from ethnic_mobilization (+0.5) and patronage (+0.3).
    Above threshold 1.5, parties suffer a national valence penalty proportional
    to excess exposure: -0.03 per point above threshold, capped at -0.15.
    """
    if modifiers.valence is None:
        return
    EXPOSURE_THRESHOLD = 1.5
    PENALTY_PER_POINT = 0.03
    MAX_PENALTY = 0.15
    for party_name in state.party_names:
        exp = state.exposure.get(party_name, 0.0)
        if exp > EXPOSURE_THRESHOLD:
            excess = exp - EXPOSURE_THRESHOLD
            penalty = min(excess * PENALTY_PER_POINT, MAX_PENALTY)
            party_idx = state.party_names.index(party_name)
            modifiers.valence[:, party_idx] -= penalty


def concentration_penalty(n_turns: int) -> float:
    """Diminishing returns from targeting the same region repeatedly.

    Returns a multiplier in (0, 1]. No penalty for first turn (n=0).
    Formula: 1 / (1 + 0.15 * n)
    """
    return 1.0 / (1.0 + 0.15 * max(n_turns, 0))


def _apply_salience_effect(
    modifiers: CampaignModifiers,
    effect: ActiveEffect,
    state: CampaignState,
) -> None:
    """Apply a salience effect to the modifier arrays."""
    if modifiers.salience_shift is None or effect.target_dimensions is None:
        return
    party_name = effect.source_party
    coh = cohesion_multiplier(state.cohesion.get(party_name, 10.0))
    conc = concentration_penalty(state.concentration.get(party_name, 0))
    mag = effect.magnitude * coh * conc

    for dim_idx in effect.target_dimensions:
        if effect.target_lgas is not None:
            modifiers.salience_shift[effect.target_lgas, dim_idx] += mag
        else:
            modifiers.salience_shift[:, dim_idx] += mag


def _apply_valence_effect(
    modifiers: CampaignModifiers,
    effect: ActiveEffect,
    state: CampaignState,
) -> None:
    """Apply a valence effect to the modifier arrays."""
    if modifiers.valence is None or effect.target_party is None:
        return
    if effect.target_party not in state.party_names:
        return
    party_idx = state.party_names.index(effect.target_party)
    party_name = effect.source_party
    coh = cohesion_multiplier(state.cohesion.get(party_name, 10.0))
    conc = concentration_penalty(state.concentration.get(party_name, 0))
    mag = effect.magnitude * coh * conc

    if effect.target_lgas is not None:
        modifiers.valence[effect.target_lgas, party_idx] += mag
    else:
        modifiers.valence[:, party_idx] += mag


def _apply_ceiling_effect(
    modifiers: CampaignModifiers,
    effect: ActiveEffect,
    state: CampaignState,
) -> None:
    """Apply a ceiling effect to the modifier arrays."""
    if modifiers.ceiling_boost is None:
        return
    party_name = effect.source_party
    coh = cohesion_multiplier(state.cohesion.get(party_name, 10.0))
    conc = concentration_penalty(state.concentration.get(party_name, 0))
    mag = effect.magnitude * coh * conc

    if effect.target_lgas is not None:
        modifiers.ceiling_boost[effect.target_lgas] += mag
    else:
        modifiers.ceiling_boost += mag


def _apply_tau_effect(
    modifiers: CampaignModifiers,
    effect: ActiveEffect,
    state: CampaignState,
) -> None:
    """Apply a tau modifier effect."""
    if modifiers.tau_modifier is None:
        return
    party_name = effect.source_party
    coh = cohesion_multiplier(state.cohesion.get(party_name, 10.0))
    conc = concentration_penalty(state.concentration.get(party_name, 0))
    mag = effect.magnitude * coh * conc

    if effect.target_lgas is not None:
        modifiers.tau_modifier[effect.target_lgas] += mag
    else:
        modifiers.tau_modifier += mag
