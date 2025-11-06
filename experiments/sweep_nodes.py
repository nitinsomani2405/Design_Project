from __future__ import annotations

import argparse
import os
import csv

import numpy as np

from uav_aoi.config import load_config
from uav_aoi.env import UAV, Radio
from uav_aoi.sim import SimParams, init_nodes_random, simulate, ensure_dir
from uav_aoi.metrics import compute_metrics


def main() -> None:
    p = argparse.ArgumentParser(description="Sweep N nodes and save results")
    p.add_argument("--config", type=str, default="configs/default.yaml")
    p.add_argument("--minN", type=int, default=10)
    p.add_argument("--maxN", type=int, default=50)
    p.add_argument("--step", type=int, default=10)
    p.add_argument("--out", type=str, default="runs")
    args = p.parse_args()

    cfg = load_config(args.config)
    seed = int(cfg.get("seed", 42))
    rng = np.random.default_rng(seed)
    field_size = tuple(cfg["field_size"])  # type: ignore[assignment]
    uav_cfg = cfg["uav"]
    radio_cfg = cfg["radio"]
    radio = Radio(
        bandwidth_Hz=float(radio_cfg["bandwidth_Hz"]),
        noise_W=float(radio_cfg["noise_W"]),
        pathloss_exponent=float(radio_cfg["pathloss_exponent"]),
        snr_threshold_linear=float(radio_cfg["snr_threshold_linear"]),
        comm_radius_m=float(radio_cfg["comm_radius_m"]),
    )
    ensure_dir(args.out)
    results_csv = os.path.join(args.out, "sweep_N.csv")
    with open(results_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "avg_aoi", "total_energy_Wh"]) 
        for N in range(args.minN, args.maxN + 1, args.step):
            nodes = init_nodes_random(N, (float(field_size[0]), float(field_size[1])), rng)
            uav = UAV(
                x=0.0,
                y=0.0,
                speed_mps=float(uav_cfg["speed_mps"]),
                battery_Wh=float(uav_cfg["battery_Wh"]),
                P_move_W=float(uav_cfg["P_move_W"]),
                P_hover_W=float(uav_cfg["P_hover_W"]),
                P_tx_W=float(uav_cfg["P_tx_W"]),
            )
            params = SimParams(
                field_size=(float(field_size[0]), float(field_size[1])),
                mission_time_s=float(cfg["mission_time_s"]),
                payload_bits=int(cfg["payload_bits"]),
                policy=str(cfg["policy"]),
                beta=float(cfg["beta"]),
                gamma=float(cfg["gamma"]),
                alpha=float(cfg["alpha"]),
                greedy_mode=bool(cfg.get("greedy_mode", False)),
                hover_cap_s=None,
            )
            summary = simulate(nodes, uav, radio, params, seed)
            m = compute_metrics(summary["log_csv"])
            writer.writerow([N, m["avg_aoi"], m["total_energy_Wh"]])


if __name__ == "__main__":
    main()


