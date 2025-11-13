from __future__ import annotations

from typing import List, Sequence, Tuple, Callable
import math

from .env import euclidean


def policy_round_robin(current_idx: int, N: int) -> int:
    """Round-robin across N nodes."""

    return (current_idx + 1) % N


def policy_maf(aoi: Sequence[float]) -> int:
    """Max-Age-First: pick node with largest AoI."""

    return int(max(range(len(aoi)), key=lambda i: aoi[i]))


def policy_awn(
    aoi: Sequence[float],
    uav_pos: Tuple[float, float],
    node_positions: Sequence[Tuple[float, float]],
    beta: float,
    gamma: float,
) -> int:
    """Age-Weighted-Nearest scoring: score = AoI^beta / (dist^gamma + 1e-6).
    
    When all AoI values are 0, uses distance-based selection (closest node).
    This ensures beta/gamma have an effect once AoI values start to differ.
    """
    # Check if all AoI values are effectively zero
    max_aoi = max(aoi) if aoi else 0.0
    if max_aoi < 1e-6:
        # All AoI are zero - use distance-based selection (closest node)
        # This is a tie-breaker when beta/gamma can't differentiate
        best_idx = 0
        best_dist = math.inf
        for i, pos in enumerate(node_positions):
            d = euclidean(uav_pos, pos)
            if d < best_dist:
                best_dist = d
                best_idx = i
        return best_idx
    
    # Normal AWN scoring when AoI values are non-zero
    best_idx = 0
    best_score = -math.inf
    for i, age in enumerate(aoi):
        d = euclidean(uav_pos, node_positions[i])
        score = (age ** beta) / (max(d, 1e-9) ** gamma + 1e-6)
        if score > best_score:
            best_score = score
            best_idx = i
    return best_idx


def nearest_neighbor_order(points: List[Tuple[float, float]]) -> List[int]:
    """Nearest Neighbor heuristic returning visiting order indices starting at 0."""

    if not points:
        return []
    N = len(points)
    unvisited = set(range(1, N))
    order = [0]
    while unvisited:
        last = order[-1]
        next_idx = min(unvisited, key=lambda j: euclidean(points[last], points[j]))
        order.append(next_idx)
        unvisited.remove(next_idx)
    return order


def two_opt(order: List[int], points: List[Tuple[float, float]]) -> List[int]:
    """2-Opt improvement on a tour (without returning to start).

    The function attempts to reduce total path length by edge swaps.
    """

    def tour_length(ordr: List[int]) -> float:
        length = 0.0
        for i in range(len(ordr) - 1):
            length += euclidean(points[ordr[i]], points[ordr[i + 1]])
        return length

    improved = True
    best = order[:]
    best_len = tour_length(best)
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for k in range(i + 1, len(best) - 1):
                new_order = best[:i] + best[i:k + 1][::-1] + best[k + 1 :]
                new_len = tour_length(new_order)
                if new_len + 1e-9 < best_len:
                    best = new_order
                    best_len = new_len
                    improved = True
    return best


def make_policy(policy_name: str) -> Callable[..., int]:
    name = policy_name.upper()
    if name == "RR":
        return policy_round_robin  # type: ignore[return-value]
    if name == "MAF":
        return policy_maf  # type: ignore[return-value]
    if name == "AWN":
        return policy_awn  # type: ignore[return-value]
    raise ValueError(f"Unknown policy: {policy_name}")


