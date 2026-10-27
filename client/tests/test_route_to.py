"""PlanetData.route_target parsing for the turn editor's Route To section.

The route destination is always a planet id (or None for no route); clicking
empty space or an object snaps to the nearest planet client-side — see
stars-reborn-research/knowledge/findings/route_to.rst."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import PlanetData  # noqa: E402


def _planet(**extra) -> dict:
    p = {"id": 1, "name": "Home", "x": 10, "y": 20}
    p.update(extra)
    return p


def test_route_target_parsed_when_present():
    p = PlanetData.from_turn_planet(_planet(owner=0, **{"route-target": 7}))
    assert p.route_target == 7


def test_route_target_none_when_absent():
    # Owned planet with no route (the common case) — wire omits route-target.
    p = PlanetData.from_turn_planet(_planet(owner=0, **{"build-queue": []}))
    assert p.route_target is None


def test_route_target_none_for_unowned():
    p = PlanetData.from_turn_planet(_planet())
    assert p.route_target is None
