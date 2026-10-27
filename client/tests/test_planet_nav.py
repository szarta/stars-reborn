"""Unit test for the Prev/Next owned-world navigation logic used by the turn
editor's planet header (ui.info_panel._next_owned_id)."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
# The client runs as ``python -m src`` from client/, so ``client`` is the
# import root and the package is ``src`` (ui modules use relative imports).
sys.path.insert(0, str(REPO / "client"))

from src.ui.info_panel import _next_owned_id  # noqa: E402


@dataclass
class _P:
    id: int
    owner: int | None = None


# Owned worlds are ids 3, 5, 9 (ordered); 1 and 7 belong to someone else.
PLANETS = [_P(7, owner=2), _P(3, owner=1), _P(9, owner=1), _P(1, owner=None), _P(5, owner=1)]


def test_forward_steps_in_id_order():
    assert _next_owned_id(PLANETS, 1, 3, +1) == 5
    assert _next_owned_id(PLANETS, 1, 5, +1) == 9


def test_forward_wraps_at_end():
    assert _next_owned_id(PLANETS, 1, 9, +1) == 3


def test_back_steps_and_wraps():
    assert _next_owned_id(PLANETS, 1, 5, -1) == 3
    assert _next_owned_id(PLANETS, 1, 3, -1) == 9


def test_current_not_owned_starts_at_edge():
    # Viewing a foreign/unseen world: Next -> first owned, Prev -> last owned.
    assert _next_owned_id(PLANETS, 1, 7, +1) == 3
    assert _next_owned_id(PLANETS, 1, 7, -1) == 9
    assert _next_owned_id(PLANETS, 1, None, +1) == 3


def test_no_owned_worlds_returns_none():
    assert _next_owned_id(PLANETS, 99, 3, +1) is None
    assert _next_owned_id([], 1, None, +1) is None


def test_single_owned_world_wraps_to_itself():
    one = [_P(4, owner=1), _P(8, owner=2)]
    assert _next_owned_id(one, 1, 4, +1) == 4
    assert _next_owned_id(one, 1, 4, -1) == 4
