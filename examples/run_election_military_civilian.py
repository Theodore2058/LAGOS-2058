"""
Military vs. Civilian Scenario: Security establishment vs. democratic forces.

Models a political landscape where the central cleavage is the role of the
military/security establishment in governance. Relevant to Nigeria's history
of military dictatorships and the tension between security imperatives
(Al-Shahid insurgency, banditry) and democratic norms.

SECURITY BLOC (pro-military, securocratic):
  NSG - National Security Guard: The retired generals' party. Pro-military
        guardianship, strong executive, centralised security apparatus.
        "The army saved this country; we know how to run it."

  HWK - Homeland Watch Koalition: Civilian hawks. Hardline security-first
        voters who want overwhelming force against Al-Shahid, bandits,
        and separatists. Authoritarian on civil liberties.

CIVILIAN BLOC (pro-democracy, anti-military):
  DCF - Democratic Civilian Front: The liberal democratic party. Civilian
        control of the military, press freedom, human rights, rule of law.
        "Never again" — remembering the military years.

  CRA - Civil Rights Alliance: Radical civilian party. Anti-militarism,
        anti-surveillance, pro-decentralisation, pro-human rights. The
        party of activists, lawyers, and journalists who've been arrested.

PRAGMATIST CENTRE:
  TPP - Third Path Party: Centrist pragmatists who think the military
        debate is a distraction. Pro-WAFTA, pro-development, moderate
        on security. "Can we please talk about the economy?"

Tests how security concerns (Al-Shahid, conflict, federal control) shape
voting patterns and whether securocratic politics can win elections.
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

# NSG - National Security Guard
# Retired generals' party. Military guardianship, strong executive, central
# security apparatus. Nostalgia for "when generals ran things properly."
NSG_POSITIONS = np.array([
    +2.0,  #  0  sharia: mildly pro (northern military base)
    -1.0,  #  1  fiscal: mildly centralist (federal security budget)
    -1.0,  #  2  chinese: mildly anti (sovereignty concerns)
    +2.0,  #  3  bic: pro-BIC (institutional order)
    +1.0,  #  4  ethnic_quotas: mildly pro (military quota system)
    +1.0,  #  5  fertility: mildly pro-natalist (manpower)
    +4.0,  #  6  constitutional: strongly presidential (commander-in-chief)
    -1.0,  #  7  resource: mildly centralist (federal control)
    +0.0,  #  8  housing: neutral
    +1.0,  #  9  education: mildly centralist (military academies)
    -1.0,  # 10  labor: mildly pro-capital (discipline)
    +5.0,  # 11  military: maximum guardianship (core identity)
    +3.0,  # 12  immigration: restrictive (border security)
    +1.0,  # 13  language: mildly English (military language)
    -2.0,  # 14  womens_rights: conservative (military culture)
    +2.0,  # 15  trad_authority: pro (hierarchy)
    +3.0,  # 16  infrastructure: universal (military logistics)
    +1.0,  # 17  land_tenure: mildly formal (military land allocation)
    +0.0,  # 18  taxation: neutral
    +1.0,  # 19  agriculture: mildly protectionist
    -1.0,  # 20  bio_enhancement: mildly anti (military purity)
    -0.5,  # 21  trade: mildly autarkic (strategic independence)
    -2.0,  # 22  environment: deregulate (security priority)
    -3.0,  # 23  media: state control (security censorship)
    +1.0,  # 24  healthcare: mildly universal (military hospitals)
    -1.0,  # 25  pada_status: mildly anti (suspicion of enhanced)
    -1.0,  # 26  energy: mildly fossil (oil revenue for defence)
    +3.0,  # 27  az_restructuring: pro-AZ (military command zones)
])

# HWK - Homeland Watch Koalition
# Civilian hawks. Hardline security-first, authoritarian on civil liberties,
# overwhelming force against insurgents and bandits. The party of people
# who want checkpoints on every corner and curfews that start at sunset.
HWK_POSITIONS = np.array([
    +1.0,  #  0  sharia: mildly pro (northern base)
    +0.0,  #  1  fiscal: neutral
    -2.0,  #  2  chinese: anti (national security risk)
    +1.0,  #  3  bic: mildly pro
    +0.5,  #  4  ethnic_quotas: mildly pro
    +0.5,  #  5  fertility: mildly pro-natalist
    +3.0,  #  6  constitutional: presidential (security executive)
    +0.0,  #  7  resource: neutral
    +1.0,  #  8  housing: mildly pro (strategic resettlement)
    +0.0,  #  9  education: neutral
    -0.5,  # 10  labor: mildly pro-capital
    +4.0,  # 11  military: strongly pro-guardianship
    +4.0,  # 12  immigration: strongly restrictive (border security)
    +0.5,  # 13  language: mildly English
    -1.5,  # 14  womens_rights: mildly conservative
    +1.5,  # 15  trad_authority: pro (order through hierarchy)
    +2.0,  # 16  infrastructure: universal (security roads)
    +0.5,  # 17  land_tenure: mildly formal
    +1.0,  # 18  taxation: mildly pro (fund security)
    +1.5,  # 19  agriculture: mildly protectionist
    -1.5,  # 20  bio_enhancement: anti
    -1.0,  # 21  trade: mildly autarkic
    -1.5,  # 22  environment: deregulate
    -4.0,  # 23  media: strongly state-controlled (anti-disinformation)
    +0.5,  # 24  healthcare: mildly universal
    -1.5,  # 25  pada_status: anti (security concern)
    -0.5,  # 26  energy: mildly fossil
    +2.0,  # 27  az_restructuring: pro-AZ
])

# DCF - Democratic Civilian Front
# Liberal democratic party. Civilian control, press freedom, human rights,
# rule of law. The party of constitutionalism and democratic consolidation.
DCF_POSITIONS = np.array([
    -3.0,  #  0  sharia: anti (secular democracy)
    -0.5,  #  1  fiscal: mildly centralist
    +2.0,  #  2  chinese: pro-WAFTA (economic openness)
    -2.0,  #  3  bic: anti (needs democratic reform)
    -1.0,  #  4  ethnic_quotas: mildly anti (meritocracy)
    -1.5,  #  5  fertility: control (rights-based)
    -3.0,  #  6  constitutional: parliamentary (civilian checks)
    +0.5,  #  7  resource: mildly local
    +2.0,  #  8  housing: planned
    +2.0,  #  9  education: centralist (national curriculum)
    +0.5,  # 10  labor: mildly pro-labor
    -5.0,  # 11  military: maximum civilian control (core identity)
    -2.0,  # 12  immigration: open (human rights)
    +2.0,  # 13  language: English (democratic discourse)
    +4.0,  # 14  womens_rights: strongly progressive
    -3.0,  # 15  trad_authority: reduce (democratic institutions)
    +1.0,  # 16  infrastructure: targeted
    +2.5,  # 17  land_tenure: formalize (rule of law)
    +1.0,  # 18  taxation: moderate
    -0.5,  # 19  agriculture: mildly free market
    +3.0,  # 20  bio_enhancement: pro (bodily autonomy)
    +2.5,  # 21  trade: open
    +3.0,  # 22  environment: regulate
    +5.0,  # 23  media: maximum press freedom (core identity)
    +3.0,  # 24  healthcare: universal
    +2.0,  # 25  pada_status: pro-Pada (minority rights)
    +3.0,  # 26  energy: green
    -1.0,  # 27  az_restructuring: mild restructure
])

# CRA - Civil Rights Alliance
# Radical civilian party. Anti-militarism, anti-surveillance, pro-
# decentralisation, pro-human-rights. Activists, lawyers, journalists.
CRA_POSITIONS = np.array([
    -4.0,  #  0  sharia: anti (religious freedom)
    +2.0,  #  1  fiscal: federalist (decentralise power)
    +0.0,  #  2  chinese: neutral
    -4.0,  #  3  bic: anti (colonial institution)
    +1.0,  #  4  ethnic_quotas: mildly pro (affirmative action)
    -1.0,  #  5  fertility: mildly control (choice)
    -4.0,  #  6  constitutional: strongly parliamentary
    +3.0,  #  7  resource: strongly local (community control)
    +3.0,  #  8  housing: planned
    +1.0,  #  9  education: mildly centralist
    +3.0,  # 10  labor: pro-labor (workers' rights)
    -5.0,  # 11  military: maximum civilian (anti-militarism)
    -3.0,  # 12  immigration: open (refugee solidarity)
    -0.5,  # 13  language: mildly vernacular (minority rights)
    +5.0,  # 14  womens_rights: maximum progressive
    -4.0,  # 15  trad_authority: marginalize (rights over hierarchy)
    +3.0,  # 16  infrastructure: universal (development rights)
    -1.0,  # 17  land_tenure: mildly customary (protect community)
    +3.0,  # 18  taxation: high (fund rights)
    +1.0,  # 19  agriculture: mildly protectionist
    +2.0,  # 20  bio_enhancement: pro (bodily autonomy)
    -1.0,  # 21  trade: mildly autarkic
    +4.0,  # 22  environment: strongly regulate
    +5.0,  # 23  media: maximum freedom
    +4.0,  # 24  healthcare: strongly universal (health as right)
    +1.0,  # 25  pada_status: mildly pro
    +4.0,  # 26  energy: strongly green (environmental justice)
    -2.0,  # 27  az_restructuring: restructure (break military zones)
])

# TPP - Third Path Party
# Centrist pragmatists. The military debate is a distraction from
# economic development. Pro-WAFTA, pro-development, moderate on security.
TPP_POSITIONS = np.array([
    -1.0,  #  0  sharia: mildly secular
    +0.0,  #  1  fiscal: neutral
    +3.5,  #  2  chinese: pro-WAFTA (economic priority)
    +0.0,  #  3  bic: neutral
    -0.5,  #  4  ethnic_quotas: mildly anti
    -1.0,  #  5  fertility: mildly control
    +0.0,  #  6  constitutional: neutral
    +0.0,  #  7  resource: neutral
    +2.0,  #  8  housing: planned (smart cities)
    +3.0,  #  9  education: centralist (national development)
    +0.0,  # 10  labor: neutral (flexible market)
    -1.0,  # 11  military: mildly civilian
    -1.0,  # 12  immigration: mildly open (talent)
    +2.0,  # 13  language: English (global competitiveness)
    +2.0,  # 14  womens_rights: progressive
    -1.0,  # 15  trad_authority: mildly reduce
    +2.0,  # 16  infrastructure: targeted (high-return)
    +3.0,  # 17  land_tenure: formalize (investment)
    +0.5,  # 18  taxation: mildly pro
    -1.0,  # 19  agriculture: mildly free market
    +2.5,  # 20  bio_enhancement: pro (productivity)
    +4.0,  # 21  trade: strongly open
    +2.0,  # 22  environment: smart regulation
    +2.0,  # 23  media: free
    +2.0,  # 24  healthcare: universal
    +2.0,  # 25  pada_status: pro-Pada
    +3.0,  # 26  energy: green
    +0.5,  # 27  az_restructuring: mildly pro
])

# Validate
for name, pos in [
    ("NSG", NSG_POSITIONS), ("HWK", HWK_POSITIONS),
    ("DCF", DCF_POSITIONS), ("CRA", CRA_POSITIONS),
    ("TPP", TPP_POSITIONS),
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
    # --- SECURITY BLOC ---
    Party(
        name="NSG",  # National Security Guard
        positions=NSG_POSITIONS,
        valence=0.15,  # military networks, institutional prestige
        leader_ethnicity="Hausa",
        religious_alignment="Mainstream Sunni",
        economic_positioning=-0.1,
        demographic_coefficients={
            "age_cohort": {"50+": 0.4, "35-49": 0.2, "18-24": -0.2},
            "education": {"Tertiary": 0.2, "Secondary": 0.1},
            "livelihood": {"Public sector": 0.5, "Formal private": 0.2},
            "income": {"Middle 40%": 0.2, "Top 20%": 0.1},
            "setting": {"Urban": 0.1, "Peri-urban": 0.1},
            "gender": {"Male": 0.3},
        },
        regional_strongholds={
            7: +0.8,   # Chad: frontline against Al-Shahid
            6: +0.5,   # Central: security establishment, FCT
            8: +0.4,   # Savanna: banditry-affected, want military
            2: +0.2,   # Niger Zone: military cantonment areas
        },
    ),
    Party(
        name="HWK",  # Homeland Watch Koalition
        positions=HWK_POSITIONS,
        valence=0.0,
        leader_ethnicity="Kanuri",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.2,
        demographic_coefficients={
            "age_cohort": {"35-49": 0.2, "50+": 0.2, "18-24": -0.1},
            "education": {"Below secondary": 0.1, "Secondary": 0.1},
            "livelihood": {"Smallholder": 0.2, "Public sector": 0.2,
                           "Trade/informal": 0.1},
            "income": {"Bottom 40%": 0.1, "Middle 40%": 0.1},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
            "gender": {"Male": 0.2},
        },
        regional_strongholds={
            7: +0.5,   # Chad: Kanuri homeland, insurgency zone
            8: +0.4,   # Savanna: banditry victims
            6: +0.3,   # Central: security-concerned
            3: +0.1,   # Confluence: border security
        },
    ),

    # --- CIVILIAN BLOC ---
    Party(
        name="DCF",  # Democratic Civilian Front
        positions=DCF_POSITIONS,
        valence=0.1,  # democratic legitimacy, international support
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.1,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.2, "35-49": 0.15, "18-24": 0.1},
            "education": {"Tertiary": 0.4, "Secondary": 0.1, "Below secondary": -0.2},
            "livelihood": {"Public sector": 0.2, "Formal private": 0.3},
            "income": {"Top 20%": 0.2, "Middle 40%": 0.1},
            "setting": {"Urban": 0.3},
            "gender": {"Female": 0.15},
        },
        regional_strongholds={
            1: +0.5,   # Lagos: democratic intelligentsia
            2: +0.4,   # Niger Zone: Yoruba democratic tradition
            3: +0.3,   # Confluence: civil society base
            5: +0.2,   # Eastern: anti-military sentiment
            4: +0.2,   # Littoral: Delta anti-military (repression memories)
        },
    ),
    Party(
        name="CRA",  # Civil Rights Alliance
        positions=CRA_POSITIONS,
        valence=-0.05,  # radical stigma, small organization
        leader_ethnicity="Ijaw",
        religious_alignment="Secular",
        economic_positioning=0.5,
        demographic_coefficients={
            "age_cohort": {"18-24": 0.4, "25-34": 0.3, "50+": -0.2},
            "education": {"Tertiary": 0.3, "Below secondary": 0.1},
            "livelihood": {"Unemployed/student": 0.3, "Trade/informal": 0.2},
            "income": {"Bottom 40%": 0.2},
            "setting": {"Urban": 0.2, "Peri-urban": 0.1},
            "gender": {"Female": 0.2},
        },
        regional_strongholds={
            4: +0.5,   # Littoral: Delta activism
            1: +0.3,   # Lagos: activist/NGO base
            5: +0.2,   # Eastern: civil rights tradition
            3: +0.2,   # Confluence: civil society
            6: +0.1,   # Central: FCT activist community
        },
    ),

    # --- PRAGMATIST CENTRE ---
    Party(
        name="TPP",  # Third Path Party
        positions=TPP_POSITIONS,
        valence=0.1,  # professional credibility
        leader_ethnicity="Igbo",
        religious_alignment="Catholic",
        economic_positioning=-0.3,
        demographic_coefficients={
            "age_cohort": {"25-34": 0.2, "35-49": 0.2},
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "livelihood": {"Formal private": 0.3, "Public sector": 0.1},
            "income": {"Top 20%": 0.2, "Middle 40%": 0.15},
            "setting": {"Urban": 0.3},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.4,   # Lagos: business pragmatists
            5: +0.4,   # Eastern: Igbo commerce
            3: +0.2,   # Confluence: professional class
            2: +0.2,   # Niger Zone: business community
            4: +0.1,   # Littoral: corporate sector
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Military vs. Civilian Scenario")
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
    print("MILITARY vs. CIVILIAN SCENARIO")
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
        "NSG": "Security (Generals)",
        "HWK": "Security (Hawks)",
        "DCF": "Civilian (Liberal)",
        "CRA": "Civilian (Radical)",
        "TPP": "Pragmatist Centre",
    }
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        bloc = blocs.get(p, "?")
        print(f"  {p:6s}  {votes:12,}  {share:6.1%}  {bloc}")

    # Bloc totals
    print("\nSECURITY vs. CIVILIAN BLOC TOTALS:")
    security = sum(summary["national_shares"][p] for p in ["NSG", "HWK"])
    civilian = sum(summary["national_shares"][p] for p in ["DCF", "CRA"])
    centre = summary["national_shares"]["TPP"]
    sec_v = sum(summary["national_votes"][p] for p in ["NSG", "HWK"])
    civ_v = sum(summary["national_votes"][p] for p in ["DCF", "CRA"])
    cen_v = summary["national_votes"]["TPP"]
    print(f"  Security (NSG+HWK):   {security:6.1%}  ({sec_v:,} votes)")
    print(f"  Civilian (DCF+CRA):   {civilian:6.1%}  ({civ_v:,} votes)")
    print(f"  Centre (TPP):         {centre:6.1%}  ({cen_v:,} votes)")

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

    # Security vs civilian by zone
    print("\nSECURITY vs. CIVILIAN BY ZONE:")
    for _, row in zonal.iterrows():
        az = row.get("AZ Name", row.get("Administrative Zone", "?"))
        sec_z = sum(row.get(f"{p}_share", 0) for p in ["NSG", "HWK"])
        civ_z = sum(row.get(f"{p}_share", 0) for p in ["DCF", "CRA"])
        cen_z = row.get("TPP_share", 0)
        dominant = "SECURITY" if sec_z > max(civ_z, cen_z) else \
                   "CIVILIAN" if civ_z > max(sec_z, cen_z) else "CENTRE"
        print(f"  {az:30s}  Sec:{sec_z:5.1%}  Civ:{civ_z:5.1%}  "
              f"Cen:{cen_z:5.1%}  -> {dominant}")

    print("\n" + "=" * 70)
    print("ANALYSIS NOTES:")
    print("  - Security bloc: NSG (retired generals) + HWK (civilian hawks)")
    print("  - Civilian bloc: DCF (liberal democrats) + CRA (radical activists)")
    print("  - Security should dominate conflict zones (Chad, Savanna)")
    print("  - Civilian should dominate Lagos, southern urban zones")
    print("  - Key question: does Al-Shahid threat push voters to security?")
    print("=" * 70)


if __name__ == "__main__":
    main()
