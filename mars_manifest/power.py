"""Power & storage sizing — solar vs fission (HANDOFF.md §5.1).

Formulas are ported verbatim from Mars-Precursor-Engineering-Budget.xlsx
('Power & Storage' sheet). Do not change them without updating the §7
regression tests.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .models import Assumptions


@dataclass(frozen=True)
class SolarOption:
    array_m2: float
    array_mass_t: float
    array_volume_m3: float
    night_kwh: float
    night_battery_t: float
    night_battery_m3: float
    dust_storm_kwh: float
    dust_storm_battery_t: float
    dust_storm_infeasible: bool  # dust-storm battery alone exceeds one ship's payload


@dataclass(frozen=True)
class FissionOption:
    units: int
    mass_t: float
    volume_m3: float
    buffer_kwh: float
    buffer_battery_t: float
    buffer_battery_m3: float


def size_solar(avg_kw: float, a: Assumptions) -> SolarOption:
    yield_w_m2 = a.get("power.solar_yield_w_per_m2")
    kg_m2 = a.get("power.solar_kg_per_m2")
    wh_per_kg = a.get("power.battery_wh_per_kg")
    kwh_per_m3 = a.get("power.battery_kwh_per_m3")
    night_hours = a.get("power.night_hours")
    sol_hours = a.get("power.sol_hours")
    dust_days = a.get("power.dust_storm_autonomy_days")

    array_m2 = avg_kw * 1000 / yield_w_m2
    array_mass_t = array_m2 * kg_m2 / 1000
    # Stowed volume derived from the solar catalog component's density
    # (volume per m2 of deployed array), so explicit and auto-sized arrays agree.
    vol_per_m2 = a.get("power.solar_stowed_m3_per_1000m2", 10.0) / 1000.0
    night_kwh = avg_kw * night_hours
    night_battery_t = night_kwh / wh_per_kg
    dust_kwh = avg_kw * dust_days * sol_hours
    dust_battery_t = dust_kwh / wh_per_kg
    return SolarOption(
        array_m2=array_m2,
        array_mass_t=array_mass_t,
        array_volume_m3=array_m2 * vol_per_m2,
        night_kwh=night_kwh,
        night_battery_t=night_battery_t,
        night_battery_m3=night_kwh / kwh_per_m3,
        dust_storm_kwh=dust_kwh,
        dust_storm_battery_t=dust_battery_t,
        dust_storm_infeasible=dust_battery_t > a.get("fleet.payload_mass_per_ship_t"),
    )


def size_fission(avg_kw: float, a: Assumptions) -> FissionOption:
    unit_kwe = a.get("power.fission_unit_kwe")
    unit_t = a.get("power.fission_unit_mass_t")
    unit_m3 = a.get("power.fission_unit_volume_m3")
    buffer_hours = a.get("power.fission_buffer_hours")
    wh_per_kg = a.get("power.battery_wh_per_kg")
    kwh_per_m3 = a.get("power.battery_kwh_per_m3")

    units = math.ceil(avg_kw / unit_kwe) if avg_kw > 0 else 0
    buffer_kwh = avg_kw * buffer_hours
    return FissionOption(
        units=units,
        mass_t=units * unit_t,
        volume_m3=units * unit_m3,
        buffer_kwh=buffer_kwh,
        buffer_battery_t=buffer_kwh / wh_per_kg,
        buffer_battery_m3=buffer_kwh / kwh_per_m3,
    )
