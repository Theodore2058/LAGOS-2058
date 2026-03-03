"""
Polarised 6-party scenario: what if Nigerian politics consolidated into
clear ideological blocs?

  1. SDP  - Social Democratic Party (centre-left, pan-southern)
  2. APC  - All Progressives Congress (centre-right, pan-northern)
  3. LP   - Labour Party (hard left, urban workers)
  4. NIF  - Nigerian Islamic Front (Islamist, NE)
  5. SCA  - Southern Confederal Alliance (autonomist, SE/SS)
  6. MBU  - Middle Belt Union (regionalist, Middle Belt)

Tests a highly polarised system with fewer parties but sharper divides.
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

# ---------------------------------------------------------------------------
# Party positions (28 dimensions)
# ---------------------------------------------------------------------------

# SDP - Social Democratic Party
# Pan-southern centre-left coalition. Pro-secular, pro-press freedom,
# pro-women's rights, moderate on economics. The party of Yoruba intellectuals,
# Edo professionals, and southern Christians who want stability and reform.
SDP_POSITIONS = np.array([
    -3.0,  #  0  sharia: secular
    +1.5,  #  1  fiscal: mild autonomy
    -2.0,  #  2  chinese: Western lean
    -2.0,  #  3  bic: mildly anti-BIC
    -1.0,  #  4  ethnic_quotas: mildly meritocratic
    -1.0,  #  5  fertility: mild population control
    -2.0,  #  6  constitutional: parliamentary
    +1.0,  #  7  resource: mild local control
    +2.0,  #  8  housing: interventionist
    +1.5,  #  9  education: mild centralism
    +1.0,  # 10  labor: mildly pro-labor
    -3.0,  # 11  military: civilian control
    -0.5,  # 12  immigration: centrist
    +2.0,  # 13  language: pro-English
    +3.0,  # 14  womens_rights: progressive
    -2.0,  # 15  trad_authority: marginalize
    +2.0,  # 16  infrastructure: universal
    +2.0,  # 17  land_tenure: formalization
    +1.5,  # 18  taxation: redistribution
    +0.5,  # 19  agriculture: centrist
    +1.5,  # 20  bio_enhancement: moderate pro
    +2.5,  # 21  trade: open
    +2.0,  # 22  environment: regulatory
    +4.0,  # 23  media: press freedom
    +2.5,  # 24  healthcare: universal
    +0.5,  # 25  pada_status: mild pro-Pada
    +2.0,  # 26  energy: green
    -1.0,  # 27  az_restructuring: mild restructure
])

# APC - All Progressives Congress
# Pan-northern centre-right. Pro-sharia, pro-natalist, pro-traditional authority,
# economic paternalism. The party of the Arewa establishment: governors, emirs,
# civil servants, and smallholders who want stability within Islamic norms.
APC_POSITIONS = np.array([
    +3.0,  #  0  sharia: pro-sharia
    +2.0,  #  1  fiscal: autonomy
    -0.5,  #  2  chinese: centrist
    -3.0,  #  3  bic: abolish BIC
    +3.0,  #  4  ethnic_quotas: affirmative action
    +3.5,  #  5  fertility: pro-natalist
    +3.0,  #  6  constitutional: presidential
    -1.0,  #  7  resource: mildly federal
    +1.5,  #  8  housing: mildly interventionist
    -2.0,  #  9  education: localist
    +0.5,  # 10  labor: centrist
    +1.5,  # 11  military: mild guardianship
    +3.0,  # 12  immigration: restrictionist
    -2.0,  # 13  language: vernacular
    -2.5,  # 14  womens_rights: conservative
    +3.5,  # 15  trad_authority: strong integration
    +2.5,  # 16  infrastructure: universal
    -1.5,  # 17  land_tenure: customary
    +1.0,  # 18  taxation: mild redistribution
    +3.0,  # 19  agriculture: protectionist
    -2.0,  # 20  bio_enhancement: against
    -1.0,  # 21  trade: mildly autarkic
    -1.5,  # 22  environment: growth first
    +0.5,  # 23  media: centrist
    +2.0,  # 24  healthcare: universal
    -3.5,  # 25  pada_status: anti-Pada
    -1.5,  # 26  energy: fossil
    +0.5,  # 27  az_restructuring: centrist
])

# LP - Labour Party
# Hard left. Urban workers, slum dwellers, gig economy. Maximum redistribution,
# housing, healthcare. Anti-capital, anti-traditional authority. Multi-ethnic
# by default: the party of anyone who works for a living.
LP_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular
    -2.0,  #  1  fiscal: centralist
    +1.5,  #  2  chinese: mild WAFTA
    -1.5,  #  3  bic: mildly anti-BIC
    +1.5,  #  4  ethnic_quotas: mild affirmative
    -2.0,  #  5  fertility: population control
    -3.0,  #  6  constitutional: parliamentary
    -0.5,  #  7  resource: centrist
    +5.0,  #  8  housing: maximum intervention
    +2.0,  #  9  education: centralist
    +5.0,  # 10  labor: maximum pro-labor
    -3.0,  # 11  military: civilian control
    -2.0,  # 12  immigration: open
    -1.5,  # 13  language: mildly vernacular
    +3.5,  # 14  womens_rights: progressive
    -4.0,  # 15  trad_authority: marginalize
    +4.5,  # 16  infrastructure: universal
    -3.0,  # 17  land_tenure: customary/communal
    +5.0,  # 18  taxation: maximum redistribution
    +3.5,  # 19  agriculture: protectionist
    +3.0,  # 20  bio_enhancement: pro-access
    -2.5,  # 21  trade: autarkic
    +2.5,  # 22  environment: regulatory
    +2.0,  # 23  media: mild press freedom
    +5.0,  # 24  healthcare: maximum universal
    -1.5,  # 25  pada_status: mildly anti-Pada
    +2.5,  # 26  energy: green
    +1.0,  # 27  az_restructuring: centrist
])

# NIF - Nigerian Islamic Front
# Islamist hardliners. Full sharia, anti-bio-enhancement, anti-Pada, pro-natalist.
# Based in NE Kanuri heartland with Al-Shahid sympathies. Wants restructuring
# toward Islamic state model.
NIF_POSITIONS = np.array([
    +5.0,  #  0  sharia: full sharia
    +4.0,  #  1  fiscal: strong autonomy
    -1.5,  #  2  chinese: mildly Western
    -4.5,  #  3  bic: abolish BIC
    +3.5,  #  4  ethnic_quotas: affirmative action
    +5.0,  #  5  fertility: maximum pro-natalist
    +2.0,  #  6  constitutional: mildly presidential
    +1.0,  #  7  resource: mild local control
    +2.5,  #  8  housing: interventionist
    -4.5,  #  9  education: radical localist/Islamic
    +2.5,  # 10  labor: pro-labor
    -2.0,  # 11  military: civilian (want Islamic militia)
    +3.5,  # 12  immigration: restrictionist
    -4.0,  # 13  language: Arabic/vernacular
    -5.0,  # 14  womens_rights: extreme patriarchy
    +4.0,  # 15  trad_authority: integration
    +3.0,  # 16  infrastructure: universal
    -3.0,  # 17  land_tenure: customary/Islamic
    +3.0,  # 18  taxation: Islamic redistribution
    +4.0,  # 19  agriculture: protectionist
    -5.0,  # 20  bio_enhancement: total prohibition
    -2.5,  # 21  trade: autarkic
    +0.5,  # 22  environment: centrist
    -1.5,  # 23  media: state-controlled
    +3.0,  # 24  healthcare: universal (Islamic welfare)
    -5.0,  # 25  pada_status: extreme anti-Pada
    -0.5,  # 26  energy: centrist
    -3.5,  # 27  az_restructuring: restructure
])

# SCA - Southern Confederal Alliance
# Southeastern/Niger Delta autonomists. Strong fiscal federalism, resource control,
# meritocracy, pro-trade. The Igbo-Ijaw alliance demanding economic self-determination.
SCA_POSITIONS = np.array([
    -3.5,  #  0  sharia: secular
    +4.5,  #  1  fiscal: near-confederal
    -2.0,  #  2  chinese: Western lean
    -1.0,  #  3  bic: mildly anti-BIC
    -3.0,  #  4  ethnic_quotas: meritocratic
    +0.5,  #  5  fertility: centrist
    +1.0,  #  6  constitutional: mildly presidential
    +4.0,  #  7  resource: strong local control
    -1.0,  #  8  housing: mildly market
    +2.0,  #  9  education: centralist
    -2.0,  # 10  labor: pro-capital
    -2.0,  # 11  military: civilian control
    +0.5,  # 12  immigration: centrist
    +2.0,  # 13  language: pro-English
    +1.5,  # 14  womens_rights: moderate progressive
    -2.0,  # 15  trad_authority: marginalize
    -1.0,  # 16  infrastructure: targeted
    +3.5,  # 17  land_tenure: formalization
    -2.5,  # 18  taxation: low tax
    -2.0,  # 19  agriculture: free market
    +2.0,  # 20  bio_enhancement: pro-access
    +3.0,  # 21  trade: open
    +1.5,  # 22  environment: mild regulation
    +2.5,  # 23  media: press freedom
    -1.0,  # 24  healthcare: mildly market
    -0.5,  # 25  pada_status: centrist
    -0.5,  # 26  energy: centrist
    -2.5,  # 27  az_restructuring: restructure toward states
])

# MBU - Middle Belt Union
# Regionalist party for minorities between north and south. Strong on traditional
# authority, infrastructure, healthcare. Pro-restructuring, anti-northern hegemony.
MBU_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular
    +2.5,  #  1  fiscal: autonomy
    +0.0,  #  2  chinese: neutral
    -1.5,  #  3  bic: mildly anti-BIC
    +3.5,  #  4  ethnic_quotas: affirmative action
    +1.0,  #  5  fertility: mildly pro-natalist
    -3.0,  #  6  constitutional: parliamentary
    +3.0,  #  7  resource: local control
    +2.5,  #  8  housing: interventionist
    -1.5,  #  9  education: mildly localist
    +1.5,  # 10  labor: mildly pro-labor
    -1.5,  # 11  military: mildly civilian
    +0.5,  # 12  immigration: centrist
    -2.5,  # 13  language: vernacular
    +1.0,  # 14  womens_rights: mildly progressive
    +4.0,  # 15  trad_authority: strongest integration
    +4.5,  # 16  infrastructure: near-maximum universal
    -2.0,  # 17  land_tenure: customary
    +2.5,  # 18  taxation: redistribution
    +3.0,  # 19  agriculture: protectionist
    +0.5,  # 20  bio_enhancement: centrist
    +0.0,  # 21  trade: neutral
    +2.5,  # 22  environment: regulatory
    +3.0,  # 23  media: press freedom
    +3.5,  # 24  healthcare: universal
    -2.5,  # 25  pada_status: anti-Pada
    +2.0,  # 26  energy: green
    -5.0,  # 27  az_restructuring: maximum restructure
])

# Validation
for name, pos in [("SDP", SDP_POSITIONS), ("APC", APC_POSITIONS),
                   ("LP", LP_POSITIONS), ("NIF", NIF_POSITIONS),
                   ("SCA", SCA_POSITIONS), ("MBU", MBU_POSITIONS)]:
    assert pos.shape == (N_ISSUES,), f"{name} has wrong shape"
    assert np.all(np.abs(pos) <= 5.0), f"{name} has out-of-range positions"

PARTIES = [
    Party(
        name="SDP",
        positions=SDP_POSITIONS,
        valence=0.3,
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=-0.2,
        demographic_coefficients={
            "education": {"Tertiary": 0.3, "Secondary": 0.2},
            "livelihood": {"Formal private": 0.3, "Public sector": 0.2},
            "income": {"Middle 40%": 0.2, "Top 20%": 0.2},
            "setting": {"Urban": 0.2, "Peri-urban": 0.1},
            "gender": {"Female": 0.15},
        },
        regional_strongholds={
            1: +0.5, 2: +0.8, 3: +0.6, 4: +0.3, 5: +0.2,
        },
    ),
    Party(
        name="APC",
        positions=APC_POSITIONS,
        valence=0.3,
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.2,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.3, "Public sector": 0.2},
            "education": {"Below secondary": 0.2, "Secondary": 0.1},
            "age_cohort": {"35-49": 0.15, "50+": 0.2},
            "income": {"Bottom 40%": 0.1, "Middle 40%": 0.1},
            "setting": {"Rural": 0.2},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            6: +0.6, 7: +0.4, 8: +1.0, 2: +0.3,
        },
    ),
    Party(
        name="LP",
        positions=LP_POSITIONS,
        valence=0.1,
        leader_ethnicity="Ijaw",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.7,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.3, "Smallholder": 0.1},
            "income": {"Bottom 40%": 0.3, "Middle 40%": 0.1},
            "education": {"Below secondary": 0.1, "Secondary": 0.1},
            "age_cohort": {"25-34": 0.1},
            "setting": {"Urban": 0.15, "Peri-urban": 0.1},
        },
        regional_strongholds={
            1: +0.3, 4: +0.4, 3: +0.2,
        },
    ),
    Party(
        name="NIF",
        positions=NIF_POSITIONS,
        valence=0.05,
        leader_ethnicity="Kanuri",
        religious_alignment="Al-Shahid",
        economic_positioning=0.5,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.3},
            "education": {"Below secondary": 0.3},
            "gender": {"Male": 0.3},
            "setting": {"Rural": 0.2},
        },
        regional_strongholds={
            7: +1.2, 8: +0.3,
        },
    ),
    Party(
        name="SCA",
        positions=SCA_POSITIONS,
        valence=0.15,
        leader_ethnicity="Igbo",
        religious_alignment="Pentecostal",
        economic_positioning=-0.5,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.4, "Formal private": 0.3},
            "income": {"Top 20%": 0.3, "Middle 40%": 0.1},
            "education": {"Tertiary": 0.2, "Secondary": 0.1},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            5: +1.0, 4: +0.5, 1: +0.2,
        },
    ),
    Party(
        name="MBU",
        positions=MBU_POSITIONS,
        valence=0.15,
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
        economic_positioning=0.3,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.3, "Trade/informal": 0.2},
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.1},
            "education": {"Secondary": 0.1},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
        },
        regional_strongholds={
            5: +0.3, 6: +0.5, 7: +0.2, 3: +0.2,
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LAGOS-2058: Polarised 6-Party Scenario")
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
    print("LAGOS-2058: POLARISED 6-PARTY SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("  SDP (south), APC (north), LP (labour), NIF (Islamist),")
    print("  SCA (SE/SS autonomist), MBU (Middle Belt)")
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

    if "Turnout" in lga_with_votes.columns:
        t = lga_with_votes["Turnout"].values
        print(f"\nTURNOUT DISTRIBUTION:")
        print(f"  Mean: {t.mean():.1%}  Median: {np.median(t):.1%}  "
              f"Min: {t.min():.1%}  Max: {t.max():.1%}")


if __name__ == "__main__":
    main()
