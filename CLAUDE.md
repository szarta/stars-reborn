@AGENTS.md

# Stars Reborn — Technical Guide

Stars Reborn is a faithful, open-source clone of Stars! (1995/1996, Jeff
Johnson & Jeff McBride). Core tenets: open and freely distributable, faithful
reproduction of the original mechanics, respectful enhancement ("Legacy" mode
preserves original behavior).

**`docs/` (Sphinx) is the authoritative developer reference — consult it
first, and read the relevant `docs/adr/` record before reopening a decision it
already settled.**

## Repository layout

| Path         | Holds                                                                  | Read it when                                                        |
| ------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `engine/`    | Rust host+engine: HTTP API, turn processing, data-model authority      | changing game logic, the API surface, or the data model             |
| `client/`    | Python/PySide6 reference client: a pure HTTP consumer, no game logic   | changing the UI or how player orders are collected                  |
| `schemas/`   | JSON Schema contract for shared objects and API messages               | changing any request/response or shared-object shape                |
| `docs/`      | Sphinx design docs + `docs/adr/` decision records                      | understanding rules/architecture, or before relitigating a decision |
| `packaging/` | Launcher and AppImage/PyInstaller build driver (`tasks.py`)            | changing how the game is built or packaged                          |
| `scripts/`   | Commit-policy guards, byte-identical with the maintainer's other repos | never edit one without updating its guard test in the same change   |

Related standalone repos (not here): `stars_file_parser` (binary file-format
library) and a private experiment-scripting repo. Research lives outside the
tree until a finding is confirmed, then it is written into `docs/`.

## Task tracking

Work is tracked with `todo-sqlite-cli`; the `.todo-sqlite-cli` marker resolves
the database. Do not trust a task list written into any file — run the CLI:

- `todo-sqlite-cli next` — the one task to work on now
- `todo-sqlite-cli list` — active tasks (`--tag <phase>` to filter)
- `todo-sqlite-cli start <id>` before, `todo-sqlite-cli done <id>` after

There is no PLAN.md / COMPLETED.md; the database is authoritative.

## Architecture invariants

Each invariant is stated with the failure it prevents, so it is not mistaken
for a preference.

- **Engine and client communicate only over HTTP; no in-process interop**
  (ADR-0001). The monorepo makes in-process coupling easy by accident — keep
  engine and client as separate build targets with no dependency edge, because
  coupling desyncs single-player from multiplayer and shuts out third-party
  clients.
- **The engine is the gatekeeper.** It rejects anything structurally or
  rules-invalid regardless of what the client sent, because any HTTP client is
  a valid client and none is trusted.
- **Clients read the data model from `/model/` endpoints; never hardcode the
  tech tree, hulls, traits, or formulae** — a duplicated copy desyncs from the
  engine, the single authority.
- **`schemas/` is the single source of truth for shared shapes, and the wire
  types are generated from it — never hand-written** (ADR-0003). Rust types
  come from `engine/build.rs` (typify, regenerated every build); Python types
  from `scripts/generate_types.py` (pydantic, committed under
  `client/src/data/generated/` and diff-guarded). Editing generated code is
  overwritten on the next build/regen; change the schema instead, then rebuild
  and run the script. A schema must match what the engine actually serializes —
  the contract tests fail otherwise. Converted so far: `race`,
  `response-turn-file`, `response-game`, `response-create-new-game` (see
  `schemas/README.md` for the full migration status). The rest follow as they
  gain typed producers/consumers; some (the hull catalog) are hand-built
  `json!` today, and the create-game/validate _request_ schemas encode a richer
  intended API than the engine implements, so those are design decisions, not
  mechanical conversions.

## Validation layers (engine)

1. **Structural** — does the input conform to the JSON schema for this request?
2. **Rules-logical** — legal race/ship design for hull and tech level, possible
   orders?
3. **Game-state** — does this player have authority to issue these orders now?

## Turn resolution order

1. Wormhole jiggles
2. Random events (comet strikes, etc.)
3. Packets/salvage move and decay
4. Fleets move (waypoints), lay mines, run devices
5. Mine fields sweep (mine-laying complete)
6. Bombing
7. Population growth
8. Factories/mines built
9. Minerals mined
10. Resources generated; production queues run
11. Research applied
12. Battle at contested locations
13. Fleets merge/split (player orders)
14. Messages generated

## Racial trait system

**Primary Racial Traits (PRT)** — mutually exclusive, one per race:
`JOAT` `HE` `SS` `WM` `CA` `IS` `SD` `PP` `IT` `AR`

**Lesser Racial Traits (LRT)** — mix-and-match modifiers:
`IFE` `TT` `ARM` `ISB` `GR` `UR` `NAS` `OBRM` `CE` `NRSE` `OTES` `MILS` `LSP`
`BET` `RS` `MA` `BBA` `SF` `PA`
