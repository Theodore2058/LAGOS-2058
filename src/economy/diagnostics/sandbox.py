"""
What-If Sandbox — run counterfactual simulations without affecting real state.

Deep-copies the economic state, applies a disruption (shock scenario),
runs the simulation for N months, and returns a trajectory of key metrics.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from src.economy.core.types import EconomicState, SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_employment_stats,
)
from src.economy.data.commodities import BASE_PRICES

logger = logging.getLogger(__name__)


@dataclass
class SandboxSnapshot:
    """A single point-in-time snapshot of key metrics."""
    month: int
    gdp_proxy: float
    inflation: float
    employment_rate: float
    forex_reserves_usd: float
    mean_price_ratio: float
    alsahid_mean_control: float
    enhancement_mean: float
    custom: Dict[str, float] = field(default_factory=dict)


@dataclass
class SandboxResult:
    """Full trajectory from a what-if simulation."""
    scenario_name: str
    n_months: int
    snapshots: List[SandboxSnapshot]
    final_state: EconomicState


def run_what_if(
    state: EconomicState,
    config: SimConfig,
    scenario_name: str,
    disruption: Callable[[EconomicState], None],
    n_months: int = 6,
    custom_metrics: Optional[Dict[str, Callable[[EconomicState, SimConfig], float]]] = None,
) -> SandboxResult:
    """
    Run a counterfactual simulation.

    Parameters
    ----------
    state : EconomicState
        Current state to branch from (deep-copied, never modified).
    config : SimConfig
        Simulation configuration.
    scenario_name : str
        Human-readable label for this scenario.
    disruption : callable
        Function(state) that modifies the copied state before simulation.
    n_months : int
        Number of months to simulate.
    custom_metrics : dict, optional
        Extra metric name -> callable(state, config) -> float.

    Returns
    -------
    SandboxResult with monthly snapshots and final state.
    """
    # Deep-copy state to avoid mutation
    sandbox_state = _deep_copy_state(state)

    # Apply disruption
    disruption(sandbox_state)

    # Initial snapshot
    snapshots = [_take_snapshot(sandbox_state, config, 0, custom_metrics)]

    # Run month-by-month
    scheduler = TickScheduler(state=sandbox_state, config=config)

    for month in range(1, n_months + 1):
        scheduler.run_mixed_ticks(n_months=1)
        snapshots.append(_take_snapshot(sandbox_state, config, month, custom_metrics))

        logger.info(
            "Sandbox '%s' month %d: GDP=%.0f, inflation=%.2f",
            scenario_name, month,
            snapshots[-1].gdp_proxy, snapshots[-1].inflation,
        )

    return SandboxResult(
        scenario_name=scenario_name,
        n_months=n_months,
        snapshots=snapshots,
        final_state=sandbox_state,
    )


def compare_scenarios(
    state: EconomicState,
    config: SimConfig,
    scenarios: List[tuple[str, Callable[[EconomicState], None]]],
    n_months: int = 6,
    custom_metrics: Optional[Dict[str, Callable[[EconomicState, SimConfig], float]]] = None,
) -> List[SandboxResult]:
    """
    Run multiple what-if scenarios and return all trajectories for comparison.

    Parameters
    ----------
    state : EconomicState
        Base state to branch from.
    config : SimConfig
    scenarios : list of (name, disruption_fn) tuples
    n_months : int
    custom_metrics : dict, optional

    Returns
    -------
    List of SandboxResult, one per scenario.
    """
    results = []
    for name, disruption in scenarios:
        result = run_what_if(state, config, name, disruption, n_months, custom_metrics)
        results.append(result)
    return results


def format_comparison(results: List[SandboxResult]) -> str:
    """Format comparison of multiple scenario trajectories as a table."""
    if not results:
        return "No results."

    lines = []
    header = f"{'Month':>6}"
    for r in results:
        header += f"  {'GDP(' + r.scenario_name[:10] + ')':>20}"
        header += f"  {'Infl(' + r.scenario_name[:10] + ')':>12}"
    lines.append(header)
    lines.append("-" * len(header))

    n_months = max(r.n_months for r in results)
    for m in range(n_months + 1):
        row = f"{m:>6}"
        for r in results:
            if m < len(r.snapshots):
                s = r.snapshots[m]
                row += f"  {s.gdp_proxy:>20.0f}"
                row += f"  {s.inflation:>12.4f}"
            else:
                row += f"  {'N/A':>20}"
                row += f"  {'N/A':>12}"
        lines.append(row)

    return "\n".join(lines)


def _deep_copy_state(state: EconomicState) -> EconomicState:
    """Deep-copy an EconomicState, properly handling numpy arrays."""
    new_state = copy.copy(state)  # shallow copy

    # Deep-copy all numpy arrays
    for attr_name in vars(new_state):
        val = getattr(new_state, attr_name)
        if isinstance(val, np.ndarray):
            setattr(new_state, attr_name, val.copy())
        elif isinstance(val, dict):
            setattr(new_state, attr_name, val.copy())
        elif isinstance(val, list):
            setattr(new_state, attr_name, list(val))

    # Fresh RNG to avoid correlation with parent
    new_state.rng = np.random.default_rng(state.rng.integers(2**32))

    return new_state


def _take_snapshot(
    state: EconomicState,
    config: SimConfig,
    month: int,
    custom_metrics: Optional[Dict[str, Callable[[EconomicState, SimConfig], float]]] = None,
) -> SandboxSnapshot:
    """Capture key metrics at a point in time."""
    ratios = state.prices / BASE_PRICES[np.newaxis, :]

    emp = compute_employment_stats(state, config)

    custom = {}
    if custom_metrics:
        for name, fn in custom_metrics.items():
            try:
                custom[name] = fn(state, config)
            except Exception:
                custom[name] = float("nan")

    return SandboxSnapshot(
        month=month,
        gdp_proxy=compute_gdp_proxy(state, config),
        inflation=compute_inflation_proxy(state, config),
        employment_rate=emp["employment_rate"],
        forex_reserves_usd=float(state.forex_reserves_usd),
        mean_price_ratio=float(ratios.mean()),
        alsahid_mean_control=float(state.alsahid_control.mean()) if state.alsahid_control is not None else 0.0,
        enhancement_mean=float(state.enhancement_adoption.mean()) if state.enhancement_adoption is not None else 0.0,
        custom=custom,
    )
