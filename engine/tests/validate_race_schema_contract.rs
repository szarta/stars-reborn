// Contract test for POST /race/validate, both directions:
//   request  — a bare Race must satisfy schemas/request-validate-race.json
//              (which $refs race.json).
//   response — what the engine serializes must satisfy
//              schemas/response-validate-race.json.
// If the engine and either schema drift apart, this fails.

use serde_json::{json, Value};

use stars_engine::game::objects::race_defaults::default_race_by_name;
use stars_engine::http::validate_race_response;

/// Rewrite `"$ref": "file.json#/foo"` to `"#/foo"` throughout (mirrors build.rs).
fn strip_file_prefixes(v: &mut Value) {
    match v {
        Value::Object(m) => {
            if let Some(Value::String(r)) = m.get_mut("$ref") {
                if let Some(idx) = r.find('#') {
                    if idx > 0 {
                        *r = r[idx..].to_string();
                    }
                }
            }
            for val in m.values_mut() {
                strip_file_prefixes(val);
            }
        }
        Value::Array(a) => {
            for val in a.iter_mut() {
                strip_file_prefixes(val);
            }
        }
        _ => {}
    }
}

fn errors(schema: &Value, instance: &Value) -> Vec<String> {
    let validator = jsonschema::validator_for(schema).expect("compile schema");
    validator
        .iter_errors(instance)
        .map(|e| e.to_string())
        .collect()
}

#[test]
fn race_validate_request_accepts_a_bare_race() {
    // request-validate-race.json is a thin $ref to race.json#/definitions/race;
    // merge race.json's definitions and localize the ref so it resolves.
    let req_text = std::fs::read_to_string("../schemas/request-validate-race.json")
        .expect("read request-validate-race.json");
    let mut schema: Value = serde_json::from_str(&req_text).expect("parse request schema");
    let race_text = std::fs::read_to_string("../schemas/race.json").expect("read race.json");
    let race_file: Value = serde_json::from_str(&race_text).expect("parse race.json");
    schema["definitions"] = race_file["definitions"].clone();
    strip_file_prefixes(&mut schema);

    let race = default_race_by_name("Humanoid").expect("Humanoid");
    let instance = serde_json::to_value(&race).expect("serialize race");
    let errs = errors(&schema, &instance);
    assert!(
        errs.is_empty(),
        "race rejected by request schema:\n  {}",
        errs.join("\n  ")
    );
}

#[test]
fn race_validate_response_matches_the_schema() {
    let text = std::fs::read_to_string("../schemas/response-validate-race.json")
        .expect("read response-validate-race.json");
    let schema: Value = serde_json::from_str(&text).expect("parse response schema");

    // Valid race: failure_reason omitted.
    let race = default_race_by_name("Humanoid").expect("Humanoid");
    let resp = validate_race_response(&race);
    assert!(resp.valid, "a default race should be legal");
    let instance = serde_json::to_value(&resp).expect("serialize response");
    assert!(
        instance.get("failure-reason").is_none(),
        "failure-reason must be omitted when valid"
    );
    let errs = errors(&schema, &instance);
    assert!(
        errs.is_empty(),
        "valid response off-schema:\n  {}",
        errs.join("\n  ")
    );

    // Invalid-race shape: failure-reason present. Built directly so the test
    // does not depend on a specific overspending race existing in the catalog.
    let invalid = json!({
        "advantage-points": -42,
        "valid": false,
        "failure-reason": "race overspends its advantage-point budget by 42"
    });
    let errs = errors(&schema, &invalid);
    assert!(
        errs.is_empty(),
        "invalid response off-schema:\n  {}",
        errs.join("\n  ")
    );
}
