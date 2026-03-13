"""
Tests using the 5-LGA micro_state fixture for fast validation.

These tests verify core mechanics work at small scale without
the 774-LGA initialization overhead (~2s → ~0.01s per test).
"""

import numpy as np
import pytest

from src.economy.core.types import (
    SimConfig, EconomicState, lgas_in_zone, aggregate_by_zone,
)
from src.economy.systems.trade import tick_market, compute_consumer_demand, clear_market
from src.economy.systems.labor import adjust_wages
from src.economy.data.commodities import BASE_PRICES


class TestMicroFixture:
    """Validate the micro_state fixture itself."""

    def test_shapes(self, micro_state, micro_config):
        s = micro_state
        N = micro_config.N_LGAS
        C = micro_config.N_COMMODITIES
        assert s.prices.shape == (N, C)
        assert s.inventories.shape == (N, C)
        assert s.labor_pool.shape == (N, 4)
        assert s.admin_zone.shape == (N,)
        assert s.population.shape == (N,)

    def test_zone_mapping(self, micro_state):
        assert set(micro_state.admin_zone) == {0, 1}
        south = lgas_in_zone(micro_state, 0)
        north = lgas_in_zone(micro_state, 1)
        assert len(south) == 2  # LGAs 0, 2
        assert len(north) == 3  # LGAs 1, 3, 4

    def test_aggregate_by_zone(self, micro_state):
        per_lga = micro_state.population
        agg = aggregate_by_zone(micro_state, per_lga, 2)
        assert agg.shape == (2,)
        # Zone 0: LGA 0 (500k) + LGA 2 (200k) = 700k
        assert abs(agg[0] - 700_000) < 1.0
        # Zone 1: LGA 1 (100k) + LGA 3 (300k) + LGA 4 (150k) = 550k
        assert abs(agg[1] - 550_000) < 1.0

    def test_prices_positive(self, micro_state):
        assert np.all(micro_state.prices > 0)

    def test_population_set(self, micro_state):
        assert micro_state.population.sum() == 1_250_000


class TestMicroMarket:
    """Market mechanics at micro scale."""

    def test_consumer_demand_positive(self, micro_state, micro_config):
        demand = compute_consumer_demand(micro_state, micro_config)
        assert demand.shape == (5, 36)
        assert np.all(demand >= 0)
        assert demand.sum() > 0

    def test_clear_market_adjusts_prices(self, micro_state, micro_config):
        old_prices = micro_state.prices.copy()
        demand = compute_consumer_demand(micro_state, micro_config)
        trader_net = np.zeros_like(demand)
        clear_market(
            prices=micro_state.prices,
            inventories=micro_state.inventories,
            hoarded=micro_state.hoarded,
            consumer_demand=demand,
            trader_net_supply=trader_net,
            price_adjustment_speed=micro_config.PRICE_ADJUSTMENT_SPEED,
        )
        # Prices should have changed
        assert not np.allclose(micro_state.prices, old_prices)
        # All prices still positive
        assert np.all(micro_state.prices > 0)

    def test_tick_market_runs(self, micro_state, micro_config):
        mutations = tick_market(micro_state, micro_config)
        assert mutations.price_changes is not None
        assert mutations.excess_demand.shape == (5, 36)


class TestMicroLabor:
    """Labor mechanics at micro scale."""

    def test_wages_adjust(self):
        N, S = 5, 4
        wages = np.full((N, S), 50_000.0)
        demand = np.full((N, S), 200.0)
        supply = np.full((N, S), 100.0)
        new_wages = adjust_wages(wages, demand, supply, 20_000.0, 0.10)
        assert np.all(new_wages > wages)

    def test_minimum_wage_floor(self):
        N, S = 5, 4
        wages = np.full((N, S), 25_000.0)
        demand = np.zeros((N, S))
        supply = np.full((N, S), 1000.0)
        new_wages = adjust_wages(wages, demand, supply, 20_000.0, 0.10)
        assert np.all(new_wages >= 20_000.0)


class TestMicroAlShahid:
    """Al-Shahid control in micro state."""

    def test_control_bounded(self, micro_state):
        assert np.all(micro_state.alsahid_control >= 0)
        assert np.all(micro_state.alsahid_control <= 1)

    def test_borno_like_has_control(self, micro_state):
        # LGA 1 (Borno-like) should have highest control
        assert micro_state.alsahid_control[1] == 0.3
        assert micro_state.alsahid_control[0] == 0.0


class TestMicroInfrastructure:
    """Infrastructure quality variation."""

    def test_urban_better_roads(self, micro_state):
        # LGA 0 (urban Lagos) should have better roads than LGA 1 (rural Borno)
        assert micro_state.infra_road_quality[0] > micro_state.infra_road_quality[1]

    def test_all_positive(self, micro_state):
        assert np.all(micro_state.infra_road_quality > 0)
        assert np.all(micro_state.infra_power_reliability > 0)
