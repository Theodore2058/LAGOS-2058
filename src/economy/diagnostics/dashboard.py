"""
Economy diagnostics — compute dashboard metrics from EconomicState.

Stateless functions that take state + config and return plain dicts.
"""
from __future__ import annotations

import numpy as np

from src.economy.core.types import (
    EconomicState,
    SimConfig,
    CONSUMPTION_BASKET_COMMODITY_MAP,
    CONSUMPTION_WEIGHTS_BY_QUINTILE,
)
from src.economy.data.commodities import COMMODITIES, BASE_PRICES


# ── Food commodity IDs (from CONSUMPTION_BASKET_COMMODITY_MAP) ───────────
_FOOD_COMMODITY_IDS = [6, 7, 8, 13, 18, 21]

# ── CPI basket: weighted commodity indices for consumer price tracking ────
# Build a (C,) weight vector that maps commodity → consumption share.
# Combines all quintile weights uniformly (population-weighted average is
# roughly equal across quintiles at the national level).
_CPI_WEIGHTS: np.ndarray | None = None
_FOOD_CPI_WEIGHTS: np.ndarray | None = None


def _build_cpi_weights() -> tuple[np.ndarray, np.ndarray]:
    """Lazily build CPI commodity weight vectors."""
    global _CPI_WEIGHTS, _FOOD_CPI_WEIGHTS
    if _CPI_WEIGHTS is not None:
        return _CPI_WEIGHTS, _FOOD_CPI_WEIGHTS  # type: ignore[return-value]

    C = len(COMMODITIES)
    # Average consumption weights across quintiles (equal population per quintile)
    avg_quintile_weights = CONSUMPTION_WEIGHTS_BY_QUINTILE.mean(axis=0)  # (9,)

    cpi_w = np.zeros(C, dtype=np.float64)
    food_w = np.zeros(C, dtype=np.float64)

    categories = list(CONSUMPTION_BASKET_COMMODITY_MAP.keys())
    for cat_idx, cat_name in enumerate(categories):
        commodity_ids = CONSUMPTION_BASKET_COMMODITY_MAP[cat_name]
        if not commodity_ids:
            continue
        cat_weight = avg_quintile_weights[cat_idx]
        per_commodity = cat_weight / len(commodity_ids)
        for c_id in commodity_ids:
            cpi_w[c_id] += per_commodity
            if cat_name == "food":
                food_w[c_id] += per_commodity

    # Normalise so weights sum to 1
    total = cpi_w.sum()
    if total > 0:
        cpi_w /= total
    food_total = food_w.sum()
    if food_total > 0:
        food_w /= food_total

    _CPI_WEIGHTS = cpi_w
    _FOOD_CPI_WEIGHTS = food_w
    return cpi_w, food_w


# ---------------------------------------------------------------------------
# 1. GDP proxy
# ---------------------------------------------------------------------------

def compute_gdp_proxy(state: EconomicState, config: SimConfig) -> float:
    """GDP proxy: total production value per month.

    Uses sell_orders (V3 order-book) if available, otherwise falls back
    to production_capacity * prices (legacy).
    """
    # V3 mode: sell_orders represents actual monthly production
    if hasattr(state, 'sell_orders') and state.sell_orders is not None and state.sell_orders.sum() > 0:
        return float(np.sum(state.sell_orders * state.prices))
    # Legacy: production_capacity * prices
    return float(np.sum(state.production_capacity * state.prices))


# ---------------------------------------------------------------------------
# 2. Consumer Price Index (CPI)
# ---------------------------------------------------------------------------

def compute_inflation_proxy(state: EconomicState, config: SimConfig) -> float:
    """Consumption-basket-weighted CPI across all LGAs.

    Uses the 9-category consumption basket (food, energy, housing, healthcare,
    clothing, transport, communication, education, security) to weight the
    price-to-base-price ratio of each commodity.  This gives a realistic
    consumer-facing inflation number rather than a naive mean across all 36
    commodities (many of which — crude oil, cobalt, arms — consumers don't
    buy directly).

    Returns
    -------
    float
        0.0 = prices at baseline, 0.10 = 10 % inflation, etc.
    """
    cpi_w, _ = _build_cpi_weights()  # (C,)

    # Price-to-base ratio per LGA per commodity
    ratios = state.prices / BASE_PRICES[np.newaxis, :]  # (N, C)

    # Weighted CPI per LGA, then national average
    lga_cpi = (ratios * cpi_w[np.newaxis, :]).sum(axis=1)  # (N,)
    return float(np.mean(lga_cpi) - 1.0)


def compute_food_cpi(state: EconomicState, config: SimConfig) -> float:
    """Food-specific CPI — weighted by food consumption basket shares.

    Food dominates spending for Nigeria's poorest quintiles (55 % of Q1
    spending goes to food), making this the most politically sensitive
    price indicator.  A food CPI above ~0.30 historically triggers unrest.

    Returns
    -------
    float
        0.0 = food prices at baseline, 0.30 = 30 % food inflation, etc.
    """
    _, food_w = _build_cpi_weights()  # (C,)

    ratios = state.prices / BASE_PRICES[np.newaxis, :]  # (N, C)
    lga_food_cpi = (ratios * food_w[np.newaxis, :]).sum(axis=1)  # (N,)
    return float(np.mean(lga_food_cpi) - 1.0)


def compute_cpi_by_quintile(state: EconomicState, config: SimConfig) -> dict:
    """CPI broken down by income quintile.

    Lower quintiles spend more on food (55 % for Q1 vs 12 % for Q5),
    so inflation hits them harder.  Returns a dict mapping quintile
    label → CPI float.
    """
    C = len(COMMODITIES)
    categories = list(CONSUMPTION_BASKET_COMMODITY_MAP.keys())
    quintile_labels = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    ratios = state.prices / BASE_PRICES[np.newaxis, :]  # (N, C)

    result = {}
    for q in range(5):
        q_weights = np.zeros(C, dtype=np.float64)
        for cat_idx, cat_name in enumerate(categories):
            commodity_ids = CONSUMPTION_BASKET_COMMODITY_MAP[cat_name]
            if not commodity_ids:
                continue
            cat_weight = CONSUMPTION_WEIGHTS_BY_QUINTILE[q, cat_idx]
            per_commodity = cat_weight / len(commodity_ids)
            for c_id in commodity_ids:
                q_weights[c_id] += per_commodity
        # Normalise
        total = q_weights.sum()
        if total > 0:
            q_weights /= total
        lga_cpi = (ratios * q_weights[np.newaxis, :]).sum(axis=1)
        result[quintile_labels[q]] = float(np.mean(lga_cpi) - 1.0)

    return result


# ---------------------------------------------------------------------------
# 3. Gini coefficient
# ---------------------------------------------------------------------------

def compute_gini_coefficient(state: EconomicState) -> float:
    """Gini coefficient of mean wages across LGAs.

    Uses the standard relative-mean-difference formula:
        G = sum_i sum_j |w_i - w_j| / (2 * n * sum(w))
    """
    # wages: (774, 4) — take the mean across skill tiers for each LGA
    mean_wages = np.mean(state.wages, axis=1)  # (774,)
    n = mean_wages.shape[0]
    total = np.sum(mean_wages)
    if total == 0.0:
        return 0.0
    # Sorted-array shortcut: G = (2 * sum(i * w_sorted) / (n * sum(w))) - (n+1)/n
    sorted_w = np.sort(mean_wages)
    index = np.arange(1, n + 1, dtype=np.float64)
    return float((2.0 * np.sum(index * sorted_w)) / (n * total) - (n + 1.0) / n)


# ---------------------------------------------------------------------------
# 4. Employment statistics
# ---------------------------------------------------------------------------

def compute_employment_stats(state: EconomicState, config: SimConfig) -> dict:
    """Aggregate and per-tier employment statistics.

    Returns
    -------
    dict with keys:
        total_pool, total_employed, total_informal, total_unemployed,
        employment_rate, informality_rate,
        by_tier (list of per-tier dicts)
    """
    # All arrays are (774, N_SKILL_TIERS)
    pool = state.labor_pool        # (774, 4)
    employed = state.labor_employed  # (774, 4)
    informal = state.labor_informal  # (774, 4)

    total_pool = float(np.sum(pool))
    total_employed = float(np.sum(employed))
    total_informal = float(np.sum(informal))
    total_unemployed = total_pool - total_employed - total_informal

    employment_rate = (total_employed + total_informal) / total_pool if total_pool > 0 else 0.0
    informality_rate = total_informal / (total_employed + total_informal) if (total_employed + total_informal) > 0 else 0.0

    by_tier: list[dict] = []
    for t in range(config.N_SKILL_TIERS):
        t_pool = float(np.sum(pool[:, t]))
        t_employed = float(np.sum(employed[:, t]))
        t_informal = float(np.sum(informal[:, t]))
        t_unemployed = t_pool - t_employed - t_informal
        t_emp_rate = (t_employed + t_informal) / t_pool if t_pool > 0 else 0.0
        by_tier.append({
            "tier": t,
            "name": config.SKILL_TIER_NAMES[t],
            "pool": t_pool,
            "employed": t_employed,
            "informal": t_informal,
            "unemployed": t_unemployed,
            "employment_rate": t_emp_rate,
        })

    return {
        "total_pool": total_pool,
        "total_employed": total_employed,
        "total_informal": total_informal,
        "total_unemployed": total_unemployed,
        "employment_rate": employment_rate,
        "informality_rate": informality_rate,
        "by_tier": by_tier,
    }


# ---------------------------------------------------------------------------
# 5. Trade balance
# ---------------------------------------------------------------------------

def compute_trade_balance(state: EconomicState) -> dict:
    """Export/import balance and reserve adequacy.

    Returns
    -------
    dict with keys: exports, imports, balance, reserve_months
    """
    exports = float(state.monthly_export_revenue_usd)
    imports = float(state.monthly_import_bill_usd)
    balance = exports - imports
    reserve_months = (
        float(state.forex_reserves_usd / imports) if imports > 0 else float("inf")
    )
    return {
        "exports": exports,
        "imports": imports,
        "balance": balance,
        "reserve_months": reserve_months,
    }


# ---------------------------------------------------------------------------
# 6. Sector output
# ---------------------------------------------------------------------------

def compute_sector_output(state: EconomicState, config: SimConfig) -> list[dict]:
    """Per-commodity output summary across all LGAs.

    Returns a list of dicts (one per commodity) with keys:
        id, name, total_output, total_inventory, mean_price
    """
    # Use sell_orders in V3 mode for output (actual_output is zero)
    output_source = state.actual_output
    if hasattr(state, 'sell_orders') and state.sell_orders is not None and state.sell_orders.sum() > 0:
        output_source = state.sell_orders

    results: list[dict] = []
    for c in COMMODITIES:
        cid = c.id
        results.append({
            "id": cid,
            "name": c.name,
            "total_output": float(np.sum(output_source[:, cid])),
            "total_inventory": float(np.sum(state.inventories[:, cid])),
            "mean_price": float(np.mean(state.prices[:, cid])),
        })
    return results


# ---------------------------------------------------------------------------
# 7. Regional inequality
# ---------------------------------------------------------------------------

def compute_regional_inequality(state: EconomicState, config: SimConfig) -> dict:
    """Compare top-10 vs bottom-10 LGAs by mean wage.

    Returns
    -------
    dict with keys:
        top10_mean_wage, bottom10_mean_wage, ratio,
        top10_lgas (list[int]), bottom10_lgas (list[int])
    """
    mean_wages = np.mean(state.wages, axis=1)  # (774,)
    ranked = np.argsort(mean_wages)  # ascending

    bottom10_idx = ranked[:10]
    top10_idx = ranked[-10:]

    bottom10_mean = float(np.mean(mean_wages[bottom10_idx]))
    top10_mean = float(np.mean(mean_wages[top10_idx]))
    ratio = top10_mean / bottom10_mean if bottom10_mean > 0 else float("inf")

    return {
        "top10_mean_wage": top10_mean,
        "bottom10_mean_wage": bottom10_mean,
        "ratio": ratio,
        "top10_lgas": top10_idx.tolist(),
        "bottom10_lgas": bottom10_idx.tolist(),
    }


# ---------------------------------------------------------------------------
# 8. Crisis indicators
# ---------------------------------------------------------------------------

def compute_crisis_indicators(state: EconomicState, config: SimConfig) -> dict:
    """Boolean / float crisis flags for the dashboard.

    Returns
    -------
    dict with keys:
        food_crisis, forex_crisis, banking_crisis,
        unemployment_crisis, inflation_crisis, alsahid_crisis
    """
    # Food crisis: food CPI > 30% OR any food commodity > 3x base in any LGA
    food_cpi = compute_food_cpi(state, config)
    food_crisis = food_cpi > 0.30
    if not food_crisis:
        for fid in _FOOD_COMMODITY_IDS:
            if np.any(state.prices[:, fid] > 3.0 * BASE_PRICES[fid]):
                food_crisis = True
                break

    # Forex crisis: parallel / official > 1.5
    forex_crisis = (
        state.parallel_exchange_rate / state.official_exchange_rate > 1.5
        if state.official_exchange_rate > 0 else False
    )

    # Banking crisis: mean bank_confidence < 0.3
    banking_crisis = bool(np.mean(state.bank_confidence) < 0.3)

    # Unemployment crisis: overall employment_rate < 0.5
    emp_stats = compute_employment_stats(state, config)
    unemployment_crisis = emp_stats["employment_rate"] < 0.5

    # Inflation crisis: inflation_proxy > 0.5
    inflation = compute_inflation_proxy(state, config)
    inflation_crisis = inflation > 0.5

    # Al-Shahid crisis: mean alsahid_control > 0.3
    alsahid_crisis = bool(np.mean(state.alsahid_control) > 0.3)

    return {
        "food_crisis": food_crisis,
        "forex_crisis": forex_crisis,
        "banking_crisis": banking_crisis,
        "unemployment_crisis": unemployment_crisis,
        "inflation_crisis": inflation_crisis,
        "alsahid_crisis": alsahid_crisis,
    }


# ---------------------------------------------------------------------------
# 9. Price history series
# ---------------------------------------------------------------------------

def compute_price_history_series(state: EconomicState, commodity_id: int) -> dict:
    """Mean price across LGAs for each of the 56 history slots (chronological).

    Parameters
    ----------
    state : EconomicState
    commodity_id : int
        Index into the commodity axis (0-35).

    Returns
    -------
    dict with keys: commodity_id (int), prices (list[float])
    """
    from src.economy.systems.trade import get_recent_prices

    H = state.price_history.shape[2]
    recent = get_recent_prices(state, H)  # (N, C, H) in chronological order
    hist = recent[:, commodity_id, :]  # (N, H)
    mean_prices = np.mean(hist, axis=0)  # (H,)
    return {
        "commodity_id": commodity_id,
        "prices": mean_prices.tolist(),
    }
