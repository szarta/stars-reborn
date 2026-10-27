// engine/src/game/objects/universe.rs
//
// Universe — the static, shared map data (.xy-equivalent).
//
// Holds only data that is safe to expose to every player at /universe:
// boundary dimensions, density bucket, and the static identity/position of
// each planet. Mutable per-game planet state lives in `GameState::planet_states`,
// not here.

// The `Universe` TYPE is GENERATED from `schemas/game-state.json` (see
// `build.rs`) and re-exported here so existing `objects::universe::Universe`
// paths keep resolving. To change the wire contract — field names, the planet
// map's key/value shape — edit the schema, never this file. See
// `docs/adr/0003`. Behavior (the methods below) stays hand-written here.
pub use super::generated::game_state::Universe;

use super::planet::PlanetStatic;

impl Universe {
    /// Return planet count.
    pub fn planet_count(&self) -> usize {
        self.planets.len()
    }

    /// Return a list of all PlanetStatic objects (order not guaranteed).
    pub fn planet_list(&self) -> Vec<&PlanetStatic> {
        self.planets.values().collect()
    }
}
