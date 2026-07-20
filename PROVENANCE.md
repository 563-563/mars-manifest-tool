# Input Provenance & Validation Audit

*GENERATED from `inputs/provenance.json` — edit the JSON, then run
`mars ledgers` to regenerate this view. Do not hand-edit this file.*

*Every number the engines consume, traced to its source. Compiled 2026-07-09.
Companion to `inputs/assumptions.json` and `inputs/catalog.csv`.
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
| `payload_volume_per_ship_m3` | 614 | **B — re-anchored 2026-07-09** | The current published Starship payload volume ([Wikipedia infobox](https://en.wikipedia.org/wiki/SpaceX_Starship), verified). Replaces the ~1,000 m³ carried from earlier 9 m × 18 m fairing statements — the baseline now uses the verified number rather than an optimistic historical one (policy: anchor to real data, never keep a known-stale value and downgrade its tier). Consequence applied at the time (2026-07-09 baseline): the then-uncrewed 2035 buildout window became volume-bound and grew to 11 ships. (Superseded by the 2026-07-14 re-baselines; the check itself is permanent.) The workbook-port regression targets are unaffected (they never depended on bay volume). |
| `packing_efficiency` | 0.65 | **D** | Notional stowage factor (usable fraction of bay volume after racks, clearances, deploy mechanisms). Consistent with ISS logistics-packing practice but not traceable to a specific Mars figure. Only affects the volume margin check — no workbook-port regression target depends on it except effective volume. |
| `tankers_per_ship` | 16 (baseline) / 10 (optimistic) | **B** | The two published bounds: SpaceX's plan shared with NASA implies ~14 refueling flights + depot + ship (GAO counted **16 total**; [NASA OIG IG-26-004](https://oig.nasa.gov/wp-content/uploads/2026/03/final-report-ig-26-004-nasas-management-of-the-human-landing-system-contracts.pdf), [Starship HLS Wikipedia](https://en.wikipedia.org/wiki/Starship_HLS)); SpaceX's own baseline is ~10; Musk has claimed 4–8 ([Universe Today](https://www.universetoday.com/articles/musk-says-that-refueling-starship-for-lunar-landings-will-take-8-launches-maybe-4)). These are *lunar* HLS numbers; a Mars ship needs a comparable full depot load. Ship-to-ship cryo transfer remains undemonstrated (mid-2026), so the spread is honest uncertainty — the tool carries both bounds by design. |

## 2. Power & energy assumptions (`power.*`)

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| `sol_hours` | 24.6 | **A** | Martian sol = 24 h 39 m 35 s = 24.66 h. We use 24.6 (0.25% low — matches the source spreadsheet; harmless). |
| `night_hours` | 12.3 | **A** | Half a sol, mid-latitude average. Actual night varies with season/latitude; ±1 h swings night-battery mass ±8%. |
| catalog `load_class` column | critical / interruptible / none | **C (structure), D (assignments)** | **Adopted 2026-07-09 from the comparative review** (Handmer): dust-storm storage is sized for *survival* loads only — thermal, comms, nav, compute, ECLSS, plant controls (~50.5 kW of the 354 kW precursor load) — because production loads pause during storms. The full-load figure is retained as the worst-case reference (it is the workbook-port formula value). This un-rigs the solar-vs-fission trade: survival storm battery ~41 t vs the 290 t full-load figure. Class assignments are our judgment (D). |
| `dust_storm_autonomy_days` | 5 | **D** | Design *target*, not a storm duration. Real global dust storms last **weeks to months** (2018 storm killed Opportunity; regional storms measured by MER span sols to tens of sols — [Lemmon et al. dust record](https://arxiv.org/pdf/1403.4234)). With survival-load sizing (see `load_class`), 5 days needs ~41 t of storm battery; a realistic 60–120-day storm scales that 12–24× (~500–1,000 t) — so long storms still argue for fission or for accepting months of production halt on solar. |
| `diversity_factor` | 0.85 | **D** | Standard electrical-engineering practice for simultaneous-demand vs connected load (typical 0.7–0.9 for industrial plants). No Mars-specific source. Affects peak sizing display only — no mass flows from it in v1. |
| `solar_yield_w_per_m2` | 30 | **C** | Derivation: Mars surface global annual average insolation ≈ **133 W/m²** (Mars solar constant ~590 W/m², [43% of Earth's](https://www.powerandresources.com/blog/solar-power-is-challenging-on-mars); surface average after atmosphere/geometry from [Appelbaum & Flood, *Solar radiation on Mars*](https://www.researchgate.net/publication/256334925_Solar_radiation_on_Mars)) × ~22% cell efficiency ≈ **29 W/m² 24h-average electrical**. Our 30 is right on the derivation for clear skies; InSight measured ~0.2%/sol dust degradation on top ([NCBI/PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7375149/)). Sound for mid-latitudes before storm effects. |
| `solar_kg_per_m2` | 4.0 | **B/C — re-anchored 2026-07-09** | Flown ROSA-class areal density: 325 kg demonstrator ([Wikipedia: ROSA](https://en.wikipedia.org/wiki/Roll_Out_Solar_Array), verified) over a ~6 × 13.7 m wing ([eoPortal](https://www.eoportal.org/satellite-missions/iss-rosa)) ≈ **~4 kg/m²**. Replaces the aspirational 1.5 kg/m² (which vendors project directionally — [Redwire flysheet](https://rdw.com/wp-content/uploads/2023/06/redwire-roll-out-solar-array-flysheet.pdf) — but no flown hardware supports). At flown density the precursor's 11,805 m² solar option masses ~47 t. With survival-load storm sizing the solar path is no longer infeasible outright — the trade is now honest: solar = lighter but months of production halt in a global storm; fission = heavier but weather-independent. A future `advanced_solar` scenario can carry the vendor number when hardware flies. |
| `battery_wh_per_kg` | 150 | **B** | Pack-level, space-rated Li-ion. Current cells run 150–270 Wh/kg ([NASA SmallSat State-of-the-Art: Power](https://www.nasa.gov/smallsat-institute/sst-soa/power-subsystems/)); pack-level integration (thermal, structure, radiation tolerance) typically derates cell numbers 30–40%, landing at ~150. Conservative-realistic. If Mars packs hit 250 Wh/kg the survival storm battery drops from ~41 t to ~25 t and the full-load reference from 290 t to ~174 t. |
| `battery_kwh_per_m3` | 300 | **C** | Implies ~2,000 kg/m³ pack density at 150 Wh/kg — EV-pack-like (Tesla-class packs run ~200–300 kWh/m³). Plausible; volume from batteries is negligible in all runs (7 m³ of 1,215 m³). |
| `fission_unit_kwe` | 40 | **B** | NASA Fission Surface Power (FSP) project specification: **40 kWe**, 10-year unattended operation, designed for the Moon "to inform future designs for Mars" ([NASA FSP](https://www.nasa.gov/exploration-systems-development-mission-directorate/fission-surface-power/), [NASA Glenn](https://www.nasa.gov/centers-and-facilities/glenn/nasas-fission-surface-power-project-energizes-lunar-exploration/), [NTRS 20220004670](https://ntrs.nasa.gov/citations/20220004670)). **Superseded Aug 2025:** the Duffy directive re-baselined FSP to **≥100 kWe** closed-Brayton, sized for a 15 t heavy-class lander, launch by Q1 FY2030 ([ANS Nuclear Newswire](https://www.ans.org/news/2025-09-02/article-7336/nuclear-power-on-the-moon-what-were-watching/), [Astronomy](https://www.astronomy.com/science/sean-duffy-accelerates-plan-for-lunar-nuclear-reactor/)). Same ~0.15 t/kWe slope. Run the `fsp_2025` scenario for the current spec: 4 units / 60 t instead of 9 / 54 t. |
| `fission_unit_mass_t` | 6.0 | **B** | NASA's FSP mass limit: **under six metric tons** at 40 kWe, sized to fit on a lander ([DOE: 5 Things About FSP](https://www.energy.gov/ne/articles/5-things-you-need-know-about-fission-surface-power-systems), [NASA Glenn](https://www.nasa.gov/centers-and-facilities/glenn/nasas-fission-surface-power-project-energizes-lunar-exploration/)). We use the spec ceiling — appropriately conservative. Note this is a *paper spec*: no FSP unit has flown; KRUSTY (2018) ground-tested only 1 kWe. |
| `fission_unit_volume_m3` | 30 | **D** | Notional stowed volume. FSP deployable concept targets a 4 m × 6 m lander envelope (~75 m³ gross); 30 m³ stowed is plausible but not published. Drives fission volume (270 m³) — worth refining if volume ever binds. |
| `fission_buffer_hours` | 6 | **D** | Engineering judgment (load-following/fault ride-through buffer). No source. Sets buffer battery at 14 t; ±2 h ⇒ ±4.7 t. |
| `power_path` = fission | — | **B (as policy)** | The dust-storm math *is* the source: months-long global storms collapse solar ([deep dive §2, Problem 3](../SpaceX-to-Mars-Deep-Dive.md)); NASA's own Mars ISRU power planning assumes nuclear. The tool sizes both and surfaces the comparison, per spec. |

## 2b. ISRU chain rates & energy (`isru.*`)

Stoichiometry (water/CO₂/O₂ per kg CH₄) is computed from molar masses in
`isru.py` — **Tier A**, not assumptions. The tunables:

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| `raptor_o_f_ratio` | 3.6 | **B** | Raptor mixture ratio, commonly cited ~3.6 ([Everyday Astronaut](https://everydayastronaut.com/raptor-engine/), [Wikipedia](https://en.wikipedia.org/wiki/SpaceX_Raptor)); some sources say ~3.8. Sensitivity flag: electrolysis co-produces 3.99 kg O₂ per kg CH₄, so above O/F ≈ 3.99 the chain needs supplemental O₂ (MOXIE-style CO₂ electrolysis) — the model warns when crossed. |
| `electrolysis_kwh_per_kg_h2o` | 6.1 | **C** | = 55 kWh/kg H₂ ÷ 8.94 kg H₂O per kg H₂. **Verified 2026-07-09**: "Electrolysis of water at ambient temperatures requires 50–55 kWh per kilogram of hydrogen — alkaline 50, PEM 55; thermodynamic limit 40" ([World Nuclear](https://world-nuclear.org/information-library/energy-and-the-environment/hydrogen-production-and-uses), primary; [EH2 whitepaper](https://eh2.com/wp-content/uploads/2025/01/Final_PEM_vs_Alkaline_December_2024_Whitepaper.pdf) secondary). **2026-07-10**: CATF PDF finally parsed (pypdf) — PEM system at **48.1 kWh_AC/kg H₂** as a 2030 estimate, i.e. our 55 is the conservative current-day figure with ~13% improvement headroom. Terrestrial numbers — Mars packaging will be worse, not better. |
| `co2_capture_kwh_per_kg_co2` | 0.7 | **D** | Cryo-freezing/adsorption of 6-mbar CO₂; literature spans ~0.3–2+ kWh/kg depending on method. Order-of-magnitude. |
| `sabatier_support_kwh_per_kg_ch4` | 1.5 | **D** | Reaction is exothermic; this covers recycle compressors, controls, thermal management. Notional. |
| `liquefaction_kwh_per_kg_propellant` | 0.8 | **C/D** | Cryocooler work for CH₄/O₂ + boil-off reliquefaction at Mars ambient; typical estimates ~0.5–1. |
| `water_processing_kwh_per_kg_h2o` | 0.2 | **D** | Melt/filter/deionize energy per kg product water. Notional; excavation energy not yet modeled. |
| `excavation_kwh_per_kg_h2o` | 0.1 | **D** | Excavator energy per kg of net water mined (icy regolith digging + haul). Notional; RASSOR-class machines are designed for low-energy digging. Not the bottleneck at any seeded configuration. |
| `plant_availability` | 0.85 | **D** | Fraction of nameplate hours the chain actually runs (maintenance, dust events, fault recovery under 4–22 min comms delay). No Mars precedent exists; terrestrial chemical plants run 0.9+, but this plant is unattended. Applied to production totals, not nameplate rates. |
| `commissioning_factor` | 0.6 | **D** | Fraction of nameplate a newly-delivered chain increment achieves during its *first* synod — deployment, checkout, and ramp under comms delay eat the rest. The campaign planner discounts only the capacity added in a given window; earlier hardware runs at full rate. No Mars precedent; terrestrial first-year plant ramp-up is the loose analogy. Effect on the baseline program: the pilot chain banks ~483 t in 2031 (vs nameplate) and `return_propellant_proven` retires at 2033 with ~3,223 t — 2.3× the 1,400 t gate, sized so the Jan-2035 return demo can burn a full load. |
| `return_propellant_t` | 1,400 | **B** | Midpoint of the established 1,200–1,500 t per crewed return ship (HANDOFF §2, deep dive Problem 3). |
| `production_sols_per_synod` | 600 | **D** | Usable production time between windows (~780-day synod minus commissioning/margin). |
| `mode` / `co2_electrolysis_kwh_per_kg_o2` | sabatier / 11 | **C/D** | **Adopted from DRA 5.0**: `oxygen_only_isru` scenario makes LOX from atmospheric CO₂ (solid-oxide electrolysis, MOXIE heritage — the only ISRU chemistry ever flown on Mars) with CH₄ imported from Earth (~304 t/load ≈ 4 ships). Spec ~13.7 kWh/kg O₂; buys out the entire water-mining risk. SOE energy is a scaled-MOXIE estimate (D). |
| `isru_high_energy` scenario | ~2× chain energies | **C (anchor B)** | **Adopted from Handmer**: his all-in figure — 17 GWh per 240 t CH₄ ([Powering the Mars base](https://caseyhandmer.wordpress.com/2024/11/05/powering-the-mars-base/)) — is ~2× our bottom-up chain math. The scenario carries spec ≈15.3 kWh/kg propellant → full-scale ≈1.7 MW. Treat 7.6–15.3 kWh/kg as the honest range. |
| `water_processing` rate anchor | — | **C** | RedWater Rodwell-class well: ~1 t water per 10 days per well ([*New Space* 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9527650/)). Our 3.5 t unit at ~3.6 t/sol implies a plant ~36× a single well — flag when sharpening the Tier-D water rows. |
| `water_confirmed` gate | prospecting + 200 sols | **C (doctrine B)** | **Adopted from Handmer** (prospect-before-commit): the window-1 fuel-factory mission carries `requires: [water_confirmed]` — site water must be confirmed by ~200 sols of window-0 prospecting before the factory fleet commits (~18-month real margin between data return and ship date). |

**Gate change (2026-07-09):** `return_propellant_proven` now additionally
requires `min_propellant_t: 1400` — cumulative tonnes actually produced by the
campaign's ISRU state, not just hardware delivered. In the program plan the
gate retires one window after the fuel-factory delivery (2033-03, 2,686 t
banked) and the first crew launches with ~10,200 t produced. The planner also
derates production when installed generation can't carry the delivered load.

**Validation checks the model now reproduces from first principles:** specific
energy ≈ **7.65 kWh/kg propellant** → one 1,400 t load ≈ **10.7 GWh** →
**~850 kW continuous** chain power (at 85% availability) to fill one load per
window — squarely the "~1 MW full-scale ISRU" domain constant (HANDOFF §2).
Net water ≈ **684 t per load** — the "hundreds of tonnes" grounding. Pilot
chain (seeded quantities): **~21 kg/hr nameplate, electrolysis-limited**,
~269 t per window = 19% of one load, ~8.8 years to a full load.

## 2b-edl. EDL risk (`edl.*`)

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| `edl.success_prob_base` | 0.5 | **D** | Musk rated the first uncrewed Mars attempt "50/50" (deep dive §4). Nothing heavier than ~1 t has landed on Mars, so window-0 uncertainty is genuine. A scenario axis, not a claim. |
| `edl.success_prob_improvement_per_synod` | 0.12 | **D** | Judgment: each synod's landings + telemetry buy down EDL risk. Ramps 0.5 → 0.95 over ~4 windows. |
| `edl.max_prob` | 0.95 | **D** | Mature-EDL ceiling; even routine Falcon 9 landing success sits in the high-90s and Mars EDL is harder. |
| demonstrated-reliability metric | rule of three | **A (statistics)** | 0 failures in N landings ⇒ failure rate ≤ ~3/N at 95% confidence, so demonstrated reliability ≈ 1 − 3/N. Standard reliability statistics; assumes independent trials. |
| water-independence constants | 3.217 kg/person-day; 90% recovery; 65.5% cache water | **B / C** | Water rate is the verified BVAD metabolic value; 90% ECLSS recovery is ISS-class (NTRS ECLSS literature, C); cache water fraction = 3.217/4.912 of the BVAD metabolic split (C). |

## 2c. Lifecycle config (`lifecycle.*`)

| Input | Tier | Source & validation |
|---|---|---|
| `risk_weights` | **D (structure B)** | Relative gate severities summing ~100, derived from the deep dive's six hard problems: return propellant 25, EDL 20, power 15, life support 15, radiation 10, remainder small. The *ranking* is well-sourced (deep dive §2); the numeric weights are judgment. Orbital refueling (Problem 1) is Earth-side and outside the surface campaign's scope. |
| `min_sols_on_surface` (ECLSS 1,000 sols) | **B (as doctrine)** | The ~1,000-day life-support proof requirement (deep dive Problem 5; NASA ECLSS reliability studies). Forces the demonstration article to fly no later than two windows before crew — the one legitimate reason to land crew-era hardware early. |
| `crew_era_components` / `demo_exempt_units` / `shelf_life_components` | **D** | Our taxonomy: hardware exercised only by crew; first habitat+ECLSS set exempted as the testbed; consumables flagged for shelf life when landed >1 synod early. |

## 3. Overheads (`overheads.*`)

| Input | Value | Tier | Source & validation |
|---|---|---|---|
| `spares_fraction_of_dry` | 0.35 | **B** | Anchored to flight experience: ECLSS accounted for **34% of all supplied logistics mass** on ISS ([NTRS 20210000437](https://ntrs.nasa.gov/citations/20210000437)); NASA deep-space studies show spares dominating maintenance logistics and closed-loop ECLSS *increasing* spares demand ([NTRS 20210022453](https://ntrs.nasa.gov/api/citations/20210022453/downloads/IEEE_Regenerative%20ECLSS%20and%20Logistics%20Analysis%20for%20Sustained%20Lunar%20Missions%20v3.docx.pdf)). NASA modeling without spares puts mission reliability <1% (deep dive §2, Problem 5). 30–40% of dry mass is the defensible planning band; scenarios carry 0.25 (optimistic) to 0.40 (conservative). At 53 t, this is the single biggest "soft" mass line. |
| `spares_fraction_by_group` (`informed_spares` scenario) | 0.10–0.40 by group | **B/C** | Per-group sparing replacing the flat 35%, from the supportability literature: a 919-day crew-of-6 Mars ECLSS analysis found spares = **34–41% of system mass** ([ECLSS reliability analysis tool](https://www.researchgate.net/publication/321105641_ECLSS_reliability_analysis_tool_for_long_duration_spaceflight); methodology line: Owens & de Weck semi-Markov sparing, [ICES/NTRS supportability series](https://ntrs.nasa.gov/api/citations/20240005642/downloads/ICES_2024_SupportabilityMethodology_FINAL_3.pdf); reference framework: [NASA Life Support BVAD, TP-2015-218570](https://ntrs.nasa.gov/api/citations/20210024855/downloads/BVAD_2.15.22-final.pdf)). Applied: 0.40 life support **and ISRU** (same continuous-process class, zero flight heritage), 0.30–0.35 mechanisms in abrasive regolith, 0.15 fission (FSP spec: 10 yr unattended), 0.10 passive/structures. Non-ECLSS class fractions are **C** (constructed, logic stated) — the literature only firmly anchors the ECLSS band. Net effect on the precursor batch: spares 53.1 t → **37.5 t**, grand total 236.4 → **220.8 t**: the flat 35% *overtaxes* power hardware designed for zero maintenance. |
| `contingency_fraction` | 0.10 | **D** | Standard mass-growth-allowance practice (AIAA S-120 class: 10–30% depending on maturity). 10% is *low* for concept-stage hardware — ANSI/AIAA guidance suggests 25–30% for TRL 3–4 systems. **The `aiaa_contingency` scenario (D3, done)** carries the honest per-group MGA (25–30% for ISRU/mining/city-industry down to 10% for off-the-shelf); kept a scenario pending review before baseline promotion. |

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
| Window 0 = 2031-01, 5 ships | — | **C (judgment from B sources)** | **Re-baselined 2026-07-09** from Musk's stated late-2026 plan: no 2026 flight is credible (Feb-2026 Moon-first pivot; orbital refueling undemonstrated and Starship grounded mid-2026, deep dive §1/§4). First robotic window 2031-01 matches the deep dive's "uncrewed plausible late 2020s–early 2030s". Musk's original 2026/2033 dates survive only in the legacy fixture `campaign_4window.yaml`. |
| First crew = 2035-05 (blue-sky baseline) | — | **C (judgment; gates B)** | **Re-baselined 2026-07-14** from the 2037-07 plan after the blue-sky review: same six crew gates plus the L1-RET-01 return-demo posture, resequenced (doubled 2033 fuel chain, fly-with provisioning, pilots one synod ahead). 2035 is beyond the aggressive end of the 2030s–2040s independent consensus and is carried as an *option*, not a promise: under `conservative_feasibility` the gates hold and crew auto-slips to 2037 — the archived `examples/conservative_program.json`. Decisions logged in docs/CONSIDERED.md (2026-07-14 rows). |
| `transit_days` | 210 | **A/B** | 6–9 month transit range for conjunction-class trajectories; 210 d is the fast end. |
| `crewed_requires` gates | 6 flags | **B (as doctrine)** | Encodes NASA/industry consensus and the deep dive's core finding: no crew without demonstrated EDL, baseload power, return propellant, closed life support, habitat, radiation management (deep dive §2 & §6). The specific flag set is our taxonomy (HANDOFF §6); the *rule* is well-sourced doctrine. |
| `capability_unlocks` rules | — | **D** | Tool extension (delivered-hardware proxies for "demonstrated capability"). Deliberately simplistic in v1: delivering a Sabatier plant is not the same as *proving* propellant production. Flagged for M6: add an explicit demonstration/commissioning delay (e.g. gate retires one window after delivery). |

### 5a. Return-leg astrodynamics (`L1-RET-01` requirement branch, `transport_readiness.{earth_entry_tps,mars_ascent_tei,surface_prop_transfer}`)

Added 2026-07-13. The tool models the outbound cargo leg only; the return
leg was asserted at L0 ("demonstrated return path") but never decomposed.
These figures verify the return is **not** a mirror of the outbound. Computed
first-order from published orbital constants (Hohmann transfer, patched-conic
v-infinity); see the derivation in the session log.

| Quantity | Value | Tier | Source & validation |
|---|---|---|---|
| Hohmann transit time (each way) | ~259 d | **A** | Same heliocentric transfer ellipse both directions → transit time is symmetric to first order. Confirms `transit_days`=210 (a faster-than-Hohmann nominal) is defensible for the return leg as a **symmetric assumption**, not a derived asymmetry. |
| Mars escape / surface gravity | 5.03 km/s / 3.73 m/s² (0.38 g) | **A** | vs Earth 11.19 km/s / 9.81 m/s². Leaving Mars is far cheaper in Δv than leaving Earth. |
| Mars surface → TEI Δv | ~5.7 km/s ideal, ~6.5 km/s with losses | **B** | Single stage, entirely on ISRU propellant; no Mars-orbit tanker (contrast Earth's LEO-refuel architecture). Underlies `L2-RET-03`. |
| Earth-return entry speed | ~11.6 km/s | **A** | v_inf ~2.9 km/s + Earth escape. **~2.04× the ~5.7 km/s Mars-arrival entry → ~8.4× heat load (∝v³).** The return TPS is a distinct qualification item, not the Mars-EDL shield reused. Underlies `L2-RET-02`. |
| Mars→Earth departure window in the gap | ~Jan 2035 dep, ~Aug 2035 Earth arr | **B** | Conjunction-class return (arrival + ~460 d surface wait); recurs every synod. Falls ~23 months before the 2037-07 crew commit → an uncrewed return demonstrator can gate crew #1. Underlies `L1-RET-01`. First-order (fixed 210 d transit, nominal stay); robust to ±weeks slop given the 23-month margin. |
| `transport_readiness` return flags | true (baseline) | **B (as doctrine)** | Mirror of the outbound orbit/reuse/refill/chill flags. All three are undemonstrated as of 2026 (nothing has ascended from Mars, transferred ISRU propellant, or flown an interplanetary-return entry at scale); `conservative_feasibility` flips them false. |

## 6. Component catalog (`catalog.csv`)

Masses, volumes, powers and duty cycles are **Tier D throughout** — notional order-of-magnitude engineering estimates derived from the manifest narrative (`../Mars-Robotic-Precursor-Flight-Manifest.md`), scaled to be internally consistent. Anchors where they exist:

| Component | Key figure | Tier | Anchor |
|---|---|---|---|
| `fission_unit` | 40 kWe / 6 t | **B** | NASA FSP spec (see §2). The only catalog row with a published program spec behind it. |
| `solar_module_1000m2` | 30 kW / 1.5 t per 1,000 m² | **C** | Both figures follow from the §2 solar derivations. |
| `battery_module_100kwh` | 0.67 t per 100 kWh | **C** | = 150 Wh/kg pack spec exactly. |
| `optimus_robot` | 0.1 t/unit | **B** | Tesla's published Optimus mass ~57–73 kg; 100 kg with Mars hardening/charger allocation is reasonable. Its *capability* on Mars is wholly unproven (autonomy under 4–22 min light delay). |
| `water_electrolysis` | 150 kW peak | **C** | Sized to pilot-scale propellant production; consistent with electrolysis dominating ISRU load in every NASA ISRU study. Full-scale (~1 MW+, deep dive: up to 10 MW-class estimates) is deliberately deferred to later windows. |
| `sabatier_reactor`, `co2_acquisition`, `cryo_liquefaction` | 2–9 t each | **D (system aggregate cross-checked, C)** | No integrated Mars plant has ever operated; the only flight datum is **MOXIE: 122 g of O₂ total, ~6–12 g/hr** ([NASA MOXIE, Sep 2023](https://www.nasa.gov/missions/mars-2020-perseverance/nasas-oxygen-generating-experiment-moxie-completes-mars-mission/)), so individual-component masses stay D-tier. **D2 cross-check (2026-07-10):** our full 1× chain is ~22 t of hardware at ~316 t/synod nameplate = **0.070 t-hw per t-propellant/synod**, within **7%** of NASA's leading Mars-Ascent-Vehicle Sabatier ISRU study (~1.7–2.2 t hardware for ~30 t propellant = 0.065; [NTRS 20170001421](https://ntrs.nasa.gov/citations/20170001421) / [AIAA 2017-0423](https://sciences.ucf.edu/class/wp-content/uploads/sites/23/2017/02/An-ISRU-propellant-production-system-for-a-fully-fueled-Mars-Ascent-Vehicle-AIAA-2017-0423.pdf)). The oxygen-only variant (~1 t hardware, 7 t CH₄ imported per MAV) likewise matches our `oxygen_only` structure. The aggregate is validated; component splits remain the refinement target. Full-scale sizing has a matching reference: [NTRS 20230017069, Kiloton-Class ISRU](https://ntrs.nasa.gov/api/citations/20230017069/downloads/SciTech%20Mars%20kiloton%20ISRU%20Final.pdf). |
| `excavator_rassor` | 2 t/unit | **D** | NASA KSC's RASSOR prototype is ~66–120 kg *class*; our 2 t assumes a production-scale icy-regolith machine. Name is an anchor, mass is a guess. |
| `habitat_module` | 15 t / 300 m³ | **C/D** | Bigelow B330-class inflatable: ~20 t / 330 m³ — our row is in family. **Workbook-fixture component only** (carries deployed volume as stowed); the live baseline flies `habitat_inflatable` (15 t / 75 m³ stowed) everywhere — see §8 log, 2026-07-13. |
| `eclss_habitat` | 7 t | **C/D** | In family with ISS ECLSS-derived masses for a small crew; the 34% logistics figure (§3) shows the real cost is in *spares*, which we carry separately. |
| `consumables_cache` | 15 t | **C** | ~1,000-day crew margin at ISS consumption rates for a small crew is single-digit-to-tens of tonnes; order-of-magnitude sound. |
| `regolith_refinery` | 12 t / 200 kW | **D (process basis B)** | Mass/power notional. The *process* is real and NASA-demonstrated: molten regolith electrolysis reduces metal oxides (FeO, SiO₂, MgO, Al₂O₃) to oxygen + ferro-alloys for structural stock ([NTRS 20120003037](https://ntrs.nasa.gov/citations/20120003037), Joule-heated MRE reactor concepts for Moon *and Mars*); vacuum demo ran Dec 2024 at KSC with Lunar Resources ([NTRS 20250003220](https://ntrs.nasa.gov/citations/20250003220)). Products for our model: metal alloys (structure, parts feedstock), ceramics/glass, sinter feedstock — the Gen-1 closure tier (verified sequence, `docs/CITY_RAMP_RESEARCH.md` §2). Added 2026-07-14. |
| `polymer_chemical_plant` | 8 t / 120 kW | **D (process basis B)** | Mass/power notional. The chemistry piggybacks the ISRU chain: CO₂ → Sabatier + modified Fischer-Tropsch → ethylene → polyethylene, per NASA's in-situ HDPE study ([NTRS 20050157853](https://ntrs.nasa.gov/citations/20050157853)). Products: HDPE film/liners (greenhouse skins, inflatable structures), pipe, 3D-printer feedstock — and radiation shielding: hydrogen-rich PE beats aluminum ~10–20% per unit mass, and PE-regolith composite filament has been FFF-printed for exactly this ([Acta Astronautica 2021](https://www.sciencedirect.com/science/article/abs/pii/S0094576521005269)). The Gen-2/2.5 closure tier. Added 2026-07-14. |
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

## 8. Source verification log (2026-07-09)

Every load-bearing citation re-fetched and checked against the claim it supports.

| Source | Claim | Result |
|---|---|---|
| [NASA Glenn — FSP](https://www.nasa.gov/centers-and-facilities/glenn/nasas-fission-surface-power-project-energizes-lunar-exploration/) | 40 kWe, <6 t, decade unattended | ✅ verified verbatim |
| [ANS Nuclear Newswire](https://www.ans.org/news/2025-09-02/article-7336/nuclear-power-on-the-moon-what-were-watching/) | Duffy directive: ≥100 kWe, closed Brayton, Q1 FY2030, 15 t lander | ✅ verified, all four figures |
| [Wikipedia — Starship](https://en.wikipedia.org/wiki/SpaceX_Starship) | 100–150 t to LEO reusable | ✅ verified |
| [Wikipedia — Starship](https://en.wikipedia.org/wiki/SpaceX_Starship) | ~1,000 m³ payload volume | ⚠️ drift found → ✅ **RESOLVED 2026-07-09**: baseline re-anchored to 614 m³ (see §1); program window 2035-05 re-planned to 11 ships |
| [Wikipedia — Starship HLS](https://en.wikipedia.org/wiki/Starship_HLS) | tankers: GAO 16 / Musk 4–8 / SpaceX ~10 | ✅ verified (2024 SpaceX VP: "10-ish") |
| [NASA — MOXIE](https://www.nasa.gov/missions/mars-2020-perseverance/nasas-oxygen-generating-experiment-moxie-completes-mars-mission/) | 122 g O₂ total, 6–12 g/hr | ✅ verified (peak 12 g/hr) |
| [Space.com](https://www.space.com/spacex-starship-flight-passenger-cost-elon-musk.html) | Musk: ~$2M/launch, ~$900k propellant | ✅ verified |
| [NTRS 20210000437](https://ntrs.nasa.gov/citations/20210000437) | ECLSS = 34% of ISS supplied logistics mass | ✅ verified verbatim |
| [Everyday Astronaut — Raptor](https://everydayastronaut.com/raptor-engine/) | O/F mixture ~3.6–3.8 | ✅ verified (article: 3.7; our 3.6 in range, O₂ balance holds to ~3.99) |
| [NASA SmallSat SoA — Power](https://www.nasa.gov/smallsat-institute/sst-soa/power-subsystems/) | Li-ion cells 150–270 Wh/kg | ✅ verified (flown packs 58–250 → our 150 pack-level is conservative-realistic) |
| [World Nuclear](https://world-nuclear.org/information-library/energy-and-the-environment/hydrogen-production-and-uses) | electrolysis 50–55 kWh/kg H₂ | ✅ verified verbatim (CATF PDF unparseable — demoted to secondary) |
| [Wikipedia](https://en.wikipedia.org/wiki/Roll_Out_Solar_Array) + [eoPortal — ROSA](https://www.eoportal.org/satellite-missions/iss-rosa) | flown areal density ~2.95 kg/m² | ⚠️ weakened → ✅ **RESOLVED 2026-07-09**: baseline re-anchored to flown ~4.0 kg/m² (see §2); solar-vs-fission verdict re-checked, unchanged |
| [NASA BVAD TP-2015-218570 (TransHab)](https://ntrs.nasa.gov/citations/20150001624) + BEAM (flew 2016) | inflatable habitats stow ~4× smaller than deployed (TransHab 329.4 m³ deployed) | ⚠️ baseline habitat billed at deployed volume → ✅ **RESOLVED 2026-07-13**: all program windows now fly `habitat_inflatable` (75 m³ stowed → ~300 m³ deployed); 2035-05 returns to 10 ships (the 11th carried deployed-volume air), 2037-07 resets to 20 via the ≥2× growth rule; fleet 394 → 392. `habitat_module` (stowed=deployed) survives only in the frozen workbook fixtures |

| NASA LMLSTP (JSC 91-day chamber demo, 1997) + ISS ECLSS chamber testing (MSFC) + BEAM (2016) | closed-loop life support is only demonstrable inside a sealed volume; inflatables need long-duration endurance demonstration | ✅ adopted as doctrine **2026-07-13**: `life_support_closed` now requires a habitat with the 1,000-sol clock on both articles; `fleet.affinity_sets` packs each habitat+ECLSS pair on one hull (L2-LS-04 pins the integrated-demo requirement) |

## 8b. Validation backlog (replace first, in order)

1. ~~Real sparing analysis to replace the flat 35%~~ **Partially done 2026-07-09**: `informed_spares` scenario carries literature-based per-group fractions (ECLSS band is solid; non-ECLSS fractions remain constructed). Full buy-down needs real per-component Mars MTBFs. **D4 (2026-07-10)**: the Poisson sparing *method* is implemented (`spares.py`, `poisson_spares` scenario) — mathematically rigorous, but its failure rates are D-tier (no real Mars MTBFs exist), so `informed_spares` remains the defensible baseline. Method now awaits data, not engineering.
2. ~~ISRU pilot-plant mass from NASA literature~~ **Done 2026-07-10 (D2)**: NASA MAV ISRU study cross-checks our chain aggregate to within 7% (see §6); numbers validated, not replaced. Component-level splits remain the refinement target.
3. Starship cargo-variant actual payload capacity as flights accumulate (watch: does 100 t survive contact with reality?).
4. ~~FSP program updates~~ **Done 2026-07-09**: `fsp_2025` scenario encodes the Aug-2025 100 kWe directive.
5. Contingency fraction to AIAA-standard MGA by subsystem TRL (current 10% is likely low).
6. Demonstration-delay model for capability gates (delivered ≠ proven).
