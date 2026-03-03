"""
Class Divide Scenario: Economic stratification as the primary cleavage.

Models a political landscape split along economic class lines rather than
ethnicity or religion. Six parties representing different economic strata:

ELITE PARTIES:
  CPF - Capital & Progress Forum: Billionaire-backed, pro-market, pro-
        trade, pro-tech. The party of CEOs, bankers, and tech founders
        who think the free market solves everything. Low taxes, minimal
        regulation, maximum bio-enhancement access (for those who can
        afford it).

  PEA - Professional Excellence Alliance: Upper-middle-class technocrats.
        Meritocracy, credentialism, good governance. The party of doctors,
        lawyers, engineers, and senior civil servants who believe in
        institutions and professional standards. Pro-education, pro-
        healthcare, moderate on everything else.

MIDDLE CLASS:
  MCA - Middle Class Awakening: Small business owners, mid-level civil
        servants, aspiring professionals. Want stability, property rights,
        affordable housing, and decent schools. Not rich enough to benefit
        from CPF's tax cuts, not poor enough for welfare. Perpetually
        squeezed and angry about it.

WORKING CLASS:
  WUP - Workers' Unity Party: Formal sector workers, unionised labor,
        factory hands, transport workers. Pro-labor, pro-minimum-wage,
        anti-automation, anti-WAFTA (threatens local jobs). The party
        of the lunch pail and the union card.

  FPA - Farmers & Pastoralists Alliance: Rural agricultural workers,
        smallholders, herders. Pro-subsidy, pro-protectionism, pro-
        traditional land tenure. The party of the people who actually
        grow the food everyone else eats.

UNDERCLASS:
  PLP - People's Liberation Platform: Unemployed, gig workers, street
        vendors, slum dwellers. Maximum redistribution, maximum welfare,
        anti-everything-that-exists. The party of people with nothing
        to lose and everything to gain.

Tests whether class-based mobilisation can overcome ethnic/religious
voting patterns when party positions align with economic interests.
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
# Party position definitions
# ---------------------------------------------------------------------------

# CPF - Capital & Progress Forum
# Billionaire-backed, pure free-market. Tax cuts, deregulation, open trade,
# bio-enhancement as competitive advantage. Anti-labor, anti-welfare.
CPF_POSITIONS = np.array([
    -3.0,  #  0  sharia: secular (bad for business)
    +1.0,  #  1  fiscal: mild federalism (local business climate)
    +4.0,  #  2  chinese: strongly pro-WAFTA (investment flows)
    +1.0,  #  3  bic: mildly pro (institutional stability)
    -3.0,  #  4  ethnic_quotas: anti (market meritocracy)
    -2.0,  #  5  fertility: control (workforce quality over quantity)
    +2.0,  #  6  constitutional: presidential (decisive executive)
    -2.0,  #  7  resource: centralize (efficient mega-projects)
    -3.0,  #  8  housing: pure market (property investment)
    +1.0,  #  9  education: mildly centralist (STEM pipeline)
    -5.0,  # 10  labor: maximum pro-capital
    -1.0,  # 11  military: mildly civilian
    -2.0,  # 12  immigration: open (talent + cheap labor)
    +3.0,  # 13  language: English (international business)
    +1.0,  # 14  womens_rights: mildly progressive (talent pool)
    -2.0,  # 15  trad_authority: reduce (modernize)
    -1.0,  # 16  infrastructure: targeted (profitable routes)
    +5.0,  # 17  land_tenure: maximum formalization (property rights)
    -4.0,  # 18  taxation: minimum taxes
    -3.0,  # 19  agriculture: free market (agribusiness)
    +4.0,  # 20  bio_enhancement: strongly pro (competitive edge)
    +5.0,  # 21  trade: maximum open
    -2.0,  # 22  environment: deregulate (growth first)
    +2.0,  # 23  media: free (business media)
    -2.0,  # 24  healthcare: private-led (premium care)
    +3.0,  # 25  pada_status: pro-Pada (tech-enhanced elite)
    +2.0,  # 26  energy: mildly green (tech investment)
    -1.0,  # 27  az_restructuring: mild restructure
])

# PEA - Professional Excellence Alliance
# Upper-middle-class technocrats. Meritocracy, credentialism, institutions.
# Pro-education, pro-healthcare, pro-good-governance. Moderate but firm
# believers in expertise and professional standards.
PEA_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular (professional governance)
    -1.0,  #  1  fiscal: mildly centralist (national standards)
    +2.0,  #  2  chinese: pro-WAFTA (professional opportunities)
    -0.5,  #  3  bic: mildly anti (needs reform)
    -1.5,  #  4  ethnic_quotas: anti (meritocracy)
    -2.0,  #  5  fertility: control (demographic planning)
    -1.0,  #  6  constitutional: mildly parliamentary
    -0.5,  #  7  resource: mildly centralist
    +1.0,  #  8  housing: mild intervention (affordable professional housing)
    +4.0,  #  9  education: strongly centralist (national excellence)
    -2.0,  # 10  labor: pro-capital (professional flexibility)
    -3.0,  # 11  military: civilian (professional governance)
    -1.0,  # 12  immigration: mildly open (skilled immigration)
    +3.0,  # 13  language: English (professional standard)
    +3.0,  # 14  womens_rights: progressive (professional women)
    -2.0,  # 15  trad_authority: reduce (professional governance)
    +1.0,  # 16  infrastructure: targeted (knowledge economy)
    +3.0,  # 17  land_tenure: formalize (legal certainty)
    +1.0,  # 18  taxation: moderate (fund services)
    -1.0,  # 19  agriculture: free market (efficiency)
    +3.0,  # 20  bio_enhancement: pro (professional advantage)
    +3.0,  # 21  trade: open (professional mobility)
    +2.0,  # 22  environment: smart regulation
    +3.0,  # 23  media: free press (informed public)
    +4.0,  # 24  healthcare: universal (public health mandate)
    +2.0,  # 25  pada_status: pro-Pada (professional colleagues)
    +3.0,  # 26  energy: green (evidence-based)
    +1.0,  # 27  az_restructuring: mild reform
])

# MCA - Middle Class Awakening
# Small business owners, mid-level civil servants. Want stability, property
# rights, affordable services. Squeezed by both elites and populists.
MCA_POSITIONS = np.array([
    -1.0,  #  0  sharia: mildly secular
    +0.5,  #  1  fiscal: centrist
    +1.0,  #  2  chinese: mildly pro (pragmatic)
    +0.5,  #  3  bic: centrist
    +0.0,  #  4  ethnic_quotas: neutral
    -1.0,  #  5  fertility: mildly control
    +0.0,  #  6  constitutional: neutral
    +0.5,  #  7  resource: mildly local
    +4.0,  #  8  housing: strongly pro (affordability crisis)
    +2.0,  #  9  education: centralist (quality schools)
    +0.0,  # 10  labor: neutral (small employers & employees)
    -1.0,  # 11  military: mildly civilian
    +0.0,  # 12  immigration: neutral
    +1.5,  # 13  language: mildly English (business)
    +1.5,  # 14  womens_rights: mildly progressive
    -0.5,  # 15  trad_authority: mildly reduce
    +3.0,  # 16  infrastructure: universal (roads, electricity)
    +3.0,  # 17  land_tenure: formalize (protect property)
    +0.0,  # 18  taxation: neutral (don't raise, don't cut)
    +0.5,  # 19  agriculture: mildly protectionist (food prices)
    +1.5,  # 20  bio_enhancement: mildly pro
    +1.0,  # 21  trade: mildly open
    +1.0,  # 22  environment: mild regulation
    +1.5,  # 23  media: mildly free
    +3.0,  # 24  healthcare: universal (cost burden)
    +0.5,  # 25  pada_status: mildly pro
    +1.5,  # 26  energy: mildly green
    +0.0,  # 27  az_restructuring: neutral
])

# WUP - Workers' Unity Party
# Formal sector workers, unions, factory hands. Pro-labor, anti-capital,
# anti-automation, anti-WAFTA. Bread-and-butter economic populism.
WUP_POSITIONS = np.array([
    -0.5,  #  0  sharia: mildly secular
    -1.0,  #  1  fiscal: mildly centralist (national labor law)
    -3.0,  #  2  chinese: anti-WAFTA (threatens jobs)
    -1.0,  #  3  bic: mildly anti
    +1.5,  #  4  ethnic_quotas: mildly pro (worker solidarity quotas)
    +0.0,  #  5  fertility: neutral
    -2.0,  #  6  constitutional: parliamentary (workers' parliament)
    +1.0,  #  7  resource: mildly local (community benefit)
    +4.0,  #  8  housing: strongly pro (workers' housing)
    +1.0,  #  9  education: mildly centralist (vocational training)
    +5.0,  # 10  labor: maximum pro-labor (defining issue)
    -2.0,  # 11  military: civilian
    +0.5,  # 12  immigration: mildly open (worker solidarity)
    -0.5,  # 13  language: mildly vernacular (working class)
    +2.0,  # 14  womens_rights: progressive (women workers)
    -1.0,  # 15  trad_authority: mildly reduce
    +4.0,  # 16  infrastructure: universal (worker mobility)
    -1.0,  # 17  land_tenure: mildly customary (protect workers)
    +3.0,  # 18  taxation: high (fund services)
    +1.0,  # 19  agriculture: mildly protectionist (food prices)
    -2.0,  # 20  bio_enhancement: anti (automation threat)
    -2.0,  # 21  trade: autarkic (protect jobs)
    +1.5,  # 22  environment: mild regulation (green jobs)
    +2.0,  # 23  media: free (workers' media)
    +5.0,  # 24  healthcare: maximum universal
    -1.0,  # 25  pada_status: mildly anti (enhancement = job loss)
    +1.0,  # 26  energy: mildly green
    -1.0,  # 27  az_restructuring: mild restructure
])

# FPA - Farmers & Pastoralists Alliance
# Rural agricultural workers, smallholders, herders. Pro-subsidy, pro-
# protectionism, pro-customary land. The agrarian interest party.
FPA_POSITIONS = np.array([
    +1.0,  #  0  sharia: mildly pro (northern farmer base)
    +3.0,  #  1  fiscal: strongly federalist (local agricultural policy)
    -2.0,  #  2  chinese: anti (land grabs, cheap imports)
    +1.0,  #  3  bic: mildly pro (rural institutions)
    +2.0,  #  4  ethnic_quotas: pro (rural representation)
    +3.0,  #  5  fertility: pro-natalist (labor force)
    +1.0,  #  6  constitutional: mildly presidential
    +3.0,  #  7  resource: local control (water, grazing rights)
    +1.0,  #  8  housing: mildly pro (rural housing)
    -2.0,  #  9  education: localist (ag-focused education)
    +2.0,  # 10  labor: pro-labor (farm workers)
    +0.5,  # 11  military: mildly pro (cattle rustling security)
    +1.0,  # 12  immigration: mildly open (pastoralist movement)
    -2.0,  # 13  language: vernacular (farming communities)
    -1.0,  # 14  womens_rights: mildly traditional
    +3.0,  # 15  trad_authority: pro (land chiefs)
    +5.0,  # 16  infrastructure: maximum universal (rural roads!)
    -4.0,  # 17  land_tenure: strongly customary (protect farmers)
    -1.0,  # 18  taxation: low tax (farmers can't afford taxes)
    +5.0,  # 19  agriculture: maximum protectionist (core identity)
    -3.0,  # 20  bio_enhancement: anti (unnatural)
    -4.0,  # 21  trade: strongly autarkic (food sovereignty)
    -0.5,  # 22  environment: mildly deregulate (farming flexibility)
    -0.5,  # 23  media: mildly regulated (rural media access)
    +2.0,  # 24  healthcare: universal (rural healthcare gap)
    -1.5,  # 25  pada_status: mildly anti (urban elite)
    -2.0,  # 26  energy: mildly fossil (rural energy needs)
    +3.0,  # 27  az_restructuring: pro-AZ (rural representation)
])

# PLP - People's Liberation Platform
# Unemployed, gig workers, street vendors, slum dwellers. Maximum
# redistribution, maximum welfare, anti-elite. The party of desperation.
PLP_POSITIONS = np.array([
    -0.5,  #  0  sharia: mildly secular (not the issue)
    -3.0,  #  1  fiscal: centralist (redistribute from rich states)
    -4.0,  #  2  chinese: anti-Chinese (exploitation, land grabs)
    -3.0,  #  3  bic: anti-BIC (elite institution)
    +3.0,  #  4  ethnic_quotas: pro (uplift the bottom)
    +1.0,  #  5  fertility: mildly pro-natalist (personal choice)
    -3.0,  #  6  constitutional: parliamentary (people's parliament)
    +4.0,  #  7  resource: strongly local (community control)
    +5.0,  #  8  housing: maximum intervention (housing is a right)
    +2.0,  #  9  education: centralist (free education)
    +5.0,  # 10  labor: maximum pro-labor
    -3.0,  # 11  military: civilian (stop military oppression)
    +0.0,  # 12  immigration: neutral (fellow sufferers)
    -1.0,  # 13  language: mildly vernacular (people's language)
    +1.0,  # 14  womens_rights: mildly progressive
    -2.0,  # 15  trad_authority: reduce (chiefs exploit)
    +5.0,  # 16  infrastructure: maximum universal
    -3.0,  # 17  land_tenure: customary (protect poor from eviction)
    +5.0,  # 18  taxation: maximum redistribution (tax the rich)
    +3.0,  # 19  agriculture: protectionist (food for all)
    -1.0,  # 20  bio_enhancement: mildly anti (not accessible to poor)
    -3.0,  # 21  trade: autarkic (protect local)
    +1.0,  # 22  environment: mildly regulate
    +1.0,  # 23  media: mildly free
    +5.0,  # 24  healthcare: maximum universal (survival issue)
    -3.0,  # 25  pada_status: anti-Pada (elite identity)
    +0.0,  # 26  energy: neutral
    -2.0,  # 27  az_restructuring: restructure (break elite AZs)
])

# Validate
for name, pos in [
    ("CPF", CPF_POSITIONS), ("PEA", PEA_POSITIONS),
    ("MCA", MCA_POSITIONS), ("WUP", WUP_POSITIONS),
    ("FPA", FPA_POSITIONS), ("PLP", PLP_POSITIONS),
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
    # --- ELITE ---
    Party(
        name="CPF",  # Capital & Progress Forum
        positions=CPF_POSITIONS,
        valence=0.2,  # campaign finance advantage, media presence
        leader_ethnicity="Pada",
        religious_alignment="Secular",
        economic_positioning=-0.8,  # strongest pro-market
        demographic_coefficients={
            "income": {"Top 20%": 0.6, "Middle 40%": -0.1, "Bottom 40%": -0.3},
            "education": {"Tertiary": 0.4, "Secondary": 0.1, "Below secondary": -0.2},
            "livelihood": {"Formal private": 0.5, "Trade/informal": 0.1},
            "age_cohort": {"35-49": 0.2, "25-34": 0.1},
            "setting": {"Urban": 0.4},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            1: +0.8,   # Lagos: financial capital
            2: +0.2,   # Niger Zone: Ibadan business class
            3: +0.1,   # Confluence: Benin City commerce
            5: +0.2,   # Eastern: Igbo commerce
        },
    ),
    Party(
        name="PEA",  # Professional Excellence Alliance
        positions=PEA_POSITIONS,
        valence=0.15,  # professional credibility
        leader_ethnicity="Igbo",
        religious_alignment="Catholic",
        economic_positioning=-0.3,
        demographic_coefficients={
            "income": {"Top 20%": 0.3, "Middle 40%": 0.2},
            "education": {"Tertiary": 0.5, "Secondary": 0.1, "Below secondary": -0.3},
            "livelihood": {"Public sector": 0.4, "Formal private": 0.3},
            "age_cohort": {"35-49": 0.2, "25-34": 0.15},
            "setting": {"Urban": 0.3},
            "gender": {"Female": 0.15},
        },
        regional_strongholds={
            1: +0.4,   # Lagos: professional class
            5: +0.4,   # Eastern: Igbo professional tradition
            3: +0.3,   # Confluence: university towns
            6: +0.2,   # Central: FCT civil service
            4: +0.1,   # Littoral: oil company professionals
        },
    ),

    # --- MIDDLE CLASS ---
    Party(
        name="MCA",  # Middle Class Awakening
        positions=MCA_POSITIONS,
        valence=0.05,  # broad but shallow appeal
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.0,
        demographic_coefficients={
            "income": {"Middle 40%": 0.4, "Top 20%": -0.1, "Bottom 40%": -0.1},
            "education": {"Secondary": 0.3, "Tertiary": 0.1},
            "livelihood": {"Formal private": 0.2, "Public sector": 0.2,
                           "Trade/informal": 0.1},
            "age_cohort": {"25-34": 0.15, "35-49": 0.15},
            "setting": {"Peri-urban": 0.2, "Urban": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.3,   # Lagos: squeezed middle class
            2: +0.3,   # Niger Zone: Yoruba middle class
            3: +0.3,   # Confluence: peri-urban professionals
            5: +0.2,   # Eastern: aspiring middle class
            6: +0.1,   # Central: mid-level civil servants
        },
    ),

    # --- WORKING CLASS ---
    Party(
        name="WUP",  # Workers' Unity Party
        positions=WUP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Ibibio",
        religious_alignment="Pentecostal",
        economic_positioning=0.6,
        demographic_coefficients={
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.1, "Top 20%": -0.3},
            "education": {"Secondary": 0.2, "Below secondary": 0.1, "Tertiary": -0.2},
            "livelihood": {"Formal private": 0.3, "Trade/informal": 0.3,
                           "Public sector": 0.1},
            "age_cohort": {"25-34": 0.2, "35-49": 0.15},
            "setting": {"Urban": 0.2, "Peri-urban": 0.15},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            1: +0.4,   # Lagos: industrial workers
            4: +0.3,   # Littoral: oil workers, port workers
            6: +0.3,   # Central: Kano industrial zone
            5: +0.2,   # Eastern: factory workers
            3: +0.1,   # Confluence: mining, manufacturing
        },
    ),
    Party(
        name="FPA",  # Farmers & Pastoralists Alliance
        positions=FPA_POSITIONS,
        valence=0.05,  # land-based patronage networks
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Tijaniyya",
        economic_positioning=0.5,
        demographic_coefficients={
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.1, "Top 20%": -0.4},
            "education": {"Below secondary": 0.3, "Secondary": 0.1, "Tertiary": -0.3},
            "livelihood": {"Smallholder": 0.5, "Commercial ag": 0.4},
            "age_cohort": {"35-49": 0.15, "50+": 0.2, "18-24": -0.1},
            "setting": {"Rural": 0.4, "Peri-urban": 0.1, "Urban": -0.2},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            8: +0.5,   # Savanna: farming heartland
            7: +0.4,   # Chad: pastoral communities
            6: +0.3,   # Central: Plateau farming
            2: +0.3,   # Niger Zone: agricultural zone
            5: +0.2,   # Eastern: Benue breadbasket
            3: +0.1,   # Confluence: Kogi farming
        },
    ),

    # --- UNDERCLASS ---
    Party(
        name="PLP",  # People's Liberation Platform
        positions=PLP_POSITIONS,
        valence=-0.1,  # radical stigma, organisational weakness
        leader_ethnicity="Ijaw",
        religious_alignment="Secular",
        economic_positioning=0.9,  # strongest pro-redistribution
        demographic_coefficients={
            "income": {"Bottom 40%": 0.5, "Middle 40%": -0.05, "Top 20%": -0.4},
            "education": {"Below secondary": 0.3, "Secondary": 0.1, "Tertiary": -0.3},
            "livelihood": {"Unemployed/student": 0.5, "Trade/informal": 0.3},
            "age_cohort": {"18-24": 0.4, "25-34": 0.2, "50+": -0.1},
            "setting": {"Peri-urban": 0.2, "Rural": 0.1},
            "gender": {"Male": 0.2},
        },
        regional_strongholds={
            4: +0.5,   # Littoral: Niger Delta poverty
            1: +0.3,   # Lagos: slum population
            7: +0.2,   # Chad: extreme poverty
            8: +0.2,   # Savanna: poverty belt
            6: +0.2,   # Central: urban unemployed
            5: +0.1,   # Eastern: frustrated graduates
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Class Divide Scenario")
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
    print("CLASS DIVIDE SCENARIO")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("=" * 70)

    print(f"\nNational Turnout: {summary['national_turnout']:.1%}")
    print(f"Total Votes Cast: {summary['total_votes']:,}")
    print(f"ENP: {summary['enp']:.2f}")

    print("\nNATIONAL RESULTS:")
    print(f"  {'Party':6s}  {'Votes':>12s}  {'Share':>7s}  Class")
    print(f"  {'-'*6}  {'-'*12}  {'-'*7}  {'-'*20}")
    sorted_parties = sorted(summary["national_shares"].items(), key=lambda x: -x[1])
    blocs = {
        "CPF": "Elite (Capital)",
        "PEA": "Elite (Professional)",
        "MCA": "Middle Class",
        "WUP": "Working Class (Urban)",
        "FPA": "Working Class (Rural)",
        "PLP": "Underclass",
    }
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        bloc = blocs.get(p, "?")
        print(f"  {p:6s}  {votes:12,}  {share:6.1%}  {bloc}")

    # Class bloc totals
    print("\nCLASS BLOC TOTALS:")
    elite = sum(summary["national_shares"][p] for p in ["CPF", "PEA"])
    middle = summary["national_shares"]["MCA"]
    working = sum(summary["national_shares"][p] for p in ["WUP", "FPA"])
    underclass = summary["national_shares"]["PLP"]
    elite_v = sum(summary["national_votes"][p] for p in ["CPF", "PEA"])
    middle_v = summary["national_votes"]["MCA"]
    working_v = sum(summary["national_votes"][p] for p in ["WUP", "FPA"])
    under_v = summary["national_votes"]["PLP"]
    print(f"  Elite (CPF+PEA):         {elite:6.1%}  ({elite_v:,} votes)")
    print(f"  Middle Class (MCA):      {middle:6.1%}  ({middle_v:,} votes)")
    print(f"  Working Class (WUP+FPA): {working:6.1%}  ({working_v:,} votes)")
    print(f"  Underclass (PLP):        {underclass:6.1%}  ({under_v:,} votes)")

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

    # Class dominance by zone
    print("\nCLASS DOMINANCE BY ZONE:")
    for _, row in zonal.iterrows():
        az = row.get("AZ Name", row.get("Administrative Zone", "?"))
        el_z = sum(row.get(f"{p}_share", 0) for p in ["CPF", "PEA"])
        mc_z = row.get("MCA_share", 0)
        wk_z = sum(row.get(f"{p}_share", 0) for p in ["WUP", "FPA"])
        ul_z = row.get("PLP_share", 0)
        dominant = max(
            [("ELITE", el_z), ("MIDDLE", mc_z), ("WORKING", wk_z), ("UNDERCLASS", ul_z)],
            key=lambda x: x[1]
        )[0]
        print(f"  {az:30s}  Elite:{el_z:5.1%}  Mid:{mc_z:5.1%}  "
              f"Work:{wk_z:5.1%}  Under:{ul_z:5.1%}  -> {dominant}")

    print("\n" + "=" * 70)
    print("ANALYSIS NOTES:")
    print("  - Elite: CPF (billionaires) + PEA (professionals)")
    print("  - Working: WUP (urban unions) + FPA (rural farmers)")
    print("  - Class voting vs ethnic/religious voting tension")
    print("  - Higher economic_positioning = stronger pro-poor push via beta_econ")
    print("=" * 70)


if __name__ == "__main__":
    main()
