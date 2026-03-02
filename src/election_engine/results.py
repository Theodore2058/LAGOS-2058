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

    share_cols = [f"{p}_share" for p in party_names]
    lga_count = len(all_runs[0])
    J = len(party_names)

    # ---- Stack all share data into a 3D numpy array (n_runs, n_lgas, J) ----
    all_shares = np.empty((n_runs, lga_count, J))
    for r, run_df in enumerate(all_runs):
        all_shares[r] = run_df[share_cols].values

    # ---- Winner per LGA per run (vectorised argmax) ----
    winner_indices = np.argmax(all_shares, axis=2)  # (n_runs, n_lgas) — int indices

    # ---- Seat counts: count how many LGAs each party wins per run ----
    seat_matrix = np.zeros((n_runs, J), dtype=int)
    for j in range(J):
        seat_matrix[:, j] = np.sum(winner_indices == j, axis=1)

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

    # Population-weighted national shares
    national = _pop_weighted_national(lga_results, party_names)

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

    return {
        "national_shares": national,
        "zonal_shares": zonal,
        "seat_counts": seats,
        "national_turnout": turnout,
    }
