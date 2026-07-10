"""Poisson spares method (D4). Tests the MATH; the rates are D-tier inputs."""
import pytest

from mars_manifest.budgets import BudgetEngine
from mars_manifest.spares import poisson_cdf, spares_for_reliability


def test_poisson_cdf_basic():
    assert poisson_cdf(0, 0.0) == 1.0
    # Poisson(1): P(X<=1) = 2*e^-1 ~ 0.7358
    assert poisson_cdf(1, 1.0) == pytest.approx(0.7358, abs=0.001)


def test_spares_for_reliability_monotone():
    # higher expected failures -> more spares; higher target -> more spares
    assert spares_for_reliability(2.0, 0.95) > spares_for_reliability(0.5, 0.95)
    assert spares_for_reliability(2.0, 0.99) >= spares_for_reliability(2.0, 0.90)
    # a unit that never fails needs no spares
    assert spares_for_reliability(0.0, 0.95) == 0
    # lam=2, 95%: need k where Poisson CDF >= .95 -> k=5 (CDF~0.983)
    assert spares_for_reliability(2.0, 0.95) == 5


def test_poisson_spares_scenario_runs_and_differs(manager, catalog, precursor):
    base = BudgetEngine(catalog, manager.resolve("baseline")).compute(precursor)
    pois = BudgetEngine(catalog, manager.resolve("poisson_spares")).compute(precursor)
    # produces a positive, group-resolved spares mass distinct from the flat 35%
    assert pois.mass.spares_t > 0
    assert pois.mass.spares_t != pytest.approx(base.mass.spares_t)
    assert set(pois.mass.spares_by_group)  # non-empty per-group breakdown
