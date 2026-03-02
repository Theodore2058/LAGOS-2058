"""
Results processing, seat allocation, and presidential spread check for LAGOS-2058.

Key functions:
    determine_winners()         — LGA-level plurality winners
    check_presidential_spread() — Nigeria constitutional spread requirement
    aggregate_monte_carlo()     — MC distributional results
    compute_summary_stats()     — national and zonal vote shares
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
    result["Winner"] = result.apply(
        lambda row: determine_lga_winner(row, party_names), axis=1
    )
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
) -> pd.DataFrame:
    """
    Compute vote shares aggregated to state level (population-weighted by LGA).

    For the spread check we need each party's share in each state.
    We approximate by averaging LGA shares within each state
    (a proper implementation would weight by LGA population).

    Returns DataFrame indexed by state with {party}_share columns.
    """
    share_cols = [f"{p}_share" for p in party_names]
    state_shares = (
        lga_results.groupby(state_col)[share_cols]
        .mean()
        .reset_index()
        .rename(columns={state_col: "State"})
    )
    return state_shares


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

    # National share (mean of LGA shares — approximate)
    national_share = float(lga_results[share_col].mean())

    # Check whether this party has national plurality
    all_national = {p: float(lga_results[f"{p}_share"].mean()) for p in party_names}
    has_national_plurality = (national_share == max(all_national.values()))

    # State-level shares
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
) -> dict:
    """
    Aggregate results from multiple Monte Carlo runs into distributional statistics.

    Parameters
    ----------
    all_runs : list[pd.DataFrame]
        Each element is one MC run's LGA results (output of apply_noise_to_results).
    party_names : list[str]

    Returns
    -------
    dict with:
        seat_stats : pd.DataFrame — mean/std/p5/p95 seats per party
        share_stats : pd.DataFrame — per-LGA: mean share, std per party
        win_probabilities : dict[party, float] — fraction of runs where party wins most seats
        swing_lgas : pd.DataFrame — LGAs where winner changes across runs
    """
    n_runs = len(all_runs)
    if n_runs == 0:
        raise ValueError("No MC runs provided")

    # ---- Seat counts across runs ----
    all_seat_counts = []
    all_winners = []

    for run_df in all_runs:
        seats = count_seats(run_df, party_names)
        all_seat_counts.append(seats)
        # National winner
        overall_winner = max(seats, key=lambda p: seats[p])
        all_winners.append(overall_winner)

    seat_array = {p: np.array([s[p] for s in all_seat_counts]) for p in party_names}

    seat_stats_rows = []
    for p in party_names:
        arr = seat_array[p]
        seat_stats_rows.append({
            "Party": p,
            "Mean Seats": float(arr.mean()),
            "Std Seats": float(arr.std()),
            "P5 Seats": float(np.percentile(arr, 5)),
            "P95 Seats": float(np.percentile(arr, 95)),
            "Median Seats": float(np.median(arr)),
        })
    seat_stats = pd.DataFrame(seat_stats_rows)

    # Win probabilities
    win_counts = {p: sum(1 for w in all_winners if w == p) for p in party_names}
    win_probabilities = {p: win_counts[p] / n_runs for p in party_names}

    # ---- Per-LGA share statistics ----
    share_cols = [f"{p}_share" for p in party_names]
    # Stack all runs (n_runs × n_lgas × n_parties)
    lga_count = len(all_runs[0])
    share_arrays = {col: np.zeros((n_runs, lga_count)) for col in share_cols}

    for r, run_df in enumerate(all_runs):
        for col in share_cols:
            share_arrays[col][r] = run_df[col].values

    share_stats_df = all_runs[0][["State", "LGA Name"]].copy()
    for col in share_cols:
        share_stats_df[f"{col}_mean"] = share_arrays[col].mean(axis=0)
        share_stats_df[f"{col}_std"] = share_arrays[col].std(axis=0)

    # ---- Swing LGAs ----
    # For each LGA, determine winner in each run and check if it changes
    winners_per_run_per_lga = []
    for run_df in all_runs:
        run_with_winners = add_lga_winners(run_df, party_names)
        winners_per_run_per_lga.append(run_with_winners["Winner"].values)

    winner_matrix = np.array(winners_per_run_per_lga)  # (n_runs, n_lgas)
    # Check which LGAs have > 1 unique winner
    swing_mask = []
    for lga_idx in range(lga_count):
        unique_winners = len(set(winner_matrix[:, lga_idx]))
        swing_mask.append(unique_winners > 1)

    swing_lgas = all_runs[0].copy()
    swing_lgas["Is Swing"] = swing_mask
    swing_lgas = swing_lgas[swing_lgas["Is Swing"]].drop(columns=["Is Swing"])

    return {
        "seat_stats": seat_stats,
        "share_stats": share_stats_df,
        "win_probabilities": win_probabilities,
        "swing_lgas": swing_lgas,
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
        zonal_shares : pd.DataFrame (one row per zone)
        seat_counts : dict[party, int]
        national_turnout : float
    """
    seats = count_seats(lga_results, party_names)

    national = {p: float(lga_results[f"{p}_share"].mean()) for p in party_names}

    zonal = (
        lga_results
        .groupby([az_col, az_name_col])[[f"{p}_share" for p in party_names] + ["Turnout"]]
        .mean()
        .reset_index()
    )

    turnout = float(lga_results["Turnout"].mean()) if "Turnout" in lga_results.columns else 0.0

    return {
        "national_shares": national,
        "zonal_shares": zonal,
        "seat_counts": seats,
        "national_turnout": turnout,
    }
