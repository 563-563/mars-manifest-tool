"""ISRU production-chain model: rates, energy budget, and bottleneck analysis
for the Sabatier propellant path (water -> electrolysis -> Sabatier -> cryo).

Stoichiometry is physics and lives here as constants (Tier A in
PROVENANCE.md). Process energies, the mixture ratio, and campaign timing are
assumptions (`isru.*` in data/assumptions_seed.json, Tier C).

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

# per kg CH4 (Sabatier stoichiometry)
H2_PER_CH4 = 4 * _M_H2 / _M_CH4                      # 0.5027
H2O_ELECTROLYZED_PER_CH4 = H2_PER_CH4 * (_M_H2O * 2 / (2 * _M_H2))   # 4.4917
H2O_RECYCLED_PER_CH4 = 2 * _M_H2O / _M_CH4           # 2.2460 (Sabatier product)
H2O_NET_PER_CH4 = H2O_ELECTROLYZED_PER_CH4 - H2O_RECYCLED_PER_CH4    # 2.2458
CO2_PER_CH4 = _M_CO2 / _M_CH4                        # 2.7432
O2_PER_KG_H2O = _M_O2 / (2 * _M_H2O)                 # 0.8881
O2_FROM_ELECTROLYSIS_PER_CH4 = H2O_ELECTROLYZED_PER_CH4 * O2_PER_KG_H2O  # 3.989


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


class IsruEngine:
    def __init__(self, catalog: Catalog, assumptions: Assumptions):
        self.catalog = catalog
        self.a = assumptions

    def assess(self, mission: Mission) -> IsruResult:
        qty = {}
        for item in mission.manifest:
            qty[item.component_id] = qty.get(item.component_id, 0.0) + item.qty
        return self.assess_quantities(qty)

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
        warnings: list[str] = []

        def avg_kw(component_id: str) -> tuple[float, float]:
            comp = self.catalog.get(component_id)
            n = quantities.get(component_id, 0.0)
            return n, n * comp.peak_power_kw * comp.duty_cycle

        steps: list[ChainStep] = []

        def step(key, cid, commodity, kwh_per_kg, prop_per_kg):
            n, kw = avg_kw(cid)
            thr = kw / kwh_per_kg if kwh_per_kg > 0 else 0.0
            steps.append(ChainStep(key, cid, n, kw, thr, commodity,
                                   thr * prop_per_kg, False))

        if "excavation" in chain and e_exc > 0:
            step("excavation", chain["excavation"], "H2O (net)", e_exc,
                 prop_per_ch4 / H2O_NET_PER_CH4)
        step("water_processing", chain["water_processing"], "H2O (net)", e_wat,
             prop_per_ch4 / H2O_NET_PER_CH4)
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

        # energy per kg of propellant, all steps at stoichiometric balance
        ch4_frac = 1.0 / prop_per_ch4
        spec = (H2O_ELECTROLYZED_PER_CH4 * e_h2o + CO2_PER_CH4 * e_co2 + e_sab) * ch4_frac \
            + e_liq + H2O_NET_PER_CH4 * (e_wat + e_exc) * ch4_frac

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
            net_water_kg_per_sol=kg_per_sol / prop_per_ch4 * H2O_NET_PER_CH4,
            water_for_return_load_t=load_t / prop_per_ch4 * H2O_NET_PER_CH4,
            spec_energy_kwh_per_kg=spec,
            energy_per_return_load_gwh=load_t * 1000.0 * spec / 1e6,
            full_scale_kw_required=full_scale_kw,
            o2_surplus_per_kg_ch4=o2_surplus,
            warnings=tuple(warnings),
        )
