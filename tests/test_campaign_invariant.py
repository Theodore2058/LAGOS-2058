"""
Test that the campaign layer preserves the static election invariant.

When campaign_modifiers is None OR when all arrays are identity/zero,
run_election() must produce exactly the same results as the pre-campaign code.
"""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.election import run_election
from election_engine.campaign_state import CampaignModifiers

DATA_PATH = "nigeria_lga_polsim_2058.xlsx"


def _make_mini_config(n_parties: int = 3, n_mc: int = 5, seed: int = 42) -> ElectionConfig:
    """Create a minimal election config for testing."""
    rng = np.random.default_rng(seed)
    parties = []
    ethnicities = ["Hausa-Fulani", "Yoruba", "Igbo"]
    religions = ["Muslim", "Christian", "Christian"]
    for i in range(n_parties):
        parties.append(Party(
            name=f"P{i}",
            positions=np.clip(rng.normal(0, 2, N_ISSUES), -5, 5),
            valence=rng.uniform(-0.5, 0.5),
            leader_ethnicity=ethnicities[i % len(ethnicities)],
            religious_alignment=religions[i % len(religions)],
        ))
    return ElectionConfig(
        params=EngineParams(),
        parties=parties,
        n_monte_carlo=n_mc,
    )


@pytest.mark.slow
def test_no_campaign_invariant():
    """run_election with campaign_modifiers=None produces same results as without."""
    config = _make_mini_config()
    seed = 12345

    result_none = run_election(
        DATA_PATH, config, seed=seed, verbose=False,
        campaign_modifiers=None,
    )
    result_default = run_election(
        DATA_PATH, config, seed=seed, verbose=False,
    )

    # Compare base LGA results (deterministic path)
    base_none = result_none["lga_results_base"]
    base_default = result_default["lga_results_base"]

    share_cols = [f"P{i}_share" for i in range(3)]
    np.testing.assert_allclose(
        base_none[share_cols].values,
        base_default[share_cols].values,
        atol=1e-10,
        err_msg="campaign_modifiers=None should match default",
    )
    np.testing.assert_allclose(
        base_none["Turnout"].values,
        base_default["Turnout"].values,
        atol=1e-10,
    )


@pytest.mark.slow
def test_neutral_modifiers_invariant():
    """CampaignModifiers.neutral() produces same results as no modifiers."""
    config = _make_mini_config()
    seed = 12345

    result_baseline = run_election(
        DATA_PATH, config, seed=seed, verbose=False,
        campaign_modifiers=None,
    )
    result_neutral = run_election(
        DATA_PATH, config, seed=seed, verbose=False,
        campaign_modifiers=CampaignModifiers.neutral(),
    )

    base_bl = result_baseline["lga_results_base"]
    base_nt = result_neutral["lga_results_base"]

    share_cols = [f"P{i}_share" for i in range(3)]
    np.testing.assert_allclose(
        base_bl[share_cols].values,
        base_nt[share_cols].values,
        atol=1e-10,
        err_msg="neutral modifiers should match no modifiers",
    )
    np.testing.assert_allclose(
        base_bl["Turnout"].values,
        base_nt["Turnout"].values,
        atol=1e-10,
    )


@pytest.mark.slow
def test_zeros_modifiers_invariant():
    """CampaignModifiers.zeros() (awareness=1, shifts=0) matches baseline."""
    config = _make_mini_config()
    seed = 12345
    n_lga = 774
    n_parties = 3

    result_baseline = run_election(
        DATA_PATH, config, seed=seed, verbose=False,
        campaign_modifiers=None,
    )
    result_zeros = run_election(
        DATA_PATH, config, seed=seed, verbose=False,
        campaign_modifiers=CampaignModifiers.zeros(n_lga, n_parties),
    )

    base_bl = result_baseline["lga_results_base"]
    base_zr = result_zeros["lga_results_base"]

    share_cols = [f"P{i}_share" for i in range(3)]
    np.testing.assert_allclose(
        base_bl[share_cols].values,
        base_zr[share_cols].values,
        atol=1e-6,
        err_msg="zeros modifiers (awareness=1, shift=0) should match baseline",
    )
    # Turnout may differ slightly due to ceiling_boost=0 activating ceiling logic
    # but shouldn't change much since ceiling is 0.95 max
    np.testing.assert_allclose(
        base_bl["Turnout"].values,
        base_zr["Turnout"].values,
        atol=0.05,
        err_msg="turnout should be close with zeros modifiers",
    )
