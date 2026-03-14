from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import requests

from ..models import WindowResult


@dataclass
class DatadogConfig:
    site: str
    api_key: str
    app_key: str
    good_query: str | None
    total_query: str | None
    ratio_query: str | None


def _dd_url(site: str) -> str:
    site = site.strip()
    if site.startswith("http"):
        return site.rstrip("/")
    return f"https://api.{site}".rstrip("/")


def _query(cfg: DatadogConfig, query: str, start: datetime, end: datetime) -> float:
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    url = _dd_url(cfg.site) + "/api/v1/query"
    params = {
        "from": int(start.timestamp()),
        "to": int(end.timestamp()),
        "query": query,
    }
    headers = {
        "DD-API-KEY": cfg.api_key,
        "DD-APPLICATION-KEY": cfg.app_key,
        "Accept": "application/json",
    }

    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()

    # Datadog returns series; we take the last point of the first series.
    series = data.get("series") or []
    if not series:
        raise ValueError("datadog query returned no series")

    points = series[0].get("pointlist") or []
    if not points:
        raise ValueError("datadog query returned no points")

    # point = [ms, value]
    val = points[-1][1]
    if val is None:
        raise ValueError("datadog point value is null")
    return float(val)


def query_window(cfg: DatadogConfig, start: datetime, end: datetime) -> WindowResult:
    if cfg.ratio_query:
        frac = _query(cfg, cfg.ratio_query, start, end)
        return WindowResult(window_seconds=int((end - start).total_seconds()), good_fraction=frac)

    if not (cfg.good_query and cfg.total_query):
        raise ValueError("must provide ratio_query OR (good_query and total_query)")

    good = _query(cfg, cfg.good_query, start, end)
    total = _query(cfg, cfg.total_query, start, end)
    return WindowResult(window_seconds=int((end - start).total_seconds()), good=good, total=total)
