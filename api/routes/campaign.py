"""Campaign session endpoints."""

from fastapi import APIRouter, HTTPException
from api.schemas.campaign import (
    NewCampaignRequest, AdvanceTurnRequest,
    CampaignStateResponse, TurnResultResponse,
)
from api.services.campaign import CampaignSession, active_campaign
from api.services.session import session
import api.services.campaign as campaign_mod

router = APIRouter(prefix="/api/campaign", tags=["campaign"])


@router.post("/new", response_model=CampaignStateResponse)
def new_campaign(req: NewCampaignRequest):
    parties = req.parties if req.parties else list(session.parties.values())
    if len(parties) < 2:
        raise HTTPException(400, "Need at least 2 parties")

    try:
        campaign_mod.active_campaign = CampaignSession(
            party_schemas=list(parties),
            params_input=req.params,
            n_monte_carlo=req.n_monte_carlo,
            seed=req.seed,
            n_turns=req.n_turns,
        )
        return campaign_mod.active_campaign.get_state_response()
    except Exception as e:
        raise HTTPException(500, f"Failed to initialize campaign: {e}")


@router.get("/state", response_model=CampaignStateResponse)
def get_state():
    if campaign_mod.active_campaign is None:
        raise HTTPException(404, "No active campaign")
    return campaign_mod.active_campaign.get_state_response()


@router.post("/advance", response_model=TurnResultResponse)
def advance_turn(req: AdvanceTurnRequest):
    if campaign_mod.active_campaign is None:
        raise HTTPException(404, "No active campaign")
    camp = campaign_mod.active_campaign
    if camp.state.turn >= camp.n_turns:
        raise HTTPException(400, f"Campaign complete (turn {camp.state.turn}/{camp.n_turns})")

    try:
        return camp.advance_turn(req.actions, req.crises)
    except Exception as e:
        raise HTTPException(500, f"Turn failed: {e}")


@router.post("/reset", response_model=CampaignStateResponse)
def reset_campaign():
    if campaign_mod.active_campaign is None:
        raise HTTPException(404, "No active campaign")
    camp = campaign_mod.active_campaign
    campaign_mod.active_campaign = CampaignSession(
        party_schemas=camp.party_schemas,
        params_input=camp.params_input,
        n_monte_carlo=camp.n_monte_carlo,
        seed=camp.seed,
        n_turns=camp.n_turns,
    )
    return campaign_mod.active_campaign.get_state_response()


@router.get("/history")
def get_history():
    if campaign_mod.active_campaign is None:
        raise HTTPException(404, "No active campaign")
    return [tr.model_dump() for tr in campaign_mod.active_campaign.turn_results]
