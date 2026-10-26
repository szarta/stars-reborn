// engine/src/game/view.rs
//
// PlayerView — the single choke point that projects a player's fog-of-war
// view from the host-side GameState. Every per-player turn file MUST be
// produced by `player_view()`; serialising GameState directly to a non-host
// client is a leak.
//
// Per stars-reborn-design/docs/architecture.rst (Per-Player Visibility),
// each planet appears in one of three states for a given player:
//
//   1. Never observed     — only identity (id, name, x, y) is known.
//   2. Observed, stale    — last-snapshot values + years_since_last_scan > 0.
//   3. Currently scanned  — current ground-truth values; years_since_last_scan = 0.
//
// State (2) is not yet reachable: scanner mechanics and per-player intel
// persistence land in a later commit. For now the visibility rule is
// "fields visible iff the player owns the planet" — the player's homeworld
// (and any later-colonised planets) appear as Observed with years_since_last_scan = 0;
// every other planet is Unobserved.
//
// As scanner mechanics land, the only place that needs updating is the
// `is_observable` predicate inside `player_view()`.

use crate::game::objects::advantage_points::{
    axis_to_idx, grav_to_idx, planet_habitability, rad_to_idx, temp_to_idx,
};
use crate::game::objects::planet::{PlanetState, PlanetStatic};
use crate::game::objects::race::Race;
use crate::game::state::GameState;

// The turn-file wire types (`PlayerView`, `PlanetIntel`, `PlanetObserved`,
// `PlanetUnobserved`) are GENERATED from `schemas/response-turn-file.json` at
// build time (see `build.rs`) and re-exported here so existing
// `game::view::*` paths keep resolving. To change the turn-file shape — field
// names, ranges, which fields are observed-only — edit the schema, not this
// file. `PlanetIntel` is untagged: a client tells observed from unobserved by
// whether the contents fields are present. See `docs/adr/0003`.
pub use crate::game::objects::generated::turn_file::{
    BuildItem, PlanetIntel, PlanetObserved, PlanetUnobserved, PlayerView,
};

/// Project a `PlayerView` for `player_id` from the host-side `GameState`.
///
/// This is the single choke point that derives per-player turn files. Any
/// host-only field that escapes through this function is a leak; the
/// integration test in `tests/player_view_leak.rs` is the safety net.
pub fn player_view(state: &GameState, player_id: u32) -> PlayerView {
    let player = state.players.iter().find(|p| p.id == player_id);
    let race = player.and_then(|p| p.race.as_ref());

    let mut planet_ids: Vec<u32> = state.universe.planets.keys().copied().collect();
    planet_ids.sort();

    let planets: Vec<PlanetIntel> = planet_ids
        .into_iter()
        .filter_map(|id| {
            let static_ = state.universe.planets.get(&id)?;
            let pstate = state.planet_states.get(&id);
            Some(intel_for(static_, pstate, player_id, race))
        })
        .collect();

    PlayerView {
        year: state.year,
        game_id: state.id.clone(),
        game_name: state.name.clone(),
        player_id,
        homeworld_id: player.and_then(|p| p.homeworld_id),
        planets,
        // The engine does not model ship designs yet (tracked separately); a
        // player's turn file carries only their own designs, so emit an empty
        // list until the design model lands. See docs/mechanics/ship_design.rst.
        ship_designs: vec![],
    }
}

/// Compute planet value (0..100 habitable, negative red) for a planet against
/// the given race. Returns 0 when the race is unknown — the safer default for
/// pre-existing saves missing the optional Race field on Player.
fn compute_value(s: &PlanetState, race: Option<&Race>) -> i32 {
    let Some(race) = race else {
        return 0;
    };
    let is_immune = [
        race.hab.gravity.immune,
        race.hab.temperature.immune,
        race.hab.radiation.immune,
    ];
    let (glo, ghi) = axis_to_idx(&race.hab.gravity, 0);
    let (tlo, thi) = axis_to_idx(&race.hab.temperature, 1);
    let (rlo, rhi) = axis_to_idx(&race.hab.radiation, 2);
    let hab_low = [glo, tlo, rlo];
    let hab_high = [ghi, thi, rhi];
    let hab_center = [(glo + ghi) / 2, (tlo + thi) / 2, (rlo + rhi) / 2];
    let planet_hab = [
        grav_to_idx(s.gravity as f64),
        temp_to_idx(s.temperature as f64),
        rad_to_idx(s.radiation as f64),
    ];
    planet_habitability(&is_immune, &hab_low, &hab_high, &hab_center, &planet_hab) as i32
}

/// Project the host-side production queue into the turn-file `BuildItem`
/// wire shape. Emitted only for owned planets (production is private); the
/// `estimated-years-to-complete` projection is deferred until the cost/output
/// model lands, so it is left absent here.
fn build_queue_view(s: &PlanetState) -> Vec<BuildItem> {
    s.build_queue
        .iter()
        .map(|bi| BuildItem {
            build_object_id: bi.build_object_id,
            build_quantity: bi.build_quantity,
            build_progress: Some(bi.build_progress),
            estimated_years_to_complete: None,
        })
        .collect()
}

/// Decide whether `player_id` can currently observe this planet, and emit
/// the matching `PlanetIntel` variant.
///
/// Today's rule: observable iff the player owns the planet. When scanner
/// mechanics land, this is the function that grows: union of fleet/planet
/// scanner coverage, with stale snapshots persisted across turns from a
/// future `PlayerIntel` store on `GameState`.
fn intel_for(
    static_: &PlanetStatic,
    pstate: Option<&PlanetState>,
    player_id: u32,
    race: Option<&Race>,
) -> PlanetIntel {
    let observable = matches!(pstate, Some(s) if s.owner == Some(player_id));

    match (observable, pstate) {
        (true, Some(s)) => PlanetIntel::Observed(PlanetObserved {
            id: static_.id,
            name: static_.name.clone(),
            x: static_.x,
            y: static_.y,
            years_since_last_scan: 0,
            gravity: s.gravity,
            temperature: s.temperature,
            radiation: s.radiation,
            ironium_concentration: s.ironium_concentration,
            boranium_concentration: s.boranium_concentration,
            germanium_concentration: s.germanium_concentration,
            surface_ironium: s.surface_ironium,
            surface_boranium: s.surface_boranium,
            surface_germanium: s.surface_germanium,
            homeworld: s.homeworld,
            owner: s.owner,
            population: s.population,
            factories: s.factories,
            mines: s.mines,
            value: compute_value(s, race),
            build_queue: build_queue_view(s),
        }),
        _ => PlanetIntel::Unobserved(PlanetUnobserved {
            id: static_.id,
            name: static_.name.clone(),
            x: static_.x,
            y: static_.y,
        }),
    }
}
