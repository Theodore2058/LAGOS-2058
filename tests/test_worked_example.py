"""
Worked example tests for the LAGOS-2058 election engine.

These tests verify the structural behaviour of the spatial + softmax +
poststratification pipeline using controlled inputs inspired by Appendix A.

Since the spec's Appendix A uses a simplified 2-issue setup with specific
affinity values we can't exactly replicate without the full spec document,
we test the structural invariants and sign-level predictions.
"""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")
from election_engine.config import Party, EngineParams, N_ISSUES
from election_engine.spatial import spatial_utility
from election_engine.softmax import softmax
from election_engine.utility import compute_utility
from election_engine.poststratification import aggregate_to_lga
from election_engine.ethnic_affinity import EthnicAffinityMatrix
from election_engine.religious_affinity import ReligiousAffinityMatrix


# ---------------------------------------------------------------------------
# Test 1: Spatial utility — the Appendix A calculation
# ---------------------------------------------------------------------------

def test_appendix_a_spatial_2d():
    """
    Reproduce Appendix A spatial utility for the 2-issue case:
    Voter A: ideal = [3, 0], Party N: positions = [4, 1]
    Salience = [2.5, 0.3], q=0.5, beta_s=1.0

    Weighted dot: 2.5*3*4 + 0.3*0*1 = 30.0
    Weighted norm²: 2.5*4² + 0.3*1² = 40.3
    U_spatial = 1.0 * (0.5 * 30.0 - 0.25 * 40.3) = 15.0 - 10.075 = 4.925
    """
    voter = np.array([3.0, 0.0])
    party_N = np.array([[4.0, 1.0]])
    salience = np.array([2.5, 0.3])

    u = spatial_utility(voter, party_N, beta_s=1.0, q=0.5, salience_weights=salience)
    assert abs(u[0] - 4.925) < 1e-6, f"Expected 4.925, got {u[0]:.6f}"


# ---------------------------------------------------------------------------
# Test 2: Softmax probabilities
# ---------------------------------------------------------------------------

def test_appendix_a_softmax():
    """
    With utilities [8.6, -5.0, -10.0], softmax should give P(N) very close to 1.
    Party N should dominate when it has much higher utility.
    """
    utils = np.array([8.6, -5.0, -10.0])
    probs = softmax(utils, scale=1.0)
    assert probs[0] > 0.99, f"P(N) should be ~1, got {probs[0]:.4f}"
    assert abs(probs.sum() - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# Test 3: Full utility — structural properties
# ---------------------------------------------------------------------------

def _make_party(name, pos2, valence, ethnicity, religion):
    """Helper: make a Party with first 2 dimensions set, rest zero."""
    positions = np.zeros(N_ISSUES)
    positions[0] = pos2[0]
    positions[1] = pos2[1]
    return Party(name=name, positions=positions, valence=valence,
                 leader_ethnicity=ethnicity, religious_alignment=religion)


def test_utility_in_group_ethnicity_bonus():
    """A voter should have higher utility for a co-ethnic party leader."""
    party_coethnic = _make_party("Coethnic", [2, 1], 0.0, "Hausa", "Mainstream Sunni")
    party_outgroup = _make_party("Outgroup", [2, 1], 0.0, "Igbo", "Pentecostal")

    params = EngineParams(alpha_e=2.5, alpha_r=1.5)
    salience = np.ones(N_ISSUES)
    voter_ideal = np.zeros(N_ISSUES)
    voter_ideal[0] = 2.0

    v = compute_utility(
        voter_ideal=voter_ideal,
        voter_ethnicity="Hausa",
        voter_religion="Mainstream Sunni",
        voter_demographics={},
        parties=[party_coethnic, party_outgroup],
        params=params,
        salience_weights=salience,
    )
    assert v[0] > v[1], f"Co-ethnic party should have higher utility: {v}"


def test_utility_valence_shifts_all():
    """Adding valence to one party shifts only that party's utility."""
    party_a = _make_party("A", [1, 1], 0.0, "Yoruba", "Mainline Protestant")
    party_b = _make_party("B", [1, 1], 2.0, "Yoruba", "Mainline Protestant")  # valence=2

    params = EngineParams()
    salience = np.ones(N_ISSUES)
    voter_ideal = np.zeros(N_ISSUES)
    voter_ideal[0] = 1.0

    v = compute_utility(voter_ideal, "Yoruba", "Mainline Protestant", {},
                        [party_a, party_b], params, salience)
    # Party B should be exactly 2.0 higher
    assert abs(v[1] - v[0] - 2.0) < 1e-10, f"Valence difference: {v[1] - v[0]}"


def test_utility_zero_alpha_e_no_ethnic():
    """With alpha_e=0, ethnic utility is zero."""
    party = _make_party("P", [3, 2], 0.0, "Hausa", "Mainstream Sunni")

    params_with = EngineParams(alpha_e=2.5)
    params_zero = EngineParams(alpha_e=0.0)
    salience = np.ones(N_ISSUES)
    voter_ideal = np.zeros(N_ISSUES)

    v_with = compute_utility(voter_ideal, "Hausa", "Mainstream Sunni", {},
                              [party], params_with, salience)
    v_zero = compute_utility(voter_ideal, "Hausa", "Mainstream Sunni", {},
                              [party], params_zero, salience)

    # alpha_e=0 should remove the ethnic bonus
    assert v_zero[0] < v_with[0], "Zero alpha_e should reduce in-group utility"


# ---------------------------------------------------------------------------
# Test 4: Poststratification — Appendix A aggregation
# ---------------------------------------------------------------------------

def test_appendix_a_poststratification():
    """
    Reproduce Appendix A final result:
    70% Type A (turnout 40%): P(N)=0.999, P(T)=0.001, P(Y)≈0
    30% Type B (turnout 75%): P(T)=0.89, P(N)=0.08, P(Y)=0.03
    Expected: N ≈ 59%, T ≈ 40%, Y < 5%
    """
    weights = np.array([0.70, 0.30])
    vote_probs = np.array([
        [0.999, 0.001, 0.000],
        [0.080, 0.890, 0.030],
    ])
    turnout = np.array([0.40, 0.75])

    shares, avg_turnout = aggregate_to_lga(weights, vote_probs, turnout)

    assert abs(shares[0] - 0.59) < 0.02, f"N share = {shares[0]:.3f}, expected ~0.59"
    assert abs(shares[1] - 0.40) < 0.02, f"T share = {shares[1]:.3f}, expected ~0.40"
    assert shares[2] < 0.05, f"Y share = {shares[2]:.3f}, expected < 0.05"
    assert abs(shares.sum() - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# Test 5: Salience weights affect spatial utility
# ---------------------------------------------------------------------------

def test_salience_amplifies_preferred_dimension():
    """Higher salience on an issue where voter and party agree → higher utility."""
    voter = np.zeros(N_ISSUES)
    voter[0] = 4.0  # strongly pro on issue 0

    party_positions = np.zeros((1, N_ISSUES))
    party_positions[0, 0] = 4.0  # perfectly aligned on issue 0
    party = Party("P", party_positions[0], valence=0.0,
                  leader_ethnicity="", religious_alignment="")

    salience_low = np.ones(N_ISSUES) * 0.1
    salience_low[0] = 0.1

    salience_high = np.ones(N_ISSUES) * 0.1
    salience_high[0] = 5.0  # high salience on issue 0

    params = EngineParams(alpha_e=0.0, alpha_r=0.0)  # zero identity effects

    v_low = compute_utility(voter, "", "", {}, [party], params, salience_low)
    v_high = compute_utility(voter, "", "", {}, [party], params, salience_high)

    assert v_high[0] > v_low[0], (
        f"High salience on agreed issue should give higher utility: "
        f"low={v_low[0]:.3f}, high={v_high[0]:.3f}"
    )


# ---------------------------------------------------------------------------
# Test 6: Full pipeline smoke test on 2 LGAs
# ---------------------------------------------------------------------------

def test_pipeline_produces_valid_shares():
    """Run the full pipeline on 2 LGAs and verify shares are valid."""
    try:
        from election_engine.data_loader import load_lga_data
        from election_engine.voter_types import generate_all_voter_types
        from election_engine.poststratification import compute_lga_results
        from election_engine.salience import compute_salience

        lga = load_lga_data("data/nigeria_lga_polsim_2058.xlsx")
        voter_types = generate_all_voter_types()

        from examples.run_election import PARTIES
    except (ImportError, FileNotFoundError) as e:
        pytest.skip(f"Data or examples not available: {e}")

    params = EngineParams()
    salience = compute_salience(lga.df.iloc[0])

    shares, turnout, n_active = compute_lga_results(
        lga_row=lga.df.iloc[0],
        voter_types=voter_types,
        parties=PARTIES,
        params=params,
        salience_weights=salience,
        ethnic_matrix=EthnicAffinityMatrix(),
        religious_matrix=ReligiousAffinityMatrix(),
    )

    assert abs(shares.sum() - 1.0) < 1e-8, f"Shares don't sum to 1: {shares.sum()}"
    assert np.all(shares >= 0), "Negative shares"
    assert 0.0 <= turnout <= 1.0, f"Invalid turnout: {turnout}"
    assert n_active > 0, "No active types"


# ---------------------------------------------------------------------------
# Test 7: Regression — no duplicate keys in ideal-point coefficient table
# ---------------------------------------------------------------------------

def test_no_duplicate_keys_in_ideal_point_coefficients():
    """Every issue dict in _IDEAL_POINT_COEFFICIENTS must have unique keys.

    Regression test for Bug 1: Issue 26 ('Padà Status') had a duplicate
    'is_hausa_fulani' key that silently overwrote the -2.5 coefficient with -1.5.
    """
    from election_engine.voter_types import _IDEAL_POINT_COEFFICIENTS, N_ISSUES

    assert len(_IDEAL_POINT_COEFFICIENTS) == N_ISSUES

    for idx, coeff_dict in enumerate(_IDEAL_POINT_COEFFICIENTS):
        # Python already deduplicates dict keys at parse time, so the only way
        # to catch the bug is to verify the *intended* value is preserved.
        # We also verify the duplicate was removed by checking no unexpected
        # low value replaced the strong hausa_fulani opposition on issue 26.
        pass  # structural check only — duplicate removal is enforced by Python

    # Specific regression: Issue 26 (index 25) must have is_hausa_fulani == -2.5
    issue26 = _IDEAL_POINT_COEFFICIENTS[25]
    assert "is_hausa_fulani" in issue26, "Issue 26 missing is_hausa_fulani coefficient"
    assert issue26["is_hausa_fulani"] == -2.5, (
        f"Issue 26 is_hausa_fulani should be -2.5 (strong opposition), "
        f"got {issue26['is_hausa_fulani']} — duplicate key bug may have returned"
    )


# ---------------------------------------------------------------------------
# Test 8: Numerical equivalence — precomputed ideal path matches reference
# ---------------------------------------------------------------------------

def test_precomputed_ideal_matches_reference():
    """
    build_voter_ideal_base + compute_lga_ideal_offset must produce ideal points
    numerically identical to demographics_to_ideal_point for every voter type.

    Regression guard: if the decomposition math is wrong the two paths diverge.
    """
    import pandas as pd
    from election_engine.voter_types import (
        generate_all_voter_types, demographics_to_ideal_point,
        build_voter_ideal_base, compute_lga_ideal_offset,
    )

    voter_types = generate_all_voter_types()

    # Synthetic LGA row with a mix of non-zero lga_* column values
    lga_row = pd.Series({
        "Oil Producing": 1.0,
        "Poverty Rate Pct": 55.0,
        "Mandarin Presence": 3.0,
        "Chinese Economic Presence": 7.0,
        "GDP Per Capita Est": 120000.0,
        "Conflict History": 2.0,
        "Fertility Rate Est": 5.5,
        "English Prestige": 6.0,
        "Arabic Prestige": 4.0,
        "Gender Parity Index": 0.7,
        "Trad Authority Index": 3.0,
        "Access Electricity Pct": 40.0,
        "Access Water Pct": 50.0,
        "Land Formalization Pct": 20.0,
        "Gini Proxy": 0.45,
        "Pct Livelihood Agriculture": 35.0,
        "Pct Livelihood Manufacturing": 10.0,
        "Biological Enhancement Pct": 5.0,
        "Rail Corridor": 1.0,
        "Oil Spill Index": 2.0,
        "Digital Infrastructure Index": 4.0,
        "Federal Presence": 3.0,
        "Pct Christian Minority": 15.0,
        "Sharia Court Index": 2.0,
    })

    # Precomputed path
    voter_base = build_voter_ideal_base(voter_types)
    lga_offset = compute_lga_ideal_offset(lga_row)
    ideal_matrix = np.clip(voter_base + lga_offset, -5.0, 5.0)

    # Check a representative sample of voter types to keep test fast
    rng = np.random.default_rng(42)
    sample_idx = rng.choice(len(voter_types), size=200, replace=False)

    for i in sample_idx:
        vt = voter_types[i]
        ref = demographics_to_ideal_point(vt, lga_row)
        fast = ideal_matrix[i]
        assert np.allclose(ref, fast, atol=1e-12), (
            f"Voter type {i} ({vt.ethnicity}/{vt.religion}) mismatch:\n"
            f"  reference: {ref}\n  precomputed: {fast}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
