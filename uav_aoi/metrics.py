from __future__ import annotations

from typing import Dict, Any, List
import csv
import math


def load_log(log_csv: str) -> List[Dict[str, float]]:
    rows: List[Dict[str, float]] = []
    with open(log_csv, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: float(v) for k, v in row.items()})
    return rows


def compute_metrics(log_csv: str) -> Dict[str, float]:
    rows = load_log(log_csv)
    if not rows:
        return {"avg_aoi": 0.0, "max_aoi": 0.0, "p99_aoi": 0.0, "total_energy_Wh": 0.0, "energy_per_update_Wh": math.inf}
    aoi_vals = [r["aoi_avg"] for r in rows]
    max_vals = [r["aoi_max"] for r in rows]
    energies = [r["energy_Wh"] for r in rows]
    avg_aoi = sum(aoi_vals) / len(aoi_vals)
    max_aoi = max(max_vals)
    p99_aoi = sorted(max_vals)[max(0, int(0.99 * (len(max_vals) - 1)))]
    total_energy = energies[-1]
    num_updates = len(rows)
    energy_per_update = total_energy / max(num_updates, 1)
    return {
        "avg_aoi": avg_aoi,
        "max_aoi": max_aoi,
        "p99_aoi": p99_aoi,
        "total_energy_Wh": total_energy,
        "energy_per_update_Wh": energy_per_update,
    }


