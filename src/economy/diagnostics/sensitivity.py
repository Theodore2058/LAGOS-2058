"""
Sensitivity analysis tooling for the economic simulator.

Provides parameter_sweep() to systematically test how different
SimConfig parameter values affect key outcome metrics.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import replace
from typing import Any, Callable

import numpy as np

from src.economy.core.types import SimConfig, EconomicState
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import BASE_PRICES
from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_gini_coefficient,
    compute_employment_stats,
)

logger = logging.getLogger(__name__)


def default_outcome_metrics(state: EconomicState, config: SimConfig) -> dict[str, float]:
    """Standard outcome metrics for sensitivity analysis."""
    ratios = state.prices / BASE_PRICES[np.newaxis, :]
    emp = compute_employment_stats(state, config)
    return {
        "gdp_proxy": compute_gdp_proxy(state, config),
        "inflation": compute_inflation_proxy(state, config),
        "gini": compute_gini_coefficient(state),
        "employment_rate": emp["employment_rate"],
        "price_ratio_max": float(ratios.max()),
        "price_ratio_mean": float(ratios.mean()),
        "forex_reserves": float(state.forex_reserves_usd),
        "alsahid_mean_control": float(state.alsahid_control.mean()),
    }


def parameter_sweep(
    param_name: str,
    values: list[Any],
    n_months: int = 3,
    base_config: SimConfig | None = None,
    metric_fn: Callable[[EconomicState, SimConfig], dict[str, float]] | None = None,
    state_mutator: Callable[[EconomicState], None] | None = None,
) -> list[dict[str, Any]]:
    """
    Run simulations across different values of a SimConfig parameter.

    Parameters
    ----------
    param_name : str
        Name of a SimConfig field to vary (e.g., "PRICE_ADJUSTMENT_SPEED").
    values : list
        Parameter values to test.
    n_months : int
        Months to simulate per run.
    base_config : SimConfig, optional
        Base config to modify. Defaults to SimConfig().
    metric_fn : callable, optional
        Function(state, config) -> dict of metric values.
        Defaults to default_outcome_metrics.
    state_mutator : callable, optional
        Function to mutate state before simulation (for shock scenarios).

    Returns
    -------
    list of dicts, one per value, with keys:
        param_value, plus all metric keys from metric_fn.
    """
    if base_config is None:
        base_config = SimConfig()
    if metric_fn is None:
        metric_fn = default_outcome_metrics

    results = []

    for val in values:
        config = replace(base_config, **{param_name: val})
        state = initialize_state(config)

        if state_mutator is not None:
            state_mutator(state)

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=n_months)

        metrics = metric_fn(state, config)
        metrics["param_value"] = val
        results.append(metrics)

        logger.info(
            "Sweep %s=%s: GDP=%.0f, inflation=%.2f, employment=%.2f",
            param_name, val,
            metrics.get("gdp_proxy", 0),
            metrics.get("inflation", 0),
            metrics.get("employment_rate", 0),
        )

    return results


def state_sweep(
    mutator_name: str,
    mutators: list[tuple[str, Callable[[EconomicState], None]]],
    n_months: int = 3,
    config: SimConfig | None = None,
    metric_fn: Callable[[EconomicState, SimConfig], dict[str, float]] | None = None,
) -> list[dict[str, Any]]:
    """
    Run simulations with different state mutations (shock scenarios).

    Parameters
    ----------
    mutator_name : str
        Label for the sweep dimension.
    mutators : list of (label, mutator_fn)
        Each mutator_fn(state) modifies the state before simulation.
    n_months : int
        Months to simulate per run.
    config : SimConfig, optional
    metric_fn : callable, optional

    Returns
    -------
    list of dicts with param_label and metric values.
    """
    if config is None:
        config = SimConfig()
    if metric_fn is None:
        metric_fn = default_outcome_metrics

    results = []

    for label, mutator in mutators:
        state = initialize_state(config)
        mutator(state)

        scheduler = TickScheduler(state=state, config=config)
        scheduler.run_mixed_ticks(n_months=n_months)

        metrics = metric_fn(state, config)
        metrics["param_label"] = label
        results.append(metrics)

        logger.info("State sweep '%s': %s", label, {k: f"{v:.2f}" for k, v in metrics.items() if isinstance(v, float)})

    return results


def format_sweep_results(results: list[dict[str, Any]], key_col: str = "param_value") -> str:
    """Format sweep results as a printable table."""
    if not results:
        return "No results."

    # Get all metric keys (exclude param cols)
    param_keys = {"param_value", "param_label"}
    metric_keys = [k for k in results[0] if k not in param_keys]

    # Header
    lines = []
    header = f"{'Value':>12}"
    for mk in metric_keys:
        header += f"  {mk:>16}"
    lines.append(header)
    lines.append("-" * len(header))

    # Rows
    for r in results:
        val = r.get(key_col, r.get("param_label", "?"))
        row = f"{str(val):>12}"
        for mk in metric_keys:
            v = r.get(mk, 0)
            if isinstance(v, float):
                if abs(v) > 1e6:
                    row += f"  {v:>16.0f}"
                else:
                    row += f"  {v:>16.4f}"
            else:
                row += f"  {str(v):>16}"
        lines.append(row)

    return "\n".join(lines)
