"""Fleet-backed turn-editor toolbar overlays (Fleet Paths + Idle Fleets).

Both overlays are pure client-side reads of the turn file's own-fleet list:
the Fleet Paths overlay threads each fleet's route polyline (fleet position
then its waypoints), and the Idle Fleets filter restricts map clicks to the
planets that have an idle (no-waypoint) fleet in orbit. The Add Waypoints mode
is intentionally not covered here — it needs a fleet order the engine does not
model yet, so it only shows a status message.

These exercise the pure helpers (no QWidget), matching the client test style.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import FleetData, planets_with_idle_fleets  # noqa: E402
from src.ui.space_map import fleet_path_points  # noqa: E402


def _fleet(**extra) -> dict:
    f = {"id": 100, "name": "Scout", "owner": 0, "x": 10, "y": 20}
    f.update(extra)
    return f


# ── FleetData parsing ────────────────────────────────────────────────────────


def test_from_turn_fleet_core_fields():
    f = FleetData.from_turn_fleet(
        _fleet(**{"orbiting-planet-id": 3, "fuel": 120, "repeat-orders": True})
    )
    assert f.id == 100
    assert f.name == "Scout"
    assert f.owner == 0
    assert (f.x, f.y) == (10.0, 20.0)
    assert f.orbiting_planet_id == 3
    assert f.fuel == 120
    assert f.repeat_orders is True


def test_from_turn_fleet_waypoints_parsed_in_order():
    f = FleetData.from_turn_fleet(
        _fleet(
            waypoints=[
                {"x": 30, "y": 40, "warp": 6, "task": "none"},
                {"x": 50, "y": 60, "target-planet-id": 7, "warp": 5, "task": "colonize"},
            ]
        )
    )
    assert len(f.waypoints) == 2
    assert (f.waypoints[0].x, f.waypoints[0].y) == (30.0, 40.0)
    assert f.waypoints[0].target_planet_id is None
    assert f.waypoints[1].target_planet_id == 7
    assert f.waypoints[1].task == "colonize"


def test_from_turn_fleet_defaults_for_minimal_wire():
    f = FleetData.from_turn_fleet(_fleet())
    assert f.orbiting_planet_id is None
    assert f.waypoints == []
    assert f.repeat_orders is False


# ── is_idle ──────────────────────────────────────────────────────────────────


def test_is_idle_true_without_waypoints():
    assert FleetData.from_turn_fleet(_fleet()).is_idle is True


def test_is_idle_false_with_waypoints():
    f = FleetData.from_turn_fleet(_fleet(waypoints=[{"x": 1, "y": 2, "warp": 5, "task": "none"}]))
    assert f.is_idle is False


# ── planets_with_idle_fleets (Idle Fleets filter) ────────────────────────────


def test_planets_with_idle_fleets_collects_orbited_planets():
    fleets = [
        FleetData.from_turn_fleet(_fleet(id=1, **{"orbiting-planet-id": 10})),  # idle, in orbit
        FleetData.from_turn_fleet(
            _fleet(
                id=2,
                **{"orbiting-planet-id": 20},
                waypoints=[{"x": 1, "y": 1, "warp": 5, "task": "none"}],
            )
        ),  # moving — excluded
        FleetData.from_turn_fleet(_fleet(id=3)),  # idle but in deep space — excluded
        FleetData.from_turn_fleet(_fleet(id=4, **{"orbiting-planet-id": 10})),  # idle, same planet
    ]
    assert planets_with_idle_fleets(fleets) == {10}


def test_planets_with_idle_fleets_empty_when_none():
    assert planets_with_idle_fleets([]) == set()


# ── fleet_path_points (Fleet Paths overlay geometry) ─────────────────────────


def test_fleet_path_points_prepends_current_position():
    f = FleetData.from_turn_fleet(
        _fleet(
            x=10,
            y=20,
            waypoints=[
                {"x": 30, "y": 40, "warp": 6, "task": "none"},
                {"x": 50, "y": 60, "warp": 6, "task": "none"},
            ],
        )
    )
    assert fleet_path_points(f) == [(10.0, 20.0), (30.0, 40.0), (50.0, 60.0)]


def test_fleet_path_points_empty_for_idle_fleet():
    assert fleet_path_points(FleetData.from_turn_fleet(_fleet())) == []
