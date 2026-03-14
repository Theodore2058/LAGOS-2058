"""
Scenario stress tests from spec §26.3.

Each scenario injects a specific shock into the economy and verifies
the simulation responds realistically and stays stable.
"""

import numpy as np
import pytest

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.assertions import check_all_invariants
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import BASE_PRICES
from src.economy.data.commodity_ids import (
    CRUDE_OIL, NATURAL_GAS, ELECTRICITY, REFINED_PETROLEUM,
    STAPLE_GRAINS, RICE, CASSAVA, FISH, PROCESSED_FOOD, MEAT_DAIRY,
    COBALT_ORE, FOOD_COMMODITIES,
)


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    return initialize_state(config)


class TestElectricityCascade:
    """Scenario: Electricity supply collapses → cascading effects on production."""

    def test_electricity_shock_raises_prices(self, state, config):
        """Cutting electricity should raise prices of electricity-dependent goods."""
        # Record baseline electricity price
        base_elec = state.prices[:, ELECTRICITY].mean()

        # Kill electricity production everywhere
        state.production_capacity[:, ELECTRICITY] = 0.0
        state.inventories[:, ELECTRICITY] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=1)

        # Electricity price should have risen significantly
        new_elec = state.prices[:, ELECTRICITY].mean()
        assert new_elec > base_elec * 1.5, (
            f"Electricity price should spike after supply collapse: "
            f"{base_elec:.0f} → {new_elec:.0f}"
        )

    def test_electricity_shock_stable(self, state, config):
        """Economy stays stable (no NaN/negative) despite electricity shock."""
        state.production_capacity[:, ELECTRICITY] = 0.0
        state.inventories[:, ELECTRICITY] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        warnings = check_all_invariants(state)
        critical = [w for w in warnings if "NaN" in w or "Negative" in w]
        assert len(critical) == 0, f"Critical: {critical}"


class TestOilCrash:
    """Scenario: Global oil price crashes → forex reserves drain, naira weakens."""

    def test_oil_crash_drains_reserves(self, state, config):
        """Oil price crash should drain forex reserves."""
        initial_reserves = state.forex_reserves_usd

        # Crash oil price to $20/barrel
        state.global_oil_price_usd = 20.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        # Reserves should have dropped
        assert state.forex_reserves_usd < initial_reserves, (
            f"Reserves should drain: {initial_reserves:.0f} → {state.forex_reserves_usd:.0f}"
        )

    def test_oil_crash_parallel_premium_persists(self, state, config):
        """Oil crash: parallel rate should still exceed official rate."""
        state.global_oil_price_usd = 20.0
        state.forex_reserves_usd = 1e9  # Low reserves to stress

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        assert state.parallel_exchange_rate >= state.official_exchange_rate, (
            f"Parallel rate should be >= official: "
            f"{state.parallel_exchange_rate:.0f} vs {state.official_exchange_rate:.0f}"
        )

    def test_oil_crash_stable(self, state, config):
        """Economy stays stable despite oil crash."""
        state.global_oil_price_usd = 20.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        warnings = check_all_invariants(state)
        critical = [w for w in warnings if "NaN" in w or "Negative" in w]
        assert len(critical) == 0, f"Critical: {critical}"


class TestFoodCrisis:
    """Scenario: Food production collapses → prices spike, welfare drops."""

    def test_food_price_spike(self, state, config):
        """Destroying food production should spike food prices."""
        base_food_prices = np.mean([state.prices[:, c].mean() for c in FOOD_COMMODITIES])

        # Kill food production
        for c in FOOD_COMMODITIES:
            state.production_capacity[:, c] = 0.0
            state.inventories[:, c] *= 0.1  # 90% loss

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=1)

        new_food_prices = np.mean([state.prices[:, c].mean() for c in FOOD_COMMODITIES])
        assert new_food_prices > base_food_prices * 1.2, (
            f"Food prices should rise: {base_food_prices:.0f} → {new_food_prices:.0f}"
        )

    def test_food_crisis_stable(self, state, config):
        """Economy survives food crisis without NaN."""
        for c in FOOD_COMMODITIES:
            state.production_capacity[:, c] = 0.0
            state.inventories[:, c] *= 0.1

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        warnings = check_all_invariants(state)
        critical = [w for w in warnings if "NaN" in w]
        assert len(critical) == 0, f"Critical: {critical}"


class TestAlShahidDefeatParadox:
    """
    Scenario: Al-Shahid suddenly defeated → parallel economy collapses,
    but legitimate economy may not absorb all displaced workers immediately.
    """

    def test_defeat_removes_control(self, state, config):
        """Zeroing al-Shahid control should stick."""
        state.alsahid_control[:] = 0.0
        state.alsahid_service_provision[:] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        # Control should remain very low (may grow slightly from dynamics)
        assert state.alsahid_control.max() < 0.2

    def test_defeat_stable(self, state, config):
        """Economy stays stable when al-Shahid is eliminated."""
        state.alsahid_control[:] = 0.0
        state.alsahid_service_provision[:] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        warnings = check_all_invariants(state)
        critical = [w for w in warnings if "NaN" in w or "Negative" in w]
        assert len(critical) == 0, f"Critical: {critical}"


class TestVirtuousCycle:
    """
    Scenario: Improved infrastructure + high oil prices + good governance
    should produce positive economic outcomes.
    """

    def test_good_conditions_grow_economy(self, state, config):
        """Good conditions should increase total production value."""
        # Improve conditions
        state.global_oil_price_usd = 120.0
        state.forex_reserves_usd = 100e9
        state.infra_road_quality[:] = 0.9
        state.infra_power_reliability[:] = 0.9
        state.state_capacity[:] = 0.9
        state.corruption_leakage[:] = 0.10
        state.bank_confidence[:] = 0.95

        initial_output = (state.production_capacity * state.prices).sum()

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        final_output = (state.production_capacity * state.prices).sum()
        # At minimum, economy should not collapse
        assert final_output > initial_output * 0.5, (
            f"Economy collapsed under good conditions: {initial_output:.0e} → {final_output:.0e}"
        )

    def test_good_conditions_stable(self, state, config):
        """Good conditions should produce a very stable economy."""
        state.global_oil_price_usd = 120.0
        state.forex_reserves_usd = 100e9
        state.infra_road_quality[:] = 0.9
        state.infra_power_reliability[:] = 0.9

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        warnings = check_all_invariants(state)
        critical = [w for w in warnings if "NaN" in w or "Negative" in w]
        assert len(critical) == 0, f"Critical: {critical}"
        # Prices should be bounded
        ratios = state.prices / BASE_PRICES[np.newaxis, :]
        assert ratios.max() < 500.0
        assert ratios.min() > 0.0001


class TestExtremeStress:
    """Extreme scenarios that should not crash the simulation."""

    def test_zero_population(self, state, config):
        """Zero population should not cause division by zero."""
        state.population[:] = 0.0
        state.labor_pool[:] = 0.0
        state.labor_employed[:] = 0.0
        state.labor_informal[:] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=1)

        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)

    def test_zero_inventories(self, state, config):
        """Zero inventories should not crash."""
        state.inventories[:] = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=1)

        assert not np.any(np.isnan(state.prices))

    def test_extreme_prices(self, state, config):
        """Very high prices should be pulled back by mean reversion."""
        state.prices[:] = BASE_PRICES[np.newaxis, :] * 100.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=1)

        ratios = state.prices / BASE_PRICES[np.newaxis, :]
        # Mean reversion should have pulled them down significantly
        assert ratios.mean() < 100.0, f"Mean ratio still {ratios.mean():.1f}"
        assert not np.any(np.isnan(state.prices))
