# inputs/ — the entire editable input surface

Everything the model reads lives in this one directory, split by concern so you
can edit only the part you care about. Change a file here, re-run, and the
consequences propagate through the engine, the tests, and the browser views.
Nothing is computed in this directory; it is pure input.

| File | Format | Holds | Edit it to… |
|---|---|---|---|
| [`program.json`](program.json) | JSON | The campaign shape: launch windows, ship counts, crew, and each window's manifest | Front-load, back-load, or ramp the program |
| [`assumptions.json`](assumptions.json) | JSON | The tunable knobs (fleet, power, ISRU, EDL, cost, overheads, lifecycle) + named scenario presets | Change a physical/cost assumption or add a preset |
| [`city.json`](city.json) | JSON | City-ramp anchors: population milestones, per-capita rates, import-mass decay, closure ladder, growth rule | Retune the post-crew city model |
| [`requirements.json`](requirements.json) | JSON | The decomposed requirements tree the campaign is bought off against | Add/loosen/tighten a verifiable requirement |
| [`catalog.csv`](catalog.csv) | CSV table | The hardware catalog: 37 components × their mass/volume/power/cost attributes | Add a component or fix an attribute |

`catalog.csv` stays a CSV because it is genuinely a table (open it in any
spreadsheet). Everything else is JSON.

> The frozen regression fixtures (`examples/*.yaml`) are **not** inputs. They
> are pinned to historical values on purpose and exist only to prove the
> engine's math hasn't drifted. Never edit them to change the plan; edit the
> files here.

---

## The workflow

```bash
# 1. edit a file in inputs/

# 2. check nothing broke (the requirements gate + regression contract)
.venv/Scripts/python.exe -m pytest tests/ -q

# 3. see the result
mars plan inputs/program.json --format md
mars requirements inputs/program.json --out docs/REQUIREMENTS.md
mars lifecycle inputs/program.json
mars manifests inputs/program.json     # regen docs/manifests/ (CI checks freshness)

# 4. regenerate the browser views (optional)
python viz/export_dashboard_data.py    # inputs/ -> viz/dashboard_data.json
python viz/build_scrolly.py            # -> viz/mars_manifest_story.html
```

The CLI auto-discovers this directory (it walks up looking for
`inputs/catalog.csv`), so you rarely pass paths by hand. Override with
`--inputs-dir` if you keep a variant set elsewhere.

---

## program.json — the shape of the campaign

This is the file most people want. It is a list of `windows`, each with one or
more `missions`, each carrying a `manifest` of catalog components:

```jsonc
{
  "windows": [
    {
      "id": "2037-07",              // launch-window label (year-month)
      "synod_index": 3,            // 0-based transfer-window number
      "objective": "First crew ...",
      "missions": [
        {
          "crewed": true,
          "settlers": 12,          // people delivered this window
          "ships": 21,             // cargo ships (drives launches + cost)
          "packing_policy": "balanced",
          "pack_spares": true,
          "requires": ["water_confirmed"],   // gates that must be met to fly
          "manifest": [
            { "id": "habitat_module", "qty": 4 },
            { "id": "consumables_cache", "qty": 12 }
          ]
        }
      ]
    }
  ]
}
```

**Reshaping the program — the three moves you asked for:**

- **Front-load.** Move ships/settlers earlier: raise `ships` in 2033/2035, drop
  them in 2041/2044. Watch the propellant and life-support gates in
  `mars plan` — pulling crew earlier can trip `return_propellant_proven` if the
  fuel plant hasn't banked enough yet.
- **Back-load.** The reverse. The gates simply retire later; the requirements
  matrix will tell you if first crew slips.
- **Massively ramp.** Push `settlers` and `ships` up in the city-ramp windows.
  The fleet-growth advisory (total landed fleet should at least double per
  synod) and the per-window consumables check will flag anything unphysical
  rather than silently accepting it.

Every knob here also lives, live, in the story page's **Adjust the model**
drawer — editing this file is the persistent version of that.

## assumptions.json — the knobs + the presets

- `baseline` holds the scalar assumptions in named groups: `fleet` (payload
  mass/volume per ship, tankers per ship), `power`, `isru`, `edl`, `cost`,
  `overheads`, `lifecycle`.
- `scenarios` are presets that `inherits` from baseline and list `overrides`
  (dotted keys, e.g. `"fleet.tankers_per_ship": 10`). To add your own, copy an
  existing scenario block and change the overrides. Run it with
  `mars plan inputs/program.json --scenario yourname` or compare two with
  `mars compare baseline yourname --campaign inputs/program.json`.
- `capability_gates` defines what unlocks each capability and what a crewed
  mission requires. This is the data behind the gating, not hard-coded logic.

## city.json — the post-crew city model

Population milestones (survival floor / settlement / autarky), per-capita
anchors (power, food area, habitable volume, consumables), the import-mass
decay curve keyed to industrial-closure stage, the fleet-growth rule, and the
closure ladder. Endpoints are sourced; intermediate steps are interpolation.

## requirements.json — the buy-off contract

A tree of `requirements`, each with an `id`, `level` (0 mission need → 2
machine-checkable criterion), `statement`, `rationale`, `source`, and (on
leaves) a `verify` block. `verify.method` uses the standard **A**nalysis /
**I**nspection / **D**emonstration / **T**est vocabulary; `verify.kind` is the
machine criterion (`capability`, `min_qty`, `min_installed_kwe`,
`min_propellant_t`, `min_landings`, `isru_rate`, and recurring checks like
`power_covers_load`, `fits_fleet`, `loss_tolerant`). CI fails if any
requirement goes OPEN against the plan.

## catalog.csv — the hardware

One row per component. Columns: `id, name, group, power_role, unit_mass_t,
unit_volume_m3, peak_power_kw, duty_cycle, load_class, generation_kwe,
storage_kwh, unit_cost_musd_low, unit_cost_musd_high, default_qty,
readiness_gate, earliest_window, depends_on, notes`. A manifest entry in
`program.json` references a component by its `id`.

---

## Provenance and confidence tiers

Every value in the model carries a confidence tier:

- **A** — physical constant
- **B** — published spec or measurement
- **C** — stated derivation
- **D** — notional estimate

`city.json` and `requirements.json` carry their `tier` and `source` **inline**,
next to each value. The scalar assumptions and catalog rows are tier-labeled in
[`PROVENANCE.md`](../PROVENANCE.md), which also holds the verification log (the
record of each source re-checked against the exact claim it supports, including
the two cases where our own numbers failed re-verification and the baseline was
re-anchored). The policy is absolute: the baseline always carries the
best-verified number, never a stale one with a downgraded tier.
