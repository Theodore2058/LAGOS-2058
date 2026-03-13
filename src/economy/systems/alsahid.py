"""
Al-Shahid Parallel Economy & Insurgency System.

Runs once per structural tick (monthly). Models territorial control dynamics,
service provision in controlled areas, trade surcharges on routes through
insurgent territory, government tax diversion, and almajiri recruitment from
unemployed youth.
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import (
    AlShahidMutations,
    EconomicState,
    SimConfig,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default config constants (overridden by SimConfig fields when available)
# ---------------------------------------------------------------------------

ALSAHID_TRADE_SURCHARGE_MIN: float = 0.30
ALSAHID_TRADE_SURCHARGE_MAX: float = 0.50
ALSAHID_TAX_DIVERSION_RATE: float = 0.40
ALSAHID_SERVICE_QUALITY: float = 0.60
ALMAJIRI_RECRUITMENT_RATE: float = 0.02

# Internal tuning
_CONTROL_GROWTH_RATE: float = 0.05      # max monthly organic growth
_CONTROL_DECAY_RATE: float = 0.02       # passive monthly decay
_POVERTY_THRESHOLD: float = 0.40        # unemployment ratio considered "high"
_STATE_CAPACITY_WEAKNESS: float = 0.50  # below this, state is "weak"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unemployment_rate(state: EconomicState) -> np.ndarray:
    """Per-LGA unemployment rate across all skill tiers. Shape (774,)."""
    pool = state.labor_pool.sum(axis=1)          # (774,)
    employed = state.labor_employed.sum(axis=1)   # (774,)
    # Avoid division by zero
    safe_pool = np.maximum(pool, 1.0)
    return np.clip((safe_pool - employed) / safe_pool, 0.0, 1.0)


# ---------------------------------------------------------------------------
# Main tick
# ---------------------------------------------------------------------------

def tick_alsahid(state: EconomicState, config: SimConfig) -> AlShahidMutations:
    """
    Execute one al-Shahid tick (monthly).

    Computes control expansion/contraction, service provision, trade
    surcharges, tax diversion, and almajiri recruitment.
    """

    n_lgas = config.N_LGAS

    # -- Pull config params --
    surcharge_min = config.ALSAHID_TRADE_SURCHARGE_MIN
    surcharge_max = config.ALSAHID_TRADE_SURCHARGE_MAX
    tax_diversion_rate = config.ALSAHID_TAX_DIVERSION_RATE
    service_quality = config.ALSAHID_SERVICE_QUALITY
    recruit_rate = config.ALMAJIRI_RECRUITMENT_RATE

    # -- Current state --
    control = state.alsahid_control.copy()           # (774,)
    bic = state.bic_enforcement_intensity             # scalar float
    # state_capacity is (12,) per ministry — use mean as per-LGA governance proxy
    mean_capacity = float(state.state_capacity.mean())
    state_cap_per_lga = np.full(n_lgas, mean_capacity, dtype=np.float64)
    unemp = _unemployment_rate(state)                    # (774,)

    # -------------------------------------------------------------------
    # 1. Control dynamics
    # -------------------------------------------------------------------
    # Growth is favoured where state is weak, poverty is high, and there
    # is already *some* al-Shahid presence (seed > 0).
    weakness = np.clip(1.0 - state_cap_per_lga, 0.0, 1.0)
    poverty_signal = np.clip(unemp / _POVERTY_THRESHOLD, 0.0, 1.0)

    growth = (
        control
        * _CONTROL_GROWTH_RATE
        * weakness
        * poverty_signal
    )

    # Enforcement pressure shrinks control
    enforcement_pressure = control * bic * _CONTROL_GROWTH_RATE

    # Passive decay
    decay = _CONTROL_DECAY_RATE * control

    # Net monthly change
    delta = growth - enforcement_pressure - decay
    control_new = np.clip(control + delta, 0.0, 1.0)

    logger.debug(
        "Al-Shahid control: mean=%.4f, max=%.4f, LGAs>0.5=%d",
        control_new.mean(),
        control_new.max(),
        int((control_new > 0.5).sum()),
    )

    # -------------------------------------------------------------------
    # 2. Service provision
    # -------------------------------------------------------------------
    service_provision_new = service_quality * control_new  # (774,)

    # -------------------------------------------------------------------
    # 3. Trade surcharges (per-LGA)
    # -------------------------------------------------------------------
    # Routes through an LGA with al-Shahid control incur surcharges.
    # Return a per-LGA surcharge array; the trade graph can look up
    # max(source_surcharge, dest_surcharge) when pricing a route.
    trade_surcharges_new = np.where(
        control_new > 0.0,
        surcharge_min + (surcharge_max - surcharge_min) * control_new,
        0.0,
    )  # (774,)

    # -------------------------------------------------------------------
    # 4. Tax diversion
    # -------------------------------------------------------------------
    # Proxy total government tax revenue from budget allocation.
    total_tax_proxy = float(state.budget_allocation.sum()) if (
        state.budget_allocation is not None
    ) else 0.0

    mean_control = float(control_new.sum()) / n_lgas
    tax_diversion_amount = tax_diversion_rate * mean_control * total_tax_proxy

    logger.debug(
        "Al-Shahid tax diversion: %.2f (%.1f%% of proxy revenue)",
        tax_diversion_amount,
        100.0 * mean_control * tax_diversion_rate,
    )

    # -------------------------------------------------------------------
    # 5. Almajiri recruitment
    # -------------------------------------------------------------------
    # Recruitment from unemployed youth in controlled areas.
    recruitment_per_lga = recruit_rate * unemp * control_new  # (774,)
    recruitment = float(recruitment_per_lga.sum())

    logger.debug("Al-Shahid recruitment this tick: %.1f", recruitment)

    return AlShahidMutations(
        control_new=control_new,
        service_provision_new=service_provision_new,
        trade_surcharges_new=trade_surcharges_new,
        tax_diversion_amount=tax_diversion_amount,
        recruitment=recruitment,
    )


# ---------------------------------------------------------------------------
# Apply mutations
# ---------------------------------------------------------------------------

def apply_alsahid_mutations(
    state: EconomicState,
    mutations: AlShahidMutations,
) -> None:
    """Write al-Shahid mutations back to the economic state."""
    state.alsahid_control[:] = mutations.control_new
    state.alsahid_service_provision[:] = mutations.service_provision_new
