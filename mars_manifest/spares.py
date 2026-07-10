"""Poisson spares model (task D4) — the supportability method, honestly scoped.

The per-group fractions in the `informed_spares` scenario are a proxy. The
rigorous approach (Owens & de Weck; NASA ICES supportability line) sizes
spares from component failure rates: if a unit is expected to fail `lam`
times over a resupply interval, you carry the smallest number of spares k
such that P(demand <= k) >= a target reliability, under a Poisson demand
model.

THE METHOD HERE IS CORRECT; THE INPUTS ARE NOT YET. No trustworthy
per-component failure rates exist for Mars hardware — building a full
semi-Markov model on invented MTBFs would be false precision (see
docs/CONSIDERED.md). This module implements the calculation and a scenario
seeds D-tier per-group rates anchored to ISS ECLSS heritage where it exists,
so real MTBFs can replace them without re-engineering. Off by default.
"""
from __future__ import annotations

import math


def poisson_cdf(k: int, lam: float) -> float:
    """P(X <= k) for X ~ Poisson(lam)."""
    if lam <= 0:
        return 1.0
    term = math.exp(-lam)
    total = term
    for i in range(1, k + 1):
        term *= lam / i
        total += term
    return total


def spares_for_reliability(expected_failures: float, target_reliability: float) -> int:
    """Smallest spare count k with P(demand <= k) >= target under Poisson
    demand of mean `expected_failures`. This is the standard sparing-to-a-
    confidence-level calculation the supportability literature uses."""
    target_reliability = min(max(target_reliability, 0.0), 0.999999)
    k = 0
    while poisson_cdf(k, expected_failures) < target_reliability:
        k += 1
        if k > 10_000:  # runaway guard
            break
    return k
