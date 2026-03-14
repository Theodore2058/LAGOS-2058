"""
Banking and credit system — operates at Administrative Zone level (8 zones).

Includes deposit collection, loan evaluation, financial accelerator,
and Naijin credit bias.
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import BankingMutations, EconomicState, SimConfig

logger = logging.getLogger(__name__)


def tick_banking(state: EconomicState, config: SimConfig) -> BankingMutations:
    """
    Banking tick at zone level.

    1. Collect deposits from household savings
    2. Evaluate loan defaults
    3. Update confidence
    4. Compute lending willingness
    5. Process new loans
    6. Set lending rates
    """
    Z = config.N_ADMIN_ZONES

    # 1. Deposits: fraction of total income in each zone
    zone_income = _compute_zone_income(state, config)
    savings_rate = 0.10  # 10% of income saved
    deposit_inflow = zone_income * savings_rate / config.PRODUCTION_TICKS_PER_MONTH
    # Withdrawal: households draw down deposits for consumption (~8% outflow)
    deposit_outflow = state.bank_deposits * 0.08 / config.PRODUCTION_TICKS_PER_MONTH
    deposits_new = state.bank_deposits + deposit_inflow - deposit_outflow
    deposits_new = np.maximum(deposits_new, 0.0)

    # 2. Loan defaults
    defaults = np.zeros(Z, dtype=np.float64)
    zone_revenue = _compute_zone_revenue(state, config)
    for z in range(Z):
        defaults[z] = evaluate_loan_defaults(
            state, z, config, zone_revenue[z],
        )

    loans_new = state.bank_loans - defaults
    loans_new = np.maximum(loans_new, 0.0)
    bad_loans_new = state.bank_bad_loans + defaults

    # 3. Confidence
    confidence_change = np.zeros(Z, dtype=np.float64)
    for z in range(Z):
        if state.bank_loans[z] > 0:
            default_ratio = defaults[z] / state.bank_loans[z]
        else:
            default_ratio = 0.0
        confidence_change[z] = -default_ratio * 2.0  # defaults hurt confidence

    # Apply financial accelerator
    for z in range(Z):
        is_contraction = confidence_change[z] < 0
        confidence_change[z] = financial_accelerator(
            confidence_change[z],
            config.FINANCIAL_ACCELERATOR_LEVERAGE,
            config.FINANCIAL_ACCELERATOR_ELASTICITY,
            is_contraction,
        )

    confidence_new = np.clip(state.bank_confidence + confidence_change, 0.05, 1.0)

    # 4-5. Lending
    max_loans = deposits_new / config.RESERVE_RATIO
    lending_willingness = confidence_new * 0.8  # high confidence = willing to lend

    # Naijin credit bias
    naijin_mod = np.ones(Z, dtype=np.float64)
    for z in range(Z):
        naijin_mod[z] = compute_naijin_credit_bias(state, z)

    credit_available = (max_loans - loans_new) * lending_willingness * naijin_mod
    credit_available = np.maximum(credit_available, 0.0)

    # New lending (demand-driven: fraction of available credit)
    new_lending = credit_available * 0.05  # 5% of available per tick
    loans_new = loans_new + new_lending

    # Loan contraction: if loans exceed reserve-ratio cap, shrink aggressively
    # 50% of excess per tick — at 7 ticks/month this converges within 2-3 ticks
    excess_loans = loans_new - max_loans
    contraction = np.where(excess_loans > 0, excess_loans * 0.50, 0.0)
    loans_new = np.maximum(loans_new - contraction, 0.0)

    # 6. Lending rates
    lending_rate_new = config.BASE_INTEREST_RATE * (
        2.0 - confidence_new  # low confidence = high rates
    )
    lending_rate_new = np.clip(lending_rate_new, 0.04, 0.25)

    return BankingMutations(
        deposits_new=deposits_new,
        loans_new=loans_new,
        bad_loans_new=bad_loans_new,
        confidence_new=confidence_new,
        lending_rate_new=lending_rate_new,
        credit_available=credit_available,
        defaults_this_tick=defaults,
    )


def financial_accelerator(
    confidence_change: float,
    leverage_ratio: float,
    elasticity: float,
    is_contraction: bool,
) -> float:
    """
    Bernanke-Gertler-Gilchrist financial accelerator.

    amplification = 1 + leverage * elasticity ≈ 2.2x with defaults.
    Contraction is faster than expansion (asymmetric).
    """
    amplification = 1.0 + leverage_ratio * elasticity
    if is_contraction:
        return confidence_change * amplification
    else:
        return confidence_change * amplification * 0.5


def evaluate_loan_defaults(
    state: EconomicState, zone: int, config: SimConfig,
    zone_revenue: float,
) -> float:
    """
    Evaluate loan defaults in a zone.

    Default when revenue < LOAN_DEFAULT_THRESHOLD * debt_service.
    """
    debt_service = state.bank_loans[zone] * state.lending_rate[zone] / 12.0
    if debt_service <= 0:
        return 0.0

    revenue_ratio = zone_revenue / max(debt_service, 1.0)
    if revenue_ratio < config.LOAN_DEFAULT_THRESHOLD:
        default_fraction = (
            config.LOAN_DEFAULT_THRESHOLD - revenue_ratio
        ) / config.LOAN_DEFAULT_THRESHOLD
        default_fraction = min(default_fraction, 0.30)  # cap at 30% per tick
        return state.bank_loans[zone] * default_fraction

    return 0.0


def compute_naijin_credit_bias(
    state: EconomicState, zone: int,
) -> float:
    """
    Credit modifier reflecting risk-adjusted lending.

    Northern zones with higher insurgency → less credit.
    Rational but politically perceived as ethnic discrimination.
    """
    if state.alsahid_control is None:
        return 1.0

    from src.economy.core.types import lgas_in_zone

    # Use real zone mapping to get actual al-Shahid control in this zone
    if state.admin_zone is not None:
        zone_lgas = lgas_in_zone(state, zone)
        if len(zone_lgas) > 0:
            zone_control = float(state.alsahid_control[zone_lgas].mean())
        else:
            zone_control = float(state.alsahid_control.mean())
    else:
        zone_control = float(state.alsahid_control.mean())

    return max(1.0 - zone_control * 0.3, 0.7)


def apply_banking_mutations(
    state: EconomicState, mutations: BankingMutations,
) -> None:
    """Apply banking results to state."""
    state.bank_deposits = mutations.deposits_new
    state.bank_loans = mutations.loans_new
    state.bank_bad_loans = mutations.bad_loans_new
    state.bank_confidence = mutations.confidence_new
    state.lending_rate = mutations.lending_rate_new


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_zone_income(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """Total wage income per zone using real admin zone mapping."""
    from src.economy.core.types import aggregate_by_zone

    total_per_lga = (state.wages * state.labor_employed).sum(axis=1)
    return aggregate_by_zone(state, total_per_lga, config.N_ADMIN_ZONES)


def _compute_zone_revenue(
    state: EconomicState, config: SimConfig,
) -> np.ndarray:
    """Total business revenue per zone using real admin zone mapping."""
    from src.economy.core.types import aggregate_by_zone

    # Use sell_orders (V3) or production_capacity (legacy) for revenue proxy
    if (
        hasattr(state, 'sell_orders')
        and state.sell_orders is not None
        and state.sell_orders.sum() > 0
    ):
        production_value = (state.sell_orders * state.prices).sum(axis=1)
    else:
        production_value = (state.production_capacity * state.prices).sum(axis=1)
    return aggregate_by_zone(state, production_value, config.N_ADMIN_ZONES)
