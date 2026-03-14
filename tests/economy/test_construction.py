"""
Construction project material and labor consumption tests (Priority 1B).

Tests that construction projects consume construction_materials inventory
and reserve labor, and stall when resources are unavailable.
"""

import numpy as np
import pytest

from src.economy.core.types import (
    ConstructionProject,
    EconomicState,
    PolicyAction,
    SimConfig,
)
from src.economy.core.initialize import initialize_state
from src.economy.data.commodity_ids import CONSTRUCTION_MATERIALS
from src.economy.systems.government import _tick_construction, process_policy


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    return initialize_state(config)


def _make_project(lga_id=0, months=6, monthly_cost=1e9, labor_demand=None):
    """Helper to create a construction project."""
    return ConstructionProject(
        project_type="refinery",
        lga_id=lga_id,
        commodity_id=None,
        months_remaining=months,
        monthly_cost_naira=monthly_cost,
        monthly_labor_demand=labor_demand or {},
        completion_effect={},
    )


class TestConstructionConsumption:
    def test_construction_consumes_materials(self, state, config):
        """Active construction project should reduce construction_materials inventory."""
        lga = 0
        # Ensure sufficient materials so project doesn't stall
        state.inventories[lga, CONSTRUCTION_MATERIALS] = 1e6

        initial_materials = float(state.inventories[lga, CONSTRUCTION_MATERIALS])

        project = _make_project(lga_id=lga, months=3, monthly_cost=1e9)
        state.construction_projects = [project]

        _tick_construction(state, config)

        final_materials = float(state.inventories[lga, CONSTRUCTION_MATERIALS])
        assert final_materials < initial_materials, (
            f"Materials should decrease: {initial_materials:.0f} -> {final_materials:.0f}"
        )

    def test_construction_decrements_timer(self, state, config):
        """Project with sufficient materials should advance."""
        # Ensure plenty of materials
        state.inventories[:, CONSTRUCTION_MATERIALS] = 1e8

        project = _make_project(lga_id=0, months=3, monthly_cost=1e6)
        state.construction_projects = [project]

        _tick_construction(state, config)

        # Project should still exist with months_remaining = 2
        assert len(state.construction_projects) == 1
        assert state.construction_projects[0].months_remaining == 2
        assert state.construction_projects[0].funded is True

    def test_construction_stalls_without_materials(self, state, config):
        """Project should stall when construction materials are near zero."""
        lga = 0
        state.inventories[lga, CONSTRUCTION_MATERIALS] = 0.0

        project = _make_project(lga_id=lga, months=3, monthly_cost=1e9)
        state.construction_projects = [project]

        _tick_construction(state, config)

        # Timer should NOT have decremented
        assert state.construction_projects[0].months_remaining == 3
        assert state.construction_projects[0].funded is False

    def test_construction_completes_and_removed(self, state, config):
        """Project with 1 month remaining and sufficient materials completes."""
        state.inventories[:, CONSTRUCTION_MATERIALS] = 1e8

        project = _make_project(lga_id=0, months=1, monthly_cost=1e6)
        state.construction_projects = [project]

        _tick_construction(state, config)

        # Project should be removed (completed)
        assert len(state.construction_projects) == 0

    def test_construction_labor_stall(self, state, config):
        """Project stalls when required labor is unavailable."""
        lga = 0
        state.inventories[lga, CONSTRUCTION_MATERIALS] = 1e8

        # Demand more labor than exists
        labor_demand = {0: 999_999_999}
        project = _make_project(lga_id=lga, months=3, labor_demand=labor_demand)
        state.construction_projects = [project]

        # Set all labor as already employed
        if state.labor_employed is not None:
            state.labor_employed[lga, :] = state.labor_pool[lga, :]

        _tick_construction(state, config)

        assert state.construction_projects[0].months_remaining == 3
        assert state.construction_projects[0].funded is False

    def test_construction_reserves_labor(self, state, config):
        """Successful construction should increase labor_employed."""
        lga = 0
        state.inventories[lga, CONSTRUCTION_MATERIALS] = 1e8

        labor_demand = {0: 100}
        project = _make_project(lga_id=lga, months=3, monthly_cost=1e6,
                                labor_demand=labor_demand)
        state.construction_projects = [project]

        initial_employed = float(state.labor_employed[lga, 0]) if state.labor_employed is not None else 0
        _tick_construction(state, config)

        if state.labor_employed is not None:
            final_employed = float(state.labor_employed[lga, 0])
            assert final_employed >= initial_employed + 100

    def test_policy_starts_construction(self, state, config):
        """start_construction policy should add a ConstructionProject."""
        policy = PolicyAction(
            action_type="start_construction",
            parameters={
                "project_type": "factory",
                "lga_id": 5,
                "months": 6,
                "monthly_cost": 5e8,
                "labor_demand": {0: 50},
                "completion_effect": {"production_capacity": {"commodity_id": 25, "amount": 1000}},
            },
            source="legislative",
            enacted_game_day=0,
            implementation_delay=0,
        )
        process_policy(state, policy, config)

        assert len(state.construction_projects) == 1
        p = state.construction_projects[0]
        assert p.project_type == "factory"
        assert p.lga_id == 5
        assert p.months_remaining == 6
