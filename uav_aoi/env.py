from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Iterable
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


def energy_fly_Wh(distance_m: float, speed_mps: float, P_move_W: float) -> float:
    t = flight_time_s(distance_m, speed_mps)
    return (P_move_W * t) / 3600.0


def energy_hover_Wh(t_hover_s: float, P_hover_W: float) -> float:
    return (P_hover_W * t_hover_s) / 3600.0


def energy_tx_Wh(t_tx_s: float, P_tx_W: float) -> float:
    return (P_tx_W * t_tx_s) / 3600.0


def total_path_length(points: Iterable[Tuple[float, float]]) -> float:
    """Compute total tour length of visiting given points in order and returning to start."""

    pts = list(points)
    if len(pts) < 2:
        return 0.0
    length = 0.0
    for i in range(len(pts) - 1):
        length += euclidean(pts[i], pts[i + 1])
    return length


