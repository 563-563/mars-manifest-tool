# CLAUDE.md — Mars Manifest Tool (working agreement)

*Rewritten 2026-07-09. The original kickoff agreement pointed at `HANDOFF.md`
as the source of truth; the project has outgrown it. This file defines what
governs NOW.*

## Hierarchy of truth (highest wins)

1. **Verified external data.** The data policy is absolute: the baseline
   carries the best-verified number — never keep a known-stale value and
   downgrade its confidence tier. `PROVENANCE.md` records every input's source,
   tier, and the verification log. When a source drifts (it has: payload
   volume, solar density), the seed changes and consequences propagate.
2. **Input data** (`inputs/*.json`, `inputs/catalog.csv`) — the single editable
   input surface, split by concern (program / assumptions / city / requirements
   / catalog). The catalog is the source of truth for component attributes;
   assumptions are injected, never hard-coded. See `inputs/README.md`.
3. **Engines** (`mars_manifest/`) — pure, deterministic, tested. Reports only
   render; no computation in the report layer.
4. **Generated documents** (`docs/REQUIREMENTS.md`, the console and walkthrough
   artifacts, xlsx reports) — regenerate, never hand-edit.

## The baseline

- **`inputs/program.json` is the program.** 2031-01 start (Moon-first
  pivot; no 2026 flight) → fuel factory 2033-03 → second plant + habitats
  2035-05 (11 ships; volume-bound at the real 614 m³ bay) → first crew 2037-07.
- Crew gating is strict by design: propellant *banked* (≥1,400 t), 1,000-sol
  ECLSS demonstration, prospect-before-commit (`water_confirmed`), and no
  single-ship loss may cost a schedule-critical capability.
- `inputs/requirements.json` + `mars requirements` is the buy-off contract;
  `docs/COMPARATIVES.md` records how we differ from Handmer / New Space 2022 /
  NASA DRA 5.0 and what we adopted from them.

## Historical documents — do NOT re-anchor to these

- **`HANDOFF.md`** — the kickoff spec. Its §5 formulas are ported and tested;
  its §7 numbers survive as the *workbook-port regression fixture* (see below). Its dates
  (2026 start), fleet volume (1,000 m³), example campaign, and open questions
  are superseded. Read it for intent and provenance, not for current values.
- **`../Mars-Precursor-Engineering-Budget.xlsx`, `../Mars-First-Batch-Cost-Model.xlsx`**
  — the spreadsheets the tool replaced. Do not update them or reconcile new
  results against them; the tool's xlsx reports supersede both.
- **`examples/precursor_2026*.yaml`, `examples/campaign_4window.yaml`** —
  regression fixtures only, pinned to historical inputs. Never present them as
  the plan.

## The regression contract, precisely

`tests/` (59 green) pins two different things — don't confuse them:
- **Workbook-port fixtures** (origin: HANDOFF.md §7, via the pinned 2026
  example files): 98.5 t fixed
  hardware, 354.15 kW, 9×40 kWe fission, 236.4 t, 55–85 launches. These verify
  the workbook math was ported correctly. They are input-frozen on purpose.
- **Current-model behavior** (program plan, ISRU chain, gates, loss tolerance,
  requirements): these assert the live baseline and MUST move when verified
  data moves. Changing a ported formula still requires tracing to a source; changing
  a *data value* requires a verified source and a PROVENANCE entry.

## Operating routine

```bash
.venv/Scripts/python.exe -m pytest tests/ -q      # must be green before commit
mars plan inputs/program.json --format md   # the program at a glance
mars requirements inputs/program.json --out docs/REQUIREMENTS.md  # regen after plan edits
mars lifecycle inputs/program.json          # risk buy-down + idle-mass audit
```

Artifacts (console + surface walkthrough) regenerate from the session
scratchpad export script (`export_dashboard_data.py` → embed JSON →
republish); see auto-memory for URLs. Re-run the PROVENANCE §8 source
verification whenever a real launch window passes or before any major
decision — both prior failures were silent source drift.

## Invariants that still hold from the original agreement

Engines pure and tested; assumptions injected; catalog is component truth;
reports render only; preserve provenance and uncertainty (low/high ranges,
notes) in all seed data.
