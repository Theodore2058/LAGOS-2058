"""Crisis management endpoints."""

from fastapi import APIRouter, HTTPException
from api.schemas.crisis import CrisisTemplate, CrisisCreate, CrisisStored, CrisisListResponse

router = APIRouter(prefix="/api/crises", tags=["crises"])

# In-memory crisis storage
_crises: list[CrisisStored] = []
_next_id = 1

CRISIS_TEMPLATES: list[CrisisTemplate] = [
    CrisisTemplate(
        name="Economic Shock",
        description="Major economic downturn. Boosts fiscal/taxation salience, hurts incumbent valence.",
        salience_shifts={"18": 2.0, "1": 1.5, "10": 1.0},
        tau_modifier=-0.3,
    ),
    CrisisTemplate(
        name="Ethnic Violence",
        description="Inter-ethnic violence outbreak. Boosts ethnic_quotas salience, hurts parties in affected region.",
        salience_shifts={"4": 2.5, "11": 1.0},
        affected_azs=[6, 7],
        tau_modifier=-0.5,
    ),
    CrisisTemplate(
        name="Security Crisis",
        description="Major security incident. Boosts military_role salience, helps security-focused parties.",
        salience_shifts={"11": 2.5, "12": 1.5},
        tau_modifier=-0.2,
    ),
    CrisisTemplate(
        name="Corruption Scandal",
        description="Major corruption scandal. Hurts named party's valence significantly.",
        salience_shifts={"23": 1.5, "18": 1.0},
    ),
    CrisisTemplate(
        name="Infrastructure Failure",
        description="Major infrastructure collapse. Boosts infrastructure/housing salience in affected region.",
        salience_shifts={"16": 2.5, "8": 2.0, "26": 1.0},
        affected_azs=[1],
    ),
    CrisisTemplate(
        name="Religious Tension",
        description="Escalation of religious tensions. Boosts sharia_jurisdiction salience.",
        salience_shifts={"0": 2.5, "14": 1.0},
        affected_azs=[7, 8],
        tau_modifier=-0.3,
    ),
    CrisisTemplate(
        name="WAFTA Trade Disruption",
        description="Disruption to WAFTA trade agreement. Boosts chinese_relations/trade_policy salience.",
        salience_shifts={"2": 2.0, "21": 2.0, "19": 1.0},
    ),
    CrisisTemplate(
        name="Natural Disaster",
        description="Natural disaster. National awareness spike, turnout depression in affected region.",
        salience_shifts={"16": 1.5, "24": 1.0, "22": 1.0},
        tau_modifier=0.5,
        affected_azs=[4],
    ),
    CrisisTemplate(
        name="Pada Controversy",
        description="Controversy over Pada community status. Boosts pada_status salience.",
        salience_shifts={"25": 3.0, "4": 1.0},
    ),
]


@router.get("/templates")
def get_templates():
    return [t.model_dump() for t in CRISIS_TEMPLATES]


@router.get("", response_model=CrisisListResponse)
def list_crises():
    return CrisisListResponse(crises=_crises, count=len(_crises))


@router.post("", response_model=CrisisStored, status_code=201)
def create_crisis(crisis: CrisisCreate):
    global _next_id
    stored = CrisisStored(id=_next_id, **crisis.model_dump())
    _next_id += 1
    _crises.append(stored)
    return stored


@router.put("/{crisis_id}", response_model=CrisisStored)
def update_crisis(crisis_id: int, crisis: CrisisCreate):
    for i, c in enumerate(_crises):
        if c.id == crisis_id:
            updated = CrisisStored(id=crisis_id, **crisis.model_dump())
            _crises[i] = updated
            return updated
    raise HTTPException(404, f"Crisis {crisis_id} not found")


@router.delete("/{crisis_id}", status_code=204)
def delete_crisis(crisis_id: int):
    global _crises
    _crises = [c for c in _crises if c.id != crisis_id]
