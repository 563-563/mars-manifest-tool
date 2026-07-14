"""Requirements buy-off matrix (requirements.py + inputs/requirements.json)."""
from pathlib import Path

import pytest

from mars_manifest.campaign import CampaignPlanner
from mars_manifest.cli import load_campaign
from mars_manifest.requirements import RequirementsEngine, load_requirements

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "inputs" / "program.json"          # the editable program shape
CAMPAIGN_4W = ROOT / "examples" / "campaign_4window.yaml"  # frozen regression fixture


@pytest.fixture(scope="module")
def reqs():
    return load_requirements(ROOT / "inputs" / "requirements.json")


@pytest.fixture(scope="module")
def engine(catalog, baseline, manager):
    return RequirementsEngine(catalog, baseline, manager.capability_unlocks())


def _run(catalog, assumptions, manager, campaign_path):
    from mars_manifest.city import city_rules, load_city_ramp
    city = load_city_ramp(ROOT / "inputs" / "city.json")
    rules = {**manager.capability_unlocks(), **city_rules(city)}
    growth = city["growth"]["fleet_min_growth_per_synod"]["value"]
    campaign = load_campaign(campaign_path, catalog)
    planner = CampaignPlanner(catalog, assumptions, rules, manager.crewed_requires(),
                              city=city, min_fleet_growth=growth)
    return planner.run(campaign)


def test_tree_shape(reqs):
    assert len(reqs) >= 25
    ids = {r.id for r in reqs}
    assert all((r.parent in ids) for r in reqs if r.parent)
    # every leaf has a machine-checkable criterion + method
    for r in reqs:
        kids = [x for x in reqs if x.parent == r.id]
        if not kids:
            assert r.verify, f"{r.id} is a leaf without verification criteria"


def test_program_plan_closes_everything(catalog, baseline, manager, reqs, engine):
    matrix = engine.evaluate(reqs, _run(catalog, baseline, manager, PROGRAM))
    assert not matrix.open_ids
    v = {x.requirement.id: x for x in matrix.verdicts}
    # mission-level requirement closes a full synod before the 2035 crew:
    # life support, radiation, and the return branch all retire at 2033
    assert v["L0-MSN-01"].status == "CLOSED"
    assert v["L0-MSN-01"].closed_window == "2033-03"
    # power scale and plant redundancy land ahead of plan
    assert v["L2-PWR-04"].status == "EARLY"
    assert v["L2-PROP-05"].status == "EARLY"
    # no single-ship loss costs a schedule-critical capability, any window
    assert v["L1-LOG-02"].status == "PASS"
    # window 0 buys off the bulk of the tree
    assert len(matrix.by_window["2031-01"]) >= 12


def test_legacy_campaign_fails_requirements(catalog, baseline, manager, reqs, engine):
    matrix = engine.evaluate(reqs, _run(catalog, baseline, manager, CAMPAIGN_4W))
    open_ids = set(matrix.open_ids)
    # workbook-pinned packing: one lost ship kills schedule-critical capabilities
    assert "L1-LOG-02" in open_ids
    v = {x.requirement.id: x for x in matrix.verdicts}
    # rollup honesty: the mission requirement cannot close
    assert v["L0-MSN-01"].status == "OPEN"


def test_transport_readiness_gates(catalog, baseline, manager, reqs, engine):
    # baseline: all four Earth-side preconditions close (matrix stays green)
    matrix = engine.evaluate(reqs, _run(catalog, baseline, manager, PROGRAM))
    v = {x.requirement.id: x for x in matrix.verdicts}
    for rid in ("L1-TRANS-01", "L1-TRANS-02", "L1-TRANS-03", "L1-TRANS-04"):
        assert v[rid].status == "CLOSED", rid


def test_conservative_feasibility_opens_refill_and_chill(catalog, manager, reqs):
    # the DLR/Maiwald skeptic scenario flips refill+chill false -> those gates OPEN
    a = manager.resolve("conservative_feasibility")
    eng = RequirementsEngine(catalog, a, manager.capability_unlocks())
    result = _run(catalog, a, manager, PROGRAM)
    matrix = eng.evaluate(reqs, result)
    v = {x.requirement.id: x for x in matrix.verdicts}
    assert v["L1-TRANS-01"].status == "CLOSED"    # orbit demonstrated
    assert v["L1-TRANS-03"].status == "OPEN"      # refill not
    assert v["L1-TRANS-04"].status == "OPEN"      # chill not
    assert "L1-TRANS-03" in matrix.open_ids
