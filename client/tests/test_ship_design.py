"""Unit tests for the Ship Designer's pure slot-fill logic
(src.data.ship_design): slot-type/component-category compatibility and the
in-memory DesignModel (place/remove/clear, max-count, additive cost/mass).

Pure logic; no running Qt application."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.ship_design import DesignModel, slot_accepts  # noqa: E402

# ── compatibility ─────────────────────────────────────────────────────────────


def test_simple_slot_accepts_only_its_category():
    assert slot_accepts("engines", "engines")
    assert not slot_accepts("engines", "weapons")
    assert slot_accepts("scanners", "scanners")
    assert not slot_accepts("scanners", "armor")


def test_composite_protection_accepts_armor_or_shields():
    assert slot_accepts("protection", "armor")
    assert slot_accepts("protection", "shields")
    assert not slot_accepts("protection", "weapons")


def test_composite_elect_mech_and_unions():
    assert slot_accepts("elect-mech", "electrical")
    assert slot_accepts("elect-mech", "mechanical")
    assert not slot_accepts("elect-mech", "scanners")
    assert slot_accepts("scanner-elect-mech", "scanners")
    assert slot_accepts("scanner-elect-mech", "mechanical")
    assert slot_accepts("weapon-shield", "weapons")
    assert slot_accepts("weapon-shield", "shields")
    assert slot_accepts("orbital-elect", "orbital")
    assert slot_accepts("orbital-elect", "electrical")


def test_general_purpose_admits_installables_but_not_engines_or_orbital():
    for cat in ("weapons", "armor", "shields", "scanners", "bombs", "mining-robots"):
        assert slot_accepts("general-purpose", cat), cat
    assert not slot_accepts("general-purpose", "engines")
    assert not slot_accepts("general-purpose", "orbital")


def test_unknown_slot_type_fails_closed():
    assert not slot_accepts("made-up-slot", "weapons")
    assert not slot_accepts("", "weapons")


# ── fixtures ──────────────────────────────────────────────────────────────────


def _hull():
    """A tiny two-slot hull: one engine slot, one general-purpose (max 3)."""
    return {
        "name": "Test Scout",
        "mass": 10,
        "cost": {"ironium": 4, "boranium": 2, "germanium": 4, "resources": 8},
        "slots": [
            {"slot-type": "engines", "max-count": 1, "position": {"row": 0, "col": 0}},
            {"slot-type": "general-purpose", "max-count": 3, "position": {"row": 0, "col": 1}},
        ],
    }


def _engine():
    return {
        "slug": "quick_jump_5",
        "name": "Quick Jump 5",
        "category": "engines",
        "mass": 4,
        "cost": {"ironium": 3, "boranium": 0, "germanium": 1, "resources": 3},
    }


def _scanner():
    return {
        "slug": "bat_scanner",
        "name": "Bat Scanner",
        "category": "scanners",
        "mass": 2,
        "cost": {"ironium": 1, "boranium": 0, "germanium": 1, "resources": 1},
    }


# ── DesignModel ─────────────────────────────────────────────────────────────


def test_new_design_starts_empty():
    d = DesignModel(hull=_hull())
    assert d.assignments == [None, None]
    assert d.filled_slot_count() == 0
    # Empty design costs exactly the hull.
    assert d.total_cost() == {"ironium": 4, "boranium": 2, "germanium": 4, "resources": 8}
    assert d.total_mass() == 10


def test_mismatched_assignments_length_rejected():
    with pytest.raises(ValueError):
        DesignModel(hull=_hull(), assignments=[None])


def test_place_rejects_incompatible_category():
    d = DesignModel(hull=_hull())
    # A scanner cannot go in an engine slot.
    assert d.place(0, _scanner()) is False
    assert d.assignments[0] is None


def test_place_and_cost_mass_update():
    d = DesignModel(hull=_hull())
    assert d.place(0, _engine()) is True
    assert d.place(1, _scanner()) is True
    cost = d.total_cost()
    # hull(4,2,4,8) + engine(3,0,1,3) + scanner(1,0,1,1)
    assert cost == {"ironium": 8, "boranium": 2, "germanium": 6, "resources": 12}
    assert d.total_mass() == 10 + 4 + 2
    assert d.filled_slot_count() == 2


def test_place_same_component_increments_up_to_max():
    d = DesignModel(hull=_hull())
    assert d.place(1, _scanner()) is True
    assert d.place(1, _scanner()) is True
    assert d.place(1, _scanner()) is True
    assert d.assignments[1]["count"] == 3
    # Slot max is 3 — a fourth is refused.
    assert d.place(1, _scanner()) is False
    assert d.assignments[1]["count"] == 3
    # Three scanners contribute 3× cost/mass.
    assert d.total_mass() == 10 + 3 * 2


def test_place_different_component_replaces():
    d = DesignModel(hull=_hull())
    weapon = {"slug": "laser", "name": "Laser", "category": "weapons", "mass": 1, "cost": {}}
    d.place(1, _scanner())
    d.place(1, _scanner())
    assert d.assignments[1]["count"] == 2
    # Dropping a different (compatible) part replaces, resetting count.
    assert d.place(1, weapon) is True
    assert d.assignments[1]["component"]["slug"] == "laser"
    assert d.assignments[1]["count"] == 1


def test_remove_one_decrements_then_clears():
    d = DesignModel(hull=_hull())
    d.place(1, _scanner())
    d.place(1, _scanner())
    assert d.remove_one(1) is True
    assert d.assignments[1]["count"] == 1
    assert d.remove_one(1) is True
    assert d.assignments[1] is None
    # Removing from an empty slot is a no-op.
    assert d.remove_one(1) is False


def test_clear_empties_slot():
    d = DesignModel(hull=_hull())
    d.place(1, _scanner())
    assert d.clear(1) is True
    assert d.assignments[1] is None
    assert d.clear(1) is False
