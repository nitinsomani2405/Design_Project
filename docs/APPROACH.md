# Project Approach & Design Decisions

This document explains how we built the simulator, the modeling choices, and key design trade-offs.

## Guiding Principles
- Keep models simple, readable, and fast to run.
- Deterministic experiments via `numpy.random.default_rng(seed)`.
- Small, composable functions with type hints and docstrings.

## Modeling Choices
- AoI: Discrete-time accumulation by advancing wall-clock time at each step; reset to 0 upon service.
- Motion & Energy: Constant-speed flight; energy computed directly from power and time for fly/hover/tx.
- Radio:
  - SNR uses path-loss only (no fading) for clarity.
  - Rate via Shannon-like `R = B log2(1+SNR)`.
  - Success if within communication radius OR SNR > threshold.

## Planning Policies
- RR: Baseline fairness.
- MAF: Focus on worst (stale) node first.
- AWN: Balance urgency (AoI) and proximity (distance) with tunable β, γ.

## Routing Heuristics
- Nearest Neighbor to initialize a tour; then refine with 2-Opt.
- Greedy mode: ignore a fixed tour and pick next node by the chosen policy at each step.

## Simulation Loop
- At each iteration:
  1) Choose next node (by policy or route sequence)
  2) Fly to node: advance time, add flight energy, increment AoI
  3) Communicate: compute rate, hover for `t_tx` (or capped), add hover/tx energy
  4) If success, reset that node’s AoI to 0
  5) Log snapshot
- Stop when mission time is reached or battery is depleted.

## Metrics & Reporting
- CSV logs per run for reproducibility.
- Aggregate metrics: average AoI, max, p99, total energy, energy/update.
- Pareto sweep over α reports the joint objective trend (for analysis/reporting only).

## Trade-offs & Simplifications
- No altitude or 3D movement.
- No queueing or packet drops beyond coverage/SNR.
- Single-packet service per contact for clarity.


