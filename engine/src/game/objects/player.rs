// engine/src/game/objects/player.rs
//
// Player — links a Race to in-game state (tech levels, ship designs,
// score, research allocation, orders).
//
// NPC (computer-controlled) players share the same data model.
//
// See stars-reborn-design/docs/architecture.rst (Game Object Model)

// The `Player` and `TechLevels` TYPES are GENERATED from
// `schemas/game-state.json` (see `build.rs`) and re-exported here so existing
// `objects::player::*` paths keep resolving. `Player::race` reuses the canonical
// `objects::race::Race` (the schema's cross-file `$ref` is redirected to that
// one generated type via `x-rust-type`, not copied). To change the wire contract
// edit the schema, never this file. See `docs/adr/0003`.
pub use super::generated::game_state::{Player, TechLevels};

/// All-zero tech levels — the starting point before any research is applied.
///
/// `TechLevels` has no intrinsic default in the schema (every field is
/// required), so the `Default` the engine relies on is provided here as
/// hand-written behavior rather than a derive.
impl Default for TechLevels {
    fn default() -> Self {
        Self {
            energy: 0,
            weapons: 0,
            propulsion: 0,
            construction: 0,
            electronics: 0,
            biotechnology: 0,
        }
    }
}
