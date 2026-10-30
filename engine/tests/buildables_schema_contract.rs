// Contract test: the GET /model/buildables response the engine serializes must
// validate against schemas/response-model-buildables.json, the single source of
// truth for that wire shape. If the engine's output and the schema ever
// disagree, this fails — the anti-drift guard for the buildable registry.
// Mirrors starbase_hulls_schema_contract; the buildables schema is
// self-contained (no cross-file $refs), so no merge is needed.

use serde_json::Value;

use stars_engine::http::buildables_response;

fn buildables_schema() -> Value {
    let text = std::fs::read_to_string("../schemas/response-model-buildables.json")
        .expect("read response-model-buildables.json");
    serde_json::from_str(&text).expect("parse schema")
}

#[test]
fn buildables_response_matches_the_schema() {
    let schema = buildables_schema();
    let validator = jsonschema::validator_for(&schema).expect("compile buildables schema");

    let instance = serde_json::to_value(buildables_response()).expect("serialize buildables");
    let errors: Vec<String> = validator
        .iter_errors(&instance)
        .map(|e| e.to_string())
        .collect();
    assert!(
        errors.is_empty(),
        "buildables response does not match response-model-buildables.json:\n  {}",
        errors.join("\n  ")
    );

    // Guard against a vacuous pass: the registry must actually produce items.
    let list = instance["buildables"].as_array().expect("buildables array");
    assert!(
        list.len() > 12,
        "expected fixed buildables plus design slots"
    );

    // A fixed installation keeps its original item id and carries no design-slot.
    let factory = list
        .iter()
        .find(|b| b["kind"] == "factory")
        .expect("factory present");
    assert_eq!(factory["build-object-id"], 7);
    assert_eq!(factory["category"], "installation");
    assert!(
        factory.get("design-slot").is_none(),
        "a fixed buildable must omit design-slot, not send null"
    );

    // A design-slot buildable carries design-slot and the ship-design category.
    let design0 = list
        .iter()
        .find(|b| b["build-object-id"] == 1024)
        .expect("design slot 0 present (build-object-id 1024)");
    assert_eq!(design0["kind"], "design");
    assert_eq!(design0["category"], "ship-design");
    assert_eq!(design0["design-slot"], 0);
}
