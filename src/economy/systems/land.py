"""
Land market system — prices, conversion, zoning, housing supply.

Called once per structural tick (monthly).
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import EconomicState, LandMutations, SimConfig, LandType

logger = logging.getLogger(__name__)

# Commodity index ranges used for demand signals
# Agricultural: staple_grains(6) through fish(13) — excludes crude_oil, gas, minerals
_AGRI_COMMODITY_IDS = list(range(6, 14))
_SERVICE_COMMODITY_IDS = list(range(31, 36))    # service-sector commodities
_MANUFACTURING_COMMODITY_IDS = list(range(14, 31))  # processed + intermediate goods

# Land conversion rate: fraction of price-differential-driven reallocation per month
_CONVERSION_RATE = 0.01


def tick_land(state: EconomicState, config: SimConfig) -> LandMutations:
    """
    Full land market tick.

    1. Compute demand signals for each land type
    2. Adjust land prices toward equilibrium
    3. Convert land between types based on price differentials
    4. Enforce zoning restrictions and conservation
    5. Compute housing supply change
    """
    N = config.N_LGAS
    L = config.N_LAND_TYPES

    # --- 1. Demand signals (unitless, higher = more demand) ---
    demand = _compute_demand_signals(state, config)

    # --- 2. Price adjustment ---
    land_prices_new = _adjust_prices(state.land_prices, demand, config)

    # --- 3. Land conversion ---
    land_area_new = _convert_land(
        state.land_area, land_prices_new, state.land_total,
        state.zoning_restriction, state.population, config,
    )

    # --- 4. Housing supply change ---
    residential_delta = land_area_new[:, LandType.RESIDENTIAL] - state.land_area[:, LandType.RESIDENTIAL]
    housing_supply_change = residential_delta  # hectares of residential land gained/lost

    return LandMutations(
        land_area_new=land_area_new,
        land_prices_new=land_prices_new,
        housing_supply_change=housing_supply_change,
    )


def _compute_demand_signals(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute relative demand for each land type per LGA.

    Returns: (N, 4) demand signals, higher = more pressure.
    """
    N = config.N_LGAS
    demand = np.zeros((N, config.N_LAND_TYPES), dtype=np.float64)

    # Farmland: driven by agricultural output value
    agri_value = np.zeros(N, dtype=np.float64)
    for c in _AGRI_COMMODITY_IDS:
        if c < state.production_capacity.shape[1]:
            agri_value += state.production_capacity[:, c] * state.prices[:, c]
    # Normalize by current farmland area to get per-hectare value
    safe_farmland = np.maximum(state.land_area[:, LandType.FARMLAND], 1.0)
    demand[:, LandType.FARMLAND] = agri_value / safe_farmland

    # Residential: driven by population density and wages
    safe_residential = np.maximum(state.land_area[:, LandType.RESIDENTIAL], 1.0)
    pop_density = state.population / safe_residential
    avg_wage = state.wages.mean(axis=1)  # average across skill tiers
    demand[:, LandType.RESIDENTIAL] = pop_density * avg_wage

    # Commercial: driven by service sector activity
    service_value = np.zeros(N, dtype=np.float64)
    for c in _SERVICE_COMMODITY_IDS:
        if c < state.production_capacity.shape[1]:
            service_value += state.production_capacity[:, c] * state.prices[:, c]
    safe_commercial = np.maximum(state.land_area[:, LandType.COMMERCIAL], 1.0)
    demand[:, LandType.COMMERCIAL] = service_value / safe_commercial

    # Industrial: driven by manufacturing output
    mfg_value = np.zeros(N, dtype=np.float64)
    for c in _MANUFACTURING_COMMODITY_IDS:
        if c < state.production_capacity.shape[1]:
            mfg_value += state.production_capacity[:, c] * state.prices[:, c]
    safe_industrial = np.maximum(state.land_area[:, LandType.INDUSTRIAL], 1.0)
    demand[:, LandType.INDUSTRIAL] = mfg_value / safe_industrial

    # Normalize each column to [0, 1] range for stable price adjustment
    for t in range(config.N_LAND_TYPES):
        col = demand[:, t]
        col_max = col.max()
        if col_max > 0:
            demand[:, t] = col / col_max

    return demand


def _adjust_prices(
    current_prices: np.ndarray,  # (N, 4)
    demand: np.ndarray,          # (N, 4) normalized 0-1
    config: SimConfig,
) -> np.ndarray:
    """
    Adjust land prices based on demand signals.

    Price moves toward demand-implied equilibrium at LAND_PRICE_ADJUSTMENT_SPEED.
    Prices are sticky downward (half speed for decreases).
    """
    speed = config.LAND_PRICE_ADJUSTMENT_SPEED

    # Demand centered at 0.5 → positive means excess demand, negative means excess supply
    excess = demand - 0.5
    price_change = speed * excess

    # Sticky downward: halve negative adjustments
    price_change = np.where(price_change < 0, price_change * 0.5, price_change)

    # Clamp per-tick change
    price_change = np.clip(price_change, -0.05, 0.10)

    new_prices = current_prices * (1.0 + price_change)

    # Floor: prices cannot go below 1.0 naira/hectare
    new_prices = np.maximum(new_prices, 1.0)

    return new_prices


def _convert_land(
    land_area: np.ndarray,          # (N, 4)
    land_prices: np.ndarray,        # (N, 4)
    land_total: np.ndarray,         # (N,)
    zoning_restriction: np.ndarray, # (N,)
    population: np.ndarray,         # (N,)
    config: SimConfig,
) -> np.ndarray:
    """
    Convert land between types based on price differentials.

    Higher-priced types attract land from lower-priced types.
    Conversion is slow (~1% of differential per month) and limited by zoning.
    Total land per LGA is conserved.
    """
    N = config.N_LGAS
    L = config.N_LAND_TYPES
    area = land_area.copy()

    # Effective conversion rate reduced by zoning restriction (0 = no restriction, 1 = fully restricted)
    effective_rate = _CONVERSION_RATE * (1.0 - zoning_restriction)  # (N,)

    # Compute average price per LGA as reference
    avg_price = land_prices.mean(axis=1, keepdims=True)  # (N, 1)
    safe_avg = np.maximum(avg_price, 1.0)

    # Price differential relative to average: positive = attractive, negative = donor
    price_diff = (land_prices - avg_price) / safe_avg  # (N, 4)

    # Conversion flow: each type gains/loses proportional to its price differential
    # Positive diff → gains land, negative diff → loses land
    flow = effective_rate[:, np.newaxis] * price_diff * area  # (N, 4)

    # Apply flow
    area_new = area + flow

    # Enforce non-negativity: no land type can go below zero
    area_new = np.maximum(area_new, 0.0)

    # Enforce conservation: renormalize so sum matches land_total
    row_sums = area_new.sum(axis=1, keepdims=True)  # (N, 1)
    safe_sums = np.maximum(row_sums, 1.0)  # prevent amplification from near-zero sums
    area_new = area_new * (land_total[:, np.newaxis] / safe_sums)
    # Cap individual land types to total (prevents renormalization overshoot)
    area_new = np.minimum(area_new, land_total[:, np.newaxis])

    return area_new


def apply_land_mutations(state: EconomicState, mutations: LandMutations) -> None:
    """Apply land tick results to state."""
    state.land_area = mutations.land_area_new
    state.land_prices = mutations.land_prices_new
