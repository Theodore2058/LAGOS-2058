"""
Full utility equation assembly for the LAGOS-2058 election engine.

The total utility of voter type i for party j in LGA c is:

    V_ij = λ_j  +  U_spatial(i, j)  +  U_ethnic(i, j)  +  U_religious(i, j)
               +  U_demographic(i, j)

Where:
    λ_j               = party j's valence (baseline appeal)
    U_spatial         = Merrill-Grofman utility (from spatial.py)
    U_ethnic          = α_e · Affinity(voter_ethnicity, leader_ethnicity)
    U_religious       = α_r · Affinity(voter_religion, leader_alignment)
    U_demographic     = Σ_m γ_mj · Demographic_m(i)  (if specified)
"""

from __future__ import annotations

import numpy as np
from typing import Optional

from .config import Party, EngineParams
from .spatial import spatial_utility, batch_spatial_utility
from .ethnic_affinity import EthnicAffinityMatrix, DEFAULT_ETHNIC_MATRIX
from .religious_affinity import ReligiousAffinityMatrix, DEFAULT_RELIGIOUS_MATRIX


def compute_utility(
    voter_ideal: np.ndarray,
    voter_ethnicity: str,
    voter_religion: str,
    voter_demographics: dict,
    parties: list,              # list[Party]
    params: EngineParams,
    salience_weights: np.ndarray,
    ethnic_matrix: Optional[EthnicAffinityMatrix] = None,
    religious_matrix: Optional[ReligiousAffinityMatrix] = None,
) -> np.ndarray:
    """
    Compute the full utility vector for one voter type across all parties.

    Parameters
    ----------
    voter_ideal : np.ndarray, shape (D,)
        Voter's ideal point on the 28 issue dimensions.
    voter_ethnicity : str
        Voter's ethnic identity (key for ethnic affinity matrix).
    voter_religion : str
        Voter's religious sub-category (key for religious affinity matrix).
    voter_demographics : dict
        Additional demographic attributes, e.g. {'education': 'Tertiary', ...}.
        Used for demographic utility if parties define demographic_coefficients.
    parties : list[Party]
        All parties in the election (shape J).
    params : EngineParams
        Global simulation parameters.
    salience_weights : np.ndarray, shape (D,)
        Per-issue salience weights for this LGA.
    ethnic_matrix : EthnicAffinityMatrix, optional
        Defaults to DEFAULT_ETHNIC_MATRIX.
    religious_matrix : ReligiousAffinityMatrix, optional
        Defaults to DEFAULT_RELIGIOUS_MATRIX.

    Returns
    -------
    np.ndarray, shape (J,)
        Total utility for each party.
    """
    if ethnic_matrix is None:
        ethnic_matrix = DEFAULT_ETHNIC_MATRIX
    if religious_matrix is None:
        religious_matrix = DEFAULT_RELIGIOUS_MATRIX

    J = len(parties)
    party_positions = np.array([p.positions for p in parties])  # (J, D)

    # 1. Valence
    valences = np.array([p.valence for p in parties])  # (J,)

    # 2. Spatial utility (J,)
    u_spatial = spatial_utility(
        voter_ideal, party_positions,
        beta_s=params.beta_s, q=params.q,
        salience_weights=salience_weights,
    )

    # 3. Ethnic utility (J,)
    u_ethnic = np.array([
        ethnic_matrix.get_utility(voter_ethnicity, p.leader_ethnicity, params.alpha_e)
        for p in parties
    ])

    # 4. Religious utility (J,)
    u_religious = np.array([
        religious_matrix.get_utility(voter_religion, p.religious_alignment, params.alpha_r)
        for p in parties
    ])

    # 5. Demographic utility (J,) — optional γ_mj terms
    u_demographic = np.zeros(J)
    for j, party in enumerate(parties):
        if party.demographic_coefficients:
            for demo_key, demo_val in voter_demographics.items():
                coeff = party.demographic_coefficients.get(demo_key, {})
                if isinstance(coeff, dict):
                    u_demographic[j] += coeff.get(str(demo_val), 0.0)
                else:
                    u_demographic[j] += float(coeff) * float(demo_val)

    return valences + u_spatial + u_ethnic + u_religious + u_demographic


def compute_utilities_batch(
    voter_ideals: np.ndarray,
    voter_ethnicities: list[str],
    voter_religions: list[str],
    voter_demographics_list: list[dict],
    parties: list,              # list[Party]
    params: EngineParams,
    salience_weights: np.ndarray,
    ethnic_matrix: Optional[EthnicAffinityMatrix] = None,
    religious_matrix: Optional[ReligiousAffinityMatrix] = None,
) -> np.ndarray:
    """
    Compute full utilities for a batch of voter types × all parties.

    Parameters
    ----------
    voter_ideals : np.ndarray, shape (N, D)
        Ideal points for N voter types.
    voter_ethnicities : list[str], length N
    voter_religions : list[str], length N
    voter_demographics_list : list[dict], length N
    parties, params, salience_weights : same as compute_utility
    ethnic_matrix, religious_matrix : optional overrides

    Returns
    -------
    np.ndarray, shape (N, J)
        Total utility for each (voter type, party) pair.
    """
    if ethnic_matrix is None:
        ethnic_matrix = DEFAULT_ETHNIC_MATRIX
    if religious_matrix is None:
        religious_matrix = DEFAULT_RELIGIOUS_MATRIX

    N = len(voter_ideals)
    J = len(parties)
    party_positions = np.array([p.positions for p in parties])  # (J, D)

    # 1. Valence — broadcast over all voters
    valences = np.array([p.valence for p in parties])  # (J,)

    # 2. Spatial utility (N, J)
    u_spatial = batch_spatial_utility(
        voter_ideals, party_positions,
        beta_s=params.beta_s, q=params.q,
        salience_weights=salience_weights,
    )

    # 3. Ethnic utility (N, J) — can be vectorised over voters
    u_ethnic = np.zeros((N, J))
    for i, eth in enumerate(voter_ethnicities):
        for j, party in enumerate(parties):
            u_ethnic[i, j] = ethnic_matrix.get_utility(
                eth, party.leader_ethnicity, params.alpha_e
            )

    # 4. Religious utility (N, J)
    u_religious = np.zeros((N, J))
    for i, rel in enumerate(voter_religions):
        for j, party in enumerate(parties):
            u_religious[i, j] = religious_matrix.get_utility(
                rel, party.religious_alignment, params.alpha_r
            )

    # 5. Demographic utility (N, J) — sparse; most parties have no demo coefficients
    u_demographic = np.zeros((N, J))
    for j, party in enumerate(parties):
        if party.demographic_coefficients:
            for i, demos in enumerate(voter_demographics_list):
                for demo_key, demo_val in demos.items():
                    coeff = party.demographic_coefficients.get(demo_key, {})
                    if isinstance(coeff, dict):
                        u_demographic[i, j] += coeff.get(str(demo_val), 0.0)
                    else:
                        u_demographic[i, j] += float(coeff) * float(demo_val)

    return valences + u_spatial + u_ethnic + u_religious + u_demographic
