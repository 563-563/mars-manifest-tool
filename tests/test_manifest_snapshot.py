"""The committed baseline manifest snapshot (docs/manifests/) — the reference
people are pointed at for mass/volume/power and requirements linkage. Two
guarantees: the `mars manifests` command produces a valid snapshot, and the
committed copy is FRESH (regenerating from inputs/ yields the same content,
so the snapshot can never silently disagree with the engine)."""
import csv
import json
from pathlib import Path

import pytest

from mars_manifest.cli import main

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def snapshot(tmp_path_factory):
    out = tmp_path_factory.mktemp("manifests")
    rc = main(["--inputs-dir", str(ROOT / "inputs"), "manifests",
               str(ROOT / "inputs" / "program.json"), "--out-dir", str(out)])
    assert rc == 0
    return out


def test_snapshot_shape_and_budgets(snapshot):
    snap = json.loads((snapshot / "manifests.json").read_text(encoding="utf-8"))
    assert len(snap["windows"]) == 7
    cap_m = snap["per_ship_capacity"]["mass_t"]
    cap_v = snap["per_ship_capacity"]["volume_m3"]
    for w in snap["windows"]:
        assert len(w["ships_detail"]) == w["ships"]
        for s in w["ships_detail"]:
            assert s["mass_t"] <= cap_m + 1e-6, (w["id"], s["ship"])
            assert s["volume_m3"] <= cap_v + 1e-6, (w["id"], s["ship"])
            # per-item masses roll up to the ship total
            assert sum(i["mass_t"] for i in s["items"]) == pytest.approx(
                s["mass_t"], abs=0.05)
    # window 0 buys off the bulk of the tree; every id resolves to a statement
    w0 = snap["windows"][0]
    assert len(w0["requirements_closed"]) >= 12
    assert all(r["statement"] for r in w0["requirements_closed"])


def test_snapshot_csv_flattens_every_item(snapshot):
    snap = json.loads((snapshot / "manifests.json").read_text(encoding="utf-8"))
    rows = list(csv.reader((snapshot / "manifests.csv").open(encoding="utf-8")))
    n_items = sum(len(s["items"]) for w in snap["windows"] for s in w["ships_detail"])
    assert len(rows) == n_items + 1  # + header


def test_committed_snapshot_is_fresh(snapshot):
    """docs/manifests/manifests.json must match a fresh regeneration — edit
    inputs/, run `mars manifests inputs/program.json`, commit the result."""
    fresh = json.loads((snapshot / "manifests.json").read_text(encoding="utf-8"))
    committed = json.loads((ROOT / "docs" / "manifests" / "manifests.json")
                           .read_text(encoding="utf-8"))
    fresh["generated_from"] = committed["generated_from"] = ""  # path spelling differs
    assert committed == fresh, (
        "docs/manifests/ is stale — regenerate with `mars manifests inputs/program.json`")


def test_line_item_costs_reconcile_with_program_cost(snapshot):
    """Per-item costs must sum to each window's cargo-hardware cost (the number
    already baked into the program totals) — proving the snapshot's line items
    ARE the program cost, not a parallel estimate. Spares are uncosted mass
    overhead by design (docs/CONSIDERED.md) and carry null costs."""
    snap = json.loads((snapshot / "manifests.json").read_text(encoding="utf-8"))
    for w in snap["windows"]:
        lo = sum(i["cost_musd_low"] for s in w["ships_detail"] for i in s["items"]
                 if i["cost_musd_low"] is not None)
        hi = sum(i["cost_musd_high"] for s in w["ships_detail"] for i in s["items"]
                 if i["cost_musd_high"] is not None)
        assert lo == pytest.approx(w["cargo_hardware_cost_musd"]["low"], rel=0.02), w["id"]
        assert hi == pytest.approx(w["cargo_hardware_cost_musd"]["high"], rel=0.02), w["id"]
        for s in w["ships_detail"]:
            for i in s["items"]:
                assert (i["cost_musd_low"] is None) == i["id"].startswith("spares:")
