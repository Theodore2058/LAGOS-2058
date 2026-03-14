"""
Trade graph construction from LGA geographic data.

Builds the network of trade routes between 774 LGAs using:
- GeoJSON centroids for distance calculation (Haversine)
- State-based adjacency for road connections
- Rail corridor flags for rail routes
- Coastal/riverine terrain for water routes
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

from src.economy.core.types import SimConfig, TradeRoute
from src.economy.data.lga_loader import EconomyLGAData

logger = logging.getLogger(__name__)

# Maximum distance for same-state connections (km)
SAME_STATE_MAX_DIST = 200.0
# Maximum distance for cross-state connections (km)
CROSS_STATE_MAX_DIST = 100.0
# Rail corridor states (Lagos-Gausa high-speed corridor)
RAIL_CORRIDOR_STATES = {
    "Lagos", "Ogun", "Oyo", "Kwara", "Niger", "FCT", "Kaduna", "Kano",
}
# Coastal/port states
COASTAL_STATES = {
    "Lagos", "Ogun", "Ondo", "Delta", "Bayelsa", "Rivers",
    "Akwa Ibom", "Cross River",
}
# River Niger/Benue states
RIVER_STATES = {
    "Niger", "Kwara", "Kogi", "Benue", "Nassarawa", "Adamawa",
    "Taraba", "FCT",
}


@dataclass
class TradeGraph:
    """The trade network between LGAs."""
    n_lgas: int
    n_routes: int
    edges: np.ndarray            # (N_ROUTES, 2) int32: (source, dest)
    distances: np.ndarray        # (N_ROUTES,) float64: km
    route_types: np.ndarray      # (N_ROUTES,) int8: 0=road, 1=rail, 2=river, 3=sea
    qualities: np.ndarray        # (N_ROUTES,) float64: 0-1
    surcharges: np.ndarray       # (N_ROUTES,) float64: al-Shahid surcharge
    adjacency_list: dict[int, list[int]] = field(default_factory=dict)
    adjacency_sparse: Optional[csr_matrix] = None
    lga_centroids: Optional[np.ndarray] = None  # (N, 2) lat, lon


def build_trade_graph(
    lga_data: EconomyLGAData,
    config: SimConfig,
    geojson_path: Optional[str | Path] = None,
) -> TradeGraph:
    """
    Construct the trade network from LGA geographic data.

    Algorithm:
    1. Load LGA centroids from GeoJSON
    2. Connect same-state LGAs by road
    3. Connect cross-state neighbors within distance threshold
    4. Add rail routes along Lagos-Gausa corridor
    5. Add sea routes between coastal LGAs
    6. Add river routes along Niger/Benue
    7. Set quality from infrastructure data
    8. Set al-Shahid surcharges

    Returns: TradeGraph
    """
    N = lga_data.n_lgas

    if geojson_path is None:
        geojson_path = Path(__file__).resolve().parents[3] / "GeoJSON" / "nga_admin2.geojson"

    # Load centroids
    centroids = _load_centroids(geojson_path, lga_data)
    logger.info("Loaded centroids for %d LGAs", len(centroids))

    # Build edges
    edges = []
    route_types = []

    # 1. Same-state road connections
    state_lgas: dict[str, list[int]] = {}
    for i, s in enumerate(lga_data.states):
        state_lgas.setdefault(s, []).append(i)

    for state, lgas in state_lgas.items():
        if len(lgas) <= 1:
            continue
        for i_idx in range(len(lgas)):
            for j_idx in range(i_idx + 1, len(lgas)):
                a, b = lgas[i_idx], lgas[j_idx]
                dist = _haversine(centroids[a], centroids[b])
                if dist <= SAME_STATE_MAX_DIST:
                    edges.append((a, b, dist))
                    route_types.append(0)  # road

    # 2. Cross-state neighbors
    for i in range(N):
        for j in range(i + 1, N):
            if lga_data.states[i] != lga_data.states[j]:
                dist = _haversine(centroids[i], centroids[j])
                if dist <= CROSS_STATE_MAX_DIST:
                    # Avoid duplicate
                    edges.append((i, j, dist))
                    route_types.append(0)

    # 3. Rail corridor (connect all LGAs on rail corridor that have rail flag)
    rail_lgas = [
        i for i in range(N)
        if lga_data.rail_corridor[i] > 0
        or lga_data.states[i] in RAIL_CORRIDOR_STATES
    ]
    # Connect sequential rail LGAs (sorted by longitude for west-east corridor)
    rail_sorted = sorted(rail_lgas, key=lambda i: centroids[i][1])  # sort by lon
    for idx in range(len(rail_sorted) - 1):
        a, b = rail_sorted[idx], rail_sorted[idx + 1]
        dist = _haversine(centroids[a], centroids[b])
        if dist <= 300:  # rail connects further apart
            edges.append((a, b, dist))
            route_types.append(1)  # rail

    # 4. Sea routes between coastal LGAs
    coastal_lgas = [
        i for i in range(N) if lga_data.states[i] in COASTAL_STATES
        and ("coastal" in lga_data.terrain[i].lower()
             or "mangrove" in lga_data.terrain[i].lower()
             or lga_data.states[i] == "Lagos")
    ]
    # Connect coastal LGAs within 500km
    for i_idx in range(len(coastal_lgas)):
        for j_idx in range(i_idx + 1, len(coastal_lgas)):
            a, b = coastal_lgas[i_idx], coastal_lgas[j_idx]
            dist = _haversine(centroids[a], centroids[b])
            if dist <= 500:
                edges.append((a, b, dist))
                route_types.append(3)  # sea

    # 5. River routes
    river_lgas = [
        i for i in range(N) if lga_data.states[i] in RIVER_STATES
        and ("riverine" in lga_data.terrain[i].lower()
             or "swamp" in lga_data.terrain[i].lower())
    ]
    river_sorted = sorted(river_lgas, key=lambda i: centroids[i][0])  # sort by lat
    for idx in range(len(river_sorted) - 1):
        a, b = river_sorted[idx], river_sorted[idx + 1]
        dist = _haversine(centroids[a], centroids[b])
        if dist <= 200:
            edges.append((a, b, dist))
            route_types.append(2)  # river

    # Convert to arrays
    n_routes = len(edges)
    edge_arr = np.zeros((n_routes, 2), dtype=np.int32)
    dist_arr = np.zeros(n_routes, dtype=np.float64)
    type_arr = np.array(route_types, dtype=np.int8)

    for idx, (a, b, d) in enumerate(edges):
        edge_arr[idx] = [a, b]
        dist_arr[idx] = d

    # Quality from road infrastructure
    qual_arr = np.ones(n_routes, dtype=np.float64)
    for idx in range(n_routes):
        a, b = edge_arr[idx]
        # Average quality of endpoints
        if type_arr[idx] == 0:  # road
            qual_arr[idx] = (lga_data.road_quality[a] + lga_data.road_quality[b]) / 2.0
        elif type_arr[idx] == 1:  # rail
            qual_arr[idx] = 0.9  # rail is high quality
        else:
            qual_arr[idx] = 0.8  # water routes moderate quality
    qual_arr = np.clip(qual_arr, 0.05, 1.0)

    # Al-Shahid surcharges
    surcharge_arr = np.zeros(n_routes, dtype=np.float64)
    for idx in range(n_routes):
        a, b = edge_arr[idx]
        max_control = max(lga_data.alsahid_influence[a], lga_data.alsahid_influence[b])
        max_control_norm = max_control / max(lga_data.alsahid_influence.max(), 1.0)
        if max_control_norm > 0.3:
            surcharge_arr[idx] = 0.3 + 0.2 * max_control_norm

    # Build adjacency list
    adj: dict[int, list[int]] = {i: [] for i in range(N)}
    for idx in range(n_routes):
        a, b = edge_arr[idx]
        adj[a].append(b)
        adj[b].append(a)

    # Build sparse adjacency matrix (for shortest path)
    row = np.concatenate([edge_arr[:, 0], edge_arr[:, 1]])
    col = np.concatenate([edge_arr[:, 1], edge_arr[:, 0]])
    data = np.concatenate([dist_arr, dist_arr])
    adj_sparse = csr_matrix((data, (row, col)), shape=(N, N))

    # Check connectivity
    connected = sum(1 for v in adj.values() if len(v) > 0)
    isolated = N - connected
    if isolated > 0:
        logger.warning("%d LGAs are isolated (no trade routes)", isolated)

    logger.info(
        "Trade graph: %d routes (%d road, %d rail, %d river, %d sea), %d isolated LGAs",
        n_routes,
        (type_arr == 0).sum(),
        (type_arr == 1).sum(),
        (type_arr == 2).sum(),
        (type_arr == 3).sum(),
        isolated,
    )

    return TradeGraph(
        n_lgas=N,
        n_routes=n_routes,
        edges=edge_arr,
        distances=dist_arr,
        route_types=type_arr,
        qualities=qual_arr,
        surcharges=surcharge_arr,
        adjacency_list=adj,
        adjacency_sparse=adj_sparse,
        lga_centroids=centroids,
    )


def update_trade_surcharges(graph: TradeGraph, alsahid_control: np.ndarray) -> None:
    """
    Refresh per-route surcharges from current al-Shahid control levels.

    Called during the structural tick after al-Shahid mutations are applied,
    so trade costs reflect territorial changes.

    Vectorized: processes all routes simultaneously instead of Python loop.
    """
    edges = graph.edges  # (R, 2)
    control_a = alsahid_control[edges[:, 0]]  # (R,)
    control_b = alsahid_control[edges[:, 1]]  # (R,)
    max_control = np.maximum(control_a, control_b)  # (R,)

    # Surcharge: 0.3 + 0.2 * max_control where control > 0.05, else 0
    graph.surcharges[:] = np.where(
        max_control > 0.05,
        0.3 + 0.2 * max_control,
        0.0,
    )


def update_trade_qualities(graph: TradeGraph, road_quality: np.ndarray) -> None:
    """
    Refresh per-route road quality from current infrastructure state.

    Called during the structural tick so that infrastructure decay/repair
    feeds back into trade transport costs. Only affects road routes (type 0);
    rail and water routes keep fixed quality.

    Vectorized: processes all routes simultaneously.
    """
    edges = graph.edges  # (R, 2)
    road_mask = graph.route_types == 0  # only road routes

    if road_mask.any():
        a = edges[road_mask, 0]
        b = edges[road_mask, 1]
        # Average quality of the two endpoints
        avg_quality = (road_quality[a] + road_quality[b]) * 0.5
        graph.qualities[road_mask] = np.clip(avg_quality, 0.05, 1.0)


def _load_centroids(
    geojson_path: Path, lga_data: EconomyLGAData,
) -> np.ndarray:
    """
    Load LGA centroids from GeoJSON, matched to LGA data order.
    Returns: (N, 2) array of (lat, lon).
    """
    N = lga_data.n_lgas
    centroids = np.zeros((N, 2), dtype=np.float64)

    with open(geojson_path, "r", encoding="utf-8") as f:
        geo = json.load(f)

    # Build name lookup: (state, lga_name) -> (lat, lon)
    geo_lookup: dict[tuple[str, str], tuple[float, float]] = {}
    for feat in geo["features"]:
        props = feat["properties"]
        state = str(props.get("adm1_name", "")).strip()
        lga = str(props.get("adm2_name", "")).strip()
        lat = props.get("center_lat")
        lon = props.get("center_lon")
        if lat is not None and lon is not None:
            geo_lookup[(state, lga)] = (float(lat), float(lon))

    matched = 0
    for i in range(N):
        key = (lga_data.states[i].strip(), lga_data.lga_names[i].strip())
        if key in geo_lookup:
            centroids[i] = geo_lookup[key]
            matched += 1
        else:
            # Try fuzzy match on LGA name alone
            for (gs, gl), (lat, lon) in geo_lookup.items():
                if gl.lower() == key[1].lower() and gs.lower() == key[0].lower():
                    centroids[i] = (lat, lon)
                    matched += 1
                    break

    if matched < N:
        logger.warning("Only matched %d/%d LGA centroids from GeoJSON", matched, N)
        # Fill unmatched with state average
        state_coords: dict[str, list] = {}
        for i in range(N):
            if centroids[i, 0] != 0:
                state_coords.setdefault(lga_data.states[i], []).append(centroids[i])
        for i in range(N):
            if centroids[i, 0] == 0 and centroids[i, 1] == 0:
                s = lga_data.states[i]
                if s in state_coords and state_coords[s]:
                    avg = np.mean(state_coords[s], axis=0)
                    centroids[i] = avg + np.random.default_rng(i).uniform(-0.1, 0.1, 2)

    return centroids


def _haversine(p1: np.ndarray, p2: np.ndarray) -> float:
    """Haversine distance between two (lat, lon) points in km."""
    R = 6371.0  # Earth radius in km
    lat1, lon1 = np.radians(p1)
    lat2, lon2 = np.radians(p2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


# ---------------------------------------------------------------------------
# Transport cost
# ---------------------------------------------------------------------------

def compute_visibility(
    graph: TradeGraph, max_hops: int,
) -> dict[int, np.ndarray]:
    """
    BFS from every LGA to find visible LGAs within max_hops.

    Returns: dict mapping lga_id → array of visible lga_ids (sorted).
    Cached on the graph object as `_visibility_cache`.
    """
    if hasattr(graph, '_visibility_cache') and graph._visibility_cache is not None:
        cached_hops = getattr(graph, '_visibility_hops', -1)
        if cached_hops == max_hops:
            return graph._visibility_cache

    adj = graph.adjacency_list
    N = graph.n_lgas
    visibility: dict[int, np.ndarray] = {}

    for start in range(N):
        visited = set()
        visited.add(start)
        frontier = [start]
        for _ in range(max_hops):
            next_frontier = []
            for node in frontier:
                for neighbor in adj.get(node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.append(neighbor)
            frontier = next_frontier
            if not frontier:
                break
        visibility[start] = np.array(sorted(visited), dtype=np.int32)

    graph._visibility_cache = visibility  # type: ignore[attr-defined]
    graph._visibility_hops = max_hops  # type: ignore[attr-defined]
    logger.info(
        "Computed BFS visibility: max_hops=%d, avg visible=%.0f LGAs",
        max_hops, np.mean([len(v) for v in visibility.values()]),
    )
    return visibility


def get_best_visible_prices(
    graph: TradeGraph,
    prices: np.ndarray,
    visibility: dict[int, np.ndarray],
) -> np.ndarray:
    """
    For each LGA, find the maximum price within its visibility radius per commodity.

    Returns: (N, C) array of best visible prices.
    """
    N, C = prices.shape
    best_prices = prices.copy()
    for i in range(N):
        visible = visibility.get(i)
        if visible is not None and len(visible) > 1:
            best_prices[i] = prices[visible].max(axis=0)
    return best_prices


def transport_cost(
    commodity_value: float,
    distance_km: float,
    route_type: int,
    road_quality: float,
    alsahid_surcharge: float,
    cost_per_km: float,
    rail_multiplier: float,
) -> float:
    """
    Cost to transport one unit of a commodity along one trade route edge.

    Route type modifiers:
    - Road: base_cost / max(quality, 0.1)
    - Rail: base_cost * rail_multiplier (cheap)
    - River: base_cost * 0.5
    - Sea: base_cost * 0.4
    """
    base_cost = commodity_value * cost_per_km * distance_km

    if route_type == 0:  # road
        modified = base_cost / max(road_quality, 0.1)
    elif route_type == 1:  # rail
        modified = base_cost * rail_multiplier
    elif route_type == 2:  # river
        modified = base_cost * 0.5
    else:  # sea
        modified = base_cost * 0.4

    return modified * (1.0 + alsahid_surcharge)


def transport_cost_vec(
    commodity_value: np.ndarray,  # (N_ROUTES,) or scalar
    distances: np.ndarray,       # (N_ROUTES,)
    route_types: np.ndarray,     # (N_ROUTES,)
    qualities: np.ndarray,       # (N_ROUTES,)
    surcharges: np.ndarray,      # (N_ROUTES,)
    cost_per_km: float,
    rail_multiplier: float,
) -> np.ndarray:
    """Vectorized transport cost calculation."""
    base_cost = commodity_value * cost_per_km * distances

    # Route type modifiers
    modified = np.where(
        route_types == 0, base_cost / np.maximum(qualities, 0.1),
        np.where(
            route_types == 1, base_cost * rail_multiplier,
            np.where(
                route_types == 2, base_cost * 0.5,
                base_cost * 0.4,  # sea
            ),
        ),
    )
    return modified * (1.0 + surcharges)
