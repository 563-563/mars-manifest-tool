"""Systems-lifecycle analysis over a campaign: risk buy-down timing and
idle-hardware accounting (config: `lifecycle` in data/assumptions_seed.json).

Two questions, asked of every flight manifest:
  1. Are we retiring the most program risk as early as possible? Each
     capability gate carries a severity weight (derived from the deep-dive's
     six hard problems); the risk curve is cumulative weight retired per window.
  2. Are we landing hardware that sits unused for years? Crew-era components
     delivered more than one window before first crew are idle mass — except
     designated demonstration articles (the 1000-day ECLSS testbed), whose
     early delivery IS the risk buy-down.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .campaign import CampaignResult
from .catalog import Catalog
from .models import Assumptions


@dataclass(frozen=True)
class RiskPoint:
    window_id: str
    retired: tuple[str, ...]           # gates newly retired this window
    weight_retired: float              # their summed weight
    cumulative_fraction: float         # of total weighted risk


@dataclass(frozen=True)
class IdleItem:
    component_id: str
    delivered_window: str
    qty: float
    mass_t: float
    idle_synods: int                   # windows beyond the 1-window verification margin
    tonne_years: float
    demo_exempt_qty: float             # units excused as demonstration articles
    shelf_life_flag: bool


@dataclass(frozen=True)
class LifecycleReport:
    risk_curve: tuple[RiskPoint, ...]
    risk_retired_first_window: float   # fraction after window 0
    unretired_gates: tuple[str, ...]
    idle_items: tuple[IdleItem, ...]
    idle_tonne_years: float
    crew_window: Optional[str]
    findings: tuple[str, ...]


YEARS_PER_SYNOD = 26 / 12.0


def analyze(result: CampaignResult, catalog: Catalog, assumptions: Assumptions) -> LifecycleReport:
    a = assumptions
    weights: dict = a.get("lifecycle.risk_weights", {})
    crew_era = set(a.get("lifecycle.crew_era_components", []))
    demo_exempt: dict = a.get("lifecycle.demo_exempt_units", {})
    shelf_life = set(a.get("lifecycle.shelf_life_components", []))
    total_weight = sum(weights.values()) or 1.0
    findings: list[str] = []

    # -- risk buy-down curve ------------------------------------------------
    curve: list[RiskPoint] = []
    cum = 0.0
    retired_all: set[str] = set()
    for w in result.windows:
        newly = tuple(g for g in w.new_capabilities if g in weights)
        wt = sum(weights[g] for g in newly)
        cum += wt
        retired_all.update(newly)
        curve.append(RiskPoint(w.window_id, newly, wt, cum / total_weight))
    unretired = tuple(sorted(set(weights) - retired_all))
    first_frac = curve[0].cumulative_fraction if curve else 0.0

    crew_idx = None
    crew_window = None
    for i, w in enumerate(result.windows):
        if any(m.crewed and not m.blocked for m in w.missions):
            crew_idx, crew_window = i, w.window_id
            break

    # -- idle-hardware accounting --------------------------------------------
    idle_items: list[IdleItem] = []
    idle_total = 0.0
    exempt_budget = dict(demo_exempt)  # first N units across the campaign
    if crew_idx is not None:
        for i, w in enumerate(result.windows[: crew_idx + 1]):
            # deliveries this window = inventory delta
            prev = result.windows[i - 1].surface_inventory if i else ()
            prev_q = {cid: q for cid, q, _ in prev}
            for cid, q, _ in w.surface_inventory:
                dq = q - prev_q.get(cid, 0.0)
                if dq <= 0 or cid not in crew_era:
                    continue
                exempt = min(dq, exempt_budget.get(cid, 0))
                exempt_budget[cid] = exempt_budget.get(cid, 0) - exempt
                # one window before crew is verification margin, not idle
                idle_synods = max(0, (crew_idx - i) - 1)
                comp = catalog.get(cid)
                billable = dq - exempt
                ty = billable * comp.unit_mass_t * idle_synods * YEARS_PER_SYNOD
                shelf = cid in shelf_life and (crew_idx - i) > 1
                idle_items.append(IdleItem(
                    component_id=cid, delivered_window=w.window_id, qty=dq,
                    mass_t=dq * comp.unit_mass_t, idle_synods=idle_synods,
                    tonne_years=ty, demo_exempt_qty=exempt, shelf_life_flag=shelf,
                ))
                idle_total += ty

    # -- findings --------------------------------------------------------------
    if first_frac > 0:
        findings.append(
            f"Window 0 retires {first_frac:.0%} of weighted program risk — the EDL, "
            f"power, water, autonomy and comms unknowns die on first landing."
        )
    for pt, w in zip(curve, result.windows):
        for gate in pt.retired:
            if weights.get(gate, 0) >= 15 and w.window_id != result.windows[0].window_id:
                findings.append(
                    f"{gate} (weight {weights[gate]:.0f}) retires at {w.window_id} — "
                    f"schedule-critical; a slip here slips first crew."
                )
    for item in idle_items:
        if item.tonne_years > 0:
            findings.append(
                f"{item.component_id} x{item.qty:g} delivered {item.delivered_window} sits "
                f"{item.idle_synods} synod(s) beyond verification margin "
                f"({item.tonne_years:,.0f} t-years idle) — defer toward the window before crew."
            )
        if item.shelf_life_flag:
            findings.append(
                f"{item.component_id} delivered {item.delivered_window} ages "
                f"{(crew_idx - result.windows.index(next(w for w in result.windows if w.window_id == item.delivered_window))) * YEARS_PER_SYNOD:.1f} "
                f"years before crew consumes it — shelf-life risk."
            )
        if item.demo_exempt_qty:
            findings.append(
                f"{item.component_id}: {item.demo_exempt_qty:g} unit(s) at "
                f"{item.delivered_window} counted as demonstration article(s) — early "
                f"delivery here is deliberate risk buy-down, not idle mass."
            )
    if unretired:
        findings.append("Never retired in this campaign: " + ", ".join(unretired))
    if idle_total == 0 and crew_idx is not None:
        findings.append("No idle crew-era mass beyond verification margin — manifests are lean.")

    return LifecycleReport(
        risk_curve=tuple(curve),
        risk_retired_first_window=first_frac,
        unretired_gates=unretired,
        idle_items=tuple(idle_items),
        idle_tonne_years=idle_total,
        crew_window=crew_window,
        findings=tuple(findings),
    )
