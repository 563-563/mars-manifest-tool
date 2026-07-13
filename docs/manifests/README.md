# docs/manifests/ — the baseline ship-by-ship manifests

**This is the place to point people for what exactly flies, on which hull, at
what mass, volume, and power, and which requirements each window buys off.**

Two files, same content, two audiences:

- [`manifests.json`](manifests.json) — structured: per window → per ship →
  per item, with window-level rollups (launches, installed kWe, propellant
  banked, population) and the list of requirements each window closes.
- [`manifests.csv`](manifests.csv) — flat: one row per (window, ship, item),
  ready for a spreadsheet or pandas. Columns: `window, ship, component_id,
  name, group, qty, mass_t, volume_m3, avg_load_kw, generation_kwe,
  readiness_gate`.

Both are **generated** from the engine — the ships here are the real packing
output (balanced policy, redundancy anti-affinity, habitat+ECLSS affinity
bundles, spares as explicit cargo, auto-sized power hardware), not a
hand-typed table.

## Regenerate — never hand-edit

```bash
mars manifests inputs/program.json          # -> docs/manifests/*.{json,csv}
```

To change what flies, edit [`inputs/program.json`](../../inputs/README.md)
(the campaign shape) or `inputs/catalog.csv` (component attributes), then
regenerate. If a challenge forces a change, that's the loop: fix the input,
re-run, commit the fresh snapshot — the snapshot can never disagree with the
engine.

## How the numbers relate to requirements

The chain is: **component → capability gate → requirement.**

1. Each catalog item can carry a `readiness_gate` (last CSV column) — the
   capability that hardware serves (e.g. `water_electrolysis` →
   `return_propellant_proven`).
2. Capabilities retire on *demonstrated state*, not delivery — the rules live
   in `inputs/assumptions.json` (`capability_gates`) and include measured
   thresholds like ≥1,400 t of propellant banked or 1,000 sols of integrated
   habitat+ECLSS runtime.
3. Requirements (L0 mission → L2 quantitative criteria,
   [`inputs/requirements.json`](../../inputs/README.md)) verify against those
   gates and against the campaign run directly. Each window's
   `requirements_closed` list in `manifests.json` shows what that window's
   deliveries bought off; the full matrix with verification methods is
   [`docs/REQUIREMENTS.md`](../REQUIREMENTS.md).

Per-ship `mass_utilisation` / `volume_utilisation` are against the verified
per-ship capacity (100 t / 614 m³, carried in the JSON header). Items named
`spares:<group>` are the sparing overhead packed as explicit cargo;
`fission_unit` and `battery_module_100kwh` rows are auto-sized by the power
budget rather than hand-listed in the campaign file.

## What the costs mean — and what is deliberately not costed

Each line item carries `cost_musd_low` / `cost_musd_high`: the catalog's
per-unit cost range × quantity. These are mostly C/D-tier notional ranges
(see `PROVENANCE.md`), which is why they are always a **range, never a
point** — quote them that way.

The line items **are** the program's cargo-hardware cost, not a parallel
estimate: each window's items sum to its `cargo_hardware_cost_musd`
(test-enforced), and those windows sum to the cumulative cargo figure the
story page quotes (~$231B–$967B). `launch_cost_musd` is carried separately
per window (ships × tanker-multiplied launch rates).

Three things are deliberately outside these numbers:

- **Spares** (`spares:<group>` rows, ~26% of packed mass) — mass overhead
  only, uncosted; their cost columns are empty by design.
- **Contingency** (mass-growth allowance) — a mass margin, not a purchase.
- **Development cost** (Starship, fission, ISRU R&D) — a separate ledger
  the model intentionally does not track (`docs/CONSIDERED.md`).
