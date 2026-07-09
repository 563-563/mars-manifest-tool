# Mars Manifest Tool

Catalog-driven flight-manifest and campaign planner for a SpaceX-style Mars
program. See `HANDOFF.md` for the full specification, `CLAUDE.md` for the
working agreement, and `PROVENANCE.md` for the source and confidence tier of
every input the engines consume.

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
mars pack   examples/precursor_2026.yaml [--tankers 10] [--launch-cost near_term] [--policy balanced] [--spares]
mars isru   examples/precursor_2026.yaml   # Sabatier-chain rates, energy budget, bottleneck
mars plan   examples/campaign_4window.yaml [--format md|xlsx]
mars compare optimistic conservative --campaign examples/campaign_4window.yaml
mars report examples/campaign_4window.yaml --format xlsx --out out/campaign.xlsx
```

## Program structure

**`examples/program_plan.yaml` is the working baseline campaign:**
loss-tolerant redundant precursor (window 0) → rate-matched fuel factory
(window 1, gate `return_propellant_proven` retires 2028-12) → second plant +
habitat cluster (window 2) → first crew (window 3, arrives with ~10,000 t of
propellant banked). All waves balanced-packed with spares as explicit cargo.

Historic fixtures kept for regression: `precursor_2026.yaml` (workbook-pinned,
guards the HANDOFF §7 contract), `precursor_2026_balanced.yaml` (packing-policy
comparison), `campaign_4window.yaml` (gate-timing fixture).

## Layout

- `mars_manifest/` — pure engines (`budgets`, `power`, `packing`, `campaign`,
  `scenarios`) + rendering (`report`) + `cli`
- `data/` — seed component catalog and assumptions (source of truth; all
  numbers notional order-of-magnitude estimates with provenance notes)
- `examples/` — the validated 2026 precursor batch and a 4-window campaign
- `tests/` — regression suite asserting the HANDOFF.md §7 targets
