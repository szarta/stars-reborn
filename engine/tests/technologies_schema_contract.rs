// Guard test for schemas/response-model-technologies.json, the single source of
// truth for the GET /model/technologies wire shape.
//
// The engine producer for this endpoint does not exist yet — the catalog of
// ~300 component items with oracle-verified values is a tracked follow-up, and
// the handler currently returns 501. So, unlike ship_hulls_schema_contract,
// this test cannot yet validate real engine output against the schema. Instead
// it guards the schema itself: it compiles (so every $ref resolves and the
// draft-07 document is well-formed) and it accepts representative tech-items
// while rejecting malformed ones. When the producer lands, add an assertion
// that its output validates here, mirroring ship_hulls_response().
//
// response-model-technologies.json references tech.json (ids, cost,
// tech-requirements) and race.json (prt, lrt enums). typify resolves those in
// build.rs via its bundler; here we do the equivalent merge so the validator
// sees one self-contained schema.

use serde_json::{json, Value};

use stars_engine::http::technologies_response;

/// Build the response schema with tech.json's and race.json's definitions
/// merged in and all cross-file `*.json#/...` refs rewritten local.
fn technologies_schema() -> Value {
    let text = std::fs::read_to_string("../schemas/response-model-technologies.json")
        .expect("read response-model-technologies.json");
    let mut schema: Value = serde_json::from_str(&text).expect("parse schema");

    let defs = schema["definitions"]
        .as_object_mut()
        .expect("definitions")
        .clone();
    let mut merged = defs;
    for file in ["tech.json", "race.json"] {
        let other_text =
            std::fs::read_to_string(format!("../schemas/{file}")).expect("read referenced schema");
        let other: Value = serde_json::from_str(&other_text).expect("parse referenced schema");
        for (name, def) in other["definitions"].as_object().expect("definitions") {
            merged.entry(name.clone()).or_insert_with(|| def.clone());
        }
    }
    schema["definitions"] = Value::Object(merged);
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

fn cost() -> Value {
    json!({"ironium": 0, "boranium": 0, "germanium": 1, "resources": 3})
}

fn reqs() -> Value {
    json!({
        "energy": 0, "weapons": 0, "propulsion": 1,
        "construction": 0, "electronics": 0, "biotechnology": 0
    })
}

#[test]
fn technologies_schema_compiles() {
    let schema = technologies_schema();
    jsonschema::validator_for(&schema).expect("compile response-model-technologies schema");
}

#[test]
fn schema_accepts_representative_items() {
    let schema = technologies_schema();
    let validator = jsonschema::validator_for(&schema).expect("compile schema");

    // One ship-installable part (engine) and one non-installable planetary
    // tech, exercising the common fields, the mass/no-mass split, a trait gate,
    // and two of the category-specific `properties` shapes.
    let instance = json!({
        "technologies": [
            {
                "id": 60,
                "slug": "long_hump_6",
                "name": "Long Hump 6",
                "category": "engines",
                "requirement": null,
                "mass": 9,
                "cost": cost(),
                "tech-requirements": reqs(),
                "properties": {
                    "fuel-usage": [0, 0, 0, 0, 0, 60, 72, 100, 126, 177, 300],
                    "battle-speed": 10,
                    "warp10-travel": true,
                    "last-free-warp": 4
                }
            },
            {
                "id": 160,
                "slug": "gravity_terraform_3",
                "name": "Gravity Terraform ±3",
                "category": "planetary",
                "requirement": {"prt": ["CA"]},
                "cost": cost(),
                "tech-requirements": reqs(),
                "properties": {
                    "kind": "terraforming",
                    "gravity": 3,
                    "temperature": 0,
                    "radiation": 0
                }
            }
        ]
    });

    let errors: Vec<String> = validator
        .iter_errors(&instance)
        .map(|e| e.to_string())
        .collect();
    assert!(
        errors.is_empty(),
        "representative tech-items should validate:\n  {}",
        errors.join("\n  ")
    );
}

#[test]
fn schema_rejects_unknown_category_and_fields() {
    let schema = technologies_schema();
    let validator = jsonschema::validator_for(&schema).expect("compile schema");

    // Unknown category value.
    let bad_category = json!({
        "technologies": [{
            "id": 1, "slug": "x", "name": "X", "category": "wormholes",
            "requirement": null, "cost": cost(), "tech-requirements": reqs(),
            "properties": {"basic-range": 0, "penetrating-range": 0}
        }]
    });
    assert!(
        !validator.is_valid(&bad_category),
        "an unknown category must be rejected"
    );

    // Extra top-level field on a tech-item (additionalProperties: false).
    let extra_field = json!({
        "technologies": [{
            "id": 1, "slug": "x", "name": "X", "category": "scanners",
            "requirement": null, "cost": cost(), "tech-requirements": reqs(),
            "properties": {"basic-range": 100, "penetrating-range": 0},
            "bogus": true
        }]
    });
    assert!(
        !validator.is_valid(&extra_field),
        "an unknown tech-item field must be rejected"
    );

    // Category/properties mismatch: 'engines' with scanner-shaped properties.
    // The if/then discrimination on 'category' must reject this.
    let mismatch = json!({
        "technologies": [{
            "id": 1, "slug": "x", "name": "X", "category": "engines",
            "requirement": null, "mass": 9, "cost": cost(), "tech-requirements": reqs(),
            "properties": {"basic-range": 100, "penetrating-range": 0}
        }]
    });
    assert!(
        !validator.is_valid(&mismatch),
        "properties that do not match the category must be rejected"
    );
}

#[test]
fn engine_output_matches_the_schema() {
    // The real GET /model/technologies producer (task #144 slice: engines,
    // armor, shields, orbital) must validate against the schema.
    let schema = technologies_schema();
    let validator = jsonschema::validator_for(&schema).expect("compile schema");

    let instance = technologies_response();
    let errors: Vec<String> = validator
        .iter_errors(&instance)
        .map(|e| e.to_string())
        .collect();
    assert!(
        errors.is_empty(),
        "technologies response does not match response-model-technologies.json:\n  {}",
        errors.join("\n  ")
    );

    // Guard against a vacuous pass: the slice ships 52 items across four
    // categories (16 engines, 11 armor, 9 shields, 16 orbital).
    let techs = instance["technologies"]
        .as_array()
        .expect("technologies array");
    assert_eq!(
        techs.len(),
        52,
        "unexpected catalog size for the #144 slice"
    );
    let has = |cat: &str| techs.iter().any(|t| t["category"] == cat);
    for cat in ["engines", "armor", "shields", "orbital"] {
        assert!(has(cat), "catalog is missing category {cat}");
    }

    // Orbital items carry no mass; installable parts do.
    for t in techs {
        if t["category"] == "orbital" {
            assert!(t.get("mass").is_none(), "orbital items must not carry mass");
        } else {
            assert!(t.get("mass").is_some(), "installable parts must carry mass");
        }
    }
}
