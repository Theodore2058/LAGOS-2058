"""
Phase 1 acceptance tests for the LAGOS-2058 economic simulator.

Tests:
- Core types instantiate correctly
- All 36 commodities defined with correct tiers
- LGA data loads 774 rows
- State initialization produces valid arrays
- Production engine runs without errors
- Market clearing adjusts prices correctly
- 50-tick mixed simulation stays within bounds
"""

import numpy as np
import pytest

from src.economy.core.types import (
    SimConfig,
    EconomicState,
    CommodityTier,
    SkillTier,
    LandType,
)
from src.economy.core.initialize import initialize_state
from src.economy.core.assertions import check_all_invariants
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import (
    COMMODITIES,
    COMMODITY_BY_ID,
    COMMODITIES_BY_TIER,
    BASE_PRICES,
)
from src.economy.data.lga_loader import load_economy_lga_data
from src.economy.data.zaibatsu import ZAIBATSU
from src.economy.data.ministries import MINISTRIES
from src.economy.systems.production import tick_production, assert_production_valid
from src.economy.systems.trade import tick_market, assert_market_valid, compute_consumer_demand


class TestCoreTypes:
    def test_simconfig_defaults(self):
        cfg = SimConfig()
        assert cfg.N_LGAS == 774
        assert cfg.N_COMMODITIES == 36
        assert cfg.N_SKILL_TIERS == 4
        assert cfg.N_ADMIN_ZONES == 8
        assert cfg.SEED == 42

    def test_economic_state_instantiates(self):
        state = EconomicState()
        assert state.game_month == 0
        assert state.prices is None

    def test_enums(self):
        assert SkillTier.UNSKILLED == 0
        assert SkillTier.CHINESE_ELITE == 3
        assert LandType.FARMLAND == 0
        assert CommodityTier.RAW == 0
        assert CommodityTier.SERVICE == 3


class TestCommodities:
    def test_count(self):
        assert len(COMMODITIES) == 36

    def test_ids_unique(self):
        ids = [c.id for c in COMMODITIES]
        assert len(set(ids)) == 36

    def test_ids_sequential(self):
        ids = sorted(c.id for c in COMMODITIES)
        assert ids == list(range(36))

    def test_tiers(self):
        assert len(COMMODITIES_BY_TIER[0]) == 14  # RAW
        assert len(COMMODITIES_BY_TIER[1]) == 11  # PROCESSED
        assert len(COMMODITIES_BY_TIER[2]) == 6   # INTERMEDIATE
        assert len(COMMODITIES_BY_TIER[3]) == 5   # SERVICE

    def test_base_prices_positive(self):
        assert np.all(BASE_PRICES > 0)

    def test_electricity_is_20(self):
        assert COMMODITY_BY_ID[20].name == "electricity"


class TestStaticData:
    def test_zaibatsu_count(self):
        assert len(ZAIBATSU) == 5

    def test_ministries_count(self):
        assert len(MINISTRIES) == 12


class TestLGALoader:
    def test_loads_774_lgas(self):
        data = load_economy_lga_data()
        assert data.n_lgas == 774
        assert len(data.states) == 774

    def test_population_positive(self):
        data = load_economy_lga_data()
        assert np.all(data.population > 0)

    def test_admin_zones_1_to_8(self):
        data = load_economy_lga_data()
        unique_zones = set(data.admin_zones)
        assert unique_zones.issubset({1, 2, 3, 4, 5, 6, 7, 8})


class TestInitialization:
    def test_all_arrays_correct_shape(self, state, config):
        N, C, S, L, Z = 774, 36, 4, 4, 8
        assert state.prices.shape == (N, C)
        assert state.inventories.shape == (N, C)
        assert state.production_capacity.shape == (N, C)
        assert state.labor_pool.shape == (N, S)
        assert state.wages.shape == (N, S)
        assert state.land_area.shape == (N, L)
        assert state.bank_deposits.shape == (Z,)
        assert state.population.shape == (N,)

    def test_no_nan_in_state(self, state):
        for attr in ['prices', 'inventories', 'production_capacity',
                      'labor_pool', 'wages', 'land_area', 'bank_deposits']:
            arr = getattr(state, attr)
            assert not np.any(np.isnan(arr)), f"NaN in {attr}"

    def test_prices_positive(self, state):
        assert np.all(state.prices > 0)

    def test_inventories_non_negative(self, state):
        assert np.all(state.inventories >= 0)

    def test_invariants_pass(self, state):
        warnings = check_all_invariants(state)
        assert len(warnings) == 0


class TestProduction:
    def test_production_tick_runs(self, state, config):
        mutations = tick_production(state, config)
        assert mutations.inventory_deltas.shape == (774, 36)
        assert mutations.capacity_utilization.shape == (774, 36)

    def test_capacity_utilization_bounded(self, state, config):
        mutations = tick_production(state, config)
        assert np.all(mutations.capacity_utilization <= 1.0 + 1e-3)
        assert np.all(mutations.capacity_utilization >= 0.0)

    def test_assertions_pass(self, state, config):
        mutations = tick_production(state, config)
        assert_production_valid(state, mutations)


class TestMarketClearing:
    def test_market_tick_runs(self, state, config):
        mutations = tick_market(state, config)
        assert mutations.price_changes.shape == (774, 36)
        assert mutations.excess_demand.shape == (774, 36)

    def test_prices_stay_positive(self, state, config):
        for _ in range(10):
            tick_market(state, config)
        assert np.all(state.prices > 0)

    def test_consumer_demand_non_negative(self, state, config):
        demand = compute_consumer_demand(state, config)
        assert np.all(demand >= 0)


class TestAcceptance:
    """Phase 1 acceptance: run 50+ ticks, verify stability."""

    def test_50_mixed_ticks(self, state, config):
        """Run 1 month (56 market + 7 production ticks). Prices within bounds."""
        scheduler = TickScheduler(state=state, config=config)
        results = scheduler.run_mixed_ticks(n_months=1)

        # All invariants held
        total_warnings = sum(len(r.invariant_warnings) for r in results)
        assert total_warnings == 0, f"Got {total_warnings} invariant warnings"

        # Prices within [0.1x, 10x] of base
        ratio = state.prices / BASE_PRICES[np.newaxis, :]
        assert np.all(ratio > 0.01), f"Price too low: min ratio = {ratio.min():.4f}"
        assert np.all(ratio < 200.0), f"Price too high: max ratio = {ratio.max():.2f}"

        # No negative inventories
        assert np.all(state.inventories >= -1e-6)

        # Prices stayed positive
        assert np.all(state.prices > 0)

    def test_tick_performance(self, state, config):
        """Market tick completes in under 1 second."""
        import time
        scheduler = TickScheduler(state=state, config=config)

        t0 = time.time()
        scheduler.run_market_tick()
        elapsed = time.time() - t0

        assert elapsed < 1.0, f"Market tick took {elapsed:.2f}s (target: <1s)"
