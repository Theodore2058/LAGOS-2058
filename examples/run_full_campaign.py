"""
Full 12-turn campaign simulation with all 14 parties and political capital.

Usage:
    python examples/run_full_campaign.py

Each party's campaign is designed to maximize seat share given their position
vectors, regional strongholds, ethnic base, and available resources.

Constraints:
- Political capital: 7 PC/turn income, 18 hoarding cap, no action cap (spend all PC)
- Every party releases a manifesto by turn 3
- Action fatigue penalizes repeating the same action type across turns
- Synergies reward pairing rally+ground_game, advertising+rally, media+oppo_research

Action costs:
  rally=2 (+1 if gm>=9), advertising=2 (+1 if budget>1.5, +2 if >2.0),
  manifesto=3, ground_game=3 (+1 if intensity>1.0), endorsement=2,
  ethnic_mob=2, patronage=3 (+1 if scale>1.5), oppo_research=2,
  media=1, eto=3, crisis_response=2, fundraising=0, poll=1-5 (by tier), pledge=1

Iteration 2 lessons applied:
- Media is the most cost-effective action (1 PC, huge returns) -- use liberally
- ETO was unused in v1 -- now every party builds zone presence
- CND/NDC/IPA were bleeding share despite heavy spend -- fix defensive gaps
- NRP was wasting actions at 2% -- pivot to niche ETO + media
- Late-game PC was hoarded (parties ended at 16-20 PC) -- spend aggressively
- Crisis responses were under-used -- respond to every relevant crisis
- No action cap means parties can take 4-6 actions/turn when flush

Strategic phases:
  Turns 1-3:  Foundation -- manifestos, fundraising, media blitz, early ETO
  Turns 4-6:  Expansion -- ETO deepening, oppo research, synergies begin
  Turns 7-9:  Intensification -- rally+gg synergies, ethnic mobilization, media+oppo
  Turns 10-12: Final push -- max spend, triple synergies, burn all remaining PC
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
    compute_competitiveness,
    compute_coalition_feasibility,
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
# 12-Turn Campaign Design (v2 -- analysis-informed)
# ---------------------------------------------------------------------------
# Key rivalries:
#   NRP vs NDC:  secular meritocracy vs northern Islamic establishment
#   NHA vs SNM:  pro-WAFTA globalists vs anti-WAFTA nationalists
#   UJP vs NSA:  Islamist radicals vs security technocrats (Chad Zone)
#   CDA vs UJP:  Christian identity vs Islamic identity
#   PLF vs NRP:  radical left vs liberal market (resource revenue)
#   NDC vs NNV:  northern establishment vs northern secular nationalists
#   IPA vs NDC:  Igbo autonomists vs northern centralists (ethnic quotas)
#
# v1 results: CND 21.5%, NDC 13.2%, NHA 12.8%, IPA 10.8%, MBPP 10.7%
# v1 biggest gainer: NHA +2.41% (media-heavy), ANPC +1.60%, UJP +0.98%
# v1 biggest losers: CND -1.90%, NDC -1.31%, IPA -1.26%, NRP -0.63%
#
# AZ reference:
#   1=Lagos  2=Niger(Oyo/Ogun)  3=Confluence(Edo/Ekiti)  4=Littoral(Delta/Rivers)
#   5=Eastern(Igbo/Benue)  6=Central(Kano/FCT)  7=Chad(Borno/Yobe)  8=Savanna(Sokoto/Kaduna)

# ===== TURN 1: Opening Salvo =====
# With no action cap, parties can do manifesto + fundraising + media + pledge = 4-5 PC.
# Key: every party starts media early (1 PC, best ROI from v1 analysis).
turn1 = [
    # --- NRP: Manifesto + media + pledge (3+1+0=4 PC, 3 left) ---
    # v1 lesson: NRP wasted actions at 2%. Pivot to media-first, save for ETO.
    ActionSpec(party="NRP", action_type="manifesto", params={}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NRP", action_type="pledge", params={
        "pledge": {"topic": "meritocratic civil service reform"},
        "dimensions": [4, 9], "popularity": 0.7}),

    # --- CND: Manifesto + media + fundraising + pledge (3+1+0+0=4 PC, 3 left) ---
    # v1 lesson: CND had only 1 media action total. Front-runner needs media defense.
    ActionSpec(party="CND", action_type="manifesto", params={}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.8}),
    ActionSpec(party="CND", action_type="fundraising", params={"source": "membership"}),
    ActionSpec(party="CND", action_type="pledge", params={
        "pledge": {"topic": "press freedom guarantee"},
        "dimensions": [23, 14], "popularity": 0.6}),

    # --- ANPC: Media + fundraising + pledge (1+0+0=1 PC, 6 left for T2 manifesto) ---
    # v1 lesson: ANPC was the #2 gainer. Keep the strategy but add more media.
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.5}),
    ActionSpec(party="ANPC", action_type="fundraising", params={"source": "diaspora"}),
    ActionSpec(party="ANPC", action_type="pledge", params={
        "pledge": {"topic": "fiscal devolution to AZs"},
        "dimensions": [1, 27], "popularity": 0.5}),

    # --- IPA: Manifesto + media + fundraising + pledge (3+1+0+0=4 PC, 3 left) ---
    # v1 lesson: IPA was losing to ANPC in Littoral. Add media, counter later.
    ActionSpec(party="IPA", action_type="manifesto", params={}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),
    ActionSpec(party="IPA", action_type="fundraising", params={"source": "business_elite"}),
    ActionSpec(party="IPA", action_type="pledge", params={
        "pledge": {"topic": "fiscal autonomy for eastern zone"},
        "dimensions": [1, 7], "popularity": 0.8}),

    # --- NDC: Manifesto + media + rally + pledge (3+1+2+0=6 PC, 1 left) ---
    # v1 lesson: NDC lost 14 LGAs. Add media (was 0 in v1), keep rally.
    ActionSpec(party="NDC", action_type="manifesto", params={}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.6}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 7.0}),
    ActionSpec(party="NDC", action_type="pledge", params={
        "pledge": {"topic": "universal infrastructure program"},
        "dimensions": [16, 24], "popularity": 0.7}),

    # --- UJP: Rally + media + fundraising + pledge (2+1+0+0=3 PC, 4 left) ---
    # v1 lesson: UJP was a gainer. Add media to amplify.
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 7.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),
    ActionSpec(party="UJP", action_type="fundraising", params={"source": "grassroots"}),
    ActionSpec(party="UJP", action_type="pledge", params={
        "pledge": {"topic": "Islamic welfare expansion"},
        "dimensions": [0, 24, 16], "popularity": 0.6}),

    # --- NWF: Manifesto + media + fundraising + pledge (3+1+0+0=4 PC, 3 left) ---
    ActionSpec(party="NWF", action_type="manifesto", params={}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),
    ActionSpec(party="NWF", action_type="fundraising", params={"source": "grassroots"}),
    ActionSpec(party="NWF", action_type="pledge", params={
        "pledge": {"topic": "minimum wage tripling"},
        "dimensions": [10, 8, 18], "popularity": 0.7}),

    # --- NHA: Advertising + media + pledge (2+1+0=3 PC, 4 left) ---
    # v1 lesson: NHA was THE biggest winner. Double down on media-heavy.
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.8}),
    ActionSpec(party="NHA", action_type="pledge", params={
        "pledge": {"topic": "universal bio-enhancement access"},
        "dimensions": [20, 9], "popularity": 0.5}),

    # --- SNM: Manifesto + media + rally + pledge (3+1+2+0=6 PC, 1 left) ---
    ActionSpec(party="SNM", action_type="manifesto", params={}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 6.0}),
    ActionSpec(party="SNM", action_type="pledge", params={
        "pledge": {"topic": "WAFTA renegotiation and import controls"},
        "dimensions": [2, 21, 12], "popularity": 0.6}),

    # --- NSA: Manifesto + media + fundraising + pledge (3+1+0+0=4 PC, 3 left) ---
    ActionSpec(party="NSA", action_type="manifesto", params={}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.6}),
    ActionSpec(party="NSA", action_type="fundraising", params={"source": "diaspora"}),
    ActionSpec(party="NSA", action_type="pledge", params={
        "pledge": {"topic": "professional border security force"},
        "dimensions": [12, 11], "popularity": 0.6}),

    # --- CDA: Manifesto + endorsement + media + pledge (3+2+1+0=6 PC, 1 left) ---
    # v1 lesson: CDA dropped -0.20%. Add media, keep religious endorsement.
    ActionSpec(party="CDA", action_type="manifesto", params={}),
    ActionSpec(party="CDA", action_type="endorsement", params={"endorser_type": "religious_leader"}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),
    ActionSpec(party="CDA", action_type="pledge", params={
        "pledge": {"topic": "secular constitution defense"},
        "dimensions": [0, 14], "popularity": 0.5}),

    # --- MBPP: Manifesto + media + fundraising + pledge (3+1+0+0=4 PC, 3 left) ---
    ActionSpec(party="MBPP", action_type="manifesto", params={}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),
    ActionSpec(party="MBPP", action_type="fundraising", params={"source": "grassroots"}),
    ActionSpec(party="MBPP", action_type="pledge", params={
        "pledge": {"topic": "Middle Belt infrastructure fund"},
        "dimensions": [16, 24, 15], "popularity": 0.7}),

    # --- PLF: Rally + media + fundraising + pledge (2+1+0+0=3 PC, 4 left) ---
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),
    ActionSpec(party="PLF", action_type="fundraising", params={"source": "grassroots"}),
    ActionSpec(party="PLF", action_type="pledge", params={
        "pledge": {"topic": "resource revenue for local communities"},
        "dimensions": [7, 24, 8], "popularity": 0.8}),

    # --- NNV: Manifesto + media + pledge (3+1+0=4 PC, 3 left) ---
    ActionSpec(party="NNV", action_type="manifesto", params={}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.6}),
    ActionSpec(party="NNV", action_type="pledge", params={
        "pledge": {"topic": "one Nigeria unity program"},
        "dimensions": [6, 11, 27], "popularity": 0.5}),
]

# ===== TURN 2: ETO Launch + Endorsements =====
# Every party starts ETO building. Delayed manifestos publish. Fundraising continues.
# PC budget: 3-6 remaining + 7 income = 10-13 available.
turn2 = [
    # --- NRP: ETO elite AZ1 (Lagos establishment) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="NRP", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NRP", action_type="endorsement", params={"endorser_type": "celebrity"}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NRP", action_type="fundraising", params={"source": "business_elite"}),

    # --- CND: Endorsement + advertising + media (2+2+1=5) ---
    # v1 lesson: CND needs more endorsements and media to defend lead.
    ActionSpec(party="CND", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.7}),

    # --- ANPC: Manifesto + endorsement + media (3+2+1=6) ---
    ActionSpec(party="ANPC", action_type="manifesto", params={}),
    ActionSpec(party="ANPC", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.6}),

    # --- IPA: ETO economic AZ5 + advertising + media (3+2+1=6) ---
    ActionSpec(party="IPA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 5, "score_change": 3.0}),
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),

    # --- NDC: Endorsement + fundraising + media (2+0+1=3) ---
    ActionSpec(party="NDC", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="NDC", action_type="fundraising", params={"source": "diaspora"}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),

    # --- UJP: Manifesto + ETO mobilization AZ7 + media (3+3+1=7) ---
    ActionSpec(party="UJP", action_type="manifesto", params={}),
    ActionSpec(party="UJP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 7, "score_change": 3.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: Ground game + rally (SYNERGY) + media (3+2+1=6) ---
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 7.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: Manifesto + ETO economic AZ1 + media (3+3+1=7) ---
    # v1 lesson: NHA's media dominance was key. Keep stacking.
    ActionSpec(party="NHA", action_type="manifesto", params={}),
    ActionSpec(party="NHA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.7}),

    # --- SNM: Endorsement + advertising + media (2+2+1=5) ---
    ActionSpec(party="SNM", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NSA: ETO elite AZ7 + rally + media (3+2+1=6) ---
    ActionSpec(party="NSA", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 7, "score_change": 2.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 7.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.5}),

    # --- CDA: Ground game + rally (SYNERGY) + media (3+2+1=6) ---
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: ETO economic AZ6 + endorsement + media (3+2+1=6) ---
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: Manifesto + ground game + media (3+3+1=7) ---
    ActionSpec(party="PLF", action_type="manifesto", params={}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    # --- NNV: Endorsement + advertising + media (2+2+1=5) ---
    ActionSpec(party="NNV", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 3: Ethnic Outreach + ETO Deepening =====
# Ethnic mobilization for identity parties. Second round of ETO. Polls for intelligence.
turn3 = [
    # --- NRP: ETO economic AZ1 (deepen) + advertising + poll tier 2 (3+2+2=7) ---
    ActionSpec(party="NRP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="NRP", action_type="poll", params={"poll_tier": 2, "scope": "zone"}),

    # --- CND: Ethnic mobilization Yoruba + media + endorsement (3+1+2=6) ---
    ActionSpec(party="CND", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Yoruba"}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.7}),
    ActionSpec(party="CND", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),

    # --- ANPC: ETO elite AZ4 (Littoral) + ground game + media (3+3+1=7) ---
    ActionSpec(party="ANPC", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 4, "score_change": 3.0}),
    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.5}),

    # --- IPA: Ethnic mobilization Igbo + rally + media (3+2+1=6) ---
    ActionSpec(party="IPA", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Igbo"}),
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 7.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),

    # --- NDC: ETO legitimacy AZ8 + advertising + media (3+2+1=6) ---
    # v1 lesson: NDC lost -5.22% in Chad, -3.03% in Savanna. Build ETO there.
    ActionSpec(party="NDC", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 8, "score_change": 3.0}),
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),

    # --- UJP: Ethnic mobilization Kanuri + rally + media (3+2+1=6) ---
    ActionSpec(party="UJP", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Kanuri"}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 7.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: Advertising + endorsement + media (2+2+1=5) ---
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: Advertising + media + ETO economic AZ6 (3+1+3=7) ---
    # v1: NHA gained +10.88% in Lagos. Now build FCT presence too.
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.5}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NHA", action_type="fundraising", params={"source": "business_elite"}),

    # --- SNM: Rally + ETO mobilization AZ8 + media (2+3+1=6) ---
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 7.0}),
    ActionSpec(party="SNM", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 8, "score_change": 3.0}),
    ActionSpec(party="SNM", action_type="fundraising", params={"source": "membership"}),

    # --- NSA: Advertising + ground game + media (2+3+1=6) ---
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NSA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.5}),

    # --- CDA: Ethnic mobilization Tiv + ETO legitimacy AZ5 + media (3+3+1=7) ---
    ActionSpec(party="CDA", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Tiv"}),
    ActionSpec(party="CDA", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 5, "score_change": 3.0}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: Ethnic mobilization + rally + media (3+2+1=6) ---
    ActionSpec(party="MBPP", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Middle Belt Minorities"}),
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 6.0}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: Ethnic mobilization Ijaw + ETO mobilization AZ4 + media (3+3+1=7) ---
    ActionSpec(party="PLF", action_type="ethnic_mobilization",
              params={"target_ethnicity": "Ijaw"}),
    ActionSpec(party="PLF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 4, "score_change": 3.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    # --- NNV: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="NNV", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 4: First Crisis (Security incident in Northeast) =====
# NSA benefits (+valence). UJP/NDC penalized. Respond to crisis + oppo research opens.
turn4 = [
    # --- NRP: Oppo research NDC + media + ETO AZ3 (2+1+3=6) ---
    ActionSpec(party="NRP", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 4]}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NRP", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 3, "score_change": 2.0}),

    # --- CND: Oppo research NDC + media + advertising (2+1+2=5) ---
    # v1 lesson: CND had 2 oppo total. Need more to slow NDC.
    ActionSpec(party="CND", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [14, 0]}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.7}),
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="CND", action_type="fundraising", params={"source": "membership"}),

    # --- ANPC: ETO elite AZ3 (Confluence) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="ANPC", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 3, "score_change": 3.0}),
    ActionSpec(party="ANPC", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.6}),

    # --- IPA: Oppo research ANPC + advertising + media (2+2+1=5) ---
    # v1 lesson: ANPC ate IPA's lunch in Littoral (+6.21%). Counter them directly.
    ActionSpec(party="IPA", action_type="opposition_research",
              params={"target_party": "ANPC", "target_dimensions": [1, 27]}),
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),
    ActionSpec(party="IPA", action_type="fundraising", params={"source": "business_elite"}),

    # --- NDC: Crisis response + rally + media (2+2+1=5) ---
    # v1 lesson: NDC never responded to crises. Fix that.
    ActionSpec(party="NDC", action_type="crisis_response", params={"effectiveness": 0.6}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),

    # --- UJP: Crisis response + rally + media (2+2+1=5) ---
    ActionSpec(party="UJP", action_type="crisis_response", params={"effectiveness": 0.6}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 8.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: ETO mobilization AZ1 + advertising + media (3+2+1=6) ---
    ActionSpec(party="NWF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: Media + oppo research SNM (SYNERGY) + advertising (1+2+2=5) ---
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.8}),
    ActionSpec(party="NHA", action_type="opposition_research",
              params={"target_party": "SNM", "target_dimensions": [2, 21]}),
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),

    # --- SNM: Media + oppo research NHA (SYNERGY) + rally (1+2+2=5) ---
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),
    ActionSpec(party="SNM", action_type="opposition_research",
              params={"target_party": "NHA", "target_dimensions": [2, 21]}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 7.0}),

    # --- NSA: Crisis benefits -- rally + advertising + media (2+2+1=5) ---
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.7}),

    # --- CDA: Rally + endorsement + media (2+2+1=5) ---
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="CDA", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="CDA", action_type="fundraising", params={"source": "membership"}),

    # --- MBPP: Ground game + ETO AZ6 + media (3+3+1=7) ---
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: Oppo research NRP + media (SYNERGY) + rally (2+1+2=5) ---
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),
    ActionSpec(party="PLF", action_type="opposition_research",
              params={"target_party": "NRP", "target_dimensions": [7, 18]}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),

    # --- NNV: Crisis response + oppo NDC + media (2+2+1=5) ---
    ActionSpec(party="NNV", action_type="crisis_response", params={"effectiveness": 0.7}),
    ActionSpec(party="NNV", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 11]}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 5: ETO Deepening + Rally/GG Synergies =====
turn5 = [
    # --- NRP: Media + advertising + endorsement (1+2+2=5) ---
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="NRP", action_type="endorsement", params={"endorser_type": "notable"}),

    # --- CND: ETO legitimacy AZ2 + rally + media (3+2+1=6) ---
    ActionSpec(party="CND", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 2, "score_change": 3.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 8.0}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.7}),

    # --- ANPC: Advertising + endorsement + media (2+2+1=5) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="ANPC", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="ANPC", action_type="fundraising", params={"source": "diaspora"}),

    # --- IPA: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 8.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),

    # --- NDC: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    # v1 lesson: NDC needs synergies, not patronage.
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),

    # --- UJP: ETO mobilization AZ7 (deepen) + advertising + media (3+2+1=6) ---
    ActionSpec(party="UJP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 7, "score_change": 3.0}),
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 7.0}),
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: ETO economic AZ6 + media + poll tier 3 (3+1+3=7) ---
    ActionSpec(party="NHA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NHA", action_type="poll", params={"poll_tier": 3, "scope": "state", "target_states": ["Lagos", "Ogun", "Oyo"]}),

    # --- SNM: Ground game + ETO AZ6 + media (3+3+1=7) ---
    ActionSpec(party="SNM", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="SNM", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 6, "score_change": 3.0}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NSA: ETO elite AZ7 (deepen) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="NSA", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 7, "score_change": 3.0}),
    ActionSpec(party="NSA", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="NSA", action_type="fundraising", params={"source": "diaspora"}),

    # --- CDA: ETO legitimacy AZ6 + rally + media (3+2+1=6) ---
    ActionSpec(party="CDA", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 6, "score_change": 3.0}),
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: Advertising + endorsement + media (2+2+1=5) ---
    ActionSpec(party="MBPP", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="MBPP", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    # --- NNV: ETO elite AZ6 + rally + media (3+2+1=6) ---
    ActionSpec(party="NNV", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 6, "score_change": 3.0}),
    ActionSpec(party="NNV", action_type="rally", language="hausa", params={"gm_score": 7.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 6: Opposition Research Blitz + Media Synergies =====
turn6 = [
    # --- NRP: Media + oppo NDC (SYNERGY) + poll tier 3 (1+2+3=6) ---
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.8}),
    ActionSpec(party="NRP", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [4, 14, 0]}),
    ActionSpec(party="NRP", action_type="poll", params={"poll_tier": 3, "scope": "state", "target_states": ["Lagos", "Kaduna", "Kano"]}),
    ActionSpec(party="NRP", action_type="fundraising", params={"source": "business_elite"}),

    # --- CND: Media + oppo NDC (SYNERGY) + rally (1+2+2=5) ---
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.8}),
    ActionSpec(party="CND", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 5, 14]}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 8.0}),

    # --- ANPC: Advertising + ETO AZ4 (deepen) + media (2+3+1=6) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="ANPC", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 4, "score_change": 3.0}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.5}),

    # --- IPA: Media + oppo ANPC (SYNERGY) + ETO AZ5 (1+2+3=6) ---
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.7}),
    ActionSpec(party="IPA", action_type="opposition_research",
              params={"target_party": "ANPC", "target_dimensions": [1, 4]}),
    ActionSpec(party="IPA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 5, "score_change": 3.0}),

    # --- NDC: Oppo CND + endorsement + media (2+2+1=5) ---
    ActionSpec(party="NDC", action_type="opposition_research",
              params={"target_party": "CND", "target_dimensions": [23, 11]}),
    ActionSpec(party="NDC", action_type="endorsement", params={"endorser_type": "religious_leader"}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),
    ActionSpec(party="NDC", action_type="fundraising", params={"source": "diaspora"}),

    # --- UJP: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 8.0}),
    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: Media + oppo NRP (SYNERGY) + endorsement (1+2+2=5) ---
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.6}),
    ActionSpec(party="NWF", action_type="opposition_research",
              params={"target_party": "NRP", "target_dimensions": [10, 8]}),
    ActionSpec(party="NWF", action_type="endorsement", params={"endorser_type": "notable"}),

    # --- NHA: Media + oppo SNM (SYNERGY) + endorsement (1+2+2=5) ---
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.8}),
    ActionSpec(party="NHA", action_type="opposition_research",
              params={"target_party": "SNM", "target_dimensions": [2, 21]}),
    ActionSpec(party="NHA", action_type="endorsement", params={"endorser_type": "celebrity"}),

    # --- SNM: Media + oppo NHA (SYNERGY) + advertising (1+2+2=5) ---
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.6}),
    ActionSpec(party="SNM", action_type="opposition_research",
              params={"target_party": "NHA", "target_dimensions": [2, 21]}),
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),

    # --- NSA: Oppo UJP + rally + media (2+2+1=5) ---
    ActionSpec(party="NSA", action_type="opposition_research",
              params={"target_party": "UJP", "target_dimensions": [0, 11]}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 7.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.6}),

    # --- CDA: Oppo UJP + endorsement + media (2+2+1=5) ---
    ActionSpec(party="CDA", action_type="opposition_research",
              params={"target_party": "UJP", "target_dimensions": [0, 14]}),
    ActionSpec(party="CDA", action_type="endorsement", params={"endorser_type": "religious_leader"}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: ETO AZ5 + rally + media (3+2+1=6) ---
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 5, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="MBPP", action_type="fundraising", params={"source": "grassroots"}),

    # --- PLF: Media + oppo NRP (SYNERGY) + advertising (1+2+2=5) ---
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.7}),
    ActionSpec(party="PLF", action_type="opposition_research",
              params={"target_party": "NRP", "target_dimensions": [7, 18, 8]}),
    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),

    # --- NNV: Oppo NDC + advertising + media (2+2+1=5) ---
    ActionSpec(party="NNV", action_type="opposition_research",
              params={"target_party": "NDC", "target_dimensions": [0, 6, 11]}),
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 7: Max Synergy Phase =====
# Rally+ground game for every party (valence synergy). Media on top where affordable.
turn7 = [
    # --- NRP: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="NRP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),

    # --- CND: Rally + ground game (SYNERGY) + media + endorsement (2+3+1+2=8) ---
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 9.0}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.7}),
    ActionSpec(party="CND", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),

    # --- ANPC: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.6}),

    # --- IPA: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 8.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),

    # --- NDC: Rally + ground game (SYNERGY) + media + endorsement (2+3+1+2=8) ---
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),
    ActionSpec(party="NDC", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),

    # --- UJP: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 8.0}),
    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="NHA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.7}),

    # --- SNM: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="SNM", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NSA: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NSA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.6}),

    # --- CDA: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    # --- NNV: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="NNV", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 8: Second Crisis (WAFTA Trade Dispute) =====
# NHA penalized, SNM boosted. Diversify from T7 to avoid fatigue.
turn8 = [
    # --- NRP: Endorsement + advertising + media (2+2+1=5) ---
    ActionSpec(party="NRP", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),

    # --- CND: Crisis response + media + advertising (2+1+2=5) ---
    # v1 lesson: CND needs crisis responses to defend lead.
    ActionSpec(party="CND", action_type="crisis_response", params={"effectiveness": 0.7}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.7}),
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 1.0}),

    # --- ANPC: Advertising + endorsement + media (2+2+1=5) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="ANPC", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.5}),

    # --- IPA: Oppo ANPC + advertising + media (2+2+1=5) ---
    ActionSpec(party="IPA", action_type="opposition_research",
              params={"target_party": "ANPC", "target_dimensions": [27, 7]}),
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),

    # --- NDC: Advertising + ETO AZ7 + media (2+3+1=6) ---
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NDC", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 7, "score_change": 3.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),

    # --- UJP: Advertising + endorsement + media (2+2+1=5) ---
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="UJP", action_type="endorsement", params={"endorser_type": "religious_leader"}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: ETO AZ4 + advertising + media (3+2+1=6) ---
    ActionSpec(party="NWF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 4, "score_change": 3.0}),
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: Crisis response + media + media (2+1+1=4) ---
    # Double media on crisis turn to control narrative.
    ActionSpec(party="NHA", action_type="crisis_response", params={"effectiveness": 0.8}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.6}),
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),

    # --- SNM: Crisis benefits -- rally + advertising + media (2+2+1=5) ---
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.7}),

    # --- NSA: Advertising + endorsement + media (2+2+1=5) ---
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 1.0}),
    ActionSpec(party="NSA", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.6}),

    # --- CDA: ETO AZ5 (deepen) + advertising + media (3+2+1=6) ---
    ActionSpec(party="CDA", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 5, "score_change": 3.0}),
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: ETO AZ6 (mobilization) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 6, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: ETO AZ4 (deepen) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="PLF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 4, "score_change": 3.0}),
    ActionSpec(party="PLF", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    # --- NNV: ETO AZ2 + advertising + media (3+2+1=6) ---
    ActionSpec(party="NNV", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 2, "score_change": 3.0}),
    ActionSpec(party="NNV", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 9: Final ETO + Strategic Endorsements =====
# Last round of institutional building before the advertising blitz.
turn9 = [
    # --- NRP: ETO AZ1 (third round) + media + advertising (3+1+2=6) ---
    ActionSpec(party="NRP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),

    # --- CND: ETO AZ3 (expand into Confluence) + media + rally (3+1+2=6) ---
    ActionSpec(party="CND", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 3, "score_change": 3.0}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.7}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 8.0}),

    # --- ANPC: ETO AZ3 (triple down Confluence) + rally + media (3+2+1=6) ---
    ActionSpec(party="ANPC", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 3, "score_change": 3.0}),
    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.5}),

    # --- IPA: ETO AZ5 (third round) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="IPA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 5, "score_change": 3.0}),
    ActionSpec(party="IPA", action_type="endorsement", params={"endorser_type": "eto_leader"}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),

    # --- NDC: ETO AZ8 (deepen) + rally + media (3+2+1=6) ---
    ActionSpec(party="NDC", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 8, "score_change": 3.0}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),

    # --- UJP: ETO AZ7 (third round) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="UJP", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 7, "score_change": 3.0}),
    ActionSpec(party="UJP", action_type="endorsement", params={"endorser_type": "religious_leader"}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: ETO AZ1 (deepen) + rally + media (3+2+1=6) ---
    ActionSpec(party="NWF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 8.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: ETO AZ1 (third round) + media + endorsement (3+1+2=6) ---
    ActionSpec(party="NHA", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 1, "score_change": 3.0}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.8}),
    ActionSpec(party="NHA", action_type="endorsement", params={"endorser_type": "notable"}),

    # --- SNM: ETO AZ6 (deepen) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="SNM", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 6, "score_change": 3.0}),
    ActionSpec(party="SNM", action_type="endorsement", params={"endorser_type": "traditional_ruler"}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NSA: ETO AZ7 (third round) + rally + media (3+2+1=6) ---
    ActionSpec(party="NSA", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 7, "score_change": 3.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.6}),

    # --- CDA: ETO AZ6 (deepen) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="CDA", action_type="eto_engagement",
              params={"eto_category": "legitimacy", "az": 6, "score_change": 3.0}),
    ActionSpec(party="CDA", action_type="endorsement", params={"endorser_type": "religious_leader"}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: ETO AZ6 (third round) + rally + media (3+2+1=6) ---
    ActionSpec(party="MBPP", action_type="eto_engagement",
              params={"eto_category": "economic", "az": 6, "score_change": 3.0}),
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 7.0}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: ETO AZ4 (third round) + rally + media (3+2+1=6) ---
    ActionSpec(party="PLF", action_type="eto_engagement",
              params={"eto_category": "mobilization", "az": 4, "score_change": 3.0}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    # --- NNV: ETO AZ6 (deepen) + endorsement + media (3+2+1=6) ---
    ActionSpec(party="NNV", action_type="eto_engagement",
              params={"eto_category": "elite", "az": 6, "score_change": 3.0}),
    ActionSpec(party="NNV", action_type="endorsement", params={"endorser_type": "notable"}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 10: Heavy Advertising Blitz =====
# Advertising + rally (SYNERGY) for everyone. Spend hard.
turn10 = [
    # --- NRP: Advertising + rally (SYNERGY) + media + ground game (4+2+1+3=10) ---
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NRP", action_type="ground_game", params={"intensity": 1.0}),

    # --- CND: Advertising + rally (SYNERGY) + media + ground game (4+2+1+3=10) ---
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 9.0}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.8}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),

    # --- ANPC: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.6}),

    # --- IPA: Advertising + rally (SYNERGY) + media + ground game (4+2+1+3=10) ---
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 9.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),

    # --- NDC: Advertising + rally (SYNERGY) + media + ground game (4+2+1+3=10) ---
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),
    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),

    # --- UJP: Advertising + rally (SYNERGY) + media (2+2+1=5) ---
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 9.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: Advertising + rally (SYNERGY) + media (2+2+1=5) ---
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.8}),

    # --- SNM: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NSA: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.6}),

    # --- CDA: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: Advertising + rally (SYNERGY) + media (2+2+1=5) ---
    ActionSpec(party="MBPP", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 10.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    # --- NNV: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NNV", action_type="rally", language="hausa", params={"gm_score": 8.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 11: Third Crisis (Religious Tensions in Middle Belt) =====
# CDA benefits (+valence). UJP/NDC penalized. Rally+GG synergies + crisis responses.
turn11 = [
    # --- NRP: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="NRP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.7}),

    # --- CND: Rally + ground game (SYNERGY) + media + crisis response (2+3+1+2=8) ---
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 9.0}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.7}),
    ActionSpec(party="CND", action_type="crisis_response", params={"effectiveness": 0.6}),

    # --- ANPC: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.5}),

    # --- IPA: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 9.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.6}),

    # --- NDC: Crisis response + rally + media (2+2+1=5) ---
    ActionSpec(party="NDC", action_type="crisis_response", params={"effectiveness": 0.6}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 10.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),

    # --- UJP: Crisis response + rally + media (2+2+1=5) ---
    ActionSpec(party="UJP", action_type="crisis_response", params={"effectiveness": 0.7}),
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 10.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 9.0}),
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: Rally + media + advertising (2+1+2=5) ---
    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.7}),
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 1.0}),

    # --- SNM: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="SNM", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NSA: Crisis response + rally + media (2+2+1=5) ---
    ActionSpec(party="NSA", action_type="crisis_response", params={"effectiveness": 0.9}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.7}),

    # --- CDA: Crisis benefits -- rally + ground game (SYNERGY) + media + crisis resp (2+3+1+2=8) ---
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.6}),
    ActionSpec(party="CDA", action_type="crisis_response", params={"effectiveness": 0.8}),

    # --- MBPP: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 8.0}),
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),

    # --- PLF: Rally + ground game (SYNERGY) + media (2+3+1=6) ---
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 10.0}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.6}),

    # --- NNV: Crisis response + rally + media (2+2+1=5) ---
    ActionSpec(party="NNV", action_type="crisis_response", params={"effectiveness": 0.7}),
    ActionSpec(party="NNV", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
]

# ===== TURN 12: Final Push =====
# Burn all remaining PC. Advertising + rally + ground game (double synergy) + media.
turn12 = [
    # --- NRP: Advertising + rally (SYNERGY) + ground game (SYNERGY) + media (4+3+3+1=11) ---
    ActionSpec(party="NRP", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NRP", action_type="rally", language="english", params={"gm_score": 10.0}),
    ActionSpec(party="NRP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NRP", action_type="media", language="english", params={"success": 0.8}),

    # --- CND: Advertising + rally (SYNERGY) + ground game (SYNERGY) + media (4+3+3+1=11) ---
    ActionSpec(party="CND", action_type="advertising", language="yoruba",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="CND", action_type="rally", language="yoruba", params={"gm_score": 10.0}),
    ActionSpec(party="CND", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CND", action_type="media", language="yoruba", params={"success": 0.8}),

    # --- ANPC: Advertising + rally (SYNERGY) + ground game + media (4+2+3+1=10) ---
    ActionSpec(party="ANPC", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="ANPC", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="ANPC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="ANPC", action_type="media", language="english", params={"success": 0.6}),

    # --- IPA: Advertising + rally (SYNERGY) + ground game (SYNERGY) + media (4+3+3+1=11) ---
    ActionSpec(party="IPA", action_type="advertising", language="igbo",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="IPA", action_type="rally", language="igbo", params={"gm_score": 10.0}),
    ActionSpec(party="IPA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="IPA", action_type="media", language="igbo", params={"success": 0.7}),

    # --- NDC: Advertising + rally (SYNERGY) + ground game (SYNERGY) + media (4+3+3+1=11) ---
    ActionSpec(party="NDC", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="NDC", action_type="rally", language="hausa", params={"gm_score": 10.0}),
    ActionSpec(party="NDC", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NDC", action_type="media", language="hausa", params={"success": 0.5}),

    # --- UJP: Rally + ground game (SYNERGY) + advertising + media (2+3+2+1=8) ---
    ActionSpec(party="UJP", action_type="rally", language="arabic", params={"gm_score": 10.0}),
    ActionSpec(party="UJP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="UJP", action_type="advertising", language="arabic",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="UJP", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NWF: Advertising + rally (SYNERGY) + ground game + media (2+2+3+1=8) ---
    ActionSpec(party="NWF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 1.0}),
    ActionSpec(party="NWF", action_type="rally", language="pidgin", params={"gm_score": 10.0}),
    ActionSpec(party="NWF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="NWF", action_type="media", language="pidgin", params={"success": 0.5}),

    # --- NHA: Advertising + rally (SYNERGY) + media + ground game (4+2+1+3=10) ---
    ActionSpec(party="NHA", action_type="advertising", language="english",
              params={"medium": "social_media", "budget": 2.0}),
    ActionSpec(party="NHA", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="NHA", action_type="media", language="english", params={"success": 0.8}),
    ActionSpec(party="NHA", action_type="ground_game", params={"intensity": 1.0}),

    # --- SNM: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="SNM", action_type="advertising", language="hausa",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="SNM", action_type="rally", language="hausa", params={"gm_score": 10.0}),
    ActionSpec(party="SNM", action_type="media", language="hausa", params={"success": 0.5}),

    # --- NSA: Advertising + rally (SYNERGY) + media (4+2+1=7) ---
    ActionSpec(party="NSA", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NSA", action_type="rally", language="hausa", params={"gm_score": 9.0}),
    ActionSpec(party="NSA", action_type="media", language="english", params={"success": 0.6}),

    # --- CDA: Rally + ground game (SYNERGY) + advertising + media (2+3+4+1=10) ---
    ActionSpec(party="CDA", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="CDA", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="CDA", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="CDA", action_type="media", language="english", params={"success": 0.5}),

    # --- MBPP: Rally + ground game (SYNERGY) + media + advertising (2+3+1+2=8) ---
    ActionSpec(party="MBPP", action_type="rally", language="english", params={"gm_score": 9.0}),
    ActionSpec(party="MBPP", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="MBPP", action_type="media", language="english", params={"success": 0.5}),
    ActionSpec(party="MBPP", action_type="advertising", language="english",
              params={"medium": "radio", "budget": 1.0}),

    # --- PLF: Rally + ground game (SYNERGY) + advertising + media (3+3+4+1=11) ---
    ActionSpec(party="PLF", action_type="rally", language="pidgin", params={"gm_score": 10.0}),
    ActionSpec(party="PLF", action_type="ground_game", params={"intensity": 1.0}),
    ActionSpec(party="PLF", action_type="advertising", language="pidgin",
              params={"medium": "radio", "budget": 2.0}),
    ActionSpec(party="PLF", action_type="media", language="pidgin", params={"success": 0.7}),

    # --- NNV: Advertising + rally (SYNERGY) + media + ground game (4+2+1+3=10) ---
    ActionSpec(party="NNV", action_type="advertising", language="english",
              params={"medium": "tv", "budget": 2.0}),
    ActionSpec(party="NNV", action_type="rally", language="hausa", params={"gm_score": 10.0}),
    ActionSpec(party="NNV", action_type="media", language="english", params={"success": 0.5}),
    ActionSpec(party="NNV", action_type="ground_game", params={"intensity": 1.0}),
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
        affected_lgas=None,
        salience_shifts={12: 0.08, 11: 0.05},
        valence_effects={"NSA": +0.05, "UJP": -0.05, "NDC": -0.03},
        awareness_boost={"NSA": 0.04, "NNV": 0.02},
    ),
    # Turn 8: WAFTA trade dispute
    CrisisEvent(
        name="WAFTA trade dispute",
        turn=8,
        affected_lgas=None,
        salience_shifts={2: 0.10, 21: 0.06},
        valence_effects={"NHA": -0.05, "SNM": +0.05},
        awareness_boost={"SNM": 0.04, "NHA": 0.03},
    ),
    # Turn 11: Religious tensions in Middle Belt
    CrisisEvent(
        name="Religious tensions in Middle Belt",
        turn=11,
        affected_lgas=None,
        salience_shifts={0: 0.08, 14: 0.04},
        valence_effects={"CDA": +0.04, "UJP": -0.04, "NDC": -0.02},
        awareness_boost={"CDA": 0.04, "UJP": 0.03},
    ),
]

# ---------------------------------------------------------------------------
# Run Campaign
# ---------------------------------------------------------------------------

def _weighted_shares(lga_df, pop, total_pop):
    """Compute population-weighted national shares."""
    shares = {}
    for p in party_names:
        col = f"{p}_share"
        if col in lga_df.columns:
            shares[p] = float(np.dot(lga_df[col].values, pop) / total_pop)
    return shares, pop, total_pop


def _weighted_turnout(lga_df, pop, total_pop):
    return float(np.dot(lga_df["Turnout"].values, pop) / total_pop)


def print_turn_summary(i, result, party_names):
    """Print concise per-turn summary."""
    lga_df = result["lga_results_base"]
    pop = lga_df["Estimated Population"].values.astype(np.float64)
    total_pop = pop.sum()
    shares, pop, total_pop = _weighted_shares(lga_df, pop, total_pop)
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
    shares, pop, total_pop = _weighted_shares(lga_df, pop := lga_df["Estimated Population"].values.astype(np.float64), pop.sum())
    turnout = _weighted_turnout(lga_df, pop, total_pop)
    sorted_parties = sorted(shares.items(), key=lambda x: -x[1])

    # --- National results with vote counts ---
    total_votes = float(np.dot(lga_df["Turnout"].values * pop, np.ones(len(pop))))
    enp = 1.0 / sum(s**2 for _, s in sorted_parties)
    print(f"\nNational Turnout: {turnout:.1%}")
    print(f"Total Votes Cast: {total_votes:,.0f}")
    print(f"Effective Number of Parties (ENP): {enp:.2f}")

    print("\nNATIONAL RESULTS:")
    print(f"  {'Party':12s}  {'Votes':>12s}  {'Share':>7s}  {'PC':>4s}")
    print(f"  {'----------':12s}  {'------------':>12s}  {'-------':>7s}  {'----':>4s}")
    pc_state = result.get("pc_state", {})
    for p, s in sorted_parties:
        votes = s * total_votes
        pc = pc_state.get(p, 0)
        print(f"  {p:12s}  {votes:12,.0f}  {s:6.1%}  {pc:4.0f}")

    # Presidential spread check
    print(f"\nPRESIDENTIAL SPREAD CHECK (>=25% in >=24 states + national plurality):")
    state_col = "State"
    states = lga_df[state_col].unique()
    plurality_party = sorted_parties[0][0]
    for p, s in sorted_parties:
        states_above_25 = 0
        for st in states:
            mask = lga_df[state_col] == st
            st_pop = pop[mask]
            st_total = st_pop.sum()
            if st_total > 0:
                st_share = float(np.dot(lga_df.loc[mask, f"{p}_share"].values, st_pop) / st_total)
                if st_share >= 0.25:
                    states_above_25 += 1
        has_plurality = (p == plurality_party)
        passed = states_above_25 >= 24 and has_plurality
        status = "PASS" if passed else "FAIL"
        print(f"  {p:12s} {status:4s}  ({states_above_25:2d}/24 states, plurality: {'yes' if has_plurality else 'no'}, national: {s:.1%})")

    # MC uncertainty
    mc = result.get("mc_aggregated", None)
    if mc is not None and "party_share_mean" in mc:
        print(f"\nMC NATIONAL SHARE UNCERTAINTY (mean [P5 - P95]):")
        mc_sorted = sorted(mc["party_share_mean"].items(), key=lambda x: -x[1])
        for p, mean_s in mc_sorted:
            p5 = mc.get("party_share_p5", {}).get(p, mean_s)
            p95 = mc.get("party_share_p95", {}).get(p, mean_s)
            print(f"  {p:12s} {mean_s:6.1%}  [{p5:5.1%} - {p95:5.1%}]")
        margin_mean = mc.get("margin_mean", 0)
        margin_p5 = mc.get("margin_p5", 0)
        margin_p95 = mc.get("margin_p95", 0)
        print(f"\nMC NATIONAL MARGIN (1st-2nd): mean {margin_mean:.1%}  [P5 {margin_p5:.1%} - P95 {margin_p95:.1%}]")

    # Zonal shares
    az_col = "Administrative Zone"
    if az_col in lga_df.columns:
        print(f"\nZONAL SHARES:")
        az_name_col = "AZ Name"
        header_parties = [p for p, _ in sorted_parties[:14]]
        hdr = f" {'Administrative Zone':>20s} {'AZ Name':>20s}  {'Turnout':>7s}"
        for p in header_parties:
            hdr += f"  {p + '_share':>10s}"
        print(hdr)
        for az in sorted(lga_df[az_col].unique()):
            mask = lga_df[az_col] == az
            az_pop = pop[mask]
            az_total = az_pop.sum()
            if az_total == 0:
                continue
            az_name = lga_df.loc[mask, az_name_col].iloc[0] if az_name_col in lga_df.columns else ""
            az_turnout = float(np.dot(lga_df.loc[mask, "Turnout"].values, az_pop) / az_total)
            row = f" {az:>20d} {az_name:>20s}  {az_turnout:7.6f}"
            for p in header_parties:
                col = f"{p}_share"
                az_share = float(np.dot(lga_df.loc[mask, col].values, az_pop) / az_total)
                row += f"  {az_share:10.6f}"
            print(row)

    # State vote counts
    print(f"\nSTATE VOTE COUNTS (top 3 parties):")
    top3_names = [p for p, _ in sorted_parties[:3]]
    print(f"  {'State':>12s}  {'Population':>10s}  {'Total_Votes':>11s}", end="")
    for pn in top3_names:
        print(f"  {pn + '_votes':>10s}", end="")
    for pn in top3_names:
        print(f"  {pn + '_share':>10s}", end="")
    print()
    for st in sorted(lga_df[state_col].unique()):
        mask = lga_df[state_col] == st
        st_pop_total = pop[mask].sum()
        st_votes_total = float(np.dot(lga_df.loc[mask, "Turnout"].values, pop[mask]))
        row = f"  {st:>12s}  {st_pop_total:10.0f}  {st_votes_total:11.0f}"
        for pn in top3_names:
            sv = float(np.dot(lga_df.loc[mask, f"{pn}_share"].values * lga_df.loc[mask, "Turnout"].values, pop[mask]))
            row += f"  {sv:10.0f}"
        for pn in top3_names:
            ss = float(np.dot(lga_df.loc[mask, f"{pn}_share"].values, pop[mask]) / st_pop_total) if st_pop_total > 0 else 0
            row += f"  {ss:10.6f}"
        print(row)

    # Seat allocation
    import pandas as pd
    seat_file = Path(data_path).parent / "nigeria_lga_polsim_2058.xlsx"
    try:
        district_seats = pd.read_excel(seat_file, sheet_name="District Seats")
        lga_mapping = pd.read_excel(seat_file, sheet_name="LGA Mapping")
        dist_df = allocate_district_seats(lga_df, party_names, district_seats, lga_mapping)
        total_seats = dist_df["Seats"].sum()
        print(f"\nNATIONAL SEAT TOTALS (Sainte-Lague, {total_seats} seats):")
        print(f"  {'Party':12s}  {'Seats':>5s}  {'%':>6s}  {'Vote %':>7s}")
        print(f"  {'----------':12s}  {'-----':>5s}  {'------':>6s}  {'-------':>7s}")
        party_seat_totals = {}
        for p in party_names:
            seat_col = f"{p}_seats"
            if seat_col in dist_df.columns:
                party_seat_totals[p] = int(dist_df[seat_col].sum())
        seat_sorted = sorted(party_seat_totals.items(), key=lambda x: -x[1])
        for p, seats in seat_sorted:
            seat_pct = seats / total_seats if total_seats > 0 else 0
            vote_pct = shares.get(p, 0)
            print(f"  {p:12s}  {seats:5d}  {seat_pct:5.1%}  {vote_pct:6.1%}")

        # Zonal seat breakdown
        if "AZ Name" in dist_df.columns:
            print(f"\nZONAL SEAT BREAKDOWN:")
            top7 = [p for p, _ in seat_sorted[:7]]
            hdr = f"  {'Zone':28s}  {'Seats':>5s}"
            for p in top7:
                hdr += f"  {p:>5s}"
            print(hdr)
            print(f"  {'-------------------------':28s}  {'-----':>5s}" + "  -----" * len(top7))
            for zone_name in sorted(dist_df["AZ Name"].unique()):
                zmask = dist_df["AZ Name"] == zone_name
                zone_total = int(dist_df.loc[zmask, "Seats"].sum())
                row = f"  {zone_name:28s}  {zone_total:5d}"
                for p in top7:
                    sc = f"{p}_seats"
                    row += f"  {int(dist_df.loc[zmask, sc].sum()) if sc in dist_df.columns else 0:5d}"
                print(row)
    except Exception as e:
        print(f"\n(Seat allocation skipped: {e})")

    # Competitiveness
    comp_df = compute_competitiveness(lga_df, party_names)
    if comp_df is not None and len(comp_df) > 0:
        margins = comp_df["margin"].values if "margin" in comp_df.columns else np.array([])
        enps = comp_df["enp"].values if "enp" in comp_df.columns else np.array([])
        if len(margins) > 0:
            print(f"\nLGA COMPETITIVENESS:")
            print(f"  Margin:  Mean: {np.mean(margins):.1%}  Median: {np.median(margins):.1%}  "
                  f"Min: {np.min(margins):.1%}  Max: {np.max(margins):.1%}")
            if len(enps) > 0:
                print(f"  ENP:     Mean: {np.mean(enps):.2f}  Median: {np.median(enps):.2f}  "
                      f"Min: {np.min(enps):.2f}  Max: {np.max(enps):.2f}")
            print(f"  Tight (<5% margin): {int(np.sum(margins < 0.05))}  |  "
                  f"Safe (>20% margin): {int(np.sum(margins > 0.20))}")

    # Turnout distribution
    turnouts = lga_df["Turnout"].values
    print(f"\nTURNOUT DISTRIBUTION:")
    print(f"  Mean: {np.mean(turnouts):.1%}  Median: {np.median(turnouts):.1%}  "
          f"Min: {np.min(turnouts):.1%}  Max: {np.max(turnouts):.1%}  Std: {np.std(turnouts):.1%}")
    for thresh in [60, 70, 80, 85, 90]:
        count = int(np.sum(turnouts > thresh / 100))
        print(f"  LGAs > {thresh}%: {count}")

    # Coalition feasibility
    try:
        coalitions = compute_coalition_feasibility(lga_df, party_names)
        if coalitions:
            print(f"\nCOALITION FEASIBILITY (2-3 party): {len(coalitions)} viable")
            for c in coalitions[:8]:
                names = "+".join(c["parties"])
                print(f"  {names:36s} {c['combined_share']:6.1%}  "
                      f"({c.get('states_above_threshold', '?')}/24 states)")
    except Exception:
        pass


def main():
    print("=" * 70)
    print("LAGOS-2058 Full Campaign Simulation - 14 Parties, 12 Turns (v2)")
    print(f"PC Income: {7}/turn | Hoarding Cap: {18} | No action cap")
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
