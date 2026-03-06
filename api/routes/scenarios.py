"""Scenario save/load/compare endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from api.services.session import session
from api.services.campaign import active_campaign
import api.services.campaign as campaign_mod

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

# In-memory scenario storage
_scenarios: dict[str, dict] = {}


class SaveScenarioRequest(BaseModel):
    name: str


@router.post("/save")
def save_scenario(req: SaveScenarioRequest):
    parties = [p.model_dump() for p in session.parties.values()]
    campaign_history = []
    if campaign_mod.active_campaign:
        campaign_history = [tr.model_dump() for tr in campaign_mod.active_campaign.turn_results]

    _scenarios[req.name] = {
        "name": req.name,
        "parties": parties,
        "campaign_history": campaign_history,
    }
    return {"saved": req.name, "total_scenarios": len(_scenarios)}


@router.get("/list")
def list_scenarios():
    return [{"name": name, "n_parties": len(s["parties"]), "n_turns": len(s["campaign_history"])}
            for name, s in _scenarios.items()]


@router.get("/{name}")
def get_scenario(name: str):
    if name not in _scenarios:
        raise HTTPException(404, f"Scenario '{name}' not found")
    return _scenarios[name]


@router.delete("/{name}")
def delete_scenario(name: str):
    if name not in _scenarios:
        raise HTTPException(404)
    del _scenarios[name]
    return {"deleted": name}


@router.get("/compare/{name_a}/{name_b}")
def compare_scenarios(name_a: str, name_b: str):
    if name_a not in _scenarios or name_b not in _scenarios:
        raise HTTPException(404, "One or both scenarios not found")

    a = _scenarios[name_a]
    b = _scenarios[name_b]

    # Compare final results if campaign histories exist
    result = {"scenario_a": name_a, "scenario_b": name_b, "delta": {}}

    hist_a = a.get("campaign_history", [])
    hist_b = b.get("campaign_history", [])

    if hist_a and hist_b:
        final_a = hist_a[-1].get("national_vote_shares", {})
        final_b = hist_b[-1].get("national_vote_shares", {})
        all_parties = set(list(final_a.keys()) + list(final_b.keys()))
        delta = {}
        for p in all_parties:
            va = final_a.get(p, 0)
            vb = final_b.get(p, 0)
            delta[p] = {"a": round(va, 4), "b": round(vb, 4), "diff": round(vb - va, 4)}
        result["delta"] = delta

        seats_a = hist_a[-1].get("seat_counts", {})
        seats_b = hist_b[-1].get("seat_counts", {})
        seat_delta = {}
        for p in all_parties:
            sa = seats_a.get(p, 0)
            sb = seats_b.get(p, 0)
            seat_delta[p] = {"a": sa, "b": sb, "diff": round(sb - sa, 1)}
        result["seat_delta"] = seat_delta

    return result


@router.get("/export/session")
def export_session():
    """Export full session state as JSON."""
    data = {
        "parties": [p.model_dump() for p in session.parties.values()],
        "campaign_history": [],
        "scenarios": {k: v for k, v in _scenarios.items()},
    }
    if campaign_mod.active_campaign:
        data["campaign_history"] = [tr.model_dump() for tr in campaign_mod.active_campaign.turn_results]

    return JSONResponse(content=data, headers={"Content-Disposition": "attachment; filename=lagos2058_session.json"})


class ImportSessionRequest(BaseModel):
    parties: list[dict] = []


@router.post("/import/session")
def import_session(req: ImportSessionRequest):
    """Import parties from a session file."""
    from api.schemas.party import PartySchema
    for pd_dict in req.parties:
        p = PartySchema(**pd_dict)
        session.parties[p.name] = p
    return {"imported": len(req.parties)}
