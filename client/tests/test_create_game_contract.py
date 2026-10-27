"""Contract test: the generated CreateGameResponse model and
schemas/response-create-new-game.json must agree on the create-game response
wire shape the engine produces."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client" / "src"))

from data.generated.create_game import CreateGameResponse  # noqa: E402

SUCCESS = {
    "request-is-valid": True,
    "created-game": {"id": "11111111-1111-4111-8111-111111111111"},
}
FAILURE = {"request-is-valid": False, "failure-reason": "invalid universe size"}


def _schema() -> dict:
    return json.loads((REPO / "schemas" / "response-create-new-game.json").read_text())


@pytest.mark.parametrize("payload", [SUCCESS, FAILURE])
def test_validates_against_schema(payload: dict) -> None:
    jsonschema.validate(payload, _schema())


@pytest.mark.parametrize("payload", [SUCCESS, FAILURE])
def test_parses_through_generated_model(payload: dict) -> None:
    response = CreateGameResponse.model_validate(payload)
    redumped = response.model_dump(by_alias=True, exclude_none=True)
    jsonschema.validate(redumped, _schema())


def test_success_carries_created_game_id() -> None:
    response = CreateGameResponse.model_validate(SUCCESS)
    assert response.request_is_valid is True
    assert response.created_game is not None
    assert response.created_game.id == "11111111-1111-4111-8111-111111111111"
