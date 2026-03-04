"""
Turnout model for the LAGOS-2058 election engine.

Implements an abstention-as-party model. A virtual "abstention" option is
appended to the utility vector and assigned its own utility:

    V_abstain = τ₀ + τ₁ · min_dist² + τ₂ / max(gap, ε)

Where:
    τ₀  = baseline abstention utility (higher = more abstention everywhere)
    τ₁  = alienation: voter is far from all parties → abstention more attractive
    τ₂  = indifference: top choice doesn't stand out → abstention more attractive
    min_dist² = min_j (1/D)||x - z_j||²  (mean per-dimension squared distance, uniform salience)
    gap = V_1 - mean(V_2, ..., V_J)  (utility gap between top-1 and mean of rest)

The gap formulation uses top-1 vs mean-of-rest rather than top-1 vs top-2.
For J=2 these are identical (mean-of-rest IS the second party). For J>2 the
"field gap" is more stable — it measures how much the voter's best choice
stands out from the whole field, preventing artificial indifference when two
parties happen to be close even though the voter has a clear overall preference.

Demographic adjustments apply before computing the abstention utility:
    Education boost: Tertiary education reduces abstention utility
    Age boost: Older cohorts (50+) have lower abstention
    Urban effect: Urban voters slightly more likely to vote

The turnout probability for a voter type is:
    P(vote) = 1 - P(abstain)
where P(abstain) uses softmax over [V₁, ..., V_J, V_abstain].
"""

from __future__ import annotations

import numpy as np

from .config import EngineParams

_EPSILON = 1e-6  # Prevents division by zero in indifference term


def compute_abstention_utility(
    utilities: np.ndarray,
    voter_ideal: np.ndarray,
    party_positions: np.ndarray,
    params: EngineParams,
    education: str = "",
    age_cohort: str = "",
    setting: str = "",
    livelihood: str = "",
    income: str = "",
    gender: str = "",
) -> float:
    """
    Compute the utility of the abstention option for one voter type.

    Parameters
    ----------
    utilities : np.ndarray, shape (J,)
        Utility for each party (already computed).
    voter_ideal : np.ndarray, shape (D,)
        Voter ideal point (for alienation calculation).
    party_positions : np.ndarray, shape (J, D)
        All party positions.
    params : EngineParams
        Simulation parameters (tau_0, tau_1, tau_2).
    education : str
        'Tertiary', 'Secondary', or 'Below secondary'.
    age_cohort : str
        '18-24', '25-34', '35-49', or '50+'.
    setting : str
        'Urban', 'Peri-urban', or 'Rural'.
    livelihood : str
        One of: 'Smallholder', 'Commercial ag', 'Trade/informal',
        'Formal private', 'Public sector', 'Unemployed/student'.
    income : str
        One of: 'Bottom 40%', 'Middle 40%', 'Top 20%'.
    gender : str
        'Male' or 'Female'.

    Returns
    -------
    float
        Utility of abstaining.
    """
    # Alienation: mean per-dimension squared distance to the nearest party.
    # Using mean (not sum) makes tau_1 scale-invariant w.r.t. the number of
    # issue dimensions, so it stays comparable to the salience-weighted party
    # utilities regardless of how many issues are in the model.
    diffs = party_positions - voter_ideal  # (J, D)
    sq_dists = np.mean(diffs ** 2, axis=1)  # (J,) — mean over D dimensions
    min_dist_sq = float(np.min(sq_dists))

    # Indifference: gap between top-1 utility and mean of all others.
    # For J=2 this equals top-2 gap; for J>2 it measures how much the
    # voter's best choice stands out from the entire field.
    if len(utilities) >= 2:
        sorted_utils = np.sort(utilities)[::-1]
        gap = sorted_utils[0] - np.mean(sorted_utils[1:])
        gap = abs(gap)  # safety: should be non-negative after sort, but guard
    else:
        gap = abs(utilities[0]) + _EPSILON

    v_abstain = (
        params.tau_0
        + params.tau_1 * min_dist_sq
        + params.tau_2 / max(gap, _EPSILON)
    )

    # Demographic adjustments — education, age, setting
    if education == "Tertiary":
        v_abstain -= 1.0  # educated voters more likely to vote
    elif education == "Below secondary":
        v_abstain += 0.3  # less educated → less engaged

    if age_cohort == "50+":
        v_abstain -= 0.5  # older voters more habitual
    elif age_cohort == "18-24":
        v_abstain += 0.2  # youth disengagement

    if setting == "Urban":
        v_abstain -= 0.2  # urban access advantage

    # Livelihood adjustments — civic engagement varies by sector
    if livelihood == "Public sector":
        v_abstain -= 0.4  # civil servants: high political awareness, stake in outcomes
    elif livelihood == "Formal private":
        v_abstain -= 0.2  # formal workers: somewhat engaged, have resources
    elif livelihood == "Unemployed/student":
        v_abstain += 0.3  # disengaged, logistic barriers, or apathy
    elif livelihood == "Smallholder":
        v_abstain += 0.1  # rural farmers: harder to reach polling stations

    # Income adjustments — moderate effects
    if income == "Top 20%":
        v_abstain -= 0.3  # wealthy voters: more stake, more resources
    elif income == "Bottom 40%":
        v_abstain += 0.2  # poor voters: logistic barriers, fatalism

    # Gender adjustment — women face additional participation barriers
    # in many contexts (security concerns, household duties, social norms).
    # This is the base effect; it interacts with education and setting.
    if gender == "Female":
        v_abstain += 0.15  # mild female participation gap

    return float(v_abstain)


def compute_turnout_probability(
    utilities: np.ndarray,
    voter_ideal: np.ndarray,
    party_positions: np.ndarray,
    params: EngineParams,
    voter_demographics: dict | None = None,
) -> float:
    """
    Compute P(vote) = 1 - P(abstain) using the abstention-as-party model.

    Parameters
    ----------
    utilities : np.ndarray, shape (J,)
        Party utilities for this voter type.
    voter_ideal : np.ndarray, shape (D,)
        Voter ideal point.
    party_positions : np.ndarray, shape (J, D)
        All party positions.
    params : EngineParams
        Simulation parameters.
    voter_demographics : dict, optional
        Must contain keys 'education', 'age_cohort', 'setting' if present.

    Returns
    -------
    float
        Turnout probability in [0, 1].
    """
    if voter_demographics is None:
        voter_demographics = {}

    v_abstain = compute_abstention_utility(
        utilities=utilities,
        voter_ideal=voter_ideal,
        party_positions=party_positions,
        params=params,
        education=voter_demographics.get("education", ""),
        age_cohort=voter_demographics.get("age_cohort", ""),
        setting=voter_demographics.get("setting", ""),
        livelihood=voter_demographics.get("livelihood", ""),
        income=voter_demographics.get("income", ""),
        gender=voter_demographics.get("gender", ""),
    )

    # Softmax over [party utilities..., abstention] with the election-level scale λ.
    # Applying params.scale here keeps the turnout trade-off consistent with the
    # party-choice softmax (higher λ → sharper abstain/vote boundary).
    all_utils = np.append(utilities, v_abstain)
    shifted = (all_utils - np.max(all_utils)) * params.scale
    exp_vals = np.exp(shifted)
    probs = exp_vals / exp_vals.sum()

    p_abstain = float(probs[-1])
    return max(0.0, min(1.0, 1.0 - p_abstain))


def compute_vote_probs_with_turnout(
    utilities: np.ndarray,
    voter_ideal: np.ndarray,
    party_positions: np.ndarray,
    params: EngineParams,
    voter_demographics: dict | None = None,
) -> tuple[np.ndarray, float]:
    """
    Compute vote probabilities conditional on voting AND turnout probability.

    Returns
    -------
    (conditional_vote_probs, turnout_prob)
        conditional_vote_probs : np.ndarray, shape (J,) — sums to 1
        turnout_prob : float — P(vote)
    """
    if voter_demographics is None:
        voter_demographics = {}

    v_abstain = compute_abstention_utility(
        utilities=utilities,
        voter_ideal=voter_ideal,
        party_positions=party_positions,
        params=params,
        education=voter_demographics.get("education", ""),
        age_cohort=voter_demographics.get("age_cohort", ""),
        setting=voter_demographics.get("setting", ""),
        livelihood=voter_demographics.get("livelihood", ""),
        income=voter_demographics.get("income", ""),
        gender=voter_demographics.get("gender", ""),
    )

    all_utils = np.append(utilities, v_abstain)
    shifted = (all_utils - np.max(all_utils)) * params.scale
    exp_vals = np.exp(shifted)
    probs = exp_vals / exp_vals.sum()

    p_abstain = float(probs[-1])
    p_vote = max(0.0, min(1.0, 1.0 - p_abstain))

    # Conditional vote probabilities (renormalise over parties only)
    party_probs = probs[:-1]
    total_party = party_probs.sum()
    if total_party > 0:
        conditional = party_probs / total_party
    else:
        conditional = np.ones(len(utilities)) / len(utilities)

    return conditional, p_vote


def batch_compute_vote_probs_with_turnout(
    utilities_matrix: np.ndarray,
    voter_ideals: np.ndarray,
    party_positions: np.ndarray,
    params: EngineParams,
    educations: np.ndarray,
    age_cohorts: np.ndarray,
    settings: np.ndarray,
    party_sq_norms_uniform: np.ndarray | None = None,
    precomputed_min_dist_sq: np.ndarray | None = None,
    precomputed_demo_adjust: np.ndarray | None = None,
    _buffers: dict | None = None,
    livelihoods: np.ndarray | None = None,
    incomes: np.ndarray | None = None,
    genders: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Vectorised vote probabilities and turnout for N voter types at once.

    Parameters
    ----------
    utilities_matrix : np.ndarray, shape (N, J)
        Party utilities for each voter type.
    voter_ideals : np.ndarray, shape (N, D)
        Ideal points.
    party_positions : np.ndarray, shape (J, D)
        Party positions.
    params : EngineParams
    educations : np.ndarray of int, shape (N,)
        0 = Below secondary, 1 = Secondary, 2 = Tertiary
    age_cohorts : np.ndarray of int, shape (N,)
        0 = 18-24, 1 = 25-34, 2 = 35-49, 3 = 50+
    settings : np.ndarray of int, shape (N,)
        0 = Urban, 1 = Peri-urban, 2 = Rural
    livelihoods : np.ndarray of int, shape (N,), optional
        0 = Smallholder, 1 = Commercial ag, 2 = Trade/informal,
        3 = Formal private, 4 = Public sector, 5 = Unemployed/student
    incomes : np.ndarray of int, shape (N,), optional
        0 = Bottom 40%, 1 = Middle 40%, 2 = Top 20%
    genders : np.ndarray of int, shape (N,), optional
        0 = Male, 1 = Female
    _buffers : dict, optional
        Pre-allocated buffers for hot-loop reuse. Keys:
        'exp_NJ' (N_max, J), 'top1' (N_max,), 'row_sum' (N_max,),
        'sum_exp' (N_max,), 'tmp' (N_max,), 'v_abstain' (N_max,).

    Returns
    -------
    (conditional_vote_probs, turnout_probs)
        conditional_vote_probs : np.ndarray, shape (N, J)
        turnout_probs : np.ndarray, shape (N,)
    """
    N, J = utilities_matrix.shape
    D = party_positions.shape[1]

    # --- Alienation: min mean-sq-distance to any party ---
    if precomputed_min_dist_sq is not None:
        min_dist_sq = precomputed_min_dist_sq
    else:
        inv_D = 1.0 / D
        voter_sq_norms = np.einsum("nd,nd->n", voter_ideals, voter_ideals) * inv_D
        if party_sq_norms_uniform is None:
            party_sq_norms_uniform = np.sum(party_positions ** 2, axis=1) * inv_D
        cross_terms = (voter_ideals @ party_positions.T) * (2.0 * inv_D)
        min_dist_sq = voter_sq_norms + party_sq_norms_uniform[0] - cross_terms[:, 0]
        for j_al in range(1, J):
            candidate = voter_sq_norms + party_sq_norms_uniform[j_al] - cross_terms[:, j_al]
            np.minimum(min_dist_sq, candidate, out=min_dist_sq)
        del cross_terms

    # --- Use pre-allocated buffers if provided ---
    if _buffers is not None:
        exp_parties = _buffers["exp_NJ"][:N]
        top1 = _buffers["top1"][:N]
        row_sum = _buffers["row_sum"][:N]
        sum_exp = _buffers["sum_exp"][:N]
        _tmp = _buffers["tmp"][:N]
        v_abstain = _buffers["v_abstain"][:N]
    else:
        exp_parties = np.empty((N, J), dtype=np.float32)
        top1 = np.empty(N, dtype=np.float32)
        row_sum = np.empty(N, dtype=np.float32)
        sum_exp = np.empty(N, dtype=np.float32)
        _tmp = np.empty(N, dtype=np.float32)
        v_abstain = np.empty(N, dtype=np.float32)

    # --- Indifference: gap = top1 - mean(rest) ---
    if J >= 2:
        np.copyto(top1, utilities_matrix[:, 0])
        np.copyto(row_sum, utilities_matrix[:, 0])
        for j_ind in range(1, J):
            col = utilities_matrix[:, j_ind]
            np.maximum(top1, col, out=top1)
            row_sum += col
        mean_rest = (row_sum - top1) * np.float32(1.0 / (J - 1))
        gap = np.abs(top1 - mean_rest)
    else:
        np.copyto(top1, utilities_matrix[:, 0])
        gap = np.abs(top1) + _EPSILON
    np.maximum(gap, _EPSILON, out=gap)

    # --- Base abstention utility ---
    # v_abstain = tau_0 + tau_1 * min_dist_sq + tau_2 / gap
    np.multiply(min_dist_sq, params.tau_1, out=v_abstain)
    v_abstain += params.tau_0
    np.divide(np.float32(params.tau_2), gap, out=_tmp)
    v_abstain += _tmp

    # --- Demographic adjustments ---
    if precomputed_demo_adjust is not None:
        v_abstain += precomputed_demo_adjust
    else:
        v_abstain[educations == 2] -= 1.0
        v_abstain[educations == 0] += 0.3
        v_abstain[age_cohorts == 3] -= 0.5
        v_abstain[age_cohorts == 0] += 0.2
        v_abstain[settings == 0] -= 0.2
        # Livelihood adjustments
        if livelihoods is not None:
            v_abstain[livelihoods == 4] -= 0.4   # Public sector: high political awareness
            v_abstain[livelihoods == 3] -= 0.2   # Formal private: somewhat engaged
            v_abstain[livelihoods == 5] += 0.3   # Unemployed/student: disengaged
            v_abstain[livelihoods == 0] += 0.1   # Smallholder: harder access
        # Income adjustments
        if incomes is not None:
            v_abstain[incomes == 2] -= 0.3       # Top 20%: more stake, more resources
            v_abstain[incomes == 0] += 0.2       # Bottom 40%: logistic barriers
        # Gender adjustments
        if genders is not None:
            v_abstain[genders == 1] += 0.15      # Female: participation gap

    # --- Softmax over [party utilities..., abstention] ---
    row_max = np.maximum(top1, v_abstain)
    scale_f32 = np.float32(params.scale)
    row_max *= scale_f32
    # rm32 = row_max (already float32 if inputs are float32)
    rm32 = row_max

    # Column-at-a-time exp + sum
    sum_exp[:] = 0.0
    for j_exp in range(J):
        np.multiply(utilities_matrix[:, j_exp], scale_f32, out=_tmp)
        _tmp -= rm32
        np.exp(_tmp, out=_tmp)
        exp_parties[:, j_exp] = _tmp
        sum_exp += _tmp

    # Abstention exp
    np.multiply(v_abstain, scale_f32, out=_tmp)
    _tmp -= rm32
    np.exp(_tmp, out=_tmp)
    exp_abstain_f32 = _tmp  # alias
    sum_exp += exp_abstain_f32
    inv_sum = np.float32(1.0) / sum_exp

    # Turnout = 1 - P(abstain)
    p_abstain_f32 = exp_abstain_f32 * inv_sum
    turnout_probs = np.clip(np.float32(1.0) - p_abstain_f32,
                            np.float32(0.0), np.float32(1.0))

    # Conditional vote probabilities
    safe_total = np.maximum(turnout_probs, np.float32(1e-30))
    scale_factor = inv_sum / safe_total
    for j_cond in range(J):
        exp_parties[:, j_cond] *= scale_factor

    return exp_parties, turnout_probs
