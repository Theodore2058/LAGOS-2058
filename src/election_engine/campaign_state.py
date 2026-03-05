"""
Campaign layer data structures for the LAGOS-2058 election engine.

Defines:
- CampaignModifiers: arrays injected into the engine for one turn's computation
- ActiveEffect: a single campaign effect currently active in the simulation
- CampaignState: full mutable state of the campaign across all turns
- CrisisEvent: an exogenous event that shifts salience and/or valence
- Political Capital (PC): resource system constraining party actions per turn
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class CampaignModifiers:
    """
    Arrays injected into the election engine for one turn's computation.
    All default to neutral (no effect on static election).
    """
    awareness: np.ndarray | None = None       # (n_lga, J) multiplier on spatial utility
    salience_shift: np.ndarray | None = None   # (n_lga, 28) additive, pre-bounded
    valence: np.ndarray | None = None          # (n_lga, J) additive per-LGA valence
    ceiling_boost: np.ndarray | None = None    # (n_lga,) additive to turnout ceiling
    tau_modifier: np.ndarray | None = None     # (n_lga,) additive shift to tau_0

    @classmethod
    def neutral(cls) -> CampaignModifiers:
        """All None = engine behaves identically to pre-campaign code."""
        return cls(
            awareness=None,
            salience_shift=None,
            valence=None,
            ceiling_boost=None,
            tau_modifier=None,
        )

    @classmethod
    def zeros(cls, n_lga: int, n_parties: int, n_dims: int = 28) -> CampaignModifiers:
        """Explicit arrays with neutral values (awareness=1.0, others=0.0)."""
        return cls(
            awareness=np.ones((n_lga, n_parties), dtype=np.float32),
            salience_shift=np.zeros((n_lga, n_dims), dtype=np.float32),
            valence=np.zeros((n_lga, n_parties), dtype=np.float32),
            ceiling_boost=np.zeros(n_lga, dtype=np.float32),
            tau_modifier=np.zeros(n_lga, dtype=np.float32),
        )


@dataclass
class ActiveEffect:
    """A single campaign effect currently active in the simulation."""
    source_party: str
    source_action: str
    source_turn: int
    channel: str                    # "awareness" | "salience" | "valence" | "ceiling"

    # Targeting
    target_lgas: np.ndarray | None  # boolean mask (n_lga,), or None for national
    target_dimensions: list[int] | None  # issue dimension indices (salience only)
    target_party: str | None        # which party is affected

    # Effect data
    magnitude: float                # base strength of the effect

    # Keying for EMA overwrite
    effect_key: str
    # Format: "{source_party}:{channel}:{target_party}:{region_hash}:{dim_hash}"


@dataclass
class CampaignState:
    """Full mutable state of the campaign across all turns."""
    turn: int = 0
    n_lga: int = 774
    n_parties: int = 0
    party_names: list[str] = field(default_factory=list)

    # Core state: all active effects, keyed for O(1) overwrite lookup
    effects: dict[str, ActiveEffect] = field(default_factory=dict)

    # Awareness accumulator: (n_lga, J) -- grows monotonically.
    # Starts from base_awareness, only increases via campaign actions.
    awareness: np.ndarray | None = None

    # Party-level tracking
    exposure: dict[str, float] = field(default_factory=dict)
    cohesion: dict[str, float] = field(default_factory=dict)
    momentum: dict[str, int] = field(default_factory=dict)
    momentum_direction: dict[str, str] = field(default_factory=dict)

    # ETO engagement scores: (party, eto_category, az) -> score 0-10
    eto_scores: dict[tuple[str, str, int], float] = field(default_factory=dict)

    # Legislative pledges: party -> list of pledge dicts
    pledges: dict[str, list] = field(default_factory=dict)

    # Geographic concentration: party -> consecutive turns targeting same region
    concentration: dict[str, int] = field(default_factory=dict)

    # Previous turn's targeted regions per party (for concentration tracking)
    _prev_regions: dict[str, set[str]] = field(default_factory=dict)

    # Position history for credibility penalty
    last_positions: dict[str, np.ndarray] = field(default_factory=dict)

    # Previous turn national shares for momentum calculation
    previous_shares: dict[str, float] = field(default_factory=dict)

    # EMA blending parameter (for salience/valence/ceiling effects)
    ema_alpha: float = 0.65

    # Political Capital (PC) tracking: party -> current PC balance
    political_capital: dict[str, float] = field(default_factory=dict)

    # Scandal history: list of {party, turn, exposure_at_trigger, valence_penalty}
    scandal_history: list[dict] = field(default_factory=list)

    # Exposure tracking: turn of last new exposure per party (for decay)
    _last_exposure_turn: dict[str, int] = field(default_factory=dict)

    # Fundraising tracking: party -> {source: consecutive_count}
    _fundraising_history: dict[str, dict[str, int]] = field(default_factory=dict)

    # Region engagement tracking: party -> {az: last_turn_engaged}
    _region_engagement: dict[str, dict[int, int]] = field(default_factory=dict)

    # Momentum direction history: party -> list of last 3 directions
    _momentum_history: dict[str, list[str]] = field(default_factory=dict)

    # Action fatigue: party -> {action_type: consecutive_turn_count}
    _action_fatigue: dict[str, dict[str, int]] = field(default_factory=dict)

    # Poll results: list of {turn, party_shares: {party: share}, noise_level}
    poll_results: list[dict] = field(default_factory=list)

    # Active endorsements: {effect_key: {endorser_type, source_party, turn_applied}}
    _endorsements: dict[str, dict] = field(default_factory=dict)

    def raise_awareness(
        self,
        party_idx: int,
        lga_mask: np.ndarray | None,
        amount: np.ndarray | float,
    ) -> None:
        """
        Increase awareness for a party in specified LGAs.
        Awareness only goes UP, never down. Clipped to [0.30, 1.0].
        Negative amounts are clamped to 0 to enforce monotonicity.
        """
        if self.awareness is None:
            return
        # Enforce monotonicity: only allow positive increments
        if np.isscalar(amount):
            amount = max(float(amount), 0.0)
        else:
            amount = np.maximum(amount, 0.0)
        old = self.awareness[:, party_idx].copy()
        if lga_mask is None:
            self.awareness[:, party_idx] += amount
        else:
            if np.isscalar(amount):
                self.awareness[lga_mask, party_idx] += amount
            else:
                self.awareness[lga_mask, party_idx] += amount[lga_mask]
        # Ensure monotonicity: never decrease below old value
        np.maximum(self.awareness[:, party_idx], old,
                   out=self.awareness[:, party_idx])
        np.clip(
            self.awareness[:, party_idx], 0.60, 1.0,
            out=self.awareness[:, party_idx],
        )

    def apply_effect(self, effect: ActiveEffect) -> None:
        """
        Apply an effect using EMA blending for same-key overwrites.
        Awareness effects are handled via raise_awareness() instead.
        """
        key = effect.effect_key
        if key in self.effects:
            old = self.effects[key]
            effect.magnitude = (
                self.ema_alpha * effect.magnitude
                + (1.0 - self.ema_alpha) * old.magnitude
            )
        self.effects[key] = effect


@dataclass
class CrisisEvent:
    """An exogenous event that shifts salience and/or valence."""
    name: str
    turn: int
    affected_lgas: np.ndarray | None    # boolean mask, or None for national
    salience_shifts: dict[int, float]    # dimension_index -> shift magnitude
    valence_effects: dict[str, float] | None = None
    awareness_boost: dict[str, float] | None = None
    tau_modifier: float = 0.0            # national tau_0 shift
