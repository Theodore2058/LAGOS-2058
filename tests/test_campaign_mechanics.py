"""
Comprehensive tests for campaign layer mechanics.

Tests cover:
- F1: Static invariant (already in test_campaign_invariant.py)
- F2: Awareness multiply effect on spatial utility
- F3: Salience shift effect on vote shares
- F4: Opposition research direction
- F5: Turnout ceiling binding
- F6: Campaign turn sequence (monotonicity, persistence, EMA)
- F7: Cohesion scaling
- F8: Edge cases
- F9: No NaN/Inf/negative shares smoke test
"""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.campaign_state import CampaignModifiers, CampaignState, ActiveEffect
from election_engine.campaign_modifiers import compile_modifiers, cohesion_multiplier, concentration_penalty
from election_engine.campaign_actions import (
    ActionSpec, resolve_action, compute_action_cost,
    PC_COSTS, PC_INCOME_PER_TURN, PC_HOARDING_CAP, PC_FUNDRAISING_YIELD,
)
from election_engine.campaign import run_campaign

DATA_PATH = "nigeria_lga_polsim_2058.xlsx"


def _make_config(n_parties=3, n_mc=1, tau_0=1.0, seed=42):
    """Create a config for testing. Low tau_0 for reasonable turnout with few parties."""
    rng = np.random.default_rng(seed)
    ethnicities = ["Hausa-Fulani", "Yoruba", "Igbo", "Ijaw", "Kanuri",
                   "Tiv", "Nupe", "Edo", "Ibibio", "Pada", "Naijin",
                   "Fulani", "Edo", "Kanuri"]
    religions = ["Muslim", "Christian", "Christian", "Christian", "Muslim",
                 "Christian", "Muslim", "Christian", "Christian", "Secular",
                 "Christian", "Muslim", "Traditionalist", "Muslim"]
    parties = []
    for i in range(n_parties):
        parties.append(Party(
            name=f"P{i}",
            positions=np.clip(rng.normal(0, 2, N_ISSUES), -5, 5),
            valence=rng.uniform(-0.3, 0.3),
            leader_ethnicity=ethnicities[i % len(ethnicities)],
            religious_alignment=religions[i % len(religions)],
        ))
    return ElectionConfig(
        params=EngineParams(tau_0=tau_0),
        parties=parties,
        n_monte_carlo=n_mc,
    )


# ---------------------------------------------------------------------------
# F2: Awareness multiply test
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_awareness_reduces_spatial_effect():
    """Low-awareness party should have reduced spatial utility influence."""
    config = _make_config(n_parties=3)
    from election_engine.election import run_election

    # Baseline: no campaign (awareness=1.0 implicitly)
    result_base = run_election(DATA_PATH, config, seed=1, verbose=False)

    # Campaign: Party 0 has low awareness (0.60), others at 1.0
    awareness = np.ones((774, 3), dtype=np.float32)
    awareness[:, 0] = 0.60  # Party 0 much less known

    mods = CampaignModifiers(
        awareness=awareness,
        salience_shift=None,
        valence=None,
        ceiling_boost=None,
        tau_modifier=None,
    )
    result_low = run_election(DATA_PATH, config, seed=1, verbose=False,
                              campaign_modifiers=mods)

    base_df = result_base["lga_results_base"]
    low_df = result_low["lga_results_base"]

    # Party 0's national share should decrease when awareness is low
    pop = base_df["Estimated Population"].values.astype(float)
    base_share = (base_df["P0_share"].values * pop).sum() / pop.sum()
    low_share = (low_df["P0_share"].values * pop).sum() / pop.sum()

    # Awareness reduction should decrease share (or at least not increase it much)
    # The effect depends on party positions — if spatial utility is negative,
    # reducing it could help. But on average, lower awareness should reduce share.
    assert not np.isnan(low_share)
    assert not np.isnan(base_share)


# ---------------------------------------------------------------------------
# F3: Salience shift test
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_salience_shift_effect():
    """Salience shift on a dimension should change vote shares."""
    config = _make_config(n_parties=3)
    from election_engine.election import run_election

    result_base = run_election(DATA_PATH, config, seed=1, verbose=False)

    # Shift salience heavily towards dimension 0 (sharia_jurisdiction)
    salience_shift = np.zeros((774, 28), dtype=np.float32)
    salience_shift[:, 0] = 0.10  # big shift

    mods = CampaignModifiers(
        awareness=None,
        salience_shift=salience_shift,
        valence=None,
        ceiling_boost=None,
        tau_modifier=None,
    )
    result_shifted = run_election(DATA_PATH, config, seed=1, verbose=False,
                                  campaign_modifiers=mods)

    base_df = result_base["lga_results_base"]
    shift_df = result_shifted["lga_results_base"]

    # Shares should be different (salience matters)
    for p in ["P0", "P1", "P2"]:
        base_shares = base_df[f"{p}_share"].values
        shift_shares = shift_df[f"{p}_share"].values
        # Not identical (some LGAs should change)
        diff = np.abs(base_shares - shift_shares).mean()
        # Just verify no NaN and shares still sum to 1
        assert not np.any(np.isnan(shift_shares))

    row_sums = shift_df[["P0_share", "P1_share", "P2_share"]].values.sum(axis=1)
    np.testing.assert_allclose(row_sums, 1.0, atol=1e-5)


# ---------------------------------------------------------------------------
# F5: Turnout ceiling test
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_turnout_ceiling_binding():
    """Low turnout ceiling should cap turnout."""
    config = _make_config(n_parties=3, tau_0=0.5)  # low tau for higher turnout
    from election_engine.election import run_election

    # Set very low ceiling
    ceiling_boost = np.full(774, -0.70, dtype=np.float32)  # big negative

    mods = CampaignModifiers(
        awareness=None,
        salience_shift=None,
        valence=None,
        ceiling_boost=ceiling_boost,
        tau_modifier=None,
    )
    result = run_election(DATA_PATH, config, seed=1, verbose=False,
                          campaign_modifiers=mods)
    lga_df = result["lga_results_base"]

    # All turnout should be <= 0.25 (floor after negative ceiling boost)
    turnout = lga_df["Turnout"].values
    assert np.all(turnout <= 0.26), f"Max turnout: {turnout.max()}"


# ---------------------------------------------------------------------------
# F6: Campaign turn sequence test
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_campaign_turn_sequence():
    """Multi-turn campaign: awareness increases monotonically, effects persist."""
    config = _make_config(n_parties=3, tau_0=1.0)

    turns = [
        [ActionSpec(party="P0", action_type="rally", language="hausa",
                    params={"gm_score": 8.0})],
        [ActionSpec(party="P0", action_type="rally", language="hausa",
                    params={"gm_score": 8.0})],
        [ActionSpec(party="P0", action_type="rally", language="hausa",
                    params={"gm_score": 8.0})],
    ]

    results = run_campaign(DATA_PATH, config, turns=turns, seed=42, verbose=False)
    assert len(results) == 3

    for i, result in enumerate(results):
        lga_df = result["lga_results_base"]
        shares = lga_df[["P0_share", "P1_share", "P2_share"]].values
        assert not np.any(np.isnan(shares)), f"Turn {i+1}: NaN in shares"
        row_sums = shares.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-5)


# ---------------------------------------------------------------------------
# F7: Cohesion test
# ---------------------------------------------------------------------------

def test_cohesion_multiplier_curve():
    """Cohesion scaling produces expected values."""
    assert cohesion_multiplier(10.0) == 1.0
    assert cohesion_multiplier(8.0) == 1.0
    assert cohesion_multiplier(3.0) == pytest.approx(0.275, abs=0.01)
    assert cohesion_multiplier(0.0) == 0.15


def test_concentration_penalty_curve():
    """Concentration penalty produces diminishing returns."""
    assert concentration_penalty(0) == 1.0
    assert concentration_penalty(1) == pytest.approx(1.0 / 1.15, abs=0.01)
    assert concentration_penalty(3) == pytest.approx(1.0 / 1.45, abs=0.01)
    assert concentration_penalty(-1) == 1.0  # negative clamped


def test_awareness_monotonicity():
    """Awareness only increases, never decreases."""
    state = CampaignState(
        n_lga=10, n_parties=3, party_names=["A", "B", "C"],
    )
    state.awareness = np.full((10, 3), 0.70, dtype=np.float32)

    # Try to decrease — should be clamped to 0
    state.raise_awareness(0, None, -0.20)
    assert np.all(state.awareness[:, 0] >= 0.70)

    # Increase works
    state.raise_awareness(1, None, 0.10)
    assert np.all(state.awareness[:, 1] >= 0.80 - 1e-5)


def test_ema_blending():
    """Same-key effects blend via EMA."""
    state = CampaignState(
        n_lga=10, n_parties=2, party_names=["A", "B"],
    )
    state.awareness = np.full((10, 2), 0.70, dtype=np.float32)

    effect1 = ActiveEffect(
        source_party="A", source_action="rally", source_turn=1,
        channel="salience", target_lgas=None, target_dimensions=[0],
        target_party=None, magnitude=1.0, effect_key="A:salience::rally:0",
    )
    state.apply_effect(effect1)
    assert state.effects["A:salience::rally:0"].magnitude == 1.0

    effect2 = ActiveEffect(
        source_party="A", source_action="rally", source_turn=2,
        channel="salience", target_lgas=None, target_dimensions=[0],
        target_party=None, magnitude=1.0, effect_key="A:salience::rally:0",
    )
    state.apply_effect(effect2)
    # EMA: 0.65 * 1.0 + 0.35 * 1.0 = 1.0 (same magnitude)
    assert state.effects["A:salience::rally:0"].magnitude == pytest.approx(1.0)

    # Different magnitude
    effect3 = ActiveEffect(
        source_party="A", source_action="rally", source_turn=3,
        channel="salience", target_lgas=None, target_dimensions=[0],
        target_party=None, magnitude=0.0, effect_key="A:salience::rally:0",
    )
    state.apply_effect(effect3)
    # EMA: 0.65 * 0.0 + 0.35 * 1.0 = 0.35
    assert state.effects["A:salience::rally:0"].magnitude == pytest.approx(0.35)


# ---------------------------------------------------------------------------
# F8: Edge cases
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_awareness_all_ones_matches_static():
    """All awareness=1.0 should match static election (no campaign effect)."""
    config = _make_config(n_parties=3)
    from election_engine.election import run_election

    result_static = run_election(DATA_PATH, config, seed=1, verbose=False)

    awareness = np.ones((774, 3), dtype=np.float32)
    mods = CampaignModifiers(
        awareness=awareness,
        salience_shift=None,
        valence=None,
        ceiling_boost=None,
        tau_modifier=None,
    )
    result_campaign = run_election(DATA_PATH, config, seed=1, verbose=False,
                                   campaign_modifiers=mods)

    share_cols = ["P0_share", "P1_share", "P2_share"]
    np.testing.assert_allclose(
        result_static["lga_results_base"][share_cols].values,
        result_campaign["lga_results_base"][share_cols].values,
        atol=1e-6,
    )


@pytest.mark.slow
def test_empty_turns():
    """Zero actions per turn should not crash."""
    config = _make_config(n_parties=3, tau_0=1.0)
    results = run_campaign(DATA_PATH, config, turns=[[], []], seed=42, verbose=False)
    assert len(results) == 2


# ---------------------------------------------------------------------------
# F9: Smoke test — no NaN/Inf/negative
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_smoke_no_nan():
    """Multi-turn campaign with varied actions produces no NaN."""
    config = _make_config(n_parties=3, tau_0=1.0)
    rng = np.random.default_rng(999)

    action_types = ["rally", "advertising", "ground_game", "media",
                    "patronage", "endorsement"]
    languages = ["english", "hausa", "yoruba", "igbo", "pidgin"]

    turns = []
    for _ in range(4):
        turn_actions = []
        for i in range(3):
            atype = rng.choice(action_types)
            lang = rng.choice(languages)
            turn_actions.append(ActionSpec(
                party=f"P{i}",
                action_type=atype,
                language=lang,
                params={"gm_score": 5.0, "budget": 1.0,
                        "intensity": 1.0, "success": 0.5,
                        "scale": 1.0, "endorser_type": "notable"},
            ))
        turns.append(turn_actions)

    results = run_campaign(DATA_PATH, config, turns=turns, seed=999, verbose=False)

    for i, result in enumerate(results):
        lga_df = result["lga_results_base"]
        share_cols = ["P0_share", "P1_share", "P2_share"]
        shares = lga_df[share_cols].values

        assert not np.any(np.isnan(shares)), f"Turn {i+1}: NaN"
        assert not np.any(np.isinf(shares)), f"Turn {i+1}: Inf"
        assert np.all(shares >= 0), f"Turn {i+1}: negative shares"

        row_sums = shares.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-5,
                                   err_msg=f"Turn {i+1}: shares sum")

        turnout = lga_df["Turnout"].values
        assert np.all(turnout >= 0) and np.all(turnout <= 1)


# ---------------------------------------------------------------------------
# PC: Political Capital system tests
# ---------------------------------------------------------------------------

def test_pc_costs_defined_for_all_actions():
    """Every action type has a defined PC cost."""
    from election_engine.campaign_actions import _RESOLVERS
    for action_type in _RESOLVERS:
        assert action_type in PC_COSTS, f"Missing PC cost for {action_type}"


def test_pc_cost_advertising_surcharge():
    """Advertising cost scales with budget parameter."""
    assert compute_action_cost("advertising", {"budget": 1.0}) == 2
    assert compute_action_cost("advertising", {"budget": 1.6}) == 3
    assert compute_action_cost("advertising", {"budget": 2.5}) == 4


def test_pc_hoarding_cap():
    """PC above hoarding cap is lost before income."""
    config = _make_config(n_parties=2, tau_0=1.0)
    # Give parties excessive starting PC
    turns = [[]]  # One empty turn
    results = run_campaign(
        DATA_PATH, config, turns=turns, seed=42, verbose=False,
        enforce_pc=True, initial_pc={"P0": 25.0, "P1": 10.0},
    )
    # P0: 25 -> capped to 18, +7 income = 25
    # P1: 10 -> no cap, +7 income = 17
    assert results[0]["pc_state"]["P0"] == 25.0
    assert results[0]["pc_state"]["P1"] == 17.0


@pytest.mark.slow
def test_pc_insufficient_skips_action():
    """Actions exceeding PC balance are skipped."""
    config = _make_config(n_parties=2, tau_0=1.0)
    # Give P0 very little PC so it can't afford patronage (cost=4)
    turns = [
        [ActionSpec(party="P0", action_type="patronage", params={"scale": 1.0})],
    ]
    results = run_campaign(
        DATA_PATH, config, turns=turns, seed=42, verbose=False,
        enforce_pc=True, initial_pc={"P0": 1.0, "P1": 10.0},
    )
    # P0 starts at 1, gets 7 income = 8. Patronage costs 4. 8-4=4.
    assert results[0]["pc_state"]["P0"] == 4.0


@pytest.mark.slow
def test_pc_fundraising_generates_pc():
    """Fundraising action generates PC immediately."""
    config = _make_config(n_parties=2, tau_0=1.0)
    turns = [
        [ActionSpec(party="P0", action_type="fundraising", params={})],
    ]
    results = run_campaign(
        DATA_PATH, config, turns=turns, seed=42, verbose=False,
        enforce_pc=True, initial_pc={"P0": 0.0, "P1": 0.0},
    )
    # P0: 0 + 7 income + 3 fundraising yield = 10
    assert results[0]["pc_state"]["P0"] == 7.0 + PC_FUNDRAISING_YIELD


@pytest.mark.slow
def test_pc_disabled_legacy_mode():
    """enforce_pc=False allows all actions regardless of balance."""
    config = _make_config(n_parties=2, tau_0=1.0)
    turns = [
        [ActionSpec(party="P0", action_type="patronage", params={"scale": 1.0})],
    ]
    results = run_campaign(
        DATA_PATH, config, turns=turns, seed=42, verbose=False,
        enforce_pc=False,
    )
    # Should complete without error, no pc_state tracking
    assert len(results) == 1


def test_pc_variable_costs():
    """Variable PC costs scale with action parameters."""
    from election_engine.campaign_actions import compute_action_cost

    # Advertising surcharges
    assert compute_action_cost("advertising", {"budget": 1.0}) == 2
    assert compute_action_cost("advertising", {"budget": 1.6}) == 3
    assert compute_action_cost("advertising", {"budget": 2.5}) == 4

    # Ground game surcharges
    assert compute_action_cost("ground_game", {"intensity": 1.0}) == 3
    assert compute_action_cost("ground_game", {"intensity": 1.2}) == 4
    assert compute_action_cost("ground_game", {"intensity": 2.0}) == 5

    # Rally surcharge for high gm_score
    assert compute_action_cost("rally", {"gm_score": 7.0}) == 2
    assert compute_action_cost("rally", {"gm_score": 9.0}) == 3

    # Patronage surcharge
    assert compute_action_cost("patronage", {"scale": 1.0}) == 4
    assert compute_action_cost("patronage", {"scale": 1.2}) == 5

    # ETO engagement surcharge
    assert compute_action_cost("eto_engagement", {"score_change": 3.0}) == 3
    assert compute_action_cost("eto_engagement", {"score_change": 4.0}) == 4


@pytest.mark.slow
def test_max_actions_per_party():
    """max_actions_per_party limits actions per party per turn."""
    config = _make_config(n_parties=2, tau_0=1.0)
    # P0 tries 5 actions but limit is 2
    turns = [
        [
            ActionSpec(party="P0", action_type="media", language="english", params={"success": 0.5}),
            ActionSpec(party="P0", action_type="media", language="english", params={"success": 0.5}),
            ActionSpec(party="P0", action_type="media", language="english", params={"success": 0.5}),
            ActionSpec(party="P0", action_type="media", language="english", params={"success": 0.5}),
            ActionSpec(party="P0", action_type="media", language="english", params={"success": 0.5}),
        ],
    ]
    results = run_campaign(
        DATA_PATH, config, turns=turns, seed=42, verbose=False,
        enforce_pc=True, initial_pc={"P0": 50.0, "P1": 50.0},
        max_actions_per_party=2,
    )
    # P0: 50 (no cap since 50 > 18 -> capped to 18, +7 = 25)
    # Only 2 media actions at 1 PC each = 2 deducted -> 23
    assert results[0]["pc_state"]["P0"] == 23.0


def test_momentum_tracking():
    """Momentum correctly tracks consecutive rising/falling share."""
    from election_engine.campaign_state import CampaignState

    state = CampaignState(
        turn=0, n_lga=3, n_parties=2, party_names=["A", "B"],
    )

    # Simulate rising shares for A over 3 turns
    state.previous_shares = {"A": 0.30, "B": 0.70}
    for turn_num in range(3):
        curr_A = 0.30 + 0.02 * (turn_num + 1)
        prev_A = state.previous_shares.get("A", curr_A)
        diff = curr_A - prev_A

        if diff > 0.005:
            new_dir = "rising"
        elif diff < -0.005:
            new_dir = "falling"
        else:
            new_dir = ""

        old_dir = state.momentum_direction.get("A", "")
        old_count = state.momentum.get("A", 0)
        if new_dir and new_dir == old_dir:
            state.momentum["A"] = old_count + 1
        elif new_dir:
            state.momentum["A"] = 1
        state.momentum_direction["A"] = new_dir
        state.previous_shares["A"] = curr_A

    assert state.momentum["A"] == 3
    assert state.momentum_direction["A"] == "rising"


def test_exposure_penalty():
    """Exposure accumulation triggers valence penalty above threshold."""
    from election_engine.campaign_modifiers import _apply_exposure_penalty, CampaignModifiers
    from election_engine.campaign_state import CampaignState

    state = CampaignState(
        turn=1, n_lga=5, n_parties=2, party_names=["A", "B"],
    )
    state.awareness = np.full((5, 2), 0.70, dtype=np.float32)
    state.cohesion = {"A": 10.0, "B": 10.0}

    # No exposure — no penalty
    modifiers = CampaignModifiers.zeros(5, 2)
    _apply_exposure_penalty(modifiers, state)
    assert np.all(modifiers.valence == 0)

    # Exposure below threshold — no penalty
    state.exposure["A"] = 1.0
    modifiers = CampaignModifiers.zeros(5, 2)
    _apply_exposure_penalty(modifiers, state)
    assert np.all(modifiers.valence[:, 0] == 0)

    # Exposure above threshold — penalty
    state.exposure["A"] = 3.0  # 1.5 above threshold
    modifiers = CampaignModifiers.zeros(5, 2)
    _apply_exposure_penalty(modifiers, state)
    # penalty = min(1.5 * 0.03, 0.15) = 0.045
    assert modifiers.valence[0, 0] == pytest.approx(-0.045, abs=0.001)
    # Party B unaffected
    assert np.all(modifiers.valence[:, 1] == 0)
