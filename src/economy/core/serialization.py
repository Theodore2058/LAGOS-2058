"""
Save / load system for EconomicState.

Serializes all numpy arrays into a compressed .npz archive, stores scalars
and list fields (policy_queue, construction_projects) as JSON strings
embedded in the archive, and preserves the RNG bit-generator state.
"""

from __future__ import annotations

import json
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from src.economy.core.types import (
    ConstructionProject,
    EconomicState,
    PolicyAction,
    SimConfig,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Every scalar field on EconomicState that we persist as a JSON blob.
_SCALAR_FIELDS: Dict[str, type] = {
    "game_month": int,
    "game_day": int,
    "game_week": int,
    "real_timestamp": float,
    "global_oil_price_usd": float,
    "global_cobalt_price_usd": float,
    "official_exchange_rate": float,
    "parallel_exchange_rate": float,
    "forex_reserves_usd": float,
    "monthly_import_bill_usd": float,
    "monthly_export_revenue_usd": float,
    "tax_rate_income": float,
    "tax_rate_corporate": float,
    "tax_rate_vat": float,
    "tax_rate_import_tariff": float,
    "minimum_wage": float,
    "bic_enforcement_intensity": float,
    "current_month_of_year": int,
    "is_rainy_season": bool,
    "rainfall_modifier": float,
    "price_history_cursor": int,
    "wafta_active": bool,
}

# Every numpy array field we persist directly in the .npz.
_ARRAY_FIELDS: List[str] = [
    "prices",
    "price_history",
    "inventories",
    "hoarded",
    "production_capacity",
    "actual_output",
    "factory_owner",
    "labor_pool",
    "labor_employed",
    "labor_informal",
    "wages",
    "strikes_active",
    "automation_level",
    "land_area",
    "land_total",
    "land_prices",
    "zoning_restriction",
    "bank_deposits",
    "bank_loans",
    "bank_bad_loans",
    "bank_confidence",
    "lending_rate",
    "budget_allocation",
    "budget_released",
    "corruption_leakage",
    "state_capacity",
    "desertification_loss",
    "alsahid_control",
    "alsahid_service_provision",
    "enhancement_adoption",
    "population",
    "voter_welfare",
    "voter_welfare_delta",
    "voter_salience",
    "voter_positions",
    "infra_road_quality",
    "infra_power_reliability",
    "infra_telecom_quality",
    "admin_zone",
]


def _policy_action_to_dict(pa: PolicyAction) -> Dict[str, Any]:
    return {
        "action_type": pa.action_type,
        "parameters": pa.parameters,
        "source": pa.source,
        "enacted_game_day": pa.enacted_game_day,
        "implementation_delay": pa.implementation_delay,
        "ministry_id": pa.ministry_id,
    }


def _dict_to_policy_action(d: Dict[str, Any]) -> PolicyAction:
    return PolicyAction(
        action_type=d["action_type"],
        parameters=d["parameters"],
        source=d["source"],
        enacted_game_day=d["enacted_game_day"],
        implementation_delay=d["implementation_delay"],
        ministry_id=d.get("ministry_id"),
    )


def _construction_project_to_dict(cp: ConstructionProject) -> Dict[str, Any]:
    return {
        "project_type": cp.project_type,
        "lga_id": cp.lga_id,
        "commodity_id": cp.commodity_id,
        "months_remaining": cp.months_remaining,
        "monthly_cost_naira": cp.monthly_cost_naira,
        "monthly_labor_demand": {str(k): v for k, v in cp.monthly_labor_demand.items()},
        "completion_effect": cp.completion_effect,
        "funded": cp.funded,
    }


def _dict_to_construction_project(d: Dict[str, Any]) -> ConstructionProject:
    return ConstructionProject(
        project_type=d["project_type"],
        lga_id=d["lga_id"],
        commodity_id=d.get("commodity_id"),
        months_remaining=d["months_remaining"],
        monthly_cost_naira=d["monthly_cost_naira"],
        monthly_labor_demand={int(k): v for k, v in d["monthly_labor_demand"].items()},
        completion_effect=d["completion_effect"],
        funded=d.get("funded", True),
    )


# ---------------------------------------------------------------------------
# Public API — save / load
# ---------------------------------------------------------------------------


def save_state(state: EconomicState, path: str) -> None:
    """Serialize *state* to a compressed ``.npz`` file at *path*.

    The archive contains:
    - one entry per numpy array field (keyed by field name)
    - ``__scalars__``  — JSON string of all scalar fields
    - ``__policy_queue__`` — JSON string of the policy queue
    - ``__construction_projects__`` — JSON string of construction projects
    - ``__rng_state__`` — JSON string of the RNG bit-generator state
    """

    arrays: Dict[str, np.ndarray] = {}

    # Collect numpy arrays (skip None).
    for name in _ARRAY_FIELDS:
        arr = getattr(state, name, None)
        if arr is not None:
            arrays[name] = arr

    # Scalars → JSON stored as a 1-D char array.
    scalars: Dict[str, Any] = {}
    for name in _SCALAR_FIELDS:
        scalars[name] = getattr(state, name)
    arrays["__scalars__"] = np.array([json.dumps(scalars)], dtype=object)

    # Dict fields → JSON.
    dict_fields = {
        "import_fulfillment": state.import_fulfillment,
        "platform_signals": state.platform_signals,
    }
    arrays["__dict_fields__"] = np.array([json.dumps(dict_fields)], dtype=object)

    # Policy queue → JSON.
    pq = [_policy_action_to_dict(pa) for pa in state.policy_queue]
    arrays["__policy_queue__"] = np.array([json.dumps(pq)], dtype=object)

    # Construction projects → JSON.
    cp = [_construction_project_to_dict(c) for c in state.construction_projects]
    arrays["__construction_projects__"] = np.array([json.dumps(cp)], dtype=object)

    # RNG state → JSON.
    rng_state = state.rng.bit_generator.state
    # Convert any numpy integers / arrays inside the state dict to plain
    # Python objects so that json.dumps can handle them.
    rng_state_serializable = _make_json_safe(rng_state)
    arrays["__rng_state__"] = np.array([json.dumps(rng_state_serializable)], dtype=object)

    np.savez_compressed(path, **arrays)


def load_state(path: str, config: SimConfig) -> EconomicState:
    """Deserialize an EconomicState from a compressed ``.npz`` file.

    Parameters
    ----------
    path:
        Path to the ``.npz`` file (the ``.npz`` extension is added
        automatically by numpy if missing).
    config:
        SimConfig is accepted for forward-compatibility (e.g. validating
        array shapes against expected dimensions).

    Returns
    -------
    EconomicState
        Fully reconstructed state with RNG, lists, and all arrays.
    """

    # Ensure the path ends with .npz for np.load.
    p = str(path)
    if not p.endswith(".npz"):
        p = p + ".npz"

    data = np.load(p, allow_pickle=True)

    state = EconomicState()

    # --- Scalars ---
    if "__scalars__" in data:
        scalars: Dict[str, Any] = json.loads(str(data["__scalars__"][0]))
        for name, typ in _SCALAR_FIELDS.items():
            if name in scalars:
                setattr(state, name, typ(scalars[name]))

    # --- Arrays ---
    for name in _ARRAY_FIELDS:
        if name in data:
            setattr(state, name, data[name])

    # --- Dict fields ---
    if "__dict_fields__" in data:
        dict_fields = json.loads(str(data["__dict_fields__"][0]))
        if "import_fulfillment" in dict_fields:
            state.import_fulfillment = dict_fields["import_fulfillment"]
        if "platform_signals" in dict_fields:
            state.platform_signals = dict_fields["platform_signals"]

    # --- Policy queue ---
    if "__policy_queue__" in data:
        pq_list = json.loads(str(data["__policy_queue__"][0]))
        state.policy_queue = [_dict_to_policy_action(d) for d in pq_list]

    # --- Construction projects ---
    if "__construction_projects__" in data:
        cp_list = json.loads(str(data["__construction_projects__"][0]))
        state.construction_projects = [_dict_to_construction_project(d) for d in cp_list]

    # --- RNG ---
    if "__rng_state__" in data:
        rng_state = json.loads(str(data["__rng_state__"][0]))
        rng_state = _restore_rng_state(rng_state)
        bg = np.random.PCG64()
        bg.state = rng_state
        state.rng = np.random.Generator(bg)
    else:
        state.rng = np.random.default_rng(config.SEED)

    data.close()
    return state


# ---------------------------------------------------------------------------
# Public API — snapshots
# ---------------------------------------------------------------------------


def state_to_snapshot(state: EconomicState) -> dict:
    """Convert *state* to a JSON-serialisable dict for API responses.

    NumPy arrays are reduced to summary statistics (mean, min, max, shape)
    to keep the payload small.
    """

    snap: Dict[str, Any] = {}

    # Scalars — pass through directly.
    for name in _SCALAR_FIELDS:
        snap[name] = getattr(state, name)

    # Arrays — summary stats only.
    for name in _ARRAY_FIELDS:
        arr = getattr(state, name, None)
        if arr is None:
            snap[name] = None
        else:
            snap[name] = {
                "shape": list(arr.shape),
                "dtype": str(arr.dtype),
                "mean": float(np.nanmean(arr)),
                "min": float(np.nanmin(arr)),
                "max": float(np.nanmax(arr)),
            }

    # Lists — counts only.
    snap["policy_queue_count"] = len(state.policy_queue)
    snap["construction_projects_count"] = len(state.construction_projects)

    return snap


def state_to_detailed_snapshot(state: EconomicState) -> dict:
    """Convert *state* to a fully detailed JSON-serialisable dict.

    NumPy arrays are included as nested Python lists (for export/download).
    """

    snap: Dict[str, Any] = {}

    # Scalars.
    for name in _SCALAR_FIELDS:
        snap[name] = getattr(state, name)

    # Arrays — full content as nested lists.
    for name in _ARRAY_FIELDS:
        arr = getattr(state, name, None)
        if arr is None:
            snap[name] = None
        else:
            snap[name] = {
                "shape": list(arr.shape),
                "dtype": str(arr.dtype),
                "data": arr.tolist(),
            }

    # Lists — full serialization.
    snap["policy_queue"] = [_policy_action_to_dict(pa) for pa in state.policy_queue]
    snap["construction_projects"] = [
        _construction_project_to_dict(cp) for cp in state.construction_projects
    ]

    return snap


# ---------------------------------------------------------------------------
# Internal — RNG state JSON helpers
# ---------------------------------------------------------------------------


def _make_json_safe(obj: Any) -> Any:
    """Recursively convert numpy types to plain Python for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_json_safe(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def _restore_rng_state(obj: Any) -> Any:
    """Recursively restore the RNG state dict from JSON-loaded data.

    The PCG64 bit-generator state expects ``s.state`` to contain a dict
    with ``state`` and ``inc`` as Python ints, and ``has_uint32`` /
    ``uinteger`` as ints.  JSON round-tripping preserves these as plain
    Python ints already, so we mainly need to ensure the top-level
    structure is correct.
    """
    if isinstance(obj, dict):
        return {k: _restore_rng_state(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_restore_rng_state(v) for v in obj]
    return obj
