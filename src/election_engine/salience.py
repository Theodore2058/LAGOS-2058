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


def is_colonial_western(lga_row: pd.Series) -> float:
    """Colonial Western Region (Yoruba heartland)."""
    return 1.0 if str(lga_row.get("Colonial Era Region", "")).strip() == "Western" else 0.0


def is_colonial_eastern(lga_row: pd.Series) -> float:
    """Colonial Eastern Region (Igbo core + minorities)."""
    return 1.0 if str(lga_row.get("Colonial Era Region", "")).strip() == "Eastern" else 0.0


def is_colonial_midwestern(lga_row: pd.Series) -> float:
    """Colonial Mid-Western Region (Edo/Delta minorities)."""
    return 1.0 if str(lga_row.get("Colonial Era Region", "")).strip() == "Mid-Western" else 0.0


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


def modernization_clash(lga_row: pd.Series) -> float:
    """Measures tension between traditional and modern forces in an LGA.
    High internet + traditional authority = cultural clash zone.
    Returns 0-1 scale."""
    internet = float(lga_row.get("Internet Access Pct", 20))
    trad = float(lga_row.get("Trad Authority Index", 0))
    pent = float(lga_row.get("Pentecostal Growth", 0))
    # Peaks where all three are high (internet × trad_auth × religious_dynamism)
    return min(1.0, (internet / 100.0) * (trad / 5.0) * max(1.0, pent / 2.0))


def literacy_fertility_tension(lga_row: pd.Series) -> float:
    """High fertility + low female literacy = demographic-education mismatch.
    Returns 0-1 scale; high values where fertility is high and literacy is low."""
    fertility = float(lga_row.get("Fertility Rate Est", 5))
    fem_lit = float(lga_row.get("Female Literacy Rate Pct", 50))
    return min(1.0, max(0.0, (fertility / 7.0) * (1.0 - fem_lit / 100.0)))


def inequality_extraction_mismatch(lga_row: pd.Series) -> float:
    """Resource-rich LGAs with high inequality = 'resource curse' anger.
    Returns 0-2 scale."""
    gini = float(lga_row.get("Gini Proxy", 0.36))
    extraction = float(lga_row.get("Extraction Intensity", 0))
    return min(2.0, max(0.0, (gini - 0.35) / 0.25) * (extraction / 5.0))


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
    "is_colonial_western": is_colonial_western,
    "is_colonial_eastern": is_colonial_eastern,
    "is_colonial_midwestern": is_colonial_midwestern,
    "modernization_clash": modernization_clash,
    "literacy_fertility_tension": literacy_fertility_tension,
    "inequality_extraction_mismatch": inequality_extraction_mismatch,
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


def _herder_farmer_conditional(lga_row: pd.Series) -> float:
    """Land tenure salience spikes where Fulani pastoralists meet farming communities.
    The herder-farmer conflict is one of Nigeria's most violent ongoing crises."""
    fulani_pct = float(lga_row.get("% Fulani", 0))
    ag_pct = float(lga_row.get("Pct Livelihood Agriculture", 0))
    conflict = float(lga_row.get("Conflict History", 0))
    extra = 0.0
    # Fulani presence + agricultural area = herder-farmer tension zone
    if fulani_pct > 5 and ag_pct > 40:
        extra += 0.3 * min(fulani_pct, 30) / 30.0
    # Amplified by active conflict
    if conflict >= 2 and fulani_pct > 5:
        extra += 0.2 * (conflict / 5.0)
    return extra


def _youth_unemployment_conditional(lga_row: pd.Series) -> float:
    """Labor/automation salience spikes where youth unemployment is extreme
    and Chinese economic presence creates automation anxiety."""
    youth_unemp = float(lga_row.get("Youth Unemployment Rate Pct", 0))
    chinese = float(lga_row.get("Chinese Economic Presence", 0))
    internet = float(lga_row.get("Internet Access Pct", 0))
    extra = 0.0
    # Extreme youth unemployment + tech presence = automation panic
    if youth_unemp > 60 and chinese > 3:
        extra += 0.3 * min(youth_unemp, 80) / 80.0
    # Internet amplifies: online discourse about job loss
    if youth_unemp > 50 and internet > 60:
        extra += 0.15
    return extra


def _immigration_border_conditional(lga_row: pd.Series) -> float:
    """Immigration salience spikes in border regions with unemployment."""
    border = border_proximity(lga_row)
    unemp = float(lga_row.get("Unemployment Rate Pct", 0))
    housing = float(lga_row.get("Housing Affordability", 5))
    extra = 0.0
    # Border + unemployment = immigration becomes heated
    if border > 0.5 and unemp > 30:
        extra += 0.3 * min(unemp, 60) / 60.0
    # Housing crisis in border areas amplifies anti-immigrant sentiment
    if border > 0.5 and housing < 4:
        extra += 0.2
    return extra


def _bic_reform_conditional(lga_row: pd.Series) -> float:
    """BIC reform salience spikes where Pada population is significant but BIC
    effectiveness is poor — people feel the system isn't serving its purpose."""
    pada = float(lga_row.get("% Pada", 0))
    bic_eff = float(lga_row.get("BIC Effectiveness", 5))
    urban = float(lga_row.get("Urban Pct", 0))
    extra = 0.0
    # Pada present but BIC failing → reform demands
    if pada > 5 and bic_eff < 4:
        extra += 0.3 * min(pada, 30) / 30.0
    # Urban areas with Pada → more vocal reform advocacy
    if pada > 3 and urban > 60:
        extra += 0.15
    return extra


def _constitutional_conflict_conditional(lga_row: pd.Series) -> float:
    """Constitutional debates spike where ethnic fragmentation meets conflict —
    people blame the constitution for failing to manage diversity."""
    frag = float(lga_row.get("ethnic_fragmentation", 0))
    conflict = float(lga_row.get("Conflict History", 0))
    trad = float(lga_row.get("Trad Authority Index", 0))
    extra = 0.0
    # High fragmentation + conflict = constitutional crisis narrative
    if frag > 0.6 and conflict >= 2:
        extra += 0.3 * min(conflict, 5) / 5.0
    # Traditional authority areas with fragmentation → restructuring debates
    if trad > 3 and frag > 0.5:
        extra += 0.15 * (trad / 5.0)
    return extra


def _taxation_inequality_conditional(lga_row: pd.Series) -> float:
    """Taxation becomes salient where inequality is high AND extraction is
    happening — people feel resources are extracted but not redistributed."""
    gini = float(lga_row.get("Gini Proxy", 0.36))
    extraction = float(lga_row.get("Extraction Intensity", 0))
    poverty = float(lga_row.get("Poverty Rate Pct", 30))
    extra = 0.0
    # High inequality + extraction = tax justice demands
    if gini > 0.45 and extraction > 2:
        extra += 0.25 * min(extraction, 5) / 5.0
    # Extreme poverty + any Gini above average = redistribution demands
    if poverty > 50 and gini > 0.40:
        extra += 0.2 * min(poverty, 80) / 80.0
    return extra


def _pada_tension_conditional(lga_row: pd.Series) -> float:
    """Pada status becomes charged where Pada population is growing rapidly
    alongside traditional populations — a demographic friction point."""
    pada = float(lga_row.get("% Pada", 0))
    bio = float(lga_row.get("Biological Enhancement Pct", 0))
    trad = float(lga_row.get("Traditionalist Practice", 0))
    extra = 0.0
    # Pada growth near traditional communities = friction
    if pada > 5 and trad > 2:
        extra += 0.25 * min(pada, 25) / 25.0
    # High bio-enhancement + Pada = identity politics intensifies
    if bio > 15 and pada > 10:
        extra += 0.2 * min(bio, 50) / 50.0
    return extra


def _safe_float(val, default: float = 0.0) -> float:
    """Convert to float, returning *default* on ValueError/TypeError."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _infrastructure_crisis_conditional(lga_row: pd.Series) -> float:
    """Infrastructure becomes hyper-salient where access deficit combines with
    population density — overcrowded areas without basic services."""
    elec = _safe_float(lga_row.get("Access Electricity Pct", 50), 50)
    water = _safe_float(lga_row.get("Access Water Pct", 50), 50)
    density = _safe_float(lga_row.get("Population Density per km2", 200), 200)
    extra = 0.0
    # Dense areas without electricity = energy crisis politics
    if elec < 40 and density > 500:
        extra += 0.3 * (1.0 - elec / 100.0)
    # No water + high density = acute public health + infrastructure demand
    if water < 30 and density > 300:
        extra += 0.2 * (1.0 - water / 100.0)
    return extra


def _education_deprivation_conditional(lga_row: pd.Series) -> float:
    """Education salience spikes where out-of-school rate is high AND youth
    population is large — a powder keg of frustrated young people."""
    osc = _safe_float(lga_row.get("Out of School Children Pct", 20), 20)
    youth_unemp = _safe_float(lga_row.get("Youth Unemployment Rate Pct", 46), 46)
    almajiri = _safe_float(lga_row.get("Almajiri Index", 0), 0)
    extra = 0.0
    # Mass out-of-school + youth unemployment = education as top issue
    if osc > 40 and youth_unemp > 50:
        extra += 0.25 * min(osc, 80) / 80.0
    # Almajiri system + high OSC = parallel education systems debate
    if almajiri > 2 and osc > 30:
        extra += 0.2 * min(almajiri, 5) / 5.0
    return extra


def _healthcare_crisis_conditional(lga_row: pd.Series) -> float:
    """Healthcare becomes politically charged where access is poor AND
    fertility is high — maternal/child mortality drives voter anger."""
    health = _safe_float(lga_row.get("Access Healthcare Pct", 50), 50)
    fertility = _safe_float(lga_row.get("Fertility Rate Est", 5), 5)
    poverty = _safe_float(lga_row.get("Poverty Rate Pct", 30), 30)
    extra = 0.0
    # Poor healthcare + high fertility = maternal mortality crisis
    if health < 30 and fertility > 5:
        extra += 0.3 * (1.0 - health / 100.0)
    # Poverty + poor healthcare = compounding deprivation
    if poverty > 50 and health < 40:
        extra += 0.2 * min(poverty, 80) / 80.0
    return extra


def _housing_pressure_conditional(lga_row: pd.Series) -> float:
    """Housing becomes politically explosive where population density meets
    low affordability — the classic urban housing crisis."""
    density = _safe_float(lga_row.get("Population Density per km2", 200), 200)
    afford = _safe_float(lga_row.get("Housing Affordability", 5), 5)
    urban = _safe_float(lga_row.get("Urban Pct", 50), 50)
    extra = 0.0
    # Dense + unaffordable = housing crisis
    if density > 1000 and afford < 4:
        extra += 0.3 * min(density, 10000) / 10000.0
    # Urban areas with low affordability
    if urban > 70 and afford < 3:
        extra += 0.2
    return extra


def _environmental_extraction_conditional(lga_row: pd.Series) -> float:
    """Environment becomes salient where extraction intensity is high AND
    poverty is high — communities bear pollution costs without benefits."""
    extraction = _safe_float(lga_row.get("Extraction Intensity", 0), 0)
    poverty = _safe_float(lga_row.get("Poverty Rate Pct", 30), 30)
    oil = _safe_float(lga_row.get("Oil Producing", 0), 0)
    extra = 0.0
    # Oil-producing + high poverty = "resource curse" anger
    if oil > 0 and poverty > 40:
        extra += 0.3 * min(poverty, 80) / 80.0
    # Intense extraction + poverty = environmental justice
    if extraction > 3 and poverty > 35:
        extra += 0.2 * min(extraction, 5) / 5.0
    return extra


def _energy_crisis_conditional(lga_row: pd.Series) -> float:
    """Energy policy becomes urgent where electricity access is low AND
    manufacturing/services need power — economic development blocked."""
    elec = _safe_float(lga_row.get("Access Electricity Pct", 50), 50)
    manuf = _safe_float(lga_row.get("Pct Livelihood Manufacturing", 15), 15)
    oil_active = _safe_float(lga_row.get("Oil Extraction Active", 0), 0)
    extra = 0.0
    # Low electricity + manufacturing base = frustrated businesses
    if elec < 40 and manuf > 10:
        extra += 0.25 * (1.0 - elec / 100.0)
    # Oil-producing area with poor electricity = paradox anger
    if oil_active > 0 and elec < 50:
        extra += 0.3 * (1.0 - elec / 100.0)
    return extra


def _fiscal_autonomy_conditional(lga_row: pd.Series) -> float:
    """Fiscal autonomy becomes hyper-salient where resource extraction
    co-exists with high poverty — the 'resource curse' paradox."""
    extraction = _safe_float(lga_row.get("Extraction Intensity", 0), 0)
    poverty = _safe_float(lga_row.get("Poverty Rate Pct", 30), 30)
    oil = _safe_float(lga_row.get("Oil Producing", 0), 0)
    gini = _safe_float(lga_row.get("Gini Proxy", 0.4), 0.4)
    extra = 0.0
    # Resource-rich but poor = rage at federal revenue distribution
    if oil > 0 and poverty > 40:
        extra += 0.3 * min(poverty, 80) / 80.0
    if extraction > 2 and gini > 0.45:
        extra += 0.2 * min(extraction, 5) / 5.0
    return extra


def _ethnic_quota_conditional(lga_row: pd.Series) -> float:
    """Ethnic quotas become hyper-salient in highly fragmented areas
    with high youth unemployment — competition for limited slots."""
    frag = ethnic_fragmentation(lga_row)
    youth_unemp = _safe_float(lga_row.get("Youth Unemployment Rate Pct", 46), 46)
    unemp = _safe_float(lga_row.get("Unemployment Rate Pct", 33), 33)
    extra = 0.0
    # High diversity + high unemployment = quota politics inflamed
    if frag > 0.7 and youth_unemp > 50:
        extra += 0.25 * frag
    if unemp > 40 and frag > 0.6:
        extra += 0.2 * min(unemp, 70) / 70.0
    return extra


def _fertility_policy_conditional(lga_row: pd.Series) -> float:
    """Fertility policy becomes charged where high fertility meets
    resource scarcity — overpopulation feels real, not abstract."""
    fertility = _safe_float(lga_row.get("Fertility Rate Est", 5), 5)
    poverty = _safe_float(lga_row.get("Poverty Rate Pct", 30), 30)
    osc = _safe_float(lga_row.get("Out of School Children Pct", 20), 20)
    extra = 0.0
    # High fertility + high poverty = population pressure politicized
    if fertility > 5.5 and poverty > 50:
        extra += 0.3 * min(fertility, 8) / 8.0
    # Very high OSC + high fertility = education system overwhelmed
    if osc > 40 and fertility > 5:
        extra += 0.2 * min(osc, 80) / 80.0
    return extra


def _language_policy_conditional(lga_row: pd.Series) -> float:
    """Language policy becomes urgent where multiple prestige languages
    compete — Arabic/English/Mandarin interface zones."""
    arabic = _safe_float(lga_row.get("Arabic Prestige", 0), 0)
    english = _safe_float(lga_row.get("English Prestige", 5), 5)
    mandarin = _safe_float(lga_row.get("Mandarin Presence", 0), 0)
    almajiri = _safe_float(lga_row.get("Almajiri Index", 0), 0)
    fem_lit = _safe_float(lga_row.get("Female Literacy Rate Pct", 50), 50)
    osc = _safe_float(lga_row.get("Out of School Children Pct", 20), 20)
    extra = 0.0
    # Arabic-English interface = language politics inflamed
    if arabic > 3 and english > 3:
        extra += 0.25 * min(arabic, 8) / 8.0
    # Mandarin presence + Arabic = trilingual tension
    if mandarin > 2 and arabic > 2:
        extra += 0.2 * min(mandarin, 8) / 8.0
    # High almajiri = Arabic vs secular education language debate
    if almajiri > 3:
        extra += 0.15 * min(almajiri, 5) / 5.0
    # Low female literacy + high OSC = language of instruction controversy
    if fem_lit < 40 and osc > 30:
        extra += 0.2 * (1.0 - fem_lit / 100.0)
    # High out-of-school + Arabic prestige = Quranic vs Western school debate
    if osc > 40 and arabic > 3:
        extra += 0.15 * min(osc, 80) / 80.0
    return extra


def _womens_rights_conditional(lga_row: pd.Series) -> float:
    """Women's rights become hyper-salient where gender parity gap
    is large AND modernizing forces are present — culture clash."""
    gpi = _safe_float(lga_row.get("Gender Parity Index", 0.8), 0.8)
    internet = _safe_float(lga_row.get("Internet Access Pct", 30), 30)
    fem_lit = _safe_float(lga_row.get("Female Literacy Rate Pct", 50), 50)
    pent_growth = _safe_float(lga_row.get("Pentecostal Growth", 0), 0)
    extra = 0.0
    # Low gender parity + internet = feminist vs conservative clash online
    if gpi < 0.6 and internet > 20:
        extra += 0.3 * (1.0 - gpi)
    # Low female literacy + Pentecostal growth = gender norms contested
    if fem_lit < 40 and pent_growth > 1:
        extra += 0.2 * (1.0 - fem_lit / 100.0)
    return extra


def _trade_policy_conditional(lga_row: pd.Series) -> float:
    """Trade policy becomes urgent where manufacturing meets Chinese
    competition — industrial areas facing import displacement."""
    manuf = _safe_float(lga_row.get("Pct Livelihood Manufacturing", 15), 15)
    chinese = _safe_float(lga_row.get("Chinese Economic Presence", 0), 0)
    informal = _safe_float(lga_row.get("Pct Livelihood Informal", 30), 30)
    extra = 0.0
    # Manufacturing + Chinese competition = trade anxiety
    if manuf > 15 and chinese > 3:
        extra += 0.25 * min(chinese, 8) / 8.0
    # Large informal economy + Chinese imports = market disruption anger
    if informal > 40 and chinese > 2:
        extra += 0.2 * min(informal, 70) / 70.0
    return extra


def _chinese_relations_conditional(lga_row: pd.Series) -> float:
    """Chinese relations become politically charged where Chinese economic
    presence is high AND unemployment/manufacturing creates winners and losers."""
    chinese = _safe_float(lga_row.get("Chinese Economic Presence", 0), 0)
    mandarin = _safe_float(lga_row.get("Mandarin Presence", 0), 0)
    unemp = _safe_float(lga_row.get("Unemployment Rate Pct", 33), 33)
    planned = _safe_float(lga_row.get("Planned City", 0), 0)
    extra = 0.0
    # Chinese presence + unemployment = WAFTA backlash
    if chinese > 3 and unemp > 35:
        extra += 0.3 * min(chinese, 8) / 8.0
    # Planned city (Chinese-built) = everyone has an opinion
    if planned > 0 and mandarin > 2:
        extra += 0.25
    return extra


def _traditional_authority_conditional(lga_row: pd.Series) -> float:
    """Traditional authority becomes hyper-salient where strong traditional
    institutions meet modernizing pressures — chiefs vs democracy."""
    trad_auth = _safe_float(lga_row.get("Trad Authority Index", 0), 0)
    trad_present = _safe_float(lga_row.get("Traditional Authority", 0), 0)
    urban = _safe_float(lga_row.get("Urban Pct", 50), 50)
    internet = _safe_float(lga_row.get("Internet Access Pct", 30), 30)
    conflict = _safe_float(lga_row.get("Conflict History", 0), 0)
    land_form = _safe_float(lga_row.get("Land Formalization Pct", 0), 0)
    extra = 0.0
    # Strong trad authority + urbanization = institutional clash
    if trad_auth > 3 and urban > 40:
        extra += 0.25 * min(trad_auth, 5) / 5.0
    # Traditional authority present + internet access = online debate
    if trad_present > 0 and internet > 30:
        extra += 0.2
    # Conflict zones where traditional mediation is needed
    if conflict >= 2 and trad_auth > 2:
        extra += 0.2 * (conflict / 5.0)
    # Land formalization threatens customary authority over land allocation
    if land_form > 30 and trad_auth > 3:
        extra += 0.15 * min(land_form, 80) / 80.0
    return extra


def _agricultural_policy_conditional(lga_row: pd.Series) -> float:
    """Agricultural policy becomes urgent where smallholder farming
    dominates AND food security is threatened by poverty/climate."""
    ag_pct = _safe_float(lga_row.get("Pct Livelihood Agriculture", 20), 20)
    poverty = _safe_float(lga_row.get("Poverty Rate Pct", 30), 30)
    fertility = _safe_float(lga_row.get("Fertility Rate Est", 5), 5)
    extra = 0.0
    # High agriculture + poverty = food security politicized
    if ag_pct > 40 and poverty > 50:
        extra += 0.3 * min(ag_pct, 80) / 80.0
    # High fertility + agriculture = population pressure on farmland
    if fertility > 5 and ag_pct > 30:
        extra += 0.2 * min(fertility, 8) / 8.0
    return extra


def _media_freedom_conditional(lga_row: pd.Series) -> float:
    """Media freedom becomes hyper-salient where internet penetration
    is high AND conflict/security creates censorship pressure."""
    internet = _safe_float(lga_row.get("Internet Access Pct", 30), 30)
    mobile = _safe_float(lga_row.get("Mobile Phone Penetration Pct", 50), 50)
    conflict = _safe_float(lga_row.get("Conflict History", 0), 0)
    fed_control = _safe_float(lga_row.get("Federal Control 2058", 0), 0)
    al_shahid = _safe_float(lga_row.get("Al-Shahid Influence", 0), 0)
    pent_growth = _safe_float(lga_row.get("Pentecostal Growth", 0), 0)
    extra = 0.0
    # High connectivity + conflict = censorship vs information freedom
    if internet > 40 and conflict > 2:
        extra += 0.25 * min(internet, 80) / 80.0
    # Federal control zones + mobile access = media suppression debate
    if fed_control > 0 and mobile > 50:
        extra += 0.2
    # Al-Shahid zones + internet = religious censorship vs free expression
    if al_shahid > 2 and internet > 20:
        extra += 0.2 * (al_shahid / 5.0)
    # Pentecostal growth + connectivity = moral censorship debate
    if pent_growth > 1.5 and internet > 40:
        extra += 0.15 * min(pent_growth, 3) / 3.0
    return extra


def _az_restructuring_conditional(lga_row: pd.Series) -> float:
    """AZ restructuring becomes hyper-salient where ethnic minorities
    feel dominated by larger groups within their current AZ."""
    frag = ethnic_fragmentation(lga_row)
    conflict = _safe_float(lga_row.get("Conflict History", 0), 0)
    trad_auth = _safe_float(lga_row.get("Trad Authority Index", 0), 0)
    extraction = _safe_float(lga_row.get("Extraction Intensity", 0), 0)
    extra = 0.0
    # High fragmentation + conflict = demand for new states/AZs
    if frag > 0.7 and conflict > 2:
        extra += 0.3 * frag
    # Extraction areas with diversity = resource-driven restructuring demands
    if extraction > 2 and frag > 0.6:
        extra += 0.2 * min(extraction, 5) / 5.0
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
            "Gini Proxy": 0.5,                   # High inequality → fiscal autonomy debate intensifies
            "is_colonial_eastern": 0.3,          # Eastern Region: strong autonomy/self-determination tradition
            "is_colonial_midwestern": 0.4,       # Mid-Western: extraction revenue → fiscal autonomy salient
        },
        conditional=_fiscal_autonomy_conditional,
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
            "Rail Corridor": 0.3,                    # Chinese-built rail → WAFTA salience
            "Internet Access Pct": 0.15 / 100.0,   # Connected areas: more WAFTA discourse
            "Urban Pct": 0.2 / 100.0,               # Urban: more exposure to Chinese trade
        },
        conditional=_chinese_relations_conditional,
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
            "Tertiary Institution": 0.15,        # Educated areas debate BIC reform
            "English Prestige": 0.1 / 10.0,     # Anglophone areas more BIC-aware
        },
        conditional=_bic_reform_conditional,
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
        conditional=_ethnic_quota_conditional,
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
            "Out of School Children Pct": 0.3 / 100.0,  # High OSC → population pressure is felt
            "Gender Parity Index": -0.5,              # Gender parity gap → fertility norms politically contested
            "literacy_fertility_tension": 0.5,         # Low female literacy + high fertility = demographic crisis salience
        },
        conditional=_fertility_policy_conditional,
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
            "is_colonial_eastern": 0.15,          # Eastern: federalist constitutional tradition
            "is_colonial_midwestern": 0.12,       # Mid-Western: minority-rights constitutional tradition
        },
        conditional=_constitutional_conflict_conditional,
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
            "inequality_extraction_mismatch": 0.5,  # Resource-rich + high inequality = resource curse anger
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
            "Unemployment Rate Pct": 0.3 / 100.0,   # Unemployment → housing insecurity
            "Poverty Rate Pct": 0.3 / 100.0,        # Poverty → housing deprivation
            "Major Urban Center": 0.8,               # Major cities: housing is top political issue
            "Gini Proxy": 0.5,                        # High inequality → housing becomes politically contested
            "Land Formalization Pct": 0.3 / 100.0,   # Formalized land → housing market issues politically salient
        },
        conditional=_housing_pressure_conditional,
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
            "Internet Access Pct": 0.2 / 100.0,   # Connected areas: education policy debates online
            "Mobile Phone Penetration Pct": 0.15 / 100.0,  # Mobile learning → education debates amplified
            "English Prestige": 0.2 / 10.0,       # English prestige → language-of-instruction debates → education salient
            "Female Literacy Rate Pct": -0.01,    # Low female literacy → girls' education as political issue
            "literacy_fertility_tension": 0.4,       # Low literacy + high fertility = education system overwhelmed
        },
        conditional=_education_deprivation_conditional,
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
            "Cobalt Extraction Active": 0.3,       # Cobalt mining: automation disruption in extraction
            "Poverty Rate Pct": 0.2 / 100.0,      # Poverty → more anxious about job displacement
            "Major Urban Center": 0.4,             # Major cities: industrial base, automation anxiety
            "Road Quality Index": 0.1 / 10.0,       # Good roads → manufacturing corridor → labor politics
        },
        conditional=_youth_unemployment_conditional,
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
            "Youth Unemployment Rate Pct": 0.2 / 100.0,  # Jobless youth: security vacuum salience
            "Poverty Rate Pct": 0.15 / 100.0,    # Poor areas: military as employer/security provider
            "Border LGA": 0.3,                    # Actual border LGAs: military presence visible
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
            "Internet Access Pct": 0.2 / 100.0,   # Internet: immigration debates amplified online
        },
        conditional=_immigration_border_conditional,
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
        conditional=_language_policy_conditional,
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
            "Out of School Children Pct": 0.5 / 100.0,  # High OSC → girls' education contested → gender salient
            "Primary Enrollment Pct": -0.2 / 100.0,  # Low primary enrollment → girls excluded → gender rights contested
            "Internet Access Pct": 0.3 / 100.0,   # Internet: women's rights campaigns amplified online
            "Mobile Phone Penetration Pct": 0.2 / 100.0,  # Phone access: gender violence reporting, activism
        },
        conditional=_womens_rights_conditional,
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
            "Traditional Authority": 0.5,          # Binary: presence of active trad authority amplifies debate
            "is_colonial_western": 0.3,             # Western: Oba institution deeply embedded → debate
            "is_colonial_midwestern": 0.2,          # Mid-Western: Oba of Benin → trad authority relevant
            "modernization_clash": 0.5,              # Internet + trad authority + Pentecostal growth = cultural clash
        },
        conditional=_traditional_authority_conditional,
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
            "Urban Pct": 0.3 / 100.0,             # Urban: traffic, congestion, infra overload
            "Pct Livelihood Manufacturing": 0.3 / 100.0,  # Industrial: reliable power + roads critical
            "Out of School Children Pct": 0.15 / 100.0,   # High OSC → school infrastructure deficit
        },
        conditional=_infrastructure_crisis_conditional,
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
            "% Fulani": 0.3 / 100.0,              # Fulani presence: herder-farmer politics
            "Urban Pct": 0.3 / 100.0,             # Urban: property rights, zoning, gentrification
            "Extraction Intensity": 0.2 / 5.0,    # Extraction: land acquisition conflicts
            "Oil Producing": 0.15,                 # Oil zones: community vs corporation land disputes
        },
        conditional=_herder_farmer_conditional,
    ),
    # 19. Taxation
    SalienceRule(
        issue_name="taxation",
        base_weight=0.10,
        feature_coefficients={
            "Gini Proxy": 1.0,
            "Poverty Rate Pct": 0.5 / 100.0,
            "GDP Per Capita Est": 0.3 / 10000.0,
            "CPI Pct": 1.0 / 100.0,               # Inflation makes tax policy salient
            "Urban Pct": 0.2 / 100.0,             # Urban areas more tax-aware
            "Pct Livelihood Informal": 0.3 / 100.0,  # Informal economy = tax evasion debates
            "Extraction Intensity": 0.2 / 5.0,    # Extraction → "where do our taxes go?"
            "border_proximity": 0.15,              # Border areas: customs/tariff debates
        },
        conditional=_taxation_inequality_conditional,
    ),
    # 20. Agricultural Policy
    SalienceRule(
        issue_name="agricultural_policy",
        base_weight=0.05,
        feature_coefficients={
            "Pct Livelihood Agriculture": 2.5 / 100.0,
            "rural_pct": 0.5 / 100.0,
            "Poverty Rate Pct": 0.5 / 100.0,
            "Food Inflation Pct": 1.5 / 100.0,    # Food price spikes politicize agriculture
            "Fertility Rate Est": 0.2,             # High-fertility rural areas = food security
            "Market Access Index": -0.3 / 10.0,   # Poor market access raises ag salience
            "% Hausa": 0.15 / 100.0,              # Hausa: agrarian heartland
            "% Fulani": 0.2 / 100.0,              # Fulani: pastoralist/herder-farmer conflicts
            "% Tiv": 0.15 / 100.0,                # Tiv: Middle Belt farming communities
        },
        conditional=_agricultural_policy_conditional,
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
            "Tertiary Institution": 0.15,          # University areas: bioethics debates
            "GDP Per Capita Est": 0.3 / 90000.0,  # Wealthier areas: more bio-enhancement exposure
            "% Pada": 0.8 / 100.0,                # Padà communities: bio-enhancement is identity issue
            "Planned City": 0.3,                   # Planned cities: tech-forward, more enhancement
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
            "Road Quality Index": 0.1 / 10.0,       # Good roads → trade-connected → trade policy matters
            "Pct Livelihood Services": 0.3 / 100.0,  # Service economy cares about trade openness
            "% Igbo": 0.2 / 100.0,                 # Igbo: entrepreneurial/trade culture
            "% Yoruba": 0.15 / 100.0,              # Yoruba: commercial tradition
            "Cobalt Extraction Active": 0.5,        # Cobalt: global battery supply chain trade
            "Refinery Present": 0.3,                # Refinery: export-oriented economy
            "is_colonial_western": 0.3,              # Western Region: Yoruba commercial tradition → trade politics
            "is_colonial_eastern": 0.2,              # Eastern Region: Igbo entrepreneurial culture → trade matters
        },
        conditional=_trade_policy_conditional,
    ),
    # 23. Environmental Regulation
    SalienceRule(
        issue_name="environmental_regulation",
        base_weight=0.05,
        feature_coefficients={
            "Extraction Intensity": 1.5 / 5.0,
            "Oil Producing": 1.0,
            "Cobalt Extraction Active": 1.0,
            "Oil Extraction Active": 0.8,            # Active oil → environmental concern amplified
            "Other Mining Active": 0.5,              # Active mining → environmental degradation
            "conflict_severity": 0.2 / 5.0,        # Extraction + conflict → environmental anger
            "Urban Pct": 0.2 / 100.0,              # Urban areas more environmentally aware
            "% Ijaw": 0.3 / 100.0,                 # Ijaw: oil spill devastation in Delta
            "% Edo": 0.15 / 100.0,                 # Edo: Benin environmental concerns
            "is_colonial_midwestern": 0.5,          # Mid-Western: Edo/Delta extraction → environmental politics
            "is_colonial_eastern": 0.2,             # Eastern: Niger Delta fringe → environmental awareness
        },
        conditional=_environmental_extraction_conditional,
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
            "is_colonial_western": 0.3,             # Western: Lagos media culture, Yoruba press tradition
            "modernization_clash": 0.3,              # Internet + trad authority + Pentecostal = censorship debates
        },
        conditional=_media_freedom_conditional,
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
            "Out of School Children Pct": 0.3 / 100.0,  # High OSC → systemic deprivation → health salient
            "Internet Access Pct": 0.15 / 100.0,  # Internet: health awareness campaigns, COVID legacy
        },
        conditional=_healthcare_crisis_conditional,
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
            "Internet Access Pct": 0.15 / 100.0,   # Online Pada identity discourse
            "Tertiary Institution": 0.1,            # University campuses: Pada rights movements
        },
        conditional=_pada_tension_conditional,
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
            "Oil Extraction Active": 0.8,         # Active oil → energy politics salient
            "Other Mining Active": 0.3,           # Mining → energy infrastructure demands
        },
        conditional=_energy_crisis_conditional,
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
            "is_colonial_eastern": 0.3,              # Eastern: Biafra memory, Igbo self-determination
            "is_colonial_midwestern": 0.4,           # Mid-Western: minority status → restructuring demand
        },
        conditional=_az_restructuring_conditional,
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
        regions_raw = lga_data["Colonial Era Region"].fillna("").astype(str)
        regions = regions_raw.str.lower()
        border_prox = ((regions.str.contains("north", na=False)) |
                       (regions.str.contains("border", na=False)) |
                       (regions.str.contains("sahel", na=False))).astype(float).values
        # Categorical colonial region indicators
        col_western = (regions_raw.str.strip() == "Western").astype(float).values
        col_eastern = (regions_raw.str.strip() == "Eastern").astype(float).values
        col_midwestern = (regions_raw.str.strip() == "Mid-Western").astype(float).values
    else:
        border_prox = np.zeros(n_lga)
        col_western = np.zeros(n_lga)
        col_eastern = np.zeros(n_lga)
        col_midwestern = np.zeros(n_lga)

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
        "is_colonial_western": col_western,
        "is_colonial_eastern": col_eastern,
        "is_colonial_midwestern": col_midwestern,
    }

    # Pre-extract columns used in conditionals (avoid repeat _col calls)
    al_shahid_arr = _col("Al-Shahid Influence")
    extraction_int = _col("Extraction Intensity")
    federal_ctrl = _col("Federal Control 2058")
    pada_arr = _col("% Pada")
    tertiary_inst = _col("Tertiary Institution")
    bio_enh_pct = _col("Biological Enhancement Pct")
    pent_col = _col("Pentecostal Growth")

    # Additional columns for vectorized conditionals
    poverty_arr = _col("Poverty Rate Pct", 30.0)
    oil_prod_arr = _col("Oil Producing")
    gini_arr = _col("Gini Proxy", 0.4)
    youth_unemp_arr = _col("Youth Unemployment Rate Pct", 46.0)
    unemp_arr = _col("Unemployment Rate Pct", 33.0)
    fertility_arr = _col("Fertility Rate Est", 5.0)
    osc_arr = _col("Out of School Children Pct", 20.0)
    internet_arr = _col("Internet Access Pct", 30.0)
    mobile_arr = _col("Mobile Phone Penetration Pct", 50.0)
    housing_afford_arr = _col("Housing Affordability", 5.0)
    chinese_arr = _col("Chinese Economic Presence")
    mandarin_arr = _col("Mandarin Presence")
    planned_arr = _col("Planned City")
    trad_auth_arr = _col("Trad Authority Index")
    trad_present_arr = _col("Traditional Authority")
    land_form_arr = _col("Land Formalization Pct")
    almajiri_arr = _col("Almajiri Index")
    arabic_arr = _col("Arabic Prestige")
    english_arr = _col("English Prestige", 5.0)
    gpi_arr = _col("Gender Parity Index", 0.8)
    ag_pct_arr = _col("Pct Livelihood Agriculture", 20.0)
    manuf_arr = _col("Pct Livelihood Manufacturing", 15.0)
    informal_arr = _col("Pct Livelihood Informal", 30.0)
    fulani_arr = _col("% Fulani")
    oil_active_cond = _col("Oil Extraction Active")
    trad_practice_arr = _col("Traditionalist Practice")
    bic_eff_arr = _col("BIC Effectiveness", 5.0)

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

        # Vectorised conditional terms — all 28 issue conditionals
        if rule.conditional is not None:
            if rule.issue_name == "sharia_jurisdiction":
                mask_sc = (muslim_arr > 30) & (christian_arr > 10)
                w += np.where(mask_sc, (pent_col / 3.0) * 0.6, 0.0)
                mask_as = (al_shahid_arr > 2) & (muslim_arr > 50)
                w += np.where(mask_as, 0.3 * (al_shahid_arr / 5.0), 0.0)
            elif rule.issue_name == "fiscal_autonomy":
                w += np.where((oil_prod_arr > 0) & (poverty_arr > 40),
                              0.3 * np.minimum(poverty_arr, 80.0) / 80.0, 0.0)
                w += np.where((extraction_int > 2) & (gini_arr > 0.45),
                              0.2 * np.minimum(extraction_int, 5.0) / 5.0, 0.0)
            elif rule.issue_name == "chinese_relations":
                w += np.where((chinese_arr > 3) & (unemp_arr > 35),
                              0.3 * np.minimum(chinese_arr, 8.0) / 8.0, 0.0)
                w += np.where((planned_arr > 0) & (mandarin_arr > 2), 0.25, 0.0)
            elif rule.issue_name == "bic_reform":
                w += np.where((pada_arr > 5) & (bic_eff_arr < 4),
                              0.3 * np.minimum(pada_arr, 30.0) / 30.0, 0.0)
                w += np.where((pada_arr > 3) & (urban > 60), 0.15, 0.0)
            elif rule.issue_name == "ethnic_quotas":
                w += np.where((eth_frag > 0.7) & (youth_unemp_arr > 50),
                              0.25 * eth_frag, 0.0)
                w += np.where((unemp_arr > 40) & (eth_frag > 0.6),
                              0.2 * np.minimum(unemp_arr, 70.0) / 70.0, 0.0)
            elif rule.issue_name == "fertility_policy":
                w += np.where((fertility_arr > 5.5) & (poverty_arr > 50),
                              0.3 * np.minimum(fertility_arr, 8.0) / 8.0, 0.0)
                w += np.where((osc_arr > 40) & (fertility_arr > 5),
                              0.2 * np.minimum(osc_arr, 80.0) / 80.0, 0.0)
            elif rule.issue_name == "constitutional_structure":
                w += np.where((eth_frag > 0.6) & (conflict >= 2),
                              0.3 * np.minimum(conflict, 5.0) / 5.0, 0.0)
                w += np.where((trad_auth_arr > 3) & (eth_frag > 0.5),
                              0.15 * (trad_auth_arr / 5.0), 0.0)
            elif rule.issue_name == "resource_revenue":
                mask_rc = (conflict >= 2) & (extraction_int >= 2)
                w += np.where(mask_rc,
                              0.5 * np.minimum(conflict, 5.0) / 5.0
                              * np.minimum(extraction_int, 5.0) / 5.0, 0.0)
            elif rule.issue_name == "housing":
                w += np.where((density > 1000) & (housing_afford_arr < 4),
                              0.3 * np.minimum(density, 10000.0) / 10000.0, 0.0)
                w += np.where((urban > 70) & (housing_afford_arr < 3), 0.2, 0.0)
            elif rule.issue_name == "education":
                w += np.where((osc_arr > 40) & (youth_unemp_arr > 50),
                              0.25 * np.minimum(osc_arr, 80.0) / 80.0, 0.0)
                w += np.where((almajiri_arr > 2) & (osc_arr > 30),
                              0.2 * np.minimum(almajiri_arr, 5.0) / 5.0, 0.0)
            elif rule.issue_name == "labor_automation":
                w += np.where((youth_unemp_arr > 60) & (chinese_arr > 3),
                              0.3 * np.minimum(youth_unemp_arr, 80.0) / 80.0, 0.0)
                w += np.where((youth_unemp_arr > 50) & (internet_arr > 60), 0.15, 0.0)
            elif rule.issue_name == "military_role":
                mask_mc = conflict >= 3
                w += np.where(mask_mc, 0.5 * (conflict / 5.0), 0.0)
                w += np.where(mask_mc & (federal_ctrl > 0), 0.3, 0.0)
            elif rule.issue_name == "immigration":
                w += np.where((border_prox > 0.5) & (unemp_arr > 30),
                              0.3 * np.minimum(unemp_arr, 60.0) / 60.0, 0.0)
                w += np.where((border_prox > 0.5) & (housing_afford_arr < 4), 0.2, 0.0)
            elif rule.issue_name == "language_policy":
                w += np.where((arabic_arr > 3) & (english_arr > 3),
                              0.25 * np.minimum(arabic_arr, 8.0) / 8.0, 0.0)
                w += np.where((mandarin_arr > 2) & (arabic_arr > 2),
                              0.2 * np.minimum(mandarin_arr, 8.0) / 8.0, 0.0)
                w += np.where(almajiri_arr > 3,
                              0.15 * np.minimum(almajiri_arr, 5.0) / 5.0, 0.0)
                w += np.where((fem_lit < 40) & (osc_arr > 30),
                              0.2 * (1.0 - fem_lit / 100.0), 0.0)
                w += np.where((osc_arr > 40) & (arabic_arr > 3),
                              0.15 * np.minimum(osc_arr, 80.0) / 80.0, 0.0)
            elif rule.issue_name == "womens_rights":
                w += np.where((gpi_arr < 0.6) & (internet_arr > 20),
                              0.3 * (1.0 - gpi_arr), 0.0)
                w += np.where((fem_lit < 40) & (pent_col > 1),
                              0.2 * (1.0 - fem_lit / 100.0), 0.0)
            elif rule.issue_name == "traditional_authority":
                w += np.where((trad_auth_arr > 3) & (urban > 40),
                              0.25 * np.minimum(trad_auth_arr, 5.0) / 5.0, 0.0)
                w += np.where((trad_present_arr > 0) & (internet_arr > 30), 0.2, 0.0)
                w += np.where((conflict >= 2) & (trad_auth_arr > 2),
                              0.2 * (conflict / 5.0), 0.0)
                w += np.where((land_form_arr > 30) & (trad_auth_arr > 3),
                              0.15 * np.minimum(land_form_arr, 80.0) / 80.0, 0.0)
            elif rule.issue_name == "infrastructure":
                w += np.where((elec < 40) & (density > 500),
                              0.3 * (1.0 - elec / 100.0), 0.0)
                w += np.where((water < 30) & (density > 300),
                              0.2 * (1.0 - water / 100.0), 0.0)
            elif rule.issue_name == "land_tenure":
                w += np.where((fulani_arr > 5) & (ag_pct_arr > 40),
                              0.3 * np.minimum(fulani_arr, 30.0) / 30.0, 0.0)
                w += np.where((conflict >= 2) & (fulani_arr > 5),
                              0.2 * (conflict / 5.0), 0.0)
            elif rule.issue_name == "taxation":
                w += np.where((gini_arr > 0.45) & (extraction_int > 2),
                              0.25 * np.minimum(extraction_int, 5.0) / 5.0, 0.0)
                w += np.where((poverty_arr > 50) & (gini_arr > 0.40),
                              0.2 * np.minimum(poverty_arr, 80.0) / 80.0, 0.0)
            elif rule.issue_name == "agricultural_policy":
                w += np.where((ag_pct_arr > 40) & (poverty_arr > 50),
                              0.3 * np.minimum(ag_pct_arr, 80.0) / 80.0, 0.0)
                w += np.where((fertility_arr > 5) & (ag_pct_arr > 30),
                              0.2 * np.minimum(fertility_arr, 8.0) / 8.0, 0.0)
            elif rule.issue_name == "biological_enhancement":
                w += np.where(bio_enh_pct > 10, 0.3 * (bio_enh_pct / 100.0), 0.0)
                w += np.where((pada_arr > 5) & (tertiary_inst > 0), 0.2, 0.0)
            elif rule.issue_name == "trade_policy":
                w += np.where((manuf_arr > 15) & (chinese_arr > 3),
                              0.25 * np.minimum(chinese_arr, 8.0) / 8.0, 0.0)
                w += np.where((informal_arr > 40) & (chinese_arr > 2),
                              0.2 * np.minimum(informal_arr, 70.0) / 70.0, 0.0)
            elif rule.issue_name == "environmental_regulation":
                w += np.where((oil_prod_arr > 0) & (poverty_arr > 40),
                              0.3 * np.minimum(poverty_arr, 80.0) / 80.0, 0.0)
                w += np.where((extraction_int > 3) & (poverty_arr > 35),
                              0.2 * np.minimum(extraction_int, 5.0) / 5.0, 0.0)
            elif rule.issue_name == "media_freedom":
                w += np.where((internet_arr > 40) & (conflict > 2),
                              0.25 * np.minimum(internet_arr, 80.0) / 80.0, 0.0)
                w += np.where((federal_ctrl > 0) & (mobile_arr > 50), 0.2, 0.0)
                w += np.where((al_shahid_arr > 2) & (internet_arr > 20),
                              0.2 * (al_shahid_arr / 5.0), 0.0)
                w += np.where((pent_col > 1.5) & (internet_arr > 40),
                              0.15 * np.minimum(pent_col, 3.0) / 3.0, 0.0)
            elif rule.issue_name == "healthcare":
                w += np.where((health < 30) & (fertility_arr > 5),
                              0.3 * (1.0 - health / 100.0), 0.0)
                w += np.where((poverty_arr > 50) & (health < 40),
                              0.2 * np.minimum(poverty_arr, 80.0) / 80.0, 0.0)
            elif rule.issue_name == "pada_status":
                w += np.where((pada_arr > 5) & (trad_practice_arr > 2),
                              0.25 * np.minimum(pada_arr, 25.0) / 25.0, 0.0)
                w += np.where((bio_enh_pct > 15) & (pada_arr > 10),
                              0.2 * np.minimum(bio_enh_pct, 50.0) / 50.0, 0.0)
            elif rule.issue_name == "energy_policy":
                w += np.where((elec < 40) & (manuf_arr > 10),
                              0.25 * (1.0 - elec / 100.0), 0.0)
                w += np.where((oil_active_cond > 0) & (elec < 50),
                              0.3 * (1.0 - elec / 100.0), 0.0)
            elif rule.issue_name == "az_restructuring":
                w += np.where((eth_frag > 0.7) & (conflict > 2),
                              0.3 * eth_frag, 0.0)
                w += np.where((extraction_int > 2) & (eth_frag > 0.6),
                              0.2 * np.minimum(extraction_int, 5.0) / 5.0, 0.0)
            else:
                # Generic fallback for any future custom conditionals
                for idx in range(n_lga):
                    w[idx] += rule.conditional(lga_data.iloc[idx])

        np.maximum(w, 0.0, out=w)
        result[:, i] = w

    # Normalize each row to sum to 1
    row_sums = result.sum(axis=1, keepdims=True)
    nonzero = row_sums > 0
    result = np.where(nonzero, result / np.maximum(row_sums, 1e-30), result)

    return result


def compute_base_awareness(
    parties: list,
    lga_data: pd.DataFrame,
) -> np.ndarray:
    """
    Compute initial awareness (n_lga, J) before any campaign actions.

    Factors:
    - Floor: every party has minimal name recognition (0.05)
    - Ethnic match: voters are more aware of parties whose candidate
      shares their ethnicity (information travels through ethnic networks)
    - Religious alignment: parties with strong religious signals are
      more known in their religious community
    - Media infrastructure: high-connectivity LGAs hear about everyone
    - Major urban / planned cities: political junkies, high information

    In campaign mode, this is the starting state. Campaigns raise awareness
    through rallies, advertising, media, manifesto publication, etc.

    In static mode (no campaign), this function is NOT called -- awareness
    defaults to 1.0 everywhere, preserving existing engine behavior.
    """
    n_lga = len(lga_data)
    J = len(parties)
    # Floor: every party on the ballot has baseline name recognition.
    # 0.60 keeps campaign mode close to static baseline (awareness=1.0).
    # Voters know ~60% of any ballot party's positions through ballot
    # access, news, and word-of-mouth. Campaign actions fill the gap.
    awareness = np.full((n_lga, J), 0.60, dtype=np.float32)

    def _col(name: str, default: float = 0.0) -> np.ndarray:
        if name in lga_data.columns:
            s = lga_data[name]
            arr = pd.to_numeric(s, errors="coerce").fillna(default).values.astype(float)
            np.nan_to_num(arr, copy=False, nan=default)
            return arr
        return np.full(n_lga, default)

    # Media infrastructure: high-connectivity LGAs hear about all parties.
    # Coefficient 0.15 keeps total media contribution moderate (~0.075 mean).
    urban = _col("Urban Pct", 30.0) / 100.0
    internet = _col("Internet Access Pct", 50.0) / 100.0
    mobile = _col("Mobile Phone Penetration Pct", 50.0) / 100.0
    literacy = _col("Adult Literacy Rate Pct", 50.0) / 100.0
    media_factor = 0.3 * urban + 0.25 * internet + 0.25 * mobile + 0.2 * literacy
    awareness += 0.15 * media_factor[:, np.newaxis].astype(np.float32)

    # Major urban centers + planned cities: high political awareness
    major_urban = _col("Major Urban Center", 0.0)
    planned = _col("Planned City", 0.0)
    awareness += 0.05 * major_urban[:, np.newaxis].astype(np.float32)
    awareness += 0.04 * planned[:, np.newaxis].astype(np.float32)

    for j, party in enumerate(parties):
        # Ethnic match: voters know parties whose leader shares their ethnicity.
        # Ethnic networks are the primary awareness channel in Nigerian politics.
        leader_eth = getattr(party, "leader_ethnicity", "")
        if leader_eth:
            eth_col_name = f"% {leader_eth}"
            if eth_col_name in lga_data.columns:
                eth_pct = lga_data[eth_col_name].fillna(0).values.astype(float) / 100.0
                awareness[:, j] += (0.15 * eth_pct).astype(np.float32)

        # Religious alignment
        rel_align = getattr(party, "religious_alignment", "")
        if rel_align:
            rel_col = f"% {rel_align}"
            if rel_col in lga_data.columns:
                rel_pct = lga_data[rel_col].fillna(0).values.astype(float) / 100.0
                awareness[:, j] += (0.08 * rel_pct).astype(np.float32)

    return np.clip(awareness, 0.60, 1.0)


def compute_turnout_ceiling(lga_data: pd.DataFrame) -> np.ndarray:
    """
    Compute maximum achievable turnout from infrastructure/logistics.

    Returns shape (n_lga,) with values in [0.25, 0.95].
    """
    n_lga = len(lga_data)

    def _col(name: str, default: float = 0.0) -> np.ndarray:
        if name in lga_data.columns:
            s = lga_data[name]
            arr = pd.to_numeric(s, errors="coerce").fillna(default).values.astype(float)
            np.nan_to_num(arr, copy=False, nan=default)
            return arr
        return np.full(n_lga, default)

    urban = _col("Urban Pct", 30.0) / 100.0
    road = _col("Road Quality Index", 5.0) / 10.0
    electricity = _col("Access Electricity Pct", 50.0) / 100.0
    mobile = _col("Mobile Phone Penetration Pct", 50.0) / 100.0
    conflict = _col("Conflict History", 0.0) / 5.0
    fed_control = _col("Federal Control 2058", 0.0)
    planned = _col("Planned City", 0.0)
    major_urban = _col("Major Urban Center", 0.0)
    al_shahid = _col("Al-Shahid Influence", 0.0) / 5.0

    ceiling = (
        0.40
        + 0.20 * urban
        + 0.15 * road
        + 0.05 * electricity
        + 0.05 * mobile
        + 0.10 * planned
        + 0.10 * major_urban
        - 0.15 * np.clip(conflict, 0.0, 1.0)
        - 0.10 * np.clip(al_shahid, 0.0, 1.0)
        - 0.05 * fed_control
    )
    return np.clip(ceiling, 0.25, 0.95).astype(np.float32)
