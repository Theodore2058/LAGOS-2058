"""Tests for economy diagnostics dashboard — CPI, food CPI, cost-push."""
from __future__ import annotations

import numpy as np
import pytest

from src.economy.core.types import EconomicState, SimConfig
from src.economy.data.commodities import BASE_PRICES
from src.economy.diagnostics.dashboard import (
    compute_inflation_proxy,
    compute_food_cpi,
    compute_cpi_by_quintile,
    compute_gdp_proxy,
    compute_employment_stats,
    compute_crisis_indicators,
    compute_banking_health,
    compute_poverty_metrics,
    compute_infrastructure_index,
    compute_fiscal_health,
)


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    """EconomicState at baseline prices."""
    s = EconomicState()
    N, C = config.N_LGAS, config.N_COMMODITIES
    s.prices = np.tile(BASE_PRICES, (N, 1)).copy()
    s.inventories = np.ones((N, C)) * 100.0
    s.hoarded = np.zeros((N, C))
    s.production_capacity = np.ones((N, C)) * 10.0
    s.actual_output = np.ones((N, C)) * 5.0
    s.wages = np.ones((N, config.N_SKILL_TIERS)) * 50_000
    s.labor_pool = np.ones((N, config.N_SKILL_TIERS)) * 1000
    s.labor_employed = np.ones((N, config.N_SKILL_TIERS)) * 800
    s.labor_informal = np.ones((N, config.N_SKILL_TIERS)) * 100
    s.bank_confidence = np.ones(config.N_ADMIN_ZONES) * 0.7
    s.bank_deposits = np.ones(config.N_ADMIN_ZONES) * 1e9
    s.bank_loans = np.ones(config.N_ADMIN_ZONES) * 5e8
    s.bank_bad_loans = np.ones(config.N_ADMIN_ZONES) * 2e7
    s.lending_rate = np.ones(config.N_ADMIN_ZONES) * 0.12
    s.budget_allocation = np.ones(12) * 1e10
    s.budget_released = np.ones(12) * 8e9
    s.corruption_leakage = 5e8
    s.alsahid_tax_diversion = 1e8
    s.alsahid_control = np.zeros(N)
    s.infra_road_quality = np.ones(N) * 0.6
    s.infra_power_reliability = np.ones(N) * 0.5
    s.infra_telecom_quality = np.ones(N) * 0.4
    s.forex_reserves_usd = 10_000_000.0
    s.monthly_import_bill_usd = 1_000_000.0
    s.monthly_export_revenue_usd = 1_200_000.0
    s.official_exchange_rate = 1500.0
    s.parallel_exchange_rate = 1600.0
    return s


class TestCPI:
    def test_baseline_cpi_is_zero(self, state, config):
        """At baseline prices, CPI should be ~0."""
        cpi = compute_inflation_proxy(state, config)
        assert abs(cpi) < 0.01

    def test_food_cpi_baseline_zero(self, state, config):
        """At baseline prices, food CPI should be ~0."""
        food = compute_food_cpi(state, config)
        assert abs(food) < 0.01

    def test_food_price_spike_raises_food_cpi(self, state, config):
        """Doubling food prices should push food CPI significantly above overall CPI."""
        food_ids = [6, 7, 8, 13, 18, 21]
        for fid in food_ids:
            state.prices[:, fid] *= 2.0

        overall = compute_inflation_proxy(state, config)
        food = compute_food_cpi(state, config)

        # Food CPI should be higher than overall
        assert food > overall
        # Food CPI should reflect the doubling (~100% for food-only basket)
        assert food > 0.5

    def test_non_food_spike_doesnt_affect_food_cpi(self, state, config):
        """Spiking industrial goods shouldn't move food CPI."""
        # Spike crude oil, cobalt, arms
        state.prices[:, 0] *= 5.0   # crude oil
        state.prices[:, 2] *= 5.0   # cobalt
        state.prices[:, 29] *= 5.0  # arms_drones

        food = compute_food_cpi(state, config)
        assert abs(food) < 0.01  # food prices unchanged

    def test_quintile_cpi_inequality(self, state, config):
        """When food prices spike, Q1 (55% food) should see worse CPI than Q5 (12% food)."""
        food_ids = [6, 7, 8, 13, 18, 21]
        for fid in food_ids:
            state.prices[:, fid] *= 2.0

        by_q = compute_cpi_by_quintile(state, config)
        assert by_q["Q1"] > by_q["Q5"]
        # Q1 spends 55% on food → ~55% CPI hit from doubling
        assert by_q["Q1"] > 0.3

    def test_cpi_weights_are_normalized(self, state, config):
        """CPI weights should sum to 1.0."""
        from src.economy.diagnostics.dashboard import _build_cpi_weights
        cpi_w, food_w = _build_cpi_weights()
        assert abs(cpi_w.sum() - 1.0) < 1e-10
        assert abs(food_w.sum() - 1.0) < 1e-10

    def test_cpi_only_consumer_goods(self, state, config):
        """CPI should NOT be affected by non-consumer commodity prices."""
        # Commodities NOT in any consumption basket: crude_oil (0), natural_gas (1),
        # cobalt_ore (2), iron_ore (3), limestone (4), etc.
        non_consumer = [0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 15, 16, 17, 19, 22, 23, 24, 25, 26, 29, 32, 35]
        for cid in non_consumer:
            state.prices[:, cid] *= 10.0

        cpi = compute_inflation_proxy(state, config)
        # CPI should be near zero — only consumer basket commodities matter
        assert abs(cpi) < 0.01


class TestFoodCrisisIntegration:
    def test_food_cpi_triggers_crisis(self, state, config):
        """Food CPI > 30% should trigger food crisis flag."""
        food_ids = [6, 7, 8, 13, 18, 21]
        for fid in food_ids:
            state.prices[:, fid] *= 1.5

        indicators = compute_crisis_indicators(state, config)
        assert indicators["food_crisis"] is True

    def test_no_food_crisis_at_baseline(self, state, config):
        """No food crisis at baseline prices."""
        indicators = compute_crisis_indicators(state, config)
        assert indicators["food_crisis"] is False


class TestBankingHealth:
    def test_npl_ratio_positive(self, state, config):
        """NPL ratio should be positive when bad loans exist."""
        health = compute_banking_health(state, config)
        assert health["npl_ratio"] > 0
        assert health["npl_ratio"] < 1.0

    def test_loan_to_deposit_ratio(self, state, config):
        """Loan-to-deposit ratio should be < 1.0 with our test data."""
        health = compute_banking_health(state, config)
        assert 0 < health["loan_to_deposit"] < 1.0

    def test_all_keys_present(self, state, config):
        """All banking health keys should be present."""
        health = compute_banking_health(state, config)
        expected = {"npl_ratio", "loan_to_deposit", "credit_to_gdp",
                    "mean_confidence", "mean_lending_rate", "reserve_adequacy"}
        assert expected == set(health.keys())


class TestPovertyMetrics:
    def test_no_poverty_without_pops(self, state, config):
        """Without pop data, poverty should default to 0."""
        metrics = compute_poverty_metrics(state, config)
        assert metrics["poverty_headcount"] == 0.0

    def test_poverty_with_low_sol(self, state, config):
        """Pops with SoL < 3.0 should count as poor."""
        N = config.N_LGAS
        state.pop_standard_of_living = np.ones(N * 10) * 2.5  # all poor
        state.pop_count = np.ones(N * 10) * 100.0
        metrics = compute_poverty_metrics(state, config)
        assert metrics["poverty_headcount"] > 0.9

    def test_no_poverty_with_high_sol(self, state, config):
        """Pops with SoL > 3.0 should not be counted as poor."""
        N = config.N_LGAS
        state.pop_standard_of_living = np.ones(N * 10) * 7.0
        state.pop_count = np.ones(N * 10) * 100.0
        metrics = compute_poverty_metrics(state, config)
        assert metrics["poverty_headcount"] == 0.0


class TestInfrastructureIndex:
    def test_composite_range(self, state, config):
        """Composite index should be between 0 and 1."""
        infra = compute_infrastructure_index(state, config)
        assert 0 <= infra["composite_index"] <= 1.0

    def test_road_quality_reflected(self, state, config):
        """Road quality should match the state."""
        infra = compute_infrastructure_index(state, config)
        assert abs(infra["road_quality_mean"] - 0.6) < 0.01

    def test_power_reliability_reflected(self, state, config):
        """Power reliability should match the state."""
        infra = compute_infrastructure_index(state, config)
        assert abs(infra["power_reliability_mean"] - 0.5) < 0.01


class TestFiscalHealth:
    def test_execution_rate_below_one(self, state, config):
        """Budget execution rate should be < 1.0 (released < allocated)."""
        fiscal = compute_fiscal_health(state, config)
        assert 0 < fiscal["budget_execution_rate"] < 1.0

    def test_corruption_present(self, state, config):
        """Corruption leakage should be reported."""
        fiscal = compute_fiscal_health(state, config)
        assert fiscal["corruption_leakage"] > 0
        assert fiscal["corruption_rate"] > 0

    def test_alsahid_diversion_present(self, state, config):
        """Al-Shahid tax diversion should be reported."""
        fiscal = compute_fiscal_health(state, config)
        assert fiscal["alsahid_tax_diversion"] > 0
