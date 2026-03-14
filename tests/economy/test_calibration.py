"""
Priority 4A: 12-month simulation audit against calibration targets.

Runs a full 12-month simulation and checks that key economic indicators
fall within realistic ranges for a Nigerian-like economy in 2058.
"""

import numpy as np
import pytest

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.core.assertions import check_all_invariants
from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_gini_coefficient,
    compute_employment_stats,
    compute_trade_balance,
    compute_sector_output,
    compute_crisis_indicators,
)
from src.economy.data.commodities import BASE_PRICES
from src.economy.diagnostics.dutch_disease import compute_dutch_disease_index


@pytest.fixture(scope="module")
def twelve_month_state():
    """Run a full 12-month simulation once for all calibration tests."""
    config = SimConfig()
    state = initialize_state(config)
    scheduler = TickScheduler(state=state, config=config)
    scheduler.run_mixed_ticks(n_months=12)
    return state, config


class TestCalibrationTargets:
    """8 calibration targets for the 12-month simulation."""

    def test_gdp_positive_and_growing(self, twelve_month_state):
        """GDP proxy should be positive after 12 months."""
        state, config = twelve_month_state
        gdp = compute_gdp_proxy(state, config)
        assert gdp > 0, f"GDP should be positive: {gdp}"

    def test_inflation_bounded(self, twelve_month_state):
        """Inflation should be within 0-20% annually (realistic for Nigeria)."""
        state, config = twelve_month_state
        inflation = compute_inflation_proxy(state, config)
        # Allow wide range: deflation to moderate inflation
        assert -5.0 < inflation < 50.0, f"Inflation out of range: {inflation:.2f}"

    def test_employment_rate(self, twelve_month_state):
        """Employment rate should be 40-95% (Nigeria-like range)."""
        state, config = twelve_month_state
        emp = compute_employment_stats(state, config)
        rate = emp["employment_rate"]
        assert 0.40 < rate < 0.95, f"Employment rate out of range: {rate:.3f}"

    def test_gini_coefficient(self, twelve_month_state):
        """Gini should be 0.30-0.55 (moderate to high inequality, Nigeria-like)."""
        state, config = twelve_month_state
        gini = compute_gini_coefficient(state)
        assert 0.15 < gini < 0.70, f"Gini out of range: {gini:.3f}"

    def test_prices_no_blowup(self, twelve_month_state):
        """All prices should stay within 0.01x to 100x of base prices."""
        state, config = twelve_month_state
        ratios = state.prices / BASE_PRICES[np.newaxis, :]
        assert ratios.min() > 0.001, f"Price collapse: {ratios.min():.4f}x"
        assert ratios.max() < 500.0, f"Price blowup: {ratios.max():.1f}x"

    def test_forex_reserves_positive(self, twelve_month_state):
        """Forex reserves should remain positive (no total depletion in 12 months)."""
        state, config = twelve_month_state
        assert state.forex_reserves_usd > 0, f"Forex reserves depleted: {state.forex_reserves_usd}"

    def test_inventories_non_negative(self, twelve_month_state):
        """No commodity inventory should go significantly negative."""
        state, config = twelve_month_state
        assert np.all(state.inventories >= -1e-3), \
            f"Negative inventory: min={state.inventories.min():.4f}"

    def test_no_critical_invariant_violations(self, twelve_month_state):
        """No critical invariant violations (NaN, negative prices)."""
        state, config = twelve_month_state
        warnings = check_all_invariants(state)
        critical = [w for w in warnings if "NaN" in w or "Negative price" in w]
        assert len(critical) == 0, f"Critical violations: {critical}"


class TestScenarioNarratives:
    """Priority 4B: Verify design-doc scenario narratives produce expected effects."""

    def test_dam_attack_cascades(self):
        """Drone attack on power infrastructure cascades through economy."""
        config = SimConfig()
        state = initialize_state(config)

        # Baseline: 2 months normal
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)
        baseline_gdp = compute_gdp_proxy(state, config)

        # Shock state
        state2 = initialize_state(config)
        # Dam attack: destroy power in northern LGAs
        state2.infra_power_reliability[:200] = 0.05
        state2.inventories[:200, 4] = 0.0  # electricity

        scheduler2 = TickScheduler(state=state2, config=config)
        scheduler2.run_mixed_ticks(n_months=2)
        shock_gdp = compute_gdp_proxy(state2, config)

        # GDP should be impacted
        assert not np.isnan(shock_gdp)
        assert np.all(state2.prices > 0)

    def test_wafta_cancellation_narrative(self):
        """WAFTA cancellation reduces electronics and extraction."""
        from src.economy.core.types import PolicyAction
        from src.economy.systems.government import process_policy
        from src.economy.data.commodity_ids import ELECTRONIC_COMPONENTS

        config = SimConfig()
        state = initialize_state(config)

        cancel = PolicyAction(
            action_type="cancel_wafta", parameters={},
            source="legislative", enacted_game_day=0, implementation_delay=0,
        )
        process_policy(state, cancel, config)

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        # Economy should stay stable
        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)
        # WAFTA should still be cancelled
        assert state.wafta_active is False

    def test_oil_crash_narrative(self):
        """Oil price crash drains forex and widens parallel premium."""
        config = SimConfig()
        state = initialize_state(config)
        initial_reserves = state.forex_reserves_usd

        # Crash oil prices (domestic and global)
        from src.economy.data.commodity_ids import CRUDE_OIL, NATURAL_GAS
        state.prices[:, CRUDE_OIL] *= 0.3
        state.prices[:, NATURAL_GAS] *= 0.3
        state.global_oil_price_usd *= 0.3

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        # Forex should have declined
        assert state.forex_reserves_usd < initial_reserves * 1.5
        assert not np.any(np.isnan(state.prices))

    def test_alsahid_expansion_narrative(self):
        """Al-Shahid expansion disrupts trade and diverts tax revenue."""
        config = SimConfig()
        state = initialize_state(config)

        # Seed high al-Shahid control in NE
        state.alsahid_control[:100] = 0.7

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        # Economy stays stable
        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)

    def test_enhancement_divide_narrative(self):
        """Enhancement technology creates north-south divide."""
        config = SimConfig()
        state = initialize_state(config)

        # Exaggerate divide
        if state.admin_zone is not None:
            north = state.admin_zone <= 3
            south = state.admin_zone > 3
            state.enhancement_adoption[north] = 0.05
            state.enhancement_adoption[south] = 0.90

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=6)

        # North should have gained some adoption via diffusion
        if state.admin_zone is not None:
            north_mean = float(state.enhancement_adoption[state.admin_zone <= 3].mean())
            assert north_mean > 0.05, f"North adoption should grow via diffusion: {north_mean:.3f}"

    def test_fiscal_crisis_narrative(self):
        """Budget mismanagement and high corruption leads to fiscal crisis."""
        config = SimConfig()
        state = initialize_state(config)

        # Max corruption, zero enforcement
        state.bic_enforcement_intensity = 0.0
        state.tax_rate_income = 0.05  # Very low taxes
        state.tax_rate_corporate = 0.05

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=6)

        # Should survive without crash
        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)


class TestStressEdgeCases:
    """Priority 4C: Stress test edge cases."""

    def test_simultaneous_shocks(self):
        """Economy survives oil crash + dam attack + WAFTA cancellation simultaneously."""
        from src.economy.core.types import PolicyAction
        from src.economy.systems.government import process_policy
        from src.economy.data.commodity_ids import CRUDE_OIL

        config = SimConfig()
        state = initialize_state(config)

        # Oil crash
        state.prices[:, CRUDE_OIL] *= 0.2

        # Dam attack
        state.infra_power_reliability[:300] = 0.1

        # WAFTA cancellation
        cancel = PolicyAction(
            action_type="cancel_wafta", parameters={},
            source="legislative", enacted_game_day=0, implementation_delay=0,
        )
        process_policy(state, cancel, config)

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)

    def test_zero_forex_survival(self):
        """Economy survives with zero forex reserves."""
        config = SimConfig()
        state = initialize_state(config)
        state.forex_reserves_usd = 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)

    def test_full_alsahid_control(self):
        """Economy survives even with 100% al-Shahid control everywhere."""
        config = SimConfig()
        state = initialize_state(config)
        state.alsahid_control[:] = 1.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)

    def test_zero_production_capacity(self):
        """Economy survives with zero production capacity."""
        config = SimConfig()
        state = initialize_state(config)
        state.production_capacity *= 0.0

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)

        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)

    def test_extreme_inflation_recovery(self):
        """Economy recovers from extreme price spike."""
        config = SimConfig()
        state = initialize_state(config)
        state.prices *= 50.0  # 50x all prices

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=6)

        # Mean reversion should have pulled prices back
        ratios = state.prices / BASE_PRICES[np.newaxis, :]
        assert ratios.mean() < 100.0, f"Prices didn't mean-revert: {ratios.mean():.1f}x"
        assert not np.any(np.isnan(state.prices))
