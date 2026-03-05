"""Pydantic schemas for party management."""

from pydantic import BaseModel, Field


class PartySchema(BaseModel):
    name: str
    full_name: str = ""
    positions: list[float] = Field(default_factory=lambda: [0.0] * 28)
    valence: float = 0.0
    leader_ethnicity: str = ""
    religious_alignment: str = ""
    demographic_coefficients: dict[str, dict[str, float]] | None = None
    regional_strongholds: dict[str, float] | None = None
    economic_positioning: float = 0.0
    color: str = "#888888"


class PartyListResponse(BaseModel):
    parties: list[PartySchema]
    count: int


class PartyImportRequest(BaseModel):
    parties: list[PartySchema]
