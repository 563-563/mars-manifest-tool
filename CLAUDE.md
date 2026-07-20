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
   / catalog / the provenance + considered ledgers). The catalog is the source of truth for component attributes;
   assumptions are injected, never hard-coded. See `inputs/README.md`.
3. **Engines** (`mars_manifest/`) — pure, deterministic, tested. Reports only
   render; no computation in the report layer.
4. **Generated documents** (`docs/REQUIREMENTS.md`, `PROVENANCE.md`,
   `docs/CONSIDERED.md`, the console and walkthrough artifacts, xlsx
   reports) — regenerate, never hand-edit. The two ledgers' source of truth
   is `inputs/provenance.json` / `inputs/considered.json`.

## The baseline

- **`inputs/program.json` is the program** (the blue-sky baseline,
  re-baselined 2026-07-14): 2031-01 precursor (5 ships) → doubled fuel
  factory + pre-landed survival bridge 2033-03 (10 ships; 3.2 loads/synod;
  uncrewed return demo departs ~Jan 2035 on its surplus) → **first crew
  2035-05** (15 ships, 12 crew, flying with the village's pilots: agri,
  refinery+polymer test articles, ISRU hot-spare depth) → village 2037-07
  (34) → town 2039-09 (97) → settlement 2041-11 (161; 1,112 adults).
  Governing doctrines: fly-with instead of pre-land (the one-synod survival
  bridge excepted), pilots one synod ahead of their scale deployment, fuel
  capacity follows demand, ≥2× cumulative fleet growth per synod, and no
  air freight: fleets sized to cargo at ≤90% mass, growth-floored windows
  topped up with risk depth.
- Crew gating is strict by design: propellant *banked* (≥1,400 t), 1,000-sol
  ECLSS demonstration, prospect-before-commit (`water_confirmed`), no
  single-ship loss may cost a schedule-critical capability, and the return
  demo departs before crew (L1-RET-01, transit-demo posture: it reports
  during crew transit; surface-hold reserves hedge a failure).
- **`examples/conservative_program.json`** is the archived gate-maximalist
  alternative (crew 2037). It is also what the baseline *becomes* under
  `conservative_feasibility` — the gates hold and crew auto-slips.
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

`tests/` (the full suite; CI-enforced green) pins two different things — don't confuse them:
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
mars manifests inputs/program.json          # regen docs/manifests/ after plan edits (test-enforced fresh)
mars lifecycle inputs/program.json          # risk buy-down + idle-mass audit
mars ledgers                                # regen PROVENANCE.md + docs/CONSIDERED.md from inputs/*.json
```

The story page regenerates from the in-repo pipeline (`viz/export_dashboard_data.py`
→ `viz/build_scrolly.py` → republish to the same artifact URL). The console
and surface-walkthrough artifacts regenerate from the session scratchpad
export (see auto-memory for URLs) and are point-in-time snapshots — check
their vintage against the current baseline before citing them. Re-run the PROVENANCE §8 source
verification whenever a real launch window passes or before any major
decision — both prior failures were silent source drift.

## Invariants that still hold from the original agreement

Engines pure and tested; assumptions injected; catalog is component truth;
reports render only; preserve provenance and uncertainty (low/high ranges,
notes) in all seed data.
