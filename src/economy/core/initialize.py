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
from src.economy.data.buildings import (
    BUILDING_TYPES, BUILDING_TYPE_BY_ID, N_BUILDING_TYPES,
    BT_OIL_WELL, BT_GAS_WELL, BT_COBALT_MINE, BT_IRON_MINE, BT_LIMESTONE_QUARRY,
    BT_TIMBER_CAMP, BT_GRAIN_FARM, BT_RICE_PADDY, BT_CASSAVA_FARM,
    BT_COCOA_PLANTATION, BT_PALM_PLANTATION, BT_COTTON_FARM, BT_CATTLE_RANCH,
    BT_FISHING_FLEET, BT_OIL_REFINERY, BT_STEEL_MILL, BT_CEMENT_FACTORY,
    BT_COBALT_PROCESSOR, BT_FOOD_PROCESSOR, BT_PALM_OIL_MILL, BT_POWER_PLANT,
    BT_MEAT_DAIRY_PLANT, BT_SAWMILL, BT_CHEMICAL_PLANT, BT_TEXTILE_MILL,
    BT_CONSTRUCTION_YARD, BT_ELECTRONICS_FACTORY, BT_PHARMA_LAB,
    BT_VEHICLE_ASSEMBLY, BT_ARMS_DRONE_FACTORY, BT_CLOTHING_FACTORY,
    BT_TELECOM_TOWER, BT_BANK_BRANCH, BT_ELECTRONICS_STORE,
    BT_HOUSING_DEVELOPER, BT_ENHANCEMENT_CLINIC,
)
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

    # --- Admin zone mapping (0-indexed from 1-indexed data) ---
    state.admin_zone = np.clip(lga_data.admin_zones - 1, 0, Z - 1).astype(np.int32)

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
    state.rainfall_modifier = 0.60  # dry season baseline (rainy = 1.25)
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

    # --- Buildings ---
    _init_buildings(state, config, lga_data)

    # --- Pop economic state ---
    _init_pop_state(state, config, lga_data)

    # --- Order book ---
    state.buy_orders = np.zeros((N, C), dtype=np.float64)
    state.sell_orders = np.zeros((N, C), dtype=np.float64)
    state.unfilled_buy = np.zeros((N, C), dtype=np.float64)
    state.unfilled_sell = np.zeros((N, C), dtype=np.float64)

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

    # Trade surcharges: zero initially (computed by tick_alsahid)
    state.alsahid_trade_surcharges = np.zeros(config.N_LGAS, dtype=np.float64)


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


def _init_buildings(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """
    Place production buildings across Nigeria's 774 LGAs.

    Placement logic based on:
      - Geographic resource endowments (oil in Niger Delta, cobalt in Zamfara)
      - Timeline lore (zaibatsu territories, refinery locations)
      - LGA economic structure (manufacturing %, services %, etc.)
      - Population and infrastructure quality
    """
    N = config.N_LGAS
    rng = state.rng

    # Collect (building_type_id, lga_id, owner, throughput_mult) tuples
    placements: list[tuple[int, int, int, float]] = []

    pop_norm = lga_data.population / max(lga_data.population.mean(), 1.0)

    # Helper: get state-to-LGA mapping
    state_lgas: dict[str, list[int]] = {}
    for i, s in enumerate(lga_data.states):
        state_lgas.setdefault(s, []).append(i)

    # Helper: Nigerian geographic regions
    niger_delta_lgas = set(np.where(lga_data.is_niger_delta)[0])
    southern_lgas = set(np.where(lga_data.is_southern)[0])
    northern_lgas = set(range(N)) - southern_lgas
    sahel_lgas = set(np.where(lga_data.is_sahel)[0])

    # Zamfara LGAs (cobalt deposit, timeline 2028)
    zamfara_lgas = [i for i, s in enumerate(lga_data.states) if s == "Zamfara"]

    # Southeast (Igwe Industries territory)
    igwe_states = {"Anambra", "Abia", "Enugu", "Ebonyi", "Imo"}
    igwe_lgas = [i for i, s in enumerate(lga_data.states) if s in igwe_states]

    # Southwest (IDA Corporation territory)
    ida_states = {"Lagos", "Ogun", "Oyo", "Osun"}
    ida_lgas = [i for i, s in enumerate(lga_data.states) if s in ida_states]

    # Northwest (BUA Group territory)
    bua_states = {"Sokoto", "Kebbi", "Zamfara", "Katsina"}
    bua_lgas = [i for i, s in enumerate(lga_data.states) if s in bua_states]

    # Danjuma territory (north-central and northwest)
    danjuma_states = {"Kaduna", "Kano", "Katsina", "Niger", "Plateau"}
    danjuma_lgas = [i for i, s in enumerate(lga_data.states) if s in danjuma_states]

    # Lagos LGAs (urban core)
    lagos_lgas = state_lgas.get("Lagos", [])

    # Kano LGAs (northern industrial center)
    kano_lgas = state_lgas.get("Kano", [])

    # Coastal/riverine LGAs
    coastal_terrain = {"coastal", "riverine", "mangrove"}
    coastal_lgas = [
        i for i, t in enumerate(lga_data.terrain)
        if any(ct in t.lower() for ct in coastal_terrain)
    ]

    # Forest LGAs
    forest_lgas = [
        i for i, t in enumerate(lga_data.terrain)
        if "forest" in t.lower() or "rainforest" in t.lower()
    ]

    # Refinery locations (from timeline):
    # 1. Bonny Island (Rivers state)
    # 2. Niger-Benue confluence (Kogi state)
    # 3. Maiduguri (Borno state)
    refinery_states = {"Rivers", "Kogi", "Borno"}

    # Cocoa belt
    cocoa_states = {"Ondo", "Oyo", "Osun", "Cross River", "Ekiti"}

    # Cotton belt
    cotton_states = {"Katsina", "Zamfara", "Kano", "Kaduna"}

    def _place_by_weight(bt_id: int, weights: np.ndarray, count: int,
                          owner: int = -1, throughput_mult: float = 1.0):
        """Place `count` buildings of type `bt_id` weighted by `weights`."""
        safe_w = np.maximum(weights, 0.0)
        total = safe_w.sum()
        if total < 1e-10:
            return
        probs = safe_w / total
        chosen = rng.choice(N, size=count, replace=True, p=probs)
        for lga in chosen:
            placements.append((bt_id, int(lga), owner, throughput_mult))

    def _place_in_lgas(bt_id: int, lga_list: list[int], density: float,
                        owner: int = -1, throughput_mult: float = 1.0):
        """Place buildings in specific LGAs, `density` buildings per LGA on average."""
        for lga in lga_list:
            n = max(1, int(density * pop_norm[lga]))
            for _ in range(n):
                placements.append((bt_id, lga, owner, throughput_mult))

    # === TIER 0: EXTRACTION & AGRICULTURE ===

    # Oil wells: Niger Delta states
    oil_weights = lga_data.oil_active * pop_norm
    _place_by_weight(BT_OIL_WELL, oil_weights, 120)

    # Gas wells: co-located with oil
    _place_by_weight(BT_GAS_WELL, oil_weights, 80)

    # Cobalt mines: Zamfara (timeline: discovered 2028)
    if zamfara_lgas:
        _place_in_lgas(BT_COBALT_MINE, zamfara_lgas, 0.8)

    # Iron mines: Plateau, Kogi, Nasarawa, Kwara
    iron_states = {"Plateau", "Kogi", "Nasarawa", "Kwara"}
    iron_lgas = [i for i, s in enumerate(lga_data.states) if s in iron_states]
    iron_weights = lga_data.mining_active * pop_norm
    _place_by_weight(BT_IRON_MINE, iron_weights, 40)

    # Limestone quarries: near cement plants
    lime_states = {"Sokoto", "Edo", "Ogun", "Cross River", "Benue"}
    lime_lgas = [i for i, s in enumerate(lga_data.states) if s in lime_states]
    if lime_lgas:
        _place_in_lgas(BT_LIMESTONE_QUARRY, lime_lgas, 0.5)

    # Timber camps: southern forests
    if forest_lgas:
        _place_in_lgas(BT_TIMBER_CAMP, forest_lgas, 0.4)

    # Grain farms: northern savanna
    grain_weights = np.zeros(N)
    for lga in northern_lgas:
        grain_weights[lga] = lga_data.pct_agric[lga] * pop_norm[lga]
    _place_by_weight(BT_GRAIN_FARM, grain_weights, 200)

    # Rice paddies: distributed but concentrated in Niger, Kebbi, Ebonyi
    rice_states = {"Niger", "Kebbi", "Ebonyi", "Benue", "Kaduna"}
    rice_lgas = [i for i, s in enumerate(lga_data.states) if s in rice_states]
    rice_weights = lga_data.pct_agric * pop_norm
    _place_by_weight(BT_RICE_PADDY, rice_weights, 120)

    # Cassava farms: south and middle belt
    cassava_weights = np.zeros(N)
    for lga in southern_lgas:
        cassava_weights[lga] = lga_data.pct_agric[lga] * pop_norm[lga]
    _place_by_weight(BT_CASSAVA_FARM, cassava_weights, 180)

    # Cocoa plantations: southwest cocoa belt
    cocoa_lgas = [i for i, s in enumerate(lga_data.states) if s in cocoa_states]
    if cocoa_lgas:
        _place_in_lgas(BT_COCOA_PLANTATION, cocoa_lgas, 0.5)

    # Palm plantations: southeast and south-south
    palm_states = {"Abia", "Anambra", "Imo", "Akwa Ibom", "Cross River", "Edo", "Delta"}
    palm_lgas = [i for i, s in enumerate(lga_data.states) if s in palm_states]
    if palm_lgas:
        _place_in_lgas(BT_PALM_PLANTATION, palm_lgas, 0.4)

    # Cotton farms: northern cotton belt
    cotton_lgas = [i for i, s in enumerate(lga_data.states) if s in cotton_states]
    if cotton_lgas:
        _place_in_lgas(BT_COTTON_FARM, cotton_lgas, 0.5)

    # Cattle ranches: north, Danjuma territory
    cattle_weights = np.zeros(N)
    for lga in northern_lgas:
        cattle_weights[lga] = lga_data.pct_agric[lga] * pop_norm[lga] * 0.5
    # Danjuma bonus
    for lga in danjuma_lgas:
        cattle_weights[lga] *= 2.0
    _place_by_weight(BT_CATTLE_RANCH, cattle_weights, 100, owner=1)

    # Fishing fleets: coastal and riverine
    if coastal_lgas:
        _place_in_lgas(BT_FISHING_FLEET, coastal_lgas, 0.5)

    # === TIER 1: PROCESSING ===

    # Oil refineries: 3 major (Bonny Island, Niger-Benue, Maiduguri)
    for ref_state in refinery_states:
        ref_lgas = state_lgas.get(ref_state, [])
        if ref_lgas:
            # Place 2-3 refineries per refinery state
            chosen = rng.choice(ref_lgas, size=min(3, len(ref_lgas)), replace=True)
            for lga in chosen:
                placements.append((BT_OIL_REFINERY, int(lga), -1, 1.0))

    # Steel mills: Igwe Industries (southeast) + some in Lagos industrial zone
    if igwe_lgas:
        _place_in_lgas(BT_STEEL_MILL, igwe_lgas[:10], 0.3, owner=0)
    if lagos_lgas:
        _place_in_lgas(BT_STEEL_MILL, lagos_lgas[:3], 0.5)

    # Cement factories: BUA territory + Dangote-esque spread
    if bua_lgas:
        _place_in_lgas(BT_CEMENT_FACTORY, bua_lgas[:6], 0.3, owner=2)
    # Also in Ogun (historical cement hub)
    ogun_lgas = state_lgas.get("Ogun", [])
    if ogun_lgas:
        _place_in_lgas(BT_CEMENT_FACTORY, ogun_lgas[:3], 0.5)

    # Cobalt processing: near mines in Zamfara
    if zamfara_lgas:
        _place_in_lgas(BT_COBALT_PROCESSOR, zamfara_lgas[:3], 0.5)

    # Food processing: distributed, population-weighted
    food_weights = lga_data.pct_agric * pop_norm * lga_data.urban_pct
    _place_by_weight(BT_FOOD_PROCESSOR, food_weights + 0.1, 150)

    # Palm oil mills: near palm plantations
    if palm_lgas:
        _place_in_lgas(BT_PALM_OIL_MILL, palm_lgas, 0.3)

    # Power plants: population-weighted, bias to gas-producing areas
    power_weights = pop_norm * (1.0 + lga_data.oil_active * 2.0)
    _place_by_weight(BT_POWER_PLANT, power_weights, 100)

    # Meat/dairy plants: Danjuma territory
    if danjuma_lgas:
        _place_in_lgas(BT_MEAT_DAIRY_PLANT, danjuma_lgas, 0.3, owner=1)

    # Sawmills: southern forest belt
    if forest_lgas:
        _place_in_lgas(BT_SAWMILL, forest_lgas, 0.3)

    # Chemical plants: near refineries and gas fields
    chem_weights = lga_data.oil_active * pop_norm * lga_data.pct_manuf
    _place_by_weight(BT_CHEMICAL_PLANT, chem_weights + 0.01, 40)

    # Textile mills: historically Kano, spreading south
    if kano_lgas:
        _place_in_lgas(BT_TEXTILE_MILL, kano_lgas, 0.4)
    textile_weights = lga_data.pct_manuf * pop_norm
    _place_by_weight(BT_TEXTILE_MILL, textile_weights, 60)

    # === TIER 2: MANUFACTURING ===

    # Construction yards: everywhere, population-weighted
    _place_by_weight(BT_CONSTRUCTION_YARD, pop_norm, 120)

    # Electronics factories: Igwe Industries (southeast) + Lagos
    if igwe_lgas:
        _place_in_lgas(BT_ELECTRONICS_FACTORY, igwe_lgas[:8], 0.3, owner=0)
    if lagos_lgas:
        _place_in_lgas(BT_ELECTRONICS_FACTORY, lagos_lgas[:5], 0.4, owner=0)

    # Pharmaceutical labs: BUA Group (northwest)
    if bua_lgas:
        _place_in_lgas(BT_PHARMA_LAB, bua_lgas[:5], 0.3, owner=2)
    # Some in Lagos (research hub)
    if lagos_lgas:
        _place_in_lgas(BT_PHARMA_LAB, lagos_lgas[:3], 0.3)

    # Vehicle assembly: industrial zones
    manuf_weights = lga_data.pct_manuf * pop_norm * lga_data.urban_pct
    _place_by_weight(BT_VEHICLE_ASSEMBLY, manuf_weights, 30, owner=0)

    # Arms/drone factories: IDA Corporation (southwest)
    if ida_lgas:
        _place_in_lgas(BT_ARMS_DRONE_FACTORY, ida_lgas[:6], 0.3, owner=3)

    # Clothing factories: labor-intensive, spread across
    _place_by_weight(BT_CLOTHING_FACTORY, pop_norm * lga_data.pct_manuf + 0.1, 100)

    # === TIER 3: SERVICES ===

    # Telecom towers: Deltel, population-weighted
    _place_by_weight(BT_TELECOM_TOWER, pop_norm * lga_data.urban_pct + 0.1, 200, owner=4)

    # Bank branches: urban areas
    _place_by_weight(BT_BANK_BRANCH, pop_norm * lga_data.urban_pct, 150)

    # Electronics stores: urban areas
    _place_by_weight(BT_ELECTRONICS_STORE, pop_norm * lga_data.urban_pct, 100, owner=0)

    # Housing developers: everywhere, population-weighted
    _place_by_weight(BT_HOUSING_DEVELOPER, pop_norm, 200)

    # Enhancement clinics: south initially (10% adoption 2047, 42% by 2058)
    enh_weights = lga_data.bio_enhance_pct * pop_norm
    _place_by_weight(BT_ENHANCEMENT_CLINIC, enh_weights + 0.01, 60, owner=2)

    # === ASSEMBLE INTO ARRAYS ===
    B = len(placements)
    state.n_buildings = B

    state.building_type_ids = np.array([p[0] for p in placements], dtype=np.int16)
    state.building_lga_ids = np.array([p[1] for p in placements], dtype=np.int16)
    state.building_owners = np.array([p[2] for p in placements], dtype=np.int8)

    # Throughput: base * placement multiplier * small random variation
    base_tp = np.array(
        [BUILDING_TYPE_BY_ID[p[0]].base_throughput * p[3] for p in placements],
        dtype=np.float64,
    )
    state.building_throughput = base_tp * rng.uniform(0.8, 1.2, size=B)

    # Technology level: 0.3-0.8 (2058 is advanced but not cutting-edge everywhere)
    state.building_tech_level = rng.uniform(0.3, 0.8, size=B)
    # Zaibatsu-owned buildings get higher tech
    for i in range(B):
        if state.building_owners[i] >= 0:
            state.building_tech_level[i] = min(state.building_tech_level[i] + 0.15, 1.0)

    # Employees: start at 80% of required labor
    state.building_employees = np.zeros((B, config.N_SKILL_TIERS), dtype=np.float64)
    for i in range(B):
        bt = BUILDING_TYPE_BY_ID[state.building_type_ids[i]]
        for skill, count in bt.labor.items():
            state.building_employees[i, int(skill)] = count * 0.8

    # All buildings start operational
    state.building_operational = np.ones(B, dtype=bool)

    # Building age: random 0-120 months (most buildings pre-exist)
    state.building_age = rng.integers(0, 120, size=B, dtype=np.int32)

    logger.info(
        "Buildings initialized: %d buildings across %d types, "
        "%d zaibatsu-owned (%.0f%%)",
        B, N_BUILDING_TYPES,
        int((state.building_owners >= 0).sum()),
        100.0 * (state.building_owners >= 0).sum() / max(B, 1),
    )


def _init_pop_state(
    state: EconomicState, config: SimConfig, lga_data: EconomyLGAData,
) -> None:
    """
    Initialize per-pop economic state for all 174,960 voter types.

    Each voter type represents a demographic slice of an LGA's population.
    Economic attributes (income, savings, SoL) are derived from the voter
    type's LGA, livelihood, and income bracket.

    Voter type decomposition (from election_engine):
      15 ethnicities x 9 religions x 3 settings x 4 ages
      x 3 educations x 2 genders x 6 livelihoods x 3 incomes = 174,960
    """
    NVT = config.N_VOTER_TYPES
    N = config.N_LGAS

    # --- Decompose voter type IDs into dimension indices ---
    # Dimension sizes: 15, 9, 3, 4, 3, 2, 6, 3
    dim_sizes = [15, 9, 3, 4, 3, 2, 6, 3]
    strides = np.empty(len(dim_sizes), dtype=np.int64)
    strides[-1] = 1
    for i in range(len(dim_sizes) - 2, -1, -1):
        strides[i] = strides[i + 1] * dim_sizes[i + 1]

    ids = np.arange(NVT, dtype=np.int64)
    # Extract relevant dimensions
    lga_ids = (ids // strides[0]) % dim_sizes[0]
    # Wait — the voter type decomposition in the election engine uses a DIFFERENT
    # set of dimensions than the VOTER_DIMENSIONS dict in types.py.
    # types.py says: lga(774), ethnicity(6), religion(3), skill_tier(4),
    #                urban_rural(2), age_cohort(3), pada_status(2), enhancement(2)
    # voter_types.py says: ethnicity(15), religion(9), setting(3), age(4),
    #                       education(3), gender(2), livelihood(6), income(3)
    # These are DIFFERENT decompositions. The voter_types.py one doesn't have LGA
    # as a dimension — it uses LGA-specific weights instead.
    #
    # For the economy, we use the types.py VOTER_DIMENSIONS which includes LGA:
    # 774 * 6 * 3 * 4 * 2 * 3 * 2 * 2 = 174,960
    # But 774 * 6 * 3 * 4 * 2 * 3 * 2 * 2 = 774 * 576 = 446,016 != 174,960
    # So the 174,960 comes from the election engine's decomposition,
    # NOT from types.py's VOTER_DIMENSIONS.
    #
    # The election engine decomposes 174,960 = 15 * 9 * 3 * 4 * 3 * 2 * 6 * 3
    # These are NOT per-LGA. Instead, each LGA has weights for all 174,960 types.
    #
    # For per-pop economics, we need to assign each pop type to an LGA.
    # We'll use a round-robin assignment: pop_type % 774 = LGA assignment.
    # This gives each LGA ~226 pop types.
    pop_lga = (ids % N).astype(np.int32)

    # Livelihood dimension: stride for livelihood (dim index 6)
    livelihood_stride = strides[6] if len(strides) > 6 else 3
    livelihood_ids = (ids // livelihood_stride) % 6

    # Income dimension: stride for income (dim index 7, rightmost)
    income_ids = ids % 3

    # --- Pop count: distribute LGA population across its pop types ---
    state.pop_count = np.zeros(NVT, dtype=np.float64)
    # Each LGA gets ~226 pop types. Distribute population proportionally.
    pop_types_per_lga = NVT // N  # ~226
    for lga in range(N):
        start = lga
        lga_pop_indices = np.arange(start, NVT, N)  # every N-th pop type
        n_types = len(lga_pop_indices)
        if n_types > 0:
            # Weight by income bracket: bottom 40% gets more people, top 20% fewer
            income_of_types = income_ids[lga_pop_indices]
            weight = np.where(income_of_types == 0, 0.4,
                     np.where(income_of_types == 1, 0.4, 0.2))
            weight = weight / weight.sum()
            state.pop_count[lga_pop_indices] = lga_data.population[lga] * weight

    # --- Pop income: based on LGA wages and livelihood ---
    state.pop_income = np.zeros(NVT, dtype=np.float64)
    if state.wages is not None:
        # Map livelihood to approximate skill tier:
        # 0=Smallholder->unskilled, 1=Commercial_ag->skilled,
        # 2=Trade_informal->unskilled, 3=Formal_private->skilled,
        # 4=Public_sector->highly_skilled, 5=Unemployed->none
        livelihood_to_skill = np.array([0, 1, 0, 1, 2, 0], dtype=np.int32)
        livelihood_income_mult = np.array([0.6, 0.9, 0.4, 1.0, 1.2, 0.1], dtype=np.float64)
        income_bracket_mult = np.array([0.5, 1.0, 2.5], dtype=np.float64)

        for vt in range(NVT):
            lga = pop_lga[vt]
            liv = livelihood_ids[vt]
            inc = income_ids[vt]
            skill = livelihood_to_skill[liv]
            state.pop_income[vt] = (
                state.wages[lga, skill]
                * livelihood_income_mult[liv]
                * income_bracket_mult[inc]
            )

    # --- Pop savings: initial savings = 2 months of income ---
    state.pop_savings = state.pop_income * 2.0

    # --- Standard of living: derived from income and LGA infrastructure ---
    state.pop_standard_of_living = np.zeros(NVT, dtype=np.float64)
    if state.pop_income is not None:
        # SoL scale 0-10, based on income relative to median
        median_income = max(np.median(state.pop_income[state.pop_income > 0]), 1.0)
        income_ratio = state.pop_income / median_income
        # Log-scaled: SoL = 5 + 2*log(income_ratio), clamped to [0, 10]
        state.pop_standard_of_living = np.clip(
            5.0 + 2.0 * np.log(np.maximum(income_ratio, 0.01)), 0.0, 10.0,
        )

    # --- Employment fractions ---
    state.pop_employed_formal = np.zeros(NVT, dtype=np.float64)
    state.pop_employed_informal = np.zeros(NVT, dtype=np.float64)
    # Set based on livelihood:
    # 0=Smallholder: 30% formal, 50% informal
    # 1=Commercial_ag: 70% formal, 20% informal
    # 2=Trade_informal: 10% formal, 80% informal
    # 3=Formal_private: 85% formal, 10% informal
    # 4=Public_sector: 95% formal, 3% informal
    # 5=Unemployed: 0% formal, 20% informal
    formal_rates = np.array([0.30, 0.70, 0.10, 0.85, 0.95, 0.0], dtype=np.float64)
    informal_rates = np.array([0.50, 0.20, 0.80, 0.10, 0.03, 0.20], dtype=np.float64)
    state.pop_employed_formal = formal_rates[livelihood_ids]
    state.pop_employed_informal = informal_rates[livelihood_ids]

    # --- Consumption fulfilled: start at 80% (some scarcity) ---
    state.pop_consumption_fulfilled = np.full(NVT, 0.80, dtype=np.float64)

    # --- Sentiment: start neutral ---
    state.pop_sentiment = np.zeros(NVT, dtype=np.float64)

    # Store the LGA mapping for later use
    state._pop_lga_ids = pop_lga
    state._pop_livelihood_ids = livelihood_ids
    state._pop_income_ids = income_ids

    logger.info(
        "Pop state initialized: %d voter types, total pop=%.0fM, "
        "median income=%.0f, mean SoL=%.1f",
        NVT,
        state.pop_count.sum() / 1e6,
        float(np.median(state.pop_income[state.pop_income > 0])),
        float(state.pop_standard_of_living.mean()),
    )
