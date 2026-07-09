"""Requirements buy-off matrix (requirements.py + data/requirements_seed.yaml)."""
from pathlib import Path

import pytest

from mars_manifest.campaign import CampaignPlanner
from mars_manifest.cli import load_campaign
from mars_manifest.requirements import RequirementsEngine, load_requirements

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def reqs():
    return load_requirements(ROOT / "data" / "requirements_seed.yaml")


@pytest.fixture(scope="module")
def engine(catalog, baseline, manager):
    return RequirementsEngine(catalog, baseline, manager.capability_unlocks())


def _run(catalog, baseline, manager, name):
    campaign = load_campaign(ROOT / "examples" / name, catalog)
    planner = CampaignPlanner(catalog, baseline, manager.capability_unlocks(),
                              manager.crewed_requires())
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
    matrix = engine.evaluate(reqs, _run(catalog, baseline, manager, "program_plan.yaml"))
    assert not matrix.open_ids
    v = {x.requirement.id: x for x in matrix.verdicts}
    # mission-level requirement closes a full synod before crew
    assert v["L0-MSN-01"].status == "CLOSED"
    assert v["L0-MSN-01"].closed_window == "2031-01"
    # power scale and plant redundancy land ahead of plan
    assert v["L2-PWR-04"].status == "EARLY"
    assert v["L2-PROP-05"].status == "EARLY"
    # no single-ship loss costs a schedule-critical capability, any window
    assert v["L1-LOG-02"].status == "PASS"
    # window 0 buys off the bulk of the tree
    assert len(matrix.by_window["2026-11"]) >= 12


def test_legacy_campaign_fails_requirements(catalog, baseline, manager, reqs, engine):
    matrix = engine.evaluate(reqs, _run(catalog, baseline, manager, "campaign_4window.yaml"))
    open_ids = set(matrix.open_ids)
    # workbook-pinned packing: one lost ship kills schedule-critical capabilities
    assert "L1-LOG-02" in open_ids
    v = {x.requirement.id: x for x in matrix.verdicts}
    # habitat count only reached at the crew window itself — no verification margin
    assert v["L2-HAB-02"].status == "LATE"
    assert v["L2-HAB-02"].closed_window == "2033-03"
    # rollup honesty: the mission requirement cannot close
    assert v["L0-MSN-01"].status == "OPEN"
