# Project Structure & File Roles

```
Design_Project/
├─ configs/
│  └─ default.yaml            # Default parameters for runs
├─ docs/
│  ├─ PROJECT_OVERVIEW.md
│  ├─ APPROACH.md
│  ├─ ENV_SETUP.md
│  ├─ PROJECT_STRUCTURE.md
│  └─ POWERSHELL_STEPS.md
├─ experiments/
│  ├─ sweep_alpha.py          # Alpha sweep (Pareto)
│  └─ sweep_nodes.py          # N sweep
├─ runs/                      # Outputs (created at runtime)
│  └─ YYYYMMDD_HHMMSS/       # Single session folder per command
│     ├─ resolved_config.yaml # Exact config used (matches plot footers)
│     ├─ log.csv              # Simulation log (for single runs)
│     ├─ *.png                # Plots with config footers
│     └─ subfolders/          # Individual run logs (for multi-run commands)
├─ tests/
│  ├─ conftest.py             # Adds project root to PYTHONPATH for pytest
│  ├─ test_aoi_updates.py
│  ├─ test_energy_accounting.py
│  ├─ test_two_opt.py
│  └─ test_policy_choice.py
├─ uav_aoi/
│  ├─ __init__.py             # Package init
│  ├─ aoi.py                  # AoI state and updates
│  ├─ config.py               # YAML/JSON loader
│  ├─ env.py                  # Nodes/UAV/radio + energy/channel models
│  ├─ metrics.py              # Metric computations
│  ├─ planner.py              # Policies and routing heuristics
│  ├─ sim.py                  # Main simulation loop
│  └─ viz.py                  # Plotting utils
├─ main.py                    # CLI entrypoint (run, sweep-alpha, compare-policies)
├─ README.md                  # Top-level guide
├─ requirements.txt           # Dependencies
└─ .venv/                     # Virtual environment (local)
```

## Key Components
- `uav_aoi/env.py`: Core physical and energy models; dataclasses for `UAV`, `Node`, `Radio`.
- `uav_aoi/aoi.py`: `AoIState` with increment/reset.
- `uav_aoi/planner.py`: Policies (RR/MAF/AWN) and routing (Nearest-Neighbor, 2-Opt).
- `uav_aoi/sim.py`: Implements the simulation loop, logging, and route/greedy modes.
- `uav_aoi/metrics.py`: Loads logs and computes summary statistics.
- `uav_aoi/viz.py`: Generates plots with config footers.
- `uav_aoi/config.py`: Loads configs from YAML/JSON.
- `main.py`: CLI entrypoint with:
  - Parameter randomization for unspecified values
  - Single session folder management
  - Alpha-aware sweep (dynamic β/γ adjustment)
  - Scenario locking (same seed/environment per command)
  - Config footer generation for plots

## Output Organization
- **Single Session Folders**: Each command (`run`, `compare-policies`, `sweep-alpha`) creates one timestamped folder.
- **Config Traceability**: `resolved_config.yaml` saved in each session folder matches plot footers exactly.
- **Multi-Run Commands**: `compare-policies` and `sweep-alpha` create subfolders for individual run logs while keeping summary files at the session level.


