"""ScenarioManager: named assumption variants + structured diffing
(spec origin: HANDOFF.md §5.4).

A scenario = base assumptions + dotted-path overrides, defined in
data/assumptions_seed.json. `compare` runs a campaign (or single mission)
under two scenarios and diffs the key outputs.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .models import Assumptions, Campaign, Mission


class ScenarioError(ValueError):
    pass


def load_seed(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as fh:
        return json.load(fh)


def _apply_override(tree: dict, dotted: str, value) -> None:
    parts = dotted.split(".")
    node = tree
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


class ScenarioManager:
    def __init__(self, seed: dict):
        self.seed = seed

    @classmethod
    def load(cls, path: str | Path) -> "ScenarioManager":
        return cls(load_seed(path))

    def names(self) -> list[str]:
        return ["baseline"] + list(self.seed.get("scenarios", {}))

    def resolve(self, name: str = "baseline", _seen: Optional[set] = None) -> Assumptions:
        if name == "baseline":
            return Assumptions(self.seed["baseline"], "baseline")
        scenarios = self.seed.get("scenarios", {})
        if name not in scenarios:
            raise ScenarioError(f"Unknown scenario '{name}' (have: {', '.join(self.names())})")
        _seen = _seen or set()
        if name in _seen:
            raise ScenarioError(f"Scenario inheritance cycle at '{name}'")
        _seen.add(name)
        spec = scenarios[name]
        base = self.resolve(spec.get("inherits", "baseline"), _seen)
        tree = base.as_dict()
        for dotted, value in spec.get("overrides", {}).items():
            if dotted.startswith("_"):
                continue
            _apply_override(tree, dotted, value)
        return Assumptions(tree, name)

    # -- extra config carried in the seed file ---------------------------

    def window_schedule(self) -> list[dict]:
        return [w for w in self.seed.get("windows", {}).get("schedule", [])]

    def crewed_requires(self) -> list[str]:
        return list(self.seed.get("capability_gates", {}).get("crewed_requires", []))

    def capability_unlocks(self) -> dict:
        return {k: v for k, v in self.seed.get("capability_gates", {})
                .get("capability_unlocks", {}).items() if not k.startswith("_")}


@dataclass(frozen=True)
class DiffRow:
    metric: str
    a: object
    b: object

    @property
    def changed(self) -> bool:
        return self.a != self.b


@dataclass(frozen=True)
class ComparisonResult:
    scenario_a: str
    scenario_b: str
    rows: tuple[DiffRow, ...]

    def changed(self) -> tuple[DiffRow, ...]:
        return tuple(r for r in self.rows if r.changed)


def compare(
    manager: ScenarioManager,
    catalog,
    name_a: str,
    name_b: str,
    campaign: Optional[Campaign] = None,
    mission: Optional[Mission] = None,
) -> ComparisonResult:
    """Run the same campaign/mission under two scenarios and diff key outputs."""
    from .budgets import BudgetEngine
    from .campaign import CampaignPlanner
    from .packing import PackingEngine

    rows: list[DiffRow] = []

    def metrics(name: str) -> dict:
        a = manager.resolve(name)
        out: dict = {"power path": a.get("power.power_path"),
                     "tankers per ship": a.get("fleet.tankers_per_ship"),
                     "launch cost tier": a.get("cost.active_launch_cost"),
                     "per-launch cost ($M)": a.per_launch_cost()}
        if campaign is not None:
            planner = CampaignPlanner(catalog, a, manager.capability_unlocks(), manager.crewed_requires())
            result = planner.run(copy.deepcopy(campaign))
            out.update({
                "total launches": result.cumulative["total_launches"],
                "mass delivered (t)": round(result.cumulative["mass_delivered_t"], 1),
                "launch cost ($M)": round(result.cumulative["launch_cost_musd"], 0),
                "cargo cost low ($M)": round(result.cumulative["cargo_cost_low_musd"], 0),
                "cargo cost high ($M)": round(result.cumulative["cargo_cost_high_musd"], 0),
                "first crew window": result.first_crew_window or "blocked",
            })
        elif mission is not None:
            engine = BudgetEngine(catalog, a)
            budget = engine.compute(mission)
            packing = PackingEngine(catalog, a).pack(mission, budget)
            out.update({
                "grand total mass (t)": round(budget.mass.grand_total_t, 1),
                "avg load (kW)": round(budget.loads.avg_kw, 1),
                "ships": packing.ship_count,
                "total launches": packing.launch.total_launches,
                "launch cost ($M)": round(packing.launch.launch_cost_musd, 0),
                "cargo cost ($M)": f"{budget.cost.cargo_low_musd:,.0f}-{budget.cost.cargo_high_musd:,.0f}",
            })
        return out

    ma, mb = metrics(name_a), metrics(name_b)
    for key in ma:
        rows.append(DiffRow(key, ma[key], mb.get(key)))
    return ComparisonResult(name_a, name_b, tuple(rows))
