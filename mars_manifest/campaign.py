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
from .catalog import CONSUMABLES_GROUP, Catalog
from .city import YEARS_PER_SYNOD, closure_stage, import_rate_t_per_person_year
from .isru import IsruEngine
from .models import Assumptions, Campaign, Mission, Window
from .packing import PackingEngine, PackingResult


@dataclass
class SurfaceState:
    delivered: dict[str, float] = field(default_factory=dict)
    installed_generation_kwe: float = 0.0
    installed_storage_kwh: float = 0.0
    landings: int = 0
    propellant_produced_t: float = 0.0
    population: int = 0
    capabilities: set[str] = field(default_factory=set)
    first_delivery_synod: dict[str, int] = field(default_factory=dict)

    def add_delivery(self, component_id: str, qty: float, synod_index: int = 0) -> None:
        self.delivered[component_id] = self.delivered.get(component_id, 0.0) + qty
        self.first_delivery_synod.setdefault(component_id, synod_index)


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
    # ISRU production during the synod following this window's deliveries
    isru_rate_kg_hr: float
    isru_bottleneck: str
    propellant_produced_t: float       # this window's production
    propellant_cumulative_t: float
    power_derate: float                # 1.0 = installed generation covers the load
    # what's physically on the surface after this window (cumulative)
    surface_hardware_t: float                                  # catalog hardware only
    surface_by_group: dict[str, float] = field(default_factory=dict)
    surface_inventory: tuple[tuple[str, float, float], ...] = ()  # (id, qty, mass_t)
    surface_avg_load_kw: float = 0.0
    installed_storage_kwh: float = 0.0
    population: int = 0                # residents on the surface after this window
    # import ledger (B1): recurring per-resident imports vs what this window
    # actually delivered as consumables; rate keyed to closure stage at the
    # window's START (imports are planned against known industrial state)
    closure_stage: str = "none"
    import_rate_t_py: float = 0.0
    import_required_t: float = 0.0
    import_delivered_t: float = 0.0
    warnings: tuple[str, ...] = ()


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
        city: Optional[dict] = None,
        min_fleet_growth: Optional[float] = None,
    ):
        self.catalog = catalog
        self.a = assumptions
        self.unlocks = capability_unlocks
        self.crewed_requires = list(crewed_requires)
        self.budget_engine = BudgetEngine(catalog, assumptions)
        self.packing_engine = PackingEngine(catalog, assumptions)
        self.isru_engine = IsruEngine(catalog, assumptions)
        self.city = city
        self.min_fleet_growth = min_fleet_growth

    def run(self, campaign: Campaign) -> CampaignResult:
        state = SurfaceState()
        window_results: list[WindowResult] = []
        violations: list[str] = []
        first_crew: Optional[str] = None
        cumulative = {
            "mass_delivered_t": 0.0, "ships": 0, "total_launches": 0,
            "launch_cost_musd": 0.0, "cargo_cost_low_musd": 0.0, "cargo_cost_high_musd": 0.0,
        }

        prev_ships = 0
        for window in sorted(campaign.windows, key=lambda w: w.synod_index):
            warnings: list[str] = []
            outcomes: list[MissionOutcome] = []
            w_mass = w_ships = w_launches = 0.0
            w_launch_cost = w_cargo_low = w_cargo_high = 0.0
            w_consumables_t = 0.0
            pop_before = state.population
            caps_before = frozenset(state.capabilities)
            delivered_before = dict(state.delivered)

            for mission in window.missions:
                needed = list(mission.requires)
                # anyone aboard means crew gates apply — settlers can't sneak
                # past the gating by leaving crewed: false
                if mission.crewed or mission.settlers > 0:
                    needed += [c for c in self.crewed_requires if c not in needed]
                missing = tuple(c for c in needed if c not in state.capabilities)
                blocked = bool(missing)
                if blocked:
                    kind = "crewed mission" if mission.crewed else "mission"
                    violations.append(
                        f"{window.id}/{mission.id}: {kind} blocked -- "
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
                self._deliver(mission, budget, state, window.synod_index)
                state.landings += packing.ship_count
                state.population += mission.settlers
                w_consumables_t += sum(
                    self.catalog.get(i.component_id).unit_mass_t * i.qty
                    for i in mission.manifest
                    if self.catalog.get(i.component_id).group == CONSUMABLES_GROUP)

            # ISRU production over the synod following this window's landings,
            # derated if installed generation can't carry the delivered load.
            # Commissioning ramp (C3): capacity added THIS window spends its
            # first synod ramping up, so only newly-delivered throughput is
            # discounted; hardware from earlier windows runs at nameplate.
            isru = self.isru_engine.assess_quantities(state.delivered)
            derate = self._power_derate(state)
            commission = self.a.get("isru.commissioning_factor", 1.0)
            if commission < 1.0 and delivered_before:
                prev_isru = self.isru_engine.assess_quantities(delivered_before)
                new_capacity = max(0.0, isru.tonnes_per_window - prev_isru.tonnes_per_window)
                effective_t = prev_isru.tonnes_per_window + commission * new_capacity
            else:
                # no prior plant (first synod of production) ramps in full
                effective_t = commission * isru.tonnes_per_window
            produced_t = effective_t * derate
            state.propellant_produced_t += produced_t
            if derate < 1.0 and produced_t > 0:
                warnings.append(
                    f"{window.id}: installed power covers {derate:.0%} of the delivered "
                    f"load — ISRU production derated accordingly"
                )

            new_caps = self._evaluate_unlocks(state, window.synod_index)
            state.capabilities.update(new_caps)
            # Advisories run against post-window state: everything in a window
            # lands together, so same-window deliveries/unlocks satisfy deps.
            for mission in window.missions:
                warnings.extend(self._advisories(mission, window, state))

            # import ledger (B1) — rate keyed to closure state entering the window
            stage = closure_stage(caps_before)
            rate = (import_rate_t_per_person_year(self.city, caps_before)
                    if self.city else 0.0)
            import_required = pop_before * rate * YEARS_PER_SYNOD
            if self.city and pop_before > 0 and w_consumables_t < import_required:
                warnings.append(
                    f"{window.id}: recurring-import deficit — {pop_before:,} residents at "
                    f"{rate:g} t/person/yr ({stage}) need {import_required:,.0f} t this synod; "
                    f"manifests deliver {w_consumables_t:,.0f} t of consumables"
                )

            # fleet growth rule (B2): the TOTAL landed fleet should at least
            # double each synod (New Space 2022, verbatim: "total number of
            # landed vehicles to double at a minimum with each consecutive
            # opportunity" — cumulative, not per-window)
            cum_after = cumulative["ships"] + int(w_ships)
            if (self.min_fleet_growth and prev_ships > 0
                    and cum_after < prev_ships * self.min_fleet_growth):
                warnings.append(
                    f"{window.id}: cumulative landed fleet below the "
                    f">={self.min_fleet_growth:g}x/synod recommendation "
                    f"({cum_after} total after {prev_ships})"
                )
            prev_ships = cum_after

            # surface snapshot: what is physically on Mars after this window
            inventory = []
            by_group: dict[str, float] = {}
            load_kw = 0.0
            for cid, qty in sorted(state.delivered.items()):
                if cid not in self.catalog:
                    continue
                comp = self.catalog.get(cid)
                mass = comp.unit_mass_t * qty
                inventory.append((cid, qty, mass))
                by_group[comp.group] = by_group.get(comp.group, 0.0) + mass
                if comp.power_role == "consumer":
                    load_kw += comp.peak_power_kw * comp.duty_cycle * qty

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
                isru_rate_kg_hr=isru.propellant_rate_kg_hr,
                isru_bottleneck=isru.bottleneck,
                propellant_produced_t=produced_t,
                propellant_cumulative_t=state.propellant_produced_t,
                power_derate=derate,
                surface_hardware_t=sum(m for _, _, m in inventory),
                surface_by_group=by_group,
                surface_inventory=tuple(inventory),
                surface_avg_load_kw=load_kw,
                installed_storage_kwh=state.installed_storage_kwh,
                population=state.population,
                closure_stage=stage,
                import_rate_t_py=rate,
                import_required_t=import_required,
                import_delivered_t=w_consumables_t,
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

    def _deliver(self, mission: Mission, budget: BudgetResult, state: SurfaceState,
                 synod_index: int = 0) -> None:
        for item in mission.manifest:
            state.add_delivery(item.component_id, item.qty, synod_index)
        hw = budget.power_hardware
        if hw.generator_units > 0:
            state.add_delivery(hw.generator_component_id, hw.generator_units, synod_index)
        if hw.storage_units > 0:
            state.add_delivery(hw.storage_component_id, hw.storage_units, synod_index)
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

    def _power_derate(self, state: SurfaceState) -> float:
        """Fraction of the delivered average load the installed generation covers."""
        load_kw = 0.0
        for cid, qty in state.delivered.items():
            if cid in self.catalog:
                comp = self.catalog.get(cid)
                if comp.power_role == "consumer":
                    load_kw += comp.peak_power_kw * comp.duty_cycle * qty
        if load_kw <= 0:
            return 1.0
        return min(1.0, state.installed_generation_kwe / load_kw)

    def _evaluate_unlocks(self, state: SurfaceState, synod_index: int = 0) -> set[str]:
        """Data-driven capability rules. Supported conditions (ANDed):
        all_of / any_of (component ids delivered), min_installed_kwe,
        min_landings, min_propellant_t (cumulative ISRU production),
        min_sols_on_surface (demonstration clock, e.g. the 1000-day ECLSS proof)."""
        sols_per_synod = self.a.get("lifecycle.sols_per_synod", 760)
        production_sols = self.a.get("isru.production_sols_per_synod", 600)

        def conditions_met(rule: dict) -> bool:
            if "any_path" in rule:  # alternative condition sets, OR'd
                return any(conditions_met(path) for path in rule["any_path"])
            ok = True
            if "all_of" in rule:
                ok = ok and all(state.delivered.get(cid, 0) >= 1 for cid in rule["all_of"])
            if "any_of" in rule:
                ok = ok and any(state.delivered.get(cid, 0) >= 1 for cid in rule["any_of"])
            if "min_installed_kwe" in rule:
                ok = ok and state.installed_generation_kwe >= rule["min_installed_kwe"]
            if "min_landings" in rule:
                ok = ok and state.landings >= rule["min_landings"]
            if "min_propellant_t" in rule:
                ok = ok and state.propellant_produced_t >= rule["min_propellant_t"]
            if "min_population" in rule:
                ok = ok and state.population >= rule["min_population"]
            if "min_sols_on_surface" in rule:
                for cid, need_sols in rule["min_sols_on_surface"].items():
                    if cid not in state.first_delivery_synod:
                        return False
                    elapsed = ((synod_index - state.first_delivery_synod[cid]) * sols_per_synod
                               + production_sols)
                    ok = ok and elapsed >= need_sols
            return ok

        unlocked: set[str] = set()
        for flag, rule in self.unlocks.items():
            if flag not in state.capabilities and conditions_met(rule):
                unlocked.add(flag)
        return unlocked
