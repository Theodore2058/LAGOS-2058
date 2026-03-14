"""
Building type definitions for the LAGOS-2058 economy.

Each building type defines an explicit production recipe:
  - Inputs: which commodities and how much per unit of output
  - Output: which commodity is produced
  - Labor: workers needed by skill tier
  - Throughput: base units per production tick
  - Construction: cost and time to build new instances

Building types are placed across Nigeria's 774 LGAs based on:
  - Geographic suitability (oil in Niger Delta, cobalt in Zamfara, etc.)
  - Timeline lore (Igwe Industries electronics, IDA drones, BUA pharma, etc.)
  - Zaibatsu control patterns
  - Infrastructure requirements

~30 building types across 4 tiers, mirroring the commodity tiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.economy.core.types import SkillTier
from src.economy.data.commodity_ids import *


# ---------------------------------------------------------------------------
# Building type definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BuildingTypeDef:
    """Static definition of a building type."""
    id: int
    name: str
    display_name: str
    tier: int                            # 0=extraction, 1=processing, 2=manufacturing, 3=services
    output_commodity: int                # commodity ID produced
    inputs: Dict[int, float]             # {commodity_id: units_per_output_unit}
    labor: Dict[int, int]                # {SkillTier: workers_per_building}
    base_throughput: float               # units output per production tick per building
    construction_cost_naira: float       # cost to build one
    construction_months: int             # months to build
    requires_power: bool                 # needs electricity infrastructure
    min_power_reliability: float         # minimum infra_power_reliability to operate
    min_road_quality: float              # minimum infra_road_quality to operate
    zaibatsu_affinity: Optional[int]     # zaibatsu ID that gets efficiency bonus, or None
    rainfall_sensitive: bool             # affected by rainfall (agriculture)
    description: str = ""


# ---------------------------------------------------------------------------
# Building type IDs
# ---------------------------------------------------------------------------

# Tier 0: Extraction & Agriculture (IDs 0-13)
BT_OIL_WELL = 0
BT_GAS_WELL = 1
BT_COBALT_MINE = 2
BT_IRON_MINE = 3
BT_LIMESTONE_QUARRY = 4
BT_TIMBER_CAMP = 5
BT_GRAIN_FARM = 6
BT_RICE_PADDY = 7
BT_CASSAVA_FARM = 8
BT_COCOA_PLANTATION = 9
BT_PALM_PLANTATION = 10
BT_COTTON_FARM = 11
BT_CATTLE_RANCH = 12
BT_FISHING_FLEET = 13

# Tier 1: Processing (IDs 14-24)
BT_OIL_REFINERY = 14
BT_STEEL_MILL = 15
BT_CEMENT_FACTORY = 16
BT_COBALT_PROCESSOR = 17
BT_FOOD_PROCESSOR = 18
BT_PALM_OIL_MILL = 19
BT_POWER_PLANT = 20
BT_MEAT_DAIRY_PLANT = 21
BT_SAWMILL = 22
BT_CHEMICAL_PLANT = 23
BT_TEXTILE_MILL = 24

# Tier 2: Manufacturing (IDs 25-30)
BT_CONSTRUCTION_YARD = 25
BT_ELECTRONICS_FACTORY = 26
BT_PHARMA_LAB = 27
BT_VEHICLE_ASSEMBLY = 28
BT_ARMS_DRONE_FACTORY = 29
BT_CLOTHING_FACTORY = 30

# Tier 3: Services (IDs 31-35)
BT_TELECOM_TOWER = 31
BT_BANK_BRANCH = 32
BT_ELECTRONICS_STORE = 33
BT_HOUSING_DEVELOPER = 34
BT_ENHANCEMENT_CLINIC = 35

N_BUILDING_TYPES = 36


# ---------------------------------------------------------------------------
# All building type definitions
# ---------------------------------------------------------------------------

BUILDING_TYPES: List[BuildingTypeDef] = [
    # ===================================================================
    # TIER 0: EXTRACTION & AGRICULTURE
    # ===================================================================
    BuildingTypeDef(
        id=BT_OIL_WELL, name="oil_well", display_name="Oil Well",
        tier=0, output_commodity=CRUDE_OIL,
        inputs={},  # primary extraction, no commodity inputs
        labor={SkillTier.UNSKILLED: 20, SkillTier.SKILLED: 8},
        base_throughput=5.0,
        construction_cost_naira=50e9, construction_months=18,
        requires_power=True, min_power_reliability=0.3, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Niger Delta oil extraction. Chinese-Nigerian joint ventures (WAFTA 2032).",
    ),
    BuildingTypeDef(
        id=BT_GAS_WELL, name="gas_well", display_name="Natural Gas Well",
        tier=0, output_commodity=NATURAL_GAS,
        inputs={},
        labor={SkillTier.UNSKILLED: 15, SkillTier.SKILLED: 8},
        base_throughput=4.0,
        construction_cost_naira=40e9, construction_months=15,
        requires_power=True, min_power_reliability=0.3, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Natural gas extraction, often co-located with oil operations.",
    ),
    BuildingTypeDef(
        id=BT_COBALT_MINE, name="cobalt_mine", display_name="Cobalt Mine",
        tier=0, output_commodity=COBALT_ORE,
        inputs={},
        labor={SkillTier.UNSKILLED: 30, SkillTier.SKILLED: 10},
        base_throughput=3.0,
        construction_cost_naira=80e9, construction_months=24,
        requires_power=True, min_power_reliability=0.4, min_road_quality=0.3,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Zamfara cobalt deposit (discovered 2028). Chinese Sinomine involvement.",
    ),
    BuildingTypeDef(
        id=BT_IRON_MINE, name="iron_mine", display_name="Iron Mine",
        tier=0, output_commodity=IRON_ORE,
        inputs={},
        labor={SkillTier.UNSKILLED: 25, SkillTier.SKILLED: 5},
        base_throughput=4.0,
        construction_cost_naira=30e9, construction_months=12,
        requires_power=True, min_power_reliability=0.3, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Iron ore extraction in Plateau, Kogi, and Nasarawa states.",
    ),
    BuildingTypeDef(
        id=BT_LIMESTONE_QUARRY, name="limestone_quarry", display_name="Limestone Quarry",
        tier=0, output_commodity=LIMESTONE,
        inputs={},
        labor={SkillTier.UNSKILLED: 15},
        base_throughput=5.0,
        construction_cost_naira=15e9, construction_months=8,
        requires_power=False, min_power_reliability=0.1, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Limestone extraction for cement production.",
    ),
    BuildingTypeDef(
        id=BT_TIMBER_CAMP, name="timber_camp", display_name="Timber Camp",
        tier=0, output_commodity=TIMBER,
        inputs={},
        labor={SkillTier.UNSKILLED: 20},
        base_throughput=3.0,
        construction_cost_naira=8e9, construction_months=4,
        requires_power=False, min_power_reliability=0.1, min_road_quality=0.15,
        zaibatsu_affinity=None, rainfall_sensitive=True,
        description="Southern forest belt logging operations.",
    ),
    BuildingTypeDef(
        id=BT_GRAIN_FARM, name="grain_farm", display_name="Grain Farm",
        tier=0, output_commodity=STAPLE_GRAINS,
        inputs={},
        labor={SkillTier.UNSKILLED: 30},
        base_throughput=4.0,
        construction_cost_naira=5e9, construction_months=3,
        requires_power=False, min_power_reliability=0.05, min_road_quality=0.1,
        zaibatsu_affinity=None, rainfall_sensitive=True,
        description="Northern savanna grain production (sorghum, millet, maize).",
    ),
    BuildingTypeDef(
        id=BT_RICE_PADDY, name="rice_paddy", display_name="Rice Paddy",
        tier=0, output_commodity=RICE,
        inputs={},
        labor={SkillTier.UNSKILLED: 25},
        base_throughput=3.5,
        construction_cost_naira=6e9, construction_months=3,
        requires_power=False, min_power_reliability=0.05, min_road_quality=0.1,
        zaibatsu_affinity=None, rainfall_sensitive=True,
        description="Rice cultivation in Niger, Kebbi, Ebonyi, and other states.",
    ),
    BuildingTypeDef(
        id=BT_CASSAVA_FARM, name="cassava_farm", display_name="Cassava Farm",
        tier=0, output_commodity=CASSAVA,
        inputs={},
        labor={SkillTier.UNSKILLED: 20},
        base_throughput=4.5,
        construction_cost_naira=4e9, construction_months=2,
        requires_power=False, min_power_reliability=0.05, min_road_quality=0.1,
        zaibatsu_affinity=None, rainfall_sensitive=True,
        description="Nigeria's staple crop. Concentrated in south and middle belt.",
    ),
    BuildingTypeDef(
        id=BT_COCOA_PLANTATION, name="cocoa_plantation", display_name="Cocoa Plantation",
        tier=0, output_commodity=COCOA_BEANS,
        inputs={},
        labor={SkillTier.UNSKILLED: 25},
        base_throughput=2.5,
        construction_cost_naira=10e9, construction_months=6,
        requires_power=False, min_power_reliability=0.05, min_road_quality=0.15,
        zaibatsu_affinity=None, rainfall_sensitive=True,
        description="Southwest cocoa belt (Ondo, Oyo, Osun, Cross River).",
    ),
    BuildingTypeDef(
        id=BT_PALM_PLANTATION, name="palm_plantation", display_name="Palm Plantation",
        tier=0, output_commodity=PALM_FRUIT,
        inputs={},
        labor={SkillTier.UNSKILLED: 20},
        base_throughput=3.0,
        construction_cost_naira=8e9, construction_months=5,
        requires_power=False, min_power_reliability=0.05, min_road_quality=0.1,
        zaibatsu_affinity=None, rainfall_sensitive=True,
        description="Oil palm cultivation in southeastern and south-south states.",
    ),
    BuildingTypeDef(
        id=BT_COTTON_FARM, name="cotton_farm", display_name="Cotton Farm",
        tier=0, output_commodity=COTTON,
        inputs={},
        labor={SkillTier.UNSKILLED: 25},
        base_throughput=3.0,
        construction_cost_naira=5e9, construction_months=3,
        requires_power=False, min_power_reliability=0.05, min_road_quality=0.1,
        zaibatsu_affinity=None, rainfall_sensitive=True,
        description="Northern cotton belt (Katsina, Zamfara, Kano).",
    ),
    BuildingTypeDef(
        id=BT_CATTLE_RANCH, name="cattle_ranch", display_name="Cattle Ranch",
        tier=0, output_commodity=LIVESTOCK,
        inputs={STAPLE_GRAINS: 0.3},  # feed
        labor={SkillTier.UNSKILLED: 15},
        base_throughput=3.0,
        construction_cost_naira=7e9, construction_months=4,
        requires_power=False, min_power_reliability=0.05, min_road_quality=0.1,
        zaibatsu_affinity=1,  # Danjuma (expanded into meat production 2037)
        rainfall_sensitive=True,
        description="Northern pastoral and Danjuma commercial ranching.",
    ),
    BuildingTypeDef(
        id=BT_FISHING_FLEET, name="fishing_fleet", display_name="Fishing Fleet",
        tier=0, output_commodity=FISH,
        inputs={},
        labor={SkillTier.UNSKILLED: 20},
        base_throughput=3.5,
        construction_cost_naira=6e9, construction_months=3,
        requires_power=False, min_power_reliability=0.05, min_road_quality=0.1,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Coastal and riverine fishing (Lagos, Rivers, Cross River, Niger).",
    ),

    # ===================================================================
    # TIER 1: PROCESSING
    # ===================================================================
    BuildingTypeDef(
        id=BT_OIL_REFINERY, name="oil_refinery", display_name="Oil Refinery",
        tier=1, output_commodity=REFINED_PETROLEUM,
        inputs={CRUDE_OIL: 1.2, ELECTRICITY: 0.3},
        labor={SkillTier.SKILLED: 15, SkillTier.HIGHLY_SKILLED: 5},
        base_throughput=4.0,
        construction_cost_naira=200e9, construction_months=36,
        requires_power=True, min_power_reliability=0.6, min_road_quality=0.4,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Three major refineries: Bonny Island (2044), Niger-Benue (2044), Maiduguri (2046).",
    ),
    BuildingTypeDef(
        id=BT_STEEL_MILL, name="steel_mill", display_name="Steel Mill",
        tier=1, output_commodity=STEEL,
        inputs={IRON_ORE: 2.0, ELECTRICITY: 0.5, NATURAL_GAS: 0.3},
        labor={SkillTier.SKILLED: 20, SkillTier.HIGHLY_SKILLED: 5},
        base_throughput=3.0,
        construction_cost_naira=100e9, construction_months=24,
        requires_power=True, min_power_reliability=0.5, min_road_quality=0.3,
        zaibatsu_affinity=0,  # Igwe Industries (Igbo, steel exports to China)
        rainfall_sensitive=False,
        description="Igwe Industries steel production (SE Nigeria). 30% of heavy manufacturing by 2045.",
    ),
    BuildingTypeDef(
        id=BT_CEMENT_FACTORY, name="cement_factory", display_name="Cement Factory",
        tier=1, output_commodity=CEMENT,
        inputs={LIMESTONE: 1.5, ELECTRICITY: 0.4, NATURAL_GAS: 0.2},
        labor={SkillTier.SKILLED: 12},
        base_throughput=4.0,
        construction_cost_naira=60e9, construction_months=18,
        requires_power=True, min_power_reliability=0.5, min_road_quality=0.3,
        zaibatsu_affinity=2,  # BUA (cement is historically BUA territory)
        rainfall_sensitive=False,
        description="Cement production. BUA Group dominant (Sokoto, Edo plants).",
    ),
    BuildingTypeDef(
        id=BT_COBALT_PROCESSOR, name="cobalt_processor", display_name="Cobalt Processing Plant",
        tier=1, output_commodity=PROCESSED_COBALT,
        inputs={COBALT_ORE: 3.0, ELECTRICITY: 0.8},
        labor={SkillTier.SKILLED: 10, SkillTier.HIGHLY_SKILLED: 8},
        base_throughput=2.0,
        construction_cost_naira=120e9, construction_months=24,
        requires_power=True, min_power_reliability=0.6, min_road_quality=0.4,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Cobalt processing near Zamfara mines. Chinese tech transfer.",
    ),
    BuildingTypeDef(
        id=BT_FOOD_PROCESSOR, name="food_processor", display_name="Food Processing Plant",
        tier=1, output_commodity=PROCESSED_FOOD,
        inputs={STAPLE_GRAINS: 0.5, CASSAVA: 0.3, RICE: 0.3, ELECTRICITY: 0.2},
        labor={SkillTier.UNSKILLED: 15, SkillTier.SKILLED: 5},
        base_throughput=5.0,
        construction_cost_naira=20e9, construction_months=10,
        requires_power=True, min_power_reliability=0.4, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Food processing distributed across Nigeria.",
    ),
    BuildingTypeDef(
        id=BT_PALM_OIL_MILL, name="palm_oil_mill", display_name="Palm Oil Mill",
        tier=1, output_commodity=PALM_OIL,
        inputs={PALM_FRUIT: 1.5, ELECTRICITY: 0.2},
        labor={SkillTier.UNSKILLED: 10, SkillTier.SKILLED: 4},
        base_throughput=3.5,
        construction_cost_naira=15e9, construction_months=8,
        requires_power=True, min_power_reliability=0.3, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Palm oil processing in southeast and south-south.",
    ),
    BuildingTypeDef(
        id=BT_POWER_PLANT, name="power_plant", display_name="Power Plant",
        tier=1, output_commodity=ELECTRICITY,
        inputs={NATURAL_GAS: 0.8},
        labor={SkillTier.SKILLED: 10, SkillTier.HIGHLY_SKILLED: 5},
        base_throughput=6.0,
        construction_cost_naira=80e9, construction_months=20,
        requires_power=False, min_power_reliability=0.1, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Gas-fired power plants. Shiroro hydro damaged by al-Shahid drone (2045).",
    ),
    BuildingTypeDef(
        id=BT_MEAT_DAIRY_PLANT, name="meat_dairy_plant", display_name="Meat & Dairy Plant",
        tier=1, output_commodity=MEAT_DAIRY,
        inputs={LIVESTOCK: 1.0, ELECTRICITY: 0.2},
        labor={SkillTier.UNSKILLED: 10, SkillTier.SKILLED: 5},
        base_throughput=3.0,
        construction_cost_naira=18e9, construction_months=10,
        requires_power=True, min_power_reliability=0.4, min_road_quality=0.2,
        zaibatsu_affinity=1,  # Danjuma (meat production 2037)
        rainfall_sensitive=False,
        description="Danjuma meat processing. Gulf-financed expansion (2037).",
    ),
    BuildingTypeDef(
        id=BT_SAWMILL, name="sawmill", display_name="Sawmill",
        tier=1, output_commodity=LUMBER,
        inputs={TIMBER: 1.2, ELECTRICITY: 0.2},
        labor={SkillTier.UNSKILLED: 12, SkillTier.SKILLED: 4},
        base_throughput=3.5,
        construction_cost_naira=10e9, construction_months=6,
        requires_power=True, min_power_reliability=0.3, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Lumber processing in southern forest belt.",
    ),
    BuildingTypeDef(
        id=BT_CHEMICAL_PLANT, name="chemical_plant", display_name="Chemical Plant",
        tier=1, output_commodity=CHEMICALS,
        inputs={NATURAL_GAS: 0.5},
        labor={SkillTier.SKILLED: 8, SkillTier.HIGHLY_SKILLED: 8},
        base_throughput=3.0,
        construction_cost_naira=50e9, construction_months=18,
        requires_power=True, min_power_reliability=0.5, min_road_quality=0.3,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Petrochemical processing near refineries and gas fields.",
    ),
    BuildingTypeDef(
        id=BT_TEXTILE_MILL, name="textile_mill", display_name="Textile Mill",
        tier=1, output_commodity=TEXTILES,
        inputs={COTTON: 1.0, ELECTRICITY: 0.2, CHEMICALS: 0.1},
        labor={SkillTier.UNSKILLED: 20, SkillTier.SKILLED: 5},
        base_throughput=4.0,
        construction_cost_naira=15e9, construction_months=10,
        requires_power=True, min_power_reliability=0.4, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Textile mills historically in Kano, now spreading south.",
    ),

    # ===================================================================
    # TIER 2: MANUFACTURING
    # ===================================================================
    BuildingTypeDef(
        id=BT_CONSTRUCTION_YARD, name="construction_yard", display_name="Construction Materials Yard",
        tier=2, output_commodity=CONSTRUCTION_MATERIALS,
        inputs={STEEL: 0.5, CEMENT: 0.8, LUMBER: 0.3},
        labor={SkillTier.UNSKILLED: 15, SkillTier.SKILLED: 10},
        base_throughput=4.0,
        construction_cost_naira=25e9, construction_months=10,
        requires_power=True, min_power_reliability=0.3, min_road_quality=0.3,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Construction materials aggregation. Critical for all building projects.",
    ),
    BuildingTypeDef(
        id=BT_ELECTRONICS_FACTORY, name="electronics_factory", display_name="Electronics Factory",
        tier=2, output_commodity=ELECTRONIC_COMPONENTS,
        inputs={PROCESSED_COBALT: 0.5, ELECTRICITY: 0.3},
        labor={SkillTier.SKILLED: 10, SkillTier.HIGHLY_SKILLED: 15, SkillTier.CHINESE_ELITE: 3},
        base_throughput=2.5,
        construction_cost_naira=80e9, construction_months=18,
        requires_power=True, min_power_reliability=0.7, min_road_quality=0.4,
        zaibatsu_affinity=0,  # Igwe Industries (electronics since 2036)
        rainfall_sensitive=False,
        description="Igwe Industries electronics. Southern industrial zones (2036+). Silicon import-dependent.",
    ),
    BuildingTypeDef(
        id=BT_PHARMA_LAB, name="pharma_lab", display_name="Pharmaceutical Laboratory",
        tier=2, output_commodity=PHARMACEUTICALS,
        inputs={CHEMICALS: 1.0, ELECTRICITY: 0.3},
        labor={SkillTier.HIGHLY_SKILLED: 15, SkillTier.CHINESE_ELITE: 3},
        base_throughput=2.0,
        construction_cost_naira=60e9, construction_months=15,
        requires_power=True, min_power_reliability=0.6, min_road_quality=0.4,
        zaibatsu_affinity=2,  # BUA Group (pharma since 2034, Naijacor)
        rainfall_sensitive=False,
        description="BUA Group pharmaceutical R&D. Naijacor heart medication (2034).",
    ),
    BuildingTypeDef(
        id=BT_VEHICLE_ASSEMBLY, name="vehicle_assembly", display_name="Vehicle & Machinery Assembly",
        tier=2, output_commodity=VEHICLES_MACHINERY,
        inputs={STEEL: 1.0, ELECTRONIC_COMPONENTS: 0.5},
        labor={SkillTier.SKILLED: 20, SkillTier.HIGHLY_SKILLED: 8},
        base_throughput=2.0,
        construction_cost_naira=100e9, construction_months=24,
        requires_power=True, min_power_reliability=0.6, min_road_quality=0.4,
        zaibatsu_affinity=0,  # Igwe (heavy manufacturing)
        rainfall_sensitive=False,
        description="Vehicle and machinery assembly in industrial zones.",
    ),
    BuildingTypeDef(
        id=BT_ARMS_DRONE_FACTORY, name="arms_drone_factory", display_name="Arms & Drone Factory",
        tier=2, output_commodity=ARMS_DRONES,
        inputs={ELECTRONIC_COMPONENTS: 1.5, STEEL: 0.8},
        labor={SkillTier.HIGHLY_SKILLED: 12, SkillTier.CHINESE_ELITE: 3},
        base_throughput=1.5,
        construction_cost_naira=120e9, construction_months=24,
        requires_power=True, min_power_reliability=0.7, min_road_quality=0.4,
        zaibatsu_affinity=3,  # IDA Corporation (Yoruba, drones since 2035)
        rainfall_sensitive=False,
        description="IDA Corporation drone manufacturing. State contract for drone swarm (2037).",
    ),
    BuildingTypeDef(
        id=BT_CLOTHING_FACTORY, name="clothing_factory", display_name="Clothing Factory",
        tier=2, output_commodity=CLOTHING,
        inputs={TEXTILES: 0.8, ELECTRICITY: 0.1},
        labor={SkillTier.UNSKILLED: 25, SkillTier.SKILLED: 5},
        base_throughput=5.0,
        construction_cost_naira=12e9, construction_months=8,
        requires_power=True, min_power_reliability=0.3, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Garment manufacturing. Labor-intensive, spreading to lower-wage northern LGAs.",
    ),

    # ===================================================================
    # TIER 3: SERVICES
    # ===================================================================
    BuildingTypeDef(
        id=BT_TELECOM_TOWER, name="telecom_tower", display_name="Telecom Tower",
        tier=3, output_commodity=TELECOMMUNICATIONS,
        inputs={ELECTRONIC_COMPONENTS: 0.5, ELECTRICITY: 0.5},
        labor={SkillTier.SKILLED: 5, SkillTier.HIGHLY_SKILLED: 8},
        base_throughput=5.0,
        construction_cost_naira=15e9, construction_months=6,
        requires_power=True, min_power_reliability=0.5, min_road_quality=0.2,
        zaibatsu_affinity=4,  # Deltel (Ngadebe, 6G towers since 2038)
        rainfall_sensitive=False,
        description="Deltel 6G infrastructure. Chinese tech partnerships.",
    ),
    BuildingTypeDef(
        id=BT_BANK_BRANCH, name="bank_branch", display_name="Bank Branch",
        tier=3, output_commodity=FINANCIAL_SERVICES,
        inputs={ELECTRICITY: 0.3, TELECOMMUNICATIONS: 0.2},
        labor={SkillTier.HIGHLY_SKILLED: 15, SkillTier.CHINESE_ELITE: 3},
        base_throughput=4.0,
        construction_cost_naira=10e9, construction_months=6,
        requires_power=True, min_power_reliability=0.5, min_road_quality=0.3,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Banking services. Naijin-dominated financial sector.",
    ),
    BuildingTypeDef(
        id=BT_ELECTRONICS_STORE, name="electronics_store", display_name="Consumer Electronics Outlet",
        tier=3, output_commodity=CONSUMER_ELECTRONICS,
        inputs={ELECTRONIC_COMPONENTS: 1.0, ELECTRICITY: 0.2},
        labor={SkillTier.SKILLED: 10, SkillTier.HIGHLY_SKILLED: 5},
        base_throughput=3.0,
        construction_cost_naira=8e9, construction_months=4,
        requires_power=True, min_power_reliability=0.4, min_road_quality=0.3,
        zaibatsu_affinity=0,  # Igwe (electronics supply chain)
        rainfall_sensitive=False,
        description="Consumer electronics retail and assembly.",
    ),
    BuildingTypeDef(
        id=BT_HOUSING_DEVELOPER, name="housing_developer", display_name="Housing Developer",
        tier=3, output_commodity=HOUSING_SERVICES,
        inputs={CONSTRUCTION_MATERIALS: 1.5},
        labor={SkillTier.UNSKILLED: 20, SkillTier.SKILLED: 8},
        base_throughput=3.0,
        construction_cost_naira=20e9, construction_months=8,
        requires_power=True, min_power_reliability=0.3, min_road_quality=0.2,
        zaibatsu_affinity=None, rainfall_sensitive=False,
        description="Housing construction. Lagos Forum padà elites restrict supply (2048 crisis).",
    ),
    BuildingTypeDef(
        id=BT_ENHANCEMENT_CLINIC, name="enhancement_clinic", display_name="Enhancement Clinic",
        tier=3, output_commodity=ENHANCEMENT_PRODUCTS,
        inputs={PHARMACEUTICALS: 0.8, CHEMICALS: 0.5},
        labor={SkillTier.HIGHLY_SKILLED: 10, SkillTier.CHINESE_ELITE: 3},
        base_throughput=2.0,
        construction_cost_naira=30e9, construction_months=10,
        requires_power=True, min_power_reliability=0.6, min_road_quality=0.3,
        zaibatsu_affinity=2,  # BUA (pharmaceutical base)
        rainfall_sensitive=False,
        description="Biological enhancement services. South-concentrated, spreading north slowly.",
    ),
]

# Quick lookups
BUILDING_TYPE_BY_ID: Dict[int, BuildingTypeDef] = {bt.id: bt for bt in BUILDING_TYPES}
BUILDING_TYPE_BY_NAME: Dict[str, BuildingTypeDef] = {bt.name: bt for bt in BUILDING_TYPES}
BUILDING_TYPES_BY_TIER: Dict[int, List[BuildingTypeDef]] = {}
for _bt in BUILDING_TYPES:
    BUILDING_TYPES_BY_TIER.setdefault(_bt.tier, []).append(_bt)

# Building type → commodity output mapping
BUILDING_FOR_COMMODITY: Dict[int, int] = {bt.output_commodity: bt.id for bt in BUILDING_TYPES}


# ---------------------------------------------------------------------------
# Zaibatsu definitions (matching existing zaibatsu.py IDs)
# ---------------------------------------------------------------------------
# 0 = Igwe Industries (Igbo, steel/electronics/vehicles)
# 1 = Danjuma (Hausa-Fulani, meat/rail/northern industry)
# 2 = BUA Group (Hausa, cement/pharma/enhancement)
# 3 = IDA Corporation (Yoruba, drones/arms)
# 4 = Deltel (Naijin-adjacent, telecom)
ZAIBATSU_NAMES = {0: "Igwe", 1: "Danjuma", 2: "BUA", 3: "IDA", 4: "Deltel"}


# ---------------------------------------------------------------------------
# Precomputed NumPy arrays for vectorized building operations
# ---------------------------------------------------------------------------
import numpy as np
from src.economy.data.zaibatsu import ZAIBATSU_BY_ID

_N_BT = 36   # number of building types
_N_C = 36    # number of commodities
_N_S = 4     # number of skill tiers

# Per building-type arrays (indexed by building type id)
BT_OUTPUT_COMMODITY = np.array([BUILDING_TYPE_BY_ID[i].output_commodity for i in range(_N_BT)], dtype=np.int32)
BT_TIER = np.array([BUILDING_TYPE_BY_ID[i].tier for i in range(_N_BT)], dtype=np.int32)
BT_REQUIRES_POWER = np.array([BUILDING_TYPE_BY_ID[i].requires_power for i in range(_N_BT)], dtype=bool)
BT_MIN_POWER = np.array([BUILDING_TYPE_BY_ID[i].min_power_reliability for i in range(_N_BT)], dtype=np.float64)
BT_RAINFALL_SENSITIVE = np.array([BUILDING_TYPE_BY_ID[i].rainfall_sensitive for i in range(_N_BT)], dtype=bool)

# Input recipe matrix: (36, 36) — bt_input_matrix[bt_id, commodity_id] = units per output
BT_INPUT_MATRIX = np.zeros((_N_BT, _N_C), dtype=np.float64)
for _bt in BUILDING_TYPES:
    for _inp_id, _inp_per in _bt.inputs.items():
        BT_INPUT_MATRIX[_bt.id, int(_inp_id)] = _inp_per

# Labor matrix: (36, 4) — bt_labor_matrix[bt_id, skill_tier] = workers
BT_LABOR_MATRIX = np.zeros((_N_BT, _N_S), dtype=np.float64)
for _bt in BUILDING_TYPES:
    for _sk, _cnt in _bt.labor.items():
        BT_LABOR_MATRIX[_bt.id, int(_sk)] = _cnt

# Zaibatsu efficiency bonus per building type
BT_ZAIBATSU_BONUS = np.ones(_N_BT, dtype=np.float64)
for _bt in BUILDING_TYPES:
    if _bt.zaibatsu_affinity is not None:
        _z = ZAIBATSU_BY_ID.get(_bt.zaibatsu_affinity)
        if _z:
            BT_ZAIBATSU_BONUS[_bt.id] = 1.0 + _z.efficiency_bonus
