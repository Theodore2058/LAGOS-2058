"""Tests for the numerically stable softmax module."""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")
from election_engine.softmax import softmax, scaled_softmax, log_softmax


def test_known_values():
    """Spec example: V = [4, 2, 1] → P ≈ [0.844, 0.114, 0.042]."""
    v = np.array([4.0, 2.0, 1.0])
    p = softmax(v, scale=1.0)
    assert abs(p[0] - 0.844) < 0.001, f"P[0]={p[0]:.4f}"
    assert abs(p[1] - 0.114) < 0.001, f"P[1]={p[1]:.4f}"
    assert abs(p[2] - 0.042) < 0.001, f"P[2]={p[2]:.4f}"
    assert abs(p.sum() - 1.0) < 1e-10


def test_overflow_protection():
    """Extreme values must not produce NaN or inf."""
    v = np.array([1000.0, 1.0, 0.0])
    p = softmax(v)
    assert not np.any(np.isnan(p)), "NaN in output"
    assert not np.any(np.isinf(p)), "Inf in output"
    assert abs(p.sum() - 1.0) < 1e-10


def test_negative_values():
    """All negative utilities should still produce valid probabilities."""
    v = np.array([-5.0, -3.0, -1.0])
    p = softmax(v)
    assert np.all(p >= 0), "Negative probabilities"
    assert abs(p.sum() - 1.0) < 1e-10
    # -1 should have highest probability
    assert p[2] > p[1] > p[0]


def test_uniform():
    """Equal utilities → uniform probabilities."""
    v = np.array([2.0, 2.0, 2.0])
    p = softmax(v)
    assert np.allclose(p, 1 / 3), f"Expected [1/3, 1/3, 1/3], got {p}"


def test_batch_mode():
    """Batch of 100 random utility vectors: all rows sum to 1."""
    rng = np.random.default_rng(42)
    utilities = rng.standard_normal((100, 5))
    p = softmax(utilities)
    assert p.shape == (100, 5)
    assert np.allclose(p.sum(axis=1), 1.0), "Rows do not sum to 1"
    assert np.all(p >= 0), "Negative probabilities in batch"


def test_scale_sharpening():
    """Higher scale → sharper distribution (winner-take-all approach)."""
    v = np.array([3.0, 1.0, 0.0])
    p_flat = softmax(v, scale=0.1)
    p_sharp = softmax(v, scale=10.0)
    # Sharp should assign more to the winner
    assert p_sharp[0] > p_flat[0]
    # Both should sum to 1
    assert abs(p_flat.sum() - 1.0) < 1e-10
    assert abs(p_sharp.sum() - 1.0) < 1e-10


def test_scaled_softmax_alias():
    """scaled_softmax should match softmax with same scale."""
    v = np.array([1.0, 2.0, 3.0])
    assert np.allclose(softmax(v, scale=2.0), scaled_softmax(v, scale=2.0))


def test_log_softmax():
    """log_softmax should equal log of softmax."""
    v = np.array([1.0, 2.0, 3.0])
    assert np.allclose(log_softmax(v), np.log(softmax(v)), atol=1e-10)


def test_two_party():
    """Two parties: equivalent to logistic function."""
    v = np.array([2.0, 0.0])
    p = softmax(v)
    expected = 1 / (1 + np.exp(-2.0))
    assert abs(p[0] - expected) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
