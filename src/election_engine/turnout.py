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

    # Demographic adjustments
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
        # Salience-weighted alienation already computed during spatial utility
        min_dist_sq = precomputed_min_dist_sq
    else:
        # Fallback: uniform-weighted alienation via BLAS matmul
        inv_D = 1.0 / D
        voter_sq_norms = np.einsum("nd,nd->n", voter_ideals, voter_ideals) * inv_D  # (N,)
        if party_sq_norms_uniform is None:
            party_sq_norms_uniform = np.sum(party_positions ** 2, axis=1) * inv_D  # (J,)
        cross_terms = (voter_ideals @ party_positions.T) * (2.0 * inv_D)  # (N, J)
        # Compute min without allocating full (N, J) — loop over J
        min_dist_sq = voter_sq_norms + party_sq_norms_uniform[0] - cross_terms[:, 0]
        for j_al in range(1, J):
            candidate = voter_sq_norms + party_sq_norms_uniform[j_al] - cross_terms[:, j_al]
            np.minimum(min_dist_sq, candidate, out=min_dist_sq)
        del cross_terms  # Free (N, J) early

    # --- Indifference: gap = top1 - mean(rest) ---
    # Column-at-a-time max + sum: each column (N,) fits in L1 cache,
    # merging two axis=1 reductions into a single pass over the (N, J) array.
    if J >= 2:
        top1 = utilities_matrix[:, 0].copy()  # (N,) float32
        row_sum = utilities_matrix[:, 0].copy()
        for j_ind in range(1, J):
            col = utilities_matrix[:, j_ind]
            np.maximum(top1, col, out=top1)
            row_sum += col
        mean_rest = (row_sum - top1) * np.float32(1.0 / (J - 1))
        gap = np.abs(top1 - mean_rest)
    else:
        top1 = utilities_matrix[:, 0].copy()
        gap = np.abs(top1) + _EPSILON
    gap = np.maximum(gap, _EPSILON)

    # --- Base abstention utility ---
    v_abstain = params.tau_0 + params.tau_1 * min_dist_sq + params.tau_2 / gap  # (N,)

    # --- Demographic adjustments ---
    if precomputed_demo_adjust is not None:
        v_abstain += precomputed_demo_adjust
    else:
        v_abstain[educations == 2] -= 1.0  # Tertiary
        v_abstain[educations == 0] += 0.3  # Below secondary
        v_abstain[age_cohorts == 3] -= 0.5  # 50+
        v_abstain[age_cohorts == 0] += 0.2  # 18-24
        v_abstain[settings == 0] -= 0.2  # Urban

    # --- Softmax over [party utilities..., abstention] ---
    # Reuse top1 from indifference; avoid second max scan over (N, J).
    row_max = np.maximum(top1, v_abstain)
    row_max *= params.scale
    rm32 = row_max.astype(np.float32)  # (N,) float32
    scale_f32 = np.float32(params.scale)

    # Column-at-a-time exp + sum: fuses the scale, shift, exp, and accumulate
    # into a single pass over (N, J).  Each column (N,) = ~60KB stays in L1;
    # avoids 3 separate full (N, J) passes of the previous approach.
    exp_parties = np.empty((N, J), dtype=np.float32)
    sum_exp = np.zeros(N, dtype=np.float32)
    _tmp = np.empty(N, dtype=np.float32)  # reusable (N,) scratch
    for j_exp in range(J):
        np.multiply(utilities_matrix[:, j_exp], scale_f32, out=_tmp)
        _tmp -= rm32
        np.exp(_tmp, out=_tmp)
        exp_parties[:, j_exp] = _tmp
        sum_exp += _tmp

    exp_abstain_f32 = np.exp(
        (v_abstain * params.scale - row_max).astype(np.float32)
    )  # (N,) float32
    sum_exp += exp_abstain_f32
    inv_sum = np.float32(1.0) / sum_exp  # (N,) float32

    # Turnout = 1 - P(abstain)
    p_abstain_f32 = exp_abstain_f32 * inv_sum
    turnout_probs = np.clip(np.float32(1.0) - p_abstain_f32,
                            np.float32(0.0), np.float32(1.0))

    # Conditional vote probabilities (column-at-a-time, stay float32)
    safe_total = np.maximum(turnout_probs, np.float32(1e-30))
    scale_factor = inv_sum / safe_total  # (N,) float32
    for j_cond in range(J):
        exp_parties[:, j_cond] *= scale_factor

    return exp_parties, turnout_probs
