"""Pydantic models for economy API responses."""

from __future__ import annotations

from pydantic import BaseModel


class EconomyStatusResponse(BaseModel):
    """High-level economy dashboard."""

    game_month: int
    game_day: int
    tick_count: int
    gdp_proxy: float  # sum of production_capacity * prices
    total_employment: float
    total_population: float
    forex_reserves_usd: float
    official_exchange_rate: float
    parallel_exchange_rate: float
    oil_price_usd: float
    cobalt_price_usd: float
    mean_price_index: float
    inflation_proxy: float  # mean price change from base
    total_bank_deposits: float
    total_bank_loans: float
    mean_bank_confidence: float
    is_rainy_season: bool
    alsahid_mean_control: float


class PriceSummaryResponse(BaseModel):
    """Per-commodity price summary across all LGAs."""

    commodity_id: int
    commodity_name: str
    mean_price: float
    min_price: float
    max_price: float
    base_price: float
    price_ratio: float  # mean/base


class LaborSummaryResponse(BaseModel):
    """Per-skill-tier labor summary."""

    skill_tier: int
    skill_name: str
    total_pool: float
    total_employed: float
    total_informal: float
    employment_rate: float
    mean_wage: float


class BankingSummaryResponse(BaseModel):
    """Per-zone banking summary."""

    zone_id: int
    deposits: float
    loans: float
    bad_loans: float
    confidence: float
    lending_rate: float


class LGADetailResponse(BaseModel):
    """Detailed view of a single LGA."""

    lga_id: int
    population: float
    wages: list[float]  # 4 skill tiers
    employment: list[float]
    prices_top5: list[dict]  # top 5 by price
    land_area: list[float]  # 4 types
    land_prices: list[float]
    road_quality: float
    power_reliability: float
    alsahid_control: float


class SimControlRequest(BaseModel):
    """Request to run simulation ticks."""

    n_months: int = 1
    seed: int | None = None


class SimControlResponse(BaseModel):
    """Response after running simulation."""

    months_run: int
    ticks_executed: int
    final_month: int
    warnings_count: int
    elapsed_seconds: float


class PolicyRequest(BaseModel):
    """Request to enqueue a policy action."""

    action_type: str
    parameters: dict
    source: str = "executive"
    implementation_delay: int = 0


class WhatIfRequest(BaseModel):
    """Request to run a what-if scenario."""

    n_months: int = 3
    policies: list[PolicyRequest] = []
    seed: int | None = None


class WhatIfResponse(BaseModel):
    """Result of what-if scenario comparison."""

    baseline: EconomyStatusResponse
    scenario: EconomyStatusResponse
    delta_gdp: float
    delta_employment: float
    delta_forex_reserves: float
    delta_inflation: float
