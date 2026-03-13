"""Diagnostic dashboard and sensitivity analysis."""

from src.economy.diagnostics.dashboard import (
    compute_gdp_proxy,
    compute_inflation_proxy,
    compute_gini_coefficient,
    compute_employment_stats,
    compute_trade_balance,
    compute_sector_output,
    compute_regional_inequality,
    compute_crisis_indicators,
    compute_price_history_series,
)

__all__ = [
    "compute_gdp_proxy",
    "compute_inflation_proxy",
    "compute_gini_coefficient",
    "compute_employment_stats",
    "compute_trade_balance",
    "compute_sector_output",
    "compute_regional_inequality",
    "compute_crisis_indicators",
    "compute_price_history_series",
]
