"""
Foreign Exchange System — runs once per structural tick (monthly).

Computes oil/cobalt export revenue, import bills, forex reserve dynamics,
official/parallel exchange rates, and global commodity price shocks.
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import (
    EconomicState,
    ForexMutations,
    IMPORT_DEPENDENCIES,
    SimConfig,
)

from src.economy.data.commodity_ids import CRUDE_OIL, NATURAL_GAS, COBALT_ORE

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Main tick
# ---------------------------------------------------------------------------

def tick_forex(state: EconomicState, config: SimConfig) -> ForexMutations:
    """
    Execute one forex tick (monthly structural tick).

    Pipeline:
        1. Update global commodity prices (random walk + crash events)
        2. Compute export revenue (oil + cobalt) at official rate
        3. Compute import bill at parallel rate
        4. Update forex reserves (+ exports - imports - drain)
        5. Update parallel exchange rate based on reserve pressure
        6. Compute rate-gap corruption drain
    """
    rng = state.rng

    # ------------------------------------------------------------------
    # 1. Global commodity price shocks
    # ------------------------------------------------------------------
    oil_price_new = _step_commodity_price(
        current_price=state.global_oil_price_usd,
        volatility=config.OIL_PRICE_VOLATILITY,
        crash_prob=config.COMMODITY_CRASH_PROBABILITY,
        crash_mag=config.COMMODITY_CRASH_MAGNITUDE,
        floor=10.0,
        rng=rng,
    )
    cobalt_price_new = _step_commodity_price(
        current_price=state.global_cobalt_price_usd,
        volatility=config.COBALT_PRICE_VOLATILITY,
        crash_prob=config.COMMODITY_CRASH_PROBABILITY,
        crash_mag=config.COMMODITY_CRASH_MAGNITUDE,
        floor=5_000.0,
        rng=rng,
    )

    # ------------------------------------------------------------------
    # 2. Export revenue (oil + gas + cobalt)
    # ------------------------------------------------------------------
    # Capacity units are abstract (~368 oil, ~295 gas, ~8 cobalt).
    # Per-commodity multipliers convert to real output volumes:
    #   Oil: 368 cap * 160K = 58.9M bbl/month ≈ 2M bbl/day
    #   Gas: 295 cap * 130K = 38.3M units (LNG exports ≈ $490M/mo)
    #   Cobalt: 8 cap * 600 = 4,920 tonnes/month
    # Normal: oil $5.0B + gas $0.49B + cobalt $0.17B ≈ $5.7B/month
    # Oil crash ($20): oil $1.2B + gas $0.12B + cobalt $0.17B ≈ $1.5B
    _OIL_OUTPUT_MULT = 160_000.0
    _GAS_OUTPUT_MULT = 130_000.0
    _COBALT_OUTPUT_MULT = 600.0

    if (
        hasattr(state, 'sell_orders')
        and state.sell_orders is not None
        and state.sell_orders.sum() > 0
    ):
        oil_output = state.sell_orders[:, CRUDE_OIL].sum()
        gas_output = state.sell_orders[:, NATURAL_GAS].sum()
        cobalt_output = state.sell_orders[:, COBALT_ORE].sum()
    else:
        oil_output = state.production_capacity[:, CRUDE_OIL].sum()
        gas_output = state.production_capacity[:, NATURAL_GAS].sum()
        cobalt_output = state.production_capacity[:, COBALT_ORE].sum()

    # LNG price tracks oil (~15% of oil price per unit)
    lng_price_usd = oil_price_new * 0.15

    export_revenue_usd = (
        oil_output * _OIL_OUTPUT_MULT * oil_price_new
        + gas_output * _GAS_OUTPUT_MULT * lng_price_usd
        + cobalt_output * _COBALT_OUTPUT_MULT * cobalt_price_new
    )

    # ------------------------------------------------------------------
    # 3. Import bill (paid at parallel rate)
    # ------------------------------------------------------------------
    import_bill_usd = _compute_import_bill(state, config)

    # ------------------------------------------------------------------
    # 4. Forex reserves
    # ------------------------------------------------------------------
    # Structural drain: central bank intervention, debt service, etc.
    reserve_drain = (
        state.forex_reserves_usd * config.RESERVE_DRAIN_RATE / 12.0
    )

    reserves_new = (
        state.forex_reserves_usd
        + export_revenue_usd
        - import_bill_usd
        - reserve_drain
    )
    reserves_new = max(reserves_new, 0.0)

    # ------------------------------------------------------------------
    # 5. Exchange rates
    # ------------------------------------------------------------------
    # Official rate is policy-set (sticky) — unchanged unless a policy
    # action explicitly modifies it.
    official_rate_new = state.official_exchange_rate

    parallel_rate_new = _update_parallel_rate(
        official_rate=official_rate_new,
        current_parallel=state.parallel_exchange_rate,
        base_premium=config.PARALLEL_RATE_PREMIUM_BASE,
        reserves_usd=reserves_new,
        monthly_imports=import_bill_usd,
        reserve_months_target=config.FOREX_RESERVE_MONTHS,
        rng=rng,
    )

    # ------------------------------------------------------------------
    # 6. Rate-gap corruption drain
    # ------------------------------------------------------------------
    safe_official = max(official_rate_new, 100.0)  # floor: prevent div-by-zero
    rate_gap = parallel_rate_new / safe_official - 1.0
    # Round-tripping profits siphoned by connected elites: proportional
    # to the gap and to total import volume.
    rate_gap_corruption_drain = max(rate_gap, 0.0) * import_bill_usd * 0.05

    logger.debug(
        "forex tick: exports=%.1fM imports=%.1fM reserves=%.1fM "
        "oil=$%.1f cobalt=$%.0f official=%.0f parallel=%.0f "
        "corruption_drain=%.1fM",
        export_revenue_usd / 1e6, import_bill_usd / 1e6, reserves_new / 1e6,
        oil_price_new, cobalt_price_new,
        official_rate_new, parallel_rate_new,
        rate_gap_corruption_drain / 1e6,
    )

    return ForexMutations(
        official_rate_new=official_rate_new,
        parallel_rate_new=parallel_rate_new,
        reserves_new=reserves_new,
        export_revenue=export_revenue_usd,
        import_bill=import_bill_usd,
        rate_gap_corruption_drain=rate_gap_corruption_drain,
        oil_price_new=oil_price_new,
        cobalt_price_new=cobalt_price_new,
    )


# ---------------------------------------------------------------------------
# Apply mutations
# ---------------------------------------------------------------------------

def apply_forex_mutations(
    state: EconomicState, mutations: ForexMutations,
) -> None:
    """Write forex tick results back into the central state."""
    state.official_exchange_rate = mutations.official_rate_new
    state.parallel_exchange_rate = mutations.parallel_rate_new
    state.forex_reserves_usd = mutations.reserves_new
    state.monthly_export_revenue_usd = mutations.export_revenue
    state.monthly_import_bill_usd = mutations.import_bill
    state.global_oil_price_usd = mutations.oil_price_new
    state.global_cobalt_price_usd = mutations.cobalt_price_new

    # Update import fulfillment based on reserves and WAFTA status
    _update_import_fulfillment(state)


def _update_import_fulfillment(state: EconomicState) -> None:
    """
    Compute import fulfillment ratios based on forex reserves and policy.

    When reserves are low, imports are rationed. WAFTA cancellation
    directly reduces fulfillment of china_wafta-sourced imports.
    """
    # Reserve adequacy: ratio of reserves to monthly import bill
    if state.monthly_import_bill_usd > 0:
        reserve_months = state.forex_reserves_usd / state.monthly_import_bill_usd
    else:
        reserve_months = 12.0

    # Base fulfillment from reserves: full above 6 months, linear decline below
    reserve_ratio = min(reserve_months / 6.0, 1.0)
    reserve_ratio = max(reserve_ratio, 0.1)  # minimum 10% even in crisis

    for name, dep in IMPORT_DEPENDENCIES.items():
        base = reserve_ratio

        # WAFTA-vulnerable imports: if WAFTA cancelled, cap at 50%
        if dep.get("vulnerability") == "wafta_cancellation" and not state.wafta_active:
            base = min(base, 0.5)

        # Forex-crisis-vulnerable imports: reduce more aggressively
        if dep.get("vulnerability") == "forex_crisis":
            base *= reserve_ratio  # double penalty

        state.import_fulfillment[name] = float(np.clip(base, 0.05, 1.0))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _step_commodity_price(
    current_price: float,
    volatility: float,
    crash_prob: float,
    crash_mag: float,
    floor: float,
    rng: np.random.Generator,
) -> float:
    """
    Geometric random walk with rare crash events.

    ln(P_{t+1}) = ln(P_t) + N(0, sigma)  -- normal drift
    With probability ``crash_prob``, price drops by ``crash_mag`` fraction.
    """
    # Normal monthly move
    log_return = rng.normal(0.0, volatility)

    # Crash event (Poisson-style rare shock)
    if rng.random() < crash_prob:
        log_return -= crash_mag  # sharp negative shock
        logger.info(
            "Commodity crash event: %.1f%% drop applied (price was %.2f)",
            crash_mag * 100,
            current_price,
        )

    new_price = current_price * np.exp(log_return)
    return float(max(new_price, floor))


def _compute_import_bill(
    state: EconomicState, config: SimConfig,
) -> float:
    """
    Sum USD import costs across the four IMPORT_DEPENDENCIES categories.

    Volume for production-linked imports is driven by the production
    capacity of commodities that require that input, scaled by
    ``units_per_output``.  Luxury consumer goods use a heuristic based
    on the official/parallel rate gap (expensive forex suppresses demand).
    """
    total_usd = 0.0

    for name, dep in IMPORT_DEPENDENCIES.items():
        price_usd: float = dep["price_usd"]
        units_per_output: float = dep["units_per_output"]
        required_by: list = dep["required_by"]

        if not required_by or units_per_output <= 0.0:
            # Luxury goods: demand inversely proportional to forex cost
            if name == "luxury_consumer_goods":
                base_demand = 50_000.0  # baseline monthly units
                forex_penalty = state.official_exchange_rate / max(
                    state.parallel_exchange_rate, 1.0,
                )
                volume = base_demand * forex_penalty
            else:
                continue
        else:
            # Production-linked: sum capacity of downstream commodities
            # multiplied by the per-unit import requirement.
            volume = 0.0
            for cid in required_by:
                volume += (
                    state.production_capacity[:, cid].sum() * units_per_output
                )

        total_usd += volume * price_usd

    # Apply import tariff (increases naira cost, reducing effective volume)
    # Tariff revenue goes to government, but the forex cost remains
    total_usd *= (1.0 + state.tax_rate_import_tariff)

    # Scale abstract capacity-based volumes to real-world import costs.
    # Nigeria-2058 target: ~$3.5B/month imports (machinery, chemicals,
    # consumer goods, refined products).
    _IMPORT_MULTIPLIER = 120.0
    total_usd *= _IMPORT_MULTIPLIER

    return total_usd


def _update_parallel_rate(
    official_rate: float,
    current_parallel: float,
    base_premium: float,
    reserves_usd: float,
    monthly_imports: float,
    reserve_months_target: float,
    rng: np.random.Generator,
) -> float:
    """
    Parallel rate adjusts based on supply/demand pressure.

    When reserves cover fewer months of imports than the target, the
    parallel premium widens.  When reserves are healthy, premium shrinks
    toward the base level.

    ``parallel = official * (1 + premium)``

    ``premium = base_premium + pressure_term + noise``
    """
    # Reserve cover in months of imports
    if monthly_imports > 0:
        reserve_cover_months = reserves_usd / monthly_imports
    else:
        # No imports → no pressure
        reserve_cover_months = reserve_months_target

    # Pressure: rises when reserve cover falls below target.
    # cover_ratio > 1 → surplus, pressure < 0
    # cover_ratio < 1 → deficit, pressure > 0
    cover_ratio = reserve_cover_months / max(reserve_months_target, 1.0)
    pressure = 0.5 * (1.0 / max(cover_ratio, 0.1) - 1.0)

    # Small monthly noise
    noise = rng.normal(0.0, 0.02)

    # Target premium (floored at zero — parallel never below official)
    target_premium = max(base_premium + pressure + noise, 0.0)

    # Smooth adjustment: close 30 % of the gap per month
    target_parallel = official_rate * (1.0 + target_premium)
    adjustment_speed = 0.3
    parallel_new = current_parallel + adjustment_speed * (
        target_parallel - current_parallel
    )

    # Floor: parallel can never fall below official
    parallel_new = max(parallel_new, official_rate)

    return parallel_new
