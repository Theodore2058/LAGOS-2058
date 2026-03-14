#!/usr/bin/env python3
"""
Generate golden run regression snapshots.

Runs a deterministic 6-month simulation and saves key metrics
to tests/economy/golden/golden_6month.npz for regression testing.

Usage:
    python scripts/generate_golden.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import BASE_PRICES
from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_gini_coefficient,
    compute_employment_stats,
)


def main():
    config = SimConfig(SEED=42)
    print("Generating golden run (6 months, seed=42)...")

    state = initialize_state(config)
    scheduler = TickScheduler(state=state, config=config)
    results = scheduler.run_mixed_ticks(n_months=6)
    print(f"  Completed {len(results)} ticks")

    # Compute metrics
    emp = compute_employment_stats(state, config)
    ratios = state.prices / BASE_PRICES[np.newaxis, :]

    golden = {
        "gdp_proxy": np.float64(compute_gdp_proxy(state, config)),
        "inflation": np.float64(compute_inflation_proxy(state, config)),
        "gini": np.float64(compute_gini_coefficient(state)),
        "employment_rate": np.float64(emp["employment_rate"]),
        "price_ratio_max": np.float64(ratios.max()),
        "price_ratio_mean": np.float64(ratios.mean()),
        "forex_reserves": np.float64(state.forex_reserves_usd),
        "population_total": np.float64(state.population.sum()),
        "alsahid_mean": np.float64(state.alsahid_control.mean()),
        "prices_snapshot": state.prices.copy(),
        "n_ticks": np.int32(len(results)),
    }

    out_path = Path(__file__).resolve().parent.parent / "tests" / "economy" / "golden" / "golden_6month.npz"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(str(out_path), **golden)
    print(f"  Saved to: {out_path}")

    # Print summary
    for k, v in golden.items():
        if isinstance(v, np.ndarray) and v.ndim > 0:
            print(f"  {k}: shape={v.shape}")
        else:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
