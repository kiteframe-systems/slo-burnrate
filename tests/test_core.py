import pytest

from slo_burnrate.core import burn_rate, error_budget


def test_error_budget():
    assert error_budget(0.999) == pytest.approx(0.001)


def test_burn_rate_zero_when_no_bad():
    assert burn_rate(0.999, 1.0, 3600, 2592000) == 0.0


def test_burn_rate_reasonable():
    br = burn_rate(0.999, 0.998, 3600, 2592000)
    assert br > 0
