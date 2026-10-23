// build.rs — generate Rust wire types from the JSON Schema single source of truth.
//
// For each schema in ../schemas that defines engine-facing types, typify emits
// serde structs/enums into OUT_DIR, which src/game/objects/generated.rs includes.
// This runs on every compile, so the Rust types cannot drift from the schema:
// change the contract by editing the schema, never the generated code. See
// docs/adr/0003.

use std::path::Path;
use typify::{TypeSpace, TypeSpaceSettings};

// (schema file stem, output file) pairs. Grows as more schemas gain generated
// engine types; today the race contract is the pilot (task #110).
const SCHEMAS: &[(&str, &str)] = &[("race", "race_types.rs")];

fn main() {
    let schema_dir = Path::new("../schemas");
    let out_dir = std::env::var("OUT_DIR").expect("OUT_DIR not set");

    for (stem, out_file) in SCHEMAS {
        let schema_path = schema_dir.join(format!("{stem}.json"));
        println!("cargo:rerun-if-changed={}", schema_path.display());

        let content = std::fs::read_to_string(&schema_path)
            .unwrap_or_else(|e| panic!("reading {}: {e}", schema_path.display()));
        let schema: schemars::schema::RootSchema = serde_json::from_str(&content)
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
