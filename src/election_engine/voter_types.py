"""
Voter type generation and ideal point mapping for the LAGOS-2058 engine.

The 8-dimensional voter typology produces 174,960 voter types:
    15 ethnicities × 9 religious sub-categories × 3 settings × 4 age cohorts
    × 3 education levels × 2 genders × 6 livelihoods × 3 income brackets
    = 174,960 types

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
from .religious_affinity import (
    RELIGIOUS_GROUPS, split_religious_subcategories,
    batch_split_religious_subcategories,
)

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
# = 15 × 9 × 3 × 4 × 3 × 2 × 6 × 3 = 174,960

# Fixed marginal arrays — used in compute_type_weights
_AGE_VALS = np.array([0.25, 0.30, 0.28, 0.17])   # matches AGE_COHORTS order
_GEN_VALS = np.array([0.50, 0.50])                 # matches GENDERS order


def _poverty_to_income_fracs(poverty_pct: float) -> np.ndarray:
    """
    Convert LGA poverty rate (0-100) to income bracket fractions.

    At the national average (~30% poverty): [40%, 40%, 20%] (baseline).
    Higher poverty shifts weight from top to bottom bracket.
    Lower poverty shifts weight from bottom to top bracket.

    Returns (3,) array: [Bottom 40%, Middle 40%, Top 20%].
    """
    # Linear shift: each 10pp above 30% shifts 5pp from top → bottom
    poverty_frac = np.clip(poverty_pct, 0.0, 80.0) / 100.0
    deviation = poverty_frac - 0.30  # positive = poorer than average
    bottom = np.clip(0.40 + deviation * 0.50, 0.20, 0.65)
    top = np.clip(0.20 - deviation * 0.30, 0.05, 0.35)
    middle = np.clip(1.0 - bottom - top, 0.15, 0.55)
    total = bottom + middle + top
    return np.array([bottom / total, middle / total, top / total])


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

    # --- Additional ethnic groups ---
    @property
    def is_kanuri(self) -> bool:
        return self.ethnicity == "Kanuri"

    @property
    def is_tiv(self) -> bool:
        return self.ethnicity == "Tiv"

    @property
    def is_nupe(self) -> bool:
        return self.ethnicity == "Nupe"

    @property
    def is_edo(self) -> bool:
        return self.ethnicity == "Edo"

    @property
    def is_ibibio(self) -> bool:
        return self.ethnicity == "Ibibio"

    @property
    def is_nd_minority(self) -> bool:
        return self.ethnicity == "Niger Delta Minorities"

    @property
    def is_mb_minority(self) -> bool:
        return self.ethnicity == "Middle Belt Minorities"

    # --- Additional religion/demographic ---
    @property
    def is_pentecostal(self) -> bool:
        return self.religion == "Pentecostal"

    @property
    def is_middle_income(self) -> bool:
        return self.income == "Middle 40%"

    @property
    def is_middle_age(self) -> bool:
        return self.age_cohort == "35-49"

    # --- Interaction terms ---
    @property
    def is_muslim_female(self) -> bool:
        return self.is_muslim and self.is_female

    @property
    def is_urban_youth(self) -> bool:
        return self.is_urban and self.is_youth

    @property
    def is_rural_muslim(self) -> bool:
        return self.is_rural and self.is_muslim

    @property
    def is_tertiary_youth(self) -> bool:
        return self.is_tertiary and self.is_youth

    @property
    def is_hf_bottom_income(self) -> bool:
        return self.is_hausa_fulani and self.is_bottom_income

    @property
    def is_christian_urban(self) -> bool:
        return self.is_christian and self.is_urban

    @property
    def is_muslim_tertiary(self) -> bool:
        return self.is_muslim and self.is_tertiary

    @property
    def is_female_tertiary(self) -> bool:
        return self.is_female and self.is_tertiary

    @property
    def is_youth_unemployed(self) -> bool:
        return self.is_youth and self.is_unemployed

    @property
    def is_rural_older(self) -> bool:
        return self.is_rural and self.is_older

    # --- New cross-pressure interaction terms ---
    @property
    def is_yoruba_muslim(self) -> bool:
        return self.is_yoruba and self.is_muslim

    @property
    def is_igbo_pentecostal(self) -> bool:
        return self.is_igbo and self.is_pentecostal

    @property
    def is_pada_tertiary(self) -> bool:
        return self.is_pada and self.is_tertiary

    @property
    def is_rural_bottom_income(self) -> bool:
        return self.is_rural and self.is_bottom_income

    @property
    def is_kanuri_rural(self) -> bool:
        return self.is_kanuri and self.is_rural

    # --- Ethnicity-livelihood interactions ---
    @property
    def is_hf_smallholder(self) -> bool:
        return self.is_hausa_fulani and self.livelihood == "Smallholder"

    @property
    def is_yoruba_trader(self) -> bool:
        return self.is_yoruba and self.livelihood == "Trade/informal"

    @property
    def is_igbo_formal(self) -> bool:
        return self.is_igbo and self.livelihood == "Formal private"

    @property
    def is_kanuri_unemployed(self) -> bool:
        return self.is_kanuri and self.livelihood == "Unemployed/student"

    @property
    def is_ijaw_extraction(self) -> bool:
        return self.is_ijaw and self.livelihood in ("Formal private", "Trade/informal")

    # --- Additional cross-pressure terms ---
    @property
    def is_igbo_bottom_income(self) -> bool:
        return self.is_igbo and self.is_bottom_income

    @property
    def is_fulani_smallholder(self) -> bool:
        return self.ethnicity == "Fulani" and self.livelihood == "Smallholder"

    @property
    def is_urban_bottom_income(self) -> bool:
        return self.is_urban and self.is_bottom_income

    @property
    def is_christian_rural(self) -> bool:
        return self.is_christian and self.is_rural

    @property
    def is_yoruba_formal(self) -> bool:
        return self.is_yoruba and self.is_formal_sector

    # --- Religion-livelihood interaction terms ---
    @property
    def is_muslim_trader(self) -> bool:
        return self.is_muslim and self.livelihood == "Trade/informal"

    @property
    def is_pentecostal_formal(self) -> bool:
        return self.is_pentecostal and self.is_formal_sector

    @property
    def is_catholic_smallholder(self) -> bool:
        return self.religion == "Catholic" and self.is_smallholder

    @property
    def is_muslim_civil_servant(self) -> bool:
        return self.is_muslim and self.is_civil_servant

    @property
    def is_tijaniyya_trader(self) -> bool:
        return self.is_tijaniyya and self.livelihood == "Trade/informal"

    # --- Additional religion properties ---
    @property
    def is_catholic(self) -> bool:
        return self.religion == "Catholic"

    @property
    def is_mainline_protestant(self) -> bool:
        return self.religion == "Mainline Protestant"

    # --- Triple interaction terms ---
    @property
    def is_hf_muslim_civil_servant(self) -> bool:
        """Hausa-Fulani Muslim in public sector: core northern establishment (NDC)."""
        return self.is_hausa_fulani and self.is_muslim and self.is_civil_servant

    @property
    def is_yoruba_christian_urban(self) -> bool:
        """Yoruba Christians in cities: cosmopolitan swing voters (CND/NRP base)."""
        return self.is_yoruba and self.is_christian and self.is_urban

    @property
    def is_igbo_pentecostal_formal(self) -> bool:
        """Igbo Pentecostals in formal sector: prosperity gospel entrepreneurs."""
        return self.is_igbo and self.is_pentecostal and self.is_formal_sector

    @property
    def is_kanuri_muslim_youth(self) -> bool:
        """Kanuri Muslim youth: Al-Shahid recruitment pool, radicalization risk."""
        return self.is_kanuri and self.is_muslim and self.is_youth

    @property
    def is_ijaw_christian_unemployed(self) -> bool:
        """Ijaw Christian unemployed: Niger Delta radical base (PLF)."""
        return self.is_ijaw and self.is_christian and self.is_unemployed

    @property
    def is_hf_rural_older(self) -> bool:
        """Hausa-Fulani rural elderly: deeply traditional, NDC base."""
        return self.is_hausa_fulani and self.is_rural and self.is_older

    @property
    def is_yoruba_muslim_trader(self) -> bool:
        """Yoruba Muslim traders: unique cross-cutting identity, SNM target."""
        return self.is_yoruba and self.is_muslim and self.livelihood == "Trade/informal"

    @property
    def is_minority_urban_youth(self) -> bool:
        """Minority urban youth: pan-ethnic progressive coalition base."""
        return self.is_minority and self.is_urban and self.is_youth

    # --- Gender-ethnic and income-education interactions ---
    @property
    def is_igbo_female(self) -> bool:
        """Igbo women: strong market women tradition, economic independence."""
        return self.is_igbo and self.is_female

    @property
    def is_yoruba_female(self) -> bool:
        """Yoruba women: Iyaloja market women tradition, political influence."""
        return self.is_yoruba and self.is_female

    @property
    def is_tertiary_bottom_income(self) -> bool:
        """Educated poor: cross-pressured between aspiration and deprivation."""
        return self.is_tertiary and self.is_bottom_income

    @property
    def is_young_adult(self) -> bool:
        """25-34 age cohort: peak working age, family formation."""
        return self.age_cohort == "25-34"

    @property
    def is_urban_trader(self) -> bool:
        """Urban informal traders: market stall economy, price-sensitive."""
        return self.is_urban and self.livelihood == "Trade/informal"

    # --- Batch 20: ethnic-religious and livelihood cross-terms ---
    @property
    def is_edo_christian(self) -> bool:
        """Edo Christians: cosmopolitan Benin City tradition."""
        return self.is_edo and self.is_christian

    @property
    def is_mb_minority_christian(self) -> bool:
        """Middle Belt Christian minorities: politically marginalised constituency."""
        return self.ethnicity == "Middle Belt Minorities" and self.is_christian

    @property
    def is_nupe_muslim(self) -> bool:
        """Nupe Muslims: bridge north-south Muslim divide."""
        return self.is_nupe and self.is_muslim

    @property
    def is_igbo_trader(self) -> bool:
        """Igbo traders: mobile entrepreneurial diaspora across Nigeria."""
        return self.is_igbo and self.livelihood == "Trade/informal"

    @property
    def is_fulani_rural(self) -> bool:
        """Rural Fulani: pastoralist herders, nomadic tradition."""
        return self.ethnicity == "Fulani" and self.is_rural


@lru_cache(maxsize=1)
def generate_all_voter_types() -> list[VoterType]:
    """
    Generate all 174,960 voter types.

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
    # Ijaw excluded — has its own category in _CORE_ETHNICITIES
    "% Ogoni", "% Ikwerre", "% Etche", "% Pere", "% Isoko",
    "% Itsekiri", "% Urhobo",
]

_MIDDLE_BELT_COLS = [
    # Tiv and Nupe excluded — have their own categories in _CORE_ETHNICITIES
    "% Ebira", "% Gwari Gbagyi", "% Idoma",
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


@lru_cache(maxsize=1)
def _build_type_indices() -> dict[str, np.ndarray]:
    """
    Precompute integer category indices for every voter type (runs once, then cached).

    Returns a dict of int32 arrays of length N_types, one per attribute dimension.
    idx["eth"][i] is the _CORE_ETHNICITIES index of voter_types[i].ethnicity, etc.
    These are used in compute_type_weights to replace the per-type Python loop with
    vectorised numpy indexing.
    """
    voter_types = generate_all_voter_types()
    eth_map = {e: j for j, e in enumerate(_CORE_ETHNICITIES)}
    rel_map = {r: j for j, r in enumerate(RELIGIONS)}
    set_map = {s: j for j, s in enumerate(SETTINGS)}
    age_map = {a: j for j, a in enumerate(AGE_COHORTS)}
    edu_map = {e: j for j, e in enumerate(EDUCATIONS)}
    gen_map = {g: j for j, g in enumerate(GENDERS)}
    liv_map = {l: j for j, l in enumerate(LIVELIHOODS)}
    inc_map = {c: j for j, c in enumerate(INCOMES)}
    return {
        "eth": np.array([eth_map[vt.ethnicity]  for vt in voter_types], dtype=np.int32),
        "rel": np.array([rel_map[vt.religion]   for vt in voter_types], dtype=np.int32),
        "set": np.array([set_map[vt.setting]    for vt in voter_types], dtype=np.int32),
        "age": np.array([age_map[vt.age_cohort] for vt in voter_types], dtype=np.int32),
        "edu": np.array([edu_map[vt.education]  for vt in voter_types], dtype=np.int32),
        "gen": np.array([gen_map[vt.gender]     for vt in voter_types], dtype=np.int32),
        "liv": np.array([liv_map[vt.livelihood] for vt in voter_types], dtype=np.int32),
        "inc": np.array([inc_map[vt.income]     for vt in voter_types], dtype=np.int32),
    }


def compute_type_weights(
    lga_row: pd.Series,
    voter_types: list[VoterType],
    weight_threshold: float = 1e-8,
    precomputed_compat: np.ndarray | None = None,
    precomputed_type_indices: dict | None = None,
    precomputed_marginals_row: tuple | None = None,
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
    precomputed_compat : np.ndarray, optional
        (N_types,) compat-factor array from precompute_compat_factors().
        If provided, skips calling the three compat functions per type.

    Returns
    -------
    np.ndarray, shape (N_types,)
        Estimated population fraction for each type. Sums to ~1.
    """
    # ---- Extract LGA-level marginals ----
    if precomputed_marginals_row is not None:
        # Fast path: pre-extracted numpy arrays from precompute_all_lga_marginals
        if len(precomputed_marginals_row) >= 6:
            eth_vals, rel_vals, set_vals, edu_vals, liv_vals, _inc_row = precomputed_marginals_row
        else:
            eth_vals, rel_vals, set_vals, edu_vals, liv_vals = precomputed_marginals_row
    else:
        # Slow path: extract from pd.Series (used when called outside batch context)
        urban_pct = float(lga_row.get("Urban Pct", 50.0)) / 100.0
        peri_urban_pct = max(0.0, min(1.0 - urban_pct, 0.30))
        rural_pct = max(0.0, 1.0 - urban_pct - peri_urban_pct)

        eth_pcts = _get_ethnic_pcts(lga_row)
        total_eth = sum(eth_pcts.values())
        if total_eth < 1e-6:
            eth_frac = {eth: 1.0 / N_ETHNICITIES for eth in _CORE_ETHNICITIES}
        else:
            eth_frac = {eth: eth_pcts[eth] / total_eth for eth in _CORE_ETHNICITIES}

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

        literacy = float(lga_row.get("Adult Literacy Rate Pct", 50.0)) / 100.0
        tertiary = float(lga_row.get("Tertiary Institution", 0))
        tertiary_pct = min(0.25, tertiary * 0.15 + urban_pct * 0.10)
        secondary_pct = min(0.60, literacy * 0.5)
        below_sec = max(0.05, 1.0 - tertiary_pct - secondary_pct)
        edu_frac = {"Tertiary": tertiary_pct, "Secondary": secondary_pct,
                    "Below secondary": below_sec}
        _normalise(edu_frac)

        agric_pct = float(lga_row.get("Pct Livelihood Agriculture", 30.0)) / 100.0
        manuf_pct = float(lga_row.get("Pct Livelihood Manufacturing", 15.0)) / 100.0
        extract_pct = float(lga_row.get("Pct Livelihood Extraction", 5.0)) / 100.0
        service_pct = float(lga_row.get("Pct Livelihood Services", 20.0)) / 100.0
        informal_pct = float(lga_row.get("Pct Livelihood Informal", 20.0)) / 100.0
        other_pct = max(0.0, 1.0 - agric_pct - manuf_pct - extract_pct - service_pct - informal_pct)
        livelihood_base = {
            "Smallholder": agric_pct * 0.80, "Commercial ag": agric_pct * 0.20,
            "Trade/informal": informal_pct,
            "Formal private": (manuf_pct + extract_pct + service_pct * 0.6),
            "Public sector": service_pct * 0.4,
            "Unemployed/student": other_pct + 0.05,
        }
        _normalise(livelihood_base)

        eth_vals = np.array([eth_frac.get(e, 0.0) for e in _CORE_ETHNICITIES])
        rel_vals = np.array([rel_frac.get(r, 0.0) for r in RELIGIONS])
        set_vals = np.array([urban_pct, peri_urban_pct, rural_pct])
        edu_vals = np.array([edu_frac[e] for e in EDUCATIONS])
        liv_vals = np.array([livelihood_base.get(l, 1.0 / N_LIVELIHOOD) for l in LIVELIHOODS])

    # Fixed marginals
    age_vals = _AGE_VALS
    gen_vals = _GEN_VALS

    # Income distribution: LGA-dependent via poverty rate when precomputed,
    # otherwise use national baseline [40%, 40%, 20%].
    if precomputed_marginals_row is not None and len(precomputed_marginals_row) >= 6:
        inc_vals = precomputed_marginals_row[5]
    else:
        # Derive from poverty rate if available
        poverty_pct = float(lga_row.get("Poverty Rate Pct", 30.0))
        inc_vals = _poverty_to_income_fracs(poverty_pct)

    # ---- Compute type weights via pair-wise outer products (float32) ----
    # The 174,960 types are a Cartesian product of 8 dimensions:
    #   (15 eth × 9 rel × 3 set × 4 age × 3 edu × 2 gen × 6 liv × 3 inc)
    # Pair-wise outer products are ~4x faster than 8-way broadcast because
    # they avoid 7 intermediate (N_total,)-sized temporaries. Float32 halves
    # memory bandwidth, giving another ~2x.
    e32 = np.asarray(eth_vals, dtype=np.float32)
    r32 = np.asarray(rel_vals, dtype=np.float32)
    s32 = np.asarray(set_vals, dtype=np.float32)
    a32 = np.asarray(age_vals, dtype=np.float32)
    u32 = np.asarray(edu_vals, dtype=np.float32)
    g32 = np.asarray(gen_vals, dtype=np.float32)
    l32 = np.asarray(liv_vals, dtype=np.float32)
    i32 = np.asarray(inc_vals, dtype=np.float32)

    # Pair, then quad, then full — only one 174,960-element allocation
    p1 = np.outer(e32, r32).ravel()      # (135,)
    p2 = np.outer(s32, a32).ravel()      # (12,)
    p3 = np.outer(u32, g32).ravel()      # (6,)
    p4 = np.outer(l32, i32).ravel()      # (18,)
    q1 = np.outer(p1, p2).ravel()        # (1620,)
    q2 = np.outer(p3, p4).ravel()        # (108,)
    weights = np.outer(q1, q2).ravel()   # (174960,) float32

    # Conditional adjustments: religion × ethnicity, income × education,
    # livelihood × setting compatibility
    if precomputed_compat is not None:
        weights *= precomputed_compat
    else:
        weights *= np.array([
            _religion_ethnicity_compat(vt)
            * _income_education_compat(vt)
            * _livelihood_setting_compat(vt)
            for vt in voter_types
        ], dtype=np.float32)

    # Apply threshold and normalise to sum to 1 (stay float32 — downstream
    # aggregation uses float32 BLAS, final vote shares promote to float64).
    weights[weights <= np.float32(weight_threshold)] = np.float32(0.0)
    total = float(weights.sum())
    if total > 0:
        weights *= np.float32(1.0 / total)
    else:
        weights[:] = np.float32(1.0 / len(voter_types))

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

    Key assumptions (2058 Nigeria):
    - Hausa-Fulani: overwhelmingly Muslim; Christians/Traditionalists ~3-5%
    - Yoruba: ~35% Muslim, Tijaniyya is the dominant order; small Qadiriyya presence
    - Edo: ~15% Muslim minority; small Tijaniyya presence
    - Igbo/Ijaw/Ibibio/Niger Delta: <5% Muslim
    - Al-Shahid: northern movement, negligible among all southern groups
    """
    if vt.is_hausa_fulani:
        if vt.is_christian:
            return 0.03  # very rare
        if vt.religion == "Traditionalist":
            return 0.05
        return 1.0
    if vt.is_yoruba:
        # Yoruba have a large Muslim population (~35%), primarily Tijaniyya
        if vt.religion == "Tijaniyya":
            return 0.50  # Tijaniyya is dominant Yoruba Muslim order
        if vt.religion == "Mainstream Sunni":
            return 0.40  # non-order-affiliated Yoruba Muslims
        if vt.religion == "Qadiriyya":
            return 0.10  # exists but rare among Yoruba
        if vt.religion == "Al-Shahid":
            return 0.03  # northern movement, near-zero Yoruba presence
        return 1.0
    if vt.ethnicity == "Edo":
        # Edo have a small but real Muslim minority (~15%)
        if vt.religion == "Tijaniyya":
            return 0.15
        if vt.religion == "Mainstream Sunni":
            return 0.15
        if vt.religion in ("Qadiriyya", "Al-Shahid"):
            return 0.03
        return 1.0
    if vt.ethnicity in ("Igbo", "Ijaw", "Ibibio", "Niger Delta Minorities"):
        # Overwhelmingly Christian; Muslim subcategories near-zero
        if vt.religion in ("Tijaniyya", "Qadiriyya", "Al-Shahid", "Mainstream Sunni"):
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


def precompute_compat_factors(
    voter_types: list[VoterType],
    type_indices: dict | None = None,
) -> np.ndarray:
    """
    Precompute the combined compatibility factor for every voter type.

    Returns (N_types,) float array.  The three compat functions depend only on
    voter-type attributes, not on LGA data, so the result is the same across
    all LGAs and only needs to be computed once per simulation run.

    Vectorised implementation uses integer codes from _build_type_indices()
    to avoid 174k × 3 Python function calls.
    """
    if type_indices is None:
        type_indices = _build_type_indices()

    N = len(voter_types)
    eth = type_indices["eth"]   # 0..14
    rel = type_indices["rel"]   # 0..8
    edu = type_indices["edu"]   # 0..2
    inc = type_indices["inc"]   # 0..2
    liv = type_indices["liv"]   # 0..5
    sett = type_indices["set"]  # 0..2

    # ------ religion_ethnicity_compat (vectorised) ------
    re_compat = np.ones(N, dtype=np.float64)

    # Hausa-Fulani group: eth in {0, 1, 2}
    is_hf = (eth == 0) | (eth == 1) | (eth == 2)
    # Christian: rel in {4, 5, 6}  (Pentecostal, Catholic, Mainline Protestant)
    is_christian = (rel == 4) | (rel == 5) | (rel == 6)
    is_trad = rel == 7  # Traditionalist
    re_compat[is_hf & is_christian] = 0.03
    re_compat[is_hf & is_trad] = 0.05

    # Yoruba: eth == 3
    is_yoruba = eth == 3
    re_compat[is_yoruba & (rel == 0)] = 0.50  # Tijaniyya
    re_compat[is_yoruba & (rel == 3)] = 0.40  # Mainstream Sunni
    re_compat[is_yoruba & (rel == 1)] = 0.10  # Qadiriyya
    re_compat[is_yoruba & (rel == 2)] = 0.03  # Al-Shahid

    # Edo: eth == 9
    is_edo = eth == 9
    re_compat[is_edo & (rel == 0)] = 0.15  # Tijaniyya
    re_compat[is_edo & (rel == 3)] = 0.15  # Mainstream Sunni
    re_compat[is_edo & ((rel == 1) | (rel == 2))] = 0.03  # Qadiriyya/Al-Shahid

    # Igbo/Ijaw/Ibibio/Niger Delta Minorities: eth in {4, 5, 10, 11}
    is_south_chr = (eth == 4) | (eth == 5) | (eth == 10) | (eth == 11)
    # Muslim subcategories: rel in {0, 1, 2, 3}
    is_muslim_sub = (rel == 0) | (rel == 1) | (rel == 2) | (rel == 3)
    re_compat[is_south_chr & is_muslim_sub] = 0.05

    # Pada/Naijin: no penalty (already 1.0)

    # ------ income_education_compat (vectorised) ------
    ie_compat = np.ones(N, dtype=np.float64)
    ie_compat[(edu == 2) & (inc == 0)] = 0.4   # Tertiary + Bottom 40%
    ie_compat[(edu != 2) & (inc == 2)] = 0.5   # Non-tertiary + Top 20%

    # ------ livelihood_setting_compat (vectorised) ------
    ls_compat = np.ones(N, dtype=np.float64)
    ls_compat[(liv == 0) & (sett == 0)] = 0.1  # Smallholder + Urban
    ls_compat[(liv == 1) & (sett == 0)] = 0.2  # Commercial ag + Urban
    ls_compat[(liv == 3) & (sett == 2)] = 0.3  # Formal private + Rural
    ls_compat[(liv == 4) & (sett == 2)] = 0.4  # Public sector + Rural

    return re_compat * ie_compat * ls_compat


def precompute_all_lga_marginals(
    lga_data: pd.DataFrame,
) -> dict[str, np.ndarray]:
    """
    Batch-extract all demographic marginals for every LGA from the DataFrame.

    This replaces ~30 per-LGA pd.Series.get() calls with a single vectorised
    pass over DataFrame columns.  Returns a dict of arrays:

        "eth": (N_lga, 15) — ethnic fractions (normalised)
        "rel": (N_lga, 9)  — religious sub-category fractions
        "set": (N_lga, 3)  — [urban, peri-urban, rural] fractions
        "edu": (N_lga, 3)  — [below-sec, secondary, tertiary] fractions
        "liv": (N_lga, 6)  — livelihood fractions
    """
    N = len(lga_data)

    # ----- Ethnic fractions (N, 15) -----
    eth_raw = np.zeros((N, N_ETHNICITIES))
    for j, eth in enumerate(_CORE_ETHNICITIES):
        col = _ETHNIC_COL_MAP.get(eth)
        if col is not None and col in lga_data.columns:
            eth_raw[:, j] = lga_data[col].fillna(0.0).values.astype(float)
        elif eth == "Niger Delta Minorities":
            for c in _NIGER_DELTA_COLS:
                if c in lga_data.columns:
                    eth_raw[:, j] += lga_data[c].fillna(0.0).values.astype(float)
        elif eth == "Middle Belt Minorities":
            for c in _MIDDLE_BELT_COLS:
                if c in lga_data.columns:
                    eth_raw[:, j] += lga_data[c].fillna(0.0).values.astype(float)
    eth_raw = np.maximum(eth_raw, 0.0)
    eth_totals = eth_raw.sum(axis=1, keepdims=True)
    # Where total is near-zero, use uniform
    uniform_eth = np.full((1, N_ETHNICITIES), 1.0 / N_ETHNICITIES)
    eth_frac = np.where(
        eth_totals > 1e-6,
        eth_raw / np.maximum(eth_totals, 1e-30),
        uniform_eth,
    )

    # ----- Setting fractions (N, 3) -----
    urban_pct_raw = lga_data.get("Urban Pct", pd.Series(np.full(N, 50.0)))
    urban_pct = np.clip(urban_pct_raw.fillna(50.0).values.astype(float) / 100.0, 0.0, 1.0)
    peri_urban = np.minimum(np.maximum(1.0 - urban_pct, 0.0), 0.30)
    rural = np.maximum(1.0 - urban_pct - peri_urban, 0.0)
    set_frac = np.column_stack([urban_pct, peri_urban, rural])

    # ----- Religious fractions (N, 9) -----
    def _col(name, default=0.0):
        if name in lga_data.columns:
            return lga_data[name].fillna(default).values.astype(float)
        return np.full(N, default)

    pada_pct = _col("% Pada", 0.0) + _col("% Naijin", 0.0)
    tertiary_col = _col("Tertiary Institution", 0.0) * 10.0

    rel_frac = batch_split_religious_subcategories(
        pct_muslim=_col("% Muslim", 0.0),
        pct_christian=_col("% Christian", 0.0),
        pct_traditionalist=_col("% Traditionalist", 0.0),
        tijaniyya_presence=_col("Tijaniyya Presence", 0.0),
        qadiriyya_presence=_col("Qadiriyya Presence", 0.0),
        pentecostal_growth=_col("Pentecostal Growth", 0.0),
        al_shahid_influence=_col("Al-Shahid Influence", 0.0),
        urban_pct=urban_pct_raw.fillna(50.0).values.astype(float),
        tertiary_pct=tertiary_col,
        pada_naijin_pct=pada_pct,
    )

    # ----- Education fractions (N, 3) -----
    literacy = np.clip(_col("Adult Literacy Rate Pct", 50.0) / 100.0, 0.0, 1.0)
    sec_enr = np.clip(_col("Secondary Enrollment Pct", 50.0) / 100.0, 0.0, 1.0)
    tertiary_ord = _col("Tertiary Institution", 0.0)
    tertiary_frac = np.minimum(0.25, tertiary_ord * 0.15 + urban_pct * 0.10)
    # Blend literacy-based estimate with actual secondary enrollment data
    secondary_frac = np.minimum(0.60, 0.3 * literacy + 0.35 * sec_enr)
    below_sec_frac = np.maximum(0.05, 1.0 - tertiary_frac - secondary_frac)
    edu_raw = np.column_stack([below_sec_frac, secondary_frac, tertiary_frac])
    edu_totals = edu_raw.sum(axis=1, keepdims=True)
    edu_frac = edu_raw / np.maximum(edu_totals, 1e-30)

    # ----- Livelihood fractions (N, 6) -----
    agric = _col("Pct Livelihood Agriculture", 30.0) / 100.0
    manuf = _col("Pct Livelihood Manufacturing", 15.0) / 100.0
    extract = _col("Pct Livelihood Extraction", 5.0) / 100.0
    service = _col("Pct Livelihood Services", 20.0) / 100.0
    informal = _col("Pct Livelihood Informal", 20.0) / 100.0
    other = np.maximum(0.0, 1.0 - agric - manuf - extract - service - informal)

    # Youth unemployment boosts unemployed/student fraction
    youth_unemp = np.clip(_col("Youth Unemployment Rate Pct", 46.0) / 100.0, 0.0, 0.8)
    unemp_boost = np.maximum(0.0, (youth_unemp - 0.46) * 0.15)  # above-avg → more unemployed weight

    liv_raw = np.column_stack([
        agric * 0.80,                           # Smallholder
        agric * 0.20,                           # Commercial ag
        informal,                               # Trade/informal
        manuf + extract + service * 0.6,        # Formal private
        service * 0.4,                          # Public sector
        other + 0.05 + unemp_boost,            # Unemployed/student
    ])
    liv_totals = liv_raw.sum(axis=1, keepdims=True)
    liv_frac = liv_raw / np.maximum(liv_totals, 1e-30)

    # ----- Income fractions (N, 3) — LGA-dependent via poverty rate + Gini -----
    poverty = np.clip(_col("Poverty Rate Pct", 30.0), 0.0, 80.0) / 100.0
    gini = np.clip(_col("Gini Proxy", 0.36), 0.20, 0.65)
    # Poverty shifts weight from top to bottom; Gini stretches the extremes
    deviation = poverty - 0.30
    gini_effect = (gini - 0.36) / 0.30  # normalised: 0 at avg, +1 at high inequality
    # High Gini → more bottom AND more top (hollowed-out middle class)
    bottom = np.clip(0.40 + deviation * 0.50 + gini_effect * 0.08, 0.20, 0.65)
    top = np.clip(0.20 - deviation * 0.30 + gini_effect * 0.05, 0.05, 0.35)
    middle = np.clip(1.0 - bottom - top, 0.15, 0.55)
    inc_raw = np.column_stack([bottom, middle, top])
    inc_totals = inc_raw.sum(axis=1, keepdims=True)
    inc_frac = inc_raw / np.maximum(inc_totals, 1e-30)

    return {
        "eth": eth_frac,
        "rel": rel_frac,
        "set": set_frac,
        "edu": edu_frac,
        "liv": liv_frac,
        "inc": inc_frac,
    }


# ---------------------------------------------------------------------------
# Ideal point mapping (28 issues)
# ---------------------------------------------------------------------------

# Coefficient table: list of dicts, one per issue.
# Each dict maps feature_name → coefficient.
# LGA-level features are prefixed with "lga_".
# Voter-level features use the VoterType property names.

_IDEAL_POINT_COEFFICIENTS: list[dict] = [
    # 1. Sharia Jurisdiction (secular ↔ full Sharia)
    {
        "intercept": -2.0,
        "is_muslim": 5.0, "is_al_shahid": 2.0, "is_tijaniyya": 1.0,
        "is_tertiary": -1.5, "is_urban": -1.0, "is_pada": -2.0, "is_female": -0.5,
        "is_kanuri": 1.5,          # Kanuri are deeply Islamist
        "is_hf_smallholder": 1.0,  # HF pastoral/agricultural base: deeply traditional Islamic
        "is_kanuri_unemployed": 1.5,  # Kanuri jobless youth: Al-Shahid recruitment target
        "is_muslim_female": 1.0,   # Muslim women still favour Sharia, just less so
        "is_muslim_tertiary": -1.5, # Educated Muslims are more moderate
        "is_tijaniyya_trader": -0.8,  # Tijaniyya traders: Sufi moderation, less Sharia-insistent
        "is_pentecostal": -1.5,    # Pentecostals strongly oppose Sharia
        "is_igbo": -1.0,           # Igbo are strongly secular
        "is_ibibio": -0.5,         # Southern Christians oppose Sharia
        "lga_Al-Shahid Influence": 0.3 / 5.0,  # Al-Shahid areas push all voters slightly pro-Sharia
        "lga_Arabic Prestige": 0.03 / 10.0,  # Arabic prestige reinforces Sharia legal-cultural norms
        "is_yoruba_muslim": -1.5,  # Yoruba Muslims less pro-Sharia than northern Muslims
        "is_kanuri_rural": 1.0,    # Rural Kanuri: deeply Islamist, Al-Shahid influence
        "is_muslim_trader": 0.5,   # Muslim traders: lean pro-Sharia (Sharia commercial courts)
        "is_tijaniyya_trader": -0.5,  # Tijaniyya traders (Yoruba): moderate, less pro-Sharia
        "is_hf_muslim_civil_servant": 0.8,  # HF Muslim civil servants: northern establishment, pro-Sharia framework
        "is_kanuri_muslim_youth": 1.5,  # Kanuri Muslim youth: radicalized, strongly pro-Sharia
        "is_yoruba_muslim_trader": -1.0,  # Yoruba Muslim traders: pragmatic, moderate on Sharia
        "lga_Colonial Western": -0.5,  # Western Region: Yoruba Islam is moderate, less pro-Sharia
    },
    # 2. Fiscal Autonomy (centralism ↔ confederalism)
    {
        "intercept": 0.0,
        "is_civil_servant": -2.0, "is_top_income": 1.5,
        "lga_Oil Producing": 3.0, "lga_Poverty Rate Pct": -1.5 / 100.0,
        "lga_GDP Per Capita Est": 0.5 / 90000.0,  # Wealthy LGAs lean confederalist (keep revenue local)
        "is_hausa_fulani": 0.5, "is_pada": -1.5,
        "is_tijaniyya": -0.5,        # Tijaniyya: moderate, comfortable with federal sharing
        "is_ijaw": 2.5,           # Niger Delta wants resource federalism
        "is_nd_minority": 2.0,    # Other Delta groups also want local control
        "is_igbo": 1.5,           # Igbo favour confederalism (self-determination tradition)
        "is_igbo_formal": 2.0,    # Igbo business class: strongest confederalist constituency
        "is_tiv": 1.0,            # Middle Belt wants local autonomy from northern hegemony
        "is_mb_minority": 1.0,    # Middle Belt minorities pro-local control
        "is_yoruba": 0.5,         # Yoruba moderately favour fiscal autonomy
        "is_yoruba_trader": 0.5,  # Yoruba traders benefit from local control of markets
        "is_ijaw_extraction": 2.5,  # Ijaw in extraction: want resource revenue kept local
        "is_igbo_pentecostal": 1.0,  # Igbo Pentecostals: self-determination + activism
        "lga_Conflict History": 0.2 / 5.0,  # Conflict zones → distrust federal, want local control
        "lga_Gini Proxy": 1.0,   # High inequality → demand local autonomy to address it
        "lga_Road Quality Index": 0.05,  # Good roads → connected to broader economy → fiscal autonomy awareness
        "lga_Refinery Present": 0.5,  # Refinery zones: want revenue kept locally
        "is_hf_muslim_civil_servant": -1.5,  # HF Muslim civil servants: benefit from federal centralism
        "is_igbo_pentecostal_formal": 1.5,  # Igbo Pentecostal business: strongly confederalist
        "is_ijaw_christian_unemployed": 2.0,  # Ijaw Christian unemployed: resource federalism radicals
        "lga_Colonial Eastern": 0.5,  # Eastern Region: Biafra legacy → confederalism tradition
        "lga_Colonial Mid-Western": 0.8,  # Mid-Western: extraction revenue + minority status → strong autonomy
    },
    # 3. Chinese Relations (Western pivot ↔ deepen WAFTA)
    {
        "intercept": 0.0,
        "is_naijin": 4.0, "is_formal_sector": 0.5, "is_tertiary": 0.5,
        "lga_Mandarin Presence": 0.3 / 10.0, "lga_Chinese Economic Presence": 0.2 / 10.0,
        "lga_Internet Access Pct": 0.005,  # Internet exposure → awareness of Chinese trade dynamics
        "is_unemployed": -1.5, "is_muslim": -0.5,
        "is_youth_unemployed": -1.0,  # Jobless youth blame Chinese competition
        "is_informal": -0.5,          # Informal traders hurt by Chinese imports
        "is_nupe": 0.5,               # Nupe traders pragmatically pro-trade
        "is_ibibio": 0.5,             # Ibibio: coastal, trade-oriented
        "is_edo": -0.5,               # Edo: wary of foreign economic domination
        "lga_Unemployment Rate Pct": -0.02,  # High unemployment → anti-WAFTA sentiment
        "lga_Planned City": 1.5,      # Chinese-built planned cities: residents pro-WAFTA
        "lga_Rail Corridor": 0.3,     # Rail corridor (Chinese-built): pro-WAFTA infrastructure
        "is_igbo": -0.5,              # Igbo traders compete with Chinese imports
        "is_hausa_fulani": -0.3,      # Northern establishment wary of Chinese cultural influence
        "is_kanuri": -0.5,            # Kanuri: security concerns about foreign involvement in NE
        "is_rural": -0.3,             # Rural: less exposure to Chinese economic benefits
        "is_top_income": 0.8,         # Top income: benefit from Chinese investment/trade
        "is_pada": 1.0,               # Pada: tech-oriented, see Chinese biotech as ally
        "lga_Poverty Rate Pct": -0.005,  # Poorer areas resent foreign capital
    },
    # 4. BIC Reform (abolish ↔ preserve BIC)
    {
        "intercept": 0.5,
        "is_pada": 2.0, "is_civil_servant": -0.5, "is_top_income": -1.5,
        "lga_BIC Effectiveness": 0.3 / 10.0, "is_hausa_fulani": -1.5, "is_tertiary": -0.5,
        "is_naijin": 1.5,             # Naijin cultural attachment to BIC
        "is_kanuri": -1.0,            # Kanuri sceptical of BIC
        "is_yoruba": -0.5,            # Yoruba mildly reformist
        "is_nupe": -0.5,              # Nupe: pragmatic, more concerned with trade than BIC
        "is_ibibio": -0.5,            # Ibibio: southern, BIC less relevant
        "lga_Al-Shahid Influence": -0.2 / 5.0,  # Al-Shahid opposes BIC as Western institution
        "lga_Conflict History": -0.15 / 5.0,     # Conflict zones distrust state institutions
        "lga_English Prestige": 0.02 / 10.0,  # English prestige → BIC is English-medium institution, more support
        "is_igbo": -0.5,              # Igbo: pragmatic, BIC less relevant to commercial priorities
        "is_urban": -0.3,             # Urban: reform-minded, less institutional loyalty
        "is_rural": 0.3,              # Rural: BIC provides community services
        "is_youth": -0.3,             # Youth: less institutional attachment
        "is_muslim": -0.5,            # Muslim: BIC seen as secular/Western institution
        "is_pentecostal": 0.3,        # Pentecostal: BIC values align with Christian institutions
        "is_older": 0.3,              # Older: institutional loyalty, remember BIC establishment
        "lga_Poverty Rate Pct": 0.003,  # Poor areas: BIC welfare services → preserve
    },
    # 5. Ethnic Quotas (meritocracy ↔ affirmative action)
    {
        "intercept": 0.0,
        "is_hausa_fulani": 2.5, "is_minority": 2.0, "is_pada": -3.0,
        "is_tertiary": -1.0, "is_civil_servant": 0.5, "is_youth": 0.5,
        "is_tiv": 1.5,                # Tiv favour quotas as Middle Belt protection
        "is_mb_minority": 1.5,        # Middle Belt minorities need quota protection
        "is_kanuri": 1.0,             # Kanuri favour northern solidarity quotas
        "is_al_shahid": 2.0,          # Al-Shahid: radical quotas to purge "infidels" from state
        "is_igbo": -1.5,              # Igbo strongly meritocratic (self-reliance ethos)
        "is_igbo_formal": -2.0,       # Igbo business class: extremely meritocratic
        "is_yoruba": -1.0,            # Yoruba lean meritocratic
        "is_edo": 0.5,                # Edo moderate pro-quota
        "is_hf_smallholder": 1.5,     # HF smallholders: benefit from northern quotas
        "is_yoruba_muslim": -0.5,     # Yoruba Muslims: less pro-quota than northern Muslims
        "lga_Trad Authority Index": 0.15 / 5.0,  # Trad authority areas: favour communal distribution
        "is_hf_muslim_civil_servant": 1.0,  # HF Muslim civil servants: benefit most from northern quotas
        "is_igbo_pentecostal_formal": -1.5,  # Igbo Pentecostal formal: extreme meritocrats
        "is_minority_urban_youth": -1.0,  # Minority urban youth: reject both quotas and ethnic politics
    },
    # 6. Fertility Policy (population control ↔ pro-natalism)
    {
        "intercept": 0.0,
        "is_muslim": 2.0, "is_rural": 1.5, "is_female": -1.5,
        "is_tertiary": -2.0, "is_pada": -1.0, "is_youth": -0.5,
        "lga_Fertility Rate Est": 0.5,
        "lga_% Population Under 30": 0.02,  # Young population areas → pro-natalist culture
        "lga_Gender Parity Index": -0.5,  # Higher gender parity → more support for family planning
        "lga_Female Literacy Rate Pct": -0.01,  # Female literacy → smaller families, pro-family-planning
        "lga_Median Age Estimate": 0.03,  # Younger median age → pro-natalist culture persists
        "is_muslim_female": 0.5,     # Muslim women still lean pro-natalist
        "is_rural_muslim": 0.5,      # Rural Muslim compound effect
        "is_kanuri": 1.0,            # Kanuri high-fertility culture
        "is_female_tertiary": -1.0,  # Educated women strongly pro-control
        "is_urban_youth": -1.0,      # Urban youth favour smaller families
        "lga_Al-Shahid Influence": 0.3 / 5.0,  # Al-Shahid areas more pro-natalist
        "is_older": 1.0,            # Elderly: pro-natalist (traditional values)
        "is_fulani_rural": 2.0,     # Rural Fulani: pastoral tradition, large families essential for herding
        "is_middle_age": 0.5,       # Middle-aged: moderately pro-natalist
        "lga_Out of School Children Pct": 0.01,  # High OSC → pro-natalist norms persist
        "is_catholic": 0.8,             # Catholics: anti-contraception, pro-natalist doctrine
        "is_pentecostal_formal": -0.5,  # Pentecostal formal: more pragmatic family planning
        "is_mainline_protestant": -0.5, # Mainline Protestants: accept family planning
        "lga_Primary Enrollment Pct": -0.005,  # High primary enrollment → more exposure to family planning education
        "is_hf_rural_older": 1.5,  # HF rural elderly: strongest pro-natalist constituency
        "is_yoruba_christian_urban": -1.0,  # Yoruba Christian urban: modern family planning
    },
    # 7. Constitutional Structure (parliamentary ↔ presidential)
    {
        "intercept": 0.0,
        "is_majority": 1.5, "is_minority": -2.0, "is_hausa_fulani": 1.0,
        "is_pada": -2.0, "is_tertiary": -0.5,
        "lga_Trad Authority Index": -0.3 / 5.0,
        "lga_BIC Effectiveness": 0.02 / 10.0,  # Effective BIC → institutional trust → presidential preference
        "lga_Traditional Authority": 0.3,  # Active traditional authority → prefer strong executive
        "is_tiv": -1.5,              # Tiv fear presidential centralism
        "is_mb_minority": -1.5,      # Middle Belt minorities pro-parliamentary
        "is_al_shahid": -3.0,        # Al-Shahid: reject secular governance entirely — want Islamic state
        "is_kanuri": 0.5,            # Kanuri moderate pro-presidential
        "is_igbo": -0.5,             # Igbo wary of presidential power
        "is_edo": -1.0,              # Edo pro-parliamentary (civic tradition)
        "is_edo_christian": -1.0,     # Edo Christians: strongly pro-parliamentary (Benin civic tradition)
        "is_mb_minority_christian": -1.5,  # MB Christian minorities: fear presidential centralisation
        "lga_Conflict History": 0.3 / 5.0,    # Conflict zones → favour strong executive
        "lga_Federal Control 2058": 0.5,       # Federal control → accept stronger executive
    },
    # 8. Resource Revenue (federal monopoly ↔ local control)
    {
        "intercept": -0.5,
        "lga_Oil Producing": 3.0, "lga_Extraction Intensity": 0.5 / 5.0,
        "is_ijaw": 3.0, "is_civil_servant": -2.0,
        "lga_Cobalt Extraction Active": 2.0,
        "lga_Oil Extraction Active": 1.5,  # Active oil extraction → demand local control
        "lga_Other Mining Active": 1.0,     # Tin/coltan mining → resource control demand
        "is_nd_minority": 2.5,        # Niger Delta minorities want local control
        "is_ijaw_extraction": 3.0,     # Ijaw in extraction: most vocal for local revenue
        "is_edo": 1.5,                 # Edo in oil zone; pro-local control
        "is_ibibio": 1.0,              # Ibibio: Akwa Ibom oil state
        "is_hausa_fulani": -1.5,       # Northern establishment benefits from federal control
        "is_hf_smallholder": -1.0,     # HF smallholders: benefit from federal redistribution
        "is_kanuri": -1.0,             # Kanuri benefit from federal redistribution
        "is_tiv": 0.5,                 # Tiv: Benue has mineral resources
        "is_yoruba": 0.5,             # Yoruba: fiscal restructuring advocates
        "is_igbo": 1.0,               # Igbo: strongly pro-fiscal federalism
        "is_urban": 0.3,              # Urban: more aware of resource politics
        "is_tertiary": 0.5,           # Educated: understand fiscal federalism arguments
        "is_pada": -0.5,              # Pada: new community, less attachment to resource battles
        "is_nupe": 0.3,               # Nupe: Middle Belt, want local resource control
        "lga_Poverty Rate Pct": 0.005,  # Poorer LGAs want more local revenue control
    },
    # 9. Housing (pure market ↔ state intervention)
    {
        "intercept": 1.0,
        "is_urban": 1.0, "is_bottom_income": 2.5, "is_top_income": -2.5,
        "lga_Housing Affordability": -0.3 / 10.0, "is_youth": 1.5, "is_pada": -1.5,
        "lga_GDP Per Capita Est": 0.5 / 90000.0,  # Wealthy LGAs: higher housing prices → more demand for intervention
        "lga_Population Density per km2": 0.5 / 55000.0,  # Dense areas → housing pressure → interventionism
        "is_urban_youth": 1.0,        # Urban youth face acute housing crisis
        "is_informal": 0.5,           # Informal workers need housing support
        "is_middle_income": 0.5,      # Squeezed middle also wants state help
        "lga_Planned City": -0.8,     # Planned cities have better housing → less demand for intervention
        "lga_Rail Corridor": -0.2,    # Rail corridors: better connectivity eases housing pressure
        "lga_Urban Pct": 0.01,        # Urban areas → more housing pressure
        "lga_Unemployment Rate Pct": 0.01,  # High unemployment → more demand for state housing
        "lga_Gini Proxy": 1.5,  # High inequality → housing affordability crisis → demand intervention
        "lga_% Population Under 30": 0.01,  # Young population → housing pressure from new households
        "lga_Pct Livelihood Informal": 0.01,  # Informal workers → housing insecurity
        "lga_Land Formalization Pct": -0.005,  # Formalized land → functioning housing market → less intervention
        "is_hf_bottom_income": 0.5,    # Poor northerners: need state housing (no private market access)
        "is_igbo_bottom_income": 1.0,  # Poor Igbo in cities: acute housing crisis
        "lga_Major Urban Center": 1.0,  # Major cities: extreme housing pressure → interventionism
        "is_tertiary_bottom_income": 1.5,  # Educated poor: acute housing pain with awareness of alternatives
        "is_young_adult": 0.5,  # 25-34: family formation, housing most acute need
    },
    # 10. Education (radical localism ↔ meritocratic centralism)
    {
        "intercept": 0.0,
        "is_tertiary": 2.0, "is_muslim": -1.0, "is_rural": -1.5,
        "is_female": 0.5, "is_naijin": 1.5,
        "lga_Out of School Children Pct": -0.2 / 100.0,
        "lga_Secondary Enrollment Pct": 0.01,      # High enrollment → more centralism/meritocratic
        "lga_Youth Unemployment Rate Pct": 0.01,  # High youth unemployment → demand centralized education
        "lga_GDP Per Capita Est": 0.3 / 90000.0,   # Wealthier LGAs → more meritocratic orientation
        "is_igbo": 1.0,               # Igbo strongly pro-education/meritocracy
        "is_kanuri": -1.5,            # Kanuri prefer Quranic/local education
        "is_rural_muslim": -1.0,      # Rural Muslims prefer almajiri/local
        "is_female_tertiary": 1.0,    # Educated women champion education reform
        "is_yoruba": 0.5,             # Yoruba favour structured education
        "lga_Al-Shahid Influence": -0.3 / 5.0,  # Al-Shahid areas: prefer Quranic/local over centralist
        "lga_Almajiri Index": -0.2 / 5.0,  # High almajiri → entrenched localist education norms
        "lga_Num Secondary Schools": 0.05,   # More schools → more invested in centralist education system
        "lga_English Prestige": 0.02 / 10.0,  # English prestige → meritocratic centralism (English as medium)
        "lga_Female Literacy Rate Pct": 0.005,  # Female literacy → investment in education → centralist
        "lga_Mobile Phone Penetration Pct": 0.003,  # Mobile learning platforms → centralist education buy-in
        "lga_% Population Under 30": 0.01,  # Young population → education demand amplified
        "lga_Traditionalist Practice": -0.1 / 5.0,  # Traditional practice → localist education
        "lga_Primary Enrollment Pct": 0.005,  # Higher primary enrollment → centralist education buy-in
        "is_muslim_civil_servant": -0.5,  # Muslim civil servants: prefer Islamic education elements
        "is_pentecostal_formal": 0.5,     # Pentecostal formal: favour faith-based but centralized schools
        "is_mainline_protestant": 0.8,    # Mainline Protestants: strongly pro-meritocratic centralism
    },
    # 11. Labor & Automation (pro-capital ↔ pro-labor)
    {
        "intercept": 0.5,
        "is_informal": 2.0, "is_formal_sector": 1.0, "is_unemployed": 0.5,
        "is_top_income": -3.0, "is_smallholder": -0.5,
        "lga_Pct Livelihood Manufacturing": 0.2 / 100.0,
        "lga_Unemployment Rate Pct": 0.02,      # High unemployment → pro-labor protection
        "lga_Youth Unemployment Rate Pct": 0.01, # Youth joblessness → automation anxiety
        "lga_Pct Livelihood Informal": 0.02,     # Informal economy → pro-labor regulation
        "is_youth_unemployed": 1.5,   # Jobless youth very pro-labor protection
        "is_nupe": 0.5,               # Nupe: artisan/trader tradition
        "is_middle_income": 0.5,      # Middle class worried about automation
        "is_urban_bottom_income": 1.0,  # Urban poor: gig economy, no labor protections
        "is_older": -0.5,             # Elderly less concerned about automation
        "lga_Chinese Economic Presence": 0.1 / 10.0,  # Chinese presence → automation threat
        "lga_Cobalt Extraction Active": 0.5,  # Cobalt mining areas: battery supply chain → automation anxiety
        "lga_Poverty Rate Pct": 0.01,         # Poorer areas → more worried about job displacement
        "lga_Urban Pct": 0.01,  # Urban areas → industrial/service employment → labor politics salient
        "lga_% Population Under 30": 0.01,  # Young population → labor market entry pressure
        "lga_Other Mining Active": 0.5,  # Mining communities → industrial labor politics
        "lga_Refinery Zone": 0.3,  # Refinery zone → industrial labor concentration
        "is_pentecostal_formal": -0.5,  # Pentecostal formal sector: pro-capital, entrepreneurial prosperity gospel
        "is_muslim_trader": 0.5,        # Muslim traders: pro-labor (guild/bazaar solidarity)
        "is_urban_trader": 0.5,  # Urban informal traders: pro-labor, fear automation of retail
    },
    # 12. Military Role (civilian control ↔ military guardianship)
    {
        "intercept": 0.0,
        "is_civil_servant": 2.0, "is_pada": 0.5, "is_hausa_fulani": 1.0,
        "lga_Conflict History": 0.8 / 5.0, "is_youth": -0.5, "is_tertiary": -1.5,
        "is_al_shahid": -2.5,         # Al-Shahid: anti-state military (want Islamic militia instead)
        "is_kanuri": 2.0,             # Kanuri heavily pro-military (Boko Haram era)
        "is_kanuri_unemployed": 1.5,  # Kanuri jobless: security concerns, some militant sympathy
        "is_tiv": -1.0,              # Tiv wary of military (history of military rule)
        "is_igbo": -1.5,             # Igbo anti-military (civil war memory)
        "is_igbo_formal": -2.0,      # Igbo business class: strongly anti-military (civ war + markets)
        "is_rural_older": 0.5,       # Rural elderly trust military for security
        "lga_Federal Control 2058": 0.8,  # Federal control zones strongly pro-military
        "lga_Al-Shahid Influence": 0.4 / 5.0,  # Al-Shahid zones: demand military response
        "is_hf_muslim_civil_servant": 1.0,  # HF Muslim civil servants: military-state nexus, pro-guardianship
        "is_kanuri_muslim_youth": 1.5,  # Kanuri Muslim youth: complex — want security but also militant sympathy
        "is_ijaw_christian_unemployed": -1.5,  # Ijaw Christian unemployed: anti-military (Delta repression)
        "is_urban": -0.5,            # Urban: prefer civilian institutional control
        "is_rural": 0.3,             # Rural: trust military for local security
        "is_formal_sector": -0.3,    # Formal sector: want stable civilian institutions
        "is_muslim": 0.3,            # Muslim: military provides northern security
        "is_nupe": -0.5,             # Nupe: civilian-oriented, Middle Belt suspicion
        "is_yoruba": -1.0,           # Yoruba: strong anti-military tradition (Abiola era)
        "lga_Urban Pct": -0.005,     # Urban LGAs: pro-civilian governance
    },
    # 13. Immigration (open borders ↔ restrictionism)
    {
        "intercept": -0.5,
        "is_pada": -0.5, "is_naijin": 1.5, "is_bottom_income": -2.0,
        "is_top_income": 1.5, "lga_Fertility Rate Est": -0.3, "is_hausa_fulani": -1.0,
        "is_kanuri": -1.5,            # Kanuri: border region, suspicious of migrants
        "is_middle_age": -0.5,       # Middle-aged: established, protective of status quo
        "is_kanuri_unemployed": -2.0,  # Kanuri unemployed: blame migrants for jobs
        "is_urban_youth": -1.0,       # Urban youth feel competition from migrants
        "is_yoruba_trader": -1.0,     # Yoruba traders: compete with migrant businesses
        "is_informal": -0.5,          # Informal workers face migrant competition
        "is_ibibio": 0.5,             # Ibibio: coastal, more open to trade/people
        "lga_Conflict History": -0.3 / 5.0,  # Conflict zones → more restrictionist
        "lga_Unemployment Rate Pct": -0.02,  # High unemployment → anti-immigration
        "lga_Youth Unemployment Rate Pct": -0.01,  # Youth joblessness → restrictionism
        "lga_Al-Shahid Influence": -0.15 / 5.0,  # Al-Shahid areas: xenophobic, restrictionist
        "lga_Planned City": 0.5,       # Chinese planned cities: cosmopolitan, pro-open borders
        "lga_Housing Affordability": 0.05 / 10.0,  # Affordable housing → less anti-immigrant sentiment
        "lga_Population Density per km2": -0.3 / 55000.0,  # Dense areas → more competition → restrictionist
        "lga_Internet Access Pct": -0.005,  # Internet: online anti-immigration echo chambers
        "lga_Road Quality Index": -0.05,  # Good roads → more migrant flows → restrictionist backlash
    },
    # 14. Language Policy (vernacular ↔ English supremacy)
    {
        "intercept": 0.0,
        "is_pada": 2.5, "is_naijin": -2.0, "is_muslim": -1.5, "is_tertiary": 1.0,
        "lga_English Prestige": 0.3 / 10.0, "lga_Arabic Prestige": -0.3 / 10.0,
        "is_igbo": 1.0,               # Igbo pragmatically pro-English
        "is_yoruba": -0.5,            # Yoruba proud of vernacular
        "is_kanuri": -1.5,            # Kanuri defend Kanuri language
        "is_tiv": -1.0,              # Tiv defend local language
        "is_nupe": -0.5,             # Nupe value local identity
        "is_nupe_muslim": -0.8,      # Nupe Muslims: Arabic influence, less pro-English
        "is_christian_urban": 0.5,    # Urban Christians lean English
        "is_yoruba_muslim": -0.5,     # Yoruba Muslims: value Arabic + Yoruba (less English)
        "is_pada_tertiary": 1.5,      # Educated Padà: strongly pro-English (cosmopolitan)
        "lga_Al-Shahid Influence": -0.2 / 5.0,  # Al-Shahid areas: pro-Arabic, anti-English
        "lga_Almajiri Index": -0.15 / 5.0,  # Almajiri areas: Arabic/vernacular preferred
        "lga_Mandarin Presence": 0.02 / 10.0,  # Mandarin presence → language diversity awareness, pragmatic multilingualism
        "is_muslim_tertiary": -0.5,  # Educated Muslims: pragmatic multilingual, moderate on language
        "is_christian_urban": 0.8,   # Urban Christians: strongly pro-English for modernity/commerce
        "lga_Colonial Western": -0.5,  # Western Region: strong Yoruba language pride → vernacular
        "lga_Colonial Eastern": 0.5,   # Eastern Region: pragmatic Igbo pro-English for commerce
    },
    # 15. Women's Rights (traditional patriarchy ↔ aggressive feminism)
    {
        "intercept": -0.5,
        "is_female": 2.0, "is_muslim": -2.0, "is_tertiary": 1.0, "is_urban": 1.0,
        "lga_Gender Parity Index": 1.0, "is_pada": 1.5,
        "lga_Female Literacy Rate Pct": 0.01,  # Higher female literacy → more feminist orientation
        "is_al_shahid": -2.5,         # Al-Shahid: extreme patriarchy, oppose all women's rights
        "is_muslim_female": 1.5,      # Muslim women still want rights, more moderate
        "is_female_tertiary": 1.5,    # Educated women strongest feminists
        "is_kanuri": -1.5,            # Kanuri strongly patriarchal
        "is_igbo": 0.5,               # Igbo moderate feminist (market women tradition)
        "is_pentecostal": -0.5,       # Pentecostal complementarian gender views
        "is_tiv": 0.5,                # Tiv: relatively egalitarian tradition
        "is_edo_christian": 0.8,      # Edo Christians: progressive Benin City tradition
        "lga_Al-Shahid Influence": -0.3 / 5.0,  # Al-Shahid areas → more conservative on women
        "lga_Conflict History": -0.2 / 5.0,      # Conflict zones → conservative retrenchment
        "is_yoruba_muslim": 0.5,      # Yoruba Muslims: more progressive than other Muslims on gender
        "is_kanuri_rural": -1.0,      # Rural Kanuri: most conservative gender views
        "lga_Almajiri Index": -0.2 / 5.0,  # Almajiri: reinforces patriarchal norms
        "lga_Traditionalist Practice": -0.1 / 5.0,  # Traditionalist areas: patriarchal customs
        "lga_Out of School Children Pct": -0.01,  # High OSC → girls excluded from education → patriarchal
        "is_pentecostal_formal": -0.5,  # Pentecostal formal sector: complementarian, prosperity-wife model
        "is_catholic": 0.5,             # Catholics: more progressive than Pentecostals on gender
        "is_mainline_protestant": 0.8,  # Mainline Protestants: most progressive Christian denomination
        "is_catholic_smallholder": -0.5,  # Catholic smallholder women: rural Catholic conservatism
        "is_yoruba_christian_urban": 1.0,  # Yoruba Christian urban women: progressive feminist base
        "is_hf_rural_older": -1.5,  # HF rural elderly: deeply patriarchal
        "is_kanuri_muslim_youth": -1.0,  # Kanuri Muslim youth: conservative gender views
        "is_igbo_female": 1.0,  # Igbo women: market women tradition, economic agency
        "is_yoruba_female": 0.8,  # Yoruba women: Iyaloja market women, political voice
        "lga_Internet Access Pct": 0.005,  # Internet: exposure to feminist discourse → progressive
        "lga_Mobile Phone Penetration Pct": 0.005,  # Mobile phones → women's economic agency, GBV reporting
        "lga_Secondary Enrollment Pct": 0.005,  # Higher secondary enrollment → gender awareness in schools
        "lga_Pentecostal Growth": -0.1 / 3.0,  # Pentecostal growth → conservative complementarian gender views
    },
    # 16. Traditional Authority (marginalization ↔ formal integration)
    {
        "intercept": 0.0,
        "is_rural": 1.5, "lga_Trad Authority Index": 0.5 / 5.0,
        "is_tertiary": -2.0, "is_pada": -2.5, "is_older": 1.0, "is_naijin": -1.5,
        "is_kanuri": 2.0,             # Kanuri: strong Shehu of Borno tradition
        "is_hausa_fulani": 1.5,       # HF: emirate system is backbone
        "is_nupe": 1.0,               # Nupe: Etsu Nupe tradition
        "is_yoruba": 1.5,             # Yoruba: Obas deeply revered
        "is_edo": 1.0,                # Edo: Oba of Benin tradition
        "is_tiv": -0.5,              # Tiv: more egalitarian, less chief-oriented
        "is_rural_older": 1.0,       # Rural elders strongest supporters
        "is_urban_youth": -1.5,       # Urban youth reject trad authority
        "is_pada_tertiary": -2.0,     # Educated Padà: techno-progressive, anti-traditional
        "is_kanuri_rural": 1.0,       # Rural Kanuri: strong traditional Shehu system
        "lga_Traditionalist Practice": 0.2 / 5.0,  # Active traditionalist practice → integrationist
        "lga_Traditional Authority": 1.0,  # Binary: LGA has active traditional authority → everyone leans integrationist
        "lga_Median Age Estimate": 0.03,  # Older median age → more support for traditional authority
        "lga_Arabic Prestige": -0.02 / 10.0,  # Arabic prestige → emirate/lamido system support (northern trad auth)
        "is_hf_rural_older": 1.5,  # HF rural elderly: strongest emirate system supporters
        "is_minority_urban_youth": -1.5,  # Minority urban youth: reject traditional authority entirely
        "is_yoruba_christian_urban": -0.5,  # Yoruba Christian urbanites: modern governance preference
        "lga_Colonial Western": 0.8,  # Western Region: Oba institution deeply embedded in governance
    },
    # 17. Infrastructure (targeted ↔ universal provision)
    {
        "intercept": 1.0,
        "is_rural": 1.5, "is_bottom_income": 1.0,
        "lga_Access Electricity Pct": -0.02, "lga_Access Water Pct": -0.01,
        "is_top_income": -1.0,
        "is_mb_minority": 0.5,        # Middle Belt underserved
        "is_nd_minority": 0.5,        # Niger Delta: pipelines but no roads
        "is_urban_youth": -0.5,       # Urban youth prefer targeted investment
        "lga_Conflict History": 0.3 / 5.0,   # Conflict zones demand reconstruction
        "lga_Federal Control 2058": 0.3,      # Federal control zones need rebuilding
        "is_rural_bottom_income": 1.0,  # Rural poor: most infrastructure-deprived
        "lga_Planned City": -0.5,     # Planned cities: already well-served → less demand
        "lga_Rail Corridor": -0.3,    # Rail access → infrastructure already decent
        "lga_Market Access Index": -0.1,  # Well-connected LGAs need less universal provision
        "lga_Road Quality Index": -0.1,  # Good roads → less demand for universal provision
        "is_commercial_ag": 0.5,          # Commercial farmers: need roads, electricity, irrigation
        "is_christian_rural": 0.5,        # Rural Christians: Middle Belt infrastructure deficit
        "is_urban_bottom_income": 0.5,   # Urban poor: inadequate infrastructure despite density
        "lga_Major Urban Center": -0.8,  # Major cities: already served → less demand for universal infra
    },
    # 18. Land Tenure (customary ↔ formalization)
    {
        "intercept": 0.0,
        "is_smallholder": -1.5, "is_rural": -1.0,
        "lga_Trad Authority Index": -0.3 / 5.0, "is_top_income": 2.5,
        "lga_Land Formalization Pct": 0.03 / 100.0, "is_pada": 2.0,
        "is_tiv": -1.5,              # Tiv: strong customary land system
        "is_nupe": -1.0,             # Nupe: traditional land allocation
        "is_fulani_rural": -2.0,     # Rural Fulani: communal grazing land tradition, fiercely anti-formalization
        "is_mb_minority_christian": -1.0,  # MB Christian farmers: customary land rights, herder-farmer disputes
        "is_igbo": 1.0,              # Igbo: pro-formalization (commercial mindset)
        "is_commercial_ag": 2.0,     # Commercial farmers want formal titles
        "is_rural_older": -1.0,      # Rural elderly defend customary tenure
        "lga_Conflict History": -0.2 / 5.0,  # Conflict zones: land disputes → customary defence
        "lga_Pct Livelihood Agriculture": -0.01,  # Agricultural LGAs → customary land defence
        "lga_Traditionalist Practice": -0.15 / 5.0,  # Traditional practice → defend customary tenure
        "lga_Road Quality Index": -0.05,  # Good roads → land markets develop → formalization pressure
        "lga_Urban Pct": 0.01,  # Urban areas → land formalization more important for housing
    },
    # 19. Taxation (low tax ↔ high redistribution)
    {
        "intercept": 0.5,
        "is_top_income": -3.5, "is_bottom_income": 2.5, "is_unemployed": 2.0,
        "lga_Gini Proxy": 2.0, "is_pada": -1.0, "lga_Poverty Rate Pct": 0.02 / 100.0,
        "lga_GDP Per Capita Est": -1.0 / 90000.0,  # Wealthy LGAs → lower appetite for redistribution
        "lga_Unemployment Rate Pct": 0.02,          # High unemployment → demand redistribution
        "is_hf_bottom_income": 0.5,  # Poor northerners want redistribution
        "is_informal": 0.5,          # Informal workers want better services
        "is_youth_unemployed": 1.0,  # Unemployed youth strongly pro-redistribution
        "is_igbo": -1.0,             # Igbo prefer low-tax self-reliance
        "is_rural_bottom_income": 1.5,  # Rural poor: strongly pro-redistribution
        "lga_Access Healthcare Pct": -0.005,  # Poor healthcare → want redistribution for services
        "lga_Access Water Pct": -0.005,       # Poor water → want redistribution for services
        "lga_Pct Livelihood Informal": 0.015,  # Informal economy → avoid tax, anti-redistribution
        "lga_Pct Livelihood Services": -0.01,  # Service economy → more tax-aware, pragmatic on redistribution
        "is_igbo_bottom_income": 0.5,  # Even poor Igbo want some redistribution (cross-pressure)
        "is_urban_bottom_income": 1.0,  # Urban poor: cost of living → demand redistribution
        "is_yoruba_formal": -0.5,      # Yoruba formal sector: tax-conscious, low-redistribution
        "is_muslim_trader": -0.5,      # Muslim traders: low tax (Islamic zakat replaces secular tax)
        "is_pentecostal_formal": -0.8, # Pentecostal formal: prosperity gospel, anti-redistribution
        "is_muslim_civil_servant": 0.5,  # Muslim civil servants: pro-redistribution (Islamic welfare)
        "is_igbo_pentecostal_formal": -1.5,  # Igbo Pentecostal formal: prosperity gospel, anti-tax
        "is_ijaw_christian_unemployed": 2.0,  # Ijaw Christian unemployed: strongly pro-redistribution
        "is_yoruba_muslim_trader": -0.5,  # Yoruba Muslim traders: low-tax, zakat over secular tax
        "is_tertiary_bottom_income": 1.5,  # Educated poor: strongly pro-redistribution (aware of inequality)
    },
    # 20. Agricultural Policy (free market ↔ protectionist smallholder)
    {
        "intercept": 0.5,
        "is_smallholder": 3.0, "is_commercial_ag": -3.0, "is_rural": 1.0,
        "is_top_income": -1.5, "lga_Pct Livelihood Agriculture": 0.02 / 100.0,
        "lga_Poverty Rate Pct": 0.01,            # Poorer LGAs → protectionist for food security
        "lga_Pct Livelihood Services": -0.01,     # Service economy → less interest in ag protection
        "lga_Market Access Index": -0.1,          # Good market access → less need for protection
        "lga_Road Quality Index": 0.05,  # Good roads → market access for farmers → less protectionist
        "lga_Land Formalization Pct": -0.005,  # Formalized land → commercial agriculture → free-market
        "is_hf_smallholder": 2.0,    # HF pastoral/farming base: strongly protectionist
        "is_fulani_smallholder": 2.5,  # Fulani pastoralists: most vulnerable to market disruption
        "is_tiv": 1.5,               # Tiv: breadbasket, smallholder heartland
        "is_nupe": 1.0,              # Nupe: farming tradition
        "is_mb_minority": 0.5,       # Middle Belt agricultural communities
        "is_yoruba": -0.5,           # Yoruba: more commercially oriented
        "is_yoruba_trader": -1.0,    # Yoruba traders: prefer free market ag
        "is_christian_rural": 0.5,   # Rural Christians in Middle Belt: smallholder base
        "is_fulani_rural": 2.5,      # Rural Fulani pastoralists: need grazing protection, most vulnerable
        "is_mb_minority_christian": 1.0,  # MB Christian minorities: farming communities, protectionist
        "is_catholic_smallholder": 1.5,  # Catholic smallholders: deeply agrarian, strongly protectionist
    },
    # 21. Biological Enhancement (prohibition ↔ universal access)
    {
        "intercept": 0.0,
        "is_top_income": 2.0, "is_muslim": -2.0, "is_youth": 1.5,
        "lga_Biological Enhancement Pct": 0.1 / 100.0, "is_tertiary": 0.5, "is_rural": -1.0,
        "lga_Internet Access Pct": 0.01,  # High internet → exposure to bio-enhancement discourse
        "is_pentecostal": -1.5,       # Pentecostals oppose "playing God"
        "is_tertiary_youth": 1.5,     # Educated youth most pro-access
        "is_kanuri": -1.5,            # Kanuri: conservative, anti-enhancement
        "is_urban_youth": 1.0,        # Urban youth embrace technology
        "is_naijin": 1.0,             # Naijin cosmopolitan, pro-tech
        "is_pada_tertiary": 2.0,       # Educated Padà: tech-progressive elite, very pro-access
        "is_kanuri_rural": -1.0,       # Rural Kanuri: deeply conservative, anti-enhancement
        "lga_Pentecostal Growth": -0.15 / 3.0,  # Pentecostal areas: moral opposition to enhancement
        "lga_Al-Shahid Influence": -0.2 / 5.0,  # Al-Shahid areas: religious opposition to enhancement
        "lga_Mobile Phone Penetration Pct": 0.003,  # Mobile exposure to tech discourse → pro-access
        "lga_Pct Livelihood Services": 0.01,  # Service sector → tech-forward, pro-enhancement
        "is_older": -1.5,             # Elderly: conservative, anti-enhancement
        "is_middle_age": -0.5,        # Middle-aged: cautious about enhancement
        "is_pentecostal_formal": -1.0,  # Pentecostal formal: strongest "playing God" opposition
        "is_catholic": -0.8,           # Catholics: cautious (Vatican bioethics) but less extreme than Pentecostal
        "is_mainline_protestant": 0.3, # Mainline Protestants: more accepting of science/medicine
        "is_igbo_pentecostal_formal": -1.5,  # Igbo Pentecostal formal: prosperity gospel but anti-enhancement
        "is_yoruba_christian_urban": 0.8,  # Yoruba Christian urban: cosmopolitan, pro-science
        "is_kanuri_muslim_youth": -1.5,  # Kanuri Muslim youth: deeply conservative, anti-enhancement
        "is_young_adult": 0.5,  # 25-34: open to enhancement for career advantage
    },
    # 22. Trade Policy (autarky ↔ full openness)
    {
        "intercept": 0.0,
        "is_formal_sector": 1.5, "lga_Pct Livelihood Manufacturing": 0.3 / 100.0,
        "is_smallholder": -1.5, "is_top_income": 2.0, "is_unemployed": -2.0,
        "lga_Rail Corridor": 0.5,
        "lga_Pct Livelihood Services": 0.02,  # Service economy → pro-open trade
        "lga_Pct Livelihood Informal": -0.02,  # Informal economy → protectionist (fear imports)
        "lga_GDP Per Capita Est": 0.5 / 90000.0,  # Wealthy LGAs benefit from open trade
        "lga_Market Access Index": 0.1,  # Good market access → benefit from open trade
        "is_commercial_ag": 1.5,      # Commercial farmers: need open export markets
        "is_igbo": 1.0,               # Igbo: entrepreneurial, pro-open trade
        "is_igbo_formal": 2.0,        # Igbo business class: strongest free-trade advocates
        "is_yoruba": 0.5,             # Yoruba: commercial culture
        "is_yoruba_trader": 1.0,      # Yoruba traders: benefit from open markets
        "is_nupe": 0.5,               # Nupe: historic trans-Saharan trade routes
        "is_nupe_muslim": 0.8,       # Nupe Muslims: trans-Saharan trade networks, pro-openness
        "is_igbo_trader": 1.5,       # Igbo traders: mobile diaspora entrepreneurialism, pro-open trade
        "is_kanuri": -0.5,            # Kanuri: protectionist instinct
        "is_hf_smallholder": -1.0,    # HF smallholders: fear cheap food imports
        "is_pada_tertiary": 1.5,       # Educated Padà: cosmopolitan, very pro-open trade
        "lga_Planned City": 0.8,      # Chinese planned cities: WAFTA trade beneficiaries
        "lga_Chinese Economic Presence": 0.15 / 10.0,  # Chinese presence → pro-open trade (WAFTA)
        "lga_Pct Livelihood Services": 0.01,  # Service economy → pro-open trade
        "lga_Cobalt Extraction Active": 0.8,  # Cobalt extraction → global battery supply chain → pro-open trade
        "lga_Refinery Present": 0.3,           # Refinery zones: export-oriented economy
        "is_muslim_trader": -0.5,    # Muslim traders: protective of local market networks
        "is_tijaniyya_trader": 0.5,  # Tijaniyya traders (Yoruba): historically cosmopolitan, pro-trade
        "lga_Major Urban Center": 0.8,  # Major cities: trade-connected, pro-openness
        "lga_Road Quality Index": 0.05,  # Good roads → trade connectivity → pro-openness
        "lga_Mandarin Presence": 0.02 / 10.0,  # Mandarin presence → Chinese trade integration → pro-WAFTA
        "is_yoruba_muslim_trader": 0.8,  # Yoruba Muslim traders: Tijaniyya trade networks, pro-open
        "is_igbo_pentecostal_formal": 1.5,  # Igbo Pentecostal formal: entrepreneurial, pro-free trade
        "is_igbo_female": 0.8,  # Igbo women: market women → pro-open trade
        "is_urban_trader": -0.5,  # Urban traders: fear cheap imports undercutting local markets
    },
    # 23. Environmental Regulation (growth first ↔ strong regulation)
    {
        "intercept": 0.0,
        "is_formal_sector": -2.0,
        "is_tertiary": 1.5, "lga_Oil Producing": 1.0,
        "is_top_income": -1.5, "is_ijaw": 2.0, "is_bottom_income": -1.0,
        "lga_Extraction Intensity": 0.3 / 5.0,  # Extraction areas → pro-regulation (pollution)
        "lga_Pct Livelihood Extraction": -0.02,  # Extraction workers → anti-regulation (livelihood)
        "lga_GDP Per Capita Est": 0.3 / 90000.0,  # Wealthier LGAs → post-materialist green values
        "is_nd_minority": 1.5,        # Niger Delta minorities: pollution victims
        "is_ijaw_extraction": 2.0,    # Ijaw in extraction: direct victims, want regulation
        "is_edo": 1.0,                # Edo: oil zone environmental awareness
        "is_christian_rural": 0.5,    # Rural Christians (Middle Belt): pollution/deforestation awareness
        "is_tertiary_youth": 1.0,     # Educated youth pro-environment
        "is_ibibio": 0.5,             # Ibibio: Akwa Ibom environmental concern
        "lga_Refinery Zone": 0.3,     # Refinery zones: direct pollution → want regulation
        "lga_Refinery Present": 0.5,  # Refinery present: residents demand clean air
        "is_older": -0.5,             # Elderly: prioritise growth over regulation
        "lga_Colonial Mid-Western": 0.5,  # Mid-Western: Edo/Delta extraction zone → environmental awareness
        "lga_Oil Extraction Active": 1.0,  # Active oil extraction → pollution → pro-regulation
        "lga_Other Mining Active": 0.5,  # Active mining → environmental degradation → pro-regulation
    },
    # 24. Media Freedom (state control ↔ full press freedom)
    {
        "intercept": 0.5,
        "is_tertiary": 1.5, "lga_Internet Access Pct": 0.05 / 100.0,
        "is_pada": -0.5, "is_youth": 1.0, "is_civil_servant": -2.0,
        "is_al_shahid": -1.0,
        "is_urban_youth": 0.5,        # Urban youth are social media generation
        "is_kanuri": -1.0,            # Kanuri: state media tradition
        "is_igbo": 0.5,               # Igbo: pro-free expression
        "is_yoruba": 0.5,             # Yoruba: strong media tradition
        "lga_Conflict History": -0.3 / 5.0,   # Conflict zones → lean state control (security)
        "lga_Federal Control 2058": -0.5,      # Federal control → accept media restrictions
        "is_igbo_pentecostal": 1.0,    # Igbo Pentecostals: strongly pro-free expression
        "is_older": -0.5,             # Elderly: prefer media control (stability)
        "lga_Mobile Phone Penetration Pct": 0.005,  # Connected areas → value media freedom
        "lga_Secondary Enrollment Pct": 0.005,  # Higher education → media literacy → value free press
        "is_ibibio": 0.5,             # Ibibio: Calabar/Uyo media tradition, pro-free press
        "is_edo": 0.5,                # Edo: Benin City press tradition
        "lga_Colonial Western": 0.5,  # Western Region: Lagos media culture, Yoruba press tradition
        "lga_Colonial Eastern": 0.3,  # Eastern Region: Igbo press freedom advocacy
    },
    # 25. Healthcare (pure market ↔ universal provision)
    {
        "intercept": 1.0,
        "is_bottom_income": 2.5, "is_top_income": -2.0,
        "lga_Access Healthcare Pct": -0.05 / 100.0, "is_rural": 1.0, "is_older": 0.5,
        "lga_Access Water Pct": -0.01,             # Low water access correlates with poor health infra
        "lga_Poverty Rate Pct": 0.015,            # Poorer LGAs → demand universal healthcare
        "lga_GDP Per Capita Est": -0.5 / 90000.0,  # Wealthy LGAs can afford private → less demand
        "is_middle_income": 0.5,      # Middle class also wants accessible healthcare
        "is_female": 0.5,             # Women (maternal health) want universal care
        "is_tiv": 0.5,                # Tiv: underserved area
        "is_kanuri": 0.5,             # Kanuri: health infrastructure poor
        "lga_Conflict History": 0.3 / 5.0,   # Conflict zones → demand universal healthcare
        "is_rural_bottom_income": 1.0,  # Rural poor: desperate for healthcare access
        "lga_Access Water Pct": -0.005, # Poor water access → demand universal healthcare
        "lga_Median Age Estimate": 0.02,  # Older population → healthcare more urgent
        "lga_Out of School Children Pct": 0.005,  # Areas with high OSC → systemic deprivation → demand universal care
        "lga_Fertility Rate Est": 0.15,  # High fertility → maternal health demand
        "lga_Gini Proxy": 1.0,  # High inequality → health disparities → demand universal provision
        "lga_Biological Enhancement Pct": 0.003,  # Bio-enhancement infrastructure → health tech awareness
        "is_muslim_tertiary": 0.5,        # Educated Muslims: want modern healthcare (Islamic + Western)
        "is_christian_rural": 1.0,       # Rural Christians: mission hospital tradition, want universal care
        "is_hf_bottom_income": 1.0,      # Poor northerners: most healthcare-deprived, strongly pro-universal
        "is_pentecostal_formal": -0.5,   # Pentecostal formal: faith-healing tradition, less state healthcare
        "is_catholic": 0.5,              # Catholics: social doctrine, pro-universal healthcare
        "is_catholic_smallholder": 0.8,  # Catholic smallholders: underserved, strongly pro-universal care
        "is_young_adult": 0.5,  # 25-34: family formation → maternal/child health demand
        "is_igbo_female": 0.5,  # Igbo women: maternal health advocates
    },
    # 26. Padà Status (anti-Padà ↔ Padà preservation)
    {
        "intercept": -1.0,
        "is_pada": 5.0, "is_hausa_fulani": -2.5, "is_bottom_income": -1.5,
        "is_civil_servant": 0.5, "is_naijin": 1.0,
        "is_kanuri": -1.5,            # Kanuri suspicious of Padà influence
        "is_igbo": 0.5,               # Igbo moderate pro-Padà (commercial allies)
        "is_yoruba": 0.5,             # Yoruba tolerant of Padà presence
        "is_tiv": -0.5,              # Tiv mild suspicion
        "is_edo": 0.5,                # Edo: cosmopolitan, tolerant
        "is_tertiary": 0.5,           # Educated: more accepting of Padà
        "is_youth": 0.3,              # Youth: less anti-Padà prejudice
        "is_urban": 0.3,              # Urban: exposed to Padà, cosmopolitan
        "is_rural": -0.3,             # Rural: more traditional, suspicious
        "is_muslim": -0.5,            # Muslim: theological objections to enhancement
        "is_pentecostal": -0.8,       # Pentecostal: "playing God" objection
        "is_traditional": -1.0,       # Traditionalists: deepest anti-Padà sentiment
        "is_formal_sector": 0.3,      # Formal sector: work alongside Padà
        "is_middle_age": -0.2,        # Middle-aged: mild anxiety about Padà
        "lga_Biological Enhancement Pct": 0.01,  # Bio-enhancement linked to Padà identity
        "lga_BIC Effectiveness": 0.15 / 10.0,    # Effective BIC → Padà more accepted
        "lga_Internet Access Pct": 0.003,         # Connected areas: more Padà discourse
        "lga_Urban Pct": 0.005,                   # Urban areas: Padà communities concentrate
    },
    # 27. Energy Policy (fossil status quo ↔ green transition)
    {
        "intercept": 0.5,
        "is_formal_sector": -2.0,
        "is_rural": 2.0, "lga_Access Electricity Pct": -0.05 / 100.0,
        "is_tertiary": 1.0, "is_top_income": -1.0,
        "lga_Pct Livelihood Extraction": -0.03,  # Extraction-dependent LGAs → resist green transition
        "lga_Extraction Intensity": -0.3 / 5.0,  # Extraction zones → fossil status quo
        "lga_GDP Per Capita Est": 0.3 / 90000.0,  # Wealthier LGAs → can afford green transition
        "is_ijaw": -0.5,              # Ijaw: complex — want transition but depend on oil
        "is_nd_minority": -0.5,       # Niger Delta: oil-dependent economies
        "is_tertiary_youth": 1.0,     # Educated youth pro-green
        "is_urban_youth": 0.5,        # Urban youth lean green
        "lga_Refinery Zone": -0.5,    # Refinery zones: fossil economy entrenched
        "lga_Refinery Present": -0.3,  # Refinery present: local jobs depend on fossil
        "lga_Cobalt Extraction Active": 0.5,  # Cobalt: battery tech → green transition aligned
        "lga_Pct Livelihood Manufacturing": 0.005,  # Manufacturing → demand reliable power → pragmatic green
        "lga_Oil Extraction Active": -0.5,  # Active oil → fossil dependency → resist green transition
        "is_edo": 0.5,                # Edo: oil zone but environmentally conscious
        "lga_Internet Access Pct": 0.005,  # Internet: exposure to global green movement → pro-transition
    },
    # 28. AZ Restructuring (return to 36+ states ↔ keep 8 AZs)
    {
        "intercept": 0.0,
        "is_yoruba": -2.0, "is_hausa_fulani": -1.0, "is_minority": -2.5,
        "is_pada": 3.0, "lga_Trad Authority Index": -0.3 / 5.0,
        "is_tiv": -2.0,              # Tiv strongly want Middle Belt state
        "is_mb_minority": -2.0,      # Middle Belt minorities want own states
        "is_nd_minority": -1.5,      # Niger Delta minorities want own states
        "is_igbo": -1.0,             # Igbo want Biafra-adjacent structures
        "is_kanuri": 1.5,            # Kanuri prefer current AZ (Borno dominance)
        "is_nupe": -1.0,             # Nupe want distinct identity from HF hegemony
        "is_edo": -1.0,              # Edo want Mid-West recognition
        "is_edo_christian": -1.5,     # Edo Christians: strongest Mid-West identity, want own AZ
        "is_mb_minority_christian": -2.0,  # MB Christian minorities: strongly want Middle Belt state(s)
        "lga_Conflict History": -0.3 / 5.0,  # Conflict areas want restructuring / more states
        "lga_Extraction Intensity": -0.2 / 5.0,  # Extraction areas want own AZ (resource control)
        "lga_Traditional Authority": 0.5,  # Active traditional authority → resist restructuring (lose power)
        "is_igbo_pentecostal": -1.5,  # Igbo Pentecostals: strongly pro-restructuring (Biafra sentiment)
        "is_yoruba_muslim": 0.5,      # Yoruba Muslims: less anti-AZ than Yoruba Christians
        "is_ibibio": -1.5,            # Ibibio: want Akwa Ibom/Cross River recognition
        "is_ijaw": -1.0,             # Ijaw: want own Niger Delta state/AZ
        "is_hf_muslim_civil_servant": 0.8,  # HF Muslim civil servants: benefit from current AZ structure
        "is_minority_urban_youth": -2.0,  # Minority urban youth: strongly pro-restructuring
        "is_ijaw_christian_unemployed": -1.5,  # Ijaw Christian unemployed: want Delta restructuring
        "lga_Colonial Eastern": -0.5,  # Eastern Region: Biafra legacy → want restructuring
        "lga_Colonial Mid-Western": -0.8,  # Mid-Western: created in 1963 split → identity tied to restructuring
        "lga_Colonial Western": -0.3,  # Western Region: Yoruba want own state recognition
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


def _build_voter_feature_matrix(voter_types: list[VoterType],
                                coeff_table: list[dict]) -> tuple[list[str], np.ndarray]:
    """
    Build (N_types, N_features) boolean matrix for all voter-level features
    used in the coefficient table.  Uses _build_type_indices() for O(1) lookup
    instead of per-type getattr (174k × 130 calls → eliminated).

    Returns (feature_names, feature_matrix) where feature_matrix is float32.
    """
    # Collect unique voter-level feature names from all issues
    feat_set: set[str] = set()
    for coeffs in coeff_table:
        for feat in coeffs:
            if feat != "intercept" and not feat.startswith("lga_"):
                feat_set.add(feat)
    feature_names = sorted(feat_set)  # deterministic order

    idx = _build_type_indices()
    N = len(voter_types)
    F = len(feature_names)
    mat = np.zeros((N, F), dtype=np.float32)

    # Precompute index lookups for O(1) category → int mapping
    eth_idx = idx["eth"]  # (N,) int32
    rel_idx = idx["rel"]
    set_idx = idx["set"]
    age_idx = idx["age"]
    edu_idx = idx["edu"]
    gen_idx = idx["gen"]
    liv_idx = idx["liv"]
    inc_idx = idx["inc"]

    # Ethnicity int codes (matching _CORE_ETHNICITIES order)
    _eth_map = {e: j for j, e in enumerate(_CORE_ETHNICITIES)}
    _hausa = _eth_map["Hausa"]
    _fulani = _eth_map["Fulani"]
    _hf_undiff = _eth_map["Hausa-Fulani Undiff"]
    _yoruba = _eth_map["Yoruba"]
    _igbo = _eth_map["Igbo"]
    _ijaw = _eth_map["Ijaw"]
    _kanuri = _eth_map["Kanuri"]
    _tiv = _eth_map["Tiv"]
    _nupe = _eth_map["Nupe"]
    _edo = _eth_map["Edo"]
    _ibibio = _eth_map["Ibibio"]
    _nd_min = _eth_map["Niger Delta Minorities"]
    _mb_min = _eth_map["Middle Belt Minorities"]
    _pada = _eth_map["Pada"]
    _naijin = _eth_map["Naijin"]
    _majority_set = {_hausa, _fulani, _hf_undiff, _yoruba, _igbo}
    _hf_set = [_hausa, _fulani, _hf_undiff]

    # Religion int codes (matching RELIGIONS order)
    _rel_map = {r: j for j, r in enumerate(RELIGIONS)}
    _tijaniyya = _rel_map["Tijaniyya"]
    _qadiriyya = _rel_map["Qadiriyya"]
    _al_shahid = _rel_map["Al-Shahid"]
    _mainstream_sunni = _rel_map["Mainstream Sunni"]
    _pentecostal = _rel_map.get("Pentecostal", -1)
    _catholic = _rel_map.get("Catholic", -1)
    _mainline_prot = _rel_map.get("Mainline Protestant", -1)
    _muslim_codes = {_tijaniyya, _qadiriyya, _al_shahid, _mainstream_sunni}
    _christian_codes = [_pentecostal, _catholic, _mainline_prot]

    # Precompute base boolean arrays for building interaction terms
    _is_muslim = np.isin(rel_idx, list(_muslim_codes))
    _is_christian = np.isin(rel_idx, _christian_codes)
    _is_female = gen_idx == 1
    _is_urban = set_idx == 0
    _is_rural = set_idx == 2
    _is_youth = age_idx == 0
    _is_tertiary = edu_idx == 2
    _is_hf = np.isin(eth_idx, _hf_set)
    _is_bottom = inc_idx == 0
    _is_top = inc_idx == 2

    # Vectorised boolean feature computation
    for fi, feat in enumerate(feature_names):
        if feat == "is_muslim":
            mat[:, fi] = _is_muslim.astype(np.float32)
        elif feat == "is_christian":
            mat[:, fi] = _is_christian.astype(np.float32)
        elif feat == "is_al_shahid":
            mat[:, fi] = (rel_idx == _al_shahid).astype(np.float32)
        elif feat == "is_tijaniyya":
            mat[:, fi] = (rel_idx == _tijaniyya).astype(np.float32)
        elif feat == "is_pentecostal":
            mat[:, fi] = (rel_idx == _pentecostal).astype(np.float32)
        elif feat == "is_tertiary":
            mat[:, fi] = _is_tertiary.astype(np.float32)
        elif feat == "is_urban":
            mat[:, fi] = _is_urban.astype(np.float32)
        elif feat == "is_rural":
            mat[:, fi] = _is_rural.astype(np.float32)
        elif feat == "is_pada":
            mat[:, fi] = (eth_idx == _pada).astype(np.float32)
        elif feat == "is_naijin":
            mat[:, fi] = (eth_idx == _naijin).astype(np.float32)
        elif feat == "is_hausa_fulani":
            mat[:, fi] = _is_hf.astype(np.float32)
        elif feat == "is_yoruba":
            mat[:, fi] = (eth_idx == _yoruba).astype(np.float32)
        elif feat == "is_igbo":
            mat[:, fi] = (eth_idx == _igbo).astype(np.float32)
        elif feat == "is_ijaw":
            mat[:, fi] = (eth_idx == _ijaw).astype(np.float32)
        elif feat == "is_kanuri":
            mat[:, fi] = (eth_idx == _kanuri).astype(np.float32)
        elif feat == "is_tiv":
            mat[:, fi] = (eth_idx == _tiv).astype(np.float32)
        elif feat == "is_nupe":
            mat[:, fi] = (eth_idx == _nupe).astype(np.float32)
        elif feat == "is_edo":
            mat[:, fi] = (eth_idx == _edo).astype(np.float32)
        elif feat == "is_ibibio":
            mat[:, fi] = (eth_idx == _ibibio).astype(np.float32)
        elif feat == "is_nd_minority":
            mat[:, fi] = (eth_idx == _nd_min).astype(np.float32)
        elif feat == "is_mb_minority":
            mat[:, fi] = (eth_idx == _mb_min).astype(np.float32)
        elif feat == "is_female":
            mat[:, fi] = _is_female.astype(np.float32)
        elif feat == "is_youth":
            mat[:, fi] = _is_youth.astype(np.float32)
        elif feat == "is_older":
            mat[:, fi] = (age_idx == 3).astype(np.float32)  # 50+ = index 3
        elif feat == "is_middle_age":
            mat[:, fi] = (age_idx == 2).astype(np.float32)  # 35-49 = index 2
        elif feat == "is_top_income":
            mat[:, fi] = _is_top.astype(np.float32)
        elif feat == "is_bottom_income":
            mat[:, fi] = _is_bottom.astype(np.float32)
        elif feat == "is_middle_income":
            mat[:, fi] = (inc_idx == 1).astype(np.float32)  # Middle 40% = index 1
        elif feat == "is_civil_servant":
            mat[:, fi] = (liv_idx == 4).astype(np.float32)
        elif feat == "is_formal_sector":
            mat[:, fi] = (liv_idx == 3).astype(np.float32)
        elif feat == "is_informal":
            mat[:, fi] = (liv_idx == 2).astype(np.float32)
        elif feat == "is_smallholder":
            mat[:, fi] = (liv_idx == 0).astype(np.float32)
        elif feat == "is_commercial_ag":
            mat[:, fi] = (liv_idx == 1).astype(np.float32)
        elif feat == "is_unemployed":
            mat[:, fi] = (liv_idx == 5).astype(np.float32)
        elif feat == "is_minority":
            mat[:, fi] = (~np.isin(eth_idx, list(_majority_set))).astype(np.float32)
        elif feat == "is_majority":
            mat[:, fi] = np.isin(eth_idx, list(_majority_set)).astype(np.float32)
        # --- Interaction terms ---
        elif feat == "is_muslim_female":
            mat[:, fi] = (_is_muslim & _is_female).astype(np.float32)
        elif feat == "is_urban_youth":
            mat[:, fi] = (_is_urban & _is_youth).astype(np.float32)
        elif feat == "is_rural_muslim":
            mat[:, fi] = (_is_rural & _is_muslim).astype(np.float32)
        elif feat == "is_tertiary_youth":
            mat[:, fi] = (_is_tertiary & _is_youth).astype(np.float32)
        elif feat == "is_hf_bottom_income":
            mat[:, fi] = (_is_hf & _is_bottom).astype(np.float32)
        elif feat == "is_christian_urban":
            mat[:, fi] = (_is_christian & _is_urban).astype(np.float32)
        elif feat == "is_muslim_tertiary":
            mat[:, fi] = (_is_muslim & _is_tertiary).astype(np.float32)
        elif feat == "is_female_tertiary":
            mat[:, fi] = (_is_female & _is_tertiary).astype(np.float32)
        elif feat == "is_youth_unemployed":
            mat[:, fi] = (_is_youth & (liv_idx == 5)).astype(np.float32)
        elif feat == "is_rural_older":
            mat[:, fi] = (_is_rural & (age_idx == 3)).astype(np.float32)
        # --- New cross-pressure interactions ---
        elif feat == "is_yoruba_muslim":
            mat[:, fi] = ((eth_idx == _yoruba) & _is_muslim).astype(np.float32)
        elif feat == "is_igbo_pentecostal":
            mat[:, fi] = ((eth_idx == _igbo) & (rel_idx == _pentecostal)).astype(np.float32)
        elif feat == "is_pada_tertiary":
            mat[:, fi] = ((eth_idx == _pada) & _is_tertiary).astype(np.float32)
        elif feat == "is_rural_bottom_income":
            mat[:, fi] = (_is_rural & _is_bottom).astype(np.float32)
        elif feat == "is_kanuri_rural":
            mat[:, fi] = ((eth_idx == _kanuri) & _is_rural).astype(np.float32)
        # --- Ethnicity-livelihood interactions ---
        elif feat == "is_hf_smallholder":
            mat[:, fi] = (_is_hf & (liv_idx == 0)).astype(np.float32)
        elif feat == "is_yoruba_trader":
            mat[:, fi] = ((eth_idx == _yoruba) & (liv_idx == 2)).astype(np.float32)
        elif feat == "is_igbo_formal":
            mat[:, fi] = ((eth_idx == _igbo) & (liv_idx == 3)).astype(np.float32)
        elif feat == "is_kanuri_unemployed":
            mat[:, fi] = ((eth_idx == _kanuri) & (liv_idx == 5)).astype(np.float32)
        elif feat == "is_ijaw_extraction":
            mat[:, fi] = ((eth_idx == _ijaw) & np.isin(liv_idx, [2, 3])).astype(np.float32)
        # --- Additional cross-pressure terms (batch 7) ---
        elif feat == "is_igbo_bottom_income":
            mat[:, fi] = ((eth_idx == _igbo) & _is_bottom).astype(np.float32)
        elif feat == "is_fulani_smallholder":
            mat[:, fi] = ((eth_idx == _fulani) & (liv_idx == 0)).astype(np.float32)
        elif feat == "is_urban_bottom_income":
            mat[:, fi] = (_is_urban & _is_bottom).astype(np.float32)
        elif feat == "is_christian_rural":
            mat[:, fi] = (_is_christian & _is_rural).astype(np.float32)
        elif feat == "is_yoruba_formal":
            mat[:, fi] = ((eth_idx == _yoruba) & (liv_idx == 3)).astype(np.float32)
        # --- Religion-livelihood interactions (batch 8) ---
        elif feat == "is_muslim_trader":
            mat[:, fi] = (_is_muslim & (liv_idx == 2)).astype(np.float32)
        elif feat == "is_pentecostal_formal":
            mat[:, fi] = ((rel_idx == _pentecostal) & (liv_idx == 3)).astype(np.float32)
        elif feat == "is_catholic_smallholder":
            mat[:, fi] = ((rel_idx == _catholic) & (liv_idx == 0)).astype(np.float32)
        elif feat == "is_muslim_civil_servant":
            mat[:, fi] = (_is_muslim & (liv_idx == 4)).astype(np.float32)
        elif feat == "is_tijaniyya_trader":
            mat[:, fi] = ((rel_idx == _tijaniyya) & (liv_idx == 2)).astype(np.float32)
        # --- Additional religion properties (batch 8) ---
        elif feat == "is_catholic":
            mat[:, fi] = (rel_idx == _catholic).astype(np.float32)
        elif feat == "is_mainline_protestant":
            mat[:, fi] = (rel_idx == _mainline_prot).astype(np.float32)
        # --- Triple interaction terms (batch 11) ---
        elif feat == "is_hf_muslim_civil_servant":
            mat[:, fi] = (_is_hf & _is_muslim & (liv_idx == 4)).astype(np.float32)
        elif feat == "is_yoruba_christian_urban":
            mat[:, fi] = ((eth_idx == _yoruba) & _is_christian & _is_urban).astype(np.float32)
        elif feat == "is_igbo_pentecostal_formal":
            mat[:, fi] = ((eth_idx == _igbo) & (rel_idx == _pentecostal) & (liv_idx == 3)).astype(np.float32)
        elif feat == "is_kanuri_muslim_youth":
            mat[:, fi] = ((eth_idx == _kanuri) & _is_muslim & _is_youth).astype(np.float32)
        elif feat == "is_ijaw_christian_unemployed":
            mat[:, fi] = ((eth_idx == _ijaw) & _is_christian & (liv_idx == 5)).astype(np.float32)
        elif feat == "is_hf_rural_older":
            mat[:, fi] = (_is_hf & _is_rural & (age_idx == 3)).astype(np.float32)
        elif feat == "is_yoruba_muslim_trader":
            mat[:, fi] = ((eth_idx == _yoruba) & _is_muslim & (liv_idx == 2)).astype(np.float32)
        elif feat == "is_minority_urban_youth":
            mat[:, fi] = (~np.isin(eth_idx, list(_majority_set)) & _is_urban & _is_youth).astype(np.float32)
        # --- Gender-ethnic and income-education interactions (batch 13) ---
        elif feat == "is_igbo_female":
            mat[:, fi] = ((eth_idx == _igbo) & _is_female).astype(np.float32)
        elif feat == "is_yoruba_female":
            mat[:, fi] = ((eth_idx == _yoruba) & _is_female).astype(np.float32)
        elif feat == "is_tertiary_bottom_income":
            mat[:, fi] = (_is_tertiary & _is_bottom).astype(np.float32)
        elif feat == "is_young_adult":
            mat[:, fi] = (age_idx == 1).astype(np.float32)  # 25-34 = index 1
        elif feat == "is_urban_trader":
            mat[:, fi] = (_is_urban & (liv_idx == 2)).astype(np.float32)
        # --- Batch 20: ethnic-religious and livelihood cross-terms ---
        elif feat == "is_edo_christian":
            mat[:, fi] = ((eth_idx == _edo) & _is_christian).astype(np.float32)
        elif feat == "is_mb_minority_christian":
            mat[:, fi] = ((eth_idx == _mb_min) & _is_christian).astype(np.float32)
        elif feat == "is_nupe_muslim":
            mat[:, fi] = ((eth_idx == _nupe) & _is_muslim).astype(np.float32)
        elif feat == "is_igbo_trader":
            mat[:, fi] = ((eth_idx == _igbo) & (liv_idx == 2)).astype(np.float32)
        elif feat == "is_fulani_rural":
            mat[:, fi] = ((eth_idx == _fulani) & _is_rural).astype(np.float32)
        else:
            # Fallback for any unknown feature — use getattr (shouldn't happen
            # for the default table, but supports custom coefficient tables)
            mat[:, fi] = np.array(
                [float(bool(getattr(vt, feat, None))) for vt in voter_types],
                dtype=np.float32,
            )

    return feature_names, mat


def build_voter_ideal_base(
    voter_types: list[VoterType],
    coeff_table: list[dict] | None = None,
) -> np.ndarray:
    """
    Precompute the voter-type-specific (non-LGA) ideal point contributions.

    Returns (N_types, N_ISSUES) array where result[i, d] = intercept_d +
    sum of all voter-level feature coefficients for type i on issue d.
    LGA-specific (lga_*) features are excluded — add compute_lga_ideal_offset()
    per LGA to obtain the full pre-clamp ideal point matrix.

    This is computed once per simulation run; the result is the same for all LGAs.

    Uses vectorised numpy operations via _build_voter_feature_matrix() to avoid
    the 174k × 130 getattr calls of the naive loop (4.1s → ~0.05s).
    """
    if coeff_table is None:
        coeff_table = _IDEAL_POINT_COEFFICIENTS
    D = len(coeff_table)

    # Build (N_types, N_features) boolean matrix and feature name list
    feature_names, feat_matrix = _build_voter_feature_matrix(voter_types, coeff_table)
    N = feat_matrix.shape[0]
    F = len(feature_names)
    feat_name_to_idx = {name: i for i, name in enumerate(feature_names)}

    # Build (D, F) coefficient matrix and (D,) intercept vector
    intercepts = np.zeros(D, dtype=np.float32)
    coeff_matrix = np.zeros((D, F), dtype=np.float32)

    for d, coeffs in enumerate(coeff_table):
        intercepts[d] = coeffs.get("intercept", 0.0)
        for feat, coeff in coeffs.items():
            if feat == "intercept" or feat.startswith("lga_"):
                continue
            fi = feat_name_to_idx.get(feat)
            if fi is not None:
                coeff_matrix[d, fi] = coeff

    # Matrix multiply: (N, F) @ (F, D) → (N, D), then add intercepts
    base = feat_matrix @ coeff_matrix.T  # (N, D) float32
    base += intercepts                    # broadcast (D,) over rows

    return base.astype(np.float64)


def compute_lga_ideal_offset(
    lga_row: pd.Series,
    coeff_table: list[dict] | None = None,
) -> np.ndarray:
    """
    Compute the LGA-specific ideal point offset (lga_* features only).

    Returns (N_ISSUES,) array.  The full clipped ideal point matrix for a
    given LGA is: np.clip(voter_base + compute_lga_ideal_offset(lga_row), -5, 5)
    where voter_base is the result of build_voter_ideal_base().
    """
    if coeff_table is None:
        coeff_table = _IDEAL_POINT_COEFFICIENTS
    D = len(coeff_table)
    offset = np.zeros(D)
    for d, coeffs in enumerate(coeff_table):
        for feat, coeff in coeffs.items():
            if feat.startswith("lga_"):
                offset[d] += coeff * float(lga_row.get(feat[4:], 0.0))
    return offset


def compute_all_lga_ideal_offsets(
    lga_data: pd.DataFrame,
    coeff_table: list[dict] | None = None,
) -> np.ndarray:
    """
    Compute LGA ideal point offsets for all LGAs at once.

    Returns (N_lga, N_ISSUES) array. Each row is the lga_* feature
    contribution to ideal points for that LGA. Vectorised over LGAs
    by extracting columns as numpy arrays and doing matrix multiplication.
    """
    if coeff_table is None:
        coeff_table = _IDEAL_POINT_COEFFICIENTS
    D = len(coeff_table)
    N = len(lga_data)

    # Collect all unique lga_* features and their (issue_index, coefficient) pairs
    lga_features: dict[str, list[tuple[int, float]]] = {}
    for d, coeffs in enumerate(coeff_table):
        for feat, coeff in coeffs.items():
            if feat.startswith("lga_"):
                col_name = feat[4:]
                if col_name not in lga_features:
                    lga_features[col_name] = []
                lga_features[col_name].append((d, coeff))

    offsets = np.zeros((N, D))
    for col_name, pairs in lga_features.items():
        if col_name in lga_data.columns:
            col_vals = lga_data[col_name].fillna(0.0).values.astype(float)  # (N,)
        else:
            continue
        for d, coeff in pairs:
            offsets[:, d] += coeff * col_vals

    return offsets
