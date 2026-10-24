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

> Migration status (task #110, #115). Converted — reconciled to the real wire
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
> Not yet converted:
>
> - `tech.json` and `response-model-ship-hulls.json` — the engine hand-builds
>   the hull catalog with `json!` and the types don't derive `Serialize`, so
>   they need a typed producer first.
> - `request-validate-race.json`, `response-validate-race.json`,
>   `request-create-new-game.json` — these describe a richer intended API than
>   the engine currently implements (e.g. structured validation failures, full
>   game-setup options), so converting them is an API-design decision, not a
>   mechanical reconciliation.
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
| `turn.json`                          | Turn input/output wrapper: player orders in, game state out                                               |
| `universe.json`                      | Universe snapshot: all planets, all fleets, all players                                                   |
| `request-create-new-game.json`       | API request to create a new game                                                                          |
| `request-create-tutorial-game.json`  | API request to create a tutorial game                                                                     |
| `request-validate-race.json`         | API request to validate a race design                                                                     |
| `response-create-new-game.json`      | API response for new game creation                                                                        |
| `response-create-tutorial-game.json` | API response for tutorial game creation                                                                   |
| `response-validate-race.json`        | API response for race validation                                                                          |
