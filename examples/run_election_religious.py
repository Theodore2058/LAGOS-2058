"""
Religious Cleavage Scenario: What if parties align along religious lines?

A scenario exploring the Sharia-secular fault line as the dominant cleavage.
6 parties defined by religious identity rather than ethnicity:

  ISP - Islamic Solidarity Party (pan-Muslim, pro-Sharia)
  CDF - Christian Democratic Front (pan-Christian, anti-Sharia)
  SUF - Sufi People's Movement (moderate Muslim, Tijaniyya-influenced)
  PEN - Pentecostal Prosperity Alliance (prosperity gospel economics)
  SEC - Secular Nigeria Party (aggressively secular, anti-religious-politics)
  TRD - Traditionalist Renewal Party (traditionalist, anti-Abrahamic)

Tests whether religious identity can override ethnic solidarity in the model.
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

# ISP - Islamic Solidarity Party
# Pan-Muslim party built around Sharia jurisdiction, pro-natalism, and
# Islamic welfare. Appeals across ethnic lines to devout Muslims. Led by
# a Hausa cleric from Kano. Anti-secular, anti-bio-enhancement, pro-
# traditional authority (Islamic emirs). The party of the mosque.
ISP_POSITIONS = np.array([
    +4.5,  #  0  sharia: near-maximum
    +2.5,  #  1  fiscal: autonomy (state-level Sharia)
    -1.0,  #  2  chinese: mildly anti
    -4.0,  #  3  bic: abolish (Western institution)
    +3.5,  #  4  ethnic_quotas: affirmative action
    +4.0,  #  5  fertility: strongly pro-natalist
    +3.0,  #  6  constitutional: presidential
    +1.5,  #  7  resource: mild local control
    +2.0,  #  8  housing: interventionist (Islamic welfare)
    -3.0,  #  9  education: localist/Islamic
    +1.0,  # 10  labor: mildly pro-labor
    +1.5,  # 11  military: mild guardianship
    +3.0,  # 12  immigration: restrictionist
    -3.0,  # 13  language: vernacular/Arabic
    -3.5,  # 14  womens_rights: conservative
    +3.5,  # 15  trad_authority: integration (emirate)
    +3.0,  # 16  infrastructure: universal
    -2.0,  # 17  land_tenure: customary (Islamic tenure)
    +2.0,  # 18  taxation: redistribution (zakat model)
    +3.0,  # 19  agriculture: protectionist
    -3.0,  # 20  bio_enhancement: prohibition
    -1.0,  # 21  trade: mildly autarkic
    -1.5,  # 22  environment: growth first
    -0.5,  # 23  media: centrist
    +3.0,  # 24  healthcare: universal (Islamic welfare)
    -4.0,  # 25  pada_status: anti-Pada (theological objection)
    -1.5,  # 26  energy: fossil (development)
    -1.5,  # 27  az_restructuring: mild restructure
])

# CDF - Christian Democratic Front
# Pan-Christian party. Anti-Sharia, pro-education, moderate on economics.
# Draws from both Pentecostal and mainline Protestant traditions. Led by
# an Igbo Catholic from Enugu. Pro-women's rights within Christian moral
# framework. The party of Sunday school and CAN meetings.
CDF_POSITIONS = np.array([
    -4.5,  #  0  sharia: maximum anti-Sharia
    +1.5,  #  1  fiscal: mild autonomy
    -1.5,  #  2  chinese: mildly anti
    +1.0,  #  3  bic: mildly preserve
    +0.5,  #  4  ethnic_quotas: centrist
    +2.0,  #  5  fertility: pro-natalist (Catholic + Pentecostal)
    +0.5,  #  6  constitutional: centrist
    +1.0,  #  7  resource: mild local control
    +1.5,  #  8  housing: mild intervention
    +1.0,  #  9  education: mildly centralist
    +0.5,  # 10  labor: centrist
    -1.0,  # 11  military: mildly civilian
    +1.0,  # 12  immigration: mildly restrictionist
    +2.0,  # 13  language: English
    -0.5,  # 14  womens_rights: centrist (Christian conservative but not extreme)
    +1.0,  # 15  trad_authority: mild integration
    +2.0,  # 16  infrastructure: universal
    +0.5,  # 17  land_tenure: mild formalization
    +0.5,  # 18  taxation: centrist
    +1.0,  # 19  agriculture: mildly protectionist
    -2.0,  # 20  bio_enhancement: against (playing God)
    +1.0,  # 21  trade: mildly open
    +1.0,  # 22  environment: mild regulation
    +2.0,  # 23  media: press freedom
    +2.5,  # 24  healthcare: universal
    -0.5,  # 25  pada_status: centrist
    +1.0,  # 26  energy: mild green
    -1.0,  # 27  az_restructuring: mild restructure
])

# SUF - Sufi People's Movement
# Moderate Muslim party rooted in Tijaniyya and Qadiriyya Sufi orders.
# Less rigid on Sharia than ISP, more tolerant, pro-trade. Led by a
# Yoruba Tijaniyya scholar from Ilorin. Represents the "Islam of the
# marketplace" — pragmatic, commercially oriented, socially moderate.
SUF_POSITIONS = np.array([
    +2.0,  #  0  sharia: moderate pro
    +1.5,  #  1  fiscal: mild autonomy
    +0.5,  #  2  chinese: centrist
    -1.5,  #  3  bic: mildly anti
    +1.0,  #  4  ethnic_quotas: mildly pro
    +1.5,  #  5  fertility: mildly pro-natalist
    +1.0,  #  6  constitutional: mildly presidential
    +0.5,  #  7  resource: centrist
    +1.0,  #  8  housing: mild intervention
    +0.5,  #  9  education: centrist
    +0.5,  # 10  labor: centrist
    -0.5,  # 11  military: mildly civilian
    +0.5,  # 12  immigration: centrist
    -1.0,  # 13  language: mildly vernacular
    +0.5,  # 14  womens_rights: mildly progressive (Sufi tolerance)
    +2.0,  # 15  trad_authority: integration (Sufi hierarchy)
    +1.5,  # 16  infrastructure: mildly universal
    -0.5,  # 17  land_tenure: centrist
    +0.5,  # 18  taxation: centrist
    +1.0,  # 19  agriculture: mildly protectionist
    -0.5,  # 20  bio_enhancement: mildly against
    +2.0,  # 21  trade: open (Sufi trade networks)
    +0.5,  # 22  environment: centrist
    +1.5,  # 23  media: mildly free press
    +1.5,  # 24  healthcare: mildly universal
    -1.0,  # 25  pada_status: mildly anti-Pada
    +0.5,  # 26  energy: centrist
    +0.0,  # 27  az_restructuring: neutral
])

# PEN - Pentecostal Prosperity Alliance
# Prosperity gospel economics meets conservative Christian social values.
# Pro-market, anti-redistribution, anti-bio-enhancement ("don't play God"),
# but pro-women's economic empowerment. Led by an Edo megachurch pastor.
# Anti-Sharia, anti-traditional authority (chiefs are "pagan"). The party
# of seed-faith and private jets.
PEN_POSITIONS = np.array([
    -4.0,  #  0  sharia: strongly anti-Sharia
    -1.0,  #  1  fiscal: mildly centralist
    -1.5,  #  2  chinese: mildly anti
    -0.5,  #  3  bic: centrist
    -2.0,  #  4  ethnic_quotas: meritocratic (prosperity = blessing)
    +3.0,  #  5  fertility: pro-natalist (be fruitful and multiply)
    -1.0,  #  6  constitutional: mildly parliamentary
    -0.5,  #  7  resource: centrist
    -2.0,  #  8  housing: market (God provides)
    +2.0,  #  9  education: centralist (faith-based + quality)
    -3.0,  # 10  labor: pro-capital (prosperity gospel)
    -2.0,  # 11  military: civilian control
    +0.5,  # 12  immigration: centrist
    +2.5,  # 13  language: English (international church language)
    +1.0,  # 14  womens_rights: mildly progressive (women's economic role)
    -3.5,  # 15  trad_authority: marginalize (anti-pagan chiefs)
    -0.5,  # 16  infrastructure: centrist
    +2.0,  # 17  land_tenure: formalization (property rights = blessing)
    -3.0,  # 18  taxation: low tax (prosperity gospel)
    -1.5,  # 19  agriculture: free market
    -3.5,  # 20  bio_enhancement: prohibition ("playing God")
    +1.5,  # 21  trade: mildly open
    -0.5,  # 22  environment: centrist
    +1.0,  # 23  media: mild press freedom (Pentecostal media empires)
    -1.0,  # 24  healthcare: mildly market (faith healing tradition)
    -1.5,  # 25  pada_status: anti-Pada (theological)
    +0.5,  # 26  energy: centrist
    +0.5,  # 27  az_restructuring: centrist
])

# SEC - Secular Nigeria Party
# Aggressively secular party that wants religion out of politics entirely.
# Pro-meritocracy, pro-science, pro-bio-enhancement, pro-green energy.
# Led by a Pada academic from Lagos. Appeals to educated cosmopolitans
# across religious lines. The party of people who think both the mosque
# and the megachurch need to stay out of the National Assembly.
SEC_POSITIONS = np.array([
    -5.0,  #  0  sharia: MAXIMUM secular
    -1.5,  #  1  fiscal: mildly centralist
    +2.0,  #  2  chinese: moderate WAFTA (pragmatic)
    +2.5,  #  3  bic: preserve (secular institution)
    -4.5,  #  4  ethnic_quotas: strongly meritocratic
    -3.0,  #  5  fertility: population control (science-based)
    -3.0,  #  6  constitutional: parliamentary
    -1.0,  #  7  resource: mildly federal
    +0.5,  #  8  housing: centrist
    +4.0,  #  9  education: strongest centralist (science-based)
    -1.0,  # 10  labor: mildly pro-capital
    -3.5,  # 11  military: civilian control
    -1.5,  # 12  immigration: mildly open
    +3.5,  # 13  language: English (science/global language)
    +4.0,  # 14  womens_rights: progressive
    -4.5,  # 15  trad_authority: marginalize (modernize!)
    -1.0,  # 16  infrastructure: targeted (smart cities)
    +3.5,  # 17  land_tenure: formalization (rational governance)
    +0.0,  # 18  taxation: neutral
    -1.5,  # 19  agriculture: free market (agritech)
    +4.5,  # 20  bio_enhancement: strong pro-access (science!)
    +3.0,  # 21  trade: open
    +3.5,  # 22  environment: strong regulation (science-based)
    +3.0,  # 23  media: press freedom
    +1.5,  # 24  healthcare: mildly universal
    +4.0,  # 25  pada_status: pro-Pada (identity freedom)
    +4.0,  # 26  energy: green (science-based)
    +2.5,  # 27  az_restructuring: keep AZs (modern admin)
])

# TRD - Traditionalist Renewal Party
# African traditionalist party seeking to restore pre-Abrahamic spiritual
# and governance systems. Anti-Sharia, anti-Pentecostal, strongly pro-
# traditional authority. Led by a Yoruba Ifa priest from Osun. Appeals to
# traditionalist communities, rural elders, and cultural revivalists.
# The party of the babalawo and the ancestral shrines.
TRD_POSITIONS = np.array([
    -3.0,  #  0  sharia: anti-Sharia (anti-Abrahamic)
    +3.0,  #  1  fiscal: strong autonomy (local tradition)
    -2.0,  #  2  chinese: anti-foreign influence
    -3.0,  #  3  bic: anti-BIC (colonial institution)
    +3.0,  #  4  ethnic_quotas: affirmative action
    +2.0,  #  5  fertility: pro-natalist (ancestral continuity)
    -2.0,  #  6  constitutional: parliamentary (council of elders)
    +3.0,  #  7  resource: strong local control
    +1.5,  #  8  housing: mild intervention
    -3.5,  #  9  education: localist (traditional knowledge)
    +1.0,  # 10  labor: mildly pro-labor
    -1.5,  # 11  military: mildly civilian
    +2.0,  # 12  immigration: restrictionist (protect culture)
    -4.0,  # 13  language: vernacular (indigenous languages)
    -1.0,  # 14  womens_rights: mildly conservative
    +5.0,  # 15  trad_authority: MAXIMUM integration
    +2.5,  # 16  infrastructure: universal
    -4.0,  # 17  land_tenure: customary (ancestral land)
    +1.0,  # 18  taxation: mild redistribution
    +3.5,  # 19  agriculture: protectionist
    -2.0,  # 20  bio_enhancement: against (unnatural)
    -2.5,  # 21  trade: autarkic
    +3.0,  # 22  environment: regulation (sacred groves)
    +0.5,  # 23  media: centrist
    +2.0,  # 24  healthcare: universal (traditional + modern)
    -2.0,  # 25  pada_status: anti-Pada
    +1.0,  # 26  energy: mild green
    -3.5,  # 27  az_restructuring: restructure (traditional territories)
])

# Validate
for name, pos in [
    ("ISP", ISP_POSITIONS), ("CDF", CDF_POSITIONS),
    ("SUF", SUF_POSITIONS), ("PEN", PEN_POSITIONS),
    ("SEC", SEC_POSITIONS), ("TRD", TRD_POSITIONS),
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
        name="ISP",
        positions=ISP_POSITIONS,
        valence=0.2,  # mosque networks
        leader_ethnicity="Hausa",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.3,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.3, "Public sector": 0.2},
            "education": {"Below secondary": 0.2},
            "age_cohort": {"35-49": 0.2, "50+": 0.3},
            "gender": {"Male": 0.3},
            "income": {"Bottom 40%": 0.2},
            "setting": {"Rural": 0.2},
        },
        regional_strongholds={
            8: +1.0,  # Savanna: Muslim heartland
            7: +0.8,  # Chad: strong Muslim presence
            6: +0.7,  # Central: Kano Muslim community
            2: +0.2,  # Niger Zone: Kwara/Niger Muslims
        },
    ),
    Party(
        name="CDF",
        positions=CDF_POSITIONS,
        valence=0.15,  # CAN networks
        leader_ethnicity="Igbo",
        religious_alignment="Catholic",
        economic_positioning=0.1,
        demographic_coefficients={
            "education": {"Secondary": 0.2, "Tertiary": 0.1},
            "livelihood": {"Public sector": 0.2, "Trade/informal": 0.2},
            "gender": {"Female": 0.1},
            "income": {"Middle 40%": 0.1},
        },
        regional_strongholds={
            5: +1.0,  # Eastern: Christian heartland
            3: +0.6,  # Confluence: Christian belt
            4: +0.5,  # Littoral: Christian communities
            6: +0.2,  # Central: Plateau Christians
        },
    ),
    Party(
        name="SUF",
        positions=SUF_POSITIONS,
        valence=0.1,  # Sufi brotherhood networks
        leader_ethnicity="Yoruba",
        religious_alignment="Tijaniyya",
        economic_positioning=0.0,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.3, "Smallholder": 0.1},
            "age_cohort": {"35-49": 0.2, "50+": 0.1},
            "income": {"Middle 40%": 0.2},
            "setting": {"Peri-urban": 0.1},
        },
        regional_strongholds={
            2: +0.8,  # Niger Zone: Yoruba Muslim heartland (Ilorin, Oyo)
            8: +0.3,  # Savanna: Sufi communities
            6: +0.2,  # Central: Kano Tijaniyya
            3: +0.2,  # Confluence: Kwara/Kogi Muslims
        },
    ),
    Party(
        name="PEN",
        positions=PEN_POSITIONS,
        valence=0.15,  # megachurch media empires
        leader_ethnicity="Edo",
        religious_alignment="Pentecostal",
        economic_positioning=-0.4,
        demographic_coefficients={
            "livelihood": {"Formal private": 0.3, "Trade/informal": 0.2},
            "income": {"Top 20%": 0.3, "Middle 40%": 0.2},
            "education": {"Tertiary": 0.2, "Secondary": 0.1},
            "age_cohort": {"25-34": 0.2},
            "gender": {"Female": 0.2},
            "setting": {"Urban": 0.2},
        },
        regional_strongholds={
            3: +0.8,  # Confluence: Pentecostal belt (Edo, Ekiti, Ondo)
            1: +0.5,  # Lagos: megachurch HQ
            5: +0.4,  # Eastern: Igbo Pentecostals
            4: +0.3,  # Littoral: Port Harcourt Pentecostals
        },
    ),
    Party(
        name="SEC",
        positions=SEC_POSITIONS,
        valence=0.15,  # intellectual prestige
        leader_ethnicity="Pada",
        religious_alignment="Secular",
        economic_positioning=-0.3,
        demographic_coefficients={
            "education": {"Tertiary": 0.5},
            "livelihood": {"Formal private": 0.4},
            "income": {"Top 20%": 0.3},
            "age_cohort": {"25-34": 0.3, "18-24": 0.2},
            "setting": {"Urban": 0.4},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +1.0,  # Lagos: secular cosmopolitan hub
            6: +0.2,  # Central: FCT educated professionals
            3: +0.1,  # Confluence: university towns
        },
    ),
    Party(
        name="TRD",
        positions=TRD_POSITIONS,
        valence=0.0,  # niche appeal
        leader_ethnicity="Yoruba",
        religious_alignment="Traditionalist",
        economic_positioning=0.2,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.3, "Trade/informal": 0.1},
            "age_cohort": {"50+": 0.3, "35-49": 0.1},
            "education": {"Below secondary": 0.2},
            "setting": {"Rural": 0.3},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            2: +0.4,  # Niger Zone: Osun/Oyo Ifa tradition
            3: +0.3,  # Confluence: Edo traditionalism
            5: +0.2,  # Eastern: Igbo traditionalism
            7: +0.1,  # Chad: northern traditionalist pockets
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LAGOS-2058: Religious Cleavage Scenario (6 parties)")
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
    print("LAGOS-2058: RELIGIOUS CLEAVAGE SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("  ISP (Islamic), CDF (Christian), SUF (Sufi moderate),")
    print("  PEN (Pentecostal), SEC (Secular), TRD (Traditionalist)")
    print("=" * 70)

    print(f"\nNational Turnout: {summary['national_turnout']:.1%}")
    print(f"Total Votes Cast: {summary['total_votes']:,}")
    print(f"Effective Number of Parties (ENP): {summary['enp']:.2f}")

    print("\nNATIONAL RESULTS (base run):")
    print(f"  {'Party':10s}  {'Votes':>12s}  {'Share':>7s}  {'Religious':>12s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*7}  {'-'*12}")
    labels = {
        "ISP": "Muslim", "CDF": "Christian", "SUF": "Sufi/Mod",
        "PEN": "Pentecostal", "SEC": "Secular", "TRD": "Traditional",
    }
    muslim_total = 0.0
    christian_total = 0.0
    sorted_parties = sorted(summary["national_shares"].items(), key=lambda x: -x[1])
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        label = labels.get(p, "")
        print(f"  {p:10s}  {votes:12,}  {share:6.1%}  {label:>12s}")
        if p in ("ISP", "SUF"):
            muslim_total += share
        elif p in ("CDF", "PEN"):
            christian_total += share

    print(f"\n  RELIGIOUS BLOC BALANCE:")
    print(f"    Muslim bloc (ISP + SUF):       {muslim_total:6.1%}")
    print(f"    Christian bloc (CDF + PEN):     {christian_total:6.1%}")
    sec_share = summary["national_shares"].get("SEC", 0)
    trd_share = summary["national_shares"].get("TRD", 0)
    print(f"    Secular (SEC):                 {sec_share:6.1%}")
    print(f"    Traditionalist (TRD):          {trd_share:6.1%}")

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

    # Turnout
    if "Turnout" in lga_with_votes.columns:
        t = lga_with_votes["Turnout"].values
        print(f"\nTURNOUT DISTRIBUTION:")
        print(f"  Mean: {t.mean():.1%}  Median: {np.median(t):.1%}  "
              f"Min: {t.min():.1%}  Max: {t.max():.1%}")


if __name__ == "__main__":
    main()
