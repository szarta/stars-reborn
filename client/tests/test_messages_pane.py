"""Unit tests for the Messages-pane helpers used by the turn editor
(ui.info_panel) and for MessageData's turn-message parsing.

These cover the pure logic — the importance filter, the counter-bar label, and
the wire→dataclass mapping — without a running Qt application."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
# The client runs as ``python -m src`` from client/, so ``client`` is the
# import root and the package is ``src`` (ui modules use relative imports).
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import MessageData  # noqa: E402
from src.ui.info_panel import message_counter_label, visible_messages  # noqa: E402


@dataclass
class _M:
    """Minimal message-like stand-in for the filter tests."""

    id: int
    important: bool = True


# ── visible_messages (the importance filter) ───────────────────────────────


def test_filter_off_shows_all():
    msgs = [_M(1, important=True), _M(2, important=False), _M(3, important=True)]
    assert visible_messages(msgs, hide_unimportant=False) == msgs


def test_filter_on_drops_unimportant():
    msgs = [_M(1, important=True), _M(2, important=False), _M(3, important=True)]
    shown = visible_messages(msgs, hide_unimportant=True)
    assert [m.id for m in shown] == [1, 3]


def test_filter_on_keeps_messages_without_flag():
    # A message missing the flag is treated as important, so the filter never
    # hides something the engine has not explicitly marked unimportant.
    class _Bare:
        pass

    bare = _Bare()
    assert visible_messages([bare], hide_unimportant=True) == [bare]


def test_filter_returns_a_copy():
    msgs = [_M(1)]
    out = visible_messages(msgs, hide_unimportant=False)
    assert out == msgs and out is not msgs


def test_filter_empty_list():
    assert visible_messages([], hide_unimportant=True) == []
    assert visible_messages([], hide_unimportant=False) == []


# ── message_counter_label ──────────────────────────────────────────────────


def test_counter_label_empty_reads_zero_of_zero():
    assert message_counter_label(2400, 0, 0) == "Year: 2400   Messages: 0 of 0"


def test_counter_label_is_one_based():
    assert message_counter_label(2410, 0, 3) == "Year: 2410   Messages: 1 of 3"
    assert message_counter_label(2410, 2, 3) == "Year: 2410   Messages: 3 of 3"


# ── MessageData.from_turn_message (wire → dataclass) ───────────────────────


def test_message_data_parses_full_wire():
    m = MessageData.from_turn_message(
        {
            "id": 5,
            "message": "Mines laid at Earth.",
            "message-type": "MinesCreated",
            "related-object": 12,
            "related-battle": 3,
            "important": False,
        }
    )
    assert m == MessageData(
        id=5,
        text="Mines laid at Earth.",
        message_type="MinesCreated",
        related_object=12,
        related_battle=3,
        important=False,
    )


def test_message_data_defaults_for_minimal_wire():
    # Only the required fields present; optionals fall back to defaults, and an
    # unclassified message defaults to important (shown).
    m = MessageData.from_turn_message(
        {
            "id": 1,
            "message": "Your production queue at Mars is empty.",
            "message-type": "PlanetProductionQueueEmpty",
        }
    )
    assert m.text == "Your production queue at Mars is empty."
    assert m.message_type == "PlanetProductionQueueEmpty"
    assert m.related_object is None
    assert m.related_battle is None
    assert m.important is True
