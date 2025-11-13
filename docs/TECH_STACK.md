# Technology Stack

This document describes the technology stack, dependencies, and tools used in the UAV-assisted Energy and AoI-aware Communications simulator.

## Table of Contents
1. [Programming Language](#programming-language)
2. [Core Dependencies](#core-dependencies)
3. [Standard Library Modules](#standard-library-modules)
4. [Development Tools](#development-tools)
5. [Project Structure](#project-structure)
6. [Configuration Management](#configuration-management)
7. [Data Formats](#data-formats)

---

## Programming Language

### Python
- **Version:** Python 3.10 or higher
- **Rationale:** 
  - Type hints support (`from __future__ import annotations`)
  - Modern dataclasses and typing features
  - Excellent scientific computing ecosystem
  - Cross-platform compatibility

### Python Features Used
- **Type Hints:** Full type annotations for better code clarity and IDE support
- **Dataclasses:** For structured data (Node, UAV, Radio, AoIState, SimParams)
- **Type Annotations:** `List`, `Dict`, `Tuple`, `Optional`, `Callable`, `Sequence`
- **Future Annotations:** `from __future__ import annotations` for forward references

---

## Core Dependencies

### NumPy (`numpy>=1.23`)
**Purpose:** Numerical computing and random number generation

**Usage:**
- Random number generation: `np.random.default_rng(seed)` for deterministic simulations
- Array operations and mathematical computations
- Linear algebra operations (implicitly through distance calculations)

**Key Functions:**
- `np.random.default_rng()` - Deterministic random number generator
- `np.linspace()` - Generate evenly spaced alpha values for sweeps
- `np.mean()`, `np.max()` - Statistical operations

### Matplotlib (`matplotlib>=3.7`)
**Purpose:** Data visualization and plotting

**Usage:**
- Generate time-series plots (AoI vs time, Energy vs time)
- Route visualization (2D path plots)
- Pareto curve plots (AoI-Energy trade-off)
- Policy comparison bar charts

**Key Modules:**
- `matplotlib.pyplot` - Main plotting interface
- `matplotlib.figure` - Figure management
- Custom styling and configuration for publication-quality plots

### PyYAML (`PyYAML>=6.0`)
**Purpose:** Configuration file parsing

**Usage:**
- Load simulation parameters from YAML configuration files
- Save resolved configurations for reproducibility
- Human-readable parameter management

**Key Functions:**
- `yaml.safe_load()` - Parse YAML files safely
- `yaml.safe_dump()` - Write YAML files

### Pandas (`pandas>=2.0`)
**Purpose:** Data manipulation and CSV handling

**Usage:**
- Read and process simulation log CSV files
- Data aggregation for metrics computation
- Efficient time-series data handling

**Key Functions:**
- `pd.read_csv()` - Load log files
- Data filtering and aggregation operations

### Pytest (`pytest>=7.0`)
**Purpose:** Unit testing framework

**Usage:**
- Unit tests for AoI updates
- Energy accounting validation
- Policy selection verification
- Routing algorithm testing (2-Opt)

**Test Structure:**
- `tests/test_aoi_updates.py` - AoI state management tests
- `tests/test_energy_accounting.py` - Energy calculation tests
- `tests/test_policy_choice.py` - Policy selection tests
- `tests/test_two_opt.py` - Routing optimization tests

---

## Standard Library Modules

### Core Modules

#### `argparse`
**Purpose:** Command-line interface and argument parsing

**Usage:**
- Define CLI commands (`run`, `sweep-alpha`, `compare-policies`)
- Parse configuration overrides (`--policy`, `--alpha`, `--seed`, etc.)
- Subcommand handling for different simulation modes

#### `csv`
**Purpose:** CSV file reading and writing

**Usage:**
- Write simulation logs (`log.csv`)
- Export results (`pareto_results.csv`, `policy_summary.csv`)
- Time-series data logging

#### `os`
**Purpose:** File system operations

**Usage:**
- Directory creation and management
- Path manipulation
- File existence checks

#### `time`
**Purpose:** Time-based operations

**Usage:**
- Generate timestamps for session folders
- Seed generation for randomization
- Time-based unique identifiers

#### `random`
**Purpose:** Random parameter generation

**Usage:**
- Random policy selection (when not specified)
- Parameter jittering for unspecified values
- Randomization utilities

#### `copy`
**Purpose:** Deep copying of configuration objects

**Usage:**
- Create independent copies of configuration dictionaries
- Prevent mutation of shared state during sweeps

#### `dataclasses`
**Purpose:** Structured data classes

**Usage:**
- Define immutable data structures (Node, UAV, Radio, AoIState, SimParams)
- Automatic `__init__`, `__repr__`, and equality methods

#### `typing`
**Purpose:** Type annotations

**Usage:**
- Type hints for function parameters and return values
- Generic types (`List`, `Dict`, `Tuple`, `Optional`, `Callable`)
- Type safety and IDE support

#### `math`
**Purpose:** Mathematical operations

**Usage:**
- `math.hypot()` - Euclidean distance calculation
- `math.log2()` - Logarithm for Shannon capacity
- `math.inf` - Infinity for initial best score values

#### `datetime`
**Purpose:** Timestamp generation

**Usage:**
- Create timestamped session folders
- Format dates for directory names (`YYYYMMDD_HHMMSS`)

---

## Development Tools

### Virtual Environment
**Purpose:** Dependency isolation

**Setup:**
```bash
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

### Package Management
**File:** `requirements.txt`

**Installation:**
```bash
pip install -r requirements.txt
```

### Testing Framework
**Tool:** pytest

**Usage:**
```bash
pytest -q
```

**Features:**
- Automatic test discovery
- Fixtures for test data (`conftest.py`)
- Assertion introspection

---

## Project Structure

### Directory Layout
```
Design_Project/
├── configs/              # Configuration files
│   └── default.yaml      # Default simulation parameters
├── docs/                 # Documentation
│   ├── FORMULAS.md       # Mathematical formulas
│   ├── TECH_STACK.md     # This file
│   ├── APPROACH.md       # Design decisions
│   └── ...
├── experiments/          # Experimental scripts
│   ├── sweep_alpha.py    # Alpha sweep experiments
│   └── sweep_nodes.py    # Node count sweep
├── runs/                 # Simulation output directory
│   └── YYYYMMDD_HHMMSS/  # Timestamped session folders
├── tests/                # Unit tests
│   ├── conftest.py       # Test fixtures
│   └── test_*.py         # Test modules
├── uav_aoi/              # Main package
│   ├── __init__.py
│   ├── aoi.py            # AoI state management
│   ├── config.py          # Configuration loading
│   ├── env.py             # Environment models (UAV, Node, Radio)
│   ├── metrics.py         # Metrics computation
│   ├── planner.py         # Policy implementations
│   ├── sim.py             # Simulation engine
│   └── viz.py             # Visualization functions
├── main.py                # CLI entry point
├── requirements.txt       # Python dependencies
└── README.md              # Project overview
```

### Module Organization

#### `uav_aoi/aoi.py`
- AoI state management
- AoI evolution logic

#### `uav_aoi/env.py`
- Physical models (Node, UAV, Radio)
- Distance calculations
- Energy functions (Zeng2016 propulsion model)
  - `propulsion_power(v, uav_cfg)` - Propulsion power at speed v
  - `energy_fly_Wh()` - Flight energy using P(v)
  - `energy_hover_Wh()` - Hover energy (P0 + Pi)
  - `energy_tx_Wh()` - Transmission energy (circuit + PA)
- Radio channel models

#### `uav_aoi/planner.py`
- Policy implementations (RR, MAF, AWN)
- Routing heuristics (Nearest Neighbor, 2-Opt)

#### `uav_aoi/sim.py`
- Main simulation loop
- Node initialization
- Simulation orchestration
- Energy breakdown tracking (E_fly_total, E_hover_total, E_tx_total)
- CSV logging with energy model annotations

#### `uav_aoi/metrics.py`
- Metrics computation from logs
- Statistical aggregations

#### `uav_aoi/viz.py`
- Plotting functions
- Visualization utilities

#### `uav_aoi/config.py`
- Configuration file loading
- Parameter parsing

---

## Configuration Management

### YAML Configuration Files
**Format:** YAML (YAML Ain't Markup Language)

**Structure:**
```yaml
field_size: [1000, 1000]
N: 30
mission_time_s: 1200
uav:
  # Zeng2016 propulsion model parameters
  mass_kg: 1.5
  g: 9.81
  rotor_radius_m: 0.15
  disc_area_m2: 0.0707
  blade_tip_speed: 140.0
  rotor_solidity: 0.05
  P0: 10.0
  Pi: null  # Computed if null
  d0: 0.3
  air_density: 1.225
  speed_mps: 12
  battery_Wh: 60
radio:
  bandwidth_Hz: 1000000
  noise_W: 1.0e-9
  pathloss_exponent: 2.7
  snr_threshold_linear: 3.0
  comm_radius_m: 220
tx:
  P_circuit_W: 1.0
  amp_efficiency: 0.4
  P_out_W: 1.0
payload_bits: 1600000
policy: "AWN"
beta: 1.0
gamma: 1.0
alpha: 0.5
seed: 42
```

**Features:**
- Hierarchical parameter organization
- Human-readable format
- Type preservation (numbers, strings, lists)

### Configuration Resolution
1. Load base configuration from YAML file
2. Apply CLI argument overrides
3. Randomize unspecified parameters (if needed)
4. Save resolved configuration to `resolved_config.yaml`

---

## Data Formats

### CSV Logs
**File:** `log.csv`

**Columns:**
- `time_s` - Simulation time (seconds)
- `energy_Wh` - Cumulative total energy (Watt-hours)
- `E_fly_total` - Cumulative flight energy (Wh)
- `E_hover_total` - Cumulative hover energy (Wh)
- `E_tx_total` - Cumulative transmission energy (Wh)
- `uav_x`, `uav_y` - UAV position (meters)
- `served_node` - Currently served node index
- `aoi_avg` - Average AoI across all nodes (seconds)
- `aoi_max` - Maximum AoI across all nodes (seconds)

**Energy Model:** Zeng et al. (2016) propulsion model with energy breakdown tracking.

### Results CSV
**Files:** `pareto_results.csv`, `policy_summary.csv`

**Format:**
- Comma-separated values
- Header row with column names
- Numerical data

### YAML Output
**File:** `resolved_config.yaml`

**Purpose:** Reproducibility and traceability

**Content:** Complete configuration used for the simulation run

---

## Platform Support

### Operating Systems
- **Windows:** Full support (PowerShell scripts)
- **macOS:** Full support
- **Linux:** Full support

### Python Versions
- **Minimum:** Python 3.10
- **Recommended:** Python 3.11 or higher

### Virtual Environment
- Standard `venv` module (Python 3.10+)
- Compatible with `virtualenv` and `conda`

---

## Performance Considerations

### Determinism
- Uses `numpy.random.default_rng(seed)` for reproducible results
- Same seed produces identical simulation outcomes

### Efficiency
- Simple models for fast execution
- Minimal dependencies to reduce overhead
- Efficient data structures (lists, dictionaries)

### Scalability
- Handles 10-100 nodes efficiently
- Mission times up to several hours (simulated)
- Memory-efficient (no large matrix operations)

---

## Future Extensibility

### Adding New Policies
1. Implement policy function in `uav_aoi/planner.py`
2. Add to `make_policy()` dispatcher
3. Update CLI help text

### Adding New Metrics
1. Implement metric computation in `uav_aoi/metrics.py`
2. Add to `compute_metrics()` return dictionary
3. Update visualization if needed

### Adding New Visualizations
1. Implement plotting function in `uav_aoi/viz.py`
2. Add CLI command or option
3. Integrate with session folder structure

---

## License and Attribution

- **License:** MIT
- **Dependencies:** All dependencies are open-source with permissive licenses
- **Standards:** Follows Python PEP 8 style guidelines (where applicable)

