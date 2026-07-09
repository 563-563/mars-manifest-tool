from pathlib import Path

import pytest

from mars_manifest.catalog import Catalog
from mars_manifest.cli import load_campaign, load_mission
from mars_manifest.scenarios import ScenarioManager

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def catalog() -> Catalog:
    return Catalog.load(ROOT / "data" / "component_catalog_seed.csv")


@pytest.fixture(scope="session")
def manager() -> ScenarioManager:
    return ScenarioManager.load(ROOT / "data" / "assumptions_seed.json")


@pytest.fixture(scope="session")
def baseline(manager):
    return manager.resolve("baseline")


@pytest.fixture(scope="session")
def precursor(catalog):
    return load_mission(ROOT / "examples" / "precursor_2026.yaml", catalog)


@pytest.fixture(scope="session")
def campaign_4w(catalog):
    return load_campaign(ROOT / "examples" / "campaign_4window.yaml", catalog)
