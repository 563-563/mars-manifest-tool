"""BudgetEngine: mass / power+storage / volume / cost budgets (HANDOFF.md §5.1).

Formulas are ported from Mars-Precursor-Engineering-Budget.xlsx and
Mars-First-Batch-Cost-Model.xlsx. The seed case must reproduce the §7
regression targets (tests/test_budgets.py).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from .catalog import CONSUMABLES_GROUP, Catalog
from .models import Assumptions, Mission
from .power import FissionOption, SolarOption, size_fission, size_solar


@dataclass(frozen=True)
class LoadBudget:
    avg_kw: float
    connected_peak_kw: float
    simultaneous_peak_kw: float
    daily_energy_kwh: float
    critical_avg_kw: float = 0.0  # survival loads that must ride through storms


@dataclass(frozen=True)
class PowerHardware:
    """Auto- or explicitly-sized generation/storage expressed as catalog units."""

    path: str                    # "fission" | "solar"
    explicit: bool               # True when the manifest placed generators/storage itself
    generator_component_id: str
    generator_units: float
    storage_component_id: str
    storage_units: float         # battery modules (fractional when auto-sized)
    generation_t: float
    generation_m3: float
    storage_t: float
    storage_m3: float
    installed_kwe: float
    installed_storage_kwh: float


@dataclass(frozen=True)
class MassBudget:
    fixed_hardware_t: float
    generation_t: float
    storage_t: float
    consumables_t: float  # memo: subset of fixed hardware
    spares_t: float
    contingency_t: float
    grand_total_t: float
    by_group: dict[str, float] = field(default_factory=dict)
    spares_by_group: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class VolumeBudget:
    fixed_m3: float
    generation_m3: float
    storage_m3: float
    spares_m3: float
    raw_m3: float
    effective_m3: float


@dataclass(frozen=True)
class CostBudget:
    fixed_hardware_low_musd: float
    fixed_hardware_high_musd: float
    generation_low_musd: float
    generation_high_musd: float
    storage_low_musd: float
    storage_high_musd: float
    cargo_low_musd: float
    cargo_high_musd: float


@dataclass(frozen=True)
class CapacityCheck:
    ships: int
    mass_capacity_t: float
    mass_utilisation: float
    mass_margin_t: float
    volume_capacity_m3: float
    volume_utilisation: float


@dataclass(frozen=True)
class BudgetResult:
    mission_id: str
    power_path: str
    loads: LoadBudget
    solar: SolarOption
    fission: FissionOption
    power_hardware: PowerHardware
    mass: MassBudget
    volume: VolumeBudget
    cost: CostBudget
    capacity: Optional[CapacityCheck]
    warnings: tuple[str, ...]


class BudgetEngine:
    def __init__(self, catalog: Catalog, assumptions: Assumptions):
        self.catalog = catalog
        self.a = assumptions

    def compute(self, mission: Mission, power_path: Optional[str] = None) -> BudgetResult:
        a = self.a
        path = power_path or a.get("power.power_path")
        if path not in ("fission", "solar"):
            raise ValueError(f"Unknown power path '{path}'")
        warnings: list[str] = []

        # -- split the manifest by power role -----------------------------
        fixed_items = []      # consumers + passives
        explicit_power = []   # generators/storage explicitly placed in the manifest
        for item in mission.manifest:
            comp = self.catalog.get(item.component_id)
            if comp.power_role in ("generator", "storage") and item.qty > 0:
                explicit_power.append((comp, item.qty))
            else:
                fixed_items.append((comp, item.qty))

        # -- loads (consumers only) ---------------------------------------
        avg_kw = sum(c.peak_power_kw * q * c.duty_cycle for c, q in fixed_items)
        connected = sum(c.peak_power_kw * q for c, q in fixed_items)
        critical_kw = sum(c.peak_power_kw * q * c.duty_cycle
                          for c, q in fixed_items if c.load_class == "critical")
        loads = LoadBudget(
            avg_kw=avg_kw,
            connected_peak_kw=connected,
            simultaneous_peak_kw=connected * a.get("power.diversity_factor"),
            daily_energy_kwh=avg_kw * a.get("power.sol_hours"),
            critical_avg_kw=critical_kw,
        )

        # -- both power options are always sized side by side --------------
        solar = size_solar(avg_kw, a, critical_kw)
        fission = size_fission(avg_kw, a)
        hardware = self._power_hardware(path, solar, fission, explicit_power, avg_kw)
        if path == "solar":
            if solar.dust_storm_infeasible:
                warnings.append(
                    f"Solar path: even the survival-load storm battery is "
                    f"{solar.dust_storm_battery_critical_t:,.0f} t -- exceeds one "
                    f"ship's payload; solar without fission is impractical."
                )
            else:
                warnings.append(
                    f"Solar path: dust storms pause ~{avg_kw - critical_kw:,.0f} kW of "
                    f"production load for up to {a.get('power.dust_storm_autonomy_days'):g} "
                    f"days; survival loads ({critical_kw:,.0f} kW) ride on "
                    f"{solar.dust_storm_battery_critical_t:,.0f} t of storm battery. "
                    f"Real global storms last weeks-months: production halts accordingly."
                )
        if hardware.explicit and hardware.installed_kwe < avg_kw:
            warnings.append(
                f"Explicit power hardware supplies {hardware.installed_kwe:,.0f} kWe "
                f"but average load is {avg_kw:,.0f} kW."
            )

        # -- mass ----------------------------------------------------------
        fixed_hw_t = sum(c.unit_mass_t * q for c, q in fixed_items)
        consumables_t = sum(c.unit_mass_t * q for c, q in fixed_items if c.group == CONSUMABLES_GROUP)
        gen_t, storage_t = hardware.generation_t, hardware.storage_t
        spares_frac = a.get("overheads.spares_fraction_of_dry")
        contingency_frac = a.get("overheads.contingency_fraction")
        spares_base_t = fixed_hw_t - consumables_t + gen_t + storage_t
        # Per-group sparing (literature-informed) when a scenario provides a
        # group->fraction map; groups absent from the map fall back to the
        # flat fraction. Baseline keeps the flat §5.1 formula exactly.
        by_group_spares = a.get("overheads.spares_fraction_by_group", None)

        def gfrac(group: str) -> float:
            return by_group_spares.get(group, spares_frac) if by_group_spares else spares_frac

        spared_masses: dict[str, float] = {}
        for c, q in fixed_items:
            if c.group != CONSUMABLES_GROUP:
                spared_masses[c.group] = spared_masses.get(c.group, 0.0) + c.unit_mass_t * q
        if gen_t > 0:
            g = self.catalog.get(hardware.generator_component_id).group
            spared_masses[g] = spared_masses.get(g, 0.0) + gen_t
        if storage_t > 0:
            g = self.catalog.get(hardware.storage_component_id).group
            spared_masses[g] = spared_masses.get(g, 0.0) + storage_t
        spares_by_group = {g: gfrac(g) * m for g, m in spared_masses.items()}
        spares_t = sum(spares_by_group.values())
        contingency_t = contingency_frac * (fixed_hw_t + gen_t + storage_t)
        by_group: dict[str, float] = {}
        for c, q in fixed_items:
            by_group[c.group] = by_group.get(c.group, 0.0) + c.unit_mass_t * q
        mass = MassBudget(
            fixed_hardware_t=fixed_hw_t,
            generation_t=gen_t,
            storage_t=storage_t,
            consumables_t=consumables_t,
            spares_t=spares_t,
            contingency_t=contingency_t,
            grand_total_t=fixed_hw_t + gen_t + storage_t + spares_t + contingency_t,
            by_group=by_group,
            spares_by_group=spares_by_group,
        )

        # -- volume ---------------------------------------------------------
        fixed_m3 = sum(c.unit_volume_m3 * q for c, q in fixed_items)
        # volume spares track the effective (possibly per-group) mass fraction;
        # identical to spares_frac * fixed_m3 under flat sparing
        eff_spares_frac = spares_t / spares_base_t if spares_base_t else 0.0
        spares_m3 = eff_spares_frac * fixed_m3
        raw_m3 = fixed_m3 + hardware.generation_m3 + hardware.storage_m3 + spares_m3
        volume = VolumeBudget(
            fixed_m3=fixed_m3,
            generation_m3=hardware.generation_m3,
            storage_m3=hardware.storage_m3,
            spares_m3=spares_m3,
            raw_m3=raw_m3,
            effective_m3=raw_m3 / a.get("fleet.packing_efficiency"),
        )

        # -- cost (cargo hardware; launch cost lives in packing) -------------
        fixed_low = sum(c.unit_cost_musd_low * q for c, q in fixed_items)
        fixed_high = sum(c.unit_cost_musd_high * q for c, q in fixed_items)
        gen_comp = self.catalog.get(hardware.generator_component_id)
        sto_comp = self.catalog.get(hardware.storage_component_id)
        gen_low = gen_comp.unit_cost_musd_low * hardware.generator_units
        gen_high = gen_comp.unit_cost_musd_high * hardware.generator_units
        sto_units_cost = math.ceil(hardware.storage_units) if not hardware.explicit else hardware.storage_units
        sto_low = sto_comp.unit_cost_musd_low * sto_units_cost
        sto_high = sto_comp.unit_cost_musd_high * sto_units_cost
        cost = CostBudget(
            fixed_hardware_low_musd=fixed_low,
            fixed_hardware_high_musd=fixed_high,
            generation_low_musd=gen_low,
            generation_high_musd=gen_high,
            storage_low_musd=sto_low,
            storage_high_musd=sto_high,
            cargo_low_musd=fixed_low + gen_low + sto_low,
            cargo_high_musd=fixed_high + gen_high + sto_high,
        )

        # -- capacity comparison ---------------------------------------------
        capacity = None
        if mission.ships:
            mass_cap = mission.ships * a.get("fleet.payload_mass_per_ship_t")
            vol_cap = mission.ships * a.get("fleet.payload_volume_per_ship_m3")
            capacity = CapacityCheck(
                ships=mission.ships,
                mass_capacity_t=mass_cap,
                mass_utilisation=mass.grand_total_t / mass_cap,
                mass_margin_t=mass_cap - mass.grand_total_t,
                volume_capacity_m3=vol_cap,
                volume_utilisation=volume.effective_m3 / vol_cap,
            )
            if mass.grand_total_t > mass_cap:
                warnings.append(f"Mass over capacity: {mass.grand_total_t:,.1f} t > {mass_cap:,.0f} t")
            if volume.effective_m3 > vol_cap:
                warnings.append(f"Volume over capacity: {volume.effective_m3:,.0f} m3 > {vol_cap:,.0f} m3")

        return BudgetResult(
            mission_id=mission.id,
            power_path=path,
            loads=loads,
            solar=solar,
            fission=fission,
            power_hardware=hardware,
            mass=mass,
            volume=volume,
            cost=cost,
            capacity=capacity,
            warnings=tuple(warnings),
        )

    # ------------------------------------------------------------------

    def _power_hardware(
        self,
        path: str,
        solar: SolarOption,
        fission: FissionOption,
        explicit_power: list,
        avg_kw: float,
    ) -> PowerHardware:
        """Express generation/storage as catalog components.

        Auto-sizing follows §5.1; if the mission manifest explicitly places
        generator/storage components, those quantities win instead (the
        catalog supports both modes per HANDOFF.md §4.1).
        """
        a = self.a
        gen_id = a.get("power.fission_component" if path == "fission" else "power.solar_component")
        sto_id = a.get("power.battery_component")

        if explicit_power:
            gen_units = sto_units = 0.0
            gen_t = gen_m3 = sto_t = sto_m3 = kwe = kwh = 0.0
            for comp, qty in explicit_power:
                if comp.power_role == "generator":
                    gen_id, gen_units = comp.id, gen_units + qty
                    gen_t += comp.unit_mass_t * qty
                    gen_m3 += comp.unit_volume_m3 * qty
                    kwe += comp.generation_kwe * qty
                else:
                    sto_id, sto_units = comp.id, sto_units + qty
                    sto_t += comp.unit_mass_t * qty
                    sto_m3 += comp.unit_volume_m3 * qty
                    kwh += comp.storage_kwh * qty
            return PowerHardware(path, True, gen_id, gen_units, sto_id, sto_units,
                                 gen_t, gen_m3, sto_t, sto_m3, kwe, kwh)

        sto_comp = self.catalog.get(sto_id)
        if path == "fission":
            gen_units = float(fission.units)
            gen_t, gen_m3 = fission.mass_t, fission.volume_m3
            sto_t, sto_m3 = fission.buffer_battery_t, fission.buffer_battery_m3
            kwe = fission.units * a.get("power.fission_unit_kwe")
            kwh = fission.buffer_kwh
        else:
            gen_comp = self.catalog.get(gen_id)
            # solar module = 1000 m2; fractional modules keep mass exactly on formula
            gen_units = solar.array_m2 / 1000.0
            gen_t, gen_m3 = solar.array_mass_t, solar.array_volume_m3
            sto_t, sto_m3 = solar.night_battery_t, solar.night_battery_m3
            kwe = gen_units * gen_comp.generation_kwe
            kwh = solar.night_kwh
        sto_units = kwh / sto_comp.storage_kwh if sto_comp.storage_kwh else 0.0
        return PowerHardware(path, False, gen_id, gen_units, sto_id, sto_units,
                             gen_t, gen_m3, sto_t, sto_m3, kwe, kwh)
