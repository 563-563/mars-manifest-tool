# Mars Manifest Tool

Catalog-driven flight-manifest and campaign planner for a SpaceX-style Mars
program. See `HANDOFF.md` for the full specification and `CLAUDE.md` for the
working agreement.

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
pip install -e ".[dev]"
pytest                        # §7 regression suite must be green
```

## CLI

```bash
mars catalog list [--group "ISRU"]
mars catalog show water_electrolysis
mars budget examples/precursor_2026.yaml [--scenario baseline] [--power solar|fission] [--format table|md|xlsx]
mars pack   examples/precursor_2026.yaml [--tankers 10] [--launch-cost near_term]
mars plan   examples/campaign_4window.yaml [--format md|xlsx]
mars compare optimistic conservative --campaign examples/campaign_4window.yaml
mars report examples/campaign_4window.yaml --format xlsx --out out/campaign.xlsx
```

## Layout

- `mars_manifest/` — pure engines (`budgets`, `power`, `packing`, `campaign`,
  `scenarios`) + rendering (`report`) + `cli`
- `data/` — seed component catalog and assumptions (source of truth; all
  numbers notional order-of-magnitude estimates with provenance notes)
- `examples/` — the validated 2026 precursor batch and a 4-window campaign
- `tests/` — regression suite asserting the HANDOFF.md §7 targets
