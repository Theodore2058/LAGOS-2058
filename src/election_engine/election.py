"""
Election orchestrator for the LAGOS-2058 engine.

Runs the full simulation pipeline:
  1. Load data
  2. Compute salience weights for all 774 LGAs
  3. Generate voter types
  4. For each LGA: compute type weights, ideal points, utilities, softmax, turnout
  5. Aggregate to LGA-level predicted shares
  6. For each Monte Carlo run: draw shocks, apply Dirichlet, determine winners
  7. Aggregate Monte Carlo results
  8. Return comprehensive results dict
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .campaign_state import CampaignModifiers
from .config import ElectionConfig
from .data_loader import load_lga_data, load_district_data
from .ethnic_affinity import EthnicAffinityMatrix
from .religious_affinity import ReligiousAffinityMatrix
from .salience import compute_all_lga_salience, SalienceRule
from .poststratification import compute_all_lga_results
from .noise import apply_noise_arrays, compute_lga_kappa_multipliers
from .results import (
    check_presidential_spread,
    aggregate_monte_carlo_from_arrays,
    allocate_district_seats,
    compute_summary_stats,
)

logger = logging.getLogger(__name__)


def run_election(
    data_path: str | Path,
    election_config: ElectionConfig,
    seed: Optional[int] = None,
    ethnic_matrix: Optional[EthnicAffinityMatrix] = None,
    religious_matrix: Optional[ReligiousAffinityMatrix] = None,
    salience_rules: Optional[list[SalienceRule]] = None,
    ideal_point_coeff_table: Optional[list[dict]] = None,
    verbose: bool = True,
    campaign_modifiers: Optional[CampaignModifiers] = None,
) -> dict:
    """
    Run a full election simulation.

    Parameters
    ----------
    data_path : str | Path
        Path to the Nigeria LGA polsim xlsx file.
    election_config : ElectionConfig
        Full election configuration (parties, params, MC count).
    seed : int, optional
        Random seed for reproducibility.
    ethnic_matrix, religious_matrix : optional overrides for affinity matrices.
    salience_rules : optional override for salience rules.
    ideal_point_coeff_table : optional override for ideal point coefficients.
    verbose : bool
        If True, log progress messages.

    Returns
    -------
    dict with keys:
        lga_results_base  : pd.DataFrame — deterministic base results (774 rows)
        mc_aggregated     : dict — seat stats, win probs, swing LGAs, ENP dist
        summary           : dict — national/zonal stats from base run
        spread_checks     : dict[party_name → spread_dict] — all parties
        metadata          : dict — timing, config info
        data              : LGAData — the loaded data object
    """
    t_start = time.time()
    rng = np.random.default_rng(seed)

    party_names = [p.name for p in election_config.parties]
    n_mc = election_config.n_monte_carlo

    # ---- Step 1: Load data ----
    if verbose:
        logger.info("Loading LGA data from %s", data_path)
    lga_data = load_lga_data(data_path)
    df = lga_data.df

    # Derive colonial region binary columns for ideal point coefficients
    if "Colonial Era Region" in df.columns:
        _cr = df["Colonial Era Region"].fillna("").astype(str).str.strip()
        _new_cols = pd.DataFrame({
            "Colonial Western": (_cr == "Western").astype(float),
            "Colonial Eastern": (_cr == "Eastern").astype(float),
            "Colonial Mid-Western": (_cr == "Mid-Western").astype(float),
        }, index=df.index)
        lga_data.df = pd.concat([df, _new_cols], axis=1)
        df = lga_data.df

    # Derive AZ binary columns for zone-specific ideal point coefficients
    if "Administrative Zone" in df.columns:
        _az = df["Administrative Zone"].fillna(0).astype(int)
        _az_cols = pd.DataFrame({
            f"AZ {i}": (_az == i).astype(float)
            for i in range(1, 9)
        }, index=df.index)
        lga_data.df = pd.concat([df, _az_cols], axis=1)
        df = lga_data.df

    if verbose:
        logger.info("Loaded %d LGAs", len(df))

    # ---- Step 1b: Load district data (optional) ----
    project_root = Path(data_path).resolve().parent.parent
    district_data = load_district_data(
        project_root / "voting_districts_summary.xlsx",
        project_root / "seat_allocation.xlsx",
        df["LGA Name"],
    )

    # ---- Step 2: Compute salience for all LGAs ----
    if verbose:
        logger.info("Computing salience weights for %d LGAs...", len(df))
    t_sal = time.time()
    salience_matrix = compute_all_lga_salience(
        df, rules=salience_rules,
        national_median_gdp=float(df["GDP Per Capita Est"].median()),
    )
    if verbose:
        logger.info("Salience computed in %.1fs", time.time() - t_sal)

    # ---- Step 3 + 4: LGA results (base, deterministic) ----
    if verbose:
        logger.info("Computing base LGA results (no noise)...")
    t_lga = time.time()

    lga_results_base = compute_all_lga_results(
        lga_data=df,
        election_config=election_config,
        ethnic_matrix=ethnic_matrix,
        religious_matrix=religious_matrix,
        salience_rules=salience_rules,
        ideal_point_coeff_table=ideal_point_coeff_table,
        precomputed_salience=salience_matrix,
        campaign_modifiers=campaign_modifiers,
    )

    if verbose:
        logger.info("Base LGA results computed in %.1fs", time.time() - t_lga)

    # ---- Step 5: Summary from base run ----
    summary = compute_summary_stats(
        lga_results_base, party_names,
        district_seats_df=district_data.district_seats if district_data else None,
        lga_mapping_df=district_data.lga_mapping if district_data else None,
    )

    # ---- Step 6: Monte Carlo runs (pre-allocated arrays) ----
    if verbose:
        logger.info("Running %d Monte Carlo iterations...", n_mc)
    t_mc = time.time()

    admin_zones = sorted(df["Administrative Zone"].unique().tolist())
    J = len(party_names)
    n_lgas = len(lga_results_base)

    # Extract base arrays once (avoid repeated DataFrame column lookups)
    share_cols = [f"{p}_share" for p in party_names]
    base_shares = lga_results_base[share_cols].values.astype(float)  # (n_lgas, J)
    base_turnout = lga_results_base["Turnout"].values.astype(float)  # (n_lgas,)
    zone_ids = lga_results_base["Administrative Zone"].values
    pop_col_name = "Estimated Population"
    pop = (lga_results_base[pop_col_name].values.astype(float)
           if pop_col_name in lga_results_base.columns
           else np.ones(n_lgas))

    # Compute per-LGA kappa multipliers for heteroscedastic noise
    kappa_mults = compute_lga_kappa_multipliers(df)

    # Pre-allocate 3D share array and 2D turnout array
    all_mc_shares = np.empty((n_mc, n_lgas, J))
    all_mc_turnout = np.empty((n_mc, n_lgas))

    for run_idx in range(n_mc):
        noisy_shares, noisy_turnout = apply_noise_arrays(
            base_shares=base_shares,
            base_turnout=base_turnout,
            zone_ids=zone_ids,
            admin_zones=admin_zones,
            params=election_config.params,
            rng=rng,
            kappa_multipliers=kappa_mults,
        )
        all_mc_shares[run_idx] = noisy_shares
        all_mc_turnout[run_idx] = noisy_turnout

        if verbose and (run_idx + 1) % 100 == 0:
            logger.info("  MC run %d / %d", run_idx + 1, n_mc)

    if verbose:
        logger.info("Monte Carlo completed in %.1fs", time.time() - t_mc)

    # ---- Step 7: Aggregate MC (from pre-allocated arrays) ----
    mc_aggregated = aggregate_monte_carlo_from_arrays(
        all_shares=all_mc_shares,
        all_turnout=all_mc_turnout,
        party_names=party_names,
        pop=pop,
        base_run_df=lga_results_base,
        lga_district_indices=district_data.lga_district_indices if district_data else None,
        district_seat_counts=district_data.district_seat_counts if district_data else None,
    )

    # ---- Step 8: Spread checks ----
    spread_checks = {}
    for party_name in party_names:
        spread_checks[party_name] = check_presidential_spread(
            lga_results_base, party_name, party_names
        )

    t_total = time.time() - t_start
    if verbose:
        logger.info("Full election run completed in %.1fs", t_total)

    # ---- District-level base results ----
    district_results = None
    total_seats = summary.get("total_seats", 774)
    if district_data is not None:
        district_results = allocate_district_seats(
            lga_results_base, party_names,
            district_data.district_seats, district_data.lga_mapping,
        )

    return {
        "lga_results_base": lga_results_base,
        "mc_aggregated": mc_aggregated,
        "summary": summary,
        "spread_checks": spread_checks,
        "district_results": district_results,
        "total_seats": total_seats,
        "metadata": {
            "n_lgas": len(df),
            "n_parties": len(election_config.parties),
            "n_monte_carlo": n_mc,
            "party_names": party_names,
            "seed": seed,
            "total_seconds": t_total,
        },
        "data": lga_data,
    }
