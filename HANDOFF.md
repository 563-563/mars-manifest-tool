# Mars Manifest Tool — Handoff Specification

*Prepared as a handoff from an exploratory research-and-modeling conversation into a Claude Code build. This document is the source of truth for intent, domain grounding, data model, formulas, and roadmap. Read it fully before writing code.*

---

## 0. What this is, in one paragraph

We are building a **flight-manifest and campaign-planning tool for a SpaceX-style Mars program**. It starts with the *uncrewed robotic precursor batch* (the first launch window) and scales to model the **full multi-decade ramp toward a self-sustaining Mars base**. The tool is catalog-driven: a master library of systems/subsystems (mass, power, volume, cost, dependencies) feeds mission definitions, which are grouped into launch windows, which are sequenced into a campaign. From any manifest or campaign it must (1) **compute budgets** — mass, power+storage, volume, cost — and check them against Starship capacity; (2) **pack and size the fleet** — bin-pack payloads into ships and derive required tanker/refueling launches; (3) **plan across launch windows** — sequence missions every synod (~26 months), carrying forward what is already on the surface and gating later missions on capabilities unlocked earlier; and (4) **compare scenarios** — run variants (pilot vs full-scale ISRU, solar vs fission, optimistic vs conservative reuse) side by side and diff them.

**Stack decision:** Python core + CLI. Pandas/openpyxl for data and report generation. No web UI in v1. Design the core as a clean importable library so a UI can be added later.

---

## 1. Why this exists — conversation context & design rationale

This tool crystallizes a long analysis conversation. The builder should inherit not just the numbers but *why they matter*. The arc was:

1. **Deep dive: "what will it take to get SpaceX to Mars?"** Established that Mars is not one problem but ~six stacked ones, none fully solved: orbital refueling, EDL of a 100 t vehicle, ISRU return propellant, life support closure, radiation, and human survival with no abort. (See `../SpaceX-to-Mars-Deep-Dive.md`.)
2. **Mechanics** — worked through the Starship Mars EDL sequence and the concept of operations for the first robotic missions (prove landing → confirm ice → deploy power/robots → prove propellant production → only then crew).
3. **Manifest** — enumerated the systems each precursor ship must carry, by function. (See `../Mars-Robotic-Precursor-Flight-Manifest.md`.)
4. **Cost model** — per-launch internal cost scenarios and the tanker-multiplication problem (each Mars ship needs its own fleet of ~10–16 refueling launches). (See `../Mars-First-Batch-Cost-Model.xlsx`.)
5. **Engineering budget** — linked mass / power+storage / volume model with per-ship rollup vs Starship capacity. (See `../Mars-Precursor-Engineering-Budget.xlsx`.)
6. **Strategy** — discussed how far SpaceX would vertically integrate (transport-critical pieces in-house; robots/power/AI cross-leveraged from Tesla/xAI; nuclear likely via NASA/DOE).

### Load-bearing insights the model must preserve

- **Refueling is the gating launch multiplier.** A Mars-bound ship launches nearly empty of deep-space propellant and is refilled in LEO from a depot. So *N cargo ships ≠ N launches*; it is `N × (1 + tankers_per_ship)`. This must be first-class in the fleet-sizing math.
- **Power is the tall pole.** In the engineering budget, ISRU (esp. water electrolysis) dominates average load (~354 kW in the seed case), and power *generation hardware* dominates cargo mass. Solar vs fission is the pivotal trade: solar is light but needs impractically large batteries to survive dust storms; fission is heavier but weather-independent. The tool must size both and let the user pick.
- **Money is not the hardest constraint.** Reusable launch economics make even ~85-launch campaigns affordable relative to development and cargo hardware. Track cost, but the binding constraints are mass/power/volume and capability-gating, not dollars.
- **Everything is capability-gated.** No crew until propellant production is demonstrated on the surface and a return path exists. The campaign planner must enforce prerequisite capabilities before a mission type is allowed.
- **Notional ≠ authoritative.** Every seed number is an order-of-magnitude estimate. The catalog must make provenance and uncertainty (low/high ranges) explicit so real data can replace estimates cleanly.

---

## 2. Domain constants & grounding (reference)

These are the physical/architectural facts established in research. Bake them into defaults/tests, not hard-coded logic.

| Fact | Value | Use |
|---|---|---|
| Starship payload to Mars surface | ~100 t (target; early likely less) | Ship mass capacity |
| Starship usable payload volume | ~1,000 m³ | Ship volume capacity |
| Tanker launches per deep-space ship | ~10 (SpaceX) to ~16 (GAO) | Fleet-sizing multiplier |
| Mars launch window cadence | every ~26 months (synodic) | Campaign timeline |
| Transit time | ~6–9 months | Mission timing |
| Surface stay (conjunction class) | ~500 days; total mission ~900–1,005 days | Crewed mission modeling |
| Return propellant per ship | ~1,200–1,500 t methalox | ISRU scale target |
| Water needed for that | ~hundreds of t | Mining scale |
| Full-scale ISRU power | ~1 MW continuous | Power scaling ceiling |
| Only prior Mars ISRU (MOXIE) | 122 g O₂ total | Reality check on ISRU maturity |
| Martian sol | 24.6 hr (≈12.3 hr night) | Energy/storage math |
| Mars solar | collapses in months-long dust storms | Solar vs fission trade |

---

## 3. Architecture

```
mars_manifest/
  __init__.py
  catalog.py          # Component catalog: load/validate/query the master library
  models.py           # Dataclasses: Component, Ship, Mission, Window, Campaign, Scenario, Assumptions
  budgets.py          # BudgetEngine: mass / power+storage / volume / cost
  power.py            # Power & storage sizing (solar vs fission), used by BudgetEngine
  packing.py          # PackingEngine: bin-pack components into ships; tanker/launch math
  campaign.py         # CampaignPlanner: sequence windows, surface-state carry-forward, capability gating
  scenarios.py        # ScenarioManager: named parameter/manifest variants; diffing
  report.py           # xlsx + markdown report generation (openpyxl/pandas)
  cli.py              # CLI entrypoint (argparse or click/typer)
data/
  component_catalog_seed.csv   # seed library (provided)
  assumptions_seed.json        # seed defaults + scenario presets (provided)
tests/
  test_budgets.py     # assert seed case reproduces the spreadsheet numbers (see §7)
  ...
examples/
  precursor_2026.yaml # example mission/campaign definitions
```

**Design principles**
- Pure functions in the engines; state lives in dataclasses. Deterministic and unit-testable.
- Assumptions are injected, never hard-coded — every formula reads from an `Assumptions` object.
- The catalog is the single source of truth for component attributes. Missions reference components by `id` + `qty` + optional `ship` assignment.
- Reports are a thin rendering layer over the engines; never compute in the report layer.

---

## 4. Data model

### 4.1 Component (catalog record)
See `data/component_catalog_seed.csv` for the seeded rows and exact columns. Fields:

- `id` (slug, unique), `name`, `group`
- `power_role`: `consumer` | `generator` | `storage` | `passive`
- `unit_mass_t`, `unit_volume_m3`
- `peak_power_kw`, `duty_cycle` (for consumers)
- `generation_kwe` (for generators), `storage_kwh` (for storage)
- `unit_cost_musd_low`, `unit_cost_musd_high` (internal build cost, USD millions)
- `default_qty`
- `readiness_gate` (which human-readiness gate this retires; see §6)
- `earliest_window` (earliest synod it can realistically fly, e.g. `2026`, `2028`)
- `depends_on` (semicolon-list of component ids or capability flags it requires)
- `notes` (provenance / uncertainty)

Generation and storage are **catalog components too** (`fission_unit`, `solar_module_1000m2`, `battery_module_100kwh`) so the power sizer can either (a) auto-size them from load, or (b) let the user place explicit quantities. Support both.

### 4.2 Mission
- `window_id`, `objective`, `crewed` (bool)
- `manifest`: list of `{component_id, qty, ship?}`
- derived: budgets, ship packing, launches

### 4.3 Window (launch window)
- `id` (e.g. `2026-11`), `synod_index` (0,1,2…), `calendar_label`, `transit_days`, `notes`
- one or more Missions

### 4.4 Campaign
- ordered list of Windows
- **surface state**: components already delivered persist and accumulate (installed power, installed ISRU, habitat volume, etc.)
- **capability flags**: unlocked when prerequisites met (e.g. `isru_operational`, `power_baseload`, `habitat_ready`, `return_propellant_proven`) — used to gate mission types (esp. crewed)
- cumulative rollups: mass delivered, launches flown, cost, power installed

### 4.5 Assumptions & Scenario
- `Assumptions`: all tunables (see `data/assumptions_seed.json`).
- `Scenario`: a named `Assumptions` override + optional manifest/catalog overrides. ScenarioManager runs and diffs them.

---

## 5. The four capabilities (specs)

### 5.1 Compute budgets (`budgets.py` + `power.py`)
Given a manifest (+ Assumptions + power scenario), compute:

**Power/energy** (port exactly from the engineering budget workbook):
```
avg_kw          = Σ (peak_power_kw × qty × duty_cycle)         # over consumers
connected_peak  = Σ (peak_power_kw × qty)
simultaneous_peak = connected_peak × diversity_factor
daily_energy_kwh = avg_kw × sol_hours                          # sol_hours = 24.6

# Solar option
array_m2        = avg_kw × 1000 / solar_yield_w_m2
solar_mass_t    = array_m2 × solar_kg_m2 / 1000
night_kwh       = avg_kw × night_hours                         # night_hours = 12.3
night_batt_t    = night_kwh / battery_wh_per_kg
duststorm_kwh   = avg_kw × dust_days × sol_hours
duststorm_batt_t= duststorm_kwh / battery_wh_per_kg            # flags solar-only infeasibility

# Fission option
fission_units   = ceil(avg_kw / fission_unit_kwe)
fission_mass_t  = fission_units × fission_unit_t
fission_vol_m3  = fission_units × fission_unit_m3
buffer_kwh      = avg_kw × buffer_hours
buffer_batt_t   = buffer_kwh / battery_wh_per_kg
```

**Mass** (baseline = fission power path):
```
fixed_hw_t   = Σ (unit_mass_t × qty)                            # catalog consumers/passives
gen_t        = fission_mass_t (or solar_mass_t per scenario)
storage_t    = buffer_batt_t (or night_batt_t per scenario)
consumables_t= Σ mass of components in group "Consumables & caches"
spares_t     = spares_frac × (fixed_hw_t − consumables_t + gen_t + storage_t)
contingency_t= contingency_frac × (fixed_hw_t + gen_t + storage_t)
grand_total_t= fixed_hw_t + gen_t + storage_t + spares_t + contingency_t
```

**Volume** (same shape; apply `packing_efficiency`):
```
raw_vol_m3       = fixed_vol + gen_vol + storage_vol + spares_frac × fixed_vol
effective_vol_m3 = raw_vol_m3 / packing_efficiency
```

**Cost** (port from cost model):
```
cargo_cost_low/high = Σ (unit_cost_musd_low/high × qty)         # includes generation/storage components
# launch cost handled in packing (needs ship count)
```

Every budget returns both the numbers *and* a comparison against capacity (utilisation %, margin). Reproduce the seed-case numbers in §7 as a regression test.

### 5.2 Pack & size the fleet (`packing.py`)
- Bin-pack manifest components into ships constrained by **both** `payload_mass_per_ship` and `payload_volume_per_ship`. (2D bin packing; a greedy first-fit-decreasing is fine for v1, but keep the packer swappable.)
- Respect explicit `ship` assignments when given; otherwise auto-assign.
- Output: ship count, per-ship mass/volume utilisation, and the binding constraint per ship (mass vs volume).
- **Launch math (critical):**
```
cargo_ship_launches = ship_count
tanker_launches     = ship_count × tankers_per_ship
total_launches      = cargo_ship_launches + tanker_launches
launch_cost_musd    = total_launches × per_launch_cost_musd   # by scenario
```
- Let `tankers_per_ship` and `per_launch_cost_musd` be scenario inputs (low/high per §7).

### 5.3 Plan across launch windows (`campaign.py`)
- A campaign is an ordered list of windows (synod indices → calendar labels via a helper: window 0 = 2026-11, +~26 months each).
- Maintain **surface state**: delivered components persist; power installed, ISRU capacity, habitat volume, cached consumables accumulate.
- **Capability gating:** define capability flags and the components/conditions that unlock them. A mission declaring `crewed=True` must assert prerequisites (e.g. `return_propellant_proven AND habitat_ready AND power_baseload AND life_support_closed`) or the planner raises/flags it. This encodes the "no crew until you can land, power, feed, and return them" rule.
- Roll up per-window and cumulative: launches, mass delivered, cost, installed power vs required, readiness gates retired.
- Support the full multi-decade ramp: windows can scale ship counts up (5 → 20 → 100 …) and shift objectives (recon → infrastructure → crew → base growth).

### 5.4 Compare scenarios (`scenarios.py`)
- A scenario = base Assumptions + overrides + optional manifest/catalog swaps.
- Provide presets in `assumptions_seed.json`: `baseline`, `optimistic` (aspirational launch cost, high reuse, pilot ISRU), `conservative` (near-term launch cost, full-scale ISRU load, higher spares).
- `compare(scenarioA, scenarioB)` returns a structured diff of key outputs (total launches, grand mass, power path, cost range, first-crew window).

---

## 6. Human-readiness gates (capability taxonomy)

Use these as the `readiness_gate` values and capability-flag vocabulary:

`edl_proven` · `precision_landing` · `power_baseload` · `water_supply` · `return_propellant_proven` · `life_support_closed` · `radiation_managed` · `comms_established` · `autonomy_proven` · `infrastructure_ready` · `mobility` · `habitat_ready`

Crewed missions require (at minimum): `edl_proven`, `power_baseload`, `return_propellant_proven`, `life_support_closed`, `habitat_ready`, `radiation_managed`. Make this rule data-driven (a config), not hard-coded.

---

## 7. Regression targets (seed case must reproduce these)

With the seeded catalog + `baseline` assumptions and the precursor manifest (26 components, qty as seeded), the BudgetEngine must reproduce the validated spreadsheet outputs (±1 rounding):

- Fixed hardware mass ≈ **98.5 t**
- Total average load ≈ **354 kW**; simultaneous peak ≈ **429 kW** (diversity 0.85)
- Solar option: array ≈ **11,800 m²**; night battery ≈ **29 t**; dust-storm battery ≈ **290 t** (infeasible)
- Fission option: **9 units**, ≈ **54 t**; buffer battery ≈ **14 t**
- Grand total mass ≈ **236 t** vs 500 t capacity → **~50% utilisation**
- Per-ship (mass/vol): Ship3/power ≈ 81 t / 330 m³; Ship5/habitat ≈ 45 t / 425 m³ (all under 100 t / 1,000 m³)
- Cost model: total launches **55** (10 tankers) to **85** (16 tankers); near-term launch campaign ≈ **$4.95B–$7.65B**; cargo hardware ≈ **$1.9B–$8.2B**

Write `tests/test_budgets.py` to assert these before adding features. They are the contract that we didn't lose anything from the conversation.

---

## 8. CLI surface (v1)

```
mars catalog list [--group G]
mars catalog show <id>
mars budget <mission.yaml> [--scenario baseline] [--power solar|fission] [--format table|md|xlsx]
mars pack   <mission.yaml> [--tankers 16] [--launch-cost near_term]
mars plan   <campaign.yaml> [--scenario baseline] [--format md|xlsx]
mars compare <scenarioA> <scenarioB> [--campaign campaign.yaml]
mars report <campaign.yaml> --format xlsx   # full workbook like the ones we built
```

Mission/campaign definitions live in YAML under `examples/`. Reports should be able to regenerate xlsx workbooks equivalent to (and eventually richer than) `../Mars-Precursor-Engineering-Budget.xlsx`.

---

## 9. Build roadmap (suggested milestones)

- **M1 — Catalog + budgets.** Load seed catalog + assumptions; implement `budgets.py`/`power.py`; pass §7 regression tests. *This alone replaces the current spreadsheets.*
- **M2 — Packing + launch math.** `packing.py`; reproduce cost-model launch totals.
- **M3 — Campaign planner.** `campaign.py`; surface-state carry-forward + capability gating; model 2026 → first-crew window.
- **M4 — Scenarios + diffing.** `scenarios.py`; baseline/optimistic/conservative presets.
- **M5 — Reporting.** `report.py`; xlsx + markdown; charts (per-ship bars, solar-vs-fission storage).
- **M6 — Full ramp.** Extend windows toward a self-sustaining base; scale ship counts; introduce crew missions and surface-growth logic.

---

## 10. Open questions / decisions deferred (resolve during build)

- **Power policy:** is fission the baseline for all crewed-era windows, or does the model let a scenario stay solar-only (and surface the dust-storm risk as a hard fail)?
- **Round-trip vs one-way early crew:** does the campaign assume return capability is mandatory before crew, or allow a settlement/one-way variant (which removes the propellant-return gate but hardens the life-support/resupply requirement)?
- **Development (non-recurring) cost:** track it as a separate ledger (Starship $15B+ already, plus fission/ISRU/habitat R&D), or leave out of per-mission budgets? Recommend: separate optional ledger.
- **ISRU scale ramp:** how does electrolysis load scale from pilot (~150 kW) to full (~1 MW+) across windows? Parameterize per window.
- **Packing fidelity:** greedy first-fit for v1; revisit if ship counts look inefficient.
- **Uncertainty propagation:** low/high cost ranges are in the catalog; decide whether mass/power should also carry ranges or stay point estimates with scenarios doing the sensitivity work.

---

## 11. Provenance & companion files (in the parent folder)

- `../SpaceX-to-Mars-Deep-Dive.md` — the cited research report (six hard problems, timeline, cost, human factors).
- `../Mars-Robotic-Precursor-Flight-Manifest.md` — the narrative manifest this catalog is derived from.
- `../Mars-First-Batch-Cost-Model.xlsx` — launch + cargo cost model (formulas ported in §5.1/§5.2).
- `../Mars-Precursor-Engineering-Budget.xlsx` — mass/power/volume model (formulas ported in §5.1; regression targets in §7).

All seed numbers are notional order-of-magnitude estimates for structure, not vetted specifications. Preserve provenance and uncertainty as real data arrives.
