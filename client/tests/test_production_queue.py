"""Unit tests for the production-queue helpers used by the turn editor's
Production section (ui.info_panel) and for PlanetData's build-queue parsing.

These cover the pure logic — the buildable registry index, queue-row labels,
and the queue→order-item conversion — without a running Qt application."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import PlanetData  # noqa: E402
from src.ui.info_panel import (  # noqa: E402
    _queue_row_label,
    build_buildables_map,
    grouped_buildables,
    insert_queue_entry,
    order_items_from_entries,
)

# A trimmed GET /model/buildables response: two fixed installations and one
# ship-design slot (which carries design-slot).
BUILDABLES_RESPONSE = {
    "buildables": [
        {"build-object-id": 7, "kind": "factory", "name": "Factory", "category": "installation"},
        {"build-object-id": 8, "kind": "mine", "name": "Mine", "category": "installation"},
        {
            "build-object-id": 1024,
            "kind": "design",
            "design-slot": 0,
            "name": "Design Slot 0",
            "category": "ship-design",
        },
    ]
}
BMAP = build_buildables_map(BUILDABLES_RESPONSE)


def test_build_buildables_map_indexes_by_id():
    assert set(BMAP) == {7, 8, 1024}
    assert BMAP[7] == {
        "name": "Factory",
        "kind": "factory",
        "category": "installation",
        "design_slot": None,
    }
    assert BMAP[1024]["design_slot"] == 0


def test_build_buildables_map_tolerates_garbage():
    assert build_buildables_map(None) == {}
    assert build_buildables_map({"buildables": [{"name": "no id"}]}) == {}


def test_queue_row_label_uses_registry_name_and_quantity():
    assert _queue_row_label({"build_object_id": 7, "build_quantity": 5}, BMAP) == "5 Factory"


def test_queue_row_label_appends_progress_when_in_progress():
    row = {"build_object_id": 8, "build_quantity": 3, "build_progress": 42}
    assert _queue_row_label(row, BMAP) == "3 Mine  (42%)"


def test_queue_row_label_unknown_id_falls_back():
    assert (
        _queue_row_label({"build_object_id": 999, "build_quantity": 1}, BMAP) == "1 Buildable 999"
    )


def test_order_items_from_entries_fixed_and_design():
    entries = [
        {"build_object_id": 7, "build_quantity": 2},
        {"build_object_id": 1024, "build_quantity": 1},
    ]
    assert order_items_from_entries(entries, BMAP) == [
        {"item": {"kind": "factory"}, "count": 2},
        {"item": {"kind": "design", "design_slot": 0}, "count": 1},
    ]


def test_order_items_drops_unknown_buildables():
    entries = [
        {"build_object_id": 7, "build_quantity": 1},
        {"build_object_id": 999, "build_quantity": 9},  # not in the registry
    ]
    assert order_items_from_entries(entries, BMAP) == [{"item": {"kind": "factory"}, "count": 1}]


# ── add-item picker helpers ──────────────────────────────────────────────────

PICKER_RESPONSE = {
    "buildables": [
        {"build-object-id": 8, "kind": "mine", "name": "Mine", "category": "installation"},
        {"build-object-id": 7, "kind": "factory", "name": "Factory", "category": "installation"},
        {
            "build-object-id": 20,
            "kind": "auto_max_mines",
            "name": "Auto Max Mines",
            "category": "auto",
        },
        {
            "build-object-id": 1025,
            "kind": "design",
            "design-slot": 1,
            "name": "Design Slot 1",
            "category": "ship-design",
        },
        {
            "build-object-id": 1024,
            "kind": "design",
            "design-slot": 0,
            "name": "Design Slot 0",
            "category": "ship-design",
        },
    ]
}


def test_grouped_buildables_fixed_category_order_and_id_sort():
    groups = grouped_buildables(build_buildables_map(PICKER_RESPONSE))
    assert [label for label, _ in groups] == ["Installations", "Auto Build", "Ship Designs"]
    # Installations sorted by build-object-id (7 before 8), not insertion order.
    assert groups[0][1] == [(7, "Factory"), (8, "Mine")]
    assert groups[1][1] == [(20, "Auto Max Mines")]
    # Design slots sorted by id too (1024 before 1025).
    assert groups[2][1] == [(1024, "Design Slot 0"), (1025, "Design Slot 1")]


def test_grouped_buildables_omits_empty_groups():
    only_installs = {"buildables": [PICKER_RESPONSE["buildables"][0]]}
    groups = grouped_buildables(build_buildables_map(only_installs))
    assert [label for label, _ in groups] == ["Installations"]


def test_grouped_buildables_unknown_category_goes_to_other():
    resp = {
        "buildables": [
            {
                "build-object-id": 99,
                "kind": "mystery",
                "name": "Mystery Trader Gift",
                "category": "weird",
            }
        ]
    }
    groups = grouped_buildables(build_buildables_map(resp))
    assert groups == [("Other", [(99, "Mystery Trader Gift")])]


def test_grouped_buildables_empty_is_empty():
    assert grouped_buildables({}) == []


def test_insert_queue_entry_at_index_lands_above_selection():
    entries = [
        {"build_object_id": 7, "build_quantity": 1},
        {"build_object_id": 8, "build_quantity": 2},
    ]
    out = insert_queue_entry(entries, 1, 1024, 3)
    assert out == [
        {"build_object_id": 7, "build_quantity": 1},
        {"build_object_id": 1024, "build_quantity": 3},
        {"build_object_id": 8, "build_quantity": 2},
    ]
    # Input is not mutated (works on a copy).
    assert len(entries) == 2


def test_insert_queue_entry_out_of_range_appends():
    entries = [{"build_object_id": 7, "build_quantity": 1}]
    # Negative index (nothing selected) and past-the-end both append.
    assert insert_queue_entry(entries, -1, 8, 5)[-1] == {"build_object_id": 8, "build_quantity": 5}
    assert insert_queue_entry(entries, 99, 8, 5)[-1] == {"build_object_id": 8, "build_quantity": 5}


def test_insert_queue_entry_into_empty_queue():
    assert insert_queue_entry([], 0, 7, 1) == [{"build_object_id": 7, "build_quantity": 1}]


# ── PlanetData.build_queue parsing ───────────────────────────────────────────


def _base_planet(**extra) -> dict:
    p = {"id": 1, "name": "Home", "x": 10, "y": 20}
    p.update(extra)
    return p


def test_planetdata_owned_queue_normalized_to_snake_keys():
    p = PlanetData.from_turn_planet(
        _base_planet(
            owner=0,
            **{
                "build-queue": [
                    {"build-object-id": 7, "build-quantity": 5, "build-progress": 30},
                    {"build-object-id": 8, "build-quantity": 1},
                ]
            },
        )
    )
    assert p.build_queue == [
        {"build_object_id": 7, "build_quantity": 5, "build_progress": 30},
        {"build_object_id": 8, "build_quantity": 1, "build_progress": 0},
    ]


def test_planetdata_owned_empty_queue_is_empty_list():
    p = PlanetData.from_turn_planet(_base_planet(owner=0, **{"build-queue": []}))
    assert p.build_queue == []


def test_planetdata_unowned_queue_is_none():
    # No build-queue key on the wire (unowned/unobserved) -> None, not [].
    p = PlanetData.from_turn_planet(_base_planet())
    assert p.build_queue is None
