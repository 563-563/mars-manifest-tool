"""Requirements engine: load the decomposed requirements tree and evaluate
buy-off against a campaign run (inputs/requirements.json).

Every leaf requirement carries a machine-checkable verification criterion
evaluated per window; parents close by rollup. The output is a verification
cross-reference matrix: which requirements each flight window buys off,
which closed early/late vs plan, and which remain open.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from .campaign import CampaignResult, WindowResult
from .catalog import Catalog
from .models import Assumptions
from .packing import PackingEngine


@dataclass(frozen=True)
class Requirement:
    id: str
    statement: str
    level: int
    parent: Optional[str]
    rationale: str
    source: str
    verify: dict          # {} for rollup requirements
    planned_window: Optional[str]

    @property
    def recurring(self) -> bool:
        return bool(self.verify.get("recurring"))

    @property
    def method(self) -> str:
        return self.verify.get("method", "Rollup")


@dataclass(frozen=True)
class Verdict:
    requirement: Requirement
    status: str                       # CLOSED | EARLY | LATE | OPEN | PASS | FAIL
    closed_window: Optional[str]      # one-time reqs
    failed_windows: tuple[str, ...]   # recurring reqs


@dataclass(frozen=True)
class BuyOffMatrix:
    verdicts: tuple[Verdict, ...]
    by_window: dict[str, tuple[str, ...]]   # window -> requirement ids bought off there
    open_ids: tuple[str, ...]
    counts: dict[str, int]


def load_requirements(path: str | Path) -> list[Requirement]:
    with Path(path).open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    reqs = []
    for r in doc["requirements"]:
        rid = r["id"]
        level = r.get("level", int(rid[1]) if rid[1].isdigit() else 1)
        reqs.append(Requirement(
            id=rid, statement=r["statement"].strip(), level=level,
            parent=r.get("parent"), rationale=r.get("rationale", ""),
            source=r.get("source", ""), verify=r.get("verify", {}) or {},
            planned_window=r.get("planned_window"),
        ))
    return reqs


class RequirementsEngine:
    def __init__(self, catalog: Catalog, assumptions: Assumptions, unlock_rules: dict):
        self.catalog = catalog
        self.a = assumptions
        self.unlock_rules = unlock_rules
        self.packer = PackingEngine(catalog, assumptions)

    def evaluate(self, requirements: list[Requirement], result: CampaignResult) -> BuyOffMatrix:
        windows = list(result.windows)
        order = {w.window_id: i for i, w in enumerate(windows)}
        verdicts: dict[str, Verdict] = {}

        # leaves first
        for req in requirements:
            if not req.verify:
                continue
            if req.recurring:
                failed = tuple(w.window_id for w in windows
                               if not self._check(req.verify, w, windows))
                verdicts[req.id] = Verdict(req, "FAIL" if failed else "PASS", None, failed)
            else:
                closed = next((w.window_id for w in windows
                               if self._check(req.verify, w, windows)), None)
                if closed is None:
                    status = "OPEN"
                elif req.planned_window is None:
                    status = "CLOSED"
                else:
                    # window ids are date-shaped (YYYY-MM), so string order works
                    # even when the planned window isn't in this campaign
                    pi = order.get(req.planned_window)
                    ci = order[closed]
                    if pi is not None:
                        status = "CLOSED" if ci == pi else ("EARLY" if ci < pi else "LATE")
                    else:
                        status = ("CLOSED" if closed == req.planned_window
                                  else ("EARLY" if closed < req.planned_window else "LATE"))
                verdicts[req.id] = Verdict(req, status, closed, ())

        # rollups (children must all be closed/pass); iterate until stable
        remaining = [r for r in requirements if not r.verify]
        for _ in range(4):
            for req in remaining:
                if req.id in verdicts:
                    continue
                kids = [v for v in verdicts.values() if v.requirement.parent == req.id]
                kid_reqs = [r for r in requirements if r.parent == req.id]
                if len(kids) < len(kid_reqs):
                    continue
                if any(v.status in ("OPEN", "FAIL") for v in kids):
                    verdicts[req.id] = Verdict(req, "OPEN", None, ())
                else:
                    one_time = [v.closed_window for v in kids if v.closed_window]
                    closed = max(one_time, key=lambda wid: order[wid]) if one_time else None
                    verdicts[req.id] = Verdict(req, "CLOSED", closed, ())

        ordered = [verdicts[r.id] for r in requirements if r.id in verdicts]
        by_window: dict[str, list[str]] = {w.window_id: [] for w in windows}
        for v in ordered:
            if v.closed_window and v.requirement.verify:
                by_window[v.closed_window].append(v.requirement.id)
        counts: dict[str, int] = {}
        for v in ordered:
            counts[v.status] = counts.get(v.status, 0) + 1
        return BuyOffMatrix(
            verdicts=tuple(ordered),
            by_window={k: tuple(v) for k, v in by_window.items()},
            open_ids=tuple(v.requirement.id for v in ordered if v.status in ("OPEN", "FAIL")),
            counts=counts,
        )

    # ------------------------------------------------------------------

    def _check(self, verify: dict, w: WindowResult, windows: list[WindowResult]) -> bool:
        kind = verify["kind"]
        if kind == "inspection":
            # Narrative requirement signed off (or not) by human review, not modeled
            # by the engine. `met: true` closes it (window-agnostic); `met: false`
            # keeps it OPEN — the honest state of a not-yet-designed capability.
            return bool(verify.get("met", False))
        if kind == "precondition":
            # Earth-side readiness flag from the active scenario; window-agnostic
            return bool(self.a.get(f"transport_readiness.{verify['flag']}", True))
        if kind == "capability":
            return verify["flag"] in w.capabilities_after
        if kind == "min_qty":
            inv = {cid: q for cid, q, _ in w.surface_inventory}
            comps = verify["component"]
            if isinstance(comps, str):
                comps = [comps]
            # a list means any mix of the named components counts toward qty
            return sum(inv.get(c, 0) for c in comps) >= verify["qty"]
        if kind == "min_installed_kwe":
            return w.installed_generation_kwe >= verify["kwe"]
        if kind == "min_propellant_t":
            return w.propellant_cumulative_t >= verify["tonnes"]
        if kind == "min_landings":
            idx = windows.index(w)
            return sum(x.ships for x in windows[: idx + 1]) >= verify["n"]
        if kind == "isru_rate":
            return w.isru_rate_kg_hr >= verify["kg_hr"]
        if kind == "power_covers_load":
            return w.power_derate >= 1.0
        if kind == "fits_fleet":
            cap = self.a.get("fleet.payload_mass_per_ship_t")
            margin = verify.get("margin", 0.0)
            return w.mass_delivered_t <= w.ships * cap * (1.0 - margin)
        if kind == "loss_tolerant":
            watched = set(verify.get("capabilities", []))
            idx = windows.index(w)
            base_q = ({cid: q for cid, q, _ in windows[idx - 1].surface_inventory}
                      if idx else {})
            base_landings = sum(x.ships for x in windows[:idx])
            for outcome in w.missions:
                if outcome.blocked:
                    continue
                lt = self.packer.loss_tolerance(
                    outcome.packing, self.unlock_rules,
                    base_quantities=base_q, base_landings=base_landings)
                if watched & set(lt.capabilities_at_risk):
                    return False
            return True
        raise ValueError(f"Unknown verification kind '{kind}'")
