# Requirements buy-off matrix — program_plan

Status vs plan: CLOSED (on plan) / EARLY / LATE / OPEN; recurring requirements: PASS / FAIL across all windows.

**CLOSED 25 · EARLY 2 · PASS 4**

## Buy-off by flight window
- **2031-01**: L1-TRANS-01, L1-TRANS-02, L1-TRANS-03, L1-TRANS-04, L1-EDL-01, L2-EDL-02, L1-NAV-01, L1-PWR-01, L2-PWR-02, L1-H2O-01, L2-PROP-02, L2-LS-02, L1-HAB-01, L1-COM-01, L1-AUT-01, L1-MOB-01, L1-INF-01
- **2033-03**: L2-PWR-04, L1-PROP-01, L2-PROP-03, L2-PROP-04, L2-PROP-05
- **2035-05**: L1-LS-01, L2-LS-03, L2-HAB-02, L1-RAD-01
- **2037-07**: —
- **2039-09**: —
- **2041-11**: —
- **2044-01**: —

## Full matrix
| Req | Statement | Verify | Planned | Actual | Status |
|---|---|---|---|---|---|
| L0-MSN-01 | The first crew shall arrive at a powered, provisioned, and fueled Mars base with a demonstrated return path, and no single cargo-ship loss shall defeat the campaign. | Rollup | rollup | 2035-05 | CLOSED |
| &nbsp;&nbsp;L1-TRANS-01 | Starship shall reach orbit and be recovered. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-TRANS-02 | Both Starship stages shall be reused (routine refly). | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-TRANS-03 | Orbital propellant transfer (refill) shall be demonstrated. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-TRANS-04 | Long-duration cryogenic propellant storage (active chill) shall be demonstrated. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-EDL-01 | The program shall demonstrate survivable EDL of a 100 t-class cargo ship on Mars. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-EDL-02 | At least 5 successful cargo landings shall be accumulated before crew commits. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-NAV-01 | Follow-on ships shall land within meters of the base (precision landing aids operating). | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-PWR-01 | The base shall have continuous, dust-storm-tolerant baseload power. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-PWR-02 | Installed generation shall reach 500 kWe or more in the first window. | Test | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-PWR-03 | Installed generation shall cover the delivered average load at every window. | Analysis | every window | — | PASS |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-PWR-04 | Installed generation shall reach 1.5 MWe or more before crew arrival. | Test | 2035-05 | 2033-03 | EARLY |
| &nbsp;&nbsp;L1-H2O-01 | The program shall confirm and exploit accessible water ice (prospect, excavate, process). | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-PROP-01 | The program shall produce and store a full crewed-return propellant load (1,400 t methalox) before crew commits. | Demonstration | 2033-03 | 2033-03 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-PROP-02 | An integrated pilot chain shall run at 40 kg/hr propellant-equivalent or more in the first window. | Test | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-PROP-03 | Chain nameplate rate shall reach one return load per synod (>= 112 kg/hr). | Test | 2033-03 | 2033-03 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-PROP-04 | Cumulative propellant produced and stored shall reach 1,400 t before crew departure. | Test | 2033-03 | 2033-03 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-PROP-05 | At least two independent Sabatier chains shall exist on the surface before crew. | Inspection | 2035-05 | 2033-03 | EARLY |
| &nbsp;&nbsp;L1-LS-01 | A near-closed life-support loop shall be demonstrated on Mars for 1,000 sols before crew. | Demonstration | 2035-05 | 2035-05 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-LS-02 | The ECLSS demonstration article shall be landed in the first window (demo clock). | Inspection | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-LS-03 | Pre-landed consumable caches of 90 t or more shall be on the surface before crew. | Inspection | 2035-05 | 2035-05 | CLOSED |
| &nbsp;&nbsp;L1-HAB-01 | Pressurized habitat volume beyond the landed ships shall be ready before crew. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-HAB-02 | At least 5 habitat modules shall be on the surface before crew arrival. | Inspection | 2035-05 | 2035-05 | CLOSED |
| &nbsp;&nbsp;L1-RAD-01 | A storm shelter and radiation protection shall be in place before crew. | Inspection | 2035-05 | 2035-05 | CLOSED |
| &nbsp;&nbsp;L1-COM-01 | A surface-to-Earth communications link shall operate from the first window. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-AUT-01 | The base shall operate autonomously under a 4-22 minute one-way light delay. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-MOB-01 | Surface mobility for cargo and instruments shall be operational from the first window. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-INF-01 | Cargo offload, power distribution, and site logistics shall be operational from the first window. | Demonstration | 2031-01 | 2031-01 | CLOSED |
| &nbsp;&nbsp;L1-LOG-01 | Every flight window's manifest shall fit within its declared fleet's mass capacity. | Analysis | every window | — | PASS |
| &nbsp;&nbsp;&nbsp;&nbsp;L2-LOG-03 | Every flight window shall retain at least 10% fleet mass margin for growth and late additions. | Analysis | every window | — | PASS |
| &nbsp;&nbsp;L1-LOG-02 | No single cargo-ship loss in any window shall cost a schedule-critical capability (power, water, propellant chain, comms, autonomy, infrastructure, mobility, precision landing), accounting for hardware already on the surface. | Analysis | every window | — | PASS |
