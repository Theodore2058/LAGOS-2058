"""
Dutch Disease Vulnerability Index.

Measures how dependent the economy is on a single commodity (crude oil)
and how exposed it is to resource curse dynamics:
  - Export concentration in oil/gas
  - Manufacturing sector crowding out
  - Real exchange rate overvaluation
  - Non-oil sector competitiveness erosion
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from src.economy.core.types import EconomicState, SimConfig
from src.economy.data.commodities import BASE_PRICES, COMMODITIES, CommodityTier
from src.economy.data.commodity_ids import (
    CRUDE_OIL, NATURAL_GAS, REFINED_PETROLEUM,
    COBALT_ORE, PROCESSED_COBALT,
)

logger = logging.getLogger(__name__)

# Extractive sector commodity IDs
_EXTRACTIVE_IDS = [CRUDE_OIL, NATURAL_GAS, COBALT_ORE]
_HYDROCARBON_IDS = [CRUDE_OIL, NATURAL_GAS, REFINED_PETROLEUM]


@dataclass
class DutchDiseaseIndex:
    """Composite Dutch Disease vulnerability assessment."""
    overall_index: float           # 0 (no risk) to 1 (severe)
    export_concentration: float    # HHI of export revenue
    manufacturing_share: float     # Share of GDP from manufacturing
    real_exchange_rate: float      # Overvaluation indicator (>1 = overvalued)
    non_oil_competitiveness: float # Non-oil production as fraction of capacity
    oil_revenue_dependency: float  # Oil revenue as fraction of total


def compute_dutch_disease_index(
    state: EconomicState,
    config: SimConfig,
) -> DutchDiseaseIndex:
    """
    Compute the Dutch Disease Vulnerability Index.

    Components (each 0-1, higher = more vulnerable):
    1. Export concentration: HHI of commodity production value
    2. Manufacturing share: inverse — low manufacturing = high vulnerability
    3. Real exchange rate overvaluation
    4. Non-oil competitiveness erosion
    5. Oil revenue dependency
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES

    # Total production value by commodity
    if state.actual_output is not None:
        output = state.actual_output  # (N, C)
    else:
        output = state.inventories * 0.1  # rough proxy

    prod_value = (output * state.prices).sum(axis=0)  # (C,)
    total_value = max(float(prod_value.sum()), 1.0)

    # 1. Export concentration (HHI of commodity shares)
    shares = prod_value / total_value
    hhi = float(np.sum(shares ** 2))
    # Normalize: HHI ranges from 1/C to 1.0
    export_concentration = min((hhi - 1.0 / C) / (1.0 - 1.0 / C), 1.0)

    # 2. Manufacturing share (Tier 2 + Tier 3 goods)
    mfg_ids = [c.id for c in COMMODITIES if c.tier in (CommodityTier.INTERMEDIATE, CommodityTier.SERVICE)]
    mfg_value = float(prod_value[mfg_ids].sum()) if mfg_ids else 0.0
    manufacturing_share = mfg_value / total_value

    # 3. Real exchange rate overvaluation
    # Proxy: parallel premium (higher = more overvalued official rate)
    if state.parallel_exchange_rate > 0 and state.official_exchange_rate > 0:
        reer = state.parallel_exchange_rate / state.official_exchange_rate
    else:
        reer = 1.0

    # 4. Non-oil sector competitiveness
    non_oil_ids = [i for i in range(C) if i not in _HYDROCARBON_IDS]
    if state.production_capacity is not None:
        non_oil_capacity = float(state.production_capacity[:, non_oil_ids].sum())
        non_oil_output = float(output[:, non_oil_ids].sum())
        non_oil_competitiveness = non_oil_output / max(non_oil_capacity, 1.0)
    else:
        non_oil_competitiveness = 0.5

    # 5. Oil revenue dependency
    oil_value = float(prod_value[_HYDROCARBON_IDS].sum())
    oil_dependency = oil_value / total_value

    # Composite index: weighted average
    overall = (
        0.20 * export_concentration
        + 0.20 * (1.0 - manufacturing_share)  # low mfg = high risk
        + 0.20 * min((reer - 1.0) / 0.5, 1.0)  # overvaluation
        + 0.20 * (1.0 - non_oil_competitiveness)  # low non-oil = high risk
        + 0.20 * oil_dependency
    )
    overall = float(np.clip(overall, 0.0, 1.0))

    return DutchDiseaseIndex(
        overall_index=overall,
        export_concentration=export_concentration,
        manufacturing_share=manufacturing_share,
        real_exchange_rate=reer,
        non_oil_competitiveness=non_oil_competitiveness,
        oil_revenue_dependency=oil_dependency,
    )
