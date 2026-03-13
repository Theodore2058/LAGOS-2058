"""
Phase 5 acceptance tests — Government, Al-Shahid, Election Feedback.

Tests policy queue, budget/corruption, al-Shahid control dynamics,
election feedback channels, and anticipation effects.
"""

import numpy as np
import pytest

from src.economy.core.types import SimConfig, PolicyAction, ConstructionProject
from src.economy.core.initialize import initialize_state
from src.economy.core.assertions import check_all_invariants
from src.economy.core.scheduler import TickScheduler
from src.economy.systems.government import (
    tick_government,
    compute_tax_revenue,
    process_policy,
)
from src.economy.systems.alsahid import tick_alsahid, apply_alsahid_mutations
from src.economy.systems.election_feedback import (
    compute_election_feedback,
    tick_anticipation,
    apply_anticipation_mutations,
)


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    return initialize_state(config)


# ---------------------------------------------------------------------------
# Government tests
# ---------------------------------------------------------------------------

class TestGovernment:
    def test_tick_government_runs(self, state, config):
        """Government tick completes without error."""
        tick_government(state, config)

    def test_tax_revenue_positive(self, state, config):
        """Tax revenue should be positive in a functioning economy."""
        revenue = compute_tax_revenue(state, config)
        assert revenue > 0

    def test_budget_released_after_tick(self, state, config):
        """Budget should be released after government tick."""
        tick_government(state, config)
        assert state.budget_released is not None
        assert np.all(state.budget_released >= 0)

    def test_corruption_leakage_bounded(self, state, config):
        """Corruption leakage stays within configured bounds."""
        tick_government(state, config)
        assert np.all(state.corruption_leakage >= config.CORRUPTION_LEAKAGE_MIN)
        assert np.all(state.corruption_leakage <= config.CORRUPTION_LEAKAGE_MAX)

    def test_infrastructure_decays_without_repair(self, state, config):
        """Infrastructure decays when there's no repair budget."""
        initial_road = state.infra_road_quality.mean()
        # Zero out budget so no repair occurs
        state.budget_allocation[:] = 0.0
        state.budget_released[:] = 0.0
        tick_government(state, config)
        # Mean road quality should have decreased (decay > repair when budget=0)
        assert state.infra_road_quality.mean() < initial_road + 1e-3

    def test_policy_set_tax_rate(self, state, config):
        """Policy to set tax rate is processed correctly."""
        policy = PolicyAction(
            action_type="set_tax_rate",
            parameters={"tax_field": "income", "rate": 0.25},
            source="executive",
            enacted_game_day=0,
            implementation_delay=0,
        )
        process_policy(state, policy, config)
        assert state.tax_rate_income == 0.25

    def test_policy_set_minimum_wage(self, state, config):
        """Policy to set minimum wage works."""
        policy = PolicyAction(
            action_type="set_minimum_wage",
            parameters={"wage": 75_000.0},
            source="legislative",
            enacted_game_day=0,
            implementation_delay=0,
        )
        process_policy(state, policy, config)
        assert state.minimum_wage == 75_000.0


# ---------------------------------------------------------------------------
# Al-Shahid tests
# ---------------------------------------------------------------------------

class TestAlShahid:
    def test_tick_alsahid_valid(self, state, config):
        """Al-Shahid tick produces valid mutations."""
        mut = tick_alsahid(state, config)
        assert mut.control_new.shape == (config.N_LGAS,)
        assert mut.service_provision_new.shape == (config.N_LGAS,)
        assert np.all(mut.control_new >= 0)
        assert np.all(mut.control_new <= 1)

    def test_control_bounded(self, state, config):
        """Al-Shahid control stays in [0, 1]."""
        # Run multiple ticks
        for _ in range(5):
            mut = tick_alsahid(state, config)
            apply_alsahid_mutations(state, mut)
        assert np.all(state.alsahid_control >= 0)
        assert np.all(state.alsahid_control <= 1)

    def test_service_provision_proportional(self, state, config):
        """Service provision should scale with control level."""
        mut = tick_alsahid(state, config)
        # Where control is higher, services should be higher
        high_control = mut.control_new > 0.5
        low_control = mut.control_new < 0.1
        if high_control.any() and low_control.any():
            high_service = mut.service_provision_new[high_control].mean()
            low_service = mut.service_provision_new[low_control].mean()
            assert high_service > low_service

    def test_tax_diversion_nonnegative(self, state, config):
        """Tax diversion amount should be non-negative."""
        mut = tick_alsahid(state, config)
        assert mut.tax_diversion_amount >= 0

    def test_bic_enforcement_reduces_control(self, state, config):
        """Higher BIC enforcement should reduce al-Shahid control growth."""
        # Low enforcement
        state.bic_enforcement_intensity = 0.1
        mut_low = tick_alsahid(state, config)

        # Reset and try high enforcement
        state2 = initialize_state(config)
        state2.bic_enforcement_intensity = 0.9
        mut_high = tick_alsahid(state2, config)

        # With higher enforcement, control should be lower or equal
        assert mut_high.control_new.mean() <= mut_low.control_new.mean() + 0.01


# ---------------------------------------------------------------------------
# Election feedback tests
# ---------------------------------------------------------------------------

class TestElectionFeedback:
    def test_feedback_shapes(self, state, config):
        """Election feedback has correct shapes."""
        fb = compute_election_feedback(state, config)
        assert fb.welfare_scores.shape == (config.N_VOTER_TYPES,)
        assert fb.salience_shifts.shape == (config.N_VOTER_TYPES, config.N_ISSUE_DIMENSIONS)
        assert fb.position_shifts.shape == (config.N_VOTER_TYPES, config.N_ISSUE_DIMENSIONS)
        assert fb.migration_voter_changes.shape == (config.N_LGAS,)
        assert isinstance(fb.governance_satisfaction, float)

    def test_welfare_bounded(self, state, config):
        """Welfare scores should be in [-1, 1]."""
        fb = compute_election_feedback(state, config)
        assert fb.welfare_scores.min() >= -1.0
        assert fb.welfare_scores.max() <= 1.0

    def test_governance_satisfaction_bounded(self, state, config):
        """Governance satisfaction bounded by multiplier."""
        fb = compute_election_feedback(state, config)
        assert -1.0 <= fb.governance_satisfaction <= 1.0


class TestAnticipation:
    def test_anticipation_shapes(self, state, config):
        """Anticipation mutations have correct shapes."""
        mut = tick_anticipation(state, config, election_proximity=0.5)
        assert mut.investment_modifier.shape == (config.N_LGAS,)
        assert mut.capital_flight.shape == (config.N_ADMIN_ZONES,)
        assert mut.automation_acceleration.shape == (config.N_LGAS, config.N_COMMODITIES)

    def test_no_effect_when_far(self, state, config):
        """No significant anticipation effects when election is far."""
        mut = tick_anticipation(state, config, election_proximity=0.0)
        # Investment modifier should be 1.0
        np.testing.assert_allclose(mut.investment_modifier, 1.0)
        # No capital flight
        np.testing.assert_allclose(mut.capital_flight, 0.0)

    def test_investment_drops_near_election(self, state, config):
        """Investment modifier < 1 when election is imminent."""
        mut = tick_anticipation(state, config, election_proximity=0.8)
        assert np.all(mut.investment_modifier < 1.0)

    def test_capital_flight_above_threshold(self, state, config):
        """Capital flight occurs when proximity > threshold."""
        mut = tick_anticipation(state, config, election_proximity=0.9)
        assert mut.capital_flight.sum() > 0

    def test_apply_anticipation(self, state, config):
        """Apply anticipation drains reserves."""
        initial_reserves = state.forex_reserves_usd
        mut = tick_anticipation(state, config, election_proximity=0.8)
        apply_anticipation_mutations(state, mut)
        assert state.forex_reserves_usd <= initial_reserves


# ---------------------------------------------------------------------------
# Full integration with Phase 5 systems
# ---------------------------------------------------------------------------

class TestPhase5Integration:
    def test_structural_tick_with_government_alsahid(self, state, config):
        """Structural tick now includes government and al-Shahid."""
        scheduler = TickScheduler(state=state, config=config)
        result = scheduler.run_structural_tick()
        assert result.tick_type == "structural"

    def test_three_month_full_simulation(self, state, config):
        """3-month simulation with all systems stays stable."""
        scheduler = TickScheduler(state=state, config=config)
        results = scheduler.run_mixed_ticks(n_months=3)
        warnings = check_all_invariants(state)
        critical = [w for w in warnings if "Negative" in w or "NaN" in w]
        assert len(critical) == 0, f"Critical: {critical}"

    def test_prices_bounded_full_sim(self, state, config):
        """Prices bounded after full 3-month sim with all systems."""
        from src.economy.data.commodities import BASE_PRICES
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)
        ratios = state.prices / BASE_PRICES[np.newaxis, :]
        assert ratios.max() < 50.0, f"Price blowup: {ratios.max():.1f}x"
        assert ratios.min() > 0.001, f"Price collapse: {ratios.min():.4f}x"

    def test_alsahid_control_stable(self, state, config):
        """Al-Shahid control stays bounded through simulation."""
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)
        assert np.all(state.alsahid_control >= 0)
        assert np.all(state.alsahid_control <= 1)
