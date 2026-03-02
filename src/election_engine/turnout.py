"""
Turnout model for the LAGOS-2058 election engine.

Implements an abstention-as-party model. A virtual "abstention" option is
appended to the utility vector and assigned its own utility:

    V_abstain = τ₀ + τ₁ · min_dist² + τ₂ / max(gap, ε)

Where:
    τ₀  = baseline abstention utility (higher = more abstention everywhere)
    τ₁  = alienation: voter is far from all parties → abstention more attractive
    τ₂  = indifference: top two parties nearly equal → abstention more attractive
    min_dist² = min_j (1/D)||x - z_j||²  (mean per-dimension squared distance, uniform salience)
    gap = |V_1 - V_2|  (utility gap between top-1 and top-2 parties)

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

    # Indifference: gap between top-1 and top-2 utilities
    if len(utilities) >= 2:
        sorted_utils = np.sort(utilities)[::-1]
        gap = abs(sorted_utils[0] - sorted_utils[1])
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
    # Compute ||x - z_j||²/D = (||x||² + ||z_j||² - 2x·z_j) / D
    # This avoids creating a (N, J, D) intermediate array.
    voter_sq_norms = np.sum(voter_ideals ** 2, axis=1) / D  # (N,)
    party_sq_norms = np.sum(party_positions ** 2, axis=1) / D  # (J,)
    cross_terms = (voter_ideals @ party_positions.T) * (2.0 / D)  # (N, J)
    sq_dists = voter_sq_norms[:, np.newaxis] + party_sq_norms[np.newaxis, :] - cross_terms
    min_dist_sq = sq_dists.min(axis=1)  # (N,)

    # --- Indifference: gap between top-1 and top-2 utilities ---
    # Sort along party axis descending
    sorted_utils = np.sort(utilities_matrix, axis=1)[:, ::-1]  # (N, J) descending
    if J >= 2:
        gap = np.abs(sorted_utils[:, 0] - sorted_utils[:, 1])  # (N,)
    else:
        # Single party: use |utility| as proxy (matches scalar function)
        gap = np.abs(sorted_utils[:, 0]) + _EPSILON
    gap = np.maximum(gap, _EPSILON)

    # --- Base abstention utility ---
    v_abstain = params.tau_0 + params.tau_1 * min_dist_sq + params.tau_2 / gap  # (N,)

    # --- Demographic adjustments (vectorised) ---
    # Education: Tertiary → -1.0, Below secondary → +0.3
    v_abstain = np.where(educations == 2, v_abstain - 1.0, v_abstain)
    v_abstain = np.where(educations == 0, v_abstain + 0.3, v_abstain)

    # Age: 50+ → -0.5, 18-24 → +0.2
    v_abstain = np.where(age_cohorts == 3, v_abstain - 0.5, v_abstain)
    v_abstain = np.where(age_cohorts == 0, v_abstain + 0.2, v_abstain)

    # Setting: Urban → -0.2
    v_abstain = np.where(settings == 0, v_abstain - 0.2, v_abstain)

    # --- Softmax over [party utilities..., abstention] ---
    # all_utils: (N, J+1)
    all_utils = np.column_stack([utilities_matrix, v_abstain])  # (N, J+1)
    shifted = (all_utils - all_utils.max(axis=1, keepdims=True)) * params.scale
    exp_vals = np.exp(shifted)
    probs = exp_vals / exp_vals.sum(axis=1, keepdims=True)  # (N, J+1)

    p_abstain = probs[:, -1]  # (N,)
    turnout_probs = np.clip(1.0 - p_abstain, 0.0, 1.0)

    # Conditional vote probabilities (renormalise over parties only)
    party_probs = probs[:, :-1]  # (N, J)
    total_party = party_probs.sum(axis=1, keepdims=True)  # (N, 1)
    # Avoid division by zero
    safe_total = np.where(total_party > 0, total_party, 1.0)
    conditional = np.where(total_party > 0, party_probs / safe_total,
                           np.ones((N, J)) / J)

    return conditional, turnout_probs
