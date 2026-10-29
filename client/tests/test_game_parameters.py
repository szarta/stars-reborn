"""Unit tests for the Game Parameters helpers
(src.data.defaults.universe_size_label, game_parameters_rows).

Pure logic; no running Qt application."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import game_parameters_rows, universe_size_label  # noqa: E402


def test_named_universe_sizes():
    assert universe_size_label(400, 400) == "Tiny (400 × 400 ly)"
    assert universe_size_label(800, 800) == "Small (800 × 800 ly)"
    assert universe_size_label(1200, 1200) == "Medium (1200 × 1200 ly)"
    assert universe_size_label(1600, 1600) == "Large (1600 × 1600 ly)"
    assert universe_size_label(2000, 2000) == "Huge (2000 × 2000 ly)"


def test_non_standard_size_is_custom():
    assert universe_size_label(1000, 1000) == "Custom (1000 × 1000 ly)"
    assert universe_size_label(800, 1200) == "Custom (800 × 1200 ly)"


def test_size_label_handles_floats_and_bad_input():
    assert universe_size_label(400.0, 400.0) == "Tiny (400 × 400 ly)"
    assert universe_size_label(None, None) == "n/a"


def test_game_parameters_rows():
    rows = game_parameters_rows("A Walk in the Park", 2400, 800, 800, 24)
    assert rows == [
        ("Game Name", "A Walk in the Park"),
        ("Year", "2400"),
        ("Universe Size", "Small (800 × 800 ly)"),
        ("Planets", "24"),
    ]
