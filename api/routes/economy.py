"""Economy simulation API routes."""
from __future__ import annotations

import copy
import time
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

import numpy as np

from api.schemas.economy import (
    BankingSummaryResponse,
    EconomyStatusResponse,
    LaborSummaryResponse,
    LGADetailResponse,
    PriceSummaryResponse,
    PolicyRequest,
    SimControlRequest,
    SimControlResponse,
    WhatIfRequest,
    WhatIfResponse,
)
from src.economy.core.types import EconomicState, PolicyAction, SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import BASE_PRICES, COMMODITIES

router = APIRouter(prefix="/api/economy", tags=["economy"])
logger = logging.getLogger(__name__)

# --- In-memory simulation state ---
# These are module-level singletons managed by start/reset endpoints.
_state: Optional[EconomicState] = None
_config: Optional[SimConfig] = None
_scheduler: Optional[TickScheduler] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_status(
    state: EconomicState,
    config: SimConfig,
    scheduler: TickScheduler,
) -> EconomyStatusResponse:
    """Convert the current simulation state into a status response."""
    prices = state.prices  # (774, 36)
    mean_prices = float(prices.mean())
    inflation_proxy = float((prices.mean(axis=0) / BASE_PRICES).mean() - 1.0)

    # V3 mode: use sell_orders for GDP; legacy: production_capacity
    if hasattr(state, 'sell_orders') and state.sell_orders is not None and state.sell_orders.sum() > 0:
        gdp_proxy = float((state.sell_orders * prices).sum())
    else:
        gdp_proxy = float((state.production_capacity * prices).sum())
    total_employment = float(state.labor_employed.sum())
    total_population = float(state.population.sum())

    return EconomyStatusResponse(
        game_month=state.game_month,
        game_day=state.game_day,
        tick_count=scheduler.tick_count,
        gdp_proxy=gdp_proxy,
        total_employment=total_employment,
        total_population=total_population,
        forex_reserves_usd=state.forex_reserves_usd,
        official_exchange_rate=state.official_exchange_rate,
        parallel_exchange_rate=state.parallel_exchange_rate,
        oil_price_usd=state.global_oil_price_usd,
        cobalt_price_usd=state.global_cobalt_price_usd,
        mean_price_index=mean_prices,
        inflation_proxy=inflation_proxy,
        total_bank_deposits=float(state.bank_deposits.sum()),
        total_bank_loans=float(state.bank_loans.sum()),
        mean_bank_confidence=float(state.bank_confidence.mean()),
        is_rainy_season=state.is_rainy_season,
        alsahid_mean_control=float(state.alsahid_control.mean()),
    )


def _require_running() -> tuple[EconomicState, SimConfig, TickScheduler]:
    """Return the active simulation objects or raise 404."""
    if _state is None or _config is None or _scheduler is None:
        raise HTTPException(
            status_code=404,
            detail="No simulation running. POST /api/economy/start first.",
        )
    return _state, _config, _scheduler


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/start", response_model=EconomyStatusResponse)
def start_simulation(seed: Optional[int] = Query(None)):
    """Initialize a new economy simulation."""
    global _state, _config, _scheduler

    _config = SimConfig()
    if seed is not None:
        _config.SEED = seed

    _state = initialize_state(config=_config)
    _scheduler = TickScheduler(state=_state, config=_config)

    logger.info("Economy simulation started (seed=%s)", _config.SEED)
    return _build_status(_state, _config, _scheduler)


@router.get("/status", response_model=EconomyStatusResponse)
def get_status():
    """Return the current economy status."""
    state, config, scheduler = _require_running()
    return _build_status(state, config, scheduler)


@router.post("/tick", response_model=SimControlResponse)
def run_tick(req: SimControlRequest):
    """Run the simulation for *n_months* months."""
    state, config, scheduler = _require_running()

    if req.seed is not None:
        state.rng = np.random.default_rng(req.seed)

    t0 = time.time()
    results = scheduler.run_mixed_ticks(n_months=req.n_months, verbose=False)
    elapsed = time.time() - t0

    warnings_count = sum(len(r.invariant_warnings) for r in results)

    return SimControlResponse(
        months_run=req.n_months,
        ticks_executed=len(results),
        final_month=state.game_month,
        warnings_count=warnings_count,
        elapsed_seconds=round(elapsed, 4),
    )


@router.get("/prices", response_model=List[PriceSummaryResponse])
def get_prices():
    """Return price summaries for all 36 commodities."""
    state, config, scheduler = _require_running()
    prices = state.prices  # (774, 36)

    out: list[PriceSummaryResponse] = []
    for cdef in COMMODITIES:
        c = cdef.id
        col = prices[:, c]
        mean_p = float(col.mean())
        base_p = float(BASE_PRICES[c])
        out.append(PriceSummaryResponse(
            commodity_id=c,
            commodity_name=cdef.name,
            mean_price=mean_p,
            min_price=float(col.min()),
            max_price=float(col.max()),
            base_price=base_p,
            price_ratio=mean_p / base_p if base_p > 0 else 0.0,
        ))
    return out


@router.get("/labor", response_model=List[LaborSummaryResponse])
def get_labor():
    """Return labor summaries for all 4 skill tiers."""
    state, config, scheduler = _require_running()

    out: list[LaborSummaryResponse] = []
    for tier in range(config.N_SKILL_TIERS):
        pool = float(state.labor_pool[:, tier].sum())
        employed = float(state.labor_employed[:, tier].sum())
        informal = float(state.labor_informal[:, tier].sum())
        emp_rate = employed / pool if pool > 0 else 0.0
        mean_wage = float(state.wages[:, tier].mean())
        out.append(LaborSummaryResponse(
            skill_tier=tier,
            skill_name=config.SKILL_TIER_NAMES[tier],
            total_pool=pool,
            total_employed=employed,
            total_informal=informal,
            employment_rate=round(emp_rate, 4),
            mean_wage=round(mean_wage, 2),
        ))
    return out


@router.get("/banking", response_model=List[BankingSummaryResponse])
def get_banking():
    """Return banking summaries for all 8 administrative zones."""
    state, config, scheduler = _require_running()

    out: list[BankingSummaryResponse] = []
    for z in range(config.N_ADMIN_ZONES):
        out.append(BankingSummaryResponse(
            zone_id=z,
            deposits=float(state.bank_deposits[z]),
            loans=float(state.bank_loans[z]),
            bad_loans=float(state.bank_bad_loans[z]),
            confidence=float(state.bank_confidence[z]),
            lending_rate=float(state.lending_rate[z]),
        ))
    return out


@router.get("/lga/{lga_id}", response_model=LGADetailResponse)
def get_lga(lga_id: int):
    """Return detailed economic data for a single LGA."""
    state, config, scheduler = _require_running()

    if not (0 <= lga_id < config.N_LGAS):
        raise HTTPException(
            status_code=400,
            detail=f"lga_id must be between 0 and {config.N_LGAS - 1}",
        )

    # Top 5 commodities by price in this LGA
    lga_prices = state.prices[lga_id]  # (36,)
    top5_ids = np.argsort(lga_prices)[-5:][::-1]
    prices_top5 = [
        {
            "commodity_id": int(cid),
            "commodity_name": COMMODITIES[cid].name,
            "price": float(lga_prices[cid]),
        }
        for cid in top5_ids
    ]

    return LGADetailResponse(
        lga_id=lga_id,
        population=float(state.population[lga_id]),
        wages=[float(state.wages[lga_id, t]) for t in range(config.N_SKILL_TIERS)],
        employment=[float(state.labor_employed[lga_id, t]) for t in range(config.N_SKILL_TIERS)],
        prices_top5=prices_top5,
        land_area=[float(state.land_area[lga_id, t]) for t in range(config.N_LAND_TYPES)],
        land_prices=[float(state.land_prices[lga_id, t]) for t in range(config.N_LAND_TYPES)],
        road_quality=float(state.infra_road_quality[lga_id]),
        power_reliability=float(state.infra_power_reliability[lga_id]),
        alsahid_control=float(state.alsahid_control[lga_id]),
    )


@router.post("/policy")
def enqueue_policy(req: PolicyRequest):
    """Enqueue a policy action for processing at the next structural tick."""
    state, config, scheduler = _require_running()

    action = PolicyAction(
        action_type=req.action_type,
        parameters=req.parameters,
        source=req.source,
        enacted_game_day=state.game_day,
        implementation_delay=req.implementation_delay,
    )
    state.policy_queue.append(action)
    logger.info("Policy enqueued: %s (source=%s)", req.action_type, req.source)
    return {"status": "enqueued"}


@router.post("/what-if", response_model=WhatIfResponse)
def run_what_if(req: WhatIfRequest):
    """
    Run a what-if scenario.

    Deep-copies the current state, applies the requested policies,
    runs n_months, and compares to baseline.
    """
    state, config, scheduler = _require_running()

    # Snapshot the baseline status before the scenario
    baseline = _build_status(state, config, scheduler)

    # Deep-copy the state for the scenario branch
    scenario_state = copy.deepcopy(state)
    if req.seed is not None:
        scenario_state.rng = np.random.default_rng(req.seed)

    # Enqueue the what-if policies
    for pol in req.policies:
        action = PolicyAction(
            action_type=pol.action_type,
            parameters=pol.parameters,
            source=pol.source,
            enacted_game_day=scenario_state.game_day,
            implementation_delay=pol.implementation_delay,
        )
        scenario_state.policy_queue.append(action)

    # Run the scenario
    scenario_scheduler = TickScheduler(state=scenario_state, config=config)
    scenario_scheduler.run_mixed_ticks(n_months=req.n_months, verbose=False)

    scenario = _build_status(scenario_state, config, scenario_scheduler)

    return WhatIfResponse(
        baseline=baseline,
        scenario=scenario,
        delta_gdp=scenario.gdp_proxy - baseline.gdp_proxy,
        delta_employment=scenario.total_employment - baseline.total_employment,
        delta_forex_reserves=scenario.forex_reserves_usd - baseline.forex_reserves_usd,
        delta_inflation=scenario.inflation_proxy - baseline.inflation_proxy,
    )


@router.post("/save")
def save_state(path: str = Query("economy_save.npz")):
    """Save the current simulation state to disk."""
    state, config, scheduler = _require_running()

    try:
        from src.economy.core import serialization
        serialization.save_state(state, path)
    except (ImportError, AttributeError):
        # Fallback: save raw numpy arrays
        arrays = {}
        for attr_name in dir(state):
            if attr_name.startswith("_"):
                continue
            val = getattr(state, attr_name)
            if isinstance(val, np.ndarray):
                arrays[attr_name] = val
        arrays["__game_month"] = np.array([state.game_month])
        arrays["__game_day"] = np.array([state.game_day])
        arrays["__game_week"] = np.array([state.game_week])
        arrays["__official_exchange_rate"] = np.array([state.official_exchange_rate])
        arrays["__parallel_exchange_rate"] = np.array([state.parallel_exchange_rate])
        arrays["__forex_reserves_usd"] = np.array([state.forex_reserves_usd])
        arrays["__global_oil_price_usd"] = np.array([state.global_oil_price_usd])
        arrays["__global_cobalt_price_usd"] = np.array([state.global_cobalt_price_usd])
        np.savez_compressed(path, **arrays)

    logger.info("State saved to %s", path)
    return {"status": "saved", "path": path}


@router.post("/load")
def load_state(path: str = Query("economy_save.npz")):
    """Load simulation state from disk."""
    global _state, _config, _scheduler

    if _config is None:
        _config = SimConfig()

    try:
        from src.economy.core import serialization
        _state = serialization.load_state(path, _config)
    except (ImportError, AttributeError):
        # Fallback: load from npz
        data = np.load(path, allow_pickle=False)
        _state = EconomicState()
        for key in data.files:
            if key.startswith("__"):
                scalar_name = key[2:]
                setattr(_state, scalar_name, float(data[key][0]))
            else:
                setattr(_state, key, data[key])
        # Restore integer fields
        _state.game_month = int(_state.game_month)
        _state.game_day = int(_state.game_day)
        _state.game_week = int(_state.game_week)
        _state.rng = np.random.default_rng(_config.SEED)

    _scheduler = TickScheduler(state=_state, config=_config)

    logger.info("State loaded from %s", path)
    return {"status": "loaded", "path": path}


@router.post("/reset")
def reset_simulation():
    """Reset the simulation to its initial state."""
    global _state, _config, _scheduler

    _state = None
    _config = None
    _scheduler = None

    logger.info("Economy simulation reset")
    return {"status": "reset"}
