from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone

from .core import burn_rate
from .models import WindowResult
from .util import WindowSpec, get_env, parse_duration_seconds
from .adapters.postgres import PostgresConfig, query_window as pg_query_window
from .adapters.datadog import DatadogConfig, query_window as dd_query_window


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _compute_windows(
    slo: float,
    period_seconds: int,
    windows: list[int],
    results: list[WindowResult],
    warn: float | None,
    page: float | None,
) -> dict:
    rows = []
    overall = "OK"

    for w, r in zip(windows, results, strict=True):
        good_frac = r.normalized_good_fraction()
        br = burn_rate(slo, good_frac, w, period_seconds)
        status = "OK"
        if page is not None and br >= page:
            status = "PAGE"
        elif warn is not None and br >= warn:
            status = "WARN"

        if status == "PAGE":
            overall = "PAGE"
        elif status == "WARN" and overall != "PAGE":
            overall = "WARN"

        rows.append(
            {
                "window_seconds": w,
                "good": r.good,
                "total": r.total,
                "good_fraction": good_frac,
                "burn_rate": br,
                "status": status,
            }
        )

    return {"windows": rows, "overall": overall}


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--slo", type=float, required=True, help="SLO fraction, e.g. 0.999")
    p.add_argument(
        "--period",
        type=str,
        required=True,
        help="Budget period (e.g. 30d, 28d, 7d, 2592000s)",
    )
    p.add_argument(
        "--window",
        action="append",
        required=True,
        help="Window duration (repeatable), e.g. --window 5m --window 1h",
    )
    p.add_argument("--warn", type=float, default=None, help="Warn burn-rate threshold")
    p.add_argument("--page", type=float, default=None, help="Page burn-rate threshold")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )


def _parse_period(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("s") and s[:-1].isdigit():
        return int(s[:-1])
    return parse_duration_seconds(s)


def cmd_pg(args) -> int:
    dsn = args.dsn or get_env(args.dsn_env)
    cfg = PostgresConfig(dsn=dsn, good_sql=args.good_sql, total_sql=args.total_sql, ratio_sql=args.ratio_sql)

    now = _now_utc()
    windows = [WindowSpec.from_str(w).seconds for w in args.window]
    results = []
    for w in windows:
        end = now
        start = now - timedelta(seconds=w)
        results.append(pg_query_window(cfg, start, end))

    out = _compute_windows(args.slo, _parse_period(args.period), windows, results, args.warn, args.page)

    if args.format == "json":
        print(json.dumps({"slo": args.slo, "period": args.period, **out}, indent=2))
    else:
        for row in out["windows"]:
            print(f"window={row['window_seconds']}s burn_rate={row['burn_rate']:.3f} status={row['status']}")
        print(f"overall={out['overall']}")

    return 0


def cmd_datadog(args) -> int:
    api_key = args.api_key or get_env(args.api_key_env)
    app_key = args.app_key or get_env(args.app_key_env)
    cfg = DatadogConfig(
        site=args.site,
        api_key=api_key,
        app_key=app_key,
        good_query=args.good_query,
        total_query=args.total_query,
        ratio_query=args.ratio_query,
    )

    now = _now_utc()
    windows = [WindowSpec.from_str(w).seconds for w in args.window]
    results = []
    for w in windows:
        end = now
        start = now - timedelta(seconds=w)
        results.append(dd_query_window(cfg, start, end))

    out = _compute_windows(args.slo, _parse_period(args.period), windows, results, args.warn, args.page)

    if args.format == "json":
        print(json.dumps({"slo": args.slo, "period": args.period, **out}, indent=2))
    else:
        for row in out["windows"]:
            print(f"window={row['window_seconds']}s burn_rate={row['burn_rate']:.3f} status={row['status']}")
        print(f"overall={out['overall']}")

    return 0


def main() -> None:
    p = argparse.ArgumentParser(prog="slo-burnrate", description="Compute SLO burn rates from various backends")
    sub = p.add_subparsers(dest="cmd", required=True)

    pg = sub.add_parser("pg", help="Compute burn rates from Postgres")
    _add_common(pg)
    pg.add_argument("--dsn", default=None, help="Postgres DSN (discouraged; prefer env)")
    pg.add_argument("--dsn-env", default="PG_DSN", help="Env var name holding DSN")
    pg.add_argument("--good-sql", default=None, help="SQL returning good count; use $START/$END")
    pg.add_argument("--total-sql", default=None, help="SQL returning total count; use $START/$END")
    pg.add_argument("--ratio-sql", default=None, help="SQL returning good_fraction; use $START/$END")
    pg.set_defaults(func=cmd_pg)

    dd = sub.add_parser("datadog", help="Compute burn rates from Datadog")
    _add_common(dd)
    dd.add_argument("--site", default="datadoghq.com", help="Datadog site (e.g. datadoghq.com, datadoghq.eu)")
    dd.add_argument("--api-key", default=None, help="Datadog API key (prefer env)")
    dd.add_argument("--app-key", default=None, help="Datadog APP key (prefer env)")
    dd.add_argument("--api-key-env", default="DD_API_KEY", help="Env var name for API key")
    dd.add_argument("--app-key-env", default="DD_APP_KEY", help="Env var name for APP key")
    dd.add_argument("--good-query", default=None, help="Datadog query for good")
    dd.add_argument("--total-query", default=None, help="Datadog query for total")
    dd.add_argument("--ratio-query", default=None, help="Datadog query returning good_fraction")
    dd.set_defaults(func=cmd_datadog)

    args = p.parse_args()
    raise SystemExit(args.func(args))
