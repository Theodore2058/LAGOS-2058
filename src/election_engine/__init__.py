"""LAGOS-2058 Election Engine — spatial voting simulation for 774 Nigerian LGAs."""

from .config import (
    ISSUE_NAMES,
    N_ISSUES,
    EngineParams,
    Party,
    ElectionConfig,
)
from .results import (
    compute_vote_counts,
    compute_state_vote_counts,
    effective_number_of_parties,
    compute_competitiveness,
    sainte_lague,
    allocate_district_seats,
)
from .campaign_state import (
    CampaignModifiers,
    CampaignState,
    ActiveEffect,
    CrisisEvent,
)
from .campaign_actions import ActionSpec
from .campaign import run_campaign

__all__ = [
    "ISSUE_NAMES",
    "N_ISSUES",
    "EngineParams",
    "Party",
    "ElectionConfig",
    "compute_vote_counts",
    "compute_state_vote_counts",
    "effective_number_of_parties",
    "compute_competitiveness",
    "sainte_lague",
    "allocate_district_seats",
    "CampaignModifiers",
    "CampaignState",
    "ActiveEffect",
    "CrisisEvent",
    "ActionSpec",
    "run_campaign",
]
