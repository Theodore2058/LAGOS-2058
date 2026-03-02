"""
Hierarchical noise model for the LAGOS-2058 election engine.

Three-tier stochastic model:
  1. National shock  — one draw per party from N(0, σ_nat²)
  2. Regional shock  — one draw per party per Administrative Zone from N(0, σ_reg²)
  3. LGA shock       — Dirichlet noise using concentration parameter κ

Shocks are applied on the log-scale (simplex proxy), then converted back via softmax:
    log_j = log(share_j)          (not true logit — omits the (1-share_j) denominator,
                                   but this is standard practice on the simplex because
                                   softmax renormalises, making the proxy exact)
    shocked_log_j = log_j + national_shock_j + regional_shock_j
    shocked_share_j = softmax(shocked_log_j)

Then Dirichlet noise:
    alpha_j = κ · shocked_share_j
    final_share ~ Dirichlet(alpha)
"""

from __future__ import annotations

import numpy as np

from .config import EngineParams

_LOG_EPSILON = 1e-9  # Prevents log(0) when computing logit-scale shocks


def draw_shocks(
    n_parties: int,
    admin_zones: list[int],
    params: EngineParams,
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict[int, np.ndarray]]:
    """
    Draw national and regional shocks for one Monte Carlo simulation run.

    Parameters
    ----------
    n_parties : int
        Number of parties (J).
    admin_zones : list[int]
        All unique Administrative Zone IDs present in the LGA data.
    params : EngineParams
        Simulation parameters (sigma_national, sigma_regional).
    rng : np.random.Generator
        Random number generator.

    Returns
    -------
    (national_shocks, regional_shocks)
        national_shocks : np.ndarray, shape (J,)
        regional_shocks : dict[int, np.ndarray]
            Maps zone_id → shock vector of shape (J,).
    """
    national_shocks = rng.normal(0.0, params.sigma_national, size=n_parties)

    regional_shocks: dict[int, np.ndarray] = {}
    for zone in admin_zones:
        regional_shocks[zone] = rng.normal(0.0, params.sigma_regional, size=n_parties)

    return national_shocks, regional_shocks


def apply_dirichlet_noise(
    predicted_shares: np.ndarray,
    kappa: float,
    national_shocks: np.ndarray,
    regional_shocks: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Apply hierarchical noise to predicted vote shares for one LGA.

    Steps:
    1. Convert predicted shares to log scale (soft logit proxy)
    2. Add national and regional shocks
    3. Convert back via softmax → shocked shares
    4. Use shocked shares as Dirichlet concentrations
    5. Draw from Dirichlet → final noisy vote shares

    Parameters
    ----------
    predicted_shares : np.ndarray, shape (J,)
        Base predicted vote shares (sum to 1, all ≥ 0).
    kappa : float
        Dirichlet concentration parameter. Higher = less noise.
    national_shocks : np.ndarray, shape (J,)
        National-level additive shocks (pre-drawn for this MC run).
    regional_shocks : np.ndarray, shape (J,)
        Regional shocks for this LGA's Administrative Zone.
    rng : np.random.Generator
        Random number generator for the Dirichlet draw.

    Returns
    -------
    np.ndarray, shape (J,)
        Noisy vote shares summing to 1.
    """
    # Step 1: log-scale representation (proxy for logit on simplex)
    safe_shares = np.maximum(predicted_shares, _LOG_EPSILON)
    log_shares = np.log(safe_shares)

    # Step 2: add shocks
    shocked_log = log_shares + national_shocks + regional_shocks

    # Step 3: softmax back to simplex
    shifted = shocked_log - np.max(shocked_log)
    exp_vals = np.exp(shifted)
    shocked_shares = exp_vals / exp_vals.sum()

    # Step 4: Dirichlet concentration parameters
    alpha = kappa * shocked_shares
    # Ensure all alphas > 0 (numerical safety)
    alpha = np.maximum(alpha, 1e-6)

    # Step 5: draw from Dirichlet
    final_shares = rng.dirichlet(alpha)
    return final_shares


def apply_noise_to_results(
    lga_results_df,             # pd.DataFrame with {party}_share columns
    party_names: list[str],
    params: EngineParams,
    admin_zone_col: str = "Administrative Zone",
    rng: np.random.Generator | None = None,
    seed: int | None = None,
) -> object:  # returns pd.DataFrame
    """
    Apply one round of hierarchical noise to the full LGA results dataframe.

    Parameters
    ----------
    lga_results_df : pd.DataFrame
        Output from compute_all_lga_results with {party}_share columns.
    party_names : list[str]
        Names of parties (to identify share columns).
    params : EngineParams
        Simulation parameters.
    admin_zone_col : str
        Column name for Administrative Zone.
    rng : np.random.Generator, optional
        If provided, use this RNG; otherwise create from seed.
    seed : int, optional
        Seed for reproducibility (used if rng is None).

    Returns
    -------
    pd.DataFrame
        Copy of lga_results_df with share columns replaced by noisy values.
        Party share columns still sum to 1 per row.
    """
    import pandas as pd

    if rng is None:
        rng = np.random.default_rng(seed)

    J = len(party_names)
    admin_zones = sorted(lga_results_df[admin_zone_col].unique().tolist())

    # Draw shocks for this run
    national_shocks, regional_shocks = draw_shocks(J, admin_zones, params, rng)

    result = lga_results_df.copy()
    share_cols = [f"{p}_share" for p in party_names]

    # Extract share values and zones as numpy arrays for bulk processing
    share_values = result[share_cols].values.astype(float)  # (N_lga, J)
    zone_values = result[admin_zone_col].values

    # Build regional shock array aligned with rows
    reg_shock_array = np.zeros((len(result), J))
    for zone in admin_zones:
        mask = zone_values == zone
        reg_shock_array[mask] = regional_shocks.get(zone, np.zeros(J))

    # Apply noise per row (Dirichlet draw is inherently sequential per-LGA,
    # but we avoid pandas overhead by collecting results into a numpy array)
    noisy_shares = np.empty_like(share_values)
    for idx in range(len(result)):
        noisy_shares[idx] = apply_dirichlet_noise(
            predicted_shares=share_values[idx],
            kappa=params.kappa,
            national_shocks=national_shocks,
            regional_shocks=reg_shock_array[idx],
            rng=rng,
        )

    # Bulk assignment back to dataframe
    result[share_cols] = noisy_shares

    return result
