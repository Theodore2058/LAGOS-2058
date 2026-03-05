"""
Full 12-turn campaign simulation with all 14 parties and political capital.

Usage:
    python examples/run_full_campaign.py

Demonstrates:
- All 14 parties from run_election.py with full position vectors
- Political capital income (7 PC/turn), hoarding cap (18 PC), costs per action
- 12 campaign turns with strategic action sequences
- Crisis events in turns 4, 8, 11
- ETO engagement and Economic ETO dividends

PC Budget per party per turn: 7 income. Total over 12 turns = 84 PC.
Hoarding cap = 18, so parties must spend or lose surplus.

Action costs:
  rally=2, advertising=2-4, manifesto=3, ground_game=3, endorsement=2,
  ethnic_mob=3, patronage=4, oppo_research=2, media=1, eto=3,
  crisis_response=2, fundraising=0(+3), poll=1, pledge=0
"""

import sys
import logging
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.campaign import run_campaign
from election_engine.campaign_actions import ActionSpec, PC_COSTS
from election_engine.campaign_state import CrisisEvent
from election_engine.results import (
    compute_vote_counts, compute_state_vote_counts,
    compute_competitiveness, compute_vote_source_decomposition,
    compute_coalition_feasibility, compute_demographic_vote_profile,
    allocate_district_seats,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

DATA_PATH = str(Path(__file__).parent.parent / "data" / "nigeria_lga_polsim_2058.xlsx")

# ---------------------------------------------------------------------------
# Import party definitions from run_election.py
# ---------------------------------------------------------------------------
from run_election import PARTIES

# Use calibrated parameters for 14-party election
# Lower tau_0 for first-election-in-decades scenario: high political excitement
# drives turnout well above typical levels. Campaign actions (rallies, ground_game)
# further reduce tau via the tau modifier channel.
params = EngineParams(
    q=0.5, beta_s=3.0, alpha_e=3.0, alpha_r=2.0,
    scale=1.5, tau_0=3.0, tau_1=0.3, tau_2=0.5,
    beta_econ=0.3,
    kappa=400.0, sigma_national=0.07, sigma_regional=0.10,
    sigma_turnout=0.02, sigma_turnout_regional=0.03,
)

config = ElectionConfig(params=params, parties=PARTIES, n_monte_carlo=5)

party_names = [p.name for p in PARTIES]

# ---------------------------------------------------------------------------
# 12-Turn Campaign Design
# ---------------------------------------------------------------------------
# Strategic logic:
# - Turns 1-3: Foundation phase (manifestos, base mobilization, fundraising)
# - Turns 4-6: Engagement phase (advertising, endorsements, ETO building)
# - Turns 7-9: Intensification (ground game, opposition research, rallies)
# - Turns 10-12: Final push (ethnic mobilization, heavy advertising, rallies)

# ===== TURN 1: Opening Salvo =====
# Every party publishes manifesto (3 PC) + fundraising (0 PC) = 3 PC of 7
turn1 = [
    # Major parties: manifesto + fundraising + media
    ActionSpec(party="NRP", action_type="manifesto", params={}),
    ActionSpec(party="NRP", action_type="fundraising", params={}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),

    ActionSpec(party="CND", action_type="manifesto", params={}),
    ActionSpec(party="CND", action_type="fundraising", params={}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.6}),

    ActionSpec(party="ANPC", action_type="manifesto", params={}),
    ActionSpec(party="ANPC", action_type="fundraising", params={}),

    ActionSpec(party="IPA", action_type="manifesto", params={}),
    ActionSpec(party="IPA", action_type="fundraising", params={}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.5}),

    ActionSpec(party="NDC", action_type="manifesto", params={}),
    ActionSpec(party="NDC", action_type="fundraising", params={}),

    ActionSpec(party="UJP", action_type="manifesto", params={}),
    ActionSpec(party="UJP", action_type="rally", language="hausa", params={"gm_score": 7.0}),

    ActionSpec(party="NWF", action_type="manifesto", params={}),
    ActionSpec(party="NWF", action_type="fundraising", params={}),

    ActionSpec(party="NHA", action_type="manifesto", params={}),
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),

    ActionSpec(party="SNM", action_type="manifesto", params={}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 6.0}),

    ActionSpec(party="NSA", action_type="manifesto", params={}),
    ActionSpec(party="NSA", action_type="fundraising", params={}),

    ActionSpec(party="CDA", action_type="manifesto", params={}),
    ActionSpec(party="CDA", action_type="fundraising", params={}),

    ActionSpec(party="MBPP", action_type="manifesto", params={}),
    ActionSpec(party="MBPP", action_type="fundraising", params={}),

    ActionSpec(party="PLF", action_type="manifesto", params={}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),

    ActionSpec(party="NNV", action_type="manifesto", params={}),
    ActionSpec(party="NNV", action_type="fundraising", params={}),
]

# ===== TURN 2: Base Building =====
# Parties start advertising and doing ground game in their strongholds
turn2 = [
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.5}),
    ActionSpec(party="NRP", action_type="endorsement",
              params={"endorser_type": "celebrity"}),

    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="ANPC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="IPA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 5, "score_change": 3.0}),

    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NDC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="NDC", action_type="fundraising", params={}),

    ActionSpec(party="UJP", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),
    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 7.0}),
    ActionSpec(party="NWF", action_type="fundraising", params={}),

    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NHA", action_type="endorsement",
              params={"endorser_type": "notable"}),

    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 7.0}),
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),

    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 6.0}),

    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="CDA", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 6, "score_change": 3.0}),

    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),

    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NNV", action_type="rally", language="hausa", params={"gm_score": 6.0}),
]

# ===== TURN 3: Ethnic Outreach =====
turn3 = [
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="NRP", action_type="poll", params={}),

    ActionSpec(party="CND", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Yoruba"}),
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 1.0}),

    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="ANPC", action_type="patronage", params={"scale": 1.0}),

    ActionSpec(party="IPA", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Igbo"}),
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 7.0}),

    ActionSpec(party="NDC", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Hausa-Fulani Undiff"}),
    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="UJP", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Kanuri"}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 7.0}),

    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 7.0}),
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="NHA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),

    ActionSpec(party="SNM", action_type="opposition_research",
              params={"target_party": "NHA", "target_dimensions": [2, 21]}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 7.0}),

    ActionSpec(party="NSA", action_type="endorsement",
              params={"endorser_type": "notable"}),
    ActionSpec(party="NSA", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 7, "score_change": 2.0}),

    ActionSpec(party="CDA", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Tiv"}),
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="MBPP", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Middle Belt Minorities"}),
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 6.0}),

    ActionSpec(party="PLF", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Ijaw"}),
    ActionSpec(party="PLF", action_type="opposition_research",
              params={"target_party": "NRP", "target_dimensions": [7, 18]}),

    ActionSpec(party="NNV", action_type="rally", language="hausa", params={"gm_score": 7.0}),
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),
]

# ===== TURN 4: First Crisis =====
turn4 = [
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NRP", action_type="fundraising", params={}),

    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 8.0}),
    ActionSpec(party="CND", action_type="endorsement",
              params={"endorser_type": "celebrity"}),

    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.5}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.6}),

    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 1.5}),
    ActionSpec(party="IPA", action_type="endorsement",
              params={"endorser_type": "eto_leader"}),

    ActionSpec(party="NDC", action_type="patronage", params={"scale": 1.0}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 8.0}),

    ActionSpec(party="UJP", action_type="crisis_response", params={"effectiveness": 0.7}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 8.0}),

    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 7.0}),

    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.5}),
    ActionSpec(party="NHA", action_type="fundraising", params={}),

    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.4}),

    ActionSpec(party="NSA", action_type="crisis_response", params={"effectiveness": 0.8}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 7.0}),

    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),

    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 6.0}),

    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    ActionSpec(party="NNV", action_type="crisis_response", params={"effectiveness": 0.6}),
    ActionSpec(party="NNV", action_type="rally", language="hausa", params={"gm_score": 7.0}),
]

# ===== TURN 5: Advertising Blitz =====
turn5 = [
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NRP", action_type="endorsement",
              params={"endorser_type": "notable"}),

    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="CND", action_type="fundraising", params={}),

    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="ANPC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 8.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="NDC", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="UJP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 7, "score_change": 3.0}),

    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="endorsement",
              params={"endorser_type": "notable"}),

    ActionSpec(party="NHA", action_type="rally", language="mandarin", params={"gm_score": 7.0}),
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),

    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="SNM", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.5}),
    ActionSpec(party="NSA", action_type="fundraising", params={}),

    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="CDA", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    ActionSpec(party="MBPP", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),

    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="PLF", action_type="fundraising", params={}),

    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.5}),
    ActionSpec(party="NNV", action_type="rally", language="hausa", params={"gm_score": 7.0}),
]

# ===== TURN 6: Opposition Research =====
turn6 = [
    ActionSpec(party="NRP", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 4, 14]}),
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 8.0}),

    ActionSpec(party="CND", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 5]}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 8.0}),

    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.5}),
    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="IPA", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [4, 9]}),
    ActionSpec(party="IPA", action_type="fundraising", params={}),
    ActionSpec(party="IPA", action_type="poll", params={}),

    ActionSpec(party="NDC", action_type="opposition_research",
              params={"target_party": "CND", "target_dimensions": [2, 11]}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 9.0}),

    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 8.0}),
    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="NWF", action_type="opposition_research",
              params={"target_party": "IPA", "target_dimensions": [10, 18]}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),

    ActionSpec(party="NHA", action_type="opposition_research",
              params={"target_party": "SNM", "target_dimensions": [2, 21]}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.7}),

    ActionSpec(party="SNM", action_type="opposition_research",
              params={"target_party": "NHA", "target_dimensions": [2, 21]}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 7.0}),

    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 7.0}),
    ActionSpec(party="NSA", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="CDA", action_type="opposition_research",
              params={"target_party": "UJP", "target_dimensions": [0, 14]}),
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 7.0}),

    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="MBPP", action_type="fundraising", params={}),

    ActionSpec(party="PLF", action_type="opposition_research",
              params={"target_party": "NRP", "target_dimensions": [8, 18, 24]}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),

    ActionSpec(party="NNV", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 6]}),
    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 7.0}),
]

# ===== TURN 7: Ground Game Intensification =====
turn7 = [
    ActionSpec(party="NRP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 8.0}),

    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 8.0}),

    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 7.0}),

    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 8.0}),

    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 9.0}),

    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 8.0}),

    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),

    ActionSpec(party="NHA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 7.0}),

    ActionSpec(party="SNM", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="SNM", action_type="fundraising", params={}),

    ActionSpec(party="NSA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 7.0}),

    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 7.0}),

    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 7.0}),

    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),

    ActionSpec(party="NNV", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 7.0}),
]

# ===== TURN 8: Second Crisis (WAFTA Trade Dispute) =====
turn8 = [
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="NRP", action_type="endorsement",
              params={"endorser_type": "celebrity"}),

    ActionSpec(party="CND", action_type="crisis_response", params={"effectiveness": 0.6}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 8.0}),

    ActionSpec(party="ANPC", action_type="patronage", params={"scale": 1.0}),
    ActionSpec(party="ANPC", action_type="fundraising", params={}),

    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 8.0}),
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 1.0}),

    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.5}),

    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 9.0}),
    ActionSpec(party="UJP", action_type="fundraising", params={}),

    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),
    ActionSpec(party="NWF", action_type="crisis_response", params={"effectiveness": 0.5}),

    ActionSpec(party="NHA", action_type="crisis_response", params={"effectiveness": 0.8}),
    ActionSpec(party="NHA", action_type="advertising", language="mandarin",
              params={"medium": "social_media", "budget": 1.5}),

    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.5}),

    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),

    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="CDA", action_type="fundraising", params={}),

    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="MBPP", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.5}),

    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="NNV", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),
]

# ===== TURN 9: ETO Building & Endorsements =====
turn9 = [
    ActionSpec(party="NRP", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 8.0}),

    ActionSpec(party="CND", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 2, "score_change": 3.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 8.0}),

    ActionSpec(party="ANPC", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 3, "score_change": 3.0}),
    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 7.0}),

    ActionSpec(party="IPA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 5, "score_change": 3.0}),
    ActionSpec(party="IPA", action_type="endorsement",
              params={"endorser_type": "eto_leader"}),

    ActionSpec(party="NDC", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 8, "score_change": 3.0}),
    ActionSpec(party="NDC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    ActionSpec(party="UJP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 7, "score_change": 3.0}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 8.0}),

    ActionSpec(party="NWF", action_type="endorsement",
              params={"endorser_type": "notable"}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),

    ActionSpec(party="NHA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NHA", action_type="poll", params={}),

    ActionSpec(party="SNM", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 8.0}),

    ActionSpec(party="NSA", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 7, "score_change": 3.0}),
    ActionSpec(party="NSA", action_type="endorsement",
              params={"endorser_type": "notable"}),

    ActionSpec(party="CDA", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 5, "score_change": 3.0}),
    ActionSpec(party="CDA", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    ActionSpec(party="PLF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 4, "score_change": 3.0}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),

    ActionSpec(party="NNV", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 6, "score_change": 3.0}),
    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 7.0}),
]

# ===== TURN 10: Heavy Advertising Push =====
turn10 = [
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 9.0}),

    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 9.0}),

    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="ANPC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 9.0}),

    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 9.0}),

    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 9.0}),

    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),

    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 8.0}),

    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 9.0}),

    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 8.0}),

    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 8.0}),

    ActionSpec(party="MBPP", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 8.0}),

    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),

    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NNV", action_type="rally", language="hausa", params={"gm_score": 8.0}),
]

# ===== TURN 11: Third Crisis (Religious Tensions) =====
turn11 = [
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="NRP", action_type="endorsement",
              params={"endorser_type": "notable"}),

    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 9.0}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="ANPC", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 9.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 10.0}),
    ActionSpec(party="NDC", action_type="crisis_response", params={"effectiveness": 0.7}),

    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 10.0}),
    ActionSpec(party="UJP", action_type="crisis_response", params={"effectiveness": 0.8}),

    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="NHA", action_type="endorsement",
              params={"endorser_type": "celebrity"}),

    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="SNM", action_type="crisis_response", params={"effectiveness": 0.5}),

    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="NSA", action_type="crisis_response", params={"effectiveness": 0.9}),

    ActionSpec(party="CDA", action_type="crisis_response", params={"effectiveness": 0.8}),
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 9.0}),

    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 10.0}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),

    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="NNV", action_type="crisis_response", params={"effectiveness": 0.7}),
]

# ===== TURN 12: Final Push =====
turn12 = [
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 10.0}),
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),

    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 10.0}),
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 2.0}),

    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),

    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 10.0}),
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 2.0}),

    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 10.0}),
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),

    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 10.0}),
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.5}),

    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 10.0}),
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.5}),

    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),

    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 10.0}),
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),

    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),

    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 2.0}),

    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="MBPP", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.5}),

    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 10.0}),
    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 2.0}),

    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 10.0}),
    ActionSpec(party="NNV", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
]

turns = [turn1, turn2, turn3, turn4, turn5, turn6,
         turn7, turn8, turn9, turn10, turn11, turn12]

# ---------------------------------------------------------------------------
# Crisis Events
# ---------------------------------------------------------------------------

crisis_events = [
    # Turn 4: Security incident in the Northeast
    CrisisEvent(
        name="Security incident in Northeast",
        turn=4,
        affected_lgas=None,  # national impact
        salience_shifts={12: 0.08, 11: 0.05},  # military_role + immigration salience
        valence_effects={"NSA": +0.05, "UJP": -0.05, "NDC": -0.03},
        awareness_boost={"NSA": 0.04, "NNV": 0.02},
    ),
    # Turn 8: WAFTA trade dispute — Chinese tariffs
    CrisisEvent(
        name="WAFTA trade dispute",
        turn=8,
        affected_lgas=None,
        salience_shifts={2: 0.10, 21: 0.06},  # chinese_relations + trade_policy
        valence_effects={"NHA": -0.05, "SNM": +0.05},
        awareness_boost={"SNM": 0.04, "NHA": 0.03},
    ),
    # Turn 11: Religious tensions in Middle Belt
    CrisisEvent(
        name="Religious tensions in Middle Belt",
        turn=11,
        affected_lgas=None,
        salience_shifts={0: 0.08, 14: 0.04},  # sharia + womens_rights
        valence_effects={"CDA": +0.04, "UJP": -0.04, "NDC": -0.02},
        awareness_boost={"CDA": 0.04, "UJP": 0.03},
    ),
]

# ---------------------------------------------------------------------------
# Run Campaign
# ---------------------------------------------------------------------------

def _weighted_shares(lga_df, party_names):
    """Compute population-weighted national shares."""
    pop = lga_df["Estimated Population"].values.astype(float)
    total_pop = pop.sum()
    shares = {}
    for p in party_names:
        shares[p] = (lga_df[f"{p}_share"].values * pop).sum() / total_pop
    return shares, pop, total_pop


def _weighted_turnout(lga_df, pop, total_pop):
    return (lga_df["Turnout"].values * pop).sum() / total_pop


def print_turn_summary(i, result, party_names):
    """Print compact per-turn summary."""
    lga_df = result["lga_results_base"]
    shares, pop, total_pop = _weighted_shares(lga_df, party_names)
    turnout = _weighted_turnout(lga_df, pop, total_pop)
    sorted_shares = sorted(shares.items(), key=lambda x: -x[1])

    print(f"\n--- Turn {i+1} ---")
    for p, s in sorted_shares:
        pc = result.get("pc_state", {}).get(p, 0)
        print(f"  {p:6s}: {s:6.1%}  (PC: {pc:.0f})")
    print(f"  Turnout: {turnout:.1%}")


def print_detailed_final(result, party_names, data_path):
    """Print detailed final results matching run_election.py output."""
    import pandas as pd

    lga_df = result["lga_results_base"]
    shares, pop, total_pop = _weighted_shares(lga_df, party_names)
    turnout = _weighted_turnout(lga_df, pop, total_pop)
    sorted_parties = sorted(shares.items(), key=lambda x: -x[1])

    # --- National results with vote counts ---
    lga_with_votes = compute_vote_counts(lga_df, party_names)
    total_votes = lga_with_votes["Total_Votes"].sum()

    print("\n" + "=" * 70)
    print("FINAL ELECTION RESULTS (Turn 12)")
    print("=" * 70)

    print(f"\nNational Turnout: {turnout:.1%}")
    print(f"Total Votes Cast: {total_votes:,.0f}")

    # ENP
    s_arr = np.array([s for _, s in sorted_parties])
    enp = 1.0 / np.sum(s_arr ** 2)
    print(f"Effective Number of Parties (ENP): {enp:.2f}")

    print(f"\nNATIONAL RESULTS:")
    print(f"  {'Party':10s}  {'Votes':>12s}  {'Share':>7s}  {'PC':>4s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*7}  {'-'*4}")
    for p, share in sorted_parties:
        votes_col = f"{p}_votes"
        if votes_col in lga_with_votes.columns:
            votes = lga_with_votes[votes_col].sum()
        else:
            votes = share * total_votes
        pc = result.get("pc_state", {}).get(p, 0)
        print(f"  {p:10s}  {votes:12,.0f}  {share:6.1%}  {pc:4.0f}")

    # --- Presidential spread check ---
    from election_engine.results import check_presidential_spread
    print("\nPRESIDENTIAL SPREAD CHECK (>=25% in >=24 states + national plurality):")
    for p, _ in sorted_parties:
        sc = check_presidential_spread(lga_df, p, party_names)
        mark = "PASS" if sc["meets_requirement"] else "FAIL"
        plurality = "yes" if sc["has_national_plurality"] else "no"
        print(f"  {p:10s}  {mark}  ({sc['states_meeting_25pct']:2d}/24 states, "
              f"plurality: {plurality}, national: {sc['national_share']:.1%})")

    # --- MC results ---
    mc = result.get("mc_aggregated")
    if mc:
        ns = mc.get("national_share_stats")
        if ns is not None:
            print("\nMC NATIONAL SHARE UNCERTAINTY (mean [P5 - P95]):")
            ns_sorted = ns.sort_values("Mean Share", ascending=False)
            for _, row in ns_sorted.iterrows():
                if row["Mean Share"] >= 0.005:
                    print(f"  {row['Party']:10s}  {row['Mean Share']:6.1%}  "
                          f"[{row['P5 Share']:5.1%} - {row['P95 Share']:5.1%}]")

        margin_stats = mc.get("margin_stats")
        if margin_stats:
            print(f"\nMC NATIONAL MARGIN (1st-2nd): "
                  f"mean {margin_stats['mean']:.1%}  "
                  f"[P5 {margin_stats['p5']:.1%} - P95 {margin_stats['p95']:.1%}]")

    # --- Zonal shares ---
    summary = result.get("summary", {})
    zonal = summary.get("zonal_shares")
    if zonal is not None:
        print("\nZONAL SHARES:")
        party_share_cols = [c for c in zonal.columns if c.endswith("_share") and c != "Turnout"]
        cols_to_show = ["Administrative Zone", "AZ Name"]
        if "Turnout" in zonal.columns:
            cols_to_show.append("Turnout")
        cols_to_show.extend(party_share_cols)
        print(zonal[cols_to_show].to_string(index=False))

    # --- State vote counts ---
    state_votes = compute_state_vote_counts(lga_df, party_names)
    top3 = [p for p, _ in sorted_parties[:3]]
    print("\nSTATE VOTE COUNTS (top 3 parties):")
    top3_vote_cols = [f"{p}_votes" for p in top3]
    top3_share_cols = [f"{p}_share" for p in top3]
    sv_cols = ["State", "Population", "Total_Votes"] + top3_vote_cols + top3_share_cols
    available_sv = [c for c in sv_cols if c in state_votes.columns]
    print(state_votes[available_sv].to_string(index=False))

    # --- Voting district results ---
    project_root = Path(data_path).parent
    district_file = project_root / "voting_districts_summary.xlsx"
    seat_file = project_root / "seat_allocation.xlsx"
    if district_file.exists() and seat_file.exists():
        lga_mapping = pd.read_excel(district_file, sheet_name="LGA Mapping")
        district_seats = pd.read_excel(seat_file, sheet_name="District Seats")

        dist_df = allocate_district_seats(
            lga_df, party_names, district_seats, lga_mapping,
        )
        total_seats = dist_df["Seats"].sum()

        national_seats = {p: int(dist_df[f"{p}_seats"].sum()) for p in party_names}
        sorted_seats = sorted(national_seats.items(), key=lambda x: -x[1])
        print(f"\nNATIONAL SEAT TOTALS (Sainte-Lague, {total_seats} seats):")
        print(f"  {'Party':10s}  {'Seats':>5s}  {'%':>6s}  {'Vote %':>7s}")
        print(f"  {'-'*10}  {'-'*5}  {'-'*6}  {'-'*7}")
        for p, s in sorted_seats:
            if s > 0:
                pct = s / total_seats
                vote_share = shares.get(p, 0)
                print(f"  {p:10s}  {s:5d}  {pct:5.1%}  {vote_share:6.1%}")

        # Zonal seat breakdown
        print(f"\nZONAL SEAT BREAKDOWN:")
        zone_seat_rows = []
        for az_name, zgroup in dist_df.groupby("AZ Name"):
            zrow = {"AZ Name": az_name, "Seats": int(zgroup["Seats"].sum())}
            for p in party_names:
                zrow[f"{p}_seats"] = int(zgroup[f"{p}_seats"].sum())
            zone_seat_rows.append(zrow)
        zone_seat_df = pd.DataFrame(zone_seat_rows)
        header = f"  {'Zone':25s}  {'Seats':>5s}"
        for p, _ in sorted_seats[:7]:
            header += f"  {p:>5s}"
        print(header)
        print(f"  {'-'*25}  {'-'*5}" + f"  {'-'*5}" * min(7, len(sorted_seats)))
        for _, zr in zone_seat_df.iterrows():
            line = f"  {str(zr['AZ Name']):25s}  {zr['Seats']:5d}"
            for p, _ in sorted_seats[:7]:
                line += f"  {zr[f'{p}_seats']:5d}"
            print(line)

    # --- Vote source decomposition ---
    decomp = compute_vote_source_decomposition(lga_df, party_names)
    print("\nVOTE SOURCE DECOMPOSITION (% of each party's vote by zone):")
    zone_names = decomp[party_names[0]]["Zone"].tolist()
    header = f"  {'Zone':30s}"
    for p, _ in sorted_parties[:7]:
        header += f"  {p:>7s}"
    print(header)
    print(f"  {'-'*30}" + f"  {'-'*7}" * min(7, len(sorted_parties)))
    for zone in zone_names:
        line = f"  {str(zone):30s}"
        for p, _ in sorted_parties[:7]:
            pct = decomp[p].loc[decomp[p]["Zone"] == zone, "Pct_of_Party_Total"].values[0]
            line += f"  {pct:6.1%}"
        print(line)

    # --- Ethnic vote profile ---
    data_obj = result.get("data")
    if data_obj is not None:
        source_df = data_obj.df
    else:
        from election_engine.data_loader import load_lga_data
        source_df = load_lga_data(data_path).df

    ethnic_cols = {
        "Hausa": "% Hausa", "Fulani": "% Fulani",
        "Hausa-Fulani Undiff": "% Hausa Fulani Undiff",
        "Yoruba": "% Yoruba", "Igbo": "% Igbo", "Ijaw": "% Ijaw",
        "Kanuri": "% Kanuri", "Tiv": "% Tiv", "Edo": "% Edo Bini",
        "Ibibio": "% Ibibio", "Pada": "% Pada", "Naijin": "% Naijin",
    }
    eth_profile = compute_demographic_vote_profile(lga_df, source_df, party_names, ethnic_cols)
    if len(eth_profile) > 0:
        print("\nETHNIC VOTE PROFILE (ecological estimate, top 5 parties per group):")
        for _, row in eth_profile.iterrows():
            group_shares = {p: row[f"{p}_share"] for p in party_names}
            top5 = sorted(group_shares.items(), key=lambda x: -x[1])[:5]
            top_str = "  ".join(f"{p}:{s:.0%}" for p, s in top5)
            pop_m = row["Population_Weight"] / 1e6
            print(f"  {row['Group']:22s} ({pop_m:5.1f}M)  {top_str}")

    # --- Competitiveness ---
    comp = compute_competitiveness(lga_df, party_names)
    margins = comp["Margin"].values
    enps = comp["ENP"].values
    print(f"\nLGA COMPETITIVENESS:")
    print(f"  Margin:  Mean: {margins.mean():.1%}  Median: {np.median(margins):.1%}  "
          f"Min: {margins.min():.1%}  Max: {margins.max():.1%}")
    print(f"  ENP:     Mean: {enps.mean():.2f}  Median: {np.median(enps):.2f}  "
          f"Min: {enps.min():.2f}  Max: {enps.max():.2f}")
    n_tight = np.sum(margins < 0.05)
    n_safe = np.sum(margins > 0.20)
    print(f"  Tight (<5% margin): {n_tight}  |  Safe (>20% margin): {n_safe}")

    # --- Turnout distribution ---
    t = lga_df["Turnout"].values
    print(f"\nTURNOUT DISTRIBUTION:")
    print(f"  Mean: {t.mean():.1%}  Median: {np.median(t):.1%}  "
          f"Min: {t.min():.1%}  Max: {t.max():.1%}  Std: {t.std():.1%}")
    for threshold in [0.60, 0.70, 0.80, 0.85, 0.90]:
        n = np.sum(t > threshold)
        print(f"  LGAs > {threshold:.0%}: {n}")

    # --- Coalition feasibility ---
    coalitions = compute_coalition_feasibility(lga_df, party_names)
    viable = [c for c in coalitions if c["meets_spread"]]
    print(f"\nCOALITION FEASIBILITY (2-3 party, meets spread requirement): "
          f"{len(viable)} viable")
    if viable:
        for c in viable[:10]:
            names = "+".join(c["parties"])
            print(f"  {names:30s}  {c['combined_share']:5.1%}  "
                  f"({c['states_25pct']:2d}/24 states)  "
                  f"margin: {c['margin_over_second']:+.1%}")
    else:
        print("  No coalition meets all requirements. Closest:")
        near = sorted(coalitions, key=lambda c: -c["states_25pct"])[:5]
        for c in near:
            names = "+".join(c["parties"])
            plur = "Y" if c["margin_over_second"] > 0 else "N"
            print(f"  {names:30s}  {c['combined_share']:5.1%}  "
                  f"({c['states_25pct']:2d}/24 states)  plur: {plur}")


def main():
    print("=" * 70)
    print("LAGOS-2058 Full Campaign Simulation — 14 Parties, 12 Turns")
    print(f"PC Income: {7}/turn | Hoarding Cap: {18} | Max 3 actions/party/turn")
    print(f"tau_0: {params.tau_0} (first election in decades — high turnout)")
    print(f"3 Crisis Events | {len(turns)} Turns")
    print("=" * 70)

    results = run_campaign(
        DATA_PATH,
        config,
        turns=turns,
        crisis_events=crisis_events,
        seed=2058,
        verbose=True,
        enforce_pc=True,
        max_actions_per_party=3,
    )

    # Per-turn summaries
    print("\n" + "=" * 70)
    print("TURN-BY-TURN SUMMARY")
    print("=" * 70)
    for i, result in enumerate(results):
        print_turn_summary(i, result, party_names)

    # Detailed final results
    print_detailed_final(results[-1], party_names, DATA_PATH)

    print("\n" + "=" * 70)
    print("Campaign simulation complete.")


if __name__ == "__main__":
    main()
