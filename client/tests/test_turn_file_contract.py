"""Contract test: the generated PlayerView model and
schemas/response-turn-file.json must agree on the per-player turn-file wire
shape the engine produces (Rust half is
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
    # Enemy designs this player has scanned. One with only basic intel
    # (identity, no slot-assignments) and one with full (penetrating) intel —
    # exercising both tiers of the scanned-design wire shape. The engine emits
    # an empty list today (fleets/scanning not modeled).
    "scanned-designs": [
        {
            "owner-player-id": 1,
            "design-slot": 2,
            "kind": "ship",
            "name": "Pirate Raider",
            "hull-id": 12,
            "years-since-last-scan": 4,
        },
        {
            "owner-player-id": 1,
            "design-slot": 0,
            "kind": "starbase",
            "name": "Fort Knox",
            "hull-id": 1,
            "years-since-last-scan": 0,
            "slot-assignments": [
                {"slot-index": 0, "part-id": 60, "count": 8},
            ],
        },
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
            "resources-per-year": 125,
            "build-queue": [{"build-object-id": 7, "build-quantity": 5}],
            "route-target": 2,
        },
        {"id": 2, "name": "Quixote", "x": 365, "y": 298},
    ],
    "messages": [
        {
            "id": 0,
            "message": "The production queue on Neptune is empty.",
            "message-type": "PlanetProductionQueueEmpty",
            "related-object": 1,
            "important": True,
        }
    ],
    "score": {
        "total": 5,
        "planet-count": 1,
        "planet-points": 1,
        "starbase-count": 0,
        "starbase-points": 0,
        "unarmed-count": 0,
        "unarmed-points": 0,
        "escort-count": 0,
        "escort-points": 0,
        "capital-count": 0,
        "capital-points": 0,
        "tech-level-sum": 0,
        "tech-points": 0,
        "resource-amount": 125,
        "resource-points": 4,
    },
    "race": {
        "format_version": 1,
        "name": "Humanoid",
        "plural_name": "Humanoids",
        "prt": "JOAT",
        "lrts": ["IFE", "NAS"],
        "hab": {
            "gravity": {"immune": False, "min": 0.22, "max": 4.4},
            "temperature": {"immune": False, "min": -140, "max": 140},
            "radiation": {"immune": True},
        },
        "economy": {
            "resource_production": 1000,
            "factory_production": 10,
            "factory_cost": 10,
            "factory_cheap_germanium": False,
            "colonists_operate_factories": 10,
            "mine_production": 10,
            "mine_cost": 5,
            "colonists_operate_mines": 10,
            "growth_rate": 15,
        },
        "research_costs": {
            "energy": "normal",
            "weapons": "normal",
            "propulsion": "normal",
            "construction": "normal",
            "electronics": "normal",
            "biotechnology": "normal",
        },
        "leftover_spend": "surface_minerals",
        "icon_index": 0,
    },
}


def _strip_file_prefixes(node):
    """Rewrite cross-file ``"$ref": "file.json#/foo"`` to local ``"#/foo"``
    throughout (mirrors engine/build.rs and the Rust contract test)."""
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and "#" in ref and not ref.startswith("#"):
            node["$ref"] = ref[ref.index("#") :]
        for value in node.values():
            _strip_file_prefixes(value)
    elif isinstance(node, list):
        for value in node:
            _strip_file_prefixes(value)


def _schema() -> dict:
    """response-turn-file.json with race.json's definitions merged in and the
    cross-file ``race.json#/...`` ref (PlayerView.race) rewritten local, so the
    schema resolves offline."""
    schema = json.loads((REPO / "schemas" / "response-turn-file.json").read_text())
    race = json.loads((REPO / "schemas" / "race.json").read_text())
    for name, definition in race["definitions"].items():
        schema["definitions"].setdefault(name, definition)
    _strip_file_prefixes(schema)
    return schema


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
    assert observed.resources_per_year == 125
    assert observed.route_target == 2
    assert unobserved.name == "Quixote"

    assert len(view.ship_designs) == 1
    design = view.ship_designs[0]
    assert design.name == "Santa Maria"
    assert design.kind.value == "ship"
    assert design.built_count == 3
    assert len(design.slot_assignments) == 2
    assert design.slot_assignments[0].part_id == 60

    # Scanned enemy designs: basic intel omits slot-assignments; full
    # (penetrating) intel carries them.
    assert len(view.scanned_designs) == 2
    basic, full = view.scanned_designs
    assert basic.name == "Pirate Raider"
    assert basic.owner_player_id == 1
    assert basic.design_slot == 2
    assert basic.years_since_last_scan == 4
    assert basic.slot_assignments is None
    assert full.kind.value == "starbase"
    assert full.slot_assignments is not None
    assert full.slot_assignments[0].count == 8

    assert len(view.messages) == 1
    msg = view.messages[0]
    assert msg.message_type == "PlanetProductionQueueEmpty"
    assert msg.related_object == 1
    assert msg.important is True

    assert view.score.total == 5
    assert view.score.planet_count == 1
    assert view.score.resource_amount == 125
    assert view.score.resource_points == 4

    assert view.race.name == "Humanoid"
    assert view.race.prt.value == "JOAT"
    assert view.race.hab.radiation.immune is True

    # Round-trip back to kebab-case wire JSON and re-validate against the schema.
    # mode="json" renders enums (e.g. ship-design kind) as their wire values.
    redumped = view.model_dump(mode="json", by_alias=True, exclude_none=True)
    jsonschema.validate(redumped, _schema())
