// engine/src/lib.rs
//
// Library root for the stars-engine crate.
// The standalone server binary (src/main.rs) links against this rlib.

// Let this crate refer to itself by its external name. The schema-generated
// wire types (build.rs / typify) redirect shared `$ref`s to hand-written
// modules via `x-rust-type` and emit absolute paths like
// `::stars_engine::game::objects::race::Race`; this alias makes those resolve
// from within the engine. See docs/adr/0003.
extern crate self as stars_engine;

pub mod game;
pub mod http;
pub mod store;

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
