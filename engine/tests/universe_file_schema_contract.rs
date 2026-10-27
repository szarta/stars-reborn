// Contract test: the public universe file (.xy equivalent) the engine
// serializes must validate against schemas/response-game.json, the source of
// truth the UniverseResponse/UniversePlanet wire types are generated from.

use stars_engine::game::objects::generated::universe_file::{UniversePlanet, UniverseResponse};
use stars_engine::game::universe::generate_universe;

#[test]
fn universe_file_matches_the_schema() {
    let generated = generate_universe(0, 1, 2, Some(42));
    let universe = generated.universe;

    let mut planets: Vec<UniversePlanet> = universe
        .planets
        .values()
        .map(|p| UniversePlanet {
            id: p.id,
            name: p.name.clone(),
            x: p.x,
            y: p.y,
        })
        .collect();
    planets.sort_by_key(|p| p.id);

    let response = UniverseResponse {
        game_id: "11111111-1111-4111-8111-111111111111".to_string(),
        game_name: "Contract Test".to_string(),
        year: 2400,
        universe_width: universe.width,
        universe_height: universe.height,
        planet_count: universe.planet_count() as u32,
        planets,
    };

    let text = std::fs::read_to_string("../schemas/response-game.json")
        .expect("read schemas/response-game.json");
    let schema: serde_json::Value = serde_json::from_str(&text).expect("parse schema");
    let validator = jsonschema::validator_for(&schema).expect("compile response-game schema");

    let instance = serde_json::to_value(&response).expect("serialize UniverseResponse");
    let errors: Vec<String> = validator
        .iter_errors(&instance)
        .map(|e| e.to_string())
        .collect();
    assert!(
        errors.is_empty(),
        "universe file does not match response-game.json:\n  {}",
        errors.join("\n  ")
    );
}
