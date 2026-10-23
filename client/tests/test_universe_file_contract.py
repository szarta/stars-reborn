"""Contract test: the generated UniverseResponse model and
schemas/response-game.json must agree on the public universe-file wire shape
the engine produces (task #115; Rust half is
engine/tests/universe_file_schema_contract.rs)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client" / "src"))

from data.generated.universe_file import UniverseResponse  # noqa: E402

UNIVERSE_FILE = {
    "game-id": "11111111-1111-4111-8111-111111111111",
    "game-name": "Contract Test",
    "year": 2400,
    "universe-width": 400,
    "universe-height": 400,
    "planet-count": 2,
    "planets": [
        {"id": 1, "name": "Neptune", "x": 182, "y": 117},
        {"id": 2, "name": "Quixote", "x": 365, "y": 298},
    ],
}


def _schema() -> dict:
    return json.loads((REPO / "schemas" / "response-game.json").read_text())


def test_universe_file_validates_against_schema() -> None:
    jsonschema.validate(UNIVERSE_FILE, _schema())


def test_universe_file_parses_through_generated_model() -> None:
    universe = UniverseResponse.model_validate(UNIVERSE_FILE)
    assert universe.game_id == "11111111-1111-4111-8111-111111111111"
    assert universe.planet_count == 2
    assert [p.name for p in universe.planets] == ["Neptune", "Quixote"]

    redumped = universe.model_dump(by_alias=True, exclude_none=True)
    jsonschema.validate(redumped, _schema())
