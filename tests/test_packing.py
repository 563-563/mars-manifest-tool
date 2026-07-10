"""Packing + launch math: formula spec from HANDOFF.md §5.2; per-ship and
launch-count targets are workbook-port regression values (HANDOFF.md §7,
frozen on purpose — see tests/test_budgets.py header)."""
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
    # workbook targets: Ship3/power ~81 t / 330 m3; Ship5/habitat ~45 t / 425 m3
    assert ships[3].mass_t == pytest.approx(80.67, abs=0.05)
    assert ships[3].volume_m3 == pytest.approx(330.08, abs=0.1)
    assert ships[5].mass_t == pytest.approx(45.0, abs=0.01)
    assert ships[5].volume_m3 == pytest.approx(425.0, abs=0.01)
    # remaining ships from the workbook's per-ship rollup
    assert ships[1].mass_t == pytest.approx(3.0, abs=0.01)
    assert ships[2].mass_t == pytest.approx(11.0, abs=0.01)
    assert ships[4].mass_t == pytest.approx(27.0, abs=0.01)
    # everything under 100 t / 614 m3 (verified bay volume)
    for s in packed.ships:
        assert s.mass_t <= 100
        assert s.volume_m3 <= 614


def test_launch_math_low_and_high(catalog, baseline, precursor):
    engine = PackingEngine(catalog, baseline)
    budget = BudgetEngine(catalog, baseline).compute(precursor)
    low = engine.pack(precursor, budget, tankers_per_ship=10, launch_cost_tier="near_term")
    high = engine.pack(precursor, budget, tankers_per_ship=16, launch_cost_tier="near_term")
    # workbook targets: 55 launches (10 tankers) to 85 (16); near-term campaign $4.95B–$7.65B
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
        assert s.volume_m3 <= 614


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
    # loads actually balanced: no near-empty ship, no dominant ship. At the
    # verified 614 m3 bay, balance is max(mass, volume)-driven, so the
    # habitat-carrying ship rightly runs lighter on mass.
    masses = [s.mass_t for s in packed.ships]
    assert min(masses) > 20 and max(masses) < 60
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


def _load_example(catalog, name):
    from mars_manifest.cli import load_mission
    from pathlib import Path
    return load_mission(Path(__file__).resolve().parents[1] / "examples" / name, catalog)


def test_loss_tolerance_pinned_vs_balanced_vs_redundant(catalog, baseline, manager, precursor):
    from mars_manifest.budgets import BudgetEngine
    rules = manager.capability_unlocks()
    engine = PackingEngine(catalog, baseline)
    be = BudgetEngine(catalog, baseline)

    # workbook pinning: losing the power ship or habitat ship kills capabilities
    pinned = engine.pack(precursor, be.compute(precursor))
    lt_pinned = engine.loss_tolerance(pinned, rules)
    assert not lt_pinned.tolerant
    assert "power_baseload" in lt_pinned.capabilities_at_risk   # all fission on ship 3
    assert "habitat_ready" in lt_pinned.capabilities_at_risk    # habitat on ship 5

    # balanced spreads multi-unit classes: power survives any loss, qty-1 items don't
    bal = _load_example(catalog, "precursor_2026_balanced.yaml")
    lt_bal = engine.loss_tolerance(engine.pack(bal, be.compute(bal)), rules)
    assert not lt_bal.tolerant
    assert "power_baseload" not in lt_bal.capabilities_at_risk

    # redundant manifest + balanced packing: no single loss costs anything
    red = _load_example(catalog, "precursor_2026_redundant.yaml")
    budget_red = be.compute(red)
    packed_red = engine.pack(red, budget_red)
    lt_red = engine.loss_tolerance(packed_red, rules)
    assert lt_red.tolerant, f"at risk: {lt_red.capabilities_at_risk} on {lt_red.vulnerable_ships}"
    # and it still fits the batch
    assert budget_red.mass.grand_total_t < budget_red.capacity.mass_capacity_t
    for s in packed_red.ships:
        assert s.mass_t <= 100 and s.volume_m3 <= 1000
