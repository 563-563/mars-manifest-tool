# The program, told as a story

*A plain-language walkthrough of what this campaign actually does, window by
window — the motivation, the ordering, what rides on each fleet, what problem
it solves, and why the calls were made the way they were. Every number here
is produced by the tool from `inputs/program.json`; nothing is
hand-typed. Run `mars plan inputs/program.json --format md` to
regenerate the spine of it.*

---

## The problem we are actually solving

Getting people to Mars is not one problem. It is roughly six hard ones stacked
on each other, none fully solved: reaching orbit and refueling there; landing
100 tonnes when nothing heavier than one has ever touched the surface; making
~1,400 tonnes of return propellant from Martian air and ice; closing a
life-support loop for a thousand days with no resupply; surviving the
radiation; and keeping a crew alive with no abort. Money is *not* the tall
pole — reusable launch makes even enormous campaigns affordable next to the
hardware and the physics.

Two things dominate the near term. **Power** is the tent-pole: the propellant
plant, mining, life support, and heat all die without it, and solar collapses
in months-long dust storms — which is why fission anchors the crewed era.
**Water is the deciding uncertainty**: we know Mars has ice, but not how deep,
how pure, how rocky, how far from a landing site. You cannot design a mining
machine against error bars that large. So the earliest job is not to build the
city — it is to *retire the unknowns* in the order that unblocks everything
downstream.

That reframing is the whole logic of the plan: **it is a sequence of proofs,
not a delivery schedule.** Each window exists to retire specific risk so the
next one is allowed to commit.

## Three rules that shape every decision

1. **Nothing commits until the thing it depends on is *demonstrated* — not
   merely delivered.** The crew does not launch toward "we sent a fuel plant."
   It launches toward "1,400 tonnes of propellant are in the tanks" and "the
   life-support loop has run for 1,000 sols." Gates retire on measured state.
2. **Every number carries a receipt.** Each input has a source and a
   confidence tier in `PROVENANCE.md`; when a source drifts, the baseline
   changes and the consequences propagate (this is why the ship bay is 614 m³,
   not the 1,000 m³ we started with). Claims that fail verification — including
   most of SpaceX's aspirational cadence figures — are recorded as failing,
   not quietly used.
3. **No single ship loss may cost a schedule-critical capability.** A
   50/50 first landing is not a plan you bet the program on, so the things
   that unblock the future — power, water, the propellant chain, comms,
   autonomy — are spread across hulls and pre-deployed a window early. Crew-era
   comforts can accept single-hull risk because a lost habitat can be re-flown
   before anyone needs it.

## The dates, and why they moved

The plan starts in **2031, not 2026.** There is no 2026 flight: the program
pivoted Moon-first, and orbital refueling — the nearest gate — was still
undemonstrated. A first robotic landing in the early 2030s matches independent
expert consensus; first crew in **2037** sits at the aggressive end of it. The
old Musk-schedule dates survive only as frozen regression fixtures, never as
the plan.

---

## The manifest, window by window

Fleet sizes obey the one ramp rule that survived scrutiny — the *total* landed
fleet at least doubles each synod (cumulative 5 → 10 → 21 → 42 → 84 → 194 →
394). Launch counts include tanker refueling (~16 per ship). Propellant
"banked" is what the plant produces by the time the *next* window arrives, with
newly-delivered capacity ramping at 60% its first synod.

### 2031 · The precursor — prove you can land, power, and prospect (5 ships)

**Motivation:** retire the "does anything work at all" unknowns on the first
landing, and shrink the water error bars before committing a fuel factory.

**What flies:** a loss-tolerant robotic batch — 16 fission reactors (640 kWe),
a pilot ISRU chain in duplicate, water prospecting, comms, humanoid + rover
robots, one habitat + one ECLSS unit as a **1,000-sol life-support testbed**,
and — the cheapest idea on the manifest — **kinetic penetrators plus an
orbital radar constellation** that read the subsurface from orbit.

**What it proves:** EDL, dust-storm-proof baseload power, mobility, autonomy,
comms, precision landing, and confirmed site water. This one window **retires
50% of the program's weighted risk** — the whole "unknown unknowns" category
dies on first landing.

**Key decision — why penetrators:** water knowledge is the binding constraint
on everything downstream, and surface drilling alone needs ~200 sols to
confirm it. Dropping steel rods and reading the craters from orbit gives a
`water_confirmed` answer in ~30 sols, cheaply and without betting on a soft
landing. It is the highest-leverage cheap move in the plan.

### 2033 · The fuel factory — prove the ride home (5 ships)

**Motivation:** the single milestone that makes a crewed *return* credible.

**What flies:** the rate-matched propellant chain from `size_chain` — 6
electrolyzers, the reactors they drag (1,760 kWe installed), CO₂ capture,
Sabatier, cryo, and the excavators to feed them.

**What it proves:** `return_propellant_proven`. By the next window ~1,826 t are
banked — over the 1,400 t a crewed ship needs, with ~30% margin. Cumulative
risk retired: 75%.

**Key decisions:** (1) This fleet is *gated on `water_confirmed`* from 2031 —
prospect-before-commit. We do not ship a fuel factory toward water we haven't
found. (2) It is the program's critical path, yet it needs **no extra
redundancy**: the capability is backstopped by 2031's pre-deployed pilot chain,
and the 30% propellant margin absorbs any one lost ship. A sixth ship was
considered and rejected as mass we don't need.

### 2035 · Second plant + the base — prove survival (11 ships)

**Motivation:** double propellant output, and stage everything a crew needs to
live before they leave Earth.

**What flies:** a second matched chain (plant-level redundancy *and* 2× rate),
the habitat cluster, deep consumable caches, shelters. Power reaches 3,040 kWe.

**What it proves:** `life_support_closed` (the ECLSS testbed has now run its
1,000 sols) and `radiation_managed`. **Cumulative risk retired: 100%** — every
schedule-critical gate is closed a full window before crew.

**Key decision — why 11 ships, not 10:** at the *verified* 614 m³ bay, this
window is volume-bound, not mass-bound (habitats and caches are bulky, not
heavy). The real bay volume forced the honest ship count.

### 2037 · First crew — arrive to a working base (21 ships, 12 people)

**Motivation:** by now the base is powered, provisioned, and fueled, and every
requirement has been bought off at least one synod early. Only now do people
go.

**What they find:** ~8,700 t of propellant banked — several return loads over.
EDL has a demonstrated ~93% reliability from the landings so far (it began at a
coin-flip). The crew is 12 — inside the peer-reviewed 10–20 first-crew range.

**Key decision — why the strict gate:** the crew commits against a fully
bought-off baseline, not a promise. This is the payoff of rule #1: the
propellant that flies them home already exists, the life-support loop is proven,
and no capability they depend on rides on a single hull.

### 2039 → 2044 · The city ramp — from outpost to settlement

Now the character changes from *proving capabilities* to *scaling population
and closing the industrial loop.*

- **2039 · Village (42 ships, ~112 people):** passes Salotti's **110-person
  survival floor**; first local industry (refinery, polymer plant) and
  agriculture come online (Gen-1/2 closure).
- **2041 · Town (110 ships, ~512 people):** **Gen-3 closure** — food,
  polymers, and structures now made locally.
- **2044 · Settlement (200 ships, ~1,112 people):** crosses the **NSS
  1,000-adult settlement milestone.**

Across this ramp the recurring import bill per resident walks down the verified
decay curve — ~10 t/person/year with nothing local, toward ~20 kg/person/year
as raw-material manufacturing closes — a ~500× cliff, not a gradient. Every
populated window is checked to deliver enough consumables to cover its
residents; none runs a deficit.

**The honest gap:** the plan reaches a *settlement*, not *autarky*. Full
industrial independence is ~1,000,000 people by the sources we trust; 1,112 is
~1.85% of the way there — even though by 2044 the surface holds ~18,500 t of
hardware, already **44× the mass of the ISS**. The tool states both plainly
rather than implying the city is around the corner: a huge outpost, and still
a rounding error against self-sufficiency.

---

## What the whole thing costs, and where the uncertainty lives

Cumulatively the plan lands **394 ships over ~6,700 launches** delivering
~25,900 t. At the disclosed near-term launch price that is ~$600B of launch;
on SpaceX's internal-cost basis (expended cargo ships, reused tankers) it is
closer to ~$90B. Cargo hardware dwarfs launch, and development cost — Starship,
fission, ISRU R&D — is larger still and deliberately kept out of these
figures (it is a separate ledger we chose not to model).

The serious disagreements are carried as **scenario axes**, not smoothed into a
single answer:

- **Is the architecture even feasible on this timeline?** The
  `conservative_feasibility` scenario carries the peer-reviewed DLR/Maiwald
  skeptic case — it flips orbital refill and cryo-chill to *not demonstrated*,
  and those Earth-side requirements go OPEN while the harsher ISRU energies
  cascade into propellant shortfalls. This is the honest lower bound.
- **How hard is ISRU energy?** 7.6 kWh/kg (our bottom-up) to 15.3 (Handmer's
  all-in) — full-scale power 0.85 to 1.7 MW.
- **Water risk:** if prospecting disappoints, `oxygen_only_isru` (import
  methane) and `h2_import` (import hydrogen, no mining) are modeled fallbacks.
- **How many people is "self-sustaining"?** 110 / 1,000 / 1,000,000 — three
  different questions, all carried as milestones.

## What we deliberately do *not* model

So omissions read as decisions, `docs/CONSIDERED.md` records every idea weighed
and set aside — Phobos propellant depots, a development-cost ledger, one-way
crew doctrine, mass-driven population growth, per-item surface offload limits,
and more, each tagged *deferred*, *out of scope*, *rejected*, or *simplified*
with the reason. The register is part of the honesty: the tool is clear about
its own edges.

## How to read the rest

- **`README.md`** — what the tool is and how to run it.
- **`PROVENANCE.md`** — every input, its source, tier, and verification log.
- **`docs/REQUIREMENTS.md`** — the machine-checked buy-off matrix (generated).
- **`docs/CITY_RAMP_RESEARCH.md`** — the sourced research behind the city ramp.
- **`docs/COMPARATIVES.md`** — how this plan differs from Handmer / *New Space*
  2022 / NASA DRA 5.0, and what was adopted.
- **`docs/CONSIDERED.md`** — the weighed-and-set-aside register.
- **`CONTRIBUTING.md`** — the rules that keep all of the above honest.

The one-line version: **this is a plan that earns each step before taking it,
shows its work for every number, and is candid about where it stops.**
