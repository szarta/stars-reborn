"""Unit tests for the Starbase-section helpers used by the turn editor
(ui.info_panel) and for PlanetData's starbase parsing.

These cover the pure logic — formatting starbase stats for display, the
mass-driver enablement predicate, and the wire→dataclass mapping — without a
running Qt application."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import PlanetData  # noqa: E402
from src.ui.info_panel import (  # noqa: E402
    starbase_field_rows,
    starbase_has_mass_driver,
)

NAMES = {1: "Earth", 7: "Mars"}

FULL_STARBASE = {
    "dock_capacity": 200,
    "armor": 500,
    "shields": 300,
    "damage_percent": 25,
    "mass_driver": "Warp 7",
    "packet_target": 7,
}


def test_field_rows_none_when_no_starbase():
    assert starbase_field_rows(None, NAMES) is None
    assert starbase_field_rows({}, NAMES) is None


def test_field_rows_formats_full_starbase():
    rows = starbase_field_rows(FULL_STARBASE, NAMES)
    assert rows == {
        "dock": "200 kT",
        "armor": "500 dp",
        "shields": "300 dp",
        "damage": "25%",
        "mass_driver": "Warp 7",
        "dest": "Mars",
    }


def test_field_rows_missing_fields_render_na_and_defaults():
    rows = starbase_field_rows({"armor": 100}, NAMES)
    assert rows["armor"] == "100 dp"
    assert rows["dock"] == "n/a"
    assert rows["shields"] == "n/a"
    # No damage ⇒ "none"; no driver ⇒ "None"; no packet target ⇒ "none".
    assert rows["damage"] == "none"
    assert rows["mass_driver"] == "None"
    assert rows["dest"] == "none"


def test_field_rows_zero_damage_reads_none():
    assert starbase_field_rows({"damage_percent": 0}, NAMES)["damage"] == "none"


def test_field_rows_unknown_destination_falls_back_to_id():
    rows = starbase_field_rows({"packet_target": 999}, NAMES)
    assert rows["dest"] == "999"


def test_has_mass_driver():
    assert starbase_has_mass_driver(FULL_STARBASE) is True
    assert starbase_has_mass_driver({"mass_driver": "Warp 5"}) is True
    assert starbase_has_mass_driver({"mass_driver": None}) is False
    assert starbase_has_mass_driver({"mass_driver": ""}) is False
    assert starbase_has_mass_driver({}) is False
    assert starbase_has_mass_driver(None) is False


def test_planet_data_parses_starbase_from_wire():
    p = PlanetData.from_turn_planet(
        {
            "id": 1,
            "name": "Earth",
            "x": 100,
            "y": 200,
            "starbase": {
                "dock-capacity": 200,
                "armor": 500,
                "shields": 300,
                "damage-percent": 25,
                "mass-driver": "Warp 7",
                "packet-target": 7,
            },
        }
    )
    assert p.starbase == FULL_STARBASE


def test_planet_data_starbase_absent_is_none():
    p = PlanetData.from_turn_planet({"id": 1, "name": "Earth", "x": 0, "y": 0})
    assert p.starbase is None
