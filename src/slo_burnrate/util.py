from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone


def parse_duration_seconds(s: str) -> int:
    s = s.strip().lower()
    m = re.fullmatch(r"(\d+)(s|m|h|d)", s)
    if not m:
        raise ValueError(f"invalid duration: {s} (expected like 5m, 1h, 30d)")
    n = int(m.group(1))
    unit = m.group(2)
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    return n * mult


def iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise ValueError(f"missing required env var: {name}")
    return v


@dataclass(frozen=True)
class WindowSpec:
    seconds: int

    @classmethod
    def from_str(cls, s: str) -> "WindowSpec":
        return cls(parse_duration_seconds(s))
