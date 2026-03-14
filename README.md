# slo-burnrate

Small utilities for error budgets and burn rates, with a boring integration contract.

The goal is to compute burn rate from *your* sources of truth (Postgres, Datadog, …) without storing secrets.

## Install (dev)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Integration contract (v1)

Common inputs:
- `--slo 0.999`
- `--period 30d`
- repeatable windows: `--window 5m --window 1h`
- optional thresholds: `--warn 6 --page 14`
- output: `--format text|json`

Secrets:
- Always user-supplied via environment variables (recommended) or explicit flags.
- CLI will not persist secrets.

JSON output includes a `schemaVersion` field for forward compatibility.

Backends must provide either:
- `good_count` and `total_count`, or
- a `good_fraction`.

## Postgres
Use when your “truth” lives in request tables or logs.

Provide:
- DSN via env var (default `PG_DSN`)
- either `--ratio-sql`, or `--good-sql` + `--total-sql`

SQL templating:
- `$START` and `$END` are substituted with UTC ISO timestamps.

Example:
```bash
export PG_DSN='postgresql://…'

slo-burnrate pg \
  --slo 0.999 \
  --period 30d \
  --window 5m --window 1h \
  --warn 6 --page 14 \
  --good-sql "SELECT count(*) FROM requests WHERE ts >= $START AND ts < $END AND status < 500" \
  --total-sql "SELECT count(*) FROM requests WHERE ts >= $START AND ts < $END" \
  --format json
```

## Datadog
Provide keys via env vars (defaults shown):
- `DD_API_KEY`
- `DD_APP_KEY`

Example:
```bash
export DD_API_KEY='…'
export DD_APP_KEY='…'

slo-burnrate datadog \
  --slo 0.999 \
  --period 30d \
  --window 5m --window 1h \
  --warn 6 --page 14 \
  --site datadoghq.com \
  --good-query  "sum:service.request.ok{env:prod}.as_count()" \
  --total-query "sum:service.request.total{env:prod}.as_count()" \
  --format text
```

## License
MIT
