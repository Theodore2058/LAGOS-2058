"""
Named constants for commodity IDs.

Import from here instead of hardcoding integer IDs in system files.
Prevents the class of bugs where commodity indices are wrong (e.g., forex
using livestock ID=12 instead of crude_oil ID=0).
"""

# ── Tier 0: Raw Materials ────────────────────────────────────────────────
CRUDE_OIL = 0
NATURAL_GAS = 1
COBALT_ORE = 2
IRON_ORE = 3
LIMESTONE = 4
TIMBER = 5
STAPLE_GRAINS = 6
RICE = 7
CASSAVA = 8
COCOA_BEANS = 9
PALM_FRUIT = 10
COTTON = 11
LIVESTOCK = 12
FISH = 13

# ── Tier 1: Processed Goods ─────────────────────────────────────────────
REFINED_PETROLEUM = 14
STEEL = 15
CEMENT = 16
PROCESSED_COBALT = 17
PROCESSED_FOOD = 18
PALM_OIL = 19
ELECTRICITY = 20
MEAT_DAIRY = 21
LUMBER = 22
CHEMICALS = 23
TEXTILES = 24

# ── Tier 2: Intermediate Goods ──────────────────────────────────────────
CONSTRUCTION_MATERIALS = 25
ELECTRONIC_COMPONENTS = 26
PHARMACEUTICALS = 27
VEHICLES_MACHINERY = 28
ARMS_DRONES = 29
CLOTHING = 30

# ── Tier 3: Services ────────────────────────────────────────────────────
TELECOMMUNICATIONS = 31
FINANCIAL_SERVICES = 32
CONSUMER_ELECTRONICS = 33
HOUSING_SERVICES = 34
ENHANCEMENT_PRODUCTS = 35

# ── Commodity groups ────────────────────────────────────────────────────
FOOD_COMMODITIES = [STAPLE_GRAINS, RICE, CASSAVA, FISH, PROCESSED_FOOD, MEAT_DAIRY]
ENERGY_COMMODITIES = [REFINED_PETROLEUM, ELECTRICITY]
EXPORT_COMMODITIES = [CRUDE_OIL, NATURAL_GAS, COBALT_ORE]
