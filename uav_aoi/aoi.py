from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class AoIState:
    """Age of Information state for N nodes.

    AoI evolves as AoI_i(t+Δ) = AoI_i(t) + Δ, and resets to 0 on successful service.
    """

    values: List[float]

    @classmethod
    def zeros(cls, N: int) -> "AoIState":
        return cls(values=[0.0 for _ in range(N)])

    def increment(self, delta_t: float) -> None:
        for i in range(len(self.values)):
            self.values[i] += delta_t

    def reset(self, idx: int) -> None:
        self.values[idx] = 0.0

    def copy(self) -> "AoIState":
        return AoIState(values=list(self.values))


