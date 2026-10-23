// Contract test: the create-game response the engine serializes must validate
// against schemas/response-create-new-game.json (task #115).

use stars_engine::game::objects::generated::create_game::{CreateGameResponse, CreatedGame};

fn validate(response: &CreateGameResponse) {
    let text =
        std::fs::read_to_string("../schemas/response-create-new-game.json").expect("read schema");
    let schema: serde_json::Value = serde_json::from_str(&text).expect("parse schema");
    let validator = jsonschema::validator_for(&schema).expect("compile schema");

    let instance = serde_json::to_value(response).expect("serialize");
    let errors: Vec<String> = validator
        .iter_errors(&instance)
        .map(|e| e.to_string())
        .collect();
    assert!(
        errors.is_empty(),
        "response does not match response-create-new-game.json:\n  {}",
        errors.join("\n  ")
    );
}

#[test]
fn success_response_matches_schema() {
    validate(&CreateGameResponse {
        request_is_valid: true,
        created_game: Some(CreatedGame {
            id: "11111111-1111-4111-8111-111111111111".to_string(),
        }),
        failure_reason: None,
    });
}

#[test]
fn failure_response_matches_schema() {
    validate(&CreateGameResponse {
        request_is_valid: false,
        created_game: None,
        failure_reason: Some("invalid universe size".to_string()),
    });
}
