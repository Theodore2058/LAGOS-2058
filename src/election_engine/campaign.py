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
    ACTION_RESOLUTION_ORDER,
    apply_synergies, update_action_fatigue, get_fatigue_multiplier,
    check_endorsement_fragility,
)
from .campaign_modifiers import compile_modifiers, roll_scandals, apply_exposure_decay
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
) -> list[ActionSpec]:
    """
    Validate that each party can afford its actions and deduct PC.

    Actions are processed in order. If a party can't afford an action,
    it is skipped (logged as warning). Fundraising generates PC immediately.
    Parties can take as many actions as they have PC for.

    Returns the list of affordable actions (may be shorter than input).
    """
    affordable: list[ActionSpec] = []
    action_counts: dict[str, int] = {}

    for action in turn_actions:
        party = action.party

        # Count targeted LGAs/AZs for area-based cost scaling
        n_target_lgas = int(action.target_lgas.sum()) if action.target_lgas is not None else 0
        n_target_azs = action.params.get("_n_target_azs", 0)
        cost = compute_action_cost(
            action.action_type, action.params,
            n_target_lgas=n_target_lgas, n_target_azs=n_target_azs,
        )
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
        action_counts[party] = action_counts.get(party, 0) + 1

        # Fundraising PC generation is now handled in resolve_fundraising()
        # which supports source-dependent yields and side effects.
        # Log the balance after fundraising resolves (via resolve_action).
        if action.action_type == "fundraising":
            logger.info(
                "  %s fundraising queued (source=%s, balance after deduct: %.0f)",
                party, action.params.get("source", "diaspora"),
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


def _extract_az_from_lga_mask(lga_mask: np.ndarray | None, lga_data: pd.DataFrame) -> set[int]:
    """Extract which AZs are covered by an LGA mask."""
    if lga_mask is None:
        # National action covers all AZs
        if "Administrative Zone" in lga_data.columns:
            return set(lga_data["Administrative Zone"].dropna().astype(int).unique())
        return set(range(1, 9))
    if "Administrative Zone" in lga_data.columns:
        return set(lga_data.loc[lga_mask, "Administrative Zone"].dropna().astype(int).unique())
    return set()


def update_post_turn(
    state: CampaignState,
    result: dict,
    turn_actions: list[ActionSpec],
    lga_data: pd.DataFrame | None = None,
    rng: np.random.Generator | None = None,
) -> dict:
    """
    Update campaign state after a turn's election is computed.

    - Momentum tracking (consecutive rising/falling share, volatile detection)
    - Geographic concentration tracking
    - Scandal rolls (probability-based, from exposure)
    - Exposure decay (3 clean turns → -1/turn)
    - Cohesion: recovery, region neglect penalty, engagement bonus

    Returns a dict with post-turn event log (scandals, cohesion changes, etc.).
    """
    post_turn_log: dict = {"scandals": [], "cohesion_changes": {}, "exposure_decay": {}}

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

    # --- Momentum tracking with volatile state detection ---
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
            new_dir = "stable"

        # Track momentum direction history for volatile detection
        if party_name not in state._momentum_history:
            state._momentum_history[party_name] = []
        state._momentum_history[party_name].append(new_dir)
        # Keep last 4 entries
        if len(state._momentum_history[party_name]) > 4:
            state._momentum_history[party_name] = state._momentum_history[party_name][-4:]

        if new_dir == "stable":
            state.momentum[party_name] = 0
            state.momentum_direction[party_name] = "stable"
            state.previous_shares[party_name] = curr
            continue

        if new_dir == old_dir:
            state.momentum[party_name] = old_count + 1
        else:
            state.momentum[party_name] = 1
        state.momentum_direction[party_name] = new_dir

    state.previous_shares = current_shares

    # --- Geographic concentration tracking ---
    turn_party_regions: dict[str, set[str]] = {}
    turn_party_azs: dict[str, set[int]] = {}
    for action in turn_actions:
        if action.target_lgas is not None:
            region_key = str(action.target_lgas.sum())
            turn_party_regions.setdefault(action.party, set()).add(region_key)
        else:
            turn_party_regions.setdefault(action.party, set()).add("national")
        # Track which AZs each party engaged this turn
        if lga_data is not None:
            azs = _extract_az_from_lga_mask(action.target_lgas, lga_data)
            turn_party_azs.setdefault(action.party, set()).update(azs)

    for party_name in state.party_names:
        current_regions = turn_party_regions.get(party_name, set())
        prev_regions = state._prev_regions.get(party_name, set())
        overlap = current_regions & prev_regions
        if overlap:
            state.concentration[party_name] = state.concentration.get(party_name, 0) + 1
        else:
            state.concentration[party_name] = 0
        state._prev_regions[party_name] = current_regions

    # --- Scandal rolls ---
    if rng is not None:
        scandals = roll_scandals(state, rng)
        post_turn_log["scandals"] = scandals

    # --- Endorsement fragility (withdrawals from scandals or ethnic tension) ---
    if rng is not None:
        endorsement_withdrawals = check_endorsement_fragility(state, turn_actions, rng)
        if endorsement_withdrawals:
            post_turn_log["endorsement_withdrawals"] = endorsement_withdrawals

    # --- Exposure decay (3 clean turns → -1/turn) ---
    apply_exposure_decay(state)
    for party_name in state.party_names:
        exp = state.exposure.get(party_name, 0.0)
        if exp > 0:
            post_turn_log["exposure_decay"][party_name] = exp

    # --- Cohesion: recovery, region neglect, engagement bonus ---
    for party_name in state.party_names:
        old_coh = state.cohesion.get(party_name, 10.0)
        new_coh = old_coh
        coh_changes: list[str] = []

        # Base recovery: +1 per turn if below 10
        if new_coh < 10.0:
            new_coh = min(10.0, new_coh + 1.0)
            coh_changes.append("+1.0 recovery")

        # Region engagement tracking & neglect penalty
        if lga_data is not None:
            engaged_azs = turn_party_azs.get(party_name, set())
            if party_name not in state._region_engagement:
                state._region_engagement[party_name] = {}

            # Update engagement timestamps
            for az in engaged_azs:
                state._region_engagement[party_name][az] = state.turn

            # Check for neglected support regions (not engaged in 3+ turns)
            # A party's "support regions" are AZs where it has regional_strongholds > 0
            party_obj = None
            for p in (result.get("_parties", []) or []):
                if hasattr(p, "name") and p.name == party_name:
                    party_obj = p
                    break

            if party_obj is None:
                # Fall back: check all AZs the party has ever engaged
                support_azs = set(state._region_engagement.get(party_name, {}).keys())
            elif hasattr(party_obj, "regional_strongholds") and party_obj.regional_strongholds:
                support_azs = {az for az, bonus in party_obj.regional_strongholds.items() if bonus > 0}
            else:
                support_azs = set()

            neglected = False
            for az in support_azs:
                last_engaged = state._region_engagement.get(party_name, {}).get(az, 0)
                if state.turn - last_engaged >= 3:
                    neglected = True
                    break

            if neglected:
                new_coh = max(0.0, new_coh - 1.0)
                coh_changes.append("-1.0 region neglect")

            # Engagement bonus: +1 if party campaigns in 3+ distinct AZs this turn
            if len(engaged_azs) >= 3 and new_coh < 10.0:
                new_coh = min(10.0, new_coh + 1.0)
                coh_changes.append("+1.0 broad engagement")

        state.cohesion[party_name] = new_coh
        if coh_changes:
            post_turn_log["cohesion_changes"][party_name] = {
                "old": old_coh, "new": new_coh, "changes": coh_changes,
            }

    return post_turn_log


def run_campaign(
    data_path: str | Path,
    election_config: ElectionConfig,
    turns: list[list[ActionSpec]],
    crisis_events: list[CrisisEvent] | None = None,
    seed: int | None = None,
    verbose: bool = True,
    enforce_pc: bool = True,
    initial_pc: dict[str, float] | None = None,
    econ_state: object | None = None,
    econ_config: object | None = None,
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

    # RNG for scandal rolls and other stochastic mechanics
    campaign_rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()

    results = []
    for turn_idx, turn_actions in enumerate(turns):
        state.turn = turn_idx + 1
        if verbose:
            logger.info("Campaign Turn %d: %d actions", state.turn, len(turn_actions))

        # Deliver pending polls from previous turn
        delivered = [p for p in state.pending_polls if p["turn_delivered"] <= state.turn]
        if delivered:
            state.poll_results.extend(delivered)
            state.pending_polls = [p for p in state.pending_polls if p["turn_delivered"] > state.turn]
            if verbose:
                for p in delivered:
                    logger.info(
                        "  Poll delivered to %s (tier %d, scope=%s, margin=+/-%.2f)",
                        p["commissioned_by"], p["poll_tier"], p["scope"], p["margin_of_error"],
                    )

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

        # Validate PC and resolve player actions in fixed resolution order
        if enforce_pc:
            turn_actions = validate_and_deduct_pc(state, turn_actions)
        # Sort by resolution order: manifesto first, fundraising last
        turn_actions_sorted = sorted(
            turn_actions,
            key=lambda a: ACTION_RESOLUTION_ORDER.get(a.action_type, 3),
        )
        for action in turn_actions_sorted:
            # Apply fatigue: scale effect magnitudes for repeated action types
            fatigue_mult = get_fatigue_multiplier(state, action.party, action.action_type)
            if fatigue_mult < 1.0:
                # Temporarily scale params that affect magnitude
                action = ActionSpec(
                    party=action.party,
                    action_type=action.action_type,
                    target_lgas=action.target_lgas,
                    language=action.language,
                    params={**action.params, "_fatigue_mult": fatigue_mult},
                )
            resolve_action(action, state, df, election_config)

        # Apply synergies for complementary same-turn actions
        synergy_log = apply_synergies(turn_actions_sorted, state)

        # Update fatigue counters for next turn
        update_action_fatigue(state, turn_actions_sorted)

        # Compile modifiers and run engine
        modifiers = compile_modifiers(state, df)
        result = run_election(
            data_path, election_config,
            campaign_modifiers=modifiers,
            seed=seed,
            verbose=verbose,
            econ_state=econ_state,
            econ_config=econ_config,
        )
        # Attach PC state and party references to result
        result["pc_state"] = dict(state.political_capital)
        result["_parties"] = election_config.parties
        results.append(result)

        # Post-turn updates (momentum, scandals, exposure decay, cohesion)
        post_log = update_post_turn(
            state, result, turn_actions_sorted,
            lga_data=df, rng=campaign_rng,
        )
        result["post_turn_log"] = post_log
        result["synergy_log"] = synergy_log

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
            # Log scandals
            for scandal in post_log.get("scandals", []):
                logger.warning(
                    "  SCANDAL: %s (exposure=%.1f, valence penalty=%.2f, PC lost=%d)",
                    scandal["party"], scandal["exposure_at_trigger"],
                    scandal["valence_penalty"], scandal["pc_damage"],
                )
            # Log synergies
            for syn in synergy_log:
                logger.info(
                    "  SYNERGY: %s - %s -> %s +%.2f",
                    syn["party"], "+".join(syn["actions"]),
                    syn["channel"], syn["magnitude"],
                )
            # Log cohesion changes
            for party_name, coh_info in post_log.get("cohesion_changes", {}).items():
                logger.info(
                    "  %s cohesion: %.0f → %.0f (%s)",
                    party_name, coh_info["old"], coh_info["new"],
                    ", ".join(coh_info["changes"]),
                )

    return results
