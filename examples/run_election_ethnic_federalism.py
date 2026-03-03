"""
Ethnic Federalism Scenario: Self-determination as primary cleavage.

Models a political landscape where the key question is the structure
of the Nigerian state. How many administrative zones? Should ethnic
homelands get their own states? Should there be fiscal confederalism
or continued centralisation? This is the ghost of the 1960s regions
and the 1967 civil war.

SEPARATIST/RESTRUCTURING BLOC:
  BIA - Biafra Identity Alliance: Igbo self-determination party.
        Pro-confederalism, pro-restructuring, pro-meritocracy, anti-
        northern-hegemony. The party of IPOB's grandchildren, now
        operating within the democratic system.

  OYO - Oduduwa Youth Organisation: Yoruba self-determination.
        Pro-restructuring to give Yorubaland true fiscal autonomy.
        Pro-commerce, pro-English, moderate on most issues. The
        party of the Yoruba nation movement.

  DRC - Delta Resource Congress: Niger Delta self-determination.
        Resource control is the singular obsession. Pro-local-control,
        pro-environment, anti-extraction-without-benefit. Ijaw +
        Delta minorities.

UNIONIST/CENTRALIST BLOC:
  ONF - One Nigeria Front: Pan-Nigerian unity party. Anti-restructuring,
        pro-AZ system, pro-central-authority. Draws from northern
        establishment (which benefits from current AZ structure) and
        cosmopolitan centrists who fear ethnic fragmentation.

  ARW - Arewa People's Movement: Northern-identity party but framed
        as unionist — the north's population advantage means central
        control benefits them. Pro-Sharia, pro-trad-authority, pro-
        strong-executive, anti-restructuring.

MIDDLE BELT BRIDGE:
  MBP - Middle Belt People's Party: The perennial swing — Middle Belt
        minorities (Tiv, Nupe, Plateau peoples) who want THEIR OWN
        states separate from both north and south. Pro-restructuring
        but for different reasons than Biafra or Oduduwa.

Tests ethnic self-determination vs national unity in a deeply
heterogeneous state.
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

# BIA - Biafra Identity Alliance
# Igbo self-determination. Confederalist, meritocratic, pro-commerce.
BIA_POSITIONS = np.array([
    -3.5,  #  0  sharia: anti (secular Biafra)
    +4.0,  #  1  fiscal: strongly confederalist
    +2.0,  #  2  chinese: pro (pragmatic trade)
    -1.5,  #  3  bic: mildly anti (wants own institutions)
    -3.0,  #  4  ethnic_quotas: strongly meritocratic
    -1.5,  #  5  fertility: control
    -2.0,  #  6  constitutional: parliamentary (power sharing)
    +3.0,  #  7  resource: local control
    +1.5,  #  8  housing: mildly state
    +3.0,  #  9  education: centralist (excellence)
    -0.5,  # 10  labor: mildly pro-capital
    -3.0,  # 11  military: civilian (civil war memory)
    +1.0,  # 12  immigration: mildly open
    +2.5,  # 13  language: English (Igbo + English bilingual)
    +2.0,  # 14  womens_rights: progressive
    -2.0,  # 15  trad_authority: reduce (modern governance)
    +2.0,  # 16  infrastructure: targeted
    +3.0,  # 17  land_tenure: formalize (property rights)
    +1.5,  # 18  taxation: moderate
    -0.5,  # 19  agriculture: mildly free market
    +2.0,  # 20  bio_enhancement: pro
    +3.5,  # 21  trade: open (commerce is Igbo identity)
    +2.0,  # 22  environment: regulate
    +3.0,  # 23  media: free press
    +2.0,  # 24  healthcare: universal
    +1.5,  # 25  pada_status: mildly pro
    +2.5,  # 26  energy: green
    -4.0,  # 27  az_restructuring: strongly restructure (Biafra state)
])

# OYO - Oduduwa Youth Organisation
# Yoruba self-determination. Fiscal autonomy, commerce, culture.
OYO_POSITIONS = np.array([
    -2.0,  #  0  sharia: anti (but tolerant of Yoruba Islam)
    +3.0,  #  1  fiscal: confederalist (Yoruba fiscal autonomy)
    +1.5,  #  2  chinese: mildly pro
    -0.5,  #  3  bic: neutral
    -1.5,  #  4  ethnic_quotas: meritocratic (Yoruba self-reliance)
    -1.0,  #  5  fertility: mildly control
    -1.0,  #  6  constitutional: mildly parliamentary
    +1.0,  #  7  resource: mildly local
    +2.0,  #  8  housing: state intervention (Lagos housing crisis)
    +2.0,  #  9  education: centralist
    -0.5,  # 10  labor: mildly pro-capital
    -2.0,  # 11  military: civilian (June 12 memory)
    +0.5,  # 12  immigration: mildly open
    +1.0,  # 13  language: mildly English (but proud of Yoruba)
    +2.0,  # 14  womens_rights: progressive (Yoruba women traders)
    -1.0,  # 15  trad_authority: mildly reduce (Obas + modern gov)
    +3.0,  # 16  infrastructure: universal (Lagos needs)
    +2.5,  # 17  land_tenure: formalize
    +1.5,  # 18  taxation: moderate
    +0.5,  # 19  agriculture: mildly protectionist
    +1.0,  # 20  bio_enhancement: mildly pro
    +2.5,  # 21  trade: open (oja = Yoruba market culture)
    +1.5,  # 22  environment: regulate
    +2.5,  # 23  media: free press (Nollywood!)
    +2.0,  # 24  healthcare: universal
    +1.0,  # 25  pada_status: mildly pro
    +2.0,  # 26  energy: green
    -3.5,  # 27  az_restructuring: strongly restructure (Oduduwa)
])

# DRC - Delta Resource Congress
# Niger Delta self-determination. Resource control obsessed.
DRC_POSITIONS = np.array([
    -2.0,  #  0  sharia: anti (secular Delta)
    +3.5,  #  1  fiscal: strongly confederalist (revenue!)
    -1.0,  #  2  chinese: mildly anti (land grabs)
    -1.0,  #  3  bic: mildly anti
    +1.5,  #  4  ethnic_quotas: mildly pro (minority representation)
    +0.0,  #  5  fertility: neutral
    -1.5,  #  6  constitutional: parliamentary
    +5.0,  #  7  resource: maximum local control (CORE IDENTITY)
    +1.5,  #  8  housing: mildly state
    +1.0,  #  9  education: mildly centralist
    +3.0,  # 10  labor: pro-labor (oil workers)
    -2.5,  # 11  military: civilian (Delta repression memory)
    +0.0,  # 12  immigration: neutral
    +0.5,  # 13  language: mildly English
    +1.5,  # 14  womens_rights: progressive
    -1.0,  # 15  trad_authority: mildly reduce
    +4.0,  # 16  infrastructure: universal (Delta development)
    -1.0,  # 17  land_tenure: mildly customary (community land)
    +2.0,  # 18  taxation: moderate (from oil revenue)
    +1.0,  # 19  agriculture: mildly protectionist
    +0.5,  # 20  bio_enhancement: mildly pro
    -0.5,  # 21  trade: mildly autarkic
    +5.0,  # 22  environment: maximum (oil spill justice!)
    +2.0,  # 23  media: free press
    +3.0,  # 24  healthcare: universal
    +0.0,  # 25  pada_status: neutral
    +4.0,  # 26  energy: green (post-oil economy)
    -3.0,  # 27  az_restructuring: restructure (Delta AZ)
])

# ONF - One Nigeria Front
# Pan-Nigerian unity. Anti-restructuring, pro-central authority.
ONF_POSITIONS = np.array([
    -0.5,  #  0  sharia: mildly anti (secular unity)
    -2.0,  #  1  fiscal: centralist (federal sharing)
    +1.5,  #  2  chinese: mildly pro (pragmatic)
    +1.0,  #  3  bic: mildly pro (national institution)
    +0.5,  #  4  ethnic_quotas: mildly pro (national harmony)
    +0.0,  #  5  fertility: neutral
    +1.0,  #  6  constitutional: mildly presidential (strong centre)
    -1.5,  #  7  resource: centralist (federal monopoly)
    +1.5,  #  8  housing: mildly state
    +2.0,  #  9  education: centralist (national curriculum)
    +0.5,  # 10  labor: mildly pro-labor
    +0.5,  # 11  military: mildly pro (national unity enforcer)
    +0.5,  # 12  immigration: mildly open (pan-African)
    +2.0,  # 13  language: English (national language)
    +1.5,  # 14  womens_rights: mildly progressive
    +0.0,  # 15  trad_authority: neutral
    +3.0,  # 16  infrastructure: universal (national grid)
    +1.5,  # 17  land_tenure: formalize
    +1.0,  # 18  taxation: moderate
    +1.0,  # 19  agriculture: mildly protectionist
    +1.0,  # 20  bio_enhancement: mildly pro
    +2.0,  # 21  trade: open
    +1.5,  # 22  environment: regulate
    +1.5,  # 23  media: mildly free
    +2.5,  # 24  healthcare: universal
    +1.0,  # 25  pada_status: mildly pro
    +1.5,  # 26  energy: mildly green
    +4.0,  # 27  az_restructuring: strongly pro-AZ (keep current)
])

# ARW - Arewa People's Movement
# Northern identity party. Unionist because north benefits from AZs.
ARW_POSITIONS = np.array([
    +4.0,  #  0  sharia: strongly pro
    -1.5,  #  1  fiscal: centralist (federal revenue flows north)
    -2.0,  #  2  chinese: anti (sovereignty)
    +3.0,  #  3  bic: pro
    +3.0,  #  4  ethnic_quotas: pro (northern representation)
    +4.0,  #  5  fertility: pro-natalist
    +3.0,  #  6  constitutional: presidential (strong north)
    -1.0,  #  7  resource: centralist (federal sharing benefits north)
    +0.0,  #  8  housing: neutral
    -2.5,  #  9  education: localist (Islamic curricula)
    +1.0,  # 10  labor: mildly pro-labor
    +2.0,  # 11  military: pro-guardianship
    -2.0,  # 12  immigration: restrictive
    -3.0,  # 13  language: vernacular (Hausa/Arabic)
    -4.0,  # 14  womens_rights: conservative
    +4.5,  # 15  trad_authority: strongly empower (emirs)
    +2.0,  # 16  infrastructure: universal (northern development)
    -3.0,  # 17  land_tenure: customary (emirate land)
    -1.0,  # 18  taxation: low
    +3.5,  # 19  agriculture: protectionist
    -4.0,  # 20  bio_enhancement: anti
    -2.5,  # 21  trade: autarkic
    -1.5,  # 22  environment: deregulate
    -2.0,  # 23  media: state control
    +0.5,  # 24  healthcare: mildly universal
    -3.0,  # 25  pada_status: anti-Pada
    -1.5,  # 26  energy: fossil
    +4.5,  # 27  az_restructuring: maximum pro-AZ (northern power)
])

# MBP - Middle Belt People's Party
# Middle Belt self-determination. Want own states.
MBP_POSITIONS = np.array([
    -1.5,  #  0  sharia: mildly anti (Christian MB)
    +1.0,  #  1  fiscal: mildly federalist
    +0.5,  #  2  chinese: mildly pro
    +0.0,  #  3  bic: neutral
    +1.5,  #  4  ethnic_quotas: pro (minority protection)
    -0.5,  #  5  fertility: mildly control
    -1.5,  #  6  constitutional: parliamentary (power sharing!)
    +2.0,  #  7  resource: local control (tin/coltan)
    +2.0,  #  8  housing: state intervention
    +2.0,  #  9  education: centralist
    +1.5,  # 10  labor: pro-labor
    -1.0,  # 11  military: mildly civilian
    +0.0,  # 12  immigration: neutral
    +1.5,  # 13  language: mildly English
    +2.0,  # 14  womens_rights: progressive
    -0.5,  # 15  trad_authority: mildly reduce (complex)
    +3.5,  # 16  infrastructure: universal (MB development)
    +0.5,  # 17  land_tenure: mildly formal
    +1.0,  # 18  taxation: moderate
    +2.5,  # 19  agriculture: protectionist (breadbasket)
    +0.5,  # 20  bio_enhancement: mildly pro
    +1.0,  # 21  trade: mildly open
    +2.0,  # 22  environment: regulate
    +2.0,  # 23  media: free press
    +3.0,  # 24  healthcare: universal
    +0.5,  # 25  pada_status: mildly pro
    +1.5,  # 26  energy: mildly green
    -4.5,  # 27  az_restructuring: maximum restructure (MB state!)
])

# Validate
for name, pos in [
    ("BIA", BIA_POSITIONS), ("OYO", OYO_POSITIONS),
    ("DRC", DRC_POSITIONS), ("ONF", ONF_POSITIONS),
    ("ARW", ARW_POSITIONS), ("MBP", MBP_POSITIONS),
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
    # --- SEPARATIST/RESTRUCTURING BLOC ---
    Party(
        name="BIA",  # Biafra Identity Alliance
        positions=BIA_POSITIONS,
        valence=0.1,  # strong identity mobilisation
        leader_ethnicity="Igbo",
        religious_alignment="Catholic",
        economic_positioning=-0.2,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.2, "18-24": 0.15},
            "education": {"Tertiary": 0.25, "Secondary": 0.15},
            "livelihood": {"Formal private": 0.3, "Trade/informal": 0.2},
            "income": {"Middle 40%": 0.15, "Top 20%": 0.1},
            "setting": {"Urban": 0.2, "Peri-urban": 0.1},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            5: +1.0,   # Eastern: Igbo heartland (Anambra, Imo, Abia, Enugu)
            1: +0.3,   # Lagos: Igbo diaspora
        },
    ),
    Party(
        name="OYO",  # Oduduwa Youth Organisation
        positions=OYO_POSITIONS,
        valence=0.1,
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=-0.1,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.2, "35-49": 0.15},
            "education": {"Tertiary": 0.2, "Secondary": 0.15},
            "livelihood": {"Trade/informal": 0.25, "Formal private": 0.2,
                           "Public sector": 0.1},
            "income": {"Middle 40%": 0.2, "Top 20%": 0.1},
            "setting": {"Urban": 0.2, "Peri-urban": 0.1},
            "gender": {"Female": 0.05},
        },
        regional_strongholds={
            1: +0.6,   # Lagos: Yoruba capital
            2: +0.8,   # Niger Zone: Ogun, Oyo — Yoruba heartland
            3: +0.5,   # Confluence: Ekiti, Ondo, Osun
        },
    ),
    Party(
        name="DRC",  # Delta Resource Congress
        positions=DRC_POSITIONS,
        valence=0.05,
        leader_ethnicity="Ijaw",
        religious_alignment="Secular",
        economic_positioning=0.3,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.15, "18-24": 0.1},
            "education": {"Secondary": 0.15, "Below secondary": 0.1},
            "livelihood": {"Trade/informal": 0.2, "Extraction/mining": 0.2,
                           "Unemployed/student": 0.15},
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.1},
            "setting": {"Rural": 0.1, "Peri-urban": 0.1},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            4: +1.0,   # Littoral: Niger Delta heartland
        },
    ),

    # --- UNIONIST/CENTRALIST BLOC ---
    Party(
        name="ONF",  # One Nigeria Front
        positions=ONF_POSITIONS,
        valence=0.1,  # national media, centrist appeal
        leader_ethnicity="Pada",
        religious_alignment="Secular",
        economic_positioning=0.0,
        demographic_coefficients={
            "age_cohort": {"35-49": 0.15, "50+": 0.1},
            "education": {"Tertiary": 0.2, "Secondary": 0.15},
            "livelihood": {"Public sector": 0.25, "Formal private": 0.15},
            "income": {"Middle 40%": 0.15, "Top 20%": 0.1},
            "setting": {"Urban": 0.15, "Peri-urban": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.3,   # Lagos: cosmopolitan unity
            6: +0.4,   # Central: Abuja + Kano cosmopolitans
        },
    ),
    Party(
        name="ARW",  # Arewa People's Movement
        positions=ARW_POSITIONS,
        valence=0.15,  # patronage, trad authority, mosque networks
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.4,
        demographic_coefficients={
            "age_cohort": {"50+": 0.2, "35-49": 0.15},
            "education": {"Below secondary": 0.25, "Secondary": 0.1},
            "livelihood": {"Smallholder": 0.3, "Public sector": 0.2,
                           "Trade/informal": 0.15},
            "income": {"Bottom 40%": 0.15, "Middle 40%": 0.1},
            "setting": {"Rural": 0.25, "Peri-urban": 0.1},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            8: +0.9,   # Savanna: Arewa heartland
            7: +0.7,   # Chad: northern solidarity
            6: +0.5,   # Central: Kano establishment
        },
    ),

    # --- MIDDLE BELT BRIDGE ---
    Party(
        name="MBP",  # Middle Belt People's Party
        positions=MBP_POSITIONS,
        valence=0.05,
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
        economic_positioning=0.2,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.15, "35-49": 0.15},
            "education": {"Secondary": 0.2, "Tertiary": 0.15},
            "livelihood": {"Smallholder": 0.2, "Public sector": 0.15,
                           "Formal private": 0.1},
            "income": {"Middle 40%": 0.2, "Bottom 40%": 0.1},
            "setting": {"Peri-urban": 0.15, "Rural": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            5: +0.5,   # Eastern: Benue (Tiv) + Ebonyi minorities
            6: +0.5,   # Central: Plateau, Nasarawa — MB heartland
            7: +0.2,   # Chad: Adamawa/Taraba minorities
            3: +0.2,   # Confluence: Kogi minorities
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Ethnic Federalism Scenario")
    parser.add_argument("--seed", type=int, default=2058)
    parser.add_argument("--mc", type=int, default=100)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    params = EngineParams(
        q=0.5, beta_s=0.7, alpha_e=3.5, alpha_r=2.5,
        scale=1.0, tau_0=3.8, tau_1=0.3, tau_2=0.5,
        beta_econ=0.25,
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
    print("ETHNIC FEDERALISM SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("=" * 70)

    print(f"\nNational Turnout: {summary['national_turnout']:.1%}")
    print(f"Total Votes Cast: {summary['total_votes']:,}")
    print(f"ENP: {summary['enp']:.2f}")

    print("\nNATIONAL RESULTS:")
    print(f"  {'Party':6s}  {'Votes':>12s}  {'Share':>7s}  Bloc")
    print(f"  {'-'*6}  {'-'*12}  {'-'*7}  {'-'*25}")
    sorted_parties = sorted(summary["national_shares"].items(), key=lambda x: -x[1])
    blocs = {
        "BIA": "Separatist (Biafra)",
        "OYO": "Separatist (Oduduwa)",
        "DRC": "Separatist (Delta)",
        "ONF": "Unionist (Pan-Nigeria)",
        "ARW": "Unionist (Arewa/North)",
        "MBP": "Middle Belt (Bridge)",
    }
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        bloc = blocs.get(p, "?")
        print(f"  {p:6s}  {votes:12,}  {share:6.1%}  {bloc}")

    # Bloc totals
    print("\nSEPARATIST vs. UNIONIST BLOC TOTALS:")
    sep = sum(summary["national_shares"][p] for p in ["BIA", "OYO", "DRC"])
    uni = sum(summary["national_shares"][p] for p in ["ONF", "ARW"])
    bridge = summary["national_shares"]["MBP"]
    sep_v = sum(summary["national_votes"][p] for p in ["BIA", "OYO", "DRC"])
    uni_v = sum(summary["national_votes"][p] for p in ["ONF", "ARW"])
    bridge_v = summary["national_votes"]["MBP"]
    print(f"  Separatist (BIA+OYO+DRC): {sep:6.1%}  ({sep_v:,} votes)")
    print(f"  Unionist (ONF+ARW):       {uni:6.1%}  ({uni_v:,} votes)")
    print(f"  Middle Belt (MBP):        {bridge:6.1%}  ({bridge_v:,} votes)")

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

    # Separatist vs Unionist by zone
    print("\nSEPARATIST vs. UNIONIST BY ZONE:")
    for _, row in zonal.iterrows():
        az = row.get("AZ Name", row.get("Administrative Zone", "?"))
        s_z = sum(row.get(f"{p}_share", 0) for p in ["BIA", "OYO", "DRC"])
        u_z = sum(row.get(f"{p}_share", 0) for p in ["ONF", "ARW"])
        m_z = row.get("MBP_share", 0)
        dominant = "SEPARATIST" if s_z > max(u_z, m_z) else \
                   "UNIONIST" if u_z > max(s_z, m_z) else "MB"
        margin = abs(s_z - u_z)
        swing = "(SWING)" if margin < 0.10 else ""
        print(f"  {az:30s}  Sep:{s_z:5.1%}  Uni:{u_z:5.1%}  MB:{m_z:5.1%}  "
              f"-> {dominant} {swing}")

    print("\n" + "=" * 70)
    print("ANALYSIS NOTES:")
    print("  - Separatist: BIA (Biafra) + OYO (Oduduwa) + DRC (Delta)")
    print("  - Unionist: ONF (pan-Nigeria) + ARW (Arewa/north)")
    print("  - Middle Belt: MBP (want own states but not secession)")
    print("  - Key question: can separatist parties form a coalition?")
    print("  - BIA + OYO + DRC = southern restructuring coalition")
    print("  - ARW captures north through identity + patronage")
    print("  - Lagos is swing: Igbo diaspora vs Yoruba identity vs unity")
    print("=" * 70)


if __name__ == "__main__":
    main()
