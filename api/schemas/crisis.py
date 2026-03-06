"""Pydantic schemas for crisis management."""

from pydantic import BaseModel


class CrisisTemplate(BaseModel):
    name: str
    description: str
    affected_azs: list[int] | None = None
    salience_shifts: dict[str, float] = {}
    valence_effects: dict[str, float] | None = None
    awareness_boost: dict[str, float] | None = None
    tau_modifier: float = 0.0


class CrisisCreate(BaseModel):
    name: str
    turn: int = 0
    affected_azs: list[int] | None = None
    affected_lgas: list[int] | None = None
    salience_shifts: dict[str, float] = {}
    valence_effects: dict[str, float] | None = None
    awareness_boost: dict[str, float] | None = None
    tau_modifier: float = 0.0
    description: str = ""


class CrisisStored(CrisisCreate):
    id: int


class CrisisListResponse(BaseModel):
    crises: list[CrisisStored]
    count: int
