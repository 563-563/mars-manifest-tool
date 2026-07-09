# Input Provenance & Validation Audit

*Every number the engines consume, traced to its source. Compiled 2026-07-09.
Companion to `data/assumptions_seed.json` and `data/component_catalog_seed.csv`.
Sources below were re-verified against the public record on the compile date;
the research grounding is `../SpaceX-to-Mars-Deep-Dive.md` (July 2026, cited).*

## Confidence tiers

| Tier | Meaning |
|---|---|
| **A** | Physical constant or directly measured value. Will not change. |
| **B** | Published program specification, disclosed figure, or flight-measured datum. Could change with program evolution. |
| **C** | Derived from published figures by a stated calculation. Check the derivation, not the source. |
| **D** | Notional engineering estimate. Order-of-magnitude only; first target for replacement with real data. |

---

## 1. Fleet assumptions (`fleet.*`)

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| `payload_mass_per_ship_t` | 100 | **B** | SpaceX's stated baseline: 100–150 t to LEO for reusable Starship; ~100 t to Mars surface is the SpaceX target ([Wikipedia: SpaceX Starship](https://en.wikipedia.org/wiki/SpaceX_Starship), [eoPortal](https://www.eoportal.org/other-space-activities/starship-of-spacex)). **Caveat:** a 2024 peer-reviewed feasibility study could not reproduce SpaceX's mass budget (*Nature Scientific Reports*, cited in deep dive §4); early ships likely deliver less. Treat 100 t as the optimistic bound; a `conservative` scenario override to 75–80 t is defensible. |
| `payload_volume_per_ship_m3` | 1000 | **B** | Standard fairing: 9 m dia × 18 m ≈ 1,000 m³ usable; a stretched 22 m fairing gives ~1,200 m³ ([Wikipedia](https://en.wikipedia.org/wiki/SpaceX_Starship), [NSF forum specs thread](https://forum.nasaspaceflight.com/index.php?topic=50049.240)). Cargo-to-surface config may differ; volume is rarely the binding constraint in our runs (37% batch utilisation). |
| `packing_efficiency` | 0.65 | **D** | Notional stowage factor (usable fraction of bay volume after racks, clearances, deploy mechanisms). Consistent with ISS logistics-packing practice but not traceable to a specific Mars figure. Only affects the volume margin check — no §7 regression depends on it except effective volume. |
| `tankers_per_ship` | 16 (baseline) / 10 (optimistic) | **B** | The two published bounds: SpaceX's plan shared with NASA implies ~14 refueling flights + depot + ship (GAO counted **16 total**; [NASA OIG IG-26-004](https://oig.nasa.gov/wp-content/uploads/2026/03/final-report-ig-26-004-nasas-management-of-the-human-landing-system-contracts.pdf), [Starship HLS Wikipedia](https://en.wikipedia.org/wiki/Starship_HLS)); SpaceX's own baseline is ~10; Musk has claimed 4–8 ([Universe Today](https://www.universetoday.com/articles/musk-says-that-refueling-starship-for-lunar-landings-will-take-8-launches-maybe-4)). These are *lunar* HLS numbers; a Mars ship needs a comparable full depot load. Ship-to-ship cryo transfer remains undemonstrated (mid-2026), so the spread is honest uncertainty — the tool carries both bounds by design. |

## 2. Power & energy assumptions (`power.*`)

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| `sol_hours` | 24.6 | **A** | Martian sol = 24 h 39 m 35 s = 24.66 h. We use 24.6 (0.25% low — matches the source spreadsheet; harmless). |
| `night_hours` | 12.3 | **A** | Half a sol, mid-latitude average. Actual night varies with season/latitude; ±1 h swings night-battery mass ±8%. |
| `dust_storm_autonomy_days` | 5 | **D** | Design *target*, not a storm duration. Real global dust storms last **weeks to months** (2018 storm killed Opportunity; regional storms measured by MER span sols to tens of sols — [Lemmon et al. dust record](https://arxiv.org/pdf/1403.4234)). 5 days already makes solar-only infeasible (290 t of batteries); a realistic 60–120-day storm makes it absurd (multiply by 12–24×). The parameter understates the case *against* solar, which strengthens the fission conclusion. |
| `diversity_factor` | 0.85 | **D** | Standard electrical-engineering practice for simultaneous-demand vs connected load (typical 0.7–0.9 for industrial plants). No Mars-specific source. Affects peak sizing display only — no mass flows from it in v1. |
| `solar_yield_w_per_m2` | 30 | **C** | Derivation: Mars surface global annual average insolation ≈ **133 W/m²** (Mars solar constant ~590 W/m², [43% of Earth's](https://www.powerandresources.com/blog/solar-power-is-challenging-on-mars); surface average after atmosphere/geometry from [Appelbaum & Flood, *Solar radiation on Mars*](https://www.researchgate.net/publication/256334925_Solar_radiation_on_Mars)) × ~22% cell efficiency ≈ **29 W/m² 24h-average electrical**. Our 30 is right on the derivation for clear skies; InSight measured ~0.2%/sol dust degradation on top ([NCBI/PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7375149/)). Sound for mid-latitudes before storm effects. |
| `solar_kg_per_m2` | 1.5 | **C/D — flagged** | **Most optimistic input in the file.** Flown ROSA on ISS is ~340 kg / 115 m² ≈ **2.95 kg/m²** ([Wikipedia: ROSA](https://en.wikipedia.org/wiki/Roll_Out_Solar_Array), [eoPortal](https://www.eoportal.org/satellite-missions/iss-rosa)). Our 1.5 assumes next-gen blanket arrays at ~2× better than flown hardware (vendors project >500 W/kg for large modular ROSA, which supports it directionally — [Redwire flysheet](https://rdw.com/wp-content/uploads/2023/06/redwire-roll-out-solar-array-flysheet.pdf)). Doubling to flown-hardware density raises the 11,805 m² array from 17.7 t to ~35 t — still light next to the 290 t dust-storm battery, so the solar-vs-fission conclusion is robust either way. |
| `battery_wh_per_kg` | 150 | **B** | Pack-level, space-rated Li-ion. Current cells run 150–270 Wh/kg ([NASA SmallSat State-of-the-Art: Power](https://www.nasa.gov/smallsat-institute/sst-soa/power-subsystems/)); pack-level integration (thermal, structure, radiation tolerance) typically derates cell numbers 30–40%, landing at ~150. Conservative-realistic. If Mars packs hit 250 Wh/kg the dust-storm battery drops from 290 t to ~174 t — still infeasible, conclusion unchanged. |
| `battery_kwh_per_m3` | 300 | **C** | Implies ~2,000 kg/m³ pack density at 150 Wh/kg — EV-pack-like (Tesla-class packs run ~200–300 kWh/m³). Plausible; volume from batteries is negligible in all runs (7 m³ of 1,215 m³). |
| `fission_unit_kwe` | 40 | **B** | NASA Fission Surface Power (FSP) project specification: **40 kWe**, 10-year unattended operation, designed for the Moon "to inform future designs for Mars" ([NASA FSP](https://www.nasa.gov/exploration-systems-development-mission-directorate/fission-surface-power/), [NASA Glenn](https://www.nasa.gov/centers-and-facilities/glenn/nasas-fission-surface-power-project-energizes-lunar-exploration/), [NTRS 20220004670](https://ntrs.nasa.gov/citations/20220004670)). **Superseded Aug 2025:** the Duffy directive re-baselined FSP to **≥100 kWe** closed-Brayton, sized for a 15 t heavy-class lander, launch by Q1 FY2030 ([ANS Nuclear Newswire](https://www.ans.org/news/2025-09-02/article-7336/nuclear-power-on-the-moon-what-were-watching/), [Astronomy](https://www.astronomy.com/science/sean-duffy-accelerates-plan-for-lunar-nuclear-reactor/)). Same ~0.15 t/kWe slope. Run the `fsp_2025` scenario for the current spec: 4 units / 60 t instead of 9 / 54 t. |
| `fission_unit_mass_t` | 6.0 | **B** | NASA's FSP mass limit: **under six metric tons** at 40 kWe, sized to fit on a lander ([DOE: 5 Things About FSP](https://www.energy.gov/ne/articles/5-things-you-need-know-about-fission-surface-power-systems), [NASA Glenn](https://www.nasa.gov/centers-and-facilities/glenn/nasas-fission-surface-power-project-energizes-lunar-exploration/)). We use the spec ceiling — appropriately conservative. Note this is a *paper spec*: no FSP unit has flown; KRUSTY (2018) ground-tested only 1 kWe. |
| `fission_unit_volume_m3` | 30 | **D** | Notional stowed volume. FSP deployable concept targets a 4 m × 6 m lander envelope (~75 m³ gross); 30 m³ stowed is plausible but not published. Drives fission volume (270 m³) — worth refining if volume ever binds. |
| `fission_buffer_hours` | 6 | **D** | Engineering judgment (load-following/fault ride-through buffer). No source. Sets buffer battery at 14 t; ±2 h ⇒ ±4.7 t. |
| `power_path` = fission | — | **B (as policy)** | The dust-storm math *is* the source: months-long global storms collapse solar ([deep dive §2, Problem 3](../SpaceX-to-Mars-Deep-Dive.md)); NASA's own Mars ISRU power planning assumes nuclear. The tool sizes both and surfaces the comparison, per spec. |

## 3. Overheads (`overheads.*`)

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| `spares_fraction_of_dry` | 0.35 | **B** | Anchored to flight experience: ECLSS accounted for **34% of all supplied logistics mass** on ISS ([NTRS 20210000437](https://ntrs.nasa.gov/citations/20210000437)); NASA deep-space studies show spares dominating maintenance logistics and closed-loop ECLSS *increasing* spares demand ([NTRS 20210022453](https://ntrs.nasa.gov/api/citations/20210022453/downloads/IEEE_Regenerative%20ECLSS%20and%20Logistics%20Analysis%20for%20Sustained%20Lunar%20Missions%20v3.docx.pdf)). NASA modeling without spares puts mission reliability <1% (deep dive §2, Problem 5). 30–40% of dry mass is the defensible planning band; scenarios carry 0.25 (optimistic) to 0.40 (conservative). At 53 t, this is the single biggest "soft" mass line — a real sparing analysis is the highest-value refinement available. |
| `contingency_fraction` | 0.10 | **D** | Standard mass-growth-allowance practice (AIAA S-120 class: 10–30% depending on maturity). 10% is *low* for concept-stage hardware — ANSI/AIAA guidance would suggest 25–30% for TRL 3–4 systems. Flag: arguably optimistic. |

## 4. Cost (`cost.*`)

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| `per_launch_cost_musd.aspirational` | 2 | **B (as a quote)** | Musk's stated marginal-cost goal: "maybe it'll be like $2 million" (2019, [Space.com](https://www.space.com/spacex-starship-flight-passenger-cost-elon-musk.html), [TechCrunch](https://techcrunch.com/2019/11/06/elon-musk-says-spacexs-starship-could-fly-for-as-little-as-2-million-per-launch/)); reiterated $2–3M in 2024 ([SpaceNews](https://spacenews.com/musk-outlines-plans-to-increase-starship-launch-rate-and-performance/)). This is an aspiration, not a price — label it that way in any output. |
| `per_launch_cost_musd.operational` | 30 | **C** | Implied by independent $100–500/kg estimates on ~100 t ($10–50M/launch; midpoint ~$30M). Derivation, not a disclosure. |
| `per_launch_cost_musd.near_term` | 90 | **B** | Approximately the disclosed real Starship launch contract price (~$90M, 2026; deep dive §5, sourced to the SpaceX S-1 era disclosures — SEC EDGAR CIK 1181412). The most defensible near-term figure; note it's a *customer price*, likely above internal marginal cost. |
| `propellant_cost_per_launch_musd` | 1 | **C** | ~4,600 t methalox at commodity prices ≈ $0.9–1M; consistent with Musk's "$900k of propellant" ([Space.com](https://www.space.com/spacex-starship-flight-passenger-cost-elon-musk.html)). |
| `spacex_internal` scenario: cargo ship $30M / tanker $12M | — | **C** | **Internal marginal-cost basis** (what the user asked the model to reflect). Anchors: Payload Research estimates ~$90M to *build* a full stack today (≈70% booster / 30% ship, i.e. ~$27M per ship), trending to ~$20M at scale; amortized per-flight cost ≈ **$12M at ~10 reuses** on a ~$50M build, ≈ $2.2M at 100 reuses ([NSF forum: Payload reports](https://forum.nasaspaceflight.com/index.php?topic=60239.0), [Space Investments: Starship economics](https://www.spaceinvestments.io/space-economy-insights/starship-economics)). Key structural point: **Mars cargo ships are expended** (they stay on the surface) so their launch carries the ship build cost; **tankers are reused** so they fly at marginal cost. The engine now prices the two legs separately when a scenario sets `cost.cargo_ship_launch_cost_musd` / `cost.tanker_launch_cost_musd`. The disclosed ~$90M contract remains the *customer-price* ceiling. Catalog hardware costs were already internal build-cost basis (workbook header). |
| Catalog `unit_cost_musd_low/high` | various | **D** | First-of-kind hardware guesses spanning 2–5× ranges. The cost workbook's system-level table ($1.9–8.2B) and the catalog decomposition ($2.7–11.6B with power) differ in scope (see `tests/test_budgets.py` note) — treat all cargo-cost outputs as order-of-magnitude. Deep-dive anchor: development cost dwarfs recurring cost (Starship $15B+ to date). |

## 5. Windows & campaign structure

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| Synod cadence | ~26 months | **A** | Earth–Mars synodic period = 779.9 days ≈ 25.6 months. Orbital mechanics. |
| Window 0 = 2026-11, 5 ships | — | **B (as a plan)** | Musk's stated 2025 plan: ~5 uncrewed ships in the late-2026 window, carrying Optimus robots; he rates it "50/50" (deep dive §4, [Space.com May 2025]). Independent consensus puts first *crew* in the 2030s–2040s, so the 2033 crewed window in our example campaign is aggressive — it's Musk-schedule, not consensus-schedule. |
| `transit_days` | 210 | **A/B** | 6–9 month transit range for conjunction-class trajectories; 210 d is the fast end. |
| `crewed_requires` gates | 6 flags | **B (as doctrine)** | Encodes NASA/industry consensus and the deep dive's core finding: no crew without demonstrated EDL, baseload power, return propellant, closed life support, habitat, radiation management (deep dive §2 & §6). The specific flag set is our taxonomy (HANDOFF §6); the *rule* is well-sourced doctrine. |
| `capability_unlocks` rules | — | **D** | Tool extension (delivered-hardware proxies for "demonstrated capability"). Deliberately simplistic in v1: delivering a Sabatier plant is not the same as *proving* propellant production. Flagged for M6: add an explicit demonstration/commissioning delay (e.g. gate retires one window after delivery). |

## 6. Component catalog (`component_catalog_seed.csv`)

Masses, volumes, powers and duty cycles are **Tier D throughout** — notional order-of-magnitude engineering estimates derived from the manifest narrative (`../Mars-Robotic-Precursor-Flight-Manifest.md`), scaled to be internally consistent. Anchors where they exist:

| Component | Key figure | Tier | Anchor |
|---|---|---|---|
| `fission_unit` | 40 kWe / 6 t | **B** | NASA FSP spec (see §2). The only catalog row with a published program spec behind it. |
| `solar_module_1000m2` | 30 kW / 1.5 t per 1,000 m² | **C** | Both figures follow from the §2 solar derivations. |
| `battery_module_100kwh` | 0.67 t per 100 kWh | **C** | = 150 Wh/kg pack spec exactly. |
| `optimus_robot` | 0.1 t/unit | **B** | Tesla's published Optimus mass ~57–73 kg; 100 kg with Mars hardening/charger allocation is reasonable. Its *capability* on Mars is wholly unproven (autonomy under 4–22 min light delay). |
| `water_electrolysis` | 150 kW peak | **C** | Sized to pilot-scale propellant production; consistent with electrolysis dominating ISRU load in every NASA ISRU study. Full-scale (~1 MW+, deep dive: up to 10 MW-class estimates) is deliberately deferred to later windows. |
| `sabatier_reactor`, `co2_acquisition`, `cryo_liquefaction` | 2–9 t each | **D** | No integrated Mars plant has ever operated. The only flight datum is **MOXIE: 122 g of O₂ total, ~6–12 g/hr** ([NASA MOXIE results, Sep 2023](https://www.nasa.gov/missions/mars-2020-perseverance/nasas-oxygen-generating-experiment-moxie-completes-mars-mission/)) — meaning these rows are extrapolated ~8 orders of magnitude from demonstrated hardware. They are the least-validated mass numbers in the catalog and simultaneously the most mission-critical. |
| `excavator_rassor` | 2 t/unit | **D** | NASA KSC's RASSOR prototype is ~66–120 kg *class*; our 2 t assumes a production-scale icy-regolith machine. Name is an anchor, mass is a guess. |
| `habitat_module` | 15 t / 300 m³ | **C/D** | Bigelow B330-class inflatable: ~20 t / 330 m³ — our row is in family. |
| `eclss_habitat` | 7 t | **C/D** | In family with ISS ECLSS-derived masses for a small crew; the 34% logistics figure (§3) shows the real cost is in *spares*, which we carry separately. |
| `consumables_cache` | 15 t | **C** | ~1,000-day crew margin at ISS consumption rates for a small crew is single-digit-to-tens of tonnes; order-of-magnitude sound. |
| Everything else (rovers, cranes, comms, thermal, dust, site prep) | 0.5–6 t | **D** | Narrative-derived engineering estimates. Individually small; collectively ~30 t of the 98.5 t fixed hardware. |

`readiness_gate`, `earliest_window`, `depends_on` columns: **our taxonomy** (Tier D structure), grounded in the deep dive's gate logic but not externally sourced.

---

## 7. Sensitivity — which inputs actually move the answers

Ranked by influence on the headline outputs (grand mass 236 t, 55–85 launches, fission 9 units):

1. **`water_electrolysis` peak (150 kW)** — 36% of total load. ±50 kW ⇒ ±1–2 fission units, ±8–12 t of power+spares mass.
2. **`spares_fraction_of_dry` (0.35)** — 53 t line. The 0.25–0.40 scenario band swings grand total ~221–244 t.
3. **`tankers_per_ship` (10–16)** — directly sets 55 vs 85 launches; dominant cost driver at near-term prices ($2.7B spread).
4. **`per_launch_cost_musd` (2–90)** — 45× spread; the entire launch-campaign cost question ($0.11B vs $7.65B for the batch).
5. **`payload_mass_per_ship_t` (100)** — if early ships deliver 75 t, batch utilisation goes 47%→63%; still fits, but margin for growth halves.
6. **`fission_unit_kwe`/`mass_t`** — spec-anchored; the pair sets the power-mass slope (0.15 t/kWe).
7. **`battery_wh_per_kg`** — only matters for the solar path; even at 250 Wh/kg solar-only stays infeasible.

## 8. Validation backlog (replace first, in order)

1. Real sparing analysis to replace the flat 35% (biggest soft mass line).
2. ISRU pilot-plant mass/power from NASA ISRU project literature to replace the D-tier Sabatier chain rows.
3. Starship cargo-variant actual payload capacity as flights accumulate (watch: does 100 t survive contact with reality?).
4. ~~FSP program updates~~ **Done 2026-07-09**: `fsp_2025` scenario encodes the Aug-2025 100 kWe directive.
5. Contingency fraction to AIAA-standard MGA by subsystem TRL (current 10% is likely low).
6. Demonstration-delay model for capability gates (delivered ≠ proven).
