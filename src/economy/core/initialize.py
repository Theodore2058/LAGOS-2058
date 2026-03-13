"""
Initialize EconomicState from the LGA database.

Builds all arrays with sensible starting values derived from real LGA data:
production capacities, labor pools, prices, inventories, banking, etc.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np

from src.economy.core.types import EconomicState, SimConfig
from src.economy.data.commodities import COMMODITIES, BASE_PRICES, CommodityTier
from src.economy.data.lga_loader import EconomyLGAData, load_economy_lga_data
from src.economy.data.ministries import MINISTRIES
from src.economy.data.zaibatsu import ZAIBATSU

logger = logging.getLogger(__name__)


def initialize_state(
    config: Optional[SimConfig] = None,
    lga_data: Optional[EconomyLGAData] = None,
    lga_path: Optional[str | Path] = None,
) -> EconomicState:
    """
    Create a fully initialized EconomicState from the LGA database.

    All arrays are set to reasonable starting values. After initialization,
    run burn-in ticks to let prices/trade reach approximate equilibrium.
    """
    if config is None:
        config = SimConfig()
    if lga_data is None:
        lga_data = load_economy_lga_data(lga_path)

    N = config.N_LGAS
    C = config.N_COMMODITIES
    S = config.N_SKILL_TIERS
    L = config.N_LAND_TYPES
    Z = config.N_ADMIN_ZONES

    rng = np.random.default_rng(config.SEED)
    state = EconomicState(rng=rng)

    # --- Prices: start at base prices with small regional variation ---
    state.prices = np.tile(BASE_PRICES, (N, 1)).copy()
    # Add ±10% regional noise
    noise = 1.0 + rng.uniform(-0.10, 0.10, size=(N, C))
    state.prices *= noise
    state.prices = np.maximum(state.prices, 1.0)

    # Price history: fill with current prices (no history yet)
    state.price_history = np.zeros((N, C, config.MARKET_TICKS_PER_MONTH), dtype=np.float64)
    for t in range(config.MARKET_TICKS_PER_MONTH):
        state.price_history[:, :, t] = state.prices

    # --- Population ---
    state.population = lga_data.population.copy()

    # --- Inventories: 10x daily consumption as initial stock ---
    _init_inventories(state, config, lga_data)

    # --- Production capacity ---
    _init_production(state, config, lga_data)

    # --- Labor ---
    _init_labor(state, config, lga_data)

    # --- Land ---
    _init_land(state, config, lga_data)

    # --- Banking ---
    _init_banking(state, config, lga_data)

    # --- Foreign exchange ---
    state.official_exchange_rate = config.OFFICIAL_EXCHANGE_RATE_INITIAL
    state.parallel_exchange_rate = (
        config.OFFICIAL_EXCHANGE_RATE_INITIAL * (1.0 + config.PARALLEL_RATE_PREMIUM_BASE)
    )
    # Forex reserves: ~8 months of import cover (approx)
    estimated_monthly_imports = 2.0e9  # USD
    state.forex_reserves_usd = config.FOREX_RESERVE_MONTHS * estimated_monthly_imports
    state.monthly_import_bill_usd = estimated_monthly_imports
    state.monthly_export_revenue_usd = 2.5e9

    # --- Government ---
    _init_government(state, config)

    # --- Climate ---
    state.current_month_of_year = 1
    state.is_rainy_season = False
    state.rainfall_modifier = 0.2  # dry season start
    state.desertification_loss = np.zeros(N, dtype=np.float64)

    # --- Al-Shahid ---
    _init_alsahid(state, config, lga_data)

    # --- Enhancement ---
    state.enhancement_adoption = lga_data.bio_enhance_pct.copy()

    # --- Infrastructure ---
    state.infra_power_reliability = np.clip(lga_data.elec_access, 0.1, 1.0)
    state.infra_road_quality = np.clip(lga_data.road_quality, 0.05, 1.0)
    state.infra_telecom_quality = np.clip(lga_data.market_access * 0.8, 0.1, 1.0)

    # --- Hoarded goods ---
    state.hoarded = np.zeros((N, C), dtype=np.float64)

    # --- Automation ---
    state.automation_level = np.zeros((N, C), dtype=np.float64)

    # --- Strikes ---
    state.strikes_active = np.zeros(N, dtype=np.int32)

    # --- Actual output (zeroed, filled during first production tick) ---
    state.actual_output = np.zeros((N, C), dtype=np.float64)

    # --- Factory ownership ---
    _init_factory_ownership(state, config, lga_data)

    logger.info(
        "EconomicState initialized: %d LGAs, pop=%.0fM, GDP/cap range $%.0f-$%.0f",
        N,
        state.population.sum() / 1e6,
        lga_data.gdp_per_capita.min(),
        lga_data.gdp_per_capita.max(),
    )
    return state


# ---------------------------------------------------------------------------
# Private initialization helpers
# ---------------------------------------------------------------------------

def _init_inventories(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """Set initial inventories proportional to population and production type."""
    N, C = config.N_LGAS, config.N_COMMODITIES
    inv = np.zeros((N, C), dtype=np.float64)

    # Base: 10 market-ticks worth of per-capita consumption scaled by population
    pop_norm = lga_data.population / max(lga_data.population.mean(), 1.0)

    for cdef in COMMODITIES:
        c = cdef.id
        # More inventory where commodity is produced
        if cdef.tier == CommodityTier.RAW:
            # Agricultural commodities: more in agricultural LGAs
            if c in (6, 7, 8, 9, 10, 11, 12, 13):
                prod_weight = lga_data.pct_agric
            elif c in (0, 1):  # oil, gas
                prod_weight = lga_data.oil_active
            elif c in (2, 3, 4):  # minerals
                prod_weight = lga_data.mining_active + lga_data.cobalt_active
            else:
                prod_weight = np.ones(N)
        elif cdef.tier == CommodityTier.PROCESSED:
            prod_weight = lga_data.pct_manuf + 0.3
        else:
            prod_weight = lga_data.pct_services + 0.3

        # Base inventory: enough for ~20 market ticks of consumption
        base = pop_norm * (prod_weight + 0.2) * 50.0
        inv[:, c] = base

    # Ensure minimums
    inv = np.maximum(inv, 1.0)
    state.inventories = inv


def _init_production(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """Set production capacity based on LGA economic structure."""
    N, C = config.N_LGAS, config.N_COMMODITIES
    cap = np.zeros((N, C), dtype=np.float64)

    pop_norm = lga_data.population / max(lga_data.population.mean(), 1.0)

    for cdef in COMMODITIES:
        c = cdef.id

        if cdef.tier == CommodityTier.RAW:
            if c == 0:  # crude oil
                cap[:, c] = lga_data.oil_active * pop_norm * 5.0
            elif c == 1:  # natural gas
                cap[:, c] = lga_data.oil_active * pop_norm * 4.0
            elif c == 2:  # cobalt
                cap[:, c] = lga_data.cobalt_active * pop_norm * 3.0
            elif c in (3, 4):  # iron, limestone
                cap[:, c] = lga_data.mining_active * pop_norm * 2.0
            elif c == 5:  # timber
                # Southern forest LGAs
                is_forest = np.array([
                    "forest" in t.lower() or "rainforest" in t.lower()
                    for t in lga_data.terrain
                ], dtype=np.float64)
                cap[:, c] = (lga_data.is_southern * 0.5 + is_forest * 1.0) * pop_norm * 2.0
            elif c in (6, 7, 8, 9, 10, 11):  # crops
                cap[:, c] = lga_data.pct_agric * pop_norm * 3.0
            elif c == 12:  # livestock
                cap[:, c] = (~lga_data.is_southern).astype(float) * lga_data.pct_agric * pop_norm * 2.0
            elif c == 13:  # fish
                is_coastal = np.array([
                    "coastal" in t.lower() or "riverine" in t.lower() or "mangrove" in t.lower()
                    for t in lga_data.terrain
                ], dtype=np.float64)
                cap[:, c] = is_coastal * pop_norm * 2.5

        elif cdef.tier == CommodityTier.PROCESSED:
            if c == 14:  # refined petroleum
                cap[:, c] = lga_data.refinery_present * pop_norm * 3.0
            elif c == 20:  # electricity
                # Proportional to infrastructure + gas availability
                cap[:, c] = lga_data.elec_access * pop_norm * 2.0
            else:
                # General manufacturing: proportional to manufacturing base
                cap[:, c] = lga_data.pct_manuf * pop_norm * 1.5

        elif cdef.tier == CommodityTier.INTERMEDIATE:
            cap[:, c] = (lga_data.pct_manuf + lga_data.pct_services * 0.3) * pop_norm * 1.0

        elif cdef.tier == CommodityTier.SERVICE:
            cap[:, c] = lga_data.pct_services * pop_norm * lga_data.urban_pct * 2.0

    # Ensure no negative capacity, small floor for all producing LGAs
    cap = np.maximum(cap, 0.0)
    state.production_capacity = cap


def _init_labor(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """Initialize labor pools based on population, literacy, and economic structure."""
    N, S = config.N_LGAS, config.N_SKILL_TIERS
    labor = np.zeros((N, S), dtype=np.float64)

    # Working-age fraction ~55% of population
    working_age = lga_data.population * 0.55

    # Skill distribution from literacy and urbanization
    lit = lga_data.literacy
    urb = lga_data.urban_pct
    chinese = np.clip(lga_data.chinese_presence / max(lga_data.chinese_presence.max(), 1.0), 0, 1)

    # Unskilled: inversely related to literacy
    labor[:, 0] = working_age * (1.0 - lit * 0.7) * 0.65
    # Skilled: proportional to literacy and urbanization
    labor[:, 1] = working_age * lit * 0.25
    # Highly skilled: concentrated in urban, educated LGAs
    labor[:, 2] = working_age * lit * urb * 0.08
    # Chinese elite: proportional to Chinese presence
    labor[:, 3] = working_age * chinese * 0.02

    labor = np.maximum(labor, 1.0)  # at least 1 worker per tier
    state.labor_pool = labor

    # Initial employment: 1 - unemployment rate
    emp_rate = 1.0 - lga_data.unemployment_rate
    state.labor_employed = labor * emp_rate[:, np.newaxis] * (1.0 - lga_data.pct_informal[:, np.newaxis])
    state.labor_employed = np.minimum(state.labor_employed, labor)

    # Informal sector
    state.labor_informal = labor * lga_data.pct_informal[:, np.newaxis] * 0.7
    state.labor_informal = np.minimum(state.labor_informal, labor - state.labor_employed)
    state.labor_informal = np.maximum(state.labor_informal, 0.0)

    # Wages: base wages scaled by GDP per capita ratio
    gdp_ratio = lga_data.gdp_per_capita / max(lga_data.gdp_per_capita.mean(), 1.0)
    state.wages = np.outer(gdp_ratio, config.BASE_WAGES)
    state.wages = np.maximum(state.wages, config.BASE_WAGES[0] * 0.5)


def _init_land(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """Initialize land areas and prices."""
    N, L = config.N_LGAS, config.N_LAND_TYPES
    land = np.zeros((N, L), dtype=np.float64)

    # Rough total hectares per LGA based on population density
    # Nigeria total ~92M hectares / 774 LGAs ≈ 119k avg
    base_area = 119_000.0
    density_factor = np.clip(
        lga_data.population / max(lga_data.population.mean(), 1.0), 0.1, 5.0,
    )

    total = base_area * density_factor
    state.land_total = total.copy()

    # Allocate by economic structure
    land[:, 0] = total * lga_data.pct_agric * 0.6       # farmland
    land[:, 1] = total * lga_data.urban_pct * 0.25       # residential
    land[:, 2] = total * lga_data.pct_services * 0.10    # commercial
    land[:, 3] = total * lga_data.pct_manuf * 0.08       # industrial

    # Ensure total doesn't exceed available
    land_sum = land.sum(axis=1, keepdims=True)
    excess_mask = land_sum[:, 0] > total
    if excess_mask.any():
        scale = (total[excess_mask] / land_sum[excess_mask, 0])[:, np.newaxis]
        land[excess_mask] *= scale

    land = np.maximum(land, 1.0)
    state.land_area = land

    # Land prices: higher in urban, southern areas
    base_land_price = np.array([50_000, 200_000, 500_000, 300_000], dtype=np.float64)
    gdp_ratio = lga_data.gdp_per_capita / max(lga_data.gdp_per_capita.mean(), 1.0)
    state.land_prices = np.outer(gdp_ratio, base_land_price)
    state.land_prices = np.maximum(state.land_prices, 10_000)

    # Zoning restrictions: Lagos LGAs get high restriction
    state.zoning_restriction = np.zeros(N, dtype=np.float64)
    for i, s in enumerate(lga_data.states):
        if s == "Lagos":
            state.zoning_restriction[i] = 0.7


def _init_banking(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """Initialize banking system at admin zone level."""
    Z = config.N_ADMIN_ZONES
    az = lga_data.admin_zones  # 1-indexed

    # Aggregate GDP and population by zone
    zone_gdp = np.zeros(Z, dtype=np.float64)
    zone_pop = np.zeros(Z, dtype=np.float64)
    for i in range(lga_data.n_lgas):
        z = az[i] - 1  # convert to 0-indexed
        if 0 <= z < Z:
            zone_gdp[z] += lga_data.gdp_per_capita[i] * lga_data.population[i]
            zone_pop[z] += lga_data.population[i]

    # Deposits: ~20% of zone GDP
    state.bank_deposits = zone_gdp * 0.20
    state.bank_deposits = np.maximum(state.bank_deposits, 1e9)

    # Loans: ~60% of deposits (under reserve ratio constraint)
    state.bank_loans = state.bank_deposits * 0.60
    state.bank_bad_loans = state.bank_loans * 0.03  # 3% NPL ratio

    # Confidence: start at 0.7 (moderate)
    state.bank_confidence = np.full(Z, 0.70, dtype=np.float64)

    # Lending rates
    state.lending_rate = np.full(Z, config.BASE_INTEREST_RATE, dtype=np.float64)


def _init_government(state: EconomicState, config: SimConfig) -> None:
    """Initialize government budget and corruption arrays."""
    N_MIN = len(MINISTRIES)
    # Budget: roughly proportional to importance
    budget_weights = np.array([
        0.15,  # Finance
        0.15,  # Infrastructure
        0.08,  # Trade
        0.05,  # Labor
        0.10,  # Health
        0.05,  # Land
        0.10,  # Education
        0.05,  # Justice
        0.12,  # Defense
        0.08,  # Agriculture
        0.05,  # Energy
        0.02,  # Communications
    ], dtype=np.float64)

    total_budget = 15e12  # 15 trillion naira
    state.budget_allocation = budget_weights * total_budget
    state.budget_released = state.budget_allocation * 0.0  # nothing released yet

    # Corruption and capacity from ministry definitions
    state.corruption_leakage = np.array(
        [MINISTRIES[i]["base_leakage"] for i in range(N_MIN)], dtype=np.float64,
    )
    state.state_capacity = np.array(
        [MINISTRIES[i]["base_capacity"] for i in range(N_MIN)], dtype=np.float64,
    )


def _init_alsahid(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """Initialize al-Shahid control from LGA data."""
    # Normalize al-Shahid influence to 0-1 range
    raw = lga_data.alsahid_influence
    max_val = max(raw.max(), 1.0)
    state.alsahid_control = np.clip(raw / max_val, 0.0, 1.0)

    # Service provision: proportional to control
    state.alsahid_service_provision = state.alsahid_control * config.ALSAHID_SERVICE_QUALITY


def _init_factory_ownership(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """Assign zaibatsu ownership to factories in their controlled commodities."""
    N, C = config.N_LGAS, config.N_COMMODITIES
    state.factory_owner = np.full((N, C), -1, dtype=np.int8)

    for z in ZAIBATSU:
        for c_id in z.controlled_commodities:
            # Assign ownership to LGAs where this commodity has production capacity
            has_capacity = state.production_capacity[:, c_id] > 0
            # Zaibatsu control the top-producing LGAs for their commodities
            if has_capacity.any():
                cap_vals = state.production_capacity[:, c_id]
                threshold = np.percentile(cap_vals[has_capacity], 50)
                top_producers = cap_vals >= threshold
                state.factory_owner[top_producers & has_capacity, c_id] = z.id
