"""Core error budget helpers.

All math here is intentionally simple and explicit.
"""

from __future__ import annotations


def error_budget(slo: float) -> float:
    """Return error budget fraction for an SLO.

    Example: slo=0.999 -> budget=0.001
    """
    if not (0 < slo < 1):
        raise ValueError("slo must be between 0 and 1")
    return 1.0 - slo


def burn_rate(
    slo: float,
    observed_good_fraction: float,
    window_seconds: float,
    period_seconds: float,
) -> float:
    """Compute burn rate.

    burn_rate = (bad_fraction / error_budget) * (period/window)

    - observed_good_fraction: fraction of good events in the window.
    - window_seconds: the lookback window you measured.
    - period_seconds: the full budget period (e.g., 30d in seconds).

    A burn rate of 1.0 means you're burning budget at a pace that will exhaust it
    exactly at the end of the period.
    """
    if window_seconds <= 0 or period_seconds <= 0:
        raise ValueError("window_seconds and period_seconds must be > 0")
    if not (0 < observed_good_fraction <= 1):
        raise ValueError("observed_good_fraction must be (0, 1]")

    budget = error_budget(slo)
    bad = 1.0 - observed_good_fraction

    # If your SLO is perfect but you observed bad=0, burn is 0.
    if bad <= 0:
        return 0.0

    return (bad / budget) * (period_seconds / window_seconds)
