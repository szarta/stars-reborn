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
use std::num::NonZeroU32;

use crate::game::objects::buildable::{design_slot_of, fixed_by_id, Category};
use crate::game::objects::fleet::{Fleet, FleetCargo, FleetWaypoint, FleetWaypointTask, ShipStack};
use crate::game::objects::planet::PlanetState;
use crate::game::objects::player::{ShipDesign, ShipDesignKind};
use crate::game::objects::race::{Prt, Race};
use crate::game::objects::ship_cost::design_cost;
use crate::game::objects::ship_hull_catalog::ship_hull_catalog;
use crate::game::objects::starbase_hull_catalog::starbase_hull_catalog;
use crate::game::objects::technology::{ShipHull, StarbaseHull};
use crate::game::objects::technology_catalog::{
    technology_catalog, PlanetaryKind, Props, TechItem,
};
use crate::game::state::GameState;

/// Travel warp a built ship uses for its Route-To waypoint. A placeholder until
/// fleet movement + per-engine ideal-speed land — the waypoint is inert (nothing
/// moves fleets yet), so only the destination matters today.
const ROUTE_WARP: u32 = 7;

/// The installation a buildable id builds, within this slice.
#[derive(Clone, Copy, PartialEq, Eq)]
enum Installation {
    Factory,
    Mine,
    Defenses,
}

/// Planetary defenses are hard-capped at 100 per planet (planetary_tech.rst);
/// factories and mines have no such structural cap (only an operating one).
const MAX_DEFENSES: u32 = 100;

/// Per-unit cost of a buildable, in every dimension production spends.
/// Installations (factory/mine) use only resources + germanium; ship designs
/// can cost all three minerals plus resources.
#[derive(Clone, Copy)]
struct UnitCost {
    ironium: u32,
    boranium: u32,
    germanium: u32,
    resources: u32,
}

/// Whole units of a `cost` the planet can afford this step from `resources`
/// (banked + this turn's) and its surface minerals, and whether RESOURCES were
/// the binding limiter (vs a mineral). A zero-cost dimension never limits.
/// `resources` cost is always > 0 (guarded by the caller).
fn affordable(cost: &UnitCost, resources: u32, planet: &PlanetState) -> (u32, bool) {
    let by_resources = resources / cost.resources;
    // A zero-cost dimension never limits the build (checked_div(0) -> None).
    let by_mineral = |cost_n: u32, have: u32| have.checked_div(cost_n).unwrap_or(u32::MAX);
    let min_mineral = by_mineral(cost.ironium, planet.surface_ironium)
        .min(by_mineral(cost.boranium, planet.surface_boranium))
        .min(by_mineral(cost.germanium, planet.surface_germanium));
    (by_resources.min(min_mineral), by_resources <= min_mineral)
}

/// Deduct `built` units of `cost`'s minerals from the planet's surface stock.
fn spend_minerals(cost: &UnitCost, built: u32, planet: &mut PlanetState) {
    planet.surface_ironium -= built * cost.ironium;
    planet.surface_boranium -= built * cost.boranium;
    planet.surface_germanium -= built * cost.germanium;
}

/// Classify a queue item for this slice: which installation it builds, whether
/// it is an auto (capacity-bounded, repeating) item, and its per-unit cost.
/// `defense_cost` is the catalog cost of one defense (shared across all defense
/// types); `None` leaves defenses unbuildable. Returns `None` for any id this
/// slice does not yet build (caller stops).
fn classify(
    id: u32,
    race: &Race,
    defense_cost: Option<UnitCost>,
) -> Option<(Installation, bool, UnitCost)> {
    let b = fixed_by_id(id)?;
    let is_auto = b.category == Category::Auto;
    let eco = &race.economy;
    match b.kind {
        "factory" | "auto_factory" | "auto_max_factories" => Some((
            Installation::Factory,
            is_auto,
            UnitCost {
                ironium: 0,
                boranium: 0,
                // "Costs 1 less germanium to build factories" race option.
                germanium: if eco.factory_cheap_germanium { 3 } else { 4 },
                resources: eco.factory_cost,
            },
        )),
        "mine" | "auto_mine" | "auto_max_mines" => Some((
            Installation::Mine,
            is_auto,
            UnitCost {
                ironium: 0,
                boranium: 0,
                germanium: 0,
                resources: eco.mine_cost,
            },
        )),
        "defenses" | "auto_defenses" => {
            let mut cost = defense_cost?;
            // Inner Strength: planetary defenses cost 40% less (STARS help).
            if race.prt == Prt::Is {
                cost = scale_cost(cost, 60);
            }
            Some((Installation::Defenses, is_auto, cost))
        }
        // alchemy / terraform / ship designs: not built in this slice.
        _ => None,
    }
}

/// `cost` scaled to `percent`% in every dimension (integer, floored). Backs the
/// flat trait cost modifiers (e.g. Inner Strength defenses at 60%).
fn scale_cost(cost: UnitCost, percent: u32) -> UnitCost {
    let s = |n: u32| n * percent / 100;
    UnitCost {
        ironium: s(cost.ironium),
        boranium: s(cost.boranium),
        germanium: s(cost.germanium),
        resources: s(cost.resources),
    }
}

/// The catalog build cost of one planetary defense (all defense types share one
/// cost, per planetary_tech.rst), or `None` if the catalog has no defense item.
fn defense_unit_cost(parts: &[TechItem]) -> Option<UnitCost> {
    parts.iter().find_map(|t| match &t.props {
        Props::Planetary(PlanetaryKind::Defense { .. }) => Some(UnitCost {
            ironium: t.cost.ironium,
            boranium: t.cost.boranium,
            germanium: t.cost.germanium,
            resources: t.cost.resources,
        }),
        _ => None,
    })
}

/// How many of an installation an auto item builds toward. Factories/mines stop
/// at the colonist-operated capacity ``(pop / 10_000) × colonists_operate_*``;
/// defenses have no operating capacity — they build to the hard cap of 100.
fn capacity(install: Installation, population: u32, race: &Race) -> u32 {
    match install {
        Installation::Factory => (population / 10_000) * race.economy.colonists_operate_factories,
        Installation::Mine => (population / 10_000) * race.economy.colonists_operate_mines,
        Installation::Defenses => MAX_DEFENSES,
    }
}

/// Structural maximum of an installation on a planet, if any. Defenses cap at
/// 100; factories/mines have no cap (unoperated ones simply sit idle).
fn hard_cap(install: Installation) -> Option<u32> {
    match install {
        Installation::Defenses => Some(MAX_DEFENSES),
        Installation::Factory | Installation::Mine => None,
    }
}

/// Current count of an installation on the planet.
fn current(install: Installation, planet: &PlanetState) -> u32 {
    match install {
        Installation::Factory => planet.factories,
        Installation::Mine => planet.mines,
        Installation::Defenses => planet.defenses,
    }
}

/// Add `n` of an installation to the planet.
fn add(install: Installation, planet: &mut PlanetState, n: u32) {
    match install {
        Installation::Factory => planet.factories += n,
        Installation::Mine => planet.mines += n,
        Installation::Defenses => planet.defenses += n,
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

/// A completed ship build at a planet: `count` ships of the owner's ship-design
/// `design_slot`, to be spawned/merged into a fleet after the planet loop (when
/// `GameState.fleets` can be mutated). `route_target` carries the planet's
/// Route-To destination so a built ship departs along the route.
struct ShipBuild {
    planet_id: u32,
    owner: u32,
    design_slot: u32,
    count: u32,
    route_target: Option<u32>,
}

/// Run the production queue for one colonised, non-AR planet. Ship-design items
/// that complete are pushed to `builds` (fleets are spawned after the loop).
#[allow(clippy::too_many_arguments)]
fn produce_planet(
    planet_id: u32,
    planet: &mut PlanetState,
    race: &Race,
    designs: &[ShipDesign],
    ship_hulls: &[ShipHull],
    starbase_hulls: &[StarbaseHull],
    parts: &[TechItem],
    defense_cost: Option<UnitCost>,
    builds: &mut Vec<ShipBuild>,
) {
    if race.prt == Prt::Ar || planet.population == 0 {
        return;
    }

    let mut resources = generate_resources(planet, race);

    let mut i = 0;
    while i < planet.build_queue.len() {
        let id = planet.build_queue[i].build_object_id;

        // Ship design-slot item: build whole ships, bounded by resources and
        // every mineral; each completed ship is recorded for fleet spawning.
        if let Some(slot) = design_slot_of(id) {
            // The slot's ship design must exist (kind=ship); a queue item for a
            // deleted design blocks the queue rather than guessing (design
            // deletion vs in-progress build is handled separately).
            let Some(design) = designs
                .iter()
                .find(|d| d.slot == slot && d.kind == ShipDesignKind::Ship)
            else {
                break;
            };
            let Some(cost) = design_cost(design, ship_hulls, starbase_hulls, parts) else {
                break; // unknown hull — do not guess a cost
            };
            let cost = UnitCost {
                ironium: cost.ironium,
                boranium: cost.boranium,
                germanium: cost.germanium,
                resources: cost.resources,
            };
            if cost.resources == 0 {
                break; // a zero-resource ship would spin the queue; none exist
            }

            let want = planet.build_queue[i].build_quantity;
            if want == 0 {
                planet.build_queue.remove(i);
                continue;
            }

            let banked = planet.build_queue[i].build_progress;
            let avail = banked + resources;
            let (afford, resources_limited) = affordable(&cost, avail, planet);
            let built = afford.min(want);

            spend_minerals(&cost, built, planet);
            let leftover = avail - built * cost.resources;
            if built > 0 {
                builds.push(ShipBuild {
                    planet_id,
                    owner: planet
                        .owner
                        .expect("produce_planet only runs for owned planets"),
                    design_slot: slot,
                    count: built,
                    route_target: planet.route_target,
                });
            }

            let remaining = want - built;
            planet.build_queue[i].build_quantity = remaining;
            if remaining == 0 {
                planet.build_queue.remove(i);
                resources = leftover;
                continue;
            }
            // Bank progress only when resources were the limiter; if a mineral
            // blocked us the surplus resources are lost (use-it-or-lose-it).
            planet.build_queue[i].build_progress = if resources_limited { leftover } else { 0 };
            return;
        }

        let Some((install, is_auto, cost)) = classify(id, race, defense_cost) else {
            break; // unhandled item type blocks the queue (see module scope note)
        };
        if cost.resources == 0 {
            break; // guard against a zero-cost item spinning; none exist today
        }

        // How many units this item still wants: an auto item builds up to the
        // remaining colonist capacity; an explicit item builds its quantity,
        // clamped to any structural cap (defenses stop at 100 per planet).
        let want = if is_auto {
            capacity(install, planet.population, race).saturating_sub(current(install, planet))
        } else {
            let requested = planet.build_queue[i].build_quantity;
            match hard_cap(install) {
                Some(cap) => requested.min(cap.saturating_sub(current(install, planet))),
                None => requested,
            }
        };
        if want == 0 {
            if is_auto {
                i += 1; // at capacity — let resources flow to the next item
                continue;
            }
            planet.build_queue.remove(i); // explicit zero-quantity: drop it
            continue;
        }

        // Spend banked progress + this turn's resources, bounded by minerals.
        let banked = planet.build_queue[i].build_progress;
        let avail = banked + resources;
        let (afford, resources_limited) = affordable(&cost, avail, planet);
        let built = afford.min(want);

        add(install, planet, built);
        spend_minerals(&cost, built, planet);
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
        planet.build_queue[i].build_progress = if resources_limited { leftover } else { 0 };
        return;
    }
}

/// Step 10 of turn resolution: generate resources and run every colonised
/// planet's production queue against the installation economy.
pub fn run_production(game: &mut GameState) {
    // Snapshot each player's race + designs so planet_states can be borrowed
    // mutably in the loop (designs are small; cloned per turn).
    let races: HashMap<u32, Race> = game
        .players
        .iter()
        .filter_map(|p| p.race.as_ref().map(|r| (p.id, r.clone())))
        .collect();
    let designs: HashMap<u32, Vec<ShipDesign>> = game
        .players
        .iter()
        .map(|p| (p.id, p.designs.clone()))
        .collect();

    // Catalogs are static data; build once and share by reference.
    let ship_hulls = ship_hull_catalog();
    let starbase_hulls = starbase_hull_catalog();
    let parts = technology_catalog();
    let defense_cost = defense_unit_cost(&parts);

    let empty: Vec<ShipDesign> = Vec::new();
    let mut builds: Vec<ShipBuild> = Vec::new();
    for (pid, planet) in game.planet_states.iter_mut() {
        let Some(owner) = planet.owner else { continue };
        let Some(race) = races.get(&owner) else {
            continue;
        };
        let owner_designs = designs.get(&owner).unwrap_or(&empty);
        produce_planet(
            *pid,
            planet,
            race,
            owner_designs,
            &ship_hulls,
            &starbase_hulls,
            &parts,
            defense_cost,
            &mut builds,
        );
    }

    apply_ship_builds(game, &designs, &ship_hulls, builds);
}

/// Spawn or merge fleets for the ships completed this turn. A planet with a
/// Route-To destination sends its built ships off in a NEW fleet carrying a
/// waypoint to that planet (route-on-build); otherwise the ships merge into an
/// idle own fleet already orbiting the planet, or form a new orbiting fleet.
/// Built ships start with full fuel (sum of their hulls' fuel capacity).
fn apply_ship_builds(
    game: &mut GameState,
    designs: &HashMap<u32, Vec<ShipDesign>>,
    ship_hulls: &[ShipHull],
    builds: Vec<ShipBuild>,
) {
    if builds.is_empty() {
        return;
    }

    // Fleet ids share the universe-wide space-object id space with planets, so
    // allocate above every existing planet AND fleet id.
    let mut next_id = game
        .universe
        .planets
        .keys()
        .chain(game.fleets.keys())
        .copied()
        .max()
        .map_or(0, |m| m + 1);

    // Group completed builds by planet; all builds at a planet share its
    // route disposition (route_target is a planet property).
    let mut by_planet: HashMap<u32, Vec<&ShipBuild>> = HashMap::new();
    for b in &builds {
        by_planet.entry(b.planet_id).or_default().push(b);
    }

    for (planet_id, planet_builds) in by_planet {
        let owner = planet_builds[0].owner;
        let route_target = planet_builds[0].route_target;
        let (px, py) = match game.universe.planets.get(&planet_id) {
            Some(p) => (p.x, p.y),
            None => continue,
        };

        // Combine into stacks by design slot and total the built ships' fuel.
        let mut stacks: HashMap<u32, u32> = HashMap::new();
        let mut fuel: u32 = 0;
        let owner_designs = designs.get(&owner).map(Vec::as_slice).unwrap_or(&[]);
        for b in &planet_builds {
            *stacks.entry(b.design_slot).or_default() += b.count;
            if let Some(cap) = design_fuel_capacity(b.design_slot, owner_designs, ship_hulls) {
                fuel += cap * b.count;
            }
        }

        // Try to merge into an existing idle own fleet orbiting this planet,
        // unless the ships are routed away (routed ships depart in a new fleet).
        let merge_target = if route_target.is_some() {
            None
        } else {
            game.fleets.values_mut().find(|f| {
                f.owner == owner
                    && f.orbiting_planet_id == Some(planet_id)
                    && f.waypoints.is_empty()
            })
        };

        if let Some(fleet) = merge_target {
            for (slot, count) in stacks {
                merge_stack(fleet, slot, count);
            }
            fleet.fuel += fuel;
            continue;
        }

        let id = next_id;
        next_id += 1;
        let ship_stacks: Vec<ShipStack> = stacks
            .into_iter()
            .map(|(slot, count)| ShipStack {
                design_slot: slot,
                count: NonZeroU32::new(count).expect("a recorded build has count >= 1"),
            })
            .collect();
        let name = fleet_name(planet_builds[0].design_slot, owner_designs, id);

        let waypoints = match route_target.and_then(|t| game.universe.planets.get(&t)) {
            Some(target) => vec![FleetWaypoint {
                x: target.x,
                y: target.y,
                target_planet_id: route_target,
                warp: ROUTE_WARP,
                task: FleetWaypointTask::None,
            }],
            None => Vec::new(),
        };

        game.fleets.insert(
            id,
            Fleet {
                id,
                name,
                owner,
                x: px,
                y: py,
                orbiting_planet_id: Some(planet_id),
                ship_stacks,
                fuel,
                cargo: FleetCargo {
                    ironium: 0,
                    boranium: 0,
                    germanium: 0,
                    colonists: 0,
                },
                waypoints,
                repeat_orders: false,
            },
        );
    }
}

/// Add `count` ships of `slot` to a fleet, extending the matching stack or
/// adding a new one.
fn merge_stack(fleet: &mut Fleet, slot: u32, count: u32) {
    if let Some(stack) = fleet.ship_stacks.iter_mut().find(|s| s.design_slot == slot) {
        stack.count = NonZeroU32::new(stack.count.get() + count).expect("sum of positives");
    } else {
        fleet.ship_stacks.push(ShipStack {
            design_slot: slot,
            count: NonZeroU32::new(count).expect("a recorded build has count >= 1"),
        });
    }
}

/// Fuel capacity of one ship of the design in `slot` (its hull's capacity).
fn design_fuel_capacity(slot: u32, designs: &[ShipDesign], ship_hulls: &[ShipHull]) -> Option<u32> {
    let design = designs
        .iter()
        .find(|d| d.slot == slot && d.kind == ShipDesignKind::Ship)?;
    ship_hulls
        .iter()
        .find(|h| u32::from(h.id) == design.hull_id)
        .map(|h| h.fuel_capacity)
}

/// Name a freshly built fleet after the design that seeded it, matching the
/// original game's "<design> #<id>" style.
fn fleet_name(slot: u32, designs: &[ShipDesign], id: u32) -> String {
    let design_name = designs
        .iter()
        .find(|d| d.slot == slot && d.kind == ShipDesignKind::Ship)
        .map(|d| d.name.as_str())
        .unwrap_or("Fleet");
    format!("{design_name} #{id}")
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
                designs: vec![],
                difficulty: None,
            }],
            year: 2400,
            player_messages: Default::default(),
            fleets: Default::default(),
            settings: None,
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

    // ── ship builds (design-slot queue items spawn fleets) ───────────────────

    use crate::game::objects::buildable::DESIGN_ID_BASE;
    use crate::game::objects::ship_hull_catalog::ship_hull_catalog;

    /// An empty ship design in `slot` on the given hull (cost = hull cost).
    fn ship_design(slot: u32, hull_id: u32) -> ShipDesign {
        ShipDesign {
            slot,
            kind: ShipDesignKind::Ship,
            name: "Scout".into(),
            hull_id,
            slot_assignments: vec![],
        }
    }

    /// A design-slot queue item for ship slot 0, pre-banked with enough
    /// resources that the build completes this turn regardless of hull cost.
    fn ship_item(qty: u32, banked: u32) -> BuildItem {
        BuildItem {
            build_object_id: DESIGN_ID_BASE,
            build_progress: banked,
            build_quantity: qty,
        }
    }

    /// Give the homeworld a ship design in slot 0 and ample surface minerals.
    fn arm_for_ship_build(game: &mut GameState, hw: u32, hull_id: u32) {
        game.players[0].designs.push(ship_design(0, hull_id));
        let s = game.planet_states.get_mut(&hw).unwrap();
        s.surface_ironium = 100_000;
        s.surface_boranium = 100_000;
        s.surface_germanium = 100_000;
    }

    #[test]
    fn a_built_ship_spawns_a_fleet_at_the_planet() {
        let hull = ship_hull_catalog().into_iter().next().unwrap();
        let (mut game, hw) = homeworld_game(vec![ship_item(1, 100_000)]);
        arm_for_ship_build(&mut game, hw, u32::from(hull.id));

        run_production(&mut game);

        assert_eq!(game.fleets.len(), 1, "one fleet spawned");
        let f = game.fleets.values().next().unwrap();
        assert_eq!(f.owner, 0);
        assert_eq!(f.orbiting_planet_id, Some(hw));
        assert_eq!(f.ship_stacks.len(), 1);
        assert_eq!(f.ship_stacks[0].design_slot, 0);
        assert_eq!(f.ship_stacks[0].count.get(), 1);
        assert_eq!(
            f.fuel, hull.fuel_capacity,
            "built ship starts with full fuel"
        );
        assert!(f.waypoints.is_empty(), "no route set -> idle fleet");
        assert!(
            game.planet_states[&hw].build_queue.is_empty(),
            "completed item removed"
        );
    }

    #[test]
    fn route_on_build_gives_the_fleet_a_waypoint_to_the_route_target() {
        let hull = ship_hull_catalog().into_iter().next().unwrap();
        let (mut game, hw) = homeworld_game(vec![ship_item(1, 100_000)]);
        arm_for_ship_build(&mut game, hw, u32::from(hull.id));
        // Route to some other planet.
        let target = *game.universe.planets.keys().find(|&&p| p != hw).unwrap();
        game.planet_states.get_mut(&hw).unwrap().route_target = Some(target);

        run_production(&mut game);

        let f = game.fleets.values().next().unwrap();
        assert_eq!(f.waypoints.len(), 1, "routed build carries one waypoint");
        let wp = &f.waypoints[0];
        assert_eq!(wp.target_planet_id, Some(target));
        let tp = &game.universe.planets[&target];
        assert_eq!(
            (wp.x, wp.y),
            (tp.x, tp.y),
            "waypoint sits on the target planet"
        );
        assert_eq!(wp.warp, ROUTE_WARP);
    }

    #[test]
    fn built_ships_merge_into_an_idle_fleet_already_in_orbit() {
        let hull = ship_hull_catalog().into_iter().next().unwrap();
        let (mut game, hw) = homeworld_game(vec![ship_item(1, 100_000)]);
        arm_for_ship_build(&mut game, hw, u32::from(hull.id));
        // An idle own fleet of the same design already orbits the homeworld.
        let (px, py) = {
            let p = &game.universe.planets[&hw];
            (p.x, p.y)
        };
        game.fleets.insert(
            7000,
            Fleet {
                id: 7000,
                name: "Scouts".into(),
                owner: 0,
                x: px,
                y: py,
                orbiting_planet_id: Some(hw),
                ship_stacks: vec![ShipStack {
                    design_slot: 0,
                    count: NonZeroU32::new(2).unwrap(),
                }],
                fuel: 0,
                cargo: FleetCargo {
                    ironium: 0,
                    boranium: 0,
                    germanium: 0,
                    colonists: 0,
                },
                waypoints: vec![],
                repeat_orders: false,
            },
        );

        run_production(&mut game);

        assert_eq!(game.fleets.len(), 1, "merged, no new fleet");
        let f = &game.fleets[&7000];
        assert_eq!(f.ship_stacks.len(), 1);
        assert_eq!(f.ship_stacks[0].count.get(), 3, "2 existing + 1 built");
    }

    #[test]
    fn a_ship_blocked_on_a_missing_mineral_does_not_build() {
        // A hull that costs ironium cannot be built with no ironium on hand.
        let hull = ship_hull_catalog()
            .into_iter()
            .find(|h| h.cost.ironium > 0)
            .expect("some ship hull costs ironium");
        let (mut game, hw) = homeworld_game(vec![ship_item(1, 100_000)]);
        arm_for_ship_build(&mut game, hw, u32::from(hull.id));
        game.planet_states.get_mut(&hw).unwrap().surface_ironium = 0;

        run_production(&mut game);

        assert!(game.fleets.is_empty(), "no ship built without ironium");
        let q = &game.planet_states[&hw].build_queue;
        assert_eq!(q.len(), 1, "item still queued");
        assert_eq!(q[0].build_quantity, 1, "nothing built");
    }

    #[test]
    fn a_queue_item_for_a_deleted_design_blocks_the_queue() {
        // No design in slot 0 -> the item cannot build and blocks (deletion vs
        // in-progress build is handled separately).
        let (mut game, hw) = homeworld_game(vec![ship_item(1, 100_000)]);
        // Note: NOT calling arm_for_ship_build, so there is no design in slot 0.
        run_production(&mut game);
        assert!(game.fleets.is_empty());
        assert_eq!(game.planet_states[&hw].build_queue.len(), 1, "blocked");
    }

    // ── defenses (id 9 explicit, 22 auto; cost 5/5/5/15; cap 100) ────────────

    const DEFENSES: u32 = 9;
    const AUTO_DEFENSES: u32 = 22;

    /// Give the homeworld ample surface minerals so defense builds are bounded
    /// by resources, not minerals.
    fn stock_minerals(game: &mut GameState, hw: u32) {
        let s = game.planet_states.get_mut(&hw).unwrap();
        s.surface_ironium = 100_000;
        s.surface_boranium = 100_000;
        s.surface_germanium = 100_000;
    }

    #[test]
    fn explicit_defenses_build_what_resources_allow_and_bank_the_rest() {
        // 125 resources / 15 per defense = 8 defenses; minerals ample.
        let (mut game, hw) = homeworld_game(vec![item(DEFENSES, 16)]);
        stock_minerals(&mut game, hw);
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.defenses, 8, "8 defenses built from 125 resources");
        assert_eq!(p.surface_ironium, 100_000 - 8 * 5);
        assert_eq!(p.surface_boranium, 100_000 - 8 * 5);
        assert_eq!(p.surface_germanium, 100_000 - 8 * 5);
        assert_eq!(p.build_queue[0].build_quantity, 8, "8 of 16 remain");
        assert_eq!(
            p.build_queue[0].build_progress,
            125 - 8 * 15,
            "resource leftover banked"
        );
    }

    #[test]
    fn defenses_cap_at_100_per_planet() {
        let (mut game, hw) = homeworld_game(vec![item(DEFENSES, 16)]);
        stock_minerals(&mut game, hw);
        game.planet_states.get_mut(&hw).unwrap().defenses = 98;
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.defenses, 100, "only 2 of the 16 fit under the cap");
        assert!(
            p.build_queue.is_empty(),
            "item dropped once the cap is reached"
        );
    }

    #[test]
    fn auto_defenses_build_toward_the_cap_and_stay_queued() {
        let (mut game, hw) = homeworld_game(vec![item(AUTO_DEFENSES, 0)]);
        stock_minerals(&mut game, hw);
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.defenses, 8, "125 resources / 15 = 8 this turn");
        assert_eq!(p.build_queue.len(), 1, "auto item is never removed");
    }

    #[test]
    fn defenses_blocked_without_a_mineral() {
        // Defenses cost ironium; with none on hand none build.
        let (mut game, hw) = homeworld_game(vec![item(DEFENSES, 5)]);
        game.planet_states.get_mut(&hw).unwrap().surface_ironium = 0;
        run_production(&mut game);
        assert_eq!(
            game.planet_states[&hw].defenses, 0,
            "no ironium -> no defenses"
        );
    }

    #[test]
    fn inner_strength_defenses_cost_40_percent_less() {
        // IS pays 60% of 5/5/5/15 = 3/3/3/9 per defense, so 125 resources buys
        // 13 (125/9) instead of the 8 (125/15) other races get.
        let (mut game, hw) = homeworld_game(vec![item(DEFENSES, 16)]);
        stock_minerals(&mut game, hw);
        game.players[0].race.as_mut().unwrap().prt = Prt::Is;
        run_production(&mut game);
        let p = &game.planet_states[&hw];
        assert_eq!(p.defenses, 13, "cheaper IS defenses: 125/9 = 13");
        assert_eq!(p.surface_ironium, 100_000 - 13 * 3, "3 ironium each for IS");
        assert_eq!(p.surface_germanium, 100_000 - 13 * 3);
    }

    #[test]
    fn ar_planets_build_no_defenses() {
        // AR builds nothing in this economy, defenses included (AR does not use
        // planetary defenses).
        let (mut game, hw) = homeworld_game(vec![item(DEFENSES, 16)]);
        stock_minerals(&mut game, hw);
        game.players[0].race.as_mut().unwrap().prt = Prt::Ar;
        run_production(&mut game);
        assert_eq!(game.planet_states[&hw].defenses, 0, "AR builds no defenses");
    }
}
