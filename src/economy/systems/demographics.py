"""
Demographics and migration system — fertility, mortality, gravity-model migration.

Called once per structural tick (monthly).
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import DemographicMutations, EconomicState, SimConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ANNUAL_DEATH_RATE = 0.005  # ~0.5% annual mortality
_MONTHLY_DEATH_RATE = _ANNUAL_DEATH_RATE / 12.0
_TOP_K_DESTINATIONS = 20  # per-LGA migration targets (keeps it sparse)
_LABOR_SKILL_DISTRIBUTION = np.array(
    [0.55, 0.25, 0.15, 0.05], dtype=np.float64,
)  # how new-born / migrant labor splits across skill tiers


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def tick_demographics(
    state: EconomicState, config: SimConfig,
) -> DemographicMutations:
    """
    Full demographics tick (monthly).

    1. Natural population growth (births - deaths), north/south fertility split.
    2. Gravity-model migration between LGAs.
    3. Update labor pool to reflect population changes + migration.
    """
    N = config.N_LGAS
    S = config.N_SKILL_TIERS

    population = state.population.copy()  # (N,)
    labor_pool = state.labor_pool.copy()  # (N, S)

    # ------------------------------------------------------------------
    # 1. Natural growth
    # ------------------------------------------------------------------
    is_northern = _northern_mask(state, N)

    fertility = np.where(
        is_northern,
        config.FERTILITY_RATE_NORTH,
        config.FERTILITY_RATE_SOUTH,
    )
    monthly_birth_rate = fertility / 12.0 / 100.0  # per-capita monthly
    # Add small stochastic jitter
    jitter = state.rng.normal(0.0, 0.02, size=N).astype(np.float64)
    monthly_birth_rate = np.clip(monthly_birth_rate + jitter * monthly_birth_rate, 0.0, None)

    births = population * monthly_birth_rate
    deaths = population * _MONTHLY_DEATH_RATE

    population += births - deaths

    # Distribute births into labor pool (working-age fraction ~0.55)
    working_age_births = births * 0.55
    labor_pool += working_age_births[:, np.newaxis] * _LABOR_SKILL_DISTRIBUTION[np.newaxis, :]

    # Remove deaths proportionally from labor pool
    labor_total = labor_pool.sum(axis=1)
    safe_total = np.maximum(labor_total, 1.0)
    death_fraction = deaths / safe_total
    death_fraction = np.clip(death_fraction, 0.0, 0.5)  # safety cap
    labor_pool *= (1.0 - death_fraction[:, np.newaxis])

    logger.debug(
        "Natural growth: births=%.0f  deaths=%.0f  net=%.0f",
        births.sum(), deaths.sum(), (births - deaths).sum(),
    )

    # ------------------------------------------------------------------
    # 2. Migration (gravity model, sparse)
    # ------------------------------------------------------------------
    pull_scores = _compute_pull_scores(state, config)  # (N,)

    migration_flows, net_migration = _gravity_migration(
        population, pull_scores, config, state.rng,
    )

    population += net_migration

    # Ensure no negative populations
    population = np.maximum(population, 0.0)

    # ------------------------------------------------------------------
    # 3. Update labor pool from migration
    # ------------------------------------------------------------------
    labor_pool = _adjust_labor_for_migration(
        labor_pool, net_migration, state.wages, config,
    )

    # Ensure non-negative
    labor_pool = np.maximum(labor_pool, 0.0)

    logger.debug(
        "Migration: %d flows, net movement=%.0f",
        len(migration_flows), np.abs(net_migration).sum() / 2,
    )

    return DemographicMutations(
        population_new=population,
        migration_flows=migration_flows,
        labor_pool_new=labor_pool,
        voter_type_populations_new=None,
    )


def apply_demographic_mutations(
    state: EconomicState, mutations: DemographicMutations,
) -> None:
    """Write demographic mutations back to state."""
    state.population = mutations.population_new
    state.labor_pool = mutations.labor_pool_new
    if mutations.voter_type_populations_new is not None:
        # future: propagate to voter model
        pass


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _northern_mask(state: EconomicState, n: int) -> np.ndarray:
    """
    Determine which LGAs are 'northern' for fertility purposes.

    Priority order:
    1. Admin zone mapping (zones 0-3 = northern: NW, NE, NC, North-Central)
    2. Desertification data as proxy (non-zero = northern/sahel)
    3. Fallback: first 4 zones' worth of LGAs (approximate)
    """
    # Best: use actual admin zone mapping
    if state.admin_zone is not None:
        # 8 zones (0-indexed): 0=NW, 1=NE, 2=NC, 3=North-Central,
        # 4=SW, 5=SE, 6=SS, 7=Lagos
        return state.admin_zone <= 3

    # Second-best: desertification proxy
    if state.desertification_loss is not None and state.desertification_loss.any():
        return state.desertification_loss > 0.0

    # Fallback: approximate half (pre-zone-mapping data)
    mask = np.zeros(n, dtype=bool)
    mask[n // 2:] = True
    return mask


def _compute_pull_scores(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """
    Compute migration pull score for each LGA.

    pull = w_wage * wage_index + w_safety * safety + w_services * services

    All components normalised to [0, 1] before weighting.
    """
    N = config.N_LGAS

    # --- Wage component: mean wage across skill tiers, normalised ---
    mean_wage = state.wages.mean(axis=1)  # (N,)
    wage_max = mean_wage.max()
    wage_index = mean_wage / wage_max if wage_max > 0 else np.ones(N)

    # --- Safety component: 1 - al-shahid control ---
    if state.alsahid_control is not None:
        safety = 1.0 - np.clip(state.alsahid_control, 0.0, 1.0)
    else:
        safety = np.ones(N, dtype=np.float64)

    # --- Services component: average of road + power quality ---
    road = state.infra_road_quality if state.infra_road_quality is not None else np.full(N, 0.5)
    power = state.infra_power_reliability if state.infra_power_reliability is not None else np.full(N, 0.5)
    services = 0.5 * np.clip(road, 0.0, 1.0) + 0.5 * np.clip(power, 0.0, 1.0)

    pull = (
        config.MIGRATION_PULL_WAGE_WEIGHT * wage_index
        + config.MIGRATION_PULL_SAFETY_WEIGHT * safety
        + config.MIGRATION_PULL_SERVICES_WEIGHT * services
    )
    return pull


def _gravity_migration(
    population: np.ndarray,   # (N,)
    pull: np.ndarray,         # (N,)
    config: SimConfig,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Sparse gravity-model migration.

    For each LGA, compute outflow to its top-K most attractive destinations.
    Returns:
        flows: (K_total, 3) array of (source, dest, amount)
        net_migration: (N,) signed array (positive = net inflow)
    """
    N = config.N_LGAS
    friction = config.MIGRATION_FRICTION
    K = min(_TOP_K_DESTINATIONS, N - 1)

    # How much each LGA can lose this month
    max_outflow = population * friction  # (N,)

    # Pull differential: how much better dest j is vs source i
    # For efficiency, sort pull to find top-K globally and let each LGA
    # target those, rather than an N^2 computation.
    top_k_global = np.argsort(pull)[-K:][::-1]  # indices of top-K LGAs by pull

    flow_rows = []
    net_migration = np.zeros(N, dtype=np.float64)

    # Vectorised: compute pull differentials for all sources vs top-K dests
    # pull_diff[i, k] = pull[top_k[k]] - pull[i]
    pull_diff = pull[top_k_global][np.newaxis, :] - pull[:, np.newaxis]  # (N, K)
    pull_diff = np.maximum(pull_diff, 0.0)  # only move toward higher pull

    # Normalise per source so fractions sum to <= 1
    row_sum = pull_diff.sum(axis=1, keepdims=True)
    safe_row_sum = np.maximum(row_sum, 1e-12)
    fractions = pull_diff / safe_row_sum  # (N, K)

    # Actual outflow
    outflow = max_outflow[:, np.newaxis] * fractions  # (N, K)

    # Add small noise to prevent deterministic lock-in
    noise = rng.uniform(0.9, 1.1, size=outflow.shape)
    outflow *= noise

    # Don't let a source send more than friction * population total
    outflow_total = outflow.sum(axis=1, keepdims=True)
    safe_outflow_total = np.maximum(outflow_total, 1e-12)
    scale = np.minimum(max_outflow[:, np.newaxis] / safe_outflow_total, 1.0)
    outflow *= scale

    # Build sparse flow array and accumulate net migration
    # Filter out negligible flows (< 1 person)
    for k_idx in range(K):
        dest = top_k_global[k_idx]
        amounts = outflow[:, k_idx]  # (N,)
        significant = amounts >= 1.0
        # Exclude self-migration
        significant[dest] = False

        sources = np.where(significant)[0]
        if len(sources) == 0:
            continue

        flow_amounts = amounts[sources]
        for s, a in zip(sources, flow_amounts):
            flow_rows.append((s, dest, a))

        net_migration[sources] -= flow_amounts
        net_migration[dest] += flow_amounts.sum()

    if flow_rows:
        flows = np.array(flow_rows, dtype=np.float64)
    else:
        flows = np.empty((0, 3), dtype=np.float64)

    logger.debug(
        "Gravity migration: %d non-trivial flows, total movers=%.0f",
        len(flow_rows), np.abs(net_migration).sum() / 2,
    )

    return flows, net_migration


def _adjust_labor_for_migration(
    labor_pool: np.ndarray,   # (N, S)
    net_migration: np.ndarray,  # (N,)
    wages: np.ndarray,         # (N, S)
    config: SimConfig,
) -> np.ndarray:
    """
    Adjust labor pool for net migration.

    Inflows add workers biased toward skill tiers with higher wages at the
    destination (workers move where they can earn). Outflows remove workers
    proportionally to existing skill distribution.
    """
    N = config.N_LGAS
    S = config.N_SKILL_TIERS
    pool = labor_pool.copy()

    inflow_mask = net_migration > 0
    outflow_mask = net_migration < 0

    # --- Outflows: remove proportionally ---
    if outflow_mask.any():
        out_lgas = np.where(outflow_mask)[0]
        totals = pool[out_lgas].sum(axis=1)
        safe_totals = np.maximum(totals, 1.0)
        fracs = pool[out_lgas] / safe_totals[:, np.newaxis]
        removals = (-net_migration[out_lgas])[:, np.newaxis] * fracs
        pool[out_lgas] -= removals

    # --- Inflows: bias toward high-wage tiers at destination ---
    if inflow_mask.any():
        in_lgas = np.where(inflow_mask)[0]
        dest_wages = wages[in_lgas]  # (n_in, S)
        wage_sum = dest_wages.sum(axis=1, keepdims=True)
        safe_wage_sum = np.maximum(wage_sum, 1.0)
        wage_weights = dest_wages / safe_wage_sum  # (n_in, S)
        additions = net_migration[in_lgas][:, np.newaxis] * wage_weights
        pool[in_lgas] += additions

    return pool
