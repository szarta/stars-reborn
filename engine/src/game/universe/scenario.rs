// engine/src/game/universe/scenario.rs
//
// Fixed-universe scenario loader.
//
// Most games get their universe from the seeded procedural `generate_universe`.
// A *scenario* is the other source: a canned, deterministic universe loaded
// from static data. The Tutorial Game is the first (and currently only)
// scenario — a fixed Tiny universe captured from the real game (see
// stars-reborn-research `knowledge/findings/tutorial_game_initial_state`).
//
// The scenario data is embedded static game data, in the same spirit as the
// hull catalogs and planet-name lists — host-only input, not a wire/shared
// shape, so it is a hand-written serde struct over an embedded JSON file rather
// than a generated schema type. The loader's OUTPUT is `GeneratedUniverse`
// (the already-schematized `Universe` + `PlanetState`), identical in shape to
// what `generate_universe` returns, so everything downstream (create-game,
// views, turn resolution) is indifferent to which path produced the universe.
//
// Scope: this builds the neutral universe (map + planet state: position, hab,
// mineral concentrations). Ownership, population, homeworld flags, starbases,
// designs and fleets are applied by the player-setup stage, which consumes the
// scenario's homeworld/player data.

use super::GeneratedUniverse;
use crate::game::objects::advantage_points::{idx_to_grav, idx_to_rad, idx_to_temp};
use crate::game::objects::planet::{PlanetState, PlanetStatic};
use crate::game::objects::player::TechLevels;
use crate::game::objects::race::Race;
use crate::game::objects::universe::Universe;
use serde::Deserialize;
use std::collections::HashMap;

/// A canned universe definition. Host-only static input.
#[derive(Debug, Clone, Deserialize)]
pub struct Scenario {
    /// Display name of the scenario game (e.g. "Tutorial Game").
    pub name: String,
    /// UniverseSize index (0=Tiny … 4=Huge), matching `generate_universe`.
    pub size: u32,
    /// Universe side lengths in light years.
    pub width: u32,
    pub height: u32,
    /// Starting year (2400 for a fresh game).
    pub year: u32,
    /// Every planet in the universe.
    pub planets: Vec<ScenarioPlanet>,
    /// The fixed players this scenario starts with.
    #[serde(default)]
    pub players: Vec<ScenarioPlayer>,
}

/// A fixed player in a scenario: which race plays, from which homeworld, with
/// what starting tech. The race is the full captured definition (race.json
/// shape) — scenarios do not depend on the predefined race registry, so an AI
/// race like the tutorial's Berserker (not in the registry) is carried here.
#[derive(Debug, Clone, Deserialize)]
pub struct ScenarioPlayer {
    pub id: u32,
    /// True for a computer player. The tutorial's Berserker is the AI race (its
    /// name comes from the AI race-name pool). The engine Player model has no
    /// CPU flag yet, so this is scenario metadata for when AI players are
    /// modelled.
    #[serde(default)]
    pub is_cpu: bool,
    /// Planet id of this player's homeworld (an id in `planets`).
    pub homeworld_planet_id: u32,
    /// Starting tech levels per field.
    pub starting_tech: TechLevels,
    /// Full race definition (race.json shape).
    pub race: Race,
}

/// One planet in a scenario.
///
/// `x`/`y` are **logical** 0-origin light-year coordinates (the game's internal
/// map-dump coordinates minus the 1000 origin offset — see the finding). The
/// three `*_idx` habitability fields are the original 0-100 axis indices;
/// `idx_to_grav`/`idx_to_temp`/`idx_to_rad` convert them to the physical units
/// `PlanetState` stores.
#[derive(Debug, Clone, Deserialize)]
pub struct ScenarioPlanet {
    pub id: u32,
    pub name: String,
    pub x: i32,
    pub y: i32,
    pub gravity_idx: i32,
    pub temperature_idx: i32,
    pub radiation_idx: i32,
    pub ironium_concentration: u32,
    pub boranium_concentration: u32,
    pub germanium_concentration: u32,
}

/// The embedded Tutorial Game scenario (captured, deterministic).
const TUTORIAL_JSON: &str = include_str!("../../../data/scenarios/tutorial.json");

/// Parse the embedded Tutorial Game scenario. Panics only if the embedded data
/// is malformed, which a test guards against — it is a build-time constant.
pub fn load_tutorial() -> Scenario {
    serde_json::from_str(TUTORIAL_JSON).expect("embedded tutorial scenario is valid JSON")
}

/// Materialize a scenario's fixed universe into the two halves `create_game`
/// stores, exactly as `generate_universe` does — but from canned data instead
/// of RNG. Planets are neutral: no owner, no population, no starbase. Surface
/// minerals mirror the concentration (the convention `generate_universe` uses
/// for a fresh planet); the player-setup stage overrides homeworld surface
/// minerals with their captured values.
pub fn scenario_universe(scenario: &Scenario) -> GeneratedUniverse {
    let mut planets = HashMap::with_capacity(scenario.planets.len());
    let mut planet_states = HashMap::with_capacity(scenario.planets.len());

    for p in &scenario.planets {
        planets.insert(
            p.id,
            PlanetStatic {
                id: p.id,
                name: p.name.clone(),
                x: p.x,
                y: p.y,
            },
        );
        planet_states.insert(
            p.id,
            PlanetState {
                gravity: idx_to_grav(p.gravity_idx) as f32,
                temperature: idx_to_temp(p.temperature_idx),
                radiation: idx_to_rad(p.radiation_idx) as u32,
                ironium_concentration: p.ironium_concentration,
                boranium_concentration: p.boranium_concentration,
                germanium_concentration: p.germanium_concentration,
                surface_ironium: p.ironium_concentration,
                surface_boranium: p.boranium_concentration,
                surface_germanium: p.germanium_concentration,
                homeworld: false,
                owner: None,
                population: 0,
                factories: 0,
                mines: 0,
                build_queue: Vec::new(),
                route_target: None,
                starbase_design_slot: None,
                packet_target: None,
            },
        );
    }

    GeneratedUniverse {
        universe: Universe {
            size: scenario.size,
            width: scenario.width,
            height: scenario.height,
            planets,
        },
        planet_states,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tutorial_scenario_parses_and_is_the_captured_tiny_universe() {
        let s = load_tutorial();
        assert_eq!(s.name, "Tutorial Game");
        assert_eq!(s.size, 0, "Tiny");
        assert_eq!((s.width, s.height), (400, 400));
        assert_eq!(s.year, 2400);
        assert_eq!(s.planets.len(), 24);
    }

    #[test]
    fn tutorial_scenario_has_the_two_captured_players() {
        let s = load_tutorial();
        assert_eq!(s.players.len(), 2);
        let p0 = s.players.iter().find(|p| p.id == 0).expect("player 0");
        assert_eq!(p0.race.name, "Humanoid");
        assert_eq!(p0.race.prt.to_string(), "JOAT");
        assert!(!p0.is_cpu);
        assert_eq!(p0.homeworld_planet_id, 13);
        assert_eq!(p0.starting_tech.energy, 3);
        let p1 = s.players.iter().find(|p| p.id == 1).expect("player 1");
        assert_eq!(p1.race.name, "Berserker"); // AI race name (SS archetype)
        assert_eq!(p1.race.prt.to_string(), "SS");
        assert!(p1.is_cpu);
        assert_eq!(p1.homeworld_planet_id, 10);
        assert_eq!(p1.starting_tech.electronics, 5);
    }

    #[test]
    fn scenario_universe_materializes_all_planets_neutral() {
        let g = scenario_universe(&load_tutorial());
        assert_eq!(g.universe.planet_count(), 24);
        assert_eq!((g.universe.width, g.universe.height), (400, 400));
        // Every planet is unowned and empty at this stage.
        for st in g.planet_states.values() {
            assert_eq!(st.owner, None);
            assert_eq!(st.population, 0);
            assert!(!st.homeworld);
            assert_eq!(st.starbase_design_slot, None);
        }
        // Coordinates sit inside the Tiny box.
        for ps in g.universe.planet_list() {
            assert!((0..400).contains(&ps.x) && (0..400).contains(&ps.y));
        }
    }

    #[test]
    fn homeworld_planets_match_the_capture() {
        let g = scenario_universe(&load_tutorial());
        // P0 homeworld: planet id 13 "Stove Top", a dead-centre 50/50/50 hab.
        let hw0 = g.universe.planets.get(&13).expect("planet 13");
        assert_eq!(hw0.name, "Stove Top");
        assert_eq!((hw0.x, hw0.y), (237, 273));
        let st0 = &g.planet_states[&13];
        assert!((st0.gravity - 1.00).abs() < 1e-6, "grav idx 50 -> 1.00 g");
        assert_eq!(st0.temperature, 0, "temp idx 50 -> 0 C");
        assert_eq!(st0.radiation, 50, "rad idx 50 -> 50 mR");
        assert_eq!(
            (
                st0.ironium_concentration,
                st0.boranium_concentration,
                st0.germanium_concentration
            ),
            (25, 70, 84)
        );
        // P1 homeworld: planet id 10 "Hacker".
        let hw1 = g.universe.planets.get(&10).expect("planet 10");
        assert_eq!(hw1.name, "Hacker");
        assert_eq!((hw1.x, hw1.y), (149, 135));
    }
}
