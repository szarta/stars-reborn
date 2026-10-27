// engine/src/game/objects/planet.rs
//
// Planet data is split into two types matching the engine's clean separation
// between the static, shared map (.xy-equivalent) and the mutable per-game
// state (.hst-equivalent). See stars-reborn-design/docs/architecture.rst.
//
//   PlanetStatic — identity and position. Lives in `Universe`. Never changes
//                  for the lifetime of a game. Safe to expose at /universe.
//   PlanetState  — everything mutable: hab values (terraforming), mineral
//                  concentrations (degrade as mines extract), surface
//                  minerals, ownership, population, factories, mines, the
//                  homeworld flag. Lives in `GameState`, host-only ground
//                  truth. Per-player views are derived from this; raw state
//                  is never sent to a non-host client.

// `PlanetStatic`, `PlanetState`, and `BuildItem` are GENERATED from
// `schemas/game-state.json` (see `build.rs`) and re-exported here so existing
// `objects::planet::*` paths keep resolving. To change the wire contract — field
// names, numeric types, the build queue shape — edit the schema, never this
// file. See `docs/adr/0003`. The behavior methods below stay hand-written here.
pub use super::generated::game_state::{BuildItem, PlanetState, PlanetStatic};

impl PlanetStatic {
    /// ``(x, y)`` coordinate tuple.
    pub fn location(&self) -> (i32, i32) {
        (self.x, self.y)
    }
}

impl PlanetState {
    /// Override hab values to the centre of the player's race tolerance per
    /// axis. Immune axes use the canonical defaults (1.00 g, 0 °C, 50 mR/yr).
    ///
    /// Per stars-reborn-design/docs/new_game/initial_state.rst: a homeworld's
    /// hab values are set to the midpoint of the race's preferred range on
    /// each axis. The midpoint is taken in **index** space (0–100), then
    /// converted back to physical units so it lands on a discrete game step.
    pub fn set_homeworld_hab(&mut self, race: &super::race::Race) {
        use super::advantage_points::{axis_to_idx, idx_to_grav, idx_to_rad, idx_to_temp};
        self.gravity = if race.hab.gravity.immune {
            1.00
        } else {
            let (lo, hi) = axis_to_idx(&race.hab.gravity, 0);
            idx_to_grav((lo + hi) / 2) as f32
        };
        self.temperature = if race.hab.temperature.immune {
            0
        } else {
            let (lo, hi) = axis_to_idx(&race.hab.temperature, 1);
            idx_to_temp((lo + hi) / 2)
        };
        self.radiation = if race.hab.radiation.immune {
            50
        } else {
            let (lo, hi) = axis_to_idx(&race.hab.radiation, 2);
            idx_to_rad((lo + hi) / 2) as u32
        };
    }
}
