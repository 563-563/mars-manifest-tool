# Considered — the ideas we looked at and did NOT model (yet)

*A register so collaborators know omissions are decisions, not blind spots.
Statuses: **deferred** (on the task list), **out of scope** (real, but not
this tool's job yet), **rejected** (failed verification or graded
low-rigor — do not resurrect without new evidence), **simplified** (modeled,
but with a stated shortcut).*

| Idea | Source | Status | Why / where recorded |
|---|---|---|---|
| Phobos/Deimos propellant depots (refuel in Mars orbit, ~½ the surface-lift propellant) | Handmer Feb-2025 comment thread | **out of scope** | Needs a crewed-return / orbital-logistics module the tool doesn't have; revisit when return flights are modeled. COMPARATIVES addendum. |
| DSN / optical-comms bandwidth limits (Psyche-style laser links) | same thread | **out of scope** | Ground-segment capacity, not a mass/schedule quantity in this model. |
| SpaceX in-housing matrix (who builds what by 2028) | Handmer Feb-2025 | **out of scope** | Organizational forecast, not a mass/schedule input. Useful context only. |
| One-way / no-return crew doctrine | HANDOFF §10 (original open question) | **deferred, no task** | Would remove the propellant-banked crew gate and harden life-support requirements instead; a doctrine fork we've deliberately not taken. |
| Development (non-recurring) cost ledger | HANDOFF §10 | **deferred, no task** | Recurring launch+cargo cost is modeled; R&D ledger (Starship $15B+, fission, ISRU) still excluded on purpose. |
| Musk cadence/timeline figures (5→20→100→500 ships; 25–30 yr self-sufficiency; 10–15 windows; late-2026 first flight; ~5-ship first batch as a *plan*) | AIAA/Teslarati/Space.com | **rejected** | Every one failed 3-vote adversarial verification or was superseded by the Feb-2026 Moon pivot. CITY_RAMP_RESEARCH §4; raw votes in `_city_ramp_raw_findings.json`. Citable as aspiration only. |
| "600 kW vs 25 kW = demo-to-production ISRU power gap" framing | Aerospace America | **rejected** | Numbers real, framing wrong: it's linear propellant-mass scaling between two vehicle sizes, killed twice by independent skeptic panels. |
| arxiv 2112.06145 & 1904.01389 (1000-person colony papers) as anchors | deep-research sweep | **rejected** | Direct reading: qualitative / low-rigor; no extractable budgets. The million-person sibling (2112.06155) survived at Tier C. |
| 500–1,000 / 5,000–10,000 population thresholds | newspaceeconomy blog | **rejected** | Source auto-graded unreliable; the milestones we carry (110 / 1,000 / 1M) trace to Salotti, NSS, Handmer instead. |
| NSS's Mars-born-generation criterion for `settlement_established` | NSS roadmap | **simplified** | We gate on population ≥1,000 only; no birth/demographics model exists. Noted in `city_ramp_seed.yaml`. |
| Orbital assets as a distinct mission type (deploy to orbit, never land) | task A4 design | **simplified** | Penetrators/orbital sats are modeled as manifest mass and appear in "surface" inventory; a true `orbital:` mission type is future work if orbital logistics grow. |
| Ratio-based industrial closure (plant capacity per capita, not presence) | task A3 design | **simplified** | Closure stages unlock on component presence + population thresholds; real closure would scale plant *count* with population. Import-decay stages are interpolated between Handmer's two verified endpoints (10 t → 20 kg). |
| Local-construction mass offsets (NSS: build habitats from regolith after Gen-3 closure) | NSS / closure ladder | **deferred, no task** | City windows still import all habitat mass; closing structures locally would cut the largest import line. Natural B-phase follow-up. |
| Population departures / return flights reducing headcount | A1 design | **simplified** | Population only accumulates; crew rotation and returnees aren't modeled. |
| LH2 boil-off physics for the h2_import mode | TheRadicalModerate analysis | **deferred → task C6** | The mode's weak point (surface LH2 cryocooling) will carry a hard D-tier flag when built. |
| Two-ship-loss / probabilistic EDL, within-window arrival sequencing | comment threads + our own flags | **deferred → task C2** | |
| Earth-side readiness gates (orbit, reuse, refill, chill) | Handmer Feb-2025 | **deferred → task C1** | Requirements tree currently starts at Mars arrival. |
| Semi-Markov component sparing; AIAA MGA contingency; NASA ISRU plant masses | PROVENANCE backlog | **deferred → tasks D2–D4** | |
| `habitat_module` stowed volume = deployed volume (300 m³) | found during B3 build | **simplified, worked around** | The workbook-era component carries deployed volume as its stowed figure — harmless at 4 units, needs ~240 ships at city scale. City windows use `habitat_inflatable` (75 m³ stowed → ~300 m³ deployed, TransHab/B330 ~4× compression). The original component is frozen into the workbook-port fixtures and cannot be re-anchored without breaking them. |
| Per-ship packing checks raw volume ≤ bay, while the batch check applies packing efficiency | found during B3 build | **simplified** | Two volume standards coexist: the packer admits raw ≤ 614 m³/ship; the budget batch check divides by 0.65 first. The stricter batch check is what surfaces warnings. Unifying them is future work. |

Add to this file whenever something is weighed and set aside — an entry here
is cheaper than a collaborator re-litigating it from scratch.
