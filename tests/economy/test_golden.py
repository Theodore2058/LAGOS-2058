"""
Golden run regression tests.

Verifies that a 6-month deterministic simulation produces results
within acceptable tolerance of the saved golden snapshot.

If the golden snapshot doesn't exist, tests are skipped.
Regenerate with: python scripts/generate_golden.py
"""

import numpy as np
import pytest
from pathlib import Path

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import BASE_PRICES
from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_gini_coefficient,
    compute_employment_stats,
)

GOLDEN_PATH = Path(__file__).parent / "golden" / "golden_6month.npz"


@pytest.fixture(scope="module")
def golden():
    """Load golden snapshot, skip if not present."""
    if not GOLDEN_PATH.exists():
        pytest.skip("Golden snapshot not found. Run: python scripts/generate_golden.py")
    return dict(np.load(str(GOLDEN_PATH), allow_pickle=True))


@pytest.fixture(scope="module")
def sim_state():
    """Run the same 6-month simulation."""
    config = SimConfig(SEED=42)
    state = initialize_state(config)
    scheduler = TickScheduler(state=state, config=config)
    results = scheduler.run_mixed_ticks(n_months=6)
    return state, config, results


class TestGoldenRegression:
    """
    Regression tests against golden snapshot.

    Tolerance is intentionally wide (20-50%) to allow for minor code
    improvements while catching catastrophic regressions.
    """

    def test_tick_count(self, golden, sim_state):
        """Tick count within expected range (tolerant of interleaving changes)."""
        _, config, results = sim_state
        # Each month: market_ticks + production_ticks + 1 structural
        n_months = 6
        expected_per_month = (
            config.MARKET_TICKS_PER_MONTH
            + config.PRODUCTION_TICKS_PER_MONTH
            + 1  # structural
        )
        expected = n_months * expected_per_month
        assert len(results) == expected

    def test_gdp_proxy(self, golden, sim_state):
        """GDP proxy within 50% of golden."""
        state, config, _ = sim_state
        actual = compute_gdp_proxy(state, config)
        expected = float(golden["gdp_proxy"])
        assert actual > expected * 0.5, f"GDP too low: {actual:.0f} vs golden {expected:.0f}"
        assert actual < expected * 2.0, f"GDP too high: {actual:.0f} vs golden {expected:.0f}"

    def test_inflation(self, golden, sim_state):
        """Inflation within reasonable range of golden."""
        state, config, _ = sim_state
        actual = compute_inflation_proxy(state, config)
        expected = float(golden["inflation"])
        # Allow wide tolerance since inflation is volatile
        assert abs(actual - expected) < max(abs(expected) * 2.0, 5.0), (
            f"Inflation diverged: {actual:.2f} vs golden {expected:.2f}"
        )

    def test_employment_rate(self, golden, sim_state):
        """Employment rate within 20% of golden."""
        state, config, _ = sim_state
        emp = compute_employment_stats(state, config)
        actual = emp["employment_rate"]
        expected = float(golden["employment_rate"])
        assert abs(actual - expected) < 0.20, (
            f"Employment rate diverged: {actual:.2f} vs golden {expected:.2f}"
        )

    def test_price_ratio_bounded(self, golden, sim_state):
        """Price ratios in same order of magnitude as golden."""
        state, _, _ = sim_state
        ratios = state.prices / BASE_PRICES[np.newaxis, :]
        expected_max = float(golden["price_ratio_max"])
        assert ratios.max() < expected_max * 5.0, (
            f"Max price ratio blew up: {ratios.max():.1f} vs golden {expected_max:.1f}"
        )

    def test_forex_reserves_positive(self, golden, sim_state):
        """Forex reserves stay positive."""
        state, _, _ = sim_state
        assert state.forex_reserves_usd > 0

    def test_population_stable(self, golden, sim_state):
        """Population within 10% of golden."""
        state, _, _ = sim_state
        actual = state.population.sum()
        expected = float(golden["population_total"])
        assert abs(actual - expected) / expected < 0.10, (
            f"Population diverged: {actual:.0f} vs golden {expected:.0f}"
        )

    def test_deterministic(self, golden, sim_state):
        """Same seed produces same tick count (basic determinism check)."""
        _, _, results = sim_state
        assert len(results) == int(golden["n_ticks"])
