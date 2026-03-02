"""
Voter type generation and ideal point mapping for the LAGOS-2058 engine.

The 8-dimensional voter typology produces 87,480 voter types:
    15 ethnicities × 9 religious sub-categories × 3 settings × 4 age cohorts
    × 3 education levels × 2 genders × 6 livelihoods × 3 income brackets
    = 87,480 types

For each LGA, type weights (population fractions) are estimated using an
independence assumption with conditional adjustments.

Ideal points in 28-dimensional issue space are derived from demographic
features using a coefficient table (pluggable for calibration).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

import numpy as np
import pandas as pd

from .config import N_ISSUES
from .ethnic_affinity import ETHNIC_GROUPS
from .religious_affinity import RELIGIOUS_GROUPS, split_religious_subcategories

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Category definitions
# ---------------------------------------------------------------------------

ETHNICITIES: list[str] = ETHNIC_GROUPS  # 15 + 2 = 17 (includes catch-alls)

# But for the typology we use the 15 named groups (excluding Other-North/Other-South)
# because the LGA data has specific percentages for these. The "Other" category maps
# to the appropriate catch-all based on northern/southern context.
_CORE_ETHNICITIES: list[str] = [
    "Hausa", "Fulani", "Hausa-Fulani Undiff", "Yoruba", "Igbo",
    "Ijaw", "Kanuri", "Tiv", "Nupe", "Edo", "Ibibio",
    "Niger Delta Minorities", "Middle Belt Minorities", "Pada", "Naijin",
]
N_ETHNICITIES = len(_CORE_ETHNICITIES)  # 15

RELIGIONS: list[str] = RELIGIOUS_GROUPS  # 9
N_RELIGIONS = len(RELIGIONS)

SETTINGS: list[str] = ["Urban", "Peri-urban", "Rural"]
N_SETTINGS = 3

AGE_COHORTS: list[str] = ["18-24", "25-34", "35-49", "50+"]
N_AGE = 4

EDUCATIONS: list[str] = ["Below secondary", "Secondary", "Tertiary"]
N_EDUCATION = 3

GENDERS: list[str] = ["Male", "Female"]
N_GENDER = 2

LIVELIHOODS: list[str] = [
    "Smallholder", "Commercial ag", "Trade/informal",
    "Formal private", "Public sector", "Unemployed/student",
]
N_LIVELIHOOD = 6

INCOMES: list[str] = ["Bottom 40%", "Middle 40%", "Top 20%"]
N_INCOME = 3

TOTAL_TYPES = N_ETHNICITIES * N_RELIGIONS * N_SETTINGS * N_AGE * N_EDUCATION * N_GENDER * N_LIVELIHOOD * N_INCOME
# = 15 × 9 × 3 × 4 × 3 × 2 × 6 × 3 = 87,480


@dataclass(frozen=True)
class VoterType:
    """One demographic voter type (combination of 8 attributes)."""
    ethnicity: str
    religion: str
    setting: str
    age_cohort: str
    education: str
    gender: str
    livelihood: str
    income: str

    @property
    def is_muslim(self) -> bool:
        return self.religion in ("Tijaniyya", "Qadiriyya", "Al-Shahid", "Mainstream Sunni")

    @property
    def is_christian(self) -> bool:
        return self.religion in ("Pentecostal", "Catholic", "Mainline Protestant")

    @property
    def is_al_shahid(self) -> bool:
        return self.religion == "Al-Shahid"

    @property
    def is_tijaniyya(self) -> bool:
        return self.religion == "Tijaniyya"

    @property
    def is_tertiary(self) -> bool:
        return self.education == "Tertiary"

    @property
    def is_urban(self) -> bool:
        return self.setting == "Urban"

    @property
    def is_rural(self) -> bool:
        return self.setting == "Rural"

    @property
    def is_pada(self) -> bool:
        return self.ethnicity == "Pada"

    @property
    def is_naijin(self) -> bool:
        return self.ethnicity == "Naijin"

    @property
    def is_hausa_fulani(self) -> bool:
        return self.ethnicity in ("Hausa", "Fulani", "Hausa-Fulani Undiff")

    @property
    def is_yoruba(self) -> bool:
        return self.ethnicity == "Yoruba"

    @property
    def is_igbo(self) -> bool:
        return self.ethnicity == "Igbo"

    @property
    def is_ijaw(self) -> bool:
        return self.ethnicity == "Ijaw"

    @property
    def is_female(self) -> bool:
        return self.gender == "Female"

    @property
    def is_youth(self) -> bool:
        return self.age_cohort == "18-24"

    @property
    def is_older(self) -> bool:
        return self.age_cohort == "50+"

    @property
    def is_top_income(self) -> bool:
        return self.income == "Top 20%"

    @property
    def is_bottom_income(self) -> bool:
        return self.income == "Bottom 40%"

    @property
    def is_civil_servant(self) -> bool:
        return self.livelihood == "Public sector"

    @property
    def is_formal_sector(self) -> bool:
        return self.livelihood == "Formal private"

    @property
    def is_informal(self) -> bool:
        return self.livelihood == "Trade/informal"

    @property
    def is_smallholder(self) -> bool:
        return self.livelihood == "Smallholder"

    @property
    def is_commercial_ag(self) -> bool:
        return self.livelihood == "Commercial ag"

    @property
    def is_unemployed(self) -> bool:
        return self.livelihood == "Unemployed/student"

    @property
    def is_minority(self) -> bool:
        """Not in one of the 5 majority groups."""
        return self.ethnicity not in (
            "Hausa", "Fulani", "Hausa-Fulani Undiff", "Yoruba", "Igbo"
        )

    @property
    def is_majority(self) -> bool:
        return not self.is_minority


@lru_cache(maxsize=1)
def generate_all_voter_types() -> list[VoterType]:
    """
    Generate all 87,480 voter types.

    Returns a list ordered by (ethnicity, religion, setting, age, education,
    gender, livelihood, income) — the order is consistent across all calls.
    """
    types = []
    for eth in _CORE_ETHNICITIES:
        for rel in RELIGIONS:
            for sett in SETTINGS:
                for age in AGE_COHORTS:
                    for edu in EDUCATIONS:
                        for gen in GENDERS:
                            for liv in LIVELIHOODS:
                                for inc in INCOMES:
                                    types.append(VoterType(
                                        ethnicity=eth, religion=rel,
                                        setting=sett, age_cohort=age,
                                        education=edu, gender=gen,
                                        livelihood=liv, income=inc,
                                    ))
    return types


# ---------------------------------------------------------------------------
# Column name constants (match data_loader.py)
# ---------------------------------------------------------------------------

_COL_ETHNIC_PREFIX = "% "
_ETHNIC_COL_MAP: dict[str, str] = {
    "Hausa": "% Hausa",
    "Fulani": "% Fulani",
    "Hausa-Fulani Undiff": "% Hausa Fulani Undiff",
    "Yoruba": "% Yoruba",
    "Igbo": "% Igbo",
    "Ijaw": "% Ijaw",
    "Kanuri": "% Kanuri",
    "Tiv": "% Tiv",
    "Nupe": "% Nupe",
    "Edo": "% Edo Bini",
    "Ibibio": "% Ibibio",
    # Niger Delta Minorities: sum of several groups
    "Niger Delta Minorities": None,
    # Middle Belt Minorities: sum of several groups
    "Middle Belt Minorities": None,
    "Pada": "% Pada",
    "Naijin": "% Naijin",
}

_NIGER_DELTA_COLS = [
    "% Ijaw", "% Ogoni", "% Ikwerre", "% Etche", "% Pere", "% Isoko",
    "% Itsekiri", "% Urhobo",
]

_MIDDLE_BELT_COLS = [
    "% Tiv", "% Nupe", "% Ebira", "% Gwari Gbagyi", "% Idoma",
    "% Berom", "% Angas", "% Igala", "% Jukun", "% Ham Jaba",
]


def _get_ethnic_pcts(lga_row: pd.Series) -> dict[str, float]:
    """Return percentage for each of the 15 core ethnic groups."""
    result = {}
    for eth, col in _ETHNIC_COL_MAP.items():
        if col is not None:
            result[eth] = max(0.0, float(lga_row.get(col, 0.0)))
        elif eth == "Niger Delta Minorities":
            result[eth] = max(0.0, sum(
                float(lga_row.get(c, 0.0)) for c in _NIGER_DELTA_COLS
            ))
        elif eth == "Middle Belt Minorities":
            result[eth] = max(0.0, sum(
                float(lga_row.get(c, 0.0)) for c in _MIDDLE_BELT_COLS
            ))
    return result


def compute_type_weights(
    lga_row: pd.Series,
    voter_types: list[VoterType],
    weight_threshold: float = 1e-8,
) -> np.ndarray:
    """
    Compute population weight for each voter type in the given LGA.

    Uses an independence assumption with conditional adjustments:
    - Religion conditioned on ethnicity (northern ethnicities → Muslim sub-categories)
    - Livelihood conditioned on setting
    - Income conditioned on education and livelihood

    Parameters
    ----------
    lga_row : pd.Series
        One row from the LGA dataframe.
    voter_types : list[VoterType]
        All voter types (from generate_all_voter_types()).
    weight_threshold : float
        Types below this weight are set to 0 (sparse representation).

    Returns
    -------
    np.ndarray, shape (N_types,)
        Estimated population fraction for each type. Sums to ~1.
    """
    # ---- Extract LGA-level marginals ----
    urban_pct = float(lga_row.get("Urban Pct", 50.0)) / 100.0
    peri_urban_pct = max(0.0, min(1.0 - urban_pct, 0.30))
    rural_pct = max(0.0, 1.0 - urban_pct - peri_urban_pct)

    # Ethnic fractions
    eth_pcts = _get_ethnic_pcts(lga_row)
    total_eth = sum(eth_pcts.values())
    if total_eth < 1e-6:
        eth_frac = {eth: 1.0 / N_ETHNICITIES for eth in _CORE_ETHNICITIES}
    else:
        eth_frac = {eth: eth_pcts[eth] / total_eth for eth in _CORE_ETHNICITIES}

    # Religious fractions (split to sub-categories using LGA ordinals)
    rel_frac = split_religious_subcategories(
        pct_muslim=float(lga_row.get("% Muslim", 0)),
        pct_christian=float(lga_row.get("% Christian", 0)),
        pct_traditionalist=float(lga_row.get("% Traditionalist", 0)),
        tijaniyya_presence=int(lga_row.get("Tijaniyya Presence", 0)),
        qadiriyya_presence=int(lga_row.get("Qadiriyya Presence", 0)),
        pentecostal_growth=int(lga_row.get("Pentecostal Growth", 0)),
        al_shahid_influence=float(lga_row.get("Al-Shahid Influence", 0)),
        urban_pct=float(lga_row.get("Urban Pct", 50.0)),
        tertiary_pct=float(lga_row.get("Tertiary Institution", 0)) * 10.0,
        pada_naijin_pct=float(lga_row.get("% Pada", 0)) + float(lga_row.get("% Naijin", 0)),
    )

    # Age fractions — approximate Nigeria-like distribution
    age_frac = {"18-24": 0.25, "25-34": 0.30, "35-49": 0.28, "50+": 0.17}

    # Education fractions — derive from literacy and tertiary indicator
    literacy = float(lga_row.get("Adult Literacy Rate Pct", 50.0)) / 100.0
    tertiary = float(lga_row.get("Tertiary Institution", 0))
    tertiary_pct = min(0.25, tertiary * 0.15 + urban_pct * 0.10)
    secondary_pct = min(0.60, literacy * 0.5)
    below_sec = max(0.05, 1.0 - tertiary_pct - secondary_pct)
    edu_frac = {
        "Tertiary": tertiary_pct,
        "Secondary": secondary_pct,
        "Below secondary": below_sec,
    }
    _normalise(edu_frac)

    # Gender fractions — approximately equal
    gender_frac = {"Male": 0.50, "Female": 0.50}

    # Livelihood fractions — conditioned on setting
    agric_pct = float(lga_row.get("Pct Livelihood Agriculture", 30.0)) / 100.0
    manuf_pct = float(lga_row.get("Pct Livelihood Manufacturing", 15.0)) / 100.0
    extract_pct = float(lga_row.get("Pct Livelihood Extraction", 5.0)) / 100.0
    service_pct = float(lga_row.get("Pct Livelihood Services", 20.0)) / 100.0
    informal_pct = float(lga_row.get("Pct Livelihood Informal", 20.0)) / 100.0
    # Remaining → unemployed/student
    other_pct = max(0.0, 1.0 - agric_pct - manuf_pct - extract_pct - service_pct - informal_pct)

    # Map livelihood categories
    # Smallholder ≈ agriculture (rural weighted)
    # Commercial ag ≈ large-scale farming (small share)
    # Trade/informal ≈ informal
    # Formal private ≈ manufacturing + services (urban weighted)
    # Public sector ≈ civil service share (~urban)
    # Unemployed/student ≈ residual
    livelihood_base = {
        "Smallholder": agric_pct * 0.80,
        "Commercial ag": agric_pct * 0.20,
        "Trade/informal": informal_pct,
        "Formal private": (manuf_pct + extract_pct + service_pct * 0.6),
        "Public sector": service_pct * 0.4,
        "Unemployed/student": other_pct + 0.05,
    }
    _normalise(livelihood_base)

    # Income fractions — approximately national distribution
    # Conditioned mildly on education and livelihood
    income_frac = {"Bottom 40%": 0.40, "Middle 40%": 0.40, "Top 20%": 0.20}

    # ---- Compute type weights ----
    weights = np.zeros(len(voter_types))

    for i, vt in enumerate(voter_types):
        # Independence assumption: product of marginals
        w = (
            eth_frac.get(vt.ethnicity, 0.0)
            * rel_frac.get(vt.religion, 0.0)
            * _setting_frac(vt.setting, urban_pct, peri_urban_pct, rural_pct)
            * age_frac.get(vt.age_cohort, 0.25)
            * edu_frac.get(vt.education, 0.33)
            * gender_frac.get(vt.gender, 0.5)
            * livelihood_base.get(vt.livelihood, 1.0 / N_LIVELIHOOD)
            * income_frac.get(vt.income, 1.0 / N_INCOME)
        )

        # Conditional adjustments: religion × ethnicity compatibility
        w *= _religion_ethnicity_compat(vt)

        # Conditional: income × education (tertiary → higher income odds)
        w *= _income_education_compat(vt)

        # Conditional: livelihood × setting (smallholder → rural)
        w *= _livelihood_setting_compat(vt)

        weights[i] = w if w > weight_threshold else 0.0

    # Normalise to sum to 1
    total = weights.sum()
    if total > 0:
        weights /= total
    else:
        weights[:] = 1.0 / len(voter_types)

    return weights


def _normalise(d: dict) -> None:
    """Normalise dict values in-place so they sum to 1."""
    total = sum(d.values())
    if total > 0:
        for k in d:
            d[k] /= total


def _setting_frac(setting: str, urban: float, peri: float, rural: float) -> float:
    if setting == "Urban":
        return urban
    elif setting == "Peri-urban":
        return peri
    else:
        return rural


def _religion_ethnicity_compat(vt: VoterType) -> float:
    """
    Compatibility factor between religion and ethnicity.
    Strongly reduces weight for implausible combinations.
    """
    if vt.is_hausa_fulani:
        if vt.is_christian:
            return 0.03  # very rare
        if vt.religion == "Traditionalist":
            return 0.05
        return 1.0
    if vt.ethnicity in ("Yoruba", "Igbo", "Ijaw", "Edo", "Ibibio", "Niger Delta Minorities"):
        if vt.religion in ("Tijaniyya", "Qadiriyya", "Al-Shahid"):
            return 0.05
        return 1.0
    if vt.is_pada or vt.is_naijin:
        # Eclectic — no penalty
        return 1.0
    return 1.0


def _income_education_compat(vt: VoterType) -> float:
    """Mild income-education compatibility adjustment."""
    if vt.is_tertiary and vt.is_bottom_income:
        return 0.4
    if not vt.is_tertiary and vt.is_top_income:
        return 0.5
    return 1.0


def _livelihood_setting_compat(vt: VoterType) -> float:
    """Livelihood-setting compatibility."""
    if vt.is_smallholder and vt.is_urban:
        return 0.1
    if vt.is_commercial_ag and vt.is_urban:
        return 0.2
    if vt.is_formal_sector and vt.is_rural:
        return 0.3
    if vt.is_civil_servant and vt.is_rural:
        return 0.4
    return 1.0


# ---------------------------------------------------------------------------
# Ideal point mapping (28 issues)
# ---------------------------------------------------------------------------

# Coefficient table: list of dicts, one per issue.
# Each dict maps feature_name → coefficient.
# LGA-level features are prefixed with "lga_".
# Voter-level features use the VoterType property names.

_IDEAL_POINT_COEFFICIENTS: list[dict] = [
    # 1. Sharia Jurisdiction
    {
        "intercept": -2.0,
        "is_muslim": 5.0, "is_al_shahid": 2.0, "is_tijaniyya": 1.0,
        "is_tertiary": -1.5, "is_urban": -1.0, "is_pada": -2.0, "is_female": -0.5,
    },
    # 2. Fiscal Autonomy
    {
        "intercept": 0.0,
        "is_civil_servant": -2.0, "is_top_income": 1.5,
        "lga_Oil Producing": 3.0, "lga_Poverty Rate Pct": -1.5 / 100.0,
        "is_hausa_fulani": 0.5, "is_pada": -1.5,
    },
    # 3. Chinese Relations
    {
        "intercept": 0.0,
        "is_naijin": 4.0, "is_formal_sector": 0.5, "is_tertiary": 0.5,
        "lga_Mandarin Presence": 0.3 / 10.0, "lga_Chinese Economic Presence": 0.2 / 10.0,
        "is_unemployed": -1.5, "is_muslim": -0.5,
    },
    # 4. BIC Reform
    {
        "intercept": 0.5,
        "is_pada": 2.0, "is_civil_servant": -0.5, "is_top_income": -1.5,
        "lga_BIC Effectiveness": 0.3 / 10.0, "is_hausa_fulani": -1.5, "is_tertiary": -0.5,
    },
    # 5. Ethnic Quotas
    {
        "intercept": 0.0,
        "is_hausa_fulani": 2.5, "is_minority": 2.0, "is_pada": -3.0,
        "is_tertiary": -1.0, "is_civil_servant": 0.5, "is_youth": 0.5,
    },
    # 6. Fertility Policy
    {
        "intercept": 0.0,
        "is_muslim": 2.0, "is_rural": 1.5, "is_female": -1.5,
        "is_tertiary": -2.0, "is_pada": -1.0, "is_youth": -0.5,
        "lga_Fertility Rate Est": 0.5,
    },
    # 7. Constitutional Structure
    {
        "intercept": 0.0,
        "is_majority": 1.5, "is_minority": -2.0, "is_hausa_fulani": 1.0,
        "is_pada": -2.0, "is_tertiary": -0.5,
        "lga_Trad Authority Index": -0.3 / 5.0,
    },
    # 8. Resource Revenue
    {
        "intercept": -0.5,
        "lga_Oil Producing": 3.0, "lga_Extraction Intensity": 0.5 / 5.0,
        "is_ijaw": 3.0, "is_civil_servant": -2.0,
        "lga_Cobalt Extraction Active": 2.0,
    },
    # 9. Housing
    {
        "intercept": 1.0,
        "is_urban": 1.0, "is_bottom_income": 2.5, "is_top_income": -2.5,
        "lga_Housing Affordability": -0.3 / 10.0, "is_youth": 1.5, "is_pada": -1.5,
    },
    # 10. Education
    {
        "intercept": 0.0,
        "is_tertiary": 2.0, "is_muslim": -1.0, "is_rural": -1.5,
        "is_female": 0.5, "is_naijin": 1.5,
        "lga_Out of School Children Pct": -0.2 / 100.0,
    },
    # 11. Labor & Automation
    {
        "intercept": 0.5,
        "is_informal": 2.0, "is_formal_sector": 1.0, "is_unemployed": 0.5,
        "is_top_income": -3.0, "is_smallholder": -0.5,
        "lga_Pct Livelihood Manufacturing": 0.2 / 100.0,
    },
    # 12. Military Role
    {
        "intercept": 0.0,
        "is_civil_servant": 2.0, "is_pada": 0.5, "is_hausa_fulani": 1.0,
        "lga_Conflict History": 0.5 / 5.0, "is_youth": -0.5, "is_tertiary": -1.5,
    },
    # 13. Immigration
    {
        "intercept": -0.5,
        "is_pada": -0.5, "is_naijin": 1.5, "is_bottom_income": -2.0,
        "is_top_income": 1.5, "lga_Fertility Rate Est": -0.3, "is_hausa_fulani": -1.0,
    },
    # 14. Language Policy
    {
        "intercept": 0.0,
        "is_pada": 2.5, "is_naijin": -2.0, "is_muslim": -1.5, "is_tertiary": 1.0,
        "lga_English Prestige": 0.3 / 10.0, "lga_Arabic Prestige": -0.3 / 10.0,
    },
    # 15. Women's Rights
    {
        "intercept": -0.5,
        "is_female": 2.0, "is_muslim": -2.0, "is_tertiary": 1.0, "is_urban": 1.0,
        "lga_Gender Parity Index": 1.0, "is_pada": 1.5,
    },
    # 16. Traditional Authority
    {
        "intercept": 0.0,
        "is_rural": 1.5, "lga_Trad Authority Index": 0.5 / 5.0,
        "is_tertiary": -2.0, "is_pada": -2.5, "is_older": 1.0, "is_naijin": -1.5,
    },
    # 17. Infrastructure
    {
        "intercept": 1.0,
        "is_rural": 1.5, "is_bottom_income": 1.0,
        "lga_Access Electricity Pct": -0.02, "lga_Access Water Pct": -0.01,
        "is_top_income": -1.0,
    },
    # 18. Land Tenure
    {
        "intercept": 0.0,
        "is_smallholder": -1.5, "is_rural": -1.0,
        "lga_Trad Authority Index": -0.3 / 5.0, "is_top_income": 2.5,
        "lga_Land Formalization Pct": 0.03 / 100.0, "is_pada": 2.0,
    },
    # 19. Taxation
    {
        "intercept": 0.5,
        "is_top_income": -3.5, "is_bottom_income": 2.5, "is_unemployed": 2.0,
        "lga_Gini Proxy": 2.0, "is_pada": -1.0, "lga_Poverty Rate Pct": 0.02 / 100.0,
    },
    # 20. Agricultural Policy
    {
        "intercept": 0.5,
        "is_smallholder": 3.0, "is_commercial_ag": -3.0, "is_rural": 1.0,
        "is_top_income": -1.5, "lga_Pct Livelihood Agriculture": 0.02 / 100.0,
    },
    # 21. Biological Enhancement
    {
        "intercept": 0.0,
        "is_top_income": 2.0, "is_muslim": -2.0, "is_youth": 1.5,
        "lga_Biological Enhancement Pct": 0.1 / 100.0, "is_tertiary": 0.5, "is_rural": -1.0,
    },
    # 22. Trade Policy
    {
        "intercept": 0.0,
        "is_formal_sector": 1.5, "lga_Pct Livelihood Manufacturing": 0.3 / 100.0,
        "is_smallholder": -1.5, "is_top_income": 2.0, "is_unemployed": -2.0,
        "lga_Rail Corridor": 0.5,
    },
    # 23. Environmental Regulation
    {
        "intercept": 0.0,
        "is_formal_sector": -2.0,  # extraction worker proxy
        "is_tertiary": 1.5, "lga_Oil Producing": 1.0,
        "is_top_income": -1.5, "is_ijaw": 2.0, "is_bottom_income": -1.0,
    },
    # 24. Media Freedom
    {
        "intercept": 0.5,
        "is_tertiary": 1.5, "lga_Internet Access Pct": 0.05 / 100.0,
        "is_pada": -0.5, "is_youth": 1.0, "is_civil_servant": -2.0,
        "is_al_shahid": -1.0,
    },
    # 25. Healthcare
    {
        "intercept": 1.0,
        "is_bottom_income": 2.5, "is_top_income": -2.0,
        "lga_Access Healthcare Pct": -0.05 / 100.0, "is_rural": 1.0, "is_older": 0.5,
    },
    # 26. Padà Status
    {
        "intercept": -1.0,
        "is_pada": 5.0, "is_hausa_fulani": -2.5, "is_bottom_income": -1.5,
        "is_civil_servant": 0.5, "is_naijin": 1.0,
    },
    # 27. Energy Policy
    {
        "intercept": 0.5,
        "is_formal_sector": -2.0,  # extraction worker proxy
        "is_rural": 2.0, "lga_Access Electricity Pct": -0.05 / 100.0,
        "is_tertiary": 1.0, "is_top_income": -1.0,
    },
    # 28. AZ Restructuring
    {
        "intercept": 0.0,
        "is_yoruba": -2.0, "is_hausa_fulani": -1.0, "is_minority": -2.5,
        "is_pada": 3.0, "lga_Trad Authority Index": -0.3 / 5.0,
    },
]

assert len(_IDEAL_POINT_COEFFICIENTS) == N_ISSUES


def demographics_to_ideal_point(
    voter_type: VoterType,
    lga_row: pd.Series,
    coeff_table: Optional[list[dict]] = None,
) -> np.ndarray:
    """
    Map a voter type + LGA context to an ideal point in 28-dimensional issue space.

    Parameters
    ----------
    voter_type : VoterType
        The voter's demographic type.
    lga_row : pd.Series
        The LGA's data row (provides LGA-level features).
    coeff_table : list[dict], optional
        Override the default coefficient table. If None, uses _IDEAL_POINT_COEFFICIENTS.

    Returns
    -------
    np.ndarray, shape (28,)
        Ideal point on each issue dimension, clamped to [-5, +5].
    """
    if coeff_table is None:
        coeff_table = _IDEAL_POINT_COEFFICIENTS

    ideal = np.zeros(N_ISSUES)

    for d, coeffs in enumerate(coeff_table):
        x = coeffs.get("intercept", 0.0)
        for feat, coeff in coeffs.items():
            if feat == "intercept":
                continue
            elif feat.startswith("lga_"):
                col = feat[4:]
                val = float(lga_row.get(col, 0.0))
                x += coeff * val
            else:
                # Voter-level boolean property
                prop = getattr(voter_type, feat, None)
                if prop is not None:
                    x += coeff * float(bool(prop))
        ideal[d] = np.clip(x, -5.0, 5.0)

    return ideal
