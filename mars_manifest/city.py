"""City-ramp seed data: loader and integration helpers.

`data/city_ramp_seed.yaml` carries the tier-labeled anchors for extending the
program past first crew (population milestones, per-capita scaling factors,
import-mass decay, growth rules, the industrial-closure ladder). Research
basis and verification trail: docs/CITY_RAMP_RESEARCH.md.

This module only loads and adapts that data; consumers:
- CampaignPlanner takes `milestone_rules()` merged into its unlock rules
  (population milestones become capability flags via `min_population`).
- The closure ladder and import-decay curve are consumed by the closure
  model (task A3) and import ledger (task B1).
"""
from __future__ import annotations

from pathlib import Path

import yaml


def load_city_ramp(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    for m in doc.get("population_milestones", []):
        for key in ("flag", "population", "tier", "source"):
            if key not in m:
                raise ValueError(f"city_ramp milestone missing '{key}': {m}")
    return doc


def milestone_rules(city: dict) -> dict:
    """Population milestones as capability-unlock rules (min_population)."""
    return {m["flag"]: {"min_population": int(m["population"])}
            for m in city.get("population_milestones", [])}


def closure_rules(city: dict) -> dict:
    """Industrial-closure stages as capability-unlock rules."""
    return dict(city.get("closure_unlocks", {}))


def city_rules(city: dict) -> dict:
    """All city-ramp capability rules (milestones + closure stages)."""
    return {**milestone_rules(city), **closure_rules(city)}


# recurring imports are per-year; a synod is ~26 months
YEARS_PER_SYNOD = 26 / 12.0

CLOSURE_ORDER = ["closure_gen_5", "closure_gen_4", "closure_gen_3",
                 "closure_gen_2", "closure_gen_1"]


def closure_stage(capabilities) -> str:
    """Highest closure stage reached, or 'none'."""
    for stage in CLOSURE_ORDER:
        if stage in capabilities:
            return stage
    return "none"


def import_rate_t_per_person_year(city: dict, capabilities) -> float:
    decay = city.get("import_decay_t_per_person_year", {})
    return float(decay.get(closure_stage(capabilities), decay.get("none", 10.0)))
