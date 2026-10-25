// Contract test: the GET /model/ships/hulls response the engine serializes must
// validate against schemas/response-model-ship-hulls.json, the single source of
// truth for that wire shape. If the engine's output and the schema ever
// disagree, this fails — the anti-drift guard for the ship-hull catalog.
//
// response-model-ship-hulls.json references tech.json (cost, tech-requirements,
// slot-type, id). typify resolves that in build.rs via its bundler; here we do
// the equivalent merge so the validator sees one self-contained schema.

use serde_json::Value;

use stars_engine::http::ship_hulls_response;

/// Build the response schema with tech.json's definitions merged in and the
/// cross-file `tech.json#/...` refs rewritten local, so every `$ref` resolves.
fn ship_hulls_schema() -> Value {
    let text = std::fs::read_to_string("../schemas/response-model-ship-hulls.json")
        .expect("read response-model-ship-hulls.json");
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
fn ship_hulls_response_matches_the_schema() {
    let schema = ship_hulls_schema();
    let validator = jsonschema::validator_for(&schema).expect("compile ship-hulls schema");

    let instance = ship_hulls_response();
    let errors: Vec<String> = validator
        .iter_errors(&instance)
        .map(|e| e.to_string())
        .collect();
    assert!(
        errors.is_empty(),
        "ship-hulls response does not match response-model-ship-hulls.json:\n  {}",
        errors.join("\n  ")
    );

    // Guard against a vacuous pass: the catalog must actually produce hulls.
    assert!(
        !instance["hulls"]
            .as_array()
            .expect("hulls array")
            .is_empty(),
        "ship-hull catalog is empty"
    );
}
