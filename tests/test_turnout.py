"""Tests for the turnout / abstention-as-party model."""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")
from election_engine.config import EngineParams
from election_engine.turnout import (
    compute_turnout_probability,
    compute_vote_probs_with_turnout,
    compute_abstention_utility,
)


def _make_params(**kwargs):
    defaults = dict(tau_0=1.5, tau_1=0.3, tau_2=0.5)
    defaults.update(kwargs)
    return EngineParams(**defaults)


def test_high_alienation_low_turnout():
    """When all parties are far from voter, abstention utility is high → low turnout."""
    params = _make_params(tau_0=1.5, tau_1=0.5)
    # Voter at 0, parties at ±5 in each dimension
    voter = np.zeros(5)
    parties = np.array([[5.0, 5.0, 5.0, 5.0, 5.0],
                        [-5.0, -5.0, -5.0, -5.0, -5.0]])
    utilities = np.array([3.0, 2.0])

    p_close = compute_turnout_probability(utilities, voter, parties, params)

    # Move parties close to voter
    parties_close = np.array([[0.1, 0.1, 0.1, 0.1, 0.1],
                               [-0.1, -0.1, -0.1, -0.1, -0.1]])
    p_far = compute_turnout_probability(utilities, voter, parties_close, params)

    # Far parties → lower turnout (higher alienation)
    assert p_close < p_far, f"Expected p_close({p_close:.3f}) < p_far({p_far:.3f})"


def test_high_indifference_lower_turnout():
    """When top two parties are nearly equal, indifference term is high → lower turnout."""
    params = _make_params(tau_2=2.0)
    voter = np.zeros(3)
    parties = np.array([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 3.0, 0.0]])

    # Nearly equal top parties → high indifference
    utils_equal = np.array([3.0, 2.99, 0.0])
    p_equal = compute_turnout_probability(utils_equal, voter, parties, params)

    # Dominant party → low indifference
    utils_dominant = np.array([5.0, 1.0, 0.0])
    p_dominant = compute_turnout_probability(utils_dominant, voter, parties, params)

    assert p_equal < p_dominant, (
        f"Equal utils should give lower turnout: equal={p_equal:.3f}, dominant={p_dominant:.3f}"
    )


def test_dominant_party_high_turnout():
    """One party very close and dominant → high turnout."""
    params = _make_params(tau_0=0.5)
    voter = np.zeros(4)
    parties = np.array([[0.1, 0.0, 0.0, 0.0],
                        [-4.0, -4.0, -4.0, -4.0]])
    utils_dominant = np.array([8.0, -5.0])
    p = compute_turnout_probability(utils_dominant, voter, parties, params)
    assert p > 0.5, f"Expected high turnout, got {p:.3f}"


def test_education_boost():
    """Tertiary education should raise turnout vs uneducated voter."""
    params = _make_params()
    voter = np.zeros(3)
    parties = np.random.default_rng(7).standard_normal((3, 3))
    utilities = np.array([2.0, 1.0, 0.0])

    p_tertiary = compute_turnout_probability(
        utilities, voter, parties, params,
        voter_demographics={"education": "Tertiary"}
    )
    p_low = compute_turnout_probability(
        utilities, voter, parties, params,
        voter_demographics={"education": "Below secondary"}
    )
    assert p_tertiary > p_low, (
        f"Tertiary ({p_tertiary:.3f}) should have higher turnout than low ({p_low:.3f})"
    )


def test_no_nan_or_inf():
    """No NaN or Inf values under any conditions."""
    rng = np.random.default_rng(42)
    params = _make_params()
    for _ in range(50):
        voter = rng.standard_normal(10)
        parties = rng.standard_normal((4, 10))
        utilities = rng.standard_normal(4)
        p = compute_turnout_probability(utilities, voter, parties, params)
        assert not np.isnan(p), "NaN turnout probability"
        assert not np.isinf(p), "Inf turnout probability"
        assert 0.0 <= p <= 1.0, f"Probability out of range: {p}"


def test_conditional_probs_sum_to_one():
    """Conditional vote probabilities must sum to 1.0."""
    params = _make_params()
    voter = np.zeros(5)
    parties = np.random.default_rng(0).standard_normal((4, 5))
    utilities = np.array([3.0, 2.0, 1.0, 0.5])
    cond_probs, p_vote = compute_vote_probs_with_turnout(utilities, voter, parties, params)
    assert abs(cond_probs.sum() - 1.0) < 1e-10
    assert cond_probs.shape == (4,)
    assert 0.0 <= p_vote <= 1.0


def test_near_zero_gap_no_crash():
    """gap → 0 should not cause division by zero."""
    params = _make_params()
    voter = np.zeros(2)
    parties = np.array([[1.0, 0.0], [-1.0, 0.0]])
    utilities = np.array([2.0, 2.0])  # exactly equal
    p = compute_turnout_probability(utilities, voter, parties, params)
    assert not np.isnan(p)
    assert 0.0 <= p <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
