"""Shared test fixtures for economy tests."""

import pytest
import numpy as np

from src.economy.core.types import SimConfig, EconomicState
from src.economy.core.initialize import initialize_state
from src.economy.data.commodities import BASE_PRICES


@pytest.fixture
def config():
    """Default SimConfig."""
    return SimConfig()


@pytest.fixture
def state(config):
    """Fully initialized EconomicState from LGA data."""
    return initialize_state(config)


def _build_micro_config() -> SimConfig:
    """SimConfig for 5-LGA micro-economy."""
    return SimConfig(
        N_LGAS=5,
        N_ADMIN_ZONES=2,
        N_VOTER_TYPES=5 * 6 * 3 * 4 * 2,  # 720
        N_TRADE_ROUTES=10,
    )


def _build_micro_state(config: SimConfig) -> EconomicState:
    """
    Synthetic 5-LGA EconomicState for fast tests.

    LGAs:
      0: urban southern (Lagos-like)
      1: rural northern (Borno-like)
      2: oil-producing (Rivers-like)
      3: manufacturing (Kano-like)
      4: agricultural (Benue-like)
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES
    S = config.N_SKILL_TIERS
    L = config.N_LAND_TYPES
    Z = config.N_ADMIN_ZONES

    rng = np.random.default_rng(42)
    state = EconomicState(rng=rng)

    # Zone mapping: 0,2 → zone 0 (south), 1,3,4 → zone 1 (north)
    state.admin_zone = np.array([0, 1, 0, 1, 1], dtype=np.int32)

    # Prices: start at base with slight variation
    state.prices = np.tile(BASE_PRICES, (N, 1)).copy()
    state.prices *= 1.0 + rng.uniform(-0.05, 0.05, (N, C))
    state.prices = np.maximum(state.prices, 1.0)

    # Price history
    state.price_history = np.zeros((N, C, config.MARKET_TICKS_PER_MONTH), dtype=np.float64)
    for t in range(config.MARKET_TICKS_PER_MONTH):
        state.price_history[:, :, t] = state.prices

    # Inventories
    state.inventories = np.tile(BASE_PRICES * 100, (N, 1)).copy()
    state.inventories *= rng.uniform(0.5, 1.5, (N, C))
    state.hoarded = np.zeros((N, C), dtype=np.float64)

    # Production capacity (varies by LGA type)
    state.production_capacity = np.full((N, C), 50.0, dtype=np.float64)
    state.production_capacity[2, 0] = 5000.0   # LGA 2: crude oil
    state.production_capacity[4, 6] = 3000.0   # LGA 4: staple grains
    state.production_capacity[3, 14] = 2000.0  # LGA 3: manufacturing
    state.actual_output = state.production_capacity.copy()
    state.factory_owner = np.zeros((N, C), dtype=np.int8)
    state.factory_owner[0, :] = 1  # Some Chinese presence in Lagos

    # Labor
    populations = np.array([500_000, 100_000, 200_000, 300_000, 150_000], dtype=np.float64)
    state.population = populations
    state.labor_pool = np.column_stack([
        populations * 0.50,  # unskilled
        populations * 0.25,  # skilled
        populations * 0.15,  # highly skilled
        populations * 0.10,  # elite
    ])
    state.labor_employed = state.labor_pool * 0.70
    state.labor_informal = state.labor_pool * 0.20
    state.wages = np.tile(config.BASE_WAGES, (N, 1)).copy()
    state.strikes_active = np.zeros(N, dtype=np.int32)
    state.automation_level = np.full((N, C), 0.05, dtype=np.float64)

    # Land
    state.land_total = np.array([500, 2000, 800, 1000, 3000], dtype=np.float64)
    state.land_area = np.zeros((N, L), dtype=np.float64)
    state.land_area[:, 0] = state.land_total * 0.40  # farmland
    state.land_area[:, 1] = state.land_total * 0.30  # residential
    state.land_area[:, 2] = state.land_total * 0.20  # commercial
    state.land_area[:, 3] = state.land_total * 0.10  # industrial
    state.land_prices = np.full((N, L), 10_000.0, dtype=np.float64)
    state.zoning_restriction = np.full(N, 0.5, dtype=np.float64)

    # Banking
    state.bank_deposits = np.array([1e10, 5e9], dtype=np.float64)
    state.bank_loans = np.array([8e9, 3e9], dtype=np.float64)
    state.bank_bad_loans = np.array([1e8, 5e7], dtype=np.float64)
    state.bank_confidence = np.array([0.80, 0.65], dtype=np.float64)
    state.lending_rate = np.array([0.12, 0.15], dtype=np.float64)

    # Forex
    state.official_exchange_rate = 1500.0
    state.parallel_exchange_rate = 1650.0
    state.forex_reserves_usd = 30e9
    state.global_oil_price_usd = 85.0
    state.global_cobalt_price_usd = 35_000.0

    # Government
    state.budget_allocation = np.full(12, 1e9, dtype=np.float64)
    state.budget_released = np.full(12, 8e8, dtype=np.float64)
    state.corruption_leakage = np.full(12, 0.25, dtype=np.float64)
    state.state_capacity = np.full(12, 0.60, dtype=np.float64)
    state.tax_rate_income = 0.15
    state.tax_rate_corporate = 0.20
    state.tax_rate_vat = 0.075
    state.tax_rate_import_tariff = 0.12
    state.minimum_wage = 50_000.0
    state.bic_enforcement_intensity = 0.50

    # Climate
    state.current_month_of_year = 6
    state.is_rainy_season = True
    state.rainfall_modifier = 1.0
    state.desertification_loss = np.array([0, 0.01, 0, 0, 0.005], dtype=np.float64)

    # Al-Shahid
    state.alsahid_control = np.array([0.0, 0.3, 0.0, 0.05, 0.0], dtype=np.float64)
    state.alsahid_service_provision = np.array([0.0, 0.2, 0.0, 0.02, 0.0], dtype=np.float64)

    # Enhancement
    state.enhancement_adoption = np.array([0.3, 0.05, 0.15, 0.10, 0.08], dtype=np.float64)

    # Infrastructure
    state.infra_road_quality = np.array([0.8, 0.3, 0.6, 0.5, 0.4], dtype=np.float64)
    state.infra_power_reliability = np.array([0.7, 0.2, 0.5, 0.4, 0.3], dtype=np.float64)
    state.infra_telecom_quality = np.array([0.9, 0.3, 0.6, 0.5, 0.3], dtype=np.float64)

    return state


@pytest.fixture
def micro_config():
    """SimConfig for 5-LGA micro-economy."""
    return _build_micro_config()


@pytest.fixture
def micro_state():
    """Synthetic 5-LGA micro-economy for fast unit tests."""
    config = _build_micro_config()
    return _build_micro_state(config)
