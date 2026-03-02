"""Tests for the full utility equation assembly (utility.py)."""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")
from election_engine.config import Party, EngineParams, N_ISSUES
from election_engine.utility import (
    compute_utility,
    compute_utilities_batch,
    precompute_ethnic_utility_table,
    precompute_religious_utility_table,
    precompute_all_ethnic_indices,
    precompute_all_religious_indices,
)
from election_engine.ethnic_affinity import DEFAULT_ETHNIC_MATRIX
from election_engine.religious_affinity import DEFAULT_RELIGIOUS_MATRIX


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_party(name, valence=0.0, ethnicity="Hausa-Fulani Undiff",
                religion="Mainstream Sunni", positions=None):
    if positions is None:
        positions = np.zeros(N_ISSUES)
    return Party(name=name, positions=positions, valence=valence,
                 leader_ethnicity=ethnicity, religious_alignment=religion)


@pytest.fixture
def two_parties():
    """Two parties: one centrist with valence, one extreme with no valence."""
    centrist = _make_party("C", valence=0.5, ethnicity="Yoruba",
                           religion="Mainline Protestant",
                           positions=np.zeros(N_ISSUES))
    extreme = _make_party("E", valence=0.0, ethnicity="Igbo",
                          religion="Pentecostal",
                          positions=np.full(N_ISSUES, 3.0))
    return [centrist, extreme]


@pytest.fixture
def params():
    return EngineParams(q=0.5, beta_s=1.0, alpha_e=2.0, alpha_r=1.0,
                        scale=1.0, tau_0=1.5, tau_1=0.3, tau_2=0.5,
                        kappa=400.0, sigma_national=0.07, sigma_regional=0.10)


# ---------------------------------------------------------------------------
# Tests: compute_utility (single voter)
# ---------------------------------------------------------------------------

class TestComputeUtility:
    """Tests for the single-voter utility function."""

    def test_output_shape(self, two_parties, params):
        """Output should be (J,) where J is number of parties."""
        voter_ideal = np.zeros(N_ISSUES)
        salience = np.ones(N_ISSUES)
        u = compute_utility(voter_ideal, "Yoruba", "Mainline Protestant", {},
                            two_parties, params, salience)
        assert u.shape == (2,)

    def test_valence_advantage(self, two_parties, params):
        """A centrist voter matching the centrist party should prefer it partly due to valence."""
        voter_ideal = np.zeros(N_ISSUES)
        salience = np.ones(N_ISSUES)
        u = compute_utility(voter_ideal, "Yoruba", "Mainline Protestant", {},
                            two_parties, params, salience)
        # Centrist party has valence=0.5, co-ethnic, co-religious
        # Extreme party has valence=0.0, different identity, positions at +3
        assert u[0] > u[1], "Centrist party should be preferred by co-ethnic centrist voter"

    def test_ethnic_affinity_boost(self, params):
        """Same-ethnicity voter-party pair should get higher utility."""
        positions = np.zeros(N_ISSUES)
        p_hausa = _make_party("H", ethnicity="Hausa-Fulani Undiff", positions=positions)
        p_igbo = _make_party("I", ethnicity="Igbo", positions=positions)
        salience = np.ones(N_ISSUES)
        u = compute_utility(np.zeros(N_ISSUES), "Hausa-Fulani Undiff", "Mainstream Sunni",
                            {}, [p_hausa, p_igbo], params, salience)
        # Hausa voter + Hausa party should get max ethnic affinity
        assert u[0] > u[1], "Co-ethnic party should have higher utility"

    def test_religious_affinity_boost(self, params):
        """Same-religion voter-party pair should get higher religious utility."""
        positions = np.zeros(N_ISSUES)
        p_sunni = _make_party("S", ethnicity="Yoruba", religion="Mainstream Sunni",
                              positions=positions)
        p_pente = _make_party("P", ethnicity="Yoruba", religion="Pentecostal",
                              positions=positions)
        salience = np.ones(N_ISSUES)
        u = compute_utility(np.zeros(N_ISSUES), "Yoruba", "Mainstream Sunni",
                            {}, [p_sunni, p_pente], params, salience)
        assert u[0] > u[1], "Co-religious party should have higher utility"

    def test_zero_beta_s_removes_spatial(self, params):
        """With beta_s=0, spatial utility should be zero — only identity and valence matter."""
        params_no_spatial = EngineParams(
            q=0.5, beta_s=0.0, alpha_e=2.0, alpha_r=1.0,
            scale=1.0, tau_0=1.5, tau_1=0.3, tau_2=0.5,
            kappa=400.0, sigma_national=0.07, sigma_regional=0.10,
        )
        far_voter = np.full(N_ISSUES, -5.0)
        close_voter = np.zeros(N_ISSUES)
        p = [_make_party("A", positions=np.zeros(N_ISSUES))]
        salience = np.ones(N_ISSUES)
        u_far = compute_utility(far_voter, "Yoruba", "Secular", {}, p, params_no_spatial, salience)
        u_close = compute_utility(close_voter, "Yoruba", "Secular", {}, p, params_no_spatial, salience)
        assert np.allclose(u_far, u_close), "With beta_s=0 spatial distance should not matter"

    def test_demographic_coefficients(self, params):
        """Parties with demographic_coefficients should get a demo utility boost."""
        p_with = Party(
            name="D", positions=np.zeros(N_ISSUES), valence=0.0,
            leader_ethnicity="Yoruba", religious_alignment="Secular",
            demographic_coefficients={"education": {"Tertiary": 1.5}},
        )
        p_without = _make_party("N", ethnicity="Yoruba", religion="Secular")
        salience = np.ones(N_ISSUES)
        u = compute_utility(np.zeros(N_ISSUES), "Yoruba", "Secular",
                            {"education": "Tertiary"},
                            [p_with, p_without], params, salience)
        assert u[0] > u[1], "Party with demographic coefficient should get bonus for matching voter"


# ---------------------------------------------------------------------------
# Tests: precompute tables
# ---------------------------------------------------------------------------

class TestPrecomputeTables:
    """Tests for ethnic and religious utility precomputation."""

    def test_ethnic_table_shape(self, two_parties, params):
        table, idx = precompute_ethnic_utility_table(two_parties, params, DEFAULT_ETHNIC_MATRIX)
        assert table.shape[1] == 2  # J=2 parties
        assert len(idx) == table.shape[0]

    def test_religious_table_shape(self, two_parties, params):
        table, idx = precompute_religious_utility_table(two_parties, params, DEFAULT_RELIGIOUS_MATRIX)
        assert table.shape[1] == 2
        assert len(idx) == table.shape[0]

    def test_ethnic_diagonal_is_max(self, params):
        """Co-ethnic affinity should be the maximum for each party."""
        p = [_make_party("H", ethnicity="Hausa-Fulani Undiff")]
        table, idx = precompute_ethnic_utility_table(p, params, DEFAULT_ETHNIC_MATRIX)
        hausa_row = idx["Hausa-Fulani Undiff"]
        # Hausa voter → Hausa party should be the max
        assert table[hausa_row, 0] == table[:, 0].max()

    def test_ethnic_indices_shape(self, params):
        """Precomputed ethnic indices should match voter type count."""
        from election_engine.voter_types import generate_all_voter_types
        voter_types = generate_all_voter_types()
        p = [_make_party("X")]
        _, idx = precompute_ethnic_utility_table(p, params, DEFAULT_ETHNIC_MATRIX)
        eth_indices = precompute_all_ethnic_indices(voter_types, idx)
        assert eth_indices.shape == (len(voter_types),)
        assert eth_indices.dtype == np.intp

    def test_religious_indices_shape(self, params):
        """Precomputed religious indices should match voter type count."""
        from election_engine.voter_types import generate_all_voter_types
        voter_types = generate_all_voter_types()
        p = [_make_party("X")]
        _, idx = precompute_religious_utility_table(p, params, DEFAULT_RELIGIOUS_MATRIX)
        rel_indices = precompute_all_religious_indices(voter_types, idx)
        assert rel_indices.shape == (len(voter_types),)


# ---------------------------------------------------------------------------
# Tests: batch computation
# ---------------------------------------------------------------------------

class TestBatchUtility:
    """Tests for vectorised batch utility computation."""

    def test_batch_matches_single(self, two_parties, params):
        """Batch result should match looping over individual voters."""
        rng = np.random.default_rng(42)
        N = 5
        ideals = rng.standard_normal((N, N_ISSUES))
        ethnicities = ["Yoruba", "Igbo", "Hausa-Fulani Undiff", "Kanuri", "Ijaw"]
        religions = ["Secular", "Pentecostal", "Mainstream Sunni", "Al-Shahid", "Catholic"]
        demos = [{} for _ in range(N)]
        salience = np.abs(rng.standard_normal(N_ISSUES)) + 0.1

        batch = compute_utilities_batch(
            ideals, ethnicities, religions, demos,
            two_parties, params, salience,
        )
        assert batch.shape == (N, 2)

        for i in range(N):
            single = compute_utility(
                ideals[i], ethnicities[i], religions[i], demos[i],
                two_parties, params, salience,
            )
            assert np.allclose(batch[i], single, atol=1e-10), f"Mismatch at row {i}"

    def test_batch_with_precomputed_tables(self, two_parties, params):
        """Batch with precomputed lookup tables should match without."""
        rng = np.random.default_rng(7)
        N = 8
        ideals = rng.standard_normal((N, N_ISSUES))
        ethnicities = ["Yoruba", "Igbo", "Hausa-Fulani Undiff", "Kanuri",
                       "Ijaw", "Tiv", "Edo", "Nupe"]
        religions = ["Secular", "Pentecostal", "Mainstream Sunni", "Al-Shahid",
                     "Catholic", "Tijaniyya", "Mainline Protestant", "Traditionalist"]
        demos = [{} for _ in range(N)]
        salience = np.ones(N_ISSUES)

        eth_table = precompute_ethnic_utility_table(two_parties, params, DEFAULT_ETHNIC_MATRIX)
        rel_table = precompute_religious_utility_table(two_parties, params, DEFAULT_RELIGIOUS_MATRIX)

        u_plain = compute_utilities_batch(
            ideals, ethnicities, religions, demos,
            two_parties, params, salience,
        )
        u_precomp = compute_utilities_batch(
            ideals, ethnicities, religions, demos,
            two_parties, params, salience,
            ethnic_utility_table=eth_table,
            religious_utility_table=rel_table,
        )
        assert np.allclose(u_plain, u_precomp, atol=1e-10)

    def test_batch_output_shape(self, two_parties, params):
        """Output shape should be (N, J)."""
        N = 10
        ideals = np.zeros((N, N_ISSUES))
        ethnicities = ["Yoruba"] * N
        religions = ["Secular"] * N
        demos = [{} for _ in range(N)]
        salience = np.ones(N_ISSUES)

        u = compute_utilities_batch(ideals, ethnicities, religions, demos,
                                    two_parties, params, salience)
        assert u.shape == (N, 2)


# ---------------------------------------------------------------------------
# Tests: parameter validation
# ---------------------------------------------------------------------------

class TestParamValidation:
    """Test EngineParams validation."""

    def test_valid_params(self):
        """Default params should be valid."""
        p = EngineParams()
        assert p.q == 0.5

    def test_q_out_of_range(self):
        with pytest.raises(ValueError, match="q must be in"):
            EngineParams(q=1.5)

    def test_negative_beta_s(self):
        with pytest.raises(ValueError, match="beta_s must be"):
            EngineParams(beta_s=-0.1)

    def test_negative_alpha_e(self):
        with pytest.raises(ValueError, match="alpha_e must be"):
            EngineParams(alpha_e=-1.0)

    def test_zero_scale(self):
        with pytest.raises(ValueError, match="scale must be"):
            EngineParams(scale=0.0)

    def test_negative_kappa(self):
        with pytest.raises(ValueError, match="kappa must be"):
            EngineParams(kappa=-10.0)

    def test_negative_sigma(self):
        with pytest.raises(ValueError, match="sigma_national must be"):
            EngineParams(sigma_national=-0.01)

    def test_boundary_values(self):
        """Boundary values should be accepted."""
        p = EngineParams(q=0.0, beta_s=0.0, alpha_e=0.0, alpha_r=0.0,
                         tau_0=0.0, tau_1=0.0, tau_2=0.0,
                         sigma_national=0.0, sigma_regional=0.0, sigma_lga=0.0)
        assert p.q == 0.0
        assert p.beta_s == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
