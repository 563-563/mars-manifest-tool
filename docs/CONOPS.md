# CONOPS-1 — Concept of Operations: the robotic era through first crew

*Covers window 0 (2031) through the first crew's surface establishment
(2036). A second document, CONOPS-2, will cover the rotation and city era
(2037 onward) once the constellation-refresh and rotation-logistics
decisions close. Program quantities are engine output from
`inputs/program.json`; operational sequences are doctrine recorded here and
in `docs/CONSIDERED.md` — the planner models mass, schedule, and gates, not
geometry or timing inside a window.*

---

## 1. System elements

- **Transport segment** — Starship-class cargo/crew ships. Cargo hulls fly
  one-way (they are surface assets on arrival: pressure vessels, tankage,
  steel). Each departure costs ~17 launches including tanker refueling. No
  ship enters Mars orbit: all arrivals are direct entry from the
  interplanetary approach.
- **Orbital segment** — one 6 t constellation set, deployed at window 0:
  an areostationary relay (~2 t; continuous base–Earth link) and 3–4 polar
  SAR/ultraspectral smallsats (~600–800 kg each) for shallow-ice radar
  mapping, impact observation, and landing-zone reconnaissance. Deployed by
  dispenser on approach; each spacecraft self-captures (~0.9 km/s chemical)
  and later aerobrakes to its operational orbit.
- **Surface segment** — fission power grid, ISRU propellant plant(s),
  water mining chain, habitat/ECLSS demonstration articles, robot workforce
  (humanoids, rovers, cranes, sintering rigs), comms/nav ground stations,
  and pre-landed consumables (the survival bridge).
- **Earth segment** — launch/refueling infrastructure (the four L1-TRANS
  preconditions: orbit, reuse, refill, chill), mission operations under
  4–22 minute one-way light delay, and the materials/labs loop that
  receives returned samples.

## 2. Phase R0 — Earth-side preconditions (before 2031)

Orbital Starship, routine reuse, orbital propellant transfer, and
long-duration cryo storage must all be demonstrated before window 0
commits (L1-TRANS-01..04). These are per-scenario readiness flags: the
baseline assumes them true; `conservative_feasibility` flips refill/chill
and the requirements matrix goes visibly open.

## 3. Phase R1 — Window 0: land, power, prospect (Jan 2031 – Mar 2033)

**Objective:** turn the unknowns that block everything downstream into
measurements, with no single ship loss costing a schedule-critical
capability.

**3.1 Launch and transit.** Five ships depart January 2031 (~85 launches
with tankers), 210-day transit. Every schedule-critical capability flies
at quantity ≥2 spread across hulls; the ISRU chain's bottleneck steps fly
at quantity 3 (at 50/50 landing odds, qty-2 keeps the five-component chain
alive ~24% of the time; qty-3 ~44%).

**3.2 Approach and deployment (arrival day, ~Aug 2031).** Hours to days
before entry interface, dispensers release two payload groups on targeted
approach trajectories (MSL-ballast heritage; zero Δv cost to the ships):
the equatorial group (areostationary relay) and the polar group (science
smallsats, carrying the kinetic penetrators). Ships proceed to direct
entry. The relay's first job is EDL telemetry for its own fleet.

**3.3 Landing.** Five direct-entry landings at the orbitally selected
site (per-ship P(land) ≈ 0.5 at this window — the redundancy spreading
exists for exactly this). Surviving hulls are safed; the robot workforce
(10 humanoids, rovers, cranes) begins deployment: power grid first
(840 kWe fission + storage), then comms/nav ground stations, then the
pilot ISRU chain.

**3.4 The 30-sol water survey (sols ~0–30).** The science smallsats
capture into 1-sol resonant ellipses (periapsis over the site every sol)
and begin low passes immediately. Penetrator strikes are commanded from
orbit, one or two per sol from ~sol 5: ~20 rods per set (100–150 kg,
steel/tungsten, impact 3.5–4 km/s), each strike timed near an observer
pass and geometry-vetted — **no strike inside the ~10 km base keep-out**
(sized by ejecta ballistics), strike ground-tracks oriented so along-track
dispersion points away from assets. Fresh craters are read over repeated
passes (imaging, radar sounding, ice-sublimation monitoring; plume
spectroscopy opportunistically); each strike doubles as a calibrated
seismic source for base-region subsurface structure. Ground truth from
30–40 impact points calibrates the radar into a district map
(~10⁴ km² class). Inside the keep-out, the two drilling prospectors
ground-truth the near-field mining patch the slow way. `water_confirmed`
closes at ~sol 30 by the fast path, with drilling (~200 sols) as the
independent fallback.

**3.5 Commissioning and steady state (sols 30+).** The pilot chain runs
up (~1.5 t methalox/day; 483 t banked by 2033 — proof of chemistry, not
production). Two demonstration clocks start: the integrated habitat+ECLSS
article begins its 1,000-sol run (completes mid-2034). The science sats
aerobrake to circular polar mapping orbits. The base operates autonomously
under light delay: robots execute plans, Earth supervises by exception.

**Phase exit criteria:** ten capabilities live (EDL, power, precision
landing, comms, autonomy, mobility, infrastructure, habitat, water supply,
water *confirmed*) — half the program's weighted risk retired.

## 4. Phase R2 — Window 1: the fuel factory, doubled (Mar 2033 – Jan 2035)

**Commit decision (mid-2032):** the factory fleet ships **only if**
window-0 prospecting confirmed site water (`requires: [water_confirmed]`),
with ~18 months between data return and departure to reshape the mining
buy around measured ice grade. If water had failed: relocate (costs a
synod) or switch ISRU mode to the DRA-5.0-style oxygen-only fallback
(no water dependency; methane imported at ~4 ships per return load).

**4.1 Arrival (Oct 2033).** Ten ships (~88% full) land on the graded
zone prepared by the window-0 robots. Cargo: **two** rate-matched ISRU
chains (window-0's pilot becomes the hot spare), their reactors
(3,000 kWe total), and the **45 t survival bridge** — one synod of food,
water, and oxygen for twelve.

**4.2 Operations.** The doubled plant commissions on the ramp (60%
first-synod factor) toward 7.7 t methalox/day — a full 1,400 t return
load roughly every six months; 3,223 t banked by the 2035 window. Robots
position and bury the radiation shelters, verify the bridge caches, and
begin sintering landing pads for the next fleet. Mid-2034 the 1,000-sol
ECLSS demonstration completes.

**Phase exit criteria: every crew gate green a full synod before anyone
launches** — propellant banked (≥1,400 t), life support closed, radiation
managed, habitat ready, EDL statistics accumulating (15 landings), power
at crew scale.

## 5. Phase R3 — The receipt flight (Jan 2035 – Aug 2035)

The plant's second tankful buys the rehearsal. In **January 2035** a
cargo ship is fueled from the surface plant — the first ISRU propellant
transfer and cryo hold-through-countdown ever performed — and flies the
entire return profile, empty: Mars ascent and trans-Earth injection
(~6.5 km/s, single stage, no orbital tanker exists at Mars), 210-day
cruise, and Earth entry at ~11.6 km/s (~2× a Mars arrival, ~8× the
heating — a distinct TPS qualification, L2-RET-02). The areostationary
relay carries its ascent telemetry. Cargo home: a tank of Mars-made
methalox and a crate of dust-weathered components for Earth-lab analysis.
Arrival at Earth: **August 2035** — during the first crew's outbound
cruise. This flight retires the L1-RET branch and closes the mission-level
requirement (L0-MSN-01) at the window before crew.

## 6. Phase C1 — First crew (May 2035 – 2036)

**6.1 Commit posture (May 2035).** Twelve crew launch with the
demonstrator still inbound: **the program's one deliberately cut corner,
priced in the open.** Commit criteria: all six crew gates green on
demonstrated state, ≥1,400 t in the tanks *after* the demo's burn, the
verified bridge on the surface, and the demo *in flight*. If the demo
fails during their cruise (report lands August; they land December), the
crew proceeds to a powered, provisioned base and holds one window while
the fix flies — the caches cover a missed return window with years of
margin. Their own return (~March 2037) flies a profile proven nineteen
months earlier.

**6.2 Fleet arrival sequencing (Dec 2035).** Fifteen ships; cargo hulls
enter first, the crew ship last, onto sintered pads, with the constellation
providing EDL telemetry and the surface beacons precision guidance. The
crew lands on 8,057 t of banked propellant (five-plus return loads),
1,500 m³ of pressurized volume (125 m³ per person against the 76.5 m³
standard), and a 26-month consumables bridge that flew beside them.

**6.3 Surface operations.** The twelve are commissioning engineers, not
survivors: their cargo is the future at pilot scale — 12 agriculture
modules (first crops), the first regolith refinery (molten-regolith
electrolysis), the first polymer plant (Sabatier→Fischer-Tropsch→HDPE),
hot-spare ISRU depth, and a robot workforce grown to ~100. Every pilot's
data shapes the 2037 village's scale buy (pilot one synod ahead). Site
prep for the 34-ship village fleet continues throughout.

**6.4 Contingency postures.**
- *Return-demo failure:* land anyway; hold one window on caches; fix
  flies on the 2037 fleet; crew returns ~May 2039 at the latest.
- *Partial fleet loss on arrival:* capabilities survive by redundancy
  spreading + surface backstops; the loss-tolerance requirement
  (L1-LOG-02) is machine-checked for exactly this.
- *ISRU plant fault:* two independent chains + the pilot hot spare; a
  full chain outage still refills a return load within the stay.
- *Skeptic-world commissioning (the `conservative_feasibility` case):*
  gates hold, the 2035 crew window auto-blocks, and the program becomes
  the archived conservative plan — crew 2037, no doctrine change.

## 7. Communications and autonomy

Continuous base–Earth relay via areostationary; surface mesh via two
relay ground stations + beacons; 4–22 min one-way light delay throughout.
Doctrine: robots execute, Earth supervises by exception, and nothing in
the critical path requires a real-time human in the loop — including the
strike campaign, plant commissioning, and pad construction. The crew adds
on-site judgment, not remote control.

## 8. Traceability

Phase exits map to the machine-checked gates: R1 → the ten window-0
capabilities; R2 → `return_propellant_proven`, `life_support_closed`,
`radiation_managed` (and L0-MSN-01 closes); R3 → the L1-RET branch; C1
spends them and closes the two crew-scale quantity requirements
(L2-HAB-02, L2-LS-03). The buy-off matrix (`docs/REQUIREMENTS.md`) and
flight summary (`docs/manifests/SUMMARY.md`) are the generated,
test-enforced views of the same claims. What this document adds — and the
model does not check — is geometry and intra-window timing: keep-out
radii, strike scheduling, arrival sequencing, orbit choices. Those are
doctrine, ledgered in `docs/CONSIDERED.md`, awaiting a spatial/timing
layer if one is ever built.
