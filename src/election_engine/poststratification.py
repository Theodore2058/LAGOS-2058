"""
Poststratification aggregation for the LAGOS-2058 election engine.

Aggregates voter-type-level vote probabilities and turnout to LGA-level
vote shares using the formula:

    VoteShare_j(c) = Σ_g [w_gc · turnout_g · P_gj] / Σ_g [w_gc · turnout_g]

Where:
    w_gc    = population weight of type g in LGA c
    turnout_g = P(vote | type g, LGA c)
    P_gj    = conditional P(party j | vote, type g, LGA c)
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .config import ElectionConfig, EngineParams, Party
from .ethnic_affinity import EthnicAffinityMatrix, DEFAULT_ETHNIC_MATRIX
from .religious_affinity import ReligiousAffinityMatrix, DEFAULT_RELIGIOUS_MATRIX
from .voter_types import (
    VoterType, generate_all_voter_types, compute_type_weights,
    demographics_to_ideal_point,
)
from .salience import compute_salience, SalienceRule, DEFAULT_SALIENCE_RULES
from .utility import compute_utility
from .turnout import compute_vote_probs_with_turnout

logger = logging.getLogger(__name__)

_WEIGHT_THRESHOLD = 1e-7  # Skip types below this population weight


def aggregate_to_lga(
    type_weights: np.ndarray,
    type_vote_probs: np.ndarray,
    type_turnout: np.ndarray,
) -> tuple[np.ndarray, float]:
    """
    Aggregate voter-type results to LGA-level vote shares.

    Parameters
    ----------
    type_weights : np.ndarray, shape (N_types,)
        Population fractions for each voter type in this LGA.
    type_vote_probs : np.ndarray, shape (N_types, J)
        Conditional P(party j | vote) for each type.
    type_turnout : np.ndarray, shape (N_types,)
        Turnout probability for each type.

    Returns
    -------
    (vote_shares, expected_turnout)
        vote_shares : np.ndarray, shape (J,) — sums to 1.0
        expected_turnout : float — weighted average turnout rate
    """
    # Effective weight: population × turnout
    eff_weights = type_weights * type_turnout   # (N_types,)
    total_eff = eff_weights.sum()

    if total_eff < 1e-12:
        J = type_vote_probs.shape[1]
        return np.ones(J) / J, 0.0

    # Weighted average over types
    # vote_shares_j = Σ_g (eff_weights_g × P_gj) / Σ_g eff_weights_g
    vote_shares = (eff_weights[:, None] * type_vote_probs).sum(axis=0) / total_eff

    # Normalise for numerical safety
    share_sum = vote_shares.sum()
    if share_sum > 0:
        vote_shares /= share_sum

    expected_turnout = float(np.dot(type_weights, type_turnout))

    return vote_shares, expected_turnout


def compute_lga_results(
    lga_row: pd.Series,
    voter_types: list[VoterType],
    parties: list,              # list[Party]
    params: EngineParams,
    salience_weights: np.ndarray,      # (28,)
    ethnic_matrix: EthnicAffinityMatrix,
    religious_matrix: ReligiousAffinityMatrix,
    ideal_point_coeff_table: list[dict] | None = None,
) -> tuple[np.ndarray, float, int]:
    """
    Compute vote shares and turnout for one LGA.

    Parameters
    ----------
    lga_row : pd.Series
    voter_types : list[VoterType]
    parties : list[Party]
    params : EngineParams
    salience_weights : np.ndarray, shape (28,)
    ethnic_matrix, religious_matrix : affinity matrices
    ideal_point_coeff_table : optional coefficient override

    Returns
    -------
    (vote_shares, turnout, n_active_types)
        vote_shares : np.ndarray, shape (J,)
        turnout : float
        n_active_types : int  — number of types with weight > threshold
    """
    J = len(parties)
    party_positions = np.array([p.positions for p in parties])  # (J, 28)

    # Step 1: LGA population weights for each type
    type_weights = compute_type_weights(lga_row, voter_types, _WEIGHT_THRESHOLD)

    # Step 2: identify active types (skip near-zero weight to save computation)
    active_idx = np.where(type_weights > _WEIGHT_THRESHOLD)[0]
    n_active = len(active_idx)

    # Step 3: for each active type, compute ideal point, utility, turnout
    active_vote_probs = np.zeros((n_active, J))
    active_turnout = np.zeros(n_active)
    active_weights = type_weights[active_idx]

    for k, i in enumerate(active_idx):
        vt = voter_types[i]

        # Ideal point in issue space
        ideal = demographics_to_ideal_point(vt, lga_row, ideal_point_coeff_table)

        # Full utility vector (J,)
        demos = {
            "education": vt.education,
            "age_cohort": vt.age_cohort,
            "setting": vt.setting,
        }
        utilities = compute_utility(
            voter_ideal=ideal,
            voter_ethnicity=vt.ethnicity,
            voter_religion=vt.religion,
            voter_demographics=demos,
            parties=parties,
            params=params,
            salience_weights=salience_weights,
            ethnic_matrix=ethnic_matrix,
            religious_matrix=religious_matrix,
        )

        # Conditional vote probs + turnout
        cond_probs, p_vote = compute_vote_probs_with_turnout(
            utilities=utilities,
            voter_ideal=ideal,
            party_positions=party_positions,
            params=params,
            voter_demographics=demos,
        )

        active_vote_probs[k] = cond_probs
        active_turnout[k] = p_vote

    # Step 4: Aggregate
    # Build full arrays (inactive types have zero weight — they don't contribute)
    full_vote_probs = np.zeros((len(voter_types), J))
    full_turnout = np.zeros(len(voter_types))

    for k, i in enumerate(active_idx):
        full_vote_probs[i] = active_vote_probs[k]
        full_turnout[i] = active_turnout[k]

    vote_shares, turnout = aggregate_to_lga(type_weights, full_vote_probs, full_turnout)

    return vote_shares, turnout, n_active


def compute_all_lga_results(
    lga_data: pd.DataFrame,
    election_config: ElectionConfig,
    ethnic_matrix: EthnicAffinityMatrix | None = None,
    religious_matrix: ReligiousAffinityMatrix | None = None,
    salience_rules: list[SalienceRule] | None = None,
    ideal_point_coeff_table: list[dict] | None = None,
) -> pd.DataFrame:
    """
    Compute vote shares for all 774 LGAs (deterministic, no noise).

    Parameters
    ----------
    lga_data : pd.DataFrame
        Full LGA dataframe.
    election_config : ElectionConfig
    ethnic_matrix, religious_matrix : optional overrides
    salience_rules : optional salience rule override
    ideal_point_coeff_table : optional coefficient table override

    Returns
    -------
    pd.DataFrame
        Columns: State, LGA Name, Administrative Zone, AZ Name,
                 {party_name}_share (for each party), Turnout, Active Types
    """
    if ethnic_matrix is None:
        ethnic_matrix = DEFAULT_ETHNIC_MATRIX
    if religious_matrix is None:
        religious_matrix = DEFAULT_RELIGIOUS_MATRIX

    voter_types = generate_all_voter_types()
    parties = election_config.parties
    params = election_config.params
    J = len(parties)

    # Precompute salience for all LGAs
    national_median_gdp = float(lga_data["GDP Per Capita Est"].median())
    salience_matrix = np.zeros((len(lga_data), 28))
    for idx in range(len(lga_data)):
        row = lga_data.iloc[idx]
        salience_matrix[idx] = compute_salience(
            row, rules=salience_rules, national_median_gdp=national_median_gdp
        )

    rows = []
    for idx in range(len(lga_data)):
        lga_row = lga_data.iloc[idx]
        salience_w = salience_matrix[idx]

        vote_shares, turnout, n_active = compute_lga_results(
            lga_row=lga_row,
            voter_types=voter_types,
            parties=parties,
            params=params,
            salience_weights=salience_w,
            ethnic_matrix=ethnic_matrix,
            religious_matrix=religious_matrix,
            ideal_point_coeff_table=ideal_point_coeff_table,
        )

        row_dict = {
            "State": lga_row.get("State", ""),
            "LGA Name": lga_row.get("LGA Name", ""),
            "Administrative Zone": lga_row.get("Administrative Zone", 0),
            "AZ Name": lga_row.get("AZ Name", ""),
            "Turnout": turnout,
            "Active Types": n_active,
        }
        for j, party in enumerate(parties):
            row_dict[f"{party.name}_share"] = vote_shares[j]

        rows.append(row_dict)

        if (idx + 1) % 100 == 0:
            logger.info("Processed %d / %d LGAs", idx + 1, len(lga_data))

    return pd.DataFrame(rows)
