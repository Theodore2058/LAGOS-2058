"""
LAGOS-2058 Engine Diagnostics

Runs a deterministic election (no MC) and prints calibration health checks:
  - Utility component magnitudes (spatial, ethnic, religious, valence, economic)
  - Spatial vs identity balance ratio
  - Turnout distribution statistics
  - Ethnic heartland dominance checks
  - Party concentration / fragmentation
  - Per-zone turnout and winner breakdown

Usage:
    python diagnostics.py [--seed 2058] [--mc 0]
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "src"))

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.election import run_election
from election_engine.spatial import batch_spatial_utility
from election_engine.results import compute_competitiveness

# Use the example parties
sys.path.insert(0, str(Path(__file__).parent / "examples"))
import run_election as example

DATA_PATH = Path(__file__).parent / "data" / "nigeria_lga_polsim_2058.xlsx"

# Ethnic group -> (data column, expected dominant party) for heartland checks
HEARTLAND_MAP = {
    "Hausa-Fulani": ("% Hausa Fulani Undiff", "NDC"),
    "Hausa": ("% Hausa", "NDC"),
    "Yoruba": ("% Yoruba", "CND"),
    "Igbo": ("% Igbo", "IPA"),
    "Ijaw": ("% Ijaw", "PLF"),
    "Kanuri": ("% Kanuri", "UJP"),
}

# Administrative Zone names for display
AZ_NAMES = {
    1: "Lagos Metropolitan",
    2: "Niger Zone",
    3: "Confluence Zone",
    4: "Southern Coastal",
    5: "Eastern Highlands",
    6: "Central (Kano/Kaduna)",
    7: "Northeastern",
    8: "Northwestern",
}


def compute_utility_magnitudes(results, params, parties):
    """Compute mean absolute utility from spatial and identity components across LGAs."""
    lga_data = results["data"]
    df = lga_data.df
    party_names = [p.name for p in parties]

    positions_matrix = np.array([p.positions for p in parties], dtype=np.float32)  # (J, D)

    # Compute spatial utility for several representative voter positions:
    # neutral (origin), moderate (+1 on all), and extreme (+3 on all)
    voters = np.array([
        np.zeros(N_ISSUES),           # neutral
        np.ones(N_ISSUES),            # mildly positive
        -np.ones(N_ISSUES),           # mildly negative
    ], dtype=np.float32)
    utils = batch_spatial_utility(
        voters, positions_matrix,
        params.q, params.beta_s,
        spatial_normalization=params.spatial_normalization,
    )
    spatial_mags = np.abs(utils)  # (3, J)

    # Identity utility magnitudes from the affinity matrices
    from election_engine.ethnic_affinity import EthnicAffinityMatrix
    from election_engine.religious_affinity import ReligiousAffinityMatrix

    eth_mat = EthnicAffinityMatrix()
    rel_mat = ReligiousAffinityMatrix()

    # Sample ethnic affinities: max is in-group (1.0 * alpha_e)
    # Typical range: 0.0 to alpha_e for ethnic, 0.0 to alpha_r for religious
    ethnic_vals = []
    for voter_eth in ["Hausa", "Yoruba", "Igbo", "Ijaw", "Kanuri", "Fulani", "Tiv"]:
        for p in parties:
            val = eth_mat.get_affinity(voter_eth, p.leader_ethnicity)
            if val != 0:
                ethnic_vals.append(abs(val * params.alpha_e))

    religious_vals = []
    for voter_rel in ["Mainstream Sunni", "Catholic", "Pentecostal", "Traditionalist"]:
        for p in parties:
            val = rel_mat.get_affinity(voter_rel, p.religious_alignment)
            if val != 0:
                religious_vals.append(abs(val * params.alpha_r))

    return {
        "spatial_mean": float(spatial_mags.mean()),
        "spatial_max": float(spatial_mags.max()),
        "spatial_std": float(spatial_mags.std()),
        "ethnic_mean": float(np.mean(ethnic_vals)) if ethnic_vals else 0.0,
        "ethnic_max": float(np.max(ethnic_vals)) if ethnic_vals else 0.0,
        "religious_mean": float(np.mean(religious_vals)) if religious_vals else 0.0,
        "religious_max": float(np.max(religious_vals)) if religious_vals else 0.0,
    }


def print_section(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(description="LAGOS-2058 Engine Diagnostics")
    parser.add_argument("--seed", type=int, default=2058)
    parser.add_argument("--mc", type=int, default=0, help="MC runs (0 for deterministic only)")
    args = parser.parse_args()

    params = EngineParams(
        q=0.5, beta_s=3.0, alpha_e=3.0, alpha_r=2.0,
        scale=1.5, tau_0=4.5, tau_1=0.3, tau_2=0.5,
        beta_econ=0.3,
        kappa=400.0, sigma_national=0.07, sigma_regional=0.10,
    )
    parties = example.PARTIES
    config = ElectionConfig(params=params, parties=parties, n_monte_carlo=args.mc)

    print("Running election (deterministic base)...")
    results = run_election(DATA_PATH, config, seed=args.seed, verbose=False)
    lga_df = results["lga_results_base"]
    summary = results["summary"]
    party_names = [p.name for p in parties]

    # ---- 1. Engine Parameters ----
    print_section("1. ENGINE PARAMETERS")
    print(f"  beta_s  = {params.beta_s:.2f}  (spatial sensitivity)")
    print(f"  alpha_e = {params.alpha_e:.2f}  (ethnic sensitivity)")
    print(f"  alpha_r = {params.alpha_r:.2f}  (religious sensitivity)")
    print(f"  scale   = {params.scale:.2f}  (softmax rationality)")
    print(f"  tau_0   = {params.tau_0:.2f}  (baseline abstention)")
    print(f"  tau_1   = {params.tau_1:.2f}  (alienation)")
    print(f"  tau_2   = {params.tau_2:.2f}  (indifference)")
    print(f"  q       = {params.q:.2f}  (prox-dir mix)")
    print(f"  spatial_norm = {params.spatial_normalization:.3f}  (sqrt({N_ISSUES}) = {np.sqrt(N_ISSUES):.3f})")
    print(f"  beta_econ    = {params.beta_econ:.2f}")

    # ---- 2. Utility Magnitudes ----
    print_section("2. UTILITY COMPONENT MAGNITUDES")
    mags = compute_utility_magnitudes(results, params, parties)
    print(f"  Spatial  (neutral voter):  mean={mags['spatial_mean']:.3f}  max={mags['spatial_max']:.3f}")
    print(f"  Ethnic   (alpha_e * aff): mean={mags['ethnic_mean']:.3f}  max={mags['ethnic_max']:.3f}")
    print(f"  Religious(alpha_r * aff): mean={mags['religious_mean']:.3f}  max={mags['religious_max']:.3f}")

    spatial_max = mags["spatial_max"]
    identity_max = max(mags["ethnic_max"], mags["religious_max"])
    if identity_max > 0:
        ratio = spatial_max / identity_max
        status = "OK" if 0.3 < ratio < 3.0 else "WARNING"
        print(f"\n  Spatial/Identity max ratio: {ratio:.2f}  [{status}]")
        print(f"  (Target: 0.3 - 3.0 for balanced model)")

    # ---- 3. Turnout Distribution ----
    print_section("3. TURNOUT DISTRIBUTION")
    turnout = lga_df["Turnout"].values
    nat_turnout = summary["national_turnout"]
    print(f"  National (pop-weighted): {nat_turnout:.1%}")
    print(f"  LGA mean:   {turnout.mean():.1%}")
    print(f"  LGA median: {np.median(turnout):.1%}")
    print(f"  LGA std:    {turnout.std():.1%}")
    print(f"  LGA min:    {turnout.min():.1%}  max: {turnout.max():.1%}")

    in_range = 0.30 <= nat_turnout <= 0.55
    print(f"\n  National turnout in [30%, 55%]: {'PASS' if in_range else 'FAIL'}")

    below_5 = np.sum(turnout < 0.05)
    above_95 = np.sum(turnout > 0.95)
    print(f"  LGAs below 5%: {below_5}  |  LGAs above 95%: {above_95}")

    # Percentile breakdown
    for pct in [5, 10, 25, 50, 75, 90, 95]:
        print(f"  P{pct:2d}: {np.percentile(turnout, pct):.1%}")

    # ---- 4. National Results ----
    print_section("4. NATIONAL RESULTS")
    sorted_shares = sorted(summary["national_shares"].items(), key=lambda x: -x[1])
    print(f"  ENP: {summary['enp']:.2f}  (target: 4-8)")
    enp_ok = 4.0 <= summary["enp"] <= 8.0
    print(f"  ENP in range: {'PASS' if enp_ok else 'FAIL'}")
    print(f"  Total votes: {summary['total_votes']:,}")
    print()
    print(f"  {'Party':10s}  {'Share':>7s}  {'Votes':>12s}  {'LGA Plur.':>9s}")
    print(f"  {'-'*10}  {'-'*7}  {'-'*12}  {'-'*9}")
    seat_counts = summary["seat_counts"]
    for p, share in sorted_shares:
        votes = summary["national_votes"][p]
        seats = seat_counts.get(p, 0)
        flag = " *" if share > 0.30 else ""
        print(f"  {p:10s}  {share:6.1%}  {votes:12,}  {seats:9d}{flag}")

    top_share = sorted_shares[0][1]
    print(f"\n  Top party share: {top_share:.1%}  (<30% target: {'PASS' if top_share < 0.30 else 'FAIL'})")

    # ---- 5. Ethnic Heartland Checks ----
    print_section("5. ETHNIC HEARTLAND DOMINANCE")
    data_df = results["data"].df
    share_cols = [f"{p}_share" for p in party_names]

    for eth_group, (col, expected_party) in HEARTLAND_MAP.items():
        if col not in data_df.columns:
            print(f"  {eth_group}: column '{col}' not found -- SKIP")
            continue

        # Find LGAs where this ethnic group > 40%
        mask = data_df[col].values > 0.40
        eth_lgas = lga_df[mask]
        if len(eth_lgas) == 0:
            print(f"  {eth_group}: no LGAs with >40% -- SKIP")
            continue

        # Count plurality wins and mean share for expected party
        winners = eth_lgas[share_cols].values.argmax(axis=1)
        winner_names = [party_names[i] for i in winners]
        expected_wins = sum(1 for w in winner_names if w == expected_party)
        pct = expected_wins / len(eth_lgas)
        # Also check: is expected party the top or top-2 in mean share?
        expected_col = f"{expected_party}_share"
        mean_share = eth_lgas[expected_col].mean() if expected_col in eth_lgas.columns else 0
        # Actual top party by mean share across these LGAs
        mean_shares = {p: eth_lgas[f"{p}_share"].mean() for p in party_names}
        actual_top = max(mean_shares, key=mean_shares.get)
        actual_top_share = mean_shares[actual_top]
        status = "PASS" if actual_top == expected_party else "WARN"
        print(f"  {eth_group:18s} -> {expected_party:5s}: "
              f"plur {expected_wins:3d}/{len(eth_lgas):<3d}  "
              f"mean share {mean_share:.1%}  "
              f"top: {actual_top}({actual_top_share:.1%})  [{status}]")

    # ---- 6. Zonal Breakdown ----
    print_section("6. ZONAL BREAKDOWN")
    zonal = summary["zonal_shares"]
    print(f"  {'Zone':30s}  {'Turnout':>7s}  {'Winner':>7s}  {'Top Share':>9s}  {'2nd Share':>9s}")
    print(f"  {'-'*30}  {'-'*7}  {'-'*7}  {'-'*9}  {'-'*9}")
    for _, row in zonal.iterrows():
        az = row.get("AZ Name", f"AZ {row.get('Administrative Zone', '?')}")
        t = row.get("Turnout", 0)
        party_shares = {p: row[f"{p}_share"] for p in party_names if f"{p}_share" in row.index}
        sorted_ps = sorted(party_shares.items(), key=lambda x: -x[1])
        winner = sorted_ps[0][0] if sorted_ps else "?"
        top_s = sorted_ps[0][1] if sorted_ps else 0
        sec_s = sorted_ps[1][1] if len(sorted_ps) > 1 else 0
        print(f"  {str(az):30s}  {t:6.1%}  {winner:>7s}  {top_s:8.1%}  {sec_s:8.1%}")

    # ---- 7. Competitiveness ----
    print_section("7. LGA COMPETITIVENESS")
    comp = compute_competitiveness(lga_df, party_names)
    margins = comp["Margin"].values
    enps = comp["ENP"].values
    print(f"  Margin -- Mean: {margins.mean():.1%}  Median: {np.median(margins):.1%}  "
          f"Std: {margins.std():.1%}")
    print(f"  ENP    -- Mean: {enps.mean():.2f}  Median: {np.median(enps):.2f}  "
          f"Std: {enps.std():.2f}")
    n_tight = np.sum(margins < 0.05)
    n_safe = np.sum(margins > 0.20)
    print(f"  Tight (<5% margin): {n_tight}  |  Safe (>20% margin): {n_safe}")

    # ---- 8. Presidential Spread ----
    print_section("8. PRESIDENTIAL SPREAD CHECK")
    print(f"  {'Party':10s}  {'Plur?':>5s}  {'States>=25%':>11s}  {'Meets?':>6s}")
    print(f"  {'-'*10}  {'-'*5}  {'-'*11}  {'-'*6}")
    for p in party_names:
        sc = results["spread_checks"][p]
        plur = "Y" if sc["has_national_plurality"] else "N"
        meets = "PASS" if sc["meets_requirement"] else "FAIL"
        print(f"  {p:10s}  {plur:>5s}  {sc['states_meeting_25pct']:11d}  {meets:>6s}")

    # ---- Summary ----
    print_section("CALIBRATION SUMMARY")
    checks = {
        "National turnout 30-55%": in_range,
        "ENP 4-8": enp_ok,
        "Top party < 30%": top_share < 0.30,
        "No LGA below 5% turnout": below_5 == 0,
        "No LGA above 95% turnout": above_95 == 0,
    }
    for check, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'}  {check}")

    n_pass = sum(checks.values())
    n_total = len(checks)
    print(f"\n  {n_pass}/{n_total} checks passed")


if __name__ == "__main__":
    main()
