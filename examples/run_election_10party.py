"""
10-party consolidation scenario: what if similar small parties merged?

Merges:
  NNV + NSA -> NUA (Nigerian Unity Alliance): nationalist-security bloc
  ANPC + CDA -> NPP (Nigerian Peoples Party): centrist Christian-inclusive
  NWF + PLF -> LAC (Labour Coalition): united left

Keeps 7 original parties: NRP, CND, NDC, IPA, NHA, UJP, MBPP, SNM
Drops NNV, NSA, ANPC, CDA, NWF, PLF as separate entities.
"""

import sys
import logging
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.election import run_election
from election_engine.results import compute_vote_counts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

# Import original position vectors
from run_election import (
    NRP_POSITIONS, CND_POSITIONS, IPA_POSITIONS, NDC_POSITIONS,
    NHA_POSITIONS, UJP_POSITIONS, SNM_POSITIONS, MBPP_POSITIONS,
    NNV_POSITIONS, NSA_POSITIONS, ANPC_POSITIONS, CDA_POSITIONS,
    NWF_POSITIONS, PLF_POSITIONS,
)

# ---------------------------------------------------------------------------
# Merged party positions (weighted average of constituent parties)
# Weights approximate relative base-run vote shares from 14-party run.
# ---------------------------------------------------------------------------

# NUA = NNV (3.0%) + NSA (3.6%) -> security-nationalist bloc
NUA_POSITIONS = np.clip(
    (NNV_POSITIONS * 3.0 + NSA_POSITIONS * 3.6) / 6.6, -5, 5
)

# NPP = ANPC (5.3%) + CDA (3.4%) -> centrist catch-all
NPP_POSITIONS = np.clip(
    (ANPC_POSITIONS * 5.3 + CDA_POSITIONS * 3.4) / 8.7, -5, 5
)

# LAC = NWF (3.6%) + PLF (4.0%) -> united labour-left
LAC_POSITIONS = np.clip(
    (NWF_POSITIONS * 3.6 + PLF_POSITIONS * 4.0) / 7.6, -5, 5
)

# ---------------------------------------------------------------------------
# Party list — 10 parties
# ---------------------------------------------------------------------------

PARTIES = [
    # --- Kept from 14-party system ---
    Party(
        name="NRP",
        positions=NRP_POSITIONS,
        valence=0.2,
        leader_ethnicity="Pada",
        religious_alignment="Secular",
        economic_positioning=-0.6,
        demographic_coefficients={
            "education": {"Tertiary": 0.5, "Secondary": 0.1},
            "livelihood": {"Formal private": 0.5, "Public sector": 0.2},
            "income": {"Top 20%": 0.4, "Middle 40%": 0.1},
            "age_cohort": {"25-34": 0.2, "35-49": 0.1},
            "setting": {"Urban": 0.3},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={1: +1.0, 2: +0.3, 3: +0.3, 5: +0.2},
    ),
    Party(
        name="CND",
        positions=CND_POSITIONS,
        valence=0.3,  # slightly higher — absorbs some ANPC moderates
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=-0.2,
        demographic_coefficients={
            "education": {"Tertiary": 0.3},
            "livelihood": {"Public sector": 0.3},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.3, 2: +0.8, 3: +0.5, 4: +0.3, 5: +0.2,
        },
    ),
    Party(
        name="NDC",
        positions=NDC_POSITIONS,
        valence=0.15,  # slightly higher — stronger in consolidated field
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.2,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.3, "Public sector": 0.2},
            "age_cohort": {"35-49": 0.1, "50+": 0.2},
            "education": {"Below secondary": 0.1},
            "gender": {"Male": 0.1},
            "income": {"Bottom 40%": 0.1, "Middle 40%": 0.1},
            "setting": {"Rural": 0.1},
        },
        regional_strongholds={6: +0.8, 7: +0.5, 8: +1.0, 2: +0.3},
    ),
    Party(
        name="IPA",
        positions=IPA_POSITIONS,
        valence=0.0,
        leader_ethnicity="Igbo",
        religious_alignment="Pentecostal",
        economic_positioning=-0.4,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.4, "Formal private": 0.3},
            "income": {"Top 20%": 0.3},
            "age_cohort": {"25-34": 0.1},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={5: +1.2, 1: +0.2, 4: +0.15, 3: +0.1},
    ),
    Party(
        name="NHA",
        positions=NHA_POSITIONS,
        valence=0.1,
        leader_ethnicity="Naijin",
        religious_alignment="Secular",
        economic_positioning=-0.5,
        demographic_coefficients={
            "education": {"Tertiary": 0.4, "Secondary": 0.1},
            "livelihood": {"Formal private": 0.3, "Trade/informal": 0.2},
            "income": {"Top 20%": 0.3},
            "age_cohort": {"25-34": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={1: +0.6, 4: +0.3, 3: +0.2, 2: +0.15},
    ),
    Party(
        name="UJP",
        positions=UJP_POSITIONS,
        valence=0.05,
        leader_ethnicity="Kanuri",
        religious_alignment="Al-Shahid",
        economic_positioning=0.5,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.2, "Trade/informal": 0.1},
            "education": {"Below secondary": 0.2},
            "gender": {"Male": 0.2},
            "setting": {"Rural": 0.1, "Peri-urban": 0.1},
        },
        regional_strongholds={7: +1.0, 8: +0.4, 6: +0.15},
    ),
    Party(
        name="MBPP",
        positions=MBPP_POSITIONS,
        valence=0.15,
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
        economic_positioning=0.3,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.3, "Trade/informal": 0.2},
            "education": {"Secondary": 0.1},
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.1},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
        },
        regional_strongholds={5: +0.4, 6: +0.5, 7: +0.3, 3: +0.2},
    ),
    Party(
        name="SNM",
        positions=SNM_POSITIONS,
        valence=0.0,
        leader_ethnicity="Yoruba",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.4,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.3, "Smallholder": 0.2},
            "education": {"Secondary": 0.15},
            "age_cohort": {"35-49": 0.15, "50+": 0.1},
            "setting": {"Peri-urban": 0.1},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={2: +0.4, 3: +0.3, 8: +0.2, 6: +0.1},
    ),
    # --- Merged parties ---
    Party(
        name="NUA",  # Nigerian Unity Alliance (NNV + NSA)
        positions=NUA_POSITIONS,
        valence=0.15,  # combined brand strength
        leader_ethnicity="Hausa",
        religious_alignment="Mainstream Sunni",
        economic_positioning=-0.1,
        demographic_coefficients={
            "livelihood": {"Public sector": 0.4, "Formal private": 0.3},
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "income": {"Middle 40%": 0.2},
            "age_cohort": {"35-49": 0.3, "50+": 0.3},
            "gender": {"Male": 0.3},
            "setting": {"Urban": 0.1},
        },
        regional_strongholds={
            7: +0.5, 6: +0.4, 8: +0.3, 2: +0.2, 3: +0.15,
        },
    ),
    Party(
        name="NPP",  # Nigerian Peoples Party (ANPC + CDA)
        positions=NPP_POSITIONS,
        valence=0.15,
        leader_ethnicity="Edo",
        religious_alignment="Catholic",
        economic_positioning=0.0,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.2, "Formal private": 0.2},
            "education": {"Secondary": 0.2, "Tertiary": 0.1},
            "income": {"Middle 40%": 0.2},
            "setting": {"Peri-urban": 0.15, "Rural": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            3: +0.4, 5: +0.3, 4: +0.2, 6: +0.15, 2: +0.1,
        },
    ),
    Party(
        name="LAC",  # Labour Coalition (NWF + PLF)
        positions=LAC_POSITIONS,
        valence=0.1,
        leader_ethnicity="Ijaw",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.6,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.3, "Smallholder": 0.2},
            "income": {"Bottom 40%": 0.3, "Middle 40%": 0.1},
            "education": {"Below secondary": 0.1, "Secondary": 0.1},
            "setting": {"Urban": 0.1, "Peri-urban": 0.1},
        },
        regional_strongholds={
            4: +0.5, 1: +0.3, 3: +0.2, 5: +0.15,
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LAGOS-2058: 10-Party Consolidation Scenario")
    parser.add_argument("--seed", type=int, default=2058)
    parser.add_argument("--mc", type=int, default=100)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    params = EngineParams(
        q=0.5, beta_s=0.7, alpha_e=3.0, alpha_r=2.0,
        scale=1.0, tau_0=3.9, tau_1=0.3, tau_2=0.5,
        beta_econ=0.3,
        kappa=400.0, sigma_national=0.07, sigma_regional=0.10,
        sigma_turnout=0.02, sigma_turnout_regional=0.03,
    )
    config = ElectionConfig(params=params, parties=PARTIES, n_monte_carlo=args.mc)

    data_path = Path(__file__).parent.parent / "data" / "nigeria_lga_polsim_2058.xlsx"
    results = run_election(data_path, config, seed=args.seed, verbose=not args.quiet)

    party_names = [p.name for p in PARTIES]
    lga_with_votes = compute_vote_counts(results["lga_results_base"], party_names)
    summary = results["summary"]
    mc = results["mc_aggregated"]

    print("\n" + "=" * 70)
    print("LAGOS-2058: 10-PARTY CONSOLIDATION SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("  Merges: NNV+NSA->NUA, ANPC+CDA->NPP, NWF+PLF->LAC")
    print("=" * 70)

    print(f"\nNational Turnout: {summary['national_turnout']:.1%}")
    print(f"Total Votes Cast: {summary['total_votes']:,}")
    print(f"Effective Number of Parties (ENP): {summary['enp']:.2f}")

    print("\nNATIONAL RESULTS (base run):")
    print(f"  {'Party':10s}  {'Votes':>12s}  {'Share':>7s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*7}")
    sorted_parties = sorted(summary["national_shares"].items(), key=lambda x: -x[1])
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        print(f"  {p:10s}  {votes:12,}  {share:6.1%}")

    # MC uncertainty
    print("\nMC NATIONAL SHARE UNCERTAINTY (mean [P5 - P95]):")
    ns = mc["national_share_stats"].sort_values("Mean Share", ascending=False)
    for _, row in ns.iterrows():
        if row["Mean Share"] >= 0.005:
            print(f"  {row['Party']:10s}  {row['Mean Share']:6.1%}  "
                  f"[{row['P5 Share']:5.1%} - {row['P95 Share']:5.1%}]")

    enp_stats = mc.get("enp_stats")
    if enp_stats:
        print(f"\nMC ENP DISTRIBUTION: "
              f"mean {enp_stats['mean']:.2f}  "
              f"[P5 {enp_stats['p5']:.2f} - P95 {enp_stats['p95']:.2f}]")

    # Turnout distribution
    if "Turnout" in lga_with_votes.columns:
        t = lga_with_votes["Turnout"].values
        print(f"\nTURNOUT DISTRIBUTION:")
        print(f"  Mean: {t.mean():.1%}  Median: {np.median(t):.1%}  "
              f"Min: {t.min():.1%}  Max: {t.max():.1%}")


if __name__ == "__main__":
    main()
