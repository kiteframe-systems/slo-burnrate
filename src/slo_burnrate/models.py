from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WindowResult:
    window_seconds: int
    good: float | None = None
    total: float | None = None
    good_fraction: float | None = None

    def normalized_good_fraction(self) -> float:
        if self.good_fraction is not None:
            if not (0 < self.good_fraction <= 1):
                raise ValueError("good_fraction must be (0,1]")
            return float(self.good_fraction)
        if self.good is None or self.total is None:
            raise ValueError("must provide either good_fraction or good+total")
        if self.total <= 0:
            raise ValueError("total must be > 0")
        return float(self.good) / float(self.total)
