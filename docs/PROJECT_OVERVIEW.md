# UAV-assisted Energy and AoI-aware Communications — Project Overview

This project simulates a single UAV that serves N ground IoT nodes on a 2D plane. It studies the trade-off between information freshness (Age of Information, AoI) and energy usage (flight, hover, and communication).

## Objectives
- Minimize AoI across nodes while respecting the UAV battery and mission time.
- Track energy consumption from flight, hovering during communication, and transmission.
- Provide multiple scheduling policies and simple routing heuristics.
- Produce clear metrics and plots, with a CLI to run scenarios.

## Key Models
- AoI: Each node’s AoI increases with time and resets to 0 upon successful service.
- Motion: UAV flies with constant speed v, flight time = d / v.
- Energy:
  - E_fly = P_move * (d / v)
  - E_hover = P_hover * t_hover
  - E_tx = P_tx * t_tx
- Radio: Rate R = B * log2(1 + SNR) with simple path-loss; success if within comm radius OR SNR above threshold.

## Algorithms
- Policies:
  - RR (Round Robin)
  - MAF (Max-Age-First)
  - AWN (Age-Weighted-Nearest): score = AoI^β / (dist^γ + ε)
- Routing: Nearest-Neighbor tour followed by 2-Opt improvement. Also a greedy next-by-policy mode.

## Metrics & Visualization
- Metrics: average AoI, max AoI, p99 AoI, total energy, energy per update.
- Plots: AoI vs time, energy vs time, route path, policy comparison bars, AoI–Energy Pareto curve (by α).

## Why This Matters
AoI captures information freshness, crucial for time-sensitive IoT data. UAVs provide mobility but have tight energy budgets. This simulator helps explore design choices balancing freshness and energy.


