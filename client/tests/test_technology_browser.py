"""Unit tests for the component-catalog pure helpers
(src.data.technologies): category grouping, availability filtering, and
icon-filename derivation. These are the pieces the Technology Browser and the
Ship Designer component picker reuse.

Pure logic; no running Qt application."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.technologies import (  # noqa: E402
    component_available,
    group_by_category,
    icon_filename,
)


def _item(name, category="engines", requirement=None):
    return {"name": name, "category": category, "requirement": requirement}


def test_icon_filename_dashes_words():
    assert icon_filename("Quick Jump 5") == "Quick-Jump-5.png"
    assert icon_filename("Enigma Pulsar") == "Enigma-Pulsar.png"


def test_group_by_category_orders_canonically_and_keeps_catalog_order():
    items = [
        _item("Galaxy Scoop", "engines"),
        _item("Tritanium", "armor"),
        _item("Quick Jump 5", "engines"),
    ]
    by_cat, ordered = group_by_category(items)
    # Armor precedes engines in the canonical dropdown order.
    assert ordered == ["armor", "engines"]
    # Within a category, catalog order is preserved.
    assert [i["name"] for i in by_cat["engines"]] == ["Galaxy Scoop", "Quick Jump 5"]


def test_group_by_category_appends_unknown_categories():
    _, ordered = group_by_category([_item("Weird", "made-up-category")])
    assert ordered == ["made-up-category"]


def test_available_when_no_requirement():
    assert component_available(_item("Long Hump 6"), "JOAT", []) is True


def test_prt_gate():
    it = _item("Settler's Delight", requirement={"prt": ["HE"]})
    assert component_available(it, "HE", []) is True
    assert component_available(it, "JOAT", []) is False


def test_lrt_gate_requires_all():
    it = _item("Scoop", requirement={"lrt": ["IFE", "NRSE"]})
    assert component_available(it, "JOAT", ["IFE", "NRSE"]) is True
    assert component_available(it, "JOAT", ["IFE"]) is False


def test_mystery_trader_items_are_unavailable():
    it = _item("Enigma Pulsar", requirement={"mystery-trader": True})
    assert component_available(it, "JOAT", []) is False


def test_case_insensitive_traits():
    it = _item("x", requirement={"prt": ["he"], "lrt": ["ife"]})
    assert component_available(it, "He", ["Ife"]) is True
