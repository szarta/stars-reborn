"""Contract test: the generated PlayerView model and
schemas/response-turn-file.json must agree on the per-player turn-file wire
shape the engine produces (task #115; Rust half is
engine/tests/turn_file_schema_contract.rs)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client" / "src"))

from data.generated.turn_file import PlanetObserved, PlanetUnobserved, PlayerView  # noqa: E402

# Ground truth as the engine serializes it (see game/view.rs), with one
# observed planet (owned homeworld) and one unobserved planet. The engine emits
# an empty ship-designs list today (designs are not modeled yet); the one design
# here is a representative example to exercise the ShipDesign/SlotAssignment
# wire shape.
TURN_FILE = {
    "year": 2400,
    "game-id": "11111111-1111-4111-8111-111111111111",
    "game-name": "Contract Test",
    "player-id": 0,
    "homeworld-id": 1,
    "ship-designs": [
        {
            "slot": 0,
            "kind": "ship",
            "name": "Santa Maria",
            "hull-id": 11,
            "slot-assignments": [
                {"slot-index": 0, "part-id": 60, "count": 1},
                {"slot-index": 1, "part-id": 70, "count": 1},
            ],
            "built-count": 3,
        }
    ],
    "planets": [
        {
            "id": 1,
            "name": "Neptune",
            "x": 182,
            "y": 117,
            "years-since-last-scan": 0,
            "gravity": 1.0,
            "temperature": 0,
            "radiation": 50,
            "ironium-concentration": 77,
            "boranium-concentration": 22,
            "germanium-concentration": 65,
            "surface-ironium": 77,
            "surface-boranium": 22,
            "surface-germanium": 65,
            "homeworld": True,
            "owner": 0,
            "population": 25000,
            "factories": 10,
            "mines": 10,
            "value": 100,
            "build-queue": [{"build-object-id": 7, "build-quantity": 5}],
        },
        {"id": 2, "name": "Quixote", "x": 365, "y": 298},
    ],
}


def _schema() -> dict:
    return json.loads((REPO / "schemas" / "response-turn-file.json").read_text())


def test_turn_file_validates_against_schema() -> None:
    jsonschema.validate(TURN_FILE, _schema())


def test_turn_file_parses_through_generated_model() -> None:
    view = PlayerView.model_validate(TURN_FILE)
    assert view.player_id == 0
    assert view.homeworld_id == 1
    assert len(view.planets) == 2

    observed, unobserved = view.planets[0].root, view.planets[1].root
    assert isinstance(observed, PlanetObserved)
    assert isinstance(unobserved, PlanetUnobserved)
    assert observed.name == "Neptune"
    assert observed.value == 100
    assert unobserved.name == "Quixote"

    assert len(view.ship_designs) == 1
    design = view.ship_designs[0]
    assert design.name == "Santa Maria"
    assert design.kind.value == "ship"
    assert design.built_count == 3
    assert len(design.slot_assignments) == 2
    assert design.slot_assignments[0].part_id == 60

    # Round-trip back to kebab-case wire JSON and re-validate against the schema.
    # mode="json" renders enums (e.g. ship-design kind) as their wire values.
    redumped = view.model_dump(mode="json", by_alias=True, exclude_none=True)
    jsonschema.validate(redumped, _schema())
