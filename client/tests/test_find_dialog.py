"""Unit tests for the Find-dialog matcher (src.data.defaults.find_planet_matches).

Pure logic over PlanetData-like objects; no running Qt application."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import find_planet_matches  # noqa: E402


@dataclass
class _P:
    id: int
    name: str


PLANETS = [_P(1, "Earth"), _P(2, "Mars"), _P(3, "Marina"), _P(4, "venus")]


def test_empty_query_matches_all_sorted_by_name():
    assert find_planet_matches(PLANETS, "") == [
        (1, "Earth"),
        (3, "Marina"),
        (2, "Mars"),
        (4, "venus"),
    ]


def test_blank_query_matches_all():
    assert len(find_planet_matches(PLANETS, "   ")) == 4


def test_case_insensitive_substring():
    assert find_planet_matches(PLANETS, "mar") == [(3, "Marina"), (2, "Mars")]
    assert find_planet_matches(PLANETS, "VEN") == [(4, "venus")]


def test_no_match_returns_empty():
    assert find_planet_matches(PLANETS, "zzz") == []


def test_matches_substring_anywhere():
    assert find_planet_matches(PLANETS, "art") == [(1, "Earth")]
