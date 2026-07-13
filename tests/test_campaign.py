"""Campaign planner: surface-state carry-forward + capability gating
(spec origin: HANDOFF.md §5.3)."""
import copy

import pytest

from mars_manifest.campaign import CampaignPlanner


@pytest.fixture(scope="module")
def planner(catalog, baseline, manager):
    return CampaignPlanner(catalog, baseline, manager.capability_unlocks(),
                           manager.crewed_requires())


@pytest.fixture(scope="module")
def result(planner, campaign_4w):
    return planner.run(campaign_4w)


def test_four_windows_in_order(result):
    assert [w.window_id for w in result.windows] == ["2026-11", "2028-12", "2031-01", "2033-03"]


def test_precursor_window_unlocks_core_capabilities(result):
    w0 = result.windows[0]
    for flag in ("edl_proven", "power_baseload", "comms_established", "precision_landing",
                 "water_supply", "habitat_ready", "radiation_managed"):
        assert flag in w0.capabilities_after, f"{flag} should unlock after window 0"
    # life support is gated on the 1000-sol ECLSS demonstration clock: the
    # window-0 testbed has only ~600 sols of runtime by the next window
    assert "life_support_closed" not in w0.capabilities_after
    assert "life_support_closed" in result.windows[1].capabilities_after
    # return propellant is now gated on tonnes in the tank (1,400 t), not
    # hardware delivered: pilot chain makes ~269 t/window, so the gate retires
    # only after the window-2 scale-up
    assert "return_propellant_proven" not in w0.capabilities_after
    assert "return_propellant_proven" not in result.windows[1].capabilities_after
    assert "return_propellant_proven" in result.windows[2].capabilities_after


def test_propellant_accrues_and_gates_crew(result):
    cum = [w.propellant_cumulative_t for w in result.windows]
    assert cum == sorted(cum)
    # 1x chain ~269 t/synod nameplate, ramped at the 0.6 commissioning factor
    assert cum[0] == pytest.approx(0.6 * 269, abs=3)
    assert cum[2] > 1400                            # full load banked before crew
    assert all(w.power_derate == 1.0 for w in result.windows)  # generation keeps pace
    assert result.windows[0].isru_bottleneck == "electrolysis"


def test_first_crew_window_is_gated_and_allowed(result):
    assert not result.violations
    assert result.first_crew_window == "2033-03"


def test_surface_state_accumulates(result):
    # installed power grows monotonically as fission units land each window
    kwe = [w.installed_generation_kwe for w in result.windows]
    assert kwe == sorted(kwe)
    assert kwe[0] == pytest.approx(360.0)  # 9 units x 40 kWe from the precursor batch


def test_cumulative_rollups(result):
    c = result.cumulative
    assert c["ships"] == sum(w.ships for w in result.windows)
    assert c["total_launches"] == sum(w.total_launches for w in result.windows)
    # baseline: 16 tankers/ship -> every ship costs 17 launches
    assert c["total_launches"] == c["ships"] * 17


def test_premature_crew_is_blocked(planner, campaign_4w):
    # Crew in the very first window: nothing is on the surface yet, so every
    # prerequisite capability is missing. (Note: the full precursor batch
    # unlocks all crew gates after one window, so window 1 crew is legal.)
    campaign = copy.deepcopy(campaign_4w)
    crew_window = campaign.windows[3]
    crew_window.synod_index = 0
    campaign.windows = [crew_window]
    result = planner.run(campaign)
    assert result.violations
    assert result.first_crew_window is None
    blocked = [m for w in result.windows for m in w.missions if m.blocked]
    assert blocked and blocked[0].crewed


def test_earliest_window_is_advisory_not_blocking(result):
    # the full precursor batch flies 2028-rated hardware in 2026 by design
    w0 = result.windows[0]
    assert any("earliest" in msg for msg in w0.warnings)
    assert not result.violations


def test_water_confirmed_gates_the_fuel_factory(catalog, baseline, manager):
    # prospect-before-commit: without window-0 prospecting on the surface,
    # a mission that requires water_confirmed is blocked
    from pathlib import Path
    from mars_manifest.cli import load_campaign
    plan = load_campaign(Path(__file__).resolve().parents[1] / "inputs" / "program.json", catalog)
    planner = CampaignPlanner(catalog, baseline, manager.capability_unlocks(),
                              manager.crewed_requires())
    # full plan: prospecting lands window 0, factory flies window 1 -> no violations
    assert not planner.run(copy.deepcopy(plan)).violations
    # drop window 0: the factory launches blind -> blocked
    gutted = copy.deepcopy(plan)
    gutted.windows = gutted.windows[1:]
    result = planner.run(gutted)
    assert any("water_confirmed" in v for v in result.violations)
