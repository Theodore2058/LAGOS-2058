"""WebSocket streaming for real-time economy tick updates."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import numpy as np

from src.economy.core.types import SimConfig
from src.economy.core.initialize import initialize_state
from src.economy.core.scheduler import TickScheduler
from src.economy.data.commodities import BASE_PRICES

router = APIRouter(tags=["economy-ws"])
logger = logging.getLogger(__name__)


def _tick_to_json(state, scheduler, tick_result) -> str:
    """Convert a tick result + state snapshot to a JSON message."""
    prices = state.prices
    mean_price = float(prices.mean())
    inflation = float((prices.mean(axis=0) / BASE_PRICES).mean() - 1.0)
    gdp = float((state.production_capacity * prices).sum())

    payload = {
        "type": "tick",
        "tick_type": tick_result.tick_type,
        "tick_number": tick_result.tick_number,
        "game_month": state.game_month,
        "game_day": state.game_day,
        "elapsed_seconds": round(tick_result.elapsed_seconds, 4),
        "warnings": len(tick_result.invariant_warnings),
        "snapshot": {
            "gdp_proxy": gdp,
            "mean_price_index": mean_price,
            "inflation_proxy": inflation,
            "total_employment": float(state.labor_employed.sum()),
            "total_population": float(state.population.sum()),
            "forex_reserves_usd": state.forex_reserves_usd,
            "official_rate": state.official_exchange_rate,
            "parallel_rate": state.parallel_exchange_rate,
            "oil_price": state.global_oil_price_usd,
            "cobalt_price": state.global_cobalt_price_usd,
            "bank_confidence": float(state.bank_confidence.mean()),
            "alsahid_control": float(state.alsahid_control.mean()),
        },
    }
    return json.dumps(payload)


@router.websocket("/ws/economy/stream")
async def economy_stream(websocket: WebSocket):
    """
    Stream economy simulation tick-by-tick over WebSocket.

    Client sends JSON commands:
        {"action": "start", "seed": 42}        — initialize simulation
        {"action": "run", "n_months": 3}        — run N months, streaming each tick
        {"action": "pause"}                     — pause streaming
        {"action": "stop"}                      — stop and close

    Server sends JSON messages:
        {"type": "tick", ...}                   — after each tick
        {"type": "status", "message": "..."}    — status updates
        {"type": "complete", "months": N}       — when run finishes
        {"type": "error", "message": "..."}     — on error
    """
    await websocket.accept()
    logger.info("WebSocket economy stream connected")

    state = None
    config = None
    scheduler = None
    paused = False

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error", "message": "Invalid JSON",
                }))
                continue

            action = msg.get("action", "")

            if action == "start":
                seed = msg.get("seed", 42)
                config = SimConfig(SEED=seed)
                state = initialize_state(config)
                scheduler = TickScheduler(state=state, config=config)
                paused = False
                await websocket.send_text(json.dumps({
                    "type": "status", "message": f"Simulation started (seed={seed})",
                }))

            elif action == "run":
                if state is None or scheduler is None or config is None:
                    await websocket.send_text(json.dumps({
                        "type": "error", "message": "No simulation running. Send 'start' first.",
                    }))
                    continue

                n_months = msg.get("n_months", 1)
                paused = False
                market_ticks_per_prod = (
                    config.MARKET_TICKS_PER_MONTH // config.PRODUCTION_TICKS_PER_MONTH
                )

                for month in range(n_months):
                    if paused:
                        break

                    for tick in range(config.MARKET_TICKS_PER_MONTH):
                        if paused:
                            break

                        if tick > 0 and tick % market_ticks_per_prod == 0:
                            result = scheduler.run_production_tick()
                        else:
                            result = scheduler.run_market_tick()

                        # Send tick update
                        await websocket.send_text(
                            _tick_to_json(state, scheduler, result)
                        )
                        # Yield to event loop so pause commands can be received
                        await asyncio.sleep(0)

                    if not paused:
                        # Structural tick at end of month
                        result = scheduler.run_structural_tick()
                        await websocket.send_text(
                            _tick_to_json(state, scheduler, result)
                        )

                if not paused:
                    await websocket.send_text(json.dumps({
                        "type": "complete",
                        "months": n_months,
                        "final_month": state.game_month,
                        "total_ticks": scheduler.tick_count,
                    }))

            elif action == "pause":
                paused = True
                await websocket.send_text(json.dumps({
                    "type": "status", "message": "Paused",
                }))

            elif action == "stop":
                await websocket.send_text(json.dumps({
                    "type": "status", "message": "Stopped",
                }))
                break

            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown action: {action}",
                }))

    except WebSocketDisconnect:
        logger.info("WebSocket economy stream disconnected")
