"""Party CRUD endpoints."""

from fastapi import APIRouter, HTTPException

from api.schemas.party import PartySchema, PartyListResponse, PartyImportRequest
from api.services.session import session
from api.services.party_loader import load_example_parties

router = APIRouter(prefix="/api/parties", tags=["parties"])


@router.get("", response_model=PartyListResponse)
def list_parties():
    parties = list(session.parties.values())
    return PartyListResponse(parties=parties, count=len(parties))


@router.post("", response_model=PartySchema, status_code=201)
def create_party(party: PartySchema):
    if party.name in session.parties:
        raise HTTPException(400, f"Party '{party.name}' already exists")
    if len(party.positions) != 28:
        raise HTTPException(400, f"Positions must have exactly 28 values, got {len(party.positions)}")
    session.parties[party.name] = party
    return party


@router.put("/{name}", response_model=PartySchema)
def update_party(name: str, party: PartySchema):
    if name not in session.parties:
        raise HTTPException(404, f"Party '{name}' not found")
    if len(party.positions) != 28:
        raise HTTPException(400, f"Positions must have exactly 28 values")
    # If name changed, remove old key
    if party.name != name:
        if party.name in session.parties:
            raise HTTPException(400, f"Party '{party.name}' already exists")
        del session.parties[name]
    session.parties[party.name] = party
    return party


@router.delete("/{name}", status_code=204)
def delete_party(name: str):
    if name not in session.parties:
        raise HTTPException(404, f"Party '{name}' not found")
    del session.parties[name]


@router.post("/load-examples", response_model=PartyListResponse)
def load_examples():
    examples = load_example_parties()
    for p in examples:
        session.parties[p.name] = p
    parties = list(session.parties.values())
    return PartyListResponse(parties=parties, count=len(parties))


@router.post("/import", response_model=PartyListResponse)
def import_parties(req: PartyImportRequest):
    for p in req.parties:
        session.parties[p.name] = p
    parties = list(session.parties.values())
    return PartyListResponse(parties=parties, count=len(parties))


@router.get("/export", response_model=PartyListResponse)
def export_parties():
    parties = list(session.parties.values())
    return PartyListResponse(parties=parties, count=len(parties))
