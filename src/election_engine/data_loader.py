"""
Data loader for the LAGOS-2058 election engine.

Loads the LGA_DATA sheet from nigeria_lga_polsim_2058.xlsx and provides
validated access to column groups used by downstream modules.

Column index reference (0-based, after reading header row 1):
  0–3    IDENTIFICATION:    State, LGA Name, Colonial Era Region, Terrain Type
  4–5    ADMINISTRATIVE:    Administrative Zone, AZ Name
  6–11   DEMOGRAPHIC:       Population, Density, Median Age, %Under30, Fertility, BioEnhance
  12–97  ETHNOLINGUISTIC:   86 ethnic group percentages (% Hausa … % Other)
  98–107 RELIGIOUS:         %Muslim, %Christian, %Traditionalist, Tijaniyya, Qadiriyya,
                            Pentecostal Growth, Traditionalist Practice, Al-Shahid Influence,
                            Almajiri Index, Religious Notes
  108–109 URBANIZATION:     Major Urban Center, Urban Pct
  110–131 ECONOMIC:         Oil Producing through Housing Affordability (22 cols)
  132–138 INFRASTRUCTURE:   Electricity/Water/Healthcare access, Road Quality, Notes,
                            Market Access, Notes
  139–147 EDUCATION:        Literacy (total/male/female), Enrollment (primary/secondary),
                            GPI, Out-of-School, Num Secondary Schools, Tertiary
  148–155 POLITICAL:        Traditional Authority (flag/index/notes), Land Formalization,
                            Notes, Conflict History, Federal Control, BIC Effectiveness
  156–157 CONNECTIVITY:     Mobile Phone Penetration, Internet Access
  158–161 CULTURAL:         English Prestige, Mandarin Presence, Arabic Prestige, Data Notes
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column name constants — match the actual header row in the spreadsheet
# ---------------------------------------------------------------------------

# Identification
COL_STATE = "State"
COL_LGA = "LGA Name"
COL_COLONIAL_REGION = "Colonial Era Region"
COL_TERRAIN = "Terrain Type"

# Administrative
COL_AZ = "Administrative Zone"
COL_AZ_NAME = "AZ Name"

# Demographic
COL_POPULATION = "Estimated Population"
COL_DENSITY = "Population Density per km2"
COL_MEDIAN_AGE = "Median Age Estimate"
COL_PCT_UNDER30 = "% Population Under 30"
COL_FERTILITY = "Fertility Rate Est"
COL_BIO_ENHANCE = "Biological Enhancement Pct"

# Religious
COL_PCT_MUSLIM = "% Muslim"
COL_PCT_CHRISTIAN = "% Christian"
COL_PCT_TRADITIONALIST = "% Traditionalist"
COL_TIJANIYYA = "Tijaniyya Presence"
COL_QADIRIYYA = "Qadiriyya Presence"
COL_PENTECOSTAL = "Pentecostal Growth"
COL_TRAD_PRACTICE = "Traditionalist Practice"
COL_AL_SHAHID = "Al-Shahid Influence"
COL_ALMAJIRI = "Almajiri Index"

# Urbanization
COL_URBAN_CENTER = "Major Urban Center"
COL_URBAN_PCT = "Urban Pct"

# Economic
COL_OIL_PRODUCING = "Oil Producing"
COL_LIVELIHOOD_AGRIC = "Pct Livelihood Agriculture"
COL_LIVELIHOOD_MANUF = "Pct Livelihood Manufacturing"
COL_LIVELIHOOD_EXTRACT = "Pct Livelihood Extraction"
COL_LIVELIHOOD_SERVICES = "Pct Livelihood Services"
COL_LIVELIHOOD_INFORMAL = "Pct Livelihood Informal"
COL_OIL_ACTIVE = "Oil Extraction Active"
COL_COBALT_ACTIVE = "Cobalt Extraction Active"
COL_MINING_ACTIVE = "Other Mining Active"
COL_REFINERY = "Refinery Present"
COL_EXTRACT_INTENSITY = "Extraction Intensity"
COL_POVERTY = "Poverty Rate Pct"
COL_UNEMPLOYMENT = "Unemployment Rate Pct"
COL_YOUTH_UNEMP = "Youth Unemployment Rate Pct"
COL_GDP = "GDP Per Capita Est"
COL_GINI = "Gini Proxy"
COL_CHINESE = "Chinese Economic Presence"
COL_RAIL = "Rail Corridor"
COL_PLANNED_CITY = "Planned City"
COL_REFINERY_ZONE = "Refinery Zone"
COL_HOUSING_AFFORD = "Housing Affordability"

# Infrastructure
COL_ELEC_ACCESS = "Access Electricity Pct"
COL_WATER_ACCESS = "Access Water Pct"
COL_HEALTH_ACCESS = "Access Healthcare Pct"
COL_ROAD_QUALITY = "Road Quality Index"
COL_MARKET_ACCESS = "Market Access Index"

# Education
COL_LITERACY = "Adult Literacy Rate Pct"
COL_MALE_LITERACY = "Male Literacy Rate Pct"
COL_FEMALE_LITERACY = "Female Literacy Rate Pct"
COL_PRIMARY_ENROLL = "Primary Enrollment Pct"
COL_SECONDARY_ENROLL = "Secondary Enrollment Pct"
COL_GPI = "Gender Parity Index"
COL_OUT_OF_SCHOOL = "Out of School Children Pct"
COL_NUM_SECONDARY = "Num Secondary Schools"
COL_TERTIARY = "Tertiary Institution"

# Political structure
COL_TRAD_AUTHORITY = "Traditional Authority"
COL_TRAD_AUTH_INDEX = "Trad Authority Index"
COL_LAND_FORMAL = "Land Formalization Pct"
COL_CONFLICT = "Conflict History"
COL_FED_CONTROL = "Federal Control 2058"
COL_BIC_EFF = "BIC Effectiveness"

# Connectivity
COL_MOBILE = "Mobile Phone Penetration Pct"
COL_INTERNET = "Internet Access Pct"

# Cultural
COL_ENGLISH_PRESTIGE = "English Prestige"
COL_MANDARIN = "Mandarin Presence"
COL_ARABIC_PRESTIGE = "Arabic Prestige"

# Ethnic columns span indices 12–97 (86 columns)
ETHNIC_COL_FIRST = "% Hausa"
ETHNIC_COL_LAST = "% Other"

_EXPECTED_ROWS = 774


class LGAData:
    """
    Validated container for LGA-level data from the polsim spreadsheet.

    Attributes
    ----------
    df : pd.DataFrame
        Full cleaned dataframe (774 rows × 162 columns).
    metadata : pd.DataFrame
        METADATA sheet (column descriptions).
    """

    def __init__(self, df: pd.DataFrame, metadata: pd.DataFrame) -> None:
        self.df = df
        self.metadata = metadata

    # ------------------------------------------------------------------
    # Column group accessors
    # ------------------------------------------------------------------

    def get_ethnic_columns(self) -> list[str]:
        """Return column names for the 86 ethnic group percentages (% Hausa … % Other)."""
        cols = list(self.df.columns)
        start = cols.index(ETHNIC_COL_FIRST)
        end = cols.index(ETHNIC_COL_LAST) + 1
        return cols[start:end]

    def get_religious_columns(self) -> list[str]:
        """Return column names for religious data (percentages + ordinal indicators)."""
        return [
            COL_PCT_MUSLIM,
            COL_PCT_CHRISTIAN,
            COL_PCT_TRADITIONALIST,
            COL_TIJANIYYA,
            COL_QADIRIYYA,
            COL_PENTECOSTAL,
            COL_TRAD_PRACTICE,
            COL_AL_SHAHID,
            COL_ALMAJIRI,
        ]

    def get_economic_columns(self) -> list[str]:
        """Return column names for economic indicators."""
        return [
            COL_OIL_PRODUCING,
            COL_LIVELIHOOD_AGRIC,
            COL_LIVELIHOOD_MANUF,
            COL_LIVELIHOOD_EXTRACT,
            COL_LIVELIHOOD_SERVICES,
            COL_LIVELIHOOD_INFORMAL,
            COL_OIL_ACTIVE,
            COL_COBALT_ACTIVE,
            COL_MINING_ACTIVE,
            COL_REFINERY,
            COL_EXTRACT_INTENSITY,
            COL_POVERTY,
            COL_UNEMPLOYMENT,
            COL_YOUTH_UNEMP,
            COL_GDP,
            COL_GINI,
            COL_CHINESE,
            COL_RAIL,
            COL_PLANNED_CITY,
            COL_REFINERY_ZONE,
            COL_HOUSING_AFFORD,
        ]

    def get_infrastructure_columns(self) -> list[str]:
        """Return column names for infrastructure indicators."""
        return [
            COL_ELEC_ACCESS,
            COL_WATER_ACCESS,
            COL_HEALTH_ACCESS,
            COL_ROAD_QUALITY,
            COL_MARKET_ACCESS,
        ]

    def get_education_columns(self) -> list[str]:
        """Return column names for education indicators."""
        return [
            COL_LITERACY,
            COL_MALE_LITERACY,
            COL_FEMALE_LITERACY,
            COL_PRIMARY_ENROLL,
            COL_SECONDARY_ENROLL,
            COL_GPI,
            COL_OUT_OF_SCHOOL,
            COL_NUM_SECONDARY,
            COL_TERTIARY,
        ]

    def get_demographic_columns(self) -> list[str]:
        """Return column names for demographic indicators."""
        return [
            COL_POPULATION,
            COL_DENSITY,
            COL_MEDIAN_AGE,
            COL_PCT_UNDER30,
            COL_FERTILITY,
            COL_BIO_ENHANCE,
        ]

    def get_connectivity_columns(self) -> list[str]:
        """Return column names for connectivity indicators."""
        return [COL_MOBILE, COL_INTERNET]

    def get_cultural_columns(self) -> list[str]:
        """Return column names for cultural indicators."""
        return [COL_ENGLISH_PRESTIGE, COL_MANDARIN, COL_ARABIC_PRESTIGE]

    def get_lga_row(self, state: str, lga_name: str) -> pd.Series:
        """Return the row for a specific LGA by state and LGA name."""
        mask = (self.df[COL_STATE] == state) & (self.df[COL_LGA] == lga_name)
        rows = self.df[mask]
        if len(rows) == 0:
            raise KeyError(f"LGA not found: state={state!r}, lga={lga_name!r}")
        if len(rows) > 1:
            logger.warning("Multiple rows matched for %s / %s; using first", state, lga_name)
        return rows.iloc[0]

    def get_identifier(self, idx: int) -> tuple[str, str, int, str]:
        """Return (state, lga_name, admin_zone, az_name) for the given row index."""
        row = self.df.iloc[idx]
        return (
            str(row[COL_STATE]),
            str(row[COL_LGA]),
            int(row[COL_AZ]),
            str(row[COL_AZ_NAME]),
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill NaN values with sensible defaults column-by-column."""
    cols = list(df.columns)

    # Percentage columns → 0
    pct_cols = [c for c in cols if c.startswith("%") or "Pct" in c or "Rate" in c]
    for col in pct_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Ordinal indicators (0–5 scale) → 0
    ordinal_cols = [
        COL_TIJANIYYA, COL_QADIRIYYA, COL_PENTECOSTAL, COL_AL_SHAHID,
        COL_TRAD_PRACTICE, COL_ALMAJIRI, COL_TRAD_AUTH_INDEX,
        COL_CONFLICT, COL_BIC_EFF, COL_CHINESE,
        COL_ROAD_QUALITY, COL_MARKET_ACCESS, COL_HOUSING_AFFORD,
        COL_EXTRACT_INTENSITY,
    ]
    for col in ordinal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Binary flags → 0
    binary_cols = [
        COL_OIL_PRODUCING, COL_OIL_ACTIVE, COL_COBALT_ACTIVE,
        COL_MINING_ACTIVE, COL_REFINERY, COL_RAIL, COL_PLANNED_CITY,
        COL_REFINERY_ZONE, COL_URBAN_CENTER, COL_FED_CONTROL,
        COL_TERTIARY, COL_TRAD_AUTHORITY,
    ]
    for col in binary_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Continuous / index columns → fill with column median
    continuous_cols = [
        COL_POPULATION, COL_DENSITY, COL_MEDIAN_AGE, COL_FERTILITY,
        COL_GDP, COL_GINI, COL_GPI, COL_LAND_FORMAL,
        COL_MOBILE, COL_INTERNET,
        COL_ENGLISH_PRESTIGE, COL_MANDARIN, COL_ARABIC_PRESTIGE,
        COL_ELEC_ACCESS, COL_WATER_ACCESS, COL_HEALTH_ACCESS,
        COL_LITERACY, COL_MALE_LITERACY, COL_FEMALE_LITERACY,
        COL_PRIMARY_ENROLL, COL_SECONDARY_ENROLL,
        COL_NUM_SECONDARY, COL_UNEMPLOYMENT, COL_YOUTH_UNEMP,
        COL_POVERTY, COL_URBAN_PCT, COL_BIO_ENHANCE,
    ]
    for col in continuous_cols:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce")
            df[col] = series.fillna(series.median())

    # Any remaining numeric NaN → 0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0.0)

    return df


def _validate(df: pd.DataFrame, path: Path) -> None:
    """Raise ValueError if the dataframe fails basic validation checks."""
    if len(df) != _EXPECTED_ROWS:
        raise ValueError(
            f"Expected {_EXPECTED_ROWS} LGA rows in {path}, got {len(df)}"
        )

    required = [COL_STATE, COL_LGA, COL_AZ, ETHNIC_COL_FIRST, ETHNIC_COL_LAST,
                COL_PCT_MUSLIM, COL_URBAN_PCT, COL_GDP, COL_ELEC_ACCESS, COL_BIC_EFF]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {path}: {missing}")

    # Administrative zones should be 1–8
    az_vals = df[COL_AZ].dropna().unique()
    if not set(az_vals).issubset(set(range(1, 9))):
        logger.warning("Unexpected Administrative Zone values: %s", sorted(az_vals))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_lga_data_cache: dict[str, LGAData] = {}


def load_lga_data(path: str | Path) -> LGAData:
    """
    Load and validate the LGA_DATA sheet from the polsim Excel file.

    Results are cached by resolved path so repeated calls (e.g., across
    campaign turns) return a deep copy without re-reading the xlsx.

    Parameters
    ----------
    path : str | Path
        Path to the xlsx file.

    Returns
    -------
    LGAData
        Validated, cleaned container with accessor methods.
    """
    import copy

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    cache_key = str(path.resolve())
    if cache_key in _lga_data_cache:
        logger.info("Using cached LGA data for %s", path)
        cached = _lga_data_cache[cache_key]
        return LGAData(df=cached.df.copy(), metadata=cached.metadata.copy())

    logger.info("Loading LGA data from %s", path)

    # Row 0 in the sheet = group header (IDENTIFICATION, DEMOGRAPHIC, …)
    # Row 1 = actual column names  →  header=1
    df = pd.read_excel(path, sheet_name="LGA_DATA", header=1, engine="openpyxl")
    df = df.reset_index(drop=True)

    # Load metadata sheet (may have different structure — just read as-is)
    try:
        metadata = pd.read_excel(path, sheet_name="METADATA", engine="openpyxl")
    except Exception:
        metadata = pd.DataFrame()
        logger.warning("Could not load METADATA sheet from %s", path)

    _validate(df, path)
    df = _fill_missing(df)

    logger.info("Loaded %d LGA rows, %d columns", len(df), len(df.columns))
    result = LGAData(df=df, metadata=metadata)
    _lga_data_cache[cache_key] = result
    return LGAData(df=df.copy(), metadata=metadata.copy())
