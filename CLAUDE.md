# CLAUDE.md — Mars Manifest Tool

Working agreement for building this project in Claude Code. Read `HANDOFF.md` first — it is the full specification. This file is the quick operating guide.

## What we're building
A Python core + CLI tool that plans a SpaceX-style Mars campaign: compute budgets (mass / power+storage / volume / cost), pack payloads into ships and derive tanker launches, sequence missions across launch windows toward a self-sustaining base, and compare scenarios. Catalog-driven; seed data in `data/`.

## Ground rules
- **Read the spec before coding.** `HANDOFF.md` §5 has the exact formulas; §7 has regression targets that MUST pass. Do not silently change a formula — the numbers trace back to validated models.
- **Assumptions are injected, never hard-coded.** Every engine reads from an `Assumptions` object loaded from `data/assumptions_seed.json`.
- **Catalog is the source of truth** for component attributes (`data/component_catalog_seed.csv`). Missions reference components by `id`.
- **Engines are pure and tested; reports only render.** No computation in the report layer.
- **Preserve provenance and uncertainty.** Seed numbers are notional; keep low/high ranges and notes intact.

## Suggested build order (milestones in HANDOFF.md §9)
1. M1 catalog + budgets → pass `tests/test_budgets.py` against §7 targets.
2. M2 packing + launch math. 3. M3 campaign planner + capability gating. 4. M4 scenarios + diff. 5. M5 reporting (xlsx/md + charts). 6. M6 full base ramp.

## First task for the agent
Scaffold the package per `HANDOFF.md` §3, load the seed catalog + assumptions, implement `budgets.py`/`power.py`, and write `tests/test_budgets.py` asserting the §7 regression numbers (fixed hardware ~98.5 t, avg load ~354 kW, fission 9 units/~54 t, grand total ~236 t, etc.). Get that green before anything else.

## Definition of done for v1
CLI can run `mars budget`, `mars pack`, `mars plan`, `mars compare`, and `mars report` on the seeded precursor and a 4-window campaign, reproduce the regression numbers, and emit an xlsx equivalent to the ones in the parent folder.

## Companion files (parent folder)
- `../SpaceX-to-Mars-Deep-Dive.md` — research grounding
- `../Mars-Robotic-Precursor-Flight-Manifest.md` — manifest narrative (catalog derived from this)
- `../Mars-First-Batch-Cost-Model.xlsx` — cost formulas
- `../Mars-Precursor-Engineering-Budget.xlsx` — budget formulas + regression source
