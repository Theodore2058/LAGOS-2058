"""Config and reference data endpoints."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from fastapi import APIRouter

from election_engine import ISSUE_NAMES, EngineParams
from election_engine.ethnic_affinity import ETHNIC_GROUPS
from election_engine.religious_affinity import RELIGIOUS_GROUPS
from election_engine.campaign_actions import (
    PC_COSTS, PC_INCOME_PER_TURN, PC_HOARDING_CAP,
    PC_FUNDRAISING_YIELD, PC_ETO_DIVIDEND_THRESHOLD,
    PC_ETO_DIVIDEND_AMOUNT, PC_ETO_DIVIDEND_CAP,
)
from api.schemas.config import (
    IssueNamesResponse, EngineParamsDefaults, EthnicGroupsResponse,
    ReligiousGroupsResponse, AdminZonesResponse, AdminZone,
    ActionTypesResponse, ActionTypeInfo, PCConstantsResponse,
)

router = APIRouter(prefix="/api", tags=["config"])

ADMIN_ZONES = {
    1: "Lagos (Southwest urban)",
    2: "Niger (Southwest rural)",
    3: "Confluence (South-Central)",
    4: "Littoral (South-South)",
    5: "Eastern (Southeast)",
    6: "Central (North-Central)",
    7: "Chad (Northeast)",
    8: "Savanna (Northwest)",
}

ACTION_DESCRIPTIONS = {
    "rally": "Hold a political rally. Boosts awareness and salience in target region. Language choice affects which issues get amplified.",
    "advertising": "Run advertising campaign via radio, TV, or internet. Budget determines reach and cost.",
    "manifesto": "Release or update party manifesto. Shifts up to 5 policy positions with credibility penalty for large changes.",
    "ground_game": "Deploy field operatives for door-to-door canvassing. Reduces abstention (tau) in target areas.",
    "endorsement": "Secure endorsement from a notable figure. Provides valence boost in endorser's region.",
    "ethnic_mobilization": "Mobilize along ethnic lines. Powerful but increases exposure risk.",
    "patronage": "Distribute patronage in target region. Boosts ceiling and awareness but carries exposure risk.",
    "opposition_research": "Investigate a rival party. May reduce their valence if successful.",
    "media": "Shape media narrative. Cheap but volatile — can backfire.",
    "eto_engagement": "Engage with Elected/Traditional/Opinion leaders. Builds institutional support scores.",
    "crisis_response": "Respond to an active crisis. Narrative quality determines valence impact.",
    "fundraising": "Raise funds. Yields +3 PC. Free to execute but limited effectiveness over time.",
    "poll": "Commission a poll. Tier 1-5 determines cost, accuracy, and detail level. Results arrive next turn.",
    "pledge": "Make a policy pledge on a specific dimension. Signals commitment but costs political capital.",
    "eto_intelligence": "Gather intelligence on ETO landscape in a target zone. Free but requires ETO score >= 5.0.",
}


@router.get("/issue-names", response_model=IssueNamesResponse)
def get_issue_names():
    return IssueNamesResponse(issue_names=list(ISSUE_NAMES), count=len(ISSUE_NAMES))


@router.get("/engine-params/defaults", response_model=EngineParamsDefaults)
def get_engine_params_defaults():
    defaults = EngineParams()
    return EngineParamsDefaults(
        q=defaults.q,
        beta_s=defaults.beta_s,
        alpha_e=defaults.alpha_e,
        alpha_r=defaults.alpha_r,
        scale=defaults.scale,
        tau_0=defaults.tau_0,
        tau_1=defaults.tau_1,
        tau_2=defaults.tau_2,
        beta_econ=defaults.beta_econ,
        kappa=defaults.kappa,
        sigma_national=defaults.sigma_national,
        sigma_regional=defaults.sigma_regional,
        sigma_turnout=defaults.sigma_turnout,
        sigma_turnout_regional=defaults.sigma_turnout_regional,
    )


@router.get("/ethnic-groups", response_model=EthnicGroupsResponse)
def get_ethnic_groups():
    return EthnicGroupsResponse(groups=list(ETHNIC_GROUPS), count=len(ETHNIC_GROUPS))


@router.get("/religious-groups", response_model=ReligiousGroupsResponse)
def get_religious_groups():
    return ReligiousGroupsResponse(groups=list(RELIGIOUS_GROUPS), count=len(RELIGIOUS_GROUPS))


@router.get("/admin-zones", response_model=AdminZonesResponse)
def get_admin_zones():
    zones = [AdminZone(id=k, name=v) for k, v in ADMIN_ZONES.items()]
    return AdminZonesResponse(zones=zones)


@router.get("/action-types", response_model=ActionTypesResponse)
def get_action_types():
    actions = [
        ActionTypeInfo(
            name=name,
            base_cost=cost,
            description=ACTION_DESCRIPTIONS.get(name, ""),
        )
        for name, cost in PC_COSTS.items()
    ]
    return ActionTypesResponse(action_types=actions)


@router.get("/pc-constants", response_model=PCConstantsResponse)
def get_pc_constants():
    return PCConstantsResponse(
        pc_income_per_turn=PC_INCOME_PER_TURN,
        pc_hoarding_cap=PC_HOARDING_CAP,
        pc_fundraising_yield=PC_FUNDRAISING_YIELD,
        pc_eto_dividend_threshold=PC_ETO_DIVIDEND_THRESHOLD,
        pc_eto_dividend_amount=PC_ETO_DIVIDEND_AMOUNT,
        pc_eto_dividend_cap=PC_ETO_DIVIDEND_CAP,
    )
