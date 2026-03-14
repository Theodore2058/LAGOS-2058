"""
Core data structures for the LAGOS-2058 Economic Simulator.

All tunable parameters live in SimConfig. All runtime state lives in EconomicState.
Supporting types: enums, policy actions, construction projects, trade routes, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SkillTier(IntEnum):
    UNSKILLED = 0
    SKILLED = 1
    HIGHLY_SKILLED = 2
    CHINESE_ELITE = 3


class LandType(IntEnum):
    FARMLAND = 0
    RESIDENTIAL = 1
    COMMERCIAL = 2
    INDUSTRIAL = 3


class CommodityTier(IntEnum):
    RAW = 0
    PROCESSED = 1
    INTERMEDIATE = 2
    SERVICE = 3
    IMPORT = 4


# ---------------------------------------------------------------------------
# SimConfig — every tunable parameter in one place
# ---------------------------------------------------------------------------

@dataclass
class SimConfig:
    """Master configuration. Every tunable parameter in the simulation."""

    # --- Dimensions ---
    N_LGAS: int = 774
    N_COMMODITIES: int = 36
    N_IMPORT_CATEGORIES: int = 4
    N_SKILL_TIERS: int = 4
    N_LAND_TYPES: int = 4
    N_ADMIN_ZONES: int = 8
    N_VOTER_TYPES: int = 174_960
    N_ISSUE_DIMENSIONS: int = 28
    N_PARTIES: int = 12
    N_PARLIAMENT_SEATS: int = 622
    N_TRADE_ROUTES: int = 10_000

    # --- Time ---
    MARKET_TICK_INTERVAL_HOURS: float = 3.0
    PRODUCTION_TICK_INTERVAL_HOURS: float = 18.0
    STRUCTURAL_TICK_INTERVAL_HOURS: float = 168.0
    MARKET_TICKS_PER_MONTH: int = 56
    PRODUCTION_TICKS_PER_MONTH: int = 7

    # --- Production ---
    COBB_DOUGLAS_LABOR_SHARE: float = 0.55
    COBB_DOUGLAS_LAND_SHARE: float = 0.25
    COBB_DOUGLAS_CAPITAL_SHARE: float = 0.20
    LEONTIEF_WASTE_FACTOR: float = 0.05
    ELECTRICITY_COMMODITY_ID: int = 20

    # --- Trade ---
    TRADER_INFO_RADIUS_HOPS: int = 5
    TRADER_MAX_ACTIVE_ROUTES: int = 8
    SPECULATION_LOOKBACK_DAYS: int = 7
    SPECULATION_THRESHOLD: float = 0.03
    HOARD_RELEASE_THRESHOLD: float = 2.5
    PRICE_ELASTICITY_OF_DEMAND: float = -0.6
    PRICE_ADJUSTMENT_SPEED: float = 0.15
    TRANSPORT_COST_PER_KM: float = 0.002
    RAIL_COST_MULTIPLIER: float = 0.3

    # --- Labor ---
    SKILL_TIER_NAMES: List[str] = field(default_factory=lambda: [
        "unskilled", "skilled", "highly_skilled", "chinese_elite",
    ])
    BASE_WAGES: np.ndarray = field(default_factory=lambda: np.array(
        [30_000, 90_000, 240_000, 450_000], dtype=np.float64,
    ))
    WAGE_ADJUSTMENT_SPEED: float = 0.10
    STRIKE_THRESHOLD: float = 0.60
    STRIKE_BASE_PROBABILITY: float = 0.15
    STRIKE_DURATION_RANGE: Tuple[int, int] = (1, 4)
    INFORMAL_WAGE_FRACTION: float = 0.40
    INFORMAL_PRODUCTIVITY_FRACTION: float = 0.30
    AUTOMATION_INVESTMENT_THRESHOLD: float = 1.5
    AUTOMATION_DISPLACEMENT_RATE: float = 0.05

    # --- Land ---
    LAND_TYPE_NAMES: List[str] = field(default_factory=lambda: [
        "farmland", "residential", "commercial", "industrial",
    ])
    LAND_PRICE_ADJUSTMENT_SPEED: float = 0.08
    ZONING_RESTRICTION_DEFAULT: float = 0.0

    # --- Banking ---
    BASE_INTEREST_RATE: float = 0.08
    RESERVE_RATIO: float = 0.15
    LOAN_DEFAULT_THRESHOLD: float = 0.70
    FINANCIAL_ACCELERATOR_LEVERAGE: float = 4.0
    FINANCIAL_ACCELERATOR_ELASTICITY: float = 0.3
    CREDIT_CONTRACTION_SPEED: float = 0.20
    CREDIT_EXPANSION_SPEED: float = 0.05

    # --- Foreign Exchange ---
    OFFICIAL_EXCHANGE_RATE_INITIAL: float = 1500.0
    PARALLEL_RATE_PREMIUM_BASE: float = 0.10
    FOREX_RESERVE_MONTHS: float = 8.0
    RESERVE_DRAIN_RATE: float = 0.12

    # --- Climate ---
    RAINY_SEASON_START_MONTH: int = 4
    RAINY_SEASON_END_MONTH: int = 10
    DROUGHT_PROBABILITY: float = 0.15
    FLOOD_PROBABILITY: float = 0.10
    DESERTIFICATION_ANNUAL_RATE: float = 0.036
    RAINFALL_VARIANCE: float = 0.20

    # --- Zaibatsu ---
    ZAIBATSU_EFFICIENCY_BONUSES: Dict[str, float] = field(default_factory=lambda: {
        "igwe": 0.25,
        "danjuma": 0.20,
        "bua": 0.20,
        "ida": 0.30,
        "deltel": 0.25,
    })

    # --- Enhancement ---
    ENHANCEMENT_PRODUCTIVITY_BONUS: float = 0.20
    ENHANCEMENT_ADOPTION_SOUTH: float = 0.70
    ENHANCEMENT_ADOPTION_NORTH: float = 0.15
    ENHANCEMENT_ADOPTION_PADA: float = 0.70
    ENHANCEMENT_ADOPTION_NAIJIN: float = 0.70

    # --- Al-Shahid ---
    ALSAHID_TRADE_SURCHARGE_MIN: float = 0.30
    ALSAHID_TRADE_SURCHARGE_MAX: float = 0.50
    ALSAHID_TAX_DIVERSION_RATE: float = 0.40
    ALSAHID_SERVICE_QUALITY: float = 0.60
    ALMAJIRI_RECRUITMENT_RATE: float = 0.02

    # --- Election Anticipation ---
    ANTICIPATION_INVESTMENT_SENSITIVITY: float = 0.30
    ANTICIPATION_CAPITAL_FLIGHT_THRESHOLD: float = 0.25
    ANTICIPATION_AUTOMATION_ACCELERATION: float = 0.15

    # --- Election Feedback ---
    WELFARE_SENSITIVITY_POOR: float = 2.5
    WELFARE_SENSITIVITY_RICH: float = 1.0
    SALIENCE_SHIFT_FOOD_CRISIS: float = 0.40
    SALIENCE_SHIFT_POWER_CRISIS: float = 0.30
    SALIENCE_SHIFT_HOUSING_CRISIS: float = 0.20
    GOVERNANCE_REWARD_MULTIPLIER: float = 0.15

    # --- Corruption ---
    CORRUPTION_LEAKAGE_MIN: float = 0.10
    CORRUPTION_LEAKAGE_MAX: float = 0.50
    STATE_CAPACITY_MIN: float = 0.30
    STATE_CAPACITY_MAX: float = 0.90
    BIC_ENFORCEMENT_LEAKAGE_REDUCTION: float = 0.15

    # --- Demographics ---
    FERTILITY_RATE_SOUTH: float = 1.3
    FERTILITY_RATE_NORTH: float = 3.0
    MIGRATION_PULL_WAGE_WEIGHT: float = 0.50
    MIGRATION_PULL_SAFETY_WEIGHT: float = 0.30
    MIGRATION_PULL_SERVICES_WEIGHT: float = 0.20
    MIGRATION_FRICTION: float = 0.05

    # --- Construction ---
    BUILD_TIME_FACTORY_MONTHS: Tuple[int, int] = (6, 18)
    BUILD_TIME_REFINERY_MONTHS: Tuple[int, int] = (18, 36)
    BUILD_TIME_POWER_PLANT_MONTHS: Tuple[int, int] = (12, 24)
    BUILD_TIME_HOUSING_MONTHS: Tuple[int, int] = (3, 12)
    BUILD_TIME_ROAD_MONTHS: Tuple[int, int] = (6, 24)
    INFRASTRUCTURE_DECAY_RATE: float = 0.02

    # --- Global Commodity Prices ---
    OIL_PRICE_INITIAL_USD: float = 85.0
    OIL_PRICE_VOLATILITY: float = 0.08
    COBALT_PRICE_INITIAL_USD: float = 35_000.0
    COBALT_PRICE_VOLATILITY: float = 0.12
    COMMODITY_CRASH_PROBABILITY: float = 0.03
    COMMODITY_CRASH_MAGNITUDE: float = 0.35

    # --- Random ---
    SEED: int = 42


# ---------------------------------------------------------------------------
# Supporting types
# ---------------------------------------------------------------------------

@dataclass
class PolicyAction:
    """A queued policy change from the political engine."""
    action_type: str
    parameters: Dict
    source: str  # "executive" or "legislative"
    enacted_game_day: int
    implementation_delay: int
    ministry_id: Optional[int] = None


@dataclass
class ConstructionProject:
    """An in-progress construction project."""
    project_type: str
    lga_id: int
    commodity_id: Optional[int]
    months_remaining: int
    monthly_cost_naira: float
    monthly_labor_demand: Dict[int, int]
    completion_effect: Dict
    funded: bool = True
    stall_months: int = 0  # months unfunded; auto-cancel after 12


@dataclass
class TradeRoute:
    """A single edge in the trade network."""
    source_lga: int
    dest_lga: int
    distance_km: float
    route_type: str  # "road", "rail", "river", "sea"
    quality: float
    alsahid_surcharge: float = 0.0


@dataclass
class TraderAgent:
    """A simulated commodity trader operating in the trade network."""
    home_lga: int
    inventory: np.ndarray  # shape (36,)
    cash: float
    info_radius: int
    speculation_aggressiveness: float
    active_routes: List[int] = field(default_factory=list)


@dataclass
class CommodityDef:
    """Static definition of a commodity."""
    id: int
    name: str
    tier: CommodityTier
    base_price: float
    production_type: str  # "cobb_douglas" or "leontief"
    inputs: Dict[int, float]
    labor_requirements: Dict[int, float]
    primary_lgas: List[int]
    is_importable: bool
    is_exportable: bool
    spoilage_rate: float
    demand_elasticity: float


@dataclass
class ZaibatsuDef:
    """Static definition of a family corporation."""
    id: int
    name: str
    controlled_commodities: List[int]
    controlled_lgas: List[int]
    efficiency_bonus: float
    ethnic_affiliation: str


@dataclass
class DisasterEvent:
    """A natural or infrastructure disaster."""
    disaster_type: str
    affected_lgas: List[int]
    severity: float
    duration_months: int
    effects: Dict


# ---------------------------------------------------------------------------
# Mutation containers — returned by each system's tick()
# ---------------------------------------------------------------------------

@dataclass
class ProductionMutations:
    """Output of a production tick."""
    inventory_deltas: np.ndarray       # (774, 36)
    labor_employed_new: np.ndarray     # (774, 4)
    wages_paid: np.ndarray             # (774, 4)
    capacity_utilization: np.ndarray   # (774, 36)


@dataclass
class MarketMutations:
    """Output of a market tick."""
    price_changes: np.ndarray      # (774, 36)
    inventory_changes: np.ndarray  # (774, 36)
    trade_volumes: np.ndarray      # (774, 774) sparse or dense
    excess_demand: np.ndarray      # (774, 36)
    hoarding_changes: np.ndarray   # (774, 36)


@dataclass
class LaborMutations:
    """Output of a labor tick."""
    wages_new: np.ndarray          # (774, 4)
    employment_new: np.ndarray     # (774, 4)
    informal_new: np.ndarray       # (774, 4)
    unemployment: np.ndarray       # (774, 4)
    strikes_triggered: List[int]
    strikes_active: np.ndarray     # (774,) int — remaining strike duration per LGA
    automation_changes: np.ndarray  # (774, 36)


@dataclass
class BankingMutations:
    """Output of a banking tick."""
    deposits_new: np.ndarray       # (8,)
    loans_new: np.ndarray          # (8,)
    bad_loans_new: np.ndarray      # (8,)
    confidence_new: np.ndarray     # (8,)
    lending_rate_new: np.ndarray   # (8,)
    credit_available: np.ndarray   # (8,)
    defaults_this_tick: np.ndarray  # (8,)


@dataclass
class LandMutations:
    """Output of a land tick."""
    land_area_new: np.ndarray      # (774, 4)
    land_prices_new: np.ndarray    # (774, 4)
    housing_supply_change: np.ndarray  # (774,)


@dataclass
class ForexMutations:
    """Output of a forex tick."""
    official_rate_new: float
    parallel_rate_new: float
    reserves_new: float
    export_revenue: float
    import_bill: float
    rate_gap_corruption_drain: float
    oil_price_new: float
    cobalt_price_new: float


@dataclass
class ClimateMutations:
    """Output of a climate tick."""
    rainfall_modifier_new: float
    is_rainy_season_new: bool
    disaster_events: List[DisasterEvent]
    desertification_delta: np.ndarray  # (774,)


@dataclass
class DemographicMutations:
    """Output of a demographics tick."""
    population_new: np.ndarray          # (774,)
    migration_flows: np.ndarray         # sparse (774, 774)
    labor_pool_new: np.ndarray          # (774, 4)
    voter_type_populations_new: Optional[np.ndarray] = None  # (174960,)


@dataclass
class AlShahidMutations:
    """Output of an al-Shahid tick."""
    control_new: np.ndarray              # (774,)
    service_provision_new: np.ndarray    # (774,)
    trade_surcharges_new: np.ndarray     # (N_ROUTES,)
    tax_diversion_amount: float
    recruitment: float


@dataclass
class AnticipationMutations:
    """Output of an election anticipation tick."""
    investment_modifier: np.ndarray      # (774,)
    capital_flight: np.ndarray           # (8,)
    automation_acceleration: np.ndarray  # (774, 36)
    forex_reserve_drain: float


@dataclass
class ElectionFeedback:
    """Economy-to-election feedback channels."""
    welfare_scores: np.ndarray        # (174960,)
    salience_shifts: np.ndarray       # (174960, 28)
    position_shifts: np.ndarray       # (174960, 28)
    migration_voter_changes: np.ndarray  # (774,)
    governance_satisfaction: float


# ---------------------------------------------------------------------------
# EconomicState — the central state object
# ---------------------------------------------------------------------------

@dataclass
class EconomicState:
    """
    Complete economic state of the simulation at a single point in time.

    All per-LGA arrays are indexed by LGA ID (0-773) on their first axis.
    Double-buffered: systems read from current state and write mutations,
    which are applied atomically at tick boundaries.
    """

    # --- Time ---
    game_month: int = 0
    game_day: int = 0
    game_week: int = 0
    real_timestamp: float = 0.0

    # --- Prices ---
    prices: Optional[np.ndarray] = None             # (774, 36) float64
    price_history: Optional[np.ndarray] = None      # (774, 36, 56) float64
    price_history_cursor: int = 0                    # ring buffer write position
    global_oil_price_usd: float = 85.0
    global_cobalt_price_usd: float = 35_000.0

    # --- Inventories ---
    inventories: Optional[np.ndarray] = None         # (774, 36) float64
    hoarded: Optional[np.ndarray] = None             # (774, 36) float64

    # --- Production ---
    production_capacity: Optional[np.ndarray] = None  # (774, 36) float64
    actual_output: Optional[np.ndarray] = None        # (774, 36) float64
    factory_owner: Optional[np.ndarray] = None        # (774, 36) int8

    # --- Labor ---
    labor_pool: Optional[np.ndarray] = None           # (774, 4) float64
    labor_employed: Optional[np.ndarray] = None       # (774, 4) float64
    labor_informal: Optional[np.ndarray] = None       # (774, 4) float64
    wages: Optional[np.ndarray] = None                # (774, 4) float64
    strikes_active: Optional[np.ndarray] = None       # (774,) int32
    automation_level: Optional[np.ndarray] = None     # (774, 36) float64

    # --- Land ---
    land_area: Optional[np.ndarray] = None            # (774, 4) float64
    land_total: Optional[np.ndarray] = None           # (774,) float64
    land_prices: Optional[np.ndarray] = None          # (774, 4) float64
    zoning_restriction: Optional[np.ndarray] = None   # (774,) float64

    # --- Banking (per Administrative Zone) ---
    bank_deposits: Optional[np.ndarray] = None        # (8,) float64
    bank_loans: Optional[np.ndarray] = None           # (8,) float64
    bank_bad_loans: Optional[np.ndarray] = None       # (8,) float64
    bank_confidence: Optional[np.ndarray] = None      # (8,) float64
    lending_rate: Optional[np.ndarray] = None         # (8,) float64

    # --- Foreign Exchange ---
    official_exchange_rate: float = 1500.0
    parallel_exchange_rate: float = 1650.0
    forex_reserves_usd: float = 0.0
    monthly_import_bill_usd: float = 0.0
    monthly_export_revenue_usd: float = 0.0
    wafta_active: bool = True
    import_fulfillment: Dict[str, float] = field(default_factory=lambda: {
        "silicon": 1.0,
        "chemical_feedstock": 1.0,
        "heavy_machinery": 1.0,
        "luxury_consumer_goods": 1.0,
    })

    # --- Government ---
    budget_allocation: Optional[np.ndarray] = None    # (12,) float64
    budget_released: Optional[np.ndarray] = None      # (12,) float64
    corruption_leakage: Optional[np.ndarray] = None   # (12,) float64
    state_capacity: Optional[np.ndarray] = None       # (12,) float64
    tax_rate_income: float = 0.15
    tax_rate_corporate: float = 0.20
    tax_rate_vat: float = 0.075
    tax_rate_import_tariff: float = 0.12
    minimum_wage: float = 50_000.0
    bic_enforcement_intensity: float = 0.50

    # --- Policy Queue ---
    policy_queue: List[PolicyAction] = field(default_factory=list)

    # --- Construction Queue ---
    construction_projects: List[ConstructionProject] = field(default_factory=list)

    # --- Climate ---
    current_month_of_year: int = 1
    is_rainy_season: bool = False
    rainfall_modifier: float = 1.0
    desertification_loss: Optional[np.ndarray] = None  # (774,) float64

    # --- Al-Shahid ---
    alsahid_control: Optional[np.ndarray] = None          # (774,) float64
    alsahid_service_provision: Optional[np.ndarray] = None  # (774,) float64
    alsahid_trade_surcharges: Optional[np.ndarray] = None   # (774,) float64
    alsahid_tax_diversion: float = 0.0                      # naira diverted/month

    # --- Enhancement ---
    enhancement_adoption: Optional[np.ndarray] = None  # (774,) float64

    # --- Demographics ---
    population: Optional[np.ndarray] = None            # (774,) float64

    # --- Voter State (computed at structural tick, lazily) ---
    voter_welfare: Optional[np.ndarray] = None          # (174960,) float64
    voter_welfare_delta: Optional[np.ndarray] = None    # (174960,) float64
    voter_salience: Optional[np.ndarray] = None         # (174960, 28) float64
    voter_positions: Optional[np.ndarray] = None        # (174960, 28) float64

    # --- Election Proximity ---
    # Months until the next election. Set by the campaign/integration layer.
    # 0 = election this month, >0 = future, -1 = no election scheduled.
    # Used by tick_anticipation to model pre-election economic effects.
    months_to_election: int = -1

    # --- Election Platform Signals ---
    # Set by campaign layer to inform anticipation effects.
    # Keys: "nationalization_risk" (0-1), "liberalization_signal" (0-1),
    #        "fiscal_expansion" (0-1), "capital_controls_risk" (0-1)
    platform_signals: Dict[str, float] = field(default_factory=lambda: {
        "nationalization_risk": 0.0,
        "liberalization_signal": 0.0,
        "fiscal_expansion": 0.0,
        "capital_controls_risk": 0.0,
    })

    # --- Infrastructure Quality ---
    infra_road_quality: Optional[np.ndarray] = None     # (774,) float64
    infra_power_reliability: Optional[np.ndarray] = None  # (774,) float64
    infra_telecom_quality: Optional[np.ndarray] = None  # (774,) float64

    # --- Zone Mapping ---
    admin_zone: Optional[np.ndarray] = None           # (774,) int32, 0-indexed zone IDs

    # --- Buildings (structure-of-arrays for all building instances) ---
    n_buildings: int = 0
    building_type_ids: Optional[np.ndarray] = None      # (B,) int16 — building type ID
    building_lga_ids: Optional[np.ndarray] = None        # (B,) int16 — which LGA
    building_owners: Optional[np.ndarray] = None         # (B,) int8  — zaibatsu ID or -1
    building_throughput: Optional[np.ndarray] = None     # (B,) float64 — current max output
    building_tech_level: Optional[np.ndarray] = None     # (B,) float64 — technology (0-1)
    building_employees: Optional[np.ndarray] = None      # (B, 4) float64 — workers per skill
    building_operational: Optional[np.ndarray] = None    # (B,) bool — currently producing
    building_age: Optional[np.ndarray] = None            # (B,) int32 — months since built

    # --- Pop Economic State (per voter type = 174,960 pops) ---
    pop_count: Optional[np.ndarray] = None               # (174960,) float64 — real people
    pop_income: Optional[np.ndarray] = None              # (174960,) float64 — monthly income
    pop_savings: Optional[np.ndarray] = None             # (174960,) float64 — accumulated
    pop_standard_of_living: Optional[np.ndarray] = None  # (174960,) float64 — SoL (0-10)
    pop_employed_formal: Optional[np.ndarray] = None     # (174960,) float64 — fraction formal
    pop_employed_informal: Optional[np.ndarray] = None   # (174960,) float64 — fraction informal
    pop_consumption_fulfilled: Optional[np.ndarray] = None  # (174960,) float64 — % demand met
    pop_sentiment: Optional[np.ndarray] = None           # (174960,) float64 — [-1, 1]

    # --- Order Book State ---
    # Aggregated buy/sell orders per LGA per commodity from the last market tick
    buy_orders: Optional[np.ndarray] = None              # (774, 36) float64 — units demanded
    sell_orders: Optional[np.ndarray] = None             # (774, 36) float64 — units offered
    unfilled_buy: Optional[np.ndarray] = None            # (774, 36) float64 — unmet demand
    unfilled_sell: Optional[np.ndarray] = None           # (774, 36) float64 — unsold supply

    # --- RNG ---
    rng: np.random.Generator = field(
        default_factory=lambda: np.random.default_rng(42),
    )


# ---------------------------------------------------------------------------
# Zone helpers
# ---------------------------------------------------------------------------

def lgas_in_zone(state: EconomicState, zone: int) -> np.ndarray:
    """Return array of LGA indices belonging to the given 0-indexed admin zone."""
    if state.admin_zone is None:
        raise ValueError("admin_zone not initialized on state")
    return np.where(state.admin_zone == zone)[0]


def aggregate_by_zone(
    state: EconomicState, per_lga: np.ndarray, n_zones: int,
) -> np.ndarray:
    """Sum a per-LGA (774,) array into per-zone (Z,) array using real zone mapping."""
    result = np.zeros(n_zones, dtype=np.float64)
    if state.admin_zone is None:
        # Fallback: equal division (should not happen after initialization)
        lgas_per = len(per_lga) // n_zones
        for z in range(n_zones):
            start = z * lgas_per
            end = start + lgas_per if z < n_zones - 1 else len(per_lga)
            result[z] = per_lga[start:end].sum()
        return result
    np.add.at(result, state.admin_zone, per_lga)
    return result


# ---------------------------------------------------------------------------
# Voter type decomposition
# ---------------------------------------------------------------------------

VOTER_DIMENSIONS = {
    "lga": 774,
    "ethnicity": 6,       # yoruba, igbo, hausa, fulani, naijin, other
    "religion": 3,        # muslim, christian, traditional
    "skill_tier": 4,
    "urban_rural": 2,
    "age_cohort": 3,      # youth, working, elder
    "pada_status": 2,
    "enhancement": 2,
}

# Theoretical max: 774 * 576 = 446,016; actual populated: 174,960


# ---------------------------------------------------------------------------
# Consumer demand baskets
# ---------------------------------------------------------------------------

CONSUMPTION_BASKET_COMMODITY_MAP = {
    "food": [6, 7, 8, 13, 18, 21],
    "energy": [14, 20],
    "housing": [34],
    "healthcare": [27],
    "clothing": [30],
    "transport": [14, 28],
    "communication": [31, 33],
    "education": [],
    "security": [],
}

CONSUMPTION_WEIGHTS_BY_QUINTILE = np.array([
    # food  energy housing health clothing transport comms education security
    [0.55, 0.10, 0.12, 0.03, 0.05, 0.05, 0.02, 0.04, 0.04],  # Q1
    [0.42, 0.10, 0.15, 0.05, 0.06, 0.07, 0.05, 0.05, 0.05],  # Q2
    [0.30, 0.08, 0.20, 0.07, 0.07, 0.10, 0.08, 0.05, 0.05],  # Q3
    [0.20, 0.07, 0.22, 0.10, 0.08, 0.12, 0.10, 0.06, 0.05],  # Q4
    [0.12, 0.05, 0.25, 0.12, 0.08, 0.13, 0.12, 0.07, 0.06],  # Q5
], dtype=np.float64)


# ---------------------------------------------------------------------------
# Import dependencies
# ---------------------------------------------------------------------------

IMPORT_DEPENDENCIES = {
    "silicon": {
        "required_by": [26],
        "units_per_output": 0.4,
        "price_usd": 3_500,
        "source": "china_wafta",
        "tariff_rate": 0.05,
        "vulnerability": "wafta_cancellation",
    },
    "chemical_feedstock": {
        "required_by": [23],
        "units_per_output": 0.3,
        "price_usd": 800,
        "source": "global_market",
        "tariff_rate": 0.12,
        "vulnerability": "sanctions",
    },
    "heavy_machinery": {
        "required_by": [0, 1, 2, 3],
        "units_per_output": 0.1,
        "price_usd": 15_000,
        "source": "china_wafta",
        "tariff_rate": 0.08,
        "vulnerability": "wafta_cancellation",
    },
    "luxury_consumer_goods": {
        "required_by": [],
        "units_per_output": 0.0,
        "price_usd": 500,
        "source": "global_market",
        "tariff_rate": 0.25,
        "vulnerability": "forex_crisis",
    },
}
