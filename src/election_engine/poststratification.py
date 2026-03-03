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
from .spatial import batch_spatial_utility
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
    # Float32 BLAS for the (N,) @ (N, J) dot product — 2x faster than float64.
    # Cast inputs to float32; the final J-length vote_shares are promoted to
    # float64 for output.  Precision loss is negligible: ~1e-5 for 15k terms.
    tw32 = np.asarray(type_weights, dtype=np.float32)
    tt32 = np.asarray(type_turnout, dtype=np.float32)
    vp32 = np.asarray(type_vote_probs, dtype=np.float32)

    eff_weights = tw32 * tt32   # (N_types,) float32
    total_eff = float(eff_weights.sum())

    if total_eff < 1e-12:
        J = type_vote_probs.shape[1]
        return np.ones(J) / J, 0.0

    # BLAS dot in float32: (N,) @ (N, J) → (J,)
    vote_shares = np.dot(eff_weights, vp32)
    vote_shares *= np.float32(1.0 / total_eff)

    # Normalise for numerical safety
    share_sum = float(vote_shares.sum())
    if share_sum > 0:
        vote_shares *= np.float32(1.0 / share_sum)

    # Promote final J-length result to float64
    vote_shares = vote_shares.astype(np.float64)
    expected_turnout = float(np.dot(tw32, tt32))

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
    turnout_demo_adjust: np.ndarray | None = None,
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
    active_demo_adj = None
    if turnout_demo_adjust is not None:
        active_demo_adj = turnout_demo_adjust[active_idx]
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
        precomputed_demo_adjust=active_demo_adj,
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
    type_indices = _build_type_indices()
    voter_ideal_base = build_voter_ideal_base(voter_types, ideal_point_coeff_table)
    voter_ideal_base = voter_ideal_base.astype(np.float32)
    compat_factors = precompute_compat_factors(voter_types, type_indices).astype(np.float32)

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
    demo_table = (precompute_demographic_utility_table(voter_types, parties, type_indices)
                  if has_demo_coeffs else None)

    # Precompute combined fixed-type utility (ethnic + religious + demographic)
    # into a single (N_types, J) table — replaces 3 fancy-index lookups per LGA
    # with a single one.  Valences are pre-baked in so the hot loop needs only
    # one fancy-index + add instead of two.
    fixed_type_utility = precompute_fixed_type_utility(
        eth_table=eth_table[0],
        all_eth_indices=all_eth_indices,
        rel_table=rel_table[0],
        all_rel_indices=all_rel_indices,
        demo_table=demo_table,
    ).astype(np.float32)
    # Pre-bake valence (broadcasts (J,) over rows)
    fixed_type_utility += valences

    # Separate identity utility tables for LGA-level context modifiers.
    # These allow per-LGA amplification/dampening of ethnic and religious
    # voting based on local conditions (fragmentation, tension, urbanization).
    # The base identity effect is already in fixed_type_utility; these tables
    # carry the raw identity utility so modifiers can scale them per LGA.
    eth_only_utility = eth_table[0][all_eth_indices].astype(np.float32)  # (N_types, J)
    rel_only_utility = rel_table[0][all_rel_indices].astype(np.float32)  # (N_types, J)

    # Precompute turnout demographic adjustment per voter type (replaces
    # boolean-mask operations per LGA with a single fancy-index + add).
    turnout_demo_adjust = np.zeros(len(voter_types), dtype=np.float32)
    # Education
    turnout_demo_adjust[type_indices["edu"] == 2] -= 1.0   # Tertiary
    turnout_demo_adjust[type_indices["edu"] == 0] += 0.3   # Below secondary
    # Age
    turnout_demo_adjust[type_indices["age"] == 3] -= 0.5   # 50+
    turnout_demo_adjust[type_indices["age"] == 0] += 0.2   # 18-24
    # Setting
    turnout_demo_adjust[type_indices["set"] == 0] -= 0.2   # Urban
    # Livelihood
    turnout_demo_adjust[type_indices["liv"] == 4] -= 0.4   # Public sector: high awareness
    turnout_demo_adjust[type_indices["liv"] == 3] -= 0.2   # Formal private: somewhat engaged
    turnout_demo_adjust[type_indices["liv"] == 5] += 0.3   # Unemployed/student: disengaged
    turnout_demo_adjust[type_indices["liv"] == 0] += 0.1   # Smallholder: harder access
    # Income
    turnout_demo_adjust[type_indices["inc"] == 2] -= 0.3   # Top 20%: more stake
    turnout_demo_adjust[type_indices["inc"] == 0] += 0.2   # Bottom 40%: barriers
    # Gender: base gap (modulated per-LGA below via gender_turnout_gap)
    turnout_demo_adjust[type_indices["gen"] == 1] += 0.05  # Female: small base gap

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

    # Precompute regional stronghold bonus matrix: (n_lga, J) float32.
    # Each entry is the additive utility bonus for party j in this LGA's AZ.
    _has_regional = any(p.regional_strongholds for p in parties)
    if _has_regional:
        az_numbers = lga_data["Administrative Zone"].values.astype(int)
        regional_bonus_matrix = np.zeros((n_lgas, J), dtype=np.float32)
        for j, party in enumerate(parties):
            if party.regional_strongholds:
                for az_num, bonus in party.regional_strongholds.items():
                    mask = az_numbers == int(az_num)
                    regional_bonus_matrix[mask, j] = bonus
    else:
        regional_bonus_matrix = None

    # Precompute economic voting modifier: (n_lga, J) float32.
    # grievance_z is z-scored composite of poverty, unemployment, inverse GDP.
    # Modifier = party.economic_positioning × grievance_z × beta_econ.
    _has_econ = params.beta_econ > 0 and any(p.economic_positioning != 0 for p in parties)
    if _has_econ:
        _pov = lga_data["Poverty Rate Pct"].fillna(30.0).values.astype(float) if "Poverty Rate Pct" in lga_data.columns else np.full(n_lgas, 30.0)
        _unemp = lga_data["Unemployment Rate Pct"].fillna(15.0).values.astype(float) if "Unemployment Rate Pct" in lga_data.columns else np.full(n_lgas, 15.0)
        _gdp = lga_data["GDP Per Capita Est"].fillna(18000.0).values.astype(float) if "GDP Per Capita Est" in lga_data.columns else np.full(n_lgas, 18000.0)
        # Composite: higher poverty + higher unemployment + lower GDP = more grievance
        _grievance_raw = (_pov / 100.0) + (_unemp / 100.0) + (1.0 - np.clip(_gdp / 50000.0, 0, 1))
        _g_mean = _grievance_raw.mean()
        _g_std = max(_grievance_raw.std(), 1e-6)
        grievance_z = ((_grievance_raw - _g_mean) / _g_std).astype(np.float32)
        econ_positions = np.array([p.economic_positioning for p in parties], dtype=np.float32)
        # econ_bonus[c, j] = beta_econ × econ_positions[j] × grievance_z[c]
        econ_bonus_matrix = np.float32(params.beta_econ) * np.outer(grievance_z, econ_positions)
    else:
        econ_bonus_matrix = None

    # Precompute LGA-level turnout modifier: (n_lga,) float32.
    # Adjusts abstention utility based on local conditions that affect
    # ALL voter types in that LGA (infrastructure, conflict, literacy, etc.).
    # Positive = more abstention, negative = less abstention.
    def _lga_col(name, default=0.0):
        if name in lga_data.columns:
            return lga_data[name].fillna(default).values.astype(float)
        return np.full(n_lgas, default)

    # Poor road quality makes it harder to reach polling stations
    _road_qi = _lga_col("Road Quality Index", 5.0)
    _lga_turnout_mod = 0.3 * np.maximum(0.0, 1.0 - _road_qi / 10.0)  # max +0.3

    # Conflict zones: insecurity deters turnout
    _conflict = _lga_col("Conflict History", 0.0)
    _lga_turnout_mod += 0.15 * np.clip(_conflict / 5.0, 0.0, 1.0)  # max +0.15

    # Low literacy: less political engagement
    _literacy = _lga_col("Adult Literacy Rate Pct", 50.0)
    _lga_turnout_mod += 0.3 * np.maximum(0.0, 1.0 - _literacy / 100.0)  # max +0.3

    # High mobile penetration: better information, easier logistics
    _mobile = _lga_col("Mobile Phone Penetration Pct", 50.0)
    _lga_turnout_mod -= 0.2 * np.clip(_mobile / 100.0, 0.0, 1.0)  # max -0.2

    # Federal control zones: military presence may suppress or boost turnout
    _fed_ctrl = _lga_col("Federal Control 2058", 0.0)
    _lga_turnout_mod += 0.1 * _fed_ctrl  # federal control zones have slightly lower turnout

    # Economic grievance effects on turnout:
    # High poverty → mixed: can mobilise but also fatalism/barriers
    _poverty = _lga_col("Poverty Rate Pct", 30.0)
    _lga_turnout_mod += 0.15 * np.clip((_poverty - 30.0) / 35.0, 0.0, 1.0)  # above-average poverty

    # High unemployment → disengagement and disillusionment
    _unemp = _lga_col("Unemployment Rate Pct", 24.0)
    _lga_turnout_mod += 0.1 * np.clip((_unemp - 24.0) / 43.0, 0.0, 1.0)  # above-average

    # High youth unemployment → youth disengagement but also protest potential
    _youth_unemp = _lga_col("Youth Unemployment Rate Pct", 46.0)
    _lga_turnout_mod += 0.1 * np.clip((_youth_unemp - 46.0) / 34.0, 0.0, 1.0)

    # High inequality (Gini) → can mobilise grievance voting
    _gini = _lga_col("Gini Proxy", 0.36)
    _lga_turnout_mod -= 0.1 * np.clip((_gini - 0.36) / 0.24, 0.0, 1.0)  # inequality mobilises

    # Extraction economy → politically engaged (resource curse mobilisation)
    _extract_int = _lga_col("Extraction Intensity", 0.0)
    _lga_turnout_mod -= 0.1 * np.clip(_extract_int / 5.0, 0.0, 1.0)  # extraction mobilises

    # Al-Shahid Influence: dual effect — intimidation suppresses turnout
    # but also mobilises supporters. Net effect: mild suppression.
    _al_shahid_t = _lga_col("Al-Shahid Influence", 0.0)
    _lga_turnout_mod += 0.15 * np.clip(_al_shahid_t / 5.0, 0.0, 1.0)  # insecurity → abstention

    # Almajiri Index: high almajiri presence → disengaged male youth
    _almajiri = _lga_col("Almajiri Index", 0.0)
    _lga_turnout_mod += 0.15 * np.clip(_almajiri / 5.0, 0.0, 1.0)  # youth disengagement

    # Traditional Authority Index: strong traditional authority → mobilisation
    # through patron-client networks (chiefs direct voting)
    _trad_auth = _lga_col("Trad Authority Index", 0.0)
    _lga_turnout_mod -= 0.15 * np.clip(_trad_auth / 5.0, 0.0, 1.0)  # chiefs mobilise turnout

    # Internet access: informed citizens more likely to vote
    _internet = _lga_col("Internet Access Pct", 60.0)
    _lga_turnout_mod -= 0.1 * np.clip(_internet / 100.0, 0.0, 1.0)

    # Terrain difficulty: hard-to-reach terrain → harder to get to polls
    # Montane, mangrove/freshwater swamp, sahel → higher abstention
    if "Terrain Type" in lga_data.columns:
        _terrain = lga_data["Terrain Type"].fillna("").astype(str).str.lower().values
        _terrain_penalty = np.zeros(n_lgas)
        for _i, _t in enumerate(_terrain):
            if "montane" in _t:
                _terrain_penalty[_i] = 0.15  # mountainous: very hard to reach
            elif "mangrove" in _t:
                _terrain_penalty[_i] = 0.12  # mangrove: waterway access
            elif "freshwater" in _t:
                _terrain_penalty[_i] = 0.1   # freshwater swamp: flooding
            elif "sahel" in _t:
                _terrain_penalty[_i] = 0.08  # sahel: long distances, sparse population
        _lga_turnout_mod += _terrain_penalty

    # Planned City: well-organized infrastructure → easy polling
    _planned = _lga_col("Planned City", 0.0)
    _lga_turnout_mod -= 0.1 * _planned  # planned cities have better logistics

    # Rail corridor: better connectivity → easier to reach polls
    _rail = _lga_col("Rail Corridor", 0.0)
    _lga_turnout_mod -= 0.05 * np.clip(_rail / 2.0, 0.0, 1.0)

    lga_turnout_modifier = _lga_turnout_mod.astype(np.float32)

    # ---- Identity context modifiers ----
    # Per-LGA scalars that amplify/dampen ethnic and religious voting
    # based on local conditions. Applied as:
    #   u_total += rel_context_mod[c] * rel_only_utility[active_types]
    #   u_total += eth_context_mod[c] * eth_only_utility[active_types]
    # This makes identity voting context-dependent: stronger in contested
    # areas, weaker in homogeneous/cosmopolitan ones.

    # Religious context modifier:
    #   (+) Mixed Muslim-Christian areas → religious identity more salient
    #   (+) Al-Shahid influence → polarisation amplifies religious voting
    #   (+) Pentecostal growth → evangelical mobilisation amplifies religious voting
    #   (-) Urbanisation → secularisation dampens religious voting
    _pct_muslim = _lga_col("% Muslim", 30.0)
    _pct_christian = _lga_col("% Christian", 30.0)
    _al_shahid_inf = _lga_col("Al-Shahid Influence", 0.0)
    _pent_growth = _lga_col("Pentecostal Growth", 0.0)
    _urban_pct_id = _lga_col("Urban Pct", 30.0)

    _rel_tension = (_pct_muslim * _pct_christian) / 2500.0  # 0-1 scale, peaks at 50/50
    _internet_id = _lga_col("Internet Access Pct", 60.0)
    _literacy_id = _lga_col("Adult Literacy Rate Pct", 50.0)
    _almajiri_id = _lga_col("Almajiri Index", 0.0)
    _trad_auth_id = _lga_col("Trad Authority Index", 0.0)
    _market_access_id = _lga_col("Market Access Index", 5.0)
    _pop_density_id = _lga_col("Population Density per km2", 200.0)
    _secondary_enr_id = _lga_col("Secondary Enrollment Pct", 50.0)

    rel_context_modifier = (
        0.3 * _rel_tension                              # mixed areas: religion more salient
        + 0.15 * np.clip(_al_shahid_inf / 5.0, 0, 1)   # Al-Shahid: polarises
        + 0.1 * np.clip(_pent_growth / 3.0, 0, 1)       # Pentecostal growth: mobilises
        + 0.12 * np.clip(_almajiri_id / 5.0, 0, 1)      # Almajiri: amplifies religious identity
        + 0.08 * np.clip(_trad_auth_id / 5.0, 0, 1)     # Traditional authority reinforces religious norms
        - 0.15 * np.clip(_urban_pct_id / 100.0, 0, 1)   # urban: secularisation
        - 0.1 * np.clip(_internet_id / 100.0, 0, 1)     # internet: cosmopolitan exposure
        - 0.08 * np.clip(_literacy_id / 100.0, 0, 1)    # literacy: reduces identity politics
        - 0.05 * np.clip(_secondary_enr_id / 100.0, 0, 1)  # education: cross-group contact
    ).astype(np.float32)

    # Ethnic context modifier:
    #   (+) Ethnic fragmentation → more competition, ethnicity more salient
    #   (+) Conflict zones → ethnic mobilisation
    #   (-) Urbanisation → cosmopolitan, ethnicity less salient
    _eth_share_cols = [
        "Hausa", "Fulani", "Yoruba", "Igbo", "Ijaw", "Kanuri",
        "Tiv", "Nupe", "Edo", "Ibibio", "Pada", "Naijin",
    ]
    _eth_shares_sq_sum = np.zeros(n_lgas)
    _eth_shares_total = np.zeros(n_lgas)
    for g in _eth_share_cols:
        col_name = f"% {g}"
        if col_name in lga_data.columns:
            s = lga_data[col_name].fillna(0).values.astype(float) / 100.0
        else:
            s = np.zeros(n_lgas)
        _eth_shares_sq_sum += s ** 2
        _eth_shares_total += s
    # "Other ethnic" residual
    _other_eth = np.clip(1.0 - _eth_shares_total, 0.0, 1.0)
    _eth_shares_sq_sum += _other_eth ** 2
    _eth_frag = 1.0 - _eth_shares_sq_sum  # 0 = homogeneous, ~0.9 = very fragmented

    _conflict_id = _lga_col("Conflict History", 0.0)
    eth_context_modifier = (
        0.25 * np.clip(_eth_frag, 0, 1)                 # fragmented: ethnicity more salient
        + 0.1 * np.clip(_conflict_id / 5.0, 0, 1)       # conflict: ethnic mobilisation
        + 0.1 * np.clip(_trad_auth_id / 5.0, 0, 1)      # traditional authority reinforces ethnic identity
        + 0.08 * np.clip(_almajiri_id / 5.0, 0, 1)      # Almajiri networks reinforce ethnic bonds
        - 0.1 * np.clip(_urban_pct_id / 100.0, 0, 1)    # urban: Allport contact hypothesis
        - 0.08 * np.clip(_internet_id / 100.0, 0, 1)    # internet: exposure to cosmopolitan norms
        - 0.06 * np.clip(_literacy_id / 100.0, 0, 1)    # literacy: reduces ethnic voting
        - 0.05 * np.clip(_market_access_id / 10.0, 0, 1)  # connected areas: less insular
        - 0.04 * np.clip(np.log1p(_pop_density_id) / 8.0, 0, 1)  # dense areas: more cross-group contact
    ).astype(np.float32)

    # ---- LGA-modulated gender turnout gap ----
    # The gender gap in turnout varies dramatically across Nigeria:
    # conservative northern areas (high almajiri, low female literacy, Al-Shahid)
    # have a much larger gap than progressive southern urban areas.
    # Shape: (n_lga,) — added to female voters' abstention utility per LGA.
    _fem_lit = _lga_col("Female Literacy Rate Pct", 50.0)
    _male_lit = _lga_col("Male Literacy Rate Pct", 50.0)
    _lit_gap = np.maximum(0.0, _male_lit - _fem_lit)  # male-female literacy gap
    _gpi = _lga_col("Gender Parity Index", 1.0)

    gender_turnout_gap = (
        0.15 * np.clip(_almajiri_id / 5.0, 0.0, 1.0)      # Almajiri: female exclusion
        + 0.1 * np.clip(_al_shahid_inf / 5.0, 0.0, 1.0)   # Al-Shahid: purdah enforcement
        + 0.1 * np.clip(_lit_gap / 40.0, 0.0, 1.0)         # Literacy gap: female disadvantage
        + 0.05 * np.maximum(0.0, 1.0 - _gpi)                # Gender parity gap
        - 0.1 * np.clip(_urban_pct_id / 100.0, 0.0, 1.0)   # Urbanisation: narrows gap
        - 0.05 * np.clip(_internet_id / 100.0, 0.0, 1.0)   # Internet: female empowerment
    ).astype(np.float32)

    # ---- Religious minority mobilisation (turnout interaction) ----
    # Per-LGA, per-religion turnout adjustment. Religious minorities
    # in an LGA are more politically mobilised (defensive voting:
    # "we must turn out or the other side dominates"), while comfortable
    # majorities have slight complacency.
    # Shape: (n_lga, 9) — one value per religious sub-category per LGA.
    # Applied to abstention utility: negative = lower abstention = higher turnout.
    #
    # Religion codes: Muslim=0-3, Christian=4-6, Trad=7, Secular=8
    minority_mobilisation = np.zeros((n_lgas, 9), dtype=np.float32)

    # Muslim voters in Christian-dominant areas → mobilised
    _muslim_minority = (_pct_muslim < 40) & (_pct_christian > 40)
    # Stronger mobilisation for larger minorities (they feel competitive)
    _muslim_mob = np.where(
        _muslim_minority,
        -0.25 * np.clip(_pct_muslim / 30.0, 0.0, 1.0),
        0.0,
    )
    # Muslim voters in Muslim-dominant areas → slight complacency
    _muslim_mob += np.where(_pct_muslim > 60, 0.1, 0.0)
    # Mixed areas (neither dominant): mild mobilisation on both sides
    _muslim_mixed = ~_muslim_minority & (_pct_muslim <= 60) & (_pct_muslim > 10)
    _muslim_mob += np.where(_muslim_mixed, -0.1, 0.0)

    for _code in range(4):  # Tijaniyya, Qadiriyya, Al-Shahid, Mainstream Sunni
        minority_mobilisation[:, _code] = _muslim_mob

    # Christian voters in Muslim-dominant areas → mobilised
    _christian_minority = (_pct_christian < 40) & (_pct_muslim > 40)
    _christian_mob = np.where(
        _christian_minority,
        -0.25 * np.clip(_pct_christian / 30.0, 0.0, 1.0),
        0.0,
    )
    # Christian voters in Christian-dominant areas → slight complacency
    _christian_mob += np.where(_pct_christian > 60, 0.1, 0.0)
    # Mixed areas
    _christian_mixed = ~_christian_minority & (_pct_christian <= 60) & (_pct_christian > 10)
    _christian_mob += np.where(_christian_mixed, -0.1, 0.0)

    for _code in range(4, 7):  # Pentecostal, Catholic, Mainline Protestant
        minority_mobilisation[:, _code] = _christian_mob

    # Pentecostal mobilisation bonus: Pentecostal churches actively mobilise
    # their members to vote as a bloc, regardless of majority/minority status.
    # This adds to any existing minority mobilisation effect for Pentecostals.
    _pent_turnout = _lga_col("Pentecostal Growth", 0.0)
    minority_mobilisation[:, 4] -= np.float32(0.1) * np.clip(
        _pent_turnout / 3.0, 0.0, 1.0
    ).astype(np.float32)  # Pentecostal: church-led voter mobilisation

    # Traditionalists: generally marginalised small group
    _pct_trad = _lga_col("% Traditionalist", 5.0)
    minority_mobilisation[:, 7] = np.where(
        _pct_trad > 5, np.float32(-0.05), np.float32(0.05)
    )
    # Secular: mostly unaffected by religious mobilisation
    # (already captured in education/urban turnout adjustments)

    # Pre-allocate output arrays for vote shares and turnout
    all_vote_shares = np.empty((n_lgas, J))
    all_turnout = np.empty(n_lgas)
    all_n_active = np.empty(n_lgas, dtype=int)

    # Pre-extract marginals arrays for inner loop (avoids dict lookup per LGA)
    _marg_eth = all_marginals["eth"]
    _marg_rel = all_marginals["rel"]
    _marg_set = all_marginals["set"]
    _marg_edu = all_marginals["edu"]
    _marg_liv = all_marginals["liv"]
    _marg_inc = all_marginals["inc"]

    # Pre-extract type_indices arrays (avoids dict lookup per LGA)
    _idx_edu = type_indices["edu"]
    _idx_age = type_indices["age"]
    _idx_set = type_indices["set"]
    _idx_rel = type_indices["rel"]
    _idx_gen = type_indices["gen"]

    # Cache frequently-used scalars
    _beta_s = np.float32(params.beta_s)
    _q_half = np.float32(params.q / 2.0)

    # Pre-allocate reusable buffers for per-LGA spatial/alienation/turnout.
    # Sized for the maximum possible active types; sliced to n_active per LGA.
    # This avoids per-LGA numpy memory allocation which adds ~1ms/LGA.
    N_types = len(voter_types)
    _wx_buf = np.empty((N_types, D), dtype=np.float32)
    _dot_buf = np.empty((N_types, J), dtype=np.float32)
    _voter_wsq_buf = np.empty(N_types, dtype=np.float32)
    _min_dist_buf = np.empty(N_types, dtype=np.float32)
    _candidate_buf = np.empty(N_types, dtype=np.float32)

    # Identity context buffers (reused across LGA iterations)
    _id_buf = np.empty((N_types, J), dtype=np.float32)

    # Turnout buffers (reused across all LGA iterations)
    _exp_NJ = np.empty((N_types, J), dtype=np.float32)
    _top1 = np.empty(N_types, dtype=np.float32)
    _row_sum = np.empty(N_types, dtype=np.float32)
    _sum_exp = np.empty(N_types, dtype=np.float32)
    _tmp = np.empty(N_types, dtype=np.float32)
    _v_abstain = np.empty(N_types, dtype=np.float32)

    # Cache scalar params as float32 to avoid repeated conversion
    _tau_0 = np.float32(params.tau_0)
    _tau_1 = np.float32(params.tau_1)
    _tau_2 = np.float32(params.tau_2)
    _scale_f32 = np.float32(params.scale)
    _inv_Jm1 = np.float32(1.0 / (J - 1)) if J >= 2 else np.float32(1.0)
    _EPSILON_F32 = np.float32(1e-6)
    _ONE_F32 = np.float32(1.0)
    _ZERO_F32 = np.float32(0.0)
    _TURNOUT_EPS = np.float32(1e-30)

    # Pre-compute transposed party positions for fast matmul
    pp_T = np.ascontiguousarray(party_positions_f32.T)  # (D, J) contiguous

    # Inline per-LGA hotloop with pre-allocated buffers.
    for idx in range(n_lgas):
        salience_w = salience_matrix[idx]
        lga_offset = all_lga_offsets[idx]
        marginals_row = (_marg_eth[idx], _marg_rel[idx], _marg_set[idx],
                         _marg_edu[idx], _marg_liv[idx], _marg_inc[idx])

        # Step 1: Type weights
        tw = compute_type_weights(
            None, voter_types, _WEIGHT_THRESHOLD, compat_factors, type_indices,
            precomputed_marginals_row=marginals_row,
        )

        # Step 2: Active types
        active_idx = np.where(tw > _WEIGHT_THRESHOLD)[0]
        n_active = len(active_idx)
        if n_active == 0:
            all_vote_shares[idx] = 1.0 / J
            all_turnout[idx] = 0.0
            all_n_active[idx] = 0
            continue

        # Step 3: Ideal points (in-place add + clip)
        active_ideals = voter_ideal_base[active_idx]
        active_ideals += lga_offset
        np.clip(active_ideals, -5.0, 5.0, out=active_ideals)

        # Step 4: Spatial utility (inlined with pre-allocated buffers)
        wx = _wx_buf[:n_active]
        np.multiply(active_ideals, salience_w, out=wx)
        dot_products = _dot_buf[:n_active]
        np.dot(wx, pp_T, out=dot_products)
        sq_norms = (party_positions_f32 ** 2) @ salience_w

        # Step 5: Alienation from UNSCALED dot products
        voter_wsq = _voter_wsq_buf[:n_active]
        np.einsum("nd,nd->n", wx, active_ideals, out=voter_wsq)
        min_dist_sq = _min_dist_buf[:n_active]
        np.subtract(voter_wsq, 2.0 * dot_products[:, 0], out=min_dist_sq)
        min_dist_sq += sq_norms[0]
        candidate = _candidate_buf[:n_active]
        for j_al in range(1, J):
            np.subtract(voter_wsq, 2.0 * dot_products[:, j_al], out=candidate)
            candidate += sq_norms[j_al]
            np.minimum(min_dist_sq, candidate, out=min_dist_sq)

        # Convert dot_products to spatial utility in-place
        dot_products -= _q_half * sq_norms
        dot_products *= _beta_s

        # Step 6: Total utility = spatial + fixed (ethnic+religious+valence)
        dot_products += fixed_type_utility[active_idx]
        # Add regional stronghold bonus (per-AZ, per-party)
        if regional_bonus_matrix is not None:
            dot_products += regional_bonus_matrix[idx]  # broadcasts (J,) over rows
        # Add economic voting modifier (pro-poor parties boosted in distressed LGAs)
        if econ_bonus_matrix is not None:
            dot_products += econ_bonus_matrix[idx]  # broadcasts (J,) over rows

        # Identity context modifiers: amplify/dampen ethnic and religious
        # utility based on local LGA conditions. The base identity effect is
        # already in fixed_type_utility; these add a context-dependent delta.
        # Uses pre-allocated buffer and np.take to avoid per-LGA allocations.
        id_buf = _id_buf[:n_active]
        np.take(rel_only_utility, active_idx, axis=0, out=id_buf)
        id_buf *= rel_context_modifier[idx]
        dot_products += id_buf
        np.take(eth_only_utility, active_idx, axis=0, out=id_buf)
        id_buf *= eth_context_modifier[idx]
        dot_products += id_buf

        u_total = dot_products  # alias — (n_active, J) total utilities

        # Step 7: Inlined turnout computation (eliminates function call +
        # 3 wasted fancy-index ops + intermediate array allocations)
        exp_parties = _exp_NJ[:n_active]
        top1 = _top1[:n_active]
        row_sum = _row_sum[:n_active]
        sum_exp = _sum_exp[:n_active]
        tmp = _tmp[:n_active]
        v_abstain = _v_abstain[:n_active]

        # 7a. Indifference gap (in-place, reuses row_sum for gap)
        np.copyto(top1, u_total[:, 0])
        np.copyto(row_sum, u_total[:, 0])
        for j_gap in range(1, J):
            col = u_total[:, j_gap]
            np.maximum(top1, col, out=top1)
            row_sum += col
        row_sum -= top1
        row_sum *= _inv_Jm1       # row_sum = mean(rest)
        np.subtract(top1, row_sum, out=row_sum)
        np.abs(row_sum, out=row_sum)
        np.maximum(row_sum, _EPSILON_F32, out=row_sum)
        # row_sum = gap

        # 7b. Abstention utility
        np.multiply(min_dist_sq, _tau_1, out=v_abstain)
        v_abstain += _tau_0
        np.divide(_tau_2, row_sum, out=tmp)
        v_abstain += tmp

        # 7c. Demographic adjustment (per voter type)
        v_abstain += turnout_demo_adjust[active_idx]

        # 7c2. LGA-level turnout adjustment (same for all types in this LGA)
        v_abstain += lga_turnout_modifier[idx]

        # 7c3. LGA-modulated gender gap (female voters only)
        v_abstain[_idx_gen[active_idx] == 1] += gender_turnout_gap[idx]

        # 7c4. Religious minority mobilisation (per-LGA, per-religion)
        # Uses religion code of each active voter type to look up the
        # minority mobilisation adjustment for this LGA.
        v_abstain += minority_mobilisation[idx, _idx_rel[active_idx]]

        # 7d. Softmax over [party utils, abstention]
        np.maximum(top1, v_abstain, out=top1)  # top1 = row_max
        top1 *= _scale_f32                      # top1 = scaled row_max (rm32)

        sum_exp[:] = _ZERO_F32
        for j_exp in range(J):
            np.multiply(u_total[:, j_exp], _scale_f32, out=tmp)
            tmp -= top1
            np.exp(tmp, out=tmp)
            exp_parties[:, j_exp] = tmp
            sum_exp += tmp

        # Abstention exp
        np.multiply(v_abstain, _scale_f32, out=tmp)
        tmp -= top1
        np.exp(tmp, out=tmp)
        sum_exp += tmp
        # tmp = exp_abstain

        # 7e. Turnout & conditional probs (all in-place, zero allocations)
        np.divide(_ONE_F32, sum_exp, out=sum_exp)     # sum_exp = inv_sum
        np.multiply(tmp, sum_exp, out=tmp)             # tmp = p_abstain
        np.subtract(_ONE_F32, tmp, out=tmp)            # tmp = turnout
        np.clip(tmp, _ZERO_F32, _ONE_F32, out=tmp)
        # tmp = turnout_probs

        # Conditional: exp_parties *= inv_sum / max(turnout, eps)
        np.copyto(row_sum, tmp)                        # row_sum = turnout copy
        np.maximum(row_sum, _TURNOUT_EPS, out=row_sum)
        np.divide(sum_exp, row_sum, out=row_sum)       # row_sum = scale_factor
        for j_cond in range(J):
            exp_parties[:, j_cond] *= row_sum

        # Step 8: Aggregate
        vote_shares, turnout = aggregate_to_lga(
            tw[active_idx], exp_parties, tmp)

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
