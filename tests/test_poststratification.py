"""Tests for the poststratification aggregation module."""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")
from election_engine.poststratification import aggregate_to_lga
from election_engine.config import Party, EngineParams, N_ISSUES


def test_vote_shares_sum_to_one():
    """Aggregated vote shares must sum to 1.0."""
    rng = np.random.default_rng(0)
    N, J = 100, 4
    weights = rng.dirichlet(np.ones(N))
    # Normalise each row of vote_probs to sum to 1
    raw = rng.dirichlet(np.ones(J), size=N)
    turnout = rng.uniform(0.3, 0.8, size=N)

    shares, avg_turnout = aggregate_to_lga(weights, raw, turnout)

    assert shares.shape == (J,)
    assert abs(shares.sum() - 1.0) < 1e-5
    assert 0.0 < avg_turnout < 1.0


def test_appendix_a_aggregation():
    """
    Reproduce Appendix A aggregation:
    70% Type A (turnout 40%), 30% Type B (turnout 75%)
    Type A: P(N)=0.999, P(T)=0.001, P(Y)=0.000
    Type B: P(T)=0.89, P(N)=0.08, P(Y)=0.03
    Expected: N ≈ 59%, T ≈ 40%, Y ≈ 1%
    """
    weights = np.array([0.70, 0.30])
    vote_probs = np.array([
        [0.999, 0.001, 0.000],   # Type A
        [0.080, 0.890, 0.030],   # Type B
    ])
    turnout = np.array([0.40, 0.75])

    shares, avg_turnout = aggregate_to_lga(weights, vote_probs, turnout)

    print(f"N={shares[0]:.3f}, T={shares[1]:.3f}, Y={shares[2]:.3f}")
    # Effective votes: A contributes 0.7*0.4=0.28, B contributes 0.3*0.75=0.225
    # Total eff = 0.505
    # N_share = (0.28*0.999 + 0.225*0.08) / 0.505 ≈ (0.2797 + 0.018) / 0.505 ≈ 0.590
    # T_share = (0.28*0.001 + 0.225*0.89) / 0.505 ≈ (0.00028 + 0.20025) / 0.505 ≈ 0.397
    assert abs(shares[0] - 0.59) < 0.02, f"N share={shares[0]:.3f}"
    assert abs(shares[1] - 0.40) < 0.02, f"T share={shares[1]:.3f}"
    assert abs(shares.sum() - 1.0) < 1e-5


def test_zero_weight_types_ignored():
    """Types with zero weight should not affect results."""
    weights = np.array([0.5, 0.0, 0.5])  # middle type has zero weight
    vote_probs = np.array([
        [0.9, 0.1],
        [0.0, 1.0],  # would give very different result if included
        [0.9, 0.1],
    ])
    turnout = np.array([0.6, 0.9, 0.6])

    shares, _ = aggregate_to_lga(weights, vote_probs, turnout)
    # Should be ~90% party 0 regardless of middle type
    assert shares[0] > 0.85


def test_higher_turnout_shifts_result():
    """Higher turnout among educated urban types should shift toward their preferred party."""
    # Type A (educated urban): high turnout, prefers party 0
    # Type B (rural low edu): low turnout, prefers party 1
    weights = np.array([0.4, 0.6])  # B more numerous
    vote_probs = np.array([
        [0.85, 0.15],  # A prefers party 0
        [0.10, 0.90],  # B prefers party 1
    ])

    # Equal turnout: B dominates
    turnout_equal = np.array([0.5, 0.5])
    shares_eq, _ = aggregate_to_lga(weights, vote_probs, turnout_equal)

    # High A turnout: A influence grows
    turnout_high_a = np.array([0.9, 0.3])
    shares_ha, _ = aggregate_to_lga(weights, vote_probs, turnout_high_a)

    assert shares_ha[0] > shares_eq[0], (
        "Higher turnout for party-0-preferring group should increase party 0 share"
    )


def test_all_zero_weights_edge_case():
    """All-zero weights should return uniform shares gracefully."""
    weights = np.zeros(5)
    vote_probs = np.random.default_rng(0).dirichlet(np.ones(3), size=5)
    turnout = np.ones(5) * 0.5

    shares, avg_turnout = aggregate_to_lga(weights, vote_probs, turnout)
    # Should return uniform distribution (not crash)
    assert shares.shape == (3,)
    assert abs(shares.sum() - 1.0) < 1e-5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
