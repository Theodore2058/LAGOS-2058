"""
Hierarchical noise model for the LAGOS-2058 election engine.

Vote share noise — three-tier stochastic model:
  1. National shock  — one draw per party from N(0, σ_nat²), centered to zero-sum
  2. Regional shock  — one draw per party per Administrative Zone from N(0, σ_reg²), centered
  3. LGA shock       — Dirichlet noise using concentration parameter κ

National and regional shocks are centered (sum to 0 across parties) so that
one party's gain comes at others' expense on the log-simplex, preventing
correlated mass inflation/deflation of all shares simultaneously.

Shocks are applied on the log-scale (simplex proxy), then converted back via softmax:
    log_j = log(share_j)          (not true logit — omits the (1-share_j) denominator,
                                   but this is standard practice on the simplex because
                                   softmax renormalises, making the proxy exact)
    shocked_log_j = log_j + national_shock_j + regional_shock_j
    shocked_share_j = softmax(shocked_log_j)

Then Dirichlet noise:
    alpha_j = κ · shocked_share_j
    final_share ~ Dirichlet(alpha)

Turnout noise — three-tier logit-scale model:
  1. National turnout shock   — one draw from N(0, σ_turnout²), shared by all LGAs
  2. Regional turnout shock   — one draw per Admin Zone from N(0, σ_turnout_regional²)
  3. LGA turnout shock        — per-LGA draw from N(0, σ_turnout²)

Applied on the logit scale then back-transformed via sigmoid.
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
    # Zero-sum: one party's gain is another's loss (on log scale)
    national_shocks -= national_shocks.mean()

    regional_shocks: dict[int, np.ndarray] = {}
    for zone in admin_zones:
        z = rng.normal(0.0, params.sigma_regional, size=n_parties)
        z -= z.mean()
        regional_shocks[zone] = z

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
    N_lga = len(result)

    # Map zone IDs to contiguous integer codes for vectorised indexing
    zone_to_code = {z: i for i, z in enumerate(admin_zones)}
    zone_codes = np.array([zone_to_code[z] for z in zone_values], dtype=np.intp)
    n_zones = len(admin_zones)

    # Build regional shock array via fancy indexing: (n_zones, J) → (N_lga, J)
    zone_shock_matrix = np.array([regional_shocks.get(z, np.zeros(J)) for z in admin_zones])
    reg_shock_array = zone_shock_matrix[zone_codes]  # (N_lga, J)

    # ---- Vectorised: log → shock → softmax → alpha (all N_lga rows at once) ----
    safe_shares = np.maximum(share_values, _LOG_EPSILON)           # (N_lga, J)
    log_shares = np.log(safe_shares)
    shocked_log = log_shares + national_shocks + reg_shock_array   # broadcasting (J,) + (N_lga, J)
    shifted = shocked_log - shocked_log.max(axis=1, keepdims=True) # (N_lga, J)
    exp_vals = np.exp(shifted)
    shocked_shares = exp_vals / exp_vals.sum(axis=1, keepdims=True)
    alphas = np.maximum(params.kappa * shocked_shares, 1e-6)       # (N_lga, J)

    # ---- Batch Dirichlet draws via gamma: Dirichlet(alpha) = normalise(Gamma(alpha_j, 1)) ----
    gamma_draws = rng.standard_gamma(alphas)  # (N_lga, J)
    row_sums = gamma_draws.sum(axis=1, keepdims=True)
    row_sums = np.maximum(row_sums, 1e-30)
    noisy_shares = gamma_draws / row_sums

    # Bulk assignment back to dataframe
    result[share_cols] = noisy_shares

    # ---- Turnout noise (logit-scale, 3-tier: national + regional + LGA) ----
    turnout_col = "Turnout"
    has_turnout_noise = (params.sigma_turnout > 0 or params.sigma_turnout_regional > 0)
    if has_turnout_noise and turnout_col in result.columns:
        base_turnout = result[turnout_col].values.astype(float)
        safe_t = np.clip(base_turnout, 0.01, 0.99)
        logit_t = np.log(safe_t / (1.0 - safe_t))
        # National turnout shock
        national_t_shock = rng.normal(0.0, params.sigma_turnout) if params.sigma_turnout > 0 else 0.0
        # Regional turnout shocks: draw per zone, broadcast via zone_codes
        if params.sigma_turnout_regional > 0:
            zone_t_shocks = rng.normal(0.0, params.sigma_turnout_regional, size=n_zones)
            reg_t_shocks = zone_t_shocks[zone_codes]  # (N_lga,)
        else:
            reg_t_shocks = np.zeros(N_lga)
        # Per-LGA turnout shock
        lga_t_shocks = rng.normal(0.0, params.sigma_turnout, size=N_lga) if params.sigma_turnout > 0 else np.zeros(N_lga)
        noisy_logit = logit_t + national_t_shock + reg_t_shocks + lga_t_shocks
        noisy_turnout = 1.0 / (1.0 + np.exp(-noisy_logit))
        result[turnout_col] = noisy_turnout

    return result


def apply_noise_arrays(
    base_shares: np.ndarray,
    base_turnout: np.ndarray,
    zone_ids: np.ndarray,
    admin_zones: list[int],
    params: EngineParams,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Fast numpy-only noise application (no DataFrame overhead).

    Parameters
    ----------
    base_shares : np.ndarray, shape (N_lga, J)
        Deterministic vote shares.
    base_turnout : np.ndarray, shape (N_lga,)
        Deterministic turnout rates.
    zone_ids : np.ndarray, shape (N_lga,)
        Administrative zone ID per LGA.
    admin_zones : list[int]
        Sorted unique zone IDs.
    params : EngineParams
    rng : np.random.Generator

    Returns
    -------
    (noisy_shares, noisy_turnout)
        noisy_shares : np.ndarray, shape (N_lga, J)
        noisy_turnout : np.ndarray, shape (N_lga,)
    """
    N_lga, J = base_shares.shape

    # --- Map zone IDs to contiguous integer codes for vectorised indexing ---
    n_zones = len(admin_zones)
    zone_to_code = {z: i for i, z in enumerate(admin_zones)}
    zone_codes = np.array([zone_to_code[z] for z in zone_ids], dtype=np.intp)

    # Draw shocks (zero-sum: one party's gain is another's loss on log scale)
    national_shocks = rng.normal(0.0, params.sigma_national, size=J)
    national_shocks -= national_shocks.mean()

    # Regional shocks: draw (n_zones, J), zero-sum per zone, then broadcast
    zone_shocks = rng.normal(0.0, params.sigma_regional, size=(n_zones, J))
    zone_shocks -= zone_shocks.mean(axis=1, keepdims=True)
    reg_shock_array = zone_shocks[zone_codes]  # (N_lga, J) via fancy indexing

    # Vectorised: log → shock → softmax → alpha
    safe_shares = np.maximum(base_shares, _LOG_EPSILON)
    log_shares = np.log(safe_shares)
    shocked_log = log_shares + national_shocks + reg_shock_array
    shifted = shocked_log - shocked_log.max(axis=1, keepdims=True)
    exp_vals = np.exp(shifted)
    shocked_shares = exp_vals / exp_vals.sum(axis=1, keepdims=True)
    alphas = np.maximum(params.kappa * shocked_shares, 1e-6)

    # Batch Dirichlet draws via gamma: Dirichlet(alpha) = normalise(Gamma(alpha_j, 1))
    gamma_draws = rng.standard_gamma(alphas)  # (N_lga, J)
    row_sums = gamma_draws.sum(axis=1, keepdims=True)
    row_sums = np.maximum(row_sums, 1e-30)  # prevent division by zero
    noisy_shares = gamma_draws / row_sums

    # Turnout noise (3-tier: national + regional + LGA)
    has_turnout_noise = (params.sigma_turnout > 0 or params.sigma_turnout_regional > 0)
    if has_turnout_noise:
        safe_t = np.clip(base_turnout, 0.01, 0.99)
        logit_t = np.log(safe_t / (1.0 - safe_t))
        # National turnout shock
        national_t_shock = rng.normal(0.0, params.sigma_turnout) if params.sigma_turnout > 0 else 0.0
        # Regional turnout shocks: draw per zone, broadcast via zone_codes
        if params.sigma_turnout_regional > 0:
            zone_t_shocks = rng.normal(0.0, params.sigma_turnout_regional, size=n_zones)
            reg_t_shocks = zone_t_shocks[zone_codes]  # (N_lga,)
        else:
            reg_t_shocks = np.zeros(N_lga)
        # Per-LGA turnout shocks
        lga_t_shocks = rng.normal(0.0, params.sigma_turnout, size=N_lga) if params.sigma_turnout > 0 else np.zeros(N_lga)
        noisy_logit = logit_t + national_t_shock + reg_t_shocks + lga_t_shocks
        noisy_turnout = 1.0 / (1.0 + np.exp(-noisy_logit))
    else:
        noisy_turnout = base_turnout.copy()

    return noisy_shares, noisy_turnout
