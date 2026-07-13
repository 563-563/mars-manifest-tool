"""Anti-drift guard for the browser what-if overlay.

The scrollytelling page (the published "The Manifest" artifact, built by the
session's viz/build_scrolly.py) recomputes program figures live in the reader's
browser as they turn knobs. That is a SECOND implementation of the campaign
math, and the project's whole discipline is "one source of truth, no silent
drift" (CLAUDE.md). This test pins the exact closed-form relationships the
browser overlay's compute() relies on, checked against the real Python engine
across several knob settings. If the engine's shape ever changes (tanker
multiplier, launch-cost split, ISRU commissioning ramp, import decay, EDL
rule-of-three), one of these assertions breaks — which is the signal that the
JS overlay must be updated to match. The browser is only ever allowed to be a
faithful re-expression of what these assertions verify.

Overlay formulas mirrored here (see build_scrolly.py `compute()`):
  launches      = ships * (1 + tankers_per_ship)                    [packing.py]
  launch_cost   = ships*cargo_rate + ships*tankers*tanker_rate      [packing.launch_math]
  propellant    = commissioning-ramped nameplate * derate, summed   [campaign.py]
  import_req    = pop_before * decay[closure] * YEARS_PER_SYNOD      [campaign.py/city.py]
  edl_reliab.   = max(0, 1 - (-ln(1-0.95))/cum_ships)               [edl.demonstrated_reliability]
"""
import math
from pathlib import Path

import pytest

from mars_manifest.campaign import CampaignPlanner
from mars_manifest.city import (YEARS_PER_SYNOD, closure_stage, city_rules,
                                 load_city_ramp)
from mars_manifest.cli import load_campaign
from mars_manifest.isru import IsruEngine

ROOT = Path(__file__).resolve().parents[1]
KC = -math.log(1 - 0.95)  # rule-of-three constant ~2.9957

SCENARIOS = ["baseline", "optimistic", "conservative_feasibility"]


@pytest.fixture(scope="module")
def city():
    return load_city_ramp(ROOT / "inputs" / "city.json")


@pytest.fixture(scope="module")
def program(catalog):
    return load_campaign(ROOT / "inputs" / "program.json", catalog)


def _run(catalog, manager, city, scenario):
    a = manager.resolve(scenario)
    rules = {**manager.capability_unlocks(), **city_rules(city)}
    growth = city["growth"]["fleet_min_growth_per_synod"]["value"]
    planner = CampaignPlanner(catalog, a, rules, manager.crewed_requires(),
                              city=city, min_fleet_growth=growth)
    return a, planner


def _launch_rates(a):
    tier = a.get("cost.active_launch_cost")
    per_launch = a.per_launch_cost(tier)
    cargo = a.get("cost.cargo_ship_launch_cost_musd", per_launch)
    tanker = a.get("cost.tanker_launch_cost_musd", per_launch)
    return a.get("fleet.tankers_per_ship"), cargo, tanker


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_launch_and_cost_closed_form(catalog, manager, city, program, scenario):
    """launches = ships*(1+tankers); cost splits cargo vs tanker legs."""
    a, planner = _run(catalog, manager, city, scenario)
    tankers, cargo, tanker = _launch_rates(a)
    result = planner.run(program)
    for w in result.windows:
        if w.ships == 0:
            continue
        assert w.total_launches == w.ships * (1 + tankers), (scenario, w.window_id)
        expect_cost = w.ships * cargo + w.ships * tankers * tanker
        assert w.launch_cost_musd == pytest.approx(expect_cost), (scenario, w.window_id)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_demonstrated_reliability_rule_of_three(catalog, manager, city, program, scenario):
    """EDL demonstrated reliability = 1 - 3/N on cumulative planned landings."""
    _, planner = _run(catalog, manager, city, scenario)
    result = planner.run(program)
    cum = 0
    for w in result.windows:
        cum += w.ships
        expect = max(0.0, 1 - KC / cum) if cum else 0.0
        assert w.demonstrated_reliability == pytest.approx(expect, abs=1e-9), (scenario, w.window_id)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_import_ledger_closed_form(catalog, manager, city, program, scenario):
    """import_required = pop_before * decay[closure_at_start] * years_per_synod."""
    a, planner = _run(catalog, manager, city, scenario)
    decay = city["import_decay_t_per_person_year"]
    result = planner.run(program)
    pop_before = 0
    for w in result.windows:
        rate = decay.get(w.closure_stage, decay["none"])
        expect = pop_before * rate * YEARS_PER_SYNOD
        assert w.import_required_t == pytest.approx(expect, rel=1e-9, abs=1e-6), (scenario, w.window_id)
        pop_before = w.population


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_propellant_commissioning_ramp(catalog, manager, city, program, scenario):
    """Cumulative propellant = engine commissioning-ramp formula replicated from
    reconstructed per-window ISRU nameplate throughput + the window derate."""
    a, planner = _run(catalog, manager, city, scenario)
    isru = IsruEngine(catalog, a)
    commission = a.get("isru.commissioning_factor", 1.0)
    result = planner.run(program)

    delivered = {}
    prev_nameplate = 0.0
    cum = 0.0
    for w in result.windows:
        had_prior = bool(delivered)
        for m in program.windows[w.synod_index].missions:
            for it in m.manifest:
                delivered[it.component_id] = delivered.get(it.component_id, 0.0) + it.qty
        nameplate = isru.assess_quantities(delivered).tonnes_per_window
        if commission < 1.0 and had_prior:
            effective = prev_nameplate + commission * max(0.0, nameplate - prev_nameplate)
        else:
            effective = commission * nameplate
        cum += effective * w.power_derate
        prev_nameplate = nameplate
        assert cum == pytest.approx(w.propellant_cumulative_t, rel=1e-6, abs=1e-3), (scenario, w.window_id)
