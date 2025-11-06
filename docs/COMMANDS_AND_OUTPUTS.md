# Commands & Outputs Reference

This document provides a complete reference for all available commands and their outputs in the UAV AoI–Energy simulator.

## Table of Contents
- [Single Run Command](#single-run-command)
- [Compare Policies Command](#compare-policies-command)
- [Sweep Alpha Command](#sweep-alpha-command)
- [Output File Descriptions](#output-file-descriptions)
- [Output Folder Structure](#output-folder-structure)

---

## Single Run Command

### Command
```powershell
python main.py --config configs/default.yaml run [OPTIONS]
```

### Options
- `--config <file>`: Configuration file (default: `configs/default.yaml`)
- `--policy <RR|MAF|AWN>`: Scheduling policy (default: random if not specified)
- `--seed <int>`: Random seed (default: time-based if not specified)
- `--N <int>`: Number of nodes
- `--T <float>`: Mission time in seconds
- `--battery <float>`: Battery capacity in Wh
- `--speed <float>`: UAV speed in m/s
- `--payload <int>`: Payload size in bits
- `--beta <float>`: AWN policy β parameter
- `--gamma <float>`: AWN policy γ parameter
- `--alpha <float>`: Joint objective α parameter
- `--comm-radius <float>`: Communication radius in meters
- `--out <dir>`: Custom output directory
- `--session-id <name>`: Custom session folder name

### Example
```powershell
python main.py --config configs/default.yaml --policy AWN --alpha 0.6 --seed 42 run
```

### Output Folder
Creates: `runs/YYYYMMDD_HHMMSS/` (or custom if `--session-id` or `--out` specified)

### Output Files

| File | Description |
|------|-------------|
| `resolved_config.yaml` | Complete configuration used for this run (matches plot footers) |
| `log.csv` | Time-series simulation log with columns: `time_s`, `energy_Wh`, `uav_x`, `uav_y`, `served_node`, `aoi_avg`, `aoi_max` |
| `aoi_time.png` | Plot showing average AoI vs time with config footer |
| `energy_time.png` | Plot showing energy consumption vs time with config footer |
| `route.png` | 2D visualization of UAV path and node locations with config footer |

### Console Output
```
Run complete: runs/20251106_231052
  log: runs/20251106_231052/log.csv
  avg_aoi=182.73s, max_aoi=424.20s, p99=418.34s
  energy=59.463 Wh
```

---

## Compare Policies Command

### Command
```powershell
python main.py --config configs/default.yaml compare-policies [OPTIONS]
```

### Options
All options from `run` command, plus:
- `--vary-seed-per-policy`: Use different seeds for each policy (for robustness experiments)

### Example
```powershell
python main.py --config configs/default.yaml compare-policies --seed 1200
```

### Output Folder
Creates: `runs/YYYYMMDD_HHMMSS/` (or custom if `--session-id` or `--out` specified)

### Output Files

| File/Folder | Description |
|-------------|-------------|
| `resolved_config.yaml` | Configuration with representative policy (AWN) - matches plot footer |
| `policy_summary.csv` | Summary table with columns: `policy`, `avg_aoi`, `total_energy_Wh` |
| `policy_compare.png` | Bar chart comparing RR, MAF, and AWN policies (AoI and Energy) with config footer |
| `rr/` | Subfolder containing individual run for Round Robin policy |
| `rr/log.csv` | Time-series log for RR policy run |
| `maf/` | Subfolder containing individual run for Max-Age-First policy |
| `maf/log.csv` | Time-series log for MAF policy run |
| `awn/` | Subfolder containing individual run for Age-Weighted-Nearest policy |
| `awn/log.csv` | Time-series log for AWN policy run |

### Console Output
```
  RR: avg_aoi=195.23s, energy=58.234Wh
  MAF: avg_aoi=178.45s, energy=61.123Wh
  AWN: avg_aoi=182.73s, energy=59.463Wh
Policy comparison saved: runs/20251106_231052/policy_compare.png
Session folder: runs/20251106_231052
```

### Notes
- All three policies run on the **same scenario** (same seed, same nodes) for fair comparison
- Uses `greedy_mode=True` so policies actually produce different results
- If `--vary-seed-per-policy` is used, each policy gets a different seed/environment

---

## Sweep Alpha Command

### Command
```powershell
python main.py --config configs/default.yaml sweep-alpha [OPTIONS]
```

### Options
All options from `run` command, plus:
- `--alphas <float> ...`: Custom alpha values to sweep (default: 0, 0.25, 0.5, 0.75, 1.0)

### Example
```powershell
python main.py --config configs/default.yaml sweep-alpha --alphas 0 0.25 0.5 0.75 1
```

### Output Folder
Creates: `runs/YYYYMMDD_HHMMSS/` (or custom if `--session-id` or `--out` specified)

### Output Files

| File/Folder | Description |
|-------------|-------------|
| `resolved_config.yaml` | Configuration with representative α=0.5 and corresponding β, γ - matches plot footer |
| `pareto_results.csv` | Pareto curve data with columns: `alpha`, `avg_aoi`, `energy_norm`, `beta`, `gamma` |
| `pareto.png` | Scatter plot showing AoI–Energy trade-off curve colored by α value, with config footer |
| `alpha_0.00/` | Subfolder for α=0.0 run (energy-focused) |
| `alpha_0.00/log.csv` | Time-series log for α=0.0 run |
| `alpha_0.25/` | Subfolder for α=0.25 run |
| `alpha_0.25/log.csv` | Time-series log for α=0.25 run |
| `alpha_0.50/` | Subfolder for α=0.5 run (balanced) |
| `alpha_0.50/log.csv` | Time-series log for α=0.5 run |
| `alpha_0.75/` | Subfolder for α=0.75 run |
| `alpha_0.75/log.csv` | Time-series log for α=0.75 run |
| `alpha_1.00/` | Subfolder for α=1.0 run (AoI-focused) |
| `alpha_1.00/log.csv` | Time-series log for α=1.0 run |

### Console Output
```
  α=0.00 (β=0.80, γ=1.60): avg_aoi=195.23s, energy_norm=0.987
  α=0.25 (β=1.00, γ=1.35): avg_aoi=188.45s, energy_norm=0.992
  α=0.50 (β=1.20, γ=1.10): avg_aoi=182.73s, energy_norm=0.991
  α=0.75 (β=1.40, γ=0.85): avg_aoi=175.12s, energy_norm=0.998
  α=1.00 (β=1.60, γ=0.60): avg_aoi=168.34s, energy_norm=1.000
Pareto saved: runs/20251106_231052/pareto.png (5 points)
Session folder: runs/20251106_231052
```

### Notes
- All α values run on the **same scenario** (same seed, same nodes) for fair comparison
- **Alpha-aware**: β and γ are dynamically adjusted based on α:
  - β = 0.8 + α × 0.8 (range: 0.8 to 1.6)
  - γ = 1.6 - α × 1.0 (range: 1.6 to 0.6)
- High α → high β, low γ (prioritize freshness)
- Low α → low β, high γ (prioritize energy efficiency)
- Policy is automatically set to AWN for the sweep

---

## Output File Descriptions

### resolved_config.yaml
Complete YAML configuration file containing all parameters used for the run(s). This file:
- Matches the config footer shown on all plots
- Includes resolved values after randomization (if any)
- Can be used to reproduce exact runs
- For multi-run commands, contains representative values

**Example structure:**
```yaml
field_size: [1000, 1000]
N: 30
mission_time_s: 1200
uav:
  speed_mps: 12
  battery_Wh: 60
  P_move_W: 180
  P_hover_W: 140
  P_tx_W: 2
radio:
  bandwidth_Hz: 1000000
  noise_W: 1.0e-9
  pathloss_exponent: 2.7
  snr_threshold_linear: 3.0
  comm_radius_m: 220
payload_bits: 1600000
policy: "AWN"
beta: 1.20
gamma: 1.10
alpha: 0.5
seed: 42
```

### log.csv
Time-series simulation log with the following columns:
- `time_s`: Simulation time in seconds
- `energy_Wh`: Cumulative energy consumption in Watt-hours
- `uav_x`: UAV X coordinate in meters
- `uav_y`: UAV Y coordinate in meters
- `served_node`: Node ID that was just served
- `aoi_avg`: Average AoI across all nodes at this time
- `aoi_max`: Maximum AoI across all nodes at this time

**Use cases:**
- Analyze temporal behavior
- Debug simulation issues
- Extract custom metrics
- Replay simulation steps

### policy_summary.csv
Summary table comparing policies (from `compare-policies` command):
- `policy`: Policy name (RR, MAF, or AWN)
- `avg_aoi`: Average AoI in seconds
- `total_energy_Wh`: Total energy consumed in Watt-hours

### pareto_results.csv
Pareto curve data (from `sweep-alpha` command):
- `alpha`: Alpha value used
- `avg_aoi`: Average AoI in seconds
- `energy_norm`: Normalized energy (Energy / E_max)
- `beta`: β parameter used (dynamically adjusted)
- `gamma`: γ parameter used (dynamically adjusted)

### PNG Plot Files

All PNG files include a config footer at the bottom showing:
```
Policy=AWN | Seed=42 | β=1.20 | γ=1.10 | α=0.50 | N=30 | T=1200 | Battery=60Wh | Payload=1.6Mb | R=220m
```

#### aoi_time.png
- **X-axis**: Time (seconds)
- **Y-axis**: Average AoI (seconds)
- **Content**: Line plot showing how average AoI evolves over time
- **Use**: Monitor freshness trends, identify periods of high AoI

#### energy_time.png
- **X-axis**: Time (seconds)
- **Y-axis**: Energy consumption (Watt-hours)
- **Content**: Line plot showing cumulative energy consumption
- **Use**: Track energy usage patterns, identify energy-intensive periods

#### route.png
- **X-axis**: X coordinate (meters)
- **Y-axis**: Y coordinate (meters)
- **Content**: 2D scatter plot showing:
  - Blue dots: Ground IoT nodes
  - Orange line: UAV path
- **Use**: Visualize spatial coverage, analyze route efficiency

#### policy_compare.png
- **Content**: Two side-by-side bar charts:
  - Left: Average AoI by policy
  - Right: Total Energy by policy
- **Use**: Quick comparison of policy performance

#### pareto.png
- **X-axis**: Average AoI (seconds)
- **Y-axis**: Normalized Energy (Energy / E_max)
- **Content**: Scatter plot with:
  - Points colored by α value (viridis colormap)
  - Colorbar showing α scale
- **Use**: Identify optimal trade-off points between AoI and energy

---

## Output Folder Structure

### Single Run (`run` command)
```
runs/20251106_231052/
├── resolved_config.yaml
├── log.csv
├── aoi_time.png
├── energy_time.png
└── route.png
```

### Compare Policies (`compare-policies` command)
```
runs/20251106_231052/
├── resolved_config.yaml
├── policy_summary.csv
├── policy_compare.png
├── rr/
│   └── log.csv
├── maf/
│   └── log.csv
└── awn/
    └── log.csv
```

### Sweep Alpha (`sweep-alpha` command)
```
runs/20251106_231052/
├── resolved_config.yaml
├── pareto_results.csv
├── pareto.png
├── alpha_0.00/
│   └── log.csv
├── alpha_0.25/
│   └── log.csv
├── alpha_0.50/
│   └── log.csv
├── alpha_0.75/
│   └── log.csv
└── alpha_1.00/
    └── log.csv
```

---

## Quick Reference

### Command Summary

| Command | Purpose | Key Outputs |
|---------|---------|-------------|
| `run` | Single simulation run | `log.csv`, `aoi_time.png`, `energy_time.png`, `route.png` |
| `compare-policies` | Compare RR/MAF/AWN | `policy_summary.csv`, `policy_compare.png`, subfolders per policy |
| `sweep-alpha` | Generate Pareto curve | `pareto_results.csv`, `pareto.png`, subfolders per α |

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--config <file>` | Config file path | `--config configs/default.yaml` |
| `--seed <int>` | Random seed | `--seed 42` |
| `--session-id <name>` | Custom folder name | `--session-id my_experiment` |
| `--out <dir>` | Custom output directory | `--out results/` |
| `--alphas <...>` | Custom alpha values | `--alphas 0 0.5 1` |

---

## Tips

1. **Reproducibility**: Use `--seed` to reproduce exact runs
2. **Organization**: Use `--session-id` for meaningful folder names
3. **Customization**: Override any parameter via CLI flags
4. **Traceability**: Always check `resolved_config.yaml` to see exact parameters used
5. **Comparison**: Use same `--seed` across commands for fair comparison
6. **Pareto Analysis**: `sweep-alpha` produces different results per α due to dynamic β/γ adjustment

---

## See Also

- [Environment Setup](ENV_SETUP.md) - Initial setup instructions
- [PowerShell Steps](POWERSHELL_STEPS.md) - Command examples
- [Project Overview](PROJECT_OVERVIEW.md) - Project goals and features
- [Approach](APPROACH.md) - Design decisions and modeling choices

