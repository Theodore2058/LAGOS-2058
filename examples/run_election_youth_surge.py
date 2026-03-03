"""
Youth Surge Scenario: What if a disruptive youth-led movement entered the race?

Starts with 8 established parties from the 14-party system (dropping the
smaller ones), then adds 2 new youth-focused parties:

  GNM - Generation Now Movement: tech-savvy, pan-ethnic youth party
        demanding radical modernisation, bio-enhancement access, and
        an end to gerontocracy. Anti-traditional authority, anti-sharia,
        pro-green, pro-trade openness. The party of smartphone-wielding
        20-somethings who want 2058 to actually look like 2058.

  PJP - People's Justice Party: radical populist youth party with
        leftist economics. Pro-worker, pro-redistribution, anti-elite,
        anti-corruption. Appeals to unemployed youth, gig workers, and
        slum dwellers. The angry counterpart to GNM's optimism.

Tests whether a youth-surge scenario can crack the ethnic/religious
voting blocs that dominate the baseline model.
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

# Import positions from the base 14-party scenario
from run_election import (
    NRP_POSITIONS, CND_POSITIONS, IPA_POSITIONS, NDC_POSITIONS,
    NHA_POSITIONS, UJP_POSITIONS, MBPP_POSITIONS, SNM_POSITIONS,
)

# ---------------------------------------------------------------------------
# New youth party definitions
# ---------------------------------------------------------------------------

# GNM - Generation Now Movement
# Pan-ethnic youth modernisation party. Anti-gerontocracy, anti-trad-authority,
# pro-technology, pro-bio-enhancement, pro-green energy. Aggressively secular,
# pro-meritocracy, pro-trade openness. Wants Nigeria to leapfrog into the
# future rather than fight over the past. Appeals to urban educated youth
# across all ethnic lines. The party of people who think all the other
# parties are run by dinosaurs.
GNM_POSITIONS = np.array([
    -4.0,  #  0  sharia: aggressively secular
    -1.0,  #  1  fiscal: mildly centralist (efficient national systems)
    +3.0,  #  2  chinese: pro-WAFTA (tech transfer)
    -3.0,  #  3  bic: anti-BIC (outdated institution)
    -4.0,  #  4  ethnic_quotas: strongly meritocratic
    -3.0,  #  5  fertility: population control (planet first)
    -3.5,  #  6  constitutional: parliamentary (checks on power)
    -0.5,  #  7  resource: centrist
    +1.0,  #  8  housing: mild intervention
    +4.0,  #  9  education: strongest centralist (national STEM push)
    -1.5,  # 10  labor: mildly pro-capital (tech startups)
    -4.0,  # 11  military: strong civilian control
    -2.0,  # 12  immigration: open borders (cosmopolitan)
    +3.0,  # 13  language: English (global competitiveness)
    +4.5,  # 14  womens_rights: most progressive
    -5.0,  # 15  trad_authority: total marginalization
    -1.0,  # 16  infrastructure: targeted (smart cities)
    +4.0,  # 17  land_tenure: strong formalization (digital cadastre)
    +0.0,  # 18  taxation: neutral (startup-friendly but fund services)
    -2.0,  # 19  agriculture: free market (agritech)
    +5.0,  # 20  bio_enhancement: maximum access (core identity)
    +4.0,  # 21  trade: strongly open
    +4.0,  # 22  environment: strong regulation (climate generation)
    +3.5,  # 23  media: press freedom (internet freedom)
    +2.0,  # 24  healthcare: universal (tech-enabled)
    +2.0,  # 25  pada_status: pro-Pada (cosmopolitan identity)
    +4.5,  # 26  energy: strongest green (defining issue)
    +3.0,  # 27  az_restructuring: keep AZs (modern admin units)
])

# PJP - People's Justice Party
# Radical populist youth party with leftist economics. Pro-worker, pro-
# redistribution, anti-elite, anti-corruption. Combines anger at the
# establishment with demands for jobs, housing, and healthcare. More
# ethnically diverse base than GNM — draws from unemployed youth, gig
# workers, and market stall assistants across ethnic lines. Less tech-
# optimist, more focused on bread-and-butter issues. The party of
# people who can't afford the future GNM is selling.
PJP_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular but less aggressive
    -2.0,  #  1  fiscal: centralist (redistribute nationally)
    -0.5,  #  2  chinese: centrist (pragmatic)
    -2.5,  #  3  bic: anti-BIC (elite institution)
    +1.0,  #  4  ethnic_quotas: mildly pro (bottom-up solidarity)
    -1.0,  #  5  fertility: mildly control
    -2.0,  #  6  constitutional: parliamentary
    +2.0,  #  7  resource: local control (community benefit)
    +5.0,  #  8  housing: maximum intervention (housing is a right)
    +1.0,  #  9  education: mildly centralist
    +5.0,  # 10  labor: maximum pro-labor (gig worker rights)
    -3.0,  # 11  military: civilian control
    +0.5,  # 12  immigration: centrist
    -1.0,  # 13  language: mildly vernacular (working class)
    +2.5,  # 14  womens_rights: progressive
    -3.5,  # 15  trad_authority: marginalize (chiefs exploit youth)
    +4.0,  # 16  infrastructure: universal (development now)
    -1.0,  # 17  land_tenure: mildly customary (protect poor)
    +5.0,  # 18  taxation: maximum redistribution (tax the rich)
    +2.5,  # 19  agriculture: protectionist (food sovereignty)
    +1.0,  # 20  bio_enhancement: mildly pro
    -1.5,  # 21  trade: mildly autarkic (protect local jobs)
    +2.0,  # 22  environment: regulation
    +2.5,  # 23  media: press freedom
    +5.0,  # 24  healthcare: maximum universal
    -1.5,  # 25  pada_status: mildly anti-Pada (elitism)
    +2.0,  # 26  energy: green
    -1.0,  # 27  az_restructuring: mild restructure
])

# Validate new positions
for name, pos in [("GNM", GNM_POSITIONS), ("PJP", PJP_POSITIONS)]:
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
    # --- 8 established parties (from 14-party system) ---
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
        valence=0.1,
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.3,
        demographic_coefficients={
            "education": {"Tertiary": 0.3},
            "livelihood": {"Public sector": 0.3},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={1: +0.3, 2: +0.6, 3: +0.5, 4: +0.1, 6: +0.1},
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
        name="NHA",
        positions=NHA_POSITIONS,
        valence=0.15,
        leader_ethnicity="Naijin",
        religious_alignment="Secular",
        economic_positioning=-0.5,
        demographic_coefficients={
            "education": {"Tertiary": 0.4},
            "livelihood": {"Formal private": 0.3},
            "income": {"Top 20%": 0.3},
            "age_cohort": {"25-34": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={1: +0.5, 6: +0.3, 3: +0.1, 4: +0.1},
    ),
    Party(
        name="UJP",
        positions=UJP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Kanuri",
        religious_alignment="Al-Shahid",
        economic_positioning=0.7,
        demographic_coefficients={
            "income": {"Bottom 40%": 0.3},
            "education": {"Below secondary": 0.2},
            "age_cohort": {"18-24": 0.3, "25-34": 0.1},
            "gender": {"Male": 0.2},
            "livelihood": {"Smallholder": 0.2, "Trade/informal": 0.1},
            "setting": {"Rural": 0.1, "Peri-urban": 0.1},
        },
        regional_strongholds={7: +1.0, 8: +0.4, 6: +0.15},
    ),
    Party(
        name="MBPP",
        positions=MBPP_POSITIONS,
        valence=0.05,
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
        economic_positioning=0.5,
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

    # --- 2 new youth-led parties ---
    Party(
        name="GNM",  # Generation Now Movement
        positions=GNM_POSITIONS,
        valence=0.25,  # high valence: viral social media presence, youth energy
        leader_ethnicity="Pada",  # mixed-heritage Lagos-born leader
        religious_alignment="Secular",
        economic_positioning=-0.3,
        demographic_coefficients={
            "age_cohort": {"18-24": 0.8, "25-34": 0.5},  # massive youth appeal
            "education": {"Tertiary": 0.5, "Secondary": 0.2},
            "livelihood": {"Formal private": 0.3, "Unemployed/student": 0.4},
            "income": {"Top 20%": 0.2, "Middle 40%": 0.1},
            "setting": {"Urban": 0.4},
            "gender": {"Female": 0.2},
        },
        regional_strongholds={
            1: +0.8,  # Lagos: urban youth epicentre
            6: +0.3,  # Central: FCT/Kano urban youth
            3: +0.2,  # Confluence: university towns
            4: +0.2,  # Littoral: Port Harcourt urban youth
        },
    ),
    Party(
        name="PJP",  # People's Justice Party
        positions=PJP_POSITIONS,
        valence=0.1,  # grassroots but less organised than GNM
        leader_ethnicity="Yoruba",  # Lagos market trader background
        religious_alignment="Secular",
        economic_positioning=0.9,  # most redistributive in the field
        demographic_coefficients={
            "age_cohort": {"18-24": 0.6, "25-34": 0.4, "35-49": 0.1},
            "livelihood": {"Trade/informal": 0.5, "Unemployed/student": 0.5,
                           "Smallholder": 0.2},
            "income": {"Bottom 40%": 0.5, "Middle 40%": 0.2},
            "education": {"Below secondary": 0.2, "Secondary": 0.2},
            "setting": {"Urban": 0.2, "Peri-urban": 0.2},
        },
        regional_strongholds={
            1: +0.5,  # Lagos: slum and market workers
            4: +0.3,  # Littoral: industrial workers
            6: +0.2,  # Central: Kano informal economy
            2: +0.1,  # Niger Zone: urban poor
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LAGOS-2058: Youth Surge Scenario (10 parties)")
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
    print("LAGOS-2058: YOUTH SURGE SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("  8 established + 2 youth parties (GNM, PJP)")
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
        tag = ""
        if p in ("GNM", "PJP"):
            tag = "  <-- YOUTH"
        print(f"  {p:10s}  {votes:12,}  {share:6.1%}{tag}")

    # MC uncertainty
    print("\nMC NATIONAL SHARE UNCERTAINTY (mean [P5 - P95]):")
    ns = mc["national_share_stats"].sort_values("Mean Share", ascending=False)
    for _, row in ns.iterrows():
        if row["Mean Share"] >= 0.005:
            tag = ""
            if row["Party"] in ("GNM", "PJP"):
                tag = "  <-- YOUTH"
            print(f"  {row['Party']:10s}  {row['Mean Share']:6.1%}  "
                  f"[{row['P5 Share']:5.1%} - {row['P95 Share']:5.1%}]{tag}")

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

    # Youth party combined share
    youth_share = sum(
        summary["national_shares"].get(p, 0) for p in ("GNM", "PJP")
    )
    print(f"\nCOMBINED YOUTH PARTY SHARE: {youth_share:.1%}")


if __name__ == "__main__":
    main()
