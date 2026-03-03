"""
WAFTA Crisis Scenario: What if the China-Nigeria trade relationship dominates?

A scenario where the West African Free Trade Agreement (WAFTA) with China
has become THE polarising issue. Parties re-align around pro-WAFTA vs
anti-WAFTA positions, splitting traditional ethnic blocs.

7 parties:
  PTN - Progress Through WAFTA (strongest pro-WAFTA, Naijin-led tech elite)
  NRP - Nigerian Renaissance Party (moderate pro-WAFTA, existing party)
  CND - Congress for Nigerian Democracy (anti-WAFTA reformist)
  NDC - Northern Democratic Congress (mildly anti-WAFTA northern establishment)
  SNM - Sovereign Nigeria Movement (fiercest anti-WAFTA, economic nationalist)
  IPA - Igbo Progressive Alliance (split: pro-trade but anti-Chinese imports)
  NLA - National Labour Alliance (anti-WAFTA workers' party)

Tests how a single dominant issue can reshape coalitions.
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

# Import existing positions for parties that carry over
from run_election import (
    NRP_POSITIONS, CND_POSITIONS, IPA_POSITIONS, NDC_POSITIONS,
    SNM_POSITIONS, NHA_POSITIONS,
)

# ---------------------------------------------------------------------------
# New party: PTN - Progress Through WAFTA
# ---------------------------------------------------------------------------
# The maximally pro-WAFTA party. Led by a Naijin tech entrepreneur who
# returned from Shenzhen. Champions full economic integration with China,
# Mandarin education, bio-enhancement access through Chinese labs, and
# green energy tech transfer. Culturally secular, economically globalist.
# The party of people who think Nigeria's future runs through the BRI.

PTN_POSITIONS = np.array([
    -3.0,  #  0  sharia: secular (tech-progressive)
    -2.0,  #  1  fiscal: centralist (efficient national systems for WAFTA)
    +5.0,  #  2  chinese: MAXIMUM WAFTA (defining issue)
    +2.0,  #  3  bic: preserve (institutional stability for trade)
    -3.0,  #  4  ethnic_quotas: meritocratic (global competitiveness)
    -2.5,  #  5  fertility: control (demographic dividend, not burden)
    -2.5,  #  6  constitutional: parliamentary (technocratic governance)
    -1.5,  #  7  resource: mildly federal (strategic resource management)
    +1.5,  #  8  housing: mild intervention (planned cities model)
    +4.0,  #  9  education: centralist (STEM/Mandarin national push)
    -2.0,  # 10  labor: pro-capital (attract Chinese investment)
    -1.0,  # 11  military: mildly civilian (stable for investors)
    -2.5,  # 12  immigration: open borders (talent mobility)
    -0.5,  # 13  language: centrist (multilingual: English + Mandarin)
    +2.0,  # 14  womens_rights: progressive (modern labour force)
    -3.0,  # 15  trad_authority: marginalize (modernize institutions)
    -1.0,  # 16  infrastructure: targeted (smart cities)
    +3.5,  # 17  land_tenure: formalization (attract investment)
    +0.0,  # 18  taxation: neutral (investor-friendly but fund tech)
    -1.5,  # 19  agriculture: free market (agritech via WAFTA)
    +4.0,  # 20  bio_enhancement: strong pro (Chinese biotech access)
    +5.0,  # 21  trade: MAXIMUM openness (WAFTA core)
    +2.0,  # 22  environment: regulation (green tech transfer)
    +1.0,  # 23  media: mild press freedom
    +2.0,  # 24  healthcare: universal (Chinese medical tech)
    +2.0,  # 25  pada_status: pro-Pada (tech-progressive identity)
    +4.0,  # 26  energy: green (Chinese solar/battery tech)
    +2.5,  # 27  az_restructuring: keep AZs (modern admin)
])

# NLA - National Labour Alliance
# Anti-WAFTA workers' party. Formed from the merger of NWF and PLF
# fragments who see Chinese imports as an existential threat to Nigerian
# workers. Pro-worker, pro-redistribution, anti-trade-openness. The
# party of factory workers who lost their jobs to Shenzhen and market
# women undercut by Chinese traders.
NLA_POSITIONS = np.array([
    -1.5,  #  0  sharia: mildly secular
    -1.5,  #  1  fiscal: mildly centralist
    -4.5,  #  2  chinese: near-maximum anti-WAFTA (existential threat)
    -1.5,  #  3  bic: mildly anti
    +1.5,  #  4  ethnic_quotas: mild affirmative action (workers' solidarity)
    -0.5,  #  5  fertility: centrist
    -2.0,  #  6  constitutional: parliamentary
    -0.5,  #  7  resource: centrist
    +4.5,  #  8  housing: strong intervention
    +1.0,  #  9  education: mildly centralist
    +5.0,  # 10  labor: MAXIMUM pro-labor (core identity)
    -2.5,  # 11  military: civilian control
    +2.0,  # 12  immigration: restrictionist (protect jobs)
    -1.5,  # 13  language: mildly vernacular
    +2.0,  # 14  womens_rights: progressive (workers' feminism)
    -2.0,  # 15  trad_authority: marginalize
    +3.5,  # 16  infrastructure: universal (workers need roads)
    -1.5,  # 17  land_tenure: mildly customary (protect poor)
    +4.5,  # 18  taxation: strong redistribution
    +3.0,  # 19  agriculture: protectionist (food sovereignty)
    +1.0,  # 20  bio_enhancement: mildly pro
    -4.0,  # 21  trade: strong autarky (protect Nigerian industry)
    +2.0,  # 22  environment: regulation
    +2.5,  # 23  media: press freedom (workers' media)
    +4.5,  # 24  healthcare: universal
    -2.0,  # 25  pada_status: mildly anti (tech-elite resentment)
    +1.5,  # 26  energy: mild green
    +0.0,  # 27  az_restructuring: neutral
])

# Modified IPA - more ambivalent on WAFTA
# In this scenario IPA is torn: pro-trade in principle but anti-Chinese
# imports that compete with Igbo manufacturers.
IPA_WAFTA_POSITIONS = IPA_POSITIONS.copy()
IPA_WAFTA_POSITIONS[2] = -1.5    # chinese: anti-WAFTA (protect Aba factories)
IPA_WAFTA_POSITIONS[21] = +0.5   # trade: neutral (pro-trade but not with China)

# Modified CND - more explicitly anti-WAFTA
CND_WAFTA_POSITIONS = CND_POSITIONS.copy()
CND_WAFTA_POSITIONS[2] = -4.0    # chinese: strongly anti-WAFTA (democratic values)

# Validate
for name, pos in [
    ("PTN", PTN_POSITIONS), ("NLA", NLA_POSITIONS),
    ("IPA_WAFTA", IPA_WAFTA_POSITIONS), ("CND_WAFTA", CND_WAFTA_POSITIONS),
]:
    assert pos.shape == (N_ISSUES,), f"{name} position shape mismatch"
    assert np.all(np.abs(pos) <= 5.0), f"{name} has out-of-range positions"

# ---------------------------------------------------------------------------
# Administrative Zone reference:
#   AZ 1 = Federal Capital Zone (Lagos)
#   AZ 2 = Niger Zone (Kwara, Niger, Ogun, Oyo)
#   AZ 3 = Confluence Zone (Edo, Ekiti, Kogi, Ondo, Osun)
#   AZ 4 = Littoral Zone (Akwa Ibom, Bayelsa, Cross River, Delta, Rivers)
#   AZ 5 = Eastern Zone (Abia, Anambra, Benue, Ebonyi, Enugu, Imo)
#   AZ 6 = Central Zone (FCT, Kano, Nasarawa, Plateau)
#   AZ 7 = Chad Zone (Adamawa, Bauchi, Borno, Gombe, Jigawa, Taraba, Yobe)
#   AZ 8 = Savanna Zone (Kaduna, Katsina, Kebbi, Sokoto, Zamfara)
# ---------------------------------------------------------------------------

PARTIES = [
    Party(
        name="PTN",  # Progress Through WAFTA
        positions=PTN_POSITIONS,
        valence=0.2,  # strong tech branding
        leader_ethnicity="Naijin",
        religious_alignment="Secular",
        economic_positioning=-0.5,
        demographic_coefficients={
            "education": {"Tertiary": 0.5, "Secondary": 0.1},
            "livelihood": {"Formal private": 0.5},
            "income": {"Top 20%": 0.4, "Middle 40%": 0.1},
            "age_cohort": {"25-34": 0.3, "18-24": 0.2},
            "setting": {"Urban": 0.4},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.8,  # Lagos: tech hub, WAFTA beneficiary
            6: +0.3,  # Central: FCT tech corridors
            3: +0.1,  # Confluence: university towns
        },
    ),
    Party(
        name="NRP",
        positions=NRP_POSITIONS,
        valence=0.15,
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
        positions=CND_WAFTA_POSITIONS,
        valence=0.15,  # boosted: anti-WAFTA + democratic values = broad appeal
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.3,
        demographic_coefficients={
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "livelihood": {"Public sector": 0.3},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={1: +0.3, 2: +0.8, 3: +0.5, 4: +0.2},
    ),
    Party(
        name="NDC",
        positions=NDC_POSITIONS,
        valence=0.1,
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
        name="SNM",
        positions=SNM_POSITIONS,
        valence=0.1,  # boosted: anti-WAFTA resonates
        leader_ethnicity="Yoruba",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.4,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.4, "Smallholder": 0.2},
            "education": {"Secondary": 0.2},
            "age_cohort": {"35-49": 0.2, "50+": 0.1},
            "setting": {"Peri-urban": 0.1},
            "gender": {"Male": 0.2},
        },
        regional_strongholds={
            2: +0.5, 3: +0.4, 8: +0.3, 6: +0.2, 1: +0.1,
        },
    ),
    Party(
        name="IPA",
        positions=IPA_WAFTA_POSITIONS,
        valence=0.0,
        leader_ethnicity="Igbo",
        religious_alignment="Pentecostal",
        economic_positioning=-0.4,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.5, "Formal private": 0.3},
            "income": {"Top 20%": 0.3},
            "age_cohort": {"25-34": 0.1},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={5: +1.2, 1: +0.2, 4: +0.15, 3: +0.1},
    ),
    Party(
        name="NLA",  # National Labour Alliance
        positions=NLA_POSITIONS,
        valence=0.1,
        leader_ethnicity="Ibibio",
        religious_alignment="Secular",
        economic_positioning=0.9,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.5, "Formal private": 0.2,
                           "Unemployed/student": 0.3},
            "income": {"Bottom 40%": 0.4, "Middle 40%": 0.1},
            "education": {"Below secondary": 0.2, "Secondary": 0.1},
            "age_cohort": {"18-24": 0.2, "25-34": 0.2, "35-49": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.5,  # Lagos: factory/gig workers
            4: +0.3,  # Littoral: PH industrial workers
            6: +0.3,  # Central: Kano industrial zone
            5: +0.2,  # Eastern: Cross River/Akwa Ibom industry
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LAGOS-2058: WAFTA Crisis Scenario (7 parties)")
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
    print("LAGOS-2058: WAFTA CRISIS SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("  Pro-WAFTA: PTN, NRP")
    print("  Anti-WAFTA: CND, SNM, NLA, IPA")
    print("  Northern establishment: NDC")
    print("=" * 70)

    print(f"\nNational Turnout: {summary['national_turnout']:.1%}")
    print(f"Total Votes Cast: {summary['total_votes']:,}")
    print(f"Effective Number of Parties (ENP): {summary['enp']:.2f}")

    print("\nNATIONAL RESULTS (base run):")
    print(f"  {'Party':10s}  {'Votes':>12s}  {'Share':>7s}  {'WAFTA':>10s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*7}  {'-'*10}")
    pro_wafta = {"PTN", "NRP"}
    anti_wafta = {"CND", "SNM", "NLA", "IPA"}
    sorted_parties = sorted(summary["national_shares"].items(), key=lambda x: -x[1])
    pro_total = 0.0
    anti_total = 0.0
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        if p in pro_wafta:
            tag = "PRO"
            pro_total += share
        elif p in anti_wafta:
            tag = "ANTI"
            anti_total += share
        else:
            tag = "NEUTRAL"
        print(f"  {p:10s}  {votes:12,}  {share:6.1%}  {tag:>10s}")

    print(f"\n  WAFTA BALANCE:")
    print(f"    Pro-WAFTA bloc:  {pro_total:6.1%}")
    print(f"    Anti-WAFTA bloc: {anti_total:6.1%}")
    ndc_share = summary["national_shares"].get("NDC", 0)
    print(f"    Neutral (NDC):   {ndc_share:6.1%}")

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
