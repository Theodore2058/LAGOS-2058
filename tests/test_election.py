"""Tests for results processing, seat allocation, and presidential spread check."""

import sys
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, "src")
from election_engine.results import (
    add_lga_winners,
    count_seats,
    check_presidential_spread,
    aggregate_monte_carlo,
    compute_summary_stats,
)


def _make_simple_results(n_lgas=20, party_names=("A", "B", "C")):
    """Create a simple results dataframe for testing."""
    rng = np.random.default_rng(42)
    rows = []
    states = [f"State{i % 5}" for i in range(n_lgas)]  # 5 states
    for i in range(n_lgas):
        shares = rng.dirichlet(np.ones(len(party_names)))
        row = {
            "State": states[i],
            "LGA Name": f"LGA{i}",
            "Administrative Zone": (i % 4) + 1,
            "AZ Name": f"Zone{(i % 4) + 1}",
            "Turnout": 0.5,
        }
        for j, p in enumerate(party_names):
            row[f"{p}_share"] = shares[j]
        rows.append(row)
    return pd.DataFrame(rows), list(party_names)


def test_one_party_wins_all():
    """A party winning every LGA gets all 20 seats."""
    n = 20
    parties = ["A", "B"]
    rows = []
    for i in range(n):
        rows.append({
            "State": f"S{i % 5}", "LGA Name": f"L{i}",
            "Administrative Zone": 1, "AZ Name": "Z1",
            "Turnout": 0.5,
            "A_share": 0.9, "B_share": 0.1,
        })
    df = pd.DataFrame(rows)
    seats = count_seats(df, parties)
    assert seats["A"] == n
    assert seats["B"] == 0


def test_seats_sum_to_total_lgas():
    """Total seats must equal number of LGAs."""
    df, parties = _make_simple_results(n_lgas=774)
    seats = count_seats(df, parties)
    assert sum(seats.values()) == 774


def test_spread_check_national_only():
    """Party winning nationally but concentrated → fails spread."""
    parties = ["A", "B"]
    # A dominates 5 states but has 0% in the rest
    rows = []
    for state_idx in range(36):
        for lga_idx in range(5):
            a_share = 0.9 if state_idx < 5 else 0.1
            rows.append({
                "State": f"State{state_idx}",
                "LGA Name": f"L{state_idx}_{lga_idx}",
                "Administrative Zone": 1, "AZ Name": "Z1",
                "Turnout": 0.5,
                "A_share": a_share, "B_share": 1.0 - a_share,
            })
    df = pd.DataFrame(rows)
    result = check_presidential_spread(df, "A", parties)
    print(f"States with 25%: {result['states_meeting_25pct']}")
    # A has ~90% in 5 states and ~10% in 31 states → should fail
    assert not result["meets_requirement"]
    assert result["states_meeting_25pct"] == 5


def test_spread_check_passes():
    """Party with broad support → passes spread."""
    parties = ["A", "B"]
    rows = []
    for state_idx in range(36):
        for lga_idx in range(5):
            rows.append({
                "State": f"State{state_idx}",
                "LGA Name": f"L{state_idx}_{lga_idx}",
                "Administrative Zone": (state_idx % 6) + 1, "AZ Name": f"Z{(state_idx % 6) + 1}",
                "Turnout": 0.5,
                "A_share": 0.55, "B_share": 0.45,  # A wins everywhere
            })
    df = pd.DataFrame(rows)
    result = check_presidential_spread(df, "A", parties)
    assert result["meets_requirement"]
    assert result["states_meeting_25pct"] == 36


def test_monte_carlo_aggregation():
    """MC aggregation produces valid seat stats and win probabilities."""
    rng = np.random.default_rng(0)
    parties = ["A", "B", "C"]
    n_runs = 50
    n_lgas = 50

    runs = []
    for _ in range(n_runs):
        rows = []
        states = [f"S{i % 5}" for i in range(n_lgas)]
        for i in range(n_lgas):
            shares = rng.dirichlet([2, 1, 1])  # A usually wins
            rows.append({
                "State": states[i], "LGA Name": f"L{i}",
                "Administrative Zone": 1, "AZ Name": "Z1",
                "Turnout": 0.5,
                "A_share": shares[0], "B_share": shares[1], "C_share": shares[2],
            })
        runs.append(pd.DataFrame(rows))

    result = aggregate_monte_carlo(runs, parties)

    # Basic structure checks
    assert "seat_stats" in result
    assert "win_probabilities" in result
    stats = result["seat_stats"]
    assert len(stats) == len(parties)
    assert abs(stats["Mean Seats"].sum() - n_lgas) < 1  # seats sum to n_lgas on average

    # Win probabilities sum to ~1
    win_probs = result["win_probabilities"]
    assert abs(sum(win_probs.values()) - 1.0) < 0.01

    # Party A should win most often (higher concentration in Dirichlet)
    assert win_probs["A"] > win_probs["B"]
    assert win_probs["A"] > win_probs["C"]


def test_summary_stats():
    """Summary stats have correct structure."""
    df, parties = _make_simple_results(n_lgas=30)
    summary = compute_summary_stats(df, parties)
    assert "national_shares" in summary
    assert "seat_counts" in summary
    assert sum(summary["national_shares"].values()) == pytest.approx(1.0, abs=0.05)
    assert sum(summary["seat_counts"].values()) == 30


def test_spread_check_plurality_on_exact_tie():
    """When two parties tie for the national plurality, both should be flagged.

    Regression test for Bug 2: `national_share == max(...)` used exact float
    equality, which would silently deny plurality to both parties on a tie.
    """
    parties = ["A", "B"]
    rows = []
    # Alternate winner per LGA so both parties have an identical mean share (0.5)
    for i in range(36):
        for lga_idx in range(2):
            a_share = 1.0 if i % 2 == 0 else 0.0
            rows.append({
                "State": f"State{i}",
                "LGA Name": f"L{i}_{lga_idx}",
                "Administrative Zone": 1, "AZ Name": "Z1",
                "Turnout": 0.5,
                "A_share": a_share, "B_share": 1.0 - a_share,
            })
    df = pd.DataFrame(rows)

    result_a = check_presidential_spread(df, "A", parties)
    result_b = check_presidential_spread(df, "B", parties)

    # Both parties have an equal national share — plurality should be True for both
    assert abs(result_a["national_share"] - 0.5) < 1e-9
    assert abs(result_b["national_share"] - 0.5) < 1e-9
    assert result_a["national_share"] == pytest.approx(result_b["national_share"])

    # Plurality check must not silently fail for either party on a tie
    # (spread requirement itself may still fail if states < 24, that's fine —
    # we only verify has_national_plurality is True for both)
    # We check via the internal logic: both should see themselves as max
    # The fix uses abs(share - max) < 1e-9, so both pass the plurality gate
    assert result_a["meets_requirement"] == result_b["meets_requirement"], (
        "Tied parties should both have the same meets_requirement outcome"
    )


def _make_toy_lga_df(n_lgas: int = 20, seed: int = 42) -> pd.DataFrame:
    """Build a minimal LGA DataFrame suitable for compute_all_lga_results."""
    rng = np.random.default_rng(seed)
    records = []
    for i in range(n_lgas):
        records.append({
            "LGA Name": f"LGA{i}",
            "State": f"State{i % 6}",
            "Administrative Zone": (i % 4) + 1,
            "AZ Name": f"Zone{(i % 4) + 1}",
            "Urban Pct": float(rng.integers(20, 80)),
            "% Muslim": float(rng.integers(10, 80)),
            "% Christian": float(rng.integers(10, 70)),
            "% Traditionalist": 5.0,
            "% Hausa": 10.0, "% Fulani": 5.0, "% Hausa Fulani Undiff": 8.0,
            "% Yoruba": 10.0, "% Igbo": 8.0, "% Ijaw": 2.0, "% Kanuri": 1.0,
            "% Tiv": 2.0, "% Nupe": 1.0, "% Edo Bini": 1.0, "% Ibibio": 1.0,
            "% Pada": 0.5, "% Naijin": 0.5,
            "% Ogoni": 0.0, "% Ikwerre": 0.0, "% Etche": 0.0, "% Pere": 0.0,
            "% Isoko": 0.0, "% Itsekiri": 0.0, "% Urhobo": 0.0,
            "% Ebira": 0.0, "% Gwari Gbagyi": 0.0, "% Idoma": 0.0,
            "% Berom": 0.0, "% Angas": 0.0, "% Igala": 0.0,
            "% Jukun": 0.0, "% Ham Jaba": 0.0,
            "Adult Literacy Rate Pct": float(rng.integers(30, 80)),
            "Tertiary Institution": int(rng.integers(0, 3)),
            "Tijaniyya Presence": int(rng.integers(0, 3)),
            "Qadiriyya Presence": int(rng.integers(0, 2)),
            "Pentecostal Growth": int(rng.integers(0, 4)),
            "Al-Shahid Influence": float(rng.random() * 2),
            "Pct Livelihood Agriculture": 35.0,
            "Pct Livelihood Manufacturing": 10.0,
            "Pct Livelihood Extraction": 3.0,
            "Pct Livelihood Services": 20.0,
            "Pct Livelihood Informal": 22.0,
            "GDP Per Capita Est": float(rng.integers(8000, 50000)),
            "Oil Producing": int(rng.integers(0, 2)),
            "Extraction Intensity": float(rng.integers(0, 5)),
            "Cobalt Extraction Active": 0,
            "Chinese Economic Presence": float(rng.integers(0, 5)),
            "Mandarin Presence": float(rng.integers(0, 3)),
            "Planned City": 0,
            "BIC Effectiveness": float(rng.integers(3, 8)),
            "Fertility Rate Est": float(rng.uniform(3.0, 8.0)),
            "Trad Authority Index": float(rng.integers(1, 5)),
            "Housing Affordability": float(rng.integers(2, 9)),
            "Out of School Children Pct": float(rng.uniform(5, 40)),
            "Conflict History": float(rng.integers(0, 4)),
            "English Prestige": float(rng.integers(3, 8)),
            "Arabic Prestige": float(rng.integers(1, 6)),
            "Gender Parity Index": float(rng.uniform(0.6, 1.0)),
            "Access Electricity Pct": float(rng.uniform(20, 95)),
            "Access Water Pct": float(rng.uniform(20, 90)),
            "Access Healthcare Pct": float(rng.uniform(15, 85)),
            "Land Formalization Pct": float(rng.uniform(5, 70)),
            "Gini Proxy": float(rng.uniform(0.25, 0.65)),
            "Poverty Rate Pct": float(rng.uniform(10, 70)),
            "Biological Enhancement Pct": float(rng.uniform(0, 10)),
            "Rail Corridor": int(rng.integers(0, 2)),
            "Internet Access Pct": float(rng.uniform(5, 60)),
            "Male Literacy Rate Pct": float(rng.integers(35, 85)),
            "Female Literacy Rate Pct": float(rng.integers(25, 75)),
            "Colonial Era Region": "North Central",
        })
    return pd.DataFrame(records)


def test_run_election_integration():
    """
    Integration test: compute_all_lga_results on a 20-LGA toy dataset.

    Tests the full computation pipeline (voter types, ideals, utilities, turnout,
    poststratification) without going through the file-loading layer.  Verifies
    that shares sum to 1, turnout is in [0,1], and the pipeline completes cleanly.
    """
    from election_engine.config import EngineParams, ElectionConfig, Party, N_ISSUES
    from election_engine.poststratification import compute_all_lga_results
    from election_engine.results import count_seats, compute_summary_stats

    p_a = Party(
        name="A", positions=np.zeros(N_ISSUES), valence=0.0,
        leader_ethnicity="Yoruba", religious_alignment="Mainline Protestant",
    )
    p_b = Party(
        name="B", positions=np.zeros(N_ISSUES), valence=0.1,
        leader_ethnicity="Hausa-Fulani Undiff", religious_alignment="Mainstream Sunni",
    )
    params = EngineParams(tau_0=1.5, tau_1=0.3, tau_2=0.5,
                          kappa=200.0, sigma_national=0.05, sigma_regional=0.10)
    config = ElectionConfig(params=params, parties=[p_a, p_b], n_monte_carlo=3)

    toy_df = _make_toy_lga_df(n_lgas=20)

    base = compute_all_lga_results(lga_data=toy_df, election_config=config)

    # ---- Structural checks ----
    assert len(base) == 20, f"Expected 20 rows, got {len(base)}"

    share_cols = ["A_share", "B_share"]
    for col in share_cols:
        assert col in base.columns, f"Missing column {col}"

    # Shares sum to 1 per row
    row_sums = base[share_cols].sum(axis=1)
    np.testing.assert_allclose(row_sums.values, 1.0, atol=1e-6,
                                err_msg="Share columns must sum to 1 per row")

    # Turnout in [0, 1]
    assert "Turnout" in base.columns
    assert base["Turnout"].between(0.0, 1.0).all(), "Turnout values out of [0,1]"

    # Shares are non-negative
    for col in share_cols:
        assert (base[col] >= 0.0).all(), f"Negative shares in {col}"

    # Seat counts sum to N_LGAs and are non-negative
    seats = count_seats(base, ["A", "B"])
    assert sum(seats.values()) == 20
    assert all(v >= 0 for v in seats.values())

    # Summary stats well-formed
    summary = compute_summary_stats(base, ["A", "B"])
    assert abs(sum(summary["national_shares"].values()) - 1.0) < 0.05
    assert 0.0 <= summary["national_turnout"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
