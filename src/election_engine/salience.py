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


def youth_unemployment_ratio(lga_row: pd.Series) -> float:
    """Youth unemployment / overall unemployment. High ratio = youth-specific crisis."""
    youth_unemp = float(lga_row.get("Youth Unemployment Rate Pct", 0))
    overall_unemp = max(1.0, float(lga_row.get("Unemployment Rate Pct", 1)))
    return min(3.0, youth_unemp / overall_unemp)


def extraction_diversity(lga_row: pd.Series) -> float:
    """Number of active extraction types (oil, cobalt, other mining). 0–3."""
    return (float(lga_row.get("Oil Extraction Active", 0) > 0)
            + float(lga_row.get("Cobalt Extraction Active", 0) > 0)
            + float(lga_row.get("Other Mining Active", 0) > 0))


def religious_tension_proxy(lga_row: pd.Series) -> float:
    """Product of Muslim% × Christian% / 2500. Peaks at 50/50 split (=1.0), low when homogeneous."""
    muslim = float(lga_row.get("% Muslim", 0))
    christian = float(lga_row.get("% Christian", 0))
    return (muslim * christian) / 2500.0


def population_pressure(lga_row: pd.Series) -> float:
    """High density × low infrastructure composite. Proxy for overstretched services."""
    density = float(lga_row.get("Population Density per km2", 200))
    road = float(lga_row.get("Road Quality Index", 5))
    # Normalised: density/500 (high = pressure) × (1 - road/10) (low quality = pressure)
    return min(3.0, (density / 500.0) * max(0.0, 1.0 - road / 10.0))


def youth_bulge(lga_row: pd.Series) -> float:
    """Fraction of population under 30, normalised to 0-1 (raw is percentage)."""
    return min(1.0, max(0.0, float(lga_row.get("% Population Under 30", 50)) / 100.0))


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
    "youth_unemployment_ratio": youth_unemployment_ratio,
    "extraction_diversity": extraction_diversity,
    "religious_tension_proxy": religious_tension_proxy,
    "population_pressure": population_pressure,
    "youth_bulge": youth_bulge,
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
    """Extra sharia salience if % Christian > 10 and % Muslim > 30.
    Also amplified where Al-Shahid is active — the movement politicises Sharia."""
    muslim = float(lga_row.get("% Muslim", 0))
    christian = float(lga_row.get("% Christian", 0))
    pent = float(lga_row.get("Pentecostal Growth", 0))
    al_shahid = float(lga_row.get("Al-Shahid Influence", 0))
    extra = 0.0
    if muslim > 30 and christian > 10:
        extra += (pent / 3.0) * 0.6
    # Al-Shahid politicises Sharia even in Muslim-majority areas
    if al_shahid > 2 and muslim > 50:
        extra += 0.3 * (al_shahid / 5.0)
    return extra


def _resource_conflict_conditional(lga_row: pd.Series) -> float:
    """Resource revenue becomes much more salient where extraction co-occurs with conflict."""
    conflict = float(lga_row.get("Conflict History", 0))
    extraction = float(lga_row.get("Extraction Intensity", 0))
    if conflict >= 2 and extraction >= 2:
        return 0.5 * min(conflict, 5.0) / 5.0 * min(extraction, 5.0) / 5.0
    return 0.0


def _military_conflict_conditional(lga_row: pd.Series) -> float:
    """Military role salience spikes in active conflict zones with federal control."""
    conflict = float(lga_row.get("Conflict History", 0))
    federal = float(lga_row.get("Federal Control 2058", 0))
    if conflict >= 3:
        extra = 0.5 * (conflict / 5.0)
        if federal > 0:
            extra += 0.3
        return extra
    return 0.0


def _bio_enhancement_conditional(lga_row: pd.Series) -> float:
    """Bio-enhancement salience increases in high-Pada areas and university towns."""
    pada = float(lga_row.get("% Pada", 0))
    tertiary = float(lga_row.get("Tertiary Institution", 0))
    bio_pct = float(lga_row.get("Biological Enhancement Pct", 0))
    extra = 0.0
    if bio_pct > 10:
        extra += 0.3 * (bio_pct / 100.0)
    if pada > 5 and tertiary > 0:
        extra += 0.2
    return extra


DEFAULT_SALIENCE_RULES: list[SalienceRule] = [
    # 1. Sharia Jurisdiction
    SalienceRule(
        issue_name="sharia_jurisdiction",
        base_weight=0.10,
        feature_coefficients={
            "% Muslim": 2.0 / 100.0,           # φ per percentage point
            "Al-Shahid Influence": 0.8 / 5.0,
            "% Christian": 0.5 / 100.0,
            "religious_tension_proxy": 0.8,     # Muslim-Christian interface amplifies
            "conflict_severity": 0.2 / 5.0,    # Conflict zones debate Sharia more
            "% Hausa": 0.3 / 100.0,            # Hausa heartland: Sharia tradition
            "% Fulani": 0.3 / 100.0,           # Fulani: historically Sharia-supporting
            "% Kanuri": 0.2 / 100.0,           # Kanuri: Borno Sharia tradition
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
            "extraction_diversity": 0.3,         # Multiple resource types = more autonomy demand
            "Poverty Rate Pct": 0.3 / 100.0,    # Poor LGAs want more from federal
            "% Igbo": 0.3 / 100.0,              # Igbo: strong fiscal autonomy tradition
            "% Yoruba": 0.2 / 100.0,            # Yoruba: federalist tradition
            "% Ijaw": 0.3 / 100.0,              # Ijaw: resource control demands
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
            "Unemployment Rate Pct": 0.3 / 100.0,  # Jobless areas blame Chinese
            "youth_bulge": 0.3,                      # Youth are more engaged with the issue
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
            "% Pada": 0.5 / 100.0,              # Padà communities care about BIC
            "% Naijin": 0.3 / 100.0,            # Naijin also invested in BIC reform
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
            "youth_unemployment_ratio": 0.3,     # Youth-specific job crisis → quota demands
            "conflict_severity": 0.2 / 5.0,     # Conflict areas debate ethnic distribution
            "% Tiv": 0.3 / 100.0,               # Tiv: Middle Belt quota politics
            "% Nupe": 0.2 / 100.0,              # Nupe: minority quota concerns
            "% Ibibio": 0.2 / 100.0,            # Ibibio: quota representation demands
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
            "population_pressure": 0.3,          # Overstretched areas care about fertility
            "Poverty Rate Pct": 0.2 / 100.0,    # Poor areas more concerned
            "% Muslim": 0.3 / 100.0,            # Muslim areas: fertility is religious/cultural issue
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
            "ethnic_fragmentation": 0.5,          # Diverse areas debate structure more
            "Trad Authority Index": 0.2 / 5.0,   # Traditional areas prefer presidential
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
            "extraction_diversity": 0.5,          # Multiple extraction → more revenue politics
            "Poverty Rate Pct": 0.3 / 100.0,     # Poor extraction areas: "resource curse" anger
            "% Ijaw": 0.5 / 100.0,               # Ijaw: Niger Delta resource control core
            "% Edo": 0.2 / 100.0,                 # Edo: Benin region extraction proximity
        },
        conditional=_resource_conflict_conditional,
    ),
    # 9. Housing
    SalienceRule(
        issue_name="housing",
        base_weight=0.05,
        feature_coefficients={
            "Urban Pct": 1.0 / 100.0,
            "Housing Affordability": -1.5 / 10.0,   # (10 - afford) / 10 * 1.5
            "Population Density per km2": 0.3 / 1000.0,
            "youth_bulge": 0.5,                      # Young populations face acute housing needs
            "population_pressure": 0.3,              # Dense, poor-infra areas
            "Median Age Estimate": -0.02,            # Younger median age → more acute housing needs
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
            "youth_bulge": 0.4,                   # Large youth populations amplify education debates
            "female_literacy_gap": 0.01,          # Gender education gap makes it more salient
            "Pentecostal Growth": 0.15 / 3.0,     # Pentecostal schools → education becomes contested
            "Num Secondary Schools": 0.01,        # More schools → education policy more salient locally
            "Median Age Estimate": -0.015,        # Younger population → education more salient
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
            "youth_unemployment_ratio": 0.4,      # Youth-specific job crisis
            "Chinese Economic Presence": 0.3 / 10.0,  # Chinese automation presence
            "Median Age Estimate": -0.015,         # Younger workforce → more automation anxiety
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
            "border_proximity": 0.3,              # Border areas care about military
            "% Kanuri": 0.3 / 100.0,             # Kanuri: Borno insurgency experience
            "% Tiv": 0.15 / 100.0,               # Tiv: Middle Belt security concerns
        },
        conditional=_military_conflict_conditional,
    ),
    # 13. Immigration
    SalienceRule(
        issue_name="immigration",
        base_weight=0.05,
        feature_coefficients={
            "Urban Pct": 0.5 / 100.0,
            "border_proximity": 1.0,
            "Housing Affordability": -0.5 / 10.0,  # (10 - afford) / 10 * 0.5
            "Population Density per km2": 0.2 / 1000.0,  # Dense areas feel immigration pressure
            "Unemployment Rate Pct": 0.3 / 100.0,  # High-unemployment → anti-immigration mood
            "ethnic_fragmentation": 0.3,            # Diverse areas more attuned to migration
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
            "ethnic_fragmentation": 0.5,           # More diverse → language politics matters
            "Almajiri Index": 0.3 / 5.0,          # Arabic vs English in education
            "% Muslim": 0.15 / 100.0,             # Muslim areas: Arabic vs English debate
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
            "Pentecostal Growth": 0.2 / 5.0,     # Pentecostal growth stirs gender debates
            "religious_tension_proxy": 0.5,        # Interfaith zones debate women's rights
            "% Muslim": 0.2 / 100.0,              # Muslim areas: gender norms are politically contested
            "% Christian": 0.15 / 100.0,           # Christian areas: feminist movements engage
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
            "conflict_severity": 0.2 / 5.0,       # Conflict areas re-evaluate trad authority
            "ethnic_fragmentation": 0.3,            # Diverse areas debate whose chiefs matter
            "% Hausa": 0.2 / 100.0,               # Hausa: strong emirate tradition
            "% Fulani": 0.15 / 100.0,             # Fulani: emirate/lamido system
            "% Yoruba": 0.15 / 100.0,             # Yoruba: Oba institution
            "% Kanuri": 0.15 / 100.0,             # Kanuri: Shehu tradition
            "Median Age Estimate": 0.01,           # Older population → traditional authority more salient
            "Traditionalist Practice": 0.2 / 5.0,  # Active traditionalist practice amplifies relevance
        },
    ),
    # 17. Infrastructure
    SalienceRule(
        issue_name="infrastructure",
        base_weight=0.15,
        feature_coefficients={
            "access_deficit": 2.0 / 300.0,
            "Road Quality Index": -1.0 / 10.0,   # (10 - road) / 10 * 1.0
            "Market Access Index": -0.3 / 10.0,  # Poor market access → infra demand
            "population_pressure": 0.4,            # Dense + poor-infra = acute demand
            "Poverty Rate Pct": 0.3 / 100.0,     # Poor areas prioritise infrastructure
            "conflict_severity": 0.2 / 5.0,       # Conflict zones: infrastructure destroyed
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
            "conflict_severity": 0.2 / 5.0,       # Land disputes fuel conflict, raises salience
            "Population Density per km2": 0.1 / 1000.0,  # Dense areas = land pressure
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
            "Urban Pct": 0.2 / 100.0,             # Urban areas more tax-aware
            "Pct Livelihood Informal": 0.3 / 100.0,  # Informal economy = tax evasion debates
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
            "Fertility Rate Est": 0.2,             # High-fertility rural areas = food security
            "Market Access Index": -0.3 / 10.0,   # Poor market access raises ag salience
            "% Hausa": 0.15 / 100.0,              # Hausa: agrarian heartland
            "% Fulani": 0.2 / 100.0,              # Fulani: pastoralist/herder-farmer conflicts
            "% Tiv": 0.15 / 100.0,                # Tiv: Middle Belt farming communities
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
            "Internet Access Pct": 0.2 / 100.0,   # Tech-connected areas engage with bioethics
            "Median Age Estimate": -0.01,          # Younger population → bio-enhancement more relevant
        },
        conditional=_bio_enhancement_conditional,
    ),
    # 22. Trade Policy
    SalienceRule(
        issue_name="trade_policy",
        base_weight=0.10,
        feature_coefficients={
            "Pct Livelihood Manufacturing": 1.5 / 100.0,
            "Rail Corridor": 0.5,
            "Chinese Economic Presence": 0.5 / 10.0,
            "border_proximity": 0.3,               # Border areas engaged with trade issues
            "Pct Livelihood Informal": 0.3 / 100.0,  # Informal traders affected by trade policy
            "Market Access Index": 0.1,             # Well-connected LGAs: trade matters more
            "Pct Livelihood Services": 0.3 / 100.0,  # Service economy cares about trade openness
            "% Igbo": 0.2 / 100.0,                 # Igbo: entrepreneurial/trade culture
            "% Yoruba": 0.15 / 100.0,              # Yoruba: commercial tradition
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
            "conflict_severity": 0.2 / 5.0,        # Extraction + conflict → environmental anger
            "Urban Pct": 0.2 / 100.0,              # Urban areas more environmentally aware
            "% Ijaw": 0.3 / 100.0,                 # Ijaw: oil spill devastation in Delta
            "% Edo": 0.15 / 100.0,                 # Edo: Benin environmental concerns
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
            "youth_bulge": 0.3,                    # Young populations more engaged with media
            "conflict_severity": 0.2 / 5.0,       # Conflict zones value press freedom
            "Pentecostal Growth": 0.15 / 3.0,     # Pentecostal media empires → media freedom matters
            "% Christian": 0.1 / 100.0,            # Christian areas: media-savvy, free press tradition
        },
    ),
    # 25. Healthcare
    SalienceRule(
        issue_name="healthcare",
        base_weight=0.10,
        feature_coefficients={
            "Access Healthcare Pct": -2.0 / 100.0,   # (100 - health) * 2.0/100
            "Access Water Pct": -0.3 / 100.0,        # Water access → health outcomes
            "Poverty Rate Pct": 0.5 / 100.0,
            "Fertility Rate Est": 0.2,                # High fertility → maternal health concerns
            "population_pressure": 0.3,               # Dense + poor-infra → health crisis
            "conflict_severity": 0.2 / 5.0,          # Conflict zones: health infrastructure destroyed
            "Median Age Estimate": 0.01,              # Older population → healthcare more salient
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
            "% Naijin": 0.5 / 100.0,               # Naijin presence amplifies Padà-politics
            "Biological Enhancement Pct": 0.3 / 100.0,  # Bio-enh linked to Padà identity
        },
    ),
    # 27. Energy Policy
    SalienceRule(
        issue_name="energy_policy",
        base_weight=0.10,
        feature_coefficients={
            "Access Electricity Pct": -2.0 / 100.0,  # (100 - elec) * 2.0/100
            "Refinery Zone": 0.5,
            "Extraction Intensity": 0.3 / 5.0,       # Energy producers debate policy
            "population_pressure": 0.3,               # Dense without power → energy salient
            "GDP Per Capita Est": 0.2 / 10000.0,     # Wealthier areas more engaged with energy transition
            "Pct Livelihood Manufacturing": 0.3 / 100.0,  # Manufacturing needs reliable power
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
            "conflict_severity": 0.3 / 5.0,         # Conflict zones want restructuring
            "religious_tension_proxy": 0.5,          # Interfaith zones want own states
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
            # salience contribution = 1.0*(10-road)/10 + 0.3*(10-market)/10
            w += 1.0 + 0.3
        if rule.issue_name == "healthcare":
            # salience contribution = 2.0*(100-health)/100 + 0.3*(100-water)/100
            w += 2.0 + 0.3
        if rule.issue_name == "energy_policy":
            # salience contribution = 2.0*(100-elec)/100 = -0.02*elec + 2.0
            w += 2.0
        if rule.issue_name == "immigration":
            # salience contribution = 0.5*(10-afford)/10 = -0.05*afford + 0.5
            w += 0.5
        if rule.issue_name == "traditional_authority":
            # land_formalization_gap helper already returns (100-land)/100; no correction needed
            pass
        if rule.issue_name == "agricultural_policy":
            # salience contribution = 0.3*(10-market_access)/10 = -0.03*market + 0.3
            w += 0.3

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
    Compute salience weights for all LGAs at once (vectorised).

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

    if rules is None:
        rules = DEFAULT_SALIENCE_RULES

    n_lga = len(lga_data)
    n_issues = len(rules)

    # --- Helper: safely extract a column as (N,) float array ---
    def _col(name: str, default: float = 0.0) -> np.ndarray:
        if name in lga_data.columns:
            s = lga_data[name]
            arr = pd.to_numeric(s, errors="coerce").fillna(default).values.astype(float)
            np.nan_to_num(arr, copy=False, nan=default)
            return arr
        return np.full(n_lga, default)

    # --- Pre-compute all derived features as (N,) arrays ---
    # ethnic_fragmentation: 1 - sum(share_k^2)
    ethnic_cols = [c for c in lga_data.columns if c.startswith("% ") and c not in
                   ("% Muslim", "% Christian", "% Traditionalist")]
    if ethnic_cols:
        eth_vals = lga_data[ethnic_cols].fillna(0.0).values.astype(float) / 100.0
        eth_frag = 1.0 - np.sum(eth_vals ** 2, axis=1)
    else:
        eth_frag = np.zeros(n_lga)

    # access_deficit: (100-elec) + (100-water) + (100-health)
    elec = _col("Access Electricity Pct")
    water = _col("Access Water Pct")
    health = _col("Access Healthcare Pct")
    acc_deficit = (100.0 - elec) + (100.0 - water) + (100.0 - health)

    # female_literacy_gap: max(0, male - female)
    male_lit = _col("Male Literacy Rate Pct")
    fem_lit = _col("Female Literacy Rate Pct")
    fem_gap = np.maximum(0.0, male_lit - fem_lit)

    # gender_parity_gap: max(0, 1 - GPI)
    gpi = _col("Gender Parity Index", 1.0)
    gp_gap = np.maximum(0.0, 1.0 - gpi)

    # conflict_severity: raw column
    conflict = _col("Conflict History")

    # border_proximity: 1 if north/border/sahel in Colonial Era Region
    if "Colonial Era Region" in lga_data.columns:
        regions = lga_data["Colonial Era Region"].fillna("").astype(str).str.lower()
        border_prox = ((regions.str.contains("north", na=False)) |
                       (regions.str.contains("border", na=False)) |
                       (regions.str.contains("sahel", na=False))).astype(float).values
    else:
        border_prox = np.zeros(n_lga)

    # land_formalization_gap: max(0, 100 - LandFormalPct)
    land_form = _col("Land Formalization Pct")
    land_gap = np.maximum(0.0, 100.0 - land_form)

    # rural_pct: max(0, 100 - Urban Pct)
    urban = _col("Urban Pct")
    r_pct = np.maximum(0.0, 100.0 - urban)

    # gdp_deviation: |GDP - median|
    gdp = _col("GDP Per Capita Est", national_median_gdp)
    gdp_dev = np.abs(gdp - national_median_gdp)

    # fertility_deviation: |FertRate - 2.1|
    fert = _col("Fertility Rate Est", 2.1)
    fert_dev = np.abs(fert - 2.1)

    # --- New derived features ---

    # youth_unemployment_ratio: youth_unemp / max(overall_unemp, 1)
    youth_unemp = _col("Youth Unemployment Rate Pct")
    overall_unemp = np.maximum(_col("Unemployment Rate Pct", 1.0), 1.0)
    youth_unemp_ratio = np.minimum(3.0, youth_unemp / overall_unemp)

    # extraction_diversity: count of active extraction types
    oil_active = (_col("Oil Extraction Active") > 0).astype(float)
    cobalt_active = (_col("Cobalt Extraction Active") > 0).astype(float)
    other_mining = (_col("Other Mining Active") > 0).astype(float)
    ext_diversity = oil_active + cobalt_active + other_mining

    # religious_tension_proxy: Muslim% × Christian% / 2500
    muslim_arr = _col("% Muslim")
    christian_arr = _col("% Christian")
    rel_tension = (muslim_arr * christian_arr) / 2500.0

    # population_pressure: (density/500) × (1 - road/10), capped at 3
    density = _col("Population Density per km2", 200.0)
    road_qi = _col("Road Quality Index", 5.0)
    pop_pressure = np.minimum(3.0, (density / 500.0) * np.maximum(0.0, 1.0 - road_qi / 10.0))

    # youth_bulge: % under 30, normalised to 0-1
    youth_b = np.clip(_col("% Population Under 30", 50.0) / 100.0, 0.0, 1.0)

    # Map derived feature keys → precomputed arrays
    derived_arrays = {
        "ethnic_fragmentation": eth_frag,
        "access_deficit": acc_deficit,
        "female_literacy_gap": fem_gap,
        "gender_parity_gap": gp_gap,
        "conflict_severity": conflict,
        "border_proximity": border_prox,
        "land_formalization_gap": land_gap,
        "rural_pct": r_pct,
        "gdp_deviation": gdp_dev,
        "youth_unemployment_ratio": youth_unemp_ratio,
        "extraction_diversity": ext_diversity,
        "religious_tension_proxy": rel_tension,
        "population_pressure": pop_pressure,
        "youth_bulge": youth_b,
    }

    # Pre-extract columns used in conditionals (avoid repeat _col calls)
    al_shahid_arr = _col("Al-Shahid Influence")
    extraction_int = _col("Extraction Intensity")
    federal_ctrl = _col("Federal Control 2058")
    pada_arr = _col("% Pada")
    tertiary_inst = _col("Tertiary Institution")
    bio_enh_pct = _col("Biological Enhancement Pct")
    pent_col = _col("Pentecostal Growth")

    # --- Build salience matrix ---
    result = np.zeros((n_lga, n_issues))

    for i, rule in enumerate(rules):
        w = np.full(n_lga, rule.base_weight)

        for feat_key, coeff in rule.feature_coefficients.items():
            if feat_key in derived_arrays:
                w += coeff * derived_arrays[feat_key]
            else:
                w += coeff * _col(feat_key)

        # Special case: fertility deviation
        if rule.issue_name == "fertility_policy":
            w += 0.8 * fert_dev
            raw_fert_coeff = rule.feature_coefficients.get("Fertility Rate Est", 0.0)
            if raw_fert_coeff != 0.0:
                w -= raw_fert_coeff * fert

        # Constant corrections for inverted features
        if rule.issue_name == "housing":
            w += 1.5
        if rule.issue_name == "infrastructure":
            w += 1.0 + 0.3  # +1.0 for road, +0.3 for market access
        if rule.issue_name == "healthcare":
            w += 2.0 + 0.3  # +2.0 for healthcare access, +0.3 for water access
        if rule.issue_name == "energy_policy":
            w += 2.0
        if rule.issue_name == "immigration":
            w += 0.5
        if rule.issue_name == "agricultural_policy":
            # Market Access Index has negative coeff: salience ∝ (10 - market_access)/10 * 0.3
            w += 0.3

        # Vectorised conditional terms
        if rule.conditional is not None:
            if rule.issue_name == "sharia_jurisdiction":
                # Sharia conditional: Pentecostal growth at Muslim-Christian interface
                mask_sc = (muslim_arr > 30) & (christian_arr > 10)
                cond_val = np.where(mask_sc, (pent_col / 3.0) * 0.6, 0.0)
                w += cond_val
                # Al-Shahid politicises Sharia in Muslim-majority areas
                mask_as = (al_shahid_arr > 2) & (muslim_arr > 50)
                w += np.where(mask_as, 0.3 * (al_shahid_arr / 5.0), 0.0)
            elif rule.issue_name == "resource_revenue":
                # Resource-conflict interaction
                mask_rc = (conflict >= 2) & (extraction_int >= 2)
                w += np.where(mask_rc,
                              0.5 * np.minimum(conflict, 5.0) / 5.0
                              * np.minimum(extraction_int, 5.0) / 5.0, 0.0)
            elif rule.issue_name == "military_role":
                # Military salience spikes in active conflict zones
                mask_mc = conflict >= 3
                w += np.where(mask_mc, 0.5 * (conflict / 5.0), 0.0)
                mask_fed = mask_mc & (federal_ctrl > 0)
                w += np.where(mask_fed, 0.3, 0.0)
            elif rule.issue_name == "biological_enhancement":
                # Bio-enhancement: high-Pada + university towns + high adoption
                mask_bio = bio_enh_pct > 10
                w += np.where(mask_bio, 0.3 * (bio_enh_pct / 100.0), 0.0)
                mask_padu = (pada_arr > 5) & (tertiary_inst > 0)
                w += np.where(mask_padu, 0.2, 0.0)
            else:
                # Generic fallback for custom conditionals
                for idx in range(n_lga):
                    w[idx] += rule.conditional(lga_data.iloc[idx])

        np.maximum(w, 0.0, out=w)
        result[:, i] = w

    # Normalize each row to sum to 1
    row_sums = result.sum(axis=1, keepdims=True)
    nonzero = row_sums > 0
    result = np.where(nonzero, result / np.maximum(row_sums, 1e-30), result)

    return result
