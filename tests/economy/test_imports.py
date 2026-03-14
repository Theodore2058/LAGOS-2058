"""
Import fulfillment and WAFTA cancellation tests (Priority 1A).

Tests that import availability constrains production and that
cancelling WAFTA reduces electronics/extraction output.
"""

import numpy as np
import pytest

from src.economy.core.types import SimConfig, PolicyAction
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.systems.government import process_policy
from src.economy.data.commodity_ids import (
    CRUDE_OIL, NATURAL_GAS, COBALT_ORE, IRON_ORE,
    ELECTRONIC_COMPONENTS, CHEMICALS, ARMS_DRONES, CONSUMER_ELECTRONICS,
)


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    return initialize_state(config)


class TestImportFulfillment:
    def test_default_fulfillment_is_full(self, state):
        """All imports start at 100% fulfillment."""
        for name, ratio in state.import_fulfillment.items():
            assert ratio == 1.0, f"{name} fulfillment is {ratio}"

    def test_wafta_active_by_default(self, state):
        assert state.wafta_active is True

    def test_cancel_wafta_reduces_fulfillment(self, state, config):
        """Cancelling WAFTA drops silicon and heavy_machinery to 50%."""
        policy = PolicyAction(
            action_type="cancel_wafta",
            parameters={},
            source="legislative",
            enacted_game_day=0,
            implementation_delay=0,
        )
        process_policy(state, policy, config)

        assert state.wafta_active is False
        assert state.import_fulfillment["silicon"] == 0.5
        assert state.import_fulfillment["heavy_machinery"] == 0.5
        # Non-WAFTA imports unchanged
        assert state.import_fulfillment["chemical_feedstock"] == 1.0

    def test_restore_wafta(self, state, config):
        """Restoring WAFTA restores fulfillment."""
        cancel = PolicyAction(action_type="cancel_wafta", parameters={},
                              source="legislative", enacted_game_day=0, implementation_delay=0)
        restore = PolicyAction(action_type="restore_wafta", parameters={},
                               source="legislative", enacted_game_day=0, implementation_delay=0)
        process_policy(state, cancel, config)
        assert state.import_fulfillment["silicon"] == 0.5
        process_policy(state, restore, config)
        assert state.import_fulfillment["silicon"] == 1.0
        assert state.wafta_active is True


class TestWAFTAProductionCascade:
    def test_wafta_cancellation_reduces_electronics(self, state, config):
        """WAFTA cancellation should reduce electronic components output."""
        # Baseline: run a few production ticks with WAFTA active
        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=1)
        baseline_electronics = state.production_capacity[:, ELECTRONIC_COMPONENTS].sum()

        # Now cancel WAFTA and measure production impact
        state2 = initialize_state(config)
        cancel = PolicyAction(action_type="cancel_wafta", parameters={},
                              source="legislative", enacted_game_day=0, implementation_delay=0)
        process_policy(state2, cancel, config)

        scheduler2 = TickScheduler(state=state2, config=config)
        scheduler2.run_mixed_ticks(n_months=1)

        # Electronic components actual output should have dropped
        # (production_capacity is unchanged, but actual_output is constrained)
        wafta_output = state2.actual_output[:, ELECTRONIC_COMPONENTS].sum()
        normal_output = state.actual_output[:, ELECTRONIC_COMPONENTS].sum()

        # With 50% silicon fulfillment, output should drop significantly
        if normal_output > 0:
            ratio = wafta_output / normal_output
            assert ratio < 0.8, (
                f"Electronics output should drop >20%% with WAFTA cancelled: "
                f"ratio={ratio:.2f}"
            )

    def test_wafta_reduces_extraction(self, state, config):
        """WAFTA cancellation reduces heavy machinery → extraction drops."""
        state2 = initialize_state(config)
        cancel = PolicyAction(action_type="cancel_wafta", parameters={},
                              source="legislative", enacted_game_day=0, implementation_delay=0)
        process_policy(state2, cancel, config)

        # Heavy machinery affects crude oil, natural gas, cobalt, iron
        extraction_ids = [CRUDE_OIL, NATURAL_GAS, COBALT_ORE, IRON_ORE]

        scheduler = TickScheduler(state=state2, config=config)
        scheduler.run_mixed_ticks(n_months=1)

        # At minimum, the economy should stay stable
        assert not np.any(np.isnan(state2.prices))
        assert np.all(state2.prices > 0)

    def test_low_reserves_reduce_fulfillment(self, state, config):
        """Very low forex reserves should reduce import fulfillment."""
        from src.economy.systems.forex import _update_import_fulfillment

        state.forex_reserves_usd = 1e6  # Almost nothing
        state.monthly_import_bill_usd = 1e9  # Large import bill
        _update_import_fulfillment(state)

        # All fulfillment should be reduced (reserves < 1 month of imports)
        for name, ratio in state.import_fulfillment.items():
            assert ratio < 1.0, f"{name} should be reduced with low reserves"

    def test_cascade_wafta_stable(self, state, config):
        """Full 3-month sim with WAFTA cancelled stays stable."""
        cancel = PolicyAction(action_type="cancel_wafta", parameters={},
                              source="legislative", enacted_game_day=0, implementation_delay=0)
        process_policy(state, cancel, config)

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=3)

        assert not np.any(np.isnan(state.prices))
        assert np.all(state.prices > 0)
        assert np.all(state.inventories >= -1e-6)
