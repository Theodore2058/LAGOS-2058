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


def test_many_party_indifference_not_excessive():
    """With many parties, turnout should not collapse due to indifference.

    Regression test: the old top-2 gap formula gave very low turnout with
    many parties because two parties would naturally be close in utility,
    making τ₂/gap blow up.  The field-gap formula (top-1 vs mean-of-rest)
    should keep turnout reasonable when the voter has a clear overall
    preference structure.
    """
    params = _make_params(tau_0=1.5, tau_2=0.5)
    voter = np.zeros(5)
    # 10 parties: voter clearly prefers party 0 (utility 6), parties 1-2 are
    # close to each other (4.9, 4.8), rest trail off
    parties_10 = np.random.default_rng(99).standard_normal((10, 5))
    utils_10 = np.array([6.0, 4.9, 4.8, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5, 0.0])
    p_10 = compute_turnout_probability(utils_10, voter, parties_10, params)

    # Same scenario with 2 parties: voter clearly prefers party 0
    parties_2 = parties_10[:2]
    utils_2 = np.array([6.0, 4.9])
    p_2 = compute_turnout_probability(utils_2, voter, parties_2, params)

    # 10-party turnout should be at least as high as 2-party (voter has
    # even more reason to vote with more at stake), or at least close
    assert p_10 > p_2 * 0.7, (
        f"10-party turnout ({p_10:.3f}) should not be much lower than "
        f"2-party ({p_2:.3f}); indifference term may be overcounting"
    )
    assert p_10 > 0.1, f"10-party turnout ({p_10:.3f}) should not collapse"


def test_batch_turnout_matches_scalar():
    """Vectorised batch turnout must match the scalar version."""
    from election_engine.turnout import batch_compute_vote_probs_with_turnout

    params = _make_params()
    rng = np.random.default_rng(123)
    N, J, D = 6, 5, 4
    parties = rng.standard_normal((J, D))
    voter_ideals = rng.standard_normal((N, D))
    utilities = rng.standard_normal((N, J))

    edu_codes = np.array([0, 1, 2, 0, 1, 2], dtype=np.int32)
    age_codes = np.array([0, 1, 2, 3, 0, 1], dtype=np.int32)
    set_codes = np.array([0, 1, 2, 0, 1, 2], dtype=np.int32)

    batch_cond, batch_turnout = batch_compute_vote_probs_with_turnout(
        utilities, voter_ideals, parties, params,
        edu_codes, age_codes, set_codes
    )

    edu_strs = ["Below secondary", "Secondary", "Tertiary"]
    age_strs = ["18-24", "25-34", "35-49", "50+"]
    set_strs = ["Urban", "Peri-urban", "Rural"]

    for i in range(N):
        demos = {
            "education": edu_strs[edu_codes[i]],
            "age_cohort": age_strs[age_codes[i]],
            "setting": set_strs[set_codes[i]],
        }
        cond_i, turn_i = compute_vote_probs_with_turnout(
            utilities[i], voter_ideals[i], parties, params, demos
        )
        assert np.allclose(batch_cond[i], cond_i, atol=1e-5), f"Mismatch cond row {i}"
        assert abs(batch_turnout[i] - turn_i) < 1e-5, f"Mismatch turnout row {i}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
