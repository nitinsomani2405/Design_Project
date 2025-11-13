from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Iterable, Dict, Any, Optional
import math


@dataclass
class Node:
    """Ground IoT node in 2D plane.

    Attributes:
        node_id: Unique identifier.
        x: X coordinate (meters).
        y: Y coordinate (meters).
    """

    node_id: int
    x: float
    y: float

    @property
    def pos(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class UAV:
    """UAV model with simple energy accounting.

    Energy is tracked in Wh; powers are in W; times are in seconds.
    """

    x: float
    y: float
    speed_mps: float
    battery_Wh: float
    P_move_W: float
    P_hover_W: float
    P_tx_W: float

    def position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def move_to(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def euclidean(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Euclidean distance in meters."""

    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.hypot(dx, dy)


@dataclass
class Radio:
    """Simple radio/channel parameters."""

    bandwidth_Hz: float
    noise_W: float
    pathloss_exponent: float
    snr_threshold_linear: float
    comm_radius_m: float


def snr_linear(tx_power_W: float, d_m: float, radio: Radio) -> float:
    """Compute received SNR (linear) with simple path-loss and constant gain.

    Model: Pr = Pt * d^{-n}. SNR = Pr / N0. No fading/shadowing for simplicity.
    A small epsilon avoids div-by-zero at d=0.
    """

    epsilon = 1e-6
    path_loss = max(d_m, epsilon) ** (-radio.pathloss_exponent)
    pr = tx_power_W * path_loss
    return pr / radio.noise_W


def achievable_rate_bps(tx_power_W: float, d_m: float, radio: Radio) -> float:
    """Shannon-like rate: R = B * log2(1 + SNR)."""

    snr = snr_linear(tx_power_W, d_m, radio)
    return radio.bandwidth_Hz * math.log2(1.0 + snr)


def in_coverage(d_m: float, radio: Radio) -> bool:
    """Coverage check using comm radius OR SNR threshold."""

    if d_m <= radio.comm_radius_m:
        return True
    return snr_linear(1.0, d_m, radio) >= radio.snr_threshold_linear  # normalized power


def flight_time_s(distance_m: float, speed_mps: float) -> float:
    return distance_m / max(speed_mps, 1e-9)


def _compute_induced_velocity(uav_cfg: Dict[str, Any]) -> float:
    """Compute induced velocity in hover v0 = sqrt(W / (2 * rho * A)).
    
    Where W = mass * g (weight in Newtons).
    """
    g = float(uav_cfg.get('g', 9.81))
    mass = float(uav_cfg['mass_kg'])
    rho = float(uav_cfg['air_density'])
    
    # Compute rotor disk area if not provided
    if 'disc_area_m2' in uav_cfg and uav_cfg['disc_area_m2'] is not None:
        A = float(uav_cfg['disc_area_m2'])
    else:
        rotor_radius = float(uav_cfg['rotor_radius_m'])
        A = math.pi * (rotor_radius ** 2)
    
    W = mass * g  # Weight in Newtons
    v0 = math.sqrt(W / (2.0 * rho * A))
    return v0


def _compute_induced_power(uav_cfg: Dict[str, Any], v0: float) -> float:
    """Compute induced power Pi = W * v0.
    
    If Pi is provided in config, use it; otherwise compute from weight and v0.
    """
    if 'Pi' in uav_cfg and uav_cfg['Pi'] is not None:
        return float(uav_cfg['Pi'])
    
    g = float(uav_cfg.get('g', 9.81))
    mass = float(uav_cfg['mass_kg'])
    W = mass * g  # Weight in Newtons
    Pi = W * v0
    return Pi


def propulsion_power(v: float, uav_cfg: Dict[str, Any], v0: Optional[float] = None, Pi: Optional[float] = None) -> float:
    """Compute propulsion power using Zeng et al. 2016 model.
    
    Formula: P(v) = P0 * (1 + 3*v^2/U_tip^2)
              + Pi * sqrt(sqrt(1 + v^4/(4*v0^4)) - v^2/(2*v0^2))
              + 0.5 * d0 * rho * s * A * v^3
    
    Args:
        v: Forward speed (m/s)
        uav_cfg: UAV configuration dictionary
        v0: Induced velocity in hover (m/s) - computed if None
        Pi: Induced power in hover (W) - computed if None
    
    Returns:
        Propulsion power (W)
    """
    if v < 0:
        v = 0.0
    
    P0 = float(uav_cfg['P0'])
    U_tip = float(uav_cfg['blade_tip_speed'])
    d0 = float(uav_cfg['d0'])
    rho = float(uav_cfg['air_density'])
    s = float(uav_cfg['rotor_solidity'])
    
    # Compute rotor disk area if not provided
    if 'disc_area_m2' in uav_cfg and uav_cfg['disc_area_m2'] is not None:
        A = float(uav_cfg['disc_area_m2'])
    else:
        rotor_radius = float(uav_cfg['rotor_radius_m'])
        A = math.pi * (rotor_radius ** 2)
    
    # Compute v0 if not provided
    if v0 is None:
        v0 = _compute_induced_velocity(uav_cfg)
    
    # Compute Pi if not provided
    if Pi is None:
        Pi = _compute_induced_power(uav_cfg, v0)
    
    # Profile power term
    profile = P0 * (1.0 + 3.0 * (v ** 2) / (U_tip ** 2))
    
    # Induced power term - handle edge cases carefully
    if v0 <= 1e-9:
        # Degenerate case: avoid division by zero
        induced = Pi
    else:
        inside_sqrt = 1.0 + (v ** 4) / (4.0 * (v0 ** 4))
        # Clamp to non-negative to handle numerical roundoff
        sqrt_term = math.sqrt(max(inside_sqrt, 0.0))
        induced_factor = sqrt_term - (v ** 2) / (2.0 * v0 ** 2)
        # Clamp induced_factor to non-negative
        induced = Pi * math.sqrt(max(induced_factor, 0.0))
    
    # Parasitic drag term
    parasitic = 0.5 * d0 * rho * s * A * (v ** 3)
    
    return profile + induced + parasitic


def energy_fly_Wh(distance_m: float, speed_mps: float, uav_cfg: Dict[str, Any], v0: Optional[float] = None, Pi: Optional[float] = None) -> float:
    """Compute flight energy using Zeng2016 propulsion model.
    
    E_fly = P(v) * (d / v) / 3600.0  (converts J to Wh)
    
    Args:
        distance_m: Distance to travel (m)
        speed_mps: Forward speed (m/s)
        uav_cfg: UAV configuration dictionary
        v0: Induced velocity in hover (m/s) - computed if None
        Pi: Induced power in hover (W) - computed if None
    
    Returns:
        Flight energy (Wh)
    """
    if speed_mps <= 0:
        return float('inf')
    
    P = propulsion_power(speed_mps, uav_cfg, v0=v0, Pi=Pi)
    t = flight_time_s(distance_m, speed_mps)
    E_J = P * t
    return E_J / 3600.0  # Convert J to Wh


def energy_hover_Wh(t_hover_s: float, uav_cfg: Dict[str, Any], v0: Optional[float] = None, Pi: Optional[float] = None) -> float:
    """Compute hover energy using Zeng2016 propulsion model.
    
    P_hover = P0 + Pi
    E_hover = P_hover * t_hover / 3600.0  (converts J to Wh)
    
    Args:
        t_hover_s: Hover duration (seconds)
        uav_cfg: UAV configuration dictionary
        v0: Induced velocity in hover (m/s) - computed if None
        Pi: Induced power in hover (W) - computed if None
    
    Returns:
        Hover energy (Wh)
    """
    if v0 is None:
        v0 = _compute_induced_velocity(uav_cfg)
    if Pi is None:
        Pi = _compute_induced_power(uav_cfg, v0)
    
    P0 = float(uav_cfg['P0'])
    P_hover = P0 + Pi
    E_J = P_hover * t_hover_s
    return E_J / 3600.0  # Convert J to Wh


def energy_tx_Wh(t_tx_s: float, tx_cfg: Dict[str, Any], P_out_W: Optional[float] = None) -> float:
    """Compute transmission energy including circuit power and PA efficiency.
    
    P_tx = P_circuit + P_out / eta_amp
    E_tx = P_tx * t_tx / 3600.0  (converts J to Wh)
    
    Args:
        t_tx_s: Transmission duration (seconds)
        tx_cfg: Transmission configuration dictionary
        P_out_W: Output power (W) - from tx_cfg if None
    
    Returns:
        Transmission energy (Wh)
    """
    P_circ = float(tx_cfg['P_circuit_W'])
    eta = float(tx_cfg['amp_efficiency'])
    
    if P_out_W is None:
        P_out_W = float(tx_cfg.get('P_out_W', 1.0))
    
    if eta <= 0:
        eta = 1.0  # Avoid division by zero
    
    P_tx = P_circ + (P_out_W / eta)
    E_J = P_tx * t_tx_s
    return E_J / 3600.0  # Convert J to Wh


def total_path_length(points: Iterable[Tuple[float, float]]) -> float:
    """Compute total tour length of visiting given points in order and returning to start."""

    pts = list(points)
    if len(pts) < 2:
        return 0.0
    length = 0.0
    for i in range(len(pts) - 1):
        length += euclidean(pts[i], pts[i + 1])
    return length


