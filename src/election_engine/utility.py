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
from .ethnic_affinity import EthnicAffinityMatrix, DEFAULT_ETHNIC_MATRIX, ETHNIC_GROUPS
from .religious_affinity import ReligiousAffinityMatrix, DEFAULT_RELIGIOUS_MATRIX, RELIGIOUS_GROUPS


def precompute_ethnic_utility_table(
    parties: list,
    params: EngineParams,
    ethnic_matrix: EthnicAffinityMatrix,
) -> tuple[np.ndarray, dict[str, int]]:
    """
    Precompute ethnic utility for every (ethnic group, party) pair.

    Returns
    -------
    (table, group_to_idx)
        table : np.ndarray, shape (N_groups, J) — α_e × affinity
        group_to_idx : dict mapping ethnic group name → row index
    """
    groups = ETHNIC_GROUPS
    group_to_idx = {g: i for i, g in enumerate(groups)}
    J = len(parties)
    table = np.zeros((len(groups), J))
    for i, g in enumerate(groups):
        for j, p in enumerate(parties):
            table[i, j] = ethnic_matrix.get_utility(g, p.leader_ethnicity, params.alpha_e)
    return table, group_to_idx


def precompute_religious_utility_table(
    parties: list,
    params: EngineParams,
    religious_matrix: ReligiousAffinityMatrix,
) -> tuple[np.ndarray, dict[str, int]]:
    """
    Precompute religious utility for every (religious group, party) pair.

    Returns
    -------
    (table, group_to_idx)
        table : np.ndarray, shape (N_groups, J) — α_r × affinity
        group_to_idx : dict mapping religious group name → row index
    """
    groups = RELIGIOUS_GROUPS
    group_to_idx = {g: i for i, g in enumerate(groups)}
    J = len(parties)
    table = np.zeros((len(groups), J))
    for i, g in enumerate(groups):
        for j, p in enumerate(parties):
            table[i, j] = religious_matrix.get_utility(g, p.religious_alignment, params.alpha_r)
    return table, group_to_idx


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

    # 1. Valence + incumbency bonus
    valences = np.array([p.valence + p.incumbency_bonus for p in parties])  # (J,)

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


def precompute_demographic_utility_table(
    voter_types: list,
    parties: list,
    type_indices: dict | None = None,
) -> np.ndarray:
    """
    Precompute demographic utility for every (voter type, party) pair.

    Returns (N_types, J) array. Since demographic utility depends only on
    voter-type attributes (education, livelihood, income, etc.) and party
    coefficients — not on LGA data — this table is computed once and reused
    for all LGAs.
    """
    from .voter_types import (
        _build_type_indices, EDUCATIONS, LIVELIHOODS, INCOMES,
        AGE_COHORTS, SETTINGS, GENDERS,
    )

    N = len(voter_types)
    J = len(parties)
    table = np.zeros((N, J))

    if type_indices is None:
        type_indices = _build_type_indices()

    # Map demographic attribute names to (index_key, category_list) for vectorised lookup
    _attr_to_idx = {
        "education":  ("edu", EDUCATIONS),
        "livelihood": ("liv", LIVELIHOODS),
        "income":     ("inc", INCOMES),
        "age_cohort": ("age", AGE_COHORTS),
        "setting":    ("set", SETTINGS),
        "gender":     ("gen", GENDERS),
    }

    for j, party in enumerate(parties):
        if not party.demographic_coefficients:
            continue
        for demo_key, coeff_spec in party.demographic_coefficients.items():
            mapping = _attr_to_idx.get(demo_key)
            if mapping is None:
                continue
            idx_key, categories = mapping
            codes = type_indices[idx_key]  # (N_types,) int32
            if isinstance(coeff_spec, dict):
                # Build value→code lookup for this category
                cat_map = {v: i for i, v in enumerate(categories)}
                for val_str, coeff in coeff_spec.items():
                    code = cat_map.get(val_str)
                    if code is not None:
                        table[codes == code, j] += coeff
            else:
                # Numeric coefficient × numeric attribute (rare)
                vals = np.array(
                    [float(getattr(vt, demo_key, 0)) for vt in voter_types],
                    dtype=float,
                )
                table[:, j] += float(coeff_spec) * vals

    return table


def precompute_all_ethnic_indices(
    voter_types: list,
    ethnic_group_to_idx: dict[str, int],
) -> np.ndarray:
    """
    Precompute ethnic group index for every voter type.

    Returns np.ndarray of shape (N_types,) with integer indices into the
    ethnic utility table.
    """
    return np.array([ethnic_group_to_idx[vt.ethnicity] for vt in voter_types], dtype=np.intp)


def precompute_all_religious_indices(
    voter_types: list,
    religious_group_to_idx: dict[str, int],
) -> np.ndarray:
    """
    Precompute religious group index for every voter type.

    Returns np.ndarray of shape (N_types,) with integer indices into the
    religious utility table.
    """
    return np.array([religious_group_to_idx[vt.religion] for vt in voter_types], dtype=np.intp)


def precompute_fixed_type_utility(
    eth_table: np.ndarray,
    all_eth_indices: np.ndarray,
    rel_table: np.ndarray,
    all_rel_indices: np.ndarray,
    demo_table: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Precompute the LGA-invariant portion of voter-type utility.

    Combines ethnic, religious, and demographic utility into a single
    (N_types, J) array. This avoids 3 separate fancy-index lookups per LGA
    in the hot loop.

    Parameters
    ----------
    eth_table : (N_eth, J) ethnic utility lookup table
    all_eth_indices : (N_types,) integer indices into eth_table
    rel_table : (N_rel, J) religious utility lookup table
    all_rel_indices : (N_types,) integer indices into rel_table
    demo_table : (N_types, J) demographic utility table, optional

    Returns
    -------
    np.ndarray, shape (N_types, J)
    """
    result = eth_table[all_eth_indices]  # (N_types, J)
    result = result + rel_table[all_rel_indices]  # new array to avoid mutating eth_table rows
    if demo_table is not None:
        result += demo_table
    return result


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
    ethnic_utility_table: Optional[tuple[np.ndarray, dict[str, int]]] = None,
    religious_utility_table: Optional[tuple[np.ndarray, dict[str, int]]] = None,
    precomputed_eth_indices: Optional[np.ndarray] = None,
    precomputed_rel_indices: Optional[np.ndarray] = None,
    party_positions: Optional[np.ndarray] = None,
    valences: Optional[np.ndarray] = None,
    has_demographic_coefficients: bool = False,
    precomputed_demo_table: Optional[np.ndarray] = None,
    active_indices: Optional[np.ndarray] = None,
    fixed_type_utility: Optional[np.ndarray] = None,
    _alienation_out: Optional[dict] = None,
) -> np.ndarray:
    """
    Compute full utilities for a batch of voter types × all parties.

    Parameters
    ----------
    voter_ideals : np.ndarray, shape (N, D)
        Ideal points for N voter types.
    voter_ethnicities : list[str], length N
        (ignored if precomputed_eth_indices is provided)
    voter_religions : list[str], length N
        (ignored if precomputed_rel_indices is provided)
    voter_demographics_list : list[dict], length N
        (ignored if has_demographic_coefficients is False)
    parties, params, salience_weights : same as compute_utility
    ethnic_matrix, religious_matrix : optional overrides
    ethnic_utility_table : optional precomputed (table, group_to_idx).
    religious_utility_table : optional precomputed (table, group_to_idx).
    precomputed_eth_indices : optional precomputed int indices into ethnic table.
    precomputed_rel_indices : optional precomputed int indices into religious table.
    party_positions : optional precomputed (J, D) party position array.
    valences : optional precomputed (J,) valence array.
    has_demographic_coefficients : if False, skip demographic utility entirely.

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
    if party_positions is None:
        party_positions = np.array([p.positions for p in parties])
    if valences is None:
        valences = np.array([p.valence + p.incumbency_bonus for p in parties])

    # 2. Spatial utility (N, J) — capture intermediates for alienation reuse
    _spatial_intermediates = {} if _alienation_out is not None else None
    u_spatial = batch_spatial_utility(
        voter_ideals, party_positions,
        beta_s=params.beta_s, q=params.q,
        salience_weights=salience_weights,
        _intermediates=_spatial_intermediates,
    )

    # Compute salience-weighted alienation from spatial intermediates
    # (avoids a second (N,D)@(D,J) matmul in the turnout function)
    if _alienation_out is not None and _spatial_intermediates:
        dot_products = _spatial_intermediates["dot_products"]  # (N, J)
        sq_norms = _spatial_intermediates["sq_norms"]          # (J,)
        wx = _spatial_intermediates["wx"]                      # (N, D)
        J_al = dot_products.shape[1]
        # voter_wsq = Σ_d w_d x_{id}² — use einsum to avoid (N,D) temporaries
        voter_wsq = np.einsum("nd,nd->n", wx, voter_ideals)   # (N,)
        # Column-at-a-time loop: better cache locality than full-array passes
        # because each column (~60KB) fits in L1 cache.
        min_dist_sq = voter_wsq + sq_norms[0] - 2.0 * dot_products[:, 0]
        for j_al in range(1, J_al):
            candidate = voter_wsq + sq_norms[j_al] - 2.0 * dot_products[:, j_al]
            np.minimum(min_dist_sq, candidate, out=min_dist_sq)
        _alienation_out["min_dist_sq"] = min_dist_sq  # (N,)

    # --- Fast path: combined fixed_type_utility table ---
    # When available, ethnic + religious + demographic + valences are already
    # precomputed into a single (N_all_types, J) table, so one fancy index
    # replaces three lookups plus the valence broadcast.
    if fixed_type_utility is not None and active_indices is not None:
        result = u_spatial
        result += fixed_type_utility[active_indices]
        return result

    # --- Fallback: separate ethnic/religious/demographic computation ---
    # 3. Ethnic utility (N, J) — vectorised via precomputed lookup table
    if precomputed_eth_indices is not None and ethnic_utility_table is not None:
        eth_table = ethnic_utility_table[0]
        u_ethnic = eth_table[precomputed_eth_indices]  # (N, J)
    elif ethnic_utility_table is not None:
        eth_table, eth_idx_map = ethnic_utility_table
        eth_indices = np.array([eth_idx_map[e] for e in voter_ethnicities], dtype=np.intp)
        u_ethnic = eth_table[eth_indices]  # (N, J)
    else:
        u_ethnic = np.zeros((N, J))
        for i, eth in enumerate(voter_ethnicities):
            for j, party in enumerate(parties):
                u_ethnic[i, j] = ethnic_matrix.get_utility(
                    eth, party.leader_ethnicity, params.alpha_e
                )

    # 4. Religious utility (N, J) — vectorised via precomputed lookup table
    if precomputed_rel_indices is not None and religious_utility_table is not None:
        rel_table = religious_utility_table[0]
        u_religious = rel_table[precomputed_rel_indices]  # (N, J)
    elif religious_utility_table is not None:
        rel_table, rel_idx_map = religious_utility_table
        rel_indices = np.array([rel_idx_map[r] for r in voter_religions], dtype=np.intp)
        u_religious = rel_table[rel_indices]  # (N, J)
    else:
        u_religious = np.zeros((N, J))
        for i, rel in enumerate(voter_religions):
            for j, party in enumerate(parties):
                u_religious[i, j] = religious_matrix.get_utility(
                    rel, party.religious_alignment, params.alpha_r
                )

    # 5. Demographic utility (N, J) — use precomputed table when available
    result = valences + u_spatial + u_ethnic + u_religious
    if has_demographic_coefficients:
        if precomputed_demo_table is not None and active_indices is not None:
            # Fast path: slice precomputed (N_all_types, J) table by active indices
            result += precomputed_demo_table[active_indices]
        elif precomputed_demo_table is not None:
            # Table provided but no index mapping — use directly (N must match)
            result += precomputed_demo_table[:N]
        else:
            # Slow fallback: triple loop (only used when no precomputation)
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
            result += u_demographic

    return result
