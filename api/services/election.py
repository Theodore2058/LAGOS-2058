"""Election runner service — transforms engine results to API schemas."""

import numpy as np
from pathlib import Path

from election_engine.config import Party, EngineParams, ElectionConfig
from election_engine.election import run_election

from api.schemas.party import PartySchema
from api.schemas.election import (
    EngineParamsInput, ElectionResultsResponse, SpreadCheckResult,
    ZonalResult, StateResult, LGAResultRow, SwingLGA,
)

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "nigeria_lga_polsim_2058.xlsx"

ADMIN_ZONE_NAMES = {
    1: "Lagos", 2: "Niger", 3: "Confluence", 4: "Littoral",
    5: "Eastern", 6: "Central", 7: "Chad", 8: "Savanna",
}


def party_schema_to_engine(ps: PartySchema) -> Party:
    strongholds = None
    if ps.regional_strongholds:
        strongholds = {int(k): v for k, v in ps.regional_strongholds.items()}
    return Party(
        name=ps.name,
        positions=np.array(ps.positions, dtype=np.float64),
        valence=ps.valence,
        leader_ethnicity=ps.leader_ethnicity,
        religious_alignment=ps.religious_alignment,
        demographic_coefficients=ps.demographic_coefficients,
        regional_strongholds=strongholds,
        economic_positioning=ps.economic_positioning,
    )


def params_to_engine(pi: EngineParamsInput) -> EngineParams:
    return EngineParams(
        q=pi.q, beta_s=pi.beta_s, alpha_e=pi.alpha_e, alpha_r=pi.alpha_r,
        scale=pi.scale, tau_0=pi.tau_0, tau_1=pi.tau_1, tau_2=pi.tau_2,
        beta_econ=pi.beta_econ, kappa=pi.kappa,
        sigma_national=pi.sigma_national, sigma_regional=pi.sigma_regional,
        sigma_turnout=pi.sigma_turnout, sigma_turnout_regional=pi.sigma_turnout_regional,
    )


def run_and_transform(parties: list[PartySchema], params_input: EngineParamsInput,
                       n_monte_carlo: int, seed: int | None) -> ElectionResultsResponse:
    engine_parties = [party_schema_to_engine(p) for p in parties]
    engine_params = params_to_engine(params_input)
    config = ElectionConfig(params=engine_params, parties=engine_parties, n_monte_carlo=n_monte_carlo)

    results = run_election(str(DATA_PATH), config, seed=seed, verbose=False)

    summary = results["summary"]
    mc = results["mc_aggregated"]
    spread = results["spread_checks"]
    lga_df = results["lga_results_base"]
    party_names = [p.name for p in engine_parties]

    # National vote shares and counts
    national_shares = {k: round(v, 6) for k, v in summary["national_shares"].items()}
    national_votes = {k: int(v) for k, v in summary["national_votes"].items()}
    national_turnout = round(float(summary["national_turnout"]), 4)

    # Seat counts from MC
    seat_stats = mc["seat_stats"]
    seat_counts = {}
    seat_std = {}
    for _, row in seat_stats.iterrows():
        name = row["Party"]
        seat_counts[name] = round(float(row["Mean Seats"]), 1)
        seat_std[name] = round(float(row["Std Seats"]), 2)

    # Win probabilities
    win_prob = {k: round(float(v), 4) for k, v in mc["win_probabilities"].items()}

    # ENP
    enp = round(float(mc["enp_stats"]["mean"]), 2)

    # Spread checks
    spread_checks = {}
    for pname, sc in spread.items():
        spread_checks[pname] = SpreadCheckResult(
            states_above_25=int(sc["states_meeting_25pct"]),
            met=bool(sc["meets_requirement"]),
        )

    # Zonal results
    zonal_df = summary["zonal_shares"]
    zonal_results = []
    for _, row in zonal_df.iterrows():
        az = int(row["Administrative Zone"])
        shares = {}
        winner = ""
        best = -1.0
        for pn in party_names:
            col = f"{pn}_share"
            if col in row:
                val = round(float(row[col]), 6)
                shares[pn] = val
                if val > best:
                    best = val
                    winner = pn
        zonal_results.append(ZonalResult(
            az=az,
            az_name=str(row.get("AZ Name", ADMIN_ZONE_NAMES.get(az, f"AZ {az}"))),
            turnout=round(float(row.get("Turnout", 0)), 4),
            vote_shares=shares,
            winner=winner,
        ))

    # State results
    state_results = []
    if "state_mc_stats" in mc:
        sdf = mc["state_mc_stats"]
        for _, row in sdf.iterrows():
            shares = {}
            winner = ""
            best = -1.0
            for pn in party_names:
                col = f"{pn}_share_mean"
                if col in row.index:
                    val = round(float(row[col]), 6)
                    shares[pn] = val
                    if val > best:
                        best = val
                        winner = pn
            state_results.append(StateResult(
                state=str(row["State"]),
                az=0,
                turnout=round(float(row.get("Turnout Mean", 0)), 4),
                vote_shares=shares,
                winner=winner,
            ))

    # LGA results (sample first 774)
    lga_results = []
    for _, row in lga_df.iterrows():
        shares = {}
        winner = ""
        best = -1.0
        for pn in party_names:
            col = f"{pn}_share"
            if col in row.index:
                val = round(float(row[col]), 6)
                shares[pn] = val
                if val > best:
                    best = val
                    winner = pn
        lga_results.append(LGAResultRow(
            lga=str(row.get("LGA Name", "")),
            state=str(row.get("State", "")),
            az=int(row.get("Administrative Zone", 0)),
            turnout=round(float(row.get("Turnout", 0)), 4),
            vote_shares=shares,
            winner=winner,
        ))

    # Swing LGAs
    swing_lgas = []
    if "swing_lgas" in mc and mc["swing_lgas"] is not None and len(mc["swing_lgas"]) > 0:
        swing_df = mc["swing_lgas"]
        for _, row in swing_df.iterrows():
            pshares = []
            for pn in party_names:
                col = f"{pn}_share"
                if col in row.index:
                    pshares.append((pn, float(row[col])))
            pshares.sort(key=lambda x: -x[1])
            margin = pshares[0][1] - pshares[1][1] if len(pshares) >= 2 else 1.0
            swing_lgas.append(SwingLGA(
                lga=str(row.get("LGA Name", "")),
                state=str(row.get("State", "")),
                margin=round(margin, 4),
                top_parties=[p[0] for p in pshares[:2]],
            ))

    return ElectionResultsResponse(
        national_vote_shares=national_shares,
        national_vote_counts=national_votes,
        national_turnout=national_turnout,
        seat_counts=seat_counts,
        seat_std=seat_std,
        win_probability=win_prob,
        enp=enp,
        spread_check=spread_checks,
        zonal_results=zonal_results,
        state_results=state_results,
        lga_results=lga_results,
        swing_lgas=swing_lgas,
    )
