//! Wire types GENERATED from `schemas/*.json` at build time by `build.rs`
//! (typify). Do not edit these types — change the JSON Schema instead; the
//! generated code is produced fresh on every compile and is never committed.
//! See `docs/adr/0003` and `schemas/README.md`.
//!
//! Each submodule mirrors one schema file. Hand-written behavior attached to
//! these types (constructors, conversions) lives in the sibling hand-written
//! module that re-exports them (e.g. `objects::race`), not here.

pub mod race {
    // Generated code: silence lints and dead-code on builder/helper items that
    // the engine does not call.
    #![allow(clippy::all, clippy::pedantic, dead_code, unused)]
    include!(concat!(env!("OUT_DIR"), "/race_types.rs"));
}

pub mod turn_file {
    #![allow(clippy::all, clippy::pedantic, dead_code, unused)]
    include!(concat!(env!("OUT_DIR"), "/turn_file_types.rs"));
}

pub mod universe_file {
    #![allow(clippy::all, clippy::pedantic, dead_code, unused)]
    include!(concat!(env!("OUT_DIR"), "/universe_file_types.rs"));
}

pub mod create_game {
    #![allow(clippy::all, clippy::pedantic, dead_code, unused)]
    include!(concat!(env!("OUT_DIR"), "/create_game_types.rs"));
}

pub mod game_state {
    #![allow(clippy::all, clippy::pedantic, dead_code, unused)]
    include!(concat!(env!("OUT_DIR"), "/game_state_types.rs"));
}

pub mod validate_race {
    #![allow(clippy::all, clippy::pedantic, dead_code, unused)]
    include!(concat!(env!("OUT_DIR"), "/validate_race_types.rs"));
}

pub mod ship_hulls {
    #![allow(clippy::all, clippy::pedantic, dead_code, unused)]
    include!(concat!(env!("OUT_DIR"), "/ship_hulls_types.rs"));
}
