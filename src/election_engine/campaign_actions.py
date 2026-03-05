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
from .config import N_ISSUES


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
    elif action_type == "ethnic_mobilization":
        # Higher cost if targeting a specific ethnicity (more aggressive)
        if params.get("target_ethnicity"):
            base += 0  # base 3 is already high
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

    effect = ActiveEffect(
        source_party=action.party,
        source_action="endorsement",
        source_turn=state.turn,
        channel="valence",
        target_lgas=endorser_lgas,
        target_dimensions=None,
        target_party=action.party,
        magnitude=mag,
        effect_key=_effect_key(action.party, "valence", action.party, "endorse", endorser_type),
    )
    state.apply_effect(effect)

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

    # Exposure
    state.exposure[action.party] = state.exposure.get(action.party, 0.0) + 0.3 * scale


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

    # Volatile: can backfire
    magnitude = 0.02 * (2.0 * success - 0.5)  # range: -0.01 to +0.03

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
    """Fundraising: PC generation (bookkeeping). No engine effect."""
    # Pure bookkeeping — no effects on engine channels
    pass


def resolve_poll(action: ActionSpec, state: CampaignState,
                 lga_data: pd.DataFrame, parties: list) -> None:
    """Poll: generates noisy election results. No engine effect."""
    # Pure information — no effects on engine channels
    pass


def resolve_pledge(action: ActionSpec, state: CampaignState,
                   lga_data: pd.DataFrame, parties: list) -> None:
    """Legislative Pledge: coalition-building multiplier. Bookkeeping."""
    pledge_data = action.params.get("pledge", {})
    if action.party not in state.pledges:
        state.pledges[action.party] = []
    state.pledges[action.party].append(pledge_data)


# ---------------------------------------------------------------------------
# Helper: safe column extraction
# ---------------------------------------------------------------------------

def _col_safe(lga_data: pd.DataFrame, name: str, default: float, n: int) -> np.ndarray:
    """Safely extract a column as float array."""
    if name in lga_data.columns:
        return pd.to_numeric(lga_data[name], errors="coerce").fillna(default).values.astype(float)
    return np.full(n, default)


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

    Applies cohesion multiplier to awareness boosts and concentration penalty.
    """
    resolver = _RESOLVERS.get(action.action_type)
    if resolver is None:
        raise ValueError(f"Unknown action type: {action.action_type}")
    if action.party not in state.party_names:
        raise ValueError(f"Unknown party: {action.party!r} (valid: {state.party_names})")

    # Snapshot awareness before resolution to scale delta by cohesion
    coh = cohesion_multiplier(state.cohesion.get(action.party, 10.0))

    if state.awareness is not None and coh < 1.0:
        old_awareness = state.awareness.copy()
        resolver(action, state, lga_data, election_config.parties)
        # Scale awareness delta by cohesion multiplier
        delta = state.awareness - old_awareness
        state.awareness = old_awareness + delta * np.float32(coh)
        np.clip(state.awareness, 0.60, 1.0, out=state.awareness)
    else:
        resolver(action, state, lga_data, election_config.parties)
