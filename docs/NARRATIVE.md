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

## Four rules that shape every decision

1. **Nothing commits until the thing it depends on is *demonstrated* — not
   merely delivered.** The crew does not launch toward "we sent a fuel plant."
   It launches toward "1,400 tonnes of propellant are in the tanks," "the
   life-support loop has run for 1,000 sols," and "an empty ship is already
   flying the trip home." Gates retire on measured state.
2. **Every number carries a receipt.** Each input has a source and a
   confidence tier in `PROVENANCE.md`; when a source drifts, the baseline
   changes and the consequences propagate. Claims that fail verification —
   including most of SpaceX's aspirational cadence figures — are recorded as
   failing, not quietly used.
3. **No single ship loss may cost a schedule-critical capability.** A
   50/50 first landing is not a plan you bet the program on, so the things
   that unblock the future — power, water, the propellant chain, comms,
   autonomy — are spread across hulls, with the pilot chain already on the
   ground as the hot spare.
4. **Pilot one synod ahead; scale when the demand ships.** Every capability
   flies first as a test article one window before its bulk buy, and nothing
   flies before its customer exists. Fuel capacity follows rotation demand;
   agriculture and industry scale on their own pilots' data; provisions
   pre-land exactly one synod of survival (the *bridge*) and fly the depth
   with the people. The one exception is the bridge itself, because its
   customer is the worst day.

## The dates, and why they moved

The plan starts in **2031, not 2026.** There is no 2026 flight: the program
pivoted Moon-first, and orbital refueling — the nearest gate — was still
undemonstrated. A first robotic landing in the early 2030s matches independent
expert consensus. First crew in **2035** is deliberately beyond the aggressive
end of that consensus — and the plan is honest about what that means: it is an
**option on 2035, not a promise.** Every gate still retires on demonstrated
state, and under the peer-reviewed skeptic scenario
(`conservative_feasibility`) the gates hold and crew auto-slips to 2037 —
which is precisely the archived conservative program
(`examples/conservative_program.json`). You choose the aggressive sequencing;
the evidence still chooses the date.

---

## The manifest, window by window

Fleets are sized to their cargo at ≤90% of fleet mass, subject to the one
ramp rule that survived scrutiny — the *cumulative* landed fleet at least
doubles each synod (5 → 10 → 15 → 34 → 97 → 161; 322 ships cumulative). No
air freight: a growth-floored window tops up its holds with risk depth
rather than flying empty. Launch counts include tanker refueling (~16 per ship).
Propellant "banked" is what the plant produces by the time the *next* window
arrives, with newly-delivered capacity ramping at 60% its first synod.

### 2031 · The precursor — prove you can land, power, and prospect (5 ships)

**Motivation:** retire the "does anything work at all" unknowns on the first
touchdown, cheaply, before anything expensive depends on the answers.
Everything schedule-critical flies at quantity two, smeared across hulls.

**What it proves:** EDL at 100-tonne class; 840 kWe of storm-proof fission
baseload; precision landing, comms, autonomy, mobility; a pilot ISRU chain
making ~1.5 t of methalox a day (483 t banked by 2033 — proof of chemistry,
not production); and **site water confirmed in ~30 sols** by kinetic
penetrators and orbital radar instead of 200 sols of drilling. The chain's
bottleneck steps fly at quantity *three*, not two — at 50/50 landing odds,
qty-2 keeps the whole five-component chain alive only ~24% of the time;
qty-3 nearly doubles that, and the holds had the margin (no air freight).

**The two clocks:** one habitat and one ECLSS unit land now, not for use but
to start the 1,000-sol life-support demonstration — the one gate money cannot
compress, only start early. It completes mid-2034, eleven months before crew
commit.

### 2033 · The fuel factory, doubled — prove the ride home (10 ships)

**Motivation:** the single thing that makes a crewed return credible is
propellant you didn't haul from Earth. This window flies **two** rate-matched
chains, not one, because one tankful is a promise and two is a plan: the
second load is what lets an empty ship rehearse the entire trip home while
the first stays banked for people.

**What it proves:** `return_propellant_proven`, `life_support_closed`, and
`radiation_managed` — **every crew gate green a full synod before anyone
launches.** 7.7 t of methalox a day (a full return load every ~6 months;
3,223 t banked by 2035) on 3,000 kWe. The 45 t **survival bridge** — one
synod of food, water and oxygen for twelve — is pre-landed and verified by
robots before any crew commits to needing it. Gated on 2031 actually finding
the water; we don't fly a factory at a hunch.

**The dress rehearsal:** in **January 2035** a cargo ship fuels from the
plant and flies home, empty — Mars ascent, trans-Earth injection, and an
Earth entry at ~11.6 km/s, twice the speed of a Mars arrival and roughly
eight times the heating. It carries a tank of Mars-made methalox and a crate
of dust-weathered parts for Earth labs. The first thing ever to come home
from Mars is a receipt.

### 2035 · First crew — twelve people and a hold full of pilots (15 ships)

**Motivation:** the base is powered, fueled, sheltered, and proven. Twelve
people — inside the peer-reviewed 10–20 band — launch in May 2035 with the
return demonstrator still inbound to Earth. **They commit three months before
it reports.** That is the one corner this program deliberately cuts, and it
cuts it in the open: if the demo fails mid-cruise, they land anyway onto
years of caches and wait out one window while the fix flies. Their own
return, ~March 2037, flies a profile by then proven nineteen months earlier.

**What they land on:** 8,057 t of banked propellant (five-plus full
ride-home loads), 1,500 m³ of pressurized volume — a roomy 125 m³ each against NASA's
76.5 m³/person standard — a ~90% demonstrated landing record, and their own
26-month consumables bridge flying beside them.

**What fills the holds:** the future at pilot scale, plus depth — 12
agriculture modules, the first regolith refinery, the first polymer plant
(both process-anchored to NASA demonstrations: molten regolith electrolysis
and Sabatier-derived polyethylene), hot-spare ISRU components, pad-sintering
rigs for the next fleet, and 100 robots on the surface to run it all.
Fifteen ships because the fleet is sized to the cargo, not the other way
around — and every hold flies at ~85%, packed with pilots and spares
instead of air.

### 2037 · The village — scale what the pilots proved (34 ships, 112 people)

**Motivation:** from proving capabilities to growing people. The target is
Salotti's 110-person survival floor: the line where, in principle, the
settlement could keep itself alive if the ships stopped coming.

**What it deploys:** every 2035 pilot at scale, shaped by two years of pilot
data — 32 agriculture modules feeding ~128, Gen-1/2 industry (refineries and
polymers turning regolith and CO₂ into structure and plastic), and two more
fuel chains **now that crew rotation is finally the customer**: 15 t of
methalox a day, 11 loads banked. Thirty-four ships land on pads the robots
paved two years earlier. Power reaches 10,000 kWe.

### 2039 · The town — Gen-3 closure (97 ships, 512 people)

Food, plastics, and structures now come out of local dirt; the import bill
per head drops from 10 to 2 t/person/year and keeps sliding down the ~500×
decay curve. It isn't free: agriculture is the power monster, and
grow-lighting shoves the base past 20,800 kWe. On Mars, food is electricity
wearing a costume. The electronics-fab pilot lands at the earliest window its
feedstock industry exists to supply — chips remain the last thing Mars ever
makes. Every populated window is machine-checked to cover its residents'
consumables; none runs a deficit.

### 2041 · The settlement — 1,112 adults (161 ships)

The NSS 1,000-adult formal-settlement milestone, **three years earlier than
the conservative plan** — reached not by cutting gates but by re-sequencing
around them. ~28,500 t of hardware across 322 ships, 39,800 kWe, 312
agriculture modules feeding ~1,248, and 91,500 m³ of pressurized volume still
sized to the honest 76.5 m³-per-person standard — with headroom for the wave
after. And the honest coda: this is
a settlement, not independence — self-sufficiency is on the order of a
million people, and we are 1,112. We'd rather say that out loud than pretend
the city is around the corner.

## What the whole thing costs, and where the uncertainty lives

Cumulative through 2041: **322 ships, ~5,474 launches** (tankers included),
**~$493 B in launch services** at the near-term ~$90 M/launch price (the
defensible disclosed figure; the aspirational internal-cost basis is a
scenario, not the baseline), and cargo hardware spanning **~$236–990 B** —
an order-of-magnitude range on purpose, because first-of-kind hardware costs
are Tier-D guesses and we refuse to pretend otherwise. Development cost
(Starship itself, fission, ISRU R&D) is deliberately outside the ledger.

## What we deliberately do *not* model

Return flights exist as requirements and doctrine (L1-RET-01), not as modeled
missions — no orbital logistics, no crew rotation reducing headcount, no
Phobos depots. Population only accumulates. EDL losses are independent
per-ship draws, not correlated bad synods. Industrial closure unlocks on
plant *presence* plus population, not ratio-scaled capacity. Each shortcut is
logged in `docs/CONSIDERED.md` so omissions read as decisions.

## How to read the rest

`README.md` for the program at a glance and the source list;
`docs/REQUIREMENTS.md` for the machine-checked buy-off matrix;
`docs/manifests/` for what flies on which hull; `PROVENANCE.md` for every
number's receipt; `docs/COMPARATIVES.md` for how this differs from Handmer,
*New Space* 2022, and DRA 5.0; the scrollytelling essay (README →
"Interactive views") for the same story with the manifest panel alongside.
