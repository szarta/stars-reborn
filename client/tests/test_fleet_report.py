"""Row builders for the F3 Fleets / Others' Fleets reports.

Pure logic over the turn snapshot (own FleetData + foreign ScannedFleetData):
location labelling, cargo/ship aggregation, idle-vs-moving orders, and the
partial-intel placeholders for detected foreign fleets. The dialog rendering is
exercised offscreen, not here."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import (  # noqa: E402
    FleetData,
    PlanetData,
    ScannedFleetData,
    fleet_report_rows,
    scanned_fleet_report_rows,
)


def _planets():
    return [
        PlanetData(id=1, name="Home", x=10, y=20),
        PlanetData(id=2, name="Rigel", x=60, y=80),
    ]


# ── own fleets ────────────────────────────────────────────────────────────────


def test_fleet_rows_location_ships_cargo_orders():
    fleets = [
        FleetData.from_turn_fleet(
            {
                "id": 100,
                "name": "Santa Maria",
                "owner": 0,
                "x": 10,
                "y": 20,
                "orbiting-planet-id": 1,
                "ship-stacks": [{"design-slot": 0, "count": 2}, {"design-slot": 1, "count": 3}],
                "fuel": 120,
                "cargo": {"ironium": 5, "boranium": 0, "germanium": 2, "colonists": 50},
                "waypoints": [],
            }
        ),
        FleetData.from_turn_fleet(
            {
                "id": 101,
                "name": "Scout",
                "owner": 0,
                "x": 33,
                "y": 44,
                "ship-stacks": [{"design-slot": 0, "count": 1}],
                "fuel": 60,
                "cargo": {"ironium": 0, "boranium": 0, "germanium": 0, "colonists": 0},
                "waypoints": [{"x": 60, "y": 80, "warp": 7, "task": "none"}],
            }
        ),
    ]
    rows = fleet_report_rows(fleets, _planets())
    # sorted by name: Santa Maria, Scout
    santa, scout = rows
    assert santa["location"] == "Home"  # orbiting planet 1
    assert santa["ships"] == 5
    assert santa["cargo"] == 57  # 5+0+2+50
    assert santa["orders"] == "Idle"
    assert scout["location"] == "(33, 44)"  # deep space
    assert scout["orders"] == "Warp 7"
    assert scout["orbiting_planet_id"] is None


def test_fleet_rows_empty():
    assert fleet_report_rows([], _planets()) == []


# ── foreign (scanned) fleets ──────────────────────────────────────────────────


def test_scanned_fleet_rows_partial_intel_and_sort():
    scanned = [
        ScannedFleetData.from_turn_scanned_fleet(
            {
                "id": 200,
                "owner-player-id": 2,
                "x": 60,
                "y": 80,
                "orbiting-planet-id": 2,
                "name": "Death Star",
                "ship-count": 4,
                "years-since-last-scan": 0,
            }
        ),
        ScannedFleetData.from_turn_scanned_fleet(
            # coarse scan: name + ship-count unknown, in deep space
            {"id": 201, "owner-player-id": 1, "x": 5, "y": 6, "years-since-last-scan": 3}
        ),
    ]
    rows = scanned_fleet_report_rows(scanned, _planets())
    # sorted by owner id then name: player 1 first
    first, second = rows
    assert first["owner"] == "Player 1"
    assert first["name"] == "(unknown)"
    assert first["ships"] is None  # rendered as a placeholder by the dialog
    assert first["location"] == "(5, 6)"
    assert first["age"] == 3
    assert second["owner"] == "Player 2"
    assert second["name"] == "Death Star"
    assert second["location"] == "Rigel"
    assert second["ships"] == 4
    assert second["orbiting_planet_id"] == 2


def test_scanned_fleet_rows_empty():
    assert scanned_fleet_report_rows([], _planets()) == []
