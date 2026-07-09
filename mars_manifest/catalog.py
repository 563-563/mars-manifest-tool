"""Component catalog: load, validate and query the master library CSV."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Optional

from .models import Component

# Group label used by the mass budget's consumables memo line (matches the
# seed catalog and the engineering-budget workbook).
CONSUMABLES_GROUP = "Consumables & caches"


class CatalogError(ValueError):
    pass


class Catalog:
    def __init__(self, components: Iterable[Component]):
        self._by_id: dict[str, Component] = {}
        for comp in components:
            if comp.id in self._by_id:
                raise CatalogError(f"Duplicate component id '{comp.id}'")
            self._by_id[comp.id] = comp
        self._validate()

    # -- loading ---------------------------------------------------------

    @classmethod
    def load(cls, csv_path: str | Path) -> "Catalog":
        path = Path(csv_path)
        with path.open(newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            raise CatalogError(f"Catalog file {path} is empty")
        return cls(cls._parse_row(r, i) for i, r in enumerate(rows, start=2))

    @staticmethod
    def _parse_row(row: dict, lineno: int) -> Component:
        def num(field: str) -> float:
            raw = (row.get(field) or "").strip()
            try:
                return float(raw) if raw else 0.0
            except ValueError as exc:
                raise CatalogError(f"Line {lineno}: bad number for '{field}': {raw!r}") from exc

        earliest = (row.get("earliest_window") or "").strip()
        depends = tuple(d.strip() for d in (row.get("depends_on") or "").split(";") if d.strip())
        return Component(
            id=row["id"].strip(),
            name=row["name"].strip(),
            group=row["group"].strip(),
            power_role=row["power_role"].strip(),
            unit_mass_t=num("unit_mass_t"),
            unit_volume_m3=num("unit_volume_m3"),
            peak_power_kw=num("peak_power_kw"),
            duty_cycle=num("duty_cycle"),
            generation_kwe=num("generation_kwe"),
            storage_kwh=num("storage_kwh"),
            unit_cost_musd_low=num("unit_cost_musd_low"),
            unit_cost_musd_high=num("unit_cost_musd_high"),
            default_qty=int(num("default_qty")),
            readiness_gate=(row.get("readiness_gate") or "").strip(),
            earliest_window=int(earliest) if earliest else None,
            depends_on=depends,
            notes=(row.get("notes") or "").strip(),
        )

    # -- validation ------------------------------------------------------

    def _validate(self) -> None:
        # Capability-flag vocabulary from HANDOFF.md §6; depends_on entries may
        # reference either another component id or one of these flags.
        known_flags = {
            "edl_proven", "precision_landing", "power_baseload", "water_supply",
            "return_propellant_proven", "life_support_closed", "radiation_managed",
            "comms_established", "autonomy_proven", "infrastructure_ready",
            "mobility", "habitat_ready",
        }
        for comp in self._by_id.values():
            if comp.power_role not in Component.POWER_ROLES:
                raise CatalogError(f"{comp.id}: invalid power_role '{comp.power_role}'")
            for attr in ("unit_mass_t", "unit_volume_m3", "peak_power_kw", "duty_cycle",
                         "generation_kwe", "storage_kwh", "unit_cost_musd_low",
                         "unit_cost_musd_high"):
                if getattr(comp, attr) < 0:
                    raise CatalogError(f"{comp.id}: negative {attr}")
            if comp.unit_cost_musd_high < comp.unit_cost_musd_low:
                raise CatalogError(f"{comp.id}: cost high < low")
            for dep in comp.depends_on:
                if dep not in self._by_id and dep not in known_flags:
                    raise CatalogError(f"{comp.id}: unknown dependency '{dep}'")

    # -- queries ---------------------------------------------------------

    def get(self, component_id: str) -> Component:
        try:
            return self._by_id[component_id]
        except KeyError:
            raise CatalogError(f"Unknown component id '{component_id}'") from None

    def __contains__(self, component_id: str) -> bool:
        return component_id in self._by_id

    def all(self) -> list[Component]:
        return list(self._by_id.values())

    def by_group(self, group: Optional[str] = None) -> list[Component]:
        comps = self.all()
        return [c for c in comps if c.group == group] if group else comps

    def groups(self) -> list[str]:
        seen: dict[str, None] = {}
        for c in self._by_id.values():
            seen.setdefault(c.group, None)
        return list(seen)
