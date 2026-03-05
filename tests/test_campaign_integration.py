"""
Integration and smoke tests for the campaign system.
"""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.campaign import run_campaign
from election_engine.campaign_actions import ActionSpec
from election_engine.campaign_state import CrisisEvent

DATA_PATH = "nigeria_lga_polsim_2058.xlsx"


def _make_config(n_mc: int = 5) -> ElectionConfig:
    """Create a 3-party config for testing."""
    rng = np.random.default_rng(42)
    parties = [
        Party(
            name="NRP",
            positions=np.clip(rng.normal(0, 2, N_ISSUES), -5, 5),
            valence=0.2,
            leader_ethnicity="Yoruba",
            religious_alignment="Christian",
        ),
        Party(
            name="APC",
            positions=np.clip(rng.normal(0, 2, N_ISSUES), -5, 5),
            valence=0.0,
            leader_ethnicity="Hausa-Fulani",
            religious_alignment="Muslim",
        ),
        Party(
            name="PDP",
            positions=np.clip(rng.normal(0, 2, N_ISSUES), -5, 5),
            valence=-0.1,
            leader_ethnicity="Igbo",
            religious_alignment="Christian",
        ),
    ]
    return ElectionConfig(
        params=EngineParams(),
        parties=parties,
        n_monte_carlo=n_mc,
    )


@pytest.mark.slow
def test_3_turn_campaign():
    """Run a 3-turn mini-campaign and verify basic properties."""
    config = _make_config()
    n_lga = 774

    # Create LGA masks for targeting
    turn1 = [
        ActionSpec(
            party="NRP",
            action_type="rally",
            language="yoruba",
            params={"gm_score": 7.0},
        ),
        ActionSpec(
            party="APC",
            action_type="advertising",
            language="hausa",
            params={"medium": "radio", "budget": 1.5},
        ),
    ]

    turn2 = [
        ActionSpec(
            party="NRP",
            action_type="manifesto",
            params={},  # no position change, just awareness boost
        ),
        ActionSpec(
            party="PDP",
            action_type="ground_game",
            params={"intensity": 1.2},
        ),
        ActionSpec(
            party="APC",
            action_type="endorsement",
            params={"endorser_type": "traditional_ruler"},
        ),
    ]

    turn3 = [
        ActionSpec(
            party="NRP",
            action_type="opposition_research",
            params={"target_party": "APC", "target_dimensions": [0, 5]},
        ),
        ActionSpec(
            party="PDP",
            action_type="ethnic_mobilization",
            params={"target_ethnicity": "Igbo"},
        ),
    ]

    results = run_campaign(
        DATA_PATH, config,
        turns=[turn1, turn2, turn3],
        seed=123,
        verbose=False,
    )

    assert len(results) == 3

    for i, result in enumerate(results):
        lga_df = result["lga_results_base"]
        assert len(lga_df) == n_lga

        # Shares should sum to ~1.0 for each LGA
        share_cols = ["NRP_share", "APC_share", "PDP_share"]
        shares = lga_df[share_cols].values
        row_sums = shares.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-6,
                                   err_msg=f"Turn {i+1}: shares don't sum to 1")

        # Turnout should be in [0, 1]
        turnout = lga_df["Turnout"].values
        assert np.all(turnout >= 0), f"Turn {i+1}: negative turnout"
        assert np.all(turnout <= 1), f"Turn {i+1}: turnout > 1"

        # No NaN
        assert not np.any(np.isnan(shares)), f"Turn {i+1}: NaN in shares"
        assert not np.any(np.isnan(turnout)), f"Turn {i+1}: NaN in turnout"


@pytest.mark.slow
def test_crisis_event():
    """Verify crisis events are applied."""
    config = _make_config()

    crisis = CrisisEvent(
        name="Test Crisis",
        turn=1,
        affected_lgas=None,  # national
        salience_shifts={12: 0.15},  # military_role
        valence_effects={"APC": -0.1},
        awareness_boost={"NRP": 0.05},
    )

    turn1 = [
        ActionSpec(party="NRP", action_type="media",
                   params={"success": 0.7}),
    ]

    results = run_campaign(
        DATA_PATH, config,
        turns=[turn1],
        crisis_events=[crisis],
        seed=456,
        verbose=False,
    )

    assert len(results) == 1
    shares = results[0]["lga_results_base"][["NRP_share", "APC_share", "PDP_share"]].values
    assert not np.any(np.isnan(shares))


@pytest.mark.slow
def test_smoke_multi_turn():
    """Smoke test: 6-turn campaign, verify no crashes."""
    config = _make_config()
    rng = np.random.default_rng(789)

    action_types = ["rally", "advertising", "ground_game", "media",
                    "patronage", "endorsement"]
    languages = ["english", "hausa", "yoruba", "igbo", "pidgin"]
    party_names = ["NRP", "APC", "PDP"]

    turns = []
    for t in range(6):
        turn_actions = []
        for party in party_names:
            atype = rng.choice(action_types)
            lang = rng.choice(languages)
            turn_actions.append(ActionSpec(
                party=party,
                action_type=atype,
                language=lang,
                params={"gm_score": 5.0, "budget": 1.0,
                        "intensity": 1.0, "success": 0.5,
                        "scale": 1.0, "endorser_type": "notable"},
            ))
        turns.append(turn_actions)

    results = run_campaign(
        DATA_PATH, config,
        turns=turns,
        seed=789,
        verbose=False,
    )

    assert len(results) == 6

    for i, result in enumerate(results):
        lga_df = result["lga_results_base"]
        share_cols = ["NRP_share", "APC_share", "PDP_share"]
        shares = lga_df[share_cols].values

        # No NaN, shares sum to 1, turnout in [0,1]
        assert not np.any(np.isnan(shares)), f"Turn {i+1}: NaN"
        row_sums = shares.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-5,
                                   err_msg=f"Turn {i+1}: shares sum")
        turnout = lga_df["Turnout"].values
        assert np.all(turnout >= 0) and np.all(turnout <= 1)
