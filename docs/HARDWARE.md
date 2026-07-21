# Hardware basis — specs, design heritage, and COTS anchors (CONOPS-1 elements)

*Companion to `docs/CONOPS.md` and `inputs/catalog.csv`. The catalog is the
source of truth for the numbers the engine consumes (mass / volume / power /
duty, Tier D unless anchored); this document records what each element
physically **is**, what flown or commercial hardware anchors it, and what
remains a guess. Tiers and verification dates refer to `PROVENANCE.md`
(§2, §5b, §6, §8). City-era hardware (agriculture, refinery, polymer,
fab at scale) gets the same treatment in the CONOPS-2 pass.*

Format per entry — **Function · Catalog spec · Design basis · Heritage /
COTS anchor · Open items.**

---

## Transport segment

### Starship cargo/crew vehicle
Function: 100 t-class direct-entry lander; cargo hulls are one-way and
become surface assets. Spec: 100 t payload (Tier B, SpaceX stated target),
614 m³ bay (B, re-anchored 2026-07-09 to the published figure), ~16 tanker
launches per departure (B, GAO/OIG count; SpaceX ~10 as the optimistic
bound). Design basis: SpaceX Starship as published; no orbit insertion at
Mars, aerodynamic EDL only. Heritage: none at this landed mass — the
heaviest prior Mars landing is ~1 t (Perseverance), which is why EDL is a
gated capability with its own probability ramp (p = 0.5 → 0.95) rather
than an assumption. Open: real cargo capacity (the 2024 peer-reviewed
attempt could not reproduce SpaceX's mass budget; a 75 t reality re-sizes
the fleet +112 ships, ~+$171B — priced in §8b of PROVENANCE).

## Orbital segment (`orbital_radar_set`, 6 t / 15 m³ per set)

### Areostationary relay (~2 t, 1 unit)
Function: continuous base–Earth trunk, EDL telemetry for every arriving
fleet, ascent/TEI witness for the receipt flight, whole-disk context
imaging. Spec: sketch within the 6 t set; ~1.4 km/s propulsive budget
(PROVENANCE §5b). Design basis: geostationary comms-bus practice at Mars-
synchronous radius (20,428 km). Heritage: every GEO comms satellite;
deep-space relay practice via MRO/TGO (which relay ~all surface-mission
data today). Open: bus selection, laser vs Ka trunk to Earth, conjunction
outage handling.

### Polar SAR/ultraspectral smallsats (~600–800 kg, 3–4 units)
Function: the shallow-ice mapper the legacy fleet cannot be — SHARAD's
~15 m vertical resolution is blind in the top ~10 m where minable ice
lives; CRISM (the ejecta-spectroscopy instrument) is retired. Spec:
sketch; capture 0.90 km/s to the 1-sol survey ellipse, aerobrake to
~300 km polar circular after the gate (§5b). Design basis:
Starlink-derived bus (Handmer's "Marslink" framing) + shallow-penetrating
SAR of the class proposed for NASA's cancelled Ice Mapper. Heritage:
MRO/TGO for capture-and-aerobrake ops (TGO: 11 months, ~1 km/s,
verified); Starlink for bus mass/production economics. Open: SAR band
and antenna packaging at this bus size; count (the ledger's open
constellation-sizing decision); refresh cadence (flagged — never
reinforced through 2041).

### Kinetic penetrator set (3 t / 2 m³, 2 sets)
Function: convert orbital ice inference into ~35–50 ground-truth points
in ~25 sols; each strike doubles as a calibrated seismic source. Spec:
~20 rods/set at 100–150 kg (steel body, tungsten nose), deorbited on
command at 3.5–4 km/s → 0.6–1.2 GJ → 5–10 m craters through 1–3 m
overburden (§5b derivations). Design basis: dumb finned long-rods, no
instruments; all reading is remote. Heritage: MSL's 2 × 75 kg tungsten
balance masses — released pre-entry, impacted, craters imaged from orbit
(verified 2026-07-20, JPL PIA16456); LCROSS for read-the-ejecta logic;
Deep Space 2 (1999, both units lost) as the cautionary tale *against*
instrumented micro-penetrators. Open: dispenser design, rod L/D and nose
material split, strike-corridor selection at the real site.

## Power (`fission_unit`, `battery_module_100kwh`, solar option)

### Fission surface unit (40 kWe / 6 t / 30 m³)
Function: storm-proof baseload; the tent-pole of everything. Spec: Tier B
— the one catalog row with a published program spec behind it (NASA
Fission Surface Power: 40 kWe, <6 t, decade unattended; verified
verbatim — though the FSP reference design is LUNAR, Mars use is an
extensibility argument, not an independently Mars-validated result).
Design basis: FSP/Kilopower lineage, closed Brayton. Heritage:
Kilopower/KRUSTY ground demo (2018); the 2025 100 kWe directive is
carried as the `fsp_2025` scenario. Open: none blocking at concept level;
this is the best-anchored active component in the catalog.

### Battery module (100 kWh / 0.67 t)
Spec: 150 Wh/kg pack-level (Tier B: space-rated cells run 150–270 Wh/kg,
NASA SmallSat SoA, verified; pack integration derates 30–40%). Heritage:
ISS/EV lithium-ion practice. Open: only sizing sensitivity — at
250 Wh/kg the storm reserve drops ~40%.

### Solar option (`solar_module_1000m2`, not baselined)
Spec: 30 W/m² 24-h average (Tier C derivation from Mars insolation ×22%
cells), 4.0 kg/m² areal density (B — re-anchored 2026-07-09 to flown ROSA
hardware, replacing the 1.5 aspirational figure). Why not baseline:
global dust storms last weeks–months; survival-load storage keeps solar
*feasible* but production halts — the honest trade is carried as the
`solar_only` scenario. Heritage: ROSA (flown, ISS), InSight dust-
degradation data (~0.2%/sol).

## ISRU propellant chain

*The chain aggregate is the validated thing: ~22 t of hardware per
rate-matched chain, cross-checked to within 7% of NASA's MAV ISRU study
(PROVENANCE §6, verified). Component splits below remain Tier D. The
whole chain's flight heritage is MOXIE: 122 g of O₂ ever produced on
Mars — 9 orders of magnitude below the 2033 plant, which is why
commissioning ramps at 60% and every rate stays honest.*

### Water electrolysis unit (4 t / 150 kW peak)
Function: the chain's workhorse and bottleneck — splits mined water for
Sabatier H₂ and the oxidizer stream. Spec basis: 6.1 kWh/kg H₂O system-
level (C; consistent with the verified 50–55 kWh/kg-H₂ industrial figure,
World Nuclear, verified). Heritage/COTS: megawatt-class PEM electrolyzers
are commercial terrestrial products; Mars deltas are thermal environment,
autonomy, and maintenance-free sealing. Open: stack lifetime in
unattended operation — the reason it's the qty-3 top-up item at window 0.

### CO₂ acquisition (2 t / 30 kW) and Sabatier reactor (3 t / 20 kW)
Function: pull 6-mbar atmosphere, catalyze CO₂ + H₂ → CH₄ + H₂O
(exothermic; the 1.5 kWh/kg-CH₄ is balance-of-plant, D). Heritage: ISS
runs a Sabatier CO₂ reduction system today; MOXIE proved atmospheric
acquisition + solid-oxide processing on Mars itself; cryo-freezing CO₂
capture spans ~0.3–2 kWh/kg; re-anchored to 1.0 (NASA Glenn TSA, C).
Open: dust management at intakes; catalyst life.

### Cryogenic liquefaction (9 t / 80 kW)
Function: liquefy CH₄/O₂ and re-liquefy boil-off at Mars ambient. Spec:
1.5 kWh/kg-propellant (B — re-anchored 2026-07-21 to NASA cryo studies,
1.6–2.2 kWh/kg-O₂ blended over methalox; was 0.8). Heritage: industrial gas
liquefaction is a mature terrestrial industry; flight cryocoolers exist
at small scale — tonne-per-day-class space-rated liquefaction is the
genuinely novel scale-up. Open: the heaviest, most power-hungry chain
step; deliberately *not* given a third unit at window 0 (its reactor drag
priced it out — CONSIDERED row).

### Water mining: excavator (2 t / 20 kW) + processing (3.5 t / 50 kW) + prospecting drills
Function: dig icy regolith, melt/filter/deionize to feed electrolysis.
Spec basis: excavation 0.1 kWh/kg-water (C — anchored 2026-07-20 to the
published RASSOR 2.0 design law: ≥2.7 t regolith/day from a 66 kg robot
at ~4 W per kg/h; our 2 t production digger is conservative at any ore
grade >~5%); processing 0.35 kWh/kg (C — re-anchored 2026-07-20 so
end-to-end water energy ~0.45 kWh/kg). **RATE is grade-limited, not
power-limited** (re-anchored 2026-07-21): baseline uses the NASA Rodwell
clean-ice model ~0.4 t/day/unit -- the RedWater 169 kg/h headline is
MODELED, its demonstrated chamber rate was ~11 kg/h, and garden regolith
falls to ~29 kg/day/unit (NASA WER). Heritage: RASSOR (NASA KSC prototype,
dry-simulant design rate only), RedWater (Honeybee, TRL 5-6 chamber), Rodwell
Antarctic practice (TRL 6 by analogy, no Mars flight). Open: abrasive-wear
rates — why the water chain carries deep spares.

## Robotics & site

### Humanoid robot (`optimus_robot`, 0.1 t)
Function: the labor force — deployment, maintenance, pad construction;
100 on surface by first crew. Spec: Tier B mass (Tesla's published
57–73 kg + Mars hardening allocation). Heritage/COTS: Optimus/Figure-
class humanoids are in factory pilots on Earth; *nothing* like the
required autonomy under 4–22 min light delay is demonstrated — the
capability, not the hardware, is the risk (gated as `autonomy_proven`).
Open: dust/thermal hardening, battery cycling, fleet-level autonomy.

### Rovers, cranes, sintering rigs, grading tools (0.5–6 t each)
Function: haulage, offload, landing-pad construction (regolith sintering
doubles as radiation-shield mass movement). Heritage: MSL/M2020 mobility
scaled up; terrestrial construction equipment logic; microwave/laser
regolith sintering is lab-demonstrated (NASA/PISCES pads work). All
Tier D — narrative-derived engineering estimates, individually small.

## Habitation & life support

### Inflatable habitat (`habitat_inflatable`, 15 t / 75 m³ stowed → ~300 m³ deployed)
Spec: Tier C/D — TransHab/B330 family (TransHab: 329.4 m³ deployed, per
BVAD; ~4× stowage compression). Heritage: BEAM has been expanded on ISS
since 2016 (endurance data accruing); B330 ground articles. Every
habitat in the program is this component; capacity math uses the honest
76.5 m³/person pressurized standard (NTRS 20200002973, verified). Open:
long-duration bladder life on Mars (why one flies at window 0 to run the
clock), MMOD/abrasion environment differences.

### ECLSS unit (`eclss_habitat`, 7 t)
Function: near-closed air/water loop for ~1,000 days; always packed 1:1
with its habitat (affinity rule — a loop is only demonstrable inside a
sealed volume; LMLSTP/ISS-chamber/BEAM precedent, adopted 2026-07-13).
Spec: Tier C/D, in family with ISS ECLSS-derived masses. Heritage: ISS
ECLSS (the sobering anchor: 34% of *all* ISS supplied logistics mass was
ECLSS support, NTRS, verified — which is why spares dominate our
overheads). Open: the 1,000-sol unattended run *is* the open item; the
window-0 demo article exists to close it.

### Radiation shelter (1 t / 5 m³) and consumables cache (15 t / 60 m³)
Shelter: equipment only — the shielding is regolith/water mass placed by
robots (sintering rigs move the mass; deep-dive RAD dosimetry sets the
need). Cache: food/O₂/water at the verified BVAD floor (0.800 / 0.895 /
3.217 kg per person-day — verified verbatim); one cache ≈ 255 person-
months of zero-recycling survival. Both Tier C/D on mass, Tier B on the
consumption rates they're sized against.

## Comms & compute (ground)

### Relay ground stations, landing beacons, central compute (0.5–1.5 t each)
Function: surface mesh, precision-approach aids, and the autonomy brain
(robots execute locally; Earth supervises by exception). Heritage:
deep-space transponders and surface-network practice (COTS-adjacent);
landing beacons are DSN-style ranging shrunk to surface emplacement —
straightforward hardware, Tier D masses. The *system* risk is autonomy
software, not these boxes.

---

*Reading guide: when a spec here disagrees with `inputs/catalog.csv`, the
catalog wins (it feeds the engine) and this document needs updating —
that's a bug, report it. When a heritage claim lacks a verification date,
it is cited from the general literature at Tier C and is fair game for
the §8-style re-verification pass.*
