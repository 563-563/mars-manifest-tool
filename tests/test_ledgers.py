"""The governance ledgers: JSON is the source of truth, markdown is a
generated view (`mars ledgers`), and the two can never drift."""
import json
from pathlib import Path

from mars_manifest.ledgers import LEDGERS, load_ledger, render_markdown

ROOT = Path(__file__).resolve().parents[1]


def _tables(doc):
    for blocks in [doc["preamble"]] + [s["blocks"] for s in doc["sections"]]:
        for b in blocks:
            if b["type"] == "table":
                yield b


def test_markdown_views_are_fresh():
    for name, paths in LEDGERS.items():
        doc = load_ledger(ROOT, name)
        committed = (ROOT / paths["md"]).read_text(encoding="utf-8")
        assert render_markdown(doc) == committed, (
            f"{paths['md']} is stale — edit {paths['json']} and run `mars ledgers`")


def test_rows_are_fielded_and_complete():
    prov = load_ledger(ROOT, "provenance")
    cons = load_ledger(ROOT, "considered")
    # every table row carries every column key
    for doc in (prov, cons):
        for t in _tables(doc):
            assert len(t["columns"]) == len(t["keys"])
            for row in t["rows"]:
                assert set(row) == set(t["keys"])
    # provenance: wherever a Tier column exists, it is populated
    tiered = [r for t in _tables(prov) if "tier" in t["keys"] for r in t["rows"]]
    assert len(tiered) >= 60
    assert all(r["tier"].strip() for r in tiered)
    # considered: the register keeps idea + status populated
    main = max(_tables(cons), key=lambda t: len(t["rows"]))
    assert len(main["rows"]) >= 40
    assert all(r["idea"].strip() and r["status"].strip() for r in main["rows"])
