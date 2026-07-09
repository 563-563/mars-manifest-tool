"""CLI entrypoint (HANDOFF.md §8).

    mars catalog list [--group G]
    mars catalog show <id>
    mars budget <mission.yaml> [--scenario S] [--power solar|fission] [--format table|md|xlsx]
    mars pack   <mission.yaml> [--tankers N] [--launch-cost TIER]
    mars plan   <campaign.yaml> [--scenario S] [--format table|md|xlsx]
    mars compare <A> <B> [--campaign C.yaml | --mission M.yaml]
    mars report <campaign.yaml> --format xlsx [--out FILE]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from . import report as rpt
from .budgets import BudgetEngine
from .campaign import CampaignPlanner
from .catalog import Catalog
from .models import Campaign, Mission, Window
from .packing import PackingEngine
from .scenarios import ScenarioManager, compare


def _find_data_dir(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "data" / "component_catalog_seed.csv").exists():
            return candidate / "data"
    # fall back to the repo the package was installed from (editable install)
    return Path(__file__).resolve().parents[1] / "data"


def load_mission(path: str | Path, catalog: Catalog) -> Mission:
    with Path(path).open(encoding="utf-8") as fh:
        return Mission.from_dict(yaml.safe_load(fh), catalog)


def load_campaign(path: str | Path, catalog: Catalog) -> Campaign:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    windows = []
    for wdoc in doc.get("windows", []):
        missions = []
        for mdoc in wdoc.get("missions", []):
            if "file" in mdoc:
                missions.append(load_mission(path.parent / mdoc["file"], catalog))
            else:
                missions.append(Mission.from_dict(mdoc, catalog))
        for m in missions:
            m.window_id = m.window_id or str(wdoc["id"])
        windows.append(Window(
            id=str(wdoc["id"]),
            synod_index=int(wdoc.get("synod_index", len(windows))),
            transit_days=int(wdoc.get("transit_days", 210)),
            objective=wdoc.get("objective", ""),
            notes=wdoc.get("notes", ""),
            missions=missions,
        ))
    return Campaign(id=doc.get("id", path.stem), windows=windows)


def _table(headers: list[str], rows: list[list]) -> str:
    def fmt(v):
        return f"{v:,.2f}" if isinstance(v, float) else str(v)
    cells = [[fmt(v) for v in row] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in cells)) if cells else len(h)
              for i, h in enumerate(headers)]
    line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    sep = "  ".join("-" * w for w in widths)
    body = ["  ".join(c.ljust(w) for c, w in zip(row, widths)) for row in cells]
    return "\n".join([line, sep, *body])


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="mars", description="Mars Manifest Tool")
    parser.add_argument("--data-dir", help="Directory containing seed catalog + assumptions")
    sub = parser.add_subparsers(dest="command", required=True)

    p_cat = sub.add_parser("catalog", help="Query the component catalog")
    cat_sub = p_cat.add_subparsers(dest="cat_command", required=True)
    p_list = cat_sub.add_parser("list")
    p_list.add_argument("--group")
    p_show = cat_sub.add_parser("show")
    p_show.add_argument("id")

    def add_common(p):
        p.add_argument("--scenario", default="baseline")
        p.add_argument("--format", choices=["table", "md", "xlsx"], default="table")
        p.add_argument("--out", help="Output file (md/xlsx)")

    p_budget = sub.add_parser("budget", help="Compute budgets for a mission")
    p_budget.add_argument("mission")
    p_budget.add_argument("--power", choices=["solar", "fission"])
    add_common(p_budget)

    p_pack = sub.add_parser("pack", help="Pack a mission into ships + launch math")
    p_pack.add_argument("mission")
    p_pack.add_argument("--tankers", type=int)
    p_pack.add_argument("--launch-cost", dest="launch_cost",
                        choices=["aspirational", "operational", "near_term"])
    p_pack.add_argument("--scenario", default="baseline")
    p_pack.add_argument("--policy", choices=["explicit", "balanced"])
    p_pack.add_argument("--spares", action="store_true",
                        help="Pack the spares overhead as explicit per-group cargo")

    p_isru = sub.add_parser("isru", help="ISRU chain rates, energy budget, bottleneck")
    p_isru.add_argument("mission")
    p_isru.add_argument("--scenario", default="baseline")
    p_isru.add_argument("--design", nargs="?", const=-1.0, type=float, metavar="TONNES",
                        help="Also print a rate-matched chain design for a target of "
                             "TONNES per synod (default: one return load)")

    p_plan = sub.add_parser("plan", help="Plan a campaign across windows")
    p_plan.add_argument("campaign")
    add_common(p_plan)

    p_life = sub.add_parser("lifecycle", help="Risk buy-down + idle-hardware review of a campaign")
    p_life.add_argument("campaign")
    p_life.add_argument("--scenario", default="baseline")

    p_req = sub.add_parser("requirements", help="Requirements buy-off matrix for a campaign")
    p_req.add_argument("campaign")
    p_req.add_argument("--scenario", default="baseline")
    p_req.add_argument("--out", help="Write markdown to a file")

    p_cmp = sub.add_parser("compare", help="Compare two scenarios")
    p_cmp.add_argument("scenario_a")
    p_cmp.add_argument("scenario_b")
    p_cmp.add_argument("--campaign")
    p_cmp.add_argument("--mission")

    p_rep = sub.add_parser("report", help="Full campaign report workbook")
    p_rep.add_argument("campaign")
    p_rep.add_argument("--scenario", default="baseline")
    p_rep.add_argument("--format", choices=["xlsx", "md"], default="xlsx")
    p_rep.add_argument("--out")

    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir) if args.data_dir else _find_data_dir(Path.cwd())
    catalog = Catalog.load(data_dir / "component_catalog_seed.csv")
    manager = ScenarioManager.load(data_dir / "assumptions_seed.json")

    if args.command == "catalog":
        if args.cat_command == "list":
            comps = catalog.by_group(args.group)
            print(_table(
                ["id", "name", "group", "role", "mass t", "vol m3", "peak kW", "qty"],
                [[c.id, c.name, c.group, c.power_role, c.unit_mass_t, c.unit_volume_m3,
                  c.peak_power_kw, c.default_qty] for c in comps]))
        else:
            c = catalog.get(args.id)
            for k, v in vars(c).items():
                print(f"{k:24} {v}")
        return 0

    if args.command == "budget":
        a = manager.resolve(args.scenario)
        mission = load_mission(args.mission, catalog)
        budget = BudgetEngine(catalog, a).compute(mission, power_path=args.power)
        packing = PackingEngine(catalog, a).pack(mission, budget)
        if args.format == "xlsx":
            out = args.out or f"{mission.id}_budget.xlsx"
            path = rpt.budget_xlsx(budget, mission, catalog, a, out, packing)
            print(f"Wrote {path}")
        else:
            md = rpt.budget_markdown(budget, mission, packing)
            if args.format == "md" and args.out:
                Path(args.out).write_text(md, encoding="utf-8")
                print(f"Wrote {args.out}")
            else:
                print(md)
        return 0

    if args.command == "pack":
        a = manager.resolve(args.scenario)
        mission = load_mission(args.mission, catalog)
        budget = BudgetEngine(catalog, a).compute(mission)
        packing = PackingEngine(catalog, a).pack(
            mission, budget, tankers_per_ship=args.tankers, launch_cost_tier=args.launch_cost,
            policy=args.policy, include_spares=args.spares or None)
        print(rpt.packing_markdown(packing))
        print()
        print(rpt.loss_markdown(
            PackingEngine(catalog, a).loss_tolerance(packing, manager.capability_unlocks())))
        if packing.warnings:
            print("\nWarnings:")
            for w in packing.warnings:
                print(f"- {w}")
        return 0

    if args.command == "isru":
        from .isru import IsruEngine
        a = manager.resolve(args.scenario)
        mission = load_mission(args.mission, catalog)
        engine = IsruEngine(catalog, a)
        print(rpt.isru_markdown(engine.assess(mission)))
        if args.design is not None:
            target = None if args.design < 0 else args.design
            print(rpt.chain_design_markdown(engine.size_chain(target_tonnes_per_synod=target)))
        return 0

    if args.command in ("plan", "report"):
        a = manager.resolve(args.scenario)
        campaign = load_campaign(args.campaign, catalog)
        planner = CampaignPlanner(catalog, a, manager.capability_unlocks(), manager.crewed_requires())
        result = planner.run(campaign)
        if args.format == "xlsx":
            out = args.out or f"{campaign.id}_campaign.xlsx"
            path = rpt.campaign_xlsx(result, out)
            print(f"Wrote {path}")
        else:
            md = rpt.campaign_markdown(result, catalog, a)
            if args.out:
                Path(args.out).write_text(md, encoding="utf-8")
                print(f"Wrote {args.out}")
            else:
                print(md)
        return 1 if result.violations else 0

    if args.command == "lifecycle":
        from .lifecycle import analyze
        a = manager.resolve(args.scenario)
        campaign = load_campaign(args.campaign, catalog)
        planner = CampaignPlanner(catalog, a, manager.capability_unlocks(), manager.crewed_requires())
        print(rpt.lifecycle_markdown(analyze(planner.run(campaign), catalog, a)))
        return 0

    if args.command == "requirements":
        from .requirements import RequirementsEngine, load_requirements
        a = manager.resolve(args.scenario)
        campaign = load_campaign(args.campaign, catalog)
        planner = CampaignPlanner(catalog, a, manager.capability_unlocks(), manager.crewed_requires())
        reqs = load_requirements(data_dir / "requirements_seed.yaml")
        engine = RequirementsEngine(catalog, a, manager.capability_unlocks())
        matrix = engine.evaluate(reqs, planner.run(campaign))
        md = rpt.requirements_markdown(matrix, reqs, campaign.id)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(md, encoding="utf-8")
            print(f"Wrote {args.out}")
        else:
            print(md)
        return 1 if matrix.open_ids else 0

    if args.command == "compare":
        campaign = load_campaign(args.campaign, catalog) if args.campaign else None
        mission = load_mission(args.mission, catalog) if args.mission else None
        comp = compare(manager, catalog, args.scenario_a, args.scenario_b,
                       campaign=campaign, mission=mission)
        print(rpt.comparison_markdown(comp))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
