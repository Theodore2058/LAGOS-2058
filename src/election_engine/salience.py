"""
Variable issue salience module for the LAGOS-2058 election engine.

Salience weights w_d(c) quantify how much LGA c cares about issue d.
General form: w_d(c) = w₀ + Σ_k φ_k · LGA_Feature_k(c),  clamped to ≥ 0.

The 28 default rules are calibrated starting values — pass a custom rule list
to override any or all of them.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, Callable


# ---------------------------------------------------------------------------
# Derived feature helpers
# ---------------------------------------------------------------------------

def ethnic_fragmentation(lga_row: pd.Series) -> float:
    """
    Herfindahl-style ethnic fragmentation: 1 - Σ(share_k²).

    Reads all columns starting with '% ' that represent ethnic groups.
    Returns value in [0, 1]; 0 = fully homogeneous, ~1 = very diverse.
    """
    ethnic_cols = [c for c in lga_row.index if c.startswith("% ") and c not in
                   ("% Muslim", "% Christian", "% Traditionalist")]
    shares = lga_row[ethnic_cols].fillna(0.0).astype(float) / 100.0
    return float(1.0 - (shares ** 2).sum())


def access_deficit(lga_row: pd.Series) -> float:
    """Access deficit: (100 - Elec) + (100 - Water) + (100 - Health)."""
    elec   = float(lga_row.get("Access Electricity Pct", 0))
    water  = float(lga_row.get("Access Water Pct", 0))
    health = float(lga_row.get("Access Healthcare Pct", 0))
    return (100 - elec) + (100 - water) + (100 - health)


def female_literacy_gap(lga_row: pd.Series) -> float:
    """Male Literacy - Female Literacy (percentage points)."""
    male = float(lga_row.get("Male Literacy Rate Pct", 0))
    fem  = float(lga_row.get("Female Literacy Rate Pct", 0))
    return max(0.0, male - fem)


def gdp_deviation(lga_row: pd.Series, national_median: float = 18000.0) -> float:
    """|GDP - national_median| (absolute deviation)."""
    gdp = float(lga_row.get("GDP Per Capita Est", national_median))
    return abs(gdp - national_median)


def gender_parity_gap(lga_row: pd.Series) -> float:
    """1 - GPI (Gender Parity Index); 0 = full parity, 1 = total disparity."""
    gpi = float(lga_row.get("Gender Parity Index", 1.0))
    return max(0.0, 1.0 - gpi)


def conflict_severity(lga_row: pd.Series) -> float:
    """Ordinal encoding of Conflict History (0–5 scale)."""
    return float(lga_row.get("Conflict History", 0))


def border_proximity(lga_row: pd.Series) -> float:
    """
    Border proximity proxy from Colonial Era Region.
    Northern/border regions score higher.
    """
    region = str(lga_row.get("Colonial Era Region", "")).lower()
    if "north" in region or "border" in region or "sahel" in region:
        return 1.0
    return 0.0


def land_formalization_gap(lga_row: pd.Series) -> float:
    """100 - Land Formalization Pct."""
    return max(0.0, 100.0 - float(lga_row.get("Land Formalization Pct", 0)))


def rural_pct(lga_row: pd.Series) -> float:
    """100 - Urban Pct."""
    return max(0.0, 100.0 - float(lga_row.get("Urban Pct", 0)))


# ---------------------------------------------------------------------------
# SalienceRule dataclass
# ---------------------------------------------------------------------------

@dataclass
class SalienceRule:
    """
    Rule for computing the salience weight of one issue dimension.

    The weight for LGA c is computed as:
        w = base_weight + Σ (coeff * feature_value)
    Where feature_value is obtained by:
      1. Looking up a derived helper via `derived_features` dict, OR
      2. Reading column `col_name` directly from lga_row, scaled by the coefficient

    Parameters
    ----------
    issue_name : str
        Issue identifier (matches ISSUE_NAMES list).
    base_weight : float
        Intercept (w₀).
    feature_coefficients : dict
        Maps feature_key → coefficient (φ). Feature keys can be:
          - A column name in the LGA dataframe (e.g., "Urban Pct")
          - A derived feature name (see DERIVED_FEATURE_KEYS)
    conditional : Callable, optional
        A function (lga_row) -> float that adds a conditional term.
        E.g., for Sharia: extra weight only if % Muslim > 30.
    """
    issue_name: str
    base_weight: float
    feature_coefficients: dict[str, float] = field(default_factory=dict)
    conditional: Optional[Callable[[pd.Series], float]] = None


# Map from derived feature key → function
DERIVED_FEATURE_KEYS: dict[str, Callable[[pd.Series], float]] = {
    "ethnic_fragmentation": ethnic_fragmentation,
    "access_deficit": access_deficit,
    "female_literacy_gap": female_literacy_gap,
    "gender_parity_gap": gender_parity_gap,
    "conflict_severity": conflict_severity,
    "border_proximity": border_proximity,
    "land_formalization_gap": land_formalization_gap,
    "rural_pct": rural_pct,
}


def _get_feature(lga_row: pd.Series, key: str, national_median: float = 18000.0) -> float:
    """Retrieve a feature value, trying derived keys first, then column lookup."""
    if key in DERIVED_FEATURE_KEYS:
        return DERIVED_FEATURE_KEYS[key](lga_row)
    # Special case: gdp_deviation needs national_median
    if key == "gdp_deviation":
        return gdp_deviation(lga_row, national_median)
    # Direct column lookup
    val = lga_row.get(key, 0.0)
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0.0
    return float(val)


# ---------------------------------------------------------------------------
# Default 28-issue salience rules
# ---------------------------------------------------------------------------

def _sharia_conditional(lga_row: pd.Series) -> float:
    """Extra sharia salience if % Christian > 10 and % Muslim > 30."""
    muslim = float(lga_row.get("% Muslim", 0))
    christian = float(lga_row.get("% Christian", 0))
    pent = float(lga_row.get("Pentecostal Growth", 0))
    if muslim > 30 and christian > 10:
        return (pent / 3.0) * 0.6
    return 0.0


DEFAULT_SALIENCE_RULES: list[SalienceRule] = [
    # 1. Sharia Jurisdiction
    SalienceRule(
        issue_name="sharia_jurisdiction",
        base_weight=0.10,
        feature_coefficients={
            "% Muslim": 2.0 / 100.0,           # φ per percentage point
            "Al-Shahid Influence": 0.8 / 5.0,
            "% Christian": 0.5 / 100.0,
        },
        conditional=_sharia_conditional,
    ),
    # 2. Fiscal Autonomy
    SalienceRule(
        issue_name="fiscal_autonomy",
        base_weight=0.20,
        feature_coefficients={
            "gdp_deviation": 0.0001,
            "Oil Producing": 1.0,
            "Extraction Intensity": 0.5 / 5.0,
        },
    ),
    # 3. Chinese Relations
    SalienceRule(
        issue_name="chinese_relations",
        base_weight=0.10,
        feature_coefficients={
            "Chinese Economic Presence": 1.5 / 10.0,
            "Mandarin Presence": 0.8 / 10.0,
            "Planned City": 0.5,
            "Pct Livelihood Manufacturing": 0.5 / 100.0,
        },
    ),
    # 4. BIC Reform
    SalienceRule(
        issue_name="bic_reform",
        base_weight=0.15,
        feature_coefficients={
            "BIC Effectiveness": 0.5 / 10.0,
            "Urban Pct": 0.3 / 100.0,
            "Internet Access Pct": 0.3 / 100.0,
        },
    ),
    # 5. Ethnic Quotas
    SalienceRule(
        issue_name="ethnic_quotas",
        base_weight=0.10,
        feature_coefficients={
            "ethnic_fragmentation": 1.5,
            "Unemployment Rate Pct": 1.0 / 100.0,
            "Tertiary Institution": 0.3,
        },
    ),
    # 6. Fertility Policy
    SalienceRule(
        issue_name="fertility_policy",
        base_weight=0.10,
        feature_coefficients={
            "Fertility Rate Est": 0.8,          # |FertRate - 2.1| applied below
            "Urban Pct": 0.3 / 100.0,
            "% Population Under 30": 0.5 / 100.0,
        },
    ),
    # 7. Constitutional Structure
    SalienceRule(
        issue_name="constitutional_structure",
        base_weight=0.10,
        feature_coefficients={
            "Urban Pct": 0.4 / 100.0,
            "Internet Access Pct": 0.3 / 100.0,
            "Adult Literacy Rate Pct": 0.3 / 100.0,
        },
    ),
    # 8. Resource Revenue
    SalienceRule(
        issue_name="resource_revenue",
        base_weight=0.05,
        feature_coefficients={
            "Extraction Intensity": 2.0 / 5.0,
            "Oil Producing": 1.5,
            "Cobalt Extraction Active": 1.5,
            "Refinery Present": 0.5,
        },
    ),
    # 9. Housing
    SalienceRule(
        issue_name="housing",
        base_weight=0.05,
        feature_coefficients={
            "Urban Pct": 1.0 / 100.0,
            "Housing Affordability": -1.5 / 10.0,   # (10 - afford) / 10 * 1.5
            "Population Density per km2": 0.3 / 1000.0,
        },
    ),
    # 10. Education
    SalienceRule(
        issue_name="education",
        base_weight=0.15,
        feature_coefficients={
            "Out of School Children Pct": 1.5 / 100.0,
            "Tertiary Institution": 0.5,
            "Almajiri Index": 1.0 / 5.0,
            "gender_parity_gap": 1.0,
        },
    ),
    # 11. Labor & Automation
    SalienceRule(
        issue_name="labor_automation",
        base_weight=0.10,
        feature_coefficients={
            "Pct Livelihood Manufacturing": 1.5 / 100.0,
            "Pct Livelihood Informal": 1.0 / 100.0,
            "Unemployment Rate Pct": 0.8 / 100.0,
        },
    ),
    # 12. Military Role
    SalienceRule(
        issue_name="military_role",
        base_weight=0.10,
        feature_coefficients={
            "conflict_severity": 0.8 / 5.0,
            "Al-Shahid Influence": 1.0 / 5.0,
            "Federal Control 2058": 0.5,
        },
    ),
    # 13. Immigration
    SalienceRule(
        issue_name="immigration",
        base_weight=0.05,
        feature_coefficients={
            "Urban Pct": 0.5 / 100.0,
            "border_proximity": 1.0,
            "Housing Affordability": -0.5 / 10.0,  # (10 - afford) / 10 * 0.5
        },
    ),
    # 14. Language Policy
    SalienceRule(
        issue_name="language_policy",
        base_weight=0.05,
        feature_coefficients={
            "Mandarin Presence": 0.8 / 10.0,
            "Arabic Prestige": 0.8 / 10.0,
            "English Prestige": 0.3 / 10.0,
            "Urban Pct": 0.5 / 100.0,
        },
    ),
    # 15. Women's Rights
    SalienceRule(
        issue_name="womens_rights",
        base_weight=0.10,
        feature_coefficients={
            "gender_parity_gap": 1.5,
            "Urban Pct": 0.5 / 100.0,
            "female_literacy_gap": 0.02,
        },
    ),
    # 16. Traditional Authority
    SalienceRule(
        issue_name="traditional_authority",
        base_weight=0.05,
        feature_coefficients={
            "Trad Authority Index": 1.5 / 5.0,
            "rural_pct": 0.5 / 100.0,
            "land_formalization_gap": 0.01 / 100.0,
        },
    ),
    # 17. Infrastructure
    SalienceRule(
        issue_name="infrastructure",
        base_weight=0.15,
        feature_coefficients={
            "access_deficit": 2.0 / 300.0,
            "Road Quality Index": -1.0 / 10.0,   # (10 - road) / 10 * 1.0
        },
    ),
    # 18. Land Tenure
    SalienceRule(
        issue_name="land_tenure",
        base_weight=0.05,
        feature_coefficients={
            "Pct Livelihood Agriculture": 1.5 / 100.0,
            "land_formalization_gap": 1.0 / 100.0,
            "Trad Authority Index": 0.5 / 5.0,
        },
    ),
    # 19. Taxation
    SalienceRule(
        issue_name="taxation",
        base_weight=0.10,
        feature_coefficients={
            "Gini Proxy": 1.0,
            "Poverty Rate Pct": 0.5 / 100.0,
            "GDP Per Capita Est": 0.3 / 10000.0,
        },
    ),
    # 20. Agricultural Policy
    SalienceRule(
        issue_name="agricultural_policy",
        base_weight=0.05,
        feature_coefficients={
            "Pct Livelihood Agriculture": 2.5 / 100.0,
            "rural_pct": 0.5 / 100.0,
            "Poverty Rate Pct": 0.5 / 100.0,
        },
    ),
    # 21. Biological Enhancement
    SalienceRule(
        issue_name="biological_enhancement",
        base_weight=0.05,
        feature_coefficients={
            "Biological Enhancement Pct": 1.0 / 100.0,
            "Urban Pct": 0.5 / 100.0,
            "% Population Under 30": 0.3 / 100.0,
        },
    ),
    # 22. Trade Policy
    SalienceRule(
        issue_name="trade_policy",
        base_weight=0.10,
        feature_coefficients={
            "Pct Livelihood Manufacturing": 1.5 / 100.0,
            "Rail Corridor": 0.5,
            "Chinese Economic Presence": 0.5 / 10.0,
        },
    ),
    # 23. Environmental Regulation
    SalienceRule(
        issue_name="environmental_regulation",
        base_weight=0.05,
        feature_coefficients={
            "Extraction Intensity": 1.5 / 5.0,
            "Oil Producing": 1.0,
            "Cobalt Extraction Active": 1.0,
        },
    ),
    # 24. Media Freedom
    SalienceRule(
        issue_name="media_freedom",
        base_weight=0.05,
        feature_coefficients={
            "Internet Access Pct": 1.0 / 100.0,
            "Mobile Phone Penetration Pct": 0.3 / 100.0,
            "Urban Pct": 0.5 / 100.0,
        },
    ),
    # 25. Healthcare
    SalienceRule(
        issue_name="healthcare",
        base_weight=0.10,
        feature_coefficients={
            "Access Healthcare Pct": -2.0 / 100.0,   # (100 - health) * 2.0/100
            "Poverty Rate Pct": 0.5 / 100.0,
        },
    ),
    # 26. Padà Status
    SalienceRule(
        issue_name="pada_status",
        base_weight=0.10,
        feature_coefficients={
            "% Pada": 2.0 / 100.0,
            "BIC Effectiveness": 0.5 / 10.0,
            "Urban Pct": 0.3 / 100.0,
        },
    ),
    # 27. Energy Policy
    SalienceRule(
        issue_name="energy_policy",
        base_weight=0.10,
        feature_coefficients={
            "Access Electricity Pct": -2.0 / 100.0,  # (100 - elec) * 2.0/100
            "Refinery Zone": 0.5,
        },
    ),
    # 28. AZ Restructuring
    SalienceRule(
        issue_name="az_restructuring",
        base_weight=0.10,
        feature_coefficients={
            "ethnic_fragmentation": 1.0,
            "Urban Pct": 0.3 / 100.0,
            "Trad Authority Index": 0.5 / 5.0,
        },
    ),
]

# Quick name → index lookup
_ISSUE_INDEX: dict[str, int] = {r.issue_name: i for i, r in enumerate(DEFAULT_SALIENCE_RULES)}


# ---------------------------------------------------------------------------
# Special per-issue feature transformations
# ---------------------------------------------------------------------------
# Some issues use (10 - value) or absolute-deviation forms.
# These are handled by signing the coefficient appropriately:
#   Housing Affordability: spec says (10 - afford)/10 * 1.5
#     → coefficient on raw column = -1.5/10 (subtract, so high affordability = low salience)
#   Road Quality: spec says (10 - road)/10 * 1.0
#     → coefficient on raw column = -1.0/10
#   Healthcare access: (100 - health)/100 * 2.0
#     → coefficient on raw column = -2.0/100
#   Electricity access: (100 - elec)/100 * 2.0
#     → coefficient on raw column = -2.0/100
# The issue-6 fertility rule uses |FertRate - 2.1| → handled below in compute_salience
# via a special intercept adjustment.


def _fertility_deviation(lga_row: pd.Series) -> float:
    """Absolute deviation of fertility rate from replacement (2.1)."""
    fert = float(lga_row.get("Fertility Rate Est", 2.1))
    return abs(fert - 2.1)


# ---------------------------------------------------------------------------
# Core computation functions
# ---------------------------------------------------------------------------

def compute_salience(
    lga_row: pd.Series,
    rules: Optional[list[SalienceRule]] = None,
    national_median_gdp: float = 18000.0,
) -> np.ndarray:
    """
    Compute salience weights for all 28 issues for one LGA.

    Parameters
    ----------
    lga_row : pd.Series
        Row from the LGA dataframe.
    rules : list[SalienceRule], optional
        Salience rules. Defaults to DEFAULT_SALIENCE_RULES.
    national_median_gdp : float
        National median GDP used for gdp_deviation feature.

    Returns
    -------
    np.ndarray, shape (28,)
        Salience weights, all ≥ 0 and summing to 1.0 (unless all raw
        weights are zero, in which case the zero vector is returned).
    """
    if rules is None:
        rules = DEFAULT_SALIENCE_RULES

    weights = np.zeros(len(rules))

    for i, rule in enumerate(rules):
        w = rule.base_weight

        for feat_key, coeff in rule.feature_coefficients.items():
            if feat_key == "gdp_deviation":
                val = gdp_deviation(lga_row, national_median_gdp)
            elif feat_key in DERIVED_FEATURE_KEYS:
                val = DERIVED_FEATURE_KEYS[feat_key](lga_row)
            else:
                raw = lga_row.get(feat_key, 0.0)
                try:
                    val = float(raw) if raw is not None else 0.0
                except (ValueError, TypeError):
                    val = 0.0
                if np.isnan(val):
                    val = 0.0

            w += coeff * val

        # Special case: fertility deviation
        if rule.issue_name == "fertility_policy":
            w += 0.8 * _fertility_deviation(lga_row)
            # Remove double-counting from raw Fertility Rate Est
            raw_fert_coeff = rule.feature_coefficients.get("Fertility Rate Est", 0.0)
            if raw_fert_coeff != 0.0:
                raw_fert = float(lga_row.get("Fertility Rate Est", 2.1))
                w -= raw_fert_coeff * raw_fert  # undo raw contribution

        # Constant corrections for "inverted" features encoded with negative coefficients.
        # Each affected rule stores a NEGATIVE coefficient on a raw value so that a
        # HIGHER raw value → LOWER weight (e.g. more affordable housing → less salient).
        # The intent is salience ∝ (max - raw), which expands to:
        #   coeff_neg * raw + constant  where  constant = |coeff_neg| * max
        # The feature_coefficients dict holds coeff_neg; these blocks add the constant.
        if rule.issue_name == "housing":
            # salience contribution = 1.5*(10-afford)/10 = -0.15*afford + 1.5
            w += 1.5
        if rule.issue_name == "infrastructure":
            # salience contribution = 1.0*(10-road)/10 = -0.10*road + 1.0
            w += 1.0
        if rule.issue_name == "healthcare":
            # salience contribution = 2.0*(100-health)/100 = -0.02*health + 2.0
            w += 2.0
        if rule.issue_name == "energy_policy":
            # salience contribution = 2.0*(100-elec)/100 = -0.02*elec + 2.0
            w += 2.0
        if rule.issue_name == "immigration":
            # salience contribution = 0.5*(10-afford)/10 = -0.05*afford + 0.5
            w += 0.5
        if rule.issue_name == "traditional_authority":
            # land_formalization_gap helper already returns (100-land)/100; no correction needed
            pass

        # Conditional term
        if rule.conditional is not None:
            w += rule.conditional(lga_row)

        weights[i] = max(0.0, w)  # clamp to non-negative

    # Normalize so weights sum to 1.0 — prevents any single dimension
    # from dominating spatial utility purely due to scale.
    total = weights.sum()
    if total > 0:
        weights /= total

    return weights


def compute_all_lga_salience(
    lga_data: pd.DataFrame,
    rules: Optional[list[SalienceRule]] = None,
    national_median_gdp: Optional[float] = None,
) -> np.ndarray:
    """
    Compute salience weights for all LGAs at once.

    Parameters
    ----------
    lga_data : pd.DataFrame
        The full LGA dataframe (774 rows).
    rules : list[SalienceRule], optional
        Salience rules to use.
    national_median_gdp : float, optional
        National median GDP. If None, computed from the dataframe.

    Returns
    -------
    np.ndarray, shape (774, 28)
        Salience weights for every LGA × issue combination.
    """
    if national_median_gdp is None:
        national_median_gdp = float(lga_data["GDP Per Capita Est"].median())

    n_lga = len(lga_data)
    n_issues = len(rules) if rules else len(DEFAULT_SALIENCE_RULES)
    result = np.zeros((n_lga, n_issues))

    for idx in range(n_lga):
        row = lga_data.iloc[idx]
        result[idx] = compute_salience(row, rules=rules,
                                       national_median_gdp=national_median_gdp)
    return result
