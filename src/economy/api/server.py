"""
FastAPI server for the economic simulator.

Provides REST endpoints for:
  - Running simulation ticks
  - Querying state snapshots and diagnostics
  - Applying policy actions
  - Running what-if scenarios
  - Streaming tick results via WebSocket
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from src.economy.core.types import EconomicState, PolicyAction, SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.core.serialization import state_to_snapshot, save_state, load_state
from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_gini_coefficient,
    compute_employment_stats,
    compute_trade_balance,
    compute_sector_output,
    compute_crisis_indicators,
)
from src.economy.diagnostics.dutch_disease import compute_dutch_disease_index

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

_state: Optional[EconomicState] = None
_config: Optional[SimConfig] = None
_scheduler: Optional[TickScheduler] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize simulation on startup."""
    global _state, _config, _scheduler
    _config = SimConfig()
    _state = initialize_state(_config)
    _scheduler = TickScheduler(state=_state, config=_config)
    logger.info("Economic simulator initialized: %d LGAs, %d commodities",
                _config.N_LGAS, _config.N_COMMODITIES)
    yield
    logger.info("Shutting down economic simulator")


app = FastAPI(
    title="LAGOS-2058 Economic Simulator",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------

class PolicyRequest(BaseModel):
    action_type: str
    parameters: Dict[str, Any] = {}
    source: str = "api"
    implementation_delay: int = 0


class SimulateRequest(BaseModel):
    n_months: int = 1


class WhatIfRequest(BaseModel):
    scenario_name: str
    disruptions: Dict[str, Any]
    n_months: int = 3


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/status")
async def get_status():
    """Current simulation status."""
    return {
        "game_month": _state.game_month,
        "game_day": _state.game_day,
        "n_lgas": _config.N_LGAS,
        "n_commodities": _config.N_COMMODITIES,
    }


@app.get("/snapshot")
async def get_snapshot():
    """Current state snapshot (summary statistics)."""
    return state_to_snapshot(_state)


@app.get("/diagnostics")
async def get_diagnostics():
    """Full diagnostic dashboard."""
    emp = compute_employment_stats(_state, _config)
    trade = compute_trade_balance(_state, _config)
    sectors = compute_sector_output(_state, _config)
    crises = compute_crisis_indicators(_state, _config)
    dd = compute_dutch_disease_index(_state, _config)

    return {
        "gdp_proxy": compute_gdp_proxy(_state, _config),
        "inflation": compute_inflation_proxy(_state, _config),
        "gini": compute_gini_coefficient(_state),
        "employment": emp,
        "trade_balance": trade,
        "sector_output": sectors,
        "crisis_indicators": crises,
        "dutch_disease": {
            "overall_index": dd.overall_index,
            "export_concentration": dd.export_concentration,
            "manufacturing_share": dd.manufacturing_share,
            "real_exchange_rate": dd.real_exchange_rate,
            "non_oil_competitiveness": dd.non_oil_competitiveness,
            "oil_revenue_dependency": dd.oil_revenue_dependency,
        },
    }


@app.post("/simulate")
async def simulate(request: SimulateRequest):
    """Run simulation for N months."""
    if request.n_months < 1 or request.n_months > 24:
        raise HTTPException(400, "n_months must be 1-24")

    results = _scheduler.run_mixed_ticks(n_months=request.n_months)

    return {
        "months_simulated": request.n_months,
        "ticks_executed": len(results),
        "game_month": _state.game_month,
        "game_day": _state.game_day,
    }


@app.post("/policy")
async def apply_policy(request: PolicyRequest):
    """Enqueue a policy action."""
    from src.economy.systems.government import process_policy

    policy = PolicyAction(
        action_type=request.action_type,
        parameters=request.parameters,
        source=request.source,
        enacted_game_day=_state.game_day,
        implementation_delay=request.implementation_delay,
    )

    if request.implementation_delay == 0:
        process_policy(_state, policy, _config)
        return {"status": "applied", "action": request.action_type}
    else:
        _state.policy_queue.append(policy)
        return {"status": "queued", "action": request.action_type,
                "delay": request.implementation_delay}


@app.get("/prices")
async def get_prices():
    """Current mean prices by commodity."""
    from src.economy.data.commodities import COMMODITIES
    return {
        c.name: float(_state.prices[:, c.id].mean())
        for c in COMMODITIES
    }


@app.get("/prices/{commodity_id}")
async def get_commodity_price(commodity_id: int):
    """Price distribution for a specific commodity."""
    if commodity_id < 0 or commodity_id >= _config.N_COMMODITIES:
        raise HTTPException(404, f"Commodity {commodity_id} not found")

    prices = _state.prices[:, commodity_id]
    return {
        "commodity_id": commodity_id,
        "mean": float(prices.mean()),
        "min": float(prices.min()),
        "max": float(prices.max()),
        "std": float(prices.std()),
    }


@app.post("/reset")
async def reset():
    """Reset simulation to initial state."""
    global _state, _scheduler
    _state = initialize_state(_config)
    _scheduler = TickScheduler(state=_state, config=_config)
    return {"status": "reset", "game_month": 0}


@app.post("/save")
async def save(path: str = "state_save"):
    """Save current state to disk."""
    save_state(_state, path)
    return {"status": "saved", "path": path}


@app.post("/load")
async def load(path: str = "state_save"):
    """Load state from disk."""
    global _state, _scheduler
    _state = load_state(path, _config)
    _scheduler = TickScheduler(state=_state, config=_config)
    return {"status": "loaded", "path": path, "game_month": _state.game_month}


# ---------------------------------------------------------------------------
# WebSocket streaming
# ---------------------------------------------------------------------------

@app.websocket("/ws/simulate")
async def websocket_simulate(websocket: WebSocket):
    """Stream tick results via WebSocket.

    Send JSON: {"n_months": 3} to start simulation.
    Receives tick results as they complete.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            n_months = data.get("n_months", 1)

            for month in range(n_months):
                # Run one month of ticks
                results = _scheduler.run_mixed_ticks(n_months=1)

                # Send monthly update
                emp = compute_employment_stats(_state, _config)
                await websocket.send_json({
                    "type": "tick_update",
                    "month": _state.game_month,
                    "ticks": len(results),
                    "gdp": compute_gdp_proxy(_state, _config),
                    "inflation": compute_inflation_proxy(_state, _config),
                    "employment_rate": emp["employment_rate"],
                    "forex_reserves": _state.forex_reserves_usd,
                })

            await websocket.send_json({"type": "complete", "months": n_months})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
