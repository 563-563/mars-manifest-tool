# -*- coding: utf-8 -*-
"""Build the scrollytelling program page: essay left, sticky manifest panel
right that advances through the seven windows as you scroll, PLUS a live
what-if control drawer.

Data from the engine (dashboard_data.json). The browser carries a *calibrated
overlay*: at baseline knob values it reproduces the engine's exact numbers
(the source of truth), and each knob propagates through the same closed-form
relationships the Python engine uses (verified in tests/test_whatif_overlay.py).
Reset snaps back to the engine truth. Self-contained HTML (inline CSS/JS/data)."""
import json
from pathlib import Path

HERE = Path(__file__).parent
data = json.loads((HERE / "dashboard_data.json").read_text(encoding="utf-8"))
W = data["campaign"]["windows"]
CUM = data["campaign"]["cumulative"]
P = data["params"]

# authored narrative per window (title / motivation / proves / decision),
# written in 563's register: direct, sharp, teeth kept, aerospace-native.
NARR = {
 "2031-01": ("The Precursor",
   "Retire the “does anything even work” unknowns on the first landing — and shrink the water error bars before you bet a fuel factory on them.",
   "EDL · dust-storm-proof power · water confirmed · autonomy · comms. Half the program’s weighted risk, gone on the first touchdown.",
   "Drop steel penetrators and read the craters from orbit — water confirmed in ~30 sols instead of the ~200 you’d burn drilling. Cheapest high-leverage move on the manifest."),
 "2033-03": ("The Fuel Factory",
   "Build the one thing that makes a return credible: propellant, made from Martian air and ice.",
   "return_propellant_proven — a full return load banked by the next window, comfortably over the 1,400 t a crewed ship needs.",
   "Gated on 2031’s water survey: we don’t ship a factory toward water we haven’t found. And no extra redundancy — the pilot chain already on the ground backstops it, and a 30% margin eats any one lost hull."),
 "2035-05": ("The Base",
   "Double the fuel output, and stage everything a crew needs to survive — before they leave Earth.",
   "life_support_closed (the ECLSS testbed has now run its 1,000 sols) · radiation_managed. Every schedule-critical risk retired a full window early.",
   "Eleven ships, not ten — at the real 614 m³ bay this window is volume-bound, not mass-bound. Habitats are bulky, not heavy, and the honest bay number forces the honest ship count."),
 "2037-07": ("First Crew",
   "Only now do people go — to a base that is already powered, provisioned, and fueled.",
   "Twelve people land against thousands of tonnes of banked propellant and a landing record that started at a coin-flip and now clears 90%.",
   "The strict gate is the whole point: the ride home exists before anyone boards. Every requirement was closed a synod earlier, not promised."),
 "2039-09": ("The Village",
   "Grow past the point where the settlement could, in principle, keep itself alive if the ships stopped coming.",
   "112 residents — past Salotti’s 110-person survival floor. First local industry and agriculture (Gen-1/2 closure).",
   "The fleet at least doubles per synod — the one ramp rule that survived scrutiny. Every Musk cadence figure failed it and is cited only as aspiration."),
 "2041-11": ("The Town",
   "Close the industrial loop on the things the settlement burns through fastest.",
   "512 residents · Gen-3 closure — food, polymers, and structures now made on Mars. The import bill per resident falls off the ~500× cliff.",
   "Agriculture is the power monster: grow-lighting drags the fleet to 110 ships and the base past 17 MWe. Food is power, made visible."),
 "2044-01": ("The Settlement",
   "Reach the first formal milestone of a settlement with a future.",
   "1,112 adults — the NSS settlement threshold. ~18,500 t on the surface, 44× the mass of the ISS.",
   "The honest stop: a settlement, not autarky. Full independence is ~1,000,000 people; this is 1.85% of the way. We say so out loud rather than implying the city is around the corner."),
}

CAPTION = {
 "2031-01": "Half the program's weighted risk, gone on the first touchdown. And site water confirmed from orbit in ~30 sols — not the ~200 you'd burn drilling for it.",
 "2033-03": "The ride home stops being a promise. Propellant made from Martian air and ice, a full return load banked before anyone straps in.",
 "2035-05": "Life support run for 1,000 straight sols, radiation handled. Every risk that could move the schedule is retired a full window before crew.",
 "2037-07": "Twelve people land against banked propellant and a landing record that started at a coin-flip and now clears 90%.",
 "2039-09": "112 residents — past the line where, in principle, the settlement could keep itself alive if the ships stopped coming.",
 "2041-11": "512 residents. Food, polymers, and structures now made on Mars while the import bill falls off the ~500× cliff.",
 "2044-01": "1,112 adults — a real settlement, and still 1.85% of the way to a city that needs nobody. We say so out loud.",
}

CAP_LABELS = {
 "edl_proven": "EDL", "power_baseload": "Power", "water_supply": "Water",
 "water_confirmed": "Water✓", "precision_landing": "Nav", "comms_established": "Comms",
 "autonomy_proven": "Autonomy", "mobility": "Mobility", "infrastructure_ready": "Infra",
 "habitat_ready": "Habitat", "return_propellant_proven": "Propellant",
 "life_support_closed": "Life sup.", "radiation_managed": "Radiation",
 "survival_floor": "Survival", "settlement_established": "Settlement",
 "closure_gen_1": "Gen-1", "closure_gen_2": "Gen-2", "closure_gen_3": "Gen-3",
}
CAP_ORDER = ["edl_proven", "power_baseload", "water_confirmed", "water_supply",
             "precision_landing", "comms_established", "autonomy_proven", "mobility",
             "infrastructure_ready", "habitat_ready", "return_propellant_proven",
             "life_support_closed", "radiation_managed", "survival_floor",
             "closure_gen_1", "closure_gen_2", "closure_gen_3", "settlement_established"]

# weighted risk retired (from the lifecycle engine); gate-driven, held at
# baseline in the overlay (the exposed knobs don't move gate retirement order,
# except the propellant->crew coupling, which the overlay flags explicitly).
RISK_CUM = {"2031-01": 0.50, "2033-03": 0.75, "2035-05": 1.0, "2037-07": 1.0,
            "2039-09": 1.0, "2041-11": 1.0, "2044-01": 1.0}

# build the base per-window payload the overlay recomputes against
cum_caps = []
windows = []
for w in W:
    for c in w["new_caps"]:
        if c not in cum_caps:
            cum_caps.append(c)
    year = w["id"].split("-")[0]
    title, motiv, proves, decision = NARR[w["id"]]
    windows.append({
        "id": w["id"], "year": year, "synod": w["synod_index"], "title": title,
        "motivation": motiv, "proves": proves, "decision": decision,
        "caption": CAPTION.get(w["id"], ""),
        # base primitives (engine truth) the overlay perturbs / holds
        "shipsBase": w["ships"], "settlers": w["settlers"],
        "mass": round(w["mass"], 1), "kwe": w["kwe"],
        "nameplate": w["isru_nameplate_t"], "derate": w["derate"],
        "hardware_t": round(w["hardware_t"], 1), "closure": w["closure"],
        "risk": RISK_CUM[w["id"]],
        "caps": list(cum_caps), "new_caps": w["new_caps"],
    })

PAYLOAD = {
    "windows": windows,
    "params": P,
    "cap_labels": CAP_LABELS, "cap_order": CAP_ORDER,
    "base_cum": {"ships": CUM["ships"], "launches": CUM["total_launches"],
                 "mass": round(CUM["mass_delivered_t"]), "cost": round(CUM["launch_cost_musd"])},
}

CONSOLE = "https://claude.ai/code/artifact/1fa983e5-510f-401f-9820-bac33444ca7c"
WALK = "https://claude.ai/code/artifact/3182378f-acac-47a3-b381-7ce2a6d36a18"

# ---------------------------------------------------------------------------
HTML = r"""<title>The Mars Manifest — a program, told window by window</title>
<style>
:root{
  --paper:#faf8f3; --ink:#1c1a17; --muted:#6b6459; --faint:#a8a091;
  --rule:#ddd6c8; --panel:#f1ece2; --accent:#8f2020; --accent-2:#b5613a;
  --good:#4a6b46; --warn:#9a7414;
  --serif:"Iowan Old Style","Palatino Linotype","Book Antiqua",Georgia,"Times New Roman",serif;
  --mono:"SFMono-Regular","Cascadia Mono",Consolas,"Liberation Mono",monospace;
}
@media (prefers-color-scheme:dark){
  :root{ --paper:#16130f; --ink:#ece5d8; --muted:#a49b8b; --faint:#6b6357;
         --rule:#332e26; --panel:#1e1a15; --accent:#d16a4f; --accent-2:#c88a5a;
         --good:#8bb083; --warn:#c8a445; }
}
:root[data-theme="light"]{ --paper:#faf8f3; --ink:#1c1a17; --muted:#6b6459; --faint:#a8a091;
  --rule:#ddd6c8; --panel:#f1ece2; --accent:#8f2020; --accent-2:#b5613a; --good:#4a6b46; --warn:#9a7414; }
:root[data-theme="dark"]{ --paper:#16130f; --ink:#ece5d8; --muted:#a49b8b; --faint:#6b6357;
  --rule:#332e26; --panel:#1e1a15; --accent:#d16a4f; --accent-2:#c88a5a; --good:#8bb083; --warn:#c8a445; }

*{box-sizing:border-box}
html{background:var(--paper)}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);
  font-size:18px;line-height:1.62;-webkit-font-smoothing:antialiased}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--accent) 35%,transparent)}
a:hover{border-bottom-color:var(--accent)}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

/* header */
header{max-width:1240px;margin:0 auto;padding:26px 32px 0;
  display:flex;justify-content:space-between;align-items:baseline;gap:20px;flex-wrap:wrap}
.brand .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.22em;
  text-transform:uppercase;color:var(--accent)}
.brand h1{font-size:20px;font-weight:600;margin:2px 0 0;letter-spacing:.01em}
nav{font-family:var(--mono);font-size:12px;display:flex;gap:16px;color:var(--muted);align-items:center}
nav a{color:var(--muted);border:0}
nav a:hover{color:var(--accent)}
.navbtn{font-family:var(--mono);font-size:12px;background:none;border:1px solid var(--rule);
  border-radius:3px;color:var(--muted);padding:4px 10px;cursor:pointer}
.navbtn:hover{color:var(--accent);border-color:var(--accent)}
#modelBtn{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,transparent)}
#modelBtn.dirty{background:color-mix(in srgb,var(--accent) 12%,transparent)}

/* layout */
.wrap{max-width:1240px;margin:0 auto;padding:0 32px 120px;
  display:grid;grid-template-columns:minmax(0,1fr) minmax(0,540px);gap:56px;align-items:start}
main{padding-top:24px;min-width:0;order:1}
aside{position:sticky;top:0;height:100vh;display:flex;align-items:center;order:2}

/* essay */
.lede h2.title{font-size:clamp(40px,6vw,64px);line-height:1.02;margin:.1em 0 .2em;
  font-weight:600;letter-spacing:-.01em;text-wrap:balance}
.authors{font-size:15px;color:var(--muted);margin:0 0 26px}
.lede p{max-width:34em}
section{padding:64px 0;border-top:1px solid var(--rule);margin-top:64px}
section:first-of-type{border-top:0;margin-top:0;padding-top:8px}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--accent);margin:0 0 6px;display:flex;gap:12px;align-items:baseline}
.kicker .yr{color:var(--faint)}
h2.win{font-size:clamp(30px,4vw,42px);line-height:1.05;margin:0 0 20px;font-weight:600;text-wrap:balance}
h2.sec{font-size:30px;margin:0 0 18px;font-weight:600}
p{margin:0 0 18px;max-width:34em}
.field{margin:20px 0}
.field .lbl{font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);margin-bottom:5px}
.field.decision{border-left:3px solid var(--accent);padding:4px 0 4px 18px;background:
  linear-gradient(90deg,color-mix(in srgb,var(--accent) 6%,transparent),transparent 60%)}
.field.decision .lbl{color:var(--accent)}
blockquote{margin:26px 0;padding-left:20px;border-left:2px solid var(--rule);
  font-style:italic;color:var(--muted);max-width:32em}
.rules{list-style:none;padding:0;margin:0;counter-reset:r}
.rules li{position:relative;padding:0 0 20px 44px;counter-increment:r;max-width:34em}
.rules li::before{content:counter(r);position:absolute;left:0;top:-2px;font-family:var(--mono);
  font-size:13px;color:var(--accent);border:1px solid var(--accent);border-radius:50%;
  width:26px;height:26px;display:grid;place-items:center}
.rules b{font-weight:600}
.live{font-variant-numeric:tabular-nums;font-weight:600}
.live.off{color:var(--accent)}

/* sticky manifest panel */
.panel{width:100%;border:1px solid var(--rule);background:var(--panel);border-radius:4px;
  padding:18px 22px 20px;box-shadow:0 1px 0 var(--rule)}
.panel .ptop{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px}
.panel .yr{font-family:var(--mono);font-size:26px;color:var(--accent);letter-spacing:.02em}
.panel .obj{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);text-align:right;max-width:60%}
.srcbadge{font-family:var(--mono);font-size:9px;letter-spacing:.08em;text-transform:uppercase;
  display:inline-flex;align-items:center;gap:5px;padding:2px 7px;border-radius:99px;
  border:1px solid var(--good);color:var(--good);margin-bottom:8px;cursor:pointer}
.srcbadge::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--good)}
.srcbadge.off{border-color:var(--accent);color:var(--accent)}
.srcbadge.off::before{background:var(--accent)}
.glyph{font-size:13px;line-height:1.1;margin:2px 0 0;letter-spacing:1px;min-height:15px}
.glyph b{font-family:var(--mono);font-size:10px;font-weight:400;color:var(--muted);letter-spacing:.08em;margin-left:6px}
canvas#site{width:100%;height:200px;display:block;margin:8px 0 4px}
.cap-site{font-family:var(--mono);font-size:10px;color:var(--faint);text-align:center;margin-bottom:6px}
.legend{display:flex;flex-wrap:wrap;gap:5px 14px;justify-content:center;align-items:center;
  font-family:var(--mono);font-size:9px;letter-spacing:.03em;color:var(--faint);margin-bottom:14px}
.legend span{display:inline-flex;align-items:center;white-space:nowrap}
.legend i{display:inline-block;margin-right:5px}
.sw{width:10px;height:7px;border-radius:1px}
.sw.new{background:var(--accent)}
.sw.old{background:var(--ink);opacity:.38}
.fig{width:7px;height:10px;position:relative}
.fig::before{content:"";position:absolute;left:2.5px;top:3px;width:2px;height:7px;background:var(--accent)}
.fig::after{content:"";position:absolute;left:2px;top:0;width:3px;height:3px;border-radius:50%;background:var(--accent)}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;border-top:1px solid var(--rule);
  border-bottom:1px solid var(--rule);padding:14px 0;margin-bottom:14px}
.metric .v{font-family:var(--mono);font-size:21px;line-height:1;color:var(--ink);font-variant-numeric:tabular-nums}
.metric .v.moved{color:var(--accent)}
.metric .v small{font-size:11px;color:var(--muted)}
.metric .k{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted);margin-top:5px}
@media(prefers-reduced-motion:no-preference){.metric .v{transition:color .3s}}
.gates{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:12px}
.gate{font-family:var(--mono);font-size:9.5px;padding:2px 6px;border-radius:2px;
  border:1px solid var(--rule);color:var(--faint)}
.gate.on{border-color:var(--good);color:var(--good)}
.gate.fresh{border-color:var(--accent);color:var(--accent);background:color-mix(in srgb,var(--accent) 10%,transparent)}
.fleetbar{display:flex;flex-direction:column;gap:6px}
.fleetbar .row{display:flex;justify-content:space-between;font-family:var(--mono);
  font-size:10px;color:var(--muted)}
.track{height:8px;background:color-mix(in srgb,var(--ink) 8%,transparent);border-radius:2px;overflow:hidden}
.track .fill{height:100%;background:var(--accent)}
@media(prefers-reduced-motion:no-preference){.track .fill{transition:width .4s ease}}
.subline{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:8px;
  display:flex;justify-content:space-between}
.warnline{font-family:var(--mono);font-size:10px;color:var(--warn);margin-top:8px;line-height:1.4;display:none}
.warnline.show{display:block}
.enable{font-size:13.5px;line-height:1.5;color:var(--muted);font-family:var(--serif);
  border-top:1px solid var(--rule);margin-top:12px;padding-top:12px;font-style:italic}

/* control drawer */
#scrim{position:fixed;inset:0;background:rgba(0,0,0,.32);opacity:0;pointer-events:none;z-index:40}
#scrim.open{opacity:1;pointer-events:auto}
@media(prefers-reduced-motion:no-preference){#scrim{transition:opacity .25s}}
#drawer{position:fixed;top:0;right:0;height:100vh;width:min(420px,92vw);z-index:41;
  background:var(--paper);border-left:1px solid var(--rule);box-shadow:-8px 0 40px rgba(0,0,0,.18);
  transform:translateX(100%);display:flex;flex-direction:column}
#drawer.open{transform:translateX(0)}
@media(prefers-reduced-motion:no-preference){#drawer{transition:transform .28s cubic-bezier(.4,0,.2,1)}}
.dhead{padding:20px 22px 14px;border-bottom:1px solid var(--rule)}
.dhead .row{display:flex;justify-content:space-between;align-items:center}
.dhead h3{margin:0;font-size:17px;font-weight:600}
.dhead .close{font-family:var(--mono);font-size:18px;background:none;border:0;color:var(--muted);cursor:pointer;line-height:1}
.dhead p{font-size:12.5px;color:var(--muted);margin:8px 0 0;max-width:none;line-height:1.45}
.dbody{overflow-y:auto;padding:6px 22px 20px;flex:1}
.dstate{font-family:var(--mono);font-size:11px;padding:10px 12px;border-radius:4px;margin:14px 0 6px;
  border:1px solid var(--good);color:var(--good);background:color-mix(in srgb,var(--good) 8%,transparent)}
.dstate.off{border-color:var(--accent);color:var(--accent);background:color-mix(in srgb,var(--accent) 8%,transparent)}
.dstate b{font-weight:600}
.preset{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 4px}
.preset button{font-family:var(--mono);font-size:11px;padding:5px 10px;border-radius:99px;
  border:1px solid var(--rule);background:none;color:var(--muted);cursor:pointer}
.preset button:hover{border-color:var(--accent);color:var(--accent)}
.preset button.sel{border-color:var(--accent);color:var(--accent);background:color-mix(in srgb,var(--accent) 10%,transparent)}
.kgroup{margin-top:20px}
.kgroup > .gt{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--accent);border-bottom:1px solid var(--rule);padding-bottom:5px;margin-bottom:12px}
.knob{margin-bottom:14px}
.knob .kl{display:flex;justify-content:space-between;align-items:baseline;font-size:13px;margin-bottom:4px}
.knob .kl .kv{font-family:var(--mono);font-size:12px;color:var(--accent)}
.knob .kl .kv.base{color:var(--muted)}
.knob input[type=range]{width:100%;accent-color:var(--accent);margin:0}
.knob select{width:100%;font-family:var(--mono);font-size:12px;padding:5px 7px;
  background:var(--panel);color:var(--ink);border:1px solid var(--rule);border-radius:3px}
.wtab{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:11px;margin-top:4px}
.wtab th{text-align:right;font-weight:400;color:var(--muted);padding:3px 4px;font-size:10px}
.wtab th:first-child{text-align:left}
.wtab td{padding:2px 4px;text-align:right}
.wtab td:first-child{text-align:left;color:var(--muted)}
.wtab input{width:52px;font-family:var(--mono);font-size:11px;text-align:right;padding:2px 4px;
  background:var(--panel);color:var(--ink);border:1px solid var(--rule);border-radius:3px}
.wtab input:disabled{opacity:.3}
.wtab tr.dirty input{border-color:var(--accent);color:var(--accent)}
.dfoot{padding:14px 22px;border-top:1px solid var(--rule);display:flex;gap:10px;align-items:center}
.dfoot button{font-family:var(--mono);font-size:12px;padding:7px 12px;border-radius:3px;cursor:pointer}
#resetBtn{border:1px solid var(--accent);color:var(--accent);background:none}
#resetBtn:hover{background:color-mix(in srgb,var(--accent) 10%,transparent)}
#resetBtn:disabled{opacity:.35;cursor:default}
.dfoot .note{font-size:11px;color:var(--muted);font-family:var(--mono)}

/* mobile */
@media(max-width:900px){
  .wrap{grid-template-columns:1fr;gap:0}
  aside{order:1;position:sticky;top:0;height:auto;z-index:5;background:var(--paper);
    padding:10px 0;border-bottom:1px solid var(--rule);margin:0 -32px 24px;padding-left:32px;padding-right:32px}
  main{order:2}
  canvas#site{height:120px}
  .panel{border-radius:0;border:0;background:transparent;box-shadow:none;padding:0}
  .enable{display:none}
}
footer{max-width:1240px;margin:0 auto;padding:40px 32px 80px;border-top:1px solid var(--rule);
  font-family:var(--mono);font-size:12px;color:var(--muted)}
footer a{color:var(--muted)}
</style>

<header>
  <div class="brand">
    <div class="eyebrow">Mars Manifest Tool &middot; Program Plan</div>
    <h1>The Manifest</h1>
  </div>
  <nav>
    <a href="__CONSOLE__">Console</a>
    <a href="__WALK__">Walkthrough</a>
    <a href="https://github.com/563-563/mars-manifest-tool">Repo</a>
    <button class="navbtn" id="modelBtn" aria-label="Adjust the model">&#9881; Adjust the model</button>
    <button class="navbtn" id="themeBtn" aria-label="Toggle theme">theme</button>
  </nav>
</header>

<div class="wrap">
<main>
  <div class="lede" data-win="0">
    <h2 class="title">A settlement, earned<br>one proof at a time</h2>
    <p class="authors mono">Generated from examples/program_plan.yaml &middot; every figure traced to a source &middot; turn the knobs and watch it move</p>
    <p>Getting people to Mars is not one problem. It is roughly six hard ones stacked on
    each other, none fully solved &mdash; orbital refueling, landing 100 tonnes, making the
    return propellant, closing life support, radiation, and a crew with no abort. Money is
    <em>not</em> the tall pole. Power and water are.</p>
    <p>So this plan is not a delivery schedule. It is a <strong>sequence of proofs</strong>: each
    launch window exists to retire specific risk so the next one is allowed to commit. Scroll,
    and watch the base accrete beside the story &mdash; every ship, reactor, and resident is a real
    line in the manifest. Want to argue with an assumption? Hit
    <em>&#9881; Adjust the model</em> and the whole page recomputes from the engine's own math.</p>
  </div>

  <section id="rules" data-win="0">
    <div class="kicker">The operating discipline</div>
    <h2 class="sec">Three rules behind every decision</h2>
    <ol class="rules">
      <li><b>Demonstrated, not delivered.</b> The crew does not launch toward &ldquo;we sent a
      fuel plant.&rdquo; It launches toward 1,400 tonnes of propellant <em>in the tanks</em> and a
      life-support loop that has <em>run</em> for 1,000 sols. Gates retire on measured state.</li>
      <li><b>Every number carries a receipt.</b> Each input has a source and a confidence tier;
      when a source drifts, the baseline changes (this is why the ship bay is 614 m&sup3;, not the
      1,000 we started with). Claims that fail verification &mdash; including most of the famous
      cadence figures &mdash; are recorded as failing, not quietly used.</li>
      <li><b>No single ship loss costs a schedule-critical capability.</b> A 50/50 first landing is
      not something you bet the program on, so power, water, the propellant chain, comms, and
      autonomy are spread across hulls and pre-deployed a window early.</li>
    </ol>
    <blockquote>The dates start in 2031, not 2026: there is no 2026 flight in the verified record,
    and orbital refueling &mdash; the nearest gate &mdash; was still undemonstrated. First crew in
    2037 sits at the aggressive end of independent consensus.</blockquote>
  </section>

  __WINDOWS__

  <section id="close" data-win="6">
    <div class="kicker">Where it stops</div>
    <h2 class="sec">Honest about the edges</h2>
    <p>Cumulatively the plan lands <strong><span class="live" id="t-ships">394</span> ships</strong>
    over ~<span class="live" id="t-launch">6,700</span> launches, delivering
    ~<span class="live" id="t-mass">25,900</span> tonnes &mdash; about
    <strong>$<span class="live" id="t-near">600</span>B</strong> of launch at near-term prices,
    closer to <strong>$<span class="live" id="t-int">90</span>B</strong> on SpaceX's internal-cost
    basis. Cargo hardware dwarfs launch; development cost is larger still and kept in a separate
    ledger we chose not to model. <span class="mono" id="t-note" style="font-size:13px;color:var(--muted)"></span></p>
    <p>The serious disagreements are carried as scenarios, not smoothed away: whether the
    architecture is even feasible on this timeline (the peer-reviewed skeptic case flips orbital
    refill and cryo-chill to <em>not demonstrated</em>), how hard ISRU energy really is
    (0.85&ndash;1.7 MW at full scale &mdash; the live model puts it at
    <span class="live" id="t-mw">0.85</span> MW), what to do if the water disappoints (import
    methane, or import hydrogen), and how many people &ldquo;self-sustaining&rdquo; even means
    &mdash; 110, 1,000, or 1,000,000, three different questions.</p>
    <p>And what the tool deliberately does <em>not</em> model &mdash; Phobos depots, a development-cost
    ledger, mass-driven population growth &mdash; is written down too, so the omissions read as
    decisions. The one-line version: <strong>a plan that earns each step before taking it, shows its
    work for every number, and is candid about where it stops.</strong></p>
  </section>
</main>

<aside>
  <div class="panel" id="panel" aria-live="polite">
    <div class="ptop"><span class="yr" id="p-yr">2031</span><span class="obj" id="p-obj"></span></div>
    <span class="srcbadge" id="p-badge" role="button" tabindex="0" title="Open the model controls">source of truth</span>
    <div class="glyph" id="p-glyph"></div>
    <canvas id="site" width="960" height="400"></canvas>
    <div class="cap-site" id="p-site"></div>
    <div class="legend">
      <span><i class="sw new"></i>tonnage landed this window</span>
      <span><i class="sw old"></i>landed earlier</span>
      <span><i class="fig"></i>each figure = residents</span>
    </div>
    <div class="metrics" id="p-metrics"></div>
    <div class="gates" id="p-gates"></div>
    <div class="fleetbar">
      <div class="row"><span>cumulative fleet landed</span><span id="p-fleetval"></span></div>
      <div class="track"><div class="fill" id="p-fleetfill"></div></div>
      <div class="row"><span>program risk retired</span><span id="p-riskval"></span></div>
      <div class="track"><div class="fill" id="p-riskfill" style="background:var(--good)"></div></div>
    </div>
    <div class="subline"><span id="p-rel"></span><span id="p-prop"></span></div>
    <div class="warnline" id="p-warn"></div>
    <div class="enable" id="p-enable"></div>
  </div>
</aside>
</div>

<footer>
  Every number is produced by the Mars Manifest Tool, not typed by hand &middot;
  the what-if knobs recompute the engine's own math in your browser &middot;
  sources and confidence tiers in <a href="https://github.com/563-563/mars-manifest-tool/blob/main/PROVENANCE.md">PROVENANCE.md</a> &middot;
  the full essay in <a href="https://github.com/563-563/mars-manifest-tool/blob/main/docs/NARRATIVE.md">NARRATIVE.md</a>
</footer>

<div id="scrim"></div>
<div id="drawer" role="dialog" aria-label="Adjust the model" aria-modal="true">
  <div class="dhead">
    <div class="row"><h3>&#9881; Adjust the model</h3><button class="close" id="drawerClose" aria-label="Close">&times;</button></div>
    <p>Every knob recomputes the engine's own closed-form math in your browser. At the
    baseline they reproduce the Python engine <em>exactly</em> &mdash; the source of truth.
    Move one and the whole page becomes a live estimate until you reset.</p>
    <div class="dstate" id="dstate"></div>
    <div class="preset" id="presetRow"></div>
  </div>
  <div class="dbody" id="dbody"></div>
  <div class="dfoot">
    <button id="resetBtn">&#8635; Reset to source of truth</button>
    <span class="note" id="footNote"></span>
  </div>
</div>

<script>
const DATA = __DATA__;
const W = DATA.windows, P = DATA.params, BC = DATA.base_cum;
const fmt = (n,d=0)=>Number(n).toLocaleString("en-US",{maximumFractionDigits:d,minimumFractionDigits:0});
const KC = -Math.log(1-0.95);            // rule-of-three constant ~2.9957 (matches edl.py)

// ---- knob state ------------------------------------------------------------
function defaults(){
  return {
    tankers: P.tankers_per_ship,
    basis: P.active_launch_cost,
    commissioning: P.commissioning_factor,
    returnLoad: P.return_propellant_t,
    importMult: 1.0,
    spec: 1.0,
    ships: W.map(w=>w.shipsBase),
    settlers: W.map(w=>w.settlers),
  };
}
let K = defaults();

const PRESETS = {
  "Baseline":     {},                                             // engine truth
  "Optimistic":   {tankers:10, basis:"aspirational"},
  "SpaceX internal": {basis:"spacex_internal"},
  "Handmer ISRU": {spec:2.0},
  "Skeptic case": {tankers:16, basis:"near_term", commissioning:0.4, spec:2.0, importMult:1.3},
};

// ---- the calibrated overlay: engine math, in the browser -------------------
function rates(k){
  if(k.basis==="spacex_internal") return {cargo:P.spacex_internal.cargo, tanker:P.spacex_internal.tanker};
  return {cargo:P.cost_tiers[k.basis], tanker:P.cost_tiers[k.basis]};
}
function compute(k){
  const {cargo,tanker} = rates(k);
  let cumShips=0, cumLaunch=0, cumCost=0, cumMass=0, prevN=0, cumProp=0, cumPop=0;
  const out=[]; let gateIdx=null;
  for(let i=0;i<W.length;i++){
    const b=W[i];
    const ships=Math.max(0,Math.round(k.ships[i]));
    const settlers=Math.max(0,Math.round(k.settlers[i]));
    const launches=ships*(1+k.tankers);
    const cost=ships*cargo + ships*k.tankers*tanker;
    const popBefore=cumPop;
    cumShips+=ships; cumLaunch+=launches; cumCost+=cost; cumMass+=b.mass;
    // propellant commissioning ramp (matches campaign.py exactly)
    const nameplate=b.nameplate;
    const eff = prevN>0 ? prevN + k.commissioning*(nameplate-prevN) : k.commissioning*nameplate;
    const produced=eff*b.derate; cumProp+=produced; prevN=nameplate;
    cumPop+=settlers;
    const rel = cumShips>0 ? Math.max(0,1-KC/cumShips) : 0;
    const edlP = Math.min(P.edl.max, P.edl.base + P.edl.improve*b.synod);
    const rate = (P.import_decay[b.closure] ?? P.import_decay["none"]) * k.importMult;
    const importReq = popBefore*rate*P.years_per_synod;
    if(gateIdx===null && cumProp>=k.returnLoad) gateIdx=i;
    out.push({...b, ships, settlers, launches, cost, cumShips, cumCost, cumLaunch,
      prop:cumProp, produced, pop:cumPop, popBefore, rel, edlP, importReq});
  }
  // cost at the two editorial reference bases (independent of the basis knob)
  const costNear = cumLaunch*P.cost_tiers.near_term;
  const costInt  = cumShips*P.spacex_internal.cargo + (cumLaunch-cumShips)*P.spacex_internal.tanker;
  return {windows:out, cumShips, cumLaunch, cumCost, cumMass, gateIdx,
    costNear, costInt, fullKw:Math.round(P.full_scale_kw*k.spec)};
}
let MODEL = compute(K);

function baseline(){ const d=defaults();
  return d.tankers===K.tankers && d.basis===K.basis && d.commissioning===K.commissioning
    && d.returnLoad===K.returnLoad && d.importMult===K.importMult && d.spec===K.spec
    && K.ships.every((v,i)=>v===d.ships[i]) && K.settlers.every((v,i)=>v===d.settlers[i]);
}

// ---- sticky panel render ---------------------------------------------------
let active = 0;
function mv(v,k,moved){ return `<div class="metric"><div class="v${moved?' moved':''}">${v}</div><div class="k">${k}</div></div>`; }
function render(i){
  const w = MODEL.windows[i], b = W[i]; if(!w) return;
  const off = !baseline();
  document.getElementById("p-yr").textContent = w.year;
  document.getElementById("p-obj").textContent = w.title;
  const badge = document.getElementById("p-badge");
  badge.className = "srcbadge" + (off?" off":"");
  badge.textContent = off ? "live estimate" : "source of truth";
  const rk = "🚀".repeat(Math.min(w.ships, 12));
  document.getElementById("p-glyph").innerHTML = `${rk}<b>${fmt(w.ships)} ships launching this window</b>`;
  document.getElementById("p-metrics").innerHTML =
    mv(`${fmt(w.ships)}<small>/${fmt(w.cumShips)}</small>`, "ships (win/cum)", w.ships!==b.shipsBase)
    + mv(`${fmt(w.kwe)}<small>kWe</small>`, "power", false)
    + mv(w.prop>=1000?`${fmt(w.prop/1000,1)}<small>kt</small>`:`${fmt(w.prop)}<small>t</small>`, "propellant", K.commissioning!==P.commissioning_factor)
    + mv(w.pop>0?fmt(w.pop):"—", "residents", w.settlers!==b.settlers);
  const gz = DATA.cap_order.filter(c=>b.caps.includes(c)).map(c=>{
    const fresh = b.new_caps.includes(c);
    return `<span class="gate ${fresh?'fresh':'on'}">${DATA.cap_labels[c]||c}</span>`;
  }).join("");
  document.getElementById("p-gates").innerHTML = gz;
  const fleetPct = w.cumShips / MODEL.cumShips * 100;
  document.getElementById("p-fleetval").textContent = `${fmt(w.cumShips)} of ${fmt(MODEL.cumShips)}`;
  document.getElementById("p-fleetfill").style.width = fleetPct.toFixed(1)+"%";
  document.getElementById("p-riskval").textContent = `${fmt(b.risk*100)}%`;
  document.getElementById("p-riskfill").style.width = (b.risk*100)+"%";
  document.getElementById("p-rel").textContent = `EDL demo’d ${fmt(w.rel*100)}%`;
  document.getElementById("p-prop").textContent = w.importReq>0 ? `import due ${fmt(w.importReq)} t` : `landing p ${w.edlP.toFixed(2)}`;
  // propellant-gate coupling warning
  const warn = document.getElementById("p-warn");
  const gi = MODEL.gateIdx;
  if(gi===null){ warn.className="warnline show";
    warn.textContent = `⚠ propellant never reaches the ${fmt(K.returnLoad)} t return-load gate — return_propellant_proven never retires; no crew can be committed.`; }
  else if(gi>2){ warn.className="warnline show";
    warn.textContent = `⚠ return-load gate not banked until ${W[gi].year} — past the ${W[2].year} deadline; first crew (${W[3].year}) would slip.`; }
  else warn.className="warnline";
  document.getElementById("p-site").textContent =
    `${fmt(b.hardware_t)} t on the surface${w.pop>0? " · "+fmt(w.pop)+" residents":" · robotic"}`;
  document.getElementById("p-enable").textContent = b.caption;
  drawSite(i);
}

// ---- essay totals + drawer state -------------------------------------------
function refreshTotals(){
  const off = !baseline();
  const set=(id,val)=>{ const e=document.getElementById(id); e.textContent=val;
    e.classList.toggle("off", off); };
  set("t-ships", fmt(MODEL.cumShips));
  set("t-launch", fmt(Math.round(MODEL.cumLaunch/100)*100));
  set("t-mass", fmt(Math.round(MODEL.cumMass/100)*100));
  set("t-near", fmt(Math.round(MODEL.costNear/1000)));
  set("t-int", fmt(Math.round(MODEL.costInt/1000)));
  set("t-mw", (MODEL.fullKw/1000).toFixed(2));
  document.getElementById("t-note").textContent = off ? "— live estimate; reset for the engine baseline." : "";
}
function refreshDrawerState(){
  const off=!baseline();
  const ds=document.getElementById("dstate");
  ds.className="dstate"+(off?" off":"");
  const dCost=MODEL.cumCost, based=compute(defaults());
  if(off){
    const dc=Math.round((dCost-based.cumCost)/1000);
    const sign=dc>=0?"+":"−";
    ds.innerHTML = `<b>Live estimate.</b> Program launch (selected basis): $${fmt(Math.round(dCost/1000))}B `
      + `(${sign}$${fmt(Math.abs(dc))}B vs engine). Fleet ${fmt(MODEL.cumShips)} ships, `
      + `full-scale ISRU ${(MODEL.fullKw/1000).toFixed(2)} MW.`;
  } else {
    ds.innerHTML = `<b>Source of truth.</b> Every figure is the Python engine's exact output for `
      + `examples/program_plan.yaml.`;
  }
  document.getElementById("modelBtn").classList.toggle("dirty", off);
  document.getElementById("resetBtn").disabled = !off;
  // preset selection highlight
  document.querySelectorAll("#presetRow button").forEach(btn=>{
    btn.classList.toggle("sel", btn.dataset.name===currentPreset());
  });
  // per-window row dirty state
  document.querySelectorAll(".wtab tr[data-i]").forEach(tr=>{
    const i=+tr.dataset.i;
    tr.classList.toggle("dirty", K.ships[i]!==W[i].shipsBase || K.settlers[i]!==W[i].settlers);
  });
}
function currentPreset(){
  for(const [name,ov] of Object.entries(PRESETS)){
    const t={...defaults(),...ov};
    if(t.tankers===K.tankers&&t.basis===K.basis&&t.commissioning===K.commissioning
      &&t.returnLoad===K.returnLoad&&t.importMult===K.importMult&&t.spec===K.spec
      &&K.ships.every((v,i)=>v===t.ships[i])&&K.settlers.every((v,i)=>v===t.settlers[i]))
      return name;
  }
  return null;
}
function recompute(){ MODEL=compute(K); render(active); refreshTotals(); refreshDrawerState(); syncControls(); }

// ---- canvas: the base footprint accreting ----------------------------------
const cv = document.getElementById("site"), cx = cv.getContext("2d");
function css(v){ return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }
function drawSite(i){
  const w = MODEL.windows[i], b = W[i];
  const dpr = Math.min(window.devicePixelRatio||1, 2);
  const rect = cv.getBoundingClientRect();
  cv.width = rect.width*dpr; cv.height = rect.height*dpr;
  cx.setTransform(dpr,0,0,dpr,0,0);
  const Wd = rect.width, Ht = rect.height;
  cx.clearRect(0,0,Wd,Ht);
  const ink = css("--ink"), accent = css("--accent");
  const horizon = Ht*0.62;
  cx.strokeStyle = css("--rule"); cx.lineWidth=1;
  cx.beginPath(); cx.moveTo(0,horizon); cx.lineTo(Wd,horizon); cx.stroke();
  cx.fillStyle = accent;
  for(let gy=6; gy<horizon-6; gy+=9){
    for(let gx=6; gx<Wd-6; gx+=9){
      cx.globalAlpha = 0.06*(1 - gy/horizon); cx.beginPath(); cx.arc(gx,gy,1,0,7); cx.fill();
    }
  }
  cx.globalAlpha = 1;
  const cumHw = b.hardware_t, prevHw = i>0? W[i-1].hardware_t : 0;
  const cellsFor = h => Math.max(1, Math.round(Math.sqrt(h)* 1.7));
  const total = cellsFor(cumHw), prior = i>0? cellsFor(prevHw):0;
  const cols = Math.ceil(Math.sqrt(total*2.2));
  const cw = Math.min(15, (Wd-40)/cols), gap = cw*0.32, unit = cw+gap;
  const rows = Math.ceil(total/cols);
  const x0 = (Wd - (cols*unit-gap))/2;
  const y0 = horizon - rows*unit + unit*0.4;
  for(let n=0;n<total;n++){
    const r = Math.floor(n/cols), c = n%cols;
    const x = x0 + c*unit, y = y0 + r*unit;
    const fresh = n>=prior;
    cx.fillStyle = fresh? accent : rgba(ink,0.20);
    cx.globalAlpha = fresh? 0.95 : 0.5;
    roundRect(cx,x,y,cw,cw*0.72,1.5); cx.fill();
  }
  cx.globalAlpha=1;
  if(w.pop>0){
    const figs = Math.min(60, Math.round(w.pop/ (w.pop>200?20:2)));
    cx.strokeStyle = accent; cx.lineWidth=1.4;
    for(let k=0;k<figs;k++){
      const fx = 14 + (k%30)*((Wd-28)/30);
      const fy = horizon + 10 + Math.floor(k/30)*11;
      cx.beginPath(); cx.moveTo(fx,fy); cx.lineTo(fx,fy+6); cx.stroke();
      cx.beginPath(); cx.arc(fx,fy-2.2,1.5,0,7); cx.stroke();
    }
  }
}
function roundRect(c,x,y,w,h,r){c.beginPath();c.moveTo(x+r,y);c.arcTo(x+w,y,x+w,y+h,r);
  c.arcTo(x+w,y+h,x,y+h,r);c.arcTo(x,y+h,x,y,r);c.arcTo(x,y,x+w,y,r);c.closePath();}
function rgba(hex,a){const c=hexToRgb(hex);return `rgba(${c.r},${c.g},${c.b},${a})`;}
function hexToRgb(h){h=h.replace('#','');if(h.length===3)h=h.split('').map(x=>x+x).join('');
  return {r:parseInt(h.slice(0,2),16),g:parseInt(h.slice(2,4),16),b:parseInt(h.slice(4,6),16)};}

// ---- scrollytelling: sections drive the panel (geometry-based, sync both ways)
const sections = [...document.querySelectorAll("[data-win]")];
const visible = new Set();
function pickActive(){
  if(!visible.size) return;
  const mid = window.innerHeight/2; let best=null, bestD=Infinity;
  visible.forEach(el=>{ const r=el.getBoundingClientRect();
    const d=Math.abs((r.top+r.bottom)/2 - mid); if(d<bestD){bestD=d;best=+el.dataset.win;} });
  if(best!==null && best!==active){ active=best; render(active); }
}
const io = new IntersectionObserver((entries)=>{
  entries.forEach(e=> e.isIntersecting ? visible.add(e.target) : visible.delete(e.target));
  pickActive();
}, {rootMargin:"-40% 0px -40% 0px", threshold:0});
sections.forEach(s=>io.observe(s));

// ---- control drawer --------------------------------------------------------
const SLIDERS = [
  {group:"Launch & fleet", items:[
    {k:"tankers", label:"Tankers per ship", min:6, max:20, step:1, base:P.tankers_per_ship,
     fmt:v=>fmt(v)},
    {k:"basis", label:"Launch-cost basis", type:"select", base:P.active_launch_cost,
     options:[["near_term","Near-term — $90M/launch"],["operational","Operational — $30M"],
              ["aspirational","Aspirational — $2M"],["spacex_internal","SpaceX internal — $30M cargo / $12M tanker"]]},
  ]},
  {group:"ISRU & propellant", items:[
    {k:"commissioning", label:"ISRU commissioning ramp (1st synod)", min:0.2, max:1, step:0.05,
     base:P.commissioning_factor, fmt:v=>Math.round(v*100)+"%"},
    {k:"returnLoad", label:"Return-load requirement", min:800, max:2000, step:50,
     base:P.return_propellant_t, fmt:v=>fmt(v)+" t"},
    {k:"spec", label:"ISRU energy × baseline", min:0.5, max:2.5, step:0.1, base:1.0,
     fmt:v=>v.toFixed(1)+"× ("+(P.full_scale_kw*v/1000).toFixed(2)+" MW)"},
  ]},
  {group:"Population & imports", items:[
    {k:"importMult", label:"Per-capita import × baseline", min:0.2, max:2, step:0.1, base:1.0,
     fmt:v=>v.toFixed(1)+"×"},
  ]},
];
function buildDrawer(){
  // presets
  const pr=document.getElementById("presetRow");
  pr.innerHTML = Object.keys(PRESETS).map(n=>`<button data-name="${n}">${n}</button>`).join("");
  pr.querySelectorAll("button").forEach(btn=>btn.onclick=()=>{
    K={...defaults(),...PRESETS[btn.dataset.name]}; recompute();
  });
  // sliders / selects
  const body=document.getElementById("dbody");
  let html="";
  for(const g of SLIDERS){
    html+=`<div class="kgroup"><div class="gt">${g.group}</div>`;
    for(const it of g.items){
      if(it.type==="select"){
        html+=`<div class="knob"><div class="kl"><label for="c-${it.k}">${it.label}</label></div>`
          +`<select id="c-${it.k}" data-k="${it.k}">`
          +it.options.map(o=>`<option value="${o[0]}">${o[1]}</option>`).join("")+`</select></div>`;
      } else {
        html+=`<div class="knob"><div class="kl"><label for="c-${it.k}">${it.label}</label>`
          +`<span class="kv" id="v-${it.k}"></span></div>`
          +`<input type="range" id="c-${it.k}" data-k="${it.k}" min="${it.min}" max="${it.max}" step="${it.step}"></div>`;
      }
    }
    html+=`</div>`;
  }
  // per-window ships & settlers
  html+=`<div class="kgroup"><div class="gt">Per-window fleet &amp; crew</div>`
    +`<table class="wtab"><tr><th>Window</th><th>Ships</th><th>Settlers</th></tr>`;
  for(let i=0;i<W.length;i++){
    const w=W[i]; const crew=w.settlers>0 || w.synod>=3;
    html+=`<tr data-i="${i}"><td>${w.year} ${w.title}</td>`
      +`<td><input type="number" min="0" data-ship="${i}" value="${w.shipsBase}"></td>`
      +`<td><input type="number" min="0" data-settler="${i}" value="${w.settlers}" ${crew?"":"disabled"}></td></tr>`;
  }
  html+=`</table></div>`;
  body.innerHTML=html;
  // wire sliders
  body.querySelectorAll('input[type=range]').forEach(inp=>{
    inp.oninput=()=>{ K[inp.dataset.k]=parseFloat(inp.value); recompute(); };
  });
  body.querySelectorAll('select').forEach(sel=>{
    sel.onchange=()=>{ K[sel.dataset.k]=sel.value; recompute(); };
  });
  body.querySelectorAll('input[data-ship]').forEach(inp=>{
    inp.onchange=()=>{ K.ships[+inp.dataset.ship]=Math.max(0,Math.round(+inp.value||0)); recompute(); };
  });
  body.querySelectorAll('input[data-settler]').forEach(inp=>{
    inp.onchange=()=>{ K.settlers[+inp.dataset.settler]=Math.max(0,Math.round(+inp.value||0)); recompute(); };
  });
}
function syncControls(){
  for(const g of SLIDERS) for(const it of g.items){
    const el=document.getElementById("c-"+it.k); if(!el) continue;
    if(it.type==="select"){ el.value=K[it.k]; }
    else { el.value=K[it.k];
      const vv=document.getElementById("v-"+it.k);
      vv.textContent=it.fmt(K[it.k]);
      vv.classList.toggle("base", K[it.k]===it.base);
    }
  }
  document.querySelectorAll('input[data-ship]').forEach(inp=>{ inp.value=K.ships[+inp.dataset.ship]; });
  document.querySelectorAll('input[data-settler]').forEach(inp=>{ inp.value=K.settlers[+inp.dataset.settler]; });
}
const drawer=document.getElementById("drawer"), scrim=document.getElementById("scrim");
function openDrawer(){ drawer.classList.add("open"); scrim.classList.add("open"); }
function closeDrawer(){ drawer.classList.remove("open"); scrim.classList.remove("open"); }
document.getElementById("modelBtn").onclick=openDrawer;
document.getElementById("drawerClose").onclick=closeDrawer;
scrim.onclick=closeDrawer;
document.getElementById("p-badge").onclick=openDrawer;
document.getElementById("p-badge").onkeydown=(e)=>{ if(e.key==="Enter"||e.key===" ")openDrawer(); };
document.getElementById("resetBtn").onclick=()=>{ K=defaults(); recompute(); };
document.addEventListener("keydown",(e)=>{ if(e.key==="Escape")closeDrawer(); });

// theme toggle
const root=document.documentElement, tb=document.getElementById("themeBtn");
tb.onclick=()=>{ const cur=root.getAttribute("data-theme")
  || (matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light");
  root.setAttribute("data-theme", cur==="dark"?"light":"dark"); drawSite(active); };
matchMedia("(prefers-color-scheme:dark)").addEventListener?.("change",()=>drawSite(active));

// boot
buildDrawer();
render(0); refreshTotals(); refreshDrawerState(); syncControls();
window.addEventListener("resize", ()=>drawSite(active));
</script>
"""

# build the seven window <section>s
sections = []
for i, w in enumerate(windows):
    sec = f'''  <section id="{w['id']}" data-win="{i}">
    <div class="kicker">{w['year']}<span class="yr">Window {i} &middot; {w['shipsBase']} ships</span></div>
    <h2 class="win">{w['title']}</h2>
    <div class="field"><div class="lbl">Why</div><p>{w['motivation']}</p></div>
    <div class="field"><div class="lbl">What it proves</div><p>{w['proves']}</p></div>
    <div class="field decision"><div class="lbl">The decision</div><p>{w['decision']}</p></div>
  </section>'''
    sections.append(sec)

html = (HTML
        .replace("__DATA__", json.dumps(PAYLOAD))
        .replace("__WINDOWS__", "\n".join(sections))
        .replace("__CONSOLE__", CONSOLE)
        .replace("__WALK__", WALK))
out = HERE / "mars_manifest_story.html"
out.write_text(html, encoding="utf-8")
print("wrote", out, len(html), "bytes")
