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

## The baseline program (`inputs/program.json`)

| Window | Fleet | What it buys |
|---|---|---|
| **2031-01** | 5 ships | Loss-tolerant robotic precursor: EDL proof, 840 kWe fission, pilot fuel plant at qty-3 on its bottleneck steps (chain survival ~44% at coin-flip landing odds, vs ~24% at qty-2), prospect-before-commit water survey, both demonstration clocks started. Retires ~50% of weighted program risk on first landing. |
| **2033-03** | 10 ships | The fuel factory, doubled: two rate-matched ISRU chains (3.4 return loads/synod, 3,000 kWe) + the 45 t survival bridge, pre-landed. `return_propellant_proven`, `life_support_closed`, and `radiation_managed` all retire — every crew gate green a full synod before anyone launches. The uncrewed Earth-return demo departs ~Jan 2035 on the plant's surplus. |
| **2035-05** | 15 ships | **First crew.** 12 people land on ~8,100 t of banked propellant (5+ return loads) with their 26-month bridge aboard — plus pilots for everything the village scales: 12 agri modules, refinery + polymer test articles, ISRU hot-spare depth, 100 robots on the surface, pad rigs for the next fleet. |
| **2037-07** | 34 ships | The village: 112 people, past the 110-person survival floor. Every 2035 pilot deploys at scale (20 agri, 2 refineries + polymer, +2 fuel chains now that crew rotation is the customer). |
| **2039-09** | 97 ships | The town: 512 people, Gen-3 closure (food, polymers, structures local), electronics-fab pilot at its earliest credible window. |
| **2041-11** | 161 ships | The settlement: 1,112 adults — the NSS 1,000-adult milestone. Imports walk the ~500× decay curve as local industry closes. |

The 2031 start reflects the verified public record (no 2026 flight;
Moon-first pivot). **2035 crew is deliberately aggressive** — but every gate
still closes on demonstrated state, and the plan degrades honestly: under the
peer-reviewed skeptic scenario (`conservative_feasibility`) the gates hold and
crew auto-slips to 2037, which is exactly the archived conservative program
(`examples/conservative_program.json`). You are choosing an option on 2035,
not a promise of it. **`docs/NARRATIVE.md` walks the whole arc through in
plain language;** the city-ramp research is tiered in
`docs/CITY_RAMP_RESEARCH.md`.

## Interactive views

Three browser views are generated from the same engine outputs (regenerate
via the session export + build scripts):

- **[The Manifest — scrollytelling essay](https://claude.ai/code/artifact/b0b7a7f8-525e-499b-9512-7501ead32fd3)** — the program told window by window, with a sticky panel that watches the base accrete, and an **Adjust the model** drawer that recomputes every figure live from curated knobs (anchored to the engine baseline; see [`viz/`](viz/README.md)). *Start here.*
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

## Sources we keep coming back to

The full per-input trail lives in `PROVENANCE.md`; these are the anchors that
shaped the model most, and they're worth reading in their own right.

**Architecture & doctrine**

- Casey Handmer — [Starship is Still Not Understood](https://caseyhandmer.wordpress.com/2021/10/28/starship-is-still-not-understood/) and the Feb-2025 follow-ups: the "orbit, reuse, refill, chill" gate sequence, prospect-before-commit, and the cargo-ships-stay economics this plan adopts.
- *New Space* 2022 — [A Roadmap for a Sustainable Human Mars Settlement](https://pmc.ncbi.nlm.nih.gov/articles/PMC9527650/): the ≥2× fleet-growth rule (the one cadence claim that survived our fact-check), the 10–20 first-crew band, and the RedWater well anchor.
- NASA [Design Reference Architecture 5.0](https://ntrs.nasa.gov/citations/20090040343): the institutional baseline we diff against; source of the oxygen-only ISRU fallback scenario.
- Maiwald et al. (DLR), *Scientific Reports* 2024: the peer-reviewed skeptic case — low-TRL ISRU/refill/chill — encoded here as the `conservative_feasibility` scenario rather than argued with.

**Human factors & life support**

- NASA BVAD ([TP-2015-218570/REV2](https://ntrs.nasa.gov/citations/20150000368)): the consumables floor (0.800 kg food / 0.895 kg O₂ / 3.217 kg water per person-day) and crop-area bounds — verified verbatim.
- NASA/NTRS [20200002973](https://ntrs.nasa.gov/citations/20200002973): net habitable volume (~29 m³/person floor) and the 76.5 m³/person pressurized standard our habitat capacity math uses.

**ISRU & local industry**

- NASA MAV ISRU sizing ([NTRS 20170001421](https://ntrs.nasa.gov/citations/20170001421)): the study our chain's hardware-per-tonne ratio cross-checks against (within 7%); [MOXIE](https://www.nasa.gov/missions/mars-2020-perseverance/nasas-oxygen-generating-experiment-moxie-completes-mars-mission/) remains the only ISRU ever flown on Mars — 122 g of O₂, a number worth keeping in view.
- Molten regolith electrolysis ([NTRS 20120003037](https://ntrs.nasa.gov/citations/20120003037); [Dec-2024 vacuum demo](https://ntrs.nasa.gov/citations/20250003220)): regolith → oxygen + structural metal alloys — the process behind the `regolith_refinery`.
- In-situ HDPE on Mars ([NTRS 20050157853](https://ntrs.nasa.gov/citations/20050157853)): CO₂ → ethylene → polyethylene via Sabatier/Fischer-Tropsch — the process behind the `polymer_chemical_plant`; see also [PE-regolith composite printing for radiation shielding](https://www.sciencedirect.com/science/article/abs/pii/S0094576521005269).

**City-scale growth**

- Freitas/Gilbreath lineage ([arXiv 1612.03238](https://arxiv.org/abs/1612.03238)): the industrial-closure generations (gases → plastics → metals → electronics → chips) and the exponential import cliff of incomplete electronics closure.
- Salotti, [*Scientific Reports* 2020](https://www.nature.com/articles/s41598-020-66740-0): the 110-person minimum-viable-settlement floor.
- [NSS Space Settlement Roadmap](https://nss.org/space-settlement-roadmap-25-martian-settlement/): the 1,000-adult formal-settlement milestone.
- Handmer, [The make-buy question in a growing Mars city](https://caseyhandmer.wordpress.com/2022/03/29/understanding-the-make-buy-question-in-a-growing-mars-city/): the ~10 t → ~20 kg per-person-year import collapse (~500×) the city ramp walks down.

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
mars plan   inputs/program.json [--format md|xlsx]
mars lifecycle inputs/program.json             # risk buy-down + idle-hardware review
mars requirements inputs/program.json [--out docs/REQUIREMENTS.md]
mars manifests inputs/program.json             # ship-by-ship snapshot -> docs/manifests/
mars compare optimistic conservative --campaign inputs/program.json
mars report inputs/program.json --format xlsx --out out/program.xlsx
```

## Document map

| File | What it is |
|---|---|
| `inputs/README.md` | **Start here to change anything** — the five input files, their fields, the tiers, and the edit → run → regenerate workflow |
| `docs/NARRATIVE.md` | **Start here for the story** — the whole program walked through in plain language, window by window, with the reasoning behind each call |
| `CONTRIBUTING.md` | The rules that keep the repo honest — read before changing any number |
| `PROVENANCE.md` | Every input: value, source, tier, sensitivity, verification log |
| `CLAUDE.md` | The working agreement: hierarchy of truth, baseline, regression contract |
| `HANDOFF.md` | The original kickoff spec — **historical**; read for intent, not values |
| `docs/REQUIREMENTS.md` | Generated buy-off matrix for the baseline program (never hand-edit) |
| `docs/manifests/` | **Generated ship-by-ship manifests** (JSON + CSV) — what flies on which hull at what mass/volume/power, and which requirements each window closes (never hand-edit; `mars manifests` regenerates) |
| `docs/COMPARATIVES.md` | How this plan differs from Handmer / *New Space* 2022 / NASA DRA 5.0, and what was adopted |
| `docs/CITY_RAMP_RESEARCH.md` | Verified research brief for the city-scale extension (population thresholds, import-mass decay, fleet-growth rules) |
| `docs/CONSIDERED.md` | Ideas weighed and set aside — deferred, out-of-scope, rejected, or simplified — so omissions read as decisions |

## Layout

- `mars_manifest/` — pure engines (`budgets`, `power`, `packing`, `isru`,
  `campaign`, `lifecycle`, `requirements`, `scenarios`) + rendering
  (`report`) + `cli`
- `inputs/` — **the entire editable input surface**, split by concern
  (`program.json`, `assumptions.json`, `city.json`, `requirements.json`,
  `catalog.csv`); see [`inputs/README.md`](inputs/README.md). This is the one
  place to change the model.
- `examples/` — frozen regression fixtures (the `*_2026*` and
  `campaign_4window` files, pinned to historical values) plus
  `conservative_program.json`, the maintained gate-maximalist alternative
  (crew 2037; the baseline's skeptic-scenario outcome)
- `viz/` — the browser-view build pipeline (reads `inputs/` via the engine)
- `tests/` — the regression + behavior suite CI enforces

## License

MIT — see `LICENSE`.
