"""
Unified spatial voting model (Merrill-Grofman proximity-directional blend).

The spatial utility of voter i for party j is:

    U_spatial(i, j) = β_s · [(1 - q) · (x_i · z_j) - (q / 2) · ||z_j||²]

Where:
  - x_i  = voter ideal point in issue space  (shape D)
  - z_j  = party j position in issue space   (shape D)
  - q    ∈ [0, 1]: mix parameter
      q = 0 → pure directional (extremist parties rewarded for distance from origin)
      q = 1 → pure proximity   (parties penalised for distance from voter)
  - β_s  = spatial sensitivity scalar

With salience weights w_d the dot products become:
    x_i · z_j  →  Σ_d w_d · x_{id} · z_{jd}
    ||z_j||²   →  Σ_d w_d · z_{jd}²

This maintains dimensional consistency: higher salience on an issue amplifies
both the directional pull and the proximity penalty for that dimension.
"""

from __future__ import annotations

import numpy as np
from typing import Optional


def spatial_utility(
    voter_ideal: np.ndarray,
    party_positions: np.ndarray,
    beta_s: float,
    q: float,
    salience_weights: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Compute spatial utility of one voter for all parties.

    Parameters
    ----------
    voter_ideal : np.ndarray, shape (D,)
        Voter's ideal point on each of the D issue dimensions.
    party_positions : np.ndarray, shape (J, D)
        All J parties' positions on each issue dimension.
    beta_s : float
        Spatial sensitivity parameter.
    q : float
        Proximity-directional mix in [0, 1].
    salience_weights : np.ndarray, shape (D,), optional
        Per-issue salience weights for this LGA.
        If None, uniform weights of 1.0 are used.

    Returns
    -------
    np.ndarray, shape (J,)
        Spatial utility for each party.
    """
    voter_ideal = np.asarray(voter_ideal, dtype=float)      # (D,)
    party_positions = np.asarray(party_positions, dtype=float)  # (J, D)

    if salience_weights is None:
        w = np.ones(voter_ideal.shape[0], dtype=float)
    else:
        w = np.asarray(salience_weights, dtype=float)        # (D,)

    # Weighted dot product: Σ_d w_d · x_d · z_{jd}   → shape (J,)
    dot_product = party_positions @ (w * voter_ideal)

    # Weighted squared norm: Σ_d w_d · z_{jd}²        → shape (J,)
    sq_norm = party_positions ** 2 @ w

    # Unified model
    utility = beta_s * ((1.0 - q) * dot_product - (q / 2.0) * sq_norm)
    return utility


def batch_spatial_utility(
    voter_ideals: np.ndarray,
    party_positions: np.ndarray,
    beta_s: float,
    q: float,
    salience_weights: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Compute spatial utilities for a batch of voter ideal points.

    Parameters
    ----------
    voter_ideals : np.ndarray, shape (N, D)
        N voter ideal points, each of dimension D.
    party_positions : np.ndarray, shape (J, D)
        J party positions, each of dimension D.
    beta_s : float
        Spatial sensitivity.
    q : float
        Proximity-directional mix.
    salience_weights : np.ndarray, shape (D,), optional
        Per-issue salience weights (same for all voters in this call).

    Returns
    -------
    np.ndarray, shape (N, J)
        Spatial utility for each (voter, party) pair.
    """
    voter_ideals = np.asarray(voter_ideals, dtype=float)      # (N, D)
    party_positions = np.asarray(party_positions, dtype=float)  # (J, D)

    if salience_weights is None:
        w = np.ones(voter_ideals.shape[1], dtype=float)
    else:
        w = np.asarray(salience_weights, dtype=float)          # (D,)

    # Weighted dot products: (N, D) · diag(w) · (D, J) → (N, J)
    wx = voter_ideals * w                                       # (N, D)
    dot_products = wx @ party_positions.T                       # (N, J)

    # Weighted squared norms: (J,)
    sq_norms = (party_positions ** 2) @ w                      # (J,)

    # Broadcast: (N, J) and (J,)
    utilities = beta_s * ((1.0 - q) * dot_products - (q / 2.0) * sq_norms)
    return utilities
