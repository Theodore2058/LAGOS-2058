"""
Campaign turn loop orchestrator for the LAGOS-2058 election engine.

Runs a multi-turn campaign simulation where actions modify the engine's
inputs -- what voters know (awareness), what they care about (salience),
how trustworthy parties seem (valence), and whether they can vote (ceiling).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .campaign_actions import (
    ActionSpec, resolve_action, compute_action_cost,
    PC_INCOME_PER_TURN, PC_HOARDING_CAP, PC_FUNDRAISING_YIELD,
    PC_ETO_DIVIDEND_THRESHOLD, PC_ETO_DIVIDEND_AMOUNT, PC_ETO_DIVIDEND_CAP,
)
from .campaign_modifiers import compile_modifiers
from .campaign_state import CampaignState, CampaignModifiers, CrisisEvent, ActiveEffect
from .config import ElectionConfig
from .data_loader import load_lga_data
from .election import run_election
from .salience import compute_base_awareness

logger = logging.getLogger(__name__)


def process_pc_income(state: CampaignState) -> dict[str, dict]:
    """
    Process start-of-turn political capital: hoarding cap, income, ETO dividends.

    Returns a dict of {party: {"cap_lost": ..., "income": ..., "eto_dividend": ..., "balance": ...}}
    for logging/display purposes.
    """
    pc_log: dict[str, dict] = {}

    for party_name in state.party_names:
        old_balance = state.political_capital.get(party_name, 0.0)
        log_entry: dict[str, float] = {"old_balance": old_balance}

        # 1. Hoarding cap: lose excess above PC_HOARDING_CAP before income
        cap_lost = max(0.0, old_balance - PC_HOARDING_CAP)
        balance = min(old_balance, PC_HOARDING_CAP)
        log_entry["cap_lost"] = cap_lost

        # 2. Unconditional income
        balance += PC_INCOME_PER_TURN
        log_entry["income"] = PC_INCOME_PER_TURN

        # 3. Economic ETO dividends
        eto_dividend = 0
        for (p, cat, az), score in state.eto_scores.items():
            if p == party_name and cat == "economic" and score >= PC_ETO_DIVIDEND_THRESHOLD:
                eto_dividend += PC_ETO_DIVIDEND_AMOUNT
        eto_dividend = min(eto_dividend, PC_ETO_DIVIDEND_CAP)
        balance += eto_dividend
        log_entry["eto_dividend"] = eto_dividend

        state.political_capital[party_name] = balance
        log_entry["balance"] = balance
        pc_log[party_name] = log_entry

    return pc_log


def validate_and_deduct_pc(
    state: CampaignState,
    turn_actions: list[ActionSpec],
    max_actions_per_party: int = 3,
) -> list[ActionSpec]:
    """
    Validate that each party can afford its actions and deduct PC.

    Actions are processed in order. If a party can't afford an action,
    it is skipped (logged as warning). Fundraising generates PC immediately.
    Each party is limited to max_actions_per_party actions per turn.

    Returns the list of affordable actions (may be shorter than input).
    """
    affordable: list[ActionSpec] = []
    action_counts: dict[str, int] = {}

    for action in turn_actions:
        party = action.party

        # Check action limit
        count = action_counts.get(party, 0)
        if count >= max_actions_per_party:
            logger.warning(
                "  %s hit action limit (%d/%d) — %s skipped",
                party, count, max_actions_per_party, action.action_type,
            )
            continue

        cost = compute_action_cost(action.action_type, action.params)
        balance = state.political_capital.get(party, 0.0)

        if cost > balance:
            logger.warning(
                "  %s cannot afford %s (cost=%d, balance=%.0f) — skipped",
                party, action.action_type, cost, balance,
            )
            continue

        # Deduct cost
        state.political_capital[party] = balance - cost
        affordable.append(action)
        action_counts[party] = count + 1

        # Fundraising immediately generates PC
        if action.action_type == "fundraising":
            state.political_capital[party] += PC_FUNDRAISING_YIELD
            logger.info(
                "  %s fundraising: +%d PC (balance: %.0f)",
                party, PC_FUNDRAISING_YIELD,
                state.political_capital[party],
            )

    return affordable


def apply_crisis(
    crisis: CrisisEvent,
    state: CampaignState,
    lga_data: pd.DataFrame,
) -> None:
    """Apply a crisis event to the campaign state."""
    # Salience shifts
    for dim_idx, shift_mag in crisis.salience_shifts.items():
        effect = ActiveEffect(
            source_party="__crisis__",
            source_action=crisis.name,
            source_turn=crisis.turn,
            channel="salience",
            target_lgas=crisis.affected_lgas,
            target_dimensions=[dim_idx],
            target_party=None,
            magnitude=shift_mag,
            effect_key=f"crisis:{crisis.name}:salience:{dim_idx}",
        )
        state.apply_effect(effect)

    # Valence effects
    if crisis.valence_effects:
        for party_name, val_mod in crisis.valence_effects.items():
            if party_name in state.party_names:
                effect = ActiveEffect(
                    source_party="__crisis__",
                    source_action=crisis.name,
                    source_turn=crisis.turn,
                    channel="valence",
                    target_lgas=crisis.affected_lgas,
                    target_dimensions=None,
                    target_party=party_name,
                    magnitude=val_mod,
                    effect_key=f"crisis:{crisis.name}:valence:{party_name}",
                )
                state.apply_effect(effect)

    # Awareness boosts
    if crisis.awareness_boost:
        for party_name, boost in crisis.awareness_boost.items():
            if party_name in state.party_names:
                party_idx = state.party_names.index(party_name)
                state.raise_awareness(party_idx, crisis.affected_lgas, np.float32(boost))

    # Tau modifier
    if crisis.tau_modifier != 0.0:
        effect = ActiveEffect(
            source_party="__crisis__",
            source_action=crisis.name,
            source_turn=crisis.turn,
            channel="tau",
            target_lgas=crisis.affected_lgas,
            target_dimensions=None,
            target_party=None,
            magnitude=crisis.tau_modifier,
            effect_key=f"crisis:{crisis.name}:tau",
        )
        state.apply_effect(effect)


def update_post_turn(
    state: CampaignState,
    result: dict,
    turn_actions: list[ActionSpec],
) -> None:
    """
    Update campaign state after a turn's election is computed.

    - Momentum tracking (consecutive rising/falling share)
    - Geographic concentration tracking
    - Cohesion recovery
    """
    # Extract national shares from results
    lga_df = result["lga_results_base"]
    pop_col = "Estimated Population"
    if pop_col in lga_df.columns:
        pop = lga_df[pop_col].values.astype(float)
    else:
        pop = np.ones(len(lga_df))
    total_pop = pop.sum()

    current_shares = {}
    for party_name in state.party_names:
        share_col = f"{party_name}_share"
        if share_col in lga_df.columns:
            weighted = (lga_df[share_col].values * pop).sum() / total_pop
            current_shares[party_name] = weighted

    # Momentum
    for party_name in state.party_names:
        curr = current_shares.get(party_name, 0.0)
        prev = state.previous_shares.get(party_name, curr)
        diff = curr - prev

        old_dir = state.momentum_direction.get(party_name, "")
        old_count = state.momentum.get(party_name, 0)

        if diff > 0.005:
            new_dir = "rising"
        elif diff < -0.005:
            new_dir = "falling"
        else:
            new_dir = ""
            state.momentum[party_name] = 0
            state.momentum_direction[party_name] = ""
            state.previous_shares[party_name] = curr
            continue

        if new_dir == old_dir:
            state.momentum[party_name] = old_count + 1
        else:
            state.momentum[party_name] = 1
        state.momentum_direction[party_name] = new_dir

    state.previous_shares = current_shares

    # Geographic concentration: track per-party which regions they target.
    # If a party targets the same region consecutively, concentration counter
    # increments; otherwise resets.
    turn_party_regions: dict[str, set[str]] = {}
    for action in turn_actions:
        if action.target_lgas is not None:
            region_key = str(action.target_lgas.sum())
            turn_party_regions.setdefault(action.party, set()).add(region_key)
        else:
            turn_party_regions.setdefault(action.party, set()).add("national")

    for party_name in state.party_names:
        current_regions = turn_party_regions.get(party_name, set())
        prev_regions = state._prev_regions.get(party_name, set())
        overlap = current_regions & prev_regions
        if overlap:
            state.concentration[party_name] = state.concentration.get(party_name, 0) + 1
        else:
            state.concentration[party_name] = 0
        state._prev_regions[party_name] = current_regions

    # Cohesion recovery: +1 per turn if below 10, max 10
    for party_name in state.party_names:
        old_coh = state.cohesion.get(party_name, 10.0)
        if old_coh < 10.0:
            state.cohesion[party_name] = min(10.0, old_coh + 1.0)


def run_campaign(
    data_path: str | Path,
    election_config: ElectionConfig,
    turns: list[list[ActionSpec]],
    crisis_events: list[CrisisEvent] | None = None,
    seed: int | None = None,
    verbose: bool = True,
    enforce_pc: bool = True,
    initial_pc: dict[str, float] | None = None,
    max_actions_per_party: int = 3,
) -> list[dict]:
    """
    Run a multi-turn campaign simulation.

    Parameters
    ----------
    data_path : str | Path
        Path to the Nigeria LGA polsim xlsx file.
    election_config : ElectionConfig
        Full election configuration (parties, params, MC count).
    turns : list[list[ActionSpec]]
        One list of actions per turn.
    crisis_events : list[CrisisEvent], optional
        Exogenous events triggered on specific turns.
    seed : int, optional
        Random seed for reproducibility.
    verbose : bool
        If True, log progress.
    enforce_pc : bool
        If True (default), enforce political capital costs. Actions that
        exceed a party's PC balance are skipped. If False, all actions
        are resolved regardless of cost (legacy behavior).
    initial_pc : dict[str, float], optional
        Starting PC balances per party. Defaults to PC_INCOME_PER_TURN
        for each party (first turn income is still added).
    max_actions_per_party : int
        Max actions any one party can take per turn (default 3).

    Returns
    -------
    list[dict]
        One election result dict per turn. Each dict includes a "pc_state"
        key with per-party PC balances after the turn.
    """
    lga_data = load_lga_data(data_path)
    df = lga_data.df

    # Derive colonial region + AZ binary columns (same as run_election)
    if "Colonial Era Region" in df.columns:
        _cr = df["Colonial Era Region"].fillna("").astype(str).str.strip()
        _new_cols = pd.DataFrame({
            "Colonial Western": (_cr == "Western").astype(float),
            "Colonial Eastern": (_cr == "Eastern").astype(float),
            "Colonial Mid-Western": (_cr == "Mid-Western").astype(float),
        }, index=df.index)
        lga_data.df = pd.concat([df, _new_cols], axis=1)
        df = lga_data.df

    if "Administrative Zone" in df.columns:
        _az = df["Administrative Zone"].fillna(0).astype(int)
        _az_cols = pd.DataFrame({
            f"AZ {i}": (_az == i).astype(float)
            for i in range(1, 9)
        }, index=df.index)
        lga_data.df = pd.concat([df, _az_cols], axis=1)
        df = lga_data.df

    party_names = [p.name for p in election_config.parties]
    n_lga = len(df)
    n_parties = len(party_names)

    # Initialize campaign state
    state = CampaignState(
        turn=0,
        n_lga=n_lga,
        n_parties=n_parties,
        party_names=list(party_names),
    )

    # Initialize awareness from base computation
    state.awareness = compute_base_awareness(election_config.parties, df)

    # Initialize cohesion
    for p in party_names:
        state.cohesion[p] = 10.0

    # Store initial positions
    for i, p in enumerate(election_config.parties):
        state.last_positions[p.name] = p.positions.copy()

    # Initialize political capital
    if initial_pc:
        state.political_capital = dict(initial_pc)
    else:
        for p in party_names:
            state.political_capital[p] = 0.0  # Will get income on first turn

    results = []
    for turn_idx, turn_actions in enumerate(turns):
        state.turn = turn_idx + 1
        if verbose:
            logger.info("Campaign Turn %d: %d actions", state.turn, len(turn_actions))

        # PC phase: hoarding cap, income, ETO dividends
        if enforce_pc:
            pc_log = process_pc_income(state)
            if verbose:
                for p, info in pc_log.items():
                    logger.info(
                        "  %s PC: balance=%.0f (income=%d, eto=%d, cap_lost=%.0f)",
                        p, info["balance"], info["income"],
                        info["eto_dividend"], info["cap_lost"],
                    )

        # Apply crisis events for this turn
        if crisis_events:
            for crisis in crisis_events:
                if crisis.turn == state.turn:
                    apply_crisis(crisis, state, df)
                    if verbose:
                        logger.info("  Crisis: %s", crisis.name)

        # Validate PC and resolve player actions
        if enforce_pc:
            turn_actions = validate_and_deduct_pc(state, turn_actions, max_actions_per_party)
        for action in turn_actions:
            resolve_action(action, state, df, election_config)

        # Compile modifiers and run engine
        modifiers = compile_modifiers(state, df)
        result = run_election(
            data_path, election_config,
            campaign_modifiers=modifiers,
            seed=seed,
            verbose=verbose,
        )
        # Attach PC state to result
        result["pc_state"] = dict(state.political_capital)
        results.append(result)

        # Post-turn updates
        update_post_turn(state, result, turn_actions)

        if verbose:
            # Print summary
            summary = result.get("summary", {})
            national = summary.get("national_shares", {})
            top3 = sorted(national.items(), key=lambda x: x[1], reverse=True)[:3]
            logger.info(
                "  Turn %d results: %s",
                state.turn,
                ", ".join(f"{k}: {v:.1%}" for k, v in top3),
            )

    return results
