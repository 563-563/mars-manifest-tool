"""ISRU chain model: rates, energy, bottleneck (isru.py).

Cross-checks against the domain grounding recorded in HANDOFF.md §2:
full-scale ISRU should come out ~1 MW continuous, water demand in the
hundreds of tonnes, and the pilot chain far short of one return load.
"""
import pytest

from mars_manifest.isru import (
    CO2_PER_CH4, H2O_ELECTROLYZED_PER_CH4, H2O_NET_PER_CH4,
    O2_FROM_ELECTROLYSIS_PER_CH4, IsruEngine,
)


@pytest.fixture(scope="module")
def result(catalog, baseline, precursor):
    return IsruEngine(catalog, baseline).assess(precursor)


def test_stoichiometry_constants():
    assert H2O_ELECTROLYZED_PER_CH4 == pytest.approx(4.49, abs=0.01)
    assert H2O_NET_PER_CH4 == pytest.approx(2.25, abs=0.01)
    assert CO2_PER_CH4 == pytest.approx(2.74, abs=0.01)
    assert O2_FROM_ELECTROLYSIS_PER_CH4 == pytest.approx(3.99, abs=0.01)


def test_electrolysis_is_the_bottleneck(result):
    assert result.bottleneck == "electrolysis"
    assert result.propellant_rate_kg_hr == pytest.approx(21.4, abs=0.2)
    # every other step has headroom
    others = [s for s in result.steps if s.key != "electrolysis"]
    assert all(s.propellant_rate_kg_hr > result.propellant_rate_kg_hr for s in others)


def test_pilot_scale_vs_return_load(result):
    # pilot chain at 85% availability: ~0.45 t/sol -> ~269 t per 600-sol window
    assert result.propellant_kg_per_sol == pytest.approx(448, abs=5)
    assert result.tonnes_per_window == pytest.approx(269, abs=3)
    assert 0.17 < result.fraction_of_return_load < 0.22
    assert result.years_to_return_load == pytest.approx(8.8, abs=0.2)


def test_full_scale_power_matches_domain_grounding(result):
    # HANDOFF.md §2: full-scale ISRU ~1 MW continuous. Chain at 85% availability
    # comes out ~850 kW — squarely the right order.
    assert result.full_scale_kw_required == pytest.approx(853, abs=15)
    assert result.spec_energy_kwh_per_kg == pytest.approx(7.65, abs=0.1)
    assert result.energy_per_return_load_gwh == pytest.approx(10.7, abs=0.2)


def test_excavation_step_present_with_headroom(result):
    exc = [s for s in result.steps if s.key == "excavation"]
    assert exc and exc[0].propellant_rate_kg_hr > result.propellant_rate_kg_hr


def test_water_demand_in_hundreds_of_tonnes(result):
    # HANDOFF.md §2: "water needed ~hundreds of t" per return load
    assert 500 < result.water_for_return_load_t < 800


def test_o2_balance_positive_at_baseline_of(result):
    assert result.o2_surplus_per_kg_ch4 > 0


def test_scaling_the_bottleneck(catalog, baseline, precursor):
    import copy
    mission = copy.deepcopy(precursor)
    for item in mission.manifest:
        if item.component_id == "water_electrolysis":
            item.qty = 5
    r = IsruEngine(catalog, baseline).assess(mission)
    # 5x electrolysis pushes the bottleneck to the next-slowest step (sabatier)
    assert r.bottleneck == "sabatier"
    assert r.propellant_rate_kg_hr > 50


def test_chain_design_one_load_per_synod(catalog, baseline):
    engine = IsruEngine(catalog, baseline)
    d = engine.size_chain()  # default: one return load per synod
    # target nameplate rate grossed up by availability
    assert d.target_rate_kg_hr == pytest.approx(111.6, abs=0.5)
    units = {s.key: s.units_required for s in d.steps}
    utils = {s.key: s.utilization for s in d.steps}
    assert units["electrolysis"] == 6
    assert units["co2_capture"] == 2
    assert units["sabatier"] == 3
    assert units["liquefaction"] == 2
    assert units["water_processing"] == 1
    # matched: big-ticket steps land at high utilization
    assert utils["electrolysis"] == pytest.approx(0.87, abs=0.02)
    assert utils["co2_capture"] == pytest.approx(0.97, abs=0.02)
    # granularity slack flagged where ceil() forces it
    assert any("sabatier" in n or "liquefaction" in n or "water_processing" in n
               for n in d.notes)
    # rollup: ~61 t of chain drags ~1 MW of power -> the domain constant again
    assert d.chain_mass_t == pytest.approx(61.0, abs=1.0)
    assert d.chain_avg_kw == pytest.approx(1050, abs=15)
    assert d.fission_units == 27
    assert d.total_mass_t == pytest.approx(265, abs=5)


def test_chain_design_custom_target(catalog, baseline):
    engine = IsruEngine(catalog, baseline)
    d = engine.size_chain(target_tonnes_per_synod=280)
    # ~pilot-scale target: one of each suffices except nothing extra
    assert all(s.units_required >= 1 for s in d.steps)
    assert d.steps[0].units_required >= 1
    small = {s.key: s.units_required for s in d.steps}
    assert small["electrolysis"] == 2  # 23.3 kg/hr needs 2 electrolyzers


def test_oxygen_only_fallback(manager, catalog, precursor):
    # DRA-5.0-style descope: LOX from CO2, methane from Earth, zero water risk
    a = manager.resolve("oxygen_only_isru")
    r = IsruEngine(catalog, a).assess(precursor)
    assert r.mode == "oxygen_only"
    assert r.bottleneck == "o2_electrolysis"
    assert r.propellant_rate_kg_hr == pytest.approx(11.6, abs=0.1)
    assert r.water_for_return_load_t == 0.0
    assert r.ch4_import_t_per_load == pytest.approx(304.3, abs=0.5)
    assert r.ch4_import_ships_per_load == 4
    assert r.spec_energy_kwh_per_kg == pytest.approx(13.7, abs=0.1)


def test_high_energy_scenario_matches_handmer_anchor(manager, catalog, precursor):
    # Handmer all-in figure (~2x our chain math): spec ~15 kWh/kg, ~1.7 MW full-scale
    a = manager.resolve("isru_high_energy")
    r = IsruEngine(catalog, a).assess(precursor)
    assert r.spec_energy_kwh_per_kg == pytest.approx(15.3, abs=0.2)
    assert r.full_scale_kw_required == pytest.approx(1706, abs=25)
    assert r.bottleneck == "electrolysis"
