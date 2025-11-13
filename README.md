# UAV-assisted Energy and AoI-aware Communications (Simulation)

A lightweight Python 3.10+ simulator for a single UAV serving N ground IoT nodes on a 2D plane, optimizing freshness (Age of Information, AoI) and tracking energy (flight, hover, and comm). Includes multiple scheduling policies, simple route optimization, metrics, and clear plots.

## Features
- Policies: RR (round-robin), MAF (max-age-first), AWN (age-weighted-nearest: AoI^beta / dist^gamma)
- Routing: Nearest-Neighbor + 2-Opt; or greedy next-by-policy mode
- Models: Shannon-like rate; simple path-loss; energy tracking for fly/hover/tx
- CLI with subcommands: single run, alpha sweep (Pareto), policy comparison
- Deterministic via numpy RNG seed

## Install
1. Create and activate a virtual environment
```bash
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
# macOS/Linux
source .venv/bin/activate
```
2. Install dependencies
```bash
pip install -r requirements.txt
```

## Quick Demo
Run a single simulation with default config and generate plots into `runs/<timestamp>/`:
```bash
python main.py --config configs/default.yaml run
```
Override parameters inline (examples):
```bash
python main.py --config configs/default.yaml --policy AWN --alpha 0.6 --seed 42 run
python main.py --config configs/default.yaml --N 40 --T 900 --battery 45 --speed 15 run
```

## Subcommands
- `run`: single run + plots (AoI vs time, Energy vs time, Route path)
- `sweep-alpha`: generate AoI–Energy Pareto over alpha∈[0,1]
- `compare-policies`: bar chart comparing RR/MAF/AWN

Example:
```bash
python main.py --config configs/default.yaml sweep-alpha --out runs
python main.py --config configs/default.yaml compare-policies --out runs
```

## Config
See `configs/default.yaml` for defaults:
- field_size, N, mission_time_s
- uav: Zeng propulsion parameters (mass_kg, rotor_radius_m, P0, Pi, d0, blade_tip_speed, etc.), speed_mps, battery_Wh
- radio: bandwidth_Hz, noise_W, pathloss_exponent, snr_threshold_linear, comm_radius_m
- tx: P_circuit_W, amp_efficiency, P_out_W
- payload_bits, policy, beta, gamma, alpha, seed

See `docs/FORMULAS.md` for detailed energy model equations.

## Models
- AoI: increments by Δt each step; on successful service: AoI_i ← 0
- Flight: constant speed v, time=d/v
- Energy: **Zeng et al. (2016) propulsion model** for realistic UAV energy consumption
  - Flight: P(v) = P₀(1+3v²/U_tip²) + P_i·√(√(1+v⁴/(4v₀⁴))-v²/(2v₀²)) + ½d₀ρsAv³
  - Hover: P_hover = P₀ + P_i
  - Transmission: P_tx = P_circuit + P_out/η_amp
- Rate: R=B*log2(1+SNR); SNR from path-loss; t_tx=payload_bits/R
- Success: within comm radius OR SNR>threshold (implemented as either condition)

## Output
- CSV log per run: `log.csv` with time, energy, UAV pos, served node, AoI stats
- Plots saved as PNGs: AoI vs time, Energy vs time, Route path
- Additional: Pareto plot and policy comparison bar chart when requested

## Tests
Run unit tests:
```bash
pytest -q
```

## Notes
- Determinism: Node placement uses `numpy.random.default_rng(seed)`
- Performance: simple models and small deps to keep runs fast
- Extensibility: add new policies in `uav_aoi/planner.py` and metrics in `uav_aoi/metrics.py`

## License
MIT


