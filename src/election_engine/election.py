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

from .config import ElectionConfig, EngineParams
from .data_loader import load_lga_data, LGAData
from .ethnic_affinity import EthnicAffinityMatrix, DEFAULT_ETHNIC_MATRIX
from .religious_affinity import ReligiousAffinityMatrix, DEFAULT_RELIGIOUS_MATRIX
from .salience import compute_all_lga_salience, SalienceRule
from .voter_types import generate_all_voter_types
from .poststratification import compute_all_lga_results
from .noise import draw_shocks, apply_noise_to_results
from .results import (
    add_lga_winners, count_seats, check_presidential_spread,
    aggregate_monte_carlo, compute_summary_stats,
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
        mc_runs           : list[pd.DataFrame] — all MC runs
        mc_aggregated     : dict — seat stats, win probs, swing LGAs
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

    if verbose:
        logger.info("Loaded %d LGAs", len(df))

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
    )

    if verbose:
        logger.info("Base LGA results computed in %.1fs", time.time() - t_lga)

    # ---- Step 5: Summary from base run ----
    summary = compute_summary_stats(lga_results_base, party_names)

    # ---- Step 6: Monte Carlo runs ----
    if verbose:
        logger.info("Running %d Monte Carlo iterations...", n_mc)
    t_mc = time.time()

    admin_zones = sorted(df["Administrative Zone"].unique().tolist())
    mc_runs = []

    for run_idx in range(n_mc):
        noisy_run = apply_noise_to_results(
            lga_results_df=lga_results_base,
            party_names=party_names,
            params=election_config.params,
            rng=rng,
        )
        mc_runs.append(noisy_run)

        if verbose and (run_idx + 1) % 100 == 0:
            logger.info("  MC run %d / %d", run_idx + 1, n_mc)

    if verbose:
        logger.info("Monte Carlo completed in %.1fs", time.time() - t_mc)

    # ---- Step 7: Aggregate MC ----
    mc_aggregated = aggregate_monte_carlo(mc_runs, party_names)

    # ---- Step 8: Spread checks ----
    spread_checks = {}
    for party_name in party_names:
        spread_checks[party_name] = check_presidential_spread(
            lga_results_base, party_name, party_names
        )

    t_total = time.time() - t_start
    if verbose:
        logger.info("Full election run completed in %.1fs", t_total)

    return {
        "lga_results_base": lga_results_base,
        "mc_runs": mc_runs,
        "mc_aggregated": mc_aggregated,
        "summary": summary,
        "spread_checks": spread_checks,
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
