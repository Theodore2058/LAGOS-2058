"""
All 36 commodity definitions for the LAGOS-2058 economy.

Organized by tier:
  Tier 0 (RAW):          IDs  0-13   (14 commodities)
  Tier 1 (PROCESSED):    IDs 14-24   (11 commodities)
  Tier 2 (INTERMEDIATE): IDs 25-30   ( 6 commodities)
  Tier 3 (SERVICE):      IDs 31-35   ( 5 commodities)
"""

from src.economy.core.types import CommodityDef, CommodityTier, SkillTier

COMMODITIES: list[CommodityDef] = [
    # ===== TIER 0: RAW MATERIALS =====
    CommodityDef(
        id=0, name="crude_oil", tier=CommodityTier.RAW,
        base_price=800_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 5.0, SkillTier.SKILLED: 2.0},
        primary_lgas=[], is_importable=False, is_exportable=True,
        spoilage_rate=0.0, demand_elasticity=-0.3,
    ),
    CommodityDef(
        id=1, name="natural_gas", tier=CommodityTier.RAW,
        base_price=400_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 3.0, SkillTier.SKILLED: 2.0},
        primary_lgas=[], is_importable=False, is_exportable=True,
        spoilage_rate=0.0, demand_elasticity=-0.2,
    ),
    CommodityDef(
        id=2, name="cobalt_ore", tier=CommodityTier.RAW,
        base_price=1_200_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 8.0, SkillTier.SKILLED: 3.0},
        primary_lgas=[], is_importable=False, is_exportable=True,
        spoilage_rate=0.0, demand_elasticity=-0.2,
    ),
    CommodityDef(
        id=3, name="iron_ore", tier=CommodityTier.RAW,
        base_price=80_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 6.0, SkillTier.SKILLED: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=4, name="limestone", tier=CommodityTier.RAW,
        base_price=40_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 4.0},
        primary_lgas=[], is_importable=False, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.5,
    ),
    CommodityDef(
        id=5, name="timber", tier=CommodityTier.RAW,
        base_price=60_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 5.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.001, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=6, name="staple_grains", tier=CommodityTier.RAW,
        base_price=30_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 8.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.005, demand_elasticity=-0.3,
    ),
    CommodityDef(
        id=7, name="rice", tier=CommodityTier.RAW,
        base_price=50_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 7.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.003, demand_elasticity=-0.25,
    ),
    CommodityDef(
        id=8, name="cassava", tier=CommodityTier.RAW,
        base_price=20_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 5.0},
        primary_lgas=[], is_importable=False, is_exportable=False,
        spoilage_rate=0.008, demand_elasticity=-0.35,
    ),
    CommodityDef(
        id=9, name="cocoa_beans", tier=CommodityTier.RAW,
        base_price=200_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 6.0},
        primary_lgas=[], is_importable=False, is_exportable=True,
        spoilage_rate=0.004, demand_elasticity=-0.5,
    ),
    CommodityDef(
        id=10, name="palm_fruit", tier=CommodityTier.RAW,
        base_price=80_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 5.0},
        primary_lgas=[], is_importable=False, is_exportable=True,
        spoilage_rate=0.006, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=11, name="cotton", tier=CommodityTier.RAW,
        base_price=45_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 6.0},
        primary_lgas=[], is_importable=True, is_exportable=True,
        spoilage_rate=0.001, demand_elasticity=-0.5,
    ),
    CommodityDef(
        id=12, name="livestock", tier=CommodityTier.RAW,
        base_price=150_000, production_type="cobb_douglas",
        inputs={6: 0.3},
        labor_requirements={SkillTier.UNSKILLED: 4.0},
        primary_lgas=[], is_importable=False, is_exportable=False,
        spoilage_rate=0.002, demand_elasticity=-0.3,
    ),
    CommodityDef(
        id=13, name="fish", tier=CommodityTier.RAW,
        base_price=90_000, production_type="cobb_douglas",
        inputs={},
        labor_requirements={SkillTier.UNSKILLED: 5.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.015, demand_elasticity=-0.35,
    ),

    # ===== TIER 1: PROCESSED INPUTS =====
    CommodityDef(
        id=14, name="refined_petroleum", tier=CommodityTier.PROCESSED,
        base_price=600_000, production_type="leontief",
        inputs={0: 1.2, 20: 0.3},
        labor_requirements={SkillTier.SKILLED: 3.0, SkillTier.HIGHLY_SKILLED: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=True,
        spoilage_rate=0.0, demand_elasticity=-0.2,
    ),
    CommodityDef(
        id=15, name="steel", tier=CommodityTier.PROCESSED,
        base_price=200_000, production_type="leontief",
        inputs={3: 2.0, 20: 0.5, 1: 0.3},
        labor_requirements={SkillTier.SKILLED: 4.0, SkillTier.HIGHLY_SKILLED: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=16, name="cement", tier=CommodityTier.PROCESSED,
        base_price=100_000, production_type="leontief",
        inputs={4: 1.5, 20: 0.4, 1: 0.2},
        labor_requirements={SkillTier.SKILLED: 3.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=17, name="processed_cobalt", tier=CommodityTier.PROCESSED,
        base_price=2_000_000, production_type="leontief",
        inputs={2: 3.0, 20: 0.8},
        labor_requirements={SkillTier.SKILLED: 2.0, SkillTier.HIGHLY_SKILLED: 2.0},
        primary_lgas=[], is_importable=False, is_exportable=True,
        spoilage_rate=0.0, demand_elasticity=-0.3,
    ),
    CommodityDef(
        id=18, name="processed_food", tier=CommodityTier.PROCESSED,
        base_price=60_000, production_type="leontief",
        inputs={6: 0.5, 8: 0.3, 7: 0.3, 20: 0.2},
        labor_requirements={SkillTier.UNSKILLED: 3.0, SkillTier.SKILLED: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.008, demand_elasticity=-0.25,
    ),
    CommodityDef(
        id=19, name="palm_oil", tier=CommodityTier.PROCESSED,
        base_price=120_000, production_type="leontief",
        inputs={10: 1.5, 20: 0.2},
        labor_requirements={SkillTier.UNSKILLED: 2.0, SkillTier.SKILLED: 1.0},
        primary_lgas=[], is_importable=False, is_exportable=True,
        spoilage_rate=0.003, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=20, name="electricity", tier=CommodityTier.PROCESSED,
        base_price=80_000, production_type="cobb_douglas",
        inputs={1: 0.8},
        labor_requirements={SkillTier.SKILLED: 2.0, SkillTier.HIGHLY_SKILLED: 1.0},
        primary_lgas=[], is_importable=False, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.15,
    ),
    CommodityDef(
        id=21, name="meat_dairy", tier=CommodityTier.PROCESSED,
        base_price=180_000, production_type="leontief",
        inputs={12: 1.0, 20: 0.2},
        labor_requirements={SkillTier.UNSKILLED: 2.0, SkillTier.SKILLED: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.012, demand_elasticity=-0.3,
    ),
    CommodityDef(
        id=22, name="lumber", tier=CommodityTier.PROCESSED,
        base_price=90_000, production_type="leontief",
        inputs={5: 1.2, 20: 0.2},
        labor_requirements={SkillTier.UNSKILLED: 3.0, SkillTier.SKILLED: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.001, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=23, name="chemicals", tier=CommodityTier.PROCESSED,
        base_price=150_000, production_type="leontief",
        inputs={1: 0.5},
        labor_requirements={SkillTier.SKILLED: 2.0, SkillTier.HIGHLY_SKILLED: 2.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=24, name="textiles", tier=CommodityTier.PROCESSED,
        base_price=100_000, production_type="leontief",
        inputs={11: 1.0, 20: 0.2, 23: 0.1},
        labor_requirements={SkillTier.UNSKILLED: 4.0, SkillTier.SKILLED: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=True,
        spoilage_rate=0.0, demand_elasticity=-0.5,
    ),

    # ===== TIER 2: INTERMEDIATE GOODS =====
    CommodityDef(
        id=25, name="construction_materials", tier=CommodityTier.INTERMEDIATE,
        base_price=130_000, production_type="leontief",
        inputs={15: 0.5, 16: 0.8, 22: 0.3},
        labor_requirements={SkillTier.UNSKILLED: 3.0, SkillTier.SKILLED: 2.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.3,
    ),
    CommodityDef(
        id=26, name="electronic_components", tier=CommodityTier.INTERMEDIATE,
        base_price=350_000, production_type="leontief",
        inputs={17: 0.5, 20: 0.3},
        labor_requirements={
            SkillTier.SKILLED: 2.0, SkillTier.HIGHLY_SKILLED: 3.0,
            SkillTier.CHINESE_ELITE: 0.5,
        },
        primary_lgas=[], is_importable=True, is_exportable=True,
        spoilage_rate=0.0, demand_elasticity=-0.3,
    ),
    CommodityDef(
        id=27, name="pharmaceuticals", tier=CommodityTier.INTERMEDIATE,
        base_price=400_000, production_type="leontief",
        inputs={23: 1.0, 20: 0.3},
        labor_requirements={SkillTier.HIGHLY_SKILLED: 4.0, SkillTier.CHINESE_ELITE: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.002, demand_elasticity=-0.2,
    ),
    CommodityDef(
        id=28, name="vehicles_machinery", tier=CommodityTier.INTERMEDIATE,
        base_price=500_000, production_type="leontief",
        inputs={15: 1.0, 26: 0.5},
        labor_requirements={SkillTier.SKILLED: 4.0, SkillTier.HIGHLY_SKILLED: 2.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=29, name="arms_drones", tier=CommodityTier.INTERMEDIATE,
        base_price=600_000, production_type="leontief",
        inputs={26: 1.5, 15: 0.8},
        labor_requirements={SkillTier.HIGHLY_SKILLED: 3.0, SkillTier.CHINESE_ELITE: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.1,
    ),
    CommodityDef(
        id=30, name="clothing", tier=CommodityTier.INTERMEDIATE,
        base_price=70_000, production_type="leontief",
        inputs={24: 0.8, 20: 0.1},
        labor_requirements={SkillTier.UNSKILLED: 5.0, SkillTier.SKILLED: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=True,
        spoilage_rate=0.0, demand_elasticity=-0.6,
    ),

    # ===== TIER 3: SERVICES AND FINAL GOODS =====
    CommodityDef(
        id=31, name="telecommunications", tier=CommodityTier.SERVICE,
        base_price=300_000, production_type="leontief",
        inputs={26: 0.5, 20: 0.5},
        labor_requirements={SkillTier.SKILLED: 2.0, SkillTier.HIGHLY_SKILLED: 3.0},
        primary_lgas=[], is_importable=False, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.3,
    ),
    CommodityDef(
        id=32, name="financial_services", tier=CommodityTier.SERVICE,
        base_price=300_000, production_type="cobb_douglas",
        inputs={20: 0.3, 31: 0.2},
        labor_requirements={SkillTier.HIGHLY_SKILLED: 5.0, SkillTier.CHINESE_ELITE: 1.0},
        primary_lgas=[], is_importable=False, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.4,
    ),
    CommodityDef(
        id=33, name="consumer_electronics", tier=CommodityTier.SERVICE,
        base_price=250_000, production_type="leontief",
        inputs={26: 1.0, 20: 0.2},
        labor_requirements={SkillTier.SKILLED: 3.0, SkillTier.HIGHLY_SKILLED: 2.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.5,
    ),
    CommodityDef(
        id=34, name="housing_services", tier=CommodityTier.SERVICE,
        base_price=200_000, production_type="leontief",
        inputs={25: 1.5},
        labor_requirements={SkillTier.UNSKILLED: 5.0, SkillTier.SKILLED: 2.0},
        primary_lgas=[], is_importable=False, is_exportable=False,
        spoilage_rate=0.0, demand_elasticity=-0.2,
    ),
    CommodityDef(
        id=35, name="enhancement_products", tier=CommodityTier.SERVICE,
        base_price=500_000, production_type="leontief",
        inputs={27: 0.8, 23: 0.5},
        labor_requirements={SkillTier.HIGHLY_SKILLED: 3.0, SkillTier.CHINESE_ELITE: 1.0},
        primary_lgas=[], is_importable=True, is_exportable=False,
        spoilage_rate=0.005, demand_elasticity=-0.6,
    ),
]

# Quick lookups
COMMODITY_BY_ID: dict[int, CommodityDef] = {c.id: c for c in COMMODITIES}
COMMODITY_BY_NAME: dict[str, CommodityDef] = {c.name: c for c in COMMODITIES}

# Tier groupings (processing order matters: lower tiers first)
COMMODITIES_BY_TIER: dict[int, list[CommodityDef]] = {}
for _c in COMMODITIES:
    COMMODITIES_BY_TIER.setdefault(int(_c.tier), []).append(_c)

# Base price vector for fast lookups
import numpy as np

BASE_PRICES = np.array([c.base_price for c in COMMODITIES], dtype=np.float64)
SPOILAGE_RATES = np.array([c.spoilage_rate for c in COMMODITIES], dtype=np.float64)
DEMAND_ELASTICITIES = np.array([c.demand_elasticity for c in COMMODITIES], dtype=np.float64)
