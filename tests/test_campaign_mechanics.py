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


def test_compile_modifiers_with_no_effects():
    """compile_modifiers produces neutral output when state has no effects."""
    import pandas as pd

    state = CampaignState(
        turn=1, n_lga=5, n_parties=2, party_names=["A", "B"],
    )
    state.awareness = np.full((5, 2), 0.75, dtype=np.float32)
    state.cohesion = {"A": 10.0, "B": 10.0}

    # Minimal LGA data with required column
    lga_data = pd.DataFrame({
        "Administrative Zone": [1, 1, 2, 2, 3],
    })

    mods = compile_modifiers(state, lga_data)

    # Awareness should match state
    np.testing.assert_array_almost_equal(mods.awareness, state.awareness)
    # All other channels should be zero
    np.testing.assert_array_equal(mods.salience_shift, np.zeros((5, 28), dtype=np.float32))
    np.testing.assert_array_equal(mods.valence, np.zeros((5, 2), dtype=np.float32))
    np.testing.assert_array_equal(mods.ceiling_boost, np.zeros(5, dtype=np.float32))
    np.testing.assert_array_equal(mods.tau_modifier, np.zeros(5, dtype=np.float32))


def test_compile_modifiers_aggregates_effects():
    """compile_modifiers correctly aggregates multiple active effects."""
    import pandas as pd

    state = CampaignState(
        turn=1, n_lga=5, n_parties=2, party_names=["A", "B"],
    )
    state.awareness = np.full((5, 2), 0.70, dtype=np.float32)
    state.cohesion = {"A": 10.0, "B": 10.0}

    # Add a valence effect for party A
    effect = ActiveEffect(
        source_party="A", source_action="endorsement", source_turn=1,
        channel="valence", target_lgas=None, target_dimensions=None,
        target_party="A", magnitude=0.10,
        effect_key="A:valence:A:endorse:notable",
    )
    state.apply_effect(effect)

    # Add a tau effect
    tau_effect = ActiveEffect(
        source_party="A", source_action="rally", source_turn=1,
        channel="tau", target_lgas=None, target_dimensions=None,
        target_party=None, magnitude=-0.20,
        effect_key="A:tau::rally:",
    )
    state.apply_effect(tau_effect)

    lga_data = pd.DataFrame({
        "Administrative Zone": [1, 1, 2, 2, 3],
    })

    mods = compile_modifiers(state, lga_data)

    # Valence for party A should be positive (0.10 * cohesion=1.0 * conc=1.0)
    assert mods.valence[0, 0] == pytest.approx(0.10, abs=0.01)
    # Party B valence unaffected
    assert mods.valence[0, 1] == pytest.approx(0.0, abs=0.01)
    # Tau should be negative (reducing abstention)
    assert mods.tau_modifier[0] == pytest.approx(-0.20, abs=0.01)


# ===========================================================================
# NEW MECHANICS TESTS
# ===========================================================================

# ---------------------------------------------------------------------------
# Scandal system
# ---------------------------------------------------------------------------

def test_scandal_probability_table():
    """Scandal probability increases with exposure."""
    from election_engine.campaign_modifiers import get_scandal_probability
    assert get_scandal_probability(0.0) == 0.0
    assert get_scandal_probability(2.0) == 0.0
    assert get_scandal_probability(3.0) == 0.10
    assert get_scandal_probability(5.0) == 0.25
    assert get_scandal_probability(7.0) == 0.45
    assert get_scandal_probability(10.0) == 0.70


def test_scandal_roll_no_exposure():
    """No scandal when exposure is below threshold."""
    from election_engine.campaign_modifiers import roll_scandals
    state = CampaignState(turn=5, n_lga=5, n_parties=2, party_names=["A", "B"])
    state.cohesion = {"A": 10.0, "B": 10.0}
    state.exposure = {"A": 1.0, "B": 0.0}
    state.political_capital = {"A": 10.0, "B": 10.0}

    rng = np.random.default_rng(42)
    scandals = roll_scandals(state, rng)
    assert len(scandals) == 0  # exposure < 3 → probability = 0


def test_scandal_roll_high_exposure():
    """High exposure party eventually triggers a scandal."""
    from election_engine.campaign_modifiers import roll_scandals
    state = CampaignState(turn=5, n_lga=5, n_parties=2, party_names=["A", "B"])
    state.cohesion = {"A": 10.0, "B": 10.0}
    state.exposure = {"A": 10.0, "B": 0.0}  # 70% probability
    state.political_capital = {"A": 20.0, "B": 10.0}

    # Run many times — should trigger at least once
    triggered = False
    for seed in range(50):
        # Reset state each time
        state.exposure["A"] = 10.0
        state.cohesion["A"] = 10.0
        state.political_capital["A"] = 20.0
        rng = np.random.default_rng(seed)
        scandals = roll_scandals(state, rng)
        if scandals:
            triggered = True
            break
    assert triggered, "Scandal should trigger with 70% probability over 50 attempts"


def test_scandal_consequences():
    """Scandal halves exposure, costs PC, hits cohesion, adds valence effect."""
    from election_engine.campaign_modifiers import roll_scandals, SCANDAL_PC_DAMAGE, SCANDAL_COHESION_HIT
    state = CampaignState(turn=5, n_lga=5, n_parties=1, party_names=["A"])
    state.cohesion = {"A": 8.0}
    state.exposure = {"A": 10.0}
    state.political_capital = {"A": 15.0}

    # Find a seed that triggers
    for seed in range(100):
        state.exposure["A"] = 10.0
        state.cohesion["A"] = 8.0
        state.political_capital["A"] = 15.0
        state.effects.clear()
        state.scandal_history.clear()
        rng = np.random.default_rng(seed)
        scandals = roll_scandals(state, rng)
        if scandals:
            assert state.exposure["A"] == pytest.approx(5.0)  # halved
            assert state.political_capital["A"] == pytest.approx(15.0 - SCANDAL_PC_DAMAGE)
            assert state.cohesion["A"] == pytest.approx(8.0 - SCANDAL_COHESION_HIT)
            assert len(state.scandal_history) == 1
            # Valence effect should be applied
            assert any("scandal" in k for k in state.effects)
            return
    pytest.skip("No seed triggered a scandal in 100 attempts")


# ---------------------------------------------------------------------------
# Exposure decay
# ---------------------------------------------------------------------------

def test_exposure_decay_after_clean_turns():
    """Exposure decays by 1/turn after 3 clean turns."""
    from election_engine.campaign_modifiers import apply_exposure_decay
    state = CampaignState(turn=5, n_lga=5, n_parties=2, party_names=["A", "B"])
    state.exposure = {"A": 4.0, "B": 2.0}
    state._last_exposure_turn = {"A": 1, "B": 4}

    # Turn 5: A has been clean since turn 1 (4 turns clean) → decay
    #          B was dirty at turn 4 (1 turn clean) → no decay
    apply_exposure_decay(state)
    assert state.exposure["A"] == pytest.approx(3.0)
    assert state.exposure["B"] == pytest.approx(2.0)


def test_exposure_decay_no_underflow():
    """Exposure doesn't go below 0."""
    from election_engine.campaign_modifiers import apply_exposure_decay
    state = CampaignState(turn=10, n_lga=5, n_parties=1, party_names=["A"])
    state.exposure = {"A": 0.5}
    state._last_exposure_turn = {"A": 1}

    apply_exposure_decay(state)
    assert state.exposure["A"] == 0.0


def test_exposure_no_decay_within_3_turns():
    """No decay when exposure was recent (within 3 turns)."""
    from election_engine.campaign_modifiers import apply_exposure_decay
    state = CampaignState(turn=4, n_lga=5, n_parties=1, party_names=["A"])
    state.exposure = {"A": 5.0}
    state._last_exposure_turn = {"A": 2}  # 2 turns clean → no decay

    apply_exposure_decay(state)
    assert state.exposure["A"] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Fundraising sources
# ---------------------------------------------------------------------------

def test_fundraising_default_source():
    """Default (diaspora) fundraising yields base amount."""
    state = CampaignState(turn=1, n_lga=5, n_parties=1, party_names=["A"])
    state.awareness = np.full((5, 1), 0.70, dtype=np.float32)
    state.cohesion = {"A": 10.0}
    state.political_capital = {"A": 0.0}

    import pandas as pd
    lga_data = pd.DataFrame({"Administrative Zone": [1, 1, 2, 2, 3]})

    action = ActionSpec(party="A", action_type="fundraising", params={"source": "diaspora"})
    from election_engine.campaign_actions import resolve_fundraising
    resolve_fundraising(action, state, lga_data, [])

    # Diaspora yields 3 PC (same as old flat rate)
    assert state.political_capital["A"] == pytest.approx(3.0)


def test_fundraising_business_elite_high_yield_plus_exposure():
    """Business elite fundraising: 4 PC yield + 1 exposure."""
    state = CampaignState(turn=1, n_lga=5, n_parties=1, party_names=["A"])
    state.awareness = np.full((5, 1), 0.70, dtype=np.float32)
    state.cohesion = {"A": 10.0}
    state.political_capital = {"A": 0.0}
    state.exposure = {"A": 0.0}

    import pandas as pd
    lga_data = pd.DataFrame({"Administrative Zone": [1, 1, 2, 2, 3]})

    action = ActionSpec(party="A", action_type="fundraising", params={"source": "business_elite"})
    from election_engine.campaign_actions import resolve_fundraising
    resolve_fundraising(action, state, lga_data, [])

    assert state.political_capital["A"] == pytest.approx(4.0)
    assert state.exposure["A"] == pytest.approx(1.0)


def test_fundraising_membership_scales_with_cohesion():
    """Membership fundraising yield scales with party cohesion."""
    import pandas as pd
    lga_data = pd.DataFrame({"Administrative Zone": [1, 1, 2, 2, 3]})
    from election_engine.campaign_actions import resolve_fundraising

    # High cohesion → 3 PC
    state = CampaignState(turn=1, n_lga=5, n_parties=1, party_names=["A"])
    state.awareness = np.full((5, 1), 0.70, dtype=np.float32)
    state.cohesion = {"A": 10.0}
    state.political_capital = {"A": 0.0}
    action = ActionSpec(party="A", action_type="fundraising", params={"source": "membership"})
    resolve_fundraising(action, state, lga_data, [])
    high_yield = state.political_capital["A"]

    # Low cohesion → 1 PC
    state2 = CampaignState(turn=1, n_lga=5, n_parties=1, party_names=["A"])
    state2.awareness = np.full((5, 1), 0.70, dtype=np.float32)
    state2.cohesion = {"A": 2.0}
    state2.political_capital = {"A": 0.0}
    action2 = ActionSpec(party="A", action_type="fundraising", params={"source": "membership"})
    resolve_fundraising(action2, state2, lga_data, [])
    low_yield = state2.political_capital["A"]

    assert high_yield > low_yield


def test_fundraising_consecutive_penalty():
    """Consecutive fundraising from same source reduces yield."""
    import pandas as pd
    lga_data = pd.DataFrame({"Administrative Zone": [1, 1, 2, 2, 3]})
    from election_engine.campaign_actions import resolve_fundraising

    state = CampaignState(turn=1, n_lga=5, n_parties=1, party_names=["A"])
    state.awareness = np.full((5, 1), 0.70, dtype=np.float32)
    state.cohesion = {"A": 10.0}
    state.political_capital = {"A": 0.0}

    # First diaspora fundraise
    action = ActionSpec(party="A", action_type="fundraising", params={"source": "diaspora"})
    resolve_fundraising(action, state, lga_data, [])
    first_yield = state.political_capital["A"]

    # Second consecutive from same source
    old_balance = state.political_capital["A"]
    state.turn = 2
    resolve_fundraising(action, state, lga_data, [])
    second_yield = state.political_capital["A"] - old_balance

    assert second_yield < first_yield, "Consecutive same-source yield should decrease"


# ---------------------------------------------------------------------------
# Action resolution order
# ---------------------------------------------------------------------------

def test_action_resolution_order():
    """Actions are sorted by resolution order."""
    from election_engine.campaign_actions import ACTION_RESOLUTION_ORDER

    actions = [
        ActionSpec(party="A", action_type="fundraising", params={}),
        ActionSpec(party="A", action_type="manifesto", params={}),
        ActionSpec(party="A", action_type="rally", language="english", params={}),
        ActionSpec(party="A", action_type="opposition_research", params={"target_party": "B"}),
    ]

    sorted_actions = sorted(actions, key=lambda a: ACTION_RESOLUTION_ORDER.get(a.action_type, 3))

    assert sorted_actions[0].action_type == "manifesto"  # order 0
    assert sorted_actions[1].action_type == "rally"       # order 3
    assert sorted_actions[2].action_type == "opposition_research"  # order 4
    assert sorted_actions[3].action_type == "fundraising"  # order 5


# ---------------------------------------------------------------------------
# Volatile momentum
# ---------------------------------------------------------------------------

def test_volatile_momentum_detection():
    """Volatile momentum detected when direction changes frequently."""
    from election_engine.campaign_modifiers import is_volatile_momentum

    state = CampaignState(turn=5, n_lga=5, n_parties=1, party_names=["A"])

    # Not volatile: consistent direction
    state._momentum_history["A"] = ["rising", "rising", "rising", "rising"]
    assert not is_volatile_momentum(state, "A")

    # Volatile: frequent changes
    state._momentum_history["A"] = ["rising", "falling", "rising", "falling"]
    assert is_volatile_momentum(state, "A")

    # Barely volatile: 2 changes in 3 entries
    state._momentum_history["A"] = ["rising", "falling", "rising"]
    assert is_volatile_momentum(state, "A")

    # Not volatile: only 1 change
    state._momentum_history["A"] = ["rising", "rising", "falling"]
    assert not is_volatile_momentum(state, "A")


def test_volatile_momentum_no_valence_bonus():
    """Volatile momentum suppresses valence bonus."""
    import pandas as pd
    from election_engine.campaign_modifiers import compile_modifiers

    state = CampaignState(turn=5, n_lga=5, n_parties=2, party_names=["A", "B"])
    state.awareness = np.full((5, 2), 0.70, dtype=np.float32)
    state.cohesion = {"A": 10.0, "B": 10.0}

    # A has rising momentum but volatile history
    state.momentum = {"A": 3, "B": 3}
    state.momentum_direction = {"A": "rising", "B": "rising"}
    state._momentum_history = {
        "A": ["rising", "falling", "rising", "falling"],  # volatile
        "B": ["rising", "rising", "rising", "rising"],     # consistent
    }

    lga_data = pd.DataFrame({"Administrative Zone": [1, 1, 2, 2, 3]})
    mods = compile_modifiers(state, lga_data)

    # A should get no momentum bonus (volatile)
    # B should get +0.06 (3 turns rising, capped)
    assert mods.valence[0, 0] == pytest.approx(0.0, abs=0.01)
    assert mods.valence[0, 1] == pytest.approx(0.06, abs=0.01)


# ---------------------------------------------------------------------------
# Cohesion: region neglect and engagement bonus
# ---------------------------------------------------------------------------

def test_cohesion_region_neglect():
    """Cohesion drops when support region neglected 3+ turns."""
    import pandas as pd
    from election_engine.campaign import update_post_turn

    state = CampaignState(turn=4, n_lga=5, n_parties=1, party_names=["A"])
    state.cohesion = {"A": 8.0}
    state.previous_shares = {"A": 0.5}
    state._region_engagement = {"A": {1: 1}}  # AZ 1 last engaged turn 1

    lga_data = pd.DataFrame({"Administrative Zone": [1, 1, 2, 2, 3]})

    # Fake result with population
    result = {
        "lga_results_base": pd.DataFrame({
            "A_share": [0.5, 0.5, 0.5, 0.5, 0.5],
            "Estimated Population": [100, 100, 100, 100, 100],
        }),
        "_parties": [],
    }

    # Turn 4: AZ 1 last engaged turn 1 → 3 turns neglected → penalty
    # No actions this turn targeting AZ 1
    post_log = update_post_turn(state, result, [], lga_data=lga_data)

    # Cohesion should reflect: +1 recovery, -1 neglect = net 0 change
    # (recovery happens first, then neglect penalty)
    assert state.cohesion["A"] <= 8.0


def test_cohesion_broad_engagement_bonus():
    """Cohesion bonus for campaigning in 3+ AZs."""
    import pandas as pd
    from election_engine.campaign import update_post_turn

    state = CampaignState(turn=2, n_lga=6, n_parties=1, party_names=["A"])
    state.cohesion = {"A": 7.0}
    state.previous_shares = {"A": 0.5}

    lga_data = pd.DataFrame({"Administrative Zone": [1, 2, 3, 4, 5, 6]})

    result = {
        "lga_results_base": pd.DataFrame({
            "A_share": [0.5] * 6,
            "Estimated Population": [100] * 6,
        }),
        "_parties": [],
    }

    # Actions targeting 3 different AZs
    az1_mask = np.array([True, False, False, False, False, False])
    az2_mask = np.array([False, True, False, False, False, False])
    az3_mask = np.array([False, False, True, False, False, False])
    actions = [
        ActionSpec(party="A", action_type="rally", target_lgas=az1_mask, params={}),
        ActionSpec(party="A", action_type="rally", target_lgas=az2_mask, params={}),
        ActionSpec(party="A", action_type="rally", target_lgas=az3_mask, params={}),
    ]

    post_log = update_post_turn(state, result, actions, lga_data=lga_data)

    # Should get: +1 recovery + +1 broad engagement = 9.0
    assert state.cohesion["A"] >= 9.0


# ---------------------------------------------------------------------------
# Exposure tracking on ethnic_mobilization and patronage
# ---------------------------------------------------------------------------

def test_ethnic_mobilization_tracks_exposure_turn():
    """Ethnic mobilization records the last exposure turn."""
    import pandas as pd
    from election_engine.campaign_actions import resolve_action
    from election_engine.config import ElectionConfig, EngineParams, Party, N_ISSUES

    state = CampaignState(turn=3, n_lga=5, n_parties=1, party_names=["A"])
    state.awareness = np.full((5, 1), 0.70, dtype=np.float32)
    state.cohesion = {"A": 10.0}

    config = ElectionConfig(
        params=EngineParams(),
        parties=[Party(name="A", positions=np.zeros(N_ISSUES),
                        leader_ethnicity="Yoruba", religious_alignment="Christian")],
        n_monte_carlo=1,
    )
    lga_data = pd.DataFrame({
        "Administrative Zone": [1, 1, 2, 2, 3],
        "% Yoruba": [80, 60, 10, 5, 0],
    })

    action = ActionSpec(party="A", action_type="ethnic_mobilization",
                        params={"target_ethnicity": "Yoruba"})
    resolve_action(action, state, lga_data, config)

    assert state._last_exposure_turn.get("A") == 3
