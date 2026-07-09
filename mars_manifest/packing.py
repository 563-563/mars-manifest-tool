"""PackingEngine: bin-pack components into ships + tanker/launch math (§5.2).

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
class PackingResult:
    mission_id: str
    ships: tuple[ShipReport, ...]
    ship_count: int
    launch: LaunchMath
    warnings: tuple[str, ...]


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
    ) -> PackingResult:
        a = self.a
        mass_cap = a.get("fleet.payload_mass_per_ship_t")
        vol_cap = a.get("fleet.payload_volume_per_ship_m3")
        warnings: list[str] = []

        items = self._expand_items(mission, budget)
        ships: dict[int, PackedShip] = {}
        if mission.ships:
            for i in range(1, mission.ships + 1):
                ships[i] = PackedShip(i)

        # Pre-place explicit assignments, then first-fit-decreasing the rest.
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
        )

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

    def _expand_items(self, mission: Mission, budget: Optional[BudgetResult]) -> list[PackItem]:
        """Expand the manifest into unit-level pack items (+ auto power hardware)."""
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
