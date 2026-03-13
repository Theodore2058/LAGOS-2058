"""
Economy diagnostics — compute dashboard metrics from EconomicState.

Stateless functions that take state + config and return plain dicts.
"""
from __future__ import annotations

import numpy as np

from src.economy.core.types import EconomicState, SimConfig
from src.economy.data.commodities import COMMODITIES, BASE_PRICES


# ── Food commodity IDs (from CONSUMPTION_BASKET_COMMODITY_MAP) ───────────
_FOOD_COMMODITY_IDS = [6, 7, 8, 13, 18, 21]


# ---------------------------------------------------------------------------
# 1. GDP proxy
# ---------------------------------------------------------------------------

def compute_gdp_proxy(state: EconomicState, config: SimConfig) -> float:
    """Sum of production_capacity * prices across all LGAs and commodities."""
    # production_capacity: (774, 36), prices: (774, 36)
    return float(np.sum(state.production_capacity * state.prices))


# ---------------------------------------------------------------------------
# 2. Inflation proxy
# ---------------------------------------------------------------------------

def compute_inflation_proxy(state: EconomicState, config: SimConfig) -> float:
    """Mean(prices / base_prices) - 1.0 across all LGAs and commodities.

    A value of 0.0 means prices are at baseline; 0.5 means 50 % inflation.
    """
    # BASE_PRICES is shape (36,); broadcast across (774, 36)
    ratios = state.prices / BASE_PRICES[np.newaxis, :]
    return float(np.mean(ratios) - 1.0)


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
    results: list[dict] = []
    for c in COMMODITIES:
        cid = c.id
        results.append({
            "id": cid,
            "name": c.name,
            "total_output": float(np.sum(state.actual_output[:, cid])),
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
    # Food crisis: any food commodity price > 3x base price in any LGA
    food_crisis = False
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
    """Mean price across LGAs for each of the 56 history slots.

    Parameters
    ----------
    state : EconomicState
    commodity_id : int
        Index into the commodity axis (0-35).

    Returns
    -------
    dict with keys: commodity_id (int), prices (list[float])
    """
    # price_history: (774, 36, 56)
    hist = state.price_history[:, commodity_id, :]  # (774, 56)
    mean_prices = np.mean(hist, axis=0)  # (56,)
    return {
        "commodity_id": commodity_id,
        "prices": mean_prices.tolist(),
    }
