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
from election_engine.results import (
    compute_vote_counts, compute_state_vote_counts,
    compute_competitiveness, compute_vote_source_decomposition,
    compute_coalition_feasibility, compute_demographic_vote_profile,
    allocate_district_seats,
)

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
    -0.5,  # 19  agriculture: mildly free-market — Yoruba urban elite, consumer prices matter
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
    -1.0,  # 27  az_restructuring: mildly pro-restructure — smaller states help workers organise
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
# Technocratic-securitarian party rooted in the professional security
# establishment. Led by a Hausa figure from the northern security
# intelligentsia, the NSA speaks for communities where security is not
# abstract but existential. Distinct from NNV's populist-nationalist
# militarism, the NSA emphasises border control, professional defence
# forces, security infrastructure, and military biotech. Draws support from
# ex-military professionals, CJTF veterans, border communities, and urban
# security contractors. The party of people who've actually seen combat.
NSA_POSITIONS = np.array([
    -1.5,  #  0  sharia: pragmatically secular — security doesn't pray
    -2.5,  #  1  fiscal: centralist — federal security spending
    -2.0,  #  2  chinese: skeptical — security risk from foreign mil-tech
    +1.5,  #  3  bic: mild preserve — institutional stability
    -1.5,  #  4  ethnic_quotas: meritocratic — professional armed forces
    +0.5,  #  5  fertility: neutral — not a priority
    +3.0,  #  6  constitutional: presidential — unified command structure
    -2.0,  #  7  resource: federal control — fund the military
    +1.5,  #  8  housing: interventionist — military housing estates
    +2.5,  #  9  education: centralist — officer training, security academies
    +0.5,  # 10  labor: centrist — pragmatic
    +4.5,  # 11  military: strongest guardianship — core identity
    +4.0,  # 12  immigration: THE border security party
    +2.0,  # 13  language: English — operational language of defence
    +1.0,  # 14  womens_rights: mildly progressive — women in security
    -1.5,  # 15  trad_authority: marginalize — professional over chieftains
    +2.5,  # 16  infrastructure: security infrastructure — roads, comms
    +2.0,  # 17  land_tenure: formalization — cadastral mapping for security
    +1.0,  # 18  taxation: pro-revenue — defence budget needs funding
    +1.5,  # 19  agriculture: food security — strategic food reserves
    +2.5,  # 20  bio_enhancement: pro-access — enhanced soldier programme
    -1.5,  # 21  trade: mildly protectionist — border controls
    -1.5,  # 22  environment: growth first — security over green
    -2.0,  # 23  media: surveillance needs, but professional not total
    +2.0,  # 24  healthcare: veteran/security personnel healthcare
    +1.0,  # 25  pada_status: mild pro — pragmatic, not identity politics
    -1.0,  # 26  energy: mild fossil — energy security
    +2.5,  # 27  az_restructuring: keep AZs — security zones work
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
    -0.5,  #  2  chinese: slight anti-WAFTA — wary of foreign land grabs
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
    -1.0,  # 21  trade: mildly protectionist — protect local farmers from imports
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
# Nationalist-authoritarian party rooted in the military-state tradition.
# Strong on security, centralism, presidential power, and immigration control.
# Led by a Hausa-Fulani former military figure who champions "One Nigeria"
# unity over ethnic/religious politics. Anti-Sharia (favors secular national
# law), pro-English (national unity language), and dirigiste economics.
# Appeals to security-state constituencies: military families, civil servants
# in conflict zones, and northern urban professionals who want order over
# ethnic patronage. Splits the northern vote with NDC by offering a secular
# nationalist alternative to the establishment.
NNV_POSITIONS = np.array([
    -2.5,  #  0  sharia: anti-sharia but not extreme — secular-nationalist, not atheist
    -3.0,  #  1  fiscal: strong centralism — "one Nigeria" ideology
    -2.5,  #  2  chinese: anti-WAFTA — economic nationalism
    +3.0,  #  3  bic: preserve BIC — nationalist institutions
    -2.0,  #  4  ethnic_quotas: meritocratic — oppose ethnic patronage
    +3.0,  #  5  fertility: pro-natalist — "populate or perish" nationalism
    +4.0,  #  6  constitutional: strongly presidential — strongman governance
    -2.5,  #  7  resource: federal control — central resource management
    +2.0,  #  8  housing: interventionist — state-built housing projects
    +3.0,  #  9  education: centralist — national curriculum, discipline
    +1.5,  # 10  labor: pro-labor — nationalist workers' solidarity
    +4.0,  # 11  military: strong guardianship — security state
    +3.5,  # 12  immigration: restrictionist — "Nigeria for Nigerians"
    +3.0,  # 13  language: English — unifying national language
    -0.5,  # 14  womens_rights: mildly conservative — traditional family
    -1.5,  # 15  trad_authority: marginalize — military over chiefs, but not extreme
    +1.5,  # 16  infrastructure: universal — national development projects
    +2.5,  # 17  land_tenure: formalization — state land management
    +1.5,  # 18  taxation: mild redistribution — statist economics
    +2.0,  # 19  agriculture: protectionist — food sovereignty
    +1.0,  # 20  bio_enhancement: cautious pro — national competitiveness
    -2.0,  # 21  trade: protectionist — economic nationalism
    -2.0,  # 22  environment: growth first — development priority
    -3.5,  # 23  media: state control — information management
    +2.0,  # 24  healthcare: universal — national health service
    +0.5,  # 25  pada_status: mild pro-Padà — all Nigerians matter
    -2.0,  # 26  energy: fossil — energy independence over green
    +3.5,  # 27  az_restructuring: keep AZs — national unity
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

# ---------------------------------------------------------------------------
# Administrative Zone reference (for regional_strongholds):
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
        name="NRP",
        positions=NRP_POSITIONS,
        valence=0.2,  # strong brand in educated urban constituencies
        leader_ethnicity="Pada",
        religious_alignment="Secular",
        economic_positioning=-0.6,  # pro-market liberal, appeals to prosperous areas
        demographic_coefficients={
            "education": {"Tertiary": 0.5, "Secondary": 0.15},
            "livelihood": {"Formal private": 0.5, "Public sector": 0.25,
                           "Trade/informal": 0.1},
            "income": {"Top 20%": 0.4, "Middle 40%": 0.15},
            "age_cohort": {"25-34": 0.25, "35-49": 0.15, "50+": -0.1},
            "setting": {"Urban": 0.35, "Peri-urban": 0.1},
            "gender": {"Female": 0.15},
        },
        regional_strongholds={
            1: +0.5,   # Lagos: cosmopolitan Padà heartland (first elections: less consolidation)
            2: +0.15,  # Niger Zone: Ogun/Oyo spillover from Lagos, Ibadan elite
            3: +0.15,  # Confluence: Ekiti/Ondo professional class
            5: +0.1,   # Eastern: Igbo business-professional overlap
        },
    ),
    Party(
        name="CND",
        positions=CND_POSITIONS,
        valence=0.1,  # established party brand
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.3,  # centre-left, social-democratic lean
        demographic_coefficients={
            "education": {"Tertiary": 0.3, "Secondary": 0.1},
            "livelihood": {"Public sector": 0.3, "Formal private": 0.1},
            "income": {"Middle 40%": 0.15, "Top 20%": 0.1},
            "age_cohort": {"25-34": 0.15, "35-49": 0.1},
            "setting": {"Urban": 0.2, "Peri-urban": 0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.2,   # Lagos: progressive intelligentsia (first elections: less consolidation)
            2: +0.3,   # Niger Zone: Yoruba heartland (Oyo, Ogun)
            3: +0.25,  # Confluence: Ekiti, Ondo, Osun
            4: +0.05,  # Littoral: educated Yoruba diaspora in Delta/Rivers
            6: +0.05,  # Central: civil servants, progressive professionals in FCT
        },
    ),
    Party(
        name="ANPC",
        positions=ANPC_POSITIONS,
        valence=0.0,
        leader_ethnicity="Edo",
        religious_alignment="Catholic",
        economic_positioning=0.1,  # centrist catch-all, mild populist lean
        demographic_coefficients={
            "education": {"Secondary": 0.2, "Tertiary": 0.1, "Below secondary": 0.05},
            "livelihood": {"Public sector": 0.2, "Formal private": 0.1,
                           "Trade/informal": 0.1, "Smallholder": 0.05},
            "income": {"Middle 40%": 0.15, "Bottom 40%": 0.05},
            "age_cohort": {"35-49": 0.15, "25-34": 0.1, "50+": 0.05},
            "setting": {"Peri-urban": 0.15, "Urban": 0.05},
            "gender": {"Female": 0.1, "Male": 0.05},
        },
        # Catch-all party: broad but shallow — mild bonus everywhere
        regional_strongholds={
            3: +0.3,   # Confluence: Edo is home base
            4: +0.2,   # Littoral: moderate appeal
            2: +0.1,   # Niger Zone: catch-all appeal
            1: +0.1,   # Lagos: centrist appeal to moderates
            5: +0.1,   # Eastern: Catholic connection, southern solidarity
        },
    ),
    Party(
        name="IPA",
        positions=IPA_POSITIONS,
        valence=0.0,
        leader_ethnicity="Igbo",
        religious_alignment="Pentecostal",
        economic_positioning=-0.4,  # pro-commerce, entrepreneurial ethos
        demographic_coefficients={
            "education": {"Tertiary": 0.2, "Secondary": 0.1},
            "livelihood": {"Trade/informal": 0.4, "Formal private": 0.3},
            "income": {"Top 20%": 0.3, "Middle 40%": 0.1},
            "age_cohort": {"25-34": 0.15, "35-49": 0.1},
            "setting": {"Urban": 0.2, "Peri-urban": 0.1},
            "gender": {"Male": 0.1},
        },
        regional_strongholds={
            5: +0.6,   # Eastern Zone: Igbo commercial heartland (first elections: less consolidation)
            1: +0.1,   # Lagos: Igbo diaspora traders
            4: +0.1,   # Littoral: Igbo communities in Port Harcourt, Calabar
            3: +0.05,  # Confluence: Igbo traders in Benin City, Kogi towns
        },
    ),
    Party(
        name="NDC",
        positions=NDC_POSITIONS,
        valence=0.1,  # deep organizational roots across the north
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.2,  # paternalist-populist, patronage economy
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.3, "Public sector": 0.25,
                           "Trade/informal": 0.1, "Commercial ag": 0.1},
            "age_cohort": {"35-49": 0.15, "50+": 0.25, "25-34": 0.05},
            "education": {"Below secondary": 0.15, "Secondary": 0.05},
            "gender": {"Male": 0.15},
            "income": {"Bottom 40%": 0.15, "Middle 40%": 0.1},
            "setting": {"Rural": 0.15, "Peri-urban": 0.05},
        },
        regional_strongholds={
            6: +0.4,   # Central: Kano is HF stronghold (first elections: less consolidation)
            7: +0.3,   # Chad: northern establishment networks, Bauchi/Gombe emirate tradition
            8: +0.5,   # Savanna: Arewa core — deepest party machinery
            2: +0.15,  # Niger Zone: northern extension (Niger, Kwara)
        },
    ),
    Party(
        name="UJP",
        positions=UJP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Kanuri",
        religious_alignment="Al-Shahid",
        economic_positioning=0.7,  # Islamist welfare state, strongly pro-poor
        demographic_coefficients={
            "income": {"Bottom 40%": 0.35, "Middle 40%": 0.05},
            "education": {"Below secondary": 0.3, "Secondary": 0.05},
            "age_cohort": {"18-24": 0.35, "25-34": 0.15, "35-49": 0.05},
            "gender": {"Male": 0.25},
            "livelihood": {"Smallholder": 0.25, "Trade/informal": 0.15,
                           "Unemployed/student": 0.2},
            "setting": {"Rural": 0.15, "Peri-urban": 0.1},
        },
        regional_strongholds={
            7: +1.0,   # Chad: Al-Shahid movement heartland (Borno, Yobe)
            8: +0.4,   # Savanna: some Shahid influence
            6: +0.15,  # Central: Kano Al-Shahid community presence
        },
    ),
    Party(
        name="NWF",
        positions=NWF_POSITIONS,
        valence=0.0,
        leader_ethnicity="Ibibio",
        religious_alignment="Secular",
        economic_positioning=0.8,  # labour party, strongly pro-worker/pro-poor
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.5, "Formal private": 0.3,
                           "Unemployed/student": 0.3},
            "income": {"Bottom 40%": 0.3},
            "education": {"Below secondary": 0.2, "Secondary": 0.1, "Tertiary": -0.2},
            "age_cohort": {"18-24": 0.3, "25-34": 0.2, "35-49": 0.1, "50+": -0.1},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.4,   # Lagos: urban factory & gig workers
            6: +0.3,   # Central: Kano industrial zone
            4: +0.3,   # Littoral: Port Harcourt industrial workers
            5: +0.2,   # Eastern: Cross River/Akwa Ibom — Ibibio core, industrial
            3: +0.1,   # Confluence: Kogi industrial workers
        },
    ),
    Party(
        name="NHA",
        positions=NHA_POSITIONS,
        valence=0.15,  # WAFTA funding and organizational capacity
        leader_ethnicity="Naijin",
        religious_alignment="Secular",
        economic_positioning=-0.5,  # tech-elite, globalist, pro-market
        demographic_coefficients={
            "education": {"Tertiary": 0.4, "Secondary": 0.15},
            "livelihood": {"Formal private": 0.35, "Public sector": 0.15,
                           "Trade/informal": 0.1},
            "income": {"Top 20%": 0.35, "Middle 40%": 0.15},
            "age_cohort": {"18-24": 0.2, "25-34": 0.25, "35-49": -0.05},
            "setting": {"Urban": 0.4, "Peri-urban": 0.1},
            "gender": {"Female": 0.15, "Male": 0.05},
        },
        regional_strongholds={
            1: +0.5,   # Lagos: tech-savvy cosmopolitans
            6: +0.3,   # Central: FCT diaspora-return hub
            3: +0.1,   # Confluence: university town professionals
            4: +0.1,   # Littoral: Port Harcourt tech sector
        },
    ),
    Party(
        name="SNM",
        positions=SNM_POSITIONS,
        valence=0.0,
        leader_ethnicity="Hausa",
        religious_alignment="Tijaniyya",
        economic_positioning=0.5,  # protectionist, defends small traders
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.4, "Smallholder": 0.3,
                           "Formal private": 0.1},
            "income": {"Bottom 40%": 0.2, "Middle 40%": 0.15},
            "education": {"Below secondary": 0.15, "Secondary": 0.1},
            "age_cohort": {"35-49": 0.2, "50+": 0.15, "25-34": 0.05},
            "setting": {"Peri-urban": 0.15, "Rural": 0.1},
            "gender": {"Male": 0.2},
        },
        regional_strongholds={
            8: +0.4,   # Savanna: northern traders squeezed by WAFTA
            6: +0.3,   # Central: Kano market traders
            7: +0.25,  # Chad: anti-WAFTA sentiment
            2: +0.15,  # Niger Zone: market town traders
        },
    ),
    Party(
        name="NSA",
        positions=NSA_POSITIONS,
        valence=0.1,  # professional credibility — "we've been to the front"
        leader_ethnicity="Hausa",
        religious_alignment="Mainstream Sunni",
        economic_positioning=-0.1,  # mildly technocratic, pragmatic
        demographic_coefficients={
            "livelihood": {"Public sector": 0.4, "Formal private": 0.3,
                           "Smallholder": 0.1},
            "education": {"Tertiary": 0.3, "Secondary": 0.15,
                           "Below secondary": 0.05},
            "income": {"Middle 40%": 0.2, "Bottom 40%": 0.1},
            "age_cohort": {"35-49": 0.3, "50+": 0.3, "25-34": 0.1},
            "gender": {"Male": 0.35},
            "setting": {"Urban": 0.15, "Rural": 0.15, "Peri-urban": 0.05},
        },
        regional_strongholds={
            7: +0.7,   # Chad Zone: Borno/Yobe Kanuri heartland, insurgency frontline
            6: +0.3,   # Central: FCT security establishment
            8: +0.3,   # Savanna: banditry-affected communities
            4: +0.1,   # Littoral: oil infrastructure security
        },
    ),
    Party(
        name="CDA",
        positions=CDA_POSITIONS,
        valence=0.0,
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
        economic_positioning=0.4,  # agrarian-populist, pro-smallholder
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.35, "Commercial ag": 0.25,
                           "Public sector": 0.1},
            "income": {"Bottom 40%": 0.15, "Middle 40%": 0.15},
            "age_cohort": {"35-49": 0.15, "50+": 0.25, "25-34": 0.05},
            "education": {"Below secondary": 0.15, "Secondary": 0.15},
            "gender": {"Female": 0.15, "Male": 0.05},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
        },
        regional_strongholds={
            5: +0.6,   # Eastern: Benue (Tiv) + Christian Middle Belt
            6: +0.5,   # Central: Plateau/Nasarawa Christian minorities
            3: +0.3,   # Confluence: Kogi Christian communities
            7: +0.1,   # Chad: Adamawa/Taraba Christian communities
        },
    ),
    Party(
        name="MBPP",
        positions=MBPP_POSITIONS,
        valence=0.0,
        leader_ethnicity="Middle Belt Minorities",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.6,  # agrarian-redistributive, pro-poor farmer
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.45, "Commercial ag": 0.3,
                           "Extraction": 0.15},
            "income": {"Bottom 40%": 0.25, "Middle 40%": 0.1},
            "age_cohort": {"35-49": 0.15, "50+": 0.25, "25-34": 0.05},
            "education": {"Below secondary": 0.2, "Secondary": 0.15},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            6: +0.8,   # Central: Plateau/Nasarawa heartland
            5: +0.5,   # Eastern: Benue solidarity
            3: +0.3,   # Confluence: southern Kogi minorities
            7: +0.1,   # Chad: Taraba/Adamawa minority farming communities
        },
    ),
    Party(
        name="PLF",
        positions=PLF_POSITIONS,
        valence=-0.1,  # organizational weakness, radical stigma
        leader_ethnicity="Ijaw",
        religious_alignment="Secular",
        economic_positioning=0.9,  # radical left, strongest pro-poor positioning
        demographic_coefficients={
            "livelihood": {"Trade/informal": 0.5, "Unemployed/student": 0.5,
                           "Extraction": 0.3, "Smallholder": 0.15},
            "income": {"Bottom 40%": 0.5},
            "education": {"Below secondary": 0.3, "Secondary": 0.1, "Tertiary": -0.3},
            "age_cohort": {"18-24": 0.4, "25-34": 0.25, "35-49": 0.05, "50+": -0.2},
            "gender": {"Male": 0.2, "Female": 0.1},
            "setting": {"Rural": 0.2, "Peri-urban": 0.15},
        },
        regional_strongholds={
            4: +1.0,   # Littoral: Niger Delta resource activism core
            1: +0.2,   # Lagos: slum organizing presence
            5: +0.3,   # Eastern: Cross River militant base
            3: +0.1,   # Confluence: marginalized communities
        },
    ),
    Party(
        name="NNV",
        positions=NNV_POSITIONS,
        valence=0.1,  # nationalist brand resonates with security-conscious voters
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.2,  # statist-nationalist economics, dirigiste
        demographic_coefficients={
            "livelihood": {"Public sector": 0.5, "Smallholder": 0.2,
                           "Formal private": 0.2},
            "age_cohort": {"50+": 0.4, "35-49": 0.2, "25-34": 0.1},
            "setting": {"Rural": 0.2, "Peri-urban": 0.1},
            "education": {"Below secondary": 0.2, "Secondary": 0.2},
            "gender": {"Male": 0.3},
            "income": {"Middle 40%": 0.2},
        },
        regional_strongholds={
            2: +0.4,   # Niger Zone: Nupe heartland, military cantonment areas
            3: +0.3,   # Confluence: security-concerned communities
            6: +0.5,   # Central: Kano/Kaduna — security state appeal, conflict zone
            7: +0.3,   # Northeastern: Borno/Yobe — military support for security
            8: +0.2,   # Northwestern: military/civil service communities
        },
    ),
]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="LAGOS-2058 Election Simulation")
    parser.add_argument("--seed", type=int, default=2058, help="Random seed (default: 2058)")
    parser.add_argument("--mc", type=int, default=100, help="Monte Carlo runs (default: 100)")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress logging")
    parser.add_argument("--export", type=str, default=None,
                        help="Export LGA results to CSV (e.g. --export results.csv)")
    args = parser.parse_args()

    params = EngineParams(
        q=0.5, beta_s=3.0, alpha_e=3.0, alpha_r=2.0,
        scale=1.5, tau_0=4.5, tau_1=0.3, tau_2=0.5,
        beta_econ=0.3,
        kappa=400.0, sigma_national=0.07, sigma_regional=0.10,
        sigma_turnout=0.02, sigma_turnout_regional=0.03,
    )
    config = ElectionConfig(params=params, parties=PARTIES, n_monte_carlo=args.mc)

    data_path = Path(__file__).parent.parent / "data" / "nigeria_lga_polsim_2058.xlsx"
    results = run_election(data_path, config, seed=args.seed, verbose=not args.quiet)

    # ---- Compute vote counts ----
    party_names = [p.name for p in PARTIES]
    lga_with_votes = compute_vote_counts(results["lga_results_base"], party_names)

    # ---- Print summary ----
    summary = results["summary"]
    mc = results["mc_aggregated"]

    print("\n" + "=" * 70)
    print("LAGOS-2058 ELECTION RESULTS SUMMARY")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
    print("=" * 70)

    # --- National vote counts and shares ---
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

    # --- MC national share confidence intervals ---
    print("\nMC NATIONAL SHARE UNCERTAINTY (mean [P5 - P95]):")
    ns = mc["national_share_stats"].sort_values("Mean Share", ascending=False)
    for _, row in ns.iterrows():
        if row["Mean Share"] >= 0.005:
            print(f"  {row['Party']:10s}  {row['Mean Share']:6.1%}  "
                  f"[{row['P5 Share']:5.1%} - {row['P95 Share']:5.1%}]")

    # --- MC national vote count confidence intervals ---
    nv = mc.get("national_vote_stats")
    if nv is not None and len(nv) > 0:
        print("\nMC NATIONAL VOTE COUNT UNCERTAINTY (mean [P5 - P95]):")
        nv_sorted = nv.sort_values("Mean Votes", ascending=False)
        for _, row in nv_sorted.iterrows():
            if row["Mean Votes"] >= 1000:
                print(f"  {row['Party']:10s}  {row['Mean Votes']:12,.0f}  "
                      f"[{row['P5 Votes']:12,.0f} - {row['P95 Votes']:12,.0f}]")
        tvs = mc.get("total_vote_stats", {})
        if tvs:
            print(f"  {'TOTAL':10s}  {tvs['mean']:12,.0f}  "
                  f"[{tvs['p5']:12,.0f} - {tvs['p95']:12,.0f}]")

    # --- MC ENP distribution ---
    enp_stats = mc.get("enp_stats")
    if enp_stats:
        print(f"\nMC ENP DISTRIBUTION: "
              f"mean {enp_stats['mean']:.2f}  "
              f"[P5 {enp_stats['p5']:.2f} - P95 {enp_stats['p95']:.2f}]")

    # --- MC national competitiveness margin ---
    margin_stats = mc.get("margin_stats")
    if margin_stats:
        print(f"MC NATIONAL MARGIN (1st-2nd): "
              f"mean {margin_stats['mean']:.1%}  "
              f"[P5 {margin_stats['p5']:.1%} - P95 {margin_stats['p95']:.1%}]")

    # --- Presidential spread check ---
    print("\nPRESIDENTIAL SPREAD CHECK (>=25% in >=24 states + national plurality):")
    for p in party_names:
        sc = results["spread_checks"][p]
        mark = "PASS" if sc["meets_requirement"] else "FAIL"
        plurality = "yes" if sc["has_national_plurality"] else "no"
        print(f"  {p:10s}  {mark}  ({sc['states_meeting_25pct']:2d}/24 states, "
              f"plurality: {plurality}, national: {sc['national_share']:.1%})")

    # --- MC spread check probabilities ---
    mc_spread = mc.get("mc_spread")
    if mc_spread:
        print("\nMC PRESIDENTIAL SPREAD PROBABILITIES (across MC runs):")
        print(f"  {'Party':10s}  {'Plurality':>10s}  {'Spread':>8s}  {'Both':>8s}  "
              f"{'States>=25% (mean)':>18s}  {'[P5 - P95]':>14s}")
        print(f"  {'-'*10}  {'-'*10}  {'-'*8}  {'-'*8}  {'-'*18}  {'-'*14}")
        for p, _ in sorted_parties:
            sp = mc_spread.get(p)
            if sp:
                print(f"  {p:10s}  {sp['plurality_prob']:9.0%}  "
                      f"{sp['spread_prob']:7.0%}  {sp['full_requirement_prob']:7.0%}  "
                      f"{sp['states_above_25pct_mean']:17.1f}  "
                      f"[{sp['states_above_25pct_p5']:.0f} - {sp['states_above_25pct_p95']:.0f}]")

    # --- Coalition feasibility analysis ---
    coalitions = compute_coalition_feasibility(results["lga_results_base"], party_names)
    viable = [c for c in coalitions if c["meets_spread"]]
    print(f"\nCOALITION FEASIBILITY (2-3 party, meets spread requirement): "
          f"{len(viable)} viable")
    if viable:
        for c in viable[:10]:
            names = "+".join(c["parties"])
            print(f"  {names:30s}  {c['combined_share']:5.1%}  "
                  f"({c['states_25pct']:2d}/24 states)  "
                  f"margin: {c['margin_over_second']:+.1%}")
    else:
        # Show top 5 closest coalitions
        print("  No coalition meets all requirements. Closest:")
        near = sorted(coalitions, key=lambda c: -c["states_25pct"])[:5]
        for c in near:
            names = "+".join(c["parties"])
            plur = "Y" if c["margin_over_second"] > 0 else "N"
            print(f"  {names:30s}  {c['combined_share']:5.1%}  "
                  f"({c['states_25pct']:2d}/24 states)  plur: {plur}")

    # --- Zonal shares and turnout ---
    print("\nZONAL SHARES (base run):")
    zonal = summary["zonal_shares"]
    party_share_cols = [c for c in zonal.columns if c.endswith("_share") and c != "Turnout"]
    cols_to_show = ["Administrative Zone", "AZ Name"]
    if "Turnout" in zonal.columns:
        cols_to_show.append("Turnout")
    cols_to_show.extend(party_share_cols)
    print(zonal[cols_to_show].to_string(index=False))

    # --- Zonal MC vote stats ---
    zonal_mc = mc.get("zonal_vote_stats")
    if zonal_mc is not None and len(zonal_mc) > 0:
        print("\nZONAL MC VOTE TOTALS (mean [P5 - P95]):")
        for _, row in zonal_mc.iterrows():
            az = row.get("AZ Name", row.get("Administrative Zone", "?"))
            print(f"  {az:30s}  {row['Total Votes Mean']:12,.0f}  "
                  f"[{row['Total Votes P5']:12,.0f} - {row['Total Votes P95']:12,.0f}]")

    # --- State vote counts ---
    state_votes = compute_state_vote_counts(results["lga_results_base"], party_names)
    print("\nSTATE VOTE COUNTS (base run):")
    # Show top 3 parties per state by national share
    top3 = [p for p, _ in sorted_parties[:3]]
    top3_vote_cols = [f"{p}_votes" for p in top3]
    top3_share_cols = [f"{p}_share" for p in top3]
    sv_cols = ["State", "Population", "Total_Votes"] + top3_vote_cols + top3_share_cols
    available_sv = [c for c in sv_cols if c in state_votes.columns]
    print(state_votes[available_sv].to_string(index=False))

    # --- Voting district results with Sainte-Laguë seat allocation ---
    import pandas as pd
    project_root = Path(__file__).parent.parent
    district_file = project_root / "voting_districts_summary.xlsx"
    seat_file = project_root / "seat_allocation.xlsx"
    if district_file.exists() and seat_file.exists():
        lga_mapping = pd.read_excel(district_file, sheet_name="LGA Mapping")
        district_seats = pd.read_excel(seat_file, sheet_name="District Seats")

        dist_df = allocate_district_seats(
            results["lga_results_base"], party_names,
            district_seats, lga_mapping,
        )
        total_seats = dist_df["Seats"].sum()

        # --- Per-district table ---
        print(f"\nVOTING DISTRICT RESULTS ({len(dist_df)} districts, "
              f"{total_seats} seats, Sainte-Laguë, base run):")
        top3_d_seats = [f"{p}_seats" for p in top3]
        top3_d_share = [f"{p}_share" for p in top3]
        show_cols = (
            ["District ID", "AZ Name", "Seats", "Total_Votes"]
            + top3_d_seats + top3_d_share
        )
        available_d = [c for c in show_cols if c in dist_df.columns]
        disp_d = dist_df[available_d].copy()
        for p in top3:
            sc = f"{p}_share"
            if sc in disp_d.columns:
                disp_d[sc] = disp_d[sc].map("{:.1%}".format)
        print(disp_d.to_string(index=False))

        # --- National seat totals ---
        national_seats = {p: int(dist_df[f"{p}_seats"].sum()) for p in party_names}
        sorted_seats = sorted(national_seats.items(), key=lambda x: -x[1])
        print(f"\nNATIONAL SEAT TOTALS (Sainte-Laguë, {total_seats} seats):")
        print(f"  {'Party':10s}  {'Seats':>5s}  {'%':>6s}  {'Votes':>12s}  {'Vote %':>7s}")
        print(f"  {'-'*10}  {'-'*5}  {'-'*6}  {'-'*12}  {'-'*7}")
        for p, s in sorted_seats:
            if s > 0:
                pct = s / total_seats
                votes = summary["national_votes"][p]
                vote_share = summary["national_shares"][p]
                print(f"  {p:10s}  {s:5d}  {pct:5.1%}  {votes:12,}  {vote_share:6.1%}")

        # --- Zonal seat breakdown ---
        print(f"\nZONAL SEAT BREAKDOWN:")
        zone_seat_rows = []
        for az_name, zgroup in dist_df.groupby("AZ Name"):
            zrow = {"AZ Name": az_name, "Seats": int(zgroup["Seats"].sum())}
            for p in party_names:
                zrow[f"{p}_seats"] = int(zgroup[f"{p}_seats"].sum())
            zone_seat_rows.append(zrow)
        zone_seat_df = pd.DataFrame(zone_seat_rows)
        header = f"  {'Zone':25s}  {'Seats':>5s}"
        for p, _ in sorted_seats[:7]:
            header += f"  {p:>5s}"
        print(header)
        print(f"  {'-'*25}  {'-'*5}" + f"  {'-'*5}" * min(7, len(sorted_seats)))
        for _, zr in zone_seat_df.iterrows():
            line = f"  {str(zr['AZ Name']):25s}  {zr['Seats']:5d}"
            for p, _ in sorted_seats[:7]:
                line += f"  {zr[f'{p}_seats']:5d}"
            print(line)

    # --- State-level MC win probabilities ---
    state_mc = mc.get("state_mc_stats")
    if state_mc is not None and len(state_mc) > 0:
        print("\nSTATE MC WIN PROBABILITIES (top 3 parties):")
        top3_win = [f"{p}_win_prob" for p in top3]
        top3_share_mc = [f"{p}_share_mean" for p in top3]
        sm_cols = ["State", "Turnout Mean"] + top3_share_mc + top3_win
        available_sm = [c for c in sm_cols if c in state_mc.columns]
        disp = state_mc[available_sm].copy()
        disp["Turnout Mean"] = disp["Turnout Mean"].map("{:.1%}".format)
        for p in top3:
            if f"{p}_share_mean" in disp.columns:
                disp[f"{p}_share_mean"] = disp[f"{p}_share_mean"].map("{:.1%}".format)
            if f"{p}_win_prob" in disp.columns:
                disp[f"{p}_win_prob"] = disp[f"{p}_win_prob"].map("{:.0%}".format)
        print(disp.to_string(index=False))

    # --- Vote source decomposition ---
    decomp = compute_vote_source_decomposition(results["lga_results_base"], party_names)
    print("\nVOTE SOURCE DECOMPOSITION (% of each party's vote by zone):")
    # Build a compact table: rows = zones, columns = parties
    zone_names = decomp[party_names[0]]["Zone"].tolist()
    header = f"  {'Zone':30s}"
    for p, _ in sorted_parties[:7]:  # top 7 by national share
        header += f"  {p:>7s}"
    print(header)
    print(f"  {'-'*30}" + f"  {'-'*7}" * min(7, len(sorted_parties)))
    for zone in zone_names:
        line = f"  {str(zone):30s}"
        for p, _ in sorted_parties[:7]:
            pct = decomp[p].loc[decomp[p]["Zone"] == zone, "Pct_of_Party_Total"].values[0]
            line += f"  {pct:6.1%}"
        print(line)

    # --- Demographic vote profiles (ecological estimate) ---
    ethnic_cols = {
        "Hausa": "% Hausa", "Fulani": "% Fulani",
        "Hausa-Fulani Undiff": "% Hausa Fulani Undiff",
        "Yoruba": "% Yoruba", "Igbo": "% Igbo", "Ijaw": "% Ijaw",
        "Kanuri": "% Kanuri", "Tiv": "% Tiv", "Edo": "% Edo Bini",
        "Ibibio": "% Ibibio", "Pada": "% Pada", "Naijin": "% Naijin",
    }
    lga_df = results["data"].df
    eth_profile = compute_demographic_vote_profile(
        results["lga_results_base"], lga_df, party_names, ethnic_cols)
    if len(eth_profile) > 0:
        print("\nETHNIC VOTE PROFILE (ecological estimate, top 5 parties per group):")
        for _, row in eth_profile.iterrows():
            shares = {p: row[f"{p}_share"] for p in party_names}
            top5 = sorted(shares.items(), key=lambda x: -x[1])[:5]
            top_str = "  ".join(f"{p}:{s:.0%}" for p, s in top5)
            pop_m = row["Population_Weight"] / 1e6
            print(f"  {row['Group']:22s} ({pop_m:5.1f}M)  {top_str}")

    # Urban/rural profile
    setting_cols = {"Urban": "Urban Pct"}
    setting_profile = compute_demographic_vote_profile(
        results["lga_results_base"], lga_df, party_names, setting_cols)
    if len(setting_profile) > 0:
        print("\nURBAN VOTE PROFILE (ecological estimate):")
        for _, row in setting_profile.iterrows():
            shares = {p: row[f"{p}_share"] for p in party_names}
            top5 = sorted(shares.items(), key=lambda x: -x[1])[:5]
            top_str = "  ".join(f"{p}:{s:.0%}" for p, s in top5)
            print(f"  {row['Group']:22s}  {top_str}")

    # --- Competitiveness ---
    comp = compute_competitiveness(results["lga_results_base"], party_names)
    margins = comp["Margin"].values
    enps = comp["ENP"].values
    print(f"\nLGA COMPETITIVENESS:")
    print(f"  Margin:  Mean: {margins.mean():.1%}  Median: {np.median(margins):.1%}  "
          f"Min: {margins.min():.1%}  Max: {margins.max():.1%}")
    print(f"  ENP:     Mean: {enps.mean():.2f}  Median: {np.median(enps):.2f}  "
          f"Min: {enps.min():.2f}  Max: {enps.max():.2f}")
    n_tight = np.sum(margins < 0.05)
    n_safe = np.sum(margins > 0.20)
    print(f"  Tight (<5% margin): {n_tight}  |  Safe (>20% margin): {n_safe}")

    # --- LGA vote volatility ---
    share_stats = mc.get("share_stats")
    if share_stats is not None and "Volatility" in share_stats.columns:
        vol = share_stats["Volatility"].values
        print(f"\nLGA VOTE VOLATILITY (mean SD of party shares across MC runs):")
        print(f"  Mean: {vol.mean():.3f}  Max: {vol.max():.3f}  "
              f"Min: {vol.min():.3f}")
        n_high_vol = np.sum(vol > 0.02)
        print(f"  High volatility LGAs (>2%): {n_high_vol}")

    # --- Swing LGAs ---
    swing = mc["swing_lgas"]
    print(f"\nSWING LGAs: {len(swing)} / 774 ({len(swing)/774*100:.1f}%)")
    if len(swing) > 0:
        share_cols = [c for c in swing.columns if c.endswith("_share")]
        shares = swing[share_cols].values
        sorted_shares = np.sort(shares, axis=1)
        swing = swing.copy()
        swing["_margin"] = sorted_shares[:, -1] - sorted_shares[:, -2]
        swing = swing.sort_values("_margin")
        print("Top 10 most competitive:")
        for _, row in swing.head(10).iterrows():
            winner = row[[c for c in share_cols]].idxmax().replace("_share", "")
            margin = row["_margin"]
            print(f"  {row['State']:20s}  {row['LGA Name']:25s}  "
                  f"leader: {winner:6s}  margin: {margin:.1%}")

    # --- Turnout distribution ---
    if "Turnout" in lga_with_votes.columns:
        t = lga_with_votes["Turnout"].values
        print(f"\nTURNOUT DISTRIBUTION:")
        print(f"  Mean: {t.mean():.1%}  Median: {np.median(t):.1%}  "
              f"Min: {t.min():.1%}  Max: {t.max():.1%}  Std: {t.std():.1%}")
        for threshold in [0.60, 0.70, 0.80, 0.85, 0.90]:
            n = np.sum(t > threshold)
            print(f"  LGAs > {threshold:.0%}: {n}")

    # --- CSV export ---
    if args.export:
        vote_cols = [f"{p}_votes" for p in party_names]
        share_cols = [f"{p}_share" for p in party_names]
        export_cols = ["State", "LGA Name", "Administrative Zone", "AZ Name",
                       "Estimated Population", "Turnout", "Total_Votes"]
        export_cols.extend(vote_cols)
        export_cols.extend(share_cols)
        available = [c for c in export_cols if c in lga_with_votes.columns]
        lga_with_votes[available].to_csv(args.export, index=False)
        print(f"\nExported LGA results to {args.export}")


if __name__ == "__main__":
    main()
