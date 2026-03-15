"""
Economy-Election Bridge — snapshots economic state into election engine format.

The election engine reads static LGA-level columns from a DataFrame
(poverty, unemployment, GDP, road quality, conflict intensity). This module
provides a function to update those columns dynamically from a running
economic simulation, so that election results reflect the live economy.

Usage (in the campaign or integration layer):
    from src.election_engine.economy_bridge import update_lga_data_from_economy
    update_lga_data_from_economy(lga_data, econ_state, econ_config)
    # Then run the election as normal — it will see the updated columns.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def update_lga_data_from_economy(
    lga_data: pd.DataFrame,
    econ_state: "EconomicState",
    econ_config: "SimConfig",
    *,
    campaign_modifiers: Optional["CampaignModifiers"] = None,
) -> pd.DataFrame:
    """
    Update LGA DataFrame columns from the current economic state.

    Modifies *lga_data* in-place and also returns it for chaining.
    Only updates columns that exist in the DataFrame; creates new ones
    for critical fields that may be missing.

    Parameters
    ----------
    lga_data : pd.DataFrame
        The LGA data DataFrame used by the election engine (774 rows).
    econ_state : EconomicState
        Current economic simulation state.
    econ_config : SimConfig
        Economic simulation configuration.
    campaign_modifiers : CampaignModifiers, optional
        If provided, also generates salience_shift from economic feedback.

    Returns
    -------
    pd.DataFrame
        The modified *lga_data* (same object, mutated in place).
    """
    N = econ_config.N_LGAS

    # Safety: ensure row counts match
    if len(lga_data) != N:
        logger.warning(
            "LGA count mismatch: DataFrame has %d rows, economy has %d LGAs. "
            "Skipping economy bridge update.",
            len(lga_data), N,
        )
        return lga_data

    # ------------------------------------------------------------------
    # 1. Unemployment Rate
    # ------------------------------------------------------------------
    if econ_state.labor_employed is not None and econ_state.labor_pool is not None:
        safe_pool = np.maximum(econ_state.labor_pool.sum(axis=1), 1.0)
        emp_rate = econ_state.labor_employed.sum(axis=1) / safe_pool
        unemployment_pct = (1.0 - np.clip(emp_rate, 0.0, 1.0)) * 100.0
        lga_data["Unemployment Rate Pct"] = unemployment_pct

        # Youth unemployment approximation: unskilled tier unemployment
        # Unskilled tier (index 0) is the best proxy for youth
        safe_unskilled = np.maximum(econ_state.labor_pool[:, 0], 1.0)
        youth_unemp = (1.0 - np.clip(
            econ_state.labor_employed[:, 0] / safe_unskilled, 0.0, 1.0,
        )) * 100.0
        lga_data["Youth Unemployment Rate Pct"] = youth_unemp

    # ------------------------------------------------------------------
    # 2. GDP Per Capita
    # ------------------------------------------------------------------
    # GDP proxy: sum(sell_orders * prices) per LGA ÷ population
    # Annualized (multiply by 12 since economy state is monthly)
    if econ_state.prices is not None and econ_state.population is not None:
        if (
            hasattr(econ_state, 'sell_orders')
            and econ_state.sell_orders is not None
            and econ_state.sell_orders.sum() > 0
        ):
            output_value = (econ_state.sell_orders * econ_state.prices).sum(axis=1)
        elif econ_state.actual_output is not None and econ_state.actual_output.sum() > 0:
            output_value = (econ_state.actual_output * econ_state.prices).sum(axis=1)
        else:
            output_value = (econ_state.production_capacity * econ_state.prices).sum(axis=1)

        # Convert monthly to annual; divide by population for per-capita
        safe_pop = np.maximum(econ_state.population, 1.0)
        gdp_per_capita = (output_value * 12.0) / safe_pop

        # Convert naira to USD equivalent using parallel rate
        # The election engine expects values in the ~5K-50K range
        safe_rate = max(econ_state.parallel_exchange_rate, 100.0)
        gdp_per_capita_usd = gdp_per_capita / safe_rate

        lga_data["GDP Per Capita Est"] = gdp_per_capita_usd

    # ------------------------------------------------------------------
    # 3. Poverty Rate
    # ------------------------------------------------------------------
    # Derive from per-pop standard of living: pops with SoL < 3.0 are "poor"
    if econ_state.pop_standard_of_living is not None:
        pop_lga = getattr(econ_state, "_pop_lga_ids", None)
        if pop_lga is not None and econ_state.pop_count is not None:
            # Count poor pops per LGA
            is_poor = econ_state.pop_standard_of_living < 3.0
            poor_count = np.bincount(
                pop_lga, weights=is_poor.astype(float) * econ_state.pop_count,
                minlength=N,
            )
            total_count = np.bincount(
                pop_lga, weights=econ_state.pop_count,
                minlength=N,
            )
            safe_total = np.maximum(total_count, 1.0)
            poverty_rate = (poor_count / safe_total) * 100.0
            lga_data["Poverty Rate Pct"] = np.clip(poverty_rate, 0.0, 100.0)

    # ------------------------------------------------------------------
    # 4. Infrastructure Indices
    # ------------------------------------------------------------------
    if econ_state.infra_road_quality is not None:
        # Road quality is 0-1 in economy; election engine expects 0-10
        lga_data["Road Quality Index"] = econ_state.infra_road_quality * 10.0

    if econ_state.infra_power_reliability is not None:
        # Electricity access (0-100 scale)
        lga_data["Elec_pct"] = econ_state.infra_power_reliability * 100.0

    # ------------------------------------------------------------------
    # 5. Conflict / Al-Shahid control
    # ------------------------------------------------------------------
    if econ_state.alsahid_control is not None:
        # Conflict History is 0-5 ordinal; al-Shahid control 0-1 → scale to 0-5
        lga_data["Conflict History"] = econ_state.alsahid_control * 5.0

    # ------------------------------------------------------------------
    # 6. Food inflation per LGA (drives voter discontent)
    # ------------------------------------------------------------------
    if econ_state.prices is not None:
        from src.economy.data.commodities import BASE_PRICES
        from src.economy.diagnostics.dashboard import _build_cpi_weights

        _, food_w = _build_cpi_weights()  # (C,) food-only weights
        # Per-LGA food CPI: weighted price ratio for food commodities
        ratios = econ_state.prices / BASE_PRICES[np.newaxis, :]  # (N, C)
        lga_food_cpi = (ratios * food_w[np.newaxis, :]).sum(axis=1) - 1.0  # (N,)

        # Store as percentage for the election engine (0 = no change, 50 = 50% spike)
        lga_data["Food Inflation Pct"] = lga_food_cpi * 100.0

        # Also compute overall CPI per LGA
        cpi_w, _ = _build_cpi_weights()
        lga_cpi = (ratios * cpi_w[np.newaxis, :]).sum(axis=1) - 1.0
        lga_data["CPI Pct"] = lga_cpi * 100.0

    # ------------------------------------------------------------------
    # 7. Gini proxy from income distribution
    # ------------------------------------------------------------------
    if econ_state.pop_income is not None:
        pop_lga = getattr(econ_state, "_pop_lga_ids", None)
        if pop_lga is not None:
            # Simplified Gini: ratio of top-20% to bottom-40% income
            pop_income_bracket = getattr(econ_state, "_pop_income_ids", None)
            if pop_income_bracket is not None:
                is_top = pop_income_bracket == 2  # Top 20%
                is_bottom = pop_income_bracket == 0  # Bottom 40%

                top_income = np.bincount(
                    pop_lga, weights=econ_state.pop_income * is_top,
                    minlength=N,
                )
                bottom_income = np.bincount(
                    pop_lga, weights=econ_state.pop_income * is_bottom,
                    minlength=N,
                )
                safe_bottom = np.maximum(bottom_income, 1.0)
                # Income ratio: higher = more unequal. Scale to 0-1 proxy
                ratio = top_income / safe_bottom
                gini_proxy = np.clip(ratio / 10.0, 0.0, 1.0)
                lga_data["Gini Proxy"] = gini_proxy

    # ------------------------------------------------------------------
    # 8. Informality rate per LGA
    # ------------------------------------------------------------------
    if econ_state.labor_informal is not None and econ_state.labor_employed is not None:
        total_working = (
            econ_state.labor_employed.sum(axis=1)
            + econ_state.labor_informal.sum(axis=1)
        )
        safe_working = np.maximum(total_working, 1.0)
        informality = econ_state.labor_informal.sum(axis=1) / safe_working * 100.0
        lga_data["Informality Rate Pct"] = informality

    # ------------------------------------------------------------------
    # 9. Banking stress per LGA's zone
    # ------------------------------------------------------------------
    if econ_state.bank_confidence is not None and econ_state.admin_zone is not None:
        zone_conf = econ_state.bank_confidence
        # Map zone-level confidence to LGA level
        lga_zone = econ_state.admin_zone.astype(np.intp)
        lga_zone = np.clip(lga_zone, 0, len(zone_conf) - 1)
        lga_bank_stress = (1.0 - zone_conf[lga_zone]) * 100.0
        lga_data["Banking Stress Pct"] = lga_bank_stress

    # ------------------------------------------------------------------
    # 10. Salience shift injection (if campaign modifiers provided)
    # ------------------------------------------------------------------
    if campaign_modifiers is not None:
        _inject_economic_salience(econ_state, econ_config, campaign_modifiers)

    logger.info(
        "Economy bridge updated %d LGA columns: unemp=%.1f%%, GDP/cap=$%.0f, "
        "poverty=%.1f%%",
        N,
        lga_data["Unemployment Rate Pct"].mean() if "Unemployment Rate Pct" in lga_data else 0,
        lga_data["GDP Per Capita Est"].mean() if "GDP Per Capita Est" in lga_data else 0,
        lga_data["Poverty Rate Pct"].mean() if "Poverty Rate Pct" in lga_data else 0,
    )

    return lga_data


def _inject_economic_salience(
    econ_state: "EconomicState",
    econ_config: "SimConfig",
    campaign_modifiers: "CampaignModifiers",
) -> None:
    """
    Inject economy-driven salience shifts into campaign modifiers.

    Uses the economy system's pre-computed voter_salience (N_VOTER_TYPES, 28)
    to update the campaign's salience_shift array (n_lga, 28).

    Since the campaign system operates at LGA level, we average the voter-type
    salience shifts within each LGA.
    """
    if econ_state.voter_salience is None:
        return

    N = econ_config.N_LGAS
    n_dim = econ_state.voter_salience.shape[1] if econ_state.voter_salience.ndim > 1 else 0
    if n_dim == 0:
        return

    pop_lga = getattr(econ_state, "_pop_lga_ids", None)
    if pop_lga is None:
        return

    # Average voter-type salience shifts to LGA level
    lga_salience = np.zeros((N, n_dim), dtype=np.float64)
    pop_count = np.bincount(pop_lga, minlength=N).astype(np.float64)
    safe_count = np.maximum(pop_count, 1.0)

    for d in range(n_dim):
        weighted_sum = np.bincount(
            pop_lga, weights=econ_state.voter_salience[:, d],
            minlength=N,
        )
        lga_salience[:, d] = weighted_sum / safe_count

    # Add to existing salience_shift or create new one
    if campaign_modifiers.salience_shift is not None:
        campaign_modifiers.salience_shift += lga_salience.astype(np.float32)
    else:
        campaign_modifiers.salience_shift = lga_salience.astype(np.float32)
