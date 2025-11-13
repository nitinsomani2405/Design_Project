# Mathematical Formulas

This document describes all mathematical formulas and models used in the UAV-assisted Energy and AoI-aware Communications simulator.

## Table of Contents
1. [Age of Information (AoI)](#age-of-information-aoi)
2. [Distance and Geometry](#distance-and-geometry)
3. [Motion and Flight](#motion-and-flight)
4. [Energy Consumption](#energy-consumption)
5. [Radio Communication](#radio-communication)
6. [Policy Scoring](#policy-scoring)
7. [Metrics](#metrics)

---

## Age of Information (AoI)

### AoI Evolution
The Age of Information for each node increases linearly with time and resets to zero upon successful service:

\[
\text{AoI}_i(t + \Delta t) = \text{AoI}_i(t) + \Delta t
\]

\[
\text{AoI}_i(t) = 0 \quad \text{(upon successful service)}
\]

**Where:**
- \(\text{AoI}_i(t)\) = Age of Information for node \(i\) at time \(t\) (seconds)
- \(\Delta t\) = Time increment (seconds)

**Initial Condition:**
\[
\text{AoI}_i(0) = 0 \quad \forall i
\]

---

## Distance and Geometry

### Euclidean Distance
Distance between two points in 2D space:

\[
d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}
\]

**Where:**
- \(d\) = Distance (meters)
- \((x_1, y_1)\), \((x_2, y_2)\) = Coordinates of two points

**Implementation:**
\[
d = \text{hypot}(x_2 - x_1, y_2 - y_1)
\]

---

## Motion and Flight

### Flight Time
Time required to fly a distance at constant speed:

\[
t_{\text{fly}} = \frac{d}{v}
\]

**Where:**
- \(t_{\text{fly}}\) = Flight time (seconds)
- \(d\) = Distance to travel (meters)
- \(v\) = UAV speed (meters per second)

**Implementation (with safety check):**
\[
t_{\text{fly}} = \frac{d}{\max(v, 10^{-9})}
\]

---

## Energy Consumption

The simulator uses the **Zeng et al. (2016) propulsion model** for realistic UAV energy consumption. This model accounts for profile power, induced power, and parasitic drag.

### Propulsion Power (Zeng Model)
Propulsion power as a function of forward speed \(v\):

\[
P(v) = P_0 \left(1 + \frac{3v^2}{U_{\text{tip}}^2}\right) + P_i \sqrt{\sqrt{1 + \frac{v^4}{4v_0^4}} - \frac{v^2}{2v_0^2}} + \frac{1}{2} d_0 \rho s A v^3
\]

**Where:**
- \(P(v)\) = Propulsion power at speed \(v\) (W)
- \(P_0\) = Profile/blade power baseline (W)
- \(P_i\) = Induced power in hover (W)
- \(U_{\text{tip}}\) = Rotor blade tip speed (m/s)
- \(v_0\) = Induced velocity in hover (m/s)
- \(d_0\) = Fuselage drag coefficient (dimensionless)
- \(\rho\) = Air density (kg/m³)
- \(s\) = Rotor solidity (dimensionless)
- \(A\) = Rotor disk area (m²)

**Induced velocity in hover:**
\[
v_0 = \sqrt{\frac{W}{2\rho A}}
\]

**Where:**
- \(W = m \cdot g\) = Weight (N)
- \(m\) = UAV mass (kg)
- \(g\) = Gravity acceleration (m/s²)

**Induced power (if not provided):**
\[
P_i = W \cdot v_0
\]

### Flight Energy
Energy consumed during flight at constant speed \(v\):

\[
E_{\text{fly}} = \frac{P(v) \cdot t_{\text{fly}}}{3600} = \frac{P(v) \cdot d}{3600 \cdot v}
\]

**Where:**
- \(E_{\text{fly}}\) = Flight energy (Wh)
- \(P(v)\) = Propulsion power at speed \(v\) (W)
- \(t_{\text{fly}} = d/v\) = Flight time (seconds)
- \(d\) = Distance traveled (m)
- \(v\) = Forward speed (m/s)
- \(3600\) = Conversion factor (seconds to hours)

### Hover Energy
Energy consumed while hovering:

\[
P_{\text{hover}} = P_0 + P_i
\]

\[
E_{\text{hover}} = \frac{P_{\text{hover}} \cdot t_{\text{hover}}}{3600}
\]

**Where:**
- \(E_{\text{hover}}\) = Hover energy (Wh)
- \(P_{\text{hover}}\) = Hover power = \(P_0 + P_i\) (W)
- \(t_{\text{hover}}\) = Hover duration (seconds)

### Transmission Energy
Energy consumed during data transmission including circuit power and power amplifier efficiency:

\[
P_{\text{tx}} = P_{\text{circuit}} + \frac{P_{\text{out}}}{\eta_{\text{amp}}}
\]

\[
E_{\text{tx}} = \frac{P_{\text{tx}} \cdot t_{\text{tx}}}{3600}
\]

**Where:**
- \(E_{\text{tx}}\) = Transmission energy (Wh)
- \(P_{\text{tx}}\) = Total transmission power (W)
- \(P_{\text{circuit}}\) = Circuit/base power (W)
- \(P_{\text{out}}\) = Output/RF power (W)
- \(\eta_{\text{amp}}\) = Power amplifier efficiency (dimensionless, 0-1)
- \(t_{\text{tx}}\) = Transmission time (seconds)

### Total Energy
\[
E_{\text{total}} = E_{\text{fly}} + E_{\text{hover}} + E_{\text{tx}}
\]

**Energy Breakdown (tracked in logs):**
- \(E_{\text{fly\_total}}\) = Cumulative flight energy (Wh)
- \(E_{\text{hover\_total}}\) = Cumulative hover energy (Wh)
- \(E_{\text{tx\_total}}\) = Cumulative transmission energy (Wh)

**Energy Constraint:**
\[
E_{\text{total}} \leq E_{\text{battery}}
\]

**Where:**
- \(E_{\text{battery}}\) = Battery capacity (Wh)

---

## Radio Communication

### Path Loss Model
Received power with simple path-loss model:

\[
P_r = P_t \cdot d^{-n}
\]

**Where:**
- \(P_r\) = Received power (W)
- \(P_t\) = Transmitted power (W)
- \(d\) = Distance (meters)
- \(n\) = Path-loss exponent

**Implementation (with epsilon to avoid division by zero):**
\[
P_r = P_t \cdot \max(d, \epsilon)^{-n}, \quad \epsilon = 10^{-6}
\]

### Signal-to-Noise Ratio (SNR)
\[
\text{SNR} = \frac{P_r}{N_0}
\]

**Where:**
- \(\text{SNR}\) = Signal-to-Noise Ratio (linear, dimensionless)
- \(N_0\) = Noise power (W)

**Combined:**
\[
\text{SNR} = \frac{P_t \cdot d^{-n}}{N_0}
\]

### Achievable Data Rate (Shannon Capacity)
\[
R = B \cdot \log_2(1 + \text{SNR})
\]

**Where:**
- \(R\) = Data rate (bits per second, bps)
- \(B\) = Bandwidth (Hz)
- \(\text{SNR}\) = Signal-to-Noise Ratio (linear)

**Full expression:**
\[
R = B \cdot \log_2\left(1 + \frac{P_t \cdot d^{-n}}{N_0}\right)
\]

### Transmission Time
Time required to transmit a payload:

\[
t_{\text{tx}} = \frac{\text{payload\_bits}}{R}
\]

**Where:**
- \(t_{\text{tx}}\) = Transmission time (seconds)
- \(\text{payload\_bits}\) = Payload size (bits)
- \(R\) = Data rate (bps)

**Implementation (with safety check):**
\[
t_{\text{tx}} = \frac{\text{payload\_bits}}{\max(R, 10^{-9})}
\]

### Communication Success
Communication is successful if either condition is met:

\[
\text{success} = \begin{cases}
\text{true} & \text{if } d \leq R_{\text{comm}} \\
\text{true} & \text{if } \text{SNR} \geq \text{SNR}_{\text{threshold}} \\
\text{false} & \text{otherwise}
\end{cases}
\]

**Where:**
- \(R_{\text{comm}}\) = Communication radius (meters)
- \(\text{SNR}_{\text{threshold}}\) = Minimum required SNR (linear)

---

## Policy Scoring

### Round-Robin (RR)
Selects nodes in cyclic order:

\[
j_{\text{next}} = (j_{\text{current}} + 1) \bmod N
\]

**Where:**
- \(j_{\text{next}}\) = Next node index
- \(j_{\text{current}}\) = Current node index
- \(N\) = Total number of nodes

### Max-Age-First (MAF)
Selects the node with maximum AoI:

\[
j = \arg\max_i \text{AoI}_i
\]

### Age-Weighted-Nearest (AWN)
Score-based selection balancing AoI and distance:

\[
\text{score}_i = \frac{\text{AoI}_i^{\beta}}{(d_i^{\gamma} + \epsilon)}
\]

**Where:**
- \(\text{score}_i\) = Score for node \(i\)
- \(\text{AoI}_i\) = Age of Information for node \(i\) (seconds)
- \(d_i\) = Distance to node \(i\) (meters)
- \(\beta\) = AoI weight exponent
- \(\gamma\) = Distance weight exponent
- \(\epsilon = 10^{-6}\) = Small constant to avoid division by zero

**Node Selection:**
\[
j = \arg\max_i \text{score}_i
\]

**Special Case (All AoI = 0):**
When all AoI values are effectively zero (\(\max(\text{AoI}) < 10^{-6}\)), the policy uses distance-based selection:

\[
j = \arg\min_i d_i
\]

### Dynamic Beta-Gamma Adjustment (Alpha Sweep)
In the `sweep-alpha` command, \(\beta\) and \(\gamma\) are dynamically adjusted based on \(\alpha\):

\[
\beta = \beta_{\min} + \alpha \cdot (\beta_{\max} - \beta_{\min})
\]

\[
\gamma = \gamma_{\max} - \alpha \cdot (\gamma_{\max} - \gamma_{\min})
\]

**Default Ranges:**
- \(\beta_{\min} = 0.8\), \(\beta_{\max} = 1.6\)
- \(\gamma_{\min} = 0.6\), \(\gamma_{\max} = 1.6\)

**Expanded:**
\[
\beta = 0.8 + \alpha \cdot 0.8 = 0.8(1 + \alpha)
\]

\[
\gamma = 1.6 - \alpha \cdot 1.0 = 1.6 - \alpha
\]

**Interpretation:**
- **Low \(\alpha\) (energy-focused):** Low \(\beta\), high \(\gamma\) → Prioritizes proximity
- **High \(\alpha\) (AoI-focused):** High \(\beta\), low \(\gamma\) → Prioritizes freshness

---

## Metrics

### Average AoI
\[
\overline{\text{AoI}} = \frac{1}{T} \sum_{t=1}^{T} \text{AoI}_{\text{avg}}(t)
\]

**Where:**
- \(\overline{\text{AoI}}\) = Average AoI (seconds)
- \(T\) = Number of time steps
- \(\text{AoI}_{\text{avg}}(t) = \frac{1}{N} \sum_{i=1}^{N} \text{AoI}_i(t)\) = Average AoI across all nodes at time \(t\)

### Maximum AoI
\[
\text{AoI}_{\max} = \max_{t} \left( \max_i \text{AoI}_i(t) \right)
\]

**Where:**
- \(\text{AoI}_{\max}\) = Maximum AoI observed (seconds)

### 99th Percentile AoI (p99)
\[
\text{AoI}_{p99} = \text{percentile}_{99}\left( \left\{ \max_i \text{AoI}_i(t) : t = 1, \ldots, T \right\} \right)
\]

**Where:**
- \(\text{AoI}_{p99}\) = 99th percentile of maximum AoI values (seconds)

### Total Energy Consumption
\[
E_{\text{total}} = E_{\text{final}}
\]

**Where:**
- \(E_{\text{total}}\) = Total energy consumed (Wh)
- \(E_{\text{final}}\) = Energy at end of simulation

### Energy per Update
\[
E_{\text{per\_update}} = \frac{E_{\text{total}}}{N_{\text{updates}}}
\]

**Where:**
- \(E_{\text{per\_update}}\) = Average energy per node update (Wh)
- \(N_{\text{updates}}\) = Number of successful node updates

### Normalized Energy (for Pareto plots)
\[
E_{\text{norm}} = \frac{E_{\text{total}}}{E_{\text{battery}}}
\]

**Where:**
- \(E_{\text{norm}}\) = Normalized energy consumption (dimensionless, typically 0-1)
- \(E_{\text{battery}}\) = Battery capacity (Wh)

---

## Simulation Constraints

### Time Constraint
\[
t \leq T_{\text{mission}}
\]

**Where:**
- \(t\) = Current simulation time (seconds)
- \(T_{\text{mission}}\) = Mission duration (seconds)

### Energy Constraint
\[
E_{\text{total}} \leq E_{\text{battery}}
\]

### Termination Conditions
The simulation terminates when either:
1. \(t \geq T_{\text{mission}}\), or
2. \(E_{\text{total}} \geq E_{\text{battery}}\)

---

## Notes

- All time values are in **seconds**
- All energy values are in **Watt-hours (Wh)**
- All power values are in **Watts (W)**
- All distances are in **meters (m)**
- All data rates are in **bits per second (bps)**
- The path-loss exponent \(n\) is typically in the range [2, 4] (default: 2.7)
- The epsilon constant \(\epsilon = 10^{-6}\) is used to prevent division by zero and numerical instability

