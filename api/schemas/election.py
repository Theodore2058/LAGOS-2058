"""Pydantic schemas for election endpoints."""

from pydantic import BaseModel
from api.schemas.party import PartySchema


class EngineParamsInput(BaseModel):
    q: float = 0.5
    beta_s: float = 3.0
    alpha_e: float = 3.0
    alpha_r: float = 2.0
    scale: float = 1.5
    tau_0: float = 4.5
    tau_1: float = 0.3
    tau_2: float = 0.5
    beta_econ: float = 0.3
    kappa: float = 200.0
    sigma_national: float = 0.10
    sigma_regional: float = 0.15
    sigma_turnout: float = 0.0
    sigma_turnout_regional: float = 0.0


class RunElectionRequest(BaseModel):
    params: EngineParamsInput = EngineParamsInput()
    parties: list[PartySchema] = []
    n_monte_carlo: int = 100
    seed: int | None = None


class SpreadCheckResult(BaseModel):
    states_above_25: int
    met: bool


class ZonalResult(BaseModel):
    az: int
    az_name: str
    turnout: float
    vote_shares: dict[str, float]
    winner: str


class StateResult(BaseModel):
    state: str
    az: int
    turnout: float
    vote_shares: dict[str, float]
    winner: str


class LGAResultRow(BaseModel):
    lga: str
    state: str
    az: int
    turnout: float
    vote_shares: dict[str, float]
    winner: str


class SwingLGA(BaseModel):
    lga: str
    state: str
    margin: float
    top_parties: list[str]


class ElectionResultsResponse(BaseModel):
    national_vote_shares: dict[str, float]
    national_vote_counts: dict[str, int]
    national_turnout: float
    seat_counts: dict[str, float]
    seat_std: dict[str, float]
    win_probability: dict[str, float]
    enp: float
    spread_check: dict[str, SpreadCheckResult]
    zonal_results: list[ZonalResult]
    state_results: list[StateResult]
    lga_results: list[LGAResultRow]
    swing_lgas: list[SwingLGA]
