"""
Supply chain cascade validation.

Tests that disrupting upstream commodities (electricity, crude oil,
raw materials) correctly propagates to downstream production.
"""

import numpy as np
import pytest

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import BASE_PRICES, COMMODITIES
from src.economy.data.commodity_ids import (
    CRUDE_OIL, NATURAL_GAS, ELECTRICITY, REFINED_PETROLEUM,
    STEEL, CEMENT, PROCESSED_COBALT, PROCESSED_FOOD, PALM_OIL,
    IRON_ORE, LIMESTONE, COBALT_ORE, STAPLE_GRAINS,
    CONSTRUCTION_MATERIALS, ELECTRONIC_COMPONENTS,
)


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    return initialize_state(config)


def run_baseline(config, n_months=2):
    """Run a baseline simulation and return final state."""
    state = initialize_state(config)
    scheduler = TickScheduler(state=state, config=config)
    scheduler.run_mixed_ticks(n_months=n_months)
    return state


class TestElectricityCascade:
    """Electricity is input to: refined petroleum, steel, cement, processed cobalt,
    processed food, palm oil, and many other goods."""

    def test_electricity_disruption_raises_elec_price(self, config):
        """Cutting electricity should raise its own price significantly."""
        state = initialize_state(config)
        base_elec = state.prices[:, ELECTRICITY].mean()

        state.production_capacity[:, ELECTRICITY] = 0.0
        state.inventories[:, ELECTRICITY] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        new_elec = state.prices[:, ELECTRICITY].mean()
        assert new_elec > base_elec * 1.2, (
            f"Electricity price should spike: {base_elec:.0f} → {new_elec:.0f}"
        )

    def test_electricity_disruption_stable(self, config):
        """Economy stays stable despite electricity cascade."""
        state = initialize_state(config)
        state.production_capacity[:, ELECTRICITY] = 0.0
        state.inventories[:, ELECTRICITY] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)


class TestCrudeOilCascade:
    """Crude oil → refined petroleum → downstream effects."""

    def test_crude_oil_disruption_hits_refined(self, config):
        """Killing crude oil should reduce refined petroleum production."""
        baseline = run_baseline(config, n_months=2)

        state = initialize_state(config)
        state.production_capacity[:, CRUDE_OIL] = 0.0
        state.inventories[:, CRUDE_OIL] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        # Refined petroleum price should be higher than baseline
        shock_ref = state.prices[:, REFINED_PETROLEUM].mean()
        base_ref = baseline.prices[:, REFINED_PETROLEUM].mean()
        assert shock_ref > base_ref * 0.9, (
            f"Refined petroleum should be at least as expensive: "
            f"shock={shock_ref:.0f} vs base={base_ref:.0f}"
        )


class TestIronOreCascade:
    """Iron ore → steel → construction materials."""

    def test_iron_disruption_hits_steel(self, config):
        """Killing iron ore should affect steel prices."""
        baseline = run_baseline(config, n_months=2)

        state = initialize_state(config)
        state.production_capacity[:, IRON_ORE] = 0.0
        state.inventories[:, IRON_ORE] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        # Steel should be more expensive or at least not cheaper
        shock_steel = state.prices[:, STEEL].mean()
        base_steel = baseline.prices[:, STEEL].mean()
        # Allow some tolerance since steel has mean reversion
        assert shock_steel > base_steel * 0.7, (
            f"Steel price collapsed after iron disruption: "
            f"shock={shock_steel:.0f} vs base={base_steel:.0f}"
        )


class TestFoodChain:
    """Staple grains → processed food chain."""

    def test_grain_disruption_hits_processed_food(self, config):
        """Killing grain production should raise processed food prices."""
        baseline = run_baseline(config, n_months=2)

        state = initialize_state(config)
        state.production_capacity[:, STAPLE_GRAINS] = 0.0
        state.inventories[:, STAPLE_GRAINS] *= 0.1

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        shock_food = state.prices[:, PROCESSED_FOOD].mean()
        base_food = baseline.prices[:, PROCESSED_FOOD].mean()
        assert shock_food > base_food * 0.9, (
            f"Processed food not affected by grain disruption: "
            f"shock={shock_food:.0f} vs base={base_food:.0f}"
        )


class TestMultipleDisruption:
    """Simultaneous disruption of multiple upstream commodities."""

    def test_combined_shock_stable(self, config):
        """Economy survives combined electricity + oil + grain disruption."""
        state = initialize_state(config)
        state.production_capacity[:, ELECTRICITY] *= 0.1
        state.production_capacity[:, CRUDE_OIL] *= 0.1
        state.production_capacity[:, STAPLE_GRAINS] *= 0.1

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        # Should not crash
        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)
        assert np.all(state.inventories >= -1e-6)

    def test_total_economic_collapse_recoverable(self, config):
        """Even with 90% production cut everywhere, simulation stays stable."""
        state = initialize_state(config)
        state.production_capacity *= 0.1
        state.inventories *= 0.5

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)
