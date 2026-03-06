"""Election endpoints."""

from fastapi import APIRouter, HTTPException
from api.schemas.election import RunElectionRequest, ElectionResultsResponse
from api.services.election import run_and_transform
from api.services.session import session

router = APIRouter(prefix="/api/election", tags=["election"])


@router.post("/run", response_model=ElectionResultsResponse)
def run_election_endpoint(req: RunElectionRequest):
    parties = req.parties if req.parties else list(session.parties.values())
    if len(parties) < 2:
        raise HTTPException(400, "Need at least 2 parties to run an election")

    try:
        results = run_and_transform(parties, req.params, req.n_monte_carlo, req.seed)
        return results
    except Exception as e:
        raise HTTPException(500, f"Election failed: {str(e)}")
