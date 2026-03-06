"""Pydantic schemas for campaign endpoints."""

from pydantic import BaseModel
from api.schemas.party import PartySchema
from api.schemas.election import EngineParamsInput


class ActionInput(BaseModel):
    party: str
    action_type: str
    target_lgas: list[int] | None = None
    target_azs: list[int] | None = None
    target_districts: list[str] | None = None
    target_party: str | None = None
    language: str = "english"
    parameters: dict = {}


class CrisisInput(BaseModel):
    name: str
    turn: int = 0
    affected_azs: list[int] | None = None
    affected_lgas: list[int] | None = None
    salience_shifts: dict[str, float] = {}
    valence_effects: dict[str, float] | None = None
    awareness_boost: dict[str, float] | None = None
    tau_modifier: float = 0.0
    description: str = ""


class NewCampaignRequest(BaseModel):
    parties: list[PartySchema] = []
    params: EngineParamsInput = EngineParamsInput()
    n_monte_carlo: int = 5
    seed: int | None = None
    n_turns: int = 12


class AdvanceTurnRequest(BaseModel):
    actions: list[ActionInput] = []
    crises: list[CrisisInput] = []


class PartyStatus(BaseModel):
    name: str
    pc: float
    cohesion: float
    exposure: float
    momentum: int
    momentum_direction: str
    vote_share: float
    seats: float
    awareness: float  # mean awareness across all LGAs (0-1)
    eto_score: float  # mean ETO score across all categories/zones


class CampaignStateResponse(BaseModel):
    turn: int
    n_turns: int
    phase: str
    party_statuses: list[PartyStatus]
    scandal_history: list[dict]
    poll_results: list[dict]


class TurnResultResponse(BaseModel):
    turn: int
    state: CampaignStateResponse
    national_vote_shares: dict[str, float]
    national_turnout: float
    seat_counts: dict[str, float]
    actions_resolved: list[dict]
    synergies: list[dict]
    scandals: list[dict]
