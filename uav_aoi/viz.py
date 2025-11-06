from __future__ import annotations

from typing import List, Tuple
import os
import csv

import matplotlib.pyplot as plt


def _load_series(log_csv: str):
    times = []
    avg_aoi = []
    energies = []
    xs = []
    ys = []
    with open(log_csv, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row["time_s"]))
            avg_aoi.append(float(row["aoi_avg"]))
            energies.append(float(row["energy_Wh"]))
            xs.append(float(row["uav_x"]))
            ys.append(float(row["uav_y"]))
    return times, avg_aoi, energies, xs, ys


def plot_aoi_time(log_csv: str, out_path: str, subtitle: str | None = None) -> None:
    t, avg_aoi, _, _, _ = _load_series(log_csv)
    plt.figure(figsize=(7, 4))
    plt.plot(t, avg_aoi, label="Average AoI")
    plt.xlabel("Time (s)")
    plt.ylabel("Average AoI (s)")
    plt.title("Average AoI vs Time")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Leave space at bottom for subtitle
    if subtitle:
        plt.figtext(0.5, 0.02, subtitle, ha="center", fontsize=7)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def plot_energy_time(log_csv: str, out_path: str, subtitle: str | None = None) -> None:
    t, _, energy, _, _ = _load_series(log_csv)
    plt.figure(figsize=(7, 4))
    plt.plot(t, energy, label="Energy (Wh)")
    plt.xlabel("Time (s)")
    plt.ylabel("Energy (Wh)")
    plt.title("Energy vs Time")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Leave space at bottom for subtitle
    if subtitle:
        plt.figtext(0.5, 0.02, subtitle, ha="center", fontsize=7)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def plot_route(field_size: Tuple[float, float], node_positions: List[Tuple[float, float]], path: List[Tuple[float, float]], out_path: str, subtitle: str | None = None) -> None:
    plt.figure(figsize=(6, 6))
    xs = [p[0] for p in path]
    ys = [p[1] for p in path]
    nx = [p[0] for p in node_positions]
    ny = [p[1] for p in node_positions]
    plt.scatter(nx, ny, c="tab:blue", label="Nodes")
    plt.plot(xs, ys, c="tab:orange", label="UAV Path")
    plt.xlim(0, field_size[0])
    plt.ylim(0, field_size[1])
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title("Route Path")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Leave space at bottom for subtitle
    if subtitle:
        plt.figtext(0.5, 0.02, subtitle, ha="center", fontsize=7)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def plot_policy_comparison(summary_csv: str, out_path: str, subtitle: str | None = None) -> None:
    import csv
    policies = []
    avg_aoi = []
    energy = []
    with open(summary_csv, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            policies.append(row["policy"])
            avg_aoi.append(float(row["avg_aoi"]))
            energy.append(float(row["total_energy_Wh"]))
    x = range(len(policies))
    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1)
    plt.bar(x, avg_aoi, color="tab:green")
    plt.xticks(x, policies)
    plt.ylabel("Avg AoI (s)")
    plt.title("AoI by Policy")
    plt.subplot(1, 2, 2)
    plt.bar(x, energy, color="tab:red")
    plt.xticks(x, policies)
    plt.ylabel("Energy (Wh)")
    plt.title("Energy by Policy")
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Leave space at bottom for subtitle
    if subtitle:
        plt.figtext(0.5, 0.02, subtitle, ha="center", fontsize=7)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


def plot_pareto(results_csv: str, out_path: str, subtitle: str | None = None) -> None:
    import csv
    alphas = []
    avg_aoi = []
    energy_norm = []
    with open(results_csv, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            alphas.append(float(row["alpha"]))
            avg_aoi.append(float(row["avg_aoi"]))
            energy_norm.append(float(row["energy_norm"]))
    plt.figure(figsize=(6, 5))
    plt.scatter(avg_aoi, energy_norm, c=alphas, cmap="viridis")
    plt.xlabel("Avg AoI (s)")
    plt.ylabel("Energy / E_max")
    plt.title("AoI–Energy Pareto (by alpha)")
    cbar = plt.colorbar()
    cbar.set_label("alpha")
    plt.grid(True, alpha=0.3)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Leave space at bottom for subtitle
    if subtitle:
        plt.figtext(0.5, 0.02, subtitle, ha="center", fontsize=7)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()


