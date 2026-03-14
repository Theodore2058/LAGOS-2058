"""
Enhancement Technology Diffusion System.

Models the spatial diffusion of biological enhancement technology across
774 LGAs. Adoption spreads from high-adoption areas to neighbors, modulated
by infrastructure quality, urbanization, and al-Shahid resistance.

Runs once per structural tick (monthly).
"""

from __future__ import annotations

import logging

import numpy as np

from src.economy.core.types import EconomicState, SimConfig

logger = logging.getLogger(__name__)

# Diffusion parameters
_BASE_DIFFUSION_RATE: float = 0.02      # Max 2% monthly spread to neighbors
_URBAN_ADOPTION_BONUS: float = 0.01     # Urban LGAs adopt 1% faster
_INFRA_THRESHOLD: float = 0.3           # Below this telecom quality, diffusion halved
_ALSAHID_RESISTANCE: float = 0.8        # Al-Shahid control reduces adoption by up to 80%
_NATURAL_ADOPTION_RATE: float = 0.005   # 0.5% autonomous monthly adoption growth
_SATURATION_DAMPENING: float = 2.0      # Logistic dampening near saturation


def tick_enhancement(
    state: EconomicState,
    config: SimConfig,
) -> np.ndarray:
    """
    Compute new enhancement adoption levels via spatial diffusion.

    Returns: (N,) updated adoption levels, clipped to [0, 1].
    """
    if state.enhancement_adoption is None:
        return np.zeros(config.N_LGAS, dtype=np.float64)

    N = config.N_LGAS
    current = state.enhancement_adoption.copy()  # (N,)

    # 1. Neighbor diffusion: each LGA's adoption pulled toward neighbor mean
    neighbor_mean = _compute_neighbor_mean(state, current)
    diffusion_pull = neighbor_mean - current  # positive = neighbors are ahead

    # Only diffuse where neighbors are ahead (no reverse diffusion)
    diffusion_pull = np.maximum(diffusion_pull, 0.0)

    # Modulate by infrastructure (telecom quality enables information spread)
    infra_mult = np.ones(N, dtype=np.float64)
    if state.infra_telecom_quality is not None:
        infra_mult = np.where(
            state.infra_telecom_quality < _INFRA_THRESHOLD,
            0.5,
            state.infra_telecom_quality,
        )

    # Al-Shahid resistance: controlled areas resist enhancement adoption
    alsahid_mult = np.ones(N, dtype=np.float64)
    if state.alsahid_control is not None:
        alsahid_mult = np.clip(1.0 - _ALSAHID_RESISTANCE * state.alsahid_control, 0.0, 1.0)

    # Logistic dampening: adoption slows as it approaches saturation
    headroom = 1.0 - current
    logistic_factor = headroom ** _SATURATION_DAMPENING

    # Combined diffusion
    diffusion = (
        _BASE_DIFFUSION_RATE * diffusion_pull
        * infra_mult * alsahid_mult * logistic_factor
    )

    # 2. Natural adoption growth (autonomous, not neighbor-dependent)
    natural = _NATURAL_ADOPTION_RATE * logistic_factor * alsahid_mult

    # 3. Urban bonus
    urban_bonus = np.zeros(N, dtype=np.float64)
    if state.land_area is not None and state.land_area.shape[1] > 2:
        # Urban fraction proxy: commercial + industrial land share
        total_land = np.maximum(state.land_area.sum(axis=1), 1.0)
        urban_frac = (state.land_area[:, 2] + state.land_area[:, 3]) / total_land
        urban_bonus = _URBAN_ADOPTION_BONUS * urban_frac * logistic_factor

    # Total change
    delta = diffusion + natural + urban_bonus
    new_adoption = np.clip(current + delta, 0.0, 1.0)

    logger.debug(
        "Enhancement diffusion: mean=%.3f -> %.3f, max_delta=%.4f",
        float(current.mean()), float(new_adoption.mean()), float(delta.max()),
    )

    return new_adoption


def apply_enhancement_diffusion(
    state: EconomicState,
    new_adoption: np.ndarray,
) -> None:
    """Apply updated enhancement adoption to state."""
    state.enhancement_adoption = new_adoption


def _compute_neighbor_mean(
    state: EconomicState,
    adoption: np.ndarray,
) -> np.ndarray:
    """Compute mean adoption of each LGA's zone-mates (same admin zone)."""
    N = adoption.shape[0]

    if state.admin_zone is not None:
        # Zone-based neighbor mean: each LGA sees the average of its zone
        zones = state.admin_zone
        n_zones = int(zones.max()) + 1
        zone_sums = np.zeros(n_zones, dtype=np.float64)
        zone_counts = np.zeros(n_zones, dtype=np.float64)
        np.add.at(zone_sums, zones, adoption)
        np.add.at(zone_counts, zones, 1.0)
        zone_means = zone_sums / np.maximum(zone_counts, 1.0)
        return zone_means[zones]

    # Fallback: global mean
    return np.full(N, adoption.mean(), dtype=np.float64)
