"""Packing + launch math regressions (HANDOFF.md §5.2 and §7)."""
import pytest

from mars_manifest.budgets import BudgetEngine
from mars_manifest.packing import PackingEngine


@pytest.fixture(scope="module")
def packed(catalog, baseline, precursor):
    budget = BudgetEngine(catalog, baseline).compute(precursor)
    return PackingEngine(catalog, baseline).pack(precursor, budget)


def test_five_ship_batch(packed):
    assert packed.ship_count == 5
    assert not packed.warnings


def test_per_ship_rollup_matches_workbook(packed):
    ships = {s.index: s for s in packed.ships}
    # §7: Ship3/power ~81 t / 330 m3; Ship5/habitat ~45 t / 425 m3
    assert ships[3].mass_t == pytest.approx(80.67, abs=0.05)
    assert ships[3].volume_m3 == pytest.approx(330.08, abs=0.1)
    assert ships[5].mass_t == pytest.approx(45.0, abs=0.01)
    assert ships[5].volume_m3 == pytest.approx(425.0, abs=0.01)
    # remaining ships from the workbook's per-ship rollup
    assert ships[1].mass_t == pytest.approx(3.0, abs=0.01)
    assert ships[2].mass_t == pytest.approx(11.0, abs=0.01)
    assert ships[4].mass_t == pytest.approx(27.0, abs=0.01)
    # everything under 100 t / 1,000 m3
    for s in packed.ships:
        assert s.mass_t <= 100
        assert s.volume_m3 <= 1000


def test_launch_math_low_and_high(catalog, baseline, precursor):
    engine = PackingEngine(catalog, baseline)
    budget = BudgetEngine(catalog, baseline).compute(precursor)
    low = engine.pack(precursor, budget, tankers_per_ship=10, launch_cost_tier="near_term")
    high = engine.pack(precursor, budget, tankers_per_ship=16, launch_cost_tier="near_term")
    # §7: 55 launches (10 tankers) to 85 (16); near-term campaign $4.95B–$7.65B
    assert low.launch.total_launches == 55
    assert high.launch.total_launches == 85
    assert low.launch.launch_cost_musd == pytest.approx(4950.0)
    assert high.launch.launch_cost_musd == pytest.approx(7650.0)


def test_aspirational_tier(catalog, baseline, precursor):
    engine = PackingEngine(catalog, baseline)
    budget = BudgetEngine(catalog, baseline).compute(precursor)
    r = engine.pack(precursor, budget, tankers_per_ship=10, launch_cost_tier="aspirational")
    assert r.launch.launch_cost_musd == pytest.approx(110.0)  # 55 x $2M


def test_auto_assignment_without_explicit_ships(catalog, baseline, precursor):
    import copy
    mission = copy.deepcopy(precursor)
    for item in mission.manifest:
        item.ship = None
    mission.ships = None
    mission.power_ship = None
    budget = BudgetEngine(catalog, baseline).compute(mission)
    packed = PackingEngine(catalog, baseline).pack(mission, budget)
    # FFD should need no more ships than the hand-packed batch
    assert packed.ship_count <= 5
    for s in packed.ships:
        assert s.mass_t <= 100
        assert s.volume_m3 <= 1000


def test_balanced_packing_spreads_redundancy(catalog, baseline):
    from mars_manifest.cli import load_mission
    from pathlib import Path
    from mars_manifest.budgets import BudgetEngine
    mission = load_mission(Path(__file__).resolve().parents[1] / "examples" / "precursor_2026_balanced.yaml", catalog)
    budget = BudgetEngine(catalog, baseline).compute(mission)
    packed = PackingEngine(catalog, baseline).pack(mission, budget)
    assert packed.policy == "balanced"
    assert packed.ship_count == 5
    # fission units spread across at least 4 ships (anti-affinity)
    fission_ships = [s.index for s in packed.ships
                     if any(cid == "fission_unit" for cid, _ in s.items)]
    assert len(fission_ships) >= 4
    # loads actually balanced: no near-empty ship, no dominant ship
    masses = [s.mass_t for s in packed.ships]
    assert min(masses) > 25 and max(masses) < 60
    # spares fly as explicit cargo: packed total = grand total - contingency
    packed_mass = sum(masses)
    expected = budget.mass.grand_total_t - budget.mass.contingency_t
    assert packed_mass == pytest.approx(expected, abs=0.1)
    for s in packed.ships:
        assert s.mass_t <= 100 and s.volume_m3 <= 1000


def test_single_point_of_failure_analysis(catalog, baseline, precursor):
    from mars_manifest.budgets import BudgetEngine
    budget = BudgetEngine(catalog, baseline).compute(precursor)
    packed = PackingEngine(catalog, baseline).pack(precursor, budget)
    spof_ids = {cid for cid, _ in packed.single_points}
    # one crane, one habitat, one ECLSS -> whole gates ride on one hull each
    assert {"cargo_crane", "habitat_module", "eclss_habitat"} <= spof_ids
    # multi-unit items spread by qty are not single points under balanced packing
    from mars_manifest.cli import load_mission
    from pathlib import Path
    balanced = load_mission(Path(__file__).resolve().parents[1] / "examples" / "precursor_2026_balanced.yaml", catalog)
    b2 = BudgetEngine(catalog, baseline).compute(balanced)
    p2 = PackingEngine(catalog, baseline).pack(balanced, b2)
    assert "fission_unit" not in {cid for cid, _ in p2.single_points}
