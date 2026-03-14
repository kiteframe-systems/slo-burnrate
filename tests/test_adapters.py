from __future__ import annotations

from datetime import datetime, timezone

import pytest

from slo_burnrate.adapters.postgres import _substitute
from slo_burnrate.adapters.datadog import _dd_url


def test_substitute_tokens():
    start = datetime(2026, 3, 14, 12, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 3, 14, 13, 0, 0, tzinfo=timezone.utc)
    q = "select * from t where ts >= $START and ts < $END"
    out = _substitute(q, start, end)
    assert "2026-03-14T12:00:00Z" in out
    assert "2026-03-14T13:00:00Z" in out


def test_dd_url():
    assert _dd_url("datadoghq.com") == "https://api.datadoghq.com"
    assert _dd_url("https://api.datadoghq.eu") == "https://api.datadoghq.eu"
