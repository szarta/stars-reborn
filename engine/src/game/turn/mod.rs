// engine/src/game/turn/mod.rs
//
// Turn processing — the annual resolution sequence applied to all player orders.
//
// See docs/mechanics/turn_resolution.rst and the turn order in CLAUDE.md.
//
// The full 14-step sequence is being built one step at a time. Each step is a
// self-contained function in its own module; `resolve_turn` (future) will call
// them in order. Implemented so far:
//
//   10. Resources generated; production queues run — `production::run_production`

pub mod production;

pub use production::run_production;
