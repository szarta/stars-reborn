// engine/src/game/orders/mod.rs
//
// Player order application. The http layer deserializes a submit-orders body
// (schemas/request-submit-orders.json) into these types and calls into here;
// all validation and state mutation lives in this module, not in http.
//
// This slice implements the production-queue order (`planet.set_production_queue`)
// and the route-to order (`planet.set_route_target`).
// Other order kinds in the schema are not yet applied — the engine
// rejects them explicitly rather than silently accepting a no-op, so a client
// is never told an order succeeded when nothing happened. They land as their
// own engine slices.

use serde::Deserialize;

use crate::game::objects::buildable::{design_build_object_id, fixed_by_kind};
use crate::game::objects::planet::BuildItem;
use crate::game::objects::player::{ShipDesign, ShipDesignKind, TechLevels};
use crate::game::objects::race::{Lrt, Prt, Race};
use crate::game::objects::ship_hull_catalog::ship_hull_catalog;
use crate::game::objects::starbase_hull_catalog::starbase_hull_catalog;
use crate::game::objects::technology::{HullRequirement, TechRequirements};
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
    /// A route order named a target planet that does not exist.
    RouteTargetNotFound(u32),
    /// A design order named a player id with no player.
    PlayerNotFound(u32),
    /// A design slot outside the valid range for its kind (ships 0–15,
    /// starbases 0–9).
    DesignSlotOutOfRange { kind: ShipDesignKind, slot: u32 },
    /// A design named a hull id not in the catalog for its kind.
    DesignHullNotFound { kind: ShipDesignKind, hull_id: u32 },
    /// A design named a hull the player cannot build: its tech requirements are
    /// not met, or its PRT/LRT gate is not satisfied by the player's race.
    DesignHullNotAvailable { kind: ShipDesignKind, hull_id: u32 },
    /// A slot assignment targeted a slot index that does not exist on the hull,
    /// or placed more parts in a slot than its max count allows.
    DesignSlotAssignmentInvalid { slot_index: u32 },
    /// An edit/delete targeted a slot whose design is built (built-count > 0);
    /// the slot is locked until the last ship of that design is gone.
    DesignSlotLocked { kind: ShipDesignKind, slot: u32 },
    /// A delete targeted a (kind, slot) with no design.
    DesignNotFound { kind: ShipDesignKind, slot: u32 },
    /// A production queue item named a ship design slot that the player has no
    /// design in — there is nothing to build there.
    BuildDesignSlotEmpty { slot: u32 },
}

/// Highest valid design slot per kind: ship designs occupy slots 0–15, starbase
/// designs 0–9 (a parallel space, disambiguated by kind).
fn max_design_slot(kind: ShipDesignKind) -> u32 {
    match kind {
        ShipDesignKind::Ship => 15,
        ShipDesignKind::Starbase => 9,
    }
}

/// True when a player's researched tech levels meet a hull's/part's tech
/// requirement in every field.
fn tech_requirements_met(req: &TechRequirements, tech: &TechLevels) -> bool {
    u32::from(req.energy) <= tech.energy
        && u32::from(req.weapons) <= tech.weapons
        && u32::from(req.propulsion) <= tech.propulsion
        && u32::from(req.construction) <= tech.construction
        && u32::from(req.electronics) <= tech.electronics
        && u32::from(req.bio) <= tech.biotechnology
}

/// True when a player's race satisfies a hull's PRT/LRT gate. `None` is open to
/// all races. With no race on record (a back-compat game persisted before the
/// race model) the gate cannot be checked and is treated as satisfied.
/// Mystery-Trader hulls are not gated on race here — acquisition via an MT
/// exchange is not modelled yet, so gating them would wrongly block them.
fn hull_requirement_met(req: Option<HullRequirement>, race: Option<&Race>) -> bool {
    let Some(req) = req else {
        return true;
    };
    let Some(race) = race else {
        return true;
    };
    match req {
        HullRequirement::HE => race.prt == Prt::He,
        HullRequirement::SS => race.prt == Prt::Ss,
        HullRequirement::WM => race.prt == Prt::Wm,
        HullRequirement::IS => race.prt == Prt::Is,
        HullRequirement::SD => race.prt == Prt::Sd,
        HullRequirement::AR => race.prt == Prt::Ar,
        HullRequirement::ARM => race.lrts.contains(&Lrt::Arm),
        HullRequirement::ISB => race.lrts.contains(&Lrt::Isb),
        HullRequirement::MT => true,
    }
}

/// Number of ships of a given design currently in existence across the player's
/// fleets. The engine does not model fleets yet, so this is always 0 (no design
/// is ever built, so no slot is ever locked). When fleets land, count ships
/// whose design matches `(kind, slot)`. See docs/mechanics/ship_design.rst.
pub fn design_built_count(
    _game: &GameState,
    _player_id: u32,
    _kind: ShipDesignKind,
    _slot: u32,
) -> u32 {
    0
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
        .get(&planet_id)
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
        // A design-slot item must resolve to a real ship design the player owns
        // in that slot (production design slots are ship designs, 0–15).
        if let BuildKind::Design { design_slot } = &it.item {
            let design_slot = *design_slot;
            let has_design = game
                .players
                .iter()
                .find(|p| p.id == player_id)
                .is_some_and(|p| {
                    p.designs
                        .iter()
                        .any(|d| d.kind == ShipDesignKind::Ship && d.slot == design_slot)
                });
            if !has_design {
                return Err(OrderError::BuildDesignSlotEmpty { slot: design_slot });
            }
        }
        queue.push(BuildItem {
            build_object_id,
            build_quantity: it.count,
            build_progress: 0,
        });
    }

    game.planet_states
        .get_mut(&planet_id)
        .expect("planet existence checked above")
        .build_queue = queue;
    Ok(())
}

/// Apply a `planet.set_route_target` order: set (or, with `target = None`,
/// clear) the planet's "Route To" destination.
///
/// The submitting player must own `planet_id`. A non-null `target` must name an
/// existing planet (any planet may be a route destination, owned or not); it is
/// validated before anything is written so a bad target leaves the route
/// unchanged.
pub fn apply_set_route_target(
    game: &mut GameState,
    player_id: u32,
    planet_id: u32,
    target: Option<u32>,
) -> Result<(), OrderError> {
    if let Some(t) = target {
        if !game.planet_states.contains_key(&t) {
            return Err(OrderError::RouteTargetNotFound(t));
        }
    }

    let planet = game
        .planet_states
        .get_mut(&planet_id)
        .ok_or(OrderError::PlanetNotFound(planet_id))?;

    if planet.owner != Some(player_id) {
        return Err(OrderError::PlanetNotOwned(planet_id));
    }

    planet.route_target = target;
    Ok(())
}

/// Apply a `design.upsert` order: create or replace the submitting player's
/// design in `design.slot` (a ship slot 0–15 or a starbase slot 0–9, by
/// `design.kind`). Validates before writing: the slot must be in range for its
/// kind, the hull id must exist in the matching catalog, and the slot must not
/// be locked (its current design is built, built-count > 0). On success the new
/// design replaces any existing design in that `(kind, slot)`.
pub fn apply_design_upsert(
    game: &mut GameState,
    player_id: u32,
    design: ShipDesign,
) -> Result<(), OrderError> {
    let kind = design.kind;
    let slot = design.slot;
    let hull_id = design.hull_id;
    if slot > max_design_slot(kind) {
        return Err(OrderError::DesignSlotOutOfRange { kind, slot });
    }

    // Look up the hull in the catalog for its kind, taking the gating and slot
    // grid we need to validate the design. Unknown id => DesignHullNotFound.
    let (requirements, requirement, slots) = match kind {
        ShipDesignKind::Ship => ship_hull_catalog()
            .into_iter()
            .find(|h| u32::from(h.id) == hull_id)
            .map(|h| (h.requirements, h.requirement, h.slots)),
        ShipDesignKind::Starbase => starbase_hull_catalog()
            .into_iter()
            .find(|h| u32::from(h.id) == hull_id)
            .map(|h| (h.requirements, h.requirement, h.slots)),
    }
    .ok_or(OrderError::DesignHullNotFound { kind, hull_id })?;

    // The hull must be available to this player: tech levels met and the
    // PRT/LRT gate satisfied by the player's race.
    let player = game
        .players
        .iter()
        .find(|p| p.id == player_id)
        .ok_or(OrderError::PlayerNotFound(player_id))?;
    if !tech_requirements_met(&requirements, &player.tech)
        || !hull_requirement_met(requirement, player.race.as_ref())
    {
        return Err(OrderError::DesignHullNotAvailable { kind, hull_id });
    }

    // Each slot assignment must target a real slot on the hull and respect its
    // max count. (Which part kinds a slot accepts is validated once the
    // component catalog is complete — see docs/mechanics/ship_design.rst.)
    for sa in &design.slot_assignments {
        let hull_slot =
            slots
                .get(sa.slot_index as usize)
                .ok_or(OrderError::DesignSlotAssignmentInvalid {
                    slot_index: sa.slot_index,
                })?;
        if sa.count.get() > u32::from(hull_slot.max_count) {
            return Err(OrderError::DesignSlotAssignmentInvalid {
                slot_index: sa.slot_index,
            });
        }
    }

    // A built design's slot is locked (cannot be edited) until its last ship is
    // gone. built-count is 0 until fleets are modelled, so this never fires yet.
    if design_built_count(game, player_id, kind, slot) > 0 {
        return Err(OrderError::DesignSlotLocked { kind, slot });
    }

    let player = game
        .players
        .iter_mut()
        .find(|p| p.id == player_id)
        .ok_or(OrderError::PlayerNotFound(player_id))?;
    match player
        .designs
        .iter_mut()
        .find(|d| d.kind == kind && d.slot == slot)
    {
        Some(existing) => *existing = design,
        None => player.designs.push(design),
    }
    Ok(())
}

/// Apply a `design.delete` order: remove the submitting player's design in
/// `(kind, slot)`. Fails if there is no such design, or if it is locked
/// (built-count > 0).
pub fn apply_design_delete(
    game: &mut GameState,
    player_id: u32,
    kind: ShipDesignKind,
    slot: u32,
) -> Result<(), OrderError> {
    if design_built_count(game, player_id, kind, slot) > 0 {
        return Err(OrderError::DesignSlotLocked { kind, slot });
    }
    let player = game
        .players
        .iter_mut()
        .find(|p| p.id == player_id)
        .ok_or(OrderError::PlayerNotFound(player_id))?;
    let before = player.designs.len();
    player
        .designs
        .retain(|d| !(d.kind == kind && d.slot == slot));
    if player.designs.len() == before {
        return Err(OrderError::DesignNotFound { kind, slot });
    }
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
                designs: vec![],
            }],
            year: 2400,
        };
        (game, hw)
    }

    #[test]
    fn sets_queue_on_owned_planet() {
        let (mut game, hw) = one_player_game();
        // A design must exist in the ship slot before it can be queued.
        game.players[0]
            .designs
            .push(design(1, ShipDesignKind::Ship, a_ship_hull(), "Scout"));
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
    fn rejects_building_an_empty_design_slot() {
        let (mut game, hw) = one_player_game();
        // Slot 2 holds no design, so it cannot be built.
        let err = apply_set_production_queue(
            &mut game,
            0,
            hw,
            &[ProductionItemInput {
                item: BuildKind::Design { design_slot: 2 },
                count: 1,
            }],
        )
        .unwrap_err();
        assert_eq!(err, OrderError::BuildDesignSlotEmpty { slot: 2 });
        assert!(game.planet_states[&hw].build_queue.is_empty());

        // Once a design exists in the slot, the same order resolves.
        game.players[0]
            .designs
            .push(design(2, ShipDesignKind::Ship, a_ship_hull(), "Scout"));
        apply_set_production_queue(
            &mut game,
            0,
            hw,
            &[ProductionItemInput {
                item: BuildKind::Design { design_slot: 2 },
                count: 1,
            }],
        )
        .unwrap();
        assert_eq!(game.planet_states[&hw].build_queue.len(), 1);
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

    /// Any planet id present in the game other than `hw`.
    fn other_planet(game: &GameState, hw: u32) -> u32 {
        *game
            .planet_states
            .keys()
            .find(|&&id| id != hw)
            .expect("universe has a second planet")
    }

    #[test]
    fn sets_and_clears_route_target() {
        let (mut game, hw) = one_player_game();
        let target = other_planet(&game, hw);

        apply_set_route_target(&mut game, 0, hw, Some(target)).unwrap();
        assert_eq!(game.planet_states[&hw].route_target, Some(target));

        // None clears it.
        apply_set_route_target(&mut game, 0, hw, None).unwrap();
        assert_eq!(game.planet_states[&hw].route_target, None);
    }

    #[test]
    fn rejects_route_on_unowned_planet() {
        let (mut game, hw) = one_player_game();
        let target = other_planet(&game, hw);
        let err = apply_set_route_target(&mut game, 2, hw, Some(target)).unwrap_err();
        assert_eq!(err, OrderError::PlanetNotOwned(hw));
        assert_eq!(game.planet_states[&hw].route_target, None);
    }

    #[test]
    fn rejects_nonexistent_route_target_atomically() {
        let (mut game, hw) = one_player_game();
        let target = other_planet(&game, hw);
        apply_set_route_target(&mut game, 0, hw, Some(target)).unwrap();

        let missing = 9999;
        let err = apply_set_route_target(&mut game, 0, hw, Some(missing)).unwrap_err();
        assert_eq!(err, OrderError::RouteTargetNotFound(missing));
        // prior route is preserved
        assert_eq!(game.planet_states[&hw].route_target, Some(target));
    }

    // -- ship designs --------------------------------------------------------

    fn design(slot: u32, kind: ShipDesignKind, hull_id: u32, name: &str) -> ShipDesign {
        ShipDesign {
            slot,
            kind,
            name: name.into(),
            hull_id,
            slot_assignments: vec![crate::game::objects::player::SlotAssignment {
                slot_index: 0,
                part_id: 112, // a valid engine id
                count: std::num::NonZeroU32::new(1).unwrap(),
            }],
        }
    }

    fn a_ship_hull() -> u32 {
        u32::from(ship_hull_catalog()[0].id)
    }

    #[test]
    fn design_upsert_creates_then_replaces_in_same_slot() {
        let (mut game, _) = one_player_game();
        let hull = a_ship_hull();
        apply_design_upsert(
            &mut game,
            0,
            design(3, ShipDesignKind::Ship, hull, "Scout I"),
        )
        .unwrap();
        assert_eq!(game.players[0].designs.len(), 1);
        assert_eq!(game.players[0].designs[0].name, "Scout I");

        // Same (kind, slot) replaces, not appends.
        apply_design_upsert(
            &mut game,
            0,
            design(3, ShipDesignKind::Ship, hull, "Scout II"),
        )
        .unwrap();
        assert_eq!(game.players[0].designs.len(), 1);
        assert_eq!(game.players[0].designs[0].name, "Scout II");

        // A starbase slot 3 is a parallel space — distinct from ship slot 3.
        let sb = u32::from(starbase_hull_catalog()[0].id);
        apply_design_upsert(
            &mut game,
            0,
            design(3, ShipDesignKind::Starbase, sb, "Fort"),
        )
        .unwrap();
        assert_eq!(game.players[0].designs.len(), 2);
    }

    #[test]
    fn design_upsert_validates_slot_and_hull() {
        let (mut game, _) = one_player_game();
        let hull = a_ship_hull();
        // Ship slot 16 is out of range (ships are 0–15).
        let err = apply_design_upsert(&mut game, 0, design(16, ShipDesignKind::Ship, hull, "x"))
            .unwrap_err();
        assert_eq!(
            err,
            OrderError::DesignSlotOutOfRange {
                kind: ShipDesignKind::Ship,
                slot: 16
            }
        );
        // Starbase slot 10 is out of range (starbases are 0–9).
        let sb = u32::from(starbase_hull_catalog()[0].id);
        let err = apply_design_upsert(&mut game, 0, design(10, ShipDesignKind::Starbase, sb, "x"))
            .unwrap_err();
        assert!(matches!(
            err,
            OrderError::DesignSlotOutOfRange { slot: 10, .. }
        ));
        // Unknown hull id.
        let err = apply_design_upsert(&mut game, 0, design(0, ShipDesignKind::Ship, 254, "x"))
            .unwrap_err();
        assert_eq!(
            err,
            OrderError::DesignHullNotFound {
                kind: ShipDesignKind::Ship,
                hull_id: 254
            }
        );
        assert!(game.players[0].designs.is_empty());
    }

    #[test]
    fn design_upsert_rejects_hull_not_researched() {
        // Ship hull 167 requires Construction 6; the test player has all-zero
        // tech, so the hull is in the catalog but not yet available.
        let (mut game, _) = one_player_game();
        let err = apply_design_upsert(&mut game, 0, design(0, ShipDesignKind::Ship, 167, "frig"))
            .unwrap_err();
        assert_eq!(
            err,
            OrderError::DesignHullNotAvailable {
                kind: ShipDesignKind::Ship,
                hull_id: 167
            }
        );
        assert!(game.players[0].designs.is_empty());
    }

    #[test]
    fn design_upsert_enforces_starbase_prt_lrt_gate() {
        // Space Dock (158) requires the Improved Starbases LRT. Max out tech so
        // only the LRT gate can block it; a Joat player without ISB is refused,
        // and granting the LRT makes it available.
        let (mut game, _) = one_player_game();
        game.players[0].tech = TechLevels {
            energy: 26,
            weapons: 26,
            propulsion: 26,
            construction: 26,
            electronics: 26,
            biotechnology: 26,
        };
        let err = apply_design_upsert(
            &mut game,
            0,
            design(0, ShipDesignKind::Starbase, 158, "dock"),
        )
        .unwrap_err();
        assert_eq!(
            err,
            OrderError::DesignHullNotAvailable {
                kind: ShipDesignKind::Starbase,
                hull_id: 158
            }
        );

        game.players[0].race.as_mut().unwrap().lrts.push(Lrt::Isb);
        apply_design_upsert(
            &mut game,
            0,
            design(0, ShipDesignKind::Starbase, 158, "dock"),
        )
        .unwrap();
        assert_eq!(game.players[0].designs.len(), 1);
    }

    #[test]
    fn design_upsert_validates_slot_assignments() {
        let (mut game, _) = one_player_game();
        let scout = a_ship_hull(); // Scout: slots 0..=2 (engine/general/scanner)

        // A slot index past the hull's slot count is rejected.
        let mut d = design(0, ShipDesignKind::Ship, scout, "x");
        d.slot_assignments[0].slot_index = 5;
        let err = apply_design_upsert(&mut game, 0, d).unwrap_err();
        assert_eq!(
            err,
            OrderError::DesignSlotAssignmentInvalid { slot_index: 5 }
        );

        // More parts than the slot holds (the Scout engine slot holds one).
        let mut d = design(0, ShipDesignKind::Ship, scout, "x");
        d.slot_assignments[0].count = std::num::NonZeroU32::new(2).unwrap();
        let err = apply_design_upsert(&mut game, 0, d).unwrap_err();
        assert_eq!(
            err,
            OrderError::DesignSlotAssignmentInvalid { slot_index: 0 }
        );

        assert!(game.players[0].designs.is_empty());
    }

    #[test]
    fn design_delete_removes_and_reports_missing() {
        let (mut game, _) = one_player_game();
        let hull = a_ship_hull();
        apply_design_upsert(&mut game, 0, design(2, ShipDesignKind::Ship, hull, "s")).unwrap();
        apply_design_delete(&mut game, 0, ShipDesignKind::Ship, 2).unwrap();
        assert!(game.players[0].designs.is_empty());
        // Deleting again (or a never-created slot) errors.
        let err = apply_design_delete(&mut game, 0, ShipDesignKind::Ship, 2).unwrap_err();
        assert_eq!(
            err,
            OrderError::DesignNotFound {
                kind: ShipDesignKind::Ship,
                slot: 2
            }
        );
    }

    #[test]
    fn designs_project_into_the_turn_file() {
        let (mut game, _) = one_player_game();
        let hull = a_ship_hull();
        apply_design_upsert(
            &mut game,
            0,
            design(5, ShipDesignKind::Ship, hull, "Range Scout"),
        )
        .unwrap();
        let view = crate::game::view::player_view(&game, 0);
        assert_eq!(view.ship_designs.len(), 1);
        let d = &view.ship_designs[0];
        assert_eq!(d.slot, 5);
        assert_eq!(d.name, "Range Scout");
        assert_eq!(d.hull_id, hull);
        // No fleets yet, so nothing is built.
        assert_eq!(d.built_count, 0);
    }
}
