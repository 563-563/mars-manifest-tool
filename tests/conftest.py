from pathlib import Path

import pytest

from mars_manifest.catalog import Catalog
from mars_manifest.cli import load_campaign, load_mission
from mars_manifest.scenarios import ScenarioManager

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def catalog() -> Catalog:
    return Catalog.load(ROOT / "inputs" / "catalog.csv")


@pytest.fixture(scope="session")
def manager() -> ScenarioManager:
    return ScenarioManager.load(ROOT / "inputs" / "assumptions.json")


@pytest.fixture(scope="session")
def baseline(manager):
    return manager.resolve("baseline")


@pytest.fixture(scope="session")
def workbook_port(manager):
    # frozen original-spreadsheet overheads/energies; the workbook-port
    # regression must not move when the live baseline is re-anchored
    return manager.resolve("workbook_port")


@pytest.fixture(scope="session")
def precursor(catalog):
    return load_mission(ROOT / "examples" / "precursor_2026.yaml", catalog)


@pytest.fixture(scope="session")
def campaign_4w(catalog):
    return load_campaign(ROOT / "examples" / "campaign_4window.yaml", catalog)
