"""
Building-based production system.

Replaces the aggregate production_capacity approach with explicit building
instances that consume inputs, employ workers, and produce output according
to their building type recipes.

Called once per production tick (7/month).
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import EconomicState, ProductionMutations, SimConfig
from src.economy.data.buildings import BUILDING_TYPE_BY_ID
from src.economy.data.zaibatsu import ZAIBATSU_BY_ID

logger = logging.getLogger(__name__)


def tick_building_production(
    state: EconomicState, config: SimConfig,
) -> ProductionMutations:
    """
    Execute one production tick using explicit building instances.

    For each building:
      1. Check operational status (power, infrastructure)
      2. Compute input bottleneck
      3. Compute labor bottleneck
      4. Apply technology, zaibatsu, enhancement, weather modifiers
      5. Consume inputs from LGA inventory
      6. Produce output into LGA inventory
      7. Employ workers from LGA labor pool
    """
    N = config.N_LGAS
    C = config.N_COMMODITIES
    S = config.N_SKILL_TIERS
    B = state.n_buildings

    # Working arrays
    inventory_deltas = np.zeros((N, C), dtype=np.float64)
    labor_employed = np.zeros((N, S), dtype=np.float64)
    wages_paid = np.zeros((N, S), dtype=np.float64)
    capacity_util = np.zeros((N, C), dtype=np.float64)

    # Track remaining labor available per LGA
    labor_remaining = state.labor_pool.copy()

    if B == 0 or state.building_type_ids is None:
        return ProductionMutations(
            inventory_deltas=inventory_deltas,
            labor_employed_new=labor_employed,
            wages_paid=wages_paid,
            capacity_utilization=capacity_util,
        )

    # Process buildings in tier order for correct input availability
    # Sort building indices by tier
    bt_tiers = np.array(
        [BUILDING_TYPE_BY_ID[int(tid)].tier for tid in state.building_type_ids],
        dtype=np.int32,
    )
    sorted_indices = np.argsort(bt_tiers, kind="stable")

    # Snapshot inventory at start of each tier to prevent double-spending
    current_tier = -1
    tier_inv = state.inventories.copy()

    for i in sorted_indices:
        bt = BUILDING_TYPE_BY_ID.get(int(state.building_type_ids[i]))
        if bt is None:
            continue

        # Tier boundary: snapshot inventory
        if bt.tier != current_tier:
            if current_tier >= 0:
                # Apply deltas from previous tier
                tier_inv = np.maximum(state.inventories + inventory_deltas, 0.0)
            current_tier = bt.tier

        lga = int(state.building_lga_ids[i])
        throughput = state.building_throughput[i]
        tech = state.building_tech_level[i]

        # --- Check operational status ---
        operational = True

        # Power check
        if bt.requires_power and state.infra_power_reliability is not None:
            power = state.infra_power_reliability[lga]
            if power < bt.min_power_reliability:
                state.building_operational[i] = False
                operational = False

        # Strike check
        if state.strikes_active is not None and state.strikes_active[lga] > 0:
            operational = False

        if not operational:
            state.building_operational[i] = False
            continue

        state.building_operational[i] = True

        # --- Compute modifiers ---
        tech_mult = 0.7 + 0.45 * tech

        # Power reliability factor
        if bt.requires_power and state.infra_power_reliability is not None:
            power = state.infra_power_reliability[lga]
            tech_mult *= max(power, 0.3)

        # Zaibatsu bonus
        zaibatsu_mult = 1.0
        owner = int(state.building_owners[i])
        if owner >= 0:
            z = ZAIBATSU_BY_ID.get(owner)
            if z:
                zaibatsu_mult = 1.0 + z.efficiency_bonus

        # Rainfall (agricultural)
        rain_mult = 1.0
        if bt.rainfall_sensitive:
            rain_mult = max(min(state.rainfall_modifier, 1.5), 0.1)

        # Enhancement
        enh_mult = 1.0
        if state.enhancement_adoption is not None:
            enh_mult = 1.0 + state.enhancement_adoption[lga] * config.ENHANCEMENT_PRODUCTIVITY_BONUS

        # Al-Shahid disruption
        alsahid_mult = 1.0
        if state.alsahid_control is not None:
            control = state.alsahid_control[lga]
            alsahid_mult = 1.0 - control * 0.4

        # Import fulfillment constraint
        import_mult = 1.0
        if state.import_fulfillment:
            from src.economy.core.types import IMPORT_DEPENDENCIES
            for dep_name, dep in IMPORT_DEPENDENCIES.items():
                fulfillment = state.import_fulfillment.get(dep_name, 1.0)
                if fulfillment < 1.0 and bt.output_commodity in dep.get("required_by", []):
                    import_mult = min(import_mult, fulfillment)

        # --- Input bottleneck ---
        bottleneck = 1.0
        if bt.inputs:
            for inp_id, inp_per_unit in bt.inputs.items():
                if 0 <= inp_id < C:
                    available = tier_inv[lga, inp_id]
                    needed = throughput * inp_per_unit
                    if needed > 0:
                        ratio = available / needed
                        bottleneck = min(bottleneck, max(ratio, 0.0))

        # --- Labor bottleneck ---
        labor_bottleneck = 1.0
        if bt.labor:
            for skill_int, count in bt.labor.items():
                s = int(skill_int)
                available = labor_remaining[lga, s]
                if count > 0:
                    ratio = available / count
                    labor_bottleneck = min(labor_bottleneck, max(ratio, 0.0))

        # --- Final output ---
        output = (
            throughput
            * tech_mult
            * min(bottleneck, 1.0)
            * min(labor_bottleneck, 1.0)
            * zaibatsu_mult
            * rain_mult
            * alsahid_mult
            * enh_mult
            * import_mult
        )
        output = max(output, 0.0)

        if output <= 0:
            continue

        # --- Consume inputs ---
        if bt.inputs:
            for inp_id, inp_per_unit in bt.inputs.items():
                if 0 <= inp_id < C:
                    consumed = output * inp_per_unit
                    consumed = min(consumed, tier_inv[lga, inp_id])
                    inventory_deltas[lga, inp_id] -= consumed
                    tier_inv[lga, inp_id] -= consumed

        # --- Produce output ---
        inventory_deltas[lga, bt.output_commodity] += output

        # --- Employ workers ---
        if bt.labor:
            cap_ratio = min(bottleneck, labor_bottleneck, 1.0)
            for skill_int, count in bt.labor.items():
                s = int(skill_int)
                workers = count * cap_ratio
                workers = min(workers, labor_remaining[lga, s])
                labor_employed[lga, s] += workers
                labor_remaining[lga, s] -= workers

                # Update building employees
                state.building_employees[i, s] = workers

        # --- Track capacity utilization ---
        if throughput > 0:
            cap_util = output / (throughput * zaibatsu_mult * enh_mult)
            capacity_util[lga, bt.output_commodity] = max(
                capacity_util[lga, bt.output_commodity],
                min(cap_util, 1.0),
            )

    # Compute wages paid
    wages_paid = labor_employed * state.wages

    return ProductionMutations(
        inventory_deltas=inventory_deltas,
        labor_employed_new=labor_employed,
        wages_paid=wages_paid,
        capacity_utilization=capacity_util,
    )
