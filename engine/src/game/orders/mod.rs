// engine/src/game/orders/mod.rs
//
// Player order application. The http layer deserializes a submit-orders body
// (schemas/request-submit-orders.json) into these types and calls into here;
// all validation and state mutation lives in this module, not in http.
//
// This slice implements the production-queue order (`planet.set_production_queue`).
// Other order kinds in the schema are not yet applied — the engine
// rejects them explicitly rather than silently accepting a no-op, so a client
// is never told an order succeeded when nothing happened. They land as their
// own engine slices.

use serde::Deserialize;

use crate::game::objects::buildable::{design_build_object_id, fixed_by_kind};
use crate::game::objects::planet::BuildItem;
use crate::game::state::GameState;

/// Semantic production-queue item kind — mirrors the `item` object in
/// `schemas/request-submit-orders.json#/definitions/production_item`. The
/// engine resolves each to a numeric `build_object_id` via the buildable
/// registry (`objects::buildable`).
#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum BuildKind {
    Factory,
    Mine,
    Defenses,
    Alchemy,
    AutoFactory,
    AutoMine,
    AutoDefenses,
    AutoAlchemy,
    AutoMinTerraform,
    AutoMaxTerraform,
    AutoMaxFactories,
    AutoMaxMines,
    Design { design_slot: u32 },
}

impl BuildKind {
    /// Resolve to the flat `build_object_id`, or `None` if it names no valid
    /// buildable (e.g. a design slot out of range).
    pub fn build_object_id(&self) -> Option<u32> {
        use BuildKind::*;
        let slug = match self {
            Factory => "factory",
            Mine => "mine",
            Defenses => "defenses",
            Alchemy => "alchemy",
            AutoFactory => "auto_factory",
            AutoMine => "auto_mine",
            AutoDefenses => "auto_defenses",
            AutoAlchemy => "auto_alchemy",
            AutoMinTerraform => "auto_min_terraform",
            AutoMaxTerraform => "auto_max_terraform",
            AutoMaxFactories => "auto_max_factories",
            AutoMaxMines => "auto_max_mines",
            Design { design_slot } => return design_build_object_id(*design_slot),
        };
        fixed_by_kind(slug).map(|b| b.id)
    }
}

/// One entry of a `planet.set_production_queue` order — mirrors
/// `production_item` (`{ item, count }`).
#[derive(Debug, Clone, Deserialize)]
pub struct ProductionItemInput {
    pub item: BuildKind,
    pub count: u32,
}

/// Why an order could not be applied. The http layer maps each to a status.
#[derive(Debug, PartialEq, Eq)]
pub enum OrderError {
    /// Target planet has no state (does not exist).
    PlanetNotFound(u32),
    /// Target planet is not owned by the submitting player.
    PlanetNotOwned(u32),
    /// An item named no valid buildable (e.g. design slot out of range).
    UnknownBuildable,
}

/// Apply a `planet.set_production_queue` order: replace the entire production
/// queue at `planet_id` with `items`, resolved to the host build-queue shape.
///
/// Atomic: every item is resolved to a `build_object_id` before anything is
/// written, so a single bad item leaves the existing queue untouched. Freshly
/// queued items start at `build_progress = 0` (the turn engine advances it);
/// `complete_percent` is server-managed and never read from input.
pub fn apply_set_production_queue(
    game: &mut GameState,
    player_id: u32,
    planet_id: u32,
    items: &[ProductionItemInput],
) -> Result<(), OrderError> {
    let planet = game
        .planet_states
        .get_mut(&planet_id)
        .ok_or(OrderError::PlanetNotFound(planet_id))?;

    if planet.owner != Some(player_id) {
        return Err(OrderError::PlanetNotOwned(planet_id));
    }

    // Resolve first; only commit once all items are valid.
    let mut queue = Vec::with_capacity(items.len());
    for it in items {
        let build_object_id = it
            .item
            .build_object_id()
            .ok_or(OrderError::UnknownBuildable)?;
        queue.push(BuildItem {
            build_object_id,
            build_quantity: it.count,
            build_progress: 0,
        });
    }

    planet.build_queue = queue;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::objects::player::{Player, TechLevels};
    use crate::game::objects::race_defaults::humanoid;
    use crate::game::universe::generate_universe;

    fn one_player_game() -> (GameState, u32) {
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
            }],
            year: 2400,
        };
        (game, hw)
    }

    #[test]
    fn sets_queue_on_owned_planet() {
        let (mut game, hw) = one_player_game();
        let items = vec![
            ProductionItemInput {
                item: BuildKind::Factory,
                count: 16,
            },
            ProductionItemInput {
                item: BuildKind::Design { design_slot: 1 },
                count: 1,
            },
        ];
        apply_set_production_queue(&mut game, 0, hw, &items).unwrap();
        let q = &game.planet_states[&hw].build_queue;
        assert_eq!(q.len(), 2);
        assert_eq!(q[0].build_object_id, 7); // factory
        assert_eq!(q[0].build_quantity, 16);
        assert_eq!(q[0].build_progress, 0);
        assert_eq!(q[1].build_object_id, 1025); // design slot 1
    }

    #[test]
    fn rejects_unowned_planet_and_leaves_queue_untouched() {
        let (mut game, hw) = one_player_game();
        // player 2 does not own the homeworld
        let err = apply_set_production_queue(
            &mut game,
            2,
            hw,
            &[ProductionItemInput {
                item: BuildKind::Mine,
                count: 1,
            }],
        )
        .unwrap_err();
        assert_eq!(err, OrderError::PlanetNotOwned(hw));
        assert!(game.planet_states[&hw].build_queue.is_empty());
    }

    #[test]
    fn bad_item_is_atomic() {
        let (mut game, hw) = one_player_game();
        // seed a valid queue, then submit one with an out-of-range design slot
        apply_set_production_queue(
            &mut game,
            0,
            hw,
            &[ProductionItemInput {
                item: BuildKind::Mine,
                count: 5,
            }],
        )
        .unwrap();
        let err = apply_set_production_queue(
            &mut game,
            0,
            hw,
            &[ProductionItemInput {
                item: BuildKind::Design { design_slot: 99 },
                count: 1,
            }],
        )
        .unwrap_err();
        assert_eq!(err, OrderError::UnknownBuildable);
        // prior queue is preserved
        assert_eq!(game.planet_states[&hw].build_queue.len(), 1);
        assert_eq!(game.planet_states[&hw].build_queue[0].build_object_id, 8);
    }
}
