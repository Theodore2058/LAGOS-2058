"""
North-South Divide Scenario: Regional polarisation as primary cleavage.

Models a deeply polarised political landscape where the fundamental
cleavage is the historical north-south divide — the most enduring
fault line in Nigerian politics since 1914.

NORTHERN ALLIANCE:
  NAC - Northern Alliance Congress: Pan-northern party uniting Hausa-
        Fulani, Kanuri, and other northern groups. Pro-sharia, pro-
        traditional authority, pro-natalist, protectionist. The party
        of the Arewa movement and northern solidarity.

  KPP - Kanem People's Party: Northeast-specific party representing
        the Chad Basin zone. Al-Shahid-influenced, Kanuri-dominated,
        pro-military security, anti-Western. Born from the insurgency
        zone's unique political culture.

SOUTHERN ALLIANCE:
  SPC - Southern People's Congress: Pan-southern party uniting Yoruba,
        Igbo, Edo, Ibibio, and other southern groups. Secular, pro-
        commerce, pro-restructuring, pro-fiscal federalism. The party
        that wants Nigeria to be more like Lagos and less like Sokoto.

  DMA - Delta Movement Alliance: Niger Delta party focused on resource
        control, environmental justice, and Ijaw/minority rights. The
        party of the creeks and the oil platforms.

CENTRIST BRIDGE:
  NBP - National Bridge Party: Middle Belt + centrist professionals
        trying to bridge the north-south divide. Led by Tiv/Middle Belt
        minorities who belong to neither bloc. Pro-dialogue, moderate
        on most issues, anti-extremism.

Tests whether geographic polarisation produces clear bloc voting
and what happens to swing zones (Central, Confluence).
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

# NAC - Northern Alliance Congress
# Pan-northern: Hausa-Fulani + Kanuri + Nupe + northern minorities.
# Maximum sharia, maximum traditional authority, anti-restructuring.
NAC_POSITIONS = np.array([
    +4.5,  #  0  sharia: strongly pro
    +3.0,  #  1  fiscal: federalist (northern states keep revenue)
    -2.0,  #  2  chinese: anti (sovereignty)
    +3.5,  #  3  bic: pro-BIC
    +3.0,  #  4  ethnic_quotas: pro (northern representation)
    +4.0,  #  5  fertility: strongly pro-natalist
    +3.0,  #  6  constitutional: presidential
    +1.0,  #  7  resource: mildly local
    +0.0,  #  8  housing: neutral
    -2.0,  #  9  education: localist (religious curricula)
    +1.0,  # 10  labor: mildly pro-labor
    +2.0,  # 11  military: pro-guardianship
    +2.0,  # 12  immigration: restrictive
    -3.0,  # 13  language: vernacular (Hausa/Arabic)
    -4.0,  # 14  womens_rights: conservative
    +5.0,  # 15  trad_authority: maximum empowerment
    +2.0,  # 16  infrastructure: universal (northern development)
    -3.0,  # 17  land_tenure: customary (emirs control land)
    -1.0,  # 18  taxation: low tax
    +3.0,  # 19  agriculture: protectionist (food self-sufficiency)
    -4.0,  # 20  bio_enhancement: anti (un-Islamic)
    -2.5,  # 21  trade: autarkic
    -2.0,  # 22  environment: deregulate
    -2.0,  # 23  media: state control
    +0.0,  # 24  healthcare: neutral
    -3.0,  # 25  pada_status: anti-Pada
    -2.0,  # 26  energy: fossil
    +4.0,  # 27  az_restructuring: pro-AZ (northern power base)
])

# KPP - Kanem People's Party
# Northeast Chad Basin party. Kanuri-dominated, Al-Shahid influenced,
# pro-military but anti-federal-neglect. The party of Borno/Yobe.
KPP_POSITIONS = np.array([
    +5.0,  #  0  sharia: maximum
    +2.0,  #  1  fiscal: federalist (reconstruction funds)
    -3.0,  #  2  chinese: anti (cultural invasion)
    +4.0,  #  3  bic: pro-BIC (Islamic legitimacy)
    +2.0,  #  4  ethnic_quotas: pro
    +3.0,  #  5  fertility: pro-natalist
    +4.0,  #  6  constitutional: presidential (strong command)
    +2.0,  #  7  resource: local control (Lake Chad basin)
    +1.0,  #  8  housing: mildly pro
    -3.0,  #  9  education: localist (Quranic)
    +0.5,  # 10  labor: mildly pro-labor
    +4.0,  # 11  military: pro-guardianship (security)
    +3.0,  # 12  immigration: restrictive (border)
    -4.0,  # 13  language: vernacular (Kanuri/Arabic)
    -5.0,  # 14  womens_rights: most conservative
    +4.0,  # 15  trad_authority: strongly pro (Shehu of Borno)
    +4.0,  # 16  infrastructure: universal (reconstruction)
    -3.0,  # 17  land_tenure: customary
    -1.0,  # 18  taxation: low tax
    +2.0,  # 19  agriculture: protectionist
    -5.0,  # 20  bio_enhancement: total ban
    -3.0,  # 21  trade: autarkic
    -2.0,  # 22  environment: deregulate
    -3.0,  # 23  media: state control (security censorship)
    +1.0,  # 24  healthcare: mildly universal
    -4.0,  # 25  pada_status: anti-Pada
    -1.0,  # 26  energy: mildly fossil
    +3.0,  # 27  az_restructuring: pro-AZ
])

# SPC - Southern People's Congress
# Pan-southern: Yoruba + Igbo + Edo + Ibibio + other southerners.
# Secular, pro-commerce, pro-restructuring, pro-fiscal federalism.
SPC_POSITIONS = np.array([
    -4.0,  #  0  sharia: anti
    +1.0,  #  1  fiscal: mildly federalist (southern revenue retention)
    +2.5,  #  2  chinese: pro-WAFTA (commerce)
    -1.0,  #  3  bic: mildly anti (reform)
    -2.0,  #  4  ethnic_quotas: anti (meritocracy)
    -2.0,  #  5  fertility: control
    -2.0,  #  6  constitutional: parliamentary
    -0.5,  #  7  resource: mildly centralist
    +2.0,  #  8  housing: planned
    +3.0,  #  9  education: centralist (national standards)
    -1.0,  # 10  labor: mildly pro-capital
    -3.0,  # 11  military: civilian
    -1.5,  # 12  immigration: mildly open
    +3.0,  # 13  language: English
    +3.5,  # 14  womens_rights: progressive
    -3.0,  # 15  trad_authority: reduce
    +1.0,  # 16  infrastructure: targeted
    +4.0,  # 17  land_tenure: formalize
    +1.0,  # 18  taxation: moderate
    -1.0,  # 19  agriculture: free market
    +3.0,  # 20  bio_enhancement: pro
    +3.5,  # 21  trade: strongly open
    +2.5,  # 22  environment: regulate
    +3.0,  # 23  media: free press
    +2.0,  # 24  healthcare: universal
    +2.5,  # 25  pada_status: pro-Pada
    +3.0,  # 26  energy: green
    -2.0,  # 27  az_restructuring: restructure (break northern power)
])

# DMA - Delta Movement Alliance
# Niger Delta party. Resource control, environmental justice, Ijaw
# and minority rights. Anti-extraction-without-benefit.
DMA_POSITIONS = np.array([
    -2.0,  #  0  sharia: anti (secular Delta)
    +2.0,  #  1  fiscal: federalist (resource revenue!)
    -1.0,  #  2  chinese: mildly anti (land grabs)
    -2.0,  #  3  bic: anti
    +1.0,  #  4  ethnic_quotas: mildly pro (minority representation)
    -0.5,  #  5  fertility: mildly control
    -2.0,  #  6  constitutional: parliamentary
    +5.0,  #  7  resource: maximum local control (core identity)
    +2.0,  #  8  housing: planned
    +1.0,  #  9  education: mildly centralist
    +3.0,  # 10  labor: pro-labor (oil workers)
    -3.0,  # 11  military: civilian (Delta repression memory)
    -1.0,  # 12  immigration: mildly open
    +0.5,  # 13  language: mildly English
    +2.0,  # 14  womens_rights: progressive
    -1.0,  # 15  trad_authority: mildly reduce
    +4.0,  # 16  infrastructure: universal (Delta development)
    -1.0,  # 17  land_tenure: mildly customary (community land)
    +2.0,  # 18  taxation: moderate
    +1.0,  # 19  agriculture: mildly protectionist
    +1.0,  # 20  bio_enhancement: mildly pro
    -0.5,  # 21  trade: mildly autarkic
    +5.0,  # 22  environment: maximum (oil spill justice)
    +2.0,  # 23  media: free press
    +3.0,  # 24  healthcare: universal
    +0.0,  # 25  pada_status: neutral
    +4.0,  # 26  energy: green (post-oil transition)
    -1.0,  # 27  az_restructuring: mild restructure
])

# NBP - National Bridge Party
# Middle Belt + centrist professionals. Tiv/plateau minorities trying
# to bridge north and south. Moderate on everything.
NBP_POSITIONS = np.array([
    -1.0,  #  0  sharia: mildly secular (religious pluralism)
    +0.0,  #  1  fiscal: neutral
    +1.0,  #  2  chinese: mildly pro
    +0.0,  #  3  bic: neutral (reform)
    +0.5,  #  4  ethnic_quotas: mildly pro (minority protection)
    -0.5,  #  5  fertility: mildly control
    -1.0,  #  6  constitutional: mildly parliamentary
    +1.0,  #  7  resource: mildly local
    +2.0,  #  8  housing: planned
    +2.0,  #  9  education: centralist
    +1.0,  # 10  labor: mildly pro-labor
    -1.0,  # 11  military: mildly civilian
    +0.0,  # 12  immigration: neutral
    +1.0,  # 13  language: mildly English
    +2.0,  # 14  womens_rights: progressive
    +0.0,  # 15  trad_authority: neutral (complex Middle Belt)
    +3.0,  # 16  infrastructure: universal (Middle Belt development)
    +1.0,  # 17  land_tenure: mildly formal
    +1.0,  # 18  taxation: mildly pro
    +2.0,  # 19  agriculture: protectionist (breadbasket)
    +1.5,  # 20  bio_enhancement: mildly pro
    +1.0,  # 21  trade: mildly open
    +2.0,  # 22  environment: regulate
    +2.0,  # 23  media: free
    +3.0,  # 24  healthcare: universal (health gap)
    +0.5,  # 25  pada_status: mildly pro
    +2.0,  # 26  energy: green
    +1.0,  # 27  az_restructuring: mildly pro
])

# Validate
for name, pos in [
    ("NAC", NAC_POSITIONS), ("KPP", KPP_POSITIONS),
    ("SPC", SPC_POSITIONS), ("DMA", DMA_POSITIONS),
    ("NBP", NBP_POSITIONS),
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
    # --- NORTHERN ALLIANCE ---
    Party(
        name="NAC",  # Northern Alliance Congress
        positions=NAC_POSITIONS,
        valence=0.15,  # patronage networks, traditional authority backing
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.3,
        demographic_coefficients={
            "age_cohort": {"50+": 0.2, "35-49": 0.1},
            "education": {"Below secondary": 0.2, "Secondary": 0.1, "Tertiary": -0.1},
            "livelihood": {"Smallholder": 0.3, "Public sector": 0.2,
                           "Trade/informal": 0.1},
            "income": {"Bottom 40%": 0.1, "Middle 40%": 0.1},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            8: +1.0,   # Savanna: Arewa heartland
            6: +0.6,   # Central: Kano + northern establishment
            7: +0.3,   # Chad: pan-northern solidarity
            2: +0.3,   # Niger Zone: northern extension (Niger, Kwara)
        },
    ),
    Party(
        name="KPP",  # Kanem People's Party
        positions=KPP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Kanuri",
        religious_alignment="Al-Shahid",
        economic_positioning=0.5,
        demographic_coefficients={
            "age_cohort": {"18-24": 0.2, "25-34": 0.1, "50+": 0.1},
            "education": {"Below secondary": 0.3},
            "livelihood": {"Smallholder": 0.2, "Trade/informal": 0.1,
                           "Unemployed/student": 0.2},
            "income": {"Bottom 40%": 0.3},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
            "gender": {"Male": 0.2},
        },
        regional_strongholds={
            7: +1.2,   # Chad: Kanuri heartland, Al-Shahid zone
            8: +0.2,   # Savanna: some Al-Shahid influence
        },
    ),

    # --- SOUTHERN ALLIANCE ---
    Party(
        name="SPC",  # Southern People's Congress
        positions=SPC_POSITIONS,
        valence=0.15,  # campaign finance, media presence
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=-0.3,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.15, "35-49": 0.1},
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "livelihood": {"Formal private": 0.3, "Public sector": 0.2,
                           "Trade/informal": 0.1},
            "income": {"Top 20%": 0.2, "Middle 40%": 0.15},
            "setting": {"Urban": 0.3},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.6,   # Lagos: southern capital
            2: +0.5,   # Niger Zone: Yoruba heartland
            3: +0.5,   # Confluence: southern solidarity
            5: +0.5,   # Eastern: Igbo + southern unity
            4: +0.2,   # Littoral: southern solidarity (except DMA)
        },
    ),
    Party(
        name="DMA",  # Delta Movement Alliance
        positions=DMA_POSITIONS,
        valence=0.0,
        leader_ethnicity="Ijaw",
        religious_alignment="Secular",
        economic_positioning=0.4,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.15, "18-24": 0.1},
            "education": {"Secondary": 0.1, "Below secondary": 0.1},
            "livelihood": {"Trade/informal": 0.3, "Unemployed/student": 0.2,
                           "Formal private": 0.1},
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.1},
            "setting": {"Rural": 0.1, "Peri-urban": 0.1},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            4: +1.0,   # Littoral: Niger Delta heartland
            5: +0.1,   # Eastern: Cross River solidarity
        },
    ),

    # --- CENTRIST BRIDGE ---
    Party(
        name="NBP",  # National Bridge Party
        positions=NBP_POSITIONS,
        valence=0.05,
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
        economic_positioning=0.1,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.15, "35-49": 0.15},
            "education": {"Tertiary": 0.2, "Secondary": 0.15},
            "livelihood": {"Smallholder": 0.2, "Public sector": 0.15,
                           "Formal private": 0.1},
            "income": {"Middle 40%": 0.2},
            "setting": {"Peri-urban": 0.15, "Rural": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            5: +0.4,   # Eastern: Benue (Tiv) + Christian Middle Belt
            6: +0.5,   # Central: Plateau/Nasarawa bridge zone
            3: +0.3,   # Confluence: transition zone
            7: +0.1,   # Chad: Adamawa/Taraba minorities
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="North-South Divide Scenario")
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
    lga_votes = compute_vote_counts(results["lga_results_base"], party_names)
    summary = results["summary"]
    mc = results["mc_aggregated"]

    print("\n" + "=" * 70)
    print("NORTH-SOUTH DIVIDE SCENARIO")
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
        "NAC": "Northern Alliance",
        "KPP": "Northern (Chad Basin)",
        "SPC": "Southern Alliance",
        "DMA": "Southern (Delta)",
        "NBP": "Centre (Bridge)",
    }
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        bloc = blocs.get(p, "?")
        print(f"  {p:6s}  {votes:12,}  {share:6.1%}  {bloc}")

    # Bloc totals
    print("\nNORTH vs. SOUTH BLOC TOTALS:")
    north = sum(summary["national_shares"][p] for p in ["NAC", "KPP"])
    south = sum(summary["national_shares"][p] for p in ["SPC", "DMA"])
    bridge = summary["national_shares"]["NBP"]
    north_v = sum(summary["national_votes"][p] for p in ["NAC", "KPP"])
    south_v = sum(summary["national_votes"][p] for p in ["SPC", "DMA"])
    bridge_v = summary["national_votes"]["NBP"]
    print(f"  Northern (NAC+KPP):  {north:6.1%}  ({north_v:,} votes)")
    print(f"  Southern (SPC+DMA):  {south:6.1%}  ({south_v:,} votes)")
    print(f"  Bridge (NBP):        {bridge:6.1%}  ({bridge_v:,} votes)")

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

    # North vs south by zone
    print("\nNORTH vs. SOUTH BY ZONE:")
    for _, row in zonal.iterrows():
        az = row.get("AZ Name", row.get("Administrative Zone", "?"))
        n_z = sum(row.get(f"{p}_share", 0) for p in ["NAC", "KPP"])
        s_z = sum(row.get(f"{p}_share", 0) for p in ["SPC", "DMA"])
        b_z = row.get("NBP_share", 0)
        dominant = "NORTH" if n_z > max(s_z, b_z) else \
                   "SOUTH" if s_z > max(n_z, b_z) else "BRIDGE"
        margin = abs(n_z - s_z)
        swing = "(SWING)" if margin < 0.10 else ""
        print(f"  {az:30s}  N:{n_z:5.1%}  S:{s_z:5.1%}  B:{b_z:5.1%}  "
              f"-> {dominant} {swing}")

    print("\n" + "=" * 70)
    print("ANALYSIS NOTES:")
    print("  - Northern: NAC (pan-north) + KPP (Chad Basin)")
    print("  - Southern: SPC (pan-south) + DMA (Niger Delta)")
    print("  - Bridge: NBP (Middle Belt centrists)")
    print("  - Key swing: Central Zone (Kano vs Plateau)")
    print("  - South has higher turnout (education, urbanisation)")
    print("  - North has more population but lower turnout")
    print("=" * 70)


if __name__ == "__main__":
    main()
