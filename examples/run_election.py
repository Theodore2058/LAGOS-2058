"""
Example: Run a full LAGOS-2058 election with 14 sample parties.

Usage:
    python examples/run_election.py

This script defines 14 parties spanning the 2058 Nigerian political landscape,
runs 100 Monte Carlo iterations, and prints a summary.

Issue dimension order (28 dimensions, -5 to +5):
  0  sharia_jurisdiction        secular ↔ full Sharia
  1  fiscal_autonomy            centralism ↔ confederalism
  2  chinese_relations          Western pivot ↔ deepen WAFTA
  3  bic_reform                 abolish ↔ preserve BIC
  4  ethnic_quotas              meritocracy ↔ affirmative action
  5  fertility_policy           population control ↔ pro-natalism
  6  constitutional_structure   parliamentary ↔ presidential
  7  resource_revenue           federal monopoly ↔ local control
  8  housing                    pure market ↔ state intervention
  9  education                  radical localism ↔ meritocratic centralism
  10 labor_automation           pro-capital ↔ pro-labor
  11 military_role              civilian control ↔ military guardianship
  12 immigration                open borders ↔ restrictionism
  13 language_policy            vernacular ↔ English supremacy
  14 womens_rights              traditional patriarchy ↔ aggressive feminism
  15 traditional_authority      marginalization ↔ formal integration
  16 infrastructure             targeted ↔ universal provision
  17 land_tenure                customary ↔ formalization
  18 taxation                   low tax ↔ high redistribution
  19 agricultural_policy        free market ↔ protectionist smallholder
  20 biological_enhancement     prohibition ↔ universal access
  21 trade_policy               autarky ↔ full openness
  22 environmental_regulation   growth first ↔ strong regulation
  23 media_freedom              state control ↔ full press freedom
  24 healthcare                 pure market ↔ universal provision
  25 pada_status                anti-Padà ↔ Padà preservation
  26 energy_policy              fossil status quo ↔ green transition
  27 az_restructuring           return to 36+ states ↔ keep 8 AZs
"""

import sys
import logging
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.election import run_election
from election_engine.results import compute_state_shares

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

# ---------------------------------------------------------------------------
# Party definitions — 28-element position vectors
# ---------------------------------------------------------------------------
#
# Positions are on the -5 to +5 scale for each of the 28 issue dimensions.
# Listed in issue order above.

# NRP — Nigerian Renaissance Party
# Cosmopolitan modernizers rooted in the Lagos-Abuja professional class and
# the Padà community. Champions meritocracy, secular governance, English-medium
# education, BIC preservation, and Padà cultural rights. Economically
# centrist-liberal with a mild pro-market lean. The closest thing to a
# classical liberal party in the 2058 landscape.
NRP_POSITIONS = np.array([
    -3.5,  #  0  sharia: strongly secular
    -2.5,  #  1  fiscal: centralist
    +0.5,  #  2  chinese: mild WAFTA tilt
    +3.0,  #  3  bic: preserve BIC
    -4.0,  #  4  ethnic_quotas: strongly meritocratic
    -2.0,  #  5  fertility: population control
    -3.0,  #  6  constitutional: parliamentary
    -2.0,  #  7  resource: federal control
    -2.0,  #  8  housing: market-oriented
    +3.5,  #  9  education: meritocratic centralism
    -2.0,  # 10  labor: pro-capital
    +1.0,  # 11  military: mild guardianship
    +1.0,  # 12  immigration: mildly restrictionist
    +4.0,  # 13  language: English supremacy
    +3.0,  # 14  womens_rights: progressive
    -3.5,  # 15  trad_authority: marginalize
    -1.5,  # 16  infrastructure: mildly targeted
    +3.5,  # 17  land_tenure: formalization
    -1.5,  # 18  taxation: low tax
    -1.5,  # 19  agriculture: free market
    +2.0,  # 20  bio_enhancement: pro-access
    +2.0,  # 21  trade: open
    +1.0,  # 22  environment: mild regulation
    -1.0,  # 23  media: mild state lean
    +0.5,  # 24  healthcare: mildly universal
    +4.5,  # 25  pada_status: strong Padà preservation
    +1.5,  # 26  energy: mild green
    +4.0,  # 27  az_restructuring: keep AZs
])

# CND — Congress for Nigerian Democracy
# Reformist democratic party with roots in the old southwestern progressive
# tradition. Strongly pro-press freedom, moderately secular, pro-women's
# rights, and pro-trade openness. Favors parliamentary reform and civilian
# control. Appeals broadly to educated southerners and urban professionals
# outside the Padà orbit. The party of newspaper editors and university
# lecturers.
CND_POSITIONS = np.array([
    -3.0,  #  0  sharia: secular
    +1.0,  #  1  fiscal: mild autonomy
    -3.0,  #  2  chinese: Western pivot
    -3.5,  #  3  bic: abolish BIC
    -1.5,  #  4  ethnic_quotas: mildly meritocratic
    -1.0,  #  5  fertility: mild population control
    -2.0,  #  6  constitutional: parliamentary
    +1.0,  #  7  resource: mild local control
    +1.5,  #  8  housing: mild intervention
    +1.0,  #  9  education: mild centralism
    +0.5,  # 10  labor: mildly pro-labor
    -4.0,  # 11  military: strong civilian control
    -1.5,  # 12  immigration: mildly open
    +2.0,  # 13  language: pro-English
    +3.5,  # 14  womens_rights: strongly progressive
    -2.5,  # 15  trad_authority: marginalize
    +1.0,  # 16  infrastructure: mildly universal
    +2.0,  # 17  land_tenure: formalization
    +0.5,  # 18  taxation: mild redistribution
    +0.0,  # 19  agriculture: neutral
    +1.5,  # 20  bio_enhancement: moderate pro
    +3.0,  # 21  trade: open
    +2.5,  # 22  environment: regulatory
    +4.5,  # 23  media: strongest press freedom
    +2.0,  # 24  healthcare: universal
    +0.5,  # 25  pada_status: mild pro-Padà
    +2.5,  # 26  energy: green transition
    -1.0,  # 27  az_restructuring: mild restructure
])

# ANPC — All-Nigeria People's Congress
# Centrist catch-all party that tries to bridge north-south, Muslim-Christian,
# and urban-rural divides. Moderate on nearly everything, slightly favoring
# fiscal autonomy and press freedom. Often accused of standing for nothing;
# supporters say it stands for stability. The party of governors who want to
# keep their jobs.
ANPC_POSITIONS = np.array([
    -2.0,  #  0  sharia: moderately secular
    +3.0,  #  1  fiscal: fiscal autonomy
    -1.5,  #  2  chinese: mild Western lean
    -1.0,  #  3  bic: mildly anti-BIC
    +1.5,  #  4  ethnic_quotas: mild affirmative action
    +1.0,  #  5  fertility: mildly pro-natalist
    +1.5,  #  6  constitutional: mildly presidential
    +1.5,  #  7  resource: mild local control
    +0.5,  #  8  housing: mildly interventionist
    -1.0,  #  9  education: mildly localist
    -0.5,  # 10  labor: centrist
    -1.5,  # 11  military: mild civilian control
    +1.0,  # 12  immigration: mildly restrictionist
    -1.0,  # 13  language: mildly vernacular
    +1.5,  # 14  womens_rights: moderate progressive
    +1.5,  # 15  trad_authority: mild integration
    -0.5,  # 16  infrastructure: centrist
    +0.5,  # 17  land_tenure: mild formalization
    -0.5,  # 18  taxation: centrist
    -0.5,  # 19  agriculture: centrist
    +1.0,  # 20  bio_enhancement: mild pro
    +1.0,  # 21  trade: mildly open
    +1.0,  # 22  environment: mild regulation
    +2.0,  # 23  media: press freedom
    +1.0,  # 24  healthcare: mildly universal
    -1.5,  # 25  pada_status: mildly anti-Padà
    +0.5,  # 26  energy: mild green
    -3.0,  # 27  az_restructuring: restructure to states
])

# IPA — Igbo Progressive Alliance
# Southeastern autonomist party built on Igbo commercial networks and diaspora
# capital. Strongly pro-fiscal autonomy and meritocracy, secular, and
# pro-trade openness. Skeptical of both northern Islamic institutions and
# Lagos-based technocratic elitism. Wants strong local resource control and
# formal land tenure. The party of Onitsha traders and Aba manufacturers.
IPA_POSITIONS = np.array([
    -3.0,  #  0  sharia: secular
    +3.5,  #  1  fiscal: strong autonomy
    -2.5,  #  2  chinese: Western pivot
    -1.5,  #  3  bic: mildly anti-BIC
    -2.5,  #  4  ethnic_quotas: meritocratic
    +0.5,  #  5  fertility: mildly pro-natalist
    +1.0,  #  6  constitutional: mildly presidential
    +2.5,  #  7  resource: strong local control
    -1.5,  #  8  housing: mildly market
    +1.5,  #  9  education: mild centralism
    -3.0,  # 10  labor: pro-capital
    -2.0,  # 11  military: civilian control
    +0.5,  # 12  immigration: centrist
    +1.5,  # 13  language: pro-English
    +1.0,  # 14  womens_rights: mildly progressive
    -1.5,  # 15  trad_authority: mildly marginalize
    -2.0,  # 16  infrastructure: targeted
    +3.0,  # 17  land_tenure: formalization
    -3.0,  # 18  taxation: low tax
    -2.5,  # 19  agriculture: free market
    +2.5,  # 20  bio_enhancement: pro-access
    +1.5,  # 21  trade: open
    -2.0,  # 22  environment: growth first
    +2.0,  # 23  media: press freedom
    -1.5,  # 24  healthcare: mildly market
    -0.5,  # 25  pada_status: mildly anti-Padà
    -1.0,  # 26  energy: mild fossil
    -1.5,  # 27  az_restructuring: mild restructure
])

# NDC — Northern Democratic Congress
# Northern Muslim establishment party. Pro-sharia, pro-ethnic quotas,
# pro-natalist, and supportive of traditional authority — but within
# democratic norms and existing AZ structures. Represents the Hausa-Fulani
# political mainstream: conservative on social issues, moderately statist on
# economics, and deeply suspicious of both Lagos cosmopolitanism and radical
# Islamism.
NDC_POSITIONS = np.array([
    +3.0,  #  0  sharia: pro-sharia
    +2.5,  #  1  fiscal: autonomy
    -0.5,  #  2  chinese: mildly Western
    -3.0,  #  3  bic: abolish BIC
    +3.5,  #  4  ethnic_quotas: strong affirmative action
    +3.0,  #  5  fertility: pro-natalist
    +3.0,  #  6  constitutional: presidential
    +2.0,  #  7  resource: local control
    +1.0,  #  8  housing: mild intervention
    -2.5,  #  9  education: localist
    +0.5,  # 10  labor: mildly pro-labor
    +0.5,  # 11  military: mild guardianship
    +3.0,  # 12  immigration: restrictionist
    -2.0,  # 13  language: vernacular
    -2.0,  # 14  womens_rights: conservative
    +3.0,  # 15  trad_authority: integration
    +3.0,  # 16  infrastructure: universal
    -1.5,  # 17  land_tenure: customary
    +1.0,  # 18  taxation: mild redistribution
    +2.5,  # 19  agriculture: protectionist
    -1.5,  # 20  bio_enhancement: against
    -0.5,  # 21  trade: mildly autarkic
    -1.0,  # 22  environment: growth first
    +1.0,  # 23  media: mildly free press
    +2.5,  # 24  healthcare: universal
    -3.0,  # 25  pada_status: anti-Padà
    -1.5,  # 26  energy: fossil
    -1.5,  # 27  az_restructuring: mild restructure
])

# UJP — Ummah Justice Party
# Islamist party anchored in the Al-Shahid movement and the northeastern
# Kanuri heartland. Full sharia jurisdiction, strong pro-natalism, aggressive
# anti-Padà, anti-bio-enhancement, and deep hostility to secular governance.
# Economically redistributive within an Islamic framework. The most
# ideologically coherent party in the system — and the most polarizing.
UJP_POSITIONS = np.array([
    +4.0,  #  0  sharia: near-full sharia
    +3.5,  #  1  fiscal: strong autonomy
    -1.0,  #  2  chinese: mildly Western
    -3.5,  #  3  bic: abolish BIC
    +3.0,  #  4  ethnic_quotas: affirmative action
    +4.0,  #  5  fertility: strongly pro-natalist
    +2.5,  #  6  constitutional: presidential
    +1.5,  #  7  resource: mild local control
    +2.0,  #  8  housing: interventionist
    -3.5,  #  9  education: localist/Islamic
    +2.0,  # 10  labor: pro-labor
    -1.0,  # 11  military: mildly civilian
    +2.0,  # 12  immigration: restrictionist
    -3.0,  # 13  language: vernacular/Arabic
    -3.5,  # 14  womens_rights: conservative
    +2.5,  # 15  trad_authority: integration
    +3.5,  # 16  infrastructure: universal
    -2.5,  # 17  land_tenure: customary
    +2.5,  # 18  taxation: redistribution
    +3.5,  # 19  agriculture: protectionist
    -3.5,  # 20  bio_enhancement: prohibition
    -1.5,  # 21  trade: autarkic
    +0.5,  # 22  environment: mild regulation
    +0.5,  # 23  media: centrist
    +3.5,  # 24  healthcare: universal
    -3.5,  # 25  pada_status: anti-Padà
    -0.5,  # 26  energy: centrist
    -2.0,  # 27  az_restructuring: mild restructure
])

# NWF — Nigerian Workers' Front
# Urban labor-left party strongest among factory workers, gig laborers, and
# informal-sector unions. Among the highest scores on labor protection, housing
# intervention, taxation/redistribution, and healthcare — second only to the
# more radical PLF. Skeptical of both capital and traditional authority.
# Cosmopolitan by default rather than ideology — its base crosses ethnic lines
# in the industrial belts of Lagos, Kano, and Port Harcourt.
NWF_POSITIONS = np.array([
    -1.0,  #  0  sharia: mildly secular
    -1.5,  #  1  fiscal: mildly centralist
    -1.0,  #  2  chinese: mildly Western
    -1.0,  #  3  bic: mildly anti-BIC
    +1.0,  #  4  ethnic_quotas: mild affirmative action
    -0.5,  #  5  fertility: centrist
    -1.5,  #  6  constitutional: mildly parliamentary
    -1.0,  #  7  resource: mildly federal
    +4.0,  #  8  housing: strong state intervention
    +0.5,  #  9  education: centrist
    +4.5,  # 10  labor: near-strongest pro-labor
    -2.5,  # 11  military: civilian control
    +1.5,  # 12  immigration: mildly restrictionist
    -2.0,  # 13  language: vernacular
    +2.0,  # 14  womens_rights: progressive
    -1.5,  # 15  trad_authority: mildly marginalize
    +3.0,  # 16  infrastructure: universal
    -1.0,  # 17  land_tenure: mildly customary
    +4.0,  # 18  taxation: high redistribution
    +3.0,  # 19  agriculture: protectionist
    +3.0,  # 20  bio_enhancement: pro-access
    -2.0,  # 21  trade: autarkic
    +2.0,  # 22  environment: regulatory
    +3.0,  # 23  media: press freedom
    +4.0,  # 24  healthcare: universal
    -2.0,  # 25  pada_status: mildly anti-Padà
    +1.0,  # 26  energy: mild green
    +0.0,  # 27  az_restructuring: neutral
])

# NHA — New Horizon Alliance
# Techno-futurist party built around the Naijin diaspora-return community and
# WAFTA-aligned business networks. Strongest pro-WAFTA position in the system.
# Pro-bio-enhancement, pro-trade openness, and aggressively pro-education
# centralism. Mildly favors multilingualism over English supremacy, reflecting
# Naijin comfort with Mandarin as a co-prestige language. Culturally liberal
# but economically globalist. The party of people who think Nigeria's future
# is in Shenzhen, not Washington or Abuja.
NHA_POSITIONS = np.array([
    -2.5,  #  0  sharia: secular
    -1.0,  #  1  fiscal: mildly centralist
    +4.5,  #  2  chinese: strongest WAFTA
    +1.5,  #  3  bic: mild BIC preservation
    -2.0,  #  4  ethnic_quotas: meritocratic
    -2.5,  #  5  fertility: population control
    -2.5,  #  6  constitutional: parliamentary
    -1.5,  #  7  resource: mildly federal
    +2.5,  #  8  housing: interventionist
    +4.0,  #  9  education: strongest centralism
    -1.5,  # 10  labor: mildly pro-capital
    +0.5,  # 11  military: centrist
    -2.0,  # 12  immigration: moderately open
    -1.0,  # 13  language: mildly vernacular
    +2.0,  # 14  womens_rights: progressive
    -3.0,  # 15  trad_authority: marginalize
    -1.0,  # 16  infrastructure: mildly targeted
    +2.5,  # 17  land_tenure: formalization
    +1.5,  # 18  taxation: mild redistribution
    -1.0,  # 19  agriculture: free market
    +3.0,  # 20  bio_enhancement: strong pro-access
    +3.5,  # 21  trade: strongly open
    +1.5,  # 22  environment: mild regulation
    -0.5,  # 23  media: centrist
    +2.5,  # 24  healthcare: universal
    +1.0,  # 25  pada_status: mild pro-Padà
    +2.0,  # 26  energy: green
    +2.0,  # 27  az_restructuring: keep AZs
])

# SNM — Sovereign Nigeria Movement
# Economic nationalist and sovereigntist party. Fiercely anti-WAFTA,
# anti-immigration, anti-Padà, and anti-trade openness. Wants to reassert
# Nigerian economic independence from Chinese influence. Pro-housing and
# pro-healthcare but through autarkic industrial policy, not redistribution.
# Appeals to northern traders squeezed by WAFTA competition and southern small
# manufacturers facing Chinese imports.
SNM_POSITIONS = np.array([
    -1.5,  #  0  sharia: mildly secular
    +1.0,  #  1  fiscal: mild autonomy
    -4.0,  #  2  chinese: fiercely anti-WAFTA
    -2.5,  #  3  bic: anti-BIC
    +2.0,  #  4  ethnic_quotas: affirmative action
    +2.5,  #  5  fertility: pro-natalist
    +2.0,  #  6  constitutional: presidential
    +2.0,  #  7  resource: local control
    +3.0,  #  8  housing: strong intervention
    -1.5,  #  9  education: mildly localist
    +2.5,  # 10  labor: pro-labor
    +1.5,  # 11  military: mild guardianship
    +4.5,  # 12  immigration: near-strongest restrictionism
    -1.5,  # 13  language: mildly vernacular
    -0.5,  # 14  womens_rights: mildly conservative
    +1.0,  # 15  trad_authority: mild integration
    +2.0,  # 16  infrastructure: universal
    -1.0,  # 17  land_tenure: mildly customary
    +2.0,  # 18  taxation: redistribution
    +2.0,  # 19  agriculture: protectionist
    -0.5,  # 20  bio_enhancement: mildly against
    -4.0,  # 21  trade: strong autarky
    -1.5,  # 22  environment: growth first
    +1.5,  # 23  media: mild press freedom
    +2.5,  # 24  healthcare: universal
    -4.5,  # 25  pada_status: strongly anti-Padà
    -2.0,  # 26  energy: fossil
    -1.0,  # 27  az_restructuring: mild restructure
])

# NSA — National Security Alliance
# Authoritarian-securitarian party. Among the strongest positions on military
# guardianship and presidential power in the system, second only to the NNV.
# Anti-press freedom, pro-centralism, and hawkish on immigration. Draws
# support from military families, security contractors, and populations in
# conflict-affected zones who want order above all else. Not ideological so
# much as dispositional: the party of people who think civilians talk too
# much.
NSA_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular
    -3.0,  #  1  fiscal: centralist
    +0.5,  #  2  chinese: centrist
    +2.5,  #  3  bic: preserve BIC
    -2.0,  #  4  ethnic_quotas: meritocratic
    +1.0,  #  5  fertility: mildly pro-natalist
    +3.5,  #  6  constitutional: strongly presidential
    -2.5,  #  7  resource: federal control
    +0.5,  #  8  housing: centrist
    +2.0,  #  9  education: centralism
    -1.0,  # 10  labor: mildly pro-capital
    +4.5,  # 11  military: strongest guardianship
    +2.5,  # 12  immigration: restrictionist
    +3.0,  # 13  language: English supremacy
    +0.5,  # 14  womens_rights: centrist
    -1.0,  # 15  trad_authority: mildly marginalize
    +0.5,  # 16  infrastructure: centrist
    +1.5,  # 17  land_tenure: mild formalization
    -0.5,  # 18  taxation: centrist
    +0.5,  # 19  agriculture: centrist
    +2.0,  # 20  bio_enhancement: pro-access
    +0.5,  # 21  trade: mildly open
    -1.0,  # 22  environment: growth first
    -3.0,  # 23  media: state control
    +1.0,  # 24  healthcare: mildly universal
    +2.0,  # 25  pada_status: pro-Padà
    -1.5,  # 26  energy: fossil
    +3.0,  # 27  az_restructuring: keep AZs
])

# CDA — Christian Democratic Alliance
# Christian identity party strongest in the Middle Belt and southeastern
# borderlands. Aggressively anti-sharia, pro-natalist, and socially
# conservative within a Christian moral framework. Moderate on economics,
# mildly pro-fiscal autonomy. Not ethno-nationalist — its Christianity is the
# organizing principle, cutting across Tiv, Igbo, and southern minority lines.
# The party of Sunday morning before the ballot box.
CDA_POSITIONS = np.array([
    -4.0,  #  0  sharia: aggressively anti-sharia
    +1.5,  #  1  fiscal: mild autonomy
    -2.0,  #  2  chinese: Western lean
    +0.5,  #  3  bic: mildly preserve
    +0.5,  #  4  ethnic_quotas: mildly pro
    +4.0,  #  5  fertility: strongly pro-natalist
    +1.0,  #  6  constitutional: mildly presidential
    +1.0,  #  7  resource: mild local control
    +1.5,  #  8  housing: mildly interventionist
    -0.5,  #  9  education: centrist
    +1.0,  # 10  labor: mildly pro-labor
    -0.5,  # 11  military: centrist
    +1.5,  # 12  immigration: mildly restrictionist
    +1.5,  # 13  language: mildly English
    -2.5,  # 14  womens_rights: socially conservative
    +1.0,  # 15  trad_authority: mild integration
    +1.5,  # 16  infrastructure: mildly universal
    +0.5,  # 17  land_tenure: mild formalization
    +0.5,  # 18  taxation: centrist
    +1.5,  # 19  agriculture: mildly protectionist
    -2.5,  # 20  bio_enhancement: against
    +1.0,  # 21  trade: mildly open
    +0.5,  # 22  environment: centrist
    +1.5,  # 23  media: mildly free press
    +2.0,  # 24  healthcare: universal
    -1.5,  # 25  pada_status: mildly anti-Padà
    +0.5,  # 26  energy: mild green
    -1.0,  # 27  az_restructuring: mild restructure
])

# MBPP — Middle Belt People's Party
# Regional party of the Middle Belt minorities — Plateau, Benue, Nassarawa,
# and southern Kaduna communities. Strongest position on traditional authority
# integration in the system. Near-strongest on infrastructure provision and
# healthcare. Pro-fiscal autonomy and local resource control. Represents
# populations caught between northern Islamic hegemony and southern commercial
# dominance, demanding recognition and development on their own terms.
MBPP_POSITIONS = np.array([
    -2.5,  #  0  sharia: secular
    +2.0,  #  1  fiscal: autonomy
    +0.0,  #  2  chinese: neutral
    -2.0,  #  3  bic: anti-BIC
    +4.0,  #  4  ethnic_quotas: strong affirmative action
    +1.5,  #  5  fertility: mildly pro-natalist
    -3.5,  #  6  constitutional: strongly parliamentary
    +3.5,  #  7  resource: strong local control
    +2.0,  #  8  housing: interventionist
    -2.0,  #  9  education: localist
    +1.5,  # 10  labor: mildly pro-labor
    -2.0,  # 11  military: civilian control
    +0.5,  # 12  immigration: centrist
    -3.0,  # 13  language: vernacular
    +0.5,  # 14  womens_rights: centrist
    +3.5,  # 15  trad_authority: strong integration
    +4.0,  # 16  infrastructure: strongest universal
    -2.0,  # 17  land_tenure: customary
    +2.5,  # 18  taxation: redistribution
    +3.0,  # 19  agriculture: protectionist
    +0.5,  # 20  bio_enhancement: mildly pro
    +0.0,  # 21  trade: neutral
    +3.0,  # 22  environment: strong regulation
    +3.0,  # 23  media: press freedom
    +3.5,  # 24  healthcare: universal
    -2.5,  # 25  pada_status: anti-Padà
    +2.5,  # 26  energy: green
    -4.5,  # 27  az_restructuring: strongly restructure
])

# PLF — People's Liberation Front
# Radical left party rooted in Niger Delta resource activism and Lagos slum
# organizing. Highest scores on labor, housing, taxation, healthcare, and
# infrastructure in the entire system. Centralist on general fiscal policy
# but fiercely pro-local-resource-control — the oil belongs to the people
# who live above it. Moderately pro-WAFTA, seeing Chinese capital as a
# useful counterweight to Western multinationals. Favors state media
# discipline over press freedom, viewing private media as captured by
# oligarchs. Anti-traditional authority and supportive of keeping the AZ
# system that weakens old regional power structures. The party of people
# who have been promised development for sixty years and received pipeline
# explosions.
PLF_POSITIONS = np.array([
    -4.0,  #  0  sharia: strongly secular
    -3.0,  #  1  fiscal: centralist (but less extreme — resource revenue is separate)
    +2.5,  #  2  chinese: moderate WAFTA
    -2.0,  #  3  bic: anti-BIC
    +2.0,  #  4  ethnic_quotas: affirmative action
    -3.0,  #  5  fertility: population control
    -3.5,  #  6  constitutional: strongly parliamentary
    +3.0,  #  7  resource: strong local control (Niger Delta core demand)
    +5.0,  #  8  housing: maximum intervention
    +3.0,  #  9  education: centralism
    +5.0,  # 10  labor: maximum pro-labor
    -3.0,  # 11  military: civilian control
    -3.5,  # 12  immigration: open borders
    -3.0,  # 13  language: vernacular
    +4.0,  # 14  womens_rights: aggressively progressive
    -5.0,  # 15  trad_authority: total marginalization
    +4.5,  # 16  infrastructure: near-maximum universal
    -4.5,  # 17  land_tenure: radical customary
    +5.0,  # 18  taxation: maximum redistribution
    +4.5,  # 19  agriculture: strong protectionist
    +4.0,  # 20  bio_enhancement: strong pro-access
    -3.5,  # 21  trade: autarkic
    +3.0,  # 22  environment: strong regulation
    -2.5,  # 23  media: mildly state-controlled
    +5.0,  # 24  healthcare: maximum universal
    -4.0,  # 25  pada_status: anti-Padà
    +3.0,  # 26  energy: green
    +3.5,  # 27  az_restructuring: mildly keep AZs
])

# NNV — Nigerian National Vanguard
# Hyper-nationalist authoritarian party. Strongest positions on military
# guardianship, presidential power, immigration restriction, and anti-press
# freedom in the entire system. Combines extreme centralism with cultural
# conservatism and aggressive pro-natalism. Anti-sharia but not secularist —
# draws on pre-Islamic traditional identity and military-state ideology. The
# party for people who think what Nigeria needs is a man on horseback and a
# closed border.
NNV_POSITIONS = np.array([
    -4.5,  #  0  sharia: strongly anti-sharia
    -4.0,  #  1  fiscal: extreme centralism
    -3.5,  #  2  chinese: anti-WAFTA
    +4.5,  #  3  bic: strongly preserve BIC
    -4.5,  #  4  ethnic_quotas: extreme meritocracy
    +4.5,  #  5  fertility: extreme pro-natalist
    +5.0,  #  6  constitutional: maximum presidential
    -3.5,  #  7  resource: federal monopoly
    +2.5,  #  8  housing: interventionist
    +4.5,  #  9  education: strongest centralism
    +1.0,  # 10  labor: mildly pro-labor
    +5.0,  # 11  military: maximum guardianship
    +5.0,  # 12  immigration: maximum restrictionism
    +5.0,  # 13  language: maximum English supremacy
    -1.0,  # 14  womens_rights: mildly conservative
    -4.5,  # 15  trad_authority: extreme marginalization
    +1.5,  # 16  infrastructure: mildly universal
    +4.0,  # 17  land_tenure: strong formalization
    +1.5,  # 18  taxation: mild redistribution
    +1.5,  # 19  agriculture: mildly protectionist
    +4.5,  # 20  bio_enhancement: extreme pro-access
    -2.5,  # 21  trade: autarkic
    -3.5,  # 22  environment: growth first
    -5.0,  # 23  media: maximum state control
    +2.5,  # 24  healthcare: universal
    +1.5,  # 25  pada_status: mildly pro-Padà
    -3.5,  # 26  energy: fossil
    +4.5,  # 27  az_restructuring: strongly keep AZs
])

# Validation check
for name, pos in [
    ("NRP", NRP_POSITIONS), ("CND", CND_POSITIONS),
    ("ANPC", ANPC_POSITIONS), ("IPA", IPA_POSITIONS),
    ("NDC", NDC_POSITIONS), ("UJP", UJP_POSITIONS),
    ("NWF", NWF_POSITIONS), ("NHA", NHA_POSITIONS),
    ("SNM", SNM_POSITIONS), ("NSA", NSA_POSITIONS),
    ("CDA", CDA_POSITIONS), ("MBPP", MBPP_POSITIONS),
    ("PLF", PLF_POSITIONS), ("NNV", NNV_POSITIONS),
]:
    assert pos.shape == (N_ISSUES,), f"{name} position shape mismatch"
    assert np.all(np.abs(pos) <= 5.0), f"{name} has out-of-range positions"

PARTIES = [
    Party(
        name="NRP",
        positions=NRP_POSITIONS,
        valence=0.2,  # strong brand in educated urban constituencies
        leader_ethnicity="Pada",
        religious_alignment="Secular",
    ),
    Party(
        name="CND",
        positions=CND_POSITIONS,
        valence=0.1,  # established party brand
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
    ),
    Party(
        name="ANPC",
        positions=ANPC_POSITIONS,
        valence=0.0,
        leader_ethnicity="Edo",
        religious_alignment="Catholic",
    ),
    Party(
        name="IPA",
        positions=IPA_POSITIONS,
        valence=0.0,
        leader_ethnicity="Igbo",
        religious_alignment="Pentecostal",
    ),
    Party(
        name="NDC",
        positions=NDC_POSITIONS,
        valence=0.1,  # deep organizational roots across the north
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
    ),
    Party(
        name="UJP",
        positions=UJP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Kanuri",
        religious_alignment="Al-Shahid",
    ),
    Party(
        name="NWF",
        positions=NWF_POSITIONS,
        valence=0.0,
        leader_ethnicity="Ibibio",
        religious_alignment="Secular",
    ),
    Party(
        name="NHA",
        positions=NHA_POSITIONS,
        valence=0.15,  # WAFTA funding and organizational capacity
        leader_ethnicity="Naijin",
        religious_alignment="Secular",
    ),
    Party(
        name="SNM",
        positions=SNM_POSITIONS,
        valence=0.0,
        leader_ethnicity="Hausa",
        religious_alignment="Tijaniyya",
    ),
    Party(
        name="NSA",
        positions=NSA_POSITIONS,
        valence=0.0,
        leader_ethnicity="Fulani",
        religious_alignment="Mainstream Sunni",
    ),
    Party(
        name="CDA",
        positions=CDA_POSITIONS,
        valence=0.0,
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
    ),
    Party(
        name="MBPP",
        positions=MBPP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Middle Belt Minorities",
        religious_alignment="Mainline Protestant",
    ),
    Party(
        name="PLF",
        positions=PLF_POSITIONS,
        valence=-0.1,  # organizational weakness, radical stigma
        leader_ethnicity="Ijaw",
        religious_alignment="Secular",
    ),
    Party(
        name="NNV",
        positions=NNV_POSITIONS,
        valence=-0.1,  # extreme positions limit broad appeal
        leader_ethnicity="Nupe",
        religious_alignment="Traditionalist",
    ),
]


def main():
    params = EngineParams(
        q=0.5, beta_s=0.7, alpha_e=3.0, alpha_r=2.0,
        scale=1.0, tau_0=1.9, tau_1=0.3, tau_2=0.5,
        kappa=400.0, sigma_national=0.07, sigma_regional=0.10,
    )
    config = ElectionConfig(params=params, parties=PARTIES, n_monte_carlo=100)

    data_path = Path(__file__).parent.parent / "data" / "nigeria_lga_polsim_2058.xlsx"
    results = run_election(data_path, config, seed=2058, verbose=True)

    # ---- Print summary ----
    summary = results["summary"]

    print("\n" + "=" * 60)
    print("LAGOS-2058 ELECTION RESULTS SUMMARY")
    print("=" * 60)

    print("\nNational Vote Shares (base run):")
    for p, share in sorted(summary["national_shares"].items(), key=lambda x: -x[1]):
        print(f"  {p:10s}  {share:.1%}")

    print(f"\nNational Turnout (base run): {summary['national_turnout']:.1%}")

    print(f"\nSwing LGAs: {len(results['mc_aggregated']['swing_lgas'])}")

    party_names = [p.name for p in PARTIES]
    state_shares = compute_state_shares(results["lga_results_base"], party_names)
    share_cols = [c for c in state_shares.columns if c.endswith("_share")]
    print("\nVote Shares per State (base run):")
    print(state_shares[["State"] + share_cols].to_string(index=False))

    print("\nZonal Shares (base run):")
    zonal = summary["zonal_shares"]
    party_share_cols = [c for c in zonal.columns if c.endswith("_share")]
    print(zonal[["Administrative Zone", "AZ Name"] + party_share_cols].to_string(index=False))

    print("\nTop 10 Swing LGAs:")
    swing = results["mc_aggregated"]["swing_lgas"]
    if len(swing) > 0:
        # Sort by margin (smallest = most competitive) so head(10) is meaningful
        share_cols = [c for c in swing.columns if c.endswith("_share")]
        shares = swing[share_cols].values
        sorted_shares = np.sort(shares, axis=1)
        swing = swing.copy()
        swing["_margin"] = sorted_shares[:, -1] - sorted_shares[:, -2]
        swing = swing.sort_values("_margin")
        print(swing.head(10)[["State", "LGA Name"]].to_string(index=False))
    else:
        print("  None (all LGAs have stable winners across MC runs)")


if __name__ == "__main__":
    main()
