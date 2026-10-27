// Contract test: the per-player turn file the engine serializes must validate
// against schemas/response-turn-file.json (the source of truth the PlayerView
// wire types are generated from). If the engine output and the schema ever
// disagree, this fails — the anti-drift guard for the turn file.

use stars_engine::game::objects::player::{Player, TechLevels};
use stars_engine::game::objects::race_defaults::humanoid;
use stars_engine::game::state::GameState;
use stars_engine::game::universe::generate_universe;
use stars_engine::game::view::player_view;

/// Two-player game with both homeworlds owned, so a view contains both an
/// observed planet (the owner's homeworld) and many unobserved ones.
fn two_player_game() -> GameState {
    let generated = generate_universe(0, 1, 2, Some(42));
    let universe = generated.universe;
    let mut planet_states = generated.planet_states;

    let mut planet_ids: Vec<u32> = universe.planets.keys().copied().collect();
    planet_ids.sort();
    let (hw0, hw1) = (planet_ids[0], planet_ids[1]);

    let race = humanoid();
    for (pid, hw_id) in [(0u32, hw0), (1u32, hw1)] {
        let s = planet_states.get_mut(&hw_id).unwrap();
        s.homeworld = true;
        s.owner = Some(pid);
        s.population = 25_000;
        s.factories = 10;
        s.mines = 10;
        s.set_homeworld_hab(&race);
    }

    GameState {
        id: "11111111-1111-4111-8111-111111111111".to_string(),
        name: "Contract Test".to_string(),
        universe,
        planet_states,
        players: vec![
            Player {
                id: 0,
                race_name: "Humanoid".to_string(),
                homeworld_id: Some(hw0),
                tech: TechLevels::default(),
                race: Some(humanoid()),
            },
            Player {
                id: 1,
                race_name: "Humanoid".to_string(),
                homeworld_id: Some(hw1),
                tech: TechLevels::default(),
                race: Some(humanoid()),
            },
        ],
        year: 2400,
    }
}

#[test]
fn turn_file_matches_the_schema() {
    let text = std::fs::read_to_string("../schemas/response-turn-file.json")
        .expect("read schemas/response-turn-file.json");
    let schema: serde_json::Value = serde_json::from_str(&text).expect("parse schema");
    let validator = jsonschema::validator_for(&schema).expect("compile turn-file schema");

    let game = two_player_game();
    for pid in [0u32, 1u32] {
        let view = player_view(&game, pid);
        let instance = serde_json::to_value(&view).expect("serialize PlayerView");

        let errors: Vec<String> = validator
            .iter_errors(&instance)
            .map(|e| e.to_string())
            .collect();
        assert!(
            errors.is_empty(),
            "player {pid} turn file does not match response-turn-file.json:\n  {}",
            errors.join("\n  ")
        );
    }
}
