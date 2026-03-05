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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

DATA_PATH = str(Path(__file__).parent.parent / "nigeria_lga_polsim_2058.xlsx")

# ---------------------------------------------------------------------------
# Import party definitions from run_election.py
# ---------------------------------------------------------------------------
from run_election import PARTIES

# Use calibrated parameters for 14-party election
params = EngineParams(
    q=0.5, beta_s=3.0, alpha_e=3.0, alpha_r=2.0,
    scale=1.5, tau_0=4.5, tau_1=0.3, tau_2=0.5,
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

def main():
    print("=" * 70)
    print("LAGOS-2058 Full Campaign Simulation — 14 Parties, 12 Turns")
    print(f"PC Income: {7}/turn | Hoarding Cap: {18} | 3 Crisis Events")
    print("=" * 70)

    results = run_campaign(
        DATA_PATH,
        config,
        turns=turns,
        crisis_events=crisis_events,
        seed=2058,
        verbose=True,
        enforce_pc=True,
    )

    # Print results
    print("\n" + "=" * 70)
    print("CAMPAIGN RESULTS")
    print("=" * 70)

    for i, result in enumerate(results):
        lga_df = result["lga_results_base"]
        pop = lga_df["Estimated Population"].values.astype(float)
        total_pop = pop.sum()

        print(f"\nTurn {i+1}:")
        shares = {}
        for p in party_names:
            share = (lga_df[f"{p}_share"].values * pop).sum() / total_pop
            shares[p] = share

        # Sort by share descending
        sorted_shares = sorted(shares.items(), key=lambda x: -x[1])
        for p, s in sorted_shares:
            print(f"  {p:6s}: {s:6.1%}", end="")
            # Show PC balance
            pc = result.get("pc_state", {}).get(p, "?")
            if isinstance(pc, (int, float)):
                print(f"  (PC: {pc:.0f})", end="")
            print()

        turnout = (lga_df["Turnout"].values * pop).sum() / total_pop
        print(f"  Turnout: {turnout:.1%}")

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL STANDINGS (Turn 12)")
    print("=" * 70)
    final_result = results[-1]
    lga_df = final_result["lga_results_base"]
    pop = lga_df["Estimated Population"].values.astype(float)
    total_pop = pop.sum()

    final_shares = {}
    for p in party_names:
        final_shares[p] = (lga_df[f"{p}_share"].values * pop).sum() / total_pop

    sorted_final = sorted(final_shares.items(), key=lambda x: -x[1])
    print(f"\n  {'Party':6s}  {'Share':>7s}  {'PC':>4s}")
    print(f"  {'------':6s}  {'-------':>7s}  {'----':>4s}")
    for p, s in sorted_final:
        pc = final_result.get("pc_state", {}).get(p, 0)
        print(f"  {p:6s}  {s:6.1%}  {pc:4.0f}")

    turnout = (lga_df["Turnout"].values * pop).sum() / total_pop
    print(f"\n  National Turnout: {turnout:.1%}")
    print("\n" + "=" * 70)
    print("Campaign simulation complete.")


if __name__ == "__main__":
    main()
