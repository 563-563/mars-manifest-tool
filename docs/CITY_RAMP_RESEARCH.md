# Research brief — from first crew to a self-sustaining city

*Compiled 2026-07-09/10. Deep-research harness, two runs (both interrupted by
session-length limits mid-verification; findings recovered from
`journal.jsonl` transcripts and independently spot-checked below — see
Methodology). Raw combined claim set: `docs/_city_ramp_raw_findings.json`.*

## Why this exists

The program plan (`examples/program_plan.yaml`) ends at first crew (2037-07,
~1,487 t of hardware, ~3,240 kWe installed, ~10,205 t propellant banked). The
user asked what it would take to go from there to a **self-sustaining city**,
and what that implies for an ongoing, multi-decade manifest. This brief
answers that with sourced, tiered anchors — the same discipline as
`PROVENANCE.md` — so a city-ramp module (M6) can be built on verified numbers
rather than vibes.

**Headline finding before the numbers:** our own tool cannot yet answer
per-capita questions, because **it has no population field.** `Mission` has
`crewed: bool`; nothing counts people. Every anchor below is denominated
per person. Adding population as a first-class quantity is the prerequisite
for everything else in this document — see §7.

---

## 1. How many people is "self-sustaining"? (three orders of magnitude apart)

| Threshold | Value | Basis | Tier | Source |
|---|---|---|---|---|
| Bare survival floor | **110** | Time-budget model: total human labor available vs. labor required for O₂/water/food/industry/life-support, with a "sharing factor" `n^α` capturing productivity gains from cooperation | **B** | Salotti, *Sci Reports* 2020 ([nature.com](https://www.nature.com/articles/s41598-020-66740-0)) — confirmed 3-0 both runs |
| Genetic/logistics floor (alt. model) | **22** | Agent-based model, different framing (survival probability under resource/accident risk, not industrial closure) | C (unverified, single source) | GMU agent-based study, via [technology.org](https://www.technology.org/2023/08/18/how-many-people-would-it-take-to-start-a-self-sufficient-mars-colony/) |
| Formal "settlement" milestone | **1,000 adults** + a Mars-born generation that itself has viable children | Population + multi-generational viability, not industrial closure | **B** | NSS Space Settlement Roadmap ([nss.org](https://nss.org/space-settlement-roadmap-25-martian-settlement/)) — confirmed 3-0 |
| Population range flagged as "most dangerous" | **1,000–100,000** | Too large to evacuate in an emergency, too small to be industrially self-sufficient | C (unverified, errored votes — session limit, not refutation) | Handmer, [How to industrialize Mars](https://caseyhandmer.wordpress.com/2018/09/03/how-to-industrialize-mars/) |
| Full industrial autarky | **~1,000,000** (Handmer: "within an order of magnitude"); Musk: same figure, no shown derivation | Analogy to Earth: only ~5-6 economic blocs (China, Japan, US, EU, India) have complete industrial stacks, and that took **10-100 million people**; Mars needs less because lower complexity/diversity bar, but still ~1M | **C** (independently re-verified — see Methodology; Handmer states this as an order-of-magnitude estimate, not a precise figure) | Handmer, [2017 roadmap](https://caseyhandmer.wordpress.com/2017/05/13/a-roadmap-to-an-industrially-self-sufficient-mars-base-in-the-minimum-time/); Musk via [Teslarati](https://www.teslarati.com/elon-musk-self-sustaining-mars-city-plausible-25-30-years/) |
| Skeptical range (survey of the field) | **100,000 to 1,000,000,000** | *A City on Mars* survey of published autarky estimates — the field genuinely does not converge | C | NSS Journal critique of *A City on Mars* |

**Read:** these are not competing answers to the same question — they're
answers to three *different* questions. 110 is "can it not die." 1,000 is
"is it a real settlement with a future generation." ~1,000,000 is "does it
need nothing from Earth ever again." A city-ramp module should carry **all
three as named milestones**, not pick one.

## 2. What closes first, and in what order

Two independent frameworks, converging on the same shape:

| Source | Sequence | Tier |
|---|---|---|
| Freitas/Gilbreath lunar-manufacturing model, adapted (arxiv 1612.03238) | **Gen 1.0**: gases, water, crude alloys, ceramics, solar cells → **Gen 2.5**: plastics, rubbers, chemicals → **Gen 3.0**: fabrics/polymers, PC cards/chassis → **Gen 4.0-6.0**: electronics closing 90%→95%→99%→100%, computer chips only from Gen 5.0 (needs local lithography) | **B** — confirmed 3-0 |
| Handmer, [How to industrialize Mars](https://caseyhandmer.wordpress.com/2018/09/03/how-to-industrialize-mars/) | Oxygen → water/fuel → plastics/some food → masonry/structural metals → alloys → electronics/advanced chemistry → **processors last**. Prioritized by (mass produced) ÷ (difficulty of manufacture) | C (errored votes, session limit — not refuted; consistent with the peer-reviewed sequence above) |
| NSS minimum-closure set | "Reasonable self-sufficiency" = only **three** capabilities: life support, stable local food, and construction of additional pressurized habitat from local materials | **B** — confirmed 2-1 |

**Read:** this maps cleanly onto our own catalog groups. `ISRU`, `Water
mining`, `Power generation` close first (we already model this — it's
exactly what window 1's fuel factory does). `Habitat & life support` and
`Consumables & caches` close next (NSS's minimum bar). `Robotics`,
`Comms nav & autonomy`, and anything semiconductor-grade close **last** —
and the paper is explicit that **incomplete closure of electronics grows
import mass exponentially**, not linearly (confirmed 2-1) — a real cliff a
city-ramp model needs to represent, not smooth over.

## 3. Import mass per person — the decay curve

| Stage | Import mass | Tier | Source |
|---|---|---|---|
| No local production | **~10 t/person/year** at ~$2M/person/year | C (fetched directly, corroborated on retry) | Handmer, [make-buy question](https://caseyhandmer.wordpress.com/2022/03/29/understanding-the-make-buy-question-in-a-growing-mars-city/) |
| Local raw-material manufacturing established | **~20 kg/person/year** — a **~500×** reduction | C (same source) | ibid. |
| Make-vs-buy rule | Anything costing **<$100/kg** to produce locally should always be made locally — it beats even the most optimistic Earth-shipping cost | C | ibid. (his working shipping-cost baseline is $200/kg, and "results don't vary much" as that assumption moves) |
| Steady-state per-capita material *usage* once industrial | **~10× Earth per-capita usage** | C (errored votes, session limit) | Handmer, [Progression of space industrialization](https://caseyhandmer.wordpress.com/2020/08/23/progression-of-space-industrialization/) |
| NASA near-term consumables floor (no closure at all) | 0.800 kg food + 0.895 kg O₂ + 3.217 kg water = **~4.9 kg/person-day ≈ 1.8 t/person-year** | B (NASA primary; PDF unfetchable this session, figures internally consistent with known ECLSS literature — flagged for direct re-verification) | NASA BVAD, TP-2015-218570/REV2 |

**Read:** the ~10 t → ~20 kg curve is the single most useful number in this
whole brief for a city-ramp module — it's a ~500× cliff, not a gradient, and
it happens at the same threshold as "raw-material manufacturing established"
(roughly Gen 1.0-2.5 in §2's sequence). **Important distinction to encode
correctly:** this is *ongoing annual* import mass per resident, not the
*one-time capital* mass to establish a person's presence. Our own program's
first-crew window delivers ~1,487 t of hardware for an unspecified but
small crew — that's capital buildout, categorically different from the
10 t/person/year *recurring* draw a settled population would need. A
city-ramp module must track these as two separate ledgers.

## 4. Ships-per-synod ramp

| Claim | Verdict | Tier |
|---|---|---|
| Fleet should **at least double** every 26-month synod (total landed vehicles) | **Confirmed 3-0**, peer-reviewed | **B** — *New Space* 2022 (PMC9527650) — the same paper already cited in `docs/COMPARATIVES.md` for the one-synod-ahead cargo rule |
| Musk's 5 → 20 → 100 → 500 Starships (2026/28/31/33), target 1,000-2,000/window | **Refuted 0-3** — superseded by the Feb-2026 Moon-first pivot (Musk's own words, "5-7 years delay"), and independently, this exact 2026-start premise is what our own `CLAUDE.md` already treats as historical/superseded | — (do not use as an anchor) |
| Musk: self-sufficiency in 25-30 years given "exponential increase in tonnage per window" | **Refuted 1-2** (weak; borderline) | do not use as a hard anchor |
| Musk: 10-15 transfer windows to self-sufficiency | **Refuted 0-3** | do not use |

**Read:** the *only* ships-per-synod number that survived adversarial
scrutiny is the peer-reviewed **"at least double every synod"** rule — which
is dramatically more conservative than Musk's rhetoric and is a rule our
planner can actually encode (`ships[i+1] >= 2 * ships[i]`, floor-bounded by
whatever the real fleet size is). Every Musk cadence number got killed —
consistent with the pattern we've already found twice this project (payload
volume, solar areal density): **his aspirational figures do not survive
verification and should never be load-bearing anchors.**

## 5. Power, food, and habitat — per person

| Quantity | Value | Regime | Tier |
|---|---|---|---|
| Constant power demand, life-support-only | **~24-25 kWe/person**, roughly flat from 4 to 500 people (mild economies of scale) | Basic operations | C (unverified, session-limit errored; independently corroborated via secondary search) — [*Space: Sci & Tech* 2021](https://spj.science.org/doi/10.34133/2021/9820546) |
| Total power, 100+ person colony (same paper, Table 1 stage 4) | **~4.4–7.7 MWe** (17 kWe/person generic load + 2,500 kWe base + 200 kWe ISRU) | Basic operations at scale | C, same source |
| Industrial/productive city power intensity | **~100 kWe/person** | Full industrial (mining, manufacturing, not just life support) | C, same source (order-of-magnitude higher regime, not a typo) |
| Net habitable volume, theoretical floor | **28-29 m³/person**, nearly flat with crew size | Long-duration transit/surface | **B** — independently re-confirmed via secondary search — NASA/NTRS 20200002973 |
| Net habitable volume, realistic (built) | **~37 m³/person** (~27% over the floor — access paths, structure) | ibid. | C (session-limit errored, single source) |
| Total pressurized volume (incl. systems/stowage) | **~76.5 m³/person** for a 4-crew case (147 m³ NHV + 104 m³ systems + 52 m³ stowage over 4 crew ≈ 306 m³ total ÷ 4) | ibid. | C |
| Food-growing area | **46-65 m²/person** — Cannon & Britt 46 m² (2-1 confirmed); NASA BVAD 65 m² for full-diet-from-plants; Frontiers paper ~40-50 m² coupling food+O₂/CO₂. Converges on **~50 m²/person**. | | B/C blend |
| Food self-sufficiency timeline | **20-40 years**, for a colony growing to 1M over 100 years | | C (2-1 confirmed) |

**Read:** two regimes matter and must NOT be conflated — life-support power
(~25 kWe/person) vs. industrial power (~100 kWe/person, 4× higher). Our own
program's crew-window power (3,240 kWe installed) is sized to run a fuel
factory and a robot workforce, not just keep people alive — it is already
"industrial-regime" power per any plausible small crew size, which is
directionally correct (the program is right to over-provision power ahead
of population) but means **none of these per-person figures apply cleanly
to our pre-city phase**. They become load-bearing only once the module
starts tracking actual settlers, not robots.

## 6. Where the serious people disagree — scenario axes

Frame these as `assumptions_seed.json`-style named scenarios, not a single
answer:

| Axis | Low end | High end | What it changes |
|---|---|---|---|
| **Self-sufficiency population target** | 1,000 (NSS formal settlement) | 1,000,000 (industrial autarky) | Everything downstream scales off this — pick the milestone, not just one number |
| **Population growth mechanism** | Organic doubling per synod (Handmer's own proposal, ~10× per decade) | Import-driven (ships carry settlers directly, capped by fleet size) | Whether population or launch cadence is the binding constraint |
| **Power regime at each population stage** | ~25 kWe/person (subsistence) | ~100 kWe/person (industrial) | 4× swing in power-plant mass per resident |
| **Feasibility of the whole architecture** | DLR/Maiwald 2024 (peer-reviewed): even a single crewed Starship mission is not feasible on the stated timeline — 1,200 t/trip ISRU propellant and 200 t EDL are unsolved at required TRL; realistic timeline is 10-20 years of *additional* development beyond what SpaceX has stated, at tens of billions of dollars | Optimistic (Handmer, Musk): city-scale achievable in decades | This is the field's single sharpest fault line — worth carrying as an explicit `conservative_feasibility` scenario that inflates TRL-gated timelines |
| **Electronics/chip closure** | Accept permanent partial import (small, bounded annual mass) | Insist on full closure (Gen 5.0+, local lithography) | Whether late-stage import mass asymptotes or keeps growing — the paper is explicit that incomplete closure grows import mass **exponentially** |

## 7. Recommendations for encoding (concrete, in this repo's idiom)

1. **Add population as a first-class quantity.** `Mission` needs a
   `settlers: int` (or similar) field distinct from `crewed: bool`; surface
   state needs a running `population` counter, analogous to
   `propellant_produced_t`. Nothing in §3-§5 can be applied without this.
2. **New seed file** `data/city_ramp_seed.yaml`, sibling to
   `requirements_seed.yaml`: population milestones (110 / 1,000 / 1,000,000)
   as named thresholds with their own capability flags
   (`survival_floor`, `settlement_established`, `industrial_autarky`);
   import-mass-per-capita as a decay curve keyed to industrial-closure state,
   not to time; the closure sequence from §2 mapped onto existing catalog
   `group` values.
3. **A `ships_per_synod` growth rule** in the campaign planner: `>= 2×` the
   prior window's fleet, matching §4's one survived anchor — this is a
   natural extension of the existing window-schedule mechanism.
4. **A new lifecycle metric**: import-mass-per-resident-per-synod, charted
   against the ~10 t → ~20 kg decay curve, so the console can show "are we
   on the closure curve or falling behind it" the same way it currently
   shows risk buy-down.
5. **A `conservative_feasibility` scenario** carrying the DLR critique's
   harsher TRL/timeline assumptions, the same way `isru_high_energy` already
   carries Handmer's harsher energy numbers — don't erase the fight between
   the optimists and the skeptics, model both.
6. **Do not** import any Musk cadence or timeline figure as a tier-B/C
   anchor — every one of them failed adversarial verification. Use "at least
   double per synod" (§4) instead.

## 8. Methodology, and what's still open

Two workflow runs (`wf_c79eb9b5-6ff`, `wf_d96e802f-f45`) both hit
session-length limits mid-verification; neither reached the automated
synthesis step. Findings were recovered directly from each run's
`journal.jsonl` and `.output` files rather than lost, then combined and
deduplicated (raw combined set: `docs/_city_ramp_raw_findings.json`, 13
claims confirmed by 3-vote adversarial panels, 5 refuted, 32 left with
errored or partial votes). I then independently re-verified the six
highest-value unverified claims by direct fetch/search rather than accepting
them on the extraction agent's word alone — three PDF primary sources
(NASA BVAD, the NTRS habitat study, two "N-person Mars colony" arxiv papers)
could not be parsed by WebFetch in this session (same limitation hit earlier
on the CATF hydrogen PDF); their figures are carried at Tier C with
independent secondary-source corroboration where I found it, and flagged for
direct re-verification when a working PDF-to-text path is available. The
DLR/Maiwald critique and the Handmer make-buy/population figures were
confirmed by direct fetch or strong secondary corroboration and are more
solid. Nothing in this brief is asserted at Tier A.
