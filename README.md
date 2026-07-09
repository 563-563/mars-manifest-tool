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
mars isru   examples/precursor_2026.yaml [--design]   # chain rates, energy, rate-matched buy
mars lifecycle examples/program_plan.yaml   # risk buy-down curve + idle-hardware review
mars requirements examples/program_plan.yaml [--out docs/REQUIREMENTS.md]   # buy-off matrix
mars plan   examples/campaign_4window.yaml [--format md|xlsx]
mars compare optimistic conservative --campaign examples/campaign_4window.yaml
mars report examples/campaign_4window.yaml --format xlsx --out out/campaign.xlsx
```

## Program structure

**`examples/program_plan.yaml` is the working baseline campaign** (2031 start —
no 2026 flight per the Moon-first pivot): loss-tolerant redundant precursor
(2031-01) → rate-matched fuel factory (2033-03, where `return_propellant_proven`
retires with 2,686 t banked) → second plant + habitat cluster (2035-05) →
first crew (2037-07, arriving with ~10,200 t of propellant banked). All waves
balanced-packed with spares as explicit cargo.

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
