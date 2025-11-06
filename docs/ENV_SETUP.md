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

## Override Configuration via CLI
Examples:
```powershell
python main.py --config configs/default.yaml --policy AWN --alpha 0.6 --seed 42 run
python main.py --config configs/default.yaml --N 40 --T 900 --battery 45 --speed 15 run
python main.py --config configs/default.yaml --payload 2000000 --beta 1.2 --gamma 0.8 --comm-radius 250 run
```

## Outputs
- Per-run folder under `runs/` with `log.csv` and PNG plots.


