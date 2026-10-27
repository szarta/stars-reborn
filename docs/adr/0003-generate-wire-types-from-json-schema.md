# 0003: Generate the wire types from the JSON Schema source of truth

**Status:** Accepted, 2026-10-22. Fulfils the "later step" anticipated in
ADR-0002.

## Context

The engine (Rust) and the reference client (Python) exchange game objects as
JSON over HTTP (ADR-0001). Three things described the same wire shapes
independently: the JSON Schemas in `schemas/`, the engine's hand-written serde
structs, and — prospectively — the client's models. ADR-0002 kept the schema as
the source of truth "by convention" and left generation as a later step.

Convention was not holding. By the time this was picked up the schemas had
drifted badly from what the engine actually serialized: `race.json` was an
early, flat, full-text sketch (`"singular-name"`, `"Hyper Expansion"`) while the
engine emitted a different, nested, abbreviated shape (`"name"`, `prt: "HE"`,
nested `hab`/`economy`/`research_costs`). Nothing loaded the schemas at all, so
the drift was silent. A hand-kept contract in three places is three things to
keep in sync and three chances to forget.

## Decision

The JSON Schema in `schemas/` is the **single source of truth** for the wire
contract, and the language types are **generated from it**, never hand-written:

- **Rust (engine):** `engine/build.rs` runs `typify` over each schema on every
  compile, emitting the serde types into `OUT_DIR`;
  `engine/src/game/objects/generated.rs` includes them and the hand-written
  modules (e.g. `objects::race`) re-export them. The types are regenerated each
  build and are never committed, so they cannot be edited or drift.
- **Python (client):** `scripts/generate_types.py` runs
  `datamodel-code-generator` over each schema into
  `client/src/data/generated/`, as pydantic v2 models (validation and
  constraints carried across). This output _is_ committed, deterministically
  (no timestamps, ruff-formatted); the `generate-python-types` pre-commit hook
  and CI regenerate it and fail on any diff.

Behavior that belongs to a type but is not part of the wire shape (constructors,
the `.r1` byte decode, convenience impls) lives in the hand-written module that
re-exports the generated type, not in the schema.

The schemas are authored in draft-07 (up-converted from draft-04 so `typify`
can consume them) and must describe the shape the engine actually serializes.
Two contract tests enforce agreement in both directions:
`engine/tests/race_schema_contract.rs` validates every engine-serialized race
against the schema, and `client/tests/test_race_contract.py` validates canonical
payloads against both the schema and the generated model.

To change the contract, edit the schema; then rebuild (Rust) and run
`scripts/generate_types.py` (Python). Never edit generated code.

## Consequences

- The Rust and Python types cannot diverge from the schema or from each other:
  Rust regenerates at build time, Python is diff-checked against a fresh
  regeneration, and the contract tests fail if the engine's actual output stops
  matching the schema.
- The schema has to be wire-accurate, not aspirational. Enriching it (e.g.
  string `maxLength`, which `typify` would turn into Rust newtypes) is a
  deliberate choice weighed against the type churn it causes, not a free
  annotation.
- A new schema is wired in by adding it to the `SCHEMAS` list in `build.rs`
  and/or `scripts/generate_types.py` and giving it a contract test. Not every
  schema needs both sides (`game-state.json` is host-only, so Rust only).
- A schema may reference another by a cross-file `$ref`
  (`race.json#/definitions/race`), keeping shared shapes defined once. typify
  cannot follow a file `$ref`, so `build.rs` bundles the referenced files'
  definitions into one self-contained schema (rewriting refs local) before
  generating. This is how interdependent schemas — the host-state model and,
  later, its fleet/wormhole/combat sub-objects — are generated as one cluster.
  A shared shape that already has a hand-written Rust home is _redirected_, not
  re-generated: an `x-rust-type` sibling on the `$ref` makes the bundler skip
  inlining that file and typify emit the existing type (e.g. the host-state
  `player.race` reuses `objects::race::Race` instead of a second generated
  `Race`), so each shared object is generated once. typify emits an absolute
  path, so the engine root carries `extern crate self as stars_engine;` for it
  to resolve internally. A map keyed by a stringified integer carries an
  `x-rust-map-key` hint that the bundler expands to `propertyNames` for typify,
  yielding a `u32` key instead of `String` without changing the (always
  string-keyed) JSON wire shape.
- `race.json` is the pilot. The remaining schemas (universe, turn, battle, …)
  are converted the same way as they gain typed producers/consumers; some are
  assembled ad hoc today and have no typed struct yet.
- This supersedes nothing; it completes ADR-0002's deferred step and leaves the
  runtime boundary of ADR-0001 untouched.
