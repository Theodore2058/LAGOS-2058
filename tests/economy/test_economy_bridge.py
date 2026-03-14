"""
Tests for economy-election bridge: updating LGA data from economic state.
"""

import numpy as np
import pandas as pd
import pytest

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.election_engine.economy_bridge import update_lga_data_from_economy


@pytest.fixture
def econ_sim():
    """Run a short economic simulation and return (state, config)."""
    config = SimConfig(SEED=42)
    state = initialize_state(config)
    scheduler = TickScheduler(state=state, config=config)
    # Run 3 months to get the economy past initialization transients
    scheduler.run_mixed_ticks(n_months=3)
    return state, config


@pytest.fixture
def lga_data(econ_sim):
    """Create a minimal LGA DataFrame with the columns the election engine expects."""
    state, config = econ_sim
    N = config.N_LGAS
    return pd.DataFrame({
        "Poverty Rate Pct": np.full(N, 30.0),
        "Unemployment Rate Pct": np.full(N, 15.0),
        "GDP Per Capita Est": np.full(N, 18000.0),
        "Road Quality Index": np.full(N, 5.0),
        "Elec_pct": np.full(N, 50.0),
        "Conflict History": np.full(N, 0.0),
        "Gini Proxy": np.full(N, 0.4),
    })


class TestEconomyBridge:
    def test_bridge_updates_unemployment(self, econ_sim, lga_data):
        """Bridge should update unemployment from labor market data."""
        state, config = econ_sim
        update_lga_data_from_economy(lga_data, state, config)

        unemp = lga_data["Unemployment Rate Pct"].values
        # Should be between 0 and 100
        assert unemp.min() >= 0.0
        assert unemp.max() <= 100.0
        # Should not all be the default 15%
        assert not np.allclose(unemp, 15.0)

    def test_bridge_updates_gdp(self, econ_sim, lga_data):
        """Bridge should update GDP per capita from production/prices."""
        state, config = econ_sim
        update_lga_data_from_economy(lga_data, state, config)

        gdp = lga_data["GDP Per Capita Est"].values
        # Should be positive
        assert gdp.min() > 0
        # Should not all be the default 18000
        assert not np.allclose(gdp, 18000.0)

    def test_bridge_updates_poverty(self, econ_sim, lga_data):
        """Bridge should update poverty rate from standard of living."""
        state, config = econ_sim
        update_lga_data_from_economy(lga_data, state, config)

        poverty = lga_data["Poverty Rate Pct"].values
        assert poverty.min() >= 0.0
        assert poverty.max() <= 100.0

    def test_bridge_updates_infrastructure(self, econ_sim, lga_data):
        """Bridge should update road quality and electricity access."""
        state, config = econ_sim
        update_lga_data_from_economy(lga_data, state, config)

        roads = lga_data["Road Quality Index"].values
        assert roads.min() >= 0.0
        assert roads.max() <= 10.0

        elec = lga_data["Elec_pct"].values
        assert elec.min() >= 0.0
        assert elec.max() <= 100.0

    def test_bridge_updates_conflict(self, econ_sim, lga_data):
        """Bridge should update conflict history from al-Shahid control."""
        state, config = econ_sim
        update_lga_data_from_economy(lga_data, state, config)

        conflict = lga_data["Conflict History"].values
        assert conflict.min() >= 0.0
        assert conflict.max() <= 5.0

    def test_bridge_row_count_mismatch_skips(self, econ_sim):
        """Bridge should skip update if row counts don't match."""
        state, config = econ_sim
        wrong_df = pd.DataFrame({"Poverty Rate Pct": [30.0, 30.0, 30.0]})
        result = update_lga_data_from_economy(wrong_df, state, config)
        # Should return unchanged
        assert len(result) == 3
        assert result["Poverty Rate Pct"].iloc[0] == 30.0

    def test_bridge_returns_same_dataframe(self, econ_sim, lga_data):
        """Bridge should return the same DataFrame object (mutated in place)."""
        state, config = econ_sim
        result = update_lga_data_from_economy(lga_data, state, config)
        assert result is lga_data
