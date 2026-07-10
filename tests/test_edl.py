"""EDL probability, demonstrated reliability, and k-ship loss tolerance (C2)."""
import pytest

from mars_manifest.budgets import BudgetEngine
from mars_manifest.edl import (
    capability_survival, demonstrated_reliability, success_prob)
from mars_manifest.packing import PackingEngine


def test_success_prob_ramps_and_caps(baseline):
    assert success_prob(baseline, 0) == pytest.approx(0.5)
    assert success_prob(baseline, 3) == pytest.approx(0.86, abs=0.01)
    assert success_prob(baseline, 20) == pytest.approx(0.95)  # capped at max_prob


def test_rule_of_three_reliability():
    assert demonstrated_reliability(0) == 0.0
    assert demonstrated_reliability(5) == pytest.approx(1 - 3/5, abs=0.02)
    assert demonstrated_reliability(300) > 0.98
    # more successes -> higher demonstrated floor
    assert demonstrated_reliability(100) > demonstrated_reliability(10)


def test_capability_survival_rewards_spreading(catalog, baseline, manager, precursor):
    # redundant fleet spreads critical components -> high survival even at p=0.5
    from mars_manifest.cli import load_mission
    from pathlib import Path
    red = load_mission(Path(__file__).resolve().parents[1] / "examples"
                       / "precursor_2026_redundant.yaml", catalog)
    eng = PackingEngine(catalog, baseline)
    packed = eng.pack(red, BudgetEngine(catalog, baseline).compute(red))
    # Honest finding: return_propellant_proven needs ALL five ISRU components;
    # at coin-flip landing odds even qty-2 redundancy only survives ~24%
    # (0.75^5) -- double-carry is NOT enough at p=0.5.
    surv50 = capability_survival(packed, manager.capability_unlocks(), p=0.5, catalog=catalog)
    assert surv50.get("return_propellant_proven", 1.0) < 0.35
    # ...but at mature-EDL odds (p=0.9) the same spread is robust (~0.95)
    surv90 = capability_survival(packed, manager.capability_unlocks(), p=0.9, catalog=catalog)
    assert surv90.get("return_propellant_proven", 0) > 0.9
    # threshold-with-many-reactors beats a 5-component all_of at the same p
    assert surv50.get("power_baseload", 0) > surv50.get("return_propellant_proven", 0)
    # a component on a single hull survives at exactly p
    pinned = eng.pack(precursor, BudgetEngine(catalog, baseline).compute(precursor))
    surv_p = capability_survival(pinned, manager.capability_unlocks(), p=0.5, catalog=catalog)
    assert surv_p.get("habitat_ready", 1.0) == pytest.approx(0.5, abs=0.01)


def test_two_ship_loss_tolerance(catalog, baseline, manager, precursor):
    eng = PackingEngine(catalog, baseline)
    red = _load(catalog, "precursor_2026_redundant.yaml")
    packed = eng.pack(red, BudgetEngine(catalog, baseline).compute(red))
    rules = manager.capability_unlocks()
    lt1 = eng.loss_tolerance(packed, rules, n_lost=1)
    lt2 = eng.loss_tolerance(packed, rules, n_lost=2)
    # single-fault tolerant by design; two-ship loss is a strictly harder bar
    assert lt1.tolerant
    assert len(lt2.capabilities_at_risk) >= len(lt1.capabilities_at_risk)


def _load(catalog, name):
    from mars_manifest.cli import load_mission
    from pathlib import Path
    return load_mission(Path(__file__).resolve().parents[1] / "examples" / name, catalog)
