"""Unit tests for the F3 Planets-report row builder
(src.data.defaults.planet_report_rows).

Pure logic over PlanetData-like objects; no running Qt application."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import planet_report_rows  # noqa: E402


@dataclass
class _P:
    id: int
    name: str
    value: int | None = None
    owner: int | None = None
    population: int = 0
    resources_per_year: int | None = None
    mines: int = 0
    factories: int = 0
    surface_ironium: int = 0
    surface_boranium: int = 0
    surface_germanium: int = 0


def test_never_observed_planets_are_omitted():
    # value is None => never observed => no contents to report.
    planets = [_P(1, "Earth", value=50, owner=0), _P(2, "Unknown", value=None)]
    rows = planet_report_rows(planets, player_id=0)
    assert [r["name"] for r in rows] == ["Earth"]


def test_rows_sorted_by_name():
    planets = [
        _P(1, "Zeta", value=10, owner=0),
        _P(2, "Alpha", value=20, owner=0),
        _P(3, "Mu", value=30, owner=0),
    ]
    assert [r["name"] for r in planet_report_rows(planets, 0)] == ["Alpha", "Mu", "Zeta"]


def test_row_fields_and_ownership_flag():
    planets = [
        _P(
            7,
            "Earth",
            value=100,
            owner=0,
            population=25000,
            resources_per_year=125,
            mines=10,
            factories=10,
            surface_ironium=77,
            surface_boranium=22,
            surface_germanium=65,
        ),
        _P(8, "Mars", value=60, owner=3, population=5000),
    ]
    rows = {r["name"]: r for r in planet_report_rows(planets, player_id=0)}
    earth = rows["Earth"]
    assert earth["id"] == 7
    assert earth["owned"] is True
    assert earth["resources"] == 125
    assert earth["ironium"] == 77 and earth["germanium"] == 65
    # A foreign observed planet is reported, flagged not-owned.
    assert rows["Mars"]["owned"] is False


def test_resources_may_be_none():
    # Observed planet with no resources figure (e.g. an AR owner): row present,
    # resources left as None for the view to render "n/a".
    planets = [_P(1, "Earth", value=50, owner=0, resources_per_year=None)]
    assert planet_report_rows(planets, 0)[0]["resources"] is None
