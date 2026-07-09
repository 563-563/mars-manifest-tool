"""CampaignPlanner: sequence windows, carry surface state forward, gate
capabilities (HANDOFF.md §5.3).

Crewed missions are checked against the capability flags unlocked by
*previous* windows — the crew must launch toward a site that is already
powered, habitable, and able to make return propellant. The rule set is
data-driven (capability_gates in data/assumptions_seed.json), not hard-coded.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .budgets import BudgetEngine, BudgetResult
from .catalog import Catalog
from .models import Assumptions, Campaign, Mission, Window
from .packing import PackingEngine, PackingResult


@dataclass
class SurfaceState:
    delivered: dict[str, float] = field(default_factory=dict)
    installed_generation_kwe: float = 0.0
    installed_storage_kwh: float = 0.0
    landings: int = 0
    capabilities: set[str] = field(default_factory=set)

    def add_delivery(self, component_id: str, qty: float) -> None:
        self.delivered[component_id] = self.delivered.get(component_id, 0.0) + qty


@dataclass(frozen=True)
class MissionOutcome:
    mission_id: str
    crewed: bool
    blocked: bool
    missing_capabilities: tuple[str, ...]
    budget: BudgetResult
    packing: PackingResult


@dataclass(frozen=True)
class WindowResult:
    window_id: str
    synod_index: int
    objective: str
    missions: tuple[MissionOutcome, ...]
    mass_delivered_t: float
    ships: int
    total_launches: int
    launch_cost_musd: float
    cargo_cost_low_musd: float
    cargo_cost_high_musd: float
    new_capabilities: tuple[str, ...]
    capabilities_after: tuple[str, ...]
    installed_generation_kwe: float
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class CampaignResult:
    campaign_id: str
    windows: tuple[WindowResult, ...]
    cumulative: dict
    first_crew_window: Optional[str]
    violations: tuple[str, ...]


class CampaignPlanner:
    def __init__(
        self,
        catalog: Catalog,
        assumptions: Assumptions,
        capability_unlocks: dict,
        crewed_requires: list[str],
    ):
        self.catalog = catalog
        self.a = assumptions
        self.unlocks = capability_unlocks
        self.crewed_requires = list(crewed_requires)
        self.budget_engine = BudgetEngine(catalog, assumptions)
        self.packing_engine = PackingEngine(catalog, assumptions)

    def run(self, campaign: Campaign) -> CampaignResult:
        state = SurfaceState()
        window_results: list[WindowResult] = []
        violations: list[str] = []
        first_crew: Optional[str] = None
        cumulative = {
            "mass_delivered_t": 0.0, "ships": 0, "total_launches": 0,
            "launch_cost_musd": 0.0, "cargo_cost_low_musd": 0.0, "cargo_cost_high_musd": 0.0,
        }

        for window in sorted(campaign.windows, key=lambda w: w.synod_index):
            warnings: list[str] = []
            outcomes: list[MissionOutcome] = []
            w_mass = w_ships = w_launches = 0.0
            w_launch_cost = w_cargo_low = w_cargo_high = 0.0

            for mission in window.missions:
                missing: tuple[str, ...] = ()
                blocked = False
                if mission.crewed:
                    missing = tuple(c for c in self.crewed_requires if c not in state.capabilities)
                    if missing:
                        blocked = True
                        violations.append(
                            f"{window.id}/{mission.id}: crewed mission blocked -- "
                            f"missing capabilities: {', '.join(missing)}"
                        )
                budget = self.budget_engine.compute(mission)
                packing = self.packing_engine.pack(mission, budget)
                outcomes.append(MissionOutcome(mission.id, mission.crewed, blocked, missing, budget, packing))
                warnings.extend(budget.warnings)
                warnings.extend(packing.warnings)
                if blocked:
                    continue  # blocked missions don't fly: no deliveries, no launches

                if mission.crewed and first_crew is None:
                    first_crew = window.id
                w_mass += budget.mass.grand_total_t
                w_ships += packing.ship_count
                w_launches += packing.launch.total_launches
                w_launch_cost += packing.launch.launch_cost_musd
                w_cargo_low += budget.cost.cargo_low_musd
                w_cargo_high += budget.cost.cargo_high_musd
                self._deliver(mission, budget, state)
                state.landings += packing.ship_count

            new_caps = self._evaluate_unlocks(state)
            state.capabilities.update(new_caps)
            # Advisories run against post-window state: everything in a window
            # lands together, so same-window deliveries/unlocks satisfy deps.
            for mission in window.missions:
                warnings.extend(self._advisories(mission, window, state))

            cumulative["mass_delivered_t"] += w_mass
            cumulative["ships"] += int(w_ships)
            cumulative["total_launches"] += int(w_launches)
            cumulative["launch_cost_musd"] += w_launch_cost
            cumulative["cargo_cost_low_musd"] += w_cargo_low
            cumulative["cargo_cost_high_musd"] += w_cargo_high

            window_results.append(WindowResult(
                window_id=window.id,
                synod_index=window.synod_index,
                objective=window.objective,
                missions=tuple(outcomes),
                mass_delivered_t=w_mass,
                ships=int(w_ships),
                total_launches=int(w_launches),
                launch_cost_musd=w_launch_cost,
                cargo_cost_low_musd=w_cargo_low,
                cargo_cost_high_musd=w_cargo_high,
                new_capabilities=tuple(sorted(new_caps)),
                capabilities_after=tuple(sorted(state.capabilities)),
                installed_generation_kwe=state.installed_generation_kwe,
                warnings=tuple(warnings),
            ))

        return CampaignResult(
            campaign_id=campaign.id,
            windows=tuple(window_results),
            cumulative=cumulative,
            first_crew_window=first_crew,
            violations=tuple(violations),
        )

    # ------------------------------------------------------------------

    def _deliver(self, mission: Mission, budget: BudgetResult, state: SurfaceState) -> None:
        for item in mission.manifest:
            state.add_delivery(item.component_id, item.qty)
        hw = budget.power_hardware
        if hw.generator_units > 0:
            state.add_delivery(hw.generator_component_id, hw.generator_units)
        if hw.storage_units > 0:
            state.add_delivery(hw.storage_component_id, hw.storage_units)
        state.installed_generation_kwe += hw.installed_kwe
        state.installed_storage_kwh += hw.installed_storage_kwh

    def _advisories(self, mission: Mission, window: Window, state: SurfaceState) -> list[str]:
        """Non-blocking checks: earliest_window and depends_on (HANDOFF.md §4.1)."""
        notes = []
        same_window_ids = {i.component_id for i in mission.manifest}
        for item in mission.manifest:
            comp = self.catalog.get(item.component_id)
            if comp.earliest_window and comp.earliest_window > window.year:
                notes.append(
                    f"{window.id}/{mission.id}: {comp.id} flies before its earliest "
                    f"window ({comp.earliest_window}) -- advisory only"
                )
            for dep in comp.depends_on:
                satisfied = (
                    dep in state.capabilities
                    or dep in state.delivered
                    or dep in same_window_ids
                )
                if not satisfied:
                    notes.append(
                        f"{window.id}/{mission.id}: {comp.id} depends on '{dep}' "
                        f"which is neither delivered nor unlocked"
                    )
        return notes

    def _evaluate_unlocks(self, state: SurfaceState) -> set[str]:
        """Data-driven capability rules. Supported conditions (ANDed):
        all_of / any_of (component ids delivered), min_installed_kwe, min_landings."""
        unlocked: set[str] = set()
        for flag, rule in self.unlocks.items():
            if flag in state.capabilities:
                continue
            ok = True
            if "all_of" in rule:
                ok = ok and all(state.delivered.get(cid, 0) >= 1 for cid in rule["all_of"])
            if "any_of" in rule:
                ok = ok and any(state.delivered.get(cid, 0) >= 1 for cid in rule["any_of"])
            if "min_installed_kwe" in rule:
                ok = ok and state.installed_generation_kwe >= rule["min_installed_kwe"]
            if "min_landings" in rule:
                ok = ok and state.landings >= rule["min_landings"]
            if ok:
                unlocked.add(flag)
        return unlocked
