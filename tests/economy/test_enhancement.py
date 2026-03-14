"""
Enhancement technology diffusion tests (Priority 2A).

Tests that enhancement adoption spreads between LGAs, is modulated by
infrastructure and al-Shahid control, and stays bounded.
"""

import numpy as np
import pytest

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.systems.enhancement import tick_enhancement, apply_enhancement_diffusion


@pytest.fixture
def config():
    return SimConfig()


@pytest.fixture
def state(config):
    return initialize_state(config)


class TestEnhancementDiffusion:
    def test_adoption_increases_over_time(self, state, config):
        """Enhancement adoption should generally increase via diffusion."""
        initial_mean = float(state.enhancement_adoption.mean())
        new = tick_enhancement(state, config)
        new_mean = float(new.mean())
        assert new_mean >= initial_mean, (
            f"Adoption should not decrease on average: {initial_mean:.4f} -> {new_mean:.4f}"
        )

    def test_adoption_bounded(self, state, config):
        """Adoption always stays in [0, 1]."""
        # Start near saturation
        state.enhancement_adoption[:] = 0.95
        new = tick_enhancement(state, config)
        assert np.all(new >= 0.0)
        assert np.all(new <= 1.0)

    def test_alsahid_slows_adoption(self, state, config):
        """High al-Shahid control should slow enhancement adoption."""
        state.enhancement_adoption[:] = 0.3

        # No al-Shahid
        state.alsahid_control[:] = 0.0
        new_free = tick_enhancement(state, config)

        # High al-Shahid
        state.alsahid_control[:] = 0.9
        new_controlled = tick_enhancement(state, config)

        assert new_free.mean() > new_controlled.mean(), (
            "Al-Shahid control should slow adoption"
        )

    def test_diffusion_spreads_from_high_to_low(self, state, config):
        """LGAs with low adoption near high-adoption zones should gain more."""
        # Set up: zone 0 = high, zone 1 = low
        if state.admin_zone is not None:
            zone0 = state.admin_zone == 0
            zone1 = state.admin_zone == 1
            state.enhancement_adoption[zone0] = 0.9
            state.enhancement_adoption[zone1] = 0.1

            new = tick_enhancement(state, config)

            # Zone 1 LGAs should have increased
            initial_z1 = 0.1
            new_z1 = float(new[zone1].mean())
            assert new_z1 > initial_z1, (
                f"Low-adoption zone should gain: {initial_z1:.3f} -> {new_z1:.3f}"
            )

    def test_apply_updates_state(self, state, config):
        """apply_enhancement_diffusion should update state.enhancement_adoption."""
        new = tick_enhancement(state, config)
        apply_enhancement_diffusion(state, new)
        np.testing.assert_array_equal(state.enhancement_adoption, new)

    def test_integration_structural_tick(self, state, config):
        """Enhancement diffusion runs as part of structural tick."""
        from src.economy.core.scheduler import TickScheduler
        initial = state.enhancement_adoption.copy()

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_structural_tick()

        # Adoption should have changed
        assert not np.array_equal(state.enhancement_adoption, initial), \
            "Enhancement adoption should change after structural tick"
