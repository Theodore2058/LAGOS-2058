"""
Example: Run a 3-turn campaign simulation on top of the LAGOS-2058 engine.

Usage:
    python examples/run_campaign.py

Demonstrates:
- Base awareness computation (North-South asymmetry)
- Rally and advertising actions raising awareness
- Manifesto publication as biggest awareness event
- Ground game raising turnout ceiling
- Opposition research defining opponents
- Crisis event injection
"""

import sys
import logging
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.campaign import run_campaign
from election_engine.campaign_actions import ActionSpec
from election_engine.campaign_state import CrisisEvent
from election_engine.salience import compute_base_awareness
from election_engine.data_loader import load_lga_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

DATA_PATH = str(Path(__file__).parent.parent / "nigeria_lga_polsim_2058.xlsx")

# ---------------------------------------------------------------------------
# Simplified 3-party setup for demo
# ---------------------------------------------------------------------------

rng = np.random.default_rng(2058)

PARTY_A = Party(
    name="NRP",
    positions=np.clip(rng.normal(0, 2, N_ISSUES), -5, 5),
    valence=0.2,
    leader_ethnicity="Pada",
    religious_alignment="Secular",
    economic_positioning=-0.4,
)

PARTY_B = Party(
    name="ANPC",
    positions=np.clip(rng.normal(1, 2, N_ISSUES), -5, 5),
    valence=0.0,
    leader_ethnicity="Hausa-Fulani",
    religious_alignment="Muslim",
    economic_positioning=0.3,
)

PARTY_C = Party(
    name="NDC",
    positions=np.clip(rng.normal(-1, 2, N_ISSUES), -5, 5),
    valence=-0.1,
    leader_ethnicity="Igbo",
    religious_alignment="Christian",
    economic_positioning=0.5,
)

# NOTE: Default EngineParams (tau_0=4.5) are calibrated for 14-party elections.
# For a 3-party demo, lower tau_0 to get realistic turnout (~40-50%).
config = ElectionConfig(
    params=EngineParams(tau_0=1.0),
    parties=[PARTY_A, PARTY_B, PARTY_C],
    n_monte_carlo=50,
)

# ---------------------------------------------------------------------------
# Show base awareness (North-South asymmetry)
# ---------------------------------------------------------------------------

print("=" * 70)
print("LAGOS-2058 Campaign Layer Demo")
print("=" * 70)

lga_data = load_lga_data(DATA_PATH)
df = lga_data.df

base_awareness = compute_base_awareness(config.parties, df)

# Compare urban Lagos vs rural Zamfara awareness
az = df["Administrative Zone"].values.astype(int)
urban_pct = df["Urban Pct"].fillna(30).values.astype(float) if "Urban Pct" in df.columns else np.full(len(df), 30.0)

# Southwest (AZ 6) high-urban LGAs vs Northwest (AZ 1) low-urban LGAs
sw_urban_mask = (az == 6) & (urban_pct > 60)
nw_rural_mask = (az == 1) & (urban_pct < 20)

if sw_urban_mask.any() and nw_rural_mask.any():
    print(f"\nBase Awareness (before any campaign):")
    print(f"  SW urban mean: {base_awareness[sw_urban_mask].mean():.3f}")
    print(f"  NW rural mean: {base_awareness[nw_rural_mask].mean():.3f}")
    print(f"  Ratio: {base_awareness[sw_urban_mask].mean() / max(base_awareness[nw_rural_mask].mean(), 0.01):.1f}x")

# ---------------------------------------------------------------------------
# Define 3-turn campaign
# ---------------------------------------------------------------------------

turn1 = [
    # NRP rallies in Yoruba language (Southwest)
    ActionSpec(
        party="NRP",
        action_type="rally",
        language="english",
        params={"gm_score": 8.0},
    ),
    # ANPC advertises on radio (effective in rural North)
    ActionSpec(
        party="ANPC",
        action_type="advertising",
        language="hausa",
        params={"medium": "radio", "budget": 1.5},
    ),
    # NDC does ground game nationally
    ActionSpec(
        party="NDC",
        action_type="ground_game",
        params={"intensity": 1.0},
    ),
]

turn2 = [
    # NRP publishes manifesto (biggest awareness event)
    ActionSpec(
        party="NRP",
        action_type="manifesto",
        params={},
    ),
    # ANPC gets endorsement from traditional ruler
    ActionSpec(
        party="ANPC",
        action_type="endorsement",
        params={"endorser_type": "traditional_ruler"},
    ),
    # NDC does opposition research on ANPC
    ActionSpec(
        party="NDC",
        action_type="opposition_research",
        params={"target_party": "ANPC", "target_dimensions": [0, 5, 15]},
    ),
]

turn3 = [
    # NRP targets social media advertising
    ActionSpec(
        party="NRP",
        action_type="advertising",
        language="english",
        params={"medium": "social_media", "budget": 2.0},
    ),
    # ANPC does ethnic mobilization
    ActionSpec(
        party="ANPC",
        action_type="ethnic_mobilization",
        params={"target_ethnicity": "Hausa-Fulani"},
    ),
    # NDC engages ETO
    ActionSpec(
        party="NDC",
        action_type="eto_engagement",
        params={"eto_category": "economic", "az": 5, "score_change": 3.0},
    ),
]

# Crisis in Turn 2: security incident
crisis = CrisisEvent(
    name="Security incident in Northeast",
    turn=2,
    affected_lgas=None,
    salience_shifts={12: 0.10},  # military_role salience spike
    valence_effects={"ANPC": -0.05},
    awareness_boost={"ANPC": 0.03},
)

# ---------------------------------------------------------------------------
# Run campaign
# ---------------------------------------------------------------------------

print("\nRunning 3-turn campaign simulation...")
print("-" * 70)

results = run_campaign(
    DATA_PATH,
    config,
    turns=[turn1, turn2, turn3],
    crisis_events=[crisis],
    seed=2058,
    verbose=True,
)

# ---------------------------------------------------------------------------
# Print results
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("CAMPAIGN RESULTS")
print("=" * 70)

party_names = ["NRP", "ANPC", "NDC"]

for i, result in enumerate(results):
    lga_df = result["lga_results_base"]
    pop = lga_df["Estimated Population"].values.astype(float) if "Estimated Population" in lga_df.columns else np.ones(len(lga_df))
    total_pop = pop.sum()

    print(f"\nTurn {i+1}:")
    for p in party_names:
        share = (lga_df[f"{p}_share"].values * pop).sum() / total_pop
        print(f"  {p}: {share:.1%}")
    turnout = (lga_df["Turnout"].values * pop).sum() / total_pop
    print(f"  Turnout: {turnout:.1%}")

print("\n" + "=" * 70)
print("Demo complete.")
