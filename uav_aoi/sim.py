from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import os
import csv

import numpy as np

from .aoi import AoIState
from .env import (
    UAV,
    Node,
    Radio,
    euclidean,
    flight_time_s,
    achievable_rate_bps,
    energy_fly_Wh,
    energy_hover_Wh,
    energy_tx_Wh,
    in_coverage,
)
from .planner import make_policy, nearest_neighbor_order, two_opt


@dataclass
class SimParams:
    field_size: Tuple[float, float]
    mission_time_s: float
    payload_bits: int
    policy: str
    beta: float
    gamma: float
    alpha: float
    greedy_mode: bool = False  # if True, choose next by policy each step; else follow route
    hover_cap_s: Optional[float] = None  # None => no cap


def init_nodes_random(N: int, field_size: Tuple[float, float], rng: np.random.Generator) -> List[Node]:
    xs = rng.uniform(0.0, field_size[0], size=N)
    ys = rng.uniform(0.0, field_size[1], size=N)
    return [Node(i, float(xs[i]), float(ys[i])) for i in range(N)]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def timestamp_run_dir(base: str = "runs") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(base, ts)
    ensure_dir(path)
    return path


def simulate(
    nodes: List[Node],
    uav: UAV,
    radio: Radio,
    params: SimParams,
    seed: int,
    run_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a single simulation and save a CSV log.

    Returns a dictionary with summary metrics and paths.
    """

    rng = np.random.default_rng(seed)
    if run_dir is None:
        run_dir = timestamp_run_dir()
    ensure_dir(run_dir)

    # Prepare routing or greedy policy
    positions = [(n.x, n.y) for n in nodes]
    if params.greedy_mode:
        route_indices: List[int] = []
    else:
        route_indices = nearest_neighbor_order(positions)
        route_indices = two_opt(route_indices, positions)

    aoi = AoIState.zeros(len(nodes))
    t = 0.0
    energy_Wh = 0.0
    E_max_Wh = uav.battery_Wh
    current_idx_rr = -1
    policy_fn = make_policy(params.policy)

    # Logs
    log_path = os.path.join(run_dir, "log.csv")
    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time_s",
            "energy_Wh",
            "uav_x",
            "uav_y",
            "served_node",
            "aoi_avg",
            "aoi_max",
        ])

    visited_path: List[Tuple[float, float]] = [(uav.x, uav.y)]
    step = 0
    route_ptr = 0
    while t < params.mission_time_s and energy_Wh < E_max_Wh:
        # Select next node index
        if params.greedy_mode:
            if params.policy.upper() == "RR":
                j = policy_fn(current_idx_rr, len(nodes))  # type: ignore[arg-type]
                current_idx_rr = j
            elif params.policy.upper() == "MAF":
                j = policy_fn(aoi.values)  # type: ignore[assignment]
            else:  # AWN
                j = policy_fn(
                    aoi.values,
                    (uav.x, uav.y),
                    positions,
                    params.beta,
                    params.gamma,
                )
        else:
            if route_ptr >= len(nodes):
                route_ptr = 0
            j = route_indices[route_ptr]
            route_ptr += 1

        node_j = nodes[j]
        d = euclidean((uav.x, uav.y), (node_j.x, node_j.y))

        # Fly
        t_fly = flight_time_s(d, uav.speed_mps)
        e_fly = energy_fly_Wh(d, uav.speed_mps, uav.P_move_W)
        t += t_fly
        aoi.increment(t_fly)
        energy_Wh += e_fly
        if energy_Wh >= E_max_Wh or t >= params.mission_time_s:
            break
        uav.move_to(node_j.x, node_j.y)
        visited_path.append((uav.x, uav.y))

        # Communication/hover
        d_now = 0.0  # at node location
        R = achievable_rate_bps(uav.P_tx_W, d_now, radio)
        t_tx = params.payload_bits / max(R, 1e-9)
        if params.hover_cap_s is not None:
            t_hover = min(t_tx, params.hover_cap_s)
        else:
            t_hover = t_tx
        # Success model: coverage or SNR threshold
        success = in_coverage(d_now, radio)
        e_hover = energy_hover_Wh(t_hover, uav.P_hover_W)
        e_tx = energy_tx_Wh(min(t_tx, t_hover), uav.P_tx_W)
        t += t_hover
        aoi.increment(t_hover)
        energy_Wh += e_hover + e_tx

        if energy_Wh >= E_max_Wh or t >= params.mission_time_s:
            break
        if success:
            aoi.reset(j)

        # Log snapshot
        with open(log_path, "a", newline="") as f:
            writer = csv.writer(f)
            avg_aoi = float(np.mean(aoi.values))
            max_aoi = float(np.max(aoi.values))
            writer.writerow([t, energy_Wh, uav.x, uav.y, j, avg_aoi, max_aoi])

        step += 1

    summary = {
        "run_dir": run_dir,
        "log_csv": log_path,
        "visited_path": visited_path,
        "final_time_s": t,
        "final_energy_Wh": energy_Wh,
        "E_max_Wh": E_max_Wh,
        "avg_aoi": float(np.mean(aoi.values)) if aoi.values else 0.0,
        "max_aoi": float(np.max(aoi.values)) if aoi.values else 0.0,
    }
    return summary


