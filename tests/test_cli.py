import json
import subprocess
import sys


def test_cli_json_output():
    cmd = [
        sys.executable,
        "-m",
        "slo_burnrate.cli",
        "--slo",
        "0.999",
        "--good",
        "0.9987",
        "--window",
        "3600",
        "--period",
        "2592000",
        "--json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)

    assert payload["slo"] == 0.999
    assert payload["observed_good_fraction"] == 0.9987
    assert payload["window_seconds"] == 3600
    assert payload["period_seconds"] == 2592000
    assert payload["burn_rate"] > 0
