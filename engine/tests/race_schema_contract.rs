// Contract test: every race the engine serializes must validate against
// schemas/race.json (the single source of truth the wire types are generated
// from). If the engine and the schema ever disagree on the Race wire shape,
// this test fails — that is the anti-drift guard for task #110.

use serde_json::{json, Value};
use stars_engine::game::objects::race_defaults;

/// Build a standalone draft-07 schema for `#/definitions/race` with the file's
/// `definitions` attached so internal `$ref`s still resolve.
fn race_schema() -> Value {
    let text = std::fs::read_to_string("../schemas/race.json").expect("read schemas/race.json");
    let file: Value = serde_json::from_str(&text).expect("parse schemas/race.json");
    let mut schema = file["definitions"]["race"].clone();
    schema["$schema"] = json!("http://json-schema.org/draft-07/schema#");
    schema["definitions"] = file["definitions"].clone();
    schema
}

#[test]
fn all_default_races_match_the_schema() {
    let schema = race_schema();
    let validator = jsonschema::validator_for(&schema).expect("compile race schema");

    for name in [
        "Humanoid",
        "Insectoid",
        "Antetheral",
        "Rabbitoid",
        "Nucleotid",
        "Silicanoid",
    ] {
        let race = race_defaults::default_race_by_name(name).expect(name);
        let instance = serde_json::to_value(&race).expect("serialize race");

        let errors: Vec<String> = validator
            .iter_errors(&instance)
            .map(|e| e.to_string())
            .collect();
        assert!(
            errors.is_empty(),
            "{name} does not match schemas/race.json:\n  {}",
            errors.join("\n  ")
        );
    }
}
