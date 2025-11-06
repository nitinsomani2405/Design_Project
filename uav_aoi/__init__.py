"""UAV-assisted Energy and AoI-aware Communications simulation package.

Modules:
- env: Environment models (nodes, UAV, channel, energy).
- aoi: Age of Information state and updates.
- planner: Scheduling policies and routing heuristics.
- sim: Main simulation loop.
- metrics: Metrics computation utilities.
- viz: Plotting utilities.
- config: Configuration loader.

This package targets Python 3.10+ and aims for deterministic simulations via
numpy.random.Generator seeded with a provided seed.
"""

__all__ = [
    "env",
    "aoi",
    "planner",
    "sim",
    "metrics",
    "viz",
    "config",
]


