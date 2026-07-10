# Mars Manifest Tool

![tests](https://github.com/563-563/mars-manifest-tool/actions/workflows/tests.yml/badge.svg)

**A campaign planner for settling Mars, where every number has a receipt.**

This is a Python engine + CLI that plans a multi-decade, Starship-class Mars
program as a sequence of launch-window manifests: what flies on each ship,
what it costs in mass/power/volume/launches/dollars, which capabilities each
window unlocks, what breaks if a ship is lost, and when a crew can defensibly
fly. It started as a faithful port of two hand-built engineering and cost
spreadsheets for a first robotic batch, and grew into a verified planning
stack: every input in the seed data is traced to a public source with a
confidence tier, and claims that fail verification — including most of
SpaceX's aspirational cadence figures — are documented as failing rather than
quietly used.

## What it answers

- **Does the manifest fit?** Mass, volume, power, and storage budgets per
  ship and per fleet, with tanker-multiplied launch counts and cost on both
  customer-price and internal-cost bases.
- **What does each window buy us?** Capability gates (power, water,
  propellant, life support…) retire on *demonstrated* state — tonnes of
  propellant actually banked, sols of ECLSS runtime — not on hardware
  delivery. Plain-English "what this enables" summaries translate each
  window into human terms (return flights banked, homes' worth of power,
  crew-months of caches).
- **What survives a bad day?** Redundancy-aware packing (anti-affinity
  spreads critical units across hulls) and a loss-tolerance analysis showing
  exactly which capabilities die if any single ship fails entry.
- **Is the plan honest about risk and waste?** A lifecycle review scores
  risk retired per window against gate severity, and flags crew-era hardware
  landed years before anyone can use it.
- **Are we meeting our own requirements?** A decomposed requirements tree
  (L0 mission → L2 quantitative criteria, standard A/I/D/T verification
  methods) is machine-checked against every campaign run; CI fails if any
  requirement goes open.

## The baseline program (`examples/program_plan.yaml`)

| Window | Fleet | What it buys |
|---|---|---|
| **2031-01** | 5 ships | Loss-tolerant robotic precursor: EDL proof, 640 kWe fission, pilot fuel plant, ECLSS demonstration article, prospect-before-commit water survey. Retires ~50% of weighted program risk on first landing. |
| **2033-03** | 5 ships | The fuel factory: rate-matched ISRU chain + the reactors it drags (1,760 kWe). `return_propellant_proven` retires with ~1,826 t banked (chain ramps at 60% its first synod) — gated on 2031 confirming site water first. |
| **2035-05** | 11 ships | Second plant (2× production) + habitat cluster + deep caches. `life_support_closed` + `radiation_managed`; all schedule-critical risk retired. Volume-bound at the real 614 m³ bay — hence 11 ships, not 10. |
| **2037-07** | 21 ships | First crew (12) lands at a powered, provisioned base with ~8,700 t of propellant banked, ~93% demonstrated EDL reliability, and every requirement closed at least one synod earlier. |
| **2039 → 2044** | 42 → 200 ships | City ramp: past the 110-person survival floor (2039), Gen-3 industrial closure (2041), the NSS 1,000-adult settlement milestone (2044, ~1,112 people). Recurring imports walk the ~500× decay curve as local industry closes. |

The 2031 start reflects the verified public record (no 2026 flight;
Moon-first pivot), and 2037 crew sits at the aggressive end of the
independent expert consensus. **`docs/NARRATIVE.md` walks the whole arc
through in plain language;** the city-ramp research is tiered in
`docs/CITY_RAMP_RESEARCH.md`.

## Interactive views

Three browser views are generated from the same engine outputs (regenerate
via the session export + build scripts):

- **[The Manifest — scrollytelling essay](https://claude.ai/code/artifact/b0b7a7f8-525e-499b-9512-7501ead32fd3)** — the program told window by window, with a sticky panel that watches the base accrete. *Start here.*
- **[Manifest console](https://claude.ai/code/artifact/1fa983e5-510f-401f-9820-bac33444ca7c)** — the analyst's instrument: budgets, packing, requirements buy-off, risk, ISRU, surface build-up.
- **[Surface walkthrough](https://claude.ai/code/artifact/3182378f-acac-47a3-b381-7ce2a6d36a18)** — a visual site plan of the base after each window.

## How it stays honest

- **Provenance tiers.** Every input carries a tier in `PROVENANCE.md`:
  **A** physical constant · **B** published spec/measurement · **C** stated
  derivation · **D** notional estimate. A verification log records each
  source re-checked against the exact claim it supports, including two cases
  where our own numbers failed re-verification and the baseline was
  re-anchored to the verified value (Starship bay volume 1,000 → 614 m³;
  solar areal density 1.5 → 4.0 kg/m²). The policy is absolute: the baseline
  carries the best-verified number — never a stale one with a downgraded tier.
- **Two-part regression contract.** The *workbook-port fixtures*
  (`examples/precursor_2026*.yaml` and the targets in
  `tests/test_budgets.py`) are deliberately frozen on historical inputs —
  they prove the original spreadsheet math was ported correctly and must
  never be "updated." Everything else asserts the live baseline and must
  move when verified data moves. `CONTRIBUTING.md` has the full rules.
- **CI on every push/PR**: the full pytest suite on Linux + Windows ×
  Python 3.10/3.12, plus a gate that runs the requirements buy-off matrix on
  the baseline program and fails if anything is open.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate     POSIX: source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## CLI

```bash
mars catalog list [--group "ISRU"]
mars catalog show water_electrolysis
mars budget examples/precursor_2026.yaml [--scenario baseline] [--power solar|fission] [--format table|md|xlsx]
mars pack   examples/precursor_2026.yaml [--tankers 10] [--launch-cost near_term] [--policy balanced] [--spares]
mars isru   examples/precursor_2026.yaml [--design]   # chain rates, energy, rate-matched buy
mars plan   examples/program_plan.yaml [--format md|xlsx]
mars lifecycle examples/program_plan.yaml             # risk buy-down + idle-hardware review
mars requirements examples/program_plan.yaml [--out docs/REQUIREMENTS.md]
mars compare optimistic conservative --campaign examples/program_plan.yaml
mars report examples/program_plan.yaml --format xlsx --out out/program.xlsx
```

## Document map

| File | What it is |
|---|---|
| `docs/NARRATIVE.md` | **Start here for the story** — the whole program walked through in plain language, window by window, with the reasoning behind each call |
| `CONTRIBUTING.md` | The rules that keep the repo honest — read before changing any number |
| `PROVENANCE.md` | Every input: value, source, tier, sensitivity, verification log |
| `CLAUDE.md` | The working agreement: hierarchy of truth, baseline, regression contract |
| `HANDOFF.md` | The original kickoff spec — **historical**; read for intent, not values |
| `docs/REQUIREMENTS.md` | Generated buy-off matrix for the baseline program (never hand-edit) |
| `docs/COMPARATIVES.md` | How this plan differs from Handmer / *New Space* 2022 / NASA DRA 5.0, and what was adopted |
| `docs/CITY_RAMP_RESEARCH.md` | Verified research brief for the city-scale extension (population thresholds, import-mass decay, fleet-growth rules) |
| `docs/CONSIDERED.md` | Ideas weighed and set aside — deferred, out-of-scope, rejected, or simplified — so omissions read as decisions |

## Layout

- `mars_manifest/` — pure engines (`budgets`, `power`, `packing`, `isru`,
  `campaign`, `lifecycle`, `requirements`, `scenarios`) + rendering
  (`report`) + `cli`
- `data/` — seed catalog, assumptions, and requirements (source of truth;
  every value tier-labeled)
- `examples/` — the baseline `program_plan.yaml` plus frozen regression
  fixtures (the `*_2026*` files are fixtures, not the plan)
- `tests/` — the regression + behavior suite CI enforces

## License

MIT — see `LICENSE`.
