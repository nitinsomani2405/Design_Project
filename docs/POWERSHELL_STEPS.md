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
python main.py --config configs/default.yaml run
python main.py --config configs/default.yaml --policy AWN --alpha 0.6 --seed 42 run
python main.py --config configs/default.yaml --N 40 --T 900 --battery 45 --speed 15 run
python main.py --config configs/default.yaml --payload 2000000 --beta 1.2 --gamma 0.8 run
```

## Experiments
```powershell
python main.py --config configs/default.yaml sweep-alpha --out runs
python main.py --config configs/default.yaml compare-policies --out runs
# Option A (module mode recommended)
python -m experiments.sweep_nodes --config configs/default.yaml --minN 10 --maxN 50 --step 10 --out runs
# Option B (script path; ensure PYTHONPATH includes project root)
python experiments\sweep_nodes.py --config configs\default.yaml --minN 10 --maxN 50 --step 10 --out runs
```

## Tests
```powershell
pytest -q
```

Outputs (CSV and PNG) are saved to `runs\...`.


