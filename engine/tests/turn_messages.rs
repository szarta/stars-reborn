// engine/tests/turn_messages.rs
//
// Integration tests for the per-player turn messages produced by
// `player_view()` (game/view.rs). Today the only message the engine can derive
// from the state it models is the production-queue-empty nudge; event messages
// land with turn resolution. These tests pin the derivation that exists and the
// fog-of-war rule that a player only hears about worlds they own.

use stars_engine::game::objects::planet::BuildItem;
use stars_engine::game::objects::player::{Player, TechLevels};
use stars_engine::game::objects::race_defaults::humanoid;
use stars_engine::game::state::GameState;
use stars_engine::game::universe::generate_universe;
use stars_engine::game::view::player_view;

const PLAYER_0: u32 = 0;
const PLAYER_1: u32 = 1;

/// Deterministic two-player game, homeworlds on the two lowest-id planets, each
/// with an empty build queue (as `create_game` leaves a fresh homeworld).
fn two_player_game() -> GameState {
    let generated = generate_universe(0, 1, 2, Some(42));
    let universe = generated.universe;
    let mut planet_states = generated.planet_states;

    let mut planet_ids: Vec<u32> = universe.planets.keys().copied().collect();
    planet_ids.sort();
    let (hw0, hw1) = (planet_ids[0], planet_ids[1]);

    let race = humanoid();
    for (pid, hw_id) in [(PLAYER_0, hw0), (PLAYER_1, hw1)] {
        let s = planet_states.get_mut(&hw_id).unwrap();
        s.homeworld = true;
        s.owner = Some(pid);
        s.population = 25_000;
        s.factories = 10;
        s.mines = 10;
        s.set_homeworld_hab(&race);
    }

    GameState {
        id: "test-game".to_string(),
        name: "Messages Test".to_string(),
        universe,
        planet_states,
        players: vec![
            Player {
                id: PLAYER_0,
                race_name: "Humanoid".to_string(),
                homeworld_id: Some(hw0),
                tech: TechLevels::default(),
                race: Some(humanoid()),
            },
            Player {
                id: PLAYER_1,
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
fn empty_homeworld_queue_yields_one_production_message() {
    let game = two_player_game();
    let hw0 = game.players[0].homeworld_id.unwrap();
    let view = player_view(&game, PLAYER_0);

    assert_eq!(view.messages.len(), 1, "one owned world, empty queue");
    let m = &view.messages[0];
    assert_eq!(m.id, 0);
    assert_eq!(m.message_type, "PlanetProductionQueueEmpty");
    assert_eq!(m.related_object, Some(hw0), "Goto subject is the planet");
    assert_eq!(m.related_battle, None);
    assert!(m.important);
    assert!(m.message.contains("production queue"));
}

#[test]
fn a_player_hears_only_about_worlds_it_owns() {
    // Player 0's message is about player 0's homeworld, never player 1's.
    let game = two_player_game();
    let hw1 = game.players[1].homeworld_id.unwrap();
    let view = player_view(&game, PLAYER_0);

    assert!(
        view.messages.iter().all(|m| m.related_object != Some(hw1)),
        "player 0 must not get a message about player 1's homeworld"
    );
}

#[test]
fn a_nonempty_queue_produces_no_production_message() {
    let mut game = two_player_game();
    let hw0 = game.players[0].homeworld_id.unwrap();
    game.planet_states
        .get_mut(&hw0)
        .unwrap()
        .build_queue
        .push(BuildItem {
            build_object_id: 7,
            build_quantity: 5,
            build_progress: 0,
        });

    let view = player_view(&game, PLAYER_0);
    assert!(
        view.messages.is_empty(),
        "a world with a queued item is not flagged empty"
    );
}

#[test]
fn a_player_with_no_worlds_gets_no_messages() {
    let game = two_player_game();
    let view = player_view(&game, 99);
    assert!(view.messages.is_empty());
}
