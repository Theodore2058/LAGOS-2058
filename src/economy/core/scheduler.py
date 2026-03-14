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
from src.economy.systems.order_book import tick_market_orderbook
from src.economy.systems.buildings_production import tick_building_production
from src.economy.systems.pops import (
    tick_pop_income,
    update_pop_employment,
    update_standard_of_living,
)
from src.economy.systems.sentiment import tick_sentiment

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

    @property
    def _use_order_book(self) -> bool:
        """True when buildings and pops are initialized — use order-book clearing."""
        return (
            self.state.n_buildings > 0
            and self.state.building_type_ids is not None
            and self.state.pop_income is not None
        )

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

        # Run market systems — order-book or legacy
        if self._use_order_book:
            mkt_mut = tick_market_orderbook(
                self.state, self.config, trader_net_supply,
            )
        else:
            mkt_mut = tick_market(self.state, self.config, trader_net_supply)

        # Lightweight per-tick sentiment update
        if self.state.pop_sentiment is not None:
            tick_sentiment(self.state, self.config)

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
        """Execute one production tick (includes labor + market afterward)."""
        t0 = time.time()

        # Production — building-based or legacy
        if self._use_order_book:
            prod_mut = tick_building_production(self.state, self.config)
        else:
            prod_mut = tick_production(self.state, self.config)
        assert_production_valid(self.state, prod_mut)
        apply_production_mutations(self.state, prod_mut)

        # Labor market
        from src.economy.systems.labor import tick_labor, apply_labor_mutations, evaluate_strikes
        labor_mut = tick_labor(self.state, self.config)
        strikes_active, _ = evaluate_strikes(self.state, self.config)
        apply_labor_mutations(self.state, labor_mut, strikes_active)

        # Banking
        from src.economy.systems.banking import tick_banking, apply_banking_mutations
        bank_mut = tick_banking(self.state, self.config)
        apply_banking_mutations(self.state, bank_mut)

        # Pop economic updates (when pops are initialized)
        if self.state.pop_income is not None:
            update_pop_employment(self.state, self.config)
            tick_pop_income(self.state, self.config)
            update_standard_of_living(self.state, self.config)

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

    def run_structural_tick(self) -> TickResult:
        """Execute one structural tick (monthly): all macro systems."""
        t0 = time.time()

        from src.economy.systems.forex import tick_forex, apply_forex_mutations
        from src.economy.systems.climate import tick_climate, apply_climate_mutations
        from src.economy.systems.demographics import tick_demographics, apply_demographic_mutations
        from src.economy.systems.land import tick_land, apply_land_mutations
        from src.economy.systems.government import tick_government
        from src.economy.systems.alsahid import tick_alsahid, apply_alsahid_mutations
        from src.economy.systems.enhancement import tick_enhancement, apply_enhancement_diffusion

        # Snapshot population for migration tracking in election feedback
        if self.state.population is not None:
            self.state._prev_population = self.state.population.copy()

        # Government (policy queue, budget, corruption, infrastructure)
        tick_government(self.state, self.config)

        # Forex
        forex_mut = tick_forex(self.state, self.config)
        apply_forex_mutations(self.state, forex_mut)

        # Climate
        climate_mut = tick_climate(self.state, self.config)
        apply_climate_mutations(self.state, climate_mut)

        # Al-Shahid parallel economy
        alsahid_mut = tick_alsahid(self.state, self.config)
        apply_alsahid_mutations(self.state, alsahid_mut)

        # Demographics
        demo_mut = tick_demographics(self.state, self.config)
        apply_demographic_mutations(self.state, demo_mut)

        # Land market
        land_mut = tick_land(self.state, self.config)
        apply_land_mutations(self.state, land_mut)

        # Enhancement technology diffusion
        new_adoption = tick_enhancement(self.state, self.config)
        apply_enhancement_diffusion(self.state, new_adoption)

        # Cache election feedback on state (lazy: only computed at structural tick)
        from src.economy.systems.election_feedback import compute_election_feedback
        fb = compute_election_feedback(self.state, self.config)
        self.state.voter_welfare = fb.welfare_scores
        self.state.voter_salience = fb.salience_shifts
        self.state.voter_positions = fb.position_shifts

        elapsed = time.time() - t0
        self.structural_tick_count += 1
        self.tick_count += 1

        warnings = check_all_invariants(self.state)

        result = TickResult(
            tick_type="structural",
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

            # Structural tick at end of each month
            structural_result = self.run_structural_tick()
            results.append(structural_result)

            if verbose:
                logger.info(
                    "Month %d complete: prices=[%.0f,%.0f] inv=%.1f warnings=%d",
                    self.state.game_month,
                    self.state.prices.min(),
                    self.state.prices.max(),
                    self.state.inventories.mean(),
                    sum(len(r.invariant_warnings) for r in results[-57:]),
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
