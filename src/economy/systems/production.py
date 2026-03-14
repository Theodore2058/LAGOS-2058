"""
Production Engine — Cobb-Douglas and Leontief production functions.

Handles all 36 commodities across 774 LGAs, processed in tier order
so higher-tier goods can consume freshly produced lower-tier inputs.
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import (
    EconomicState,
    IMPORT_DEPENDENCIES,
    ProductionMutations,
    SimConfig,
    SkillTier,
)
from src.economy.data.commodities import (
    COMMODITIES,
    COMMODITIES_BY_TIER,
    CommodityTier,
)
from src.economy.data.zaibatsu import ZAIBATSU_BY_ID

logger = logging.getLogger(__name__)


def tick_production(state: EconomicState, config: SimConfig) -> ProductionMutations:
    """
    Execute one production tick across all 774 LGAs and 36 commodities.

    Processes commodities in tier order (0 -> 1 -> 2 -> 3) so higher-tier
    goods see freshly produced lower-tier inputs. Within a tier, all
    commodities are processed using the same inventory snapshot.
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES
    S = config.N_SKILL_TIERS

    # Working copies
    inv = state.inventories.copy()
    labor_available = state.labor_pool.copy()
    labor_employed = np.zeros((N, S), dtype=np.float64)
    wages_paid = np.zeros((N, S), dtype=np.float64)
    capacity_util = np.zeros((N, C), dtype=np.float64)
    output_total = np.zeros((N, C), dtype=np.float64)

    # Build import fulfillment constraint per commodity
    import_cap = np.ones(C, dtype=np.float64)
    if state.import_fulfillment:
        for dep_name, dep in IMPORT_DEPENDENCIES.items():
            fulfillment = state.import_fulfillment.get(dep_name, 1.0)
            if fulfillment < 1.0:
                for cid in dep.get("required_by", []):
                    if 0 <= cid < C:
                        import_cap[cid] = min(import_cap[cid], fulfillment)

    # Process tiers in order
    for tier in sorted(COMMODITIES_BY_TIER.keys()):
        tier_commodities = COMMODITIES_BY_TIER[tier]

        # Snapshot inventory at start of tier (within-tier commodities share inputs)
        tier_inv_snapshot = inv.copy()
        # Track total input consumption this tier to avoid double-spending
        tier_consumed = np.zeros((N, C), dtype=np.float64)

        for cdef in tier_commodities:
            c = cdef.id

            # Skip commodities with zero capacity everywhere
            cap = state.production_capacity[:, c].copy()
            # Apply import fulfillment constraint (reduces effective capacity)
            if import_cap[c] < 1.0:
                cap = cap * import_cap[c]
            if cap.max() <= 0:
                continue

            # Build input requirement arrays
            input_ids = sorted(cdef.inputs.keys())
            input_reqs = np.array([cdef.inputs[i] for i in input_ids], dtype=np.float64)

            # Build labor requirement array
            labor_req = np.zeros(S, dtype=np.float64)
            for skill_int, amount in cdef.labor_requirements.items():
                labor_req[int(skill_int)] = amount

            # Vectorized production across all LGAs
            output, inp_consumed, lab_used = _produce_commodity(
                capacity=cap,
                inventory=tier_inv_snapshot,
                input_ids=np.array(input_ids, dtype=np.int32) if input_ids else np.array([], dtype=np.int32),
                input_reqs=input_reqs if len(input_reqs) > 0 else np.array([], dtype=np.float64),
                labor_available=labor_available - labor_employed,  # remaining labor
                labor_req=labor_req,
                power_reliability=state.infra_power_reliability,
                factory_owner=state.factory_owner[:, c],
                enhancement_adoption=state.enhancement_adoption,
                automation_level=state.automation_level[:, c],
                rainfall_modifier=max(min(state.rainfall_modifier, 1.5), 0.1) if cdef.tier == CommodityTier.RAW and c in (6,7,8,9,10,11,12,13) else 1.0,
                production_type=cdef.production_type,
                waste_factor=config.LEONTIEF_WASTE_FACTOR,
                alpha_labor=config.COBB_DOUGLAS_LABOR_SHARE,
                alpha_land=config.COBB_DOUGLAS_LAND_SHARE,
                alpha_capital=config.COBB_DOUGLAS_CAPITAL_SHARE,
                enhancement_bonus=config.ENHANCEMENT_PRODUCTIVITY_BONUS,
                strikes=state.strikes_active,
            )

            # Record results
            output_total[:, c] = output
            safe_cap_c = np.where(cap > 0, cap, 1.0)
            capacity_util[:, c] = np.where(cap > 0, output / safe_cap_c, 0.0)

            # Accumulate input consumption
            for idx, inp_id in enumerate(input_ids):
                tier_consumed[:, inp_id] += inp_consumed[:, idx] if inp_consumed.shape[1] > idx else 0

            # Accumulate labor usage
            labor_employed += lab_used

        # Deduct consumed inputs and add produced outputs
        inv -= tier_consumed
        inv = np.maximum(inv, 0.0)  # safety clamp

        # Add outputs from this tier to inventory
        for cdef in tier_commodities:
            inv[:, cdef.id] += output_total[:, cdef.id]

    # Compute inventory deltas
    inventory_deltas = inv - state.inventories

    # Compute wages paid
    wages_paid = labor_employed * state.wages

    return ProductionMutations(
        inventory_deltas=inventory_deltas,
        labor_employed_new=labor_employed,
        wages_paid=wages_paid,
        capacity_utilization=capacity_util,
    )


def _produce_commodity(
    capacity: np.ndarray,           # (N,)
    inventory: np.ndarray,          # (N, C)
    input_ids: np.ndarray,          # (n_inputs,)
    input_reqs: np.ndarray,         # (n_inputs,)
    labor_available: np.ndarray,    # (N, S)
    labor_req: np.ndarray,          # (S,)
    power_reliability: np.ndarray,  # (N,)
    factory_owner: np.ndarray,      # (N,) int8
    enhancement_adoption: np.ndarray,  # (N,)
    automation_level: np.ndarray,   # (N,)
    rainfall_modifier: float,
    production_type: str,
    waste_factor: float,
    alpha_labor: float,
    alpha_land: float,
    alpha_capital: float,
    enhancement_bonus: float,
    strikes: np.ndarray,            # (N,)
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized production for one commodity across all LGAs.

    Returns:
        output: (N,) units produced
        inputs_consumed: (N, n_inputs) actual inputs consumed
        labor_used: (N, S) workers employed
    """
    N = capacity.shape[0]
    S = labor_req.shape[0]
    n_inputs = len(input_ids)

    output = np.zeros(N, dtype=np.float64)
    inputs_consumed = np.zeros((N, max(n_inputs, 1)), dtype=np.float64)
    labor_used = np.zeros((N, S), dtype=np.float64)

    # Mask: only produce where capacity > 0 and no strike
    active = (capacity > 0) & (strikes <= 0)
    if not active.any():
        return output, inputs_consumed, labor_used

    # Zaibatsu efficiency bonus
    zaibatsu_bonus = np.ones(N, dtype=np.float64)
    for z_id, z_def in ZAIBATSU_BY_ID.items():
        mask = factory_owner == z_id
        zaibatsu_bonus[mask] = 1.0 + z_def.efficiency_bonus

    # Enhancement bonus
    enh_mult = 1.0 + enhancement_adoption * enhancement_bonus

    # Automation increases effective labor
    auto_labor_mult = 1.0 + automation_level * 0.5

    if production_type == "cobb_douglas":
        output[active] = _cobb_douglas_vec(
            capacity[active],
            inventory[active],
            input_ids, input_reqs,
            labor_available[active],
            labor_req,
            auto_labor_mult[active],
            rainfall_modifier,
            enh_mult[active],
            alpha_labor, alpha_land, alpha_capital,
        )
    else:  # leontief
        output[active] = _leontief_vec(
            capacity[active],
            inventory[active],
            input_ids, input_reqs,
            labor_available[active],
            labor_req,
            auto_labor_mult[active],
            power_reliability[active],
            zaibatsu_bonus[active],
            enh_mult[active],
            waste_factor,
        )

    # Clamp output to capacity
    output = np.minimum(output, capacity)
    output = np.maximum(output, 0.0)

    # Compute actual inputs consumed
    if n_inputs > 0:
        for idx in range(n_inputs):
            if production_type == "leontief":
                inputs_consumed[:, idx] = output * input_reqs[idx] * (1.0 + waste_factor)
            else:
                # Cobb-Douglas: inputs consumed proportional to output fraction
                inputs_consumed[:, idx] = output * input_reqs[idx]
            # Don't consume more than available
            avail = inventory[:, input_ids[idx]]
            inputs_consumed[:, idx] = np.minimum(inputs_consumed[:, idx], avail)

    # Compute labor used (proportional to output/capacity ratio)
    safe_cap = np.where(capacity > 0, capacity, 1.0)
    cap_ratio = np.where(capacity > 0, output / safe_cap, 0.0)
    for s in range(S):
        if labor_req[s] > 0:
            needed = capacity * labor_req[s] * cap_ratio / auto_labor_mult
            labor_used[:, s] = np.minimum(needed, labor_available[:, s])

    return output, inputs_consumed, labor_used


def _cobb_douglas_vec(
    capacity: np.ndarray,
    inventory: np.ndarray,
    input_ids: np.ndarray,
    input_reqs: np.ndarray,
    labor_available: np.ndarray,
    labor_req: np.ndarray,
    auto_labor_mult: np.ndarray,
    rainfall_modifier: float,
    enh_mult: np.ndarray,
    alpha_labor: float,
    alpha_land: float,
    alpha_capital: float,
) -> np.ndarray:
    """
    Vectorized Cobb-Douglas: output = capacity * (L/L_req)^a_L * (K/K_req)^a_K * rain * enh

    Each factor clamped to [0, 1].
    """
    n = capacity.shape[0]
    S = labor_req.shape[0]

    # Labor factor
    labor_factor = np.ones(n, dtype=np.float64)
    total_labor_req = labor_req.sum()
    if total_labor_req > 0:
        effective_labor = np.zeros(n, dtype=np.float64)
        for s in range(S):
            if labor_req[s] > 0:
                avail = labor_available[:, s] * auto_labor_mult
                needed = capacity * labor_req[s]
                ratio = np.where(needed > 0, avail / needed, 1.0)
                effective_labor += np.clip(ratio, 0.0, 1.0) * (labor_req[s] / total_labor_req)
        labor_factor = np.clip(effective_labor, 0.0, 1.0) ** alpha_labor

    # Input/capital factor
    input_factor = np.ones(n, dtype=np.float64)
    if len(input_ids) > 0:
        total_input_req = input_reqs.sum()
        if total_input_req > 0:
            for idx in range(len(input_ids)):
                avail = inventory[:, input_ids[idx]]
                needed = capacity * input_reqs[idx]
                ratio = np.where(needed > 0, avail / needed, 1.0)
                input_factor *= np.clip(ratio, 0.0, 1.0)
            input_factor = input_factor ** alpha_capital

    output = capacity * labor_factor * input_factor * rainfall_modifier * enh_mult
    return np.clip(output, 0.0, capacity)


def _leontief_vec(
    capacity: np.ndarray,
    inventory: np.ndarray,
    input_ids: np.ndarray,
    input_reqs: np.ndarray,
    labor_available: np.ndarray,
    labor_req: np.ndarray,
    auto_labor_mult: np.ndarray,
    power_reliability: np.ndarray,
    zaibatsu_bonus: np.ndarray,
    enh_mult: np.ndarray,
    waste_factor: float,
) -> np.ndarray:
    """
    Vectorized Leontief: output = capacity * min(bottleneck ratios) * bonuses

    Bottleneck: output limited by scarcest input or labor.
    """
    n = capacity.shape[0]
    S = labor_req.shape[0]

    # Start with capacity as upper bound
    bottleneck = np.ones(n, dtype=np.float64)

    # Input bottleneck: for each input, how much of capacity can we supply?
    if len(input_ids) > 0:
        for idx in range(len(input_ids)):
            avail = inventory[:, input_ids[idx]]
            needed = capacity * input_reqs[idx] * (1.0 + waste_factor)
            ratio = np.where(needed > 0, avail / needed, 1.0)
            bottleneck = np.minimum(bottleneck, np.clip(ratio, 0.0, 1.0))

    # Labor bottleneck
    for s in range(S):
        if labor_req[s] > 0:
            effective = labor_available[:, s] * auto_labor_mult
            needed = capacity * labor_req[s]
            ratio = np.where(needed > 0, effective / needed, 1.0)
            bottleneck = np.minimum(bottleneck, np.clip(ratio, 0.0, 1.0))

    # Power reliability bottleneck
    # Below 0.3, production halts
    power_factor = np.where(power_reliability < 0.3, 0.0, power_reliability)
    bottleneck = np.minimum(bottleneck, power_factor)

    output = capacity * bottleneck * zaibatsu_bonus * enh_mult
    return np.clip(output, 0.0, capacity * zaibatsu_bonus * enh_mult)


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------

def assert_production_valid(
    state: EconomicState, mutations: ProductionMutations,
) -> None:
    """Run after every production tick."""
    # No inventory goes negative (with tolerance)
    new_inv = state.inventories + mutations.inventory_deltas
    if np.any(new_inv < -1e-3):
        worst = new_inv.min()
        logger.warning("Production: inventory went negative (min=%.4f), clamping", worst)

    # Capacity utilization bounded
    assert np.all(mutations.capacity_utilization <= 1.0 + 1e-3), \
        "Production exceeded capacity"

    # Employment doesn't exceed labor pool
    total_employed = mutations.labor_employed_new.sum(axis=1)
    total_available = state.labor_pool.sum(axis=1)
    overemployed = total_employed > total_available + 1e-3
    if overemployed.any():
        logger.warning(
            "Production: %d LGAs over-employed (max excess: %.0f)",
            overemployed.sum(),
            (total_employed - total_available)[overemployed].max(),
        )


def apply_production_mutations(
    state: EconomicState, mutations: ProductionMutations,
) -> None:
    """Apply production results to state."""
    state.inventories = np.maximum(state.inventories + mutations.inventory_deltas, 0.0)
    state.labor_employed = mutations.labor_employed_new
    state.actual_output = mutations.inventory_deltas.clip(min=0.0)  # actual production output
