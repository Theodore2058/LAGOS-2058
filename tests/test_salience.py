"""Tests for the variable issue salience module."""

import sys
import math
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, "src")
from election_engine.salience import (
    compute_salience,
    compute_all_lga_salience,
    DEFAULT_SALIENCE_RULES,
    ethnic_fragmentation,
    access_deficit,
    female_literacy_gap,
    gdp_deviation,
    gender_parity_gap,
    land_formalization_gap,
    rural_pct,
)
from election_engine.config import N_ISSUES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_lga_row(**overrides) -> pd.Series:
    """Build a representative LGA row with sensible defaults."""
    defaults = {
        "% Muslim": 50.0, "% Christian": 45.0, "% Traditionalist": 5.0,
        "% Hausa": 15.0, "% Fulani": 5.0, "% Hausa Fulani Undiff": 10.0,
        "% Yoruba": 8.0, "% Igbo": 6.0, "% Ijaw": 2.0, "% Kanuri": 2.0,
        "% Tiv": 2.0, "% Nupe": 1.0, "% Edo Bini": 1.0, "% Ibibio": 1.0,
        "% Pada": 0.5, "% Naijin": 0.5,
        "Urban Pct": 40.0,
        "GDP Per Capita Est": 18000.0,
        "Oil Producing": 0,
        "Extraction Intensity": 1,
        "Chinese Economic Presence": 2,
        "Mandarin Presence": 1,
        "Planned City": 0,
        "Al-Shahid Influence": 0.2,
        "BIC Effectiveness": 5,
        "Fertility Rate Est": 5.2,
        "Trad Authority Index": 2,
        "Housing Affordability": 5,
        "Out of School Children Pct": 20.0,
        "Pct Livelihood Manufacturing": 12.0,
        "Pct Livelihood Agriculture": 35.0,
        "Conflict History": 1,
        "English Prestige": 5, "Arabic Prestige": 3,
        "Gender Parity Index": 0.85,
        "Access Electricity Pct": 60.0,
        "Access Water Pct": 55.0,
        "Access Healthcare Pct": 50.0,
        "Land Formalization Pct": 30.0,
        "Gini Proxy": 0.40,
        "Poverty Rate Pct": 40.0,
        "Biological Enhancement Pct": 2.0,
        "Rail Corridor": 0,
        "Internet Access Pct": 25.0,
        "Pentecostal Growth": 2,
        "Qadiriyya Presence": 1,
        "Tijaniyya Presence": 1,
        "Cobalt Extraction Active": 0,
        "Male Literacy Rate Pct": 65.0,
        "Female Literacy Rate Pct": 50.0,
        "Adult Literacy Rate Pct": 57.0,
        "Colonial Era Region": "North Central",
    }
    defaults.update(overrides)
    return pd.Series(defaults)


# ---------------------------------------------------------------------------
# Default rules sanity
# ---------------------------------------------------------------------------

def test_default_rules_count():
    """There must be exactly 28 default salience rules."""
    assert len(DEFAULT_SALIENCE_RULES) == N_ISSUES


def test_default_rules_issue_names_unique():
    """Each rule must have a unique issue_name."""
    names = [r.issue_name for r in DEFAULT_SALIENCE_RULES]
    assert len(names) == len(set(names)), "Duplicate issue names in DEFAULT_SALIENCE_RULES"


# ---------------------------------------------------------------------------
# compute_salience output properties
# ---------------------------------------------------------------------------

def test_salience_shape():
    """Returns (N_ISSUES,) array."""
    lga = _make_lga_row()
    s = compute_salience(lga, national_median_gdp=18000.0)
    assert s.shape == (N_ISSUES,)


def test_all_salience_non_negative():
    """Every salience weight must be ≥ 0 for a standard LGA."""
    lga = _make_lga_row()
    s = compute_salience(lga, national_median_gdp=18000.0)
    assert np.all(s >= 0.0), f"Negative salience found: {s}"


def test_salience_sums_to_one():
    """Salience weights must sum to 1.0 after normalization."""
    lga = _make_lga_row()
    s = compute_salience(lga, national_median_gdp=18000.0)
    assert abs(s.sum() - 1.0) < 1e-10, f"Salience sum = {s.sum()}, expected 1.0"


def test_salience_non_negative_all_zeros():
    """Even a minimal LGA (all-zero features) should give non-negative salience."""
    lga = pd.Series({col: 0.0 for col in _make_lga_row().index})
    s = compute_salience(lga, national_median_gdp=18000.0)
    assert np.all(s >= 0.0)


def test_no_nan_or_inf_salience():
    """No NaN or Inf in salience output."""
    lga = _make_lga_row()
    s = compute_salience(lga, national_median_gdp=18000.0)
    assert not np.any(np.isnan(s))
    assert not np.any(np.isinf(s))


def test_salience_nan_column_treated_as_zero():
    """A NaN value in an LGA column should default to 0 without crashing."""
    lga = _make_lga_row(**{"GDP Per Capita Est": float("nan")})
    s = compute_salience(lga, national_median_gdp=18000.0)
    assert not np.any(np.isnan(s))
    assert np.all(s >= 0.0)


def test_salience_string_column_treated_as_zero():
    """A non-numeric string in a numeric column should default to 0."""
    lga = _make_lga_row(**{"Oil Producing": "yes"})
    # Should not raise; should treat as 0.0
    try:
        s = compute_salience(lga, national_median_gdp=18000.0)
        assert not np.any(np.isnan(s))
    except (ValueError, TypeError):
        pytest.fail("compute_salience raised on a string column value")


# ---------------------------------------------------------------------------
# Issue-specific salience direction tests
# ---------------------------------------------------------------------------

def test_sharia_higher_in_muslim_lga():
    """Sharia salience is higher when % Muslim is higher."""
    lga_low  = _make_lga_row(**{"% Muslim": 5.0,  "% Christian": 90.0})
    lga_high = _make_lga_row(**{"% Muslim": 90.0, "% Christian": 5.0})
    median_gdp = 18000.0
    sharia_idx = next(i for i, r in enumerate(DEFAULT_SALIENCE_RULES)
                      if r.issue_name == "sharia_jurisdiction")
    s_low  = compute_salience(lga_low,  national_median_gdp=median_gdp)[sharia_idx]
    s_high = compute_salience(lga_high, national_median_gdp=median_gdp)[sharia_idx]
    assert s_high > s_low, (
        f"Sharia salience should be higher in Muslim LGA: high={s_high:.3f}, low={s_low:.3f}"
    )


def test_oil_lga_higher_fiscal_salience():
    """Oil-producing LGAs should have higher fiscal autonomy salience."""
    lga_no_oil = _make_lga_row(**{"Oil Producing": 0})
    lga_oil    = _make_lga_row(**{"Oil Producing": 1})
    median_gdp = 18000.0
    fiscal_idx = next(i for i, r in enumerate(DEFAULT_SALIENCE_RULES)
                      if r.issue_name == "fiscal_autonomy")
    s_no = compute_salience(lga_no_oil, national_median_gdp=median_gdp)[fiscal_idx]
    s_oi = compute_salience(lga_oil,    national_median_gdp=median_gdp)[fiscal_idx]
    assert s_oi > s_no


def test_fertility_salience_uses_deviation():
    """Fertility salience: LGA with very high fertility rate > national baseline."""
    lga_normal = _make_lga_row(**{"Fertility Rate Est": 2.1})
    lga_high   = _make_lga_row(**{"Fertility Rate Est": 8.0})
    fert_idx = next(i for i, r in enumerate(DEFAULT_SALIENCE_RULES)
                    if r.issue_name == "fertility_policy")
    median_gdp = 18000.0
    s_n = compute_salience(lga_normal, national_median_gdp=median_gdp)[fert_idx]
    s_h = compute_salience(lga_high,   national_median_gdp=median_gdp)[fert_idx]
    assert s_h > s_n, "High fertility LGA should have higher fertility salience"


def test_housing_salience_inverted():
    """Low-affordability LGAs should have higher housing salience (inverted feature)."""
    lga_afford = _make_lga_row(**{"Housing Affordability": 9.0})  # good (high = affordable)
    lga_crisis = _make_lga_row(**{"Housing Affordability": 1.0})  # bad (low = unaffordable)
    housing_idx = next(i for i, r in enumerate(DEFAULT_SALIENCE_RULES)
                       if r.issue_name == "housing")
    median_gdp = 18000.0
    s_afford = compute_salience(lga_afford, national_median_gdp=median_gdp)[housing_idx]
    s_crisis = compute_salience(lga_crisis, national_median_gdp=median_gdp)[housing_idx]
    assert s_crisis > s_afford, (
        f"Unaffordable housing LGA should have higher housing salience: "
        f"crisis={s_crisis:.3f}, afford={s_afford:.3f}"
    )


def test_healthcare_salience_inverted():
    """Lower healthcare access → higher healthcare salience."""
    lga_good = _make_lga_row(**{"Access Healthcare Pct": 95.0})
    lga_bad  = _make_lga_row(**{"Access Healthcare Pct": 10.0})
    hc_idx = next(i for i, r in enumerate(DEFAULT_SALIENCE_RULES)
                  if r.issue_name == "healthcare")
    median_gdp = 18000.0
    s_good = compute_salience(lga_good, national_median_gdp=median_gdp)[hc_idx]
    s_bad  = compute_salience(lga_bad,  national_median_gdp=median_gdp)[hc_idx]
    assert s_bad > s_good


# ---------------------------------------------------------------------------
# compute_all_lga_salience
# ---------------------------------------------------------------------------

def test_compute_all_lga_salience_shape():
    """Returns (N_LGAs, N_ISSUES) array."""
    rows = [_make_lga_row() for _ in range(10)]
    df = pd.DataFrame(rows)
    df["GDP Per Capita Est"] = 18000.0
    result = compute_all_lga_salience(df)
    assert result.shape == (10, N_ISSUES)


def test_compute_all_lga_salience_non_negative():
    """All salience weights from batch computation are ≥ 0."""
    rows = [_make_lga_row() for _ in range(15)]
    df = pd.DataFrame(rows)
    df["GDP Per Capita Est"] = 18000.0
    result = compute_all_lga_salience(df)
    assert np.all(result >= 0.0)


# ---------------------------------------------------------------------------
# Derived feature helpers
# ---------------------------------------------------------------------------

def test_ethnic_fragmentation_homogeneous():
    """Fully homogeneous LGA (one group = 100%) → fragmentation ≈ 0."""
    lga = _make_lga_row(**{
        "% Hausa": 100.0,
        "% Fulani": 0.0, "% Hausa Fulani Undiff": 0.0, "% Yoruba": 0.0,
        "% Igbo": 0.0, "% Ijaw": 0.0, "% Kanuri": 0.0, "% Tiv": 0.0,
        "% Nupe": 0.0, "% Edo Bini": 0.0, "% Ibibio": 0.0,
        "% Pada": 0.0, "% Naijin": 0.0,
    })
    f = ethnic_fragmentation(lga)
    assert f < 0.05, f"Homogeneous LGA should have near-zero fragmentation, got {f:.3f}"


def test_ethnic_fragmentation_diverse():
    """Evenly-split LGA → fragmentation close to 1."""
    lga = _make_lga_row(**{
        "% Hausa": 10.0, "% Fulani": 10.0, "% Hausa Fulani Undiff": 10.0,
        "% Yoruba": 10.0, "% Igbo": 10.0, "% Ijaw": 10.0,
        "% Kanuri": 10.0, "% Tiv": 10.0, "% Nupe": 10.0, "% Edo Bini": 10.0,
    })
    f = ethnic_fragmentation(lga)
    assert f > 0.7, f"Diverse LGA should have high fragmentation, got {f:.3f}"


def test_access_deficit_full_access():
    """Full access (100% each) → deficit = 0."""
    lga = _make_lga_row(**{
        "Access Electricity Pct": 100.0,
        "Access Water Pct": 100.0,
        "Access Healthcare Pct": 100.0,
    })
    assert access_deficit(lga) == pytest.approx(0.0)


def test_access_deficit_no_access():
    """Zero access → deficit = 300."""
    lga = _make_lga_row(**{
        "Access Electricity Pct": 0.0,
        "Access Water Pct": 0.0,
        "Access Healthcare Pct": 0.0,
    })
    assert access_deficit(lga) == pytest.approx(300.0)


def test_female_literacy_gap_zero():
    """Equal male/female literacy → gap = 0."""
    lga = _make_lga_row(**{"Male Literacy Rate Pct": 70.0, "Female Literacy Rate Pct": 70.0})
    assert female_literacy_gap(lga) == pytest.approx(0.0)


def test_gdp_deviation_at_median():
    """GDP exactly at national median → deviation = 0."""
    lga = _make_lga_row(**{"GDP Per Capita Est": 25000.0})
    assert gdp_deviation(lga, national_median=25000.0) == pytest.approx(0.0)


def test_land_formalization_gap():
    """100% formalized → gap = 0; 0% formalized → gap = 100."""
    lga_full = _make_lga_row(**{"Land Formalization Pct": 100.0})
    lga_zero = _make_lga_row(**{"Land Formalization Pct": 0.0})
    assert land_formalization_gap(lga_full) == pytest.approx(0.0)
    assert land_formalization_gap(lga_zero) == pytest.approx(100.0)


def test_rural_pct():
    """rural_pct = 100 - Urban Pct."""
    lga = _make_lga_row(**{"Urban Pct": 35.0})
    assert rural_pct(lga) == pytest.approx(65.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
