"""
Lightweight per-tick sentiment update.

Runs every market tick (56/month) to give pops a fast-reacting sentiment
signal based on price changes affecting their consumption basket, plus
employment and wage changes.

This is the lightweight version — full election feedback (welfare, salience,
position shifts) still fires monthly at the structural tick.

Sentiment is a [-1, 1] score:
  -1 = extremely dissatisfied (prices spiking, no employment)
   0 = neutral
  +1 = very satisfied (prices stable/falling, good employment)
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import EconomicState, SimConfig
from src.economy.data.commodities import BASE_PRICES

logger = logging.getLogger(__name__)

# Food commodity IDs (high weight in sentiment for poor pops)
_FOOD_IDS = [6, 7, 8, 13, 18, 21]
# Energy commodity IDs
_ENERGY_IDS = [14, 20]
# Housing
_HOUSING_IDS = [34]


def tick_sentiment(state: EconomicState, config: SimConfig) -> None:
    """
    Update per-pop sentiment based on current economic conditions.

    Fast-running: designed to execute every market tick (56/month).
    Uses vectorized operations across all 174,960 pop types.
    """
    NVT = config.N_VOTER_TYPES

    if state.pop_sentiment is None or state.prices is None:
        return

    pop_lga = getattr(state, "_pop_lga_ids", None)
    pop_income_bracket = getattr(state, "_pop_income_ids", None)
    if pop_lga is None or pop_income_bracket is None:
        return

    # --- 1. Price change signal ---
    # Compare current prices to recent history
    H = state.price_history.shape[2]
    cursor = state.price_history_cursor
    # Price from ~7 ticks ago (roughly 1 day)
    lookback_idx = (cursor - 7) % H
    prev_prices = state.price_history[:, :, lookback_idx]  # (N, C)
    safe_prev = np.maximum(prev_prices, 1.0)
    price_change = (state.prices - prev_prices) / safe_prev  # (N, C) fractional change

    # Food price change per LGA (average across food commodities)
    food_change = price_change[:, _FOOD_IDS].mean(axis=1)  # (N,)
    energy_change = price_change[:, _ENERGY_IDS].mean(axis=1)  # (N,)

    # Map to pop types
    pop_food_change = food_change[pop_lga]  # (NVT,)
    pop_energy_change = energy_change[pop_lga]  # (NVT,)

    # Poor pops care more about food prices
    food_sensitivity = np.array([2.5, 1.5, 0.8], dtype=np.float64)
    energy_sensitivity = np.array([1.5, 1.0, 0.6], dtype=np.float64)

    food_impact = -pop_food_change * food_sensitivity[pop_income_bracket]
    energy_impact = -pop_energy_change * energy_sensitivity[pop_income_bracket]

    # --- 2. Employment signal ---
    employment_signal = np.zeros(NVT, dtype=np.float64)
    if state.pop_employed_formal is not None:
        # Higher formal employment = positive sentiment
        employment_signal = (state.pop_employed_formal - 0.5) * 0.3

    # --- 3. Consumption fulfillment signal ---
    fulfill_signal = np.zeros(NVT, dtype=np.float64)
    if state.pop_consumption_fulfilled is not None:
        # Low fulfillment = negative sentiment
        fulfill_signal = (state.pop_consumption_fulfilled - 0.7) * 0.5

    # --- 4. Al-Shahid security signal ---
    security_signal = np.zeros(NVT, dtype=np.float64)
    if state.alsahid_control is not None:
        control = state.alsahid_control[pop_lga]
        security_signal = -control * 0.4  # living under insurgent control is negative

    # --- 5. Infrastructure signal ---
    infra_signal = np.zeros(NVT, dtype=np.float64)
    if state.infra_power_reliability is not None:
        power = state.infra_power_reliability[pop_lga]
        # Blackouts -> negative sentiment
        infra_signal = (power - 0.6) * 0.3

    # --- Combine signals ---
    new_sentiment = (
        food_impact * 0.30
        + energy_impact * 0.15
        + employment_signal * 0.25
        + fulfill_signal * 0.15
        + security_signal * 0.10
        + infra_signal * 0.05
    )

    # EMA smoothing: sentiment changes fast but with some inertia
    alpha = 0.25  # 25% weight to new signal per tick
    state.pop_sentiment = np.clip(
        (1.0 - alpha) * state.pop_sentiment + alpha * new_sentiment,
        -1.0, 1.0,
    )
