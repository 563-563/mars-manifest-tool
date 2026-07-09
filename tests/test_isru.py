"""ISRU chain model: rates, energy, bottleneck (isru.py).

Cross-checks against the domain grounding in HANDOFF.md §2:
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
    # pilot chain: ~0.53 t/sol -> ~316 t per 600-sol window = ~23% of one load
    assert result.propellant_kg_per_sol == pytest.approx(527, abs=5)
    assert result.tonnes_per_window == pytest.approx(316, abs=3)
    assert 0.20 < result.fraction_of_return_load < 0.25
    assert result.years_to_return_load == pytest.approx(7.5, abs=0.2)


def test_full_scale_power_matches_domain_grounding(result):
    # HANDOFF §2: full-scale ISRU ~1 MW continuous. Chain-only comes out ~720 kW;
    # with mining/thermal overheads that is the right order.
    assert result.full_scale_kw_required == pytest.approx(721, abs=10)
    assert result.spec_energy_kwh_per_kg == pytest.approx(7.6, abs=0.1)
    assert result.energy_per_return_load_gwh == pytest.approx(10.6, abs=0.2)


def test_water_demand_in_hundreds_of_tonnes(result):
    # HANDOFF §2: "water needed ~hundreds of t" per return load
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
