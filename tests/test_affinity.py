"""Tests for ethnic and religious affinity matrices."""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")
from election_engine.ethnic_affinity import (
    EthnicAffinityMatrix,
    DEFAULT_ETHNIC_MATRIX,
    ETHNIC_GROUPS,
)


def test_diagonal_unity():
    """Every group should have perfect affinity with itself."""
    m = EthnicAffinityMatrix()
    for group in ETHNIC_GROUPS:
        a = m.get_affinity(group, group)
        assert a == 1.0, f"{group} self-affinity = {a}, expected 1.0"


def test_known_pairs():
    """Spec-defined values: Yoruba-Igbo = 0.30, Hausa-Igbo = 0.05."""
    m = EthnicAffinityMatrix()
    assert abs(m.get_affinity("Yoruba", "Igbo") - 0.30) < 0.01
    assert abs(m.get_affinity("Hausa", "Igbo") - 0.05) < 0.01


def test_pada_yoruba():
    """Yoruba-Pada: 0.40 per spec."""
    m = EthnicAffinityMatrix()
    assert abs(m.get_affinity("Yoruba", "Pada") - 0.40) < 0.01


def test_naijin_pada():
    """Naijin-Pada highest for Naijin: 0.55 per spec."""
    m = EthnicAffinityMatrix()
    assert abs(m.get_affinity("Naijin", "Pada") - 0.55) < 0.02


def test_alias_resolution():
    """Various alias forms should resolve to canonical groups."""
    m = EthnicAffinityMatrix()
    # Hausa-Fulani cluster aliases
    a1 = m.get_affinity("hausa", "fulani")
    a2 = m.get_affinity("Hausa", "Fulani")
    assert abs(a1 - a2) < 1e-10

    # Igbo alias
    a3 = m.get_affinity("ibo", "Yoruba")
    a4 = m.get_affinity("Igbo", "Yoruba")
    assert abs(a3 - a4) < 1e-10


def test_unknown_group_fallback():
    """Unknown group should return a sensible fallback, not crash."""
    m = EthnicAffinityMatrix()
    a = m.get_affinity("totally_unknown_group", "Yoruba")
    assert 0.0 <= a <= 1.0


def test_utility_scaling():
    """Utility = alpha_e × affinity."""
    m = EthnicAffinityMatrix()
    alpha_e = 2.5
    # In-group
    u_ingroup = m.get_utility("Hausa", "Hausa", alpha_e)
    assert abs(u_ingroup - 2.5) < 1e-10

    # Near-zero cross-group
    u_cross = m.get_utility("Hausa", "Igbo", alpha_e)
    assert abs(u_cross - 2.5 * 0.05) < 0.01


def test_all_values_in_range():
    """All affinity values should be in [0, 1]."""
    mat, groups = DEFAULT_ETHNIC_MATRIX.as_numpy()
    assert np.all(mat >= 0.0), "Negative affinity values found"
    assert np.all(mat <= 1.0), "Affinity values > 1.0 found"


def test_as_numpy_diagonal():
    """Diagonal of numpy matrix should be all 1.0."""
    mat, groups = DEFAULT_ETHNIC_MATRIX.as_numpy()
    assert np.allclose(np.diag(mat), 1.0)


def test_custom_matrix():
    """Users can supply a custom matrix."""
    custom = {"A": {"A": 1.0, "B": 0.3}, "B": {"A": 0.3, "B": 1.0}}
    m = EthnicAffinityMatrix(matrix=custom)
    assert m.get_affinity("A", "B") == 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
