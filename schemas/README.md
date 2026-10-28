# Stars Reborn — Schemas

JSON Schema definitions for all Stars Reborn game objects and API contracts.

These schemas are the **single source of truth** for the engine↔client wire
contract. The language types are generated from them, never hand-written (see
`docs/adr/0003`):

- **Engine (Rust):** `engine/build.rs` runs `typify` over each schema at build
  time into `OUT_DIR`; the types are never committed and regenerate every
  compile.
- **Client (Python):** `scripts/generate_types.py` runs
  `datamodel-code-generator` into `client/src/data/generated/` as pydantic v2
  models. That output is committed and the `generate-python-types` pre-commit
  hook / CI fail if it is stale.

To change the contract, edit the schema — then rebuild (Rust) and run
`python3 scripts/generate_types.py` (Python). Never edit generated code. A
schema must describe the shape the engine actually serializes; contract tests
(`engine/tests/race_schema_contract.rs`, `client/tests/test_race_contract.py`)
fail if a schema and the real wire output disagree.

Schemas are authored in **JSON Schema draft-07**. For the meaning and design
rationale behind each one, see `docs/` (the Sphinx design guide).

> Migration status. Converted — reconciled to the real wire
> format and wired into a generator: `race.json`, `response-turn-file.json`
> (per-player turn file), `response-game.json` (public universe/.xy file),
> `response-create-new-game.json`, `game-state.json` (host-side authoritative
> state persisted to `game.json`; Rust-only — the client never receives it).
>
> `game-state.json` references `race.json` (`player.race`). typify cannot follow
> a cross-file `$ref`, so `engine/build.rs` bundles referenced files' definitions
> into one self-contained schema before generating. That bundler is the shared
> infrastructure the remaining interdependent schemas (fleets, wormholes, etc.)
> will reuse as they are added.
>
> A cross-file `$ref` to a shape that already has a hand-written Rust home is
> _redirected_ rather than re-generated: adding an `x-rust-type` sibling to the
> `$ref` (as `player.race` does, pointing at `crate::game::objects::race::Race`)
> makes `build.rs` skip inlining that file and emit the existing type, so a
> shared object such as `Race` is generated exactly once and merely re-used by
> `game_state_types.rs`. The on-disk schema keeps the `$ref` so validators still
> resolve the shape; the engine root carries `extern crate self as stars_engine;`
> so typify's absolute `::stars_engine::…` path resolves from inside the engine.
>
> A map whose JSON keys are stringified integers (e.g. `planet_states`,
> `universe.planets`, keyed by planet id) carries the `x-rust-map-key: "uint32"`
> generation hint, which `build.rs` expands into a `propertyNames` schema for
> typify so the generated key type is `u32` rather than `String`. serde
> round-trips the integer key through the string JSON key, so the wire shape is
> unchanged; a literal `propertyNames: {type: integer}` is deliberately avoided
> because object keys are always strings and it would fail validation.
>
> `response-model-ship-hulls.json` (GET /model/ships/hulls) and the `tech.json`
> leaf defs it references (both up-converted to draft-07) are reconciled to the
> engine's live output and guarded by a Rust contract test
> (`engine/tests/ship_hulls_schema_contract.rs`); client pydantic types are
> generated (`ship_hulls.py`). The engine still hand-builds the response with
> `json!` — replacing that with the generated typed producer is a tracked
> follow-up.
>
> `response-model-starbase-hulls.json` (GET /model/starbase/hulls) mirrors the
> ship-hulls schema for the five starbase hulls (starbase-hull-id space, no
> category/mass/fuel/cargo; adds `dock-capacity`, absent = unlimited). It
> references the same `tech.json` leaf defs, is reconciled to the engine's live
> output from `starbase_hull_catalog.rs`, and is guarded by a Rust contract test
> (`engine/tests/starbase_hulls_schema_contract.rs`). The engine maps the
> internal catalog into the generated wire type (no `json!`). No client consumer
> yet, so pydantic types are not generated until the Ship Designer needs them.
>
> `response-model-technologies.json` (GET /model/technologies) is
> authored draft-07 and references `tech.json` (ids, cost, tech-requirements)
> and `race.json` (prt/lrt enums for trait gating). It is the **design target**
> for the full component tree — every installable ship/starbase part plus the
> non-installable planetary/orbital techs — with per-category `properties`
> selected by an if/then discriminator on `category`. A **first producer slice**
> is now wired (task #144): `engine/src/game/objects/technology_catalog.rs`
> holds engines, armor, shields and orbital components (stargates + mass
> drivers), the `/model/technologies` and `/{id}` handlers serve it, and the
> output is built with `json!` (like `/model/buildables`; not in a codegen
> allowlist, so no Rust/client types are generated from it yet). The guard test
> `engine/tests/technologies_schema_contract.rs` validates that real output
> against the schema in addition to the schema-validity checks. Still to come as
> tracked follow-ups: the remaining categories (weapons, bombs, scanners,
> electrical, mechanical, mine-layers, mining-robots, planetary), the two
> Mystery-Trader items (MegaPolyShell, LangstonShell), oracle verification of the
> non-engine values, generated client types, and the `icon` field once the icon
> convention lands.
>
> `GET /model/buildables` (the production-queue buildable registry) is
> likewise hand-built with `json!` in `engine/src/http/mod.rs`
> (`buildables_response`) and covered by a unit test, but has **no schema file
> yet** — formalizing `response-model-buildables.json` (draft-07, contract test,
> generated client types) is a tracked follow-up, mirroring the ship-hulls one.
> The production-queue shape itself is in the SSoT: `build_queue` /
> `build-item` were added to `game-state.json` (host, snake_case) and
> `response-turn-file.json` (view, kebab-case), both contract-tested.
>
> The POST /race/validate contract is reconciled (draft-07) and
> contract-tested both ways: `request-validate-race.json` is a bare `Race`
> (a `$ref` to race.json, matching the engine), and `response-validate-race.json`
> is `{advantage-points, valid, failure-reason?}` — the engine now serializes
> the generated `RaceValidateResponse` type, and client pydantic types are
> generated (`validate_race.py`).
>
> Not yet converted:
>
> - `request-create-new-game.json` — kept as the **design target**: it
>   describes the full New Game dialog (victory conditions, galaxy clumping,
>   play flags, universe params) while the engine parses only
>   name/players/size/density today. It is converted and wired when the engine
>   grows to consume those options, not flattened down to the current stub.
> - `universe.json`, `player.json`, `planet.json`, `battle.json`, `turn.json` —
>   the original draft-04 sketches of the full game model (fleets, wormholes,
>   minefields, salvage, mineral packets, combat). The host-state _subset_ the
>   engine serializes today is covered by `game-state.json`; these remain the
>   design target for the rest and are reconciled (and folded into the
>   `game-state.json` cluster via the bundler) as the engine serializes those
>   objects. They still carry known ref bugs to fix on conversion.
> - `request-submit-orders.json`, `request-create-tutorial-game.json`,
>   `response-create-tutorial-game.json`, `error.json` — convert as they gain
>   stable typed producers/consumers.

## Contents

| Schema                               | Description                                                                                               |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `battle.json`                        | Battle report: rounds, events, surviving/destroyed ships                                                  |
| `game-state.json`                    | Host-side authoritative game state persisted to `game.json` (host-gated, never sent to a non-host client) |
| `planet.json`                        | Planet state: hab values, minerals, population, infrastructure, owner                                     |
| `player.json`                        | Player state: race, known planets, fleets, tech levels                                                    |
| `race.json`                          | Race definition: PRT, LRTs, economy parameters, hab ranges, tech costs                                    |
| `tech.json`                          | Shared tech-item types: ids, mineral costs, tech-level requirements, slot-type enum                       |
| `response-model-ship-hulls.json`     | API response for `GET /model/ships/hulls`: full ship-hull catalog                                         |
| `response-model-starbase-hulls.json` | API response for `GET /model/starbase/hulls`: full starbase-hull catalog                                  |
| `response-model-technologies.json`   | API response for `GET /model/technologies`: full component tree (parts + planetary/orbital techs)         |
| `turn.json`                          | Turn input/output wrapper: player orders in, game state out                                               |
| `universe.json`                      | Universe snapshot: all planets, all fleets, all players                                                   |
| `request-create-new-game.json`       | API request to create a new game                                                                          |
| `request-create-tutorial-game.json`  | API request to create a tutorial game                                                                     |
| `request-validate-race.json`         | API request to validate a race design                                                                     |
| `response-create-new-game.json`      | API response for new game creation                                                                        |
| `response-create-tutorial-game.json` | API response for tutorial game creation                                                                   |
| `response-validate-race.json`        | API response for race validation                                                                          |
