// Guard: every `$ref` in every schema under schemas/ must resolve — both the
// local `#/definitions/...` form and the cross-file `file.json#/definitions/...`
// form the bundler and validators depend on. A dangling ref compiles fine and
// passes the per-schema contract tests (which bundle only their own cluster),
// so this is the only thing that catches a typo'd target name or a ref to a
// file/def that does not exist. It exists because the draft-04 design-target
// sketches (universe/planet/player.json) carried exactly such dangling refs
// (`planets.json#/...`, `#/definitions/warp-speed`) that no other test touched.
//
// The on-disk `$ref` is authoritative even where an `x-rust-type` sibling
// redirects code generation to an existing Rust type: the README requires the
// ref to still resolve so JSON Schema validators can follow the shape. So this
// guard checks the ref regardless of any `x-rust-type` sibling.

use std::collections::HashMap;
use std::path::Path;

use serde_json::Value;

/// Load every `schemas/*.json` as (file name -> parsed root).
fn load_schemas() -> HashMap<String, Value> {
    let dir = Path::new("../schemas");
    let mut out = HashMap::new();
    for entry in std::fs::read_dir(dir).expect("read schemas dir") {
        let path = entry.expect("dir entry").path();
        if path.extension().and_then(|e| e.to_str()) != Some("json") {
            continue;
        }
        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .expect("file name")
            .to_string();
        let text = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("read {name}: {e}"));
        let value: Value =
            serde_json::from_str(&text).unwrap_or_else(|e| panic!("parse {name}: {e}"));
        out.insert(name, value);
    }
    out
}

/// Resolve an RFC-6901 JSON pointer (`/definitions/foo`) against `root`.
fn resolve_pointer<'a>(root: &'a Value, pointer: &str) -> Option<&'a Value> {
    if pointer.is_empty() {
        return Some(root);
    }
    let mut cur = root;
    for raw in pointer.trim_start_matches('/').split('/') {
        let token = raw.replace("~1", "/").replace("~0", "~");
        cur = match cur {
            Value::Object(m) => m.get(&token)?,
            Value::Array(a) => a.get(token.parse::<usize>().ok()?)?,
            _ => return None,
        };
    }
    Some(cur)
}

/// Collect every `$ref` string found anywhere under `v`.
fn collect_refs(v: &Value, out: &mut Vec<String>) {
    match v {
        Value::Object(m) => {
            if let Some(Value::String(r)) = m.get("$ref") {
                out.push(r.clone());
            }
            for val in m.values() {
                collect_refs(val, out);
            }
        }
        Value::Array(a) => {
            for val in a.iter() {
                collect_refs(val, out);
            }
        }
        _ => {}
    }
}

#[test]
fn every_schema_ref_resolves() {
    let schemas = load_schemas();
    let mut failures = Vec::new();

    for (file, root) in &schemas {
        let mut refs = Vec::new();
        collect_refs(root, &mut refs);
        for r in refs {
            // Split "file.json#/fragment" into (optional file, fragment).
            let (file_part, fragment) = match r.split_once('#') {
                Some((f, frag)) => (f, frag),
                None => (r.as_str(), ""),
            };
            let (target_file, target_root) = if file_part.is_empty() {
                (file.as_str(), root)
            } else {
                match schemas.get(file_part) {
                    Some(t) => (file_part, t),
                    None => {
                        failures.push(format!("{file}: $ref \"{r}\" -> no such schema file"));
                        continue;
                    }
                }
            };
            if resolve_pointer(target_root, fragment).is_none() {
                failures.push(format!(
                    "{file}: $ref \"{r}\" -> \"{fragment}\" not found in {target_file}"
                ));
            }
        }
    }

    assert!(
        failures.is_empty(),
        "unresolvable $ref(s) in schemas/:\n  {}",
        failures.join("\n  ")
    );
}
