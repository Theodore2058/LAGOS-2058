"""
Campaign Layer Diagnostic Script for LAGOS-2058.

Prints detailed metrics about the campaign state and election results
at each turn, enabling calibration and debugging.

Usage:
    python diagnostics_campaign.py
"""

import sys
import logging
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "src"))

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES, ISSUE_NAMES
from election_engine.campaign import run_campaign
from election_engine.campaign_actions import ActionSpec
from election_engine.campaign_state import CampaignState, CampaignModifiers
from election_engine.campaign_modifiers import compile_modifiers
from election_engine.salience import compute_base_awareness, compute_turnout_ceiling
from election_engine.data_loader import load_lga_data
from election_engine.election import run_election

logging.basicConfig(level=logging.WARNING)

DATA_PATH = str(Path(__file__).parent / "nigeria_lga_polsim_2058.xlsx")


def print_section(title: str) -> None:
    print(f"\n--- {title} ---")


def diagnose_awareness(awareness: np.ndarray, party_names: list[str],
                       az: np.ndarray) -> None:
    """Print awareness distribution stats."""
    print_section("Awareness Distribution")
    n_lga, J = awareness.shape
    for j, name in enumerate(party_names):
        a = awareness[:, j]
        print(f"  {name:12s}: mean={a.mean():.3f}  std={a.std():.3f}  "
              f"min={a.min():.3f}  max={a.max():.3f}")

    # North vs South
    north_mask = np.isin(az, [7, 8])  # NW, NE
    south_mask = np.isin(az, [1, 2, 3])  # SW, SS, SE
    if north_mask.any() and south_mask.any():
        print(f"\n  North (AZ 7-8) mean: {awareness[north_mask].mean():.3f}")
        print(f"  South (AZ 1-3) mean: {awareness[south_mask].mean():.3f}")


def diagnose_turnout_ceiling(lga_data: pd.DataFrame,
                             campaign_mods: CampaignModifiers | None,
                             turnout: np.ndarray) -> None:
    """Print turnout ceiling diagnostics."""
    print_section("Turnout Ceiling")
    ceiling = compute_turnout_ceiling(lga_data)

    if campaign_mods is not None and campaign_mods.ceiling_boost is not None:
        effective_ceiling = np.clip(
            ceiling + campaign_mods.ceiling_boost.astype(np.float32), 0.25, 0.95)
    else:
        effective_ceiling = ceiling

    binding = turnout >= (effective_ceiling - 0.001)
    n_binding = binding.sum()
    print(f"  Ceiling binding: {n_binding} / {len(ceiling)} LGAs")
    print(f"  Mean ceiling: {effective_ceiling.mean():.3f}")
    print(f"  Mean desired turnout: {turnout.mean():.3f}")

    if campaign_mods is not None and campaign_mods.ceiling_boost is not None:
        boosted = campaign_mods.ceiling_boost > 0.001
        if boosted.any():
            print(f"  LGAs with ceiling boost: {boosted.sum()}")
            print(f"  Mean boost: {campaign_mods.ceiling_boost[boosted].mean():.4f}")


def diagnose_salience(salience_matrix: np.ndarray,
                      campaign_mods: CampaignModifiers | None) -> None:
    """Print salience diagnostics."""
    print_section("Salience State")
    # Check sum-to-one
    row_sums = salience_matrix.sum(axis=1)
    max_dev = np.abs(row_sums - 1.0).max()
    print(f"  Max salience sum deviation from 1.0: {max_dev:.2e}")

    if campaign_mods is not None and campaign_mods.salience_shift is not None:
        shift = campaign_mods.salience_shift
        # Top shifted dimensions
        dim_shift_mag = np.abs(shift).mean(axis=0)
        top5 = np.argsort(dim_shift_mag)[-5:][::-1]
        print(f"  Top 5 shifted dimensions:")
        for d in top5:
            if d < len(ISSUE_NAMES):
                print(f"    {ISSUE_NAMES[d]:30s}: mean|shift|={dim_shift_mag[d]:.4f}")


def diagnose_vote_shares(lga_df: pd.DataFrame, party_names: list[str],
                         prev_df: pd.DataFrame | None = None) -> None:
    """Print national vote share diagnostics."""
    print_section("National Vote Shares")
    pop = lga_df["Estimated Population"].values.astype(float)
    total_pop = pop.sum()

    for name in party_names:
        share = (lga_df[f"{name}_share"].values * pop).sum() / total_pop
        line = f"  {name:12s}: {share:6.1%}"
        if prev_df is not None:
            prev_share = (prev_df[f"{name}_share"].values * pop).sum() / total_pop
            diff = share - prev_share
            line += f"  (delta: {diff:+.2%})"
        print(line)

    turnout = (lga_df["Turnout"].values * pop).sum() / total_pop
    print(f"  {'Turnout':12s}: {turnout:6.1%}")


def main():
    print("=" * 70)
    print("LAGOS-2058 Campaign Layer Diagnostics")
    print("=" * 70)

    # Setup
    rng = np.random.default_rng(2058)
    parties = [
        Party(name="NRP", positions=np.clip(rng.normal(0, 2, N_ISSUES), -5, 5),
              valence=0.2, leader_ethnicity="Pada", religious_alignment="Secular"),
        Party(name="ANPC", positions=np.clip(rng.normal(1, 2, N_ISSUES), -5, 5),
              valence=0.0, leader_ethnicity="Hausa-Fulani", religious_alignment="Muslim"),
        Party(name="NDC", positions=np.clip(rng.normal(-1, 2, N_ISSUES), -5, 5),
              valence=-0.1, leader_ethnicity="Igbo", religious_alignment="Christian"),
    ]
    party_names = [p.name for p in parties]
    config = ElectionConfig(params=EngineParams(tau_0=1.0), parties=parties, n_monte_carlo=5)

    lga_data = load_lga_data(DATA_PATH)
    df = lga_data.df
    az = df["Administrative Zone"].values.astype(int)

    # Base awareness
    base_awareness = compute_base_awareness(parties, df)
    diagnose_awareness(base_awareness, party_names, az)

    # Static election (for comparison)
    print("\n" + "=" * 70)
    print("Static Election (no campaign)")
    print("=" * 70)
    result_static = run_election(DATA_PATH, config, seed=2058, verbose=False)
    diagnose_vote_shares(result_static["lga_results_base"], party_names)
    diagnose_turnout_ceiling(df, None, result_static["lga_results_base"]["Turnout"].values)

    # Campaign
    turns = [
        [ActionSpec(party="NRP", action_type="rally", language="english",
                    params={"gm_score": 8.0}),
         ActionSpec(party="ANPC", action_type="advertising", language="hausa",
                    params={"medium": "radio", "budget": 1.5}),
         ActionSpec(party="NDC", action_type="ground_game",
                    params={"intensity": 1.0})],
        [ActionSpec(party="NRP", action_type="manifesto", params={}),
         ActionSpec(party="ANPC", action_type="endorsement",
                    params={"endorser_type": "traditional_ruler"}),
         ActionSpec(party="NDC", action_type="opposition_research",
                    params={"target_party": "ANPC", "target_dimensions": [0, 5]})],
        [ActionSpec(party="NRP", action_type="advertising", language="english",
                    params={"medium": "social_media", "budget": 2.0}),
         ActionSpec(party="ANPC", action_type="ethnic_mobilization",
                    params={"target_ethnicity": "Hausa-Fulani"}),
         ActionSpec(party="NDC", action_type="eto_engagement",
                    params={"eto_category": "economic", "az": 5, "score_change": 3.0})],
    ]

    results = run_campaign(DATA_PATH, config, turns=turns, seed=2058, verbose=False)

    prev_df = result_static["lga_results_base"]
    for i, result in enumerate(results):
        print(f"\n{'=' * 70}")
        print(f"Campaign Turn {i+1}")
        print(f"{'=' * 70}")

        lga_df = result["lga_results_base"]
        diagnose_vote_shares(lga_df, party_names, prev_df)
        diagnose_turnout_ceiling(df, None, lga_df["Turnout"].values)
        prev_df = lga_df

    print(f"\n{'=' * 70}")
    print("Diagnostics complete.")


if __name__ == "__main__":
    main()
