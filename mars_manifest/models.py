"""Core dataclasses: Component, Mission, Window, Campaign, Assumptions.

State lives here; computation lives in the engine modules.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Optional

_RAISE = object()


@dataclass(frozen=True)
class Component:
    """One catalog record. Attributes mirror data/component_catalog_seed.csv."""

    id: str
    name: str
    group: str
    power_role: str  # consumer | generator | storage | passive
    unit_mass_t: float
    unit_volume_m3: float
    peak_power_kw: float
    duty_cycle: float
    generation_kwe: float
    storage_kwh: float
    unit_cost_musd_low: float
    unit_cost_musd_high: float
    default_qty: int
    readiness_gate: str
    earliest_window: Optional[int]
    depends_on: tuple[str, ...]
    notes: str

    POWER_ROLES = ("consumer", "generator", "storage", "passive")


@dataclass
class ManifestItem:
    """A mission's reference to a catalog component: id + qty (+ optional ship)."""

    component_id: str
    qty: float
    ship: Optional[int] = None  # explicit ship assignment (1-based), else auto


@dataclass
class Mission:
    id: str
    objective: str = ""
    window_id: str = ""
    crewed: bool = False
    ships: Optional[int] = None       # declared batch size (capacity checks / launch math)
    power_ship: Optional[int] = None  # ship that carries auto-sized generation + storage
    auto_power: bool = True           # auto-size power unless manifest places generators/storage
    packing_policy: str = "explicit"  # "explicit" (honor ship pins) | "balanced" (spread + redundancy)
    pack_spares: bool = False         # pack spares tonnage as explicit per-group cargo items
    manifest: list[ManifestItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict, catalog=None) -> "Mission":
        items = []
        for entry in d.get("manifest", []):
            qty = entry.get("qty")
            if qty is None and catalog is not None:
                qty = catalog.get(entry["id"]).default_qty
            items.append(ManifestItem(entry["id"], float(qty if qty is not None else 1), entry.get("ship")))
        return cls(
            id=d.get("id", "mission"),
            objective=d.get("objective", ""),
            window_id=str(d.get("window", d.get("window_id", ""))),
            crewed=bool(d.get("crewed", False)),
            ships=d.get("ships"),
            power_ship=d.get("power_ship"),
            auto_power=bool(d.get("auto_power", True)),
            packing_policy=d.get("packing_policy", "explicit"),
            pack_spares=bool(d.get("pack_spares", False)),
            manifest=items,
        )


@dataclass
class Window:
    id: str  # e.g. "2026-11"
    synod_index: int
    transit_days: int = 210
    objective: str = ""
    notes: str = ""
    missions: list[Mission] = field(default_factory=list)

    @property
    def year(self) -> int:
        return int(str(self.id).split("-")[0])


@dataclass
class Campaign:
    id: str
    windows: list[Window] = field(default_factory=list)


class Assumptions:
    """Read-only dotted-path view over a resolved scenario's assumption tree.

    Engines must fetch every tunable through ``get`` so that scenario
    overrides propagate everywhere (HANDOFF.md ground rule).
    """

    def __init__(self, data: dict, name: str = "baseline"):
        self._data = copy.deepcopy(data)
        self.name = name

    def get(self, path: str, default: Any = _RAISE) -> Any:
        node: Any = self._data
        for part in path.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                if default is _RAISE:
                    raise KeyError(f"Assumption '{path}' not found in scenario '{self.name}'")
                return default
        return node

    def per_launch_cost(self, tier: Optional[str] = None) -> float:
        tier = tier or self.get("cost.active_launch_cost")
        return float(self.get(f"cost.per_launch_cost_musd.{tier}"))

    def as_dict(self) -> dict:
        return copy.deepcopy(self._data)
