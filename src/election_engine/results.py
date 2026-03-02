"""
Results processing, vote counts, and presidential spread check for LAGOS-2058.

Key functions:
    compute_vote_counts()       — raw vote counts from shares × population × turnout
    determine_winners()         — LGA-level plurality winners
    check_presidential_spread() — Nigeria constitutional spread requirement
    aggregate_monte_carlo()     — MC distributional results
    compute_summary_stats()     — national and zonal vote shares + vote counts
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Presidential spread requirement (2058 constitution, following 1999 model)
_REQUIRED_STATES_WITH_25PCT = 24   # ≥25% in at least this many states
_TOTAL_STATES = 37                  # 36 states + FCT


def compute_vote_counts(
    lga_results: pd.DataFrame,
    party_names: list[str],
    pop_col: str = "Estimated Population",
    turnout_col: str = "Turnout",
) -> pd.DataFrame:
    """
    Compute raw vote counts per party per LGA from shares, population, and turnout.

    Vote count for party j in LGA c:
        votes_jc = population_c × turnout_c × share_jc

    Parameters
    ----------
    lga_results : pd.DataFrame
        LGA-level results with {party}_share, population, and turnout columns.
    party_names : list[str]
        Party names in order.
    pop_col : str
        Column name for LGA population.
    turnout_col : str
        Column name for LGA turnout rate (0–1).

    Returns
    -------
    pd.DataFrame
        Copy of lga_results with added {party}_votes columns and Total_Votes column.
    """
    result = lga_results.copy()
    pop = result[pop_col].values.astype(float)
    turnout = result[turnout_col].values.astype(float) if turnout_col in result.columns else np.ones(len(result))
    total_voters = pop * turnout

    for p in party_names:
        share_col = f"{p}_share"
        result[f"{p}_votes"] = np.round(total_voters * result[share_col].values.astype(float)).astype(int)

    result["Total_Votes"] = np.round(total_voters).astype(int)
    return result


def determine_lga_winner(lga_result_row: pd.Series, party_names: list[str]) -> str:
    """Return the name of the party with the highest vote share in one LGA."""
    share_cols = [f"{p}_share" for p in party_names]
    shares = lga_result_row[share_cols].values.astype(float)
    winner_idx = np.argmax(shares)
    return party_names[winner_idx]


def add_lga_winners(
    lga_results: pd.DataFrame,
    party_names: list[str],
) -> pd.DataFrame:
    """
    Add a 'Winner' column to the results dataframe.

    Uses vectorised numpy argmax over all LGAs instead of row-by-row apply.

    Parameters
    ----------
    lga_results : pd.DataFrame
        One row per LGA with {party}_share columns.
    party_names : list[str]
        Party names in order.

    Returns
    -------
    pd.DataFrame
        Copy with added 'Winner' column.
    """
    result = lga_results.copy()
    share_cols = [f"{p}_share" for p in party_names]
    shares = result[share_cols].values.astype(float)
    winner_indices = np.argmax(shares, axis=1)
    party_arr = np.array(party_names)
    result["Winner"] = party_arr[winner_indices]
    return result


def count_seats(
    lga_results: pd.DataFrame,
    party_names: list[str],
) -> dict[str, int]:
    """
    Count LGA seats per party (plurality in each LGA = 1 seat).

    Returns dict mapping party_name → seat_count. Seats total 774.
    """
    if "Winner" not in lga_results.columns:
        lga_results = add_lga_winners(lga_results, party_names)
    counts = lga_results["Winner"].value_counts()
    return {p: int(counts.get(p, 0)) for p in party_names}


def compute_state_shares(
    lga_results: pd.DataFrame,
    party_names: list[str],
    state_col: str = "State",
    pop_col: str = "Estimated Population",
) -> pd.DataFrame:
    """
    Compute vote shares aggregated to state level, weighted by LGA population.

    For the spread check we need each party's share in each state.
    Each LGA's shares are weighted by its population to produce proper
    state-level aggregates.

    Returns DataFrame with 'State' and {party}_share columns.
    """
    share_cols = [f"{p}_share" for p in party_names]
    has_pop = pop_col in lga_results.columns

    if has_pop:
        # Population-weighted aggregation
        def _weighted_mean(group: pd.DataFrame) -> pd.Series:
            pop = group[pop_col].values.astype(float)
            total_pop = pop.sum()
            if total_pop <= 0:
                return group[share_cols].mean()
            weights = pop / total_pop
            return pd.Series(
                {col: float(np.dot(weights, group[col].values)) for col in share_cols}
            )

        state_shares = (
            lga_results.groupby(state_col)
            .apply(_weighted_mean, include_groups=False)
            .reset_index()
            .rename(columns={state_col: "State"})
        )
    else:
        # Fall back to unweighted mean if no population column
        state_shares = (
            lga_results.groupby(state_col)[share_cols]
            .mean()
            .reset_index()
            .rename(columns={state_col: "State"})
        )
    return state_shares


def compute_state_vote_counts(
    lga_results: pd.DataFrame,
    party_names: list[str],
    state_col: str = "State",
    pop_col: str = "Estimated Population",
    turnout_col: str = "Turnout",
) -> pd.DataFrame:
    """
    Compute vote counts aggregated to state level.

    Parameters
    ----------
    lga_results : pd.DataFrame
        LGA-level results with {party}_share, population, and turnout columns.
    party_names : list[str]
        Party names in order.

    Returns
    -------
    pd.DataFrame
        One row per state with columns: State, Total_Votes,
        {party}_votes, {party}_share (population-weighted).
    """
    df = lga_results.copy()
    has_pop = pop_col in df.columns
    has_turnout = turnout_col in df.columns

    pop = df[pop_col].values.astype(float) if has_pop else np.ones(len(df))
    turnout = df[turnout_col].values.astype(float) if has_turnout else np.ones(len(df))
    total_voters = pop * turnout

    # Build per-party vote arrays
    for p in party_names:
        df[f"_votes_{p}"] = total_voters * df[f"{p}_share"].values.astype(float)
    df["_total_voters"] = total_voters

    # Aggregate by state
    agg_cols = {f"_votes_{p}": "sum" for p in party_names}
    agg_cols["_total_voters"] = "sum"
    if has_pop:
        agg_cols[pop_col] = "sum"
    state_agg = df.groupby(state_col).agg(agg_cols).reset_index()
    state_agg = state_agg.rename(columns={state_col: "State"})

    # Build output DataFrame
    out = pd.DataFrame({"State": state_agg["State"]})
    if has_pop:
        out["Population"] = state_agg[pop_col].astype(int)
    out["Total_Votes"] = np.round(state_agg["_total_voters"]).astype(int)

    state_total = state_agg["_total_voters"].values
    safe_total = np.where(state_total > 0, state_total, 1.0)

    for p in party_names:
        votes = state_agg[f"_votes_{p}"].values
        out[f"{p}_votes"] = np.round(votes).astype(int)
        out[f"{p}_share"] = votes / safe_total

    return out


def effective_number_of_parties(shares: np.ndarray) -> float:
    """
    Compute the Laakso-Taagepera effective number of parties (ENP).

    ENP = 1 / Σ(s_j²) where s_j are vote shares summing to 1.
    A system with 3 equal parties has ENP=3; a dominant-party system has ENP≈1.

    Parameters
    ----------
    shares : np.ndarray, shape (J,)
        Vote shares per party, summing to ~1.

    Returns
    -------
    float
        Effective number of parties.
    """
    shares = np.asarray(shares, dtype=float)
    shares = shares[shares > 0]  # exclude zero-share parties
    hhi = np.sum(shares ** 2)
    if hhi < 1e-12:
        return 0.0
    return 1.0 / hhi


def compute_competitiveness(
    lga_results: pd.DataFrame,
    party_names: list[str],
) -> pd.DataFrame:
    """
    Add competitiveness metrics to LGA results.

    Adds columns:
        Margin        — share gap between 1st and 2nd place parties
        HHI           — Herfindahl-Hirschman Index of vote shares (0–1)
        ENP           — Effective Number of Parties (Laakso-Taagepera)

    Parameters
    ----------
    lga_results : pd.DataFrame
        LGA-level results with {party}_share columns.
    party_names : list[str]

    Returns
    -------
    pd.DataFrame
        Copy with added competitiveness columns.
    """
    result = lga_results.copy()
    share_cols = [f"{p}_share" for p in party_names]
    shares = result[share_cols].values.astype(float)  # (N_lga, J)

    # Margin: gap between 1st and 2nd place
    sorted_shares = np.sort(shares, axis=1)[:, ::-1]  # descending
    if shares.shape[1] >= 2:
        result["Margin"] = sorted_shares[:, 0] - sorted_shares[:, 1]
    else:
        result["Margin"] = 1.0

    # HHI: sum of squared shares
    hhi = np.sum(shares ** 2, axis=1)
    result["HHI"] = hhi

    # ENP: 1 / HHI
    safe_hhi = np.where(hhi > 1e-12, hhi, 1.0)
    result["ENP"] = 1.0 / safe_hhi

    return result


def _pop_weighted_national(
    lga_results: pd.DataFrame,
    party_names: list[str],
    pop_col: str = "Estimated Population",
) -> dict[str, float]:
    """Compute population-weighted national share per party."""
    share_cols = [f"{p}_share" for p in party_names]
    if pop_col in lga_results.columns:
        pop = lga_results[pop_col].values.astype(float)
        total_pop = pop.sum()
        if total_pop > 0:
            weights = pop / total_pop
            return {
                p: float(np.dot(weights, lga_results[f"{p}_share"].values))
                for p in party_names
            }
    # Fallback: unweighted
    return {p: float(lga_results[f"{p}_share"].mean()) for p in party_names}


def check_presidential_spread(
    lga_results: pd.DataFrame,
    candidate_party: str,
    party_names: list[str],
    state_col: str = "State",
) -> dict:
    """
    Check whether a party meets the presidential spread requirement.

    The winner must hold national plurality AND achieve ≥25% in at least
    24 of 36 states (+FCT = 37 total).

    Parameters
    ----------
    lga_results : pd.DataFrame
        LGA-level results with {party}_share columns.
    candidate_party : str
        Name of the party to check.
    party_names : list[str]
        All party names.
    state_col : str
        Column name for State.

    Returns
    -------
    dict with keys:
        meets_requirement : bool
        national_share : float
        states_meeting_25pct : int
        state_breakdown : dict[state_name, party_share]
    """
    share_col = f"{candidate_party}_share"
    if share_col not in lga_results.columns:
        raise ValueError(f"Column {share_col!r} not found in results")

    # National shares (population-weighted)
    all_national = _pop_weighted_national(lga_results, party_names)
    national_share = all_national[candidate_party]

    # Check whether this party has national plurality
    max_share = max(all_national.values())
    has_national_plurality = abs(national_share - max_share) < 1e-6

    # State-level shares (population-weighted)
    state_shares = compute_state_shares(lga_results, party_names, state_col)

    state_breakdown = {}
    states_meeting = 0
    for _, row in state_shares.iterrows():
        state = row["State"]
        share = float(row[share_col])
        state_breakdown[state] = share
        if share >= 0.25:
            states_meeting += 1

    meets_requirement = has_national_plurality and (states_meeting >= _REQUIRED_STATES_WITH_25PCT)

    return {
        "meets_requirement": meets_requirement,
        "national_share": national_share,
        "has_national_plurality": has_national_plurality,
        "states_meeting_25pct": states_meeting,
        "required_states": _REQUIRED_STATES_WITH_25PCT,
        "state_breakdown": state_breakdown,
    }


def aggregate_monte_carlo(
    all_runs: list[pd.DataFrame],
    party_names: list[str],
    state_col: str = "State",
    pop_col: str = "Estimated Population",
) -> dict:
    """
    Aggregate results from multiple Monte Carlo runs into distributional statistics.

    Parameters
    ----------
    all_runs : list[pd.DataFrame]
        Each element is one MC run's LGA results (output of apply_noise_to_results).
    party_names : list[str]
    pop_col : str
        Column name for LGA population (used for national share weighting).

    Returns
    -------
    dict with:
        seat_stats : pd.DataFrame — mean/std/p5/p95 seats per party
        national_share_stats : pd.DataFrame — mean/std/p5/p95 national share per party
        share_stats : pd.DataFrame — per-LGA: mean share, std per party
        win_probabilities : dict[party, float] — fraction of runs where party wins most seats
        swing_lgas : pd.DataFrame — LGAs where winner changes across runs
    """
    n_runs = len(all_runs)
    if n_runs == 0:
        raise ValueError("No MC runs provided")

    share_cols = [f"{p}_share" for p in party_names]
    lga_count = len(all_runs[0])
    J = len(party_names)

    # ---- Stack all share data into a 3D numpy array (n_runs, n_lgas, J) ----
    all_shares = np.empty((n_runs, lga_count, J))
    for r, run_df in enumerate(all_runs):
        all_shares[r] = run_df[share_cols].values

    # ---- Winner per LGA per run (vectorised argmax) ----
    winner_indices = np.argmax(all_shares, axis=2)  # (n_runs, n_lgas) — int indices

    # ---- Seat counts per run (vectorised via bincount) ----
    seat_matrix = np.array([
        np.bincount(winner_indices[r], minlength=J) for r in range(n_runs)
    ])

    seat_stats_rows = []
    for j, p in enumerate(party_names):
        arr = seat_matrix[:, j]
        seat_stats_rows.append({
            "Party": p,
            "Mean Seats": float(arr.mean()),
            "Std Seats": float(arr.std()),
            "P5 Seats": float(np.percentile(arr, 5)),
            "P95 Seats": float(np.percentile(arr, 95)),
            "Median Seats": float(np.median(arr)),
        })
    seat_stats = pd.DataFrame(seat_stats_rows)

    # National winner per run = party with most seats
    national_winner_idx = np.argmax(seat_matrix, axis=1)  # (n_runs,)
    win_probabilities = {}
    for j, p in enumerate(party_names):
        win_probabilities[p] = float(np.sum(national_winner_idx == j)) / n_runs

    # ---- National share statistics (population-weighted) ----
    has_pop = pop_col in all_runs[0].columns
    if has_pop:
        pop = all_runs[0][pop_col].values.astype(float)  # (n_lgas,)
        pop_weights = pop / pop.sum()  # (n_lgas,)
        # (n_runs, n_lgas, J) × (n_lgas, 1) → sum over LGAs → (n_runs, J)
        national_shares_per_run = np.einsum("rlj,l->rj", all_shares, pop_weights)
    else:
        national_shares_per_run = all_shares.mean(axis=1)  # (n_runs, J)

    nat_share_rows = []
    for j, p in enumerate(party_names):
        arr = national_shares_per_run[:, j]
        nat_share_rows.append({
            "Party": p,
            "Mean Share": float(arr.mean()),
            "Std Share": float(arr.std()),
            "P5 Share": float(np.percentile(arr, 5)),
            "P95 Share": float(np.percentile(arr, 95)),
            "Median Share": float(np.median(arr)),
        })
    national_share_stats = pd.DataFrame(nat_share_rows)

    # ---- National vote count statistics ----
    turnout_col = "Turnout"
    has_turnout = turnout_col in all_runs[0].columns
    if has_pop and has_turnout:
        # Stack turnout across runs: (n_runs, n_lgas)
        all_turnout = np.empty((n_runs, lga_count))
        for r, run_df in enumerate(all_runs):
            all_turnout[r] = run_df[turnout_col].values.astype(float)

        # total_voters per LGA per run: pop * turnout
        total_voters_per_run = pop[np.newaxis, :] * all_turnout  # (n_runs, n_lgas)

        # votes per party per run: total_voters * share → sum over LGAs → (n_runs, J)
        national_votes_per_run = np.einsum("rl,rlj->rj", total_voters_per_run, all_shares)
        total_votes_per_run = total_voters_per_run.sum(axis=1)  # (n_runs,)

        nat_vote_rows = []
        for j, p in enumerate(party_names):
            arr = national_votes_per_run[:, j]
            nat_vote_rows.append({
                "Party": p,
                "Mean Votes": float(arr.mean()),
                "Std Votes": float(arr.std()),
                "P5 Votes": float(np.percentile(arr, 5)),
                "P95 Votes": float(np.percentile(arr, 95)),
                "Median Votes": float(np.median(arr)),
            })
        national_vote_stats = pd.DataFrame(nat_vote_rows)
        total_vote_stats = {
            "mean": float(total_votes_per_run.mean()),
            "std": float(total_votes_per_run.std()),
            "p5": float(np.percentile(total_votes_per_run, 5)),
            "p95": float(np.percentile(total_votes_per_run, 95)),
        }
    else:
        national_vote_stats = pd.DataFrame()
        total_vote_stats = {}

    # ---- Per-LGA share statistics ----
    share_stats_df = all_runs[0][["State", "LGA Name"]].copy()
    for j, col in enumerate(share_cols):
        col_data = all_shares[:, :, j]  # (n_runs, n_lgas)
        share_stats_df[f"{col}_mean"] = col_data.mean(axis=0)
        share_stats_df[f"{col}_std"] = col_data.std(axis=0)

    # ---- Swing LGAs (vectorised) ----
    # Check which LGAs have > 1 unique winner across runs
    first_run_winners = winner_indices[0]  # (n_lgas,)
    # An LGA is swing if any run has a different winner than the first run
    swing_mask = np.any(winner_indices != first_run_winners[np.newaxis, :], axis=0)

    swing_lgas = all_runs[0].copy()
    swing_lgas["Is Swing"] = swing_mask
    swing_lgas = swing_lgas[swing_lgas["Is Swing"]].drop(columns=["Is Swing"])

    return {
        "seat_stats": seat_stats,
        "national_share_stats": national_share_stats,
        "national_vote_stats": national_vote_stats,
        "total_vote_stats": total_vote_stats,
        "share_stats": share_stats_df,
        "win_probabilities": win_probabilities,
        "swing_lgas": swing_lgas,
        "n_runs": n_runs,
    }


def aggregate_monte_carlo_from_arrays(
    all_shares: np.ndarray,
    all_turnout: np.ndarray,
    party_names: list[str],
    pop: np.ndarray,
    base_run_df: pd.DataFrame,
) -> dict:
    """
    Aggregate MC results from pre-allocated numpy arrays (fast path).

    Parameters
    ----------
    all_shares : np.ndarray, shape (n_runs, n_lgas, J)
        Noisy vote shares for each MC run.
    all_turnout : np.ndarray, shape (n_runs, n_lgas)
        Noisy turnout for each MC run.
    party_names : list[str]
    pop : np.ndarray, shape (n_lgas,)
        LGA populations (for weighting).
    base_run_df : pd.DataFrame
        Base (deterministic) LGA results (for State/LGA Name metadata).

    Returns
    -------
    dict — same structure as aggregate_monte_carlo.
    """
    n_runs, lga_count, J = all_shares.shape

    # Winner per LGA per run
    winner_indices = np.argmax(all_shares, axis=2)

    # Seat counts per run (vectorised via bincount)
    seat_matrix = np.array([
        np.bincount(winner_indices[r], minlength=J) for r in range(n_runs)
    ])

    seat_stats_rows = []
    for j, p in enumerate(party_names):
        arr = seat_matrix[:, j]
        seat_stats_rows.append({
            "Party": p,
            "Mean Seats": float(arr.mean()),
            "Std Seats": float(arr.std()),
            "P5 Seats": float(np.percentile(arr, 5)),
            "P95 Seats": float(np.percentile(arr, 95)),
            "Median Seats": float(np.median(arr)),
        })
    seat_stats = pd.DataFrame(seat_stats_rows)

    national_winner_idx = np.argmax(seat_matrix, axis=1)
    win_probabilities = {}
    for j, p in enumerate(party_names):
        win_probabilities[p] = float(np.sum(national_winner_idx == j)) / n_runs

    # National share stats (population-weighted)
    total_pop = pop.sum()
    if total_pop > 0:
        pop_weights = pop / total_pop
        national_shares_per_run = np.einsum("rlj,l->rj", all_shares, pop_weights)
    else:
        national_shares_per_run = all_shares.mean(axis=1)

    nat_share_rows = []
    for j, p in enumerate(party_names):
        arr = national_shares_per_run[:, j]
        nat_share_rows.append({
            "Party": p,
            "Mean Share": float(arr.mean()),
            "Std Share": float(arr.std()),
            "P5 Share": float(np.percentile(arr, 5)),
            "P95 Share": float(np.percentile(arr, 95)),
            "Median Share": float(np.median(arr)),
        })
    national_share_stats = pd.DataFrame(nat_share_rows)

    # National vote count stats
    total_voters_per_run = pop[np.newaxis, :] * all_turnout
    national_votes_per_run = np.einsum("rl,rlj->rj", total_voters_per_run, all_shares)
    total_votes_per_run = total_voters_per_run.sum(axis=1)

    nat_vote_rows = []
    for j, p in enumerate(party_names):
        arr = national_votes_per_run[:, j]
        nat_vote_rows.append({
            "Party": p,
            "Mean Votes": float(arr.mean()),
            "Std Votes": float(arr.std()),
            "P5 Votes": float(np.percentile(arr, 5)),
            "P95 Votes": float(np.percentile(arr, 95)),
            "Median Votes": float(np.median(arr)),
        })
    national_vote_stats = pd.DataFrame(nat_vote_rows)
    total_vote_stats = {
        "mean": float(total_votes_per_run.mean()),
        "std": float(total_votes_per_run.std()),
        "p5": float(np.percentile(total_votes_per_run, 5)),
        "p95": float(np.percentile(total_votes_per_run, 95)),
    }

    # Per-LGA share statistics
    share_cols = [f"{p}_share" for p in party_names]
    share_stats_df = base_run_df[["State", "LGA Name"]].copy()
    for j, col in enumerate(share_cols):
        col_data = all_shares[:, :, j]
        share_stats_df[f"{col}_mean"] = col_data.mean(axis=0)
        share_stats_df[f"{col}_std"] = col_data.std(axis=0)

    # Swing LGAs
    first_run_winners = winner_indices[0]
    swing_mask = np.any(winner_indices != first_run_winners[np.newaxis, :], axis=0)
    swing_lgas = base_run_df.copy()
    swing_lgas["Is Swing"] = swing_mask
    swing_lgas = swing_lgas[swing_lgas["Is Swing"]].drop(columns=["Is Swing"])

    # MC ENP distribution
    hhi_per_run = np.sum(national_shares_per_run ** 2, axis=1)  # (n_runs,)
    enp_per_run = 1.0 / np.maximum(hhi_per_run, 1e-12)
    enp_stats = {
        "mean": float(enp_per_run.mean()),
        "std": float(enp_per_run.std()),
        "p5": float(np.percentile(enp_per_run, 5)),
        "p95": float(np.percentile(enp_per_run, 95)),
    }

    # National competitiveness margin: gap between 1st and 2nd place national share
    sorted_nat = np.sort(national_shares_per_run, axis=1)[:, ::-1]  # (n_runs, J) desc
    if J >= 2:
        nat_margins = sorted_nat[:, 0] - sorted_nat[:, 1]  # (n_runs,)
    else:
        nat_margins = np.ones(n_runs)
    margin_stats = {
        "mean": float(nat_margins.mean()),
        "std": float(nat_margins.std()),
        "p5": float(np.percentile(nat_margins, 5)),
        "p95": float(np.percentile(nat_margins, 95)),
    }

    # Per-LGA vote volatility: mean std of each party's share across MC runs
    lga_volatility = all_shares.std(axis=0).mean(axis=1)  # (n_lgas,) avg over parties
    share_stats_df["Volatility"] = lga_volatility

    return {
        "seat_stats": seat_stats,
        "national_share_stats": national_share_stats,
        "national_vote_stats": national_vote_stats,
        "total_vote_stats": total_vote_stats,
        "share_stats": share_stats_df,
        "win_probabilities": win_probabilities,
        "swing_lgas": swing_lgas,
        "enp_stats": enp_stats,
        "margin_stats": margin_stats,
        "n_runs": n_runs,
    }


def compute_summary_stats(
    lga_results: pd.DataFrame,
    party_names: list[str],
    az_col: str = "Administrative Zone",
    az_name_col: str = "AZ Name",
    state_col: str = "State",
) -> dict:
    """
    Compute national and zonal summary statistics.

    Returns dict with:
        national_shares : dict[party, float]
        national_votes : dict[party, int]
        total_votes : int
        zonal_shares : pd.DataFrame (one row per zone)
        seat_counts : dict[party, int] (kept for backwards compatibility)
        national_turnout : float
    """
    seats = count_seats(lga_results, party_names)

    # Population-weighted national shares
    national = _pop_weighted_national(lga_results, party_names)

    # National vote counts
    pop_col = "Estimated Population"
    turnout_col = "Turnout"
    has_pop = pop_col in lga_results.columns
    has_turnout = turnout_col in lga_results.columns
    if has_pop and has_turnout:
        pop = lga_results[pop_col].values.astype(float)
        turnout = lga_results[turnout_col].values.astype(float)
        total_voters = pop * turnout
        national_votes = {}
        for p in party_names:
            votes = total_voters * lga_results[f"{p}_share"].values.astype(float)
            national_votes[p] = int(np.round(votes.sum()))
        total_votes = int(np.round(total_voters.sum()))
    else:
        national_votes = {p: 0 for p in party_names}
        total_votes = 0

    # Population-weighted zonal shares
    share_and_turnout = [f"{p}_share" for p in party_names]
    if "Turnout" in lga_results.columns:
        share_and_turnout = share_and_turnout + ["Turnout"]
    pop_col = "Estimated Population"
    has_pop = pop_col in lga_results.columns

    if has_pop:
        def _weighted_zonal(group: pd.DataFrame) -> pd.Series:
            pop = group[pop_col].values.astype(float)
            total_pop = pop.sum()
            if total_pop <= 0:
                return group[share_and_turnout].mean()
            weights = pop / total_pop
            return pd.Series(
                {col: float(np.dot(weights, group[col].values)) for col in share_and_turnout}
            )

        zonal = (
            lga_results.groupby([az_col, az_name_col])
            .apply(_weighted_zonal, include_groups=False)
            .reset_index()
        )
    else:
        zonal = (
            lga_results
            .groupby([az_col, az_name_col])[share_and_turnout]
            .mean()
            .reset_index()
        )

    # Population-weighted turnout
    if "Turnout" in lga_results.columns:
        if has_pop:
            pop = lga_results[pop_col].values.astype(float)
            total_pop = pop.sum()
            if total_pop > 0:
                turnout = float(np.dot(pop / total_pop, lga_results["Turnout"].values))
            else:
                turnout = float(lga_results["Turnout"].mean())
        else:
            turnout = float(lga_results["Turnout"].mean())
    else:
        turnout = 0.0

    # Effective Number of Parties (national level)
    national_share_arr = np.array([national[p] for p in party_names])
    enp = effective_number_of_parties(national_share_arr)

    return {
        "national_shares": national,
        "national_votes": national_votes,
        "total_votes": total_votes,
        "zonal_shares": zonal,
        "seat_counts": seats,
        "national_turnout": turnout,
        "enp": enp,
    }
