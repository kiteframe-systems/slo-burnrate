from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import psycopg

from ..models import WindowResult
from ..util import iso_z


@dataclass
class PostgresConfig:
    dsn: str
    good_sql: str | None
    total_sql: str | None
    ratio_sql: str | None


def _substitute(sql: str, start: datetime, end: datetime) -> str:
    # Intentionally minimal templating: replace literal tokens.
    return (
        sql.replace("$START", f"'{iso_z(start)}'")
        .replace("$END", f"'{iso_z(end)}'")
    )


def _scalar(cur) -> float:
    row = cur.fetchone()
    if row is None:
        raise ValueError("query returned no rows")
    v = row[0]
    if v is None:
        raise ValueError("query returned null")
    return float(v)


def query_window(
    cfg: PostgresConfig,
    start: datetime,
    end: datetime,
) -> WindowResult:
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    with psycopg.connect(cfg.dsn) as conn:
        with conn.cursor() as cur:
            if cfg.ratio_sql:
                q = _substitute(cfg.ratio_sql, start, end)
                cur.execute(q)
                frac = _scalar(cur)
                return WindowResult(window_seconds=int((end - start).total_seconds()), good_fraction=frac)

            if not (cfg.good_sql and cfg.total_sql):
                raise ValueError("must provide ratio_sql OR (good_sql and total_sql)")

            qg = _substitute(cfg.good_sql, start, end)
            qt = _substitute(cfg.total_sql, start, end)

            cur.execute(qg)
            good = _scalar(cur)
            cur.execute(qt)
            total = _scalar(cur)
            return WindowResult(window_seconds=int((end - start).total_seconds()), good=good, total=total)
