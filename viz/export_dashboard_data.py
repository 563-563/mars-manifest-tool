"""Dump engine results across scenarios as JSON for the dashboard artifacts.

Run from the repo: `python viz/export_dashboard_data.py` -> viz/dashboard_data.json.
Then `python viz/build_scrolly.py` -> viz/mars_manifest_story.html."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mars_manifest.budgets import BudgetEngine
from mars_manifest.campaign import CampaignPlanner
from mars_manifest.catalog import Catalog
from mars_manifest.cli import load_campaign, load_mission
from mars_manifest.packing import PackingEngine
from mars_manifest.scenarios import ScenarioManager

catalog = Catalog.load(ROOT / "inputs" / "catalog.csv")
manager = ScenarioManager.load(ROOT / "inputs" / "assumptions.json")
mission = load_mission(ROOT / "examples" / "precursor_2026.yaml", catalog)
mission_bal = load_mission(ROOT / "examples" / "precursor_2026_balanced.yaml", catalog)
campaign = load_campaign(ROOT / "inputs" / "program.json", catalog)
# the program baseline = the lifecycle-trimmed redundant fleet flying window 0
mission_red = campaign.windows[0].missions[0]
from mars_manifest.city import city_rules, load_city_ramp
CITY = load_city_ramp(ROOT / "inputs" / "city.json")
RULES = {**manager.capability_unlocks(), **city_rules(CITY)}


def loss_dump(engine, packing):
    lt = engine.loss_tolerance(packing, RULES)
    return {"tolerant": lt.tolerant,
            "ships": [[i, list(caps)] for i, caps in lt.vulnerable_ships],
            "at_risk": list(lt.capabilities_at_risk)}


def ship_dump(p):
    return [{"i": s.index, "mass": s.mass_t, "vol": s.volume_m3,
             "mu": s.mass_utilisation, "vu": s.volume_utilisation,
             "items": [[d[0], round(d[1], 3), round(d[2], 3), round(d[3], 2)]
                       for d in s.manifest_detail]} for s in p.ships]

SCENARIOS = ["baseline"]  # console shows the program baseline only (other presets remain in the tool/CLI)
out = {"scenarios": {}, "campaign": None}

for name in SCENARIOS:
    a = manager.resolve(name)
    b = BudgetEngine(catalog, a).compute(mission)
    p = PackingEngine(catalog, a).pack(mission, b)
    lm = p.launch
    out["scenarios"][name] = {
        "power_path": b.power_path,
        "loads": {"avg_kw": b.loads.avg_kw, "peak_kw": b.loads.simultaneous_peak_kw},
        "mass": {
            "fixed": b.mass.fixed_hardware_t, "gen": b.mass.generation_t,
            "storage": b.mass.storage_t, "spares": b.mass.spares_t,
            "contingency": b.mass.contingency_t, "total": b.mass.grand_total_t,
            "capacity": b.capacity.mass_capacity_t, "util": b.capacity.mass_utilisation,
        },
        "volume": {"effective": b.volume.effective_m3, "capacity": b.capacity.volume_capacity_m3},
        "solar": {"array_m2": b.solar.array_m2, "array_t": b.solar.array_mass_t,
                  "night_t": b.solar.night_battery_t, "dust_t": b.solar.dust_storm_battery_t,
                  "dust_crit": b.solar.dust_storm_battery_critical_t,
                  "infeasible": b.solar.dust_storm_infeasible},
        "fission": {"units": b.fission.units, "mass_t": b.fission.mass_t,
                    "buffer_t": b.fission.buffer_battery_t,
                    "unit_kwe": a.get("power.fission_unit_kwe")},
        "cost": {"cargo_low": b.cost.cargo_low_musd, "cargo_high": b.cost.cargo_high_musd},
        "ships": ship_dump(p),
        "spof": [list(x) for x in p.single_points],
        "launch": {"total": lm.total_launches, "tankers": lm.tankers_per_ship,
                   "cargo_rate": lm.cargo_ship_rate_musd, "tanker_rate": lm.tanker_rate_musd,
                   "split": lm.split_rates, "cost": lm.launch_cost_musd, "tier": lm.launch_cost_tier},
        "warnings": list(b.warnings),
    }
    eng = PackingEngine(catalog, a)
    p_bal = eng.pack(mission_bal, BudgetEngine(catalog, a).compute(mission_bal))
    b_red = BudgetEngine(catalog, a).compute(mission_red)
    # program windows no longer pin `ships` (top-down sizing); size window 0
    # the way the planner does so capacity/util can be reported
    if not mission_red.ships:
        _fill = a.get("fleet.target_fill", 0.9)
        _cap = a.get("fleet.payload_mass_per_ship_t")
        mission_red.ships = max(1, math.ceil(b_red.mass.grand_total_t / (_cap * _fill)))
        b_red = BudgetEngine(catalog, a).compute(mission_red)
    p_red = eng.pack(mission_red, b_red)
    lm_red = p_red.launch
    out["scenarios"][name].update({
        "ships_balanced": ship_dump(p_bal),
        "ships_redundant": ship_dump(p_red),
        "redundant_total_t": round(b_red.mass.grand_total_t, 1),
        "loss": {"pinned": loss_dump(eng, p),
                 "balanced": loss_dump(eng, p_bal),
                 "redundant": loss_dump(eng, p_red)},
        # full budget dataset for the program-baseline mission, so the
        # mission-level panels can follow the packing-view toggle
        "red": {
            "power_path": b_red.power_path,
            "loads": {"avg_kw": b_red.loads.avg_kw, "peak_kw": b_red.loads.simultaneous_peak_kw},
            "mass": {"fixed": b_red.mass.fixed_hardware_t, "gen": b_red.mass.generation_t,
                     "storage": b_red.mass.storage_t, "spares": b_red.mass.spares_t,
                     "contingency": b_red.mass.contingency_t, "total": b_red.mass.grand_total_t,
                     "capacity": b_red.capacity.mass_capacity_t, "util": b_red.capacity.mass_utilisation},
            "volume": {"effective": b_red.volume.effective_m3, "capacity": b_red.capacity.volume_capacity_m3},
            "solar": {"array_m2": b_red.solar.array_m2, "array_t": b_red.solar.array_mass_t,
                      "night_t": b_red.solar.night_battery_t, "dust_t": b_red.solar.dust_storm_battery_t,
                      "dust_crit": b_red.solar.dust_storm_battery_critical_t,
                      "infeasible": b_red.solar.dust_storm_infeasible},
            "fission": {"units": b_red.fission.units, "mass_t": b_red.fission.mass_t,
                        "buffer_t": b_red.fission.buffer_battery_t,
                        "unit_kwe": a.get("power.fission_unit_kwe")},
            "cost": {"cargo_low": b_red.cost.cargo_low_musd, "cargo_high": b_red.cost.cargo_high_musd},
            "launch": {"total": lm_red.total_launches, "tankers": lm_red.tankers_per_ship,
                       "cargo_rate": lm_red.cargo_ship_rate_musd, "tanker_rate": lm_red.tanker_rate_musd,
                       "split": lm_red.split_rates, "cost": lm_red.launch_cost_musd,
                       "tier": lm_red.launch_cost_tier},
        },
    })

from mars_manifest.isru import IsruEngine

a = manager.resolve("baseline")


def isru_dump(ir):
    return {
        "steps": [{"key": s.key, "cid": s.component_id, "units": s.units, "kw": s.avg_kw,
                   "thr": round(s.throughput_kg_hr, 1), "commodity": s.commodity,
                   "prop": round(s.propellant_rate_kg_hr, 2)} for s in ir.steps],
        "bottleneck": ir.bottleneck,
        "rate": round(ir.propellant_rate_kg_hr, 2),
        "kg_sol": round(ir.propellant_kg_per_sol),
        "t_window": round(ir.tonnes_per_window, 1),
        "load_t": ir.return_load_t,
        "frac": round(ir.fraction_of_return_load, 4),
        "years": round(ir.years_to_return_load, 1),
        "water_t": round(ir.water_for_return_load_t),
        "spec": round(ir.spec_energy_kwh_per_kg, 2),
        "gwh": round(ir.energy_per_return_load_gwh, 2),
        "full_kw": round(ir.full_scale_kw_required),
        "full_rate": round(ir.return_load_t * 1000 /
                           (a.get("isru.production_sols_per_synod") * a.get("power.sol_hours")
                            * a.get("isru.plant_availability")), 1),
        "avail": a.get("isru.plant_availability"),
    }


isru_engine = IsruEngine(catalog, a)
out["isru"] = {"pinned": isru_dump(isru_engine.assess(mission)),
               "redundant": isru_dump(isru_engine.assess(mission_red))}
design = isru_engine.size_chain()
out["isru"]["design"] = {
    "steps": [[s.key, s.units_required, round(s.utilization, 3), round(s.mass_t, 1),
               round(s.avg_kw)] for s in design.steps],
    "chain_mass": round(design.chain_mass_t, 1),
    "chain_kw": round(design.chain_avg_kw),
    "fission_units": design.fission_units,
    "fission_mass": round(design.fission_mass_t),
    "buffer_t": round(design.buffer_battery_t, 1),
    "total": round(design.total_mass_t, 1),
}

planner = CampaignPlanner(catalog, a, RULES, manager.crewed_requires(), city=CITY)
r = planner.run(campaign)

from mars_manifest.requirements import RequirementsEngine, load_requirements
reqs = load_requirements(ROOT / "inputs" / "requirements.json")
matrix = RequirementsEngine(catalog, a, RULES).evaluate(reqs, r)
req_by_id = {x.id: x for x in reqs}
out["requirements"] = {
    "counts": matrix.counts,
    "by_window": {k: list(v) for k, v in matrix.by_window.items()},
    "open": list(matrix.open_ids),
    "rows": [{"id": v.requirement.id, "lvl": v.requirement.level,
              "parent": v.requirement.parent or "",
              "stmt": v.requirement.statement, "method": v.requirement.method,
              "rationale": v.requirement.rationale,
              "planned": v.requirement.planned_window or
                         ("every window" if v.requirement.recurring else "rollup"),
              "actual": v.closed_window or "",
              "status": v.status} for v in matrix.verdicts],
}

# --- what-if overlay primitives -------------------------------------------
# Per-window ISRU nameplate throughput (tonnes/synod at full rate on the
# cumulative delivered chain) + settlers, so the browser what-if engine can
# replay the campaign's commissioning-ramp formula exactly. ISRU nameplate
# depends only on the delivered chain hardware (throughput-bound), so it is
# reconstructed from the manifests — knob-independent, matches state.delivered.
from mars_manifest.city import YEARS_PER_SYNOD
_delivered: dict[str, float] = {}
_nameplate_by_id: dict[str, float] = {}
_settlers_by_id: dict[str, int] = {}
for _w in sorted(campaign.windows, key=lambda w: w.synod_index):
    _stt = 0
    for _m in _w.missions:
        for _it in _m.manifest:
            _delivered[_it.component_id] = _delivered.get(_it.component_id, 0.0) + _it.qty
        _stt += _m.settlers
    _nameplate_by_id[_w.id] = round(
        isru_engine.assess_quantities(_delivered).tonnes_per_window, 3)
    _settlers_by_id[_w.id] = _stt

# baseline parameter block the browser overlay is calibrated against
out["params"] = {
    "tankers_per_ship": a.get("fleet.tankers_per_ship"),
    "payload_mass_per_ship_t": a.get("fleet.payload_mass_per_ship_t"),
    "cost_tiers": a.get("cost.per_launch_cost_musd"),
    "active_launch_cost": a.get("cost.active_launch_cost"),
    "spacex_internal": {"cargo": 30, "tanker": 12},   # from spacex_internal scenario
    "return_propellant_t": a.get("isru.return_propellant_t"),
    "commissioning_factor": a.get("isru.commissioning_factor"),
    "plant_availability": a.get("isru.plant_availability"),
    "years_per_synod": YEARS_PER_SYNOD,
    "import_decay": CITY["import_decay_t_per_person_year"],
    "edl": {"base": a.get("edl.success_prob_base"),
            "improve": a.get("edl.success_prob_improvement_per_synod"),
            "max": a.get("edl.max_prob")},
    "spec_energy_kwh_per_kg": round(isru_engine.assess(mission_red).spec_energy_kwh_per_kg, 3),
    "full_scale_kw": round(isru_engine.assess(mission_red).full_scale_kw_required),
}

from mars_manifest.lifecycle import analyze
rep = analyze(r, catalog, a)
out["lifecycle"] = {
    "curve": [{"id": pt.window_id, "retired": list(pt.retired),
               "wt": round(pt.weight_retired, 1),
               "cum": round(pt.cumulative_fraction, 3)} for pt in rep.risk_curve],
    "idle_ty": round(rep.idle_tonne_years, 1),
    "findings": list(rep.findings),
}
wlist = list(r.windows)
out["campaign"] = {
    "windows": [{
        "id": w.window_id, "objective": w.objective, "ships": w.ships,
        "synod_index": w.synod_index,
        "settlers": _settlers_by_id.get(w.window_id, 0),
        "isru_nameplate_t": _nameplate_by_id.get(w.window_id, 0.0),
        "derate": round(w.power_derate, 4),
        "launches": w.total_launches, "mass": w.mass_delivered_t,
        "kwe": w.installed_generation_kwe, "launch_cost": w.launch_cost_musd,
        "prop": round(w.propellant_cumulative_t),
        "prop_produced": round(w.propellant_produced_t, 2),
        "new_caps": list(w.new_capabilities),
        "pop": w.population, "closure": w.closure_stage,
        "imp_req": round(w.import_required_t), "imp_del": round(w.import_delivered_t),
        "hardware_t": round(w.surface_hardware_t, 1),
        "load_kw": round(w.surface_avg_load_kw),
        "enables": __import__("mars_manifest.report", fromlist=["window_enablements"])
                   .window_enablements(w, catalog, a,
                                       wlist[i + 1].window_id if i + 1 < len(wlist) else None),
        "groups": {g: round(m, 1) for g, m in sorted(w.surface_by_group.items())},
        "inv": [[cid, round(qty, 1), round(mass, 1)] for cid, qty, mass in w.surface_inventory],
        "crewed": any(m.crewed and not m.blocked for m in w.missions),
    } for i, w in enumerate(wlist)],
    "cumulative": r.cumulative, "first_crew": r.first_crew_window,
}

dest = Path(__file__).parent / "dashboard_data.json"
dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(f"wrote {dest} ({dest.stat().st_size} bytes)")
