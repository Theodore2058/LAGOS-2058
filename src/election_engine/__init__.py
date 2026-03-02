"""LAGOS-2058 Election Engine — spatial voting simulation for 774 Nigerian LGAs."""

from .config import (
    ISSUE_NAMES,
    N_ISSUES,
    EngineParams,
    Party,
    ElectionConfig,
)
from .results import compute_vote_counts

__all__ = [
    "ISSUE_NAMES",
    "N_ISSUES",
    "EngineParams",
    "Party",
    "ElectionConfig",
    "compute_vote_counts",
]
