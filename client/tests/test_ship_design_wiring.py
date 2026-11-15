"""Wiring the Ship Designer to the engine's real design model.

Covers the pure (Qt-free) bridge between the turn file's ``ship-designs`` and
the editor/order layer: parsing a stored design, reconstructing its editable
DesignModel over a live hull, and emitting design.upsert / design.delete
orders. The dialog rendering itself is exercised by the offscreen smoke test,
not here (no running Qt app in the unit suite)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import RaceInfo, ShipDesignData, SlotAssignmentData  # noqa: E402
from src.data.ship_design import (  # noqa: E402
    components_by_id,
    design_delete_order,
    design_model_from_assignments,
    design_upsert_order,
    model_to_wire_slot_assignments,
)

# ── turn-file design parsing ──────────────────────────────────────────────────


def _design_wire(**extra) -> dict:
    d = {
        "slot": 2,
        "kind": "ship",
        "name": "Long Range Scout",
        "hull-id": 1,
        "slot-assignments": [
            {"slot-index": 0, "part-id": 10, "count": 1},
            {"slot-index": 1, "part-id": 20, "count": 2},
        ],
        "built-count": 3,
    }
    d.update(extra)
    return d


def test_from_turn_design_parses_all_fields():
    d = ShipDesignData.from_turn_design(_design_wire())
    assert d.slot == 2
    assert d.kind == "ship"
    assert d.name == "Long Range Scout"
    assert d.hull_id == 1
    assert d.built_count == 3
    assert [(s.slot_index, s.part_id, s.count) for s in d.slot_assignments] == [
        (0, 10, 1),
        (1, 20, 2),
    ]


def test_from_turn_design_defaults_for_minimal_wire():
    d = ShipDesignData.from_turn_design({"slot": 0, "hull-id": 5})
    assert d.kind == "ship"
    assert d.name == ""
    assert d.slot_assignments == []
    assert d.built_count == 0


# ── race info ─────────────────────────────────────────────────────────────────


def test_race_info_from_turn_race():
    r = RaceInfo.from_turn_race({"prt": "JOAT", "lrts": ["IFE", "TT"], "name": "Human"})
    assert r.prt == "JOAT"
    assert r.lrts == ["IFE", "TT"]
    assert r.name == "Human"


def test_race_info_none_when_absent():
    assert RaceInfo.from_turn_race(None) is None
    assert RaceInfo.from_turn_race({}) is None


# ── DesignModel reconstruction over a hull ───────────────────────────────────


def _hull() -> dict:
    return {
        "id": 1,
        "name": "Scout",
        "slug": "scout",
        "mass": 8,
        "armor": 20,
        "cost": {"ironium": 4, "boranium": 2, "germanium": 4, "resources": 10},
        "slots": [
            {"slot-type": "engines", "max-count": 1, "position": {"row": 0, "col": 0}},
            {"slot-type": "scanners", "max-count": 1, "position": {"row": 0, "col": 1}},
            {"slot-type": "general-purpose", "max-count": 2, "position": {"row": 0, "col": 2}},
        ],
    }


def _catalog() -> list[dict]:
    return [
        {
            "id": 10,
            "slug": "quick_jump",
            "name": "Quick Jump 5",
            "category": "engines",
            "mass": 4,
            "cost": {"ironium": 3, "boranium": 0, "germanium": 1, "resources": 3},
        },
        {
            "id": 20,
            "slug": "bat_scanner",
            "name": "Bat Scanner",
            "category": "scanners",
            "mass": 2,
            "cost": {"ironium": 1, "boranium": 0, "germanium": 1, "resources": 1},
        },
    ]


def test_components_by_id_indexes_catalog():
    by_id = components_by_id(_catalog())
    assert set(by_id) == {10, 20}
    assert by_id[10]["slug"] == "quick_jump"


def test_design_model_from_assignments_lays_parts_over_hull():
    by_id = components_by_id(_catalog())
    assignments = [
        SlotAssignmentData(0, 10, 1),
        SlotAssignmentData(1, 20, 1),
    ]
    model = design_model_from_assignments(_hull(), assignments, by_id, "Scout I")
    assert model.name == "Scout I"
    assert model.assignments[0]["component"]["id"] == 10
    assert model.assignments[1]["component"]["id"] == 20
    assert model.assignments[2] is None  # empty general-purpose slot
    # mass = hull 8 + engine 4 + scanner 2
    assert model.total_mass() == 14


def test_design_model_skips_out_of_range_and_unknown_parts():
    by_id = components_by_id(_catalog())
    assignments = [
        SlotAssignmentData(0, 10, 1),
        SlotAssignmentData(9, 20, 1),  # slot index past the hull — skipped
        SlotAssignmentData(1, 999, 1),  # part not in catalog — skipped
    ]
    model = design_model_from_assignments(_hull(), assignments, by_id)
    assert model.assignments[0] is not None
    assert model.assignments[1] is None
    assert model.filled_slot_count() == 1


# ── order payloads ────────────────────────────────────────────────────────────


def test_model_to_wire_slot_assignments_roundtrips_filled_slots():
    by_id = components_by_id(_catalog())
    model = design_model_from_assignments(
        _hull(), [SlotAssignmentData(0, 10, 1), SlotAssignmentData(1, 20, 2)], by_id
    )
    assert model_to_wire_slot_assignments(model) == [
        {"slot-index": 0, "part-id": 10, "count": 1},
        {"slot-index": 1, "part-id": 20, "count": 2},
    ]


def test_design_upsert_order_shape():
    by_id = components_by_id(_catalog())
    model = design_model_from_assignments(_hull(), [SlotAssignmentData(0, 10, 1)], by_id, "S")
    order = design_upsert_order(3, "ship", "S", 1, model)
    assert order == {
        "kind": "design.upsert",
        "design_slot": 3,
        "design": {
            "kind": "ship",
            "name": "S",
            "hull-id": 1,
            "slot-assignments": [{"slot-index": 0, "part-id": 10, "count": 1}],
        },
    }


def test_design_delete_order_shape():
    assert design_delete_order(4, "starbase") == {
        "kind": "design.delete",
        "design_slot": 4,
        "design_kind": "starbase",
    }
