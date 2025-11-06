# PowerShell Commands Used (Setup & Run)

Below are the exact or equivalent commands you executed:

## Environment Setup
```powershell
cd D:\IIITV\Design_Project
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Single Runs
```powershell
# Basic run (auto-randomizes unspecified params)
python main.py --config configs/default.yaml run

# With explicit parameters
python main.py --config configs/default.yaml --policy AWN --alpha 0.6 --seed 42 run
python main.py --config configs/default.yaml --N 40 --T 900 --battery 45 --speed 15 run
python main.py --config configs/default.yaml --payload 2000000 --beta 1.2 --gamma 0.8 run

# Custom session folder
python main.py --config configs/default.yaml --session-id my_experiment run
```

## Experiments
```powershell
# Sweep alpha (produces Pareto curve with different results per α)
python main.py --config configs/default.yaml sweep-alpha
python main.py --config configs/default.yaml sweep-alpha --alphas 0 0.25 0.5 0.75 1
python main.py --config configs/default.yaml sweep-alpha --session-id pareto_test

# Compare policies (RR, MAF, AWN on same scenario)
python main.py --config configs/default.yaml compare-policies
python main.py --config configs/default.yaml compare-policies --seed 1200
python main.py --config configs/default.yaml compare-policies --vary-seed-per-policy

# Sweep number of nodes (experiment script)
python -m experiments.sweep_nodes --config configs/default.yaml --minN 10 --maxN 50 --step 10 --out runs
```

## Tests
```powershell
pytest -q
```

## Output Structure
Each command creates a single timestamped folder (e.g., `runs/20251106_231052/`) containing:
- `resolved_config.yaml`: Exact config used (matches plot footers)
- All PNG plots with config footers
- CSV logs and summary files
- Subfolders for multi-run commands (e.g., `alpha_0.00/`, `rr/`, `maf/`, `awn/`)


