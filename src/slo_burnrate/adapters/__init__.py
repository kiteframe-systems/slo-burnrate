"""Backend adapters for slo-burnrate.

Adapters must return either:
- good_count + total_count, or
- good_fraction.

No secrets are stored in this package; callers provide creds via env/config.
"""
