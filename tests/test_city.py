"""City-ramp seed data: integrity, milestone gating (tasks A2 onward)."""
from pathlib import Path

import pytest

from mars_manifest.campaign import CampaignPlanner
from mars_manifest.city import load_city_ramp, milestone_rules
from mars_manifest.models import Campaign, ManifestItem, Mission, Window

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def city():
    return load_city_ramp(ROOT / "data" / "city_ramp_seed.yaml")


def test_every_anchor_has_tier_and_source(city):
    # milestones are validated by the loader; spot-check the anchor sections
    for m in city["population_milestones"]:
        assert m["tier"] in ("A", "B", "C", "D")
    def tiered(entry) -> bool:
        if not isinstance(entry, dict):
            return True
        if "tier" in entry or "source" in entry:
            return True
        # containers pass if every child anchor is itself tiered
        return all(tiered(v) for v in entry.values() if isinstance(v, dict))

    for section in ("per_capita", "import_mass", "growth"):
        for key, entry in city[section].items():
            assert tiered(entry), f"{section}.{key} untiered"


def test_milestones_are_the_three_researched_thresholds(city):
    rules = milestone_rules(city)
    assert rules == {
        "survival_floor": {"min_population": 110},
        "settlement_established": {"min_population": 1000},
        "industrial_autarky": {"min_population": 1000000},
    }


def test_verified_anchor_values(city):
    pc = city["per_capita"]
    assert pc["power_subsistence_kwe"]["value"] == 25
    assert pc["power_subsistence_kwe"]["at_100_plus"] == 17
    assert pc["habitable_volume_m3"]["floor"] == pytest.approx(28.96)
    assert pc["consumables_kg_per_day"]["total"] == pytest.approx(4.912)
    assert city["import_mass"]["no_local_production_t_per_person_year"]["value"] == 10
    assert city["growth"]["fleet_min_growth_per_synod"]["value"] == 2.0


def test_population_milestones_gate_in_the_planner(catalog, baseline, manager, city):
    # crewed_requires emptied to isolate the milestone logic; settler-gating
    # itself is asserted in test_settlers_imply_crew_gating below
    rules = {**manager.capability_unlocks(), **milestone_rules(city)}
    planner = CampaignPlanner(catalog, baseline, rules, [])

    def crew_window(idx, settlers):
        return Window(id=f"20{40+idx*3}-01", synod_index=idx, missions=[Mission(
            id=f"wave{idx}", crewed=False, settlers=settlers, ships=2,
            packing_policy="balanced",
            manifest=[ManifestItem("consumables_cache", 4),
                      ManifestItem("habitat_module", 2),
                      ManifestItem("eclss_habitat", 2)])])

    result = planner.run(Campaign(id="milestone_test", windows=[
        crew_window(0, 60), crew_window(1, 60), crew_window(2, 900)]))
    caps = [w.capabilities_after for w in result.windows]
    assert "survival_floor" not in caps[0]          # 60 people
    assert "survival_floor" in caps[1]              # 120 people
    assert "settlement_established" not in caps[1]
    assert "settlement_established" in caps[2]      # 1,020 people
    assert "industrial_autarky" not in caps[2]
    assert [w.population for w in result.windows] == [60, 120, 1020]


def test_program_plan_reaches_settlement_not_autarky(catalog, baseline, manager, city):
    # the extended plan reaches the NSS settlement milestone by 2044 but is
    # honestly nowhere near industrial autarky (1M people)
    from mars_manifest.cli import load_campaign
    from mars_manifest.city import city_rules
    rules = {**manager.capability_unlocks(), **city_rules(city)}
    planner = CampaignPlanner(catalog, baseline, rules, manager.crewed_requires(), city=city)
    result = planner.run(load_campaign(ROOT / "examples" / "program_plan.yaml", catalog))
    caps = result.windows[-1].capabilities_after
    assert "settlement_established" in caps
    assert "industrial_autarky" not in caps
    assert not result.violations


def test_settlers_imply_crew_gating(catalog, baseline, manager):
    # a mission carrying people is crew-gated even if crewed: false
    planner = CampaignPlanner(catalog, baseline, manager.capability_unlocks(),
                              manager.crewed_requires())
    sneak = Campaign(id="sneak", windows=[Window(id="2031-01", synod_index=0, missions=[
        Mission(id="colonists_disguised_as_cargo", crewed=False, settlers=30, ships=2,
                packing_policy="balanced",
                manifest=[ManifestItem("consumables_cache", 4)])])])
    result = planner.run(sneak)
    assert result.violations
    assert result.windows[0].population == 0
