"""
Tick scheduler — orchestrates the three economic clocks.

Phase 1: Market tick only (synchronous).
Full async implementation with production and structural ticks in later phases.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import numpy as np

from src.economy.core.assertions import check_all_invariants
from src.economy.core.types import EconomicState, SimConfig
from src.economy.systems.production import (
    apply_production_mutations,
    assert_production_valid,
    tick_production,
)
from src.economy.systems.trade import assert_market_valid, tick_market

logger = logging.getLogger(__name__)


@dataclass
class TickResult:
    """Result of a single tick execution."""
    tick_type: str           # "market", "production", "structural"
    tick_number: int
    game_day: int
    game_month: int
    elapsed_seconds: float
    invariant_warnings: List[str]


@dataclass
class TickScheduler:
    """
    Orchestrates the three economic clocks.

    Supports optional trade graph and trader agents for inter-LGA trade.
    """

    state: EconomicState
    config: SimConfig
    trade_graph: object = None   # Optional[TradeGraph]
    traders: object = None       # Optional[List[TraderAgent]]
    tick_count: int = 0
    market_tick_count: int = 0
    production_tick_count: int = 0
    structural_tick_count: int = 0
    history: List[TickResult] = field(default_factory=list)
    on_tick: Optional[Callable[[TickResult], None]] = None

    def run_market_tick(self) -> TickResult:
        """Execute one market clock tick."""
        t0 = time.time()

        # Run trader agents if available
        trader_net_supply = None
        if self.trade_graph is not None and self.traders is not None:
            from src.economy.systems.traders import tick_traders
            trader_net_supply = tick_traders(
                self.state, self.config, self.traders, self.trade_graph,
            )

        # Run market systems
        mkt_mut = tick_market(self.state, self.config, trader_net_supply)

        # Advance game time
        self.state.game_day += 1
        if self.state.game_day >= self.config.MARKET_TICKS_PER_MONTH:
            self.state.game_day = 0
            self.state.game_month += 1

        # Assertions
        assert_market_valid(self.state, mkt_mut)
        warnings = check_all_invariants(self.state)

        elapsed = time.time() - t0
        self.market_tick_count += 1
        self.tick_count += 1

        result = TickResult(
            tick_type="market",
            tick_number=self.tick_count,
            game_day=self.state.game_day,
            game_month=self.state.game_month,
            elapsed_seconds=elapsed,
            invariant_warnings=warnings,
        )
        self.history.append(result)
        if self.on_tick:
            self.on_tick(result)
        return result

    def run_production_tick(self) -> TickResult:
        """Execute one production tick (includes a market tick afterward)."""
        t0 = time.time()

        # Production
        prod_mut = tick_production(self.state, self.config)
        assert_production_valid(self.state, prod_mut)
        apply_production_mutations(self.state, prod_mut)

        # Advance game week
        self.state.game_week += 1

        # Market tick follows production
        mkt_result = self.run_market_tick()

        elapsed = time.time() - t0
        self.production_tick_count += 1

        warnings = check_all_invariants(self.state)

        result = TickResult(
            tick_type="production",
            tick_number=self.tick_count,
            game_day=self.state.game_day,
            game_month=self.state.game_month,
            elapsed_seconds=elapsed,
            invariant_warnings=warnings + mkt_result.invariant_warnings,
        )
        self.history.append(result)
        if self.on_tick:
            self.on_tick(result)
        return result

    def run_n_market_ticks(self, n: int, verbose: bool = False) -> list[TickResult]:
        """Run n market ticks sequentially."""
        results = []
        for i in range(n):
            result = self.run_market_tick()
            results.append(result)
            if verbose and (i + 1) % 10 == 0:
                logger.info(
                    "Tick %d/%d: day=%d month=%d prices=[%.0f,%.0f] inv_mean=%.1f (%.3fs)",
                    i + 1, n,
                    self.state.game_day,
                    self.state.game_month,
                    self.state.prices.min(),
                    self.state.prices.max(),
                    self.state.inventories.mean(),
                    result.elapsed_seconds,
                )
        return results

    def run_mixed_ticks(
        self, n_months: int = 1, verbose: bool = False,
    ) -> list[TickResult]:
        """
        Run a full month of ticks: 56 market ticks with 7 production ticks interleaved.

        Production ticks fire every 8 market ticks.
        """
        results = []
        market_ticks_per_prod = self.config.MARKET_TICKS_PER_MONTH // self.config.PRODUCTION_TICKS_PER_MONTH

        for month in range(n_months):
            for tick in range(self.config.MARKET_TICKS_PER_MONTH):
                if tick > 0 and tick % market_ticks_per_prod == 0:
                    result = self.run_production_tick()
                else:
                    result = self.run_market_tick()
                results.append(result)

            if verbose:
                logger.info(
                    "Month %d complete: prices=[%.0f,%.0f] inv=%.1f warnings=%d",
                    self.state.game_month,
                    self.state.prices.min(),
                    self.state.prices.max(),
                    self.state.inventories.mean(),
                    sum(len(r.invariant_warnings) for r in results[-56:]),
                )

        return results

    def get_price_summary(self) -> dict:
        """Return summary statistics for current prices."""
        return {
            "min": float(self.state.prices.min()),
            "max": float(self.state.prices.max()),
            "mean": float(self.state.prices.mean()),
            "median": float(np.median(self.state.prices)),
        }

    def get_inventory_summary(self) -> dict:
        """Return summary statistics for current inventories."""
        return {
            "min": float(self.state.inventories.min()),
            "max": float(self.state.inventories.max()),
            "mean": float(self.state.inventories.mean()),
            "total": float(self.state.inventories.sum()),
        }
