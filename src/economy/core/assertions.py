"""
Economic invariant checks — run after every tick.

Violations of these invariants indicate bugs, not tuning issues.
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import EconomicState

logger = logging.getLogger(__name__)


class SimulationInvariantError(Exception):
    """Raised when an economic invariant is violated."""
    pass


def check_all_invariants(state: EconomicState, strict: bool = False) -> list[str]:
    """
    Run all invariant checks. Returns list of warning messages.
    If strict=True, raises SimulationInvariantError on first violation.
    """
    warnings = []

    def _check(condition: bool, msg: str) -> None:
        if not condition:
            warnings.append(msg)
            if strict:
                raise SimulationInvariantError(msg)
            logger.warning("INVARIANT: %s", msg)

    # 1. No negative prices
    if state.prices is not None:
        _check(np.all(state.prices > 0), "Negative or zero price detected")

    # 2. No negative inventories (with small tolerance)
    if state.inventories is not None:
        _check(
            np.all(state.inventories >= -1e-3),
            f"Negative inventory: min={state.inventories.min():.6f}",
        )

    # 3. No negative populations
    if state.population is not None:
        _check(np.all(state.population >= 0), "Negative population")

    # 4. Labor employed <= labor available
    if state.labor_employed is not None and state.labor_pool is not None:
        excess = state.labor_employed - state.labor_pool
        _check(
            np.all(excess <= 1e-3),
            f"Employed > available: max excess={excess.max():.0f}",
        )

    # 5. Land use <= total land
    if state.land_area is not None and state.land_total is not None:
        land_sum = state.land_area.sum(axis=1)
        _check(
            np.all(land_sum <= state.land_total + 1e-3),
            "Land use exceeds total",
        )

    # 6. Bank loans bounded by deposits / reserve_ratio (with 10% slack)
    if state.bank_deposits is not None and state.bank_loans is not None:
        max_loans = state.bank_deposits / 0.15
        _check(
            np.all(state.bank_loans <= max_loans * 1.1),
            "Excessive lending beyond reserve ratio",
        )

    # 7. Exchange rates positive, parallel >= official
    _check(state.official_exchange_rate > 0, "Negative official exchange rate")
    _check(
        state.parallel_exchange_rate >= state.official_exchange_rate,
        "Parallel rate below official",
    )

    # 8. Al-Shahid control bounded [0, 1]
    if state.alsahid_control is not None:
        _check(
            np.all(state.alsahid_control >= 0) and np.all(state.alsahid_control <= 1),
            "Al-Shahid control out of [0,1]",
        )

    # 9. Enhancement adoption bounded [0, 1]
    if state.enhancement_adoption is not None:
        _check(
            np.all(state.enhancement_adoption >= 0) and np.all(state.enhancement_adoption <= 1),
            "Enhancement adoption out of [0,1]",
        )

    # 10. No NaN or Inf in critical arrays
    for attr_name in [
        "prices", "inventories", "production_capacity", "wages",
        "labor_pool", "land_area", "bank_deposits",
        "pop_income", "pop_sentiment", "pop_standard_of_living",
    ]:
        arr = getattr(state, attr_name, None)
        if arr is not None:
            _check(not np.any(np.isnan(arr)), f"NaN in {attr_name}")
            _check(not np.any(np.isinf(arr)), f"Inf in {attr_name}")

    return warnings
