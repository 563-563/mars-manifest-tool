# viz/ — the browser views, generated from the engine

These build the published browser artifacts from the same engine outputs the
CLI produces. Nothing here computes program physics; it renders. The rule from
`CLAUDE.md` holds: **reports only render; the engine is the source of truth.**

## The story page (with the live what-if drawer)

```bash
python viz/export_dashboard_data.py   # engine -> viz/dashboard_data.json
python viz/build_scrolly.py           # data   -> viz/mars_manifest_story.html
```

`mars_manifest_story.html` is a self-contained scrollytelling essay: prose on
the left, a sticky manifest panel on the right that advances through the seven
launch windows as you scroll, and an **Adjust the model** drawer.

### How the what-if drawer stays honest

The drawer recomputes program figures live in the browser as the reader turns
curated knobs (tankers/ship, launch-cost basis, ISRU commissioning ramp,
return-load requirement, ISRU energy, per-capita imports, and per-window ship
& crew counts). This is a *second* implementation of the campaign math, so it
is held to the project's no-drift discipline two ways:

1. **Calibrated to the source of truth.** `dashboard_data.json` carries the
   Python engine's exact baseline. At baseline knob values the browser
   reproduces those numbers exactly; every knob is a closed-form overlay on top
   of that anchor; **Reset** snaps back to the engine truth. The page labels
   itself "source of truth" vs "live estimate" at all times.
2. **Guarded by a test.** `tests/test_whatif_overlay.py` runs the real engine
   across baseline / optimistic / conservative_feasibility and asserts the
   exact closed forms the browser's `compute()` uses still reproduce it
   (launch multiplier, cost split, commissioning ramp, import decay, EDL
   rule-of-three). If the engine's shape changes, that test fails — the signal
   that `build_scrolly.py`'s JS must be updated to match.

The knobs that are *not* wired (they hold at the engine baseline and the page
says so) are anything requiring a re-pack or re-gate: changing a ship count
adjusts launches/cost but not the manifest mass, and capability-gate retirement
order is held except the propellant→crew coupling, which the panel flags
explicitly.

## Published URLs

- Story:       https://claude.ai/code/artifact/b0b7a7f8-525e-499b-9512-7501ead32fd3
- Console:     https://claude.ai/code/artifact/1fa983e5-510f-401f-9820-bac33444ca7c
- Walkthrough: https://claude.ai/code/artifact/3182378f-acac-47a3-b381-7ce2a6d36a18

To republish after regenerating, re-upload the HTML to the same artifact URL.
