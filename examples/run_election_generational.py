"""
Generational Divide Scenario: Old Guard vs. New Generation

Models a political landscape where the primary cleavage is generational
rather than ethnic or religious. Three generational blocs:

OLD GUARD (50+ establishment):
  EPP - Elders' Patriotic Party: Northern conservative establishment.
        Pro-sharia, pro-traditional authority, paternalist economics.
        The party of retired generals, emirs, and civil service mandarins.

  ONC - Old Nigeria Congress: Southern conservative establishment.
        Pro-business, Christian-leaning, pro-BIC. The party of Lagos
        money men, Igbo merchant princes, and Yoruba obas who want
        things to stay exactly as they are (profitable).

MIDDLE GENERATION (35-49, pragmatist technocrats):
  NPP - New Pragmatist Party: Centrist technocrats. Data-driven, post-
        ideological, pro-WAFTA. The party of MBA graduates who think
        Nigeria's problem is 'governance' not politics.

  AFR - African Futures Rally: Pan-Africanist modernisers. Pro-green,
        pro-continental integration, moderate on everything else. Think
        Nigeria should lead Africa into a post-carbon future.

YOUTH BLOC (18-34, insurgent movements):
  DRM - Digital Rights Movement: Cyber-libertarian youth party. Maximum
        bio-enhancement, internet freedom, anti-surveillance, crypto-
        economy. Born-online generation who want the state to get out
        of their data feeds and into their wallets.

  PPM - Pan-People's Movement: Radical leftist youth coalition. Anti-
        elite, pro-redistribution, pro-worker. The 'burn it down and
        rebuild' party of unemployed graduates and gig workers.

  GEP - Green Earth Party: Environmental youth party. Climate anxiety
        meets political action. Pro-green energy, anti-extraction,
        anti-deforestation. The party of young people who can see the
        Sahara advancing from their bedroom window.

Tests whether generational cleavages can override ethnic/religious
voting patterns, and how turnout varies across age cohorts.
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
# OLD GUARD parties
# ---------------------------------------------------------------------------

# EPP - Elders' Patriotic Party
# Northern conservative establishment. Emirs, retired generals, civil
# service old guard. Pro-sharia, pro-traditional authority, paternalist
# state. Suspicious of technology, bio-enhancement, and young people
# in general. The party of "respect your elders."
EPP_POSITIONS = np.array([
    +4.5,  #  0  sharia: strongly pro
    +3.0,  #  1  fiscal: maximum federalism (emirs control local funds)
    -3.0,  #  2  chinese: anti-Chinese (sovereignty concerns)
    +4.0,  #  3  bic: strongly pro-BIC (Islamic institutional prestige)
    +3.0,  #  4  ethnic_quotas: pro-quotas (patronage network preservation)
    +4.0,  #  5  fertility: strongly pro-natalist (Islamic duty)
    +3.0,  #  6  constitutional: presidential (strong executive tradition)
    +2.0,  #  7  resource: local control
    -1.0,  #  8  housing: laissez-faire
    -2.0,  #  9  education: states control (religious curricula)
    +1.0,  # 10  labor: mildly pro-labor (paternalist)
    +2.0,  # 11  military: pro-military (retired officers)
    +2.0,  # 12  immigration: restrictive (cultural protection)
    -3.0,  # 13  language: vernacular (Arabic/Hausa prestige)
    -4.0,  # 14  womens_rights: conservative
    +5.0,  # 15  trad_authority: maximum empowerment
    +2.0,  # 16  infrastructure: universal (patronage projects)
    -3.0,  # 17  land_tenure: customary (chiefs control land)
    -2.0,  # 18  taxation: low taxes (informal economy)
    +3.0,  # 19  agriculture: protectionist (food self-sufficiency)
    -5.0,  # 20  bio_enhancement: total ban (un-Islamic, un-natural)
    -3.0,  # 21  trade: autarkic (self-reliance)
    -3.0,  # 22  environment: deregulate (development priority)
    -2.0,  # 23  media: state guidance (social stability)
    -1.0,  # 24  healthcare: limited state role (traditional medicine)
    -2.0,  # 25  pada_status: anti-Pada (cultural contamination)
    -3.0,  # 26  energy: fossil (oil wealth)
    +4.0,  # 27  az_restructuring: strong AZs (northern power base)
])

# ONC - Old Nigeria Congress
# Southern conservative establishment. Lagos business elite, Igbo merchant
# princes, old Yoruba intelligentsia. Pro-business, pro-BIC, Christian-
# leaning but pragmatic. Want continuity, stability, and their investments
# to keep growing. The party of "if it ain't broke (for us), don't fix it."
ONC_POSITIONS = np.array([
    -3.0,  #  0  sharia: anti (secularism protects business)
    +1.0,  #  1  fiscal: mild federalism
    +2.0,  #  2  chinese: pro-Chinese (business partnerships)
    +3.0,  #  3  bic: pro-BIC (institutional stability)
    -2.0,  #  4  ethnic_quotas: anti-quotas (meritocratic capitalism)
    -1.0,  #  5  fertility: mildly pro-control
    +2.0,  #  6  constitutional: presidential (strong executive for business)
    -2.0,  #  7  resource: centralize (federal resource management)
    -2.0,  #  8  housing: market-led
    +1.0,  #  9  education: mildly centralist
    -3.0,  # 10  labor: pro-capital (business flexibility)
    +0.5,  # 11  military: mildly pro (security for business)
    -1.0,  # 12  immigration: mildly open (business talent)
    +2.0,  # 13  language: English (business language)
    +1.0,  # 14  womens_rights: mildly progressive
    -1.0,  # 15  trad_authority: mildly reduce (modernize)
    +1.0,  # 16  infrastructure: selective (profitable routes)
    +3.0,  # 17  land_tenure: formalize (property rights for investment)
    -1.0,  # 18  taxation: low taxes (business-friendly)
    -2.0,  # 19  agriculture: free market
    +1.0,  # 20  bio_enhancement: mildly pro (business advantage)
    +3.0,  # 21  trade: open (export-oriented economy)
    -1.0,  # 22  environment: mild deregulation (business costs)
    +1.5,  # 23  media: mildly free (business media)
    +1.0,  # 24  healthcare: private-led
    +3.0,  # 25  pada_status: pro-Pada (cosmopolitan business class)
    +0.0,  # 26  energy: neutral (diversify)
    -1.0,  # 27  az_restructuring: mild restructure
])

# ---------------------------------------------------------------------------
# MIDDLE GENERATION parties
# ---------------------------------------------------------------------------

# NPP - New Pragmatist Party
# Centrist technocrats, MBA types, mid-career professionals. Post-
# ideological: "we don't care about left/right, we care about what
# works." Pro-WAFTA, pro-tech, pro-evidence-based-policy. The party
# of PowerPoint presentations and key performance indicators.
NPP_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular (governance, not religion)
    -1.0,  #  1  fiscal: mildly centralist (efficient allocation)
    +3.0,  #  2  chinese: pro-WAFTA (data says it works)
    -1.0,  #  3  bic: mildly anti-BIC (reform needed)
    -1.0,  #  4  ethnic_quotas: mildly anti (competence over quotas)
    -2.0,  #  5  fertility: control (demographic transition)
    -1.0,  #  6  constitutional: mildly parliamentary
    -0.5,  #  7  resource: mildly centralist
    +2.0,  #  8  housing: planned (smart cities)
    +3.0,  #  9  education: centralist (national standards)
    -1.0,  # 10  labor: mildly pro-capital (flexible labor)
    -2.0,  # 11  military: civilian (professional defence)
    -1.5,  # 12  immigration: open (talent acquisition)
    +2.5,  # 13  language: English (global integration)
    +2.5,  # 14  womens_rights: progressive (talent pool)
    -2.0,  # 15  trad_authority: reduce (modernize institutions)
    +1.0,  # 16  infrastructure: targeted (high-return)
    +3.0,  # 17  land_tenure: formalize (investment climate)
    +1.5,  # 18  taxation: moderate (fund services)
    -1.0,  # 19  agriculture: free market (efficiency)
    +3.0,  # 20  bio_enhancement: pro (productivity gains)
    +3.5,  # 21  trade: strongly open (WAFTA champion)
    +2.0,  # 22  environment: smart regulation (cost-benefit)
    +2.5,  # 23  media: free (transparency)
    +2.0,  # 24  healthcare: universal (human capital)
    +2.0,  # 25  pada_status: pro-Pada
    +3.0,  # 26  energy: green (future-oriented)
    +1.0,  # 27  az_restructuring: mild reform
])

# AFR - African Futures Rally
# Pan-Africanist modernisers. Mid-career professionals who think Nigeria
# should lead Africa into a post-carbon, pan-continental future. Pro-green,
# pro-continental integration, moderate on social issues. Neither left nor
# right — "forward." The party of people who read Achille Mbembe.
AFR_POSITIONS = np.array([
    -1.0,  #  0  sharia: mildly secular (religious pluralism)
    +0.5,  #  1  fiscal: centrist (pragmatic federalism)
    +1.0,  #  2  chinese: mildly pro (South-South cooperation)
    -2.0,  #  3  bic: anti-BIC (neo-colonial institution)
    +0.5,  #  4  ethnic_quotas: mildly pro (inclusive development)
    -1.5,  #  5  fertility: control (sustainable population)
    -2.0,  #  6  constitutional: parliamentary (democratic accountability)
    +1.0,  #  7  resource: mildly local (community benefit)
    +2.0,  #  8  housing: planned
    +2.0,  #  9  education: centralist (pan-African curriculum)
    +1.0,  # 10  labor: mildly pro-labor
    -3.0,  # 11  military: civilian (peace-building)
    -2.5,  # 12  immigration: open (pan-African movement)
    +1.0,  # 13  language: mildly English (African lingua franca)
    +3.0,  # 14  womens_rights: progressive
    -2.5,  # 15  trad_authority: reduce (post-colonial institutions)
    +3.0,  # 16  infrastructure: universal (continental connectivity)
    +1.5,  # 17  land_tenure: moderate formalization
    +2.0,  # 18  taxation: moderate (development finance)
    +1.0,  # 19  agriculture: mildly protectionist (food sovereignty)
    +2.0,  # 20  bio_enhancement: pro (African biotech)
    +2.0,  # 21  trade: open (continental free trade)
    +4.5,  # 22  environment: strongest regulation (climate crisis)
    +3.0,  # 23  media: press freedom
    +3.0,  # 24  healthcare: universal (pan-African health)
    +1.0,  # 25  pada_status: mildly pro
    +5.0,  # 26  energy: maximum green (Africa's solar future)
    +0.0,  # 27  az_restructuring: neutral (focus on continental)
])

# ---------------------------------------------------------------------------
# YOUTH BLOC parties
# ---------------------------------------------------------------------------

# DRM - Digital Rights Movement
# Cyber-libertarian youth party. Born on the internet, lives on the
# internet, wants the government to stay off the internet. Maximum bio-
# enhancement, crypto-economy, decentralised governance. Anti-surveillance,
# anti-censorship. The party of the chronically online.
DRM_POSITIONS = np.array([
    -4.5,  #  0  sharia: aggressively secular (no religious law)
    -3.0,  #  1  fiscal: centralist (efficient digital state)
    +3.0,  #  2  chinese: pro-WAFTA (tech transfer)
    -4.0,  #  3  bic: anti-BIC (colonial relic)
    -3.5,  #  4  ethnic_quotas: anti (meritocracy/algorithm)
    -3.0,  #  5  fertility: control (body autonomy)
    -4.0,  #  6  constitutional: parliamentary (decentralised)
    -1.0,  #  7  resource: mildly centralist (transparent allocation)
    +1.0,  #  8  housing: mild intervention
    +4.0,  #  9  education: centralist (universal digital education)
    -2.0,  # 10  labor: pro-capital (gig economy innovation)
    -4.5,  # 11  military: strong civilian (anti-surveillance state)
    -3.0,  # 12  immigration: open (digital nomad economy)
    +3.5,  # 13  language: English (code is in English)
    +4.0,  # 14  womens_rights: progressive
    -5.0,  # 15  trad_authority: total marginalization
    -1.0,  # 16  infrastructure: targeted (fibre, not roads)
    +4.5,  # 17  land_tenure: formalize (blockchain cadastre)
    +0.0,  # 18  taxation: neutral (crypto complicates this)
    -3.0,  # 19  agriculture: free market (food tech)
    +5.0,  # 20  bio_enhancement: maximum (core identity)
    +4.0,  # 21  trade: open (digital free trade)
    +3.0,  # 22  environment: regulate (tech solutions)
    +5.0,  # 23  media: maximum freedom (no censorship)
    +2.0,  # 24  healthcare: universal (telemedicine)
    +3.0,  # 25  pada_status: pro-Pada (digital cosmopolitan)
    +4.0,  # 26  energy: green (solar-powered servers)
    +2.0,  # 27  az_restructuring: reform (digital governance)
])

# PPM - Pan-People's Movement
# Radical leftist youth coalition. Angry at everything: inequality,
# unemployment, corruption, exploitation, environmental destruction.
# Pro-redistribution, pro-worker, anti-elite, anti-foreign capital.
# The party that organises via WhatsApp and shows up to protest.
PPM_POSITIONS = np.array([
    -1.0,  #  0  sharia: mildly secular (not the issue)
    -2.5,  #  1  fiscal: centralist (redistribute nationally)
    -4.0,  #  2  chinese: anti-Chinese (exploitation)
    -3.0,  #  3  bic: anti-BIC (neo-colonial)
    +2.0,  #  4  ethnic_quotas: pro (solidarity quotas)
    +0.0,  #  5  fertility: neutral (personal choice)
    -3.0,  #  6  constitutional: parliamentary (people's parliament)
    +3.0,  #  7  resource: local control (community ownership)
    +5.0,  #  8  housing: maximum (housing is a right)
    +1.0,  #  9  education: mildly centralist
    +5.0,  # 10  labor: maximum pro-labor
    -3.0,  # 11  military: civilian (stop militarism)
    +0.0,  # 12  immigration: neutral
    -1.5,  # 13  language: vernacular (working class voice)
    +2.0,  # 14  womens_rights: progressive
    -3.0,  # 15  trad_authority: reduce (chiefs exploit workers)
    +5.0,  # 16  infrastructure: maximum universal
    -2.0,  # 17  land_tenure: customary (protect poor from landlords)
    +5.0,  # 18  taxation: maximum redistribution
    +3.0,  # 19  agriculture: protectionist (food sovereignty)
    +0.0,  # 20  bio_enhancement: neutral (not the priority)
    -3.0,  # 21  trade: autarkic (protect jobs)
    +2.5,  # 22  environment: regulate (polluters pay)
    +2.0,  # 23  media: press freedom (workers' media)
    +5.0,  # 24  healthcare: maximum universal
    -2.0,  # 25  pada_status: anti-Pada (elite identity)
    +2.0,  # 26  energy: green (just transition)
    -2.0,  # 27  az_restructuring: restructure (break elite power)
])

# GEP - Green Earth Party
# Environmental youth party. Single-issue voters who've expanded into
# a full platform. The Sahel is advancing, flooding is worsening,
# the Niger Delta is dying. Climate anxiety meets political action.
# Draws from educated youth across ethnic/religious lines.
GEP_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular (science-based governance)
    -1.0,  #  1  fiscal: mildly centralist (environmental standards)
    +1.0,  #  2  chinese: mildly pro (green tech transfer)
    -2.0,  #  3  bic: anti-BIC (needs reform)
    -1.0,  #  4  ethnic_quotas: mildly anti (environmental justice instead)
    -3.5,  #  5  fertility: control (population-environment link)
    -2.0,  #  6  constitutional: parliamentary
    +1.0,  #  7  resource: mildly local (community stewardship)
    +1.5,  #  8  housing: planned (eco-housing)
    +2.0,  #  9  education: centralist (environmental curriculum)
    +1.0,  # 10  labor: mildly pro-labor (green jobs)
    -3.0,  # 11  military: civilian (peace, not war)
    -1.0,  # 12  immigration: mildly open (climate refugees)
    +1.5,  # 13  language: mildly English
    +3.5,  # 14  womens_rights: progressive (women & environment)
    -3.0,  # 15  trad_authority: reduce
    +2.5,  # 16  infrastructure: universal (green infrastructure)
    +1.0,  # 17  land_tenure: moderate
    +2.5,  # 18  taxation: moderate (green taxes)
    +2.0,  # 19  agriculture: mildly protectionist (sustainable farming)
    +2.0,  # 20  bio_enhancement: pro (environmental biotech)
    +1.0,  # 21  trade: mildly open (green trade)
    +5.0,  # 22  environment: maximum regulation (existential issue)
    +3.0,  # 23  media: press freedom
    +2.5,  # 24  healthcare: universal
    +1.0,  # 25  pada_status: mildly pro
    +5.0,  # 26  energy: maximum green (core identity)
    +0.5,  # 27  az_restructuring: mild reform
])

# Validate all positions
for name, pos in [
    ("EPP", EPP_POSITIONS), ("ONC", ONC_POSITIONS),
    ("NPP", NPP_POSITIONS), ("AFR", AFR_POSITIONS),
    ("DRM", DRM_POSITIONS), ("PPM", PPM_POSITIONS),
    ("GEP", GEP_POSITIONS),
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
    # --- OLD GUARD ---
    Party(
        name="EPP",  # Elders' Patriotic Party
        positions=EPP_POSITIONS,
        valence=0.15,  # patronage networks, institutional memory
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.4,
        demographic_coefficients={
            "age_cohort": {"50+": 0.5, "35-49": 0.2, "25-34": -0.1, "18-24": -0.3},
            "education": {"Below secondary": 0.2, "Tertiary": -0.1},
            "livelihood": {"Public sector": 0.3, "Smallholder": 0.2},
            "income": {"Middle 40%": 0.1, "Bottom 40%": 0.1},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
            "gender": {"Male": 0.2},
        },
        regional_strongholds={
            8: +1.0,   # Savanna: Arewa core
            7: +0.8,   # Chad: northern establishment
            6: +0.5,   # Central: Kano traditional power
            2: +0.2,   # Niger Zone: northern extension
        },
    ),
    Party(
        name="ONC",  # Old Nigeria Congress
        positions=ONC_POSITIONS,
        valence=0.15,  # business networks, campaign finance
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=-0.5,
        demographic_coefficients={
            "age_cohort": {"50+": 0.4, "35-49": 0.2, "25-34": -0.05, "18-24": -0.2},
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "livelihood": {"Formal private": 0.4, "Public sector": 0.2},
            "income": {"Top 20%": 0.4, "Middle 40%": 0.1},
            "setting": {"Urban": 0.2},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            1: +0.6,   # Lagos: business elite
            2: +0.4,   # Niger Zone: Yoruba establishment
            3: +0.3,   # Confluence: southern conservative
            5: +0.3,   # Eastern: Igbo business class
            4: +0.1,   # Littoral: oil company links
        },
    ),

    # --- MIDDLE GENERATION ---
    Party(
        name="NPP",  # New Pragmatist Party
        positions=NPP_POSITIONS,
        valence=0.1,  # technocratic credibility
        leader_ethnicity="Igbo",
        religious_alignment="Secular",
        economic_positioning=-0.3,
        demographic_coefficients={
            "age_cohort": {"35-49": 0.3, "25-34": 0.2, "50+": -0.1, "18-24": -0.1},
            "education": {"Tertiary": 0.4, "Secondary": 0.1},
            "livelihood": {"Formal private": 0.3, "Public sector": 0.2},
            "income": {"Top 20%": 0.2, "Middle 40%": 0.1},
            "setting": {"Urban": 0.3},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.5,   # Lagos: professional class
            5: +0.3,   # Eastern: Igbo professionals
            6: +0.2,   # Central: FCT technocrats
            3: +0.2,   # Confluence: university towns
            4: +0.1,   # Littoral: corporate sector
        },
    ),
    Party(
        name="AFR",  # African Futures Rally
        positions=AFR_POSITIONS,
        valence=0.05,  # idealistic but less well-organised
        leader_ethnicity="Edo",
        religious_alignment="Catholic",
        economic_positioning=0.1,
        demographic_coefficients={
            "age_cohort": {"35-49": 0.2, "25-34": 0.3, "50+": -0.1, "18-24": 0.1},
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "livelihood": {"Public sector": 0.2, "Formal private": 0.2},
            "income": {"Middle 40%": 0.2},
            "setting": {"Urban": 0.2, "Peri-urban": 0.1},
            "gender": {"Female": 0.15},
        },
        regional_strongholds={
            1: +0.3,   # Lagos: cosmopolitan intellectuals
            3: +0.4,   # Confluence: Edo base + university towns
            4: +0.2,   # Littoral: environmental concern
            5: +0.2,   # Eastern: intellectual tradition
            2: +0.1,   # Niger Zone: Ibadan academic community
        },
    ),

    # --- YOUTH BLOC ---
    Party(
        name="DRM",  # Digital Rights Movement
        positions=DRM_POSITIONS,
        valence=0.2,  # viral social media, tech savvy organising
        leader_ethnicity="Pada",
        religious_alignment="Secular",
        economic_positioning=-0.4,
        demographic_coefficients={
            "age_cohort": {"18-24": 0.6, "25-34": 0.4, "35-49": -0.1, "50+": -0.3},
            "education": {"Tertiary": 0.4, "Secondary": 0.2},
            "livelihood": {"Formal private": 0.3, "Unemployed/student": 0.2},
            "income": {"Top 20%": 0.15, "Middle 40%": 0.1},
            "setting": {"Urban": 0.4},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            1: +0.8,   # Lagos: tech capital, Pada homeland
            6: +0.3,   # Central: FCT tech sector
            3: +0.1,   # Confluence: university youth
            5: +0.1,   # Eastern: tech-savvy youth
        },
    ),
    Party(
        name="PPM",  # Pan-People's Movement
        positions=PPM_POSITIONS,
        valence=-0.05,  # radical stigma, disorganised
        leader_ethnicity="Ijaw",
        religious_alignment="Secular",
        economic_positioning=0.9,
        demographic_coefficients={
            "age_cohort": {"18-24": 0.5, "25-34": 0.3, "35-49": -0.05, "50+": -0.2},
            "education": {"Below secondary": 0.2, "Secondary": 0.1, "Tertiary": -0.2},
            "livelihood": {"Trade/informal": 0.4, "Unemployed/student": 0.5},
            "income": {"Bottom 40%": 0.4},
            "setting": {"Peri-urban": 0.2, "Rural": 0.1},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            4: +0.5,   # Littoral: Niger Delta radical tradition
            1: +0.3,   # Lagos: urban poor, slum organising
            6: +0.2,   # Central: unemployed youth
            5: +0.2,   # Eastern: frustrated graduates
            7: +0.1,   # Chad: youth anger
        },
    ),
    Party(
        name="GEP",  # Green Earth Party
        positions=GEP_POSITIONS,
        valence=0.1,  # moral authority, international support
        leader_ethnicity="Tiv",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.2,
        demographic_coefficients={
            "age_cohort": {"18-24": 0.4, "25-34": 0.3, "35-49": 0.05, "50+": -0.15},
            "education": {"Tertiary": 0.3, "Secondary": 0.15},
            "livelihood": {"Formal private": 0.1, "Public sector": 0.1,
                           "Unemployed/student": 0.1},
            "income": {"Middle 40%": 0.1},
            "setting": {"Urban": 0.2, "Rural": 0.1},
            "gender": {"Female": 0.2},
        },
        regional_strongholds={
            4: +0.4,   # Littoral: environmental devastation zone
            5: +0.3,   # Eastern: Benue (Tiv) + farming communities
            1: +0.3,   # Lagos: environmental awareness
            3: +0.2,   # Confluence: deforestation concern
            6: +0.1,   # Central: Plateau environmental issues
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generational Divide Scenario")
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
    print("GENERATIONAL DIVIDE SCENARIO")
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
        "EPP": "Old Guard (50+)",
        "ONC": "Old Guard (50+)",
        "NPP": "Middle Gen (35-49)",
        "AFR": "Middle Gen (35-49)",
        "DRM": "Youth (18-34)",
        "PPM": "Youth (18-34)",
        "GEP": "Youth (18-34)",
    }
    for p, share in sorted_parties:
        votes = summary["national_votes"][p]
        bloc = blocs.get(p, "?")
        print(f"  {p:6s}  {votes:12,}  {share:6.1%}  {bloc}")

    # Bloc totals
    print("\nGENERATIONAL BLOC TOTALS:")
    old_guard = sum(summary["national_shares"][p] for p in ["EPP", "ONC"])
    middle_gen = sum(summary["national_shares"][p] for p in ["NPP", "AFR"])
    youth_bloc = sum(summary["national_shares"][p] for p in ["DRM", "PPM", "GEP"])
    old_votes = sum(summary["national_votes"][p] for p in ["EPP", "ONC"])
    mid_votes = sum(summary["national_votes"][p] for p in ["NPP", "AFR"])
    youth_votes = sum(summary["national_votes"][p] for p in ["DRM", "PPM", "GEP"])
    print(f"  Old Guard (EPP+ONC):   {old_guard:6.1%}  ({old_votes:,} votes)")
    print(f"  Middle Gen (NPP+AFR):  {middle_gen:6.1%}  ({mid_votes:,} votes)")
    print(f"  Youth Bloc (DRM+PPM+GEP): {youth_bloc:6.1%}  ({youth_votes:,} votes)")

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

    # Generational dominance by zone
    print("\nGENERATIONAL DOMINANCE BY ZONE:")
    for _, row in zonal.iterrows():
        az = row.get("AZ Name", row.get("Administrative Zone", "?"))
        old_z = sum(row.get(f"{p}_share", 0) for p in ["EPP", "ONC"])
        mid_z = sum(row.get(f"{p}_share", 0) for p in ["NPP", "AFR"])
        youth_z = sum(row.get(f"{p}_share", 0) for p in ["DRM", "PPM", "GEP"])
        dominant = "OLD GUARD" if old_z > max(mid_z, youth_z) else \
                   "MIDDLE GEN" if mid_z > max(old_z, youth_z) else "YOUTH"
        print(f"  {az:30s}  Old:{old_z:5.1%}  Mid:{mid_z:5.1%}  "
              f"Youth:{youth_z:5.1%}  -> {dominant}")

    print("\n" + "=" * 70)
    print("ANALYSIS NOTES:")
    print("  - Youth Bloc includes DRM (digital), PPM (radical), GEP (green)")
    print("  - Higher ENP = more fragmented, lower = generational consolidation")
    print("  - Old guard advantage: turnout (50+ vote more reliably)")
    print("  - Youth advantage: sheer numbers (median age ~22)")
    print("=" * 70)


if __name__ == "__main__":
    main()
