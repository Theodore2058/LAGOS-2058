#!/usr/bin/env python3
"""
Diagnostic CLI for LAGOS-2058 Economic Simulator.

Usage:
    python scripts/run_diagnostic.py                  # Run 3-month sim + report
    python scripts/run_diagnostic.py --months 6       # 6-month simulation
    python scripts/run_diagnostic.py --shock oil      # Oil crash scenario
    python scripts/run_diagnostic.py --shock food     # Food crisis scenario
    python scripts/run_diagnostic.py --shock power    # Electricity collapse
    python scripts/run_diagnostic.py --save state.npz # Save final state
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.assertions import check_all_invariants
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import BASE_PRICES, COMMODITIES
from src.economy.data.commodity_ids import (
    CRUDE_OIL, ELECTRICITY, FOOD_COMMODITIES, REFINED_PETROLEUM,
)
from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_gini_coefficient,
    compute_employment_stats,
    compute_trade_balance,
    compute_crisis_indicators,
    compute_regional_inequality,
)


def apply_shock(state, shock_name: str) -> str:
    """Apply a named shock scenario. Returns description."""
    if shock_name == "oil":
        state.global_oil_price_usd = 20.0
        return "Oil price crash: $85 -> $20/barrel"
    elif shock_name == "food":
        for c in FOOD_COMMODITIES:
            state.production_capacity[:, c] = 0.0
            state.inventories[:, c] *= 0.1
        return "Food crisis: production zeroed, inventories -90%"
    elif shock_name == "power":
        state.production_capacity[:, ELECTRICITY] = 0.0
        state.inventories[:, ELECTRICITY] = 0.0
        return "Electricity collapse: all power production zeroed"
    elif shock_name == "reserves":
        state.forex_reserves_usd = 1e8
        return "Forex reserves crisis: reserves at $100M"
    elif shock_name == "alsahid":
        state.alsahid_control[:] = np.minimum(state.alsahid_control + 0.3, 1.0)
        return "Al-Shahid surge: control +30% everywhere"
    else:
        return f"Unknown shock '{shock_name}', no changes applied"


def print_header(text: str):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_report(state, config):
    """Print comprehensive diagnostic report."""
    print_header("LAGOS-2058 Economy Diagnostic Report")

    # GDP
    gdp = compute_gdp_proxy(state, config)
    inflation = compute_inflation_proxy(state, config)
    gini = compute_gini_coefficient(state)
    print(f"\n  GDP proxy:    {gdp:>16,.0f} NGN")
    print(f"  Inflation:    {inflation:>16.1%}")
    print(f"  Gini coeff:   {gini:>16.3f}")

    # Employment
    emp = compute_employment_stats(state, config)
    print(f"\n  Employment rate:   {emp['employment_rate']:>10.1%}")
    print(f"  Informal rate:     {emp['informality_rate']:>10.1%}")
    unemp = 1.0 - emp['employment_rate']
    print(f"  Unemployment rate: {unemp:>10.1%}")

    # Forex
    trade = compute_trade_balance(state)
    print(f"\n  Forex reserves:     ${state.forex_reserves_usd:>14,.0f}")
    print(f"  Official rate:       {state.official_exchange_rate:>14,.0f} NGN/USD")
    print(f"  Parallel rate:       {state.parallel_exchange_rate:>14,.0f} NGN/USD")
    print(f"  Trade balance:      ${trade['balance']:>14,.0f}")
    print(f"  Oil price:          ${state.global_oil_price_usd:>14,.1f}/bbl")

    # Crisis indicators
    crisis = compute_crisis_indicators(state, config)
    active = [k.replace("_crisis", "").upper() for k, v in crisis.items() if v]
    print(f"\n  Crisis Indicators: {', '.join(active) if active else 'NONE ACTIVE'}")
    for k, v in crisis.items():
        flag = "!!!" if v else "   "
        print(f"    {flag} {k}: {v}")

    # Regional inequality
    reg = compute_regional_inequality(state, config)
    print(f"\n  Regional Inequality:")
    print(f"    Top 10 LGAs mean wage:    {reg['top10_mean_wage']:>12,.0f}")
    print(f"    Bottom 10 LGAs mean wage: {reg['bottom10_mean_wage']:>12,.0f}")
    print(f"    Top/bottom ratio:         {reg['ratio']:>12.1f}x")

    # Price extremes
    ratios = state.prices / BASE_PRICES[np.newaxis, :]
    print(f"\n  Price Extremes (vs base):")
    max_idx = np.unravel_index(ratios.argmax(), ratios.shape)
    min_idx = np.unravel_index(ratios.argmin(), ratios.shape)
    print(f"    Max: {ratios.max():>8.1f}x (LGA {max_idx[0]}, {COMMODITIES[max_idx[1]].name})")
    print(f"    Min: {ratios.min():>8.4f}x (LGA {min_idx[0]}, {COMMODITIES[min_idx[1]].name})")
    print(f"    Mean: {ratios.mean():>8.2f}x")

    # Invariant check
    warnings = check_all_invariants(state)
    if warnings:
        print(f"\n  Invariant Warnings ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"    - {w}")
        if len(warnings) > 10:
            print(f"    ... and {len(warnings) - 10} more")
    else:
        print(f"\n  Invariants: ALL CLEAR")


def main():
    parser = argparse.ArgumentParser(description="LAGOS-2058 Economy Diagnostic")
    parser.add_argument("--months", type=int, default=3, help="Months to simulate")
    parser.add_argument("--shock", type=str, default=None,
                        help="Shock scenario: oil, food, power, reserves, alsahid")
    parser.add_argument("--save", type=str, default=None, help="Save final state to .npz")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    config = SimConfig(SEED=args.seed)
    print(f"Initializing 774-LGA economy (seed={args.seed})...")
    t0 = time.time()
    state = initialize_state(config)
    print(f"  Init: {time.time() - t0:.1f}s")

    if args.shock:
        desc = apply_shock(state, args.shock)
        print(f"  Shock applied: {desc}")

    print(f"Running {args.months}-month simulation...")
    t0 = time.time()
    scheduler = TickScheduler(state=state, config=config)
    results = scheduler.run_mixed_ticks(n_months=args.months)
    elapsed = time.time() - t0
    print(f"  Sim: {elapsed:.1f}s ({len(results)} ticks, {elapsed/len(results)*1000:.0f}ms/tick)")

    print_report(state, config)

    if args.save:
        from src.economy.core.serialization import save_state
        save_state(state, args.save)
        print(f"\n  State saved to: {args.save}")


if __name__ == "__main__":
    main()
