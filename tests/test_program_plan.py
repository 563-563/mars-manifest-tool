"""The program-plan baseline: redundant window 0 + rate-matched waves."""
from pathlib import Path

import pytest

from mars_manifest.campaign import CampaignPlanner
from mars_manifest.cli import load_campaign

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def plan_result(catalog, baseline, manager):
    campaign = load_campaign(ROOT / "examples" / "program_plan.yaml", catalog)
    planner = CampaignPlanner(catalog, baseline, manager.capability_unlocks(),
                              manager.crewed_requires())
    return planner.run(campaign)


def test_no_violations_and_crew_on_schedule(plan_result):
    assert not plan_result.violations
    assert plan_result.first_crew_window == "2033-03"


def test_propellant_gate_retires_with_the_fuel_factory(plan_result):
    w = {r.window_id: r for r in plan_result.windows}
    # redundant precursor (2x chain) banks ~537 t; matched buy closes the gate
    assert w["2026-11"].propellant_cumulative_t == pytest.approx(537, abs=5)
    assert "return_propellant_proven" in w["2028-12"].new_capabilities
    # crew arrives with several full return loads banked
    assert w["2033-03"].propellant_cumulative_t > 5 * 1400


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
    # two matched chains + the redundant pilot pair
    assert inv["water_electrolysis"] == 14
    assert inv["habitat_module"] == 10
    # power generation is the biggest thing on Mars, as the research predicted
    top_group = max(final.surface_by_group, key=final.surface_by_group.get)
    assert top_group == "Power generation"
    # installed generation stays ahead of the surface load
    assert final.installed_generation_kwe >= final.surface_avg_load_kw
