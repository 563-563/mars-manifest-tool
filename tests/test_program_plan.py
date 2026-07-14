"""The program-plan baseline: redundant window 0 + rate-matched waves."""
from pathlib import Path

import pytest

from mars_manifest.campaign import CampaignPlanner
from mars_manifest.cli import load_campaign

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def plan_result(catalog, baseline, manager):
    from mars_manifest.city import city_rules, load_city_ramp
    city = load_city_ramp(ROOT / "inputs" / "city.json")
    rules = {**manager.capability_unlocks(), **city_rules(city)}
    growth = city["growth"]["fleet_min_growth_per_synod"]["value"]
    campaign = load_campaign(ROOT / "inputs" / "program.json", catalog)
    planner = CampaignPlanner(catalog, baseline, rules, manager.crewed_requires(),
                              city=city, min_fleet_growth=growth)
    return planner.run(campaign)


def test_no_violations_and_crew_on_schedule(plan_result):
    assert not plan_result.violations
    assert plan_result.first_crew_window == "2035-05"


def test_propellant_gate_retires_with_the_fuel_factory(plan_result):
    w = {r.window_id: r for r in plan_result.windows}
    # pilot chain ramps in over its first synod (commissioning factor 0.6),
    # so window 0 banks ~322 t rather than the ~537 t nameplate
    assert w["2031-01"].propellant_cumulative_t == pytest.approx(322, abs=5)
    # the doubled chain closes the 1,400 t gate at 2033 with ~2,793 t banked
    # (just shy of two loads): the Jan-2035 return demo burns one, leaving a
    # full crew load at the May-2035 commit, refilled at ~3.2 loads/synod
    assert "return_propellant_proven" in w["2033-03"].new_capabilities
    assert w["2033-03"].propellant_cumulative_t == pytest.approx(2793, abs=15)
    assert w["2033-03"].propellant_cumulative_t > 1400
    # crew lands 2035 on ~5 full return loads
    assert w["2035-05"].propellant_cumulative_t > 5 * 1400


def test_honest_fleet_counts(plan_result):
    # fleet sized to cargo at <=90% mass, subject to the cumulative >=2x
    # growth floor ("no air freight"): 2035 and 2041 are growth-floored and
    # topped up with risk depth; 2037/2039 are genuinely cargo-bound
    assert [w.ships for w in plan_result.windows] == [5, 10, 15, 34, 97, 161]


def test_every_window_fits_its_fleet(plan_result, baseline):
    cap = baseline.get("fleet.payload_mass_per_ship_t")
    for w in plan_result.windows:
        assert w.mass_delivered_t <= w.ships * cap, w.window_id
        assert w.power_derate == 1.0, f"{w.window_id}: power fell behind the load"


def test_surface_state_lays_flat(plan_result):
    hw = [w.surface_hardware_t for w in plan_result.windows]
    assert hw == sorted(hw)  # hardware only accumulates
    final = plan_result.windows[-1]
    inv = {cid: qty for cid, qty, _ in final.surface_inventory}
    # pilot (2) + doubled factory (12) + crew-wave hot spares (3+2) +
    # village chains (12) + town/settlement growth (6+8)
    assert inv["water_electrolysis"] == 45
    # all habitats are inflatables (honest ~75 m3 stowed volume): 5 pre-village
    # (1+4) + 299 city-era, sized to the 76.5 m3/person pressurized standard
    # with settlement growth headroom; habitat_module survives only in fixtures
    assert "habitat_module" not in inv
    assert inv["habitat_inflatable"] == 304
    # power and habitat dominate the city-era surface, per the research
    top_group = max(final.surface_by_group, key=final.surface_by_group.get)
    assert top_group in ("Power generation", "Habitat & life support")
    # installed generation stays ahead of the surface load
    assert final.installed_generation_kwe >= final.surface_avg_load_kw


def test_population_is_first_class(plan_result):
    # zero through the robotic era; first crew 2035; the ramp runs one synod
    # earlier than the conservative program (village 2037 ... settlement 2041)
    pops = [w.population for w in plan_result.windows]
    assert pops == [0, 0, 12, 112, 512, 1112]
    # blocked missions must not add settlers: covered by delivery gating
    # (population increments live next to landings, after the blocked check)


def test_population_appears_in_enablements(plan_result, catalog, baseline):
    from mars_manifest.report import window_enablements
    lines = window_enablements(plan_result.windows[2], catalog, baseline)
    assert any("Resident population: 12" in ln for ln in lines)
    robotic = window_enablements(plan_result.windows[0], catalog, baseline)
    assert not any("Resident population" in ln for ln in robotic)


def test_city_ramp_milestones_and_ledger(plan_result):
    w = {r.window_id: r for r in plan_result.windows}
    # prospecting fast path retires water_confirmed in window 0 (30 sols)
    assert "water_confirmed" in w["2031-01"].capabilities_after
    # milestones fire on the researched thresholds
    assert "survival_floor" in w["2037-07"].new_capabilities
    assert "settlement_established" in w["2041-11"].new_capabilities
    assert "industrial_autarky" not in w["2041-11"].capabilities_after
    # closure ladder progresses and the import rate walks the decay curve
    assert w["2037-07"].closure_stage == "none"          # rate keyed to window START
    assert w["2039-09"].closure_stage == "closure_gen_2"
    assert w["2041-11"].closure_stage == "closure_gen_3"
    assert w["2041-11"].import_rate_t_py == 0.8
    # every populated window covers its recurring-import requirement
    for r in plan_result.windows:
        if r.population and r.import_required_t:
            assert r.import_delivered_t >= r.import_required_t, r.window_id
    # no growth-rule or deficit warnings anywhere
    all_warnings = " ".join(x for r in plan_result.windows for x in r.warnings)
    assert "below the" not in all_warnings and "deficit" not in all_warnings
    assert "over capacity" not in all_warnings


def test_edl_and_water_metrics_in_enablements(plan_result, catalog, baseline):
    from mars_manifest.report import window_enablements
    # crew window has both new C5 metrics
    crew = window_enablements(plan_result.windows[2], catalog, baseline)
    text = " ".join(crew)
    assert "EDL track record" in text
    assert "Water independence" in text and "months" in text
    # robotic window 0 has EDL confidence but no water-independence (no crew)
    w0 = window_enablements(plan_result.windows[0], catalog, baseline)
    assert any("EDL track record" in ln for ln in w0)
    assert not any("Water independence" in ln for ln in w0)


def test_habitat_and_eclss_ride_the_same_hull(catalog, baseline, manager):
    """The demo set is complementary, not redundant: an ECLSS without a sealed
    volume demonstrates nothing (LMLSTP/BEAM precedent), so the balanced packer
    bundles each habitat with an ECLSS unit on one hull, in every window."""
    from mars_manifest.budgets import BudgetEngine
    from mars_manifest.packing import PackingEngine
    campaign = load_campaign(ROOT / "inputs" / "program.json", catalog)
    be, pe = BudgetEngine(catalog, baseline), PackingEngine(catalog, baseline)
    for window in campaign.windows:
        for mission in window.missions:
            packing = pe.pack(mission, be.compute(mission))
            for ship in packing.ships:
                inv = {cid: q for cid, q in ship.items}
                habs = inv.get("habitat_inflatable", 0) + inv.get("habitat_module", 0)
                assert habs == inv.get("eclss_habitat", 0), (
                    f"{window.id} ship {ship.index}: {habs} habitats vs "
                    f"{inv.get('eclss_habitat', 0)} ECLSS units")


def test_life_support_demo_requires_the_habitat(catalog, baseline, manager):
    """Dropping the window-0 habitat must delay life_support_closed (the loop
    has no sealed volume to run in until 2035's habitats land) and block crew."""
    import copy
    from mars_manifest.city import city_rules, load_city_ramp
    city = load_city_ramp(ROOT / "inputs" / "city.json")
    rules = {**manager.capability_unlocks(), **city_rules(city)}
    campaign = load_campaign(ROOT / "inputs" / "program.json", catalog)
    crippled = copy.deepcopy(campaign)
    m0 = crippled.windows[0].missions[0]
    m0.manifest = [it for it in m0.manifest if it.component_id != "habitat_inflatable"]
    planner = CampaignPlanner(catalog, baseline, rules, manager.crewed_requires(), city=city)
    result = planner.run(crippled)
    w = {r.window_id: r for r in result.windows}
    assert "life_support_closed" not in w["2035-05"].capabilities_after
    assert any("first_crew" in v or "blocked" in v for v in result.violations)
    assert result.first_crew_window != "2035-05"
