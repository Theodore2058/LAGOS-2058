"""
Global parameters, constants, and dataclasses for the LAGOS-2058 election engine.

Parameter reference table:
┌─────────────────────┬────────┬─────────┬──────────┬──────────────────────────────────────────┐
│ Parameter           │ Symbol │ Default │ Range    │ Effect                                   │
├─────────────────────┼────────┼─────────┼──────────┼──────────────────────────────────────────┤
│ Prox-Dir mix        │ q      │ 0.50    │ 0–1      │ 0=extremism pays, 1=centrism pays        │
│ Spatial sensitivity │ β_s    │ 1.00    │ 0–5      │ Higher → policy matters more vs identity │
│ Ethnic sensitivity  │ α_e    │ 2.50    │ 0–5+     │ Likely largest param in Nigerian context  │
│ Religious sensitiv. │ α_r    │ 1.50    │ 0–5      │ Lower than ethnic; negative matrix amps  │
│ Scale/rationality   │ λ      │ 1.00    │ 0.1–10   │ Higher → sharper; lower → mushier        │
│ Baseline abstention │ τ₀     │ 1.50    │ 0–5      │ Higher → lower turnout everywhere        │
│ Alienation          │ τ₁     │ 0.30    │ 0–2      │ More abstention when all parties distant │
│ Indifference        │ τ₂     │ 0.50    │ 0–2      │ More abstention when top parties similar │
│ Dirichlet conc.     │ κ      │ 200     │ 50–1000  │ Higher → less noise                      │
│ National shock SD   │ σ_nat  │ 0.10    │ 0–0.5    │ Bigger national swings                   │
│ Regional shock SD   │ σ_reg  │ 0.15    │ 0–0.5    │ Bigger regional swings                   │
│ LGA shock SD        │ σ_lga  │ 0.20    │ 0–0.5    │ More local randomness                    │
│ Turnout shock SD    │ σ_t    │ 0.00    │ 0–0.3    │ National turnout noise on logit scale     │
│ Turnout reg. SD     │ σ_t_r  │ 0.00    │ 0–0.3    │ Regional turnout noise (per admin zone)   │
└─────────────────────┴────────┴─────────┴──────────┴──────────────────────────────────────────┘
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np

# The 28 issue dimensions — all scales run -5 to +5
# Zero = Khalilian status quo or neutral midpoint
ISSUE_NAMES: list[str] = [
    "sharia_jurisdiction",       # 1  secular ↔ full Sharia
    "fiscal_autonomy",           # 2  centralism ↔ confederalism
    "chinese_relations",         # 3  Western pivot ↔ deepen WAFTA
    "bic_reform",                # 4  abolish ↔ preserve BIC
    "ethnic_quotas",             # 5  meritocracy ↔ affirmative action
    "fertility_policy",          # 6  population control ↔ pro-natalism
    "constitutional_structure",  # 7  parliamentary ↔ presidential
    "resource_revenue",          # 8  federal monopoly ↔ local control
    "housing",                   # 9  pure market ↔ state intervention
    "education",                 # 10 radical localism ↔ meritocratic centralism
    "labor_automation",          # 11 pro-capital ↔ pro-labor
    "military_role",             # 12 civilian control ↔ military guardianship
    "immigration",               # 13 open borders ↔ restrictionism
    "language_policy",           # 14 vernacular ↔ English supremacy
    "womens_rights",             # 15 traditional patriarchy ↔ aggressive feminism
    "traditional_authority",     # 16 marginalization ↔ formal integration
    "infrastructure",            # 17 targeted ↔ universal provision
    "land_tenure",               # 18 customary ↔ formalization
    "taxation",                  # 19 low tax ↔ high redistribution
    "agricultural_policy",       # 20 free market ↔ protectionist smallholder
    "biological_enhancement",    # 21 prohibition ↔ universal access
    "trade_policy",              # 22 autarky ↔ full openness
    "environmental_regulation",  # 23 growth first ↔ strong regulation
    "media_freedom",             # 24 state control ↔ full press freedom
    "healthcare",                # 25 pure market ↔ universal provision
    "pada_status",               # 26 anti-Padà ↔ Padà preservation
    "energy_policy",             # 27 fossil status quo ↔ green transition
    "az_restructuring",          # 28 return to 36+ states ↔ keep 8 AZs
]

N_ISSUES: int = 28  # D — total number of policy dimensions


@dataclass
class EngineParams:
    """Global simulation parameters with calibrated defaults."""

    # Spatial model
    q: float = 0.5          # Proximity-directional mix (0=directional, 1=proximity)
    beta_s: float = 3.0     # Spatial sensitivity (β_s) — scaled with √D normalization
    spatial_normalization: float = 0.0  # Divisor for spatial utility (0 = auto = √N_ISSUES)

    # Identity affinity
    alpha_e: float = 3.0    # Ethnic sensitivity (α_e) — primary vote driver in Nigerian context
    alpha_r: float = 2.0    # Religious sensitivity (α_r)

    # Multinomial logit
    scale: float = 1.5      # Softmax scale / rationality (λ). Higher = sharper choices

    # Turnout / abstention
    tau_0: float = 4.5      # Baseline abstention utility (τ₀) — high for post-authoritarian 1st election
    tau_1: float = 0.3      # Alienation strength (τ₁)
    tau_2: float = 0.5      # Indifference strength (τ₂)

    # Economic voting
    beta_econ: float = 0.3        # Economic voting sensitivity. Higher = local economy matters more

    # Noise model
    kappa: float = 200.0          # Dirichlet concentration (κ). Higher = less noise
    sigma_national: float = 0.10  # National shock SD (σ_nat)
    sigma_regional: float = 0.15  # Regional shock SD (σ_reg)
    sigma_lga: float = 0.20       # LGA shock SD (σ_lga)
    sigma_turnout: float = 0.0    # National turnout noise SD on logit scale. 0 = deterministic turnout
    sigma_turnout_regional: float = 0.0  # Regional turnout noise SD on logit scale (per admin zone)

    def __post_init__(self) -> None:
        # Auto-compute spatial normalization from issue dimensionality
        if self.spatial_normalization <= 0.0:
            self.spatial_normalization = float(np.sqrt(N_ISSUES))
        if not (0.0 <= self.q <= 1.0):
            raise ValueError(f"q must be in [0, 1], got {self.q}")
        if self.beta_s < 0:
            raise ValueError(f"beta_s must be >= 0, got {self.beta_s}")
        if self.alpha_e < 0:
            raise ValueError(f"alpha_e must be >= 0, got {self.alpha_e}")
        if self.alpha_r < 0:
            raise ValueError(f"alpha_r must be >= 0, got {self.alpha_r}")
        if self.scale <= 0:
            raise ValueError(f"scale must be > 0, got {self.scale}")
        if self.tau_0 < 0:
            raise ValueError(f"tau_0 must be >= 0, got {self.tau_0}")
        if self.tau_1 < 0:
            raise ValueError(f"tau_1 must be >= 0, got {self.tau_1}")
        if self.tau_2 < 0:
            raise ValueError(f"tau_2 must be >= 0, got {self.tau_2}")
        if self.beta_econ < 0:
            raise ValueError(f"beta_econ must be >= 0, got {self.beta_econ}")
        if self.kappa <= 0:
            raise ValueError(f"kappa must be > 0, got {self.kappa}")
        if self.sigma_national < 0:
            raise ValueError(f"sigma_national must be >= 0, got {self.sigma_national}")
        if self.sigma_regional < 0:
            raise ValueError(f"sigma_regional must be >= 0, got {self.sigma_regional}")
        if self.sigma_lga < 0:
            raise ValueError(f"sigma_lga must be >= 0, got {self.sigma_lga}")
        if self.sigma_turnout < 0:
            raise ValueError(f"sigma_turnout must be >= 0, got {self.sigma_turnout}")
        if self.sigma_turnout_regional < 0:
            raise ValueError(f"sigma_turnout_regional must be >= 0, got {self.sigma_turnout_regional}")


@dataclass
class Party:
    """A political party in the simulation.

    Parameters
    ----------
    name : str
        Short party name / acronym.
    positions : np.ndarray, shape (28,)
        Position on each issue dimension, scale -5 to +5.
    valence : float
        Baseline appeal (candidate quality, media presence, etc.).
        One party should typically be 0 as the reference.
    leader_ethnicity : str
        Key into ethnic affinity matrix.
    religious_alignment : str
        Key into religious affinity matrix.
    demographic_coefficients : dict, optional
        Maps demographic attribute → {value: coeff} for targeted appeal.
    regional_strongholds : dict, optional
        Maps Administrative Zone number (1-8) → additive utility bonus.
        Captures historical territorial bases of support, ground-level
        party organisation, and patron-client networks. Values are
        directly added to total utility for all voter types in the zone.
        Typical range: -1.0 (hostile territory) to +2.0 (core base).
    economic_positioning : float
        Party's economic orientation on a -1 to +1 scale.
        +1 = populist/pro-poor (benefits from economic grievance),
        -1 = pro-market/elite (benefits from prosperity).
        Zero = neutral. The actual utility modifier is:
            economic_positioning × lga_grievance_z × engine_param.
        Where lga_grievance_z is z-scored (mean 0, std 1).
    """

    name: str
    positions: np.ndarray              # shape (28,) — position on each issue, scale -5 to +5
    valence: float = 0.0               # Baseline valence advantage (one party must be 0)
    leader_ethnicity: str = ""         # Key into ethnic affinity matrix
    religious_alignment: str = ""      # Key into religious affinity matrix
    demographic_coefficients: Optional[dict] = None  # γ_mj terms for demographic utility
    regional_strongholds: Optional[dict] = None  # AZ number → utility bonus
    economic_positioning: float = 0.0  # -1=pro-market, +1=populist/pro-poor

    def __post_init__(self) -> None:
        self.positions = np.asarray(self.positions, dtype=float)
        if self.positions.shape != (N_ISSUES,):
            raise ValueError(
                f"Party '{self.name}' positions must have shape ({N_ISSUES},), "
                f"got {self.positions.shape}"
            )
        if np.any(np.abs(self.positions) > 5.0):
            raise ValueError(
                f"Party '{self.name}' positions must be in [-5, +5]; "
                f"found values: {self.positions[np.abs(self.positions) > 5]}"
            )
        if self.regional_strongholds is not None:
            for az, bonus in self.regional_strongholds.items():
                if not isinstance(az, (int, float)):
                    raise ValueError(
                        f"Party '{self.name}' regional_strongholds keys must be "
                        f"integers (AZ numbers), got {type(az).__name__}: {az}"
                    )


@dataclass
class ElectionConfig:
    """Full configuration for one election run."""

    params: EngineParams
    parties: list  # list[Party]
    issue_names: list[str] = field(default_factory=lambda: list(ISSUE_NAMES))
    n_monte_carlo: int = 1000

    def __post_init__(self) -> None:
        if len(self.issue_names) != N_ISSUES:
            raise ValueError(
                f"issue_names must have {N_ISSUES} entries, got {len(self.issue_names)}"
            )
        if not self.parties:
            raise ValueError("ElectionConfig must have at least one party")

    @property
    def n_parties(self) -> int:
        return len(self.parties)
