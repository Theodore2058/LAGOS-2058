"""
Unified spatial voting model (Merrill-Grofman proximity-directional blend).

The spatial utility of voter i for party j is:

    U_spatial(i, j) = β_s · [(x_i · z_j) - (q / 2) · ||z_j||²]

Derivation: mixing directional utility U_dir = x·z with proximity utility
U_prox = −½||x−z||² (dropping the voter-constant ||x||² term):

    U = (1−q)·x·z + q·(x·z − ½||z||²) = x·z − (q/2)·||z||²

Where:
  - x_i  = voter ideal point in issue space  (shape D)
  - z_j  = party j position in issue space   (shape D)
  - q    ∈ [0, 1]: mix parameter
      q = 0 → pure directional (no extremism penalty)
      q = 1 → pure proximity   (equivalent to −½||x−z||² up to voter-constant)
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

    # Unified model: x·z - (q/2)·||z||²
    utility = beta_s * (dot_product - (q / 2.0) * sq_norm)
    return utility


def batch_spatial_utility(
    voter_ideals: np.ndarray,
    party_positions: np.ndarray,
    beta_s: float,
    q: float,
    salience_weights: Optional[np.ndarray] = None,
    _intermediates: Optional[dict] = None,
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
    _intermediates : dict, optional
        If provided, populated with intermediate arrays for reuse
        (dot_products, sq_norms, w) to avoid redundant matmuls elsewhere.

    Returns
    -------
    np.ndarray, shape (N, J)
        Spatial utility for each (voter, party) pair.
    """
    voter_ideals = np.asarray(voter_ideals)                    # (N, D)
    party_positions = np.asarray(party_positions)               # (J, D)

    if salience_weights is None:
        w = np.ones(voter_ideals.shape[1], dtype=np.float32)
    else:
        w = np.asarray(salience_weights)                        # (D,)

    # Float32 BLAS: matmul is ~4x faster in float32. When input is already
    # float32 (preconverted by caller), astype is a no-op (copy=False).
    w_f32 = w.astype(np.float32, copy=False)
    vi_f32 = voter_ideals.astype(np.float32, copy=False)
    pp_f32 = party_positions.astype(np.float32, copy=False)

    # Weighted dot products: (N, D) · diag(w) · (D, J) → (N, J)
    wx = vi_f32 * w_f32                                         # (N, D) float32
    dot_products = wx @ pp_f32.T                                # (N, J) float32

    # Weighted squared norms: (J,) — compute in float32 if inputs are float32
    sq_norms = (pp_f32 ** 2) @ w_f32                           # (J,) float32

    # Broadcast: stay in float32 to avoid promoting the whole chain to float64
    utilities = np.float32(beta_s) * (dot_products - np.float32(q / 2.0) * sq_norms)

    if _intermediates is not None:
        _intermediates["dot_products"] = dot_products
        _intermediates["sq_norms"] = sq_norms
        _intermediates["wx"] = wx

    return utilities
