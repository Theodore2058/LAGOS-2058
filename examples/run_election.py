"""
Example: Run a full LAGOS-2058 election with 5 sample parties.

Usage:
    python examples/run_election.py

This script defines 5 parties spanning the 2058 Nigerian political landscape,
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

NDF_POSITIONS = np.array([
    +3.0,  # 0  sharia: moderate pro
    -1.0,  # 1  fiscal: mildly centralist
    -1.0,  # 2  chinese: mild Western tilt
    -2.0,  # 3  bic: anti-BIC
    +3.0,  # 4  ethnic quotas: pro (northern advantage)
    +2.0,  # 5  fertility: pro-natalist
    +2.0,  # 6  constitutional: presidential (majority friendly)
    -2.0,  # 7  resource: centralist
    -1.0,  # 8  housing: mildly market
    -2.0,  # 9  education: decentralist
    -2.0,  # 10 labor: pro-capital
    +2.0,  # 11 military: guardianship
    +1.0,  # 12 immigration: mildly restrictionist
    -1.5,  # 13 language: anti-English supremacy
    -2.0,  # 14 women's rights: conservative
    +2.5,  # 15 trad authority: pro
    -0.5,  # 16 infrastructure: mildly targeted
    +1.0,  # 17 land tenure: customary
    -1.5,  # 18 taxation: low tax
    +1.5,  # 19 agriculture: protectionist
    -2.5,  # 20 bio enhancement: against
    -1.5,  # 21 trade: autarky leaning
    -1.0,  # 22 environment: growth first
    -2.0,  # 23 media: state control
    -1.5,  # 24 healthcare: market leaning
    -2.0,  # 25 pada status: anti-Padà
    -1.5,  # 26 energy: fossil
    -1.5,  # 27 az restructuring: keep current AZs
])

TECHNOCRATIC_POSITIONS = np.array([
    -3.0,  # 0  sharia: secularist
    +0.0,  # 1  fiscal: centrist
    +3.0,  # 2  chinese: WAFTA pro
    +3.0,  # 3  bic: preserve BIC
    -3.0,  # 4  ethnic quotas: meritocratic
    -1.0,  # 5  fertility: mild control
    -2.0,  # 6  constitutional: parliamentary
    +1.0,  # 7  resource: mild decentralization
    -1.0,  # 8  housing: mildly market
    +3.0,  # 9  education: meritocratic centralism
    +1.0,  # 10 labor: mild labor
    -2.0,  # 11 military: civilian
    +2.0,  # 12 immigration: open
    +2.5,  # 13 language: English prestige
    +2.0,  # 14 women's rights: progressive
    -2.5,  # 15 trad authority: marginalize
    +1.5,  # 16 infrastructure: universal
    +2.0,  # 17 land tenure: formalization
    +0.5,  # 18 taxation: mild redistribution
    -1.0,  # 19 agriculture: market
    +2.5,  # 20 bio enhancement: pro
    +3.5,  # 21 trade: openness
    +2.0,  # 22 environment: regulatory
    +3.0,  # 23 media: press freedom
    +1.5,  # 24 healthcare: mild universal
    +4.0,  # 25 pada status: preserve Padà
    +2.0,  # 26 energy: green leaning
    +2.0,  # 27 az restructuring: keep AZs
])

YORUBA_CONGRESS_POSITIONS = np.array([
    -1.0,  # 0  sharia: mild secular
    +3.0,  # 1  fiscal: strong fiscal autonomy
    +1.0,  # 2  chinese: mild WAFTA
    +0.0,  # 3  bic: neutral
    +1.0,  # 4  ethnic quotas: mild pro
    +0.0,  # 5  fertility: neutral
    -1.5,  # 6  constitutional: semi-parliamentary
    +2.5,  # 7  resource: strong decentralization
    +0.5,  # 8  housing: mild intervention
    +0.5,  # 9  education: centrist
    +1.5,  # 10 labor: pro-labor
    -1.0,  # 11 military: civilian
    +0.5,  # 12 immigration: mild open
    +1.5,  # 13 language: vernacular empowerment
    +1.0,  # 14 women's rights: moderate
    +0.5,  # 15 trad authority: mild integration
    +2.0,  # 16 infrastructure: universal
    +1.0,  # 17 land tenure: mild formalization
    +1.0,  # 18 taxation: mild redistribution
    +1.0,  # 19 agriculture: mild protectionism
    +0.5,  # 20 bio enhancement: cautious pro
    +2.0,  # 21 trade: open
    +1.0,  # 22 environment: moderate regulatory
    +2.0,  # 23 media: press freedom
    +2.0,  # 24 healthcare: universal
    +0.5,  # 25 pada status: mild pro
    +1.0,  # 26 energy: mild green
    -3.0,  # 27 az restructuring: restructure (back to states)
])

PEOPLES_JUSTICE_POSITIONS = np.array([
    -2.0,  # 0  sharia: secular
    +2.0,  # 1  fiscal: strong autonomy
    -3.0,  # 2  chinese: anti-WAFTA/Western
    -3.0,  # 3  bic: abolish
    +2.0,  # 4  ethnic quotas: pro
    -0.5,  # 5  fertility: mild control
    -2.0,  # 6  constitutional: parliamentary
    +3.0,  # 7  resource: strong local control
    +3.0,  # 8  housing: strong state intervention
    +1.0,  # 9  education: mild centralism
    +3.0,  # 10 labor: strong pro-labor
    -1.5,  # 11 military: civilian
    +0.0,  # 12 immigration: neutral
    +0.5,  # 13 language: mild vernacular
    +1.5,  # 14 women's rights: moderate
    -1.0,  # 15 trad authority: marginalize
    +2.5,  # 16 infrastructure: universal
    +0.5,  # 17 land tenure: mild formalization
    +3.0,  # 18 taxation: high redistribution
    +2.0,  # 19 agriculture: protectionist smallholder
    +0.5,  # 20 bio enhancement: cautious pro
    -0.5,  # 21 trade: mild autarky
    +2.0,  # 22 environment: regulatory
    +2.5,  # 23 media: press freedom
    +3.0,  # 24 healthcare: strong universal
    -3.0,  # 25 pada status: anti-Padà
    +1.5,  # 26 energy: green
    -2.0,  # 27 az restructuring: restructure
])

NIM_POSITIONS = np.array([
    +5.0,  # 0  sharia: full Sharia
    +4.0,  # 1  fiscal: confederalist
    -3.0,  # 2  chinese: anti-WAFTA
    -4.0,  # 3  bic: abolish
    +4.0,  # 4  ethnic quotas: strong pro
    +4.0,  # 5  fertility: strong pro-natalist
    +3.0,  # 6  constitutional: strong presidential
    +1.0,  # 7  resource: mild local
    -1.0,  # 8  housing: market
    -3.0,  # 9  education: decentralist
    -3.0,  # 10 labor: pro-capital
    +3.5,  # 11 military: guardianship
    +3.0,  # 12 immigration: strongly restrictionist
    -2.5,  # 13 language: vernacular/Arabic
    -4.0,  # 14 women's rights: conservative
    +4.0,  # 15 trad authority: integrate strongly
    -1.0,  # 16 infrastructure: targeted
    +2.0,  # 17 land tenure: customary
    -3.0,  # 18 taxation: low tax
    +2.0,  # 19 agriculture: protectionist
    -4.0,  # 20 bio enhancement: prohibition
    -3.0,  # 21 trade: autarky
    -1.0,  # 22 environment: growth first
    -4.0,  # 23 media: state control
    -1.0,  # 24 healthcare: market
    -2.0,  # 25 pada status: anti-Padà
    -2.0,  # 26 energy: fossil
    -2.5,  # 27 az restructuring: keep AZs
])

# Validation check
for name, pos in [
    ("NDF", NDF_POSITIONS), ("TA", TECHNOCRATIC_POSITIONS),
    ("YC", YORUBA_CONGRESS_POSITIONS), ("PJP", PEOPLES_JUSTICE_POSITIONS),
    ("NIM", NIM_POSITIONS)
]:
    assert pos.shape == (N_ISSUES,), f"{name} position shape mismatch"
    assert np.all(np.abs(pos) <= 5.0), f"{name} has out-of-range positions"

PARTIES = [
    Party(
        name="NDF",
        positions=NDF_POSITIONS,
        valence=0.0,  # baseline party
        leader_ethnicity="Hausa-Fulani Undiff",
        religious_alignment="Mainstream Sunni",
    ),
    Party(
        name="TA",
        positions=TECHNOCRATIC_POSITIONS,
        valence=0.3,
        leader_ethnicity="Pada",
        religious_alignment="Secular",
    ),
    Party(
        name="YC",
        positions=YORUBA_CONGRESS_POSITIONS,
        valence=0.1,
        leader_ethnicity="Yoruba",
        religious_alignment="Mainline Protestant",
    ),
    Party(
        name="PJP",
        positions=PEOPLES_JUSTICE_POSITIONS,
        valence=0.0,
        leader_ethnicity="Igbo",
        religious_alignment="Pentecostal",
    ),
    Party(
        name="NIM",
        positions=NIM_POSITIONS,
        valence=0.0,
        # NIM represents a pan-northern conservative Islamic platform.  The party
        # was founded in Borno (Kanuri heartland) but its religious appeal targets
        # the broad Mainstream Sunni majority across the north, not just the small
        # Al-Shahid order — giving it a viable base among conservative northern voters.
        leader_ethnicity="Kanuri",
        religious_alignment="Mainstream Sunni",
    ),
]


def main():
    params = EngineParams(
        q=0.5, beta_s=1.0, alpha_e=2.5, alpha_r=1.5,
        scale=1.0, tau_0=1.5, tau_1=0.3, tau_2=0.5,
        kappa=200.0, sigma_national=0.10, sigma_regional=0.15, sigma_lga=0.20,
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
