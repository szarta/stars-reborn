// engine/src/game/objects/race.rs
//
// Race model: Primary Racial Trait, Lesser Racial Traits, habitat preferences,
// economy parameters, and research costs.
//
// The data TYPES (`Race`, `Prt`, `Lrt`, `TechCost`, `LeftoverSpend`, `HabAxis`,
// `HabPreferences`, `Economy`, `ResearchCosts`, `PredefinedRace`) are GENERATED
// from `schemas/race.json` at build time (see `build.rs`) and re-exported here
// so existing `objects::race::*` paths keep resolving. To change the wire
// contract — field names, enum values, ranges — edit the schema, never this
// file. See `docs/adr/0003`.
//
// Wire encodings (for reference; authoritative in the schema):
//   Prt   : "HE" "SS" "WM" "CA" "IS" "SD" "PP" "IT" "AR" "JOAT"
//   Lrt   : "NRE" "IFE" "CE" "TT" "OBRM" "ARM" "NAS" "ISB" "LSP" "GR" "BET"
//           "UR" "RS" "MA"
//   TechCost : "expensive" "normal" "cheap"
//   HabAxis  : `immune` always present; `min`/`max` (physical) and
//              `min_idx`/`max_idx` (raw 0-100 Stars! index, authoritative when
//              present) are optional.
//
// The .r1 byte-offset decode that produces these types lives in the standalone
// `stars_file_parser` crate, not here.

pub use crate::game::objects::generated::race::*;
