# CONOPS-1: Concept of Operations: the robotic era through first crew

## 1. Purpose and scope

This document describes how the program's first three flights operate:
window 0 (2031) through the first crew's surface establishment (2036). It
is written to be self-contained. A reader needs no other document to
follow the mission, though every quantity here is traceable to the
references in §6. A second document, CONOPS-2, will cover the rotation and
city era (2037 onward) once the constellation-refresh and
rotation-logistics decisions close.

Program quantities (fleet sizes, masses, propellant, gates) are engine
output from `inputs/program.json`. Operational sequences, meaning the
geometry, orbits, and timing inside a window, are doctrine recorded here
and in the considered ledger; the planner deliberately does not model
them. Every operational quantity is derived or heritage-anchored in
**Appendix A**, which is generated into this document from the provenance
ledger and freshness-tested against it. Hardware spec-and-heritage sheets
live in `docs/HARDWARE.md`.

## 2. Mission objective and success criteria

The mission-level requirement (L0-MSN-01): *the first crew shall arrive at
a powered, provisioned, and fueled Mars base with a demonstrated return
path, and no single cargo-ship loss shall defeat the campaign.*

Success is defined by gates that retire on demonstrated state, never on
hardware delivery. Crew may not launch until all six are green:

| Gate | Retires when |
|---|---|
| `edl_proven` | a 100 t-class ship has landed (statistics accumulate thereafter) |
| `power_baseload` | continuous, dust-storm-tolerant power is operating |
| `return_propellant_proven` | ≥1,400 t of methalox is *produced and banked* on the surface |
| `life_support_closed` | the integrated habitat+ECLSS article has run **1,000 sols** |
| `habitat_ready` | pressurized volume beyond the landed ships exists |
| `radiation_managed` | regolith-shielded storm shelters are in place |

One more condition sits on top: the return-flight posture (L1-RET-01). An
uncrewed ship flies the complete Mars-to-Earth profile before crew launch
and reports during their transit. End state: December 2035, twelve people
alive and working at a base holding five-plus fueled return loads.

## 3. Background: the program in brief

Six flights, one every 26 months, each earning permission for the next:

| Flight | Window | Ships | People | Role |
|---|---|---|---|---|
| 1 | 2031 | 5 | - | Precursor: land, power, prospect; start the clocks |
| 2 | 2033 | 10 | - | Fuel factory ×2 + survival bridge; all gates green |
| 3 | 2035 | 15 | 12 | **First crew** + pilots for everything that scales |
| 4 | 2037 | 34 | 112 | Village (CONOPS-2) |
| 5 | 2039 | 97 | 512 | Town (CONOPS-2) |
| 6 | 2041 | 161 | 1,112 | Settlement (CONOPS-2) |

Five doctrines shape every manifest, and this document applies them
operationally:

1. **Evidence gates, not calendar dates.** Nothing commits until the
   thing it depends on is demonstrated.
2. **Every number carries a receipt**: a source and confidence tier
   (§5). Claims that fail verification are recorded as failing.
3. **No single ship loss may cost a schedule-critical capability.**
   Critical hardware flies at quantity ≥2, spread across hulls.
4. **Pilot one synod ahead; scale when the demand ships.** Provisions
   pre-land one synod of survival (the *bridge*); depth flies with the
   people.
5. **No air freight.** Fleets are sized to their cargo at ≤90% of mass
   capacity, and floored windows top up with risk depth.

On the dates: first crew in 2035 sits beyond the aggressive end of
published consensus, and the plan says so plainly. It is an option on
2035, not a promise. Under the peer-reviewed skeptic scenario
(`conservative_feasibility`) every gate holds and crew slips
automatically to 2037. The evidence chooses the date; the sequencing just
makes the early date possible.

## 4. Grounding: the environment and the clock

**The synodic clock rules everything.** Earth and Mars align for
low-energy transfer once every ~26 months (779.9 days), and a
conjunction-class crossing takes ~210 days at the fast end. Miss a window,
wait a synod.

Return geometry is offset: a ship that arrives must wait ~460 days on the
surface before the Mars-to-Earth window opens, so there is one return
opportunity per synod. The first fuel-feasible one falls in January 2035.
Production planning uses ~600 usable sols per synod.

All surface operations run under a 4-22 minute one-way light delay, plus
a ~2-week comms blackout at solar conjunction each synod. Robots execute,
Earth supervises by exception, and nothing on the critical path requires
a real-time human in the loop.

**The environment, operationally.** Gravity is 0.38 g. A Mars sol is
24.66 h; timelines here use sols on the surface and days in flight. The
CO₂ atmosphere is ~6 mbar: thick enough for aerobraking, entry heating,
and dust, far too thin to breathe or to slow a lander without propulsion.

Global dust storms last weeks to months (the 2018 storm ended the
Opportunity rover). They starve solar power but only inconvenience
fission, which is why fission anchors the baseline and solar is carried
as a scenario. Galactic cosmic radiation is unshielded by the thin
atmosphere, so crew-era operations require regolith-covered storm
shelters (the `radiation_managed` gate).

Water exists as subsurface ice at mid-latitudes. It is known from orbit
in general and unproven at any specific site at mining grade, and that
gap is the single uncertainty this mission's first month exists to
retire.

## 5. How to read the numbers

Every figure in this document carries (or inherits) a confidence tier
from the provenance ledger:

| Tier | Meaning |
|---|---|
| **A** | Physical constant or directly measured value. Will not change. |
| **B** | Published program specification, disclosed figure, or flight-measured datum. Could change as programs evolve. |
| **C** | Derived from published figures by a stated calculation. Check the derivation, not the source. |
| **D** | Notional engineering estimate. Order-of-magnitude only; first target for replacement with real data. |

Rows marked ✅ verified with a date were re-fetched from the primary
source and checked against the exact claim on that date. Where this
document states a number without a tier, it is engine output computed
from tiered inputs.

The honest summary: the architecture rests mostly on A/B/C anchors, while
most hardware masses are still Tier D. That split is the reason gates
retire on demonstrated state rather than on specifications.

## 6. Referenced documents

| Document | Role |
|---|---|
| `inputs/program.json` | The program itself: windows, fleets, manifests (engine input) |
| `docs/REQUIREMENTS.md` | Machine-checked requirements buy-off matrix (generated) |
| `docs/manifests/` | Ship-by-ship manifests and the flight summary (generated) |
| `PROVENANCE.md` | Every input's value, source, tier, and verification log (generated from `inputs/provenance.json`) |
| `docs/CONSIDERED.md` | Decision register: everything weighed and adopted, rejected, or deferred (generated from `inputs/considered.json`) |
| `docs/HARDWARE.md` | Spec-and-heritage sheets for every element in this CONOPS |
| `docs/NARRATIVE.md` | The same program told in plain language |

## 7. System elements

- **Transport segment.** Starship-class cargo/crew ships. Cargo hulls fly
  one-way and become surface assets on arrival: pressure vessels, tankage,
  steel. Each departure costs ~17 launches including tanker refueling. No
  ship enters Mars orbit; all arrivals are direct entry from the
  interplanetary approach.
- **Orbital segment.** One 6 t constellation set, deployed at window 0:
  an areostationary relay (~2 t, continuous base-Earth link) and 3-4 polar
  SAR/ultraspectral smallsats (~600-800 kg each) for shallow-ice radar
  mapping, impact observation, and landing-zone reconnaissance. Deployed
  by dispenser on approach; each spacecraft self-captures (~0.9 km/s
  chemical) and later aerobrakes to its operational orbit.
- **Surface segment.** Fission power grid, ISRU propellant plant(s),
  water mining chain, habitat/ECLSS demonstration articles, robot
  workforce (humanoids, rovers, cranes, sintering rigs), comms/nav ground
  stations, and pre-landed consumables (the survival bridge).
- **Earth segment.** Launch and refueling infrastructure (the four
  L1-TRANS preconditions: orbit, reuse, refill, chill), mission operations
  under light delay, and the materials-and-labs loop that receives
  returned samples.

## 8. Phase R0: Earth-side preconditions (before 2031)

Orbital Starship, routine reuse, orbital propellant transfer, and
long-duration cryo storage must all be demonstrated before window 0
commits (L1-TRANS-01..04). These are per-scenario readiness flags: the
baseline assumes them true, and `conservative_feasibility` flips
refill/chill so the requirements matrix goes visibly open.

## 9. Phase R1: land, power, prospect (window 0, Jan 2031 to Mar 2033)

**Objective:** turn the unknowns that block everything downstream into
measurements, with no single ship loss costing a schedule-critical
capability.

**9.1 Launch and transit.** Five ships depart January 2031 (~85 launches
with tankers), 210-day transit. Every schedule-critical capability flies
at quantity ≥2 spread across hulls. The ISRU chain's bottleneck steps fly
at quantity 3: at 50/50 landing odds, qty-2 keeps the five-component chain
alive ~24% of the time, and qty-3 raises that to ~44%.

**9.2 Approach and deployment (arrival day, ~Aug 2031).** Hours to days
before entry interface, dispensers release two payload groups on targeted
approach trajectories (MSL-ballast heritage, Appendix A; zero Δv cost to
the ships): the equatorial group (areostationary relay) and the polar
group (science smallsats, carrying the kinetic penetrators). Ships proceed
to direct entry. The relay's first job is EDL telemetry for its own fleet.

**9.3 Landing.** Five direct-entry landings at the orbitally selected
site. Per-ship P(land) ≈ 0.5 at this window; the redundancy spreading
exists for this case. Surviving hulls are safed, and the robot workforce
(10 humanoids, rovers, cranes) begins deployment: power grid first
(840 kWe fission plus storage), then comms/nav ground stations, then the
pilot ISRU chain.

**9.4 The 30-sol water survey (sols ~0-30).** The science smallsats
capture into 1-sol resonant ellipses, putting a periapsis pass over the
site every sol (Δv ladder in Appendix A), and begin observing
immediately. Penetrator strikes are commanded from orbit, one or two per
sol from ~sol 5: ~20 rods per set (100-150 kg, steel/tungsten, impact
3.5-4 km/s), each strike timed near an observer pass and geometry-vetted.
No strike lands inside the ~10 km base keep-out (sized by ejecta
ballistics, Appendix A), and strike ground-tracks are oriented so
along-track dispersion points away from assets. Fresh craters are read
over repeated passes: imaging, radar sounding, ice-sublimation
monitoring, with plume spectroscopy taken opportunistically. Each strike
also serves as a calibrated seismic source for base-region subsurface
structure. Ground truth from 30-40 impact points calibrates the radar
into a district map of order 10⁴ km². Inside the keep-out, the two
drilling prospectors ground-truth the near-field mining patch the slow
way. `water_confirmed` closes at ~sol 30 by the fast path, with drilling
(~200 sols) as the independent fallback.

**9.5 Commissioning and steady state (sols 30+).** The pilot chain runs
up to ~1.5 t of methalox per day, banking 483 t by 2033: proof of
chemistry, not production. Two demonstration clocks start, with the
integrated habitat+ECLSS article beginning its 1,000-sol run (completes
mid-2034). The science sats aerobrake to circular polar mapping orbits.
The base operates autonomously under light delay; robots execute plans
and Earth supervises by exception.

**Phase exit criteria:** ten capabilities live (EDL, power, precision
landing, comms, autonomy, mobility, infrastructure, habitat, water
supply, water *confirmed*). Half the program's weighted risk is retired.

## 10. Phase R2: the fuel factory, doubled (window 1, Mar 2033 to Jan 2035)

**Commit decision (mid-2032).** The factory fleet ships only if window-0
prospecting confirmed site water (`requires: [water_confirmed]`), with
~18 months between data return and departure to reshape the mining buy
around measured ice grade. If water had failed, the program either
relocates (costing a synod) or switches ISRU mode to the DRA-5.0-style
oxygen-only fallback, which needs no water and imports methane at ~4
ships per return load.

**10.1 Arrival (Oct 2033).** Ten ships (~88% full) land on the graded
zone prepared by the window-0 robots. Cargo: two rate-matched ISRU
chains (window-0's pilot becomes the hot spare), their reactors
(3,000 kWe total), and the 45 t survival bridge.

The bridge is one synod of food, water, and oxygen for twelve, and it is
the single exception to fly-with provisioning (the bridge-not-depth
doctrine in the considered ledger). Its customer is a common-mode arrival
failure, so it must exist and be robot-verified on the ground *before*
any crew commits. Everything beyond one synod flies with the crew in
2035.

**10.2 Plant operations.** The doubled plant commissions on the ramp
(60% first-synod factor) toward 7.7 t of methalox per day, a full
1,400 t return load roughly every six months, with 3,223 t banked by the
2035 window. Robots position and bury the radiation shelters, verify the
bridge caches, and begin sintering landing pads for the next fleet.
Mid-2034 the 1,000-sol ECLSS demonstration completes.

**10.3 Return-flight ground segment.** The receipt flight needs a ground
segment as much as a fuel supply, and this window builds it from assets
already on the manifest:

- *The tank farm is the fleet.* Banked methalox stores in the main tanks
  of landed one-way hulls; each holds a full ~1,200 t load, so three
  hulls' tankage covers everything banked through 2035. Robots fit the
  farm hulls with multi-layer insulation blankets; at the ~99% heat-flow
  reduction MLI provides, boil-off runs of order 1 t per hull-day and the
  plant's reliquefaction loop absorbs it for a ~100 kW-class overhead
  (research anchors in PROVENANCE §5c; exact power is a backlog item).
  Zero-boil-off cryocoolers for Mars methalox are a named NASA technology
  line, in testing but not shelf hardware. No dedicated storage tanks
  fly.
- *The ascent pad.* A landing pad takes a nearly-empty ship on a short
  braking burn; a launch puts full thrust into the ground for the whole
  commit. The sintering rigs thicken one pad to launch grade, sited at
  debris standoff from the base, and robots emplace the insulated cryo
  transfer run from the tank farm to it. Standoff distances are doctrine,
  not yet quantified (plume-ejecta modeling is an open item in the
  ledger).
- *Demonstrator selection.* A window-1 hull in the best post-landing
  health is chosen for the receipt flight; robotic survey of its
  Earth-entry TPS, engines, and tankage begins a full year before
  departure.

**Phase exit criteria:** every crew gate green a full synod before anyone
launches. Propellant banked (≥1,400 t), life support closed, radiation
managed, habitat ready, EDL statistics accumulating (15 landings), power
at crew scale.

## 11. Phase R3: The receipt flight (Jan 2035 to Aug 2035)

The plant's second tankful buys the rehearsal.

**11.1 Pre-flight campaign (late 2034).** The selected hull moves to the
ascent pad and is fueled from the tank farm over several weeks: the first
ISRU propellant transfer and cryogenic hold-through-countdown ever
performed. Robots complete the TPS survey and replace suspect tiles from
spares, run engine chill cycles and spin-primes, and finish with a short
static fire on the pad: the first rocket firing on Mars since the ship's
own landing, and the pad's qualification event. This campaign is the
mitigation for a genuinely novel risk: no cryogenic engine has ever
restarted after long dormancy on a planetary surface, and NASA's own
Mars Ascent Vehicle chose solid motors in 2019 partly to avoid exactly
this problem (PROVENANCE §5c). Countdown is autonomous
under light delay; Earth holds a veto up to light-time, and the commit
criteria are simple: telemetry green, farm topped, and the constellation's
weather watch showing no dust storm inbound.

**11.2 The flight (Jan to Aug 2035).** Three-engine ascent off the
sintered pad, with the base protected by the standoff geometry, then
trans-Earth injection (~6.5 km/s total, single stage, since no orbital
tanker exists at Mars). The areostationary relay carries the ascent
telemetry. A 210-day cruise follows, then Earth entry at ~11.6 km/s;
that entry is roughly twice the speed of a Mars arrival and eight times
the heating, a TPS qualification of its own (L2-RET-02).

Cargo home: a tank of Mars-made methalox and a crate of dust-weathered
components for Earth-lab analysis. Arrival at Earth comes in August 2035,
during the first crew's outbound cruise.

**11.3 What it proves.** The flight retires the L1-RET branch and closes
the mission-level requirement (L0-MSN-01) at the window before crew. Just
as important, it qualifies the *ground segment*: the pad, the transfer
run, the checkout regime, and the autonomous countdown are the same ones
the crew's own March 2037 departure will use.

## 12. Phase C1: First crew (May 2035 to 2036)

**12.1 Commit posture (May 2035).** Twelve crew launch with the
demonstrator still inbound: **the program's one deliberately cut corner,
priced in the open.** Commit criteria: all six crew gates green on
demonstrated state, ≥1,400 t in the tanks *after* the demo's burn, the
verified bridge on the surface, and the demo in flight. If the demo fails
during their cruise (its report lands in August; they land in December),
the crew proceeds to a powered, provisioned base and holds one window
while the fix flies. The caches cover a missed return window with years
of margin. Their own return, ~March 2037, flies a profile proven nineteen
months earlier.

This blind spot is the price of the accelerated schedule, and it is worth
stating plainly: under the archived conservative program (crew 2037), the
demo's August 2035 report lands ~23 months *before* the crew commit and
the corner does not exist. Accelerating crew to 2035 created it; reverting
to 2037 removes it. The program carries the 2035 option because the hedge
(bridge, caches, a proven profile before the crew's own return) prices the
residual risk honestly.

**12.2 Fleet arrival sequencing (Dec 2035).** Fifteen ships. Cargo hulls
enter first and the crew ship last, onto sintered pads, with the
constellation providing EDL telemetry and the surface beacons precision
guidance. The crew lands on 8,057 t of banked propellant (five-plus
return loads), 1,500 m³ of pressurized volume (125 m³ per person against
the 76.5 m³ standard), and a 26-month consumables bridge that flew beside
them.

**12.3 Surface operations.** The twelve are commissioning engineers, not
survivors. Their cargo is the future at pilot scale: 12 agriculture
modules (first crops), the first regolith refinery (molten-regolith
electrolysis), the first polymer plant (Sabatier to Fischer-Tropsch to
HDPE), hot-spare ISRU depth, and a robot workforce grown to ~100. Every
pilot's data shapes the 2037 village's scale buy, one synod ahead. Site
prep for the 34-ship village fleet continues throughout.

**12.4 Contingency postures.**
- *Return-demo failure:* land anyway; hold one window on caches; the fix
  flies on the 2037 fleet; crew returns ~May 2039 at the latest.
- *Partial fleet loss on arrival:* capabilities survive by redundancy
  spreading plus surface backstops. The loss-tolerance requirement
  (L1-LOG-02) is machine-checked for this case.
- *ISRU plant fault:* two independent chains plus the pilot hot spare; a
  full chain outage still refills a return load within the stay.
- *Skeptic-world commissioning (the `conservative_feasibility` case):*
  gates hold, the 2035 crew window auto-blocks, and the program becomes
  the archived conservative plan: crew 2037, no doctrine change.

## 13. Communications and autonomy

Continuous base-Earth relay via areostationary; surface mesh via two
relay ground stations plus beacons; 4-22 min one-way light delay
throughout, with a ~2-week conjunction blackout each synod that the base
rides out autonomously.

Doctrine: robots execute, Earth supervises by exception, and nothing in
the critical path requires a real-time human in the loop. That includes
the strike campaign, plant commissioning, pad construction, and the
receipt flight's countdown. The crew adds on-site judgment, not remote
control.

## 14. Traceability

Phase exits map to the machine-checked gates: R1 retires the ten window-0
capabilities; R2 retires `return_propellant_proven`,
`life_support_closed`, and `radiation_managed` (and L0-MSN-01 closes); R3
retires the L1-RET branch; C1 spends them and closes the two crew-scale
quantity requirements (L2-HAB-02, L2-LS-03).

The buy-off matrix (`docs/REQUIREMENTS.md`) and flight summary
(`docs/manifests/SUMMARY.md`) are the generated, test-enforced views of
the same claims.

What this document adds, and the model does not check, is geometry and
intra-window timing: keep-out radii, strike scheduling, arrival
sequencing, orbit choices, pad standoff. Those are doctrine, ledgered in
`docs/CONSIDERED.md`, awaiting a spatial/timing layer if one is ever
built.

---

## Appendix A: operational quantities: derivations and heritage

<!-- CONOPS_BASIS:BEGIN -->
<!-- generated from inputs/provenance.json 5b by `mars ledgers`; do not hand-edit -->
Added 2026-07-20 alongside `docs/CONOPS.md`. These are the doctrine-layer quantities the planner does not check (geometry, orbits, impact energetics). Derivations are shown inline. Heritage rows marked ✅ were re-fetched and verified on the date shown, per the §8 practice. Constants: Mars μ = 42,828 km³/s², surface g = 3.71 m/s², arrival v∞ ≈ 2.65 km/s (Hohmann, §5a).

| Quantity | Value | Tier | Derivation / heritage |
|---|---|---|---|
| Hyperbolic periapsis speed (300 km alt) | ~5.5 km/s | **C** | v = √(v∞² + v_esc²) with v_esc(300 km) = √(2μ/3690 km) ≈ 4.82 km/s, so √(2.65² + 4.82²) = 5.50 km/s. Pure two-body arithmetic on §5a constants. |
| Satellite capture Δv: minimal / 1-sol resonant / direct-to-LMO | 0.68 / 0.90 / 2.09 km/s | **C** | Burns at 300 km periapsis: to barely-bound = 5.50 − 4.82; to a 1-sol-period ellipse (T = 88,775 s → a ≈ 20,440 km, apoapsis ≈ 37,200 km, v_p = 4.60) = 5.50 − 4.60; to 300 km circular (v_c = 3.41) = 5.50 − 3.41. The resonant ellipse is the CONOPS choice: daily periapsis passes over the site during the 30-sol survey, for ~26% propellant fraction on storables (Isp 320 s). |
| Areostationary circularization (from 300 km × areostationary-radius ellipse) | ~0.65 km/s | **C** | Areostationary radius 20,428 km (T = 1 sol). Apoapsis burn: v_circ = √(μ/20,428) = 1.45 km/s; ellipse apoapsis speed = 0.80 km/s, so Δv = 0.65. Relay all-in ≈ capture 0.68 + 0.65 + trims ≈ 1.4 km/s. |
| Aerobraking in place of ~1 km/s of propellant | months-scale, flown twice | **B (verified 2026-07-20)** | ExoMars TGO aerobraked March 2017 to February 2018 (11 months, paused for conjunction), shedding ~3,600 km/h (~1 km/s) from a 98,000 × 200 km capture ellipse to reach 400 km circular ([Universe Today](https://www.universetoday.com/138480/esas-exomars-completed-aerobraking-maneuvers-bring-circular-400-km-orbit-around-mars/), [ESA](https://blogs.esa.int/rocketscience/2017/12/06/keeping-up-with-tgo/)); MRO used the same technique in 2006. This is why the science sats survey from the capture ellipse first and circularize after the gate closes. |
| Dispenser release on hyperbolic approach | flown heritage (MSL, M2020) | **B (verified 2026-07-20)** | MSL jettisoned two 75 kg tungsten cruise balance masses minutes before entry; their impact scars were imaged by CTX/HiRISE ~80 km from the landing site ([JPL PIA16456](https://www.jpl.nasa.gov/images/pia16456-impact-scars-from-msl-cruise-stage-and-two-balance-weights)). Proves both halves of the concept for free: dense masses released pre-entry survive to surface at multi-km/s, and the craters are orbitally observable. |
| Penetrator unit: mass, impact speed, energy | 100-150 kg · 3.5-4 km/s · 0.6-1.2 GJ | **D (physics C)** | Deorbited from the survey ellipse: periapsis speed 4.6-5.5 km/s less drag on a high-β rod gives 3.5-4+ km/s at the surface. KE = ½mv² = 0.6-1.2 GJ ≈ 150-290 kg TNT. Crater ~5-10 m class in regolith (impact-scaling order of magnitude), which exposes ice through the 1-3 m overburden expected at SWIM-favorable sites. Unit mass is a design choice, bracketed by MSL's 75 kg (observable) and diminishing returns above ~300 kg. |
| Penetrator set composition | ~20 rods + dispenser per 3 t set | **D** | Set arithmetic: 3,000 kg ÷ (100-150 kg + dispenser/bus allocation) ≈ 18-25 rods. Two sets flown (window-0 top-up), so 35-50 ground-truth points. |
| Base keep-out radius for strikes | 10 km | **D (doctrine)** | Ejecta ballistic range r = v²/g: 100 m/s gives 2.7 km at Mars g = 3.71 m/s², and bulk ejecta from 5-10 m craters is slower. 10 km is a 3-4× margin over the energetic tail. The direct-hit term is smaller (km-class impact accuracy from a commanded deorbit). Near-field ground truth inside the keep-out is assigned to the flight-1 drilling prospectors. |
| Fresh-crater ice observability window | days-weeks (fade is itself a measurement) | **C** | HiRISE has repeatedly imaged bright water ice in fresh mid-latitude impact craters, sublimating over weeks to months (Byrne et al. 2009, *Science*; established literature, not re-fetched). This is why live plume spectroscopy is opportunistic rather than required: craters keep testifying between passes. |
| Calibrated survey coverage | ~10⁴ km² class | **D (judgment)** | 30-40 ground-truth points across a ~100 km district, each calibrating the SAR return signature for its terrain unit; coverage extends over geologically similar terrain. The program's actual mining appetite is ~1 ha/yr. The survey's real product is a ranked decade of sites plus a validated method. |
| Smallsat bus class | ~600-800 kg science / ~2 t relay | **D (analog C)** | Starlink-derived bus masses (~260 kg V1.0 to ~800 kg V2 Mini class, public figures, not re-verified) plus Mars hardening and capture propellant (~26-36% fractions per the Δv rows) inside the 6 t catalog set. Count (3-4 + 1) is a sketch; the sizing decision is open in the ledger. |
<!-- CONOPS_BASIS:END -->

## Appendix B: glossary

| Term | Meaning |
|---|---|
| **Synod** | The ~26-month Earth-Mars alignment cycle; one launch window per synod each way |
| **Sol** | A Mars day, 24.66 h; surface timelines count sols |
| **Conjunction-class transfer** | The low-energy ~210-day crossing used by every flight here |
| **v∞ (v-infinity)** | Arrival or departure speed relative to the planet, before its gravity is counted |
| **EDL** | Entry, Descent, and Landing |
| **TEI** | Trans-Earth Injection, the burn that leaves Mars for home |
| **ISRU** | In-Situ Resource Utilization: making propellant (and more) from local air and ice |
| **Methalox** | Methane plus liquid-oxygen propellant; ~1,400 t is one crewed ride home |
| **Sabatier** | The CO₂ + H₂ → CH₄ + H₂O reaction at the heart of the fuel plant |
| **ECLSS** | Environmental Control and Life Support System, the air/water recycling loop |
| **Areostationary** | The Mars-synchronous orbit (~17,000 km altitude): a satellite hangs over one longitude |
| **SAR** | Synthetic Aperture Radar, the shallow-ice mapping instrument |
| **Rodwell** | A water well melted into an ice sheet (Antarctic practice; RedWater's Mars version) |
| **RASSOR** | NASA's counter-rotating bucket-drum excavator line, the ancestor of our diggers |
| **The bridge** | The pre-landed 45 t, one-synod survival cache: the only provisions that fly ahead of people |
| **The receipt flight** | The January 2035 uncrewed Mars-to-Earth demonstration |
| **Gate** | A capability requirement that retires on demonstrated state, never on delivery |
| **Tier (A/B/C/D)** | Confidence grade of a number; see §5 |
