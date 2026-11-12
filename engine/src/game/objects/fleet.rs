// engine/src/game/objects/fleet.rs
//
// Fleet — a named group of ships at a location, with a waypoint list.
//
// See stars-reborn-design/docs/gameplay/fleets.rst
//     stars-reborn-design/docs/mechanics/fleet_movement.rst

// `Fleet`, `ShipStack`, `FleetCargo`, `FleetWaypoint`, and `FleetWaypointTask`
// are GENERATED from `schemas/game-state.json` (see `build.rs`) and re-exported
// here so `objects::fleet::*` paths resolve. A fleet is host-side ground truth:
// it lives in `GameState.fleets`, and per-player turn files expose only the
// fleets a player may see (own in full; others within scanner coverage),
// derived through `game::view::player_view`. Raw state is never sent to a
// non-host client. To change the wire contract — field names, numeric types,
// the waypoint/task shape — edit the schema, never this file. See
// `docs/adr/0003`. Hand-written behavior stays here.
pub use super::generated::game_state::{
    Fleet, FleetCargo, FleetWaypoint, FleetWaypointTask, ShipStack,
};

impl Fleet {
    /// ``(x, y)`` coordinate tuple — the fleet's current position.
    pub fn location(&self) -> (i32, i32) {
        (self.x, self.y)
    }

    /// Total number of ships across every stack. A fleet with no ships is
    /// empty (it would be removed at turn resolution).
    pub fn ship_count(&self) -> u32 {
        self.ship_stacks.iter().map(|s| s.count.get()).sum()
    }

    /// How many ships in this fleet are built from the owner's ship design in
    /// `slot` — the fleet's contribution to that design's built-count.
    pub fn ships_of_design(&self, slot: u32) -> u32 {
        self.ship_stacks
            .iter()
            .filter(|s| s.design_slot == slot)
            .map(|s| s.count.get())
            .sum()
    }
}

impl FleetCargo {
    /// Total cargo mass (kT): minerals plus colonists.
    pub fn total(&self) -> u32 {
        self.ironium + self.boranium + self.germanium + self.colonists
    }
}
