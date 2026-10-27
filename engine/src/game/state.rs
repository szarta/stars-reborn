// engine/src/game/state.rs
//
// GameState — runtime representation of an active game.
// Stored in-memory in AppState; persisted to disk via store/.
//
// `GameState` is the host's ground-truth view of the game and must never be
// serialised directly to a non-host client. Per-player turn files are derived
// from `GameState` through a single choke point (see game/view.rs once
// PlayerView lands).

// The `GameState` TYPE is GENERATED from `schemas/game-state.json` (see
// `build.rs`) — the single source of truth for the host-state wire shape — and
// re-exported here so existing `game::state::GameState` paths keep resolving.
// Its component types (`Universe`, `PlanetState`, `Player`, …) are generated
// from the same schema and re-exported from their hand-written modules, which
// carry the behavior. To change the shape edit the schema, never this file.
// See `docs/adr/0003`.
pub use crate::game::objects::generated::game_state::GameState;
