"""Tests for the unified spatial voting model."""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")
from election_engine.spatial import spatial_utility, batch_spatial_utility


# Appendix A test setup (2-issue simplified for sanity, then full 28-issue)
# Type A ideal = [3, 0] (2D), Party N positions = [4, 1]
# salience = [2.5, 0.3], q=0.5, beta_s=1.0
# Weighted dot: 2.5*3*4 + 0.3*0*1 = 30.0
# Weighted norm²: 2.5*16 + 0.3*1 = 40.3
# Spatial = 1.0 * (30.0 - 0.25 * 40.3) = 30.0 - 10.075 = 19.925

VOTER_A = np.array([3.0, 0.0])
PARTY_N = np.array([[4.0, 1.0]])   # shape (1, 2)
SALIENCE = np.array([2.5, 0.3])


def test_appendix_a_spatial():
    """Reproduce Appendix A spatial utility: Type A + Party N = 19.925."""
    u = spatial_utility(VOTER_A, PARTY_N, beta_s=1.0, q=0.5, salience_weights=SALIENCE)
    assert u.shape == (1,)
    assert abs(u[0] - 19.925) < 1e-6, f"Expected 19.925, got {u[0]:.6f}"


def test_pure_directional_q0():
    """q=0: no proximity penalty. Utility = beta_s * (x·z)."""
    x = np.array([2.0, 1.0])
    z = np.array([[3.0, 2.0]])
    u = spatial_utility(x, z, beta_s=1.0, q=0.0)
    expected = 1.0 * (1.0 * (2*3 + 1*2) - 0.0)  # = 8.0
    assert abs(u[0] - 8.0) < 1e-10


def test_pure_proximity_q1():
    """q=1: pure proximity. Utility = beta_s * (x·z - 0.5 * ||z||²)."""
    x = np.array([2.0, 1.0])
    z = np.array([[3.0, 2.0]])
    u = spatial_utility(x, z, beta_s=1.0, q=1.0)
    # Formula: beta_s * [dot - (q/2)*||z||²]
    # q=1 → dot - 0.5*||z||² = (2*3+1*2) - 0.5*(9+4) = 8 - 6.5 = 1.5
    dot = 2*3 + 1*2                    # 8.0
    norm2 = 3**2 + 2**2               # 13.0
    expected = dot - 0.5 * norm2       # 1.5
    assert abs(u[0] - expected) < 1e-10, f"Expected {expected}, got {u[0]}"


def test_uniform_vs_weighted_salience():
    """Uniform salience [1,1,...] should match no salience argument."""
    x = np.array([1.0, 2.0, -1.0])
    z = np.array([[0.5, 1.5, 0.3], [-1.0, 0.0, 2.0]])
    u_none = spatial_utility(x, z, beta_s=1.5, q=0.4)
    u_ones = spatial_utility(x, z, beta_s=1.5, q=0.4, salience_weights=np.ones(3))
    assert np.allclose(u_none, u_ones)


def test_multiple_parties():
    """Shape check: J parties → (J,) output."""
    x = np.zeros(5)
    z = np.random.default_rng(0).standard_normal((7, 5))
    u = spatial_utility(x, z, beta_s=1.0, q=0.5)
    assert u.shape == (7,)


def test_batch_shape():
    """Batch of N voters × J parties → (N, J) output."""
    rng = np.random.default_rng(42)
    voters = rng.standard_normal((50, 28))
    parties = rng.standard_normal((4, 28))
    u = batch_spatial_utility(voters, parties, beta_s=1.0, q=0.5)
    assert u.shape == (50, 4)


def test_batch_matches_single():
    """Batch result should match looping over individual voters."""
    rng = np.random.default_rng(99)
    voters = rng.standard_normal((10, 5))
    parties = rng.standard_normal((3, 5))
    w = np.abs(rng.standard_normal(5)) + 0.1

    batch = batch_spatial_utility(voters, parties, beta_s=2.0, q=0.3, salience_weights=w)
    for i in range(10):
        single = spatial_utility(voters[i], parties, beta_s=2.0, q=0.3, salience_weights=w)
        assert np.allclose(batch[i], single), f"Mismatch at row {i}"


def test_beta_s_scaling():
    """Doubling beta_s should double the utility."""
    x = np.array([1.0, -1.0])
    z = np.array([[2.0, 0.5]])
    u1 = spatial_utility(x, z, beta_s=1.0, q=0.5)
    u2 = spatial_utility(x, z, beta_s=2.0, q=0.5)
    assert np.allclose(u2, 2.0 * u1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
