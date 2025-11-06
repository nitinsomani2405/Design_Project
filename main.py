from __future__ import annotations

import argparse
from typing import Tuple, List, Dict, Any
import os
import csv
import time
import random
import copy

import numpy as np

from uav_aoi.config import load_config
from uav_aoi.env import UAV, Radio
from uav_aoi.sim import SimParams, init_nodes_random, simulate, ensure_dir
from uav_aoi.metrics import compute_metrics
from uav_aoi.viz import (
    plot_aoi_time,
    plot_energy_time,
    plot_route,
    plot_policy_comparison,
    plot_pareto,
)
import yaml


def build_uav_radio(cfg: Dict[str, Any]) -> tuple[UAV, Radio]:
    uav_cfg = cfg["uav"]
    radio_cfg = cfg["radio"]
    uav = UAV(
        x=0.0,
        y=0.0,
        speed_mps=float(uav_cfg["speed_mps"]),
        battery_Wh=float(uav_cfg["battery_Wh"]),
        P_move_W=float(uav_cfg["P_move_W"]),
        P_hover_W=float(uav_cfg["P_hover_W"]),
        P_tx_W=float(uav_cfg["P_tx_W"]),
    )
    radio = Radio(
        bandwidth_Hz=float(radio_cfg["bandwidth_Hz"]),
        noise_W=float(radio_cfg["noise_W"]),
        pathloss_exponent=float(radio_cfg["pathloss_exponent"]),
        snr_threshold_linear=float(radio_cfg["snr_threshold_linear"]),
        comm_radius_m=float(radio_cfg["comm_radius_m"]),
    )
    return uav, radio


def override_cfg(cfg: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    # Simple overrides
    if args.N is not None:
        cfg["N"] = args.N
    if args.T is not None:
        cfg["mission_time_s"] = args.T
    if args.battery is not None:
        cfg["uav"]["battery_Wh"] = args.battery
    if args.speed is not None:
        cfg["uav"]["speed_mps"] = args.speed
    if args.payload is not None:
        cfg["payload_bits"] = args.payload
    if args.beta is not None:
        cfg["beta"] = args.beta
    if args.gamma is not None:
        cfg["gamma"] = args.gamma
    if args.comm_radius is not None:
        cfg["radio"]["comm_radius_m"] = args.comm_radius
    if args.policy is not None:
        cfg["policy"] = args.policy
    if args.alpha is not None:
        cfg["alpha"] = args.alpha
    if args.seed is not None:
        cfg["seed"] = args.seed
    return cfg


def lock_scenario_seed(args: argparse.Namespace) -> int:
    """Lock a single seed for the entire command execution.
    
    If --seed is provided, use it. Otherwise, generate one time-based seed
    that will be reused for all runs in this command.
    """
    if args.seed is not None:
        return args.seed
    return int(time.time_ns() % 2_147_483_647)


def randomize_unspecified(cfg: Dict[str, Any], args: argparse.Namespace, locked_seed: int | None = None) -> Dict[str, Any]:
    """Randomize parameters that the user did not explicitly set via CLI.

    - seed: use locked_seed if provided, otherwise time-based if not in args
    - policy: random among RR/MAF/AWN if not provided
    - beta/gamma/alpha: small jitter around current cfg values if not provided
    - payload_bits: small jitter if not provided
    """
    # Seed: use locked seed if provided, otherwise randomize if not in args
    if args.seed is None:
        if locked_seed is not None:
            cfg["seed"] = locked_seed
        else:
            cfg["seed"] = int(time.time_ns() % 2_147_483_647)
    else:
        cfg["seed"] = args.seed

    # Policy
    if args.policy is None:
        cfg["policy"] = random.choice(["RR", "MAF", "AWN"])

    def jitter(val: float, rel: float = 0.2, lo: float | None = None, hi: float | None = None) -> float:
        low = val * (1 - rel)
        high = val * (1 + rel)
        if lo is not None:
            low = max(low, lo)
        if hi is not None:
            high = min(high, hi)
        return random.uniform(low, high)

    # Beta/Gamma/Alpha
    if args.beta is None:
        cfg["beta"] = float(jitter(float(cfg.get("beta", 1.0)), rel=0.3, lo=0.1))
    if args.gamma is None:
        cfg["gamma"] = float(jitter(float(cfg.get("gamma", 1.0)), rel=0.3, lo=0.1))
    if args.alpha is None:
        cfg["alpha"] = float(min(1.0, max(0.0, jitter(float(cfg.get("alpha", 0.5)), rel=0.2, lo=0.0, hi=1.0))))

    # Payload
    if args.payload is None:
        base_payload = int(cfg.get("payload_bits", 1_600_000))
        jittered = int(jitter(float(base_payload), rel=0.1))
        cfg["payload_bits"] = max(1, jittered)

    return cfg


def build_subtitle(cfg: Dict[str, Any]) -> str:
    u = cfg["uav"]
    r = cfg["radio"]
    payload_mb = cfg.get("payload_bits", 1_600_000) / 1_000_000
    return (
        f"Policy={cfg['policy']} | Seed={cfg['seed']} | "
        f"β={cfg['beta']:.2f} | γ={cfg['gamma']:.2f} | α={cfg['alpha']:.2f} | "
        f"N={cfg['N']} | T={cfg['mission_time_s']} | Battery={u['battery_Wh']}Wh | "
        f"Payload={payload_mb:.1f}Mb | R={r['comm_radius_m']}m"
    )


def do_run(args: argparse.Namespace) -> None:
    # Lock seed for this command
    locked_seed = lock_scenario_seed(args)
    
    cfg = load_config(args.config)
    cfg = override_cfg(cfg, args)
    cfg = randomize_unspecified(cfg, args, locked_seed=locked_seed)
    seed = int(cfg.get("seed", 42))
    rng = np.random.default_rng(seed)
    N = int(cfg["N"])
    field_size = tuple(cfg["field_size"])  # type: ignore[assignment]
    uav, radio = build_uav_radio(cfg)
    nodes = init_nodes_random(N, (float(field_size[0]), float(field_size[1])), rng)
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

    # Plots
    run_dir = summary["run_dir"]
    # Save resolved config for traceability
    with open(os.path.join(run_dir, "resolved_config.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    log_csv = summary["log_csv"]
    aoi_png = os.path.join(run_dir, "aoi_time.png")
    energy_png = os.path.join(run_dir, "energy_time.png")
    route_png = os.path.join(run_dir, "route.png")
    subtitle = build_subtitle(cfg)
    plot_aoi_time(log_csv, aoi_png, subtitle=subtitle)
    plot_energy_time(log_csv, energy_png, subtitle=subtitle)
    positions = [(n.x, n.y) for n in nodes]
    plot_route(params.field_size, positions, summary["visited_path"], route_png, subtitle=subtitle)

    m = compute_metrics(log_csv)
    print("Run complete:")
    print(f"  log: {log_csv}")
    print(f"  avg_aoi={m['avg_aoi']:.2f}s, max_aoi={m['max_aoi']:.2f}s, p99={m['p99_aoi']:.2f}s")
    print(f"  energy={m['total_energy_Wh']:.3f} Wh")


def do_sweep_alpha(args: argparse.Namespace) -> None:
    # Lock seed for this command - same environment for all alpha values
    locked_seed = lock_scenario_seed(args)
    
    cfg = load_config(args.config)
    cfg = override_cfg(cfg, args)
    # Don't randomize alpha here - we'll sweep it
    alpha_override = args.alpha
    args.alpha = None  # Temporarily clear to avoid randomization
    cfg = randomize_unspecified(cfg, args, locked_seed=locked_seed)
    if alpha_override is not None:
        args.alpha = alpha_override  # Restore if was set
    
    seed = int(cfg.get("seed", 42))
    rng = np.random.default_rng(seed)
    N = int(cfg["N"])
    field_size = tuple(cfg["field_size"])  # type: ignore[assignment]
    uav_base, radio = build_uav_radio(cfg)
    # Same nodes for all alpha values
    nodes = init_nodes_random(N, (float(field_size[0]), float(field_size[1])), rng)
    
    run_dir = args.out or "runs"
    ensure_dir(run_dir)
    results_csv = os.path.join(run_dir, "pareto_results.csv")
    
    # Default alpha sweep: [0, 0.25, 0.5, 0.75, 1.0] (5 points)
    alphas = np.linspace(0.0, 1.0, num=5).tolist()
    
    with open(results_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["alpha", "avg_aoi", "energy_norm"])
        for alpha_val in alphas:
            # Fresh UAV per run
            uav = UAV(
                x=0.0,
                y=0.0,
                speed_mps=uav_base.speed_mps,
                battery_Wh=uav_base.battery_Wh,
                P_move_W=uav_base.P_move_W,
                P_hover_W=uav_base.P_hover_W,
                P_tx_W=uav_base.P_tx_W,
            )
            params = SimParams(
                field_size=(float(field_size[0]), float(field_size[1])),
                mission_time_s=float(cfg["mission_time_s"]),
                payload_bits=int(cfg["payload_bits"]),
                policy=str(cfg["policy"]),
                beta=float(cfg["beta"]),
                gamma=float(cfg["gamma"]),
                alpha=float(alpha_val),
                greedy_mode=bool(cfg.get("greedy_mode", False)),
                hover_cap_s=None,
            )
            summary = simulate(nodes, uav, radio, params, seed)
            m = compute_metrics(summary["log_csv"])
            energy_norm = m["total_energy_Wh"] / max(summary["E_max_Wh"], 1e-9)
            writer.writerow([alpha_val, m["avg_aoi"], energy_norm])
            print(f"  α={alpha_val:.2f}: avg_aoi={m['avg_aoi']:.2f}s, energy_norm={energy_norm:.3f}")

    # Save resolved config (with representative alpha, e.g., 0.5)
    cfg_save = copy.deepcopy(cfg)
    cfg_save["alpha"] = 0.5  # Representative value
    with open(os.path.join(run_dir, "resolved_config.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg_save, f, sort_keys=False)

    pareto_png = os.path.join(run_dir, "pareto.png")
    subtitle = build_subtitle(cfg_save)
    plot_pareto(results_csv, pareto_png, subtitle=subtitle)
    print(f"Pareto saved: {pareto_png} ({len(alphas)} points)")


def do_compare_policies(args: argparse.Namespace) -> None:
    # Lock seed for this command - same environment for all policies
    locked_seed = lock_scenario_seed(args)
    
    # Check if user wants different seeds per policy (for robustness experiments)
    vary_seed = getattr(args, "vary_seed_per_policy", False)
    
    cfg = load_config(args.config)
    cfg = override_cfg(cfg, args)
    # Don't randomize policy here - we'll test all three
    policy_override = args.policy
    args.policy = None  # Temporarily clear to avoid randomization
    cfg = randomize_unspecified(cfg, args, locked_seed=locked_seed)
    if policy_override is not None:
        args.policy = policy_override  # Restore if was set
    
    seed = int(cfg.get("seed", 42))
    rng = np.random.default_rng(seed)
    N = int(cfg["N"])
    field_size = tuple(cfg["field_size"])  # type: ignore[assignment]
    uav_base, radio = build_uav_radio(cfg)
    # Same nodes for all policies (unless vary_seed is True)
    nodes_base = init_nodes_random(N, (float(field_size[0]), float(field_size[1])), rng)
    
    run_dir = args.out or "runs"
    ensure_dir(run_dir)
    summary_csv = os.path.join(run_dir, "policy_summary.csv")
    
    with open(summary_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["policy", "avg_aoi", "total_energy_Wh"])
        
        for policy in ["RR", "MAF", "AWN"]:
            # Deep copy config per policy to avoid mutations
            cfg_policy = copy.deepcopy(cfg)
            cfg_policy["policy"] = policy
            
            # Use same seed/environment unless vary_seed is True
            if vary_seed:
                policy_seed = int(time.time_ns() % 2_147_483_647)
                rng_policy = np.random.default_rng(policy_seed)
                nodes = init_nodes_random(N, (float(field_size[0]), float(field_size[1])), rng_policy)
            else:
                policy_seed = seed
                nodes = nodes_base  # Reuse same nodes
            
            # Fresh UAV per policy
            uav = UAV(
                x=0.0,
                y=0.0,
                speed_mps=uav_base.speed_mps,
                battery_Wh=uav_base.battery_Wh,
                P_move_W=uav_base.P_move_W,
                P_hover_W=uav_base.P_hover_W,
                P_tx_W=uav_base.P_tx_W,
            )
            
            # CRITICAL: Use greedy_mode=True so policies actually differ!
            # With greedy_mode=False, all policies follow the same route and produce identical results
            params = SimParams(
                field_size=(float(field_size[0]), float(field_size[1])),
                mission_time_s=float(cfg_policy["mission_time_s"]),
                payload_bits=int(cfg_policy["payload_bits"]),
                policy=policy,
                beta=float(cfg_policy["beta"]),
                gamma=float(cfg_policy["gamma"]),
                alpha=float(cfg_policy["alpha"]),
                greedy_mode=True,  # Force greedy mode so policies differ
                hover_cap_s=None,
            )
            
            summary = simulate(nodes, uav, radio, params, policy_seed)
            m = compute_metrics(summary["log_csv"])
            writer.writerow([policy, m["avg_aoi"], m["total_energy_Wh"]])
            print(f"  {policy}: avg_aoi={m['avg_aoi']:.2f}s, energy={m['total_energy_Wh']:.3f}Wh")

    # Save resolved config (with representative policy, e.g., AWN)
    cfg_save = copy.deepcopy(cfg)
    cfg_save["policy"] = "AWN"  # Representative value
    with open(os.path.join(run_dir, "resolved_config.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg_save, f, sort_keys=False)

    bar_png = os.path.join(run_dir, "policy_compare.png")
    subtitle = build_subtitle(cfg_save)
    plot_policy_comparison(summary_csv, bar_png, subtitle=subtitle)
    print(f"Policy comparison saved: {bar_png}")


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="UAV AoI/Energy Simulation")
    p.add_argument("--config", type=str, default="configs/default.yaml")
    p.add_argument("--policy", type=str)
    p.add_argument("--alpha", type=float)
    p.add_argument("--seed", type=int)
    p.add_argument("--N", type=int)
    p.add_argument("--T", type=float)
    p.add_argument("--battery", type=float)
    p.add_argument("--speed", type=float)
    p.add_argument("--payload", type=int)
    p.add_argument("--beta", type=float)
    p.add_argument("--gamma", type=float)
    p.add_argument("--comm-radius", dest="comm_radius", type=float)

    sub = p.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="Run a single simulation and plots")
    sweep = sub.add_parser("sweep-alpha", help="Sweep alpha and plot Pareto")
    sweep.add_argument("--out", type=str, help="Output dir", default="runs")
    comp = sub.add_parser("compare-policies", help="Compare RR/MAF/AWN")
    comp.add_argument("--out", type=str, help="Output dir", default="runs")
    comp.add_argument("--vary-seed-per-policy", action="store_true", 
                      help="Use different seeds for each policy (for robustness experiments)")
    return p


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    if args.cmd == "run":
        do_run(args)
    elif args.cmd == "sweep-alpha":
        do_sweep_alpha(args)
    elif args.cmd == "compare-policies":
        do_compare_policies(args)
    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()


