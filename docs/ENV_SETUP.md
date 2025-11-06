# Environment Setup & Configuration

This guide explains how to set up the environment and configure runs on Windows PowerShell.

## Prerequisites
- Python 3.10+ installed and available as `python`

## Create and Activate Virtual Environment
```powershell
cd D:\IIITV\Design_Project
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

## Install Dependencies
```powershell
pip install -r requirements.txt
```

## Default Configuration
- File: `configs/default.yaml`
- Includes field size, N, mission time, UAV power/speed/battery, radio params, payload, policy, β, γ, α, seed.

## Parameter Behavior
- **Explicit Parameters**: If you pass `--seed`, `--policy`, `--beta`, etc., those values are used.
- **Automatic Randomization**: Unspecified parameters are randomly selected:
  - `seed`: Time-based unique seed (if not provided)
  - `policy`: Random choice from RR/MAF/AWN (if not provided)
  - `beta`, `gamma`, `alpha`: Small jitter around config defaults (if not provided)
  - `payload_bits`: Small jitter around config default (if not provided)

## Override Configuration via CLI
Examples:
```powershell
# Single run with explicit parameters
python main.py --config configs/default.yaml --policy AWN --alpha 0.6 --seed 42 run

# Single run with automatic randomization (unique each time)
python main.py --config configs/default.yaml run

# Override specific parameters
python main.py --config configs/default.yaml --N 40 --T 900 --battery 45 --speed 15 run
python main.py --config configs/default.yaml --payload 2000000 --beta 1.2 --gamma 0.8 --comm-radius 250 run

# Custom session folder
python main.py --config configs/default.yaml --session-id my_experiment run

# Sweep alpha with custom values
python main.py --config configs/default.yaml sweep-alpha --alphas 0 0.25 0.5 0.75 1
```

## Outputs
- **Single Session Folder**: Each command creates one timestamped folder under `runs/` (e.g., `runs/20251106_231052/`)
- **Contents**:
  - `resolved_config.yaml`: Exact configuration used (matches plot footers)
  - `log.csv`: Simulation log (for single runs)
  - `aoi_time.png`, `energy_time.png`, `route.png`: Plots with config footers
  - For `compare-policies`: `policy_summary.csv`, `policy_compare.png`, plus subfolders `rr/`, `maf/`, `awn/`
  - For `sweep-alpha`: `pareto_results.csv`, `pareto.png`, plus subfolders `alpha_0.00/`, `alpha_0.25/`, etc.


