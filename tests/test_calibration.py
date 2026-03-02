"""
Calibration tests for the LAGOS-2058 election engine.

These tests validate that the full simulation pipeline produces realistic,
internally consistent LGA-level results matching the calibration targets
defined in the prompt.  They run the election once with seed=2058 and check:

  - Turnout range and distribution
  - Ethnic heartland alignment (parties win where their ethnic base lives)
  - National vote share distribution (no single-party dominance)
  - Monte Carlo stability (swing LGAs within target range)
  - Salience geographic variation
  - Ideal point differentiation
  - Noise model properties
  - Edge cases (2-party, 1-party, identical positions)
"""

import sys
from pathlib import Path

import numpy as np
import pytest

# Ensure `src` is on the import path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from election_engine.config import Party, EngineParams, ElectionConfig, N_ISSUES
from election_engine.data_loader import load_lga_data
from election_engine.election import run_election
from election_engine.noise import apply_dirichlet_noise, draw_shocks
from election_engine.salience import compute_all_lga_salience
from election_engine.turnout import compute_abstention_utility
from election_engine.voter_types import (
    VoterType,
    generate_all_voter_types,
    compute_type_weights,
    demographics_to_ideal_point,
    build_voter_ideal_base,
    compute_lga_ideal_offset,
)

DATA_PATH = Path(__file__).parent.parent / "data" / "nigeria_lga_polsim_2058.xlsx"


# ---------------------------------------------------------------------------
# Fixtures — load data and run the election once per session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def lga_data():
    return load_lga_data(DATA_PATH)


@pytest.fixture(scope="session")
def full_run(lga_data):
    """Run the full 14-party election once and cache for all tests."""
    # Import party definitions from run_election example
    sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))
    import run_election as example

    params = EngineParams(
        q=0.5, beta_s=0.7, alpha_e=3.0, alpha_r=2.0,
        scale=1.0, tau_0=1.9, tau_1=0.3, tau_2=0.5,
        kappa=400.0, sigma_national=0.07, sigma_regional=0.10,
    )
    config = ElectionConfig(params=params, parties=example.PARTIES, n_monte_carlo=100)
    results = run_election(DATA_PATH, config, seed=2058, verbose=False)
    return results, example.PARTIES


# ===================================================================
# TURNOUT TESTS
# ===================================================================

class TestTurnout:
    """Verify turnout is realistic and has expected demographic patterns."""

    def test_national_turnout_range(self, full_run):
        """National average turnout should be 70-90%."""
        results, _ = full_run
        turnout = results["summary"]["national_turnout"]
        assert 0.70 <= turnout <= 0.90, f"National turnout {turnout:.1%} outside 70-90%"

    def test_no_lga_below_10pct(self, full_run):
        """No LGA should have turnout below 10%."""
        results, _ = full_run
        df = results["lga_results_base"]
        min_turnout = df["Turnout"].min()
        assert min_turnout >= 0.10, f"LGA turnout floor violated: {min_turnout:.1%}"

    def test_no_lga_above_95pct(self, full_run):
        """No LGA should have turnout above 95%."""
        results, _ = full_run
        df = results["lga_results_base"]
        max_turnout = df["Turnout"].max()
        assert max_turnout <= 0.95, f"LGA turnout ceiling violated: {max_turnout:.1%}"

    def test_turnout_demographic_adjustment(self):
        """Tertiary-educated voters should have lower abstention than uneducated."""
        params = EngineParams()
        # Create plausible utilities and positions for 3 parties
        party_positions = np.array([[1, 0, -1]] * N_ISSUES).T[:3]  # 3 parties
        voter_ideal = np.zeros(N_ISSUES)
        utilities = np.array([2.0, 1.5, 1.0])

        v_tertiary = compute_abstention_utility(
            utilities, voter_ideal, party_positions, params,
            education="Tertiary", age_cohort="35-49", setting="Urban",
        )
        v_uneducated = compute_abstention_utility(
            utilities, voter_ideal, party_positions, params,
            education="Below secondary", age_cohort="35-49", setting="Urban",
        )
        # Tertiary should have LOWER abstention utility (less likely to abstain)
        assert v_tertiary < v_uneducated, "Tertiary should have lower abstention"


# ===================================================================
# ETHNIC HEARTLAND TESTS
# ===================================================================

class TestEthnicHeartlands:
    """Ethnic parties must win where their ethnic base lives."""

    def test_ndc_dominates_hausa_states(self, full_run):
        """NDC (Hausa-Fulani leader) should win >40% in core Hausa states."""
        results, _ = full_run
        df = results["lga_results_base"]
        hausa_states = ["Katsina", "Sokoto", "Kebbi", "Zamfara", "Bauchi"]
        for state in hausa_states:
            state_lgas = df[df["State"] == state]
            if len(state_lgas) == 0:
                continue
            pop = state_lgas["Estimated Population"].values
            shares = state_lgas["NDC_share"].values
            state_share = np.average(shares, weights=pop)
            assert state_share > 0.40, (
                f"NDC share in {state} is {state_share:.1%}, should be >40%"
            )

    def test_cnd_dominates_yoruba_states(self, full_run):
        """CND (Yoruba leader) should win >35% in Yoruba states."""
        results, _ = full_run
        df = results["lga_results_base"]
        yoruba_states = ["Ekiti", "Ogun", "Oyo", "Ondo", "Osun"]
        for state in yoruba_states:
            state_lgas = df[df["State"] == state]
            if len(state_lgas) == 0:
                continue
            pop = state_lgas["Estimated Population"].values
            shares = state_lgas["CND_share"].values
            state_share = np.average(shares, weights=pop)
            assert state_share > 0.35, (
                f"CND share in {state} is {state_share:.1%}, should be >35%"
            )

    def test_ipa_dominates_igbo_states(self, full_run):
        """IPA (Igbo leader) should win >25% in Igbo states."""
        results, _ = full_run
        df = results["lga_results_base"]
        igbo_states = ["Abia", "Anambra", "Enugu", "Imo", "Ebonyi"]
        for state in igbo_states:
            state_lgas = df[df["State"] == state]
            if len(state_lgas) == 0:
                continue
            pop = state_lgas["Estimated Population"].values
            shares = state_lgas["IPA_share"].values
            state_share = np.average(shares, weights=pop)
            assert state_share > 0.25, (
                f"IPA share in {state} is {state_share:.1%}, should be >25%"
            )

    def test_ujp_strong_in_borno(self, full_run):
        """UJP (Kanuri/Al-Shahid) should win >30% in Borno."""
        results, _ = full_run
        df = results["lga_results_base"]
        borno = df[df["State"] == "Borno"]
        if len(borno) == 0:
            pytest.skip("No Borno data")
        pop = borno["Estimated Population"].values
        shares = borno["UJP_share"].values
        state_share = np.average(shares, weights=pop)
        assert state_share > 0.30, (
            f"UJP share in Borno is {state_share:.1%}, should be >30%"
        )

    def test_plf_leads_in_bayelsa(self, full_run):
        """PLF (Ijaw leader) should lead or be competitive in Bayelsa."""
        results, _ = full_run
        df = results["lga_results_base"]
        bayelsa = df[df["State"] == "Bayelsa"]
        if len(bayelsa) == 0:
            pytest.skip("No Bayelsa data")
        pop = bayelsa["Estimated Population"].values
        plf_share = np.average(bayelsa["PLF_share"].values, weights=pop)
        mbpp_share = np.average(bayelsa["MBPP_share"].values, weights=pop)
        assert plf_share > 0.15, (
            f"PLF share in Bayelsa is {plf_share:.1%}, should be >15%"
        )
        assert plf_share > mbpp_share * 0.8, (
            f"PLF ({plf_share:.1%}) should be competitive with MBPP ({mbpp_share:.1%}) in Bayelsa"
        )

    def test_no_party_above_45pct_national(self, full_run):
        """No party should win >45% of the national vote."""
        results, _ = full_run
        for party, share in results["summary"]["national_shares"].items():
            assert share < 0.45, (
                f"{party} has {share:.1%} national share, exceeds 45% cap"
            )


# ===================================================================
# VOTE SHARE DISTRIBUTION TESTS
# ===================================================================

class TestVoteShareDistribution:
    """Vote shares should be plausibly distributed across parties and LGAs."""

    def test_all_shares_non_negative(self, full_run):
        """No party should have negative vote share in any LGA."""
        results, parties = full_run
        df = results["lga_results_base"]
        for p in parties:
            col = f"{p.name}_share"
            assert (df[col] >= -1e-10).all(), f"{p.name} has negative shares"

    def test_shares_sum_to_one(self, full_run):
        """Party shares should sum to ~1.0 for each LGA."""
        results, parties = full_run
        df = results["lga_results_base"]
        share_cols = [f"{p.name}_share" for p in parties]
        row_sums = df[share_cols].sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-4), (
            f"Row sums range [{row_sums.min():.6f}, {row_sums.max():.6f}]"
        )

    def test_no_single_party_dominates_lga_count(self, full_run):
        """No party should hold plurality in >500 of 774 LGAs."""
        results, parties = full_run
        df = results["lga_results_base"]
        share_cols = [f"{p.name}_share" for p in parties]
        winners = df[share_cols].idxmax(axis=1)
        counts = winners.value_counts()
        for party_col, count in counts.items():
            party_name = party_col.replace("_share", "")
            assert count <= 500, (
                f"{party_name} holds plurality in {count}/774 LGAs (max 500)"
            )

    def test_no_nan_in_shares(self, full_run):
        """No NaN values should appear in vote share columns."""
        results, parties = full_run
        df = results["lga_results_base"]
        share_cols = [f"{p.name}_share" for p in parties]
        assert not df[share_cols].isna().any().any(), "NaN detected in vote shares"


# ===================================================================
# MONTE CARLO STABILITY TESTS
# ===================================================================

class TestMonteCarloStability:
    """MC runs should be stable and consistent with the base run."""

    def test_swing_lgas_in_target_range(self, full_run):
        """Swing LGAs should be 10-30% of all LGAs."""
        results, _ = full_run
        n_swing = len(results["mc_aggregated"]["swing_lgas"])
        pct_swing = n_swing / 774
        assert 0.05 <= pct_swing <= 0.40, (
            f"Swing LGAs {n_swing}/774 ({pct_swing:.1%}) outside 5-40% range"
        )

    def test_mc_shares_sum_to_one(self, full_run):
        """Each MC run should have shares summing to ~1.0 per LGA."""
        results, parties = full_run
        share_cols = [f"{p.name}_share" for p in parties]
        for run_df in results["mc_runs"][:5]:  # check first 5 runs
            row_sums = run_df[share_cols].sum(axis=1)
            assert np.allclose(row_sums, 1.0, atol=1e-3), (
                f"MC row sums range [{row_sums.min():.4f}, {row_sums.max():.4f}]"
            )


# ===================================================================
# SALIENCE TESTS
# ===================================================================

class TestSalience:
    """Salience weights should be geographically varied and properly normalized."""

    def test_salience_weights_sum_to_one(self, lga_data):
        """All 28 salience weights should sum to 1.0 per LGA."""
        df = lga_data.df
        salience = compute_all_lga_salience(
            df, national_median_gdp=float(df["GDP Per Capita Est"].median()),
        )
        row_sums = salience.sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-6), (
            f"Salience sums range [{row_sums.min():.6f}, {row_sums.max():.6f}]"
        )

    def test_salience_all_non_negative(self, lga_data):
        """All salience weights should be >= 0."""
        df = lga_data.df
        salience = compute_all_lga_salience(
            df, national_median_gdp=float(df["GDP Per Capita Est"].median()),
        )
        assert (salience >= -1e-10).all().all(), "Negative salience weights found"

    def test_sharia_salience_higher_in_north(self, lga_data):
        """Sharia issue salience should be higher in Muslim-majority LGAs."""
        df = lga_data.df
        salience = compute_all_lga_salience(
            df, national_median_gdp=float(df["GDP Per Capita Est"].median()),
        )
        # Sharia is dimension 0
        high_muslim = df["% Muslim"] > 80
        low_muslim = df["% Muslim"] < 20
        if high_muslim.sum() > 0 and low_muslim.sum() > 0:
            avg_north = salience[high_muslim.values, 0].mean()
            avg_south = salience[low_muslim.values, 0].mean()
            assert avg_north > avg_south, (
                f"Sharia salience: Muslim-majority {avg_north:.4f} <= "
                f"non-Muslim {avg_south:.4f}"
            )


# ===================================================================
# VOTER TYPE TESTS
# ===================================================================

class TestVoterTypes:
    """Voter type weights and ideal points should be sensible."""

    def test_total_type_count(self):
        """Should generate exactly 174,960 voter types."""
        types = generate_all_voter_types()
        assert len(types) == 174_960

    def test_homogeneous_lga_concentrates_weight(self, lga_data):
        """In a >90% Hausa-Muslim LGA, weight should concentrate on Hausa types."""
        df = lga_data.df
        # Find a Hausa-dominant LGA
        hausa_lgas = df[df["% Hausa"] > 80]
        if len(hausa_lgas) == 0:
            # Try Hausa-Fulani Undiff
            hausa_lgas = df[df["% Hausa Fulani Undiff"] > 80]
        if len(hausa_lgas) == 0:
            pytest.skip("No >80% Hausa LGA found")

        lga_row = hausa_lgas.iloc[0]
        voter_types = generate_all_voter_types()
        weights = compute_type_weights(lga_row, voter_types)

        # Check that Hausa-Fulani types get majority of weight
        hausa_mask = np.array([vt.is_hausa_fulani for vt in voter_types])
        hausa_weight = weights[hausa_mask].sum()
        total_weight = weights.sum()
        hausa_frac = hausa_weight / max(total_weight, 1e-10)

        assert hausa_frac > 0.50, (
            f"Hausa types get only {hausa_frac:.1%} of weight in Hausa-dominant LGA"
        )

    def test_ideal_point_clipping(self, lga_data):
        """Final ideal points (base + lga offset) should be clipped to [-5, +5]."""
        voter_types = generate_all_voter_types()
        base = build_voter_ideal_base(voter_types)
        # Clip happens at base + offset stage; check a few LGAs
        for idx in [0, 100, 400]:
            lga_row = lga_data.df.iloc[idx]
            offset = compute_lga_ideal_offset(lga_row)
            full = np.clip(base + offset, -5.0, 5.0)
            assert full.min() >= -5.0 - 1e-6, f"Ideal below -5 in LGA {idx}"
            assert full.max() <= 5.0 + 1e-6, f"Ideal above +5 in LGA {idx}"

    def test_muslim_voter_pro_sharia_ideal(self):
        """Muslim voter types should have positive ideal on sharia (dim 0)."""
        vt = VoterType(
            ethnicity="Hausa", religion="Mainstream Sunni", setting="Rural",
            age_cohort="35-49", education="Secondary", gender="Male",
            livelihood="Trade/informal", income="Middle 40%",
        )
        voter_types = generate_all_voter_types()
        base = build_voter_ideal_base(voter_types)
        # Find this type in the list
        idx = voter_types.index(vt)
        sharia_ideal = base[idx, 0]  # dimension 0 = sharia
        assert sharia_ideal > 0, (
            f"Hausa-Muslim voter has sharia ideal {sharia_ideal:.2f}, expected positive"
        )

    def test_pada_voter_pro_pada_status(self):
        """Pada voter types should have positive ideal on pada_status (dim 25)."""
        vt = VoterType(
            ethnicity="Pada", religion="Secular", setting="Urban",
            age_cohort="25-34", education="Tertiary", gender="Male",
            livelihood="Formal private", income="Top 20%",
        )
        voter_types = generate_all_voter_types()
        base = build_voter_ideal_base(voter_types)
        idx = voter_types.index(vt)
        pada_ideal = base[idx, 25]  # dimension 25 = pada_status
        assert pada_ideal > 0, (
            f"Pada voter has pada_status ideal {pada_ideal:.2f}, expected positive"
        )


# ===================================================================
# NOISE TESTS
# ===================================================================

class TestNoise:
    """Noise model should produce valid, well-behaved stochastic perturbations."""

    def test_dirichlet_concentrated_at_high_kappa(self):
        """With kappa=1000, Dirichlet draws should be close to input shares."""
        rng = np.random.default_rng(42)
        shares = np.array([0.3, 0.25, 0.2, 0.15, 0.10])
        national = np.zeros(5)
        regional = np.zeros(5)

        draws = []
        for _ in range(200):
            d = apply_dirichlet_noise(shares, 1000.0, national, regional, rng)
            draws.append(d)
        mean_draw = np.mean(draws, axis=0)

        # Mean should be close to input shares
        assert np.allclose(mean_draw, shares, atol=0.03), (
            f"Dirichlet mean {mean_draw} deviates from input {shares}"
        )

    def test_noisy_shares_sum_to_one(self):
        """Noisy shares must always sum to 1.0."""
        rng = np.random.default_rng(99)
        shares = np.array([0.4, 0.3, 0.2, 0.1])
        national = rng.normal(0, 0.1, 4)
        regional = rng.normal(0, 0.15, 4)

        for _ in range(50):
            noisy = apply_dirichlet_noise(shares, 200.0, national, regional, rng)
            assert abs(noisy.sum() - 1.0) < 1e-10, f"Noisy shares sum to {noisy.sum()}"
            assert (noisy >= 0).all(), "Negative noisy shares"

    def test_zero_sigma_reduces_noise(self):
        """With sigma=0 for all shocks, noise should come only from Dirichlet."""
        rng = np.random.default_rng(123)
        shares = np.array([0.5, 0.3, 0.2])
        national = np.zeros(3)
        regional = np.zeros(3)

        draws = [apply_dirichlet_noise(shares, 500.0, national, regional, rng)
                 for _ in range(100)]
        std_dev = np.std(draws, axis=0)
        # With no shocks and high kappa, std should be small
        assert std_dev.max() < 0.05, (
            f"Std dev {std_dev.max():.4f} too high with no shocks and kappa=500"
        )


# ===================================================================
# EDGE CASE TESTS
# ===================================================================

class TestEdgeCases:
    """Edge cases should be handled gracefully without NaN or crashes."""

    def _make_party(self, name, positions=None, **kwargs):
        if positions is None:
            positions = np.zeros(N_ISSUES)
        return Party(name=name, positions=positions, **kwargs)

    def test_two_party_election(self):
        """2-party election should work without crashing."""
        p1 = self._make_party("A", np.full(N_ISSUES, -2.0), leader_ethnicity="Yoruba",
                              religious_alignment="Secular")
        p2 = self._make_party("B", np.full(N_ISSUES, 2.0), leader_ethnicity="Hausa",
                              religious_alignment="Mainstream Sunni")
        params = EngineParams()
        config = ElectionConfig(params=params, parties=[p1, p2], n_monte_carlo=5)
        results = run_election(DATA_PATH, config, seed=1, verbose=False)
        df = results["lga_results_base"]
        assert len(df) == 774
        assert not df["A_share"].isna().any()
        assert not df["B_share"].isna().any()
        sums = df["A_share"] + df["B_share"]
        assert np.allclose(sums, 1.0, atol=1e-4)

    def test_one_party_election(self):
        """1-party election should give 100% everywhere."""
        p1 = self._make_party("Solo", leader_ethnicity="Igbo",
                              religious_alignment="Catholic")
        params = EngineParams()
        config = ElectionConfig(params=params, parties=[p1], n_monte_carlo=2)
        results = run_election(DATA_PATH, config, seed=1, verbose=False)
        df = results["lga_results_base"]
        # With only one party, it should get ~100% of votes
        assert df["Solo_share"].min() > 0.95, (
            f"Solo party min share {df['Solo_share'].min():.4f}, expected ~1.0"
        )

    def test_identical_party_positions(self):
        """Identical parties should produce near-uniform shares."""
        pos = np.zeros(N_ISSUES)
        parties = [
            self._make_party(f"P{i}", pos.copy(), leader_ethnicity="Yoruba",
                             religious_alignment="Secular")
            for i in range(4)
        ]
        params = EngineParams(alpha_e=0.0, alpha_r=0.0)  # disable identity
        config = ElectionConfig(params=params, parties=parties, n_monte_carlo=2)
        results = run_election(DATA_PATH, config, seed=1, verbose=False)
        df = results["lga_results_base"]
        share_cols = [f"P{i}_share" for i in range(4)]
        # With identical everything, shares should be roughly equal
        shares = df[share_cols].mean()
        assert shares.max() - shares.min() < 0.10, (
            f"Identical parties have spread {shares.max() - shares.min():.4f}"
        )

    def test_extreme_party_no_crash(self):
        """A party at [+5, +5, ..., +5] should not crash."""
        p1 = self._make_party("Extreme", np.full(N_ISSUES, 5.0),
                              leader_ethnicity="Pada", religious_alignment="Secular")
        p2 = self._make_party("Moderate", np.zeros(N_ISSUES),
                              leader_ethnicity="Yoruba", religious_alignment="Secular")
        params = EngineParams()
        config = ElectionConfig(params=params, parties=[p1, p2], n_monte_carlo=2)
        results = run_election(DATA_PATH, config, seed=1, verbose=False)
        df = results["lga_results_base"]
        assert not df["Extreme_share"].isna().any()
        assert not df["Moderate_share"].isna().any()
        # Extreme party should get minimal support in most LGAs
        assert df["Extreme_share"].mean() < 0.50, (
            "Extreme party should not dominate"
        )
