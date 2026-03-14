"""
Economy-to-election feedback system and election anticipation effects.

Provides two main interfaces:
  - compute_election_feedback(): 5-channel feedback from economy to election engine
  - tick_anticipation(): election proximity effects on economic behaviour
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from src.economy.core.types import (
    EconomicState,
    ElectionFeedback,
    AnticipationMutations,
    SimConfig,
    VOTER_DIMENSIONS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Voter-type decomposition helpers
# ---------------------------------------------------------------------------

# Build strides for modular-arithmetic decomposition of voter_type_id.
# Ordering follows VOTER_DIMENSIONS dict insertion order:
#   lga, ethnicity, religion, skill_tier, urban_rural, age_cohort, pada_status, enhancement
_DIM_NAMES = list(VOTER_DIMENSIONS.keys())
_DIM_SIZES = list(VOTER_DIMENSIONS.values())

# Strides: the rightmost dimension changes fastest (row-major / C order).
_STRIDES = np.empty(len(_DIM_SIZES), dtype=np.int64)
_STRIDES[-1] = 1
for _i in range(len(_DIM_SIZES) - 2, -1, -1):
    _STRIDES[_i] = _STRIDES[_i + 1] * _DIM_SIZES[_i + 1]

_LGA_IDX = _DIM_NAMES.index("lga")
_SKILL_IDX = _DIM_NAMES.index("skill_tier")
_LGA_STRIDE = int(_STRIDES[_LGA_IDX])
_SKILL_STRIDE = int(_STRIDES[_SKILL_IDX])
_N_LGA = VOTER_DIMENSIONS["lga"]
_N_SKILL = VOTER_DIMENSIONS["skill_tier"]

# Issue dimension indices (must match the 28-dim ordering used by the election engine)
_ISSUE_ECONOMY = 0
_ISSUE_INFRASTRUCTURE = 3
_ISSUE_HOUSING = 5

# Skill-tier to income-quintile mapping (4 tiers -> quintile 1-5)
# UNSKILLED -> Q1-Q2 (poor), SKILLED -> Q3, HIGHLY_SKILLED -> Q4, CHINESE_ELITE -> Q5
_TIER_TO_QUINTILE = np.array([1, 2, 4, 5], dtype=np.int32)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _decompose_voter_ids(n_voter_types: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (lga_ids, skill_tier_ids) arrays of length *n_voter_types*."""
    ids = np.arange(n_voter_types, dtype=np.int64)
    lga_ids = (ids // _LGA_STRIDE) % _N_LGA
    skill_ids = (ids // _SKILL_STRIDE) % _N_SKILL
    return lga_ids.astype(np.int32), skill_ids.astype(np.int32)


def _welfare_sensitivity(skill_tiers: np.ndarray, config: SimConfig) -> np.ndarray:
    """Per-voter sensitivity weight: higher for poor quintiles."""
    quintiles = _TIER_TO_QUINTILE[skill_tiers]
    weights = np.where(
        quintiles <= 2,
        config.WELFARE_SENSITIVITY_POOR,
        config.WELFARE_SENSITIVITY_RICH,
    )
    return weights.astype(np.float64)


# ---------------------------------------------------------------------------
# 1. compute_election_feedback
# ---------------------------------------------------------------------------

def compute_election_feedback(
    state: EconomicState,
    config: SimConfig,
) -> ElectionFeedback:
    """
    Compute 5-channel feedback from the economy to the election engine.

    Returns an :class:`ElectionFeedback` with:
      - welfare_scores        (N_VOTER_TYPES,)
      - salience_shifts       (N_VOTER_TYPES, N_ISSUE_DIMENSIONS)
      - position_shifts       (N_VOTER_TYPES, N_ISSUE_DIMENSIONS)
      - migration_voter_changes (N_LGAS,)
      - governance_satisfaction (scalar)
    """
    n_vt = config.N_VOTER_TYPES
    n_dim = config.N_ISSUE_DIMENSIONS

    lga_ids, skill_ids = _decompose_voter_ids(n_vt)

    # --- (a) Welfare scores ---------------------------------------------------
    welfare = _compute_welfare(state, config, lga_ids, skill_ids)

    # --- (b) Salience shifts ---------------------------------------------------
    salience = _compute_salience_shifts(state, config, n_vt, n_dim, lga_ids)

    # --- (c) Position shifts: economic stress shifts voter positions ------------
    positions = _compute_position_shifts(state, config, n_vt, n_dim, lga_ids, skill_ids)

    # --- (d) Migration voter changes -------------------------------------------
    migration = _compute_migration_changes(state, config)

    # --- (e) Governance satisfaction -------------------------------------------
    governance = _compute_governance_satisfaction(state, config)

    logger.debug(
        "election_feedback: welfare=[%.3f, %.3f], governance=%.4f",
        float(np.min(welfare)),
        float(np.max(welfare)),
        governance,
    )

    return ElectionFeedback(
        welfare_scores=welfare,
        salience_shifts=salience,
        position_shifts=positions,
        migration_voter_changes=migration,
        governance_satisfaction=governance,
    )


def _compute_welfare(
    state: EconomicState,
    config: SimConfig,
    lga_ids: np.ndarray,
    skill_ids: np.ndarray,
) -> np.ndarray:
    """
    Welfare score per voter type.

    When per-pop SoL and sentiment are available (V3 systems), blends them
    for a richer signal. Falls back to aggregate wages/employment otherwise.
    """
    n_vt = config.N_VOTER_TYPES

    # --- V3 path: use per-pop standard-of-living + sentiment ---
    if (
        state.pop_standard_of_living is not None
        and state.pop_sentiment is not None
        and state.pop_standard_of_living.shape[0] == n_vt
    ):
        # SoL is 0-10, normalise to [-1, 1]: (sol - 5) / 5
        sol_signal = (state.pop_standard_of_living - 5.0) / 5.0  # (NVT,)
        # Sentiment is already [-1, 1]
        sentiment_signal = state.pop_sentiment  # (NVT,)

        # Blend: 60% SoL (slow-moving), 40% sentiment (fast-moving)
        raw_welfare = 0.6 * sol_signal + 0.4 * sentiment_signal

        # Al-Shahid service bonus
        pop_lga = getattr(state, "_pop_lga_ids", None)
        if (
            pop_lga is not None
            and state.alsahid_service_provision is not None
            and state.alsahid_control is not None
        ):
            control = state.alsahid_control[pop_lga]
            service = state.alsahid_service_provision[pop_lga]
            # Better al-Shahid services in controlled areas modestly boost welfare
            raw_welfare += control * service * 0.15

        welfare = np.clip(raw_welfare, -1.0, 1.0)
        return welfare

    # --- Legacy fallback: aggregate wages/employment ---
    if state.wages is not None:
        wages = state.wages
    else:
        wages = np.tile(config.BASE_WAGES, (config.N_LGAS, 1))

    if state.labor_employed is not None and state.labor_pool is not None:
        safe_pool = np.maximum(state.labor_pool, 1.0)
        emp_rate = state.labor_employed / safe_pool
    else:
        emp_rate = np.ones((config.N_LGAS, config.N_SKILL_TIERS), dtype=np.float64)

    if state.prices is not None:
        food_ids = [6, 7, 8, 13, 18, 21]
        col = np.mean(state.prices[:, food_ids], axis=1)
    else:
        col = np.zeros(config.N_LGAS, dtype=np.float64)

    vt_wages = wages[lga_ids, skill_ids]
    vt_emp = emp_rate[lga_ids, skill_ids]
    vt_col = col[lga_ids]

    raw_welfare = vt_wages * vt_emp - vt_col

    if state.alsahid_service_provision is not None and state.alsahid_control is not None:
        if state.budget_released is not None and state.budget_allocation is not None:
            safe_alloc = np.maximum(state.budget_allocation.sum(), 1.0)
            gov_service = float(np.sum(state.budget_released) / safe_alloc)
        else:
            gov_service = 0.5

        alsahid_svc = state.alsahid_service_provision
        control = state.alsahid_control
        effective_service = (1.0 - control) * gov_service + control * alsahid_svc
        service_bonus = effective_service * 0.2 * col
        vt_service_bonus = service_bonus[lga_ids]
        raw_welfare += vt_service_bonus

    sensitivity = _welfare_sensitivity(skill_ids, config)
    weighted = raw_welfare * sensitivity

    abs_max = np.maximum(np.max(np.abs(weighted)), 1e-12)
    welfare = np.clip(weighted / abs_max, -1.0, 1.0)

    return welfare


def _compute_salience_shifts(
    state: EconomicState,
    config: SimConfig,
    n_vt: int,
    n_dim: int,
    lga_ids: np.ndarray,
) -> np.ndarray:
    """Issue salience shifts driven by economic crises."""
    shifts = np.zeros((n_vt, n_dim), dtype=np.float64)

    if state.prices is None:
        return shifts

    # Food crisis: food prices > 2x base
    food_ids = [6, 7, 8, 13, 18, 21]
    food_prices = np.mean(state.prices[:, food_ids], axis=1)  # (774,)
    base_food = np.mean(config.BASE_WAGES[0]) * 0.001  # rough base proxy
    if base_food < 1e-6:
        base_food = np.median(food_prices) / 2.0 if np.median(food_prices) > 0 else 1.0
    food_crisis_mask = food_prices > 2.0 * base_food  # (774,) bool
    vt_food_crisis = food_crisis_mask[lga_ids]
    shifts[vt_food_crisis, _ISSUE_ECONOMY] += config.SALIENCE_SHIFT_FOOD_CRISIS

    # Power crisis: reliability < 0.4
    if state.infra_power_reliability is not None:
        power_crisis_mask = state.infra_power_reliability < 0.4  # (774,)
        vt_power_crisis = power_crisis_mask[lga_ids]
        shifts[vt_power_crisis, _ISSUE_INFRASTRUCTURE] += config.SALIENCE_SHIFT_POWER_CRISIS

    # Housing crisis: housing prices > 3x base
    if state.land_prices is not None:
        housing_prices = state.land_prices[:, 1]  # residential
        base_housing = np.median(housing_prices)
        if base_housing > 0:
            housing_crisis_mask = housing_prices > 3.0 * base_housing
            vt_housing_crisis = housing_crisis_mask[lga_ids]
            shifts[vt_housing_crisis, _ISSUE_HOUSING] += config.SALIENCE_SHIFT_HOUSING_CRISIS

    return shifts


def _compute_position_shifts(
    state: EconomicState,
    config: SimConfig,
    n_vt: int,
    n_dim: int,
    lga_ids: np.ndarray,
    skill_ids: np.ndarray,
) -> np.ndarray:
    """
    Economic stress shifts voter issue positions.

    - High unemployment/inflation → more interventionist on ECONOMY dimension
    - High al-Shahid control → more security-focused
    - Enhancement adoption → shift on TECHNOLOGY dimension
    """
    shifts = np.zeros((n_vt, n_dim), dtype=np.float64)

    # Issue dimension indices
    _ISSUE_SECURITY = 1  # security dimension
    _ISSUE_TECHNOLOGY = 4  # technology/enhancement dimension

    # Employment stress → economic interventionism
    if state.labor_employed is not None and state.labor_pool is not None:
        safe_pool = np.maximum(state.labor_pool, 1.0)
        unemployment_rate = 1.0 - (state.labor_employed / safe_pool)  # (N, S)
        # Per voter type: their skill tier's unemployment in their LGA
        vt_unemp = unemployment_rate[lga_ids, skill_ids]
        # High unemployment shifts toward interventionism (positive direction)
        shifts[:, _ISSUE_ECONOMY] += 0.3 * (vt_unemp - 0.15)  # centered on 15% baseline

    # Al-Shahid control → security priority
    if state.alsahid_control is not None:
        control_per_vt = state.alsahid_control[lga_ids]
        # High control shifts toward security hawk position
        shifts[:, _ISSUE_SECURITY] += 0.4 * control_per_vt

    # Enhancement adoption → technology position
    if state.enhancement_adoption is not None:
        enh_per_vt = state.enhancement_adoption[lga_ids]
        # High adoption normalizes enhancement (shifts toward pro-tech)
        shifts[:, _ISSUE_TECHNOLOGY] += 0.2 * (enh_per_vt - 0.5)

    return np.clip(shifts, -0.5, 0.5)


def _compute_migration_changes(
    state: EconomicState,
    config: SimConfig,
) -> np.ndarray:
    """Net migration voter changes per LGA."""
    if state.population is not None and hasattr(state, "_prev_population"):
        return state.population - state._prev_population  # type: ignore[attr-defined]
    return np.zeros(config.N_LGAS, dtype=np.float64)


def _compute_governance_satisfaction(
    state: EconomicState,
    config: SimConfig,
) -> float:
    """
    satisfaction = mean(budget_released / budget_allocated) * (1 - mean(corruption_leakage))
    Scaled by GOVERNANCE_REWARD_MULTIPLIER.
    """
    if state.budget_released is not None and state.budget_allocation is not None:
        safe_alloc = np.maximum(state.budget_allocation, 1.0)
        execution_rate = float(np.mean(state.budget_released / safe_alloc))
    else:
        execution_rate = 0.5  # neutral default

    if state.corruption_leakage is not None:
        corruption = float(np.mean(state.corruption_leakage))
    else:
        corruption = 0.2  # moderate default

    raw = execution_rate * (1.0 - corruption)

    # Al-Shahid governance penalty: high al-Shahid control signals government failure
    if state.alsahid_control is not None:
        mean_control = float(state.alsahid_control.mean())
        # Each 10% average control penalises satisfaction by ~5%
        raw *= (1.0 - 0.5 * mean_control)

    return float(np.clip(raw * config.GOVERNANCE_REWARD_MULTIPLIER, -1.0, 1.0))


# ---------------------------------------------------------------------------
# 2. tick_anticipation
# ---------------------------------------------------------------------------

def tick_anticipation(
    state: EconomicState,
    config: SimConfig,
    election_proximity: float,
) -> AnticipationMutations:
    """
    Compute election-anticipation effects on the economy.

    Parameters
    ----------
    state : EconomicState
    config : SimConfig
    election_proximity : float
        0.0 = far from election, 1.0 = imminent.

    Returns
    -------
    AnticipationMutations
    """
    proximity = float(np.clip(election_proximity, 0.0, 1.0))

    # --- Platform-driven modifiers ---
    # Leading party's policy signals amplify or dampen anticipation effects.
    signals = state.platform_signals
    nationalization = signals.get("nationalization_risk", 0.0)
    liberalization = signals.get("liberalization_signal", 0.0)
    capital_controls = signals.get("capital_controls_risk", 0.0)

    # Nationalization risk amplifies capital flight and investment withdrawal.
    # Liberalization reduces both (investors welcome market-friendly platforms).
    policy_fear = 1.0 + 0.5 * nationalization - 0.3 * liberalization
    policy_fear = max(policy_fear, 0.2)  # floor

    # Investment modifier: firms reduce investment as election nears
    inv_sensitivity = config.ANTICIPATION_INVESTMENT_SENSITIVITY * policy_fear
    inv_modifier_scalar = 1.0 - inv_sensitivity * proximity
    investment_modifier = np.full(
        config.N_LGAS, inv_modifier_scalar, dtype=np.float64,
    )

    # Capital flight: outflows from admin zones when proximity exceeds threshold
    capital_flight = np.zeros(config.N_ADMIN_ZONES, dtype=np.float64)
    flight_threshold = config.ANTICIPATION_CAPITAL_FLIGHT_THRESHOLD
    # Capital controls risk lowers the threshold (flight starts earlier)
    flight_threshold = max(flight_threshold - 0.2 * capital_controls, 0.3)
    if proximity > flight_threshold:
        excess = proximity - flight_threshold
        flight_multiplier = policy_fear * (1.0 + capital_controls)
        if state.bank_deposits is not None:
            capital_flight = state.bank_deposits * excess * 0.1 * flight_multiplier
        else:
            capital_flight = np.full(
                config.N_ADMIN_ZONES, excess * 1e9 * flight_multiplier, dtype=np.float64,
            )

    # Automation acceleration: firms automate faster to hedge against policy change
    accel = config.ANTICIPATION_AUTOMATION_ACCELERATION * proximity * policy_fear
    if state.automation_level is not None:
        automation_acceleration = state.automation_level * accel
    else:
        automation_acceleration = np.full(
            (config.N_LGAS, config.N_COMMODITIES), accel * 0.01, dtype=np.float64,
        )

    # Forex drain: capital flight drains reserves
    forex_drain = float(np.sum(capital_flight)) * 0.001  # convert to USD equivalent

    logger.debug(
        "anticipation: proximity=%.2f, inv_mod=%.3f, capital_flight=%.2e, forex_drain=%.2e",
        proximity,
        inv_modifier_scalar,
        float(np.sum(capital_flight)),
        forex_drain,
    )

    return AnticipationMutations(
        investment_modifier=investment_modifier,
        capital_flight=capital_flight,
        automation_acceleration=automation_acceleration,
        forex_reserve_drain=forex_drain,
    )


# ---------------------------------------------------------------------------
# 3. apply_anticipation_mutations
# ---------------------------------------------------------------------------

def apply_anticipation_mutations(
    state: EconomicState,
    mutations: AnticipationMutations,
) -> None:
    """Apply anticipation mutations to the economic state in-place."""
    # Scale production capacity by investment modifier
    if state.production_capacity is not None:
        state.production_capacity *= mutations.investment_modifier[:, np.newaxis]

    # Drain deposits by capital flight
    if state.bank_deposits is not None:
        state.bank_deposits = np.maximum(
            state.bank_deposits - mutations.capital_flight, 0.0,
        )

    # Accelerate automation
    if state.automation_level is not None:
        state.automation_level += mutations.automation_acceleration

    # Drain forex reserves
    state.forex_reserves_usd = max(
        state.forex_reserves_usd - mutations.forex_reserve_drain, 0.0,
    )
