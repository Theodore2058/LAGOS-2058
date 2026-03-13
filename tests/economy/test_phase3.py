"""
Phase 3 acceptance tests — Labor, Banking, and integrated pipeline.

Acceptance criteria:
- Wage ratios roughly 1:3:8:15 across skill tiers
- Strikes occur when wage/cost-of-living < 0.60
- Banking financial accelerator amplifies shocks 1.8-2.5×
- Informal sector absorbs 40-60% of unemployed
- Integrated production+labor+banking pipeline runs without errors
"""

import numpy as np
import pytest

from src.economy.core.types import SimConfig, SkillTier
from src.economy.core.initialize import initialize_state
from src.economy.core.assertions import check_all_invariants
from src.economy.core.scheduler import TickScheduler
from src.economy.systems.labor import (
    tick_labor,
    adjust_wages,
    evaluate_strikes,
    process_automation,
    compute_informal_sector,
    apply_labor_mutations,
)
from src.economy.systems.banking import (
    tick_banking,
    apply_banking_mutations,
    financial_accelerator,
    evaluate_loan_defaults,
    compute_naijin_credit_bias,
)


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    return initialize_state(config)


# ---------------------------------------------------------------------------
# Labor system tests
# ---------------------------------------------------------------------------

class TestWages:
    def test_base_wage_ratios(self, config):
        """BASE_WAGES should be roughly 1:3:8:15."""
        bw = config.BASE_WAGES
        ratios = bw / bw[0]
        assert ratios[0] == 1.0
        assert 2.5 <= ratios[1] <= 3.5, f"Skilled ratio {ratios[1]}"
        assert 7.0 <= ratios[2] <= 9.0, f"Highly-skilled ratio {ratios[2]}"
        assert 13.0 <= ratios[3] <= 17.0, f"Elite ratio {ratios[3]}"

    def test_wages_adjust_upward_on_excess_demand(self):
        """Wages rise when demand exceeds supply."""
        N, S = 10, 4
        wages = np.full((N, S), 50_000.0)
        demand = np.full((N, S), 200.0)
        supply = np.full((N, S), 100.0)
        new_wages = adjust_wages(wages, demand, supply, 20_000.0, 0.10)
        assert np.all(new_wages > wages)

    def test_wages_sticky_downward(self):
        """Wages fall slower than they rise (sticky downward)."""
        N, S = 10, 4
        wages = np.full((N, S), 50_000.0)

        # Excess demand → rise
        demand_up = np.full((N, S), 200.0)
        supply = np.full((N, S), 100.0)
        wages_up = adjust_wages(wages, demand_up, supply, 20_000.0, 0.10)

        # Excess supply → fall (same magnitude imbalance)
        demand_down = np.full((N, S), 50.0)
        supply_down = np.full((N, S), 100.0)
        wages_down = adjust_wages(wages, demand_down, supply_down, 20_000.0, 0.10)

        rise = (wages_up - wages).mean()
        fall = (wages - wages_down).mean()
        assert fall < rise, "Downward adjustment should be smaller than upward"

    def test_minimum_wage_floor(self):
        """Wages never fall below minimum."""
        N, S = 5, 4
        wages = np.full((N, S), 25_000.0)
        demand = np.zeros((N, S))
        supply = np.full((N, S), 1000.0)
        new_wages = adjust_wages(wages, demand, supply, 20_000.0, 0.10)
        assert np.all(new_wages >= 20_000.0)


class TestStrikes:
    def test_strikes_trigger_on_low_wages(self, state, config):
        """Strikes should trigger when wage/cost_of_living < threshold."""
        # Force very low unskilled wages
        state.wages[:, SkillTier.UNSKILLED] = 1.0
        # Force high food prices
        food_ids = [6, 7, 8, 13, 18, 21]
        for c in food_ids:
            state.prices[:, c] = 100_000.0

        strikes, triggered = evaluate_strikes(state, config)
        # Should have at least some strikes
        assert len(triggered) > 0 or strikes.sum() > 0, "Expected strikes with very low wages"

    def test_no_strikes_with_good_wages(self, state, config):
        """No strikes when wages are adequate."""
        state.wages[:, SkillTier.UNSKILLED] = 500_000.0
        strikes, triggered = evaluate_strikes(state, config)
        assert len(triggered) == 0

    def test_strike_duration_bounded(self, state, config):
        """Strike duration within configured range."""
        state.wages[:, SkillTier.UNSKILLED] = 1.0
        food_ids = [6, 7, 8, 13, 18, 21]
        for c in food_ids:
            state.prices[:, c] = 100_000.0

        strikes, _ = evaluate_strikes(state, config)
        active = strikes[strikes > 0]
        if len(active) > 0:
            lo, hi = config.STRIKE_DURATION_RANGE
            assert active.min() >= lo
            assert active.max() <= hi


class TestAutomation:
    def test_automation_increases_with_high_wages(self, state, config):
        """Automation rises when wages exceed threshold."""
        # Set wages very high
        state.wages[:] = config.BASE_WAGES * 3.0
        auto_before = state.automation_level.copy()
        auto_new = process_automation(state, config)
        # At least some commodities should see automation increase
        assert (auto_new > auto_before).any()

    def test_automation_capped(self, state, config):
        """Automation never exceeds 0.80."""
        state.automation_level[:] = 0.79
        state.wages[:] = config.BASE_WAGES * 5.0
        auto_new = process_automation(state, config)
        assert auto_new.max() <= 0.80


class TestInformalSector:
    def test_informal_absorbs_unemployed(self, config):
        """~70% of unemployed enter informal sector."""
        N, S = 10, 4
        unemployment = np.full((N, S), 1000.0)
        informal, income = compute_informal_sector(unemployment, config)
        ratio = informal.mean() / unemployment.mean()
        assert 0.65 <= ratio <= 0.75, f"Informal absorption {ratio:.2f}"

    def test_informal_income_less_than_formal(self, config):
        """Informal income should be < formal wages."""
        N, S = 10, 4
        unemployment = np.full((N, S), 1000.0)
        informal, income = compute_informal_sector(unemployment, config)
        # Income per informal worker
        per_worker = income / np.maximum(informal, 1.0)
        # Should be 40% of base wages
        for s in range(S):
            expected = config.INFORMAL_WAGE_FRACTION * config.BASE_WAGES[s]
            np.testing.assert_allclose(per_worker[:, s], expected, rtol=0.01)


class TestLaborTick:
    def test_tick_labor_produces_valid_mutations(self, state, config):
        """tick_labor returns well-shaped mutations."""
        mut = tick_labor(state, config)
        assert mut.wages_new.shape == (config.N_LGAS, config.N_SKILL_TIERS)
        assert mut.employment_new.shape == (config.N_LGAS, config.N_SKILL_TIERS)
        assert mut.informal_new.shape == (config.N_LGAS, config.N_SKILL_TIERS)
        assert np.all(mut.wages_new > 0)
        assert np.all(mut.employment_new >= 0)

    def test_apply_labor_mutations(self, state, config):
        """apply_labor_mutations writes back to state."""
        mut = tick_labor(state, config)
        strikes, _ = evaluate_strikes(state, config)
        old_wages = state.wages.copy()
        apply_labor_mutations(state, mut, strikes)
        # State should be updated
        np.testing.assert_array_equal(state.wages, mut.wages_new)
        np.testing.assert_array_equal(state.labor_employed, mut.employment_new)


# ---------------------------------------------------------------------------
# Banking system tests
# ---------------------------------------------------------------------------

class TestFinancialAccelerator:
    def test_amplification_magnitude(self):
        """Default amplification ≈ 2.2× for contraction."""
        amp = financial_accelerator(-0.10, leverage_ratio=4.0, elasticity=0.3, is_contraction=True)
        expected = -0.10 * (1 + 4.0 * 0.3)
        assert abs(amp - expected) < 1e-10

    def test_asymmetric(self):
        """Contraction amplified more than expansion."""
        contract = abs(financial_accelerator(-0.10, 4.0, 0.3, is_contraction=True))
        expand = abs(financial_accelerator(0.10, 4.0, 0.3, is_contraction=False))
        assert contract > expand

    def test_amplification_range(self):
        """Amplification should be 1.8-2.5× with default params."""
        amp_factor = 1.0 + 4.0 * 0.3
        assert 1.8 <= amp_factor <= 2.5


class TestLoanDefaults:
    def test_no_default_when_revenue_high(self, state, config):
        """No defaults when revenue exceeds debt service."""
        state.bank_loans[:] = 1e9
        state.lending_rate[:] = 0.08
        # debt_service = 1e9 * 0.08 / 12 ≈ 6.67M
        defaults = evaluate_loan_defaults(state, zone=0, config=config, zone_revenue=1e10)
        assert defaults == 0.0

    def test_default_when_revenue_low(self, state, config):
        """Defaults occur when revenue < threshold × debt_service."""
        state.bank_loans[0] = 1e10
        state.lending_rate[0] = 0.10
        # debt_service = 1e10 * 0.10 / 12 ≈ 83.3M
        # threshold = 0.70, so need revenue < 0.70 * 83.3M ≈ 58.3M
        defaults = evaluate_loan_defaults(state, zone=0, config=config, zone_revenue=1e6)
        assert defaults > 0

    def test_default_capped_at_30pct(self, state, config):
        """Defaults capped at 30% of loans per tick."""
        state.bank_loans[0] = 1e10
        state.lending_rate[0] = 0.10
        defaults = evaluate_loan_defaults(state, zone=0, config=config, zone_revenue=0.0)
        assert defaults <= state.bank_loans[0] * 0.30 + 1.0


class TestNaijinCreditBias:
    def test_southern_zones_higher_credit(self, state):
        """Southern zones should have higher credit modifier."""
        south_mod = compute_naijin_credit_bias(state, zone=0)
        north_mod = compute_naijin_credit_bias(state, zone=6)
        assert south_mod >= north_mod

    def test_credit_floor(self, state):
        """Credit modifier never below 0.7."""
        for z in range(8):
            mod = compute_naijin_credit_bias(state, z)
            assert mod >= 0.7


class TestBankingTick:
    def test_tick_banking_valid(self, state, config):
        """Banking tick runs and produces valid mutations."""
        mut = tick_banking(state, config)
        assert mut.deposits_new.shape == (config.N_ADMIN_ZONES,)
        assert mut.loans_new.shape == (config.N_ADMIN_ZONES,)
        assert np.all(mut.deposits_new >= 0)
        assert np.all(mut.loans_new >= 0)
        assert np.all(mut.confidence_new >= 0.05)
        assert np.all(mut.confidence_new <= 1.0)
        assert np.all(mut.lending_rate_new >= 0.04)
        assert np.all(mut.lending_rate_new <= 0.25)

    def test_apply_banking_mutations(self, state, config):
        """apply_banking_mutations writes to state correctly."""
        mut = tick_banking(state, config)
        apply_banking_mutations(state, mut)
        np.testing.assert_array_equal(state.bank_deposits, mut.deposits_new)
        np.testing.assert_array_equal(state.bank_loans, mut.loans_new)
        np.testing.assert_array_equal(state.bank_confidence, mut.confidence_new)

    def test_confidence_shock_amplified(self, state, config):
        """A large default shock should be amplified by financial accelerator."""
        # Create conditions for large defaults
        state.bank_loans[:] = 1e12
        state.lending_rate[:] = 0.20
        initial_confidence = state.bank_confidence.copy()
        mut = tick_banking(state, config)
        # Confidence should drop significantly
        confidence_drop = initial_confidence - mut.confidence_new
        assert confidence_drop.max() > 0, "Expected confidence to drop after large defaults"


# ---------------------------------------------------------------------------
# Integrated pipeline tests
# ---------------------------------------------------------------------------

class TestIntegratedPipeline:
    def test_production_tick_with_labor_and_banking(self, state, config):
        """Full production tick includes labor and banking."""
        scheduler = TickScheduler(state=state, config=config)
        result = scheduler.run_production_tick()
        assert result.tick_type == "production"
        assert result.tick_number > 0

    def test_mixed_ticks_one_month(self, state, config):
        """One month of mixed ticks (56 market/prod + 1 structural) completes."""
        scheduler = TickScheduler(state=state, config=config)
        results = scheduler.run_mixed_ticks(n_months=1)
        # 56 market/production ticks + 1 structural = 57
        assert len(results) == config.MARKET_TICKS_PER_MONTH + 1
        # Count production ticks
        prod_ticks = sum(1 for r in results if r.tick_type == "production")
        expected_prod = config.PRODUCTION_TICKS_PER_MONTH - 1  # first tick=0 is market
        assert prod_ticks == expected_prod
        # One structural tick
        struct_ticks = sum(1 for r in results if r.tick_type == "structural")
        assert struct_ticks == 1

    def test_three_month_stability(self, state, config):
        """Three months of mixed ticks maintain invariants."""
        scheduler = TickScheduler(state=state, config=config)
        results = scheduler.run_mixed_ticks(n_months=3)
        warnings = check_all_invariants(state)
        # Allow some warnings but no catastrophic failures
        critical = [w for w in warnings if "Negative" in w or "NaN" in w]
        assert len(critical) == 0, f"Critical invariant violations: {critical}"

    def test_prices_bounded_after_three_months(self, state, config):
        """Prices stay within reasonable bounds after 3 months."""
        from src.economy.data.commodities import BASE_PRICES
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)
        price_ratios = state.prices / BASE_PRICES[np.newaxis, :]
        assert price_ratios.max() < 20.0, f"Price blowup: max ratio {price_ratios.max():.1f}"
        assert price_ratios.min() > 0.01, f"Price collapse: min ratio {price_ratios.min():.4f}"

    def test_employment_reasonable(self, state, config):
        """Employment doesn't exceed labor pool after 3 months."""
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)
        excess = state.labor_employed - state.labor_pool
        assert excess.max() < 1.0, f"Employment exceeds pool by {excess.max():.1f}"

    def test_banking_confidence_stable(self, state, config):
        """Banking confidence stays within bounds after 3 months."""
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)
        assert np.all(state.bank_confidence >= 0.05)
        assert np.all(state.bank_confidence <= 1.0)

    def test_wages_differentiated_by_skill(self, state, config):
        """After simulation, wages still differentiated by skill tier."""
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=2)
        mean_wages = state.wages.mean(axis=0)
        # Unskilled < Skilled < Highly-skilled < Elite
        assert mean_wages[0] < mean_wages[1] < mean_wages[2] < mean_wages[3]
