// build.rs — generate Rust wire types from the JSON Schema single source of truth.
//
// For each schema in ../schemas that defines engine-facing types, typify emits
// serde structs/enums into OUT_DIR, which src/game/objects/generated.rs includes.
// This runs on every compile, so the Rust types cannot drift from the schema:
// change the contract by editing the schema, never the generated code. See
// docs/adr/0003.

use std::collections::BTreeSet;
use std::path::Path;

use serde_json::Value;
use typify::{CrateVers, TypeSpace, TypeSpaceSettings};

// (schema file stem, output file) pairs. Grows as more schemas gain generated
// engine types.
const SCHEMAS: &[(&str, &str)] = &[
    ("race", "race_types.rs"),
    ("response-turn-file", "turn_file_types.rs"),
    ("response-game", "universe_file_types.rs"),
    ("response-create-new-game", "create_game_types.rs"),
    ("response-validate-race", "validate_race_types.rs"),
    // Host-side authoritative game state (game.json / .sr save). References
    // race.json; the bundler below resolves that cross-file ref for typify.
    ("game-state", "game_state_types.rs"),
];

fn main() {
    let schema_dir = Path::new("../schemas");
    let out_dir = std::env::var("OUT_DIR").expect("OUT_DIR not set");

    // Rebuild if any schema changes — a schema may pull in others via $ref.
    for entry in std::fs::read_dir(schema_dir).expect("read schemas dir") {
        let path = entry.expect("schema dir entry").path();
        if path.extension().and_then(|e| e.to_str()) == Some("json") {
            println!("cargo:rerun-if-changed={}", path.display());
        }
    }

    for (stem, out_file) in SCHEMAS {
        let schema_path = schema_dir.join(format!("{stem}.json"));

        let content = std::fs::read_to_string(&schema_path)
            .unwrap_or_else(|e| panic!("reading {}: {e}", schema_path.display()));
        let root: Value = serde_json::from_str(&content)
            .unwrap_or_else(|e| panic!("parsing {} as JSON: {e}", schema_path.display()));

        let bundled = bundle(root, schema_dir);
        let schema: schemars::schema::RootSchema = serde_json::from_value(bundled)
            .unwrap_or_else(|e| panic!("parsing {} as JSON Schema: {e}", schema_path.display()));

        let mut settings = TypeSpaceSettings::default();
        // `x-rust-type` annotations point at this crate's own hand-written
        // modules (e.g. race.json#/definitions/race -> objects::race::Race) so
        // a shared object is generated once and merely re-used here. typify
        // emits the absolute path `::stars_engine::...`; the engine's lib root
        // carries `extern crate self as stars_engine;` so it resolves from
        // inside the engine itself.
        settings.with_crate("stars-engine", CrateVers::Any, None);
        let mut type_space = TypeSpace::new(&settings);
        type_space
            .add_root_schema(schema)
            .unwrap_or_else(|e| panic!("typify on {}: {e}", schema_path.display()));

        let tokens = type_space.to_stream();
        let file: syn::File = syn::parse2(tokens)
            .unwrap_or_else(|e| panic!("parsing generated tokens for {stem}: {e}"));
        let rendered = prettyplease::unparse(&file);

        std::fs::write(Path::new(&out_dir).join(out_file), rendered)
            .unwrap_or_else(|e| panic!("writing {out_file}: {e}"));
    }

    println!("cargo:rerun-if-changed=build.rs");
}

// Resolve cross-file `$ref`s into a single self-contained draft-07 schema:
// typify cannot follow a `other.json#/definitions/x` reference, so merge every
// referenced file's `definitions` into this schema's `definitions` (by bare
// name) and rewrite all `$ref`s to local `#/definitions/<name>`. A schema with
// no cross-file refs passes through unchanged. Referenced files are assumed
// self-contained (their own refs are already local); this is checked by the
// contract tests. On a bare-name collision the existing definition wins.
//
// A `$ref` that also carries an `x-rust-type` sibling is a redirect to a type
// already generated elsewhere in this crate (e.g. `race.json#/definitions/race`
// -> `objects::race::Race`). typify's `x-rust-type` handling takes precedence
// over the `$ref`, so such a shape must NOT be inlined — its referenced file is
// skipped here and the redundant `$ref` is dropped so typify emits only the
// native type (no duplicate generated copy, no dangling local ref). The on-disk
// schema keeps the `$ref` so the JSON Schema validators (contract tests) still
// resolve and check the shape.
fn bundle(mut root: Value, schema_dir: &Path) -> Value {
    let mut merged: BTreeSet<String> = BTreeSet::new();
    loop {
        let pending: Vec<String> = referenced_files(&root)
            .into_iter()
            .filter(|f| !merged.contains(f))
            .collect();
        if pending.is_empty() {
            break;
        }
        for file in pending {
            let path = schema_dir.join(&file);
            let content = std::fs::read_to_string(&path)
                .unwrap_or_else(|e| panic!("reading $ref'd {}: {e}", path.display()));
            let other: Value = serde_json::from_str(&content)
                .unwrap_or_else(|e| panic!("parsing $ref'd {}: {e}", path.display()));

            if !root
                .get("definitions")
                .map(Value::is_object)
                .unwrap_or(false)
            {
                root["definitions"] = Value::Object(serde_json::Map::new());
            }
            if let Some(other_defs) = other.get("definitions").and_then(Value::as_object) {
                let root_defs = root["definitions"].as_object_mut().unwrap();
                for (name, def) in other_defs {
                    root_defs.entry(name.clone()).or_insert_with(|| def.clone());
                }
            }
            merged.insert(file);
        }
    }
    expand_rust_map_keys(&mut root);
    strip_file_prefixes(&mut root);
    root
}

// Expand the `x-rust-map-key` vendor hint into a `propertyNames` schema that
// typify reads to choose the map's Rust KEY type (e.g. `HashMap<u32, V>`
// instead of `HashMap<String, V>`). JSON object keys are always strings on the
// wire, so a literal `propertyNames: {type: integer}` would be invalid to a
// JSON Schema validator (every key is a string) — hence this generation-only
// hint, which validators ignore as an unknown keyword, is expanded here just
// before typify sees the schema and never ships in the on-disk schema's
// meaning. serde round-trips the integer key through the string JSON key, so
// the wire shape is unchanged. Supported values: `uint32`, `int32`.
fn expand_rust_map_keys(v: &mut Value) {
    match v {
        Value::Object(m) => {
            if let Some(Value::String(key_fmt)) = m.remove("x-rust-map-key") {
                let (ty, fmt) = match key_fmt.as_str() {
                    "uint32" => ("integer", "uint32"),
                    "int32" => ("integer", "int32"),
                    other => panic!("unsupported x-rust-map-key value {other:?}"),
                };
                m.insert(
                    "propertyNames".to_string(),
                    serde_json::json!({ "type": ty, "format": fmt }),
                );
            }
            for val in m.values_mut() {
                expand_rust_map_keys(val);
            }
        }
        Value::Array(a) => {
            for val in a.iter_mut() {
                expand_rust_map_keys(val);
            }
        }
        _ => {}
    }
}

// Collect the file portion of every `"$ref": "file.json#/..."` in the document.
fn referenced_files(v: &Value) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    walk_refs(v, &mut out);
    out
}

fn walk_refs(v: &Value, out: &mut BTreeSet<String>) {
    match v {
        Value::Object(m) => {
            // A ref redirected by x-rust-type is not inlined (see `bundle`).
            if m.get("x-rust-type").is_none() {
                if let Some(Value::String(r)) = m.get("$ref") {
                    if let Some((file, _)) = r.split_once('#') {
                        if !file.is_empty() {
                            out.insert(file.to_string());
                        }
                    }
                }
            }
            for val in m.values() {
                walk_refs(val, out);
            }
        }
        Value::Array(a) => {
            for val in a {
                walk_refs(val, out);
            }
        }
        _ => {}
    }
}

// Rewrite every `"$ref": "file.json#/foo"` to `"#/foo"` (local). On a node that
// also carries `x-rust-type`, drop the `$ref` entirely instead: typify uses the
// native type and the referenced definitions are deliberately absent, so a
// rewritten local ref would dangle.
fn strip_file_prefixes(v: &mut Value) {
    match v {
        Value::Object(m) => {
            if m.contains_key("x-rust-type") {
                m.remove("$ref");
            } else if let Some(Value::String(r)) = m.get_mut("$ref") {
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
