"""Profile per-LGA step breakdown with sub-step timing."""
import time, sys
sys.path.insert(0, "src")
import numpy as np
from election_engine.config import EngineParams, Party, N_ISSUES
from election_engine.data_loader import load_lga_data
from election_engine.voter_types import (
    generate_all_voter_types, compute_type_weights, build_voter_ideal_base,
    precompute_compat_factors, _build_type_indices, compute_all_lga_ideal_offsets,
    precompute_all_lga_marginals,
)
from election_engine.utility import (
    precompute_ethnic_utility_table, precompute_religious_utility_table,
    precompute_all_ethnic_indices, precompute_all_religious_indices,
    precompute_fixed_type_utility,
)
from election_engine.spatial import batch_spatial_utility
from election_engine.turnout import batch_compute_vote_probs_with_turnout
from election_engine.ethnic_affinity import DEFAULT_ETHNIC_MATRIX
from election_engine.religious_affinity import DEFAULT_RELIGIOUS_MATRIX
from election_engine.salience import compute_all_lga_salience

lga_data = load_lga_data("data/nigeria_lga_polsim_2058.xlsx")
df = lga_data.df

rng = np.random.default_rng(42)
parties = []
ethnicities = ["Yoruba","Hausa-Fulani Undiff","Igbo","Ijaw","Kanuri",
               "Fulani","Tiv","Edo-Bini","Ibibio","Pada","Naijin",
               "Yoruba","Igbo","Hausa-Fulani Undiff"]
religions = ["Pentecostal","Mainstream Sunni","Catholic","Mainline Protestant",
             "Sufi Sunni","Mainstream Sunni","Catholic","Pentecostal",
             "Mainline Protestant","Pentecostal","Catholic","Mainstream Sunni",
             "Pentecostal","Sufi Sunni"]
for i in range(14):
    pos = np.clip(rng.normal(0, 2, N_ISSUES), -5, 5)
    parties.append(Party(name=f"P{i:02d}", positions=pos, valence=rng.uniform(-1, 1),
                         leader_ethnicity=ethnicities[i], religious_alignment=religions[i]))
params = EngineParams(tau_0=1.5, tau_1=0.3, tau_2=0.5, kappa=200.0,
                      sigma_national=0.05, sigma_regional=0.10)

voter_types = generate_all_voter_types()
voter_ideal_base = build_voter_ideal_base(voter_types).astype(np.float32)
compat_factors = precompute_compat_factors(voter_types)
type_indices = _build_type_indices()
eth_table = precompute_ethnic_utility_table(parties, params, DEFAULT_ETHNIC_MATRIX)
rel_table = precompute_religious_utility_table(parties, params, DEFAULT_RELIGIOUS_MATRIX)
all_eth_indices = precompute_all_ethnic_indices(voter_types, eth_table[1])
all_rel_indices = precompute_all_religious_indices(voter_types, rel_table[1])
party_positions = np.array([p.positions for p in parties]).astype(np.float32)
valences = np.array([p.valence for p in parties], dtype=np.float32)
D = party_positions.shape[1]
J = len(parties)
party_sq_norms_uniform = np.sum(party_positions ** 2, axis=1) / D
fixed_type_utility = precompute_fixed_type_utility(
    eth_table=eth_table[0], all_eth_indices=all_eth_indices,
    rel_table=rel_table[0], all_rel_indices=all_rel_indices,
).astype(np.float32)
fixed_type_utility += valences  # Pre-bake valences

# Precompute turnout demographic adjustment per type
turnout_demo_adjust = np.zeros(len(voter_types), dtype=np.float32)
turnout_demo_adjust[type_indices["edu"] == 2] -= 1.0
turnout_demo_adjust[type_indices["edu"] == 0] += 0.3
turnout_demo_adjust[type_indices["age"] == 3] -= 0.5
turnout_demo_adjust[type_indices["age"] == 0] += 0.2
turnout_demo_adjust[type_indices["set"] == 0] -= 0.2

national_median_gdp = float(df["GDP Per Capita Est"].median())
salience_matrix = compute_all_lga_salience(df, national_median_gdp=national_median_gdp).astype(np.float32)
all_lga_offsets = compute_all_lga_ideal_offsets(df).astype(np.float32)
all_marginals = precompute_all_lga_marginals(df)

_WEIGHT_THRESHOLD = 1e-7
N_SAMPLE = 100

# Warm up
for idx in range(5):
    marginals_row = (all_marginals["eth"][idx], all_marginals["rel"][idx],
                     all_marginals["set"][idx], all_marginals["edu"][idx],
                     all_marginals["liv"][idx], all_marginals["inc"][idx])
    tw = compute_type_weights(df.iloc[idx], voter_types, _WEIGHT_THRESHOLD,
                              compat_factors, type_indices,
                              precomputed_marginals_row=marginals_row)
    ai = np.where(tw > _WEIGHT_THRESHOLD)[0]
    ideals = voter_ideal_base[ai] + all_lga_offsets[idx]
    np.clip(ideals, -5, 5, out=ideals)
    batch_spatial_utility(ideals, party_positions, params.beta_s, params.q,
                          salience_matrix[idx])

# Accumulators
t_weights = t_active = t_ideals = 0
t_spatial = t_alien = t_fixutil = 0
t_indiff = t_abstain = t_softmax = 0
t_aggregate = 0
total_active = 0

for idx in range(N_SAMPLE):
    salience_w = salience_matrix[idx]
    lga_offset = all_lga_offsets[idx]
    marginals_row = (all_marginals["eth"][idx], all_marginals["rel"][idx],
                     all_marginals["set"][idx], all_marginals["edu"][idx],
                     all_marginals["liv"][idx], all_marginals["inc"][idx])

    # --- Type weights ---
    t0 = time.perf_counter()
    type_weights = compute_type_weights(df.iloc[idx], voter_types, _WEIGHT_THRESHOLD,
                                        compat_factors, type_indices,
                                        precomputed_marginals_row=marginals_row)
    t1 = time.perf_counter()
    active_idx = np.where(type_weights > _WEIGHT_THRESHOLD)[0]
    total_active += len(active_idx)
    t2 = time.perf_counter()

    # --- Ideal points ---
    active_ideals = voter_ideal_base[active_idx]
    active_ideals += lga_offset
    np.clip(active_ideals, -5.0, 5.0, out=active_ideals)
    t3 = time.perf_counter()

    # --- Spatial utility sub-step ---
    _intermediates = {}
    u_spatial = batch_spatial_utility(active_ideals, party_positions,
                                      params.beta_s, params.q, salience_w,
                                      _intermediates=_intermediates)
    t4 = time.perf_counter()

    # --- Alienation from intermediates (column-at-a-time for cache locality) ---
    dot_products = _intermediates["dot_products"]
    sq_norms = _intermediates["sq_norms"]
    wx = _intermediates["wx"]
    voter_wsq = np.einsum("nd,nd->n", wx, active_ideals)
    min_dist_sq = voter_wsq + sq_norms[0] - 2.0 * dot_products[:, 0]
    for j_al in range(1, J):
        candidate = voter_wsq + sq_norms[j_al] - 2.0 * dot_products[:, j_al]
        np.minimum(min_dist_sq, candidate, out=min_dist_sq)
    t5 = time.perf_counter()

    # --- Fixed utility add (valences pre-baked) ---
    result = u_spatial
    result += fixed_type_utility[active_idx]
    utilities_matrix = result
    t6 = time.perf_counter()

    # --- Turnout (full, with precomputed demo adjust) ---
    active_demo_adj = turnout_demo_adjust[active_idx]
    edu_codes = type_indices["edu"][active_idx]
    age_codes = type_indices["age"][active_idx]
    set_codes = type_indices["set"][active_idx]
    active_vote_probs, active_turnout = batch_compute_vote_probs_with_turnout(
        utilities_matrix=utilities_matrix, voter_ideals=active_ideals,
        party_positions=party_positions, params=params,
        educations=edu_codes, age_cohorts=age_codes, settings=set_codes,
        party_sq_norms_uniform=party_sq_norms_uniform,
        precomputed_min_dist_sq=min_dist_sq,
        precomputed_demo_adjust=active_demo_adj,
    )
    t7 = time.perf_counter()

    # --- Aggregation (float32 BLAS) ---
    active_weights = np.asarray(type_weights[active_idx], dtype=np.float32)
    eff_weights = active_weights * active_turnout  # float32
    total_eff = float(eff_weights.sum())
    if total_eff > 1e-12:
        vote_shares = np.dot(eff_weights, active_vote_probs) / total_eff
    t8 = time.perf_counter()

    t_weights += t1 - t0
    t_active += t2 - t1
    t_ideals += t3 - t2
    t_spatial += t4 - t3
    t_alien += t5 - t4
    t_fixutil += t6 - t5
    t_softmax += t7 - t6
    t_aggregate += t8 - t7

scale = 1000.0 / N_SAMPLE
total = t_weights + t_active + t_ideals + t_spatial + t_alien + t_fixutil + t_softmax + t_aggregate
print(f"Per-LGA breakdown (avg over {N_SAMPLE} LGAs, ms):")
print(f"  Type weights:      {t_weights*scale:.2f}ms")
print(f"  Active select:     {t_active*scale:.2f}ms")
print(f"  Ideal points:      {t_ideals*scale:.2f}ms")
print(f"  Spatial utility:   {t_spatial*scale:.2f}ms")
print(f"  Alienation:        {t_alien*scale:.2f}ms")
print(f"  Fixed util add:    {t_fixutil*scale:.2f}ms")
print(f"  Turnout (full):    {t_softmax*scale:.2f}ms")
print(f"  Aggregation:       {t_aggregate*scale:.2f}ms")
print(f"  TOTAL:             {total*scale:.2f}ms")
print(f"  Avg active:        {total_active/N_SAMPLE:.0f} types")
print(f"  Est full (774):    {total/N_SAMPLE*774:.2f}s")
print(f"  N_types total:     {len(voter_types)}")
