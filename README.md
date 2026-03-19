# slo-burnrate

Small utilities for error budgets and burn rates.

## Install (dev)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## CLI
```bash
slo-burnrate --slo 0.999 --good 0.9987 --window 3600 --period 2592000
```

### JSON output
```bash
slo-burnrate --slo 0.999 --good 0.9987 --window 3600 --period 2592000 --json
```

## Notes
This intentionally avoids cleverness. Under load, explicit math wins.

## License
MIT
