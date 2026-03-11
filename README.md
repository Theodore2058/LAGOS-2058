# LAGOS-2058

## A Complete Guide to the Nigerian Election Simulation Engine

**LAGOS-2058** is a software system that simulates elections in a fictional future Nigeria (set in the year 2058). It models how 774 local government areas (LGAs) across Nigeria would vote, given 14 political parties, 28 policy issues, and a population divided along ethnic, religious, economic, and demographic lines.

This document explains every part of the system, starting from the simplest concepts and building up to the full technical details. You do not need any background in programming or mathematics to begin reading — each section builds on the last, and every formula is explained in plain language before it appears.

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [What Is a Voting Model?](#2-what-is-a-voting-model)
3. [The World of 2058 Nigeria](#3-the-world-of-2058-nigeria)
4. [The Voters](#4-the-voters)
5. [The Parties](#5-the-parties)
6. [The Issues](#6-the-issues)
7. [How Voters Decide: The Utility Equation](#7-how-voters-decide-the-utility-equation)
8. [Policy Voting: The Spatial Model](#8-policy-voting-the-spatial-model)
9. [Identity Voting: Ethnicity and Religion](#9-identity-voting-ethnicity-and-religion)
10. [Other Influences on the Vote](#10-other-influences-on-the-vote)
11. [From Preferences to Probabilities](#11-from-preferences-to-probabilities)
12. [Who Stays Home: The Turnout Model](#12-who-stays-home-the-turnout-model)
13. [Salience: Why Different Places Care About Different Things](#13-salience-why-different-places-care-about-different-things)
14. [Adding Randomness: The Noise Model](#14-adding-randomness-the-noise-model)
15. [Counting the Votes: Aggregation](#15-counting-the-votes-aggregation)
16. [The Campaign System](#16-the-campaign-system)
17. [Campaign Actions](#17-campaign-actions)
18. [Political Capital: The Resource Economy](#18-political-capital-the-resource-economy)
19. [Campaign Dynamics: Cohesion, Exposure, and Momentum](#19-campaign-dynamics-cohesion-exposure-and-momentum)
20. [Running the Simulation](#20-running-the-simulation)
21. [Understanding the Output](#21-understanding-the-output)
22. [Technical Reference](#22-technical-reference)

---

## 1. The Big Picture

Imagine you could build a miniature Nigeria inside a computer — one where every community has a population with specific ethnic backgrounds, religious beliefs, education levels, income brackets, ages, and occupations. Now imagine placing 14 political parties into this world, each with a platform of positions on 28 different policy issues and a leader from a particular ethnic and religious background.

LAGOS-2058 asks: **if these voters behaved rationally — weighing policy positions, ethnic loyalty, religious affinity, and personal circumstances — who would they vote for? And would they bother to vote at all?**

The system answers this question for each of 774 local government areas in Nigeria, producing:

- **Vote shares** for every party in every LGA
- **Turnout rates** that vary by location and demographics
- **Seat counts** across the whole country
- **Uncertainty ranges** via hundreds of randomized simulation runs

It also includes a **campaign layer** where parties can spend political resources over 8 turns to shift voter awareness, change issue salience, boost their appeal, and drive turnout — simulating the strategic dynamics of a real election campaign.

---

## 2. What Is a Voting Model?

Before diving into the specifics, let's establish what a voting model is and why it's useful.

### The Core Idea

In the real world, millions of people make individual decisions about who to vote for (or whether to vote at all). These decisions are influenced by countless factors: a voter's ethnic identity, their economic situation, whether they agree with a party's stance on education, whether they trust a party's leader, and so on.

A **voting model** is a mathematical framework that tries to capture these decision-making processes in a structured way. It doesn't try to predict what any single person will do (that would be impossible). Instead, it says: "Given what we know about this *type* of person and these parties, here is the *probability* that they would vote for each party."

### Why Probabilities, Not Certainties?

Real voters are unpredictable. Two people with identical backgrounds might vote differently because of a conversation they had, a news story they saw, or simply their mood on election day. The model accounts for this by working with probabilities. It might say: "A young, urban, Igbo, Christian voter with a university degree has a 35% chance of voting for Party A, a 25% chance for Party B, a 15% chance for Party C, and a 25% chance of not voting at all."

### Types of Voting Models

LAGOS-2058 uses a **spatial voting model**, one of the most well-studied frameworks in political science. The word "spatial" refers to the idea that voters and parties can be placed in a "space" defined by policy issues. Voters prefer parties that are "closer" to them in this space — that is, parties whose positions on the issues are most similar to what the voter wants.

But LAGOS-2058 goes beyond pure spatial voting. It also includes:
- **Identity voting** — where ethnicity and religion influence the vote independently of policy
- **Valence** — the overall appeal or quality of a party (charisma, competence, media presence)
- **Economic voting** — how local economic conditions affect preferences
- **Demographic targeting** — how parties can appeal specifically to certain demographic groups
- **Turnout modeling** — whether people vote at all

This combination makes it a **hybrid model** that captures both the rational, issue-based side of voting and the emotional, identity-based side — both of which are critical in the Nigerian context.

---

## 3. The World of 2058 Nigeria

The simulation is set in a fictional future Nigeria that has undergone significant political restructuring. Understanding this setting is important for understanding why the model works the way it does.

### Administrative Zones

Instead of today's 36 states and FCT, this future Nigeria is organized into **8 Administrative Zones (AZs)**, each containing roughly 90-100 LGAs. These zones loosely correspond to the geopolitical zones used in contemporary Nigerian politics (Northwest, Northeast, North Central, Southwest, Southeast, South-South, etc.) but have been formally codified into administrative units.

### 774 Local Government Areas

The LGA remains the basic unit of the simulation. Each of the 774 LGAs has a detailed profile including:

- **Demographics**: Population, density, median age, percentage under 30, fertility rate
- **Ethnicity**: Percentage breakdown across 15+ ethnic groups (Hausa, Fulani, Yoruba, Igbo, Ijaw, Kanuri, Tiv, Nupe, Edo, Ibibio, and several minority groupings)
- **Religion**: Percentages for Muslim, Christian, and Traditionalist, with sub-denominations (Tijaniyya, Qadiriyya, Pentecostal, Catholic, Mainline Protestant, etc.)
- **Urbanization**: Whether it's a major urban center and what percentage of the population is urban
- **Economy**: Oil production status, livelihood types (farming, trade, formal employment), poverty rates, unemployment, GDP estimates, inequality (Gini coefficient)
- **Infrastructure**: Access to electricity, water, healthcare, road quality, market connectivity
- **Education**: Literacy rates (male/female), school enrollment, out-of-school rates, tertiary education access
- **Political factors**: Traditional authority strength, land formalization, conflict history, federal control presence
- **Connectivity**: Mobile phone and internet penetration
- **Cultural markers**: English, Mandarin, and Arabic prestige levels

All of this data lives in a single Excel spreadsheet with 774 rows and 162 columns.

### The Padà Community

One distinctive feature of this 2058 setting is the **Padà** — a fictional diasporic community (the name suggests "returnees" in Yoruba). They have their own political dimension (`pada_status`) and their own party (NRP). This adds a unique layer of identity politics to the simulation.

### Biological Enhancement

Another future-specific element is **biological enhancement** — a policy dimension covering the regulation of human augmentation technologies. Some LGAs have higher percentages of enhanced populations, making this a locally salient issue.

---

## 4. The Voters

### The Concept of Voter Types

It would be computationally impossible to simulate every individual Nigerian. Instead, LAGOS-2058 creates **voter types** — representative profiles that capture every meaningful combination of demographic characteristics.

Think of it this way: instead of modeling 200 million individuals, the system says "let's create one representative person for every possible combination of ethnicity, religion, setting, age, education, gender, livelihood, and income." Each of these types represents all real people who share those characteristics.

### The Eight Dimensions of Identity

Every voter type is defined by a combination of eight characteristics:

| Dimension | Categories | Count |
|-----------|-----------|-------|
| **Ethnicity** | Hausa, Fulani, Hausa-Fulani, Yoruba, Igbo, Ijaw, Kanuri, Tiv, Nupe, Edo, Ibibio, Niger Delta Minorities, Middle Belt Minorities, Padà, Naijin | 15 |
| **Religion** | Tijaniyya (Sufi), Qadiriyya (Sufi), Al-Shahid (activist Muslim), Mainstream Sunni, Pentecostal, Catholic, Mainline Protestant, Traditionalist, Secular | 9 |
| **Setting** | Urban, Peri-urban, Rural | 3 |
| **Age Cohort** | 18-24, 25-34, 35-49, 50+ | 4 |
| **Education** | Below secondary, Secondary, Tertiary | 3 |
| **Gender** | Male, Female | 2 |
| **Livelihood** | Smallholder farmer, Commercial agriculture, Trade/informal, Formal private sector, Public sector, Unemployed/student | 6 |
| **Income** | Bottom 40%, Middle 40%, Top 20% | 3 |

Multiplying all possibilities: 15 × 9 × 3 × 4 × 3 × 2 × 6 × 3 = **174,960 voter types**.

### How Types Map to LGAs

Not all voter types exist equally in every LGA. A rural, northern LGA might have many Hausa-Fulani Muslim smallholders but very few Igbo Catholic urban professionals. The system calculates **type weights** for each LGA — the fraction of the local population that each voter type represents.

These weights are derived from the LGA data:
- Ethnic composition comes from the 86 ethnic percentage columns
- Religious composition comes from the Muslim/Christian/Traditionalist percentages and sub-denomination scales
- Urbanization determines the Urban/Peri-urban/Rural split
- Education weights come from literacy rates and enrollment data
- Livelihood weights come from agricultural, industrial, and service sector percentages
- Income distribution is derived from poverty rates
- Age distribution uses fixed national marginals (25% aged 18-24, 30% aged 25-34, 28% aged 35-49, 17% aged 50+)
- Gender is assumed 50-50

The weights are calculated as the **product of marginals** — meaning each dimension is treated as roughly independent, with some conditional adjustments (for example, rural areas have more agricultural livelihoods).

---

## 5. The Parties

The simulation includes 14 political parties, each representing a distinct political tendency in 2058 Nigeria. Each party is defined by:

1. **A name and acronym**
2. **Positions on all 28 issues** (each on a scale from -5 to +5)
3. **A valence score** (baseline appeal independent of policy)
4. **Leader ethnicity** (which ethnic group the party leader belongs to)
5. **Religious alignment** (the party's religious affiliation)
6. **Demographic coefficients** (targeted appeal to specific groups)
7. **Regional strongholds** (extra support in certain Administrative Zones)
8. **Economic positioning** (-1 = pro-market/elite, +1 = populist/pro-poor)

### The 14 Parties

| Party | Full Name | Base | Character |
|-------|-----------|------|-----------|
| **NDC** | Nigerian Democratic Coalition | Northern Muslim, Hausa-Fulani | Centrist catch-all, strongest in the north |
| **CND** | Congress for Nigerian Democracy | Southwestern, Yoruba | Progressive, pro-women's rights, pro-press freedom |
| **ANPC** | All-Nigeria People's Congress | National | Bridge-building centrist, moderate on all axes |
| **MBPP** | Middle Belt Progressive Party | Central Nigeria, Tiv/Nupe | Federalist, represents Middle Belt minorities |
| **IPA** | Igbo People's Alliance | Southeast, Igbo | Pro-local control, pro-trade, fiscal autonomy |
| **UJP** | United Jihad Party | Far North, Kanuri/Borno | Islamic governance, northern conservative |
| **NWF** | Northern Workers' Front | Northern labor | Populist, worker-focused, extraction economy |
| **NHA** | Northern Heritage Alliance | Northern traditionalist | Conservative, religious authority, heritage preservation |
| **SNM** | Sahel National Movement | Northern border regions | Pastoralist interests, border communities |
| **NSA** | Niger-South Alliance | South-south | Regional coalition, diverse southern interests |
| **CDA** | Coastal Development Alliance | Coastal states | Infrastructure and trade focus |
| **PLF** | People's Liberation Front | Niger Delta, Ijaw | Resource nationalism, oil revenue control |
| **NRP** | Nigerian Renaissance Party | Lagos/Abuja elites, Padà | Meritocratic, cosmopolitan |
| **NNV** | National Niluvian Vanguard | Ideological fringe | Extreme positions, nationally nonviable (~0.5%) |

Each party's positions on 28 issues create a unique political profile. For example, the NDC might score +3 on Sharia jurisdiction (favoring it) while the CND might score -2 (opposing it). The IPA might score +4 on fiscal autonomy (wanting local control) while the ANPC scores +1 (moderate centralism).

---

## 6. The Issues

The simulation models politics across **28 policy dimensions**. Each dimension represents a spectrum of opinion on a major political question, scaled from -5 to +5.

Here is every issue dimension, with what the two extremes represent:

| # | Issue | -5 (Left End) | +5 (Right End) |
|---|-------|---------------|----------------|
| 1 | Sharia Jurisdiction | Fully secular state | Full Sharia implementation |
| 2 | Fiscal Autonomy | Strong centralism | Confederalism (local control) |
| 3 | Chinese Relations | Pivot to Western alliances | Deepen WAFTA (China partnership) |
| 4 | BIC Reform | Abolish the BIC | Preserve the BIC as-is |
| 5 | Ethnic Quotas | Pure meritocracy | Strong affirmative action |
| 6 | Fertility Policy | Population control measures | Pro-natalism (encourage births) |
| 7 | Constitutional Structure | Parliamentary system | Presidential system |
| 8 | Resource Revenue | Federal monopoly on resources | Full local control of revenue |
| 9 | Housing | Pure market housing | Heavy state intervention |
| 10 | Education | Radical localism | Meritocratic centralism |
| 11 | Labor & Automation | Pro-capital (favor businesses) | Pro-labor (favor workers) |
| 12 | Military Role | Strict civilian control | Military guardianship accepted |
| 13 | Immigration | Open borders | Strict restrictionism |
| 14 | Language Policy | Vernacular languages first | English supremacy |
| 15 | Women's Rights | Traditional patriarchy | Aggressive feminism |
| 16 | Traditional Authority | Marginalize traditional rulers | Formally integrate them |
| 17 | Infrastructure | Targeted investment | Universal provision |
| 18 | Land Tenure | Customary land rights | Full formalization |
| 19 | Taxation | Low tax, small government | High tax, redistribution |
| 20 | Agricultural Policy | Free market agriculture | Protectionist smallholder support |
| 21 | Biological Enhancement | Prohibition | Universal access |
| 22 | Trade Policy | Autarky (self-sufficiency) | Full trade openness |
| 23 | Environmental Regulation | Growth first, regulate later | Strong environmental regulation |
| 24 | Media Freedom | State-controlled media | Full press freedom |
| 25 | Healthcare | Market-based healthcare | Universal public provision |
| 26 | Padà Status | Anti-Padà policies | Padà preservation and protection |
| 27 | Energy Policy | Fossil fuel status quo | Aggressive green transition |
| 28 | AZ Restructuring | Return to 36+ states | Keep the 8 AZ system |

### Why 28 Dimensions?

Real politics is multidimensional. Nigerian politics cannot be reduced to a single "left vs. right" spectrum. A voter might be socially conservative (pro-Sharia, traditionalist) but economically progressive (pro-redistribution, pro-labor). Another might be pro-trade-openness but anti-immigration. The 28 dimensions capture these cross-cutting cleavages.

### Voter Ideal Points

Each voter type has an **ideal point** — their preferred position on each of the 28 dimensions. These ideal points are not random; they are constructed from the voter's demographic characteristics:

- **A university-educated voter** tends toward pro-meritocracy, pro-English language, and more cosmopolitan positions
- **A rural smallholder** tends toward pro-local-control, pro-protectionism, and customary land rights
- **A northern Muslim voter** tends toward pro-Sharia, higher religious identity salience
- **A young southern voter** tends toward pro-women's rights, pro-environmental regulation

These base tendencies are further adjusted by the voter's LGA — creating local cultural shifts. A Hausa voter in a cosmopolitan urban LGA will have somewhat different ideal points than a Hausa voter in a rural northern LGA, even if all other demographics are identical.

---

## 7. How Voters Decide: The Utility Equation

Now we arrive at the heart of the model. How does a voter decide which party to support?

### The Concept of Utility

In economics and political science, **utility** is a number that represents how much satisfaction or benefit someone gets from a choice. It's not something anyone actually calculates in their head — it's an abstract way of representing preferences.

A voter's utility for a party is the sum of everything they like and dislike about that party. Higher utility = more appeal. The party with the highest utility is the one the voter is most likely to support.

### The Full Equation

The total utility that voter *i* assigns to party *j* is:

**V(i,j) = Valence + Spatial + Ethnic + Religious + Regional + Economic + Demographic**

In plain language:

> "How much do I like this party?" = "How generally appealing are they?" + "How close are their policies to what I want?" + "Do they represent my ethnic group?" + "Do they share my religious values?" + "Are they strong in my region?" + "Does my economic situation make me like them more or less?" + "Do they specifically appeal to people like me?"

Let's examine each component.

---

## 8. Policy Voting: The Spatial Model

This is the most mathematically complex part of the system, so we'll build up to it step by step.

### The Basic Intuition

Imagine you and a politician each have a position on a single issue — say, taxation. You want moderate taxes (you'd rate yourself at +1 on a -5 to +5 scale). One party wants very high taxes (+4) and another wants very low taxes (-3). Intuitively, you prefer the +4 party because it's closer to your position (+1) than the -3 party.

This is **proximity voting**: you prefer parties that are closer to you in policy space.

### The Directional Alternative

But there's another theory: **directional voting**. This theory says voters don't care about exact positions — they care about which *direction* a party leans. If you want any level of higher taxes (positive side of the scale), you prefer the party that is *most strongly* on your side, even if they're more extreme than you'd like.

Under directional voting, a voter at +1 who favors higher taxes would actually prefer the +4 party not just because it's close, but because it's pushing hard in the direction they favor. A more extreme party is a stronger advocate.

### The Merrill-Grofman Blend

The real world is somewhere in between. The political scientists Bernard Grofman and Samuel Merrill developed a model that **blends** proximity and directional voting using a single mixing parameter called **q**:

- **q = 0**: Pure directional voting. Extremism on "your side" is rewarded. Parties that take strong positions gain support.
- **q = 1**: Pure proximity voting. Distance is punished. Moderate parties closer to the average voter win.
- **q = 0.5** (the default): A balanced mix. Being on the voter's side matters, but being too extreme carries a penalty.

### The Formula (Simple Version)

For a single issue, the spatial utility of a voter with ideal point *x* for a party at position *z* is:

> Spatial utility = (voter position × party position) - (q / 2) × (party position)²

The first term (*x* × *z*) is the directional component — it's positive when voter and party are on the same side (both positive or both negative) and grows larger when the party takes a stronger position.

The second term (-(q/2) × *z*²) is the proximity penalty — it penalizes parties for being extreme. The larger q is, the stronger this penalty becomes.

### Extending to 28 Dimensions

With 28 issues, we simply add up the contributions from each dimension. But there's a mathematical problem: when you add up 28 terms, the total becomes much larger than a single term. This would make policy voting overwhelm everything else (ethnic identity, religion, etc.).

The solution is **square root normalization**: divide the total by √28 ≈ 5.29. This keeps the spatial utility comparable in magnitude to the identity components, regardless of how many issue dimensions the model uses.

### The Full Spatial Formula

For voter *i* and party *j*, across all 28 dimensions *d*, with salience weights *w(d)* for the voter's LGA:

> U_spatial(i,j) = (β / √28) × [ Σ w(d) × x(i,d) × z(j,d) - (q/2) × Σ w(d) × z(j,d)² ]

Where:
- **β** (beta_s = 3.0) is the **spatial sensitivity** — how much policy matters relative to other factors. Higher β means policy positions drive more of the vote.
- **w(d)** is the **salience weight** for issue *d* in this LGA — how much local voters care about this issue (explained in [Section 13](#13-salience-why-different-places-care-about-different-things)).
- **x(i,d)** is the voter's ideal point on issue *d*.
- **z(j,d)** is the party's position on issue *d*.
- **q** (= 0.5) is the proximity-directional mix.
- **√28** is the dimensional normalization.

### What This Means in Practice

- A voter in an oil-producing LGA (where resource revenue has high salience) will weight parties' positions on resource revenue heavily
- A party that takes extreme positions on many issues will attract strong directional supporters but repel moderate voters
- The spatial model creates natural geographic variation: northern voters with pro-Sharia preferences favor different parties than southern voters with secular preferences

---

## 9. Identity Voting: Ethnicity and Religion

Policy isn't everything. In many democracies — and especially in Nigeria — ethnic and religious identity play a massive role in voting decisions. LAGOS-2058 models this explicitly.

### Ethnic Affinity

Each party has a leader from a particular ethnic group. Voters of the same ethnic group feel an **affinity** toward that party's leader. This is captured through an **ethnic affinity matrix** — a table that maps every (voter ethnicity, party leader ethnicity) pair to a score between 0 and 1.

- A score of 1.0 means maximum affinity (same group)
- A score of 0.0 means no affinity at all
- Intermediate scores represent partial affinity (related groups, historical alliances, etc.)

For example:
- A Hausa voter evaluating a party with a Hausa leader: affinity ≈ 0.9
- A Hausa voter evaluating a party with a Fulani leader: affinity ≈ 0.6 (historically allied groups)
- A Hausa voter evaluating a party with a Yoruba leader: affinity ≈ 0.15 (low but non-zero)
- A Hausa voter evaluating a party with an Igbo leader: affinity ≈ 0.10 (very low)

The ethnic component of utility is:

> U_ethnic(i,j) = α_e × affinity(voter_ethnicity, party_leader_ethnicity)

Where **α_e** (alpha_e = 3.0) is the **ethnic sensitivity parameter**. This is the single largest driver of voting behavior in the model — deliberately calibrated to reflect the reality that ethnic identity remains the primary political cleavage in Nigerian politics.

### Religious Affinity

Religious affinity works the same way, with its own matrix and its own sensitivity parameter:

> U_religious(i,j) = α_r × affinity(voter_religion, party_religious_alignment)

Where **α_r** (alpha_r = 2.0) is the **religious sensitivity parameter**. It is deliberately set lower than ethnic sensitivity, reflecting that while religion matters, ethnicity tends to be the stronger predictor of voting behavior in Nigeria.

The religious affinity matrix captures not just the Muslim-Christian divide but the important divisions within each religion:
- A Tijaniyya Sufi voter and a mainstream Sunni-aligned party share some affinity
- A Pentecostal voter and a Catholic-aligned party share Christian identity but differ in denomination
- A Traditionalist voter has low affinity with both Muslim and Christian-aligned parties

### The 15 Ethnic Groups

The model recognizes these ethnic groups:

**Northern groups:** Hausa, Fulani, Hausa-Fulani (undifferentiated), Kanuri
**Southern groups:** Yoruba, Igbo, Ijaw, Edo, Ibibio
**Central groups:** Tiv, Nupe
**Collective groups:** Niger Delta Minorities, Middle Belt Minorities
**Special groups:** Padà (diasporic returnees), Naijin

### The 9 Religious Categories

**Muslim:** Tijaniyya (Sufi order), Qadiriyya (Sufi order), Al-Shahid (activist movement), Mainstream Sunni
**Christian:** Pentecostal, Catholic, Mainline Protestant
**Other:** Traditionalist, Secular

---

## 10. Other Influences on the Vote

Beyond policy and identity, several additional factors influence how voters evaluate parties.

### Valence

**Valence** is a party's baseline appeal — the part of its attractiveness that has nothing to do with policy or identity. It captures things like:
- Leadership charisma and competence
- Organizational strength
- Media presence and brand recognition
- Perceived corruption or cleanliness

Each party has a valence score (one party is set to 0 as the reference point). A party with valence +0.3 has a structural advantage over one with valence 0 — all else being equal, voters find it more appealing.

### Regional Strongholds

Parties can have extra appeal in certain Administrative Zones, representing historical territorial bases of support, patron-client networks, and institutional party infrastructure. These are expressed as additive bonuses:

> U_regional(i,j) = regional_stronghold_bonus(party_j, voter_AZ)

A party might have +1.5 in its home region (substantial advantage) and -0.5 in a hostile region (mild penalty).

### Economic Voting

Local economic conditions interact with a party's economic positioning:

> U_economic(i,j) = β_econ × economic_positioning(j) × local_grievance_z

Where:
- **β_econ** (= 0.3) is the economic voting sensitivity
- **economic_positioning** ranges from -1 (pro-market/elite) to +1 (populist/pro-poor)
- **local_grievance_z** is the LGA's economic grievance level, standardized (mean 0, standard deviation 1), derived from poverty rates, unemployment, and infrastructure deficits

This means populist parties gain support in economically deprived LGAs, while pro-market parties do better in prosperous areas.

### Demographic Targeting

Parties can have specific appeal to certain demographic groups through **demographic coefficients**. For example, a party might have a +0.2 coefficient for "Tertiary education" voters (attracting the educated) or a +0.15 coefficient for "18-24" voters (attracting youth).

These coefficients are optional and party-specific, allowing fine-grained political targeting.

---

## 11. From Preferences to Probabilities

We now have a utility score for every voter type for every party. But utility scores aren't votes — we need to convert them into **probabilities**. This is where the **softmax function** (also called the multinomial logit) comes in.

### The Intuition

Imagine a voter has utility scores of 5.0, 4.0, and 3.0 for three parties. The softmax function converts these into probabilities that:
1. Add up to 100%
2. Give the highest probability to the party with the highest utility
3. Don't give zero probability to any party (because there's always some chance of surprise)

### How It Works

The probability that voter *i* votes for party *j* is:

> P(j) = exp(λ × V(j)) / [ exp(λ × V(1)) + exp(λ × V(2)) + ... + exp(λ × V(J)) ]

Where:
- **exp** is the exponential function (e raised to a power)
- **λ** (lambda, called "scale" in the code, = 1.5) controls how **sharply** voters respond to utility differences

### The Role of the Scale Parameter

The scale parameter λ is crucial:

- **Low λ (e.g., 0.5)**: Voters are "mushy." Even large utility differences produce only small probability differences. Many parties get meaningful vote shares. This represents a world where voters are fickle, uninformed, or vote randomly.
- **High λ (e.g., 5.0)**: Voters are "sharp." Small utility differences produce large probability gaps. The highest-utility party captures almost all votes. This represents a world where voters are perfectly rational and strategic.
- **λ = 1.5 (the default)**: A moderate setting. The party with the highest utility gets the most votes, but other parties still receive meaningful support. This produces the kind of multiparty fragmentation seen in real Nigerian elections.

### A Concrete Example

Suppose three parties have utilities of 3.0, 2.5, and 2.0, with λ = 1.5:

- exp(1.5 × 3.0) = exp(4.5) ≈ 90.0
- exp(1.5 × 2.5) = exp(3.75) ≈ 42.5
- exp(1.5 × 2.0) = exp(3.0) ≈ 20.1

Total: 90.0 + 42.5 + 20.1 = 152.6

Probabilities: 59%, 28%, 13%

The leading party gets the most votes but doesn't sweep — the others still compete.

### Numerical Stability

When utilities are very large, the exponential function can produce numbers too big for a computer to handle (called "overflow"). The model prevents this using the **max-subtraction trick**: before computing exponentials, it subtracts the maximum utility from all values. This doesn't change the probabilities (it cancels out in the fraction) but keeps the numbers manageable.

---

## 12. Who Stays Home: The Turnout Model

Not everyone votes. In many elections, especially in post-authoritarian or developing contexts, turnout can be quite low. LAGOS-2058 models turnout through an elegant mechanism called the **abstention-as-party model**.

### The Core Idea

Instead of treating "not voting" as a separate decision, the model treats it as if the voter has one additional option: the "abstention party." This virtual party competes with all real parties for the voter's choice. If the abstention option has higher utility than all real parties, the voter stays home.

### What Makes Someone Not Vote?

Three factors drive abstention:

**1. Baseline Apathy (τ₀ = 4.5)**

This represents the default cost of voting — the effort of going to a polling station, the time taken, and general political disengagement. The value 4.5 is set high to reflect a post-authoritarian setting where this is the first election in decades and many citizens are skeptical of democratic institutions.

For a campaign simulation, this is lowered to 3.0 — campaigns exist precisely to overcome this baseline apathy.

**2. Alienation (τ₁ = 0.3)**

If all parties are far from what a voter wants, they feel **alienated** — "nobody represents me." The model measures this as the mean squared distance from the voter's ideal point to the nearest party's positions (averaged across all 28 dimensions). If the closest party is still very far away, the voter is more likely to stay home.

> Alienation component = τ₁ × (average per-dimension squared distance to nearest party)

**3. Indifference (τ₂ = 0.5)**

If several parties are equally appealing (or equally unappealing), the voter feels **indifferent** — "why bother choosing?" The model measures this as how much the voter's top choice stands out from the rest of the field. If the gap between the best party and the average of the rest is small, indifference is high.

> Indifference component = τ₂ / gap between top choice and field mean

When the gap is very small, this term becomes very large, pushing the voter toward abstention.

### The Full Abstention Utility

> V_abstain = τ₀ + τ₁ × min_dist² + τ₂ / max(gap, ε)

Where ε is a tiny number (0.000001) to prevent division by zero.

### Demographic Adjustments to Turnout

Not all voters are equally likely to vote, even with the same party utilities. The model applies demographic adjustments to the abstention utility:

| Group | Adjustment | Reasoning |
|-------|-----------|-----------|
| Tertiary education | -1.0 (more likely to vote) | Educated voters are more politically engaged |
| Below secondary education | +0.3 (less likely to vote) | Less informed, less engaged |
| Age 50+ | -0.5 (more likely to vote) | Older voters are habitual voters |
| Age 18-24 | +0.2 (less likely to vote) | Youth disengagement |
| Urban | -0.2 (more likely to vote) | Easier access to polling stations |
| Public sector worker | -0.4 (more likely to vote) | High political awareness, direct stake |
| Formal private sector | -0.2 (more likely to vote) | Resources and engagement |
| Unemployed/student | +0.3 (less likely to vote) | Disengaged, logistic barriers |
| Smallholder farmer | +0.1 (less likely to vote) | Remote, harder access |
| Top 20% income | -0.3 (more likely to vote) | More stake, more resources |
| Bottom 40% income | +0.2 (less likely to vote) | Logistic barriers, fatalism |
| Female | +0.15 (slightly less likely to vote) | Participation barriers (security, household duties, social norms) |

These adjustments create realistic turnout variation: urban, educated, older, wealthier voters turn out at higher rates. National turnout typically falls in the 30-55% range, varying dramatically by LGA.

### How It All Comes Together

The abstention utility competes with all party utilities through the same softmax function:

> P(vote) = 1 - P(abstain) = 1 - exp(λ × V_abstain) / [Σ exp(λ × V_j) + exp(λ × V_abstain)]

If the abstention utility is higher than all party utilities, the voter is more likely to stay home than to vote. If parties offer compelling choices, the voter is drawn to the polls.

---

## 13. Salience: Why Different Places Care About Different Things

A farmer in the oil-producing Niger Delta cares deeply about resource revenue distribution. A student in Lagos cares more about labor automation and biological enhancement policy. A community near the Sahel border worries about immigration and military security. LAGOS-2058 captures these differences through **variable salience**.

### What Is Salience?

**Salience** is how much voters in a particular area care about a particular issue. Every issue has a **base weight** (how much the average Nigerian cares about it), which is then adjusted up or down based on local conditions.

### How Salience Is Computed

For each LGA and each issue:

> salience_weight = base_weight + Σ (feature_adjustment × LGA_feature)

The result is clamped to be non-negative (you can't care a negative amount about an issue). After all 28 weights are computed, they are normalized so that the total weight equals 28 (preserving the overall scale).

### Examples of Salience Rules

| Issue | Base Weight | Gets Higher When... |
|-------|------------|-------------------|
| Sharia jurisdiction | 0.8 | Northern LGA (+0.15), >60% Muslim (+0.10) |
| Resource revenue | 0.9 | Oil-producing LGA (+0.30), active extraction (+0.25) |
| Fiscal autonomy | 1.0 | Oil-producing (+0.20), former Eastern Region (+0.15) |
| Education | 1.2 | Low literacy (+0.10), urban area (+0.05) |
| Infrastructure | 1.1 | Low electricity access (+0.15), rural (+0.10) |
| Healthcare | 1.0 | Low health access (+0.15) |
| Women's rights | 0.7 | High female literacy gap (+0.10) |
| Environmental regulation | 0.6 | Planned city (+0.10), green presence (+0.05) |
| Labor/automation | 0.6 | High unemployment (+0.10), urban (+0.05) |
| Media freedom | 0.5 | Urban (+0.10), conflict history (+0.05) |

### Derived Features

Some adjustments are based on features computed from the raw data:

- **Ethnic fragmentation** (Herfindahl index: 1 - Σ share²) — measures how diverse the LGA is
- **Access deficit** (100 - electricity%) + (100 - water%) + (100 - health%) — measures infrastructure deprivation
- **Conflict severity** — 0-5 ordinal scale
- **Border proximity** — northern/Sahel regions flag
- **Colonial region** — Western, Eastern, or Mid-Western legacy

### Why This Matters

Variable salience means that the spatial utility calculation effectively uses **different weights in different places**. A party with strong positions on resource revenue will do well in oil-producing LGAs (where that issue is salient) but won't benefit as much in northern LGAs (where Sharia and traditional authority are more salient).

This creates natural **geographic variation** in party support that emerges from the interaction of party positions, voter preferences, and local conditions — rather than being hard-coded.

---

## 14. Adding Randomness: The Noise Model

Real elections are unpredictable. Polls miss late-breaking swings, turnout fluctuates, and local factors create surprises. LAGOS-2058 uses **Monte Carlo simulation** with a multi-tier noise model to capture this uncertainty.

### What Is Monte Carlo Simulation?

Instead of running the election once and getting a single result, the simulation runs it many times (typically 100-1000 iterations), each time adding random perturbations. This produces a **distribution** of possible outcomes rather than a single prediction.

Think of it like weather forecasting: instead of saying "it will rain tomorrow," a good forecast says "there is a 70% chance of rain." Similarly, instead of saying "Party X will win 120 seats," the model says "Party X will win between 90 and 150 seats, with 120 being most likely."

### Three Tiers of Noise

The noise model operates at three nested levels:

**Tier 1: National Shocks**

These represent election-day swings that affect a party everywhere — a last-minute scandal, a viral endorsement, a national mood shift.

> national_shock(j) ~ Normal(0, σ_national²)     for each party j

These shocks are **centered** — they sum to zero across parties. One party's unexpected gain must come at another's expense. σ_national = 0.10 by default.

**Tier 2: Regional Shocks**

These represent zone-specific surprises — regional turnout surges, local media effects, weather on election day.

> regional_shock(j, zone) ~ Normal(0, σ_regional²)     for each party in each AZ

These are also centered within each zone. σ_regional = 0.15 by default (larger than national, since regions are more volatile).

**Tier 3: LGA-Level Noise (Dirichlet)**

At the finest level, the model uses the **Dirichlet distribution** to add LGA-specific randomness. The Dirichlet is a mathematical distribution that generates random sets of proportions that sum to 1 — perfect for vote shares.

The **concentration parameter κ** (kappa = 200) controls how much LGA-level noise there is:
- Higher κ = less noise, results stick closer to the model's prediction
- Lower κ = more noise, more surprises at the local level

### How Noise Is Applied

1. Start with the model's predicted vote shares for each LGA
2. Apply national shocks (shift all LGAs for each party)
3. Apply regional shocks (shift within each AZ)
4. Use Dirichlet to generate final noisy shares
5. Determine the winner in each LGA

This is repeated 100+ times. The result is a distribution: "Party X won this LGA in 73 out of 100 runs" → 73% probability of winning.

### Swing LGAs

An LGA where different parties win in different Monte Carlo runs is called a **swing LGA**. These are the competitive battlegrounds where campaign efforts matter most. Typically 15-25% of LGAs are swing LGAs, which is realistic for a multiparty system.

---

## 15. Counting the Votes: Aggregation

### From Types to LGA Results

The computation follows this path for each LGA:

1. **Calculate type weights**: What fraction of this LGA's population does each of the 174,960 voter types represent?
2. **Compute utilities**: For each voter type, compute their utility for each of the 14 parties
3. **Apply softmax**: Convert utilities to vote probabilities
4. **Compute turnout**: For each type, determine the probability they'll vote
5. **Aggregate**: Weight each type's vote probabilities by their population share and turnout probability

> LGA_vote_share(j) = Σ [type_weight(i) × turnout(i) × P(vote for j | voting)] / Σ [type_weight(i) × turnout(i)]

This weighted average produces a single set of vote shares for each LGA.

### Seat Allocation

The 774 LGAs are grouped into **150 voting districts**, each with a variable number of seats (totaling **622 seats** nationally). Within each district, seats are allocated proportionally using the **Sainte-Laguë method** — a divisor-based proportional representation system that divides each party's district vote total by successive odd numbers (1, 3, 5, 7, ...) and awards seats to the highest quotients.

This means seat allocation is not winner-take-all at the LGA level. A party that wins 40% of the vote in a 5-seat district will typically get 2 seats, while the runner-up at 30% gets 1-2 seats. This produces more proportional outcomes than pure plurality and rewards parties with broad geographic support.

### The Presidential Spread Rule

In Nigeria, winning the presidency requires more than just getting the most total votes — a candidate must demonstrate **geographic spread**. Specifically, they need at least 25% of the vote in at least 24 of the states/zones. This prevents a candidate from winning solely on the back of overwhelming support in their home region.

The model checks this constraint for each party in each Monte Carlo run, flagging parties that fail the spread test. A party might win the most seats overall but still fail the presidential spread requirement.

### Key Statistics

The output includes:
- **Effective Number of Parties (ENP)**: A measure of how fragmented the party system is. ENP = 1/Σ(share²). An ENP of 8 means the system behaves as if there are 8 equally-sized parties.
- **Herfindahl-Hirschman Index (HHI)**: The inverse of fragmentation. HHI = Σ(share²). Lower = more competitive.
- **Competitiveness**: The margin between the winner and runner-up in each LGA.

---

## 16. The Campaign System

Everything described so far produces a **static election** — a snapshot of what would happen if the election were held today with no campaigning. The **campaign layer** adds an 8-turn strategic game on top of this foundation.

### The Core Principle

Campaign actions do not directly change vote shares. Instead, they modify the **inputs** to the election engine — the information environment, issue salience, party appeal, and turnout conditions. The engine then recalculates vote shares based on these modified inputs.

This design is realistic: a political rally doesn't magically move votes from column A to column B. It changes how aware people are of a party, how much they care about certain issues, or how motivated they are to show up on election day. The votes then follow from these changed conditions.

### Five Modification Channels

Campaign effects flow through exactly five channels:

**1. Awareness** — How well voters know a party's policy positions

- Array shape: (774 LGAs × 14 parties)
- Range: 0.60 (minimum) to 1.0 (maximum)
- Starts at 0.60 for all parties in all LGAs (voters are only 60% aware of each party's platform)
- **Monotonically increasing** — awareness can only go up, never down (once you know something, you don't un-know it)
- Effect: Multiplies the spatial utility. At 0.60 awareness, voters only get 60% of the policy signal. At 1.0, they get the full picture. Low awareness makes identity voting dominate; high awareness lets policy compete.

**2. Salience Shift** — How much voters care about specific issues

- Array shape: (774 LGAs × 28 issues)
- Additive modification to the base salience weights
- Capped at 50% of the structural (base) salience — campaigns can nudge issue priorities but can't completely rewrite them
- Renormalized after application (total weight stays at 28)
- Effect: A party that's strong on education can run campaigns to raise education salience, making voters weight that issue more heavily

**3. Valence** — How appealing a party seems beyond policy

- Array shape: (774 LGAs × 14 parties)
- Additive modification to baseline valence
- Range typically -0.5 to +0.5
- Effect: Endorsements, positive media, and charismatic rallies boost valence. Scandals, opposition research, and mismanagement reduce it. This directly adds to a party's utility for all voters in affected LGAs.

**4. Turnout Ceiling** — The maximum achievable turnout in an LGA

- Array shape: (774 LGAs)
- Represents infrastructure constraints on voting (enough polling stations, enough staff, accessible roads)
- Raised by ground game and field operations
- Effect: Even if voters want to vote, inadequate infrastructure can prevent them. This channel lets parties invest in removing those barriers.

**5. Tau Modifier** — Reduction in baseline abstention

- Array shape: (774 LGAs)
- Directly reduces τ₀ (baseline abstention utility) in target LGAs
- Effect: Rallies and ground game generate political excitement that overcomes voter apathy. A tau modifier of -0.12 in an LGA might boost turnout by 3-5 percentage points.

---

## 17. Campaign Actions

Parties can take **14 types of campaign actions**, each with different costs, targets, and effects across the five channels. Every action fills a distinct strategic niche -- there is no single dominant strategy. All action magnitudes are scaled by a **GM score multiplier** (sm = gm_score / 6.0), so the quality of a party's execution directly affects outcomes.

### The Full Action Menu

**1. Manifesto (Cost: 3 PC)**
A major policy document released nationally. Raises awareness broadly (scaled by media infrastructure, 0.08-0.30 range). Can update the party's positions on any of the 28 dimensions. If positions shift too dramatically (more than 3 points on any dimension), the party suffers a credibility penalty (reduced valence) and loses internal cohesion. *Niche: repositioning on issues. The only way to change your party's policy stance.*

**2. Advertising (Cost: 2-5 PC)**
Paid media campaigns. The cost scales with budget tier (0/1/2 extra PC) and medium (TV adds +1 PC surcharge). Comes in different media: radio (better in low-media areas), TV (better in high-media areas, but costs more), social media (scales with internet access). Raises awareness and shifts salience on language-profiled dimensions. Heavy advertising (budget tier >= 1) also provides a small turnout boost. *Niche: broad awareness reach with medium-specific targeting.*

**3. Rally (Cost: 2 PC)**
Physical campaign events. Raises salience (+0.025 x sm) on language-profiled dimensions, boosts awareness (+0.04 x sm) in target LGAs (scaled by population density), reduces abstention (tau -0.02 x sm), and **recovers cohesion** (+0.15 x sm). *Niche: the cheapest cohesion recovery tool and synergy hub -- pairs with ground_game (valence +0.04), advertising (salience +0.02), and endorsement (valence +0.03).*

**4. Ground Game (Cost: 3-5 PC)**
Door-to-door canvassing and field operations. The primary turnout-boosting mechanism (tau -0.05 x intensity x sm). Also raises the turnout ceiling (+0.04 x intensity x sm). Personal contact builds trust (valence +0.02 x intensity x sm) and awareness (+0.03 x intensity x sm). Intensity tier 1 adds +1 PC, tier 2 adds +2 PC. *Niche: the GOTV workhorse. Best combined value per PC when you need turnout + valence in a targeted region. Synergizes with rally (valence) and patronage (tau).*

**5. Endorsement (Cost: 2 PC)**
Securing public support from influential figures. Different endorser types have different valence impact and shape the conversation on different issue dimensions:
- Traditional ruler: +0.12 valence, shifts salience on traditional authority + infrastructure
- Religious leader: +0.10 valence, shifts salience on sharia + women's rights
- ETO leader: +0.10 valence, shifts salience on resource revenue + taxation
- Celebrity: +0.08 valence, shifts salience on biological enhancement + media freedom
- Notable/professional: +0.06 valence, shifts salience on constitutional structure + education

Also provides an awareness boost (+0.05) through the endorser's network. **Endorsements are fragile**: if a party triggers a scandal, all its endorsements are automatically withdrawn. If a party uses ethnic_mobilization in the same region as a religious leader or traditional ruler endorsement, there is a 30% chance the endorsement is withdrawn. *Niche: regional valence with issue framing, but requires careful play to maintain.*

**6. Ethnic Mobilization (Cost: 2 PC)**
Activating ethnic identity as a voting cue. Raises salience on identity-correlated dimensions (ethnic quotas, traditional authority, constitutional structure, AZ restructuring) at +0.04 each. Boosts awareness among the target ethnic group, scaled by their population share in each LGA (+0.08 x ethnic_pct). Provides a turnout boost (tau -0.04 x sm) in the target region. **Generates exposure** (+0.8 per use) -- overuse creates a backlash risk (see [Section 19](#19-campaign-dynamics-cohesion-exposure-and-momentum)). *Niche: cheap identity activation for parties with strong ethnic bases. The high exposure cost means ~3 uses approaches scandal territory.*

**7. Patronage (Cost: 3-5 PC)**
Direct material incentives to voters or communities. Provides a strong valence boost (+0.10 x scale) and turnout mobilization via patronage networks (tau -0.05 x scale) in target LGAs. Small awareness boost (+0.02 x scale). **Generates significant exposure** (+0.3 x scale). Tier 1 adds +1 PC, tier 2 adds +2 PC. *Niche: the strongest single-action valence boost in the game, but carries the highest exposure risk. Best used sparingly in key regions. Synergizes with ground_game (tau -0.03).*

**8. Opposition Research (Cost: 2 PC)**
Investigating and publicizing an opponent's weaknesses. Raises salience on dimensions where the target party holds unpopular positions (+0.03 per dimension, up to 4 dimensions). Applies negative valence (-0.08 x sm) to the target party. Raises the *acting party's own* awareness (+0.02 x sm) as the opposition becomes a topic of conversation. **Costs cohesion** (-0.3) -- going negative hurts internal party discipline. *Niche: the only offensive action that directly damages a rival's valence. Synergizes with media (+0.03 additional valence penalty to target).*

**9. Media Engagement (Cost: 1 PC)**
Press conferences, interviews, social media engagement. Cheap but volatile -- the GM score is amplified (2x deviation from center), so low-quality media backfires hard and high-quality media overperforms. Valence and salience scale with the amplified media impact. Successful media (impact > 0.2) **adds +0.2 exposure** as media blitzes attract scrutiny. Creativity bonuses are capped at +1 for media (vs +3 for other actions), preserving genuine risk. Momentum penalty: -25% effectiveness if the party has changed direction 3+ times recently. *Niche: cheapest action but genuinely risky. Best combined with oppo research for the synergy bonus.*

**10. ETO Engagement (Cost: 3-4 PC)**
Building relationships with Elite Territorial Organizations -- the institutional power brokers in each Administrative Zone. Four categories, each with immediate salience effects on relevant issue dimensions in the target zone:
- **Economic ETOs**: Salience on resource revenue, land tenure, taxation. Awareness boost in AZ.
- **Labor ETOs**: Salience on labor/automation, education, housing.
- **Elite ETOs**: Salience on Chinese relations, constitutional structure, BIC reform.
- **Youth ETOs**: Salience on biological enhancement, media freedom, environmental regulation.

ETO scores accumulate on a 0-10 scale per (party, category, AZ) and persist across turns. All categories raise awareness in their zone (+0.04 x score_change x sm) and provide a valence boost (+0.02 x score_change x sm) in the AZ. Salience shifts at +0.03 per relevant dimension. Score_change > 3.0 adds +1 PC cost. At score >= 7.0, Economic ETOs generate PC dividends (+1 PC/turn, max 2). At score >= 5.0, parties can use **ETO Intelligence** (free zone-level polling). *Niche: long-term investment with compounding returns. The immediate effects give value on the turn you spend, while dividends and intelligence reward sustained commitment.*

**11. Crisis Response (Cost: 2 PC)**
Reactive action to exogenous events (security crisis, economic shock, scandal). Provides a strong valence boost (+0.08 x sm) and high awareness spike (+0.05 x sm). Also restores party cohesion (+0.50 x sm) -- rallying around a crisis strengthens internal discipline. **Exempt from action fatigue.** *Niche: the best valence-per-PC ratio when a crisis is active, and a strong cohesion recovery tool. Purely reactive -- most valuable on turns when crisis events fire.*

**12. Fundraising (Cost: 2 PC, Generates PC)**
Costs 2 PC to execute; yield depends on source and GM score (poor execution can net a loss). Different sources offer different base yields and side effects:
- **Business elite**: 5 PC base yield, but +1.5 exposure (donors expect favors)
- **Diaspora**: 4 PC base yield, no side effects
- **Grassroots**: 4 PC base yield, turnout boost (tau -0.03 x sm), awareness boost (+0.02 x sm)
- **Membership**: 2-5 PC yield scaled by cohesion, +0.10 cohesion recovery

Actual yield = floor(base x sm), so a poor GM score (sm < 0.5) can result in 0-1 PC yield against a 2 PC cost -- a net loss. Consecutive fundraising from the same source suffers -1 PC per repeat. Economic ETOs scoring >= 7.0 add +1 PC bonus. *Niche: resource generation with meaningful source trade-offs. Business_elite is highest yield but 2 uses = 3.0 exposure = scandal territory.*

**13. Poll (Cost: 1-5 PC by tier)**
Intelligence-gathering action that reveals where voters stand on issue dimensions. Polls return noisy estimates of population-weighted average ideal points for target LGAs -- they tell you *what voters care about*, not how they'll vote. Results are queued and delivered next turn.

Five cost tiers with increasing scope and precision:

| Tier | Cost | Scope | Margin of Error (per dimension) |
|------|------|-------|---------------------------------|
| 1 | 1 PC | National aggregate | +/-1.5 |
| 2 | 2 PC | Zonal breakdown (8 zones) | +/-1.0 |
| 3 | 3 PC | State breakdown | +/-0.7 |
| 4 | 4 PC | State breakdown (tighter) | +/-0.4 |
| 5 | 5 PC | LGA-level detail | +/-0.25 |

Optional filters: target_zones, target_states, specific dimensions. Noise is Gaussian, clamped to [-5, +5]. *Niche: informs strategic decisions about where to advertise, what language to use, and which dimensions to emphasize. Higher tiers let you micro-target.*

**14. ETO Intelligence (Cost: 0 PC)**
Free alternative to polls for parties with established ETO presence. Requires ETO score >= 5.0 in the target zone (any category). Returns zone-level voter positions with margin +/-0.8 (improving to +/-0.5 at ETO score 10). Unlike polls, results are delivered same turn. *Niche: rewards ETO investment with free, faster intelligence. The margin is worse than a tier 2 poll but the cost is zero.*

### Language Profiles

Many actions (advertising, rallies, media) operate through a campaign **language**, which determines which issue dimensions get salience shifts. Seven language profiles are defined:

| Language | Primary Issue Dimensions |
|----------|------------------------|
| **English** | Chinese relations, BIC reform, constitutional structure, labor, media freedom |
| **Hausa** | Sharia, fertility, education, traditional authority, women's rights |
| **Yoruba** | Fiscal autonomy, resource revenue, AZ restructuring, Padà status |
| **Igbo** | Fiscal autonomy, AZ restructuring, resource revenue, trade policy |
| **Arabic** | Sharia (heavy), education, traditional authority, women's rights |
| **Pidgin** | Housing, taxation, labor, healthcare, infrastructure |
| **Mandarin** | Chinese relations (heavy), trade policy, labor, biological enhancement |

This means the same action type (e.g., advertising) will shift different issue dimensions depending on what language it's conducted in — a realistic reflection of how political messaging works in multilingual societies.

---

## 18. Political Capital: The Resource Economy

Campaign actions cost **Political Capital (PC)** — a scarce resource that forces parties to make strategic trade-offs.

### Income and Hoarding

- **Income**: Every party receives **7 PC per turn** automatically
- **Hoarding cap**: A party can hold at most **18 PC** at any time. Excess above 18 is lost before new income is added.
- **Total budget**: Over 8 turns, a party earns 7 x 8 = 56 PC (before fundraising or ETO dividends)
- **Fundraising**: Costs 2 PC; yields 2-5 PC depending on source and GM score (poor execution can net a loss)
- **ETO dividends**: Economic ETOs scoring >= 7 generate +1 PC each (max 2 per turn)

### No Action Cap

There is no per-turn action limit. Parties can take as many actions as they can afford. This means flush parties can take 5-8 actions per turn in the late game, while early turns require careful rationing.

### Variable Costs

Several actions have costs that scale with their parameters:

| Action | Base Cost | Surcharge Conditions |
|--------|-----------|---------------------|
| Advertising | 2 PC | +0/1/2 by budget tier, +1 if medium is TV |
| Rally | 2 PC | (flat cost) |
| Ground Game | 3 PC | +0/1/2 by intensity tier |
| Patronage | 3 PC | +0/1/2 by patronage tier |
| Fundraising | 2 PC | (flat cost; yield depends on source and GM score) |
| ETO Engagement | 3 PC | +1 if score_change > 3.0 |
| Poll | 1-5 PC | Directly set by poll_tier parameter |

### Action Fatigue

Repeating the same action type on consecutive turns suffers diminishing returns:

> fatigue_multiplier = 1 / (1 + 0.2 x consecutive_turns)

After 3 consecutive turns of media engagement, effectiveness drops to 62.5%. Exempt actions: fundraising, poll, manifesto, crisis_response. This prevents spam strategies and encourages action diversity.

### Synergies

Using complementary actions in the same turn on overlapping regions triggers bonus effects:

| Pair | Bonus |
|------|-------|
| Rally + Ground Game | +0.04 valence (ground game primes the audience) |
| Advertising + Rally | +0.02 salience boost (ads amplify rally message) |
| Media + Opposition Research | -0.03 valence to target party (media amplifies oppo) |
| Endorsement + Rally | +0.03 valence (endorser appears at rally) |
| Patronage + Ground Game | -0.03 tau (patronage networks enable GOTV) |

Synergies reward players who plan complementary action pairs rather than stacking the same action.

### Strategic Implications

With 56 PC total (before fundraising), a party must choose between:
- **Breadth vs. depth**: Cheap actions (media at 1 PC) spread thin, while expensive ones (ground_game at 3 PC, patronage at 3 PC) concentrate impact
- **Risk vs. reward**: Patronage gives the best single-action valence (+0.10) but accumulates exposure that can trigger scandals; media is cheap but can backfire with 2x volatility
- **Short-term vs. investment**: ETO engagement costs 3 PC with immediate salience/valence/awareness effects, but compounds into free intelligence and PC dividends at higher scores
- **Offense vs. defense**: Opposition research damages rivals but costs cohesion (-0.3); crisis response is reactive but gives the best valence-per-PC when a crisis fires
- **Cohesion management**: Rally (+0.15 cohesion) and crisis response (+0.50 cohesion) are the only active cohesion recovery tools beyond natural +1/turn healing
- **Information**: Polls and ETO intelligence cost PC (or ETO investment) but inform where to target actions for maximum effect

The hoarding cap (18 PC) prevents indefinite saving, and the lack of an action cap means unspent PC represents wasted potential. This creates a natural campaign rhythm where parties should stay aggressive.

---

## 19. Campaign Dynamics: Cohesion, Exposure, and Momentum

Beyond the five channels, the campaign system tracks several dynamic properties for each party.

### Cohesion (0-10)

**Cohesion** represents a party's internal unity and organizational effectiveness. It ranges from 0 (completely fractured) to 10 (perfectly unified).

- All parties start at cohesion 10.0
- **Cohesion multiplier**: Effects scale with cohesion. A party at cohesion 2 gets only 15% of the benefit from its actions, while a party at cohesion 8+ gets full benefit.
- **Recovery**: Cohesion recovers +1 per turn naturally (internal healing). Rally (+0.15) and crisis response (+0.50) also restore cohesion. Membership fundraising adds +0.10.
- **Broad engagement bonus**: If a party campaigns in 3+ distinct Administrative Zones in a single turn, it gains +1.0 cohesion (capped at 10).
- **Damage**: Opposition research costs -0.3 cohesion. Scandals cost -1.0 cohesion.
- **Region neglect**: If any of a party's support regions (AZs where it has regional strongholds) go unengaged for 3+ consecutive turns, the party suffers -1.0 cohesion per turn.
- **GM score penalty**: When cohesion falls between 4.0 and 5.0, action GM scores suffer a -1 penalty, making it harder to achieve strong outcomes.
- **Implication**: A party that goes negative or neglects its base regions will find its subsequent campaign actions less effective until cohesion recovers

The cohesion multiplier follows a piecewise curve: at cohesion 0-2, effectiveness is 15%; at cohesion 5, it's about 55%; at cohesion 8-10, it's near 100%. This means cohesion damage is devastating and recovery matters.

### Exposure (0+)

**Exposure** represents how much scrutiny and controversy a party has attracted through aggressive tactics.

- Increases from patronage (+0.3 x scale), ethnic mobilization (+0.8 per use), business_elite fundraising (+1.5 per use), and successful media (+0.2 when media_impact > 0.2)
- Penalty kicks in above **1.0** exposure -- the party suffers a valence penalty of -0.04 per point above the threshold (capped at -0.20)
- **Scandal risk**: At exposure 2.0+, each turn carries a chance of triggering a scandal (5% at 2.0, scaling to 75% at 9.0+). Scandals cause -0.12 valence, -3 PC, -1.0 cohesion, and halve remaining exposure
- **Decay**: After 3 consecutive clean turns (no new exposure), exposure decays by -1.0/turn. Scandals also halve exposure.
- **Endorsement withdrawal**: Scandals auto-withdraw all endorsements. Additionally, using ethnic mobilization has a 30% chance of withdrawing religious_leader or traditional_ruler endorsements.

This creates a risk/reward trade-off: patronage (strongest valence) and ethnic mobilization (cheapest identity play) are powerful tools, but a single ethnic mobilization (+0.8) nearly hits the penalty threshold, and two uses of business_elite fundraising (+3.0 total) guarantees scandal risk. The scandal system makes exposure a genuine strategic constraint.

### Momentum

**Momentum** tracks whether a party's vote share is rising or falling across consecutive turns.

- If a party's share rises for multiple consecutive turns, it gains positive momentum
- If it falls for multiple consecutive turns, it gains negative momentum
- Momentum translates to a small valence bonus or penalty (±0.02 per turn, capped at 3 turns)
- This creates bandwagon effects: success breeds success, failure breeds failure

### Concentration Penalty

If a party repeatedly targets the same region turn after turn, it suffers **diminishing returns**:

> concentration_penalty = 1 / (1 + 0.15 × N)

Where N is the number of consecutive turns targeting the same area. After 3 turns of focusing on the same zone, effectiveness drops to about 69% of the base level. This encourages parties to diversify their campaign efforts geographically.

### EMA Blending

When a party takes the same type of action in the same area on successive turns, the effects don't simply add up or replace each other. Instead, they blend using **Exponential Moving Average (EMA)** with α = 0.65:

> new_effect = 0.65 × latest_action + 0.35 × previous_effect

This means the most recent action dominates (65% weight) but older effects don't vanish entirely (35% carryover). It prevents unrealistic stacking while maintaining campaign continuity.

### Crisis Events

At predetermined turns (e.g., turns 4, 6, and 7 in the default scenario), the simulation can inject **crisis events** — exogenous shocks that change the campaign environment. These might include:

- Security crises (raising military salience, hurting incumbent valence)
- Economic shocks (raising economic salience, benefiting populist parties)
- Scandals (reducing specific parties' valence)
- Natural disasters (raising infrastructure salience)

Parties can respond with the crisis_response action to mitigate damage or capitalize on the situation.

---

## 20. Running the Simulation

### Static Election (No Campaign)

The simplest way to run the simulation:

1. **Load data**: Read the 774-LGA Excel spreadsheet
2. **Configure**: Set engine parameters (τ₀, β_s, α_e, etc.) and define 14 parties
3. **Compute base results**: For each LGA, calculate vote shares and turnout
4. **Run Monte Carlo**: Repeat with random noise 100+ times
5. **Aggregate**: Compute mean seats, win probabilities, swing LGAs, ENP

This takes about 2-3 minutes for 100 Monte Carlo runs. The hot loop processes 174,960 voter types × 774 LGAs × 14 parties using optimized Float32 arithmetic.

### Campaign Simulation

A campaign simulation extends the static election:

1. **Initialize campaign state**: Set up awareness arrays (at 0.60), cohesion, PC balances
2. **For each of 8 turns**:
   a. Process PC income (apply hoarding cap, add 7 PC per party, process ETO dividends)
   b. Process crisis events (if any for this turn)
   c. For each party's actions this turn: validate PC, deduct cost, resolve action
   d. Compile campaign modifiers from accumulated effects
   e. Run full election with modifiers applied
   f. Record results, update momentum
   g. Recover cohesion (+1 per party)
3. **Final results**: The election results after turn 8 are the campaign outcome

### Example Usage

```python
from election_engine.config import Party, EngineParams, ElectionConfig
from election_engine.election import run_election

# Configure the engine
params = EngineParams(tau_0=4.5, beta_s=3.0, alpha_e=3.0, alpha_r=2.0, scale=1.5)

# Define parties (14 of them, each with 28-dimensional position vectors)
parties = [
    Party(name="NDC", positions=[...], valence=0.3, leader_ethnicity="Hausa-Fulani", ...),
    Party(name="CND", positions=[...], valence=0.2, leader_ethnicity="Yoruba", ...),
    # ... 12 more parties
]

config = ElectionConfig(params=params, parties=parties, n_monte_carlo=100)

# Run the election
results = run_election(data_path="data/nigeria_lga_polsim_2058.xlsx", election_config=config)
```

---

## 21. Understanding the Output

### LGA-Level Results

For each of the 774 LGAs, the output includes:
- **Vote shares** for all 14 parties (as percentages)
- **Vote counts** (shares × population × turnout)
- **Winner** (party with highest share)
- **Margin** (winner's share minus runner-up's share)
- **Turnout** (expected percentage of eligible voters who vote)
- **Competitiveness** (how close the race is)

### National Summary

- **National vote shares**: Aggregate across all LGAs (population-weighted)
- **National turnout**: Aggregate turnout rate
- **Seat counts**: How many of the 622 district seats each party won (allocated via Sainte-Laguë across 150 districts)
- **Top party**: Which party won the most seats

### Zonal and State Breakdowns

- Vote shares broken down by Administrative Zone (8 zones)
- Vote shares broken down by state
- Identifies regional strongholds and weaknesses

### Monte Carlo Aggregation

- **Mean seats**: Average seat count across all MC runs
- **Seat standard deviation**: How much seat counts vary
- **Win probability**: Fraction of MC runs where each party leads in seats
- **ENP distribution**: Effective Number of Parties across runs
- **Swing LGA count**: How many LGAs change hands across different runs
- **Spread failure rate**: How often each party fails the presidential spread requirement

### Campaign-Specific Output

When running a campaign simulation, additional output includes:
- **Per-turn results**: Vote shares and seat counts after each campaign turn
- **PC balances**: Remaining political capital for each party
- **Awareness levels**: Current awareness matrix
- **Cohesion and exposure**: Party health metrics
- **ETO scores**: Institutional engagement levels
- **Poll results**: Noisy voter position estimates on issue dimensions (delivered next turn)
- **Synergy log**: Which action pairs triggered bonus effects each turn
- **Scandal history**: Exposure-triggered scandals with valence penalties

---

## 22. Technical Reference

### All Engine Parameters

| Parameter | Symbol | Default | Effect |
|-----------|--------|---------|--------|
| Proximity-directional mix | q | 0.5 | 0 = extremism pays, 1 = centrism pays |
| Spatial sensitivity | β_s | 3.0 | How much policy matters vs. identity |
| Ethnic sensitivity | α_e | 3.0 | Strength of ethnic identity voting |
| Religious sensitivity | α_r | 2.0 | Strength of religious identity voting |
| Scale / rationality | λ | 1.5 | Softmax sharpness (higher = more deterministic) |
| Baseline abstention | τ₀ | 4.5 (static) / 3.0 (campaign) | Higher = lower turnout |
| Alienation | τ₁ | 0.3 | Abstention when all parties distant |
| Indifference | τ₂ | 0.5 | Abstention when top parties similar |
| Economic sensitivity | β_econ | 0.3 | How much local economy affects vote |
| Dirichlet concentration | κ | 200 | Higher = less LGA-level noise |
| National shock SD | σ_nat | 0.10 | National election-day swing magnitude |
| Regional shock SD | σ_reg | 0.15 | Zonal election-day swing magnitude |
| Turnout noise SD | σ_t | 0.0 | National turnout randomness |
| Regional turnout noise | σ_t_r | 0.0 | Zonal turnout randomness |

### Campaign Constants

| Constant | Value | Meaning |
|----------|-------|---------|
| PC income per turn | 7 | Automatic political capital income |
| PC hoarding cap | 18 | Maximum PC a party can hold |
| Fundraising yield | 2-5 base | PC generated per fundraising action (source-dependent, scaled by GM score) |
| Action cap | None | Parties can take unlimited actions per turn (PC-limited) |
| Action fatigue rate | 0.2 | Diminishing returns multiplier for consecutive same-type actions |
| Awareness floor | 0.60 | Minimum awareness level |
| Awareness cap | 1.0 | Maximum awareness level |
| EMA alpha | 0.65 | Effect blending weight for same-key overwrites |
| Concentration decay | 0.15 | Diminishing returns for repeated regional targeting |
| Cohesion recovery | +1/turn | Natural internal healing rate |
| Exposure penalty threshold | 1.0 | Exposure above this triggers valence penalty (-0.04/point, max -0.20) |
| Exposure penalty per point | 0.04 | Valence penalty per exposure point above threshold |
| Scandal threshold | 2.0+ | Exposure level where scandal probability begins (5% at 2.0, up to 75% at 9.0+) |
| ETO dividend threshold | 7 | Economic ETO score needed for PC dividend |
| ETO intelligence threshold | 5 | ETO score needed for free zone-level polling |
| ETO dividend amount | 1 PC | Per qualifying Economic ETO |
| ETO dividend cap | 2/turn | Maximum ETO dividends per turn |

### Project Structure

```
LAGOS-2058/
├── data/
│   └── nigeria_lga_polsim_2058.xlsx    # 774 LGAs × 162 columns
├── src/
│   └── election_engine/
│       ├── config.py                    # EngineParams, Party, ElectionConfig
│       ├── data_loader.py               # Excel ingestion and validation
│       ├── election.py                  # Main orchestrator: run_election()
│       ├── voter_types.py               # 174,960 voter type generation
│       ├── salience.py                  # LGA-dependent issue salience
│       ├── spatial.py                   # Merrill-Grofman spatial utility
│       ├── ethnic_affinity.py           # Ethnic affinity matrix (17 groups: 15 core + 2 catch-alls)
│       ├── religious_affinity.py        # Religious affinity matrix (9 categories)
│       ├── utility.py                   # Total utility computation
│       ├── softmax.py                   # Multinomial logit (probability conversion)
│       ├── turnout.py                   # Abstention-as-party model
│       ├── poststratification.py        # Voter type → LGA aggregation
│       ├── noise.py                     # 3-tier Monte Carlo noise
│       ├── results.py                   # Seat allocation, statistics
│       ├── campaign.py                  # Multi-turn campaign loop
│       ├── campaign_state.py            # CampaignState, CampaignModifiers
│       ├── campaign_actions.py          # 14 action types, PC system, GM scoring, synergies
│       └── campaign_modifiers.py        # Effect compilation, cohesion curve, scandal system
├── api/
│   ├── main.py                          # FastAPI application entry point
│   ├── routes/
│   │   ├── config.py                    # Reference data endpoints (issues, zones, LGAs)
│   │   ├── parties.py                   # Party configuration endpoints
│   │   ├── election.py                  # Static election endpoints
│   │   ├── campaign.py                  # Campaign simulation endpoints
│   │   ├── crises.py                    # Crisis event endpoints
│   │   └── scenarios.py                 # Scenario management endpoints
│   ├── schemas/                         # Pydantic request/response models
│   └── services/                        # Business logic layer
├── frontend/
│   └── src/
│       ├── pages/                       # Dashboard, Parties, Election, Campaign, etc.
│       └── components/                  # ActionBuilder, CheatSheet, TargetSelector, etc.
├── examples/
│   ├── run_election.py                  # Static election with 14 parties
│   ├── run_full_campaign.py             # 8-turn campaign simulation
│   └── ...                              # Additional scenario variants
├── tests/                               # 258 tests across 15 files
└── README.md                            # This document
```

### Performance

- **174,960 voter types × 774 LGAs × 14 parties** computed using Float32 BLAS operations
- Full election run (no campaign): ~2-3 minutes for 100 Monte Carlo iterations
- Campaign simulation (8 turns × 100 MC runs): ~10-15 minutes
- Test suite: ~3 minutes for all 258 tests

### Calibration Targets

The default parameters are calibrated to produce:
- **National turnout**: ~46% (realistic for a post-authoritarian first election)
- **Top party vote share**: ~19% (highly fragmented multiparty system)
- **Effective Number of Parties**: ~8 (genuine multiparty competition)
- **Ethnic heartland dominance**: Parties win overwhelmingly in their ethnic base
- **Geographic variation**: Vote patterns vary realistically by region
- **Swing LGA rate**: ~15-25% of LGAs are competitive

---

## Summary

LAGOS-2058 is a production-grade election simulation that combines:

- **Rigorous political science theory** (Merrill-Grofman spatial model, multinomial logit, abstention-as-party)
- **Rich demographic modeling** (174,960 voter types across 8 dimensions of identity)
- **Nigerian institutional context** (ethnic federalism, presidential spread rule, 774 LGAs, 8 AZs)
- **Strategic campaign gameplay** (5 modification channels, 14 action types, synergies, political capital economy)
- **Robust uncertainty quantification** (3-tier Monte Carlo noise, swing LGA analysis)

It models the full complexity of a multiethnic, multireligious, regionally diverse democracy where identity, policy, economics, and campaign strategy all interact to produce election outcomes.
