"""Unit tests for the Status-section fields that PlanetData parses from the
turn file (src.data.defaults.PlanetData).

Pure wire->dataclass logic; no running Qt application. The Status section
itself reads these via getattr and degrades to "n/a" when absent, so the
parsing is the part worth pinning."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import PlanetData  # noqa: E402


def test_resources_per_year_parsed_from_wire():
    p = PlanetData.from_turn_planet(
        {"id": 1, "name": "Earth", "x": 0, "y": 0, "resources-per-year": 125}
    )
    assert p.resources_per_year == 125


def test_resources_per_year_absent_is_none():
    # Unowned/unobserved planet, or an AR owner the engine cannot compute for:
    # the field is absent and the Status section shows "n/a".
    p = PlanetData.from_turn_planet({"id": 1, "name": "Earth", "x": 0, "y": 0})
    assert p.resources_per_year is None
