# Comparative review — how our program plan stacks against published Mars-base architectures

*Compiled 2026-07-09. Sources fetched and read, not just cited.*

## Who we compared against

1. **Casey Handmer** (ex-JPL, Terraform Industries) — the most quantitative independent
   Starship-Mars analyst: [Starting the Mars Base](https://caseyhandmer.wordpress.com/2020/05/21/starting-the-mars-base/),
   [Powering the Mars base](https://caseyhandmer.wordpress.com/2024/11/05/powering-the-mars-base/) (2024),
   [What can we send to Mars on the first Starships?](https://caseyhandmer.wordpress.com/2025/02/24/what-can-we-send-to-mars-on-the-first-starships/) (2025).
2. **Peer-reviewed Starship architecture** — [*New Space* 2022 (PMC9527650)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9527650/):
   uncrewed wave → crew at the *next* window, ~600 t water per refill, RedWater
   Rodwell wells, 25 MW-class nuclear long-term.
3. **NASA DRA 5.0** — [Design Reference Architecture 5.0](https://www.nasa.gov/wp-content/uploads/2015/09/373669main_2008-12-04_mars_dra5_executive_summary-presentation.pdf):
   split cargo/crew missions, cargo pre-deployed one synod ahead, nuclear surface
   power, ISRU descoped to **ascent oxygen only** (~92 kWe peak).

## Where they agree with us (convergent findings)

- **Pre-deploy cargo one synod before it's needed** (DRA 5.0's split mission = our
  one-window verification margin rule).
- **Nuclear for the crewed era** (DRA baseline; the 2022 paper long-term).
- **Water scale**: the 2022 paper's ~600 t per refill brackets our 684 t net per
  1,400 t load.
- **Redundancy philosophy**: the 2022 paper's "multiple mobility platforms, backup
  habitation, pre-positioned supplies, autonomy proven before crew" is exactly our
  loss-tolerance + gating structure — we just quantify it.
- **Crew timing discipline**: everyone gates crew on demonstrated ISRU; nobody
  reputable flies crew before propellant production works.

## Where we meaningfully differ

| Topic | Them | Us | Verdict |
|---|---|---|---|
| Crew timing | 2022 paper: crew at the *second* window (~52 months after first landing) | Fourth window (propellant banked + 1,000-sol ECLSS demo) | Ours is defensibly stricter; theirs assumes gates retire on first attempt |
| Early power | Handmer + 2022 paper: **solar-first** (mass-produced panels, oversize the farm) | Fission-first (dust-storm battery math) | Partly a modeling artifact on our side — see adoption #1 |
| Water risk | Handmer: **the** dominant near-term uncertainty; prospect (orbitally, even with kinetic penetrators) *before* committing infrastructure | We retire `water_supply` by delivering hardware; site-water risk is unmodeled | He's right — see adoption #2 |
| ISRU energy | Handmer: 17 GWh per 240 t CH₄ ≈ **~70 kWh/kg CH₄** (≈14 kWh/kg propellant) | ~35 kWh/kg CH₄ (7.6 kWh/kg propellant) | We may be ~2× optimistic; his figure includes real-world inefficiencies |
| ISRU scope | DRA 5.0: **oxygen-only** ISRU (no water dependency; methane from Earth) | Full Sabatier chain | Their descope is a compelling fallback — see adoption #3 |

## Ideas adopted (all five implemented 2026-07-09)

1. **Survival-vs-production load split for storm sizing.** Our dust-storm battery
   sizes for the *full* average load (290 t → "solar infeasible"). Handmer's framing:
   production loads (ISRU) can *pause* during storms; only survival loads (thermal,
   comms, ECLSS) need ride-through. Sizing storage for critical loads only would cut
   the solar dust-storm battery ~10× and make the solar-vs-fission trade honest
   rather than rigged for fission. **Highest-value model change on this list.** *Adopted: catalog `load_class` column; storm storage sized on ~50 kW survival loads (41 t) with the 290 t full-load figure kept as reference.*
2. **Prospect-before-commit decision point.** Add a `water_confirmed` gate between
   window 0's prospecting and the window-1 fuel-factory commit, and note the real
   schedule: window-0 data returns ~18 months before the window-1 fleet must ship —
   tight but workable. *Adopted: `water_confirmed` capability (200 prospecting sols) gates the window-1 factory via the new mission-level `requires` mechanism. Orbital prospecting assets remain outside the surface-cargo scope — noted, not modeled.*
3. **Oxygen-only ISRU fallback scenario** (from DRA 5.0). O₂ is 78% of propellant
   mass and can be made from atmosphere alone (MOXIE-style or via Sabatier O₂
   co-product paths) — no mining, no water risk. Cost: ~304 t of Earth-supplied CH₄
   per return load ≈ 3–4 extra cargo ships. A clean plan-B if window-0 prospecting disappoints. *Adopted: `oxygen_only_isru` scenario (SOE chain, 304 t CH₄ import, ~4 extra ships, 13.7 kWh/kg O₂).*
4. **ISRU energy sensitivity range.** Carry 7.6–15 kWh/kg propellant as an explicit
   low/high (our chain math vs Handmer's all-in figure); full-scale power becomes
   0.85–1.7 MW, which still brackets the research constant. *Adopted: `isru_high_energy` scenario (15.3 kWh/kg, 1.7 MW).*
5. **Rodwell rate anchor.** RedWater-class well: ~1 t water per 10 days per well
   (2022 paper) — a real datum to check `water_processing` rates against when
   sharpening Tier-D ISRU rows. *Adopted: recorded as the rate anchor in PROVENANCE §2b.*

## What we have that none of them do

Quantified loss-tolerance per window, propellant-*banked* crew gating, idle-mass
lifecycle discipline, and a machine-checked requirements buy-off matrix. The
published architectures assert these principles; the tool enforces them.
