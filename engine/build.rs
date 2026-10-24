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
use typify::{TypeSpace, TypeSpaceSettings};

// (schema file stem, output file) pairs. Grows as more schemas gain generated
// engine types.
const SCHEMAS: &[(&str, &str)] = &[
    ("race", "race_types.rs"),
    ("response-turn-file", "turn_file_types.rs"),
    ("response-game", "universe_file_types.rs"),
    ("response-create-new-game", "create_game_types.rs"),
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

        let mut type_space = TypeSpace::new(&TypeSpaceSettings::default());
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
    strip_file_prefixes(&mut root);
    root
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
            if let Some(Value::String(r)) = m.get("$ref") {
                if let Some((file, _)) = r.split_once('#') {
                    if !file.is_empty() {
                        out.insert(file.to_string());
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

// Rewrite every `"$ref": "file.json#/foo"` to `"#/foo"` (local).
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
