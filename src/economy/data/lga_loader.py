"""
Economy-specific LGA data loader.

Reads the LGA database (via the election engine's data_loader) and extracts
arrays needed by the economic simulator: production capacities, labor pools,
infrastructure quality, administrative zone mapping, geographic coordinates, etc.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.election_engine.data_loader import (
    LGAData,
    load_lga_data,
    COL_STATE,
    COL_LGA,
    COL_AZ,
    COL_POPULATION,
    COL_FERTILITY,
    COL_BIO_ENHANCE,
    COL_URBAN_PCT,
    COL_OIL_ACTIVE,
    COL_COBALT_ACTIVE,
    COL_MINING_ACTIVE,
    COL_REFINERY,
    COL_LIVELIHOOD_AGRIC,
    COL_LIVELIHOOD_MANUF,
    COL_LIVELIHOOD_EXTRACT,
    COL_LIVELIHOOD_SERVICES,
    COL_LIVELIHOOD_INFORMAL,
    COL_POVERTY,
    COL_UNEMPLOYMENT,
    COL_GDP,
    COL_CHINESE,
    COL_RAIL,
    COL_HOUSING_AFFORD,
    COL_ELEC_ACCESS,
    COL_ROAD_QUALITY,
    COL_MARKET_ACCESS,
    COL_LITERACY,
    COL_AL_SHAHID,
    COL_ALMAJIRI,
    COL_TERRAIN,
)

logger = logging.getLogger(__name__)

# States in the Sahel band (desertification-prone)
SAHEL_STATES = {"Borno", "Yobe", "Jigawa", "Katsina", "Sokoto", "Zamfara", "Kebbi"}

# States considered "southern" for economic purposes
SOUTHERN_STATES = {
    "Lagos", "Ogun", "Oyo", "Osun", "Ondo", "Ekiti",           # Southwest
    "Edo", "Delta", "Bayelsa", "Rivers", "Cross River", "Akwa Ibom",  # South-South
    "Abia", "Anambra", "Enugu", "Ebonyi", "Imo",                # Southeast
}

# Niger Delta oil-producing states
NIGER_DELTA_STATES = {"Delta", "Rivers", "Bayelsa", "Akwa Ibom", "Edo", "Ondo", "Imo", "Abia"}

# States with significant agricultural output
NORTHERN_AGRIC_STATES = {
    "Kano", "Kaduna", "Katsina", "Jigawa", "Kebbi", "Sokoto",
    "Zamfara", "Niger", "Benue", "Plateau", "Nasarawa", "Taraba",
    "Adamawa", "Bauchi", "Gombe", "Borno", "Yobe",
}


class EconomyLGAData:
    """Extracted economic data arrays indexed by LGA ID (0-773)."""

    def __init__(self, lga_data: LGAData) -> None:
        df = lga_data.df
        n = len(df)
        assert n == 774, f"Expected 774 LGAs, got {n}"

        self.n_lgas = n
        self.states: list[str] = df[COL_STATE].tolist()
        self.lga_names: list[str] = df[COL_LGA].tolist()
        self.admin_zones: np.ndarray = _safe_int(df[COL_AZ].values)  # 1-8

        # Demographics
        self.population: np.ndarray = _safe_float(df[COL_POPULATION].values)
        self.fertility: np.ndarray = _safe_float(df[COL_FERTILITY].values)
        self.urban_pct: np.ndarray = _safe_float(df[COL_URBAN_PCT].values) / 100.0
        self.bio_enhance_pct: np.ndarray = _safe_float(df[COL_BIO_ENHANCE].values) / 100.0

        # Economic structure (livelihoods as fractions)
        self.pct_agric: np.ndarray = _safe_float(df[COL_LIVELIHOOD_AGRIC].values) / 100.0
        self.pct_manuf: np.ndarray = _safe_float(df[COL_LIVELIHOOD_MANUF].values) / 100.0
        self.pct_extract: np.ndarray = _safe_float(df[COL_LIVELIHOOD_EXTRACT].values) / 100.0
        self.pct_services: np.ndarray = _safe_float(df[COL_LIVELIHOOD_SERVICES].values) / 100.0
        self.pct_informal: np.ndarray = _safe_float(df[COL_LIVELIHOOD_INFORMAL].values) / 100.0

        # Extractive flags
        self.oil_active: np.ndarray = _safe_float(df[COL_OIL_ACTIVE].values)
        self.cobalt_active: np.ndarray = _safe_float(df[COL_COBALT_ACTIVE].values)
        self.mining_active: np.ndarray = _safe_float(df[COL_MINING_ACTIVE].values)
        self.refinery_present: np.ndarray = _safe_float(df[COL_REFINERY].values)
        self.rail_corridor: np.ndarray = _safe_float(df[COL_RAIL].values)

        # Welfare / income
        self.poverty_rate: np.ndarray = _safe_float(df[COL_POVERTY].values) / 100.0
        self.unemployment_rate: np.ndarray = _safe_float(df[COL_UNEMPLOYMENT].values) / 100.0
        self.gdp_per_capita: np.ndarray = _safe_float(df[COL_GDP].values)
        self.housing_afford: np.ndarray = _safe_float(df[COL_HOUSING_AFFORD].values)

        # Infrastructure (0-1 scale)
        self.elec_access: np.ndarray = _safe_float(df[COL_ELEC_ACCESS].values) / 100.0
        road_raw = _safe_float(df[COL_ROAD_QUALITY].values)
        self.road_quality: np.ndarray = road_raw / max(road_raw.max(), 1.0)
        market_raw = _safe_float(df[COL_MARKET_ACCESS].values)
        self.market_access: np.ndarray = market_raw / max(market_raw.max(), 1.0)

        # Education / skill proxy
        self.literacy: np.ndarray = _safe_float(df[COL_LITERACY].values) / 100.0

        # Chinese economic presence
        self.chinese_presence: np.ndarray = _safe_float(df[COL_CHINESE].values)

        # Al-Shahid / insurgency
        self.alsahid_influence: np.ndarray = _safe_float(df[COL_AL_SHAHID].values)
        self.almajiri_index: np.ndarray = _safe_float(df[COL_ALMAJIRI].values)

        # Terrain
        self.terrain: list[str] = df[COL_TERRAIN].fillna("").tolist()

        # Derived boolean masks
        self.is_southern: np.ndarray = np.array(
            [s in SOUTHERN_STATES for s in self.states], dtype=bool,
        )
        self.is_sahel: np.ndarray = np.array(
            [s in SAHEL_STATES for s in self.states], dtype=bool,
        )
        self.is_niger_delta: np.ndarray = np.array(
            [s in NIGER_DELTA_STATES for s in self.states], dtype=bool,
        )

        logger.info(
            "EconomyLGAData: %d LGAs, pop=%.0fM, %d southern, %d sahel, %d niger-delta",
            n,
            self.population.sum() / 1e6,
            self.is_southern.sum(),
            self.is_sahel.sum(),
            self.is_niger_delta.sum(),
        )


def load_economy_lga_data(
    path: Optional[str | Path] = None,
) -> EconomyLGAData:
    """Load and return economy-specific LGA data arrays."""
    if path is None:
        path = Path(__file__).resolve().parents[3] / "data" / "nigeria_lga_polsim_2058.xlsx"
    lga_data = load_lga_data(path)
    return EconomyLGAData(lga_data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(arr) -> np.ndarray:
    """Convert to float64, coercing errors to 0."""
    return pd.to_numeric(pd.Series(arr), errors="coerce").fillna(0.0).values.astype(np.float64)


def _safe_int(arr) -> np.ndarray:
    """Convert to int32, coercing errors to 0."""
    return pd.to_numeric(pd.Series(arr), errors="coerce").fillna(0).values.astype(np.int32)
