// engine/src/game/turn/production.rs
//
// Turn-resolution step 10: resources are generated at each colonised planet and
// its production queue is run. See docs/mechanics/production.rst and the turn
// order in CLAUDE.md.
//
// SCOPE (this slice). Only the installation economy is built here:
//   * explicit Factory / Mine queue items (block-until-complete, partial
//     progress banked across turns, quantity decremented, item removed at 0);
//   * auto Factory / Mine items (build toward the colonist-operated capacity,
//     then let leftover resources flow to the next item; never removed).
// Resource generation (colonist labour + operated factories) feeds the queue.
//
// DELIBERATELY NOT YET HANDLED (each blocks the queue when reached, which is
// faithful — the original would spend resources on it — and each has a
// follow-up task):
//   * Defenses — PlanetState has no `defenses` field and there is no
//     defense-cost-by-tech model yet.
//   * Ship / starbase designs (DESIGN_ID_BASE+) and route-on-build — need the
//     fleet model, which is still a stub (objects/fleet.rs).
//   * Mineral alchemy (and its "as needed" sentinel), terraform items.
//   * AR (Alternate Reality) economy — AR planets are skipped entirely; AR does
//     not use colonist/factory resource generation and has no factories.
//
// When an unhandled item sits at the front of the queue the planet simply does
// not build past it this turn; nothing is silently skipped or mis-built
// (ADR-0001: never guess).

use std::collections::HashMap;

use crate::game::objects::buildable::{fixed_by_id, Category};
use crate::game::objects::planet::PlanetState;
use crate::game::objects::race::{Prt, Race};
use crate::game::state::GameState;

/// The installation a buildable id builds, within this slice.
#[derive(Clone, Copy, PartialEq, Eq)]
enum Installation {
    Factory,
    Mine,
}

/// Per-unit cost of a buildable, limited to the dimensions this slice spends.
struct UnitCost {
    resources: u32,
    germanium: u32,
}

/// Classify a queue item for this slice: which installation it builds, whether
/// it is an auto (capacity-bounded, repeating) item, and its per-unit cost.
/// Returns `None` for any id this slice does not yet build (caller stops).
fn classify(id: u32, race: &Race) -> Option<(Installation, bool, UnitCost)> {
    let b = fixed_by_id(id)?;
    let is_auto = b.category == Category::Auto;
    let eco = &race.economy;
    match b.kind {
        "factory" | "auto_factory" | "auto_max_factories" => Some((
            Installation::Factory,
            is_auto,
            UnitCost {
                resources: eco.factory_cost,
                // "Costs 1 less germanium to build factories" race option.
                germanium: if eco.factory_cheap_germanium { 3 } else { 4 },
            },
        )),
        "mine" | "auto_mine" | "auto_max_mines" => Some((
            Installation::Mine,
            is_auto,
            UnitCost {
                resources: eco.mine_cost,
                germanium: 0,
            },
        )),
        // defenses / alchemy / terraform / ship designs: not built in this slice.
        _ => None,
    }
}

/// Colonist-operated capacity for an installation: ``(pop / 10_000) × colonists_operate_*``.
/// Installations beyond this sit idle (factories) / cannot mine (mines); auto
/// items stop building at it.
fn capacity(install: Installation, population: u32, race: &Race) -> u32 {
    let per_10k = match install {
        Installation::Factory => race.economy.colonists_operate_factories,
        Installation::Mine => race.economy.colonists_operate_mines,
    };
    (population / 10_000) * per_10k
}

/// Current count of an installation on the planet.
fn current(install: Installation, planet: &PlanetState) -> u32 {
    match install {
        Installation::Factory => planet.factories,
        Installation::Mine => planet.mines,
    }
}

/// Add `n` of an installation to the planet.
fn add(install: Installation, planet: &mut PlanetState, n: u32) {
    match install {
        Installation::Factory => planet.factories += n,
        Installation::Mine => planet.mines += n,
    }
}

/// Resources generated at the planet this turn: colonist labour plus the output
/// of operated (capacity-limited) factories. `resource_production` is colonists
/// per resource; idle factories produce nothing.
fn generate_resources(planet: &PlanetState, race: &Race) -> u32 {
    let colonist = planet.population / race.economy.resource_production;
    let operating = planet
        .factories
        .min(capacity(Installation::Factory, planet.population, race));
    colonist + operating * race.economy.factory_production
}

/// Run the production queue for one colonised, non-AR planet.
fn produce_planet(planet: &mut PlanetState, race: &Race) {
    if race.prt == Prt::Ar || planet.population == 0 {
        return;
    }

    let mut resources = generate_resources(planet, race);

    let mut i = 0;
    while i < planet.build_queue.len() {
        let id = planet.build_queue[i].build_object_id;
        let Some((install, is_auto, cost)) = classify(id, race) else {
            break; // unhandled item type blocks the queue (see module scope note)
        };
        if cost.resources == 0 {
            break; // guard against a zero-cost item spinning; none exist today
        }

        // How many units this item still wants: an auto item builds up to the
        // remaining colonist capacity; an explicit item builds its quantity.
        let want = if is_auto {
            capacity(install, planet.population, race).saturating_sub(current(install, planet))
        } else {
            planet.build_queue[i].build_quantity
        };
        if want == 0 {
            if is_auto {
                i += 1; // at capacity — let resources flow to the next item
                continue;
            }
            planet.build_queue.remove(i); // explicit zero-quantity: drop it
            continue;
        }

        // Spend banked progress + this turn's resources, bounded by germanium.
        let banked = planet.build_queue[i].build_progress;
        let avail = banked + resources;
        let by_resources = avail / cost.resources;
        // No germanium cost (mines) ⇒ germanium never limits the build.
        let by_germanium = planet
            .surface_germanium
            .checked_div(cost.germanium)
            .unwrap_or(u32::MAX);
        let built = by_resources.min(by_germanium).min(want);

        add(install, planet, built);
        planet.surface_germanium -= built * cost.germanium;
        let leftover = avail - built * cost.resources;

        if is_auto {
            // Auto items never bank partial progress. If capacity was reached,
            // leftover resources flow to the next item; otherwise the limiter
            // was resources/germanium and the queue stops here.
            planet.build_queue[i].build_progress = 0;
            if built == want {
                resources = leftover;
                i += 1;
                continue;
            }
            return;
        }

        let remaining = want - built;
        planet.build_queue[i].build_quantity = remaining;
        if remaining == 0 {
            // Finished this item; leftover resources flow to the next.
            planet.build_queue.remove(i);
            resources = leftover;
            continue;
        }

        // Could not finish. Bank progress only when resources were the limiter
        // (a partial unit, leftover < unit cost); if germanium blocked us the
        // surplus resources are lost, matching the original's use-it-or-lose-it.
        planet.build_queue[i].build_progress = if by_resources <= by_germanium {
            leftover
        } else {
            0
        };
        return;
    }
}

/// Step 10 of turn resolution: generate resources and run every colonised
/// planet's production queue against the installation economy.
pub fn run_production(game: &mut GameState) {
    // Snapshot each player's race so planet_states can be borrowed mutably.
    let races: HashMap<u32, Race> = game
        .players
        .iter()
        .filter_map(|p| p.race.as_ref().map(|r| (p.id, r.clone())))
        .collect();

    for planet in game.planet_states.values_mut() {
        let Some(owner) = planet.owner else { continue };
        let Some(race) = races.get(&owner) else {
            continue;
        };
        produce_planet(planet, race);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::objects::planet::BuildItem;
    use crate::game::objects::player::{Player, TechLevels};
    use crate::game::objects::race_defaults::humanoid;
    use crate::game::universe::generate_universe;

    /// A one-player game with a Humanoid homeworld: pop 25,000, 10 factories,
    /// 10 mines, ample surface germanium. Humanoid economy: factory 10 res + 4
    /// germanium, mine 5 res; resource_production 1000; factory output 10;
    /// 10 factories/mines operated per 10,000 colonists. So the homeworld
    /// generates 25 (colonist) + 100 (10 operated factories × 10) = 125
    /// resources/turn, and its operating capacity is 20 factories / 20 mines.
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
            }],
            year: 2400,
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
    fn explicit_factories_build_what_resources_allow_and_bank_the_rest() {
        // 125 resources / 10 each = 12 factories; germanium is ample.
        let (mut game, hw) = homeworld_game(vec![item(7, 16)]);
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.factories, 22, "10 existing + 12 built");
        assert_eq!(
            p.surface_germanium,
            1000 - 12 * 4,
            "4 germanium per factory"
        );
        assert_eq!(p.build_queue.len(), 1, "item not finished, stays in queue");
        assert_eq!(p.build_queue[0].build_quantity, 4, "16 - 12 built");
        assert_eq!(
            p.build_queue[0].build_progress, 5,
            "125 - 120 banked toward next"
        );
    }

    #[test]
    fn banked_progress_completes_the_item_next_turn() {
        let (mut game, hw) = homeworld_game(vec![item(7, 16)]);
        run_production(&mut game); // builds 12, banks 5, factories -> 22
        run_production(&mut game); // 22 operated-capped at 20 -> 225 res + 5 banked
        let p = &game.planet_states[&hw];
        assert_eq!(p.factories, 26, "remaining 4 factories complete");
        assert!(p.build_queue.is_empty(), "finished item removed");
    }

    #[test]
    fn mines_cost_resources_only() {
        // 125 / 5 = 25 mines; no germanium spent.
        let (mut game, hw) = homeworld_game(vec![item(8, 100)]);
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.mines, 35, "10 existing + 25 built");
        assert_eq!(p.surface_germanium, 1000, "mines need no germanium");
        assert_eq!(p.build_queue[0].build_quantity, 75);
    }

    #[test]
    fn auto_factories_stop_at_capacity_and_persist() {
        // Capacity is 20 factories; 10 exist, so at most 10 build (and 125 res
        // affords 12). Auto item stays in the queue for future turns.
        let (mut game, hw) = homeworld_game(vec![item(26, 0)]);
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.factories, 20, "built up to capacity, not resource max");
        assert_eq!(p.surface_germanium, 1000 - 10 * 4);
        assert_eq!(p.build_queue.len(), 1, "auto item is never removed");
    }

    #[test]
    fn ar_planets_are_skipped() {
        let (mut game, hw) = homeworld_game(vec![item(7, 16)]);
        game.players[0].race.as_mut().unwrap().prt = Prt::Ar;
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.factories, 10, "AR economy not handled here; no build");
    }

    #[test]
    fn an_unhandled_front_item_blocks_the_queue() {
        // Defenses (id 9) are not built in this slice; the factory behind them
        // must not build either (resources would go to defenses first).
        let (mut game, hw) = homeworld_game(vec![item(9, 10), item(7, 16)]);
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.factories, 10, "blocked by the unhandled defenses item");
        assert_eq!(p.build_queue.len(), 2, "nothing consumed");
    }
}
