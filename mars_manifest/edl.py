"""EDL (Entry/Descent/Landing) risk analysis — the probabilistic complement
to the deterministic single-ship loss_tolerance check (task C2).

Three things, all honest about their assumptions:
  1. a per-ship landing-success probability that improves as EDL matures
     (window 0 is Musk's "50/50"; nothing heavier than ~1 t has landed);
  2. per-capability survival probability, given how many hulls carry each
     required component (independent-loss approximation);
  3. the statistical confidence a run of successful landings actually buys
     (rule of three: 0 failures in N trials → failure rate ≤ ~3/N at 95%).

Assumes ship losses are independent and a capability needs ≥1 surviving
carrier of each required component. Correlated-failure modes (a bad synod,
a shared design flaw) are out of scope — logged in docs/CONSIDERED.md.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import Assumptions


def success_prob(a: Assumptions, synod_index: int) -> float:
    base = a.get("edl.success_prob_base", 0.5)
    improve = a.get("edl.success_prob_improvement_per_synod", 0.0)
    cap = a.get("edl.max_prob", 0.99)
    return min(cap, base + improve * synod_index)


@dataclass(frozen=True)
class EdlWindow:
    window_id: str
    synod_index: int
    ships: int
    p: float
    expected_landed: float
    p_all_land: float                       # no losses at all this window
    p_at_least_one_loss: float
    capability_survival: tuple[tuple[str, float], ...]  # (flag, P survives)
    cumulative_landings_planned: int
    demonstrated_reliability: float          # rule-of-three floor from successes so far


def _component_carriers(packing) -> dict[str, int]:
    """How many distinct ships carry ≥1 of each component this window."""
    carriers: dict[str, int] = {}
    for s in packing.ships:
        for cid, qty, _, _ in s.manifest_detail:
            if qty > 0:
                carriers[cid] = carriers.get(cid, 0) + 1
    return carriers


def capability_survival(packing, unlock_rules: dict, p: float,
                        base_quantities: dict | None = None,
                        catalog=None) -> dict[str, float]:
    """P(each currently-satisfiable capability survives this window's EDL).

    A component already on the surface (base_quantities) is not at risk, so it
    contributes P=1. A component carried on k of this window's ships survives
    with 1-(1-p)^k. all_of -> product; any_of/any_path -> 1 minus product of
    failures. min_installed_kwe is evaluated by enumerating ship-loss outcomes
    (exact for small fleets; skipped above ~18 ships). Only rules with hardware
    on this window's ships are scored.
    """
    base = base_quantities or {}
    carriers = _component_carriers(packing)
    ships = list(packing.ships)

    def p_component(cid: str) -> float:
        if base.get(cid, 0) >= 1:
            return 1.0
        k = carriers.get(cid, 0)
        return 1.0 - (1.0 - p) ** k if k else 0.0

    def p_min_kwe(threshold: float) -> float:
        if catalog is None or len(ships) > 18:
            return None  # can't score without generation data / too many combos
        # installed kWe already on the surface is not at risk
        base_kwe = sum(catalog.get(c).generation_kwe * q for c, q in base.items()
                       if c in catalog and catalog.get(c).power_role == "generator")
        ship_kwe = []
        for s in ships:
            kwe = sum(catalog.get(cid).generation_kwe * q for cid, q, _, _ in s.manifest_detail
                      if cid in catalog and catalog.get(cid).power_role == "generator")
            ship_kwe.append(kwe)
        import itertools
        prob_ok = 0.0
        n = len(ships)
        for mask in itertools.product((0, 1), repeat=n):  # 1 = lands
            surv = base_kwe + sum(k for k, m in zip(ship_kwe, mask) if m)
            if surv >= threshold:
                lands = sum(mask)
                prob_ok += p ** lands * (1 - p) ** (n - lands)
        return prob_ok

    def p_rule(rule: dict):
        if "any_path" in rule:
            sub = [p_rule(pth) for pth in rule["any_path"]]
            sub = [s for s in sub if s is not None]
            return 1.0 - _prod(1.0 - s for s in sub) if sub else None
        parts = []
        if "all_of" in rule:
            parts += [p_component(c) for c in rule["all_of"]]
        if "any_of" in rule:
            parts.append(1.0 - _prod(1.0 - p_component(c) for c in rule["any_of"]))
        if "min_installed_kwe" in rule:
            pk = p_min_kwe(rule["min_installed_kwe"])
            if pk is not None:
                parts.append(pk)
        # non-hardware conditions (min_population etc.) aren't EDL-at-risk
        return _prod(parts) if parts else 1.0

    out = {}
    for flag, rule in unlock_rules.items():
        touches = ("min_installed_kwe" in rule or flag in carriers
                   or any(c in carriers for c in rule.get("all_of", []) + rule.get("any_of", [])))
        pr = p_rule(rule)
        if pr is not None and (pr < 1.0 or touches):
            out[flag] = pr
    return out


def demonstrated_reliability(successful_landings: int, confidence: float = 0.95) -> float:
    """Rule of three: with 0 observed failures in N landings, the failure rate
    is ≤ ~3/N at 95% confidence, so demonstrated reliability ≈ 1 - 3/N."""
    if successful_landings <= 0:
        return 0.0
    import math
    # -ln(1-conf) ≈ 3.0 at 95%; general form keeps it honest at other levels
    k = -math.log(1.0 - confidence)
    return max(0.0, 1.0 - k / successful_landings)


def _prod(xs) -> float:
    out = 1.0
    for x in xs:
        out *= x
    return out
