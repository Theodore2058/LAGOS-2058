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


def is_volatile_momentum(state: CampaignState, party_name: str) -> bool:
    """
    Check if a party has volatile momentum (direction changes frequently).

    Volatile = at least 3 direction changes in last 4 turns.
    """
    history = state._momentum_history.get(party_name, [])
    if len(history) < 3:
        return False
    recent = history[-4:] if len(history) >= 4 else history
    changes = sum(1 for i in range(1, len(recent)) if recent[i] != recent[i - 1])
    return changes >= 2


def _apply_momentum_valence(
    modifiers: CampaignModifiers,
    state: CampaignState,
) -> None:
    """
    Convert momentum counter into national valence modifier.

    Rising 1/2/3 turns: +0.02/+0.04/+0.06
    Falling 1/2/3 turns: -0.02/-0.04/-0.06
    Volatile: no valence effect (media penalty handled in resolve_media)
    Stable: no effect
    """
    if modifiers.valence is None:
        return
    for party_name in state.party_names:
        turns = state.momentum.get(party_name, 0)
        direction = state.momentum_direction.get(party_name, "")

        # Volatile momentum: no valence bonus/penalty
        if is_volatile_momentum(state, party_name):
            continue

        if turns <= 0 or direction == "stable":
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

    Exposure accumulates from ethnic_mobilization (+0.8), patronage (+0.3*scale),
    business_elite fundraising (+1.5), and successful media (+0.2).
    Above threshold 1.0, parties suffer a national valence penalty proportional
    to excess exposure: -0.04 per point above threshold, capped at -0.20.
    """
    if modifiers.valence is None:
        return
    EXPOSURE_THRESHOLD = 1.0
    PENALTY_PER_POINT = 0.04
    MAX_PENALTY = 0.20
    for party_name in state.party_names:
        exp = state.exposure.get(party_name, 0.0)
        if exp > EXPOSURE_THRESHOLD:
            excess = exp - EXPOSURE_THRESHOLD
            penalty = min(excess * PENALTY_PER_POINT, MAX_PENALTY)
            party_idx = state.party_names.index(party_name)
            modifiers.valence[:, party_idx] -= penalty


# ---------------------------------------------------------------------------
# Scandal system
# ---------------------------------------------------------------------------

# Probability of scandal triggering at each exposure tier, per turn
SCANDAL_PROBABILITY_TABLE: dict[tuple[float, float], float] = {
    (0.0, 2.0): 0.0,
    (2.0, 3.0): 0.05,
    (3.0, 4.0): 0.15,
    (4.0, 6.0): 0.30,
    (6.0, 9.0): 0.50,
    (9.0, float("inf")): 0.75,
}

SCANDAL_VALENCE_PENALTY = 0.12       # National valence hit
SCANDAL_PC_DAMAGE = 3                # PC lost to damage control
SCANDAL_COHESION_HIT = 1.0           # Cohesion lost


def get_scandal_probability(exposure: float) -> float:
    """Return the per-turn scandal probability for a given exposure level."""
    for (lo, hi), prob in SCANDAL_PROBABILITY_TABLE.items():
        if lo <= exposure < hi:
            return prob
    return 0.0


def roll_scandals(
    state: CampaignState,
    rng: np.random.Generator,
) -> list[dict]:
    """
    Roll for scandal triggers based on each party's cumulative exposure.

    A triggered scandal causes:
    - Immediate national valence penalty (applied via scandal_history)
    - PC damage (deducted from balance)
    - Exposure halved (floor(exposure / 2))
    - Cohesion hit (-1)

    Returns list of scandal event dicts for logging.
    """
    scandals: list[dict] = []
    for party_name in state.party_names:
        exp = state.exposure.get(party_name, 0.0)
        prob = get_scandal_probability(exp)
        if prob <= 0.0:
            continue
        if rng.random() < prob:
            scandal = {
                "party": party_name,
                "turn": state.turn,
                "exposure_at_trigger": exp,
                "valence_penalty": SCANDAL_VALENCE_PENALTY,
                "pc_damage": SCANDAL_PC_DAMAGE,
            }
            scandals.append(scandal)
            state.scandal_history.append(scandal)

            # Apply consequences
            # Exposure halved
            state.exposure[party_name] = exp / 2.0

            # PC damage
            old_pc = state.political_capital.get(party_name, 0.0)
            state.political_capital[party_name] = max(0.0, old_pc - SCANDAL_PC_DAMAGE)

            # Cohesion hit
            old_coh = state.cohesion.get(party_name, 10.0)
            state.cohesion[party_name] = max(0.0, old_coh - SCANDAL_COHESION_HIT)

            # Valence penalty applied via effect
            effect = ActiveEffect(
                source_party=party_name,
                source_action="scandal",
                source_turn=state.turn,
                channel="valence",
                target_lgas=None,
                target_dimensions=None,
                target_party=party_name,
                magnitude=-SCANDAL_VALENCE_PENALTY,
                effect_key=f"{party_name}:valence:{party_name}::scandal:{state.turn}",
            )
            state.apply_effect(effect)

    return scandals


def apply_exposure_decay(state: CampaignState) -> None:
    """
    Decay exposure for parties that haven't accumulated new exposure recently.

    After 3 consecutive turns with no new exposure, exposure decays by 1/turn.
    """
    for party_name in state.party_names:
        last_turn = state._last_exposure_turn.get(party_name, 0)
        turns_clean = state.turn - last_turn
        if turns_clean >= 3:
            exp = state.exposure.get(party_name, 0.0)
            if exp > 0:
                state.exposure[party_name] = max(0.0, exp - 1.0)


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
