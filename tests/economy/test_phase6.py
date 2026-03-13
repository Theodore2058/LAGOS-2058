"""
Phase 6 acceptance tests — Serialization, diagnostics, and API integration.

Tests save/load round-trip, diagnostic computations, and API route behavior.
"""

import copy
import os
import tempfile

import numpy as np
import pytest

from src.economy.core.types import (
    SimConfig,
    PolicyAction,
    ConstructionProject,
)
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.core.serialization import (
    save_state,
    load_state,
    state_to_snapshot,
    state_to_detailed_snapshot,
)
from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_gini_coefficient,
    compute_employment_stats,
    compute_trade_balance,
    compute_sector_output,
    compute_regional_inequality,
    compute_crisis_indicators,
    compute_price_history_series,
)


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    return initialize_state(config)


# ---------------------------------------------------------------------------
# Serialization tests
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_save_load_round_trip(self, state, config):
        """Save and load should produce identical scalar fields."""
        state.game_month = 7
        state.game_day = 33
        state.official_exchange_rate = 2000.0
        state.parallel_exchange_rate = 2500.0

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "test_save")
            save_state(state, path)
            loaded = load_state(path, config)

        assert loaded.game_month == 7
        assert loaded.game_day == 33
        assert loaded.official_exchange_rate == 2000.0
        assert loaded.parallel_exchange_rate == 2500.0

    def test_save_load_arrays(self, state, config):
        """Arrays should round-trip exactly."""
        state.prices[0, 0] = 12345.67
        state.wages[100, 2] = 999_999.0

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "test_arrays")
            save_state(state, path)
            loaded = load_state(path, config)

        np.testing.assert_array_equal(loaded.prices, state.prices)
        np.testing.assert_array_equal(loaded.wages, state.wages)

    def test_save_load_policy_queue(self, state, config):
        """Policy queue should round-trip."""
        state.policy_queue.append(PolicyAction(
            action_type="set_tax_rate",
            parameters={"tax_field": "income", "rate": 0.30},
            source="executive",
            enacted_game_day=5,
            implementation_delay=2,
        ))

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "test_policy")
            save_state(state, path)
            loaded = load_state(path, config)

        assert len(loaded.policy_queue) == 1
        assert loaded.policy_queue[0].action_type == "set_tax_rate"
        assert loaded.policy_queue[0].parameters["rate"] == 0.30

    def test_save_load_construction_projects(self, state, config):
        """Construction projects should round-trip."""
        state.construction_projects.append(ConstructionProject(
            project_type="factory",
            lga_id=42,
            commodity_id=5,
            months_remaining=6,
            monthly_cost_naira=1e9,
            monthly_labor_demand={0: 100, 1: 50},
            completion_effect={"production_capacity": {"commodity_id": 5, "amount": 100}},
        ))

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "test_construction")
            save_state(state, path)
            loaded = load_state(path, config)

        assert len(loaded.construction_projects) == 1
        assert loaded.construction_projects[0].project_type == "factory"
        assert loaded.construction_projects[0].lga_id == 42

    def test_save_load_rng_determinism(self, state, config):
        """RNG should produce same sequence after round-trip."""
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "test_rng")
            save_state(state, path)
            # Generate from original state AFTER save
            vals_before = state.rng.random(5).copy()
            loaded = load_state(path, config)

        vals_after = loaded.rng.random(5)
        np.testing.assert_array_equal(vals_before, vals_after)

    def test_save_load_after_simulation(self, state, config):
        """State after running ticks should round-trip correctly."""
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=1)

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "test_post_sim")
            save_state(state, path)
            loaded = load_state(path, config)

        assert loaded.game_month == state.game_month
        np.testing.assert_allclose(loaded.prices, state.prices, rtol=1e-10)
        np.testing.assert_allclose(loaded.wages, state.wages, rtol=1e-10)


class TestSnapshots:
    def test_snapshot_keys(self, state):
        """Snapshot should contain expected keys."""
        snap = state_to_snapshot(state)
        assert "game_month" in snap
        assert "prices" in snap
        assert isinstance(snap["prices"], dict)
        assert "mean" in snap["prices"]
        assert "shape" in snap["prices"]

    def test_snapshot_no_arrays(self, state):
        """Snapshot should not contain raw numpy arrays."""
        snap = state_to_snapshot(state)
        for key, val in snap.items():
            assert not isinstance(val, np.ndarray), f"{key} is still ndarray"

    def test_detailed_snapshot_has_data(self, state):
        """Detailed snapshot should include full array data."""
        snap = state_to_detailed_snapshot(state)
        assert "prices" in snap
        assert "data" in snap["prices"]
        assert len(snap["prices"]["data"]) == 774

    def test_detailed_snapshot_policy_queue(self, state):
        """Detailed snapshot should include policy queue."""
        state.policy_queue.append(PolicyAction(
            action_type="set_minimum_wage",
            parameters={"wage": 100_000},
            source="legislative",
            enacted_game_day=0,
            implementation_delay=0,
        ))
        snap = state_to_detailed_snapshot(state)
        assert len(snap["policy_queue"]) == 1


# ---------------------------------------------------------------------------
# Diagnostics tests
# ---------------------------------------------------------------------------

class TestDiagnosticsGDP:
    def test_gdp_positive(self, state, config):
        """GDP proxy should be positive for initialized state."""
        gdp = compute_gdp_proxy(state, config)
        assert gdp > 0

    def test_gdp_increases_with_prices(self, state, config):
        """GDP should increase when prices double."""
        gdp_before = compute_gdp_proxy(state, config)
        state.prices *= 2.0
        gdp_after = compute_gdp_proxy(state, config)
        assert gdp_after > gdp_before * 1.5


class TestDiagnosticsInflation:
    def test_inflation_near_zero_at_start(self, state, config):
        """Inflation should be near 0 at initialization (prices ≈ base)."""
        inflation = compute_inflation_proxy(state, config)
        assert abs(inflation) < 0.1

    def test_inflation_positive_after_price_increase(self, state, config):
        """Inflation should be positive after price increase."""
        state.prices *= 1.5
        inflation = compute_inflation_proxy(state, config)
        assert inflation > 0.3


class TestDiagnosticsGini:
    def test_gini_bounded(self, state):
        """Gini should be in [0, 1]."""
        gini = compute_gini_coefficient(state)
        assert 0.0 <= gini <= 1.0

    def test_gini_perfect_equality(self):
        """Gini should be ~0 when all wages are equal."""
        from src.economy.core.types import EconomicState
        state = EconomicState()
        state.wages = np.full((774, 4), 50_000.0)
        gini = compute_gini_coefficient(state)
        assert gini < 0.01


class TestDiagnosticsEmployment:
    def test_employment_stats_shape(self, state, config):
        """Employment stats should have expected structure."""
        stats = compute_employment_stats(state, config)
        assert "total_pool" in stats
        assert "employment_rate" in stats
        assert len(stats["by_tier"]) == 4

    def test_employment_rate_bounded(self, state, config):
        """Employment rate should be in [0, 1]."""
        stats = compute_employment_stats(state, config)
        assert 0.0 <= stats["employment_rate"] <= 1.0


class TestDiagnosticsTradeBalance:
    def test_trade_balance_structure(self, state):
        """Trade balance should have expected keys."""
        tb = compute_trade_balance(state)
        assert "exports" in tb
        assert "imports" in tb
        assert "balance" in tb
        assert "reserve_months" in tb


class TestDiagnosticsSectorOutput:
    def test_sector_output_length(self, state, config):
        """Should return one entry per commodity."""
        sectors = compute_sector_output(state, config)
        assert len(sectors) == 36

    def test_sector_output_names(self, state, config):
        """Each entry should have a name."""
        sectors = compute_sector_output(state, config)
        for s in sectors:
            assert "name" in s
            assert isinstance(s["name"], str)


class TestDiagnosticsRegionalInequality:
    def test_inequality_structure(self, state, config):
        """Regional inequality should have expected keys."""
        ineq = compute_regional_inequality(state, config)
        assert "top10_mean_wage" in ineq
        assert "bottom10_mean_wage" in ineq
        assert "ratio" in ineq
        assert len(ineq["top10_lgas"]) == 10
        assert len(ineq["bottom10_lgas"]) == 10

    def test_top_greater_than_bottom(self, state, config):
        """Top-10 LGAs should have higher wages than bottom-10."""
        ineq = compute_regional_inequality(state, config)
        assert ineq["top10_mean_wage"] >= ineq["bottom10_mean_wage"]


class TestDiagnosticsCrisisIndicators:
    def test_no_crises_at_start(self, state, config):
        """No crises should be flagged at initialization."""
        crises = compute_crisis_indicators(state, config)
        assert crises["food_crisis"] is False
        assert crises["inflation_crisis"] is False

    def test_food_crisis_detected(self, state, config):
        """Food crisis should trigger when food prices spike."""
        food_ids = [6, 7, 8, 13, 18, 21]
        from src.economy.data.commodities import BASE_PRICES
        for fid in food_ids:
            state.prices[:, fid] = BASE_PRICES[fid] * 4.0
        crises = compute_crisis_indicators(state, config)
        assert crises["food_crisis"] is True


class TestDiagnosticsPriceHistory:
    def test_price_history_length(self, state):
        """Price history should have 56 entries."""
        ph = compute_price_history_series(state, commodity_id=0)
        assert len(ph["prices"]) == 56


# ---------------------------------------------------------------------------
# Integration: simulation + diagnostics
# ---------------------------------------------------------------------------

class TestDiagnosticsIntegration:
    def test_diagnostics_after_simulation(self, state, config):
        """All diagnostics should work after running simulation."""
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        # All functions should complete without error
        gdp = compute_gdp_proxy(state, config)
        assert gdp > 0

        inflation = compute_inflation_proxy(state, config)
        assert isinstance(inflation, float)

        gini = compute_gini_coefficient(state)
        assert 0.0 <= gini <= 1.0

        stats = compute_employment_stats(state, config)
        assert stats["total_employed"] > 0

        tb = compute_trade_balance(state)
        assert isinstance(tb["balance"], float)

        sectors = compute_sector_output(state, config)
        assert len(sectors) == 36

        ineq = compute_regional_inequality(state, config)
        assert ineq["ratio"] >= 1.0

        crises = compute_crisis_indicators(state, config)
        assert isinstance(crises, dict)

    def test_save_load_preserves_diagnostics(self, state, config):
        """Diagnostics should give same results after save/load."""
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=1)

        gdp_before = compute_gdp_proxy(state, config)
        gini_before = compute_gini_coefficient(state)

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "diag_test")
            save_state(state, path)
            loaded = load_state(path, config)

        gdp_after = compute_gdp_proxy(loaded, config)
        gini_after = compute_gini_coefficient(loaded)

        np.testing.assert_allclose(gdp_before, gdp_after, rtol=1e-10)
        np.testing.assert_allclose(gini_before, gini_after, rtol=1e-10)
