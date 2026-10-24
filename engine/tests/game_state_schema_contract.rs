// Contract test: the host-side authoritative GameState the engine serializes
// to game.json must validate against schemas/game-state.json, the single source
// of truth its wire types are generated from. If the engine and the schema ever
// disagree on the GameState shape, this fails — the anti-drift guard for the
// host-state model.
//
// game-state.json references race.json (`player.race`). typify resolves that in
// build.rs via its bundler; here we do the equivalent merge so the validator
// sees one self-contained schema.

use serde_json::{json, Value};

use stars_engine::game::objects::player::{Player, TechLevels};
use stars_engine::game::objects::race_defaults::default_race_by_name;
use stars_engine::game::state::GameState;
use stars_engine::game::universe::generate_universe;

/// Build a standalone draft-07 schema rooted at `#/definitions/game-state`,
/// with game-state.json's own definitions plus race.json's merged in and the
/// cross-file `race.json#/...` ref rewritten local, so every `$ref` resolves.
fn game_state_schema() -> Value {
    let gs_text =
        std::fs::read_to_string("../schemas/game-state.json").expect("read game-state.json");
    let gs: Value = serde_json::from_str(&gs_text).expect("parse game-state.json");
    let race_text = std::fs::read_to_string("../schemas/race.json").expect("read race.json");
    let race: Value = serde_json::from_str(&race_text).expect("parse race.json");

    let mut defs = gs["definitions"].as_object().expect("definitions").clone();
    for (name, def) in race["definitions"].as_object().expect("race definitions") {
        defs.entry(name.clone()).or_insert_with(|| def.clone());
    }

    let mut schema = Value::Object(defs.get("game-state").unwrap().as_object().unwrap().clone());
    schema["$schema"] = json!("http://json-schema.org/draft-07/schema#");
    schema["definitions"] = Value::Object(defs);
    strip_file_prefixes(&mut schema);
    schema
}

/// Rewrite `"$ref": "file.json#/foo"` to `"#/foo"` throughout (mirrors build.rs).
fn strip_file_prefixes(v: &mut Value) {
    match v {
        Value::Object(m) => {
            if let Some(Value::String(r)) = m.get_mut("$ref") {
                if let Some(idx) = r.find('#') {
                    if idx > 0 {
                        *r = r[idx..].to_string();
                    }
                }
            }
            for val in m.values_mut() {
                strip_file_prefixes(val);
            }
        }
        Value::Array(a) => {
            for val in a.iter_mut() {
                strip_file_prefixes(val);
            }
        }
        _ => {}
    }
}

/// A representative game: a real race on an owned, populated homeworld, plus a
/// second player — exercises `race`, `owner`, `homeworld`, non-empty maps.
fn sample_game_state() -> GameState {
    let generated = generate_universe(0, 1, 2, Some(42));
    let universe = generated.universe;
    let mut planet_states = generated.planet_states;

    let mut planet_ids: Vec<u32> = universe.planets.keys().copied().collect();
    planet_ids.sort();

    let mut players = Vec::new();
    for (slot, name) in ["Humanoid", "Insectoid"].iter().enumerate() {
        let race = default_race_by_name(name).expect("default race");
        let homeworld_id = planet_ids.get(slot).copied();
        if let Some(hw) = homeworld_id {
            if let Some(ps) = planet_states.get_mut(&hw) {
                ps.homeworld = true;
                ps.owner = Some(slot as u32);
                ps.population = 25_000;
                ps.factories = 10;
                ps.mines = 10;
                ps.set_homeworld_hab(&race);
            }
        }
        players.push(Player {
            id: slot as u32,
            race_name: race.name.clone(),
            homeworld_id,
            tech: TechLevels::default(),
            race: Some(race),
        });
    }

    GameState {
        id: "11111111-1111-4111-8111-111111111111".to_string(),
        name: "Contract Test".to_string(),
        universe,
        planet_states,
        players,
        year: 2400,
    }
}

#[test]
fn game_state_matches_the_schema() {
    let schema = game_state_schema();
    let validator = jsonschema::validator_for(&schema).expect("compile game-state schema");

    let game = sample_game_state();
    let instance = serde_json::to_value(&game).expect("serialize GameState");

    let errors: Vec<String> = validator
        .iter_errors(&instance)
        .map(|e| e.to_string())
        .collect();
    assert!(
        errors.is_empty(),
        "GameState does not match schemas/game-state.json:\n  {}",
        errors.join("\n  ")
    );
}
