from __future__ import annotations

import argparse
import json

from .core import burn_rate, error_budget


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
    p.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of text",
    )
    args = p.parse_args()

    br = burn_rate(args.slo, args.good, args.window, args.period)

    if args.json:
        budget = error_budget(args.slo)
        payload = {
            "slo": args.slo,
            "observed_good_fraction": args.good,
            "observed_bad_fraction": 1.0 - args.good,
            "error_budget": budget,
            "window_seconds": args.window,
            "period_seconds": args.period,
            "burn_rate": br,
        }
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"burn_rate={br:.3f}")


if __name__ == "__main__":
    main()
