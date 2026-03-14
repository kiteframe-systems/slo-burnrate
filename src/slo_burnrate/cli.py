from __future__ import annotations

import argparse

from .core import burn_rate


def main() -> None:
    p = argparse.ArgumentParser(description="Compute SLO error-budget burn rate")
    p.add_argument("--slo", type=float, required=True, help="SLO as fraction, e.g. 0.999")
    p.add_argument(
        "--good",
        type=float,
        required=True,
        help="Observed good fraction in the window, e.g. 0.9987",
    )
    p.add_argument(
        "--window",
        type=float,
        required=True,
        help="Window seconds, e.g. 3600 for 1h",
    )
    p.add_argument(
        "--period",
        type=float,
        required=True,
        help="Budget period seconds, e.g. 2592000 for 30d",
    )
    args = p.parse_args()

    br = burn_rate(args.slo, args.good, args.window, args.period)
    print(f"burn_rate={br:.3f}")
