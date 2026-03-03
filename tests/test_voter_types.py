"""Tests for voter type generation, weight computation, and ideal point mapping."""

import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, "src")
from election_engine.voter_types import (
    VoterType,
    generate_all_voter_types,
    compute_type_weights,
    demographics_to_ideal_point,
    precompute_compat_factors,
    build_voter_ideal_base,
    compute_lga_ideal_offset,
    compute_all_lga_ideal_offsets,
    _build_type_indices,
    _CORE_ETHNICITIES,
    RELIGIONS,
    SETTINGS,
    AGE_COHORTS,
    EDUCATIONS,
    GENDERS,
    LIVELIHOODS,
    INCOMES,
    TOTAL_TYPES,
)
from election_engine.config import N_ISSUES


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_lga_row(**overrides) -> pd.Series:
    """Build a minimal valid LGA row for testing."""
    defaults = {
        "Urban Pct": 40.0,
        "% Muslim": 50.0,
        "% Christian": 45.0,
        "% Traditionalist": 5.0,
        "Adult Literacy Rate Pct": 55.0,
        "Tertiary Institution": 1,
        "Tijaniyya Presence": 1,
        "Qadiriyya Presence": 0,
        "Pentecostal Growth": 2,
        "Al-Shahid Influence": 0.1,
        "Pct Livelihood Agriculture": 35.0,
        "Pct Livelihood Manufacturing": 10.0,
        "Pct Livelihood Extraction": 3.0,
        "Pct Livelihood Services": 20.0,
        "Pct Livelihood Informal": 22.0,
        # Ethnic columns
        "% Hausa": 10.0,
        "% Fulani": 5.0,
        "% Hausa Fulani Undiff": 20.0,
        "% Yoruba": 5.0,
        "% Igbo": 3.0,
        "% Ijaw": 1.0,
        "% Kanuri": 2.0,
        "% Tiv": 2.0,
        "% Nupe": 1.0,
        "% Edo Bini": 1.0,
        "% Ibibio": 1.0,
        "% Pada": 0.5,
        "% Naijin": 0.5,
        # LGA-level ideal-point features
        "Oil Producing": 0,
        "Poverty Rate Pct": 40.0,
        "Mandarin Presence": 0,
        "Chinese Economic Presence": 0,
        "BIC Effectiveness": 5,
        "Fertility Rate Est": 5.0,
        "Trad Authority Index": 2,
        "Extraction Intensity": 1,
        "Cobalt Extraction Active": 0,
        "Housing Affordability": 5,
        "Out of School Children Pct": 20.0,
        "Pct Livelihood Manufacturing": 10.0,
        "Conflict History": 1,
        "English Prestige": 5,
        "Arabic Prestige": 3,
        "Gender Parity Index": 0.85,
        "Access Electricity Pct": 60.0,
        "Access Water Pct": 55.0,
        "Land Formalization Pct": 30.0,
        "Gini Proxy": 0.40,
        "Biological Enhancement Pct": 2.0,
        "Rail Corridor": 0,
        "Internet Access Pct": 25.0,
        "Access Healthcare Pct": 45.0,
    }
    defaults.update(overrides)
    return pd.Series(defaults)


# ---------------------------------------------------------------------------
# Type generation
# ---------------------------------------------------------------------------

def test_generate_all_voter_types_count():
    """TOTAL_TYPES matches the generated list length."""
    types = generate_all_voter_types()
    assert len(types) == TOTAL_TYPES


def test_generate_all_voter_types_cached():
    """Multiple calls return the identical cached list object."""
    t1 = generate_all_voter_types()
    t2 = generate_all_voter_types()
    assert t1 is t2


def test_voter_type_attributes_in_range():
    """Every type has attributes from the defined category lists."""
    types = generate_all_voter_types()
    for vt in types[:500]:   # sample first 500 for speed
        assert vt.ethnicity  in _CORE_ETHNICITIES
        assert vt.religion   in RELIGIONS
        assert vt.setting    in SETTINGS
        assert vt.age_cohort in AGE_COHORTS
        assert vt.education  in EDUCATIONS
        assert vt.gender     in GENDERS
        assert vt.livelihood in LIVELIHOODS
        assert vt.income     in INCOMES


# ---------------------------------------------------------------------------
# Type index precomputation
# ---------------------------------------------------------------------------

def test_build_type_indices_shape():
    """Each index array has length TOTAL_TYPES with the correct value range."""
    idx = _build_type_indices()
    assert set(idx.keys()) == {"eth", "rel", "set", "age", "edu", "gen", "liv", "inc"}
    assert idx["eth"].shape == (TOTAL_TYPES,)
    assert idx["eth"].max() == len(_CORE_ETHNICITIES) - 1
    assert idx["eth"].min() == 0
    assert idx["rel"].max() == len(RELIGIONS) - 1
    assert idx["inc"].max() == len(INCOMES) - 1


def test_build_type_indices_matches_voter_types():
    """Indices decode back to the correct category strings."""
    voter_types = generate_all_voter_types()
    idx = _build_type_indices()
    rng = np.random.default_rng(42)
    sample = rng.choice(TOTAL_TYPES, size=200, replace=False)
    for i in sample:
        vt = voter_types[i]
        assert _CORE_ETHNICITIES[idx["eth"][i]] == vt.ethnicity
        assert RELIGIONS[idx["rel"][i]]          == vt.religion
        assert SETTINGS[idx["set"][i]]           == vt.setting
        assert AGE_COHORTS[idx["age"][i]]        == vt.age_cohort
        assert EDUCATIONS[idx["edu"][i]]         == vt.education
        assert GENDERS[idx["gen"][i]]            == vt.gender
        assert LIVELIHOODS[idx["liv"][i]]        == vt.livelihood
        assert INCOMES[idx["inc"][i]]            == vt.income


# ---------------------------------------------------------------------------
# compute_type_weights
# ---------------------------------------------------------------------------

def test_weights_sum_to_one():
    """Weights must sum to 1 for any LGA row."""
    voter_types = generate_all_voter_types()
    lga = _make_lga_row()
    w = compute_type_weights(lga, voter_types)
    assert abs(w.sum() - 1.0) < 1e-9, f"weights sum = {w.sum()}"


def test_weights_non_negative():
    """No negative weights."""
    voter_types = generate_all_voter_types()
    lga = _make_lga_row()
    w = compute_type_weights(lga, voter_types)
    assert np.all(w >= 0.0)


def test_weights_missing_ethnic_columns():
    """Missing ethnic-share columns default to uniform without crashing."""
    voter_types = generate_all_voter_types()
    # LGA row with NO ethnic columns → all fracs default to 0 → uniform fallback
    lga_empty = pd.Series({
        "Urban Pct": 50.0,
        "% Muslim": 60.0, "% Christian": 35.0, "% Traditionalist": 5.0,
        "Adult Literacy Rate Pct": 50.0, "Tertiary Institution": 0,
        "Tijaniyya Presence": 0, "Qadiriyya Presence": 0,
        "Pentecostal Growth": 0, "Al-Shahid Influence": 0.0,
        "Pct Livelihood Agriculture": 40.0, "Pct Livelihood Manufacturing": 5.0,
        "Pct Livelihood Extraction": 2.0, "Pct Livelihood Services": 15.0,
        "Pct Livelihood Informal": 25.0,
        "% Pada": 0.0, "% Naijin": 0.0,
    })
    w = compute_type_weights(lga_empty, voter_types)
    assert abs(w.sum() - 1.0) < 1e-9
    assert np.all(w >= 0.0)


def test_weights_compat_precompute_matches_reference():
    """Vectorised path with precomputed_compat produces the same result as the fallback."""
    voter_types = generate_all_voter_types()
    lga = _make_lga_row()
    compat = precompute_compat_factors(voter_types)

    w_precomputed = compute_type_weights(lga, voter_types, precomputed_compat=compat)
    w_reference   = compute_type_weights(lga, voter_types, precomputed_compat=None)

    np.testing.assert_allclose(w_precomputed, w_reference, atol=1e-6, rtol=1e-5,
        err_msg="Precomputed compat path must match the reference loop path")


def test_weights_ethnically_dominated_lga():
    """An LGA with 100% Hausa should assign higher total weight to Hausa types."""
    voter_types = generate_all_voter_types()
    lga = _make_lga_row(**{
        "% Hausa": 100.0,
        "% Fulani": 0.0, "% Hausa Fulani Undiff": 0.0,
        "% Yoruba": 0.0, "% Igbo": 0.0, "% Ijaw": 0.0,
        "% Kanuri": 0.0, "% Tiv": 0.0, "% Nupe": 0.0,
        "% Edo Bini": 0.0, "% Ibibio": 0.0,
        "% Pada": 0.0, "% Naijin": 0.0,
    })
    w = compute_type_weights(lga, voter_types)
    hausa_mask = np.array([vt.ethnicity == "Hausa" for vt in voter_types])
    assert w[hausa_mask].sum() > 0.5, "Hausa types should dominate in a Hausa LGA"


# ---------------------------------------------------------------------------
# precompute_compat_factors
# ---------------------------------------------------------------------------

def test_precompute_compat_shape():
    """Returns (N_types,) array with values in (0, 1]."""
    voter_types = generate_all_voter_types()
    compat = precompute_compat_factors(voter_types)
    assert compat.shape == (TOTAL_TYPES,)
    assert np.all(compat > 0.0)
    assert np.all(compat <= 1.0)


# ---------------------------------------------------------------------------
# demographics_to_ideal_point
# ---------------------------------------------------------------------------

def test_ideal_point_shape():
    """Returns (N_ISSUES,) array."""
    vt = generate_all_voter_types()[0]
    lga = _make_lga_row()
    ideal = demographics_to_ideal_point(vt, lga)
    assert ideal.shape == (N_ISSUES,)


def test_ideal_point_clamped():
    """All ideal point values are in [-5, +5]."""
    voter_types = generate_all_voter_types()
    lga = _make_lga_row()
    rng = np.random.default_rng(0)
    sample_idx = rng.choice(TOTAL_TYPES, size=100, replace=False)
    for i in sample_idx:
        ideal = demographics_to_ideal_point(voter_types[i], lga)
        assert np.all(ideal >= -5.0), f"Type {i}: ideal below -5"
        assert np.all(ideal <= +5.0), f"Type {i}: ideal above +5"


# ---------------------------------------------------------------------------
# build_voter_ideal_base + compute_lga_ideal_offset (precomputed path)
# ---------------------------------------------------------------------------

def test_precomputed_ideal_matches_reference():
    """
    Full ideal matrix from build_voter_ideal_base + compute_lga_ideal_offset
    must match demographics_to_ideal_point for a sample of voter types.
    """
    voter_types = generate_all_voter_types()
    lga = _make_lga_row()

    voter_base   = build_voter_ideal_base(voter_types)
    lga_offset   = compute_lga_ideal_offset(lga)
    ideal_matrix = np.clip(voter_base + lga_offset, -5.0, 5.0)

    rng = np.random.default_rng(99)
    sample_idx = rng.choice(TOTAL_TYPES, size=200, replace=False)
    for i in sample_idx:
        ref = demographics_to_ideal_point(voter_types[i], lga)
        np.testing.assert_allclose(
            ideal_matrix[i], ref, atol=1e-12,
            err_msg=f"Mismatch at voter type index {i}",
        )


def test_lga_offset_shape():
    """compute_lga_ideal_offset returns (N_ISSUES,) array."""
    lga = _make_lga_row()
    offset = compute_lga_ideal_offset(lga)
    assert offset.shape == (N_ISSUES,)


def test_voter_ideal_base_shape():
    """build_voter_ideal_base returns (N_types, N_ISSUES) array."""
    voter_types = generate_all_voter_types()
    base = build_voter_ideal_base(voter_types)
    assert base.shape == (TOTAL_TYPES, N_ISSUES)


def test_vectorised_lga_offsets_match_per_row():
    """compute_all_lga_ideal_offsets must match per-row compute_lga_ideal_offset."""
    # Build a small DataFrame with 3 LGAs with different features
    rows = [
        _make_lga_row(**{"GDP Per Capita Est": 10000, "Oil Producing": 1,
                         "Urban Pct": 80, "Conflict History": 3}),
        _make_lga_row(**{"GDP Per Capita Est": 50000, "Oil Producing": 0,
                         "Urban Pct": 20, "Al-Shahid Influence": 4}),
        _make_lga_row(**{"GDP Per Capita Est": 25000, "Extraction Intensity": 3,
                         "Urban Pct": 50, "Fertility Rate Est": 6.0}),
    ]
    df = pd.DataFrame(rows)
    bulk_offsets = compute_all_lga_ideal_offsets(df)
    assert bulk_offsets.shape == (3, N_ISSUES)

    for idx in range(3):
        per_row = compute_lga_ideal_offset(df.iloc[idx])
        np.testing.assert_allclose(
            bulk_offsets[idx], per_row, atol=1e-12,
            err_msg=f"Mismatch at LGA {idx}",
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
