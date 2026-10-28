"""Unit tests for the Race-view summary (src.data.defaults.race_summary) used by
the F8 Race view dialog.

Pure dict->rows logic; no running Qt application."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import race_summary  # noqa: E402

RACE = {
    "name": "Humanoid",
    "plural_name": "Humanoids",
    "prt": "JOAT",
    "lrts": ["IFE", "NAS"],
    "hab": {
        "gravity": {"immune": False, "min": 0.22, "max": 4.4},
        "temperature": {"immune": False, "min": -140, "max": 140},
        "radiation": {"immune": True},
    },
    "economy": {
        "resource_production": 1000,
        "factory_production": 10,
        "factory_cost": 10,
        "colonists_operate_factories": 10,
        "mine_production": 10,
        "mine_cost": 5,
        "colonists_operate_mines": 10,
        "growth_rate": 15,
    },
    "research_costs": {
        "energy": "cheap",
        "weapons": "expensive",
        "propulsion": "normal",
        "construction": "normal",
        "electronics": "normal",
        "biotechnology": "normal",
    },
}


def _flatten(sections):
    return {label: value for _title, rows in sections for label, value in rows}


def test_empty_race_yields_no_sections():
    assert race_summary(None) == []
    assert race_summary({}) == []


def test_section_titles_and_order():
    assert [t for t, _ in race_summary(RACE)] == [
        "Race",
        "Habitability",
        "Economy",
        "Research Costs",
    ]


def test_identity_and_traits():
    rows = _flatten(race_summary(RACE))
    assert rows["Name"] == "Humanoid"
    assert rows["Primary Trait"] == "JOAT"
    assert rows["Lesser Traits"] == "IFE, NAS"


def test_no_lrts_reads_none():
    rows = _flatten(race_summary({**RACE, "lrts": []}))
    assert rows["Lesser Traits"] == "None"


def test_hab_ranges_and_immune():
    rows = _flatten(race_summary(RACE))
    assert rows["Gravity"] == "0.22g – 4.4g"
    assert rows["Temperature"] == "-140°C – 140°C"
    assert rows["Radiation"] == "Immune"
    assert rows["Growth Rate"] == "15%"


def test_economy_and_research_rows():
    rows = _flatten(race_summary(RACE))
    assert rows["Colonists per Resource"] == "1000"
    assert rows["Factory Output"] == "10"
    assert rows["Energy"] == "cheap"
    assert rows["Weapons"] == "expensive"
