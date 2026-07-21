"""ISRU production-chain model: rates, energy budget, and bottleneck analysis
for the Sabatier propellant path (water -> electrolysis -> Sabatier -> cryo).

Stoichiometry is physics and lives here as constants (Tier A in
PROVENANCE.md). Process energies, the mixture ratio, and campaign timing are
assumptions (`isru.*` in inputs/assumptions.json, Tier C).

Chain, per kg of CH4 produced:
    CO2 + 4 H2 -> CH4 + 2 H2O           (Sabatier, exothermic)
    2 H2O -> 2 H2 + O2                  (electrolysis, the big load)
Water electrolyzed per kg CH4 is 4.49 kg; the Sabatier reaction returns
2.25 kg of it, so net mined water is ~2.25 kg per kg CH4. Electrolysis
co-produces ~3.99 kg O2 per kg CH4 — just above the ~3.6 the engine burns.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .catalog import Catalog
from .models import Assumptions, Mission

# molar masses, kg/kmol
_M_CH4, _M_CO2, _M_H2, _M_H2O, _M_O2 = 16.043, 44.009, 2.016, 18.015, 31.998

# oxygen-only fallback (2 CO2 -> 2 CO + O2, solid-oxide electrolysis)
CO2_PER_O2 = 2 * _M_CO2 / _M_O2  # 2.751

# per kg CH4 (Sabatier stoichiometry)
H2_PER_CH4 = 4 * _M_H2 / _M_CH4                      # 0.5027
H2O_ELECTROLYZED_PER_CH4 = H2_PER_CH4 * (_M_H2O * 2 / (2 * _M_H2))   # 4.4917
H2O_RECYCLED_PER_CH4 = 2 * _M_H2O / _M_CH4           # 2.2460 (Sabatier product)
H2O_NET_PER_CH4 = H2O_ELECTROLYZED_PER_CH4 - H2O_RECYCLED_PER_CH4    # 2.2458
CO2_PER_CH4 = _M_CO2 / _M_CH4                        # 2.7432
O2_PER_KG_H2O = _M_O2 / (2 * _M_H2O)                 # 0.8881
O2_FROM_ELECTROLYSIS_PER_CH4 = H2O_ELECTROLYZED_PER_CH4 * O2_PER_KG_H2O  # 3.989

# h2_import mode: bring H2 from Earth, source O2 from CO2 locally, no water
# mining. Net imported H2 = the H bound into the CH4 (Sabatier product water
# is electrolyzed to recycle the rest), i.e. the H mass fraction of CH4.
H2_IMPORT_PER_CH4 = (4 * 1.008) / _M_CH4             # 0.2513 (H mass fraction of CH4)
LH2_KG_PER_M3 = 70.8                                 # liquid hydrogen density


@dataclass(frozen=True)
class ChainStep:
    key: str
    component_id: str
    units: float
    avg_kw: float
    throughput_kg_hr: float        # in the step's own commodity (H2O, CO2, CH4, propellant)
    commodity: str
    propellant_rate_kg_hr: float   # propellant-equivalent capacity of this step
    is_bottleneck: bool


@dataclass(frozen=True)
class IsruResult:
    steps: tuple[ChainStep, ...]
    bottleneck: str
    propellant_rate_kg_hr: float
    propellant_kg_per_sol: float
    tonnes_per_window: float
    return_load_t: float
    fraction_of_return_load: float
    sols_to_return_load: Optional[float]
    years_to_return_load: Optional[float]
    net_water_kg_per_sol: float
    water_for_return_load_t: float
    spec_energy_kwh_per_kg: float
    energy_per_return_load_gwh: float
    full_scale_kw_required: float
    o2_surplus_per_kg_ch4: float
    warnings: tuple[str, ...]
    mode: str = "sabatier"
    ch4_import_t_per_load: float = 0.0   # oxygen_only: Earth-supplied methane
    ch4_import_ships_per_load: int = 0
    h2_import_t_per_load: float = 0.0    # h2_import: Earth-supplied hydrogen
    h2_import_ships_per_load: int = 0    # binding of mass vs LH2 volume


@dataclass(frozen=True)
class DesignStep:
    key: str
    component_id: str
    unit_rate_kg_hr: float     # propellant-equivalent capacity of ONE unit
    units_required: int
    utilization: float         # target / installed capacity
    mass_t: float
    avg_kw: float
    cost_low_musd: float
    cost_high_musd: float


@dataclass(frozen=True)
class ChainDesign:
    """A rate-matched equipment buy for a target propellant production rate.

    Answers 'what would we bring to bring the step rates into parallel?':
    units per step are the minimum that meet the target, so utilization is
    driven to 1.0 except where unit granularity (ceil) forces slack.
    """
    target_rate_kg_hr: float          # nameplate chain rate to hit
    target_tonnes_per_synod: float    # expected output at plant availability
    steps: tuple[DesignStep, ...]
    chain_mass_t: float
    chain_avg_kw: float
    fission_units: int
    fission_mass_t: float
    buffer_battery_t: float
    total_mass_t: float               # chain + power + storage
    cost_low_musd: float
    cost_high_musd: float
    notes: tuple[str, ...]


class IsruEngine:
    def __init__(self, catalog: Catalog, assumptions: Assumptions):
        self.catalog = catalog
        self.a = assumptions

    def assess(self, mission: Mission) -> IsruResult:
        qty = {}
        for item in mission.manifest:
            qty[item.component_id] = qty.get(item.component_id, 0.0) + item.qty
        return self.assess_quantities(qty)

    def size_chain(self, target_tonnes_per_synod: Optional[float] = None,
                   target_rate_kg_hr: Optional[float] = None) -> ChainDesign:
        """Rate-match the chain: minimum units per step to hit a target.

        Default target: one return load per synod. Rates are nameplate; the
        tonnes target is grossed up by plant availability.
        """
        import math

        a = self.a
        sol_hours = a.get("power.sol_hours")
        window_sols = a.get("isru.production_sols_per_synod")
        availability = a.get("isru.plant_availability", 1.0)
        if target_rate_kg_hr is None:
            tonnes = target_tonnes_per_synod or a.get("isru.return_propellant_t")
            target_rate_kg_hr = tonnes * 1000.0 / (window_sols * sol_hours * availability)
        expected_t = target_rate_kg_hr * sol_hours * availability * window_sols / 1000.0

        # per-unit propellant-equivalent rates from a one-of-each assessment
        one_each = {cid: 1.0 for cid in a.get("isru.chain_components").values()}
        base = self.assess_quantities(one_each)

        steps: list[DesignStep] = []
        notes: list[str] = []
        chain_mass = chain_kw = cost_lo = cost_hi = 0.0
        for s in base.steps:
            comp = self.catalog.get(s.component_id)
            units = max(1, math.ceil(target_rate_kg_hr / s.propellant_rate_kg_hr))
            util = target_rate_kg_hr / (units * s.propellant_rate_kg_hr)
            steps.append(DesignStep(
                key=s.key, component_id=s.component_id,
                unit_rate_kg_hr=s.propellant_rate_kg_hr,
                units_required=units, utilization=util,
                mass_t=units * comp.unit_mass_t,
                avg_kw=units * comp.peak_power_kw * comp.duty_cycle,
                cost_low_musd=units * comp.unit_cost_musd_low,
                cost_high_musd=units * comp.unit_cost_musd_high,
            ))
            chain_mass += steps[-1].mass_t
            chain_kw += steps[-1].avg_kw
            cost_lo += steps[-1].cost_low_musd
            cost_hi += steps[-1].cost_high_musd
            if util < 0.7:
                notes.append(
                    f"{s.key}: unit granularity leaves {1 - util:.0%} slack "
                    f"({units}x units for {target_rate_kg_hr / s.propellant_rate_kg_hr:.2f}x demand)"
                )

        # control unit rides along (one per plant)
        ctrl = self.catalog.get("isru_control") if "isru_control" in self.catalog else None
        if ctrl:
            chain_mass += ctrl.unit_mass_t
            chain_kw += ctrl.peak_power_kw * ctrl.duty_cycle
            cost_lo += ctrl.unit_cost_musd_low
            cost_hi += ctrl.unit_cost_musd_high

        fission_kwe = a.get("power.fission_unit_kwe")
        fission_units = math.ceil(chain_kw / fission_kwe)
        fission_mass = fission_units * a.get("power.fission_unit_mass_t")
        buffer_t = chain_kw * a.get("power.fission_buffer_hours") / a.get("power.battery_wh_per_kg")
        fission_comp_id = a.get("power.fission_component")
        fission_comp = self.catalog.get(fission_comp_id)
        cost_lo += fission_units * fission_comp.unit_cost_musd_low
        cost_hi += fission_units * fission_comp.unit_cost_musd_high

        return ChainDesign(
            target_rate_kg_hr=target_rate_kg_hr,
            target_tonnes_per_synod=expected_t,
            steps=tuple(steps),
            chain_mass_t=chain_mass,
            chain_avg_kw=chain_kw,
            fission_units=fission_units,
            fission_mass_t=fission_mass,
            buffer_battery_t=buffer_t,
            total_mass_t=chain_mass + fission_mass + buffer_t,
            cost_low_musd=cost_lo,
            cost_high_musd=cost_hi,
            notes=tuple(notes),
        )

    def assess_quantities(self, quantities: dict[str, float]) -> IsruResult:
        a = self.a
        of = a.get("isru.raptor_o_f_ratio")
        prop_per_ch4 = 1.0 + of
        e_h2o = a.get("isru.electrolysis_kwh_per_kg_h2o")
        e_co2 = a.get("isru.co2_capture_kwh_per_kg_co2")
        e_sab = a.get("isru.sabatier_support_kwh_per_kg_ch4")
        e_liq = a.get("isru.liquefaction_kwh_per_kg_propellant")
        e_wat = a.get("isru.water_processing_kwh_per_kg_h2o")
        e_exc = a.get("isru.excavation_kwh_per_kg_h2o", 0.0)
        availability = a.get("isru.plant_availability", 1.0)
        chain = a.get("isru.chain_components")
        sol_hours = a.get("power.sol_hours")
        window_sols = a.get("isru.production_sols_per_synod")
        load_t = a.get("isru.return_propellant_t")
        mode = a.get("isru.mode", "sabatier")
        warnings: list[str] = []

        if mode == "oxygen_only":
            return self._assess_oxygen_only(quantities, a, chain, sol_hours,
                                            window_sols, load_t, of, availability)

        # h2_import shares the sabatier chain rate math (same electrolysis /
        # Sabatier / liquefaction equipment); it differs only in feedstock —
        # H2 imported, water recycled not mined — handled at the return below.
        h2_import = mode == "h2_import"

        def avg_kw(component_id: str) -> tuple[float, float]:
            comp = self.catalog.get(component_id)
            n = quantities.get(component_id, 0.0)
            return n, n * comp.peak_power_kw * comp.duty_cycle

        steps: list[ChainStep] = []

        # water extraction is NOT power-limited in reality: melt-cavity
        # geometry, ice grade, thermal conduction, and pumping cap the yield
        # far below what electrical power alone would predict (deep-research
        # 2026-07-20; NASA Rodwell/WER data). A per-unit rate ceiling on the
        # extraction step encodes that. Keyed to ice grade: baseline is the
        # clean-ice Rodwell case; the garden_regolith scenario slashes it.
        water_cap = a.get("isru.water_extraction_kg_h2o_per_hr_per_unit", None)

        def step(key, cid, commodity, kwh_per_kg, prop_per_kg, rate_cap_per_unit=None):
            n, kw = avg_kw(cid)
            thr = kw / kwh_per_kg if kwh_per_kg > 0 else 0.0
            if rate_cap_per_unit is not None and n > 0:
                thr = min(thr, n * rate_cap_per_unit)  # process/grade-limited, not power
            steps.append(ChainStep(key, cid, n, kw, thr, commodity,
                                   thr * prop_per_kg, False))

        if "excavation" in chain and e_exc > 0:
            step("excavation", chain["excavation"], "H2O (net)", e_exc,
                 prop_per_ch4 / H2O_NET_PER_CH4)
        step("water_processing", chain["water_processing"], "H2O (net)", e_wat,
             prop_per_ch4 / H2O_NET_PER_CH4, rate_cap_per_unit=water_cap)
        step("electrolysis", chain["electrolysis"], "H2O", e_h2o,
             prop_per_ch4 / H2O_ELECTROLYZED_PER_CH4)
        step("co2_capture", chain["co2_capture"], "CO2", e_co2,
             prop_per_ch4 / CO2_PER_CH4)
        step("sabatier", chain["sabatier"], "CH4", e_sab, prop_per_ch4)
        step("liquefaction", chain["liquefaction"], "propellant", e_liq, 1.0)

        missing = [s.key for s in steps if s.units == 0]
        if missing:
            warnings.append("Chain incomplete — no units of: " + ", ".join(missing))
        rate = min(s.propellant_rate_kg_hr for s in steps)
        bottleneck = min(steps, key=lambda s: s.propellant_rate_kg_hr).key
        steps = [ChainStep(s.key, s.component_id, s.units, s.avg_kw, s.throughput_kg_hr,
                           s.commodity, s.propellant_rate_kg_hr, s.key == bottleneck)
                 for s in steps]

        # energy per kg of propellant, all steps at stoichiometric balance.
        # h2_import mines no water, so the mining/processing energy drops out.
        ch4_frac = 1.0 / prop_per_ch4
        mining_e = 0.0 if h2_import else H2O_NET_PER_CH4 * (e_wat + e_exc) * ch4_frac
        spec = (H2O_ELECTROLYZED_PER_CH4 * e_h2o + CO2_PER_CH4 * e_co2 + e_sab) * ch4_frac \
            + e_liq + mining_e

        o2_surplus = O2_FROM_ELECTROLYSIS_PER_CH4 - of
        if o2_surplus < 0:
            warnings.append(
                f"O/F ratio {of} exceeds electrolysis O2 co-production "
                f"({O2_FROM_ELECTROLYSIS_PER_CH4:.2f} per kg CH4) — supplemental O2 "
                f"(CO2 electrolysis, MOXIE-style) required."
            )

        # expected production applies plant availability (maintenance, dust,
        # faults under a 4-22 min comms delay); rates above are nameplate
        kg_per_sol = rate * sol_hours * availability
        t_per_window = kg_per_sol * window_sols / 1000.0
        sols_to_load = (load_t * 1000.0 / kg_per_sol) if kg_per_sol > 0 else None
        years_to_load = sols_to_load * sol_hours / 8766.0 if sols_to_load else None
        full_scale_kw = load_t * 1000.0 * spec / (window_sols * sol_hours * availability)

        if t_per_window < load_t and kg_per_sol > 0:
            warnings.append(
                f"Pilot chain fills {t_per_window / load_t:.0%} of one return load "
                f"per window — scaling the '{bottleneck}' step is the gate to "
                f"return-propellant capability."
            )

        # h2_import: feedstock is Earth hydrogen; water is recycled, not mined
        h2_import_t = h2_import_ships = 0
        net_water_kg_per_sol = kg_per_sol / prop_per_ch4 * H2O_NET_PER_CH4
        water_for_load_t = load_t / prop_per_ch4 * H2O_NET_PER_CH4
        if h2_import:
            ch4_per_load = load_t / prop_per_ch4
            h2_import_t = ch4_per_load * H2_IMPORT_PER_CH4
            payload_t = a.get("fleet.payload_mass_per_ship_t")
            bay_m3 = a.get("fleet.payload_volume_per_ship_m3")
            by_mass = h2_import_t / payload_t
            by_volume = (h2_import_t * 1000.0 / LH2_KG_PER_M3) / bay_m3
            h2_import_ships = int(-(-max(by_mass, by_volume) // 1))  # ceil, volume usually binds
            net_water_kg_per_sol = 0.0
            water_for_load_t = 0.0
            warnings.append(
                f"h2_import mode: {h2_import_t:,.0f} t of LH2 per return load ships from "
                f"Earth (volume-bound: ~{h2_import_ships} ships at {bay_m3:g} m3/bay); "
                f"O2 sourced from CO2 locally, no water mining. LH2 surface cryocooling "
                f"is the weak point (D-tier, unmodeled)."
            )

        return IsruResult(
            steps=tuple(steps),
            bottleneck=bottleneck,
            propellant_rate_kg_hr=rate,
            propellant_kg_per_sol=kg_per_sol,
            tonnes_per_window=t_per_window,
            return_load_t=load_t,
            fraction_of_return_load=t_per_window / load_t if load_t else 0.0,
            sols_to_return_load=sols_to_load,
            years_to_return_load=years_to_load,
            net_water_kg_per_sol=net_water_kg_per_sol,
            water_for_return_load_t=water_for_load_t,
            spec_energy_kwh_per_kg=spec,
            energy_per_return_load_gwh=load_t * 1000.0 * spec / 1e6,
            full_scale_kw_required=full_scale_kw,
            o2_surplus_per_kg_ch4=o2_surplus,
            warnings=tuple(warnings),
            mode=mode,
            h2_import_t_per_load=h2_import_t,
            h2_import_ships_per_load=h2_import_ships,
        )

    def _assess_oxygen_only(self, quantities, a, chain, sol_hours, window_sols,
                            load_t, of, availability) -> IsruResult:
        """DRA-5.0-style fallback: LOX from atmospheric CO2 (solid-oxide
        electrolysis, MOXIE heritage); methane imported from Earth. No water
        dependency at all — the descope that buys out site-water risk.

        The 'electrolysis' chain component stands in as the SOE plant; the
        production commodity is O2 (the of/(1+of) fraction of a return load).
        """
        e_co2 = a.get("isru.co2_capture_kwh_per_kg_co2")
        e_soe = a.get("isru.co2_electrolysis_kwh_per_kg_o2")
        e_liq = a.get("isru.liquefaction_kwh_per_kg_propellant")
        payload_t = a.get("fleet.payload_mass_per_ship_t")
        o2_per_load = load_t * of / (1.0 + of)
        ch4_import = load_t - o2_per_load
        warnings = [
            f"Oxygen-only mode: {ch4_import:,.0f} t of CH4 per return load ships "
            f"from Earth (~{-(-ch4_import // payload_t):.0f} extra cargo ships); "
            f"no water mining required."
        ]

        def avg_kw(cid):
            comp = self.catalog.get(cid)
            n = quantities.get(cid, 0.0)
            return n, n * comp.peak_power_kw * comp.duty_cycle

        steps = []
        for key, cid, commodity, kwh_per_kg, o2_per_kg in (
            ("co2_capture", chain["co2_capture"], "CO2", e_co2, 1.0 / CO2_PER_O2),
            ("o2_electrolysis", chain["electrolysis"], "O2", e_soe, 1.0),
            ("liquefaction", chain["liquefaction"], "O2 (liquid)", e_liq, 1.0),
        ):
            n, kw = avg_kw(cid)
            thr = kw / kwh_per_kg if kwh_per_kg > 0 else 0.0
            steps.append(ChainStep(key, cid, n, kw, thr, commodity, thr * o2_per_kg, False))
        if any(s.units == 0 for s in steps):
            warnings.append("Chain incomplete — no units of: "
                            + ", ".join(s.key for s in steps if s.units == 0))
        rate = min(s.propellant_rate_kg_hr for s in steps)
        bottleneck = min(steps, key=lambda s: s.propellant_rate_kg_hr).key
        steps = [ChainStep(s.key, s.component_id, s.units, s.avg_kw, s.throughput_kg_hr,
                           s.commodity, s.propellant_rate_kg_hr, s.key == bottleneck)
                 for s in steps]

        spec = CO2_PER_O2 * e_co2 + e_soe + e_liq  # per kg O2
        kg_per_sol = rate * sol_hours * availability
        t_per_window = kg_per_sol * window_sols / 1000.0
        sols_to_load = (o2_per_load * 1000.0 / kg_per_sol) if kg_per_sol > 0 else None
        return IsruResult(
            steps=tuple(steps),
            bottleneck=bottleneck,
            propellant_rate_kg_hr=rate,
            propellant_kg_per_sol=kg_per_sol,
            tonnes_per_window=t_per_window,
            return_load_t=o2_per_load,
            fraction_of_return_load=t_per_window / o2_per_load if o2_per_load else 0.0,
            sols_to_return_load=sols_to_load,
            years_to_return_load=sols_to_load * sol_hours / 8766.0 if sols_to_load else None,
            net_water_kg_per_sol=0.0,
            water_for_return_load_t=0.0,
            spec_energy_kwh_per_kg=spec,
            energy_per_return_load_gwh=o2_per_load * 1000.0 * spec / 1e6,
            full_scale_kw_required=o2_per_load * 1000.0 * spec / (window_sols * sol_hours * availability),
            o2_surplus_per_kg_ch4=0.0,
            warnings=tuple(warnings),
            mode="oxygen_only",
            ch4_import_t_per_load=ch4_import,
            ch4_import_ships_per_load=int(-(-ch4_import // payload_t)),
        )
