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
    build_voter_ideal_base, compute_lga_ideal_offset,
    compute_all_lga_ideal_offsets, precompute_compat_factors,
    precompute_all_lga_marginals,
    _build_type_indices, EDUCATIONS, AGE_COHORTS, SETTINGS,
)
from .salience import SalienceRule, DEFAULT_SALIENCE_RULES
from .utility import (
    compute_utility, compute_utilities_batch,
    precompute_ethnic_utility_table, precompute_religious_utility_table,
    precompute_all_ethnic_indices, precompute_all_religious_indices,
    precompute_demographic_utility_table, precompute_fixed_type_utility,
)
from .turnout import compute_vote_probs_with_turnout, batch_compute_vote_probs_with_turnout

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

    # Weighted average via BLAS dot: (N,) @ (N, J) → (J,) — avoids (N,J) broadcast
    vote_shares = np.dot(eff_weights, type_vote_probs)
    vote_shares *= 1.0 / total_eff

    # Normalise for numerical safety
    share_sum = vote_shares.sum()
    if share_sum > 0:
        vote_shares *= 1.0 / share_sum

    expected_turnout = float(np.dot(type_weights, type_turnout))

    return vote_shares, expected_turnout


def compute_lga_results(
    lga_row,  # pd.Series or None (None when precomputed_marginals_row provided)
    voter_types: list[VoterType],
    parties: list,              # list[Party]
    params: EngineParams,
    salience_weights: np.ndarray,      # (28,)
    ethnic_matrix: EthnicAffinityMatrix,
    religious_matrix: ReligiousAffinityMatrix,
    ideal_point_coeff_table: list[dict] | None = None,
    precomputed_ideals: np.ndarray | None = None,
    precomputed_compat: np.ndarray | None = None,
    ethnic_utility_table: tuple | None = None,
    religious_utility_table: tuple | None = None,
    type_indices: dict | None = None,
    all_eth_indices: np.ndarray | None = None,
    all_rel_indices: np.ndarray | None = None,
    party_positions: np.ndarray | None = None,
    valences: np.ndarray | None = None,
    has_demographic_coefficients: bool = False,
    voter_ideal_base: np.ndarray | None = None,
    lga_ideal_offset: np.ndarray | None = None,
    precomputed_demo_table: np.ndarray | None = None,
    precomputed_marginals_row: tuple | None = None,
    fixed_type_utility: np.ndarray | None = None,
    party_sq_norms_uniform: np.ndarray | None = None,
) -> tuple[np.ndarray, float, int]:
    """
    Compute vote shares and turnout for one LGA (fully vectorised).

    Parameters
    ----------
    lga_row : pd.Series
    voter_types : list[VoterType]
    parties : list[Party]
    params : EngineParams
    salience_weights : np.ndarray, shape (28,)
    ethnic_matrix, religious_matrix : affinity matrices
    ideal_point_coeff_table : optional coefficient override
    precomputed_ideals : np.ndarray, optional
        (N_types, 28) array of clipped ideal points for this LGA.
    precomputed_compat : np.ndarray, optional
        (N_types,) compat-factor array from precompute_compat_factors().
    ethnic_utility_table : optional precomputed lookup from
        precompute_ethnic_utility_table().
    religious_utility_table : optional precomputed lookup from
        precompute_religious_utility_table().
    type_indices : optional precomputed indices from _build_type_indices().
    all_eth_indices : optional precomputed (N_types,) ethnic group indices.
    all_rel_indices : optional precomputed (N_types,) religious group indices.
    party_positions : optional precomputed (J, D) party positions array.
    valences : optional precomputed (J,) valence array.
    has_demographic_coefficients : if False, skip demographic utility.

    Returns
    -------
    (vote_shares, turnout, n_active_types)
        vote_shares : np.ndarray, shape (J,)
        turnout : float
        n_active_types : int  — number of types with weight > threshold
    """
    J = len(parties)
    if party_positions is None:
        party_positions = np.array([p.positions for p in parties])

    # Step 1: LGA population weights for each type
    type_weights = compute_type_weights(
        lga_row, voter_types, _WEIGHT_THRESHOLD, precomputed_compat, type_indices,
        precomputed_marginals_row=precomputed_marginals_row,
    )

    # Step 2: identify active types (skip near-zero weight to save computation)
    active_idx = np.where(type_weights > _WEIGHT_THRESHOLD)[0]
    n_active = len(active_idx)

    if n_active == 0:
        return np.ones(J) / J, 0.0, 0

    # Step 3: Batch compute ideal points, utilities, turnout for all active types
    if precomputed_ideals is not None:
        active_ideals = precomputed_ideals[active_idx]  # (n_active, 28)
    elif voter_ideal_base is not None and lga_ideal_offset is not None:
        # Only compute ideals for active types — in-place ops avoid temporaries
        active_ideals = voter_ideal_base[active_idx]  # fancy index copy
        active_ideals += lga_ideal_offset              # in-place broadcast add
        np.clip(active_ideals, -5.0, 5.0, out=active_ideals)  # in-place clip
    else:
        active_ideals = np.array([
            demographics_to_ideal_point(voter_types[i], lga_row, ideal_point_coeff_table)
            for i in active_idx
        ])

    # Slice precomputed ethnic/religious indices for active types
    active_eth_idx = all_eth_indices[active_idx] if all_eth_indices is not None else None
    active_rel_idx = all_rel_indices[active_idx] if all_rel_indices is not None else None

    # Build ethnicity/religion string lists only if precomputed indices unavailable
    has_precomputed = (active_eth_idx is not None and ethnic_utility_table is not None
                       and active_rel_idx is not None and religious_utility_table is not None)
    if has_precomputed:
        active_ethnicities = None
        active_religions = None
    else:
        active_ethnicities = [voter_types[i].ethnicity for i in active_idx]
        active_religions = [voter_types[i].religion for i in active_idx]

    # Build demographics list only if needed (skip when precomputed table available)
    if has_demographic_coefficients and precomputed_demo_table is None:
        active_demographics = [
            {"education": voter_types[i].education,
             "age_cohort": voter_types[i].age_cohort,
             "setting": voter_types[i].setting}
            for i in active_idx
        ]
    else:
        active_demographics = None

    # Batch utility computation (N_active, J)
    # Capture salience-weighted alienation from spatial intermediates to
    # avoid a redundant (N, D) @ (D, J) matmul in turnout.
    alienation_out = {}
    utilities_matrix = compute_utilities_batch(
        voter_ideals=active_ideals,
        voter_ethnicities=active_ethnicities,
        voter_religions=active_religions,
        voter_demographics_list=active_demographics,
        parties=parties,
        params=params,
        salience_weights=salience_weights,
        ethnic_matrix=ethnic_matrix,
        religious_matrix=religious_matrix,
        ethnic_utility_table=ethnic_utility_table,
        religious_utility_table=religious_utility_table,
        precomputed_eth_indices=active_eth_idx,
        precomputed_rel_indices=active_rel_idx,
        party_positions=party_positions,
        valences=valences,
        has_demographic_coefficients=has_demographic_coefficients,
        precomputed_demo_table=precomputed_demo_table,
        active_indices=active_idx,
        fixed_type_utility=fixed_type_utility,
        _alienation_out=alienation_out,
    )
    precomputed_alienation = alienation_out.get("min_dist_sq")

    # Slice integer-coded demographic arrays for batch turnout
    if type_indices is not None:
        edu_codes = type_indices["edu"][active_idx]
        age_codes = type_indices["age"][active_idx]
        set_codes = type_indices["set"][active_idx]
    else:
        edu_map = {e: i for i, e in enumerate(EDUCATIONS)}
        age_map = {a: i for i, a in enumerate(AGE_COHORTS)}
        set_map = {s: i for i, s in enumerate(SETTINGS)}
        edu_codes = np.array([edu_map[voter_types[i].education] for i in active_idx], dtype=np.int32)
        age_codes = np.array([age_map[voter_types[i].age_cohort] for i in active_idx], dtype=np.int32)
        set_codes = np.array([set_map[voter_types[i].setting] for i in active_idx], dtype=np.int32)

    # Batch turnout computation
    active_vote_probs, active_turnout = batch_compute_vote_probs_with_turnout(
        utilities_matrix=utilities_matrix,
        voter_ideals=active_ideals,
        party_positions=party_positions,
        params=params,
        educations=edu_codes,
        age_cohorts=age_codes,
        settings=set_codes,
        party_sq_norms_uniform=party_sq_norms_uniform,
        precomputed_min_dist_sq=precomputed_alienation,
    )

    # Step 4: Aggregate (only active types contribute; inactive have zero weight)
    active_weights = type_weights[active_idx]
    vote_shares, turnout = aggregate_to_lga(active_weights, active_vote_probs, active_turnout)

    return vote_shares, turnout, n_active


def compute_all_lga_results(
    lga_data: pd.DataFrame,
    election_config: ElectionConfig,
    ethnic_matrix: EthnicAffinityMatrix | None = None,
    religious_matrix: ReligiousAffinityMatrix | None = None,
    salience_rules: list[SalienceRule] | None = None,
    ideal_point_coeff_table: list[dict] | None = None,
    precomputed_salience: np.ndarray | None = None,
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
    precomputed_salience : np.ndarray, optional
        (N_lga, 28) pre-computed salience weights. If provided, skips
        salience computation (avoids duplicate work when called from
        election.py which already computed salience).

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

    # Precompute voter-type-invariant quantities (done once, shared across all LGAs)
    # Float32 for large arrays used in BLAS matmul (4x faster than float64).
    voter_ideal_base = build_voter_ideal_base(voter_types, ideal_point_coeff_table)
    voter_ideal_base = voter_ideal_base.astype(np.float32)
    compat_factors = precompute_compat_factors(voter_types).astype(np.float32)
    type_indices = _build_type_indices()

    # Precompute ethnic/religious utility lookup tables (avoids dict lookups per voter)
    eth_table = precompute_ethnic_utility_table(parties, params, ethnic_matrix)
    rel_table = precompute_religious_utility_table(parties, params, religious_matrix)

    # Precompute ethnic/religious integer index arrays for all voter types
    all_eth_indices = precompute_all_ethnic_indices(voter_types, eth_table[1])
    all_rel_indices = precompute_all_religious_indices(voter_types, rel_table[1])

    # Precompute party arrays (avoid recreating per LGA)
    party_positions = np.array([p.positions for p in parties])  # (J, 28)
    party_positions_f32 = party_positions.astype(np.float32)
    valences = np.array([p.valence for p in parties], dtype=np.float32)  # (J,)
    D = party_positions.shape[1]
    party_sq_norms_uniform = np.sum(party_positions ** 2, axis=1) / D  # (J,)
    has_demo_coeffs = any(p.demographic_coefficients for p in parties)

    # Precompute demographic utility table (N_types, J) — avoids triple loop per LGA
    demo_table = (precompute_demographic_utility_table(voter_types, parties)
                  if has_demo_coeffs else None)

    # Precompute combined fixed-type utility (ethnic + religious + demographic)
    # into a single (N_types, J) table — replaces 3 fancy-index lookups per LGA
    # with a single one.
    fixed_type_utility = precompute_fixed_type_utility(
        eth_table=eth_table[0],
        all_eth_indices=all_eth_indices,
        rel_table=rel_table[0],
        all_rel_indices=all_rel_indices,
        demo_table=demo_table,
    ).astype(np.float32)

    # Use pre-computed salience if provided; otherwise compute here
    if precomputed_salience is not None:
        salience_matrix = precomputed_salience
    else:
        from .salience import compute_all_lga_salience
        national_median_gdp = float(lga_data["GDP Per Capita Est"].median())
        salience_matrix = compute_all_lga_salience(
            lga_data, rules=salience_rules, national_median_gdp=national_median_gdp
        )
    salience_matrix = salience_matrix.astype(np.float32)

    # Precompute all LGA ideal offsets (vectorised over LGAs) — float32 for fast ops
    all_lga_offsets = compute_all_lga_ideal_offsets(lga_data, ideal_point_coeff_table)
    all_lga_offsets = all_lga_offsets.astype(np.float32)

    # Precompute all LGA demographic marginals (eliminates per-LGA pd.Series.get())
    all_marginals = precompute_all_lga_marginals(lga_data)

    # Pre-extract metadata columns as numpy arrays to avoid df.iloc per LGA
    n_lgas = len(lga_data)
    _col_state = lga_data["State"].values if "State" in lga_data.columns else [""] * n_lgas
    _col_lga = lga_data["LGA Name"].values if "LGA Name" in lga_data.columns else [""] * n_lgas
    _col_az = lga_data["Administrative Zone"].values if "Administrative Zone" in lga_data.columns else np.zeros(n_lgas, dtype=int)
    _col_azn = lga_data["AZ Name"].values if "AZ Name" in lga_data.columns else [""] * n_lgas
    _col_pop = lga_data["Estimated Population"].values.astype(float) if "Estimated Population" in lga_data.columns else np.zeros(n_lgas)

    # Pre-allocate output arrays for vote shares and turnout
    all_vote_shares = np.empty((n_lgas, J))
    all_turnout = np.empty(n_lgas)
    all_n_active = np.empty(n_lgas, dtype=int)

    for idx in range(n_lgas):
        salience_w = salience_matrix[idx]
        lga_ideal_offset = all_lga_offsets[idx]
        marginals_row = (
            all_marginals["eth"][idx],
            all_marginals["rel"][idx],
            all_marginals["set"][idx],
            all_marginals["edu"][idx],
            all_marginals["liv"][idx],
            all_marginals["inc"][idx],
        )

        vote_shares, turnout, n_active = compute_lga_results(
            lga_row=None,
            voter_types=voter_types,
            parties=parties,
            params=params,
            salience_weights=salience_w,
            ethnic_matrix=ethnic_matrix,
            religious_matrix=religious_matrix,
            ideal_point_coeff_table=ideal_point_coeff_table,
            precomputed_compat=compat_factors,
            ethnic_utility_table=eth_table,
            religious_utility_table=rel_table,
            type_indices=type_indices,
            all_eth_indices=all_eth_indices,
            all_rel_indices=all_rel_indices,
            party_positions=party_positions,
            valences=valences,
            has_demographic_coefficients=has_demo_coeffs,
            voter_ideal_base=voter_ideal_base,
            lga_ideal_offset=lga_ideal_offset,
            precomputed_demo_table=demo_table,
            precomputed_marginals_row=marginals_row,
            fixed_type_utility=fixed_type_utility,
            party_sq_norms_uniform=party_sq_norms_uniform,
        )

        all_vote_shares[idx] = vote_shares
        all_turnout[idx] = turnout
        all_n_active[idx] = n_active

        if (idx + 1) % 100 == 0:
            logger.info("Processed %d / %d LGAs", idx + 1, n_lgas)

    # Build DataFrame from pre-extracted columns + computed arrays (no per-row dicts)
    result_dict = {
        "State": _col_state,
        "LGA Name": _col_lga,
        "Administrative Zone": _col_az,
        "AZ Name": _col_azn,
        "Estimated Population": _col_pop,
        "Turnout": all_turnout,
        "Active Types": all_n_active,
    }
    for j, party in enumerate(parties):
        result_dict[f"{party.name}_share"] = all_vote_shares[:, j]

    return pd.DataFrame(result_dict)
