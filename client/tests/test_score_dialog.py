"""Unit tests for the F10 Score helpers (src.data.defaults.ScoreData and
score_rows) used by the Score dialog.

Pure wire->dataclass and row-formatting logic; no running Qt application. The
client reads points from the engine and never recomputes the score formula, so
these only pin parsing and display ordering."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.defaults import ScoreData, score_rows  # noqa: E402

WIRE = {
    "total": 318,
    "planet-count": 5,
    "planet-points": 20,
    "starbase-count": 5,
    "starbase-points": 15,
    "unarmed-count": 71,
    "unarmed-points": 2,
    "escort-count": 8,
    "escort-points": 16,
    "capital-count": 1,
    "capital-points": 6,
    "tech-level-sum": 60,
    "tech-points": 100,
    "resource-amount": 3807,
    "resource-points": 126,
}


def test_from_turn_score_parses_all_fields():
    s = ScoreData.from_turn_score(WIRE)
    assert s.total == 318
    assert s.planet_count == 5
    assert s.planet_points == 20
    assert s.capital_count == 1
    assert s.resource_amount == 3807
    assert s.resource_points == 126


def test_from_turn_score_none_when_absent():
    assert ScoreData.from_turn_score(None) is None
    assert ScoreData.from_turn_score({}) is None


def test_from_turn_score_defaults_missing_fields_to_zero():
    s = ScoreData.from_turn_score({"total": 5, "planet-count": 1})
    assert s.total == 5
    assert s.planet_count == 1
    assert s.starbase_count == 0
    assert s.resource_points == 0


def test_score_rows_order_and_contents():
    rows = score_rows(ScoreData.from_turn_score(WIRE))
    assert [r[0] for r in rows] == [
        "Planets",
        "Starbases",
        "Unarmed Ships",
        "Escort Ships",
        "Capital Ships",
        "Tech Levels",
        "Resources",
    ]
    # Each row is (label, count, points).
    assert rows[0] == ("Planets", 5, 20)
    assert rows[4] == ("Capital Ships", 1, 6)
    assert rows[6] == ("Resources", 3807, 126)
