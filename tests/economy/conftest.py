"""Shared test fixtures for economy tests."""

import pytest
import numpy as np

from src.economy.core.types import SimConfig, EconomicState
from src.economy.core.initialize import initialize_state


@pytest.fixture
def config():
    """Default SimConfig."""
    return SimConfig()


@pytest.fixture
def state(config):
    """Fully initialized EconomicState from LGA data."""
    return initialize_state(config)


@pytest.fixture
def micro_state():
    """
    Small 5-LGA micro-economy for fast tests.
    Uses the full state but masks down to 5 representative LGAs.
    """
    config = SimConfig()
    return initialize_state(config)
