"""Campaign session service — manages turn-by-turn campaign state."""

from pathlib import Path
import numpy as np
import pandas as pd

from election_engine.config import Party, EngineParams, ElectionConfig
from election_engine.campaign import (
    process_pc_income, validate_and_deduct_pc, apply_crisis, update_post_turn,
)
from election_engine.campaign_actions import (
    ActionSpec, resolve_action, compute_action_cost,
    ACTION_RESOLUTION_ORDER, apply_synergies, update_action_fatigue,
    get_fatigue_multiplier,
)
from election_engine.campaign_modifiers import compile_modifiers
from election_engine.campaign_state import CampaignState, CrisisEvent
from election_engine.data_loader import load_lga_data
from election_engine.election import run_election
from election_engine.salience import compute_base_awareness

from api.schemas.party import PartySchema
from api.schemas.election import EngineParamsInput
from api.schemas.campaign import (
    ActionInput, CrisisInput, PartyStatus,
    CampaignStateResponse, TurnResultResponse,
)
from api.services.election import party_schema_to_engine, params_to_engine

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "nigeria_lga_polsim_2058.xlsx"

PHASE_NAMES = {
    (1, 3): "Foundation",
    (4, 6): "Expansion",
    (7, 9): "Intensification",
    (10, 12): "Final Push",
}


def get_phase(turn: int) -> str:
    for (lo, hi), name in PHASE_NAMES.items():
        if lo <= turn <= hi:
            return name
    return "Unknown"


class CampaignSession:
    def __init__(self, party_schemas: list[PartySchema], params_input: EngineParamsInput,
                 n_monte_carlo: int, seed: int | None, n_turns: int):
        self.party_schemas = party_schemas
        self.params_input = params_input
        self.engine_parties = [party_schema_to_engine(p) for p in party_schemas]
        self.engine_params = params_to_engine(params_input)
        # Use lower tau for campaign mode
        self.engine_params.tau_0 = min(self.engine_params.tau_0, 3.0)
        self.n_monte_carlo = n_monte_carlo
        self.seed = seed
        self.n_turns = n_turns
        self.party_names = [p.name for p in self.engine_parties]

        # Load data
        self.lga_data = load_lga_data(str(DATA_PATH))
        df = self.lga_data.df

        # Add AZ columns if needed
        if "Administrative Zone" in df.columns:
            _az = df["Administrative Zone"].fillna(0).astype(int)
            for i in range(1, 9):
                col = f"AZ {i}"
                if col not in df.columns:
                    df[col] = (_az == i).astype(float)
            self.lga_data.df = df

        if "Colonial Era Region" in df.columns:
            _cr = df["Colonial Era Region"].fillna("").astype(str).str.strip()
            for name, val in [("Colonial Western", "Western"), ("Colonial Eastern", "Eastern"), ("Colonial Mid-Western", "Mid-Western")]:
                if name not in df.columns:
                    df[name] = (_cr == val).astype(float)
            self.lga_data.df = df

        self.config = ElectionConfig(
            params=self.engine_params, parties=self.engine_parties,
            n_monte_carlo=n_monte_carlo,
        )

        # Initialize campaign state
        n_lga = len(df)
        self.state = CampaignState(
            turn=1, n_lga=n_lga, n_parties=len(self.party_names),
            party_names=list(self.party_names),
        )
        self.state.awareness = compute_base_awareness(self.engine_parties, df)
        for p in self.party_names:
            self.state.cohesion[p] = 10.0
            self.state.political_capital[p] = 0.0
        for party in self.engine_parties:
            self.state.last_positions[party.name] = party.positions.copy()

        # Give turn-1 PC income so the UI shows available budget immediately
        process_pc_income(self.state)

        self.rng = np.random.default_rng(seed) if seed else np.random.default_rng()
        self.history: list[dict] = []
        self.turn_results: list[TurnResultResponse] = []

    def get_state_response(self) -> CampaignStateResponse:
        party_statuses = []
        for pname in self.party_names:
            last_share = self.state.previous_shares.get(pname, 0.0)
            last_seats = 0.0
            if self.history:
                last_result = self.history[-1]
                mc = last_result.get("mc_aggregated", {})
                seat_stats = mc.get("seat_stats")
                if seat_stats is not None:
                    row = seat_stats[seat_stats["Party"] == pname]
                    if len(row) > 0:
                        last_seats = float(row.iloc[0]["Mean Seats"])

            party_statuses.append(PartyStatus(
                name=pname,
                pc=self.state.political_capital.get(pname, 0.0),
                cohesion=self.state.cohesion.get(pname, 10.0),
                exposure=self.state.exposure.get(pname, 0.0),
                momentum=self.state.momentum.get(pname, 0),
                momentum_direction=self.state.momentum_direction.get(pname, "stable"),
                vote_share=round(last_share, 4),
                seats=round(last_seats, 1),
            ))

        return CampaignStateResponse(
            turn=self.state.turn,
            n_turns=self.n_turns,
            phase=get_phase(self.state.turn),
            party_statuses=party_statuses,
            scandal_history=self.state.scandal_history,
            poll_results=self.state.poll_results,
        )

    def advance_turn(self, action_inputs: list[ActionInput],
                     crisis_inputs: list[CrisisInput]) -> TurnResultResponse:
        df = self.lga_data.df
        n_lga = len(df)

        # Deliver pending polls
        delivered = [p for p in self.state.pending_polls if p["turn_delivered"] <= self.state.turn]
        if delivered:
            self.state.poll_results.extend(delivered)
            self.state.pending_polls = [p for p in self.state.pending_polls if p["turn_delivered"] > self.state.turn]

        # Apply crises
        for ci in crisis_inputs:
            salience = {int(k): v for k, v in ci.salience_shifts.items()}
            affected = None
            if ci.affected_azs:
                az_col = df.get("Administrative Zone", pd.Series(dtype=int))
                affected = np.zeros(n_lga, dtype=bool)
                for az_id in ci.affected_azs:
                    affected |= (az_col == az_id).values
            elif ci.affected_lgas:
                affected = np.zeros(n_lga, dtype=bool)
                for idx in ci.affected_lgas:
                    if 0 <= idx < n_lga:
                        affected[idx] = True

            crisis = CrisisEvent(
                name=ci.name,
                turn=self.state.turn,
                affected_lgas=affected,
                salience_shifts=salience,
                valence_effects=ci.valence_effects,
                awareness_boost=ci.awareness_boost,
                tau_modifier=ci.tau_modifier,
            )
            apply_crisis(crisis, self.state, df)

        # Convert actions
        turn_actions = []
        actions_log = []
        for ai in action_inputs:
            target = None
            if ai.target_azs:
                az_col = df.get("Administrative Zone", pd.Series(dtype=int))
                target = np.zeros(n_lga, dtype=bool)
                for az_id in ai.target_azs:
                    target |= (az_col == az_id).values
            elif ai.target_lgas:
                target = np.zeros(n_lga, dtype=bool)
                for idx in ai.target_lgas:
                    if 0 <= idx < n_lga:
                        target[idx] = True

            params = dict(ai.parameters)
            if ai.target_party:
                params["target_party"] = ai.target_party

            spec = ActionSpec(
                party=ai.party,
                action_type=ai.action_type,
                target_lgas=target,
                language=ai.language,
                params=params,
            )
            turn_actions.append(spec)
            actions_log.append({
                "party": ai.party,
                "action_type": ai.action_type,
                "cost": compute_action_cost(ai.action_type, params),
            })

        # Validate PC
        turn_actions = validate_and_deduct_pc(self.state, turn_actions)

        # Resolve actions
        turn_actions_sorted = sorted(
            turn_actions,
            key=lambda a: ACTION_RESOLUTION_ORDER.get(a.action_type, 3),
        )
        for action in turn_actions_sorted:
            fatigue_mult = get_fatigue_multiplier(self.state, action.party, action.action_type)
            if fatigue_mult < 1.0:
                action = ActionSpec(
                    party=action.party,
                    action_type=action.action_type,
                    target_lgas=action.target_lgas,
                    language=action.language,
                    params={**action.params, "_fatigue_mult": fatigue_mult},
                )
            resolve_action(action, self.state, df, self.config)

        synergy_log = apply_synergies(turn_actions_sorted, self.state)
        update_action_fatigue(self.state, turn_actions_sorted)

        # Run election
        modifiers = compile_modifiers(self.state, df)
        result = run_election(
            str(DATA_PATH), self.config,
            campaign_modifiers=modifiers,
            seed=self.seed, verbose=False,
        )
        result["pc_state"] = dict(self.state.political_capital)
        result["_parties"] = self.engine_parties
        self.history.append(result)

        # Post-turn updates
        post_log = update_post_turn(
            self.state, result, turn_actions_sorted,
            lga_data=df, rng=self.rng,
        )

        # Extract results for response
        summary = result.get("summary", {})
        mc = result.get("mc_aggregated", {})

        national_shares = {k: round(v, 6) for k, v in summary.get("national_shares", {}).items()}
        turnout = round(float(summary.get("national_turnout", 0)), 4)

        seat_counts = {}
        seat_stats = mc.get("seat_stats")
        if seat_stats is not None:
            for _, row in seat_stats.iterrows():
                seat_counts[row["Party"]] = round(float(row["Mean Seats"]), 1)

        # Serialize synergy log
        synergies_serializable = []
        for s in synergy_log:
            synergies_serializable.append({
                "party": s.get("party", ""),
                "actions": s.get("actions", []),
                "channel": s.get("channel", ""),
                "magnitude": float(s.get("magnitude", 0)),
            })

        scandals = post_log.get("scandals", [])
        scandals_serializable = []
        for sc in scandals:
            scandals_serializable.append({
                "party": sc.get("party", ""),
                "exposure": round(float(sc.get("exposure_at_trigger", 0)), 2),
                "valence_penalty": round(float(sc.get("valence_penalty", 0)), 2),
                "pc_damage": int(sc.get("pc_damage", 0)),
            })

        processed_turn = self.state.turn
        self.state.turn += 1  # Advance to next turn for state response

        # Give next turn's PC income so the UI shows available budget
        if self.state.turn <= self.n_turns:
            process_pc_income(self.state)

        turn_result = TurnResultResponse(
            turn=processed_turn,
            state=self.get_state_response(),
            national_vote_shares=national_shares,
            national_turnout=turnout,
            seat_counts=seat_counts,
            actions_resolved=actions_log,
            synergies=synergies_serializable,
            scandals=scandals_serializable,
        )
        self.turn_results.append(turn_result)
        return turn_result


# Singleton campaign session
active_campaign: CampaignSession | None = None
