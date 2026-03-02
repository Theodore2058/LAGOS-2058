"""Tests for the hierarchical noise model."""

import sys
import numpy as np
import pytest

sys.path.insert(0, "src")
from election_engine.config import EngineParams
from election_engine.noise import draw_shocks, apply_dirichlet_noise


def _params(**kwargs):
    defaults = dict(kappa=200.0, sigma_national=0.10, sigma_regional=0.15)
    defaults.update(kwargs)
    return EngineParams(**defaults)


def test_negligible_noise_high_kappa():
    """With kappa=100000 and zero shocks, output ≈ input (kappa controls Dirichlet spread)."""
    rng = np.random.default_rng(0)
    shares = np.array([0.5, 0.3, 0.2])
    # Zero shocks to isolate the kappa effect (national/regional shocks are separate)
    noisy = apply_dirichlet_noise(shares, kappa=100_000,
                                   national_shocks=np.zeros(3),
                                   regional_shocks=np.zeros(3), rng=rng)
    assert np.allclose(noisy, shares, atol=0.01), f"noisy={noisy}, shares={shares}"


def test_low_kappa_varies_widely():
    """With kappa=10 (small), output varies widely but remains valid simplex."""
    rng = np.random.default_rng(42)
    shares = np.array([0.5, 0.3, 0.2])
    params = _params(kappa=10)
    national, regional = draw_shocks(3, [1], params, rng)

    results = []
    for _ in range(50):
        noisy = apply_dirichlet_noise(shares, params.kappa, national, regional[1], rng)
        assert abs(noisy.sum() - 1.0) < 1e-9
        assert np.all(noisy >= 0)
        results.append(noisy)

    results = np.array(results)
    std = results.std(axis=0)
    # With kappa=10, there should be substantial variation
    assert np.any(std > 0.05), f"Expected variation, got std={std}"


def test_output_always_sums_to_one():
    """Final shares must always sum to 1.0."""
    rng = np.random.default_rng(99)
    params = _params(kappa=50)
    for _ in range(100):
        shares = rng.dirichlet(np.ones(5))
        national, regional = draw_shocks(5, [1, 2, 3], params, rng)
        noisy = apply_dirichlet_noise(shares, params.kappa, national, regional[1], rng)
        assert abs(noisy.sum() - 1.0) < 1e-9
        assert np.all(noisy >= 0)


def test_national_shock_correlation():
    """Same national shock applied to two LGAs produces correlated log-space residuals."""
    rng = np.random.default_rng(7)
    params = _params(kappa=1_000_000, sigma_national=2.0, sigma_regional=0.0)
    # Huge kappa → near-zero Dirichlet noise; large sigma_national → strong shock signal.
    national, regional = draw_shocks(3, [1], params, rng)

    shares1 = np.array([0.40, 0.35, 0.25])
    shares2 = np.array([0.45, 0.30, 0.25])

    n1 = apply_dirichlet_noise(shares1, params.kappa, national, regional[1], rng)
    n2 = apply_dirichlet_noise(shares2, params.kappa, national, regional[1], rng)

    # With negligible Dirichlet noise, log(n) ≈ log(shares) + national_shocks.
    # The residuals (log(n) - log(shares)) should be nearly identical for both LGAs,
    # so their correlation must be very high (> 0.99).
    _EPS = 1e-12
    residual1 = np.log(n1 + _EPS) - np.log(shares1 + _EPS)
    residual2 = np.log(n2 + _EPS) - np.log(shares2 + _EPS)
    correlation = float(np.corrcoef(residual1, residual2)[0, 1])
    assert correlation > 0.99, f"Expected high shock correlation, got {correlation:.4f}"


def test_mean_converges_to_predicted():
    """Over 1000 draws, mean should be close to predicted shares."""
    rng = np.random.default_rng(0)
    params = _params(kappa=200, sigma_national=0.0, sigma_regional=0.0)
    shares = np.array([0.50, 0.30, 0.20])
    national = np.zeros(3)
    regional = np.zeros(3)

    samples = [apply_dirichlet_noise(shares, params.kappa, national, regional, rng)
               for _ in range(1000)]
    mean = np.mean(samples, axis=0)
    assert np.allclose(mean, shares, atol=0.02), f"Mean={mean}, expected={shares}"


def test_no_nan_or_inf():
    """No NaN or Inf in output even with extreme inputs."""
    rng = np.random.default_rng(0)
    params = _params(kappa=50)
    # Extreme: one party has almost all share
    shares = np.array([0.999, 0.0005, 0.0005])
    national, regional = draw_shocks(3, [1], params, rng)
    noisy = apply_dirichlet_noise(shares, params.kappa, national, regional[1], rng)
    assert not np.any(np.isnan(noisy))
    assert not np.any(np.isinf(noisy))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
