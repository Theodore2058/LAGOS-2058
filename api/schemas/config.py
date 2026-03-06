"""Pydantic schemas for config/data endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    engine: str


class IssueNamesResponse(BaseModel):
    issue_names: list[str]
    count: int


class EngineParamsDefaults(BaseModel):
    q: float
    beta_s: float
    alpha_e: float
    alpha_r: float
    scale: float
    tau_0: float
    tau_1: float
    tau_2: float
    beta_econ: float
    kappa: float
    sigma_national: float
    sigma_regional: float
    sigma_turnout: float
    sigma_turnout_regional: float


class EthnicGroupsResponse(BaseModel):
    groups: list[str]
    count: int


class ReligiousGroupsResponse(BaseModel):
    groups: list[str]
    count: int


class AdminZone(BaseModel):
    id: int
    name: str


class AdminZonesResponse(BaseModel):
    zones: list[AdminZone]


class ActionTypeInfo(BaseModel):
    name: str
    base_cost: int
    description: str


class ActionTypesResponse(BaseModel):
    action_types: list[ActionTypeInfo]


class PCConstantsResponse(BaseModel):
    pc_income_per_turn: int
    pc_hoarding_cap: int
    pc_fundraising_yield: int
    pc_eto_dividend_threshold: int
    pc_eto_dividend_amount: int
    pc_eto_dividend_cap: int


class LGAInfo(BaseModel):
    index: int
    name: str
    state: str
    az: int


class LGAListResponse(BaseModel):
    lgas: list[LGAInfo]
    count: int
