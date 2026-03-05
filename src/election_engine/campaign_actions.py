"""
Campaign action resolution for the LAGOS-2058 election engine.

Each action type has a resolve function that:
1. Produces effects in one or more channels (salience, valence, ceiling, tau)
2. Raises awareness for the acting party as a side effect

Actions are specified via ActionSpec and resolved through resolve_action().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from .campaign_state import CampaignState, ActiveEffect
from .campaign_modifiers import cohesion_multiplier


# ---------------------------------------------------------------------------
# Political Capital costs per action type
# ---------------------------------------------------------------------------

PC_COSTS: dict[str, int] = {
    "rally": 2,                  # Core campaign activity
    "advertising": 2,            # Base cost; budget param > 1.5 adds +1, > 2.0 adds +2
    "manifesto": 3,              # Major national event
    "ground_game": 3,            # Resource-intensive field operations
    "endorsement": 2,            # Relationship-based
    "ethnic_mobilization": 3,    # High-impact identity play
    "patronage": 4,              # Expensive, generates exposure risk
    "opposition_research": 2,    # Strategic but narrow
    "media": 1,                  # Cheap but volatile
    "eto_engagement": 3,         # Building institutional support
    "crisis_response": 2,        # Reactive situational cost
    "fundraising": 0,            # Free — generates PC
    "poll": 1,                   # Cheap intelligence
    "pledge": 0,                 # Free to promise
}

# PC system constants
PC_INCOME_PER_TURN = 7           # Unconditional income at start of each turn
PC_HOARDING_CAP = 18             # Hard cap: excess above this lost before income
PC_FUNDRAISING_YIELD = 3         # Base PC from a fundraising action
PC_ETO_DIVIDEND_THRESHOLD = 8    # Economic ETO score required for dividend
PC_ETO_DIVIDEND_AMOUNT = 1       # PC per qualifying Economic ETO
PC_ETO_DIVIDEND_CAP = 2          # Max ETO dividend per turn


def compute_action_cost(action_type: str, params: dict) -> int:
    """Compute the PC cost for an action, including param-based surcharges."""
    base = PC_COSTS.get(action_type, 2)
    if action_type == "advertising":
        budget = params.get("budget", 1.0)
        if budget > 2.0:
            base += 2
        elif budget > 1.5:
            base += 1
    elif action_type == "ground_game":
        intensity = params.get("intensity", 1.0)
        if intensity > 1.5:
            base += 2
        elif intensity > 1.0:
            base += 1
    elif action_type == "rally":
        gm_score = params.get("gm_score", 5.0)
        if gm_score >= 9.0:
            base += 1
    elif action_type == "patronage":
        scale = params.get("scale", 1.0)
        if scale > 1.5:
            base += 2
        elif scale > 1.0:
            base += 1
    elif action_type == "eto_engagement":
        score_change = params.get("score_change", 1.0)
        if score_change > 3.0:
            base += 1
    return base


# ---------------------------------------------------------------------------
# ActionSpec dataclass
# ---------------------------------------------------------------------------

@dataclass
class ActionSpec:
    """
    Specification for one campaign action.

    Parameters
    ----------
    party : str
        Party name (must match CampaignState.party_names).
    action_type : str
        One of: "rally", "advertising", "manifesto", "ground_game",
        "endorsement", "ethnic_mobilization", "patronage",
        "opposition_research", "media", "eto_engagement",
        "crisis_response", "fundraising", "poll", "pledge".
    target_lgas : np.ndarray | None
        Boolean mask (n_lga,). None = national.
    language : str
        Campaign language. Determines which salience dimensions shift.
    params : dict
        Action-specific parameters.
    """
    party: str
    action_type: str
    target_lgas: np.ndarray | None = None
    language: str = "english"
    params: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Language → Issue Dimension Profiles
# ---------------------------------------------------------------------------

LANGUAGE_ISSUE_PROFILES: dict[str, dict[int, float]] = {
    "english": {
        3: 0.15,   # chinese_relations
        4: 0.15,   # bic_reform
        7: 0.12,   # constitutional_structure
        11: 0.10,  # labor_automation
        14: 0.08,  # language_policy
        19: 0.08,  # taxation
        21: 0.08,  # biological_enhancement
        22: 0.08,  # trade_policy
        24: 0.08,  # media_freedom
        26: 0.08,  # pada_status
    },
    "hausa": {
        0: 0.25,   # sharia_jurisdiction
        5: 0.15,   # fertility_policy
        10: 0.12,  # education
        15: 0.12,  # traditional_authority
        14: 0.10,  # womens_rights
        13: 0.08,  # immigration
        27: 0.08,  # az_restructuring
        17: 0.05,  # land_tenure
        8: 0.05,   # resource_revenue
    },
    "yoruba": {
        1: 0.20,   # fiscal_autonomy
        8: 0.15,   # resource_revenue
        27: 0.12,  # az_restructuring
        10: 0.10,  # education
        26: 0.10,  # pada_status
        17: 0.08,  # land_tenure
        19: 0.08,  # taxation
        16: 0.05,  # infrastructure
        9: 0.05,   # housing
        15: 0.07,  # traditional_authority
    },
    "igbo": {
        1: 0.20,   # fiscal_autonomy
        27: 0.15,  # az_restructuring
        8: 0.12,   # resource_revenue
        22: 0.10,  # trade_policy
        19: 0.10,  # taxation
        4: 0.08,   # bic_reform
        16: 0.08,  # infrastructure
        10: 0.07,  # education
        11: 0.05,  # labor_automation
        5: 0.05,   # ethnic_quotas
    },
    "arabic": {
        0: 0.35,   # sharia_jurisdiction
        10: 0.15,  # education
        15: 0.12,  # traditional_authority
        14: 0.10,  # womens_rights
        5: 0.08,   # fertility_policy
        13: 0.05,  # immigration
        16: 0.05,  # infrastructure
        12: 0.05,  # military_role
        17: 0.05,  # land_tenure
    },
    "pidgin": {
        9: 0.15,   # housing
        19: 0.12,  # taxation
        11: 0.12,  # labor_automation
        25: 0.10,  # healthcare
        16: 0.10,  # infrastructure
        26: 0.10,  # pada_status
        4: 0.08,   # bic_reform
        20: 0.08,  # agricultural_policy
        13: 0.08,  # immigration
        17: 0.07,  # land_tenure
    },
    "mandarin": {
        3: 0.25,   # chinese_relations
        22: 0.15,  # trade_policy
        11: 0.12,  # labor_automation
        21: 0.10,  # biological_enhancement
        16: 0.10,  # infrastructure
        10: 0.08,  # education
        27: 0.05,  # energy_policy
        23: 0.05,  # environmental_regulation
        14: 0.05,  # language_policy
        9: 0.05,   # housing
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _media_factor(lga_data: pd.DataFrame) -> np.ndarray:
    """Compute media infrastructure factor (n_lga,) in [0, ~0.85]."""
    n = len(lga_data)

    def _col(name, default=0.0):
        if name in lga_data.columns:
            return pd.to_numeric(lga_data[name], errors="coerce").fillna(default).values.astype(float)
        return np.full(n, default)

    urban = _col("Urban Pct", 30.0) / 100.0
    internet = _col("Internet Access Pct", 50.0) / 100.0
    mobile = _col("Mobile Phone Penetration Pct", 50.0) / 100.0
    literacy = _col("Adult Literacy Rate Pct", 50.0) / 100.0
    return 0.3 * urban + 0.25 * internet + 0.25 * mobile + 0.2 * literacy


def _language_dims(language: str) -> tuple[list[int], list[float]]:
    """Get dimension indices and weights from language profile."""
    profile = LANGUAGE_ISSUE_PROFILES.get(language, LANGUAGE_ISSUE_PROFILES["english"])
    dims = list(profile.keys())
    weights = list(profile.values())
    return dims, weights


def _effect_key(party: str, channel: str, target: str = "",
                region: str = "", dim: str = "") -> str:
    """Build a unique effect key for EMA overwrite logic."""
    return f"{party}:{channel}:{target}:{region}:{dim}"


# ---------------------------------------------------------------------------
# Action resolvers
# ---------------------------------------------------------------------------

def resolve_rally(action: ActionSpec, state: CampaignState,
                  lga_data: pd.DataFrame, parties: list) -> None:
    """
    Rally: raises salience on language-profiled dimensions in target LGAs
    and raises awareness for the acting party.
    """
    dims, weights = _language_dims(action.language)
    gm_score = action.params.get("gm_score", 5.0) / 10.0
    base_magnitude = 0.03 * gm_score
    party_idx = state.party_names.index(action.party)

    for dim, w in zip(dims, weights):
        effect = ActiveEffect(
            source_party=action.party,
            source_action="rally",
            source_turn=state.turn,
            channel="salience",
            target_lgas=action.target_lgas,
            target_dimensions=[dim],
            target_party=None,
            magnitude=base_magnitude * w,
            effect_key=_effect_key(action.party, "salience", "", "rally", str(dim)),
        )
        state.apply_effect(effect)

    # Awareness boost: scales with population density in target LGAs
    awareness_boost = 0.06 * gm_score
    if action.target_lgas is not None:
        n = len(lga_data)
        density = _col_safe(lga_data, "Population Density per km2", 200.0, n) / 1000.0
        boost = awareness_boost * np.clip(density, 0.1, 1.0)
        state.raise_awareness(party_idx, action.target_lgas, boost.astype(np.float32))
    else:
        state.raise_awareness(party_idx, None, np.float32(awareness_boost * 0.5))

    # Rallies reduce abstention (tau) — political excitement drives turnout
    tau_mag = -0.04 * gm_score  # negative = less abstention = higher turnout
    tau_effect = ActiveEffect(
        source_party=action.party,
        source_action="rally",
        source_turn=state.turn,
        channel="tau",
        target_lgas=action.target_lgas,
        target_dimensions=None,
        target_party=None,
        magnitude=tau_mag,
        effect_key=_effect_key(action.party, "tau", "", "rally", ""),
    )
    state.apply_effect(tau_effect)


def resolve_advertising(action: ActionSpec, state: CampaignState,
                        lga_data: pd.DataFrame, parties: list) -> None:
    """
    Advertising: raises salience broadly and awareness scaled by medium match.
    """
    dims, weights = _language_dims(action.language)
    medium = action.params.get("medium", "radio")
    budget_scale = action.params.get("budget", 1.0)
    base_magnitude = 0.02 * budget_scale
    party_idx = state.party_names.index(action.party)
    n = len(lga_data)

    for dim, w in zip(dims, weights):
        effect = ActiveEffect(
            source_party=action.party,
            source_action="advertising",
            source_turn=state.turn,
            channel="salience",
            target_lgas=action.target_lgas,
            target_dimensions=[dim],
            target_party=None,
            magnitude=base_magnitude * w,
            effect_key=_effect_key(action.party, "salience", "", "ad", str(dim)),
        )
        state.apply_effect(effect)

    # Awareness: medium-dependent
    mf = _media_factor(lga_data)
    if medium == "radio":
        reach = 0.08 * budget_scale * (1.0 - 0.3 * mf)  # radio better in low-media
    elif medium == "tv":
        reach = 0.08 * budget_scale * mf
    elif medium == "social_media":
        internet = _col_safe(lga_data, "Internet Access Pct", 50.0, n) / 100.0
        reach = 0.10 * budget_scale * internet
    else:
        reach = 0.06 * budget_scale * mf

    state.raise_awareness(party_idx, action.target_lgas, reach.astype(np.float32))

    # Heavy advertising creates general political awareness → slight turnout boost
    if budget_scale >= 1.5:
        tau_mag = -0.02 * budget_scale
        tau_effect = ActiveEffect(
            source_party=action.party,
            source_action="advertising",
            source_turn=state.turn,
            channel="tau",
            target_lgas=action.target_lgas,
            target_dimensions=None,
            target_party=None,
            magnitude=tau_mag,
            effect_key=_effect_key(action.party, "tau", "", "ad", ""),
        )
        state.apply_effect(tau_effect)


def resolve_manifesto(action: ActionSpec, state: CampaignState,
                      lga_data: pd.DataFrame, parties: list) -> None:
    """
    Manifesto: updates Party.positions, raises awareness nationally,
    credibility penalty if sharp reversal.
    """
    party_idx = state.party_names.index(action.party)
    new_positions = action.params.get("positions", None)
    party_obj = parties[party_idx]

    if new_positions is not None:
        new_pos = np.asarray(new_positions, dtype=float)
        np.clip(new_pos, -5.0, 5.0, out=new_pos)

        # Check for credibility penalty (sharp reversal > 3 points)
        old_pos = state.last_positions.get(action.party, party_obj.positions.copy())
        max_shift = float(np.max(np.abs(new_pos - old_pos)))
        if max_shift > 3.0:
            penalty = -0.15 * (max_shift - 3.0) / 2.0
            effect = ActiveEffect(
                source_party=action.party,
                source_action="manifesto_penalty",
                source_turn=state.turn,
                channel="valence",
                target_lgas=None,
                target_dimensions=None,
                target_party=action.party,
                magnitude=penalty,
                effect_key=_effect_key(action.party, "valence", action.party, "", "credibility"),
            )
            state.apply_effect(effect)
            # Cohesion hit
            old_coh = state.cohesion.get(action.party, 10.0)
            coh_penalty = min(3.0, max_shift - 3.0)
            state.cohesion[action.party] = max(0.0, old_coh - coh_penalty)

        state.last_positions[action.party] = new_pos.copy()
        party_obj.positions = new_pos

    # National awareness boost, proportional to media infrastructure
    mf = _media_factor(lga_data)
    awareness_boost = (0.08 + 0.22 * mf).astype(np.float32)  # 0.08-0.30 range
    state.raise_awareness(party_idx, None, awareness_boost)


def resolve_ground_game(action: ActionSpec, state: CampaignState,
                        lga_data: pd.DataFrame, parties: list) -> None:
    """
    Ground Game: raises turnout ceiling in target LGAs and small awareness boost.
    """
    intensity = action.params.get("intensity", 1.0)
    party_idx = state.party_names.index(action.party)

    effect = ActiveEffect(
        source_party=action.party,
        source_action="ground_game",
        source_turn=state.turn,
        channel="ceiling",
        target_lgas=action.target_lgas,
        target_dimensions=None,
        target_party=None,
        magnitude=0.05 * intensity,
        effect_key=_effect_key(action.party, "ceiling", "", "gg", ""),
    )
    state.apply_effect(effect)

    # Small awareness boost from door-to-door
    state.raise_awareness(party_idx, action.target_lgas, np.float32(0.03 * intensity))

    # Ground game is the primary GOTV mechanism — reduces abstention
    tau_mag = -0.06 * intensity  # stronger turnout effect than rallies
    tau_effect = ActiveEffect(
        source_party=action.party,
        source_action="ground_game",
        source_turn=state.turn,
        channel="tau",
        target_lgas=action.target_lgas,
        target_dimensions=None,
        target_party=None,
        magnitude=tau_mag,
        effect_key=_effect_key(action.party, "tau", "", "gg", ""),
    )
    state.apply_effect(tau_effect)


def resolve_endorsement(action: ActionSpec, state: CampaignState,
                        lga_data: pd.DataFrame, parties: list) -> None:
    """
    Endorsement: valence boost + awareness boost in endorser's domain.
    """
    endorser_type = action.params.get("endorser_type", "notable")
    endorser_lgas = action.params.get("endorser_lgas", action.target_lgas)
    party_idx = state.party_names.index(action.party)

    magnitude_map = {
        "traditional_ruler": 0.12,
        "religious_leader": 0.10,
        "celebrity": 0.08,
        "notable": 0.06,
        "eto_leader": 0.10,
    }
    mag = magnitude_map.get(endorser_type, 0.06)

    eff_key = _effect_key(action.party, "valence", action.party, "endorse", endorser_type)
    effect = ActiveEffect(
        source_party=action.party,
        source_action="endorsement",
        source_turn=state.turn,
        channel="valence",
        target_lgas=endorser_lgas,
        target_dimensions=None,
        target_party=action.party,
        magnitude=mag,
        effect_key=eff_key,
    )
    state.apply_effect(effect)

    # Track endorsement for potential withdrawal
    state._endorsements[eff_key] = {
        "endorser_type": endorser_type,
        "source_party": action.party,
        "turn_applied": state.turn,
    }

    # Awareness boost through endorser's network
    state.raise_awareness(party_idx, endorser_lgas, np.float32(0.05))


def resolve_ethnic_mobilization(action: ActionSpec, state: CampaignState,
                                lga_data: pd.DataFrame, parties: list) -> None:
    """
    Ethnic Mobilization: salience shift on identity-correlated dimensions,
    awareness boost among target ethnic group's LGAs.
    """
    target_ethnicity = action.params.get("target_ethnicity", "")
    party_idx = state.party_names.index(action.party)
    n = len(lga_data)

    # Get ethnic percentage for scaling
    eth_col = f"% {target_ethnicity}"
    if eth_col in lga_data.columns:
        eth_pct = lga_data[eth_col].fillna(0).values.astype(float) / 100.0
    else:
        eth_pct = np.zeros(n)

    # Identity-correlated dimensions (ethnic quotas, traditional authority,
    # constitutional structure, az_restructuring)
    identity_dims = [5, 15, 7, 27]
    for dim in identity_dims:
        effect = ActiveEffect(
            source_party=action.party,
            source_action="ethnic_mobilization",
            source_turn=state.turn,
            channel="salience",
            target_lgas=action.target_lgas,
            target_dimensions=[dim],
            target_party=None,
            magnitude=0.04,
            effect_key=_effect_key(action.party, "salience", "", "ethnic", str(dim)),
        )
        state.apply_effect(effect)

    # Awareness boost scaled by ethnic population share
    awareness_boost = (0.08 * eth_pct).astype(np.float32)
    state.raise_awareness(party_idx, action.target_lgas, awareness_boost)

    # Exposure accumulation
    state.exposure[action.party] = state.exposure.get(action.party, 0.0) + 0.5
    state._last_exposure_turn[action.party] = state.turn


def resolve_patronage(action: ActionSpec, state: CampaignState,
                      lga_data: pd.DataFrame, parties: list) -> None:
    """
    Patronage: valence boost in target LGAs, small awareness boost,
    exposure accumulation.
    """
    party_idx = state.party_names.index(action.party)
    scale = action.params.get("scale", 1.0)

    effect = ActiveEffect(
        source_party=action.party,
        source_action="patronage",
        source_turn=state.turn,
        channel="valence",
        target_lgas=action.target_lgas,
        target_dimensions=None,
        target_party=action.party,
        magnitude=0.06 * scale,
        effect_key=_effect_key(action.party, "valence", action.party, "patronage", ""),
    )
    state.apply_effect(effect)

    # Small awareness boost
    state.raise_awareness(party_idx, action.target_lgas, np.float32(0.02 * scale))

    # Patronage networks mobilize voters — turnout boost in target LGAs
    tau_effect = ActiveEffect(
        source_party=action.party,
        source_action="patronage",
        source_turn=state.turn,
        channel="tau",
        target_lgas=action.target_lgas,
        target_dimensions=None,
        target_party=None,
        magnitude=-0.03 * scale,  # negative = less abstention = more turnout
        effect_key=_effect_key(action.party, "tau", "", "patronage", ""),
    )
    state.apply_effect(tau_effect)

    # Exposure — scaled by patronage size
    state.exposure[action.party] = state.exposure.get(action.party, 0.0) + 0.3 * scale
    state._last_exposure_turn[action.party] = state.turn


def resolve_opposition_research(action: ActionSpec, state: CampaignState,
                                lga_data: pd.DataFrame, parties: list) -> None:
    """
    Opposition Research: raises salience on dimensions where TARGET party
    holds unpopular positions; raises OPPONENT awareness (defines your opponent).
    """
    target_party = action.params.get("target_party", "")
    target_dims = action.params.get("target_dimensions", None)

    if not target_party or target_party not in state.party_names:
        return

    target_idx = state.party_names.index(target_party)

    # Raise salience on target dimensions (or auto-detect worst ones)
    if target_dims is None:
        # Default: raise salience broadly
        target_dims = [0, 1, 5, 7, 27]

    for dim in target_dims:
        effect = ActiveEffect(
            source_party=action.party,
            source_action="opposition_research",
            source_turn=state.turn,
            channel="salience",
            target_lgas=action.target_lgas,
            target_dimensions=[dim],
            target_party=None,
            magnitude=0.03,
            effect_key=_effect_key(action.party, "salience", target_party, "oppo", str(dim)),
        )
        state.apply_effect(effect)

    # Negative valence on target party (reputation damage)
    valence_effect = ActiveEffect(
        source_party=action.party,
        source_action="opposition_research",
        source_turn=state.turn,
        channel="valence",
        target_lgas=action.target_lgas,
        target_dimensions=None,
        target_party=target_party,
        magnitude=-0.06,
        effect_key=_effect_key(action.party, "valence", target_party, "oppo", ""),
    )
    state.apply_effect(valence_effect)

    # Raise OPPONENT's awareness (you're introducing voters to their worst positions)
    state.raise_awareness(target_idx, action.target_lgas, np.float32(0.06))


def resolve_media(action: ActionSpec, state: CampaignState,
                  lga_data: pd.DataFrame, parties: list) -> None:
    """
    Media Engagement: broad salience shift (volatile magnitude),
    awareness boost scaled by media infrastructure.
    """
    dims, weights = _language_dims(action.language)
    success = action.params.get("success", 0.5)  # 0-1 scale
    party_idx = state.party_names.index(action.party)

    # Volatile: ×1.5 multiplier on deviation from 0.5 (doc: score deviation from 5)
    # success=0.8 → effective 0.95; success=0.3 → effective 0.2
    magnitude = 0.02 * (2.0 * success - 0.5)  # range: -0.01 to +0.03
    volatility_amplifier = 1.0 + 0.5 * abs(success - 0.5) / 0.5  # 1.0 at center, 1.5 at extremes
    magnitude *= volatility_amplifier

    # Volatile momentum penalizes media effectiveness
    if state._momentum_history.get(action.party):
        recent = state._momentum_history[action.party][-3:]
        if len(recent) >= 3 and len(set(recent)) >= 3:
            # Direction changes frequently → volatile, -25% media effectiveness
            magnitude *= 0.75

    for dim, w in zip(dims, weights):
        effect = ActiveEffect(
            source_party=action.party,
            source_action="media",
            source_turn=state.turn,
            channel="salience",
            target_lgas=None,  # national
            target_dimensions=[dim],
            target_party=None,
            magnitude=magnitude * w,
            effect_key=_effect_key(action.party, "salience", "", "media", str(dim)),
        )
        state.apply_effect(effect)

    # Valence effect: good press helps, bad press hurts
    # success > 0.5 → positive valence, < 0.5 → negative
    valence_mag = 0.06 * (success - 0.5)  # range: -0.03 to +0.03
    valence_mag *= volatility_amplifier
    valence_effect = ActiveEffect(
        source_party=action.party,
        source_action="media",
        source_turn=state.turn,
        channel="valence",
        target_lgas=None,
        target_dimensions=None,
        target_party=action.party,
        magnitude=valence_mag,
        effect_key=_effect_key(action.party, "valence", action.party, "media", ""),
    )
    state.apply_effect(valence_effect)

    # Awareness boost (you're in the news)
    mf = _media_factor(lga_data)
    awareness_boost = (0.04 * success * mf).astype(np.float32)
    state.raise_awareness(party_idx, None, awareness_boost)


def resolve_eto_engagement(action: ActionSpec, state: CampaignState,
                           lga_data: pd.DataFrame, parties: list) -> None:
    """
    ETO Engagement: updates ETO scores in CampaignState.
    Economic ETOs also raise awareness in their AZ.
    """
    eto_category = action.params.get("eto_category", "elite")
    az = action.params.get("az", 1)
    score_change = action.params.get("score_change", 1.0)
    party_idx = state.party_names.index(action.party)

    key = (action.party, eto_category, az)
    old_score = state.eto_scores.get(key, 0.0)
    new_score = np.clip(old_score + score_change, 0.0, 10.0)
    state.eto_scores[key] = new_score

    # Economic ETOs raise awareness in their AZ
    if eto_category == "economic" and score_change > 0:
        n = len(lga_data)
        az_mask = (lga_data["Administrative Zone"].values.astype(int) == az)
        state.raise_awareness(party_idx, az_mask, np.float32(0.03 * score_change))


def resolve_crisis_response(action: ActionSpec, state: CampaignState,
                            lga_data: pd.DataFrame, parties: list) -> None:
    """
    Crisis Response: valence protection + awareness boost.
    """
    effectiveness = action.params.get("effectiveness", 0.5)
    party_idx = state.party_names.index(action.party)

    effect = ActiveEffect(
        source_party=action.party,
        source_action="crisis_response",
        source_turn=state.turn,
        channel="valence",
        target_lgas=action.target_lgas,
        target_dimensions=None,
        target_party=action.party,
        magnitude=0.08 * effectiveness,
        effect_key=_effect_key(action.party, "valence", action.party, "crisis", ""),
    )
    state.apply_effect(effect)

    # Crisis puts you in the news
    state.raise_awareness(party_idx, action.target_lgas, np.float32(0.04 * effectiveness))


def resolve_fundraising(action: ActionSpec, state: CampaignState,
                        lga_data: pd.DataFrame, parties: list) -> None:
    """
    Fundraising: source-dependent PC generation with side effects.

    Sources:
    - business_elite: High yield (4 PC), +1 exposure (donors expect favors)
    - diaspora: Medium yield (3 PC), no side effects
    - grassroots: Low yield (2 PC), small turnout bonus in target region
    - membership: Yield scales with cohesion (1-3 PC), no side effect

    Consecutive fundraising from the same source: -1 PC yield per repeat.
    """
    source = action.params.get("source", "diaspora")
    party = action.party

    # Track consecutive same-source fundraising
    if party not in state._fundraising_history:
        state._fundraising_history[party] = {}
    hist = state._fundraising_history[party]
    consecutive = hist.get(source, 0)

    # Base yields per source
    if source == "business_elite":
        base_yield = 4
        # Side effect: exposure from donor expectations
        state.exposure[party] = state.exposure.get(party, 0.0) + 1.0
        state._last_exposure_turn[party] = state.turn
    elif source == "grassroots":
        base_yield = 2
        # Side effect: small turnout boost in target region
        if action.target_lgas is not None:
            tau_effect = ActiveEffect(
                source_party=party,
                source_action="fundraising_gotv",
                source_turn=state.turn,
                channel="tau",
                target_lgas=action.target_lgas,
                target_dimensions=None,
                target_party=None,
                magnitude=-0.02,
                effect_key=_effect_key(party, "tau", "", "fund_grass", ""),
            )
            state.apply_effect(tau_effect)
    elif source == "membership":
        # Yield scales with cohesion: cohesion 10 = 3 PC, cohesion 5 = 2, cohesion 2 = 1
        coh = state.cohesion.get(party, 10.0)
        base_yield = max(1, min(3, int(coh / 3.5) + 1))
    else:  # diaspora or unspecified
        base_yield = PC_FUNDRAISING_YIELD  # 3 PC

    # Economic ETO multiplier: score 7+ gives 20% bonus
    eto_bonus = 0
    for (p, cat, az), score in state.eto_scores.items():
        if p == party and cat == "economic" and score >= 7.0:
            eto_bonus = 1
            break

    # Consecutive same-source penalty: -1 per repeat
    penalty = min(consecutive, base_yield - 1)  # don't go below 1
    final_yield = max(1, base_yield - penalty + eto_bonus)

    # Apply yield — override the flat PC_FUNDRAISING_YIELD in the campaign loop
    # We store the computed yield so the campaign loop can use it
    state.political_capital[party] = state.political_capital.get(party, 0.0) + final_yield

    # Update consecutive tracking: increment this source, reset others
    for s in hist:
        if s != source:
            hist[s] = 0
    hist[source] = consecutive + 1


def resolve_poll(action: ActionSpec, state: CampaignState,
                 lga_data: pd.DataFrame, parties: list) -> None:
    """
    Poll: generates noisy projected vote shares from previous_shares.

    Noise scales inversely with sample_size param (default 1000).
    Results stored in state.poll_results for caller inspection.
    """
    sample_size = action.params.get("sample_size", 1000)
    noise_level = 1.0 / np.sqrt(max(sample_size, 100))  # ~3% for 1000

    # Use previous shares as ground truth (or equal if no data yet)
    poll_shares: dict[str, float] = {}
    rng = np.random.default_rng(state.turn * 1000 + hash(action.party) % 10000)

    for party_name in state.party_names:
        true_share = state.previous_shares.get(party_name, 1.0 / max(state.n_parties, 1))
        noise = rng.normal(0, noise_level * true_share)
        poll_shares[party_name] = max(0.0, true_share + noise)

    # Normalize to sum to 1
    total = sum(poll_shares.values())
    if total > 0:
        poll_shares = {k: v / total for k, v in poll_shares.items()}

    state.poll_results.append({
        "turn": state.turn,
        "commissioned_by": action.party,
        "party_shares": poll_shares,
        "sample_size": sample_size,
        "noise_level": noise_level,
    })


def resolve_pledge(action: ActionSpec, state: CampaignState,
                   lga_data: pd.DataFrame, parties: list) -> None:
    """
    Legislative Pledge: promises on issue dimensions create a valence boost.

    Params:
    - pledge: dict with pledge metadata (stored for bookkeeping)
    - dimensions: list of issue dimension indices the pledge addresses
    - popularity: 0-1 scale of how popular the pledge is (default 0.5)

    Valence boost = 0.04 * popularity, applied nationally.
    Duplicate pledges (same party, same dimensions) produce no additional effect.
    """
    pledge_data = action.params.get("pledge", {})
    dimensions = action.params.get("dimensions", [])
    popularity = action.params.get("popularity", 0.5)

    if action.party not in state.pledges:
        state.pledges[action.party] = []
    state.pledges[action.party].append(pledge_data)

    # Valence boost from promising popular policies
    if popularity > 0:
        dim_key = ",".join(str(d) for d in sorted(dimensions)) if dimensions else "general"
        effect = ActiveEffect(
            source_party=action.party,
            source_action="pledge",
            source_turn=state.turn,
            channel="valence",
            target_lgas=action.target_lgas,
            target_dimensions=None,
            target_party=action.party,
            magnitude=0.04 * popularity,
            effect_key=_effect_key(action.party, "valence", action.party, "pledge", dim_key),
        )
        state.apply_effect(effect)


# ---------------------------------------------------------------------------
# Helper: safe column extraction
# ---------------------------------------------------------------------------

def _col_safe(lga_data: pd.DataFrame, name: str, default: float, n: int) -> np.ndarray:
    """Safely extract a column as float array."""
    if name in lga_data.columns:
        return pd.to_numeric(lga_data[name], errors="coerce").fillna(default).values.astype(float)
    return np.full(n, default)


# ---------------------------------------------------------------------------
# Action Resolution Order — actions resolve in this fixed sequence
# ---------------------------------------------------------------------------

ACTION_RESOLUTION_ORDER: dict[str, int] = {
    "manifesto": 0,              # Positions updated first
    "eto_engagement": 1,         # ETO scores updated early
    "endorsement": 2,            # Coalition/endorsement effects
    "pledge": 2,                 # Pledges alongside endorsements
    "rally": 3,                  # Campaign actions resolve simultaneously
    "advertising": 3,
    "media": 3,
    "ethnic_mobilization": 3,
    "patronage": 3,
    "ground_game": 3,
    "crisis_response": 3,
    "opposition_research": 4,    # After campaign actions (uses current exposure)
    "fundraising": 5,            # Resolved last; PC available next turn
    "poll": 6,                   # Data from post-resolution state
}


# ---------------------------------------------------------------------------
# Main resolver dispatch
# ---------------------------------------------------------------------------

_RESOLVERS = {
    "rally": resolve_rally,
    "advertising": resolve_advertising,
    "manifesto": resolve_manifesto,
    "ground_game": resolve_ground_game,
    "endorsement": resolve_endorsement,
    "ethnic_mobilization": resolve_ethnic_mobilization,
    "patronage": resolve_patronage,
    "opposition_research": resolve_opposition_research,
    "media": resolve_media,
    "eto_engagement": resolve_eto_engagement,
    "crisis_response": resolve_crisis_response,
    "fundraising": resolve_fundraising,
    "poll": resolve_poll,
    "pledge": resolve_pledge,
}


def resolve_action(
    action: ActionSpec,
    state: CampaignState,
    lga_data: pd.DataFrame,
    election_config,
) -> None:
    """
    Resolve a single campaign action, updating CampaignState.

    Applies cohesion multiplier to awareness boosts, concentration penalty,
    and fatigue scaling for repeated action types.
    """
    resolver = _RESOLVERS.get(action.action_type)
    if resolver is None:
        raise ValueError(f"Unknown action type: {action.action_type}")
    if action.party not in state.party_names:
        raise ValueError(f"Unknown party: {action.party!r} (valid: {state.party_names})")

    # Fatigue multiplier (passed via params by campaign loop, or 1.0)
    fatigue_mult = action.params.get("_fatigue_mult", 1.0)

    # Snapshot effects before resolution to apply fatigue scaling
    old_effect_keys = set(state.effects.keys())

    # Snapshot awareness before resolution to scale delta by cohesion
    coh = cohesion_multiplier(state.cohesion.get(action.party, 10.0))

    if state.awareness is not None and coh < 1.0:
        old_awareness = state.awareness.copy()
        resolver(action, state, lga_data, election_config.parties)
        # Scale awareness delta by cohesion multiplier and fatigue
        delta = state.awareness - old_awareness
        state.awareness = old_awareness + delta * np.float32(coh * fatigue_mult)
        np.clip(state.awareness, 0.60, 1.0, out=state.awareness)
    else:
        resolver(action, state, lga_data, election_config.parties)
        if fatigue_mult < 1.0 and state.awareness is not None:
            # Even with full cohesion, fatigue scales awareness gains
            # (handled below via effect scaling)
            pass

    # Scale newly created effects by fatigue multiplier
    if fatigue_mult < 1.0:
        for key, effect in state.effects.items():
            if key not in old_effect_keys and effect.source_party == action.party:
                effect.magnitude *= fatigue_mult


# ---------------------------------------------------------------------------
# Action synergies
# ---------------------------------------------------------------------------

# Synergy pairs: (type_a, type_b) -> (bonus_channel, bonus_magnitude)
# Bonus applied when same party uses both in same turn on overlapping regions.
SYNERGY_TABLE: dict[frozenset[str], tuple[str, float]] = {
    frozenset({"rally", "ground_game"}): ("valence", 0.04),      # ground game primes audience
    frozenset({"advertising", "rally"}): ("salience_boost", 0.02),  # ads amplify rally message
    frozenset({"media", "opposition_research"}): ("valence_penalty", 0.03),  # media amplifies oppo
}


def _regions_overlap(a: np.ndarray | None, b: np.ndarray | None) -> bool:
    """Check if two LGA masks overlap (or either is national)."""
    if a is None or b is None:
        return True  # national overlaps with everything
    return bool(np.any(a & b))


def apply_synergies(
    turn_actions: list[ActionSpec],
    state: CampaignState,
) -> list[dict]:
    """
    Detect and apply synergy bonuses for complementary actions by the same party.

    Returns list of synergy event dicts for logging.
    """
    synergy_log: list[dict] = []

    # Group actions by party
    party_actions: dict[str, list[ActionSpec]] = {}
    for action in turn_actions:
        party_actions.setdefault(action.party, []).append(action)

    for party, actions in party_actions.items():
        if len(actions) < 2:
            continue

        # Check all pairs
        checked: set[frozenset[int]] = set()
        for i, a in enumerate(actions):
            for j, b in enumerate(actions):
                if i >= j:
                    continue
                pair_key = frozenset({i, j})
                if pair_key in checked:
                    continue
                checked.add(pair_key)

                type_pair = frozenset({a.action_type, b.action_type})
                if type_pair not in SYNERGY_TABLE:
                    continue
                if not _regions_overlap(a.target_lgas, b.target_lgas):
                    continue

                channel, magnitude = SYNERGY_TABLE[type_pair]
                # Determine target LGAs (intersection or narrower)
                if a.target_lgas is not None and b.target_lgas is not None:
                    target = a.target_lgas & b.target_lgas
                else:
                    target = a.target_lgas if a.target_lgas is not None else b.target_lgas

                if channel == "valence":
                    effect = ActiveEffect(
                        source_party=party,
                        source_action="synergy",
                        source_turn=state.turn,
                        channel="valence",
                        target_lgas=target,
                        target_dimensions=None,
                        target_party=party,
                        magnitude=magnitude,
                        effect_key=_effect_key(party, "valence", party, "synergy",
                                               f"{a.action_type}+{b.action_type}"),
                    )
                    state.apply_effect(effect)
                elif channel == "valence_penalty":
                    # Media + oppo_research: extra damage to oppo target
                    oppo_action = a if a.action_type == "opposition_research" else b
                    target_party = oppo_action.params.get("target_party", "")
                    if target_party and target_party in state.party_names:
                        effect = ActiveEffect(
                            source_party=party,
                            source_action="synergy",
                            source_turn=state.turn,
                            channel="valence",
                            target_lgas=target,
                            target_dimensions=None,
                            target_party=target_party,
                            magnitude=-magnitude,
                            effect_key=_effect_key(party, "valence", target_party, "synergy",
                                                   "media+oppo"),
                        )
                        state.apply_effect(effect)
                elif channel == "salience_boost":
                    # Ads + rally: amplify salience on rally dimensions
                    rally_action = a if a.action_type == "rally" else b
                    dims, weights = _language_dims(rally_action.language)
                    for dim, w in zip(dims[:3], weights[:3]):  # top 3 dims
                        effect = ActiveEffect(
                            source_party=party,
                            source_action="synergy",
                            source_turn=state.turn,
                            channel="salience",
                            target_lgas=target,
                            target_dimensions=[dim],
                            target_party=None,
                            magnitude=magnitude * w,
                            effect_key=_effect_key(party, "salience", "", "synergy",
                                                   f"ad+rally:{dim}"),
                        )
                        state.apply_effect(effect)

                synergy_log.append({
                    "party": party,
                    "actions": sorted([a.action_type, b.action_type]),
                    "channel": channel,
                    "magnitude": magnitude,
                })

    return synergy_log


# ---------------------------------------------------------------------------
# Action fatigue
# ---------------------------------------------------------------------------

# Actions exempt from fatigue (free actions, info-only)
_FATIGUE_EXEMPT = {"fundraising", "poll", "pledge", "manifesto"}

# Fatigue multiplier: 1/(1 + 0.2*N) where N = consecutive turns using same action type
FATIGUE_RATE = 0.20


def action_fatigue_multiplier(consecutive_turns: int) -> float:
    """Diminishing returns from repeating the same action type across turns."""
    return 1.0 / (1.0 + FATIGUE_RATE * max(consecutive_turns, 0))


def update_action_fatigue(
    state: CampaignState,
    turn_actions: list[ActionSpec],
) -> None:
    """
    Update fatigue counters based on this turn's actions.

    For each party, track which action types were used. Increment counter
    for types used, reset counter for types not used.
    """
    # Collect action types used per party this turn
    party_types: dict[str, set[str]] = {}
    for action in turn_actions:
        party_types.setdefault(action.party, set()).add(action.action_type)

    for party in state.party_names:
        if party not in state._action_fatigue:
            state._action_fatigue[party] = {}
        fatigue = state._action_fatigue[party]
        used = party_types.get(party, set())

        for atype in list(fatigue.keys()):
            if atype in used:
                fatigue[atype] += 1
            else:
                fatigue[atype] = 0  # reset when not used

        for atype in used:
            if atype not in fatigue:
                fatigue[atype] = 1


def get_fatigue_multiplier(state: CampaignState, party: str, action_type: str) -> float:
    """Get the current fatigue multiplier for a party's action type."""
    if action_type in _FATIGUE_EXEMPT:
        return 1.0
    consecutive = state._action_fatigue.get(party, {}).get(action_type, 0)
    return action_fatigue_multiplier(consecutive)


# ---------------------------------------------------------------------------
# Endorsement withdrawal
# ---------------------------------------------------------------------------

def withdraw_endorsement(
    party: str,
    endorser_type: str,
    state: CampaignState,
) -> bool:
    """
    Remove an endorsement effect from a party.

    Looks for endorsement effects matching the party and endorser_type.
    Removes the effect and endorsement tracking record.
    Returns True if an endorsement was found and removed.
    """
    target_key = _effect_key(party, "valence", party, "endorse", endorser_type)
    if target_key in state.effects:
        del state.effects[target_key]
        if target_key in state._endorsements:
            del state._endorsements[target_key]
        return True
    return False
