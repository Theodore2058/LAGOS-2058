"""
Urban-Rural Divide Scenario: Settlement type as primary political cleavage.

Models a political landscape fractured along the urban-rural axis — a
cleavage that cuts across ethnicity, religion, and region. In 2058 Lagos
State alone has more people than many African countries; the sheer scale
of urbanisation reshapes political demands.

URBAN BLOC:
  MCL - Metropolitan Civic League: The party of the big cities. Pro-tech,
        pro-globalisation, secular, feminist, green, free press. Draws
        from Lagos, Kano-metro, Port Harcourt, Abuja, Ibadan, and Enugu.
        Led by young professionals who think the 8-AZ system works fine
        as long as cities are empowered.

  DGP - Digital Generation Party: Radical urban youth movement. Cyber-
        libertarian, pro-crypto, pro-Pada, anti-military, anti-
        traditional-authority. Born on social media, strongest in Lagos
        Island and university towns. The party of the "japa generation"
        that decided to stay and fight.

RURAL BLOC:
  FCA - Farmers & Communities Alliance: The party of the villages. Pro-
        traditional authority, pro-customary land, protectionist on
        agriculture, pro-natalist, vernacular-first. Smallholders,
        pastoralists, and artisans. Strongest in northern savanna and
        southern farming belts alike.

  TCM - Traditional Council Movement: Ultra-conservative rural party.
        Maximum empowerment of emirs, obas, and obis. Anti-modern,
        anti-bio-enhancement, anti-WAFTA. The party that wants to
        return to pre-colonial governance structures. Strongest where
        traditional authority indices are highest.

PERI-URBAN SWING:
  PPP - Peri-urban People's Party: The suburbs and satellite towns.
        Caught between urban aspiration and rural roots. Moderate on
        most issues, pro-housing, pro-infrastructure, pro-education.
        The swing vote that decides elections.

  IWP - Industrial Workers' Party: Factory towns, manufacturing zones,
        refinery communities. Pro-labor, pro-automation-protection,
        pro-housing, anti-capital. The party of the industrial belt
        stretching from Lagos to Ogun to Oyo.

Tests whether the urban-rural cleavage can override ethnic/religious
voting patterns and produce a genuinely cross-cutting alignment.
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
# Party positions
# ---------------------------------------------------------------------------

# MCL - Metropolitan Civic League
# The party of the big cities. Secular, globalised, feminist, green.
MCL_POSITIONS = np.array([
    -3.0,  #  0  sharia: anti (secular urbanism)
    +0.0,  #  1  fiscal: neutral (city budgets already large)
    +3.5,  #  2  chinese: pro-WAFTA (trade, tech, investment)
    -1.0,  #  3  bic: mildly reform
    -2.0,  #  4  ethnic_quotas: meritocracy (city = melting pot)
    -3.0,  #  5  fertility: control (urban family planning)
    -1.5,  #  6  constitutional: mildly parliamentary
    -0.5,  #  7  resource: mildly centralist (federal infrastructure)
    +3.0,  #  8  housing: state intervention (housing crisis)
    +3.5,  #  9  education: centralist (national standards)
    -1.0,  # 10  labor: mildly pro-capital (business-friendly)
    -3.0,  # 11  military: civilian
    +1.0,  # 12  immigration: mildly open (cities need workers)
    +3.5,  # 13  language: English (lingua franca of cities)
    +4.0,  # 14  womens_rights: progressive
    -3.5,  # 15  trad_authority: reduce (cities run by elected councils)
    +2.0,  # 16  infrastructure: targeted (smart cities)
    +4.0,  # 17  land_tenure: formalize (property rights for apartments)
    +2.0,  # 18  taxation: moderate (fund urban services)
    -2.0,  # 19  agriculture: free market (cheap food imports)
    +3.5,  # 20  bio_enhancement: pro (tech hub identity)
    +4.0,  # 21  trade: open (global city connectivity)
    +3.0,  # 22  environment: regulate (air quality, waste)
    +4.0,  # 23  media: free press (vibrant urban media)
    +2.0,  # 24  healthcare: universal (urban health networks)
    +3.0,  # 25  pada_status: pro-Pada (tech acceptance)
    +3.5,  # 26  energy: green (solar, grid modernisation)
    +1.0,  # 27  az_restructuring: mildly pro (empower cities)
])

# DGP - Digital Generation Party
# Radical urban youth. Cyber-libertarian, pro-Pada, anti-military.
DGP_POSITIONS = np.array([
    -4.0,  #  0  sharia: strongly anti
    +1.5,  #  1  fiscal: mildly federalist (local innovation)
    +2.0,  #  2  chinese: pro (tech partners)
    -2.0,  #  3  bic: anti (wants decentralised governance)
    -3.0,  #  4  ethnic_quotas: anti (pure meritocracy)
    -4.0,  #  5  fertility: control (individual choice)
    -2.5,  #  6  constitutional: parliamentary
    +0.0,  #  7  resource: neutral
    +2.0,  #  8  housing: state intervention
    +2.0,  #  9  education: centralist (STEM focus)
    -2.0,  # 10  labor: pro-capital (startup culture)
    -4.0,  # 11  military: civilian (anti-security-state)
    +2.5,  # 12  immigration: open (global talent)
    +4.0,  # 13  language: English (digital language)
    +4.5,  # 14  womens_rights: radical progressive
    -5.0,  # 15  trad_authority: abolish
    +1.0,  # 16  infrastructure: targeted (tech corridors)
    +3.0,  # 17  land_tenure: formalize (tokenised property)
    +1.0,  # 18  taxation: mildly pro (digital services tax)
    -2.0,  # 19  agriculture: free market
    +5.0,  # 20  bio_enhancement: maximum pro
    +4.5,  # 21  trade: maximum open
    +2.5,  # 22  environment: regulate
    +5.0,  # 23  media: maximum free press
    +1.0,  # 24  healthcare: mildly universal (telemedicine)
    +5.0,  # 25  pada_status: maximum pro-Pada
    +4.0,  # 26  energy: green
    -1.0,  # 27  az_restructuring: mildly restructure (city-states)
])

# FCA - Farmers & Communities Alliance
# The party of the villages. Pro-trad-authority, protectionist, pro-natalist.
FCA_POSITIONS = np.array([
    +2.5,  #  0  sharia: moderately pro (northern rural)
    +1.0,  #  1  fiscal: mildly federalist
    -2.5,  #  2  chinese: anti (land grabs, cheap imports)
    +2.0,  #  3  bic: pro (community services)
    +2.0,  #  4  ethnic_quotas: pro (regional representation)
    +3.5,  #  5  fertility: pro-natalist (farm labor = children)
    +2.0,  #  6  constitutional: presidential (strong leader)
    +1.5,  #  7  resource: mildly local
    +0.0,  #  8  housing: neutral (land is cheap)
    -2.0,  #  9  education: localist (vernacular, practical)
    +2.0,  # 10  labor: pro-labor (farmer cooperatives)
    +1.0,  # 11  military: mildly pro (security)
    -2.0,  # 12  immigration: restrictive (land pressure)
    -3.0,  # 13  language: vernacular (mother tongue first)
    -3.0,  # 14  womens_rights: conservative (patriarchal tradition)
    +4.5,  # 15  trad_authority: strongly empower
    +3.0,  # 16  infrastructure: universal (rural roads, wells)
    -3.5,  # 17  land_tenure: customary (community land rights)
    -1.5,  # 18  taxation: low (farmers can't pay)
    +4.5,  # 19  agriculture: maximum protectionist
    -3.5,  # 20  bio_enhancement: anti (unnatural)
    -3.0,  # 21  trade: autarkic (protect local markets)
    -1.0,  # 22  environment: mildly deregulate (farm expansion)
    -1.0,  # 23  media: mildly controlled (community radio)
    +1.0,  # 24  healthcare: mildly universal
    -2.0,  # 25  pada_status: anti-Pada
    -1.5,  # 26  energy: mildly fossil (kerosene, charcoal)
    +2.0,  # 27  az_restructuring: pro-AZ (rural power)
])

# TCM - Traditional Council Movement
# Ultra-conservative rural. Maximum traditional authority, anti-modern.
TCM_POSITIONS = np.array([
    +4.0,  #  0  sharia: pro (religious law = trad order)
    +2.0,  #  1  fiscal: federalist (emirate budgets)
    -4.0,  #  2  chinese: strongly anti (cultural invasion)
    +4.0,  #  3  bic: pro (BIC + traditional legitimacy)
    +3.0,  #  4  ethnic_quotas: pro (communal distribution)
    +5.0,  #  5  fertility: maximum pro-natalist
    +3.0,  #  6  constitutional: presidential (strong ruler)
    +1.0,  #  7  resource: mildly local
    -1.0,  #  8  housing: mildly market (land is chief's domain)
    -3.5,  #  9  education: strongly localist (Quranic/trad)
    +1.0,  # 10  labor: mildly pro-labor (guild tradition)
    +2.0,  # 11  military: pro-guardianship
    -3.0,  # 12  immigration: restrictive (communal boundaries)
    -4.5,  # 13  language: maximum vernacular
    -5.0,  # 14  womens_rights: maximum conservative
    +5.0,  # 15  trad_authority: maximum empowerment
    +2.0,  # 16  infrastructure: universal (rural electrification)
    -5.0,  # 17  land_tenure: maximum customary
    -2.0,  # 18  taxation: low
    +3.0,  # 19  agriculture: protectionist
    -5.0,  # 20  bio_enhancement: total ban
    -4.0,  # 21  trade: autarkic
    -2.0,  # 22  environment: deregulate (trad use rights)
    -3.0,  # 23  media: state control
    +0.0,  # 24  healthcare: neutral
    -4.0,  # 25  pada_status: anti-Pada
    -2.0,  # 26  energy: fossil
    +3.0,  # 27  az_restructuring: pro-AZ (trad structures)
])

# PPP - Peri-urban People's Party
# The suburbs. Caught between urban aspiration and rural roots.
PPP_POSITIONS = np.array([
    -0.5,  #  0  sharia: mildly secular
    +0.5,  #  1  fiscal: mildly federalist
    +1.0,  #  2  chinese: mildly pro
    +0.0,  #  3  bic: neutral
    +0.0,  #  4  ethnic_quotas: neutral
    +0.0,  #  5  fertility: neutral
    -0.5,  #  6  constitutional: mildly parliamentary
    +0.5,  #  7  resource: mildly local
    +4.0,  #  8  housing: strongly pro intervention (core issue!)
    +2.0,  #  9  education: centralist
    +1.5,  # 10  labor: pro-labor (commuter workers)
    -1.0,  # 11  military: mildly civilian
    +0.0,  # 12  immigration: neutral
    +1.0,  # 13  language: mildly English
    +1.0,  # 14  womens_rights: mildly progressive
    -0.5,  # 15  trad_authority: mildly reduce
    +4.5,  # 16  infrastructure: maximum (roads, transit, water!)
    +2.0,  # 17  land_tenure: formalize (satellite town titles)
    +1.5,  # 18  taxation: moderate (fund services)
    +1.0,  # 19  agriculture: mildly protectionist
    +0.5,  # 20  bio_enhancement: mildly pro
    +1.0,  # 21  trade: mildly open
    +2.0,  # 22  environment: regulate (suburban sprawl)
    +1.5,  # 23  media: mildly free
    +3.0,  # 24  healthcare: universal (suburban clinics)
    +0.5,  # 25  pada_status: mildly pro
    +2.0,  # 26  energy: green (reliable power for suburbs)
    +0.0,  # 27  az_restructuring: neutral
])

# IWP - Industrial Workers' Party
# Factory towns, manufacturing zones, refinery communities.
IWP_POSITIONS = np.array([
    -1.0,  #  0  sharia: mildly anti (class > religion)
    +0.0,  #  1  fiscal: neutral
    -1.5,  #  2  chinese: anti (Chinese factory competition)
    -1.0,  #  3  bic: mildly anti
    +1.0,  #  4  ethnic_quotas: mildly pro (worker solidarity)
    +0.5,  #  5  fertility: mildly pro-natalist (working families)
    -1.0,  #  6  constitutional: mildly parliamentary
    +2.0,  #  7  resource: local control (refinery revenue)
    +3.5,  #  8  housing: strongly pro (workers' housing)
    +2.0,  #  9  education: centralist (vocational training)
    +5.0,  # 10  labor: maximum pro-labor (core identity!)
    -1.5,  # 11  military: mildly civilian
    -1.5,  # 12  immigration: mildly restrictive (job protection)
    +0.5,  # 13  language: mildly English
    +1.5,  # 14  womens_rights: progressive (women workers)
    -1.0,  # 15  trad_authority: mildly reduce
    +4.0,  # 16  infrastructure: universal (industrial infra)
    +1.0,  # 17  land_tenure: mildly formal
    +0.0,  # 18  taxation: neutral
    +2.0,  # 19  agriculture: protectionist (food processing)
    -1.0,  # 20  bio_enhancement: mildly anti
    -1.0,  # 21  trade: mildly autarkic (protect industry)
    +1.0,  # 22  environment: mildly regulate
    +1.0,  # 23  media: mildly free
    +3.5,  # 24  healthcare: strongly universal (occupational health)
    -0.5,  # 25  pada_status: mildly anti (job competition fear)
    +0.5,  # 26  energy: mildly green
    +0.0,  # 27  az_restructuring: neutral
])

# Validate
for name, pos in [
    ("MCL", MCL_POSITIONS), ("DGP", DGP_POSITIONS),
    ("FCA", FCA_POSITIONS), ("TCM", TCM_POSITIONS),
    ("PPP", PPP_POSITIONS), ("IWP", IWP_POSITIONS),
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
    # --- URBAN BLOC ---
    Party(
        name="MCL",  # Metropolitan Civic League
        positions=MCL_POSITIONS,
        valence=0.15,  # media presence, campaign finance
        leader_ethnicity="Yoruba",
        religious_alignment="Secular",
        economic_positioning=-0.3,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.2, "35-49": 0.15},
            "education": {"Tertiary": 0.35, "Secondary": 0.15},
            "livelihood": {"Formal private": 0.3, "Public sector": 0.2,
                           "Trade/informal": 0.1},
            "income": {"Top 20%": 0.25, "Middle 40%": 0.15},
            "setting": {"Urban": 0.4},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.8,   # Lagos: urban capital
            6: +0.3,   # Central: Kano metro + Abuja
            3: +0.2,   # Confluence: Ibadan metro spillover
            5: +0.2,   # Eastern: Enugu, Onitsha
        },
    ),
    Party(
        name="DGP",  # Digital Generation Party
        positions=DGP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Pada",
        religious_alignment="Secular",
        economic_positioning=-0.5,
        demographic_coefficients={
            "age_cohort": {"18-24": 0.35, "25-34": 0.2},
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "livelihood": {"Formal private": 0.2, "Unemployed/student": 0.2,
                           "Trade/informal": 0.1},
            "income": {"Middle 40%": 0.15, "Top 20%": 0.1},
            "setting": {"Urban": 0.4},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.6,   # Lagos: tech hub
            6: +0.2,   # Central: university towns
        },
    ),

    # --- RURAL BLOC ---
    Party(
        name="FCA",  # Farmers & Communities Alliance
        positions=FCA_POSITIONS,
        valence=0.1,  # traditional authority endorsements
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.3,
        demographic_coefficients={
            "age_cohort": {"50+": 0.25, "35-49": 0.15},
            "education": {"Below secondary": 0.3, "Secondary": 0.1},
            "livelihood": {"Smallholder": 0.4, "Trade/informal": 0.15,
                           "Extraction/mining": 0.1},
            "income": {"Bottom 40%": 0.25, "Middle 40%": 0.1},
            "setting": {"Rural": 0.4, "Peri-urban": 0.1},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            8: +0.8,   # Savanna: rural heartland
            7: +0.7,   # Chad: rural + trad authority
            2: +0.3,   # Niger Zone: farming belt
            3: +0.2,   # Confluence: rural Ekiti, Ondo hinterland
        },
    ),
    Party(
        name="TCM",  # Traditional Council Movement
        positions=TCM_POSITIONS,
        valence=-0.05,  # seen as retrograde by many
        leader_ethnicity="Kanuri",
        religious_alignment="Al-Shahid",
        economic_positioning=0.5,
        demographic_coefficients={
            "age_cohort": {"50+": 0.3, "35-49": 0.2},
            "education": {"Below secondary": 0.35},
            "livelihood": {"Smallholder": 0.3, "Trade/informal": 0.1},
            "income": {"Bottom 40%": 0.3},
            "setting": {"Rural": 0.45},
            "gender": {"Male": 0.2},
        },
        regional_strongholds={
            7: +0.8,   # Chad: strongest trad authority
            8: +0.6,   # Savanna: emirs
        },
    ),

    # --- PERI-URBAN SWING ---
    Party(
        name="PPP",  # Peri-urban People's Party
        positions=PPP_POSITIONS,
        valence=0.05,
        leader_ethnicity="Igbo",
        religious_alignment="Catholic",
        economic_positioning=0.1,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.2, "35-49": 0.15},
            "education": {"Secondary": 0.2, "Tertiary": 0.1},
            "livelihood": {"Trade/informal": 0.2, "Formal private": 0.15,
                           "Public sector": 0.1},
            "income": {"Middle 40%": 0.25, "Bottom 40%": 0.1},
            "setting": {"Peri-urban": 0.4, "Urban": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            2: +0.4,   # Niger Zone: peri-urban Ogun, Oyo
            3: +0.4,   # Confluence: satellite towns
            5: +0.3,   # Eastern: peri-urban Anambra, Imo
            4: +0.2,   # Littoral: suburban PH, Calabar
            1: +0.2,   # Lagos: suburban sprawl
        },
    ),
    Party(
        name="IWP",  # Industrial Workers' Party
        positions=IWP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Edo",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.6,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.2, "35-49": 0.15, "18-24": 0.1},
            "education": {"Secondary": 0.2, "Below secondary": 0.15},
            "livelihood": {"Formal private": 0.25, "Trade/informal": 0.2,
                           "Extraction/mining": 0.15},
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.15},
            "setting": {"Peri-urban": 0.3, "Urban": 0.15},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            4: +0.5,   # Littoral: refinery towns, PH industrial
            1: +0.3,   # Lagos: industrial Ikeja, Agege
            2: +0.3,   # Niger Zone: Ogun industrial corridor
            3: +0.2,   # Confluence: Edo industry
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Urban-Rural Divide Scenario")
    parser.add_argument("--seed", type=int, default=2058)
    parser.add_argument("--mc", type=int, default=100)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    params = EngineParams(
        q=0.5, beta_s=0.7, alpha_e=3.0, alpha_r=2.0,
        scale=1.0, tau_0=3.8, tau_1=0.3, tau_2=0.5,
        beta_econ=0.3,
        kappa=400.0, sigma_national=0.07, sigma_regional=0.10,
        sigma_turnout=0.02, sigma_turnout_regional=0.03,
    )
    config = ElectionConfig(params=params, parties=PARTIES, n_monte_carlo=args.mc)

    data_path = Path(__file__).parent.parent / "data" / "nigeria_lga_polsim_2058.xlsx"
    results = run_election(data_path, config, seed=args.seed, verbose=not args.quiet)

    party_names = [p.name for p in PARTIES]
    lga_votes = compute_vote_counts(results["lga_results_base"], party_names)
    summary = results["summary"]
    mc = results["mc_aggregated"]

    print("\n" + "=" * 70)
    print("URBAN-RURAL DIVIDE SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("=" * 70)

    print(f"\nNational Turnout: {summary['national_turnout']:.1%}")
    print(f"Total Votes Cast: {summary['total_votes']:,}")
    print(f"ENP: {summary['enp']:.2f}")

    print("\nNATIONAL RESULTS:")
    print(f"  {'Party':6s}  {'Votes':>12s}  {'Share':>7s}  Bloc")
    print(f"  {'-'*6}  {'-'*12}  {'-'*7}  {'-'*20}")
    sorted_parties = sorted(summary["national_shares"].items(), key=lambda x: -x[1])
    blocs = {
        "MCL": "Urban (Metro)",
        "DGP": "Urban (Digital Youth)",
        "FCA": "Rural (Farmers)",
        "TCM": "Rural (Traditional)",
        "PPP": "Peri-urban (Swing)",
        "IWP": "Peri-urban (Workers)",
    }
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        bloc = blocs.get(p, "?")
        print(f"  {p:6s}  {votes:12,}  {share:6.1%}  {bloc}")

    # Bloc totals
    print("\nURBAN vs. RURAL BLOC TOTALS:")
    urban = sum(summary["national_shares"][p] for p in ["MCL", "DGP"])
    rural = sum(summary["national_shares"][p] for p in ["FCA", "TCM"])
    peri = sum(summary["national_shares"][p] for p in ["PPP", "IWP"])
    urban_v = sum(summary["national_votes"][p] for p in ["MCL", "DGP"])
    rural_v = sum(summary["national_votes"][p] for p in ["FCA", "TCM"])
    peri_v = sum(summary["national_votes"][p] for p in ["PPP", "IWP"])
    print(f"  Urban (MCL+DGP):     {urban:6.1%}  ({urban_v:,} votes)")
    print(f"  Rural (FCA+TCM):     {rural:6.1%}  ({rural_v:,} votes)")
    print(f"  Peri-urban (PPP+IWP):{peri:6.1%}  ({peri_v:,} votes)")

    # MC uncertainty
    print("\nMC SHARE UNCERTAINTY (mean [P5 - P95]):")
    ns = mc["national_share_stats"].sort_values("Mean Share", ascending=False)
    for _, row in ns.iterrows():
        if row["Mean Share"] >= 0.01:
            print(f"  {row['Party']:6s}  {row['Mean Share']:6.1%}  "
                  f"[{row['P5 Share']:5.1%} - {row['P95 Share']:5.1%}]")

    # Zonal analysis
    print("\nZONAL SHARES:")
    zonal = summary["zonal_shares"]
    share_cols = [c for c in zonal.columns if c.endswith("_share") and c != "Turnout"]
    cols = ["Administrative Zone", "AZ Name"]
    if "Turnout" in zonal.columns:
        cols.append("Turnout")
    cols.extend(share_cols)
    print(zonal[cols].to_string(index=False))

    # Urban vs rural by zone
    print("\nURBAN vs. RURAL BY ZONE:")
    for _, row in zonal.iterrows():
        az = row.get("AZ Name", row.get("Administrative Zone", "?"))
        u_z = sum(row.get(f"{p}_share", 0) for p in ["MCL", "DGP"])
        r_z = sum(row.get(f"{p}_share", 0) for p in ["FCA", "TCM"])
        p_z = sum(row.get(f"{p}_share", 0) for p in ["PPP", "IWP"])
        dominant = "URBAN" if u_z > max(r_z, p_z) else \
                   "RURAL" if r_z > max(u_z, p_z) else "PERI-URBAN"
        margin = abs(u_z - r_z)
        swing = "(SWING)" if margin < 0.10 else ""
        print(f"  {az:30s}  U:{u_z:5.1%}  R:{r_z:5.1%}  P:{p_z:5.1%}  "
              f"-> {dominant} {swing}")

    print("\n" + "=" * 70)
    print("ANALYSIS NOTES:")
    print("  - Urban: MCL (professionals) + DGP (digital youth)")
    print("  - Rural: FCA (farmers) + TCM (traditional council)")
    print("  - Peri-urban: PPP (suburban swing) + IWP (industrial workers)")
    print("  - Key question: does urban-rural cut across ethnic lines?")
    print("  - Lagos tests whether urban identity > Yoruba identity")
    print("  - Chad/Savanna tests whether rural identity > Hausa identity")
    print("=" * 70)


if __name__ == "__main__":
    main()
