"""
Example: Run a full LAGOS-2058 election with 24 parties.

Usage:
    python examples/run_election_24party.py

This script defines a hyper-fragmented 24-party landscape spanning the full
range of 2058 Nigerian political cleavages — ethnic, religious, class,
generational, and issue-based. It extends the base 14-party system with 10
additional parties representing splinter movements, single-issue coalitions,
and demographic insurgencies.

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
  23 media_freedom              state control ↔ complete freedom
  24 healthcare                 pure market ↔ universal provision
  25 pada_status                anti-Padà ↔ Padà preservation
  26 energy_policy              fossil/nuclear ↔ full green
  27 az_restructuring           dissolve AZs ↔ keep/strengthen AZs
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
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

# ---------------------------------------------------------------------------
# Import the base 14 party position vectors
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from run_election import (
    NRP_POSITIONS, CND_POSITIONS, ANPC_POSITIONS, IPA_POSITIONS,
    NDC_POSITIONS, UJP_POSITIONS, NWF_POSITIONS, NHA_POSITIONS,
    SNM_POSITIONS, NSA_POSITIONS, CDA_POSITIONS, MBPP_POSITIONS,
    PLF_POSITIONS, NNV_POSITIONS,
)

# ---------------------------------------------------------------------------
# 10 NEW party position vectors
# ---------------------------------------------------------------------------

# YPC — Youth Power Congress
# Gen-Z/millennial insurgent party. Anti-gerontocracy, pro-digital economy,
# pro-bio-enhancement, pro-media-freedom. Rejects both traditional northern
# conservatism and Lagos technocratic elitism. The party of TikTok political
# commentators and unemployed computer science graduates who want to burn the
# old system down and build a digital republic.
YPC_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular but not crusading
    +0.5,  #  1  fiscal: mildly decentralist
    +1.5,  #  2  chinese: moderate WAFTA (tech pragmatism)
    -2.0,  #  3  bic: anti-BIC (outdated institution)
    -2.5,  #  4  ethnic_quotas: meritocratic (youth vs elders, not tribe)
    -3.0,  #  5  fertility: population control (fewer kids, more resources)
    -2.0,  #  6  constitutional: mildly parliamentary
    +0.5,  #  7  resource: centrist
    +3.5,  #  8  housing: strong intervention (housing crisis is #1 youth issue)
    +2.5,  #  9  education: centralist (quality, not patronage)
    +2.0,  # 10  labor: pro-labor (gig economy protections)
    -3.5,  # 11  military: civilian control (anti-junta)
    -1.0,  # 12  immigration: mildly open
    +2.5,  # 13  language: pro-English (digital lingua franca)
    +3.0,  # 14  womens_rights: progressive
    -4.0,  # 15  trad_authority: strongly marginalize (anti-gerontocracy)
    +2.0,  # 16  infrastructure: universal (digital + physical)
    +2.0,  # 17  land_tenure: formalization (property rights for youth)
    +2.0,  # 18  taxation: redistribution (generational equity)
    -1.5,  # 19  agriculture: free market
    +3.5,  # 20  bio_enhancement: strongly pro-access
    +1.5,  # 21  trade: mildly open
    +2.0,  # 22  environment: regulatory
    +4.0,  # 23  media: strong press/internet freedom
    +2.5,  # 24  healthcare: universal
    +0.5,  # 25  pada_status: mildly pro-Padà
    +3.0,  # 26  energy: green (climate generation)
    -2.0,  # 27  az_restructuring: restructure (new model)
])

# GPF — Green People's Front
# Environmental party born from Niger Delta pollution activism, expanded to
# national climate politics. Strongest on environmental regulation and green
# energy in the system. Pro-regulation, pro-green-tech, moderate left on
# economics. Appeals to educated environmentalists, oil-spill victims, and
# the international NGO-connected class. The party of the person who cried
# when they saw the Ogoni creeks.
GPF_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular
    +1.0,  #  1  fiscal: mild autonomy
    +0.0,  #  2  chinese: neutral (pragmatic on green tech supply chains)
    -1.0,  #  3  bic: mildly anti-BIC
    +0.5,  #  4  ethnic_quotas: centrist
    -2.0,  #  5  fertility: population control
    -1.5,  #  6  constitutional: mildly parliamentary
    +2.0,  #  7  resource: local control (communities own their environment)
    +1.5,  #  8  housing: mildly interventionist (sustainable housing)
    +1.5,  #  9  education: mildly centralist (environmental education)
    +1.0,  # 10  labor: mildly pro-labor (green jobs)
    -2.0,  # 11  military: civilian control
    -0.5,  # 12  immigration: centrist
    +1.0,  # 13  language: mildly English
    +2.5,  # 14  womens_rights: progressive (ecofeminism)
    -2.0,  # 15  trad_authority: marginalize
    +2.0,  # 16  infrastructure: universal (green infra)
    +1.5,  # 17  land_tenure: formalization (environmental protections)
    +1.5,  # 18  taxation: mild redistribution (carbon tax)
    +1.0,  # 19  agriculture: mildly protectionist (organic farming)
    +1.0,  # 20  bio_enhancement: mildly pro
    +0.5,  # 21  trade: mildly open (green tech imports)
    +5.0,  # 22  environment: MAXIMUM regulation
    +3.0,  # 23  media: press freedom (environmental reporting)
    +2.0,  # 24  healthcare: universal
    +0.0,  # 25  pada_status: neutral
    +5.0,  # 26  energy: FULL green transition
    -0.5,  # 27  az_restructuring: centrist
])

# DRA — Delta Resource Alliance
# Niger Delta micro-party focused almost exclusively on resource federalism,
# oil revenue, and Delta infrastructure. Where PLF is radical-left, DRA is
# pragmatic resource-nationalist. "Give us our oil money and we'll build our
# own roads." Led by an Ijaw businessman-activist who made his money in oil
# services and now wants to redirect federal revenue to Delta communities.
DRA_POSITIONS = np.array([
    -2.5,  #  0  sharia: secular
    +4.5,  #  1  fiscal: near-maximum confederalism
    -0.5,  #  2  chinese: mildly Western
    -1.0,  #  3  bic: mildly anti-BIC
    +1.5,  #  4  ethnic_quotas: mild affirmative action
    +0.5,  #  5  fertility: centrist
    +0.5,  #  6  constitutional: centrist
    +5.0,  #  7  resource: MAXIMUM local control (core identity)
    +2.0,  #  8  housing: interventionist
    +0.5,  #  9  education: centrist
    +1.0,  # 10  labor: mildly pro-labor
    -1.0,  # 11  military: mildly civilian (anti-military in Delta)
    +0.5,  # 12  immigration: centrist
    +0.5,  # 13  language: centrist
    +1.0,  # 14  womens_rights: mildly progressive
    -1.0,  # 15  trad_authority: mildly marginalize
    +3.5,  # 16  infrastructure: strongly universal (Delta needs everything)
    -1.5,  # 17  land_tenure: mildly customary (ancestral creek land)
    +1.5,  # 18  taxation: mild redistribution
    +1.0,  # 19  agriculture: mildly protectionist (fishing communities)
    +1.0,  # 20  bio_enhancement: mildly pro
    +0.5,  # 21  trade: mildly open
    +3.5,  # 22  environment: strong regulation (oil pollution)
    +2.0,  # 23  media: press freedom
    +3.0,  # 24  healthcare: universal
    -1.0,  # 25  pada_status: mildly anti-Padà
    -1.0,  # 26  energy: mildly fossil (oil = Delta economy)
    -3.5,  # 27  az_restructuring: restructure (new Delta zone)
])

# ABP — Arewa Brotherhood Party
# Northern traditionalist party — more conservative than NDC on social issues,
# deeply pro-Sharia, pro-emirate, pro-natalist, anti-Western influence. NDC
# with the compromise stripped out. Appeals to older rural northerners who
# think NDC sold out to southern politicians. The party of the village imam
# who distrusts both Abuja and Lagos.
ABP_POSITIONS = np.array([
    +4.5,  #  0  sharia: near-maximum Sharia
    +1.5,  #  1  fiscal: mild autonomy
    -2.0,  #  2  chinese: Western lean (anti-WAFTA on Islamic grounds)
    -4.0,  #  3  bic: abolish BIC (Western institution)
    +4.5,  #  4  ethnic_quotas: strongest affirmative action
    +4.5,  #  5  fertility: strongest pro-natalist
    +3.5,  #  6  constitutional: presidential (strongman + Sharia)
    +1.5,  #  7  resource: mild local control
    +2.0,  #  8  housing: interventionist (communal housing)
    -4.0,  #  9  education: radical localism (Quranic + vernacular)
    +1.5,  # 10  labor: mildly pro-labor (Islamic labor charity)
    +2.0,  # 11  military: guardianship (Islamic order)
    +4.0,  # 12  immigration: restrictionist
    -4.0,  # 13  language: vernacular/Arabic
    -4.5,  # 14  womens_rights: strongly conservative
    +4.5,  # 15  trad_authority: strongest integration (emirate system)
    +3.5,  # 16  infrastructure: universal
    -3.0,  # 17  land_tenure: customary (communal Islamic land)
    +3.0,  # 18  taxation: redistribution (Islamic zakat model)
    +4.0,  # 19  agriculture: protectionist
    -4.5,  # 20  bio_enhancement: near-prohibition (haram)
    -2.5,  # 21  trade: autarkic
    -2.0,  # 22  environment: growth first
    -1.0,  # 23  media: mildly state-controlled
    +3.0,  # 24  healthcare: universal (Islamic welfare)
    -4.5,  # 25  pada_status: strongly anti-Padà
    -2.0,  # 26  energy: fossil
    +0.0,  # 27  az_restructuring: neutral (current zones OK for north)
])

# YDP — Yoruba Democratic Party
# Yoruba ethno-nationalist party pushing for southwestern autonomy and Oduduwa
# cultural revival. Distinct from CND (pan-southern progressive) — YDP is
# explicitly "Yoruba first." Pro-fiscal-autonomy for the southwest, pro-Yoruba-
# language, pro-traditional-Oba-authority, anti-sharia, and economically
# moderate. The party of the person who wants Lagos to keep its own tax revenue
# and resents both Abuja and the Igbo trader next door.
YDP_POSITIONS = np.array([
    -3.5,  #  0  sharia: strongly secular
    +3.5,  #  1  fiscal: strong autonomy (Yoruba fiscal independence)
    -1.0,  #  2  chinese: mildly Western
    -0.5,  #  3  bic: centrist
    -1.0,  #  4  ethnic_quotas: mildly meritocratic
    +0.5,  #  5  fertility: centrist
    -1.0,  #  6  constitutional: mildly parliamentary (Yoruba legislative tradition)
    +2.5,  #  7  resource: local control
    +1.0,  #  8  housing: mildly interventionist
    +0.5,  #  9  education: centrist
    +0.5,  # 10  labor: centrist
    -1.5,  # 11  military: civilian control (Abiola memory)
    +2.0,  # 12  immigration: restrictionist (Omo-onile tradition)
    -3.0,  # 13  language: Yoruba vernacular
    +1.0,  # 14  womens_rights: mildly progressive
    +3.0,  # 15  trad_authority: integration (Oba system)
    +1.0,  # 16  infrastructure: mildly universal
    +1.5,  # 17  land_tenure: mild formalization
    +0.5,  # 18  taxation: centrist
    -0.5,  # 19  agriculture: centrist
    +1.0,  # 20  bio_enhancement: mildly pro
    +1.0,  # 21  trade: mildly open (Lagos port)
    +1.0,  # 22  environment: mild regulation
    +2.5,  # 23  media: press freedom (Yoruba press tradition)
    +1.5,  # 24  healthcare: mildly universal
    -2.0,  # 25  pada_status: anti-Padà (territorial)
    +1.0,  # 26  energy: mild green
    -3.5,  # 27  az_restructuring: restructure (Oduduwa zone)
])

# PDA — Padà Democratic Alliance
# Padà identity party — unlike NRP (cosmopolitan liberal), PDA is radical
# pro-Padà-rights. Strongest position on Padà preservation, bio-enhancement
# access, and anti-discrimination. Single-issue party that sees the BIC as
# essential and bio-enhancement as a fundamental right. Appeals to Padà
# communities who feel NRP is too focused on general governance and not enough
# on Padà survival. The party of the enhanced human who's been refused service
# at a Kano restaurant.
PDA_POSITIONS = np.array([
    -3.0,  #  0  sharia: secular (Padà secular by nature)
    -1.0,  #  1  fiscal: mildly centralist (BIC needs federal backing)
    +1.0,  #  2  chinese: mild WAFTA (pragmatic)
    +5.0,  #  3  bic: MAXIMUM preserve (core identity)
    -3.0,  #  4  ethnic_quotas: meritocratic (Padà are merit-coded)
    -2.5,  #  5  fertility: population control
    -1.5,  #  6  constitutional: mildly parliamentary
    -1.0,  #  7  resource: mildly federal
    +1.5,  #  8  housing: mildly interventionist
    +2.5,  #  9  education: centralist (inclusive Padà education)
    -0.5,  # 10  labor: centrist
    -1.5,  # 11  military: civilian control
    -2.5,  # 12  immigration: open borders (Padà are global)
    +3.5,  # 13  language: English (cosmopolitan)
    +2.0,  # 14  womens_rights: progressive
    -4.5,  # 15  trad_authority: strongly marginalize (trad auth = anti-Padà)
    +0.5,  # 16  infrastructure: centrist
    +2.5,  # 17  land_tenure: formalization (Padà property rights)
    +0.5,  # 18  taxation: centrist
    -1.0,  # 19  agriculture: free market
    +5.0,  # 20  bio_enhancement: MAXIMUM access (existential issue)
    +2.0,  # 21  trade: open (enhancement tech imports)
    +0.5,  # 22  environment: centrist
    +1.5,  # 23  media: press freedom
    +1.5,  # 24  healthcare: mildly universal (enhancement healthcare)
    +5.0,  # 25  pada_status: MAXIMUM Padà preservation
    +1.5,  # 26  energy: mild green
    +3.0,  # 27  az_restructuring: keep AZs (stable for Padà)
])

# WPP — Women's Progressive Party
# Feminist party demanding gender quotas, maternal health, girls' education,
# and anti-GBV legislation. Not just a women's party but a gender-justice
# movement. Strongest position on women's rights in the system. Economically
# centre-left, pro-healthcare, pro-education. Appeals to educated women across
# religious lines, NGO workers, and female-headed households. The party of the
# nurse who delivers babies in a clinic without electricity.
WPP_POSITIONS = np.array([
    -2.5,  #  0  sharia: secular (Sharia restricts women)
    +0.5,  #  1  fiscal: centrist
    +0.0,  #  2  chinese: neutral
    +0.0,  #  3  bic: neutral
    +2.0,  #  4  ethnic_quotas: affirmative action (gender + ethnic)
    -3.5,  #  5  fertility: population control (women's reproductive autonomy)
    -1.5,  #  6  constitutional: mildly parliamentary
    +0.5,  #  7  resource: centrist
    +2.5,  #  8  housing: interventionist (women's safe housing)
    +2.5,  #  9  education: centralist (girls' education mandate)
    +2.0,  # 10  labor: pro-labor (equal pay, maternity)
    -2.0,  # 11  military: civilian control
    +0.0,  # 12  immigration: neutral
    +1.5,  # 13  language: mildly English
    +5.0,  # 14  womens_rights: MAXIMUM progressive
    -3.5,  # 15  trad_authority: marginalize (patriarchal institution)
    +2.5,  # 16  infrastructure: universal (maternal health infra)
    +1.0,  # 17  land_tenure: mild formalization (women's land rights)
    +2.0,  # 18  taxation: redistribution (gender budgeting)
    +1.0,  # 19  agriculture: mildly protectionist (market women)
    +1.5,  # 20  bio_enhancement: mildly pro
    +0.5,  # 21  trade: mildly open
    +1.5,  # 22  environment: mild regulation
    +3.0,  # 23  media: press freedom (women's voices)
    +4.5,  # 24  healthcare: near-maximum universal (maternal health)
    +0.5,  # 25  pada_status: centrist
    +2.0,  # 26  energy: green
    -0.5,  # 27  az_restructuring: centrist
])

# NFM — Nigerian Farmers' Movement
# Agrarian populist party — single-issue focus on smallholder protection,
# land rights, food sovereignty, anti-WAFTA for agriculture. The party of
# people who grow the food that everyone eats but nobody values. Strongest
# position on agricultural protectionism and near-strongest on customary
# land tenure. Cross-ethnic appeal across farming communities from Benue
# to Bauchi.
NFM_POSITIONS = np.array([
    +0.5,  #  0  sharia: centrist (farmers everywhere)
    +2.0,  #  1  fiscal: autonomy (local agricultural boards)
    -2.0,  #  2  chinese: anti-WAFTA (food imports destroy farming)
    -1.0,  #  3  bic: mildly anti-BIC
    +2.5,  #  4  ethnic_quotas: affirmative action (farmers deserve quotas)
    +2.0,  #  5  fertility: pro-natalist (farm labor tradition)
    +0.5,  #  6  constitutional: centrist
    +2.0,  #  7  resource: local control
    +1.5,  #  8  housing: mildly interventionist
    -2.5,  #  9  education: localist (agricultural education)
    +2.5,  # 10  labor: pro-labor (farm worker protection)
    -0.5,  # 11  military: centrist
    +2.0,  # 12  immigration: restrictionist (protect local farms)
    -2.0,  # 13  language: vernacular (farming communities)
    -0.5,  # 14  womens_rights: centrist
    +2.0,  # 15  trad_authority: integration (land chiefs)
    +4.0,  # 16  infrastructure: strongly universal (farm roads, irrigation)
    -4.0,  # 17  land_tenure: strongly customary (communal farming land)
    +3.0,  # 18  taxation: redistribution (farm subsidies)
    +5.0,  # 19  agriculture: MAXIMUM protectionist
    -1.5,  # 20  bio_enhancement: mildly against
    -3.5,  # 21  trade: autarkic (food sovereignty)
    +0.5,  # 22  environment: centrist (farmer pragmatism)
    +1.0,  # 23  media: centrist
    +3.0,  # 24  healthcare: universal (rural healthcare)
    -2.0,  # 25  pada_status: anti-Padà (rural suspicion)
    -0.5,  # 26  energy: centrist
    -2.0,  # 27  az_restructuring: restructure (farm-zone representation)
])

# TRP — Tijaniyya Reform Party
# Moderate Sufi Islamic party rooted in the Tijaniyya brotherhood's
# commercial and scholarly networks. Different from NDC (establishment),
# UJP (radical), and ABP (traditionalist). Pro-Sharia but moderate,
# pro-trade (Tijaniyya merchants), anti-Al-Shahid, economically pragmatic.
# The party of the Ibadan-based Tijaniyya sheikh who trades in Chinese
# electronics while preaching Sufi devotion.
TRP_POSITIONS = np.array([
    +2.5,  #  0  sharia: moderate pro-Sharia (Sufi interpretation)
    +1.5,  #  1  fiscal: mild autonomy
    +1.0,  #  2  chinese: mildly WAFTA (trade pragmatism)
    -2.5,  #  3  bic: anti-BIC (Islamic sovereignty)
    +2.0,  #  4  ethnic_quotas: affirmative action
    +2.0,  #  5  fertility: pro-natalist
    +1.0,  #  6  constitutional: mildly presidential
    +1.0,  #  7  resource: mild local control
    +1.5,  #  8  housing: mildly interventionist
    -1.5,  #  9  education: mildly localist (Islamic + secular mix)
    +0.5,  # 10  labor: centrist
    -0.5,  # 11  military: centrist (Sufi pacifist lean)
    +1.0,  # 12  immigration: mildly restrictionist
    -2.0,  # 13  language: vernacular/Arabic
    -1.5,  # 14  womens_rights: conservative but less extreme (Sufi moderation)
    +2.5,  # 15  trad_authority: integration (brotherhood structures)
    +2.0,  # 16  infrastructure: universal
    -1.0,  # 17  land_tenure: mildly customary
    +1.0,  # 18  taxation: mildly redistributive (zakat)
    +2.0,  # 19  agriculture: protectionist
    -2.5,  # 20  bio_enhancement: against
    +1.5,  # 21  trade: mildly open (Tijaniyya commercial networks)
    +0.0,  # 22  environment: neutral
    +0.5,  # 23  media: centrist
    +2.5,  # 24  healthcare: universal
    -3.0,  # 25  pada_status: anti-Padà
    -0.5,  # 26  energy: centrist
    +1.0,  # 27  az_restructuring: mildly keep AZs
])

# CTF — Chinese-Trade Front
# Pro-WAFTA party focused on deepening Chinese economic integration, Mandarin
# education, and planned-city development. Techno-optimist, pro-bio-
# enhancement, pro-trade-openness. Appeals to Naijin, communities near
# Chinese economic zones, and urban youth who see China as the future.
# The party of the Mandarin-speaking Nigerian who works at Huawei Lagos.
CTF_POSITIONS = np.array([
    -2.0,  #  0  sharia: secular
    -1.5,  #  1  fiscal: centralist (WAFTA needs central coordination)
    +5.0,  #  2  chinese: MAXIMUM WAFTA
    +2.0,  #  3  bic: preserve (WAFTA stability)
    -2.0,  #  4  ethnic_quotas: meritocratic
    -1.5,  #  5  fertility: population control
    -1.0,  #  6  constitutional: mildly parliamentary
    -1.5,  #  7  resource: mildly federal
    +2.0,  #  8  housing: interventionist (planned housing)
    +3.5,  #  9  education: centralist (Mandarin + STEM)
    -2.0,  # 10  labor: pro-capital (business-friendly for FDI)
    +0.0,  # 11  military: neutral
    -2.0,  # 12  immigration: open (Chinese workers, students)
    -0.5,  # 13  language: mildly multilingual (Mandarin + English)
    +1.5,  # 14  womens_rights: mildly progressive
    -2.5,  # 15  trad_authority: marginalize
    +0.5,  # 16  infrastructure: centrist (Chinese-built infra)
    +3.0,  # 17  land_tenure: formalization (investment zones)
    -0.5,  # 18  taxation: centrist (FDI-friendly tax)
    -2.0,  # 19  agriculture: free market (import food, export tech)
    +3.5,  # 20  bio_enhancement: strongly pro (Chinese biotech)
    +4.5,  # 21  trade: near-maximum openness
    +0.5,  # 22  environment: centrist
    +0.0,  # 23  media: neutral
    +1.5,  # 24  healthcare: mildly universal
    +1.5,  # 25  pada_status: mildly pro-Padà
    +1.5,  # 26  energy: mild green (Chinese solar)
    +2.0,  # 27  az_restructuring: keep AZs
])

# Validation check for all new parties
for name, pos in [
    ("YPC", YPC_POSITIONS), ("GPF", GPF_POSITIONS), ("DRA", DRA_POSITIONS),
    ("ABP", ABP_POSITIONS), ("YDP", YDP_POSITIONS), ("PDA", PDA_POSITIONS),
    ("WPP", WPP_POSITIONS), ("NFM", NFM_POSITIONS), ("TRP", TRP_POSITIONS),
    ("CTF", CTF_POSITIONS),
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

# Reuse base 14 parties but slightly reduce valence (brand dilution in
# a 24-party system) and import their demographic_coefficients
from run_election import PARTIES as BASE_PARTIES

PARTIES = []
for bp in BASE_PARTIES:
    # Reduce base party valence slightly — brand fragmentation
    new_valence = bp.valence * 0.85
    PARTIES.append(Party(
        name=bp.name,
        positions=bp.positions,
        valence=new_valence,
        leader_ethnicity=bp.leader_ethnicity,
        religious_alignment=bp.religious_alignment,
        economic_positioning=bp.economic_positioning,
        demographic_coefficients=bp.demographic_coefficients,
        regional_strongholds=bp.regional_strongholds,
    ))

# Now add the 10 new parties
PARTIES.extend([
    Party(
        name="YPC",
        positions=YPC_POSITIONS,
        valence=-0.1,  # new party, limited organization
        leader_ethnicity="Yoruba",
        religious_alignment="Secular",
        economic_positioning=0.3,  # centre-left, generational
        demographic_coefficients={
            "age_cohort": {"18-24": 0.6, "25-34": 0.3},
            "education": {"Tertiary": 0.3, "Secondary": 0.2},
            "livelihood": {"Unemployed/student": 0.5, "Trade/informal": 0.2,
                           "Formal private": 0.1},
            "setting": {"Urban": 0.3, "Peri-urban": 0.2},
            "gender": {"Female": 0.1},
            "income": {"Bottom 40%": 0.15, "Middle 40%": 0.1},
        },
        regional_strongholds={
            1: +0.5,   # Lagos: youth digital economy
            6: +0.2,   # Central: FCT/Kano university towns
            2: +0.2,   # Niger: Ibadan youth
            4: +0.1,   # Littoral: Port Harcourt youth
        },
    ),
    Party(
        name="GPF",
        positions=GPF_POSITIONS,
        valence=-0.15,  # niche party, weak organization
        leader_ethnicity="Ijaw",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.4,  # green-left
        demographic_coefficients={
            "education": {"Tertiary": 0.4, "Secondary": 0.1},
            "age_cohort": {"18-24": 0.2, "25-34": 0.2},
            "livelihood": {"Formal private": 0.2, "Public sector": 0.15},
            "income": {"Middle 40%": 0.15, "Top 20%": 0.1},
            "setting": {"Urban": 0.2},
            "gender": {"Female": 0.15},
        },
        regional_strongholds={
            4: +0.5,   # Littoral: Niger Delta environmental activism
            1: +0.3,   # Lagos: educated environmentalists
            5: +0.1,   # Eastern: Cross River conservation
            3: +0.1,   # Confluence: Edo/Ondo environmental awareness
        },
    ),
    Party(
        name="DRA",
        positions=DRA_POSITIONS,
        valence=-0.1,  # regional party, moderate organization
        leader_ethnicity="Ijaw",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.5,  # resource-redistributive
        demographic_coefficients={
            "livelihood": {"Extraction": 0.5, "Smallholder": 0.2,
                           "Trade/informal": 0.2},
            "income": {"Bottom 40%": 0.3, "Middle 40%": 0.1},
            "age_cohort": {"25-34": 0.15, "35-49": 0.15, "50+": 0.1},
            "education": {"Below secondary": 0.1, "Secondary": 0.15},
            "setting": {"Rural": 0.15, "Peri-urban": 0.1},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            4: +1.2,   # Littoral: Delta resource heartland
            5: +0.1,   # Eastern: Abia oil communities
        },
    ),
    Party(
        name="ABP",
        positions=ABP_POSITIONS,
        valence=-0.05,  # moderate: emirate network provides some organization
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
        economic_positioning=0.6,  # Islamic welfare, redistributive
        demographic_coefficients={
            "age_cohort": {"50+": 0.4, "35-49": 0.2},
            "education": {"Below secondary": 0.3},
            "livelihood": {"Smallholder": 0.3, "Trade/informal": 0.1},
            "income": {"Bottom 40%": 0.2},
            "setting": {"Rural": 0.3, "Peri-urban": 0.05},
            "gender": {"Male": 0.25},
        },
        regional_strongholds={
            8: +0.8,   # Savanna: deepest northern traditionalism
            7: +0.5,   # Chad: northeastern emirate system
            6: +0.3,   # Central: Kano old-city conservatives
        },
    ),
    Party(
        name="YDP",
        positions=YDP_POSITIONS,
        valence=-0.05,  # moderate organization through Yoruba cultural networks
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
        economic_positioning=0.1,  # centrist, pragmatic
        demographic_coefficients={
            "age_cohort": {"35-49": 0.2, "50+": 0.15, "25-34": 0.1},
            "education": {"Secondary": 0.2, "Below secondary": 0.1},
            "livelihood": {"Trade/informal": 0.3, "Smallholder": 0.15,
                           "Public sector": 0.1},
            "income": {"Middle 40%": 0.15, "Bottom 40%": 0.1},
            "setting": {"Peri-urban": 0.15, "Urban": 0.1},
            "gender": {"Male": 0.15},
        },
        regional_strongholds={
            2: +0.8,   # Niger Zone: Yoruba heartland (Oyo, Ogun)
            3: +0.6,   # Confluence: Ekiti, Ondo, Osun
            1: +0.3,   # Lagos: Yoruba identity politics
        },
    ),
    Party(
        name="PDA",
        positions=PDA_POSITIONS,
        valence=-0.15,  # niche identity party
        leader_ethnicity="Pada",
        religious_alignment="Secular",
        economic_positioning=-0.3,  # mildly pro-market
        demographic_coefficients={
            "education": {"Tertiary": 0.5, "Secondary": 0.2},
            "livelihood": {"Formal private": 0.4, "Public sector": 0.2},
            "income": {"Top 20%": 0.3, "Middle 40%": 0.15},
            "age_cohort": {"25-34": 0.2, "18-24": 0.15},
            "setting": {"Urban": 0.4},
            "gender": {"Female": 0.15},
        },
        regional_strongholds={
            1: +0.8,   # Lagos: Padà diaspora capital
            6: +0.3,   # Central: FCT Padà community
            3: +0.1,   # Confluence: tech-hub Padà
        },
    ),
    Party(
        name="WPP",
        positions=WPP_POSITIONS,
        valence=-0.2,  # new party, organizational challenge
        leader_ethnicity="Igbo",
        religious_alignment="Catholic",
        economic_positioning=0.4,  # centre-left gender-budgeting
        demographic_coefficients={
            "gender": {"Female": 0.6},
            "education": {"Tertiary": 0.3, "Secondary": 0.15},
            "age_cohort": {"25-34": 0.2, "35-49": 0.15},
            "livelihood": {"Public sector": 0.2, "Formal private": 0.15,
                           "Trade/informal": 0.1},
            "income": {"Middle 40%": 0.15, "Bottom 40%": 0.1},
            "setting": {"Urban": 0.2, "Peri-urban": 0.1},
        },
        regional_strongholds={
            1: +0.3,   # Lagos: feminist organizations
            5: +0.3,   # Eastern: Igbo women's movement tradition
            3: +0.2,   # Confluence: Ondo/Ekiti women's cooperatives
            6: +0.1,   # Central: FCT gender activists
        },
    ),
    Party(
        name="NFM",
        positions=NFM_POSITIONS,
        valence=-0.1,  # moderate: agricultural union networks
        leader_ethnicity="Tiv",
        religious_alignment="Catholic",
        economic_positioning=0.7,  # agrarian-populist, pro-poor
        demographic_coefficients={
            "livelihood": {"Smallholder": 0.6, "Commercial ag": 0.4},
            "income": {"Bottom 40%": 0.3, "Middle 40%": 0.1},
            "age_cohort": {"35-49": 0.15, "50+": 0.25},
            "education": {"Below secondary": 0.25, "Secondary": 0.1},
            "setting": {"Rural": 0.35, "Peri-urban": 0.1},
            "gender": {"Male": 0.1, "Female": 0.05},
        },
        regional_strongholds={
            5: +0.6,   # Eastern: Benue food basket
            6: +0.4,   # Central: Nasarawa/Plateau farming
            7: +0.3,   # Chad: Bauchi/Gombe agricultural communities
            8: +0.2,   # Savanna: northern farming belt
            3: +0.2,   # Confluence: Kogi farming communities
        },
    ),
    Party(
        name="TRP",
        positions=TRP_POSITIONS,
        valence=-0.05,  # Tijaniyya brotherhood provides real organizational depth
        leader_ethnicity="Yoruba",
        religious_alignment="Tijaniyya",
        economic_positioning=0.3,  # moderate, trade-oriented
        demographic_coefficients={
            "education": {"Secondary": 0.15, "Below secondary": 0.1},
            "livelihood": {"Trade/informal": 0.35, "Smallholder": 0.15,
                           "Public sector": 0.1},
            "age_cohort": {"35-49": 0.2, "50+": 0.2, "25-34": 0.1},
            "income": {"Middle 40%": 0.15, "Bottom 40%": 0.1},
            "setting": {"Peri-urban": 0.15, "Urban": 0.1},
            "gender": {"Male": 0.2},
        },
        regional_strongholds={
            2: +0.5,   # Niger Zone: Tijaniyya heartland (Oyo, Ilorin)
            8: +0.3,   # Savanna: Sokoto/Kaduna Tijaniyya networks
            6: +0.2,   # Central: Kano Tijaniyya community
            3: +0.15,  # Confluence: Osun/Ekiti Muslim traders
        },
    ),
    Party(
        name="CTF",
        positions=CTF_POSITIONS,
        valence=-0.1,  # moderate: Chinese-funded organizational support
        leader_ethnicity="Naijin",
        religious_alignment="Secular",
        economic_positioning=-0.4,  # pro-FDI, pro-business
        demographic_coefficients={
            "education": {"Tertiary": 0.4, "Secondary": 0.15},
            "livelihood": {"Formal private": 0.4, "Public sector": 0.1},
            "income": {"Top 20%": 0.3, "Middle 40%": 0.15},
            "age_cohort": {"18-24": 0.2, "25-34": 0.25},
            "setting": {"Urban": 0.35},
            "gender": {"Female": 0.1},
        },
        regional_strongholds={
            1: +0.4,   # Lagos: Chinese business hub
            6: +0.3,   # Central: FCT WAFTA institutions, Kano Chinese industry
            7: +0.1,   # Chad: Chinese mining/infrastructure
            4: +0.1,   # Littoral: Chinese port operations
        },
    ),
])

# Final validation
assert len(PARTIES) == 24, f"Expected 24 parties, got {len(PARTIES)}"
for p in PARTIES:
    assert p.positions.shape == (N_ISSUES,), f"{p.name} shape mismatch"


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LAGOS-2058 Election: 24-Party Hyper-Fragmented Scenario")
    parser.add_argument("--seed", type=int, default=2058)
    parser.add_argument("--mc", type=int, default=100)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--export", type=str, default=None)
    args = parser.parse_args()

    # tau_0 raised to 5.0 (from 3.9) because with 24 parties every voter
    # finds a nearby party, collapsing abstention; the higher baseline
    # compensates for the mechanical party-count turnout inflation.
    params = EngineParams(
        q=0.5, beta_s=0.7, alpha_e=3.0, alpha_r=2.0,
        scale=1.0, tau_0=5.5, tau_1=0.3, tau_2=0.5,
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
    print("LAGOS-2058: 24-PARTY HYPER-FRAGMENTED ELECTION")
    print(f"  Seed: {args.seed}  |  MC runs: {args.mc}  |  Parties: {len(PARTIES)}")
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

    # --- MC confidence intervals ---
    print("\nMC NATIONAL SHARE UNCERTAINTY (mean [P5 - P95]):")
    ns = mc["national_share_stats"].sort_values("Mean Share", ascending=False)
    for _, row in ns.iterrows():
        if row["Mean Share"] >= 0.003:
            print(f"  {row['Party']:10s}  {row['Mean Share']:6.1%}  "
                  f"[{row['P5 Share']:5.1%} - {row['P95 Share']:5.1%}]")

    # --- MC ENP ---
    enp_stats = mc.get("enp_stats")
    if enp_stats:
        print(f"\nMC ENP DISTRIBUTION: "
              f"mean {enp_stats['mean']:.2f}  "
              f"[P5 {enp_stats['p5']:.2f} - P95 {enp_stats['p95']:.2f}]")

    # --- Presidential spread ---
    print("\nPRESIDENTIAL SPREAD CHECK (>=25% in >=24 states):")
    for p, _ in sorted_parties[:10]:
        sc = results["spread_checks"][p]
        mark = "PASS" if sc["meets_requirement"] else "FAIL"
        plurality = "yes" if sc["has_national_plurality"] else "no"
        print(f"  {p:10s}  {mark}  ({sc['states_meeting_25pct']:2d}/24 states, "
              f"plurality: {plurality}, national: {sc['national_share']:.1%})")

    # --- Coalition feasibility (2-3 party) ---
    coalitions = compute_coalition_feasibility(results["lga_results_base"], party_names)
    viable = [c for c in coalitions if c["meets_spread"]]
    print(f"\nCOALITION FEASIBILITY: {len(viable)} viable coalitions")
    if viable:
        for c in viable[:15]:
            names = "+".join(c["parties"])
            print(f"  {names:35s}  {c['combined_share']:5.1%}  "
                  f"({c['states_25pct']:2d}/24 states)")
    else:
        print("  No coalition meets all requirements. Closest:")
        near = sorted(coalitions, key=lambda c: -c["states_25pct"])[:10]
        for c in near:
            names = "+".join(c["parties"])
            plur = "Y" if c["margin_over_second"] > 0 else "N"
            print(f"  {names:35s}  {c['combined_share']:5.1%}  "
                  f"({c['states_25pct']:2d}/24 states)  plur: {plur}")

    # --- Zonal shares ---
    print("\nZONAL SHARES (top 8 parties, base run):")
    zonal = summary["zonal_shares"]
    top8 = [p for p, _ in sorted_parties[:8]]
    top8_cols = [f"{p}_share" for p in top8]
    cols_to_show = ["Administrative Zone", "AZ Name"]
    if "Turnout" in zonal.columns:
        cols_to_show.append("Turnout")
    available_top8 = [c for c in top8_cols if c in zonal.columns]
    cols_to_show.extend(available_top8)
    print(zonal[cols_to_show].to_string(index=False))

    # --- Vote source decomposition ---
    decomp = compute_vote_source_decomposition(results["lga_results_base"], party_names)
    print("\nVOTE SOURCE DECOMPOSITION (top 8 parties, % by zone):")
    zone_names = decomp[party_names[0]]["Zone"].tolist()
    header = f"  {'Zone':30s}"
    for p in top8:
        header += f"  {p:>7s}"
    print(header)
    print(f"  {'-'*30}" + f"  {'-'*7}" * len(top8))
    for zone in zone_names:
        line = f"  {str(zone):30s}"
        for p in top8:
            pct = decomp[p].loc[decomp[p]["Zone"] == zone, "Pct_of_Party_Total"].values[0]
            line += f"  {pct:6.1%}"
        print(line)

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
    n_safe = np.sum(margins > 0.15)
    print(f"  Tight (<5% margin): {n_tight}  |  Safe (>15% margin): {n_safe}")

    # --- Turnout ---
    if "Turnout" in lga_with_votes.columns:
        t = lga_with_votes["Turnout"].values
        print(f"\nTURNOUT DISTRIBUTION:")
        print(f"  Mean: {t.mean():.1%}  Median: {np.median(t):.1%}  "
              f"Min: {t.min():.1%}  Max: {t.max():.1%}")

    # --- Fragmentation analysis ---
    print("\n" + "=" * 70)
    print("FRAGMENTATION ANALYSIS")
    print("=" * 70)

    # Count how many parties get >5% nationally
    above_5 = [(p, s) for p, s in sorted_parties if s >= 0.05]
    above_3 = [(p, s) for p, s in sorted_parties if s >= 0.03]
    above_1 = [(p, s) for p, s in sorted_parties if s >= 0.01]
    print(f"  Parties above 5%: {len(above_5)}")
    print(f"  Parties above 3%: {len(above_3)}")
    print(f"  Parties above 1%: {len(above_1)}")
    print(f"  Combined share of top 3: "
          f"{sum(s for _, s in sorted_parties[:3]):.1%}")
    print(f"  Combined share of top 5: "
          f"{sum(s for _, s in sorted_parties[:5]):.1%}")

    # Who are the "wasted vote" micro-parties?
    below_1 = [(p, s) for p, s in sorted_parties if s < 0.01]
    if below_1:
        print(f"\n  Micro-parties (<1%):")
        for p, s in below_1:
            print(f"    {p}: {s:.2%}")

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
