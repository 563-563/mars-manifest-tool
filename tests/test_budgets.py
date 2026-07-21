"""Workbook-port regression: the frozen seed-case targets.

These numbers verify that the math from the original hand-built
spreadsheets (Mars-Precursor-Engineering-Budget.xlsx; targets recorded in
HANDOFF.md section 7, historical) was ported correctly. The inputs are
deliberately frozen: do not update them to current data — that is the point
of them. Live-baseline behavior is asserted in the other test files.
"""
import pytest

from mars_manifest.budgets import BudgetEngine


@pytest.fixture(scope="module")
def budget(catalog, workbook_port, precursor):
    return BudgetEngine(catalog, workbook_port).compute(precursor)


def test_manifest_is_the_26_component_batch(precursor):
    assert len(precursor.manifest) == 26
    assert precursor.ships == 5


def test_fixed_hardware_mass(budget):
    assert budget.mass.fixed_hardware_t == pytest.approx(98.5, abs=0.05)


def test_power_loads(budget):
    assert budget.loads.avg_kw == pytest.approx(354.15, abs=0.01)
    assert budget.loads.connected_peak_kw == pytest.approx(505.0, abs=0.01)
    # simultaneous peak ~429 kW at diversity 0.85
    assert budget.loads.simultaneous_peak_kw == pytest.approx(429.25, abs=0.01)
    # survival loads (thermal, comms, nav, compute, ECLSS testbed, controls)
    assert budget.loads.critical_avg_kw == pytest.approx(50.5, abs=0.1)
    assert budget.loads.daily_energy_kwh == pytest.approx(354.15 * 24.6, rel=1e-6)


def test_solar_option(budget):
    # array ~11,800 m2; night battery ~29 t; full-load storm battery ~290 t
    # (workbook formula, kept as worst-case reference). Survival-load sizing
    # (production pauses in storms; only critical loads ride through) needs
    # ~41 t, so solar is no longer flagged infeasible outright.
    assert budget.solar.array_m2 == pytest.approx(11805.0, abs=1)
    assert budget.solar.night_battery_t == pytest.approx(29.04, abs=0.05)
    assert budget.solar.dust_storm_battery_t == pytest.approx(290.4, abs=0.5)
    assert budget.solar.dust_storm_battery_critical_t == pytest.approx(41.4, abs=0.5)
    assert budget.solar.dust_storm_infeasible is False


def test_fission_option(budget):
    # 9 units, ~54 t; buffer battery ~14 t
    assert budget.fission.units == 9
    assert budget.fission.mass_t == pytest.approx(54.0, abs=0.01)
    assert budget.fission.buffer_battery_t == pytest.approx(14.17, abs=0.05)


def test_grand_total_mass_and_utilisation(budget):
    # ~236 t vs 500 t batch capacity -> ~50% utilisation
    assert budget.mass.grand_total_t == pytest.approx(236.4, abs=0.1)
    assert budget.capacity.mass_capacity_t == 500
    assert budget.capacity.mass_utilisation == pytest.approx(0.473, abs=0.005)


def test_mass_budget_lines(budget):
    m = budget.mass
    assert m.consumables_t == pytest.approx(15.0)
    assert m.spares_t == pytest.approx(0.35 * (98.5 - 15.0 + 54.0 + m.storage_t), abs=0.01)
    assert m.contingency_t == pytest.approx(0.10 * (98.5 + 54.0 + m.storage_t), abs=0.01)


def test_volume_budget(budget):
    v = budget.volume
    assert v.fixed_m3 == pytest.approx(695.0, abs=0.1)
    assert v.generation_m3 == pytest.approx(270.0, abs=0.1)   # 9 fission units x 30 m3
    assert v.raw_m3 == pytest.approx(695 + 270 + 7.083 + 0.35 * 695, abs=0.1)
    assert v.effective_m3 == pytest.approx(v.raw_m3 / 0.65, rel=1e-9)


def test_cargo_hardware_cost(budget):
    # Catalog-driven cargo cost per HANDOFF.md §5.1 (fixed hardware + auto-sized power).
    # Note: the cost-model workbook's system-level table (~$1.9B–$8.2B) is a
    # coarser scope (e.g. includes relay sats, excludes sized fission fleet);
    # the catalog decomposition is the tool's source of truth.
    c = budget.cost
    assert c.fixed_hardware_low_musd == pytest.approx(1740.0)
    assert c.fixed_hardware_high_musd == pytest.approx(7850.0)
    assert c.generation_low_musd == pytest.approx(900.0)    # 9 fission x $100M
    assert c.generation_high_musd == pytest.approx(3600.0)
    assert c.storage_low_musd == pytest.approx(44.0)        # ceil(21.25) modules x $2M
    assert c.cargo_low_musd == pytest.approx(2684.0)
    assert c.cargo_high_musd == pytest.approx(11626.0)


def test_solar_scenario_swaps_generation(catalog, manager, precursor):
    a = manager.resolve("solar_only")
    b = BudgetEngine(catalog, a).compute(precursor)
    assert b.power_path == "solar"
    assert b.mass.generation_t == pytest.approx(b.solar.array_mass_t)
    assert b.mass.storage_t == pytest.approx(b.solar.night_battery_t)
    assert any("pause" in w for w in b.warnings)  # storms pause production loads


def test_explicit_power_hardware_overrides_autosize(catalog, baseline, precursor):
    import copy
    from mars_manifest.models import ManifestItem
    mission = copy.deepcopy(precursor)
    mission.manifest.append(ManifestItem("fission_unit", 4, ship=3))
    mission.manifest.append(ManifestItem("battery_module_100kwh", 10, ship=3))
    b = BudgetEngine(catalog, baseline).compute(mission)
    assert b.power_hardware.explicit is True
    assert b.mass.generation_t == pytest.approx(24.0)   # 4 x 6 t
    assert b.mass.storage_t == pytest.approx(6.7)       # 10 x 0.67 t
    # 4 x 40 kWe = 160 kWe < 354 kW load -> shortfall warning
    assert any("kWe" in w for w in b.warnings)
