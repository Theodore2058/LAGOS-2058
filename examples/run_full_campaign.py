"""
Full 12-turn campaign simulation with all 14 parties and political capital.

Usage:
    python examples/run_full_campaign.py

Each party's campaign is designed to maximize seat share given their position
vectors, regional strongholds, ethnic base, and available resources.

Constraints:
- Political capital: 7 PC/turn income, 18 hoarding cap, max 3 actions/party/turn
- Every party releases a manifesto by turn 3
- Action fatigue penalizes repeating the same action type across turns
- Synergies reward pairing rally+ground_game, advertising+rally, media+oppo_research

Action costs:
  rally=2 (+1 if gm>=9), advertising=2 (+1 if budget>1.5, +2 if >2.0),
  manifesto=3, ground_game=3 (+1 if intensity>1.0), endorsement=2,
  ethnic_mob=3, patronage=4 (+1 if scale>1.0), oppo_research=2,
  media=1, eto=3, crisis_response=2, fundraising=0, poll=1, pledge=0

Strategic phases:
  Turns 1-3:  Foundation — manifestos, fundraising, initial media/endorsements
  Turns 4-6:  Expansion — advertising, ETO building, opposition research, pledges
  Turns 7-9:  Intensification — rally+ground_game synergies, ethnic mobilization
  Turns 10-12: Final push — heavy ads, final rallies, last-minute ground game
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
# Each party's strategy reflects their position vectors, ethnic base,
# regional strongholds, and available mechanics. PC flows are tracked
# carefully to ensure no party overspends.
#
# Key rivalries:
#   NRP vs NDC:  secular meritocracy vs northern Islamic establishment
#   NHA vs SNM:  pro-WAFTA globalists vs anti-WAFTA nationalists
#   UJP vs NSA:  Islamist radicals vs security technocrats (Chad Zone)
#   CDA vs UJP:  Christian identity vs Islamic identity
#   PLF vs NRP:  radical left vs liberal market (resource revenue)
#   NDC vs NNV:  northern establishment vs northern secular nationalists
#   IPA vs NDC:  Igbo autonomists vs northern centralists (ethnic quotas)
#
# AZ reference:
#   1=Lagos  2=Niger(Oyo/Ogun)  3=Confluence(Edo/Ekiti)  4=Littoral(Delta/Rivers)
#   5=Eastern(Igbo/Benue)  6=Central(Kano/FCT)  7=Chad(Borno/Yobe)  8=Savanna(Sokoto/Kaduna)

# ===== TURN 1: Opening Salvo =====
# Major parties: manifesto (3) + fundraising (0) + media/pledge (0-1) = 3-4 PC
# Minor parties: manifesto (3) + fundraising (0) = 3 PC, saving 4 for turn 2
# Some parties delay manifesto to turn 2 to maximize early momentum.
turn1 = [
    # --- NRP: Manifesto launch + media blitz (cosmopolitan modernizers) ---
    # PC: 7 - 3(manifesto) - 1(media) = 3 remaining
    ActionSpec(party="NRP", action_type="manifesto", params={}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NRP", action_type="pledge", params={
        "pledge": {"topic": "meritocratic civil service reform"},
        "dimensions": [4, 9], "popularity": 0.7}),

    # --- CND: Manifesto + fundraising from loyal membership ---
    # PC: 7 - 3(manifesto) = 4 remaining
    ActionSpec(party="CND", action_type="manifesto", params={}),
    ActionSpec(party="CND", action_type="fundraising",
              params={"source": "membership"}),
    ActionSpec(party="CND", action_type="pledge", params={
        "pledge": {"topic": "press freedom guarantee"},
        "dimensions": [23, 14], "popularity": 0.6}),

    # --- ANPC: Fundraise first, manifesto turn 2 (centrist catch-all) ---
    # PC: 7 - 1(media) = 6 remaining
    ActionSpec(party="ANPC", action_type="fundraising",
              params={"source": "diaspora"}),
    ActionSpec(party="ANPC", action_type="media", language="english",
              params={"success": 0.5}),
    ActionSpec(party="ANPC", action_type="pledge", params={
        "pledge": {"topic": "fiscal devolution to AZs"},
        "dimensions": [1, 27], "popularity": 0.5}),

    # --- IPA: Manifesto + business_elite fundraising (Igbo commercial networks) ---
    # PC: 7 - 3(manifesto) = 4 remaining
    ActionSpec(party="IPA", action_type="manifesto", params={}),
    ActionSpec(party="IPA", action_type="fundraising",
              params={"source": "business_elite"}),
    ActionSpec(party="IPA", action_type="pledge", params={
        "pledge": {"topic": "fiscal autonomy for eastern zone"},
        "dimensions": [1, 7], "popularity": 0.8}),

    # --- NDC: Manifesto + rally in northern heartland ---
    # PC: 7 - 3(manifesto) - 2(rally) = 2 remaining
    ActionSpec(party="NDC", action_type="manifesto", params={}),
    ActionSpec(party="NDC", action_type="rally", language="hausa",
              params={"gm_score": 7.0}),
    ActionSpec(party="NDC", action_type="pledge", params={
        "pledge": {"topic": "universal infrastructure program"},
        "dimensions": [16, 24], "popularity": 0.7}),

    # --- UJP: Rally in Kanuri heartland, delay manifesto ---
    # PC: 7 - 2(rally) = 5 remaining
    ActionSpec(party="UJP", action_type="rally", language="arabic",
              params={"gm_score": 7.0}),
    ActionSpec(party="UJP", action_type="fundraising",
              params={"source": "grassroots"}),
    ActionSpec(party="UJP", action_type="pledge", params={
        "pledge": {"topic": "Islamic welfare expansion"},
        "dimensions": [0, 24, 16], "popularity": 0.6}),

    # --- NWF: Manifesto + grassroots fundraising (labor base) ---
    # PC: 7 - 3(manifesto) = 4 remaining
    ActionSpec(party="NWF", action_type="manifesto", params={}),
    ActionSpec(party="NWF", action_type="fundraising",
              params={"source": "grassroots"}),
    ActionSpec(party="NWF", action_type="pledge", params={
        "pledge": {"topic": "minimum wage tripling"},
        "dimensions": [10, 8, 18], "popularity": 0.7}),

    # --- NHA: Social media advertising (tech-savvy base) ---
    # PC: 7 - 2(advertising) - 1(media) = 4 remaining
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="NHA", action_type="media", language="english",
              params={"success": 0.7}),
    ActionSpec(party="NHA", action_type="pledge", params={
        "pledge": {"topic": "universal bio-enhancement access"},
        "dimensions": [20, 9], "popularity": 0.5}),

    # --- SNM: Manifesto + rally (economic nationalist base) ---
    # PC: 7 - 3(manifesto) - 2(rally) = 2 remaining
    ActionSpec(party="SNM", action_type="manifesto", params={}),
    ActionSpec(party="SNM", action_type="rally", language="hausa",
              params={"gm_score": 6.0}),
    ActionSpec(party="SNM", action_type="pledge", params={
        "pledge": {"topic": "WAFTA renegotiation and import controls"},
        "dimensions": [2, 21, 12], "popularity": 0.6}),

    # --- NSA: Manifesto + fundraising ---
    # PC: 7 - 3(manifesto) = 4 remaining
    ActionSpec(party="NSA", action_type="manifesto", params={}),
    ActionSpec(party="NSA", action_type="fundraising",
              params={"source": "diaspora"}),
    ActionSpec(party="NSA", action_type="pledge", params={
        "pledge": {"topic": "professional border security force"},
        "dimensions": [12, 11], "popularity": 0.6}),

    # --- CDA: Manifesto + religious leader endorsement ---
    # PC: 7 - 3(manifesto) - 2(endorsement) = 2 remaining
    ActionSpec(party="CDA", action_type="manifesto", params={}),
    ActionSpec(party="CDA", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),
    ActionSpec(party="CDA", action_type="pledge", params={
        "pledge": {"topic": "secular constitution defense"},
        "dimensions": [0, 14], "popularity": 0.5}),

    # --- MBPP: Manifesto + fundraising ---
    # PC: 7 - 3(manifesto) = 4 remaining
    ActionSpec(party="MBPP", action_type="manifesto", params={}),
    ActionSpec(party="MBPP", action_type="fundraising",
              params={"source": "grassroots"}),
    ActionSpec(party="MBPP", action_type="pledge", params={
        "pledge": {"topic": "Middle Belt infrastructure fund"},
        "dimensions": [16, 24, 15], "popularity": 0.7}),

    # --- PLF: Rally in Niger Delta + grassroots fundraising ---
    # PC: 7 - 2(rally) = 5 remaining
    ActionSpec(party="PLF", action_type="rally", language="pidgin",
              params={"gm_score": 8.0}),
    ActionSpec(party="PLF", action_type="fundraising",
              params={"source": "grassroots"}),
    ActionSpec(party="PLF", action_type="pledge", params={
        "pledge": {"topic": "resource revenue for local communities"},
        "dimensions": [7, 24, 8], "popularity": 0.8}),

    # --- NNV: Manifesto + media (nationalist messaging) ---
    # PC: 7 - 3(manifesto) - 1(media) = 3 remaining
    ActionSpec(party="NNV", action_type="manifesto", params={}),
    ActionSpec(party="NNV", action_type="media", language="english",
              params={"success": 0.6}),
    ActionSpec(party="NNV", action_type="pledge", params={
        "pledge": {"topic": "one Nigeria unity program"},
        "dimensions": [6, 11, 27], "popularity": 0.5}),
]

# ===== TURN 2: Base Building =====
# Endorsements, initial advertising, ground game in strongholds.
# Parties that delayed manifesto (ANPC, UJP, NHA, PLF) publish now.
turn2 = [
    # --- NRP: Celebrity endorsement + social media ads (3+7=10 PC, spend 5) ---
    ActionSpec(party="NRP", action_type="endorsement",
              params={"endorser_type": "celebrity"}),
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.5}),

    # --- CND: Yoruba radio advertising + endorsement (4+3+7=14, spend 5) ---
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="CND", action_type="endorsement",
              params={"endorser_type": "notable"}),

    # --- ANPC: Manifesto + traditional ruler endorsement (6+3+7=16→capped 18, spend 5) ---
    ActionSpec(party="ANPC", action_type="manifesto", params={}),
    ActionSpec(party="ANPC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    # --- IPA: ETO economic AZ5 (Igbo commercial heartland) + advertising ---
    ActionSpec(party="IPA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 5, "score_change": 3.0}),
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "radio", "budget": 1.0}),

    # --- NDC: Traditional ruler endorsement + fundraising ---
    ActionSpec(party="NDC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="NDC", action_type="fundraising",
              params={"source": "diaspora"}),

    # --- UJP: Manifesto + religious leader endorsement (5+2+7=14, spend 5) ---
    ActionSpec(party="UJP", action_type="manifesto", params={}),
    ActionSpec(party="UJP", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    # --- NWF: Ground game in Lagos industrial zones + rally (SYNERGY) ---
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin",
              params={"gm_score": 7.0}),

    # --- NHA: Manifesto + ETO economic AZ1 (Lagos tech) ---
    ActionSpec(party="NHA", action_type="manifesto", params={}),
    ActionSpec(party="NHA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),

    # --- SNM: Radio advertising in northern markets + endorsement ---
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="SNM", action_type="endorsement",
              params={"endorser_type": "notable"}),

    # --- NSA: Rally in conflict zones + ETO elite AZ7 (Chad security) ---
    ActionSpec(party="NSA", action_type="rally", language="hausa",
              params={"gm_score": 7.0}),
    ActionSpec(party="NSA", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 7, "score_change": 2.0}),

    # --- CDA: Ground game in Middle Belt + rally (SYNERGY) ---
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CDA", action_type="rally", language="english",
              params={"gm_score": 7.0}),

    # --- MBPP: ETO economic AZ6 (Central heartland) + endorsement ---
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    # --- PLF: Manifesto + ground game in Niger Delta ---
    ActionSpec(party="PLF", action_type="manifesto", params={}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),

    # --- NNV: TV advertising + endorsement ---
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NNV", action_type="endorsement",
              params={"endorser_type": "notable"}),
]

# ===== TURN 3: Ethnic Outreach & Consolidation =====
# Ethnic mobilization where appropriate, ETO building, polls for intelligence.
turn3 = [
    # --- NRP: Poll for intelligence + advertising (English TV) ---
    ActionSpec(party="NRP", action_type="poll", params={"sample_size": 2000}),
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NRP", action_type="fundraising",
              params={"source": "business_elite"}),

    # --- CND: Ethnic mobilization Yoruba + media (press freedom champion) ---
    ActionSpec(party="CND", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Yoruba"}),
    ActionSpec(party="CND", action_type="media", language="yoruba",
              params={"success": 0.7}),

    # --- ANPC: Ground game broadly + advertising (catch-all) ---
    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),

    # --- IPA: Ethnic mobilization Igbo + rally in Eastern Zone ---
    ActionSpec(party="IPA", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Igbo"}),
    ActionSpec(party="IPA", action_type="rally", language="igbo",
              params={"gm_score": 7.0}),

    # --- NDC: Ethnic mobilization Hausa-Fulani + ground game (SYNERGY next turn) ---
    ActionSpec(party="NDC", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Hausa-Fulani Undiff"}),
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),

    # --- UJP: Ethnic mobilization Kanuri + ETO mobilization AZ7 ---
    ActionSpec(party="UJP", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Kanuri"}),
    ActionSpec(party="UJP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 7, "score_change": 3.0}),

    # --- NWF: Advertising pidgin (cross-ethnic) + endorsement ---
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="endorsement",
              params={"endorser_type": "notable"}),

    # --- NHA: Social media advertising + fundraising ---
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.5}),
    ActionSpec(party="NHA", action_type="fundraising",
              params={"source": "business_elite"}),

    # --- SNM: Rally in Kano markets + fundraising ---
    ActionSpec(party="SNM", action_type="rally", language="hausa",
              params={"gm_score": 7.0}),
    ActionSpec(party="SNM", action_type="fundraising",
              params={"source": "membership"}),

    # --- NSA: Advertising + ground game in conflict zones ---
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NSA", action_type="ground_game", params={"intensity": 1.0}),

    # --- CDA: Ethnic mobilization Tiv + advertising ---
    ActionSpec(party="CDA", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Tiv"}),
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),

    # --- MBPP: Ethnic mobilization Middle Belt + rally ---
    ActionSpec(party="MBPP", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Middle Belt Minorities"}),
    ActionSpec(party="MBPP", action_type="rally", language="english",
              params={"gm_score": 6.0}),

    # --- PLF: Ethnic mobilization Ijaw + rally in Niger Delta (SYNERGY setup) ---
    ActionSpec(party="PLF", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Ijaw"}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin",
              params={"gm_score": 8.0}),

    # --- NNV: Rally + ground game (SYNERGY) ---
    ActionSpec(party="NNV", action_type="rally", language="english",
              params={"gm_score": 7.0}),
    ActionSpec(party="NNV", action_type="ground_game", params={"intensity": 1.0}),
]

# ===== TURN 4: First Crisis (Security incident in Northeast) =====
# NSA benefits (+valence). UJP/NDC penalized. Parties that can respond, do.
# Others continue building. Opposition research opens up.
turn4 = [
    # --- NRP: Oppo research NDC on sharia/quotas + fundraising ---
    ActionSpec(party="NRP", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 4]}),
    ActionSpec(party="NRP", action_type="fundraising",
              params={"source": "business_elite"}),

    # --- CND: Oppo research NDC on women's rights + advertising ---
    ActionSpec(party="CND", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [14, 0]}),
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 1.5}),

    # --- ANPC: Patronage (catch-all, moderate exposure risk) + media ---
    ActionSpec(party="ANPC", action_type="patronage", params={"scale": 1.0}),
    ActionSpec(party="ANPC", action_type="media", language="english",
              params={"success": 0.6}),

    # --- IPA: Oppo research NDC on ethnic quotas + advertising ---
    ActionSpec(party="IPA", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [4, 7]}),
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 1.5}),

    # --- NDC: Crisis hurts them — rally to shore up base + patronage (risky!) ---
    ActionSpec(party="NDC", action_type="rally", language="hausa",
              params={"gm_score": 8.0}),
    ActionSpec(party="NDC", action_type="patronage", params={"scale": 1.0}),

    # --- UJP: Crisis hurts them — crisis response + rally ---
    ActionSpec(party="UJP", action_type="crisis_response",
              params={"effectiveness": 0.6}),
    ActionSpec(party="UJP", action_type="rally", language="arabic",
              params={"gm_score": 8.0}),

    # --- NWF: Advertising (varies from ground_game to avoid fatigue) + fundraising ---
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="fundraising",
              params={"source": "grassroots"}),

    # --- NHA: Oppo research SNM (WAFTA rivalry) + media (SYNERGY) ---
    ActionSpec(party="NHA", action_type="opposition_research",
              params={"target_party": "SNM", "target_dimensions": [2, 21]}),
    ActionSpec(party="NHA", action_type="media", language="english",
              params={"success": 0.7}),

    # --- SNM: Oppo research NHA (WAFTA rivalry) + media (SYNERGY) ---
    ActionSpec(party="SNM", action_type="opposition_research",
              params={"target_party": "NHA", "target_dimensions": [2, 21]}),
    ActionSpec(party="SNM", action_type="media", language="hausa",
              params={"success": 0.5}),

    # --- NSA: Crisis benefits them — rally + advertising (capitalize) ---
    ActionSpec(party="NSA", action_type="rally", language="hausa",
              params={"gm_score": 8.0}),
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.5}),

    # --- CDA: Rally + endorsement (religious leader, more impactful) ---
    ActionSpec(party="CDA", action_type="rally", language="english",
              params={"gm_score": 7.0}),
    ActionSpec(party="CDA", action_type="fundraising",
              params={"source": "membership"}),

    # --- MBPP: Ground game + ETO building (Central Zone) ---
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),

    # --- PLF: Oppo research NRP on resource revenue + media ---
    ActionSpec(party="PLF", action_type="opposition_research",
              params={"target_party": "NRP", "target_dimensions": [7, 18]}),
    ActionSpec(party="PLF", action_type="media", language="pidgin",
              params={"success": 0.6}),

    # --- NNV: Crisis response + oppo research NDC ---
    ActionSpec(party="NNV", action_type="crisis_response",
              params={"effectiveness": 0.7}),
    ActionSpec(party="NNV", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 11]}),
]

# ===== TURN 5: Mid-Campaign Expansion =====
# ETO building, polls, diversify action types to avoid fatigue.
turn5 = [
    # --- NRP: ETO elite AZ1 (Lagos establishment) + endorsement ---
    ActionSpec(party="NRP", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NRP", action_type="endorsement",
              params={"endorser_type": "notable"}),

    # --- CND: ETO economic AZ2 (Yoruba heartland) + ground game ---
    ActionSpec(party="CND", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 2, "score_change": 3.0}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),

    # --- ANPC: Endorsement (traditional ruler) + advertising ---
    ActionSpec(party="ANPC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.5}),

    # --- IPA: Rally + ground game in Eastern Zone (SYNERGY) ---
    ActionSpec(party="IPA", action_type="rally", language="igbo",
              params={"gm_score": 8.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),

    # --- NDC: Rally + ground game in northern strongholds (SYNERGY) ---
    ActionSpec(party="NDC", action_type="rally", language="hausa",
              params={"gm_score": 8.0}),
    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),

    # --- UJP: ETO mobilization AZ7 (deepen) + advertising ---
    ActionSpec(party="UJP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 7, "score_change": 3.0}),
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.0}),

    # --- NWF: Rally + ground game (SYNERGY, different from T4 to avoid fatigue) ---
    ActionSpec(party="NWF", action_type="rally", language="pidgin",
              params={"gm_score": 7.0}),
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),

    # --- NHA: ETO economic AZ6 (FCT tech hub) + poll ---
    ActionSpec(party="NHA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),
    ActionSpec(party="NHA", action_type="poll", params={"sample_size": 2000}),

    # --- SNM: Ground game in market towns + media ---
    ActionSpec(party="SNM", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="SNM", action_type="media", language="hausa",
              params={"success": 0.5}),

    # --- NSA: ETO elite AZ7 (deepen security establishment) + fundraising ---
    ActionSpec(party="NSA", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 7, "score_change": 3.0}),
    ActionSpec(party="NSA", action_type="fundraising",
              params={"source": "diaspora"}),

    # --- CDA: ETO legitimacy AZ5 (Eastern/Benue Christian communities) + endorsement ---
    ActionSpec(party="CDA", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 5, "score_change": 3.0}),
    ActionSpec(party="CDA", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    # --- MBPP: Advertising + endorsement (traditional ruler, second endorsement) ---
    ActionSpec(party="MBPP", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="MBPP", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    # --- PLF: Rally + ground game in Niger Delta (SYNERGY) ---
    ActionSpec(party="PLF", action_type="rally", language="pidgin",
              params={"gm_score": 9.0}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),

    # --- NNV: ETO elite AZ6 (Kano/Kaduna nationalists) + rally ---
    ActionSpec(party="NNV", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 6, "score_change": 3.0}),
    ActionSpec(party="NNV", action_type="rally", language="hausa",
              params={"gm_score": 7.0}),
]

# ===== TURN 6: Opposition Research Blitz =====
# Major parties target their key rivals. Use media+oppo synergy where possible.
turn6 = [
    # --- NRP: Media + oppo research NDC (SYNERGY) + poll ---
    ActionSpec(party="NRP", action_type="media", language="english",
              params={"success": 0.8}),
    ActionSpec(party="NRP", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [4, 14, 0]}),
    ActionSpec(party="NRP", action_type="poll", params={"sample_size": 3000}),

    # --- CND: Oppo research NDC + rally ---
    ActionSpec(party="CND", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 5, 14]}),
    ActionSpec(party="CND", action_type="rally", language="yoruba",
              params={"gm_score": 8.0}),

    # --- ANPC: Advertising + ground game (avoid oppo — centrist has no natural target) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.5}),
    ActionSpec(party="ANPC", action_type="fundraising",
              params={"source": "diaspora"}),

    # --- IPA: Media + oppo research NDC (SYNERGY) ---
    ActionSpec(party="IPA", action_type="media", language="igbo",
              params={"success": 0.6}),
    ActionSpec(party="IPA", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [4, 1]}),
    ActionSpec(party="IPA", action_type="fundraising",
              params={"source": "business_elite"}),

    # --- NDC: Oppo research CND + endorsement (religious leader) ---
    ActionSpec(party="NDC", action_type="opposition_research",
              params={"target_party": "CND", "target_dimensions": [23, 11]}),
    ActionSpec(party="NDC", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),
    ActionSpec(party="NDC", action_type="fundraising",
              params={"source": "diaspora"}),

    # --- UJP: Rally + ground game (SYNERGY, building Chad Zone dominance) ---
    ActionSpec(party="UJP", action_type="rally", language="arabic",
              params={"gm_score": 8.0}),
    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),

    # --- NWF: Oppo research NRP on labor/housing + media ---
    ActionSpec(party="NWF", action_type="opposition_research",
              params={"target_party": "NRP", "target_dimensions": [10, 8]}),
    ActionSpec(party="NWF", action_type="media", language="pidgin",
              params={"success": 0.6}),

    # --- NHA: Media + oppo research SNM (SYNERGY) ---
    ActionSpec(party="NHA", action_type="media", language="english",
              params={"success": 0.8}),
    ActionSpec(party="NHA", action_type="opposition_research",
              params={"target_party": "SNM", "target_dimensions": [2, 21]}),

    # --- SNM: Media + oppo research NHA (SYNERGY, mirror rivalry) ---
    ActionSpec(party="SNM", action_type="media", language="hausa",
              params={"success": 0.6}),
    ActionSpec(party="SNM", action_type="opposition_research",
              params={"target_party": "NHA", "target_dimensions": [2, 21]}),

    # --- NSA: Oppo research UJP (security vs Islamism) + rally ---
    ActionSpec(party="NSA", action_type="opposition_research",
              params={"target_party": "UJP", "target_dimensions": [0, 11]}),
    ActionSpec(party="NSA", action_type="rally", language="hausa",
              params={"gm_score": 7.0}),

    # --- CDA: Oppo research UJP (Christian vs Islamist) + rally ---
    ActionSpec(party="CDA", action_type="opposition_research",
              params={"target_party": "UJP", "target_dimensions": [0, 14]}),
    ActionSpec(party="CDA", action_type="rally", language="english",
              params={"gm_score": 7.0}),

    # --- MBPP: Rally + fundraising (building war chest for final push) ---
    ActionSpec(party="MBPP", action_type="rally", language="english",
              params={"gm_score": 7.0}),
    ActionSpec(party="MBPP", action_type="fundraising",
              params={"source": "grassroots"}),

    # --- PLF: Media + oppo research NRP (SYNERGY, resource revenue attack) ---
    ActionSpec(party="PLF", action_type="media", language="pidgin",
              params={"success": 0.7}),
    ActionSpec(party="PLF", action_type="opposition_research",
              params={"target_party": "NRP", "target_dimensions": [7, 18, 8]}),

    # --- NNV: Oppo research NDC (competing for northern voters) + advertising ---
    ActionSpec(party="NNV", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 6, 11]}),
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.5}),
]

# ===== TURN 7: Rally+Ground Game Synergy Phase =====
# Maximum synergy exploitation. Pair rally+ground_game for every party.
turn7 = [
    # --- NRP: Rally + ground game (SYNERGY) + endorsement ---
    ActionSpec(party="NRP", action_type="rally", language="english",
              params={"gm_score": 8.0}),
    ActionSpec(party="NRP", action_type="ground_game", params={"intensity": 1.0}),

    # --- CND: Rally + ground game (SYNERGY, Yoruba heartland GOTV) ---
    ActionSpec(party="CND", action_type="rally", language="yoruba",
              params={"gm_score": 8.0}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),

    # --- ANPC: Rally + ground game (SYNERGY, broad appeal) ---
    ActionSpec(party="ANPC", action_type="rally", language="english",
              params={"gm_score": 7.0}),
    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),

    # --- IPA: Advertising + rally (SYNERGY, Eastern Zone blitz) ---
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 1.5}),
    ActionSpec(party="IPA", action_type="rally", language="igbo",
              params={"gm_score": 8.0}),

    # --- NDC: Rally + ground game (SYNERGY, northern GOTV machine) ---
    ActionSpec(party="NDC", action_type="rally", language="hausa",
              params={"gm_score": 9.0}),
    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),

    # --- UJP: Rally + ground game (SYNERGY, northeast consolidation) ---
    ActionSpec(party="UJP", action_type="rally", language="arabic",
              params={"gm_score": 8.0}),
    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),

    # --- NWF: Advertising + rally (SYNERGY, varies to avoid fatigue) ---
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin",
              params={"gm_score": 8.0}),

    # --- NHA: Rally + ground game (SYNERGY, Lagos/FCT) ---
    ActionSpec(party="NHA", action_type="rally", language="english",
              params={"gm_score": 7.0}),
    ActionSpec(party="NHA", action_type="ground_game", params={"intensity": 1.0}),

    # --- SNM: Rally + ground game (SYNERGY, northern market towns) ---
    ActionSpec(party="SNM", action_type="rally", language="hausa",
              params={"gm_score": 8.0}),
    ActionSpec(party="SNM", action_type="ground_game", params={"intensity": 1.0}),

    # --- NSA: Rally + ground game (SYNERGY, conflict zones) ---
    ActionSpec(party="NSA", action_type="rally", language="hausa",
              params={"gm_score": 8.0}),
    ActionSpec(party="NSA", action_type="ground_game", params={"intensity": 1.0}),

    # --- CDA: Rally + ground game (SYNERGY, Middle Belt GOTV) ---
    ActionSpec(party="CDA", action_type="rally", language="english",
              params={"gm_score": 8.0}),
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),

    # --- MBPP: Rally + ground game (SYNERGY, Central Zone) ---
    ActionSpec(party="MBPP", action_type="rally", language="english",
              params={"gm_score": 7.0}),
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),

    # --- PLF: Advertising + rally (SYNERGY, Niger Delta mobilization) ---
    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin",
              params={"gm_score": 9.0}),

    # --- NNV: Rally + ground game (SYNERGY, northern nationalist base) ---
    ActionSpec(party="NNV", action_type="rally", language="english",
              params={"gm_score": 7.0}),
    ActionSpec(party="NNV", action_type="ground_game", params={"intensity": 1.0}),
]

# ===== TURN 8: Second Crisis (WAFTA Trade Dispute) =====
# NHA penalized, SNM boosted. Parties diversify to avoid T7 fatigue.
turn8 = [
    # --- NRP: Endorsement (new) + advertising (shift from T7 rally) ---
    ActionSpec(party="NRP", action_type="endorsement",
              params={"endorser_type": "notable"}),
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),

    # --- CND: Crisis response (trade-affected Yoruba) + fundraising ---
    ActionSpec(party="CND", action_type="crisis_response",
              params={"effectiveness": 0.6}),
    ActionSpec(party="CND", action_type="fundraising",
              params={"source": "membership"}),

    # --- ANPC: Advertising + endorsement (maintain broad appeal) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.5}),
    ActionSpec(party="ANPC", action_type="fundraising",
              params={"source": "diaspora"}),

    # --- IPA: ETO economic AZ5 (deepen) + advertising ---
    ActionSpec(party="IPA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 5, "score_change": 3.0}),
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "radio", "budget": 1.0}),

    # --- NDC: Advertising + endorsement (avoid T7 rally fatigue) ---
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="NDC", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    # --- UJP: Advertising + fundraising (diversify from T7) ---
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="UJP", action_type="fundraising",
              params={"source": "grassroots"}),

    # --- NWF: Ground game + endorsement (avoid ad fatigue from T7) ---
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NWF", action_type="endorsement",
              params={"endorser_type": "notable"}),

    # --- NHA: Crisis hurts them — crisis response + media damage control ---
    ActionSpec(party="NHA", action_type="crisis_response",
              params={"effectiveness": 0.8}),
    ActionSpec(party="NHA", action_type="media", language="english",
              params={"success": 0.5}),

    # --- SNM: Crisis benefits them — rally + advertising (capitalize!) ---
    ActionSpec(party="SNM", action_type="rally", language="hausa",
              params={"gm_score": 9.0}),
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.5}),

    # --- NSA: Advertising + endorsement (diversify) ---
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.5}),
    ActionSpec(party="NSA", action_type="endorsement",
              params={"endorser_type": "notable"}),

    # --- CDA: Advertising + fundraising ---
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="CDA", action_type="fundraising",
              params={"source": "membership"}),

    # --- MBPP: ETO building + endorsement ---
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 6, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    # --- PLF: Ground game + fundraising (save for final push) ---
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="fundraising",
              params={"source": "grassroots"}),

    # --- NNV: Advertising + ETO (diversify from T7) ---
    ActionSpec(party="NNV", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="NNV", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 6, "score_change": 3.0}),
]

# ===== TURN 9: Late ETO Building & Strategic Endorsements =====
# Final round of institutional building before the advertising blitz.
turn9 = [
    # --- NRP: ETO economic AZ1 (build toward dividend) + media ---
    ActionSpec(party="NRP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NRP", action_type="media", language="english",
              params={"success": 0.7}),

    # --- CND: ETO legitimacy AZ2 + rally (Yoruba final consolidation) ---
    ActionSpec(party="CND", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 2, "score_change": 3.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba",
              params={"gm_score": 8.0}),

    # --- ANPC: ETO elite AZ3 (Confluence) + rally ---
    ActionSpec(party="ANPC", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 3, "score_change": 3.0}),
    ActionSpec(party="ANPC", action_type="rally", language="english",
              params={"gm_score": 7.0}),

    # --- IPA: Endorsement (eto_leader) + poll (intelligence for final push) ---
    ActionSpec(party="IPA", action_type="endorsement",
              params={"endorser_type": "eto_leader"}),
    ActionSpec(party="IPA", action_type="poll", params={"sample_size": 3000}),
    ActionSpec(party="IPA", action_type="fundraising",
              params={"source": "business_elite"}),

    # --- NDC: ETO legitimacy AZ8 (Savanna stronghold) + patronage ---
    ActionSpec(party="NDC", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 8, "score_change": 3.0}),
    ActionSpec(party="NDC", action_type="patronage", params={"scale": 1.0}),

    # --- UJP: ETO mobilization AZ7 (third round — dominance) + endorsement ---
    ActionSpec(party="UJP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 7, "score_change": 3.0}),
    ActionSpec(party="UJP", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    # --- NWF: ETO mobilization AZ1 (Lagos labor) + media ---
    ActionSpec(party="NWF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin",
              params={"success": 0.6}),

    # --- NHA: ETO economic AZ1 (deepen — aim for dividend) + endorsement ---
    ActionSpec(party="NHA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NHA", action_type="endorsement",
              params={"endorser_type": "celebrity"}),

    # --- SNM: ETO mobilization AZ8 + endorsement ---
    ActionSpec(party="SNM", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 8, "score_change": 3.0}),
    ActionSpec(party="SNM", action_type="endorsement",
              params={"endorser_type": "traditional_ruler"}),

    # --- NSA: ETO elite AZ7 (third round) + endorsement ---
    ActionSpec(party="NSA", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 7, "score_change": 3.0}),
    ActionSpec(party="NSA", action_type="endorsement",
              params={"endorser_type": "notable"}),

    # --- CDA: ETO legitimacy AZ6 (Central Christian communities) + endorsement ---
    ActionSpec(party="CDA", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 6, "score_change": 3.0}),
    ActionSpec(party="CDA", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    # --- MBPP: ETO economic AZ6 (aim for dividend) + media ---
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="media", language="english",
              params={"success": 0.5}),

    # --- PLF: ETO mobilization AZ4 (Niger Delta GOTV) + endorsement ---
    ActionSpec(party="PLF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 4, "score_change": 3.0}),
    ActionSpec(party="PLF", action_type="endorsement",
              params={"endorser_type": "notable"}),

    # --- NNV: ETO elite AZ2 (Nupe/military areas) + endorsement ---
    ActionSpec(party="NNV", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 2, "score_change": 3.0}),
    ActionSpec(party="NNV", action_type="endorsement",
              params={"endorser_type": "notable"}),
]

# ===== TURN 10: Heavy Advertising Blitz =====
# Spend hoarded PC on advertising. Parties with business_elite fundraising
# have the most to spend. Advertising+rally synergy where possible.
turn10 = [
    # --- NRP: Heavy social media ads + rally (SYNERGY) ---
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NRP", action_type="rally", language="english",
              params={"gm_score": 9.0}),

    # --- CND: TV advertising + rally (SYNERGY) ---
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba",
              params={"gm_score": 9.0}),

    # --- ANPC: TV advertising + rally (SYNERGY) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="ANPC", action_type="rally", language="english",
              params={"gm_score": 8.0}),

    # --- IPA: Social media ads + rally (SYNERGY, Eastern Zone climax) ---
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="IPA", action_type="rally", language="igbo",
              params={"gm_score": 9.0}),

    # --- NDC: Radio ads + rally (SYNERGY, northern GOTV blitz) ---
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="NDC", action_type="rally", language="hausa",
              params={"gm_score": 9.0}),

    # --- UJP: Radio ads + rally (SYNERGY, northeast mobilization) ---
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="UJP", action_type="rally", language="arabic",
              params={"gm_score": 9.0}),

    # --- NWF: Radio ads + rally (SYNERGY, industrial belt) ---
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin",
              params={"gm_score": 9.0}),

    # --- NHA: Social media ads + rally (SYNERGY, Lagos tech) ---
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NHA", action_type="rally", language="english",
              params={"gm_score": 8.0}),

    # --- SNM: Radio ads + rally (SYNERGY, economic nationalist base) ---
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="SNM", action_type="rally", language="hausa",
              params={"gm_score": 9.0}),

    # --- NSA: TV ads + rally (SYNERGY, national security message) ---
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa",
              params={"gm_score": 8.0}),

    # --- CDA: Radio ads + rally (SYNERGY, Middle Belt) ---
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="CDA", action_type="rally", language="english",
              params={"gm_score": 8.0}),

    # --- MBPP: Radio ads + rally (SYNERGY, Central Zone push) ---
    ActionSpec(party="MBPP", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="MBPP", action_type="rally", language="english",
              params={"gm_score": 8.0}),

    # --- PLF: Radio ads + rally (SYNERGY, Delta mobilization) ---
    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin",
              params={"gm_score": 10.0}),

    # --- NNV: TV ads + rally (SYNERGY, nationalist push) ---
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NNV", action_type="rally", language="hausa",
              params={"gm_score": 8.0}),
]

# ===== TURN 11: Third Crisis (Religious Tensions in Middle Belt) =====
# CDA benefits (+valence). UJP/NDC penalized. Diversify from T10 ads.
turn11 = [
    # --- NRP: Rally + ground game (SYNERGY, diversify from T10 ads) ---
    ActionSpec(party="NRP", action_type="rally", language="english",
              params={"gm_score": 9.0}),
    ActionSpec(party="NRP", action_type="ground_game", params={"intensity": 1.0}),

    # --- CND: Rally + ground game (SYNERGY, Yoruba GOTV sprint) ---
    ActionSpec(party="CND", action_type="rally", language="yoruba",
              params={"gm_score": 9.0}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),

    # --- ANPC: Rally + endorsement (final push) ---
    ActionSpec(party="ANPC", action_type="rally", language="english",
              params={"gm_score": 8.0}),
    ActionSpec(party="ANPC", action_type="endorsement",
              params={"endorser_type": "religious_leader"}),

    # --- IPA: Rally + ground game (SYNERGY, Eastern Zone final) ---
    ActionSpec(party="IPA", action_type="rally", language="igbo",
              params={"gm_score": 9.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),

    # --- NDC: Crisis hurts — crisis response + rally (stabilize) ---
    ActionSpec(party="NDC", action_type="crisis_response",
              params={"effectiveness": 0.6}),
    ActionSpec(party="NDC", action_type="rally", language="hausa",
              params={"gm_score": 10.0}),

    # --- UJP: Crisis hurts — crisis response + rally ---
    ActionSpec(party="UJP", action_type="crisis_response",
              params={"effectiveness": 0.7}),
    ActionSpec(party="UJP", action_type="rally", language="arabic",
              params={"gm_score": 10.0}),

    # --- NWF: Rally + ground game (SYNERGY, final industrial belt push) ---
    ActionSpec(party="NWF", action_type="rally", language="pidgin",
              params={"gm_score": 9.0}),
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),

    # --- NHA: Rally + media (recover from T8 crisis damage) ---
    ActionSpec(party="NHA", action_type="rally", language="english",
              params={"gm_score": 8.0}),
    ActionSpec(party="NHA", action_type="media", language="english",
              params={"success": 0.7}),

    # --- SNM: Rally + ground game (SYNERGY, diversify from T10 ads) ---
    ActionSpec(party="SNM", action_type="rally", language="hausa",
              params={"gm_score": 9.0}),
    ActionSpec(party="SNM", action_type="ground_game", params={"intensity": 1.0}),

    # --- NSA: Crisis response (security crisis = their domain) + rally ---
    ActionSpec(party="NSA", action_type="crisis_response",
              params={"effectiveness": 0.9}),
    ActionSpec(party="NSA", action_type="rally", language="hausa",
              params={"gm_score": 9.0}),

    # --- CDA: Crisis benefits them — rally + ground game (SYNERGY, capitalize!) ---
    ActionSpec(party="CDA", action_type="rally", language="english",
              params={"gm_score": 9.0}),
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CDA", action_type="crisis_response",
              params={"effectiveness": 0.8}),

    # --- MBPP: Rally + ground game (SYNERGY, Central Zone defensive) ---
    ActionSpec(party="MBPP", action_type="rally", language="english",
              params={"gm_score": 8.0}),
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),

    # --- PLF: Rally + ground game (SYNERGY, Niger Delta final push) ---
    ActionSpec(party="PLF", action_type="rally", language="pidgin",
              params={"gm_score": 10.0}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),

    # --- NNV: Crisis response + rally (security nationalist response) ---
    ActionSpec(party="NNV", action_type="crisis_response",
              params={"effectiveness": 0.7}),
    ActionSpec(party="NNV", action_type="rally", language="english",
              params={"gm_score": 9.0}),
]

# ===== TURN 12: Final Push =====
# Maximum effort. Advertising + rally (SYNERGY) for everyone.
# Spend remaining PC — no point hoarding past election day.
turn12 = [
    # --- NRP: Advertising + rally (SYNERGY) + ground_game ---
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NRP", action_type="rally", language="english",
              params={"gm_score": 10.0}),
    ActionSpec(party="NRP", action_type="ground_game", params={"intensity": 1.0}),

    # --- CND: Advertising + rally (SYNERGY) + ground_game ---
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba",
              params={"gm_score": 10.0}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),

    # --- ANPC: Advertising + rally (SYNERGY) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="ANPC", action_type="rally", language="english",
              params={"gm_score": 9.0}),

    # --- IPA: Advertising + rally (SYNERGY) + ground_game ---
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="IPA", action_type="rally", language="igbo",
              params={"gm_score": 10.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),

    # --- NDC: Advertising + rally (SYNERGY) + ground_game ---
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="NDC", action_type="rally", language="hausa",
              params={"gm_score": 10.0}),
    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),

    # --- UJP: Rally + ground game (SYNERGY) + advertising ---
    ActionSpec(party="UJP", action_type="rally", language="arabic",
              params={"gm_score": 10.0}),
    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.0}),

    # --- NWF: Advertising + rally (SYNERGY) ---
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.5}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin",
              params={"gm_score": 10.0}),

    # --- NHA: Advertising + rally (SYNERGY) ---
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NHA", action_type="rally", language="english",
              params={"gm_score": 9.0}),

    # --- SNM: Advertising + rally (SYNERGY) ---
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="SNM", action_type="rally", language="hausa",
              params={"gm_score": 10.0}),

    # --- NSA: Advertising + rally (SYNERGY) ---
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa",
              params={"gm_score": 9.0}),

    # --- CDA: Rally + ground game (SYNERGY) + advertising ---
    ActionSpec(party="CDA", action_type="rally", language="english",
              params={"gm_score": 9.0}),
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.5}),

    # --- MBPP: Rally + ground game (SYNERGY) ---
    ActionSpec(party="MBPP", action_type="rally", language="english",
              params={"gm_score": 9.0}),
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),

    # --- PLF: Rally + ground game (SYNERGY) + advertising ---
    ActionSpec(party="PLF", action_type="rally", language="pidgin",
              params={"gm_score": 10.0}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.5}),

    # --- NNV: Advertising + rally (SYNERGY) ---
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NNV", action_type="rally", language="hausa",
              params={"gm_score": 10.0}),
]

turns = [turn1, turn2, turn3, turn4, turn5, turn6,
         turn7, turn8, turn9, turn10, turn11, turn12]

# ---------------------------------------------------------------------------
# Crisis Events
# ---------------------------------------------------------------------------

crisis_events = [
    # Turn 4: Security incident in the Northeast
    # Benefits NSA (security credibility). Hurts UJP (associated with instability),
    # NDC (establishment blamed for neglect).
    CrisisEvent(
        name="Security incident in Northeast",
        turn=4,
        affected_lgas=None,  # national impact
        salience_shifts={12: 0.08, 11: 0.05},  # military_role + immigration salience
        valence_effects={"NSA": +0.05, "UJP": -0.05, "NDC": -0.03},
        awareness_boost={"NSA": 0.04, "NNV": 0.02},
    ),
    # Turn 8: WAFTA trade dispute — Chinese tariffs hit Nigerian manufacturers
    # Benefits SNM (anti-WAFTA vindication). Hurts NHA (pro-WAFTA party).
    CrisisEvent(
        name="WAFTA trade dispute",
        turn=8,
        affected_lgas=None,
        salience_shifts={2: 0.10, 21: 0.06},  # chinese_relations + trade_policy
        valence_effects={"NHA": -0.05, "SNM": +0.05},
        awareness_boost={"SNM": 0.04, "NHA": 0.03},
    ),
    # Turn 11: Religious tensions in Middle Belt
    # Benefits CDA (Christian identity, Middle Belt party). Hurts UJP (Islamist),
    # NDC (northern establishment blamed).
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

    # Print synergies if any
    synergies = result.get("synergy_log", [])
    for syn in synergies:
        print(f"  SYNERGY: {syn['party']} - {'+'.join(syn['actions'])} -> {syn['channel']}")

    # Print scandals if any
    post_log = result.get("post_turn_log", {})
    for scandal in post_log.get("scandals", []):
        print(f"  SCANDAL: {scandal['party']} (exposure={scandal['exposure_at_trigger']:.1f})")


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
    project_root = Path(data_path).parent.parent
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
    print("LAGOS-2058 Full Campaign Simulation - 14 Parties, 12 Turns")
    print(f"PC Income: {7}/turn | Hoarding Cap: {18} | Max 3 actions/party/turn")
    print(f"tau_0: {params.tau_0} (first election in decades - high turnout)")
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
