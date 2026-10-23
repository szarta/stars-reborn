"""Contract test: the generated pydantic Race model and schemas/race.json must
agree on the wire shape the engine produces.

Canonical race payloads (captured from the engine's serializer) are validated
against schemas/race.json with jsonschema AND parsed through the generated
model. If the schema, the generated model, or the engine wire format ever drift
apart, this test fails. This is the Python half of the task #110 anti-drift
guard (the Rust half is engine/tests/race_schema_contract.rs).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client" / "src"))

from data.generated.race import Prt, Race  # noqa: E402

# Ground-truth payloads as the engine serializes them (see race_defaults.rs).
HUMANOID = {
    "format_version": 1,
    "name": "Humanoid",
    "plural_name": "Humanoids",
    "prt": "JOAT",
    "lrts": [],
    "hab": {
        "gravity": {"immune": False, "min_idx": 15, "max_idx": 85},
        "temperature": {"immune": False, "min_idx": 15, "max_idx": 85},
        "radiation": {"immune": False, "min_idx": 15, "max_idx": 85},
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
        "expensive_tech_boost": False,
    },
    "leftover_spend": "surface_minerals",
    "icon_index": 0,
}

# Exercises the other HabAxis shapes: an immune axis and axes with physical
# min/max as well as indices, plus a populated LRT list.
INSECTOID = {
    "format_version": 1,
    "name": "Insectoid",
    "plural_name": "Insectoids",
    "prt": "WM",
    "lrts": ["ISB", "CE", "RS"],
    "hab": {
        "gravity": {"immune": True},
        "temperature": {
            "immune": False,
            "min": -200.0,
            "max": 200.0,
            "min_idx": 0,
            "max_idx": 100,
        },
        "radiation": {
            "immune": False,
            "min": 70.0,
            "max": 100.0,
            "min_idx": 70,
            "max_idx": 100,
        },
    },
    "economy": {
        "resource_production": 1000,
        "factory_production": 10,
        "factory_cost": 10,
        "factory_cheap_germanium": False,
        "colonists_operate_factories": 10,
        "mine_production": 9,
        "mine_cost": 10,
        "colonists_operate_mines": 6,
        "growth_rate": 10,
    },
    "research_costs": {
        "energy": "cheap",
        "weapons": "cheap",
        "propulsion": "cheap",
        "construction": "cheap",
        "electronics": "normal",
        "biotechnology": "expensive",
        "expensive_tech_boost": False,
    },
    "leftover_spend": "surface_minerals",
    "icon_index": 3,
}

RACES = [HUMANOID, INSECTOID]


def _race_schema() -> dict:
    """draft-07 schema for #/definitions/race with definitions attached."""
    doc = json.loads((REPO / "schemas" / "race.json").read_text())
    schema = dict(doc["definitions"]["race"])
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    schema["definitions"] = doc["definitions"]
    return schema


@pytest.mark.parametrize("payload", RACES, ids=lambda p: p["name"])
def test_payload_validates_against_schema(payload: dict) -> None:
    jsonschema.validate(payload, _race_schema())


@pytest.mark.parametrize("payload", RACES, ids=lambda p: p["name"])
def test_payload_parses_through_generated_model(payload: dict) -> None:
    race = Race.model_validate(payload)
    # Round-trip back to wire JSON and confirm it still satisfies the schema.
    redumped = race.model_dump(mode="json", exclude_none=True)
    jsonschema.validate(redumped, _race_schema())


def test_parsed_values_are_faithful() -> None:
    race = Race.model_validate(INSECTOID)
    assert race.prt is Prt.WM
    assert [lrt.value for lrt in race.lrts] == ["ISB", "CE", "RS"]
    assert race.hab.gravity.immune is True
    assert race.hab.temperature.min == -200.0
    assert race.economy.growth_rate == 10
