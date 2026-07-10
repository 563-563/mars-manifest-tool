"""PackingEngine: bin-pack components into ships + tanker/launch math
(spec origin: HANDOFF.md §5.2).

Greedy first-fit-decreasing over both mass and volume; explicit ship
assignments in the manifest are respected. The packer is deliberately a
standalone strategy function so it can be swapped later.

Launch math (the load-bearing insight — refueling multiplies launches):
    total_launches = ships × (1 + tankers_per_ship)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from .budgets import BudgetResult
from .catalog import Catalog
from .models import Assumptions, Mission


@dataclass
class PackItem:
    component_id: str
    name: str
    qty: float
    mass_t: float
    volume_m3: float
    ship: Optional[int] = None  # requested assignment


@dataclass
class PackedShip:
    index: int
    items: list[PackItem] = field(default_factory=list)

    @property
    def mass_t(self) -> float:
        return sum(i.mass_t for i in self.items)

    @property
    def volume_m3(self) -> float:
        return sum(i.volume_m3 for i in self.items)


@dataclass(frozen=True)
class ShipReport:
    index: int
    mass_t: float
    volume_m3: float
    mass_utilisation: float
    volume_utilisation: float
    binding_constraint: str  # "mass" | "volume"
    items: tuple[tuple[str, float], ...]  # (component_id, qty)
    manifest_detail: tuple[tuple[str, float, float, float], ...] = ()  # (id, qty, mass_t, vol_m3)


@dataclass(frozen=True)
class LaunchMath:
    cargo_ship_launches: int
    tankers_per_ship: int
    tanker_launches: int
    total_launches: int
    launch_cost_tier: str
    per_launch_cost_musd: float        # tier rate (used for both legs unless split)
    cargo_ship_rate_musd: float        # cargo ships are expended on Mars
    tanker_rate_musd: float            # tankers are recovered and reused
    launch_cost_musd: float

    @property
    def split_rates(self) -> bool:
        return self.cargo_ship_rate_musd != self.tanker_rate_musd


@dataclass(frozen=True)
class LossTolerance:
    tolerant: bool  # no single ship loss kills any unlocked capability
    vulnerable_ships: tuple[tuple[int, tuple[str, ...]], ...]  # (ship, capabilities lost)
    capabilities_at_risk: tuple[str, ...]


@dataclass(frozen=True)
class PackingResult:
    mission_id: str
    ships: tuple[ShipReport, ...]
    ship_count: int
    launch: LaunchMath
    warnings: tuple[str, ...]
    policy: str = "explicit"
    # gate-bearing components carried on exactly one ship: losing that one
    # ship on EDL loses the capability (component_id, readiness_gate)
    single_points: tuple[tuple[str, str], ...] = ()


class PackingEngine:
    def __init__(self, catalog: Catalog, assumptions: Assumptions):
        self.catalog = catalog
        self.a = assumptions

    def pack(
        self,
        mission: Mission,
        budget: Optional[BudgetResult] = None,
        tankers_per_ship: Optional[int] = None,
        launch_cost_tier: Optional[str] = None,
        policy: Optional[str] = None,
        include_spares: Optional[bool] = None,
    ) -> PackingResult:
        a = self.a
        mass_cap = a.get("fleet.payload_mass_per_ship_t")
        vol_cap = a.get("fleet.payload_volume_per_ship_m3")
        policy = policy or mission.packing_policy
        if policy not in ("explicit", "balanced"):
            raise ValueError(f"Unknown packing policy '{policy}'")
        include_spares = mission.pack_spares if include_spares is None else include_spares
        warnings: list[str] = []

        items = self._expand_items(mission, budget, split_storage=(policy == "balanced"))
        if include_spares:
            if budget is None:
                warnings.append("pack_spares requested but no budget supplied — spares not packed")
            else:
                items += self._spares_items(budget)

        if policy == "balanced":
            ships = self._pack_balanced(items, mission, mass_cap, vol_cap, warnings)
        else:
            ships = self._pack_explicit(items, mission, mass_cap, vol_cap, warnings)

        reports = []
        for idx in sorted(ships):
            ship = ships[idx]
            mass_util = ship.mass_t / mass_cap
            vol_util = ship.volume_m3 / vol_cap
            rollup = self._rollup(ship.items)
            reports.append(ShipReport(
                index=idx,
                mass_t=ship.mass_t,
                volume_m3=ship.volume_m3,
                mass_utilisation=mass_util,
                volume_utilisation=vol_util,
                binding_constraint="mass" if mass_util >= vol_util else "volume",
                items=tuple((cid, v[0]) for cid, v in sorted(rollup.items())),
                manifest_detail=tuple((cid, v[0], v[1], v[2]) for cid, v in sorted(rollup.items())),
            ))

        ship_count = len(ships)
        launch = self.launch_math(ship_count, tankers_per_ship, launch_cost_tier)
        return PackingResult(
            mission_id=mission.id,
            ships=tuple(reports),
            ship_count=ship_count,
            launch=launch,
            warnings=tuple(warnings),
            policy=policy,
            single_points=self._single_points(ships),
        )

    # -- packing strategies ------------------------------------------------

    def _pack_explicit(self, items, mission, mass_cap, vol_cap, warnings):
        """Honor ship pins; first-fit-decreasing for the rest."""
        ships: dict[int, PackedShip] = {}
        if mission.ships:
            for i in range(1, mission.ships + 1):
                ships[i] = PackedShip(i)
        auto: list[PackItem] = []
        for item in items:
            if item.ship is not None:
                ships.setdefault(item.ship, PackedShip(item.ship)).items.append(item)
            else:
                auto.append(item)
        for idx, ship in sorted(ships.items()):
            if ship.mass_t > mass_cap or ship.volume_m3 > vol_cap:
                warnings.append(
                    f"Ship {idx} over capacity as explicitly assigned: "
                    f"{ship.mass_t:,.1f} t / {ship.volume_m3:,.0f} m3"
                )
        auto.sort(key=lambda i: max(i.mass_t / mass_cap, i.volume_m3 / vol_cap), reverse=True)
        for item in auto:
            placed = False
            for idx in sorted(ships):
                ship = ships[idx]
                if ship.mass_t + item.mass_t <= mass_cap and ship.volume_m3 + item.volume_m3 <= vol_cap:
                    ship.items.append(item)
                    placed = True
                    break
            if not placed:
                if item.mass_t > mass_cap or item.volume_m3 > vol_cap:
                    warnings.append(
                        f"{item.component_id}: single unit exceeds ship capacity "
                        f"({item.mass_t:,.1f} t / {item.volume_m3:,.0f} m3); placed on its own ship"
                    )
                new_idx = max(ships) + 1 if ships else 1
                ships[new_idx] = PackedShip(new_idx, [item])
                if mission.ships and new_idx > mission.ships:
                    warnings.append(f"Batch grew beyond declared {mission.ships} ships (ship {new_idx})")
        return ships

    def _pack_balanced(self, items, mission, mass_cap, vol_cap, warnings):
        """Load-balance across the declared fleet with redundancy anti-affinity:
        units of the same component prefer ships that don't already carry one,
        so no single EDL loss takes out a whole capability class. Ship pins are
        ignored under this policy."""
        n = mission.ships or max(1, math.ceil(
            sum(i.mass_t for i in items) / mass_cap))
        ships = {i: PackedShip(i) for i in range(1, n + 1)}
        ordered = sorted(items, key=lambda i: max(i.mass_t / mass_cap, i.volume_m3 / vol_cap),
                         reverse=True)

        def load_after(s: PackedShip, item: PackItem) -> float:
            return max((s.mass_t + item.mass_t) / mass_cap,
                       (s.volume_m3 + item.volume_m3) / vol_cap)

        for item in ordered:
            fits = [s for s in ships.values()
                    if s.mass_t + item.mass_t <= mass_cap and s.volume_m3 + item.volume_m3 <= vol_cap]
            if not fits:
                if item.mass_t > mass_cap or item.volume_m3 > vol_cap:
                    warnings.append(
                        f"{item.component_id}: single unit exceeds ship capacity; placed on its own ship")
                idx = max(ships) + 1
                ships[idx] = PackedShip(idx, [item])
                warnings.append(f"Batch grew beyond declared {n} ships (ship {idx})")
                continue
            fresh = [s for s in fits
                     if not any(it.component_id == item.component_id for it in s.items)]
            pool = fresh or fits
            min(pool, key=lambda s: load_after(s, item)).items.append(item)
        return ships

    def _spares_items(self, budget: BudgetResult) -> list[PackItem]:
        """Turn the spares overhead into explicit, packable per-group cargo,
        chunked so the packer can spread it across ships."""
        out: list[PackItem] = []
        spares = budget.mass.spares_by_group
        total = sum(spares.values()) or 1.0
        chunk_t = 5.0
        for group, mass in sorted(spares.items()):
            if mass <= 0:
                continue
            vol = budget.volume.spares_m3 * (mass / total)
            n_chunks = max(1, math.ceil(mass / chunk_t))
            for _ in range(n_chunks):
                out.append(PackItem(f"spares:{group}", f"Spares — {group}",
                                    1, mass / n_chunks, vol / n_chunks))
        return out

    def loss_tolerance(self, packing: PackingResult, unlock_rules: dict,
                       base_quantities: Optional[dict] = None,
                       base_landings: int = 0, n_lost: int = 1) -> "LossTolerance":
        """Which capabilities die if any `n_lost` ships are lost on EDL?

        n_lost=1 is the standard single-fault check; n_lost=2 tests every pair
        (the probabilistic complement lives in edl.py). `vulnerable_ships`
        reports the lost ships as a tuple per failing combination.

        Evaluates the data-driven capability_unlocks rules against the fleet
        minus each ship in turn — the mission-level view of redundancy, as
        opposed to the component-level single_points list. Time-accrued
        conditions (min_propellant_t) are hardware-independent here and are
        skipped; the all_of hardware behind them is still checked.

        base_quantities/base_landings account for hardware already on the
        surface from earlier windows: a lost singleton doesn't cost a
        capability the base already has.
        """
        def quantities(exclude: tuple = ()) -> dict[str, float]:
            out: dict[str, float] = dict(base_quantities or {})
            for s in packing.ships:
                if s.index in exclude:
                    continue
                for cid, qty, _, _ in s.manifest_detail:
                    out[cid] = out.get(cid, 0.0) + qty
            return out

        def satisfied(flag: str, rule: dict, q: dict[str, float], landings: int) -> bool:
            if "any_path" in rule:  # hardware check on each alternative path
                return any(satisfied(flag, path, q, landings) for path in rule["any_path"])
            ok = True
            if "all_of" in rule:
                ok = ok and all(q.get(cid, 0) >= 1 for cid in rule["all_of"])
            if "any_of" in rule:
                ok = ok and any(q.get(cid, 0) >= 1 for cid in rule["any_of"])
            if "min_installed_kwe" in rule:
                kwe = sum(self.catalog.get(cid).generation_kwe * qty
                          for cid, qty in q.items()
                          if cid in self.catalog and self.catalog.get(cid).power_role == "generator")
                ok = ok and kwe >= rule["min_installed_kwe"]
            if "min_landings" in rule:
                ok = ok and landings >= rule["min_landings"]
            return ok

        import itertools
        full = quantities()
        n = len(packing.ships) + base_landings
        baseline_caps = {f for f, r in unlock_rules.items()
                         if satisfied(f, r, full, n)}
        per_ship = []
        for combo in itertools.combinations([s.index for s in packing.ships], n_lost):
            q = quantities(exclude=combo)
            lost = tuple(sorted(f for f in baseline_caps
                                if not satisfied(f, unlock_rules[f], q, n - n_lost)))
            if lost:
                key = combo[0] if n_lost == 1 else combo
                per_ship.append((key, lost))
        return LossTolerance(
            tolerant=not per_ship,
            vulnerable_ships=tuple(per_ship),
            capabilities_at_risk=tuple(sorted({c for _, lost in per_ship for c in lost})),
        )

    def _single_points(self, ships: dict[int, PackedShip]) -> tuple[tuple[str, str], ...]:
        carriers: dict[str, set[int]] = {}
        for idx, ship in ships.items():
            for item in ship.items:
                carriers.setdefault(item.component_id, set()).add(idx)
        out = []
        for cid, on_ships in sorted(carriers.items()):
            if cid.startswith("spares:") or len(on_ships) != 1:
                continue
            if cid in self.catalog:
                gate = self.catalog.get(cid).readiness_gate
                if gate:
                    out.append((cid, gate))
        return tuple(out)

    def launch_math(
        self,
        ship_count: int,
        tankers_per_ship: Optional[int] = None,
        launch_cost_tier: Optional[str] = None,
    ) -> LaunchMath:
        a = self.a
        tankers = tankers_per_ship if tankers_per_ship is not None else a.get("fleet.tankers_per_ship")
        tier = launch_cost_tier or a.get("cost.active_launch_cost")
        per_launch = a.per_launch_cost(tier)
        # Internal-cost refinement: a Mars cargo ship is expended (it stays on
        # the surface) while tankers are recovered and reused, so scenarios may
        # price the two legs separately. Default: both at the tier rate.
        cargo_rate = a.get("cost.cargo_ship_launch_cost_musd", per_launch)
        tanker_rate = a.get("cost.tanker_launch_cost_musd", per_launch)
        cargo = ship_count
        tanker_launches = ship_count * tankers
        total = cargo + tanker_launches
        return LaunchMath(
            cargo_ship_launches=cargo,
            tankers_per_ship=tankers,
            tanker_launches=tanker_launches,
            total_launches=total,
            launch_cost_tier=tier,
            per_launch_cost_musd=per_launch,
            cargo_ship_rate_musd=cargo_rate,
            tanker_rate_musd=tanker_rate,
            launch_cost_musd=cargo * cargo_rate + tanker_launches * tanker_rate,
        )

    # ------------------------------------------------------------------

    def _expand_items(self, mission: Mission, budget: Optional[BudgetResult],
                      split_storage: bool = False) -> list[PackItem]:
        """Expand the manifest into unit-level pack items (+ auto power hardware).

        split_storage breaks the aggregate battery block into module-sized
        items so a balanced pack can spread storage across ships."""
        items: list[PackItem] = []
        for entry in mission.manifest:
            comp = self.catalog.get(entry.component_id)
            whole = int(entry.qty)
            for _ in range(whole):
                items.append(PackItem(comp.id, comp.name, 1, comp.unit_mass_t, comp.unit_volume_m3, entry.ship))
            frac = entry.qty - whole
            if frac > 1e-9:
                items.append(PackItem(comp.id, comp.name, frac, comp.unit_mass_t * frac,
                                      comp.unit_volume_m3 * frac, entry.ship))

        if budget is not None and not budget.power_hardware.explicit and mission.auto_power:
            hw = budget.power_hardware
            gen = self.catalog.get(hw.generator_component_id)
            units = int(math.ceil(hw.generator_units))
            for i in range(units):
                q = min(1.0, hw.generator_units - i)
                items.append(PackItem(gen.id, gen.name, q, gen.unit_mass_t * q,
                                      gen.unit_volume_m3 * q, mission.power_ship))
            if hw.storage_t > 0:
                sto = self.catalog.get(hw.storage_component_id)
                if split_storage and hw.storage_units > 1:
                    n = int(math.ceil(hw.storage_units))
                    for _ in range(n):
                        items.append(PackItem(sto.id, sto.name, hw.storage_units / n,
                                              hw.storage_t / n, hw.storage_m3 / n))
                else:
                    items.append(PackItem(sto.id, sto.name, hw.storage_units, hw.storage_t,
                                          hw.storage_m3, mission.power_ship))
        return items

    @staticmethod
    def _rollup(items: list[PackItem]) -> dict[str, list[float]]:
        """component_id -> [qty, mass_t, volume_m3] using packed (actual) figures."""
        out: dict[str, list[float]] = {}
        for i in items:
            acc = out.setdefault(i.component_id, [0.0, 0.0, 0.0])
            acc[0] += i.qty
            acc[1] += i.mass_t
            acc[2] += i.volume_m3
        return out
