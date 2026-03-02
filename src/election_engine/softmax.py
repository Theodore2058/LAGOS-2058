"""
Numerically stable softmax (multinomial logit) for the LAGOS-2058 engine.

The multinomial logit (softmax) converts utilities to vote probabilities:

    P(j) = exp(λ · V_j) / Σ_k exp(λ · V_k)

Using the max-subtraction trick to prevent overflow:

    P(j) = exp(λ · V_j - max_k(λ · V_k)) / Σ_k exp(λ · V_k - max)
"""

from __future__ import annotations

import numpy as np


def softmax(utilities: np.ndarray, scale: float = 1.0) -> np.ndarray:
    """
    Numerically stable softmax (multinomial logit).

    Parameters
    ----------
    utilities : np.ndarray
        Shape (J,) for a single voter or (N, J) for a batch of voters.
        J = number of parties (or parties + abstention option).
    scale : float
        Rationality / scale parameter λ. Higher values sharpen the
        distribution (more deterministic); lower values flatten it.

    Returns
    -------
    np.ndarray
        Probabilities with same shape as *utilities*, summing to 1
        along the last axis.
    """
    scaled = scale * utilities
    # Subtract max per row (or scalar) for numerical stability
    shifted = scaled - np.max(scaled, axis=-1, keepdims=True)
    exp_vals = np.exp(shifted)
    return exp_vals / np.sum(exp_vals, axis=-1, keepdims=True)


# Alias: scaled_softmax is just softmax with an explicit scale arg
def scaled_softmax(utilities: np.ndarray, scale: float) -> np.ndarray:
    """Apply scale factor then softmax. Equivalent to softmax(utilities, scale)."""
    return softmax(utilities, scale=scale)


def log_softmax(utilities: np.ndarray, scale: float = 1.0) -> np.ndarray:
    """
    Numerically stable log-softmax.

    Returns log-probabilities (useful for log-likelihood calculations).
    """
    scaled = scale * utilities
    shifted = scaled - np.max(scaled, axis=-1, keepdims=True)
    log_sum_exp = np.log(np.sum(np.exp(shifted), axis=-1, keepdims=True))
    return shifted - log_sum_exp
