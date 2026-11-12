// engine/src/game/turn/mod.rs
//
// Turn processing — the annual resolution sequence applied to all player orders.
//
// See docs/mechanics/turn_resolution.rst and the turn order in CLAUDE.md.
//
// `resolve_turn` is the orchestrator: it clears the per-turn message store,
// runs every turn-resolution step that has been built so far in canonical
// order, and advances the year. The full Phase 0–14 sequence is being built one
// step at a time; each step is a self-contained function in its own module.
// Implemented so far:
//
//   Phase 6 — Production (resources generated; production queues run) —
//             `production::run_production`.
//
// Each remaining phase lands with its mechanic; when it does, that phase emits
// its catalogue messages by calling `push_message`. Production of
// factories/mines emits no player messages in the original game, so today the
// orchestrator runs the store lifecycle with no message family yet attached.

pub mod production;

pub use production::run_production;

use crate::game::state::{GameState, PlayerMessage};

/// Append a resolution-time message to a player's per-turn store.
///
/// Turn-resolution steps call this as they produce events; `player_view()`
/// later merges the store with its view-time messages to build the turn file.
/// The message's turn-file `id` is NOT set here — it is assigned at projection
/// time, where it is the only place an id is meaningful.
pub fn push_message(game: &mut GameState, player_id: u32, message: PlayerMessage) {
    game.player_messages
        .entry(player_id)
        .or_default()
        .push(message);
}

/// Resolve one annual turn: run every implemented turn-resolution step in
/// canonical order (docs/mechanics/turn_resolution.rst), then advance the year.
///
/// Messages are strictly per-turn, so the store is cleared before any step
/// runs; the events a step records this year are read back in the turn file the
/// players receive for `year + 1`.
pub fn resolve_turn(game: &mut GameState) {
    // Discard last year's messages before any step appends this year's.
    game.player_messages.clear();

    // Canonical turn order. Only the steps built so far run; the rest land with
    // their mechanics, each wiring in its own phase's messages at that time.
    //   Phase 6 — Production: resources generated; production queues run.
    production::run_production(game);

    game.year += 1;
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::objects::planet::BuildItem;
    use crate::game::objects::player::{Player, TechLevels};
    use crate::game::objects::race_defaults::humanoid;
    use crate::game::universe::generate_universe;
    use crate::game::view::player_view;

    /// One-player Humanoid homeworld (pop 25,000, 10 factories/mines, ample
    /// germanium) with the given build queue — generates 125 resources/turn.
    fn homeworld_game(queue: Vec<BuildItem>) -> (GameState, u32) {
        let generated = generate_universe(0, 1, 1, Some(42));
        let universe = generated.universe;
        let mut planet_states = generated.planet_states;
        let mut ids: Vec<u32> = universe.planets.keys().copied().collect();
        ids.sort();
        let hw = ids[0];
        {
            let s = planet_states.get_mut(&hw).unwrap();
            s.owner = Some(0);
            s.homeworld = true;
            s.population = 25_000;
            s.factories = 10;
            s.mines = 10;
            s.surface_germanium = 1000;
            s.build_queue = queue;
        }
        let game = GameState {
            id: "g".into(),
            name: "t".into(),
            universe,
            planet_states,
            players: vec![Player {
                id: 0,
                race_name: "Humanoid".into(),
                homeworld_id: Some(hw),
                tech: TechLevels::default(),
                race: Some(humanoid()),
                designs: vec![],
            }],
            year: 2400,
            player_messages: Default::default(),
            fleets: Default::default(),
        };
        (game, hw)
    }

    fn item(id: u32, qty: u32) -> BuildItem {
        BuildItem {
            build_object_id: id,
            build_progress: 0,
            build_quantity: qty,
        }
    }

    #[test]
    fn resolve_turn_advances_the_year_and_runs_production() {
        // 125 resources / 5 each = 25 mines built (no germanium cost).
        let (mut game, hw) = homeworld_game(vec![item(8, 100)]);
        resolve_turn(&mut game);
        assert_eq!(game.year, 2401, "year advances by one");
        assert_eq!(game.planet_states[&hw].mines, 35, "production ran");
    }

    #[test]
    fn resolve_turn_clears_last_years_messages() {
        let (mut game, _hw) = homeworld_game(vec![]);
        // Seed a stale message as if produced in a prior resolution.
        push_message(
            &mut game,
            0,
            PlayerMessage {
                message: "stale".into(),
                message_type: "PlanetProductionQueueEmpty".into(),
                related_object: None,
                related_battle: None,
                important: true,
            },
        );
        resolve_turn(&mut game);
        assert!(
            game.player_messages.get(&0).is_none_or(Vec::is_empty),
            "per-turn store is cleared at the start of resolution"
        );
    }

    #[test]
    fn stored_messages_are_projected_into_the_turn_file_before_view_messages() {
        // An empty-queue homeworld yields one view-time message; a stored
        // resolution message must precede it and both get contiguous ids.
        let (mut game, hw) = homeworld_game(vec![]);
        push_message(
            &mut game,
            0,
            PlayerMessage {
                message: "an event happened".into(),
                message_type: "MinesCreated".into(),
                related_object: Some(hw),
                related_battle: None,
                important: false,
            },
        );
        let view = player_view(&game, 0);
        assert_eq!(view.messages.len(), 2, "stored + view-time");
        assert_eq!(view.messages[0].id, 0);
        assert_eq!(view.messages[0].message_type, "MinesCreated");
        assert!(!view.messages[0].important, "stored importance preserved");
        assert_eq!(view.messages[1].id, 1);
        assert_eq!(view.messages[1].message_type, "PlanetProductionQueueEmpty");
    }

    #[test]
    fn stored_messages_reach_only_their_target_player() {
        let (mut game, _hw) = homeworld_game(vec![item(8, 1)]);
        push_message(
            &mut game,
            0,
            PlayerMessage {
                message: "for player 0".into(),
                message_type: "MinesCreated".into(),
                related_object: None,
                related_battle: None,
                important: true,
            },
        );
        // A different player sees none of player 0's stored messages.
        let other = player_view(&game, 7);
        assert!(other.messages.is_empty());
    }
}
