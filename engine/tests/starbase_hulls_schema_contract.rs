// Contract test: the GET /model/starbase/hulls response the engine serializes
// must validate against schemas/response-model-starbase-hulls.json, the single
// source of truth for that wire shape. If the engine's output and the schema
// ever disagree, this fails — the anti-drift guard for the starbase-hull
// catalog. Mirrors ship_hulls_schema_contract.
//
// response-model-starbase-hulls.json references tech.json (cost,
// tech-requirements, slot-type, starbase-hull-id). typify resolves that in
// build.rs via its bundler; here we do the equivalent merge so the validator
// sees one self-contained schema.

use serde_json::Value;

use stars_engine::http::starbase_hulls_response;

/// Build the response schema with tech.json's definitions merged in and the
/// cross-file `tech.json#/...` refs rewritten local, so every `$ref` resolves.
fn starbase_hulls_schema() -> Value {
    let text = std::fs::read_to_string("../schemas/response-model-starbase-hulls.json")
        .expect("read response-model-starbase-hulls.json");
    let mut schema: Value = serde_json::from_str(&text).expect("parse schema");
    let tech_text = std::fs::read_to_string("../schemas/tech.json").expect("read tech.json");
    let tech: Value = serde_json::from_str(&tech_text).expect("parse tech.json");

    let defs = schema["definitions"].as_object_mut().expect("definitions");
    for (name, def) in tech["definitions"].as_object().expect("tech definitions") {
        defs.entry(name.clone()).or_insert_with(|| def.clone());
    }
    strip_file_prefixes(&mut schema);
    schema
}

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

#[test]
fn starbase_hulls_response_matches_the_schema() {
    let schema = starbase_hulls_schema();
    let validator = jsonschema::validator_for(&schema).expect("compile starbase-hulls schema");

    let instance =
        serde_json::to_value(starbase_hulls_response()).expect("serialize starbase-hulls");
    let errors: Vec<String> = validator
        .iter_errors(&instance)
        .map(|e| e.to_string())
        .collect();
    assert!(
        errors.is_empty(),
        "starbase-hulls response does not match response-model-starbase-hulls.json:\n  {}",
        errors.join("\n  ")
    );

    // Guard against a vacuous pass: the catalog must actually produce hulls.
    let hulls = instance["hulls"].as_array().expect("hulls array");
    assert_eq!(hulls.len(), 5, "expected the five canonical starbase hulls");

    // Orbital Fort has a finite dock (0); Space Station is unlimited (absent).
    let fort = hulls
        .iter()
        .find(|h| h["slug"] == "orbital_fort")
        .expect("orbital_fort present");
    assert_eq!(fort["dock-capacity"], 0);
    let station = hulls
        .iter()
        .find(|h| h["slug"] == "space_station")
        .expect("space_station present");
    assert!(
        station.get("dock-capacity").is_none(),
        "unlimited dock must be absent, not present"
    );
}
