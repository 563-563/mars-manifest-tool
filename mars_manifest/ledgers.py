"""Structured ledgers: provenance and the considered register.

The source of truth for the two governance ledgers is JSON
(`inputs/provenance.json`, `inputs/considered.json`) — fielded rows a
machine can query. The markdown files (`PROVENANCE.md`,
`docs/CONSIDERED.md`) are GENERATED views: `mars ledgers` renders them, and
a freshness test enforces that the committed markdown matches the JSON.

Document model (JSON):
    {"title": str,
     "preamble": [block, ...],
     "sections": [{"level": 2|3, "title": str, "blocks": [block, ...]}]}
    block = {"type": "prose", "md": str}                  # verbatim markdown
          | {"type": "table", "columns": [str, ...],
             "keys": [str, ...],                          # slugged columns
             "rows": [{key: cell, ...}, ...]}
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# parsing (markdown -> document model)
# ---------------------------------------------------------------------------

_SEP_RE = re.compile(r"^\|\s*:?-{2,}")


def _slug(name: str, seen: set) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "col"
    base, i = s, 2
    while s in seen:
        s, i = f"{base}_{i}", i + 1
    seen.add(s)
    return s


def _split_row(line: str, ncols: int) -> list[str]:
    cells = line.strip().strip("|").split("|")
    if len(cells) > ncols:  # a literal '|' inside the last cell: re-join tail
        cells = cells[: ncols - 1] + ["|".join(cells[ncols - 1:])]
    while len(cells) < ncols:
        cells.append("")
    return [c.strip() for c in cells]


def parse_markdown(text: str) -> dict:
    lines = text.rstrip("\n").split("\n")
    doc = {"title": "", "preamble": [], "sections": []}
    blocks = doc["preamble"]
    i = 0
    if lines and lines[0].startswith("# "):
        doc["title"] = lines[0][2:].strip()
        i = 1
    prose: list[str] = []

    def flush():
        while prose and prose[0] == "":
            prose.pop(0)
        while prose and prose[-1] == "":
            prose.pop()
        if prose:
            blocks.append({"type": "prose", "md": "\n".join(prose)})
        prose.clear()

    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^(##+)\s+(.*)$", ln)
        if m:
            flush()
            sec = {"level": len(m.group(1)), "title": m.group(2).strip(), "blocks": []}
            doc["sections"].append(sec)
            blocks = sec["blocks"]
            i += 1
            continue
        if ln.startswith("|") and i + 1 < len(lines) and _SEP_RE.match(lines[i + 1] or ""):
            flush()
            seen: set = set()
            columns = _split_row(ln, ln.count("|") - 1)
            keys = [_slug(c, seen) for c in columns]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = _split_row(lines[i], len(columns))
                rows.append(dict(zip(keys, cells)))
                i += 1
            blocks.append({"type": "table", "columns": columns, "keys": keys,
                           "rows": rows})
            continue
        prose.append(ln)
        i += 1
    flush()
    return doc


# ---------------------------------------------------------------------------
# rendering (document model -> markdown)
# ---------------------------------------------------------------------------

def _render_table(b: dict) -> str:
    out = ["| " + " | ".join(b["columns"]) + " |",
           "|" + "|".join("---" for _ in b["columns"]) + "|"]
    for row in b["rows"]:
        out.append("| " + " | ".join(row.get(k, "") for k in b["keys"]) + " |")
    return "\n".join(out)


def render_markdown(doc: dict) -> str:
    parts = []
    if doc.get("title"):
        parts.append("# " + doc["title"])
    for b in doc.get("preamble", []):
        parts.append(b["md"] if b["type"] == "prose" else _render_table(b))
    for sec in doc.get("sections", []):
        parts.append("#" * sec["level"] + " " + sec["title"])
        for b in sec["blocks"]:
            parts.append(b["md"] if b["type"] == "prose" else _render_table(b))
    return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# the two ledgers
# ---------------------------------------------------------------------------

LEDGERS = {
    "provenance": {"json": "inputs/provenance.json", "md": "PROVENANCE.md"},
    "considered": {"json": "inputs/considered.json", "md": "docs/CONSIDERED.md"},
}


def load_ledger(root: Path, name: str) -> dict:
    return json.loads((root / LEDGERS[name]["json"]).read_text(encoding="utf-8"))


def render_ledgers(root: Path) -> list[Path]:
    """Regenerate both markdown views from their JSON sources."""
    written = []
    for name, paths in LEDGERS.items():
        doc = load_ledger(root, name)
        out = root / paths["md"]
        out.write_text(render_markdown(doc), encoding="utf-8", newline="\n")
        written.append(out)
    return written
