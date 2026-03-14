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

    Optimized: computes LGA-level base signal (774 elements) per income bracket,
    then broadcasts to pops. Per-pop signals (employment, fulfillment) are
    combined in a single pass to minimize 174K-element allocations.
    """
    NVT = config.N_VOTER_TYPES

    if state.pop_sentiment is None or state.prices is None:
        return

    pop_lga = getattr(state, "_pop_lga_ids", None)
    pop_income_bracket = getattr(state, "_pop_income_ids", None)
    if pop_lga is None or pop_income_bracket is None:
        return

    N = config.N_LGAS

    # --- LGA-level signals (computed on 774 elements, not 174K) ---

    # Price changes
    H = state.price_history.shape[2]
    cursor = state.price_history_cursor
    lookback_idx = (cursor - 7) % H
    prev_prices = state.price_history[:, :, lookback_idx]  # (N, C)
    safe_prev = np.maximum(prev_prices, 1.0)
    price_change = (state.prices - prev_prices) / safe_prev  # (N, C)

    food_change = price_change[:, _FOOD_IDS].mean(axis=1)  # (N,)
    energy_change = price_change[:, _ENERGY_IDS].mean(axis=1)  # (N,)

    # Al-Shahid and infrastructure (LGA-level)
    security_lga = np.zeros(N, dtype=np.float64)
    if state.alsahid_control is not None:
        security_lga = -state.alsahid_control * 0.4

    infra_lga = np.zeros(N, dtype=np.float64)
    if state.infra_power_reliability is not None:
        infra_lga = (state.infra_power_reliability - 0.6) * 0.3

    # Precompute LGA-level base sentiment per income bracket: (N, 3)
    food_sensitivity = np.array([2.5, 1.5, 0.8], dtype=np.float64)
    energy_sensitivity = np.array([1.5, 1.0, 0.6], dtype=np.float64)

    # (N, 3) = food + energy + security + infra (broadcast to brackets)
    lga_base = np.empty((N, 3), dtype=np.float64)
    for b in range(3):
        lga_base[:, b] = (
            -food_change * food_sensitivity[b] * 0.30
            + -energy_change * energy_sensitivity[b] * 0.15
            + security_lga * 0.10
            + infra_lga * 0.05
        )

    # --- Map to pops in single pass ---
    # LGA+bracket signal
    new_sentiment = lga_base[pop_lga, pop_income_bracket]  # (NVT,)

    # Per-pop signals (combined inline)
    if state.pop_employed_formal is not None:
        new_sentiment += (state.pop_employed_formal - 0.5) * 0.3 * 0.25

    if state.pop_consumption_fulfilled is not None:
        new_sentiment += (state.pop_consumption_fulfilled - 0.7) * 0.5 * 0.15

    # EMA smoothing
    alpha = 0.25
    state.pop_sentiment *= (1.0 - alpha)
    state.pop_sentiment += alpha * new_sentiment
    np.clip(state.pop_sentiment, -1.0, 1.0, out=state.pop_sentiment)
