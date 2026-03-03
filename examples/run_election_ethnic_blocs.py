"""
Ethnic Bloc Scenario: What if parties aligned strictly along ethnic lines?

5 parties representing the major ethno-regional blocs:
  HFC - Hausa-Fulani Congress (NW/NE establishment)
  YAP - Yoruba Action Party (SW tradition, new pan-Yoruba identity)
  IPC - Igbo People's Congress (SE/SS commercial networks)
  MBU - Middle Belt Union (minority plateau/benue/nasarawa)
  DPA - Delta People's Alliance (Niger Delta/Littoral minorities)

This is the nightmare scenario for national unity - pure ethnic mobilisation
with minimal cross-cutting appeals. Tests how the engine handles extreme
identity-based voting.
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
# Party definitions - 28-element position vectors
# ---------------------------------------------------------------------------

# HFC - Hausa-Fulani Congress
# The northern establishment party, representing the Hausa-Fulani mainstream.
# Pro-sharia, pro-natalist, pro-ethnic quotas, anti-Pada. Traditional authority
# integration. Economically patronage-based. Suspicious of southern commercial
# interests and Western cultural influence. The party of the Sultanate, the
# emirs, and the farming villages of Katsina.
HFC_POSITIONS = np.array([
    +4.0,  #  0  sharia: full jurisdiction
    +3.0,  #  1  fiscal: strong autonomy for northern states
    -1.0,  #  2  chinese: mild Western lean
    -4.0,  #  3  bic: abolish BIC (Western institution)
    +4.5,  #  4  ethnic_quotas: maximum affirmative action
    +4.0,  #  5  fertility: strongly pro-natalist
    +3.5,  #  6  constitutional: presidential
    +2.5,  #  7  resource: local control
    +1.5,  #  8  housing: mild intervention
    -3.0,  #  9  education: localist/Islamic
    +1.0,  # 10  labor: mildly pro-labor
    +2.0,  # 11  military: guardianship
    +3.5,  # 12  immigration: restrictionist
    -3.0,  # 13  language: vernacular/Hausa
    -3.0,  # 14  womens_rights: conservative
    +4.0,  # 15  trad_authority: strong integration
    +3.0,  # 16  infrastructure: universal
    -2.5,  # 17  land_tenure: customary
    +1.5,  # 18  taxation: mild redistribution
    +3.0,  # 19  agriculture: protectionist
    -2.5,  # 20  bio_enhancement: against
    -1.0,  # 21  trade: mildly autarkic
    -1.5,  # 22  environment: growth first
    +0.5,  # 23  media: centrist
    +2.5,  # 24  healthcare: universal (Islamic welfare tradition)
    -4.5,  # 25  pada_status: strongly anti-Pada
    -2.0,  # 26  energy: fossil
    -2.0,  # 27  az_restructuring: restructure (return to states)
])

# YAP - Yoruba Action Party
# Pan-Yoruba identity party drawing on the AG/UPN tradition. Pro-secular,
# pro-education, pro-press freedom, mildly pro-fiscal autonomy. Combines
# Yoruba cultural pride with modernist aspirations. More economically
# centrist than HFC. Strong on women's rights relative to northern parties.
# The party of Ibadan lawyers, Lagos journalists, and Ogun industrialists.
YAP_POSITIONS = np.array([
    -3.5,  #  0  sharia: strongly secular
    +2.0,  #  1  fiscal: autonomy (Yoruba self-governance tradition)
    -2.0,  #  2  chinese: Western lean
    -2.0,  #  3  bic: anti-BIC (Yoruba cultural institutions instead)
    -1.0,  #  4  ethnic_quotas: mildly meritocratic
    -0.5,  #  5  fertility: neutral
    -2.5,  #  6  constitutional: parliamentary (Yoruba democratic tradition)
    +1.5,  #  7  resource: mild local control
    +1.0,  #  8  housing: mild intervention
    +2.0,  #  9  education: centralist (Awolowo education legacy)
    +0.5,  # 10  labor: mildly pro-labor
    -3.0,  # 11  military: civilian control
    +0.5,  # 12  immigration: centrist
    +2.5,  # 13  language: English (but with Yoruba pride)
    +2.5,  # 14  womens_rights: progressive
    +1.0,  # 15  trad_authority: mild integration (Oba system)
    +1.0,  # 16  infrastructure: mildly universal
    +1.5,  # 17  land_tenure: mild formalization
    +0.5,  # 18  taxation: mild redistribution
    -0.5,  # 19  agriculture: centrist
    +1.0,  # 20  bio_enhancement: mild pro
    +2.0,  # 21  trade: open
    +2.0,  # 22  environment: regulation
    +4.0,  # 23  media: strong press freedom (Yoruba press tradition)
    +1.5,  # 24  healthcare: mildly universal
    +0.5,  # 25  pada_status: mild pro-Pada
    +1.5,  # 26  energy: mild green
    -2.5,  # 27  az_restructuring: restructure (Yoruba want old West Region)
])

# IPC - Igbo People's Congress
# Igbo ethnic vehicle built on commercial networks, Biafra memory, and
# southeastern autonomism. Fiercely pro-fiscal autonomy and meritocratic.
# Pro-capital, pro-trade, anti-quotas. Views federal structure as northern
# domination. Strong entrepreneurial culture drives pro-market positions.
# The party of Onitsha traders, Aba manufacturers, and the diaspora.
IPC_POSITIONS = np.array([
    -3.5,  #  0  sharia: secular
    +4.5,  #  1  fiscal: strongest autonomy (Biafra shadow)
    -2.5,  #  2  chinese: Western pivot
    -1.0,  #  3  bic: mildly anti
    -3.5,  #  4  ethnic_quotas: strongly meritocratic
    +1.0,  #  5  fertility: mildly pro-natalist
    +2.0,  #  6  constitutional: presidential
    +3.5,  #  7  resource: strong local control
    -2.0,  #  8  housing: market
    +2.0,  #  9  education: centralist
    -3.5,  # 10  labor: pro-capital
    -2.0,  # 11  military: civilian control
    +1.0,  # 12  immigration: mildly restrictionist
    +2.0,  # 13  language: English
    +1.5,  # 14  womens_rights: mildly progressive
    -2.0,  # 15  trad_authority: marginalize
    -2.5,  # 16  infrastructure: targeted (invest in SE)
    +3.5,  # 17  land_tenure: formalization
    -3.5,  # 18  taxation: low tax (commercial freedom)
    -2.0,  # 19  agriculture: free market
    +2.5,  # 20  bio_enhancement: pro-access
    +2.5,  # 21  trade: open
    -1.5,  # 22  environment: growth first
    +2.5,  # 23  media: press freedom
    -1.0,  # 24  healthcare: mildly market
    -1.0,  # 25  pada_status: mildly anti-Pada
    -0.5,  # 26  energy: centrist
    -3.5,  # 27  az_restructuring: restructure (SE wants autonomy)
])

# MBU - Middle Belt Union
# Minority ethnic coalition of Tiv, Ngas, Berom, Jukun, Idoma, and other
# plateau/benue peoples. Caught between northern Islamic hegemony and
# southern commercial domination. Strong on traditional authority, fiscal
# autonomy, and infrastructure. Anti-sharia, pro-affirmative action.
# Agricultural base. The party of the peoples who are nobody's majority.
MBU_POSITIONS = np.array([
    -3.0,  #  0  sharia: secular (anti-Islamic encroachment)
    +3.0,  #  1  fiscal: strong autonomy
    +0.0,  #  2  chinese: neutral
    -2.0,  #  3  bic: anti-BIC
    +4.5,  #  4  ethnic_quotas: strongest affirmative action (minority protection)
    +1.0,  #  5  fertility: mildly pro-natalist
    -3.0,  #  6  constitutional: parliamentary
    +3.5,  #  7  resource: strong local control
    +2.0,  #  8  housing: interventionist
    -1.5,  #  9  education: mildly localist
    +2.0,  # 10  labor: pro-labor
    -2.5,  # 11  military: civilian control (military abuses in MB)
    +1.0,  # 12  immigration: mildly restrictionist
    -2.5,  # 13  language: vernacular (protect local languages)
    +1.0,  # 14  womens_rights: mildly progressive
    +4.5,  # 15  trad_authority: strongest integration
    +4.5,  # 16  infrastructure: strongest universal (development deficit)
    -2.5,  # 17  land_tenure: customary (protect ancestral lands)
    +3.0,  # 18  taxation: redistribution
    +3.5,  # 19  agriculture: protectionist (farming heartland)
    +0.5,  # 20  bio_enhancement: mildly pro
    +0.0,  # 21  trade: neutral
    +3.5,  # 22  environment: strong regulation
    +3.5,  # 23  media: press freedom
    +4.0,  # 24  healthcare: universal (health deficit)
    -2.0,  # 25  pada_status: anti-Pada
    +2.5,  # 26  energy: green
    -4.5,  # 27  az_restructuring: strongly restructure (want Middle Belt state)
])

# DPA - Delta People's Alliance
# Niger Delta minority coalition: Ijaw, Urhobi, Itsekiri, Ogoni, Efik, Ibibio.
# Resource justice is the core identity. Fiercely pro-local resource control,
# pro-environmental regulation (oil spills), pro-fiscal autonomy. Secular,
# moderately progressive on social issues. Anti-traditional authority where
# it conflicts with resource demands. The party of the creeks, the pipelines,
# and the broken promises.
DPA_POSITIONS = np.array([
    -2.5,  #  0  sharia: secular
    +4.0,  #  1  fiscal: strong autonomy (resource control)
    +1.0,  #  2  chinese: mild WAFTA (Chinese oil investment)
    -1.5,  #  3  bic: mildly anti
    +2.0,  #  4  ethnic_quotas: affirmative action (minority protection)
    -1.0,  #  5  fertility: mildly control
    -2.0,  #  6  constitutional: parliamentary
    +4.5,  #  7  resource: strongest local control (THE Delta issue)
    +3.0,  #  8  housing: intervention
    +0.5,  #  9  education: centrist
    +3.0,  # 10  labor: pro-labor (oil workers)
    -2.0,  # 11  military: civilian control (JTF abuses in Delta)
    -1.0,  # 12  immigration: mildly open
    +0.5,  # 13  language: centrist
    +2.0,  # 14  womens_rights: progressive
    -1.5,  # 15  trad_authority: mildly marginalize
    +3.5,  # 16  infrastructure: universal (development deficit)
    -3.0,  # 17  land_tenure: customary (protect ancestral/fishing rights)
    +2.5,  # 18  taxation: redistribution
    +1.5,  # 19  agriculture: mildly protectionist
    +1.5,  # 20  bio_enhancement: mildly pro
    -1.0,  # 21  trade: mildly autarkic
    +4.5,  # 22  environment: strongest regulation (oil spill trauma)
    +2.0,  # 23  media: press freedom
    +3.5,  # 24  healthcare: universal
    -1.0,  # 25  pada_status: mildly anti-Pada
    +3.5,  # 26  energy: green transition (away from fossil extraction)
    +1.0,  # 27  az_restructuring: mild keep AZ (Littoral AZ serves them)
])

# Validate
for name, pos in [
    ("HFC", HFC_POSITIONS), ("YAP", YAP_POSITIONS),
    ("IPC", IPC_POSITIONS), ("MBU", MBU_POSITIONS),
    ("DPA", DPA_POSITIONS),
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
        name="HFC",
        positions=HFC_POSITIONS,
        valence=0.2,  # deep institutional roots
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.3,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.4, "Public sector": 0.3},
            "education": {"Below secondary": 0.2},
            "age_cohort": {"35-49": 0.2, "50+": 0.3},
            "gender": {"Male": 0.2},
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.1},
            "setting": {"Rural": 0.2},
        },
        regional_strongholds={
            8: +1.2,  # Savanna: deepest HF establishment
            7: +0.8,  # Chad: HF presence, Kanuri split
            6: +0.8,  # Central: Kano heartland
            2: +0.3,  # Niger Zone: Kwara/Niger northern extension
        },
    ),
    Party(
        name="YAP",
        positions=YAP_POSITIONS,
        valence=0.15,  # strong organizational tradition
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.0,
        demographic_coefficients={
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "livelihood": {"Public sector": 0.3, "Formal private": 0.2},
            "gender": {"Female": 0.1},
            "age_cohort": {"35-49": 0.1},
        },
        regional_strongholds={
            2: +1.2,  # Niger Zone: Yoruba heartland (Oyo, Ogun)
            3: +1.0,  # Confluence: Ekiti, Ondo, Osun
            1: +0.8,  # Lagos: Yoruba-dominated capital
        },
    ),
    Party(
        name="IPC",
        positions=IPC_POSITIONS,
        valence=0.1,
        leader_ethnicity="Igbo",
        religious_alignment="Pentecostal",
        economic_positioning=-0.5,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.5, "Formal private": 0.3},
            "income": {"Top 20%": 0.4, "Middle 40%": 0.1},
            "age_cohort": {"25-34": 0.2},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            5: +1.5,  # Eastern: Igbo core (highest single-party stronghold)
            1: +0.3,  # Lagos: Igbo diaspora traders
            4: +0.2,  # Littoral: Igbo in Port Harcourt, Calabar
            3: +0.1,  # Confluence: Igbo traders in Benin, Kogi
        },
    ),
    Party(
        name="MBU",
        positions=MBU_POSITIONS,
        valence=0.1,
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
        economic_positioning=0.4,
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.4, "Trade/informal": 0.2},
            "education": {"Secondary": 0.1},
            "income": {"Bottom 40%": 0.3, "Middle 40%": 0.1},
            "setting": {"Rural": 0.3, "Peri-urban": 0.1},
        },
        regional_strongholds={
            5: +0.5,  # Eastern: Benue Tiv heartland
            6: +0.6,  # Central: Plateau, Nasarawa minorities
            7: +0.3,  # Chad: Taraba, southern Adamawa minorities
            3: +0.2,  # Confluence: Kogi minorities
        },
    ),
    Party(
        name="DPA",
        positions=DPA_POSITIONS,
        valence=0.05,
        leader_ethnicity="Ijaw",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.3,
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.3, "Smallholder": 0.2,
                           "Formal private": 0.1},
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.1},
            "age_cohort": {"25-34": 0.2, "18-24": 0.1},
            "setting": {"Rural": 0.1, "Peri-urban": 0.1},
        },
        regional_strongholds={
            4: +1.5,  # Littoral: Ijaw/Urhobi/Itsekiri core (strongest)
            1: +0.2,  # Lagos: Delta diaspora
            3: +0.3,  # Confluence: Edo, Delta spillover
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LAGOS-2058: Ethnic Bloc Scenario (5 parties)")
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
    print("LAGOS-2058: ETHNIC BLOC SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("  HFC (Hausa-Fulani), YAP (Yoruba), IPC (Igbo),")
    print("  MBU (Middle Belt), DPA (Delta)")
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
