// engine/src/game/view.rs
//
// PlayerView — the single choke point that projects a player's fog-of-war
// view from the host-side GameState. Every per-player turn file MUST be
// produced by `player_view()`; serialising GameState directly to a non-host
// client is a leak.
//
// Per stars-reborn-design/docs/architecture.rst (Per-Player Visibility),
// each planet appears in one of three states for a given player:
//
//   1. Never observed     — only identity (id, name, x, y) is known.
//   2. Observed, stale    — last-snapshot values + years_since_last_scan > 0.
//   3. Currently scanned  — current ground-truth values; years_since_last_scan = 0.
//
// State (2) is not yet reachable: scanner mechanics and per-player intel
// persistence land in a later commit. For now the visibility rule is
// "fields visible iff the player owns the planet" — the player's homeworld
// (and any later-colonised planets) appear as Observed with years_since_last_scan = 0;
// every other planet is Unobserved.
//
// As scanner mechanics land, the only place that needs updating is the
// `is_observable` predicate inside `player_view()`.

use crate::game::objects::advantage_points::{
    axis_to_idx, grav_to_idx, planet_habitability, rad_to_idx, temp_to_idx,
};
use crate::game::objects::planet::{PlanetState, PlanetStatic};
use crate::game::objects::race::{Lrt, Prt, Race};
use crate::game::state::GameState;

// The turn-file wire types (`PlayerView`, `PlanetIntel`, `PlanetObserved`,
// `PlanetUnobserved`) are GENERATED from `schemas/response-turn-file.json` at
// build time (see `build.rs`) and re-exported here so existing
// `game::view::*` paths keep resolving. To change the turn-file shape — field
// names, ranges, which fields are observed-only — edit the schema, not this
// file. `PlanetIntel` is untagged: a client tells observed from unobserved by
// whether the contents fields are present. See `docs/adr/0003`.
use crate::game::objects::fleet::{Fleet, FleetWaypointTask};
pub use crate::game::objects::generated::turn_file::{
    BuildItem, Fleet as WireFleet, FleetCargo as WireFleetCargo,
    FleetWaypoint as WireFleetWaypoint, FleetWaypointTask as WireFleetWaypointTask, PlanetIntel,
    PlanetObserved, PlanetUnobserved, PlayerView, ScannedFleet, ShipStack as WireShipStack,
    StarbaseStatus, TurnMessage, TurnScore,
};
use crate::game::objects::generated::turn_file::{
    ShipDesign as WireShipDesign, ShipDesignKind as WireShipDesignKind,
    SlotAssignment as WireSlotAssignment,
};
use crate::game::objects::player::{Player, ShipDesignKind, TechLevels};
use crate::game::objects::starbase_hull_catalog::starbase_hull_catalog;
use crate::game::objects::technology::TechRequirements;
use crate::game::objects::technology_catalog::{technology_catalog, PlanetaryKind, Props};
use crate::game::orders::design_built_count;

use crate::game::score;

/// Project a `PlayerView` for `player_id` from the host-side `GameState`.
///
/// This is the single choke point that derives per-player turn files. Any
/// host-only field that escapes through this function is a leak; the
/// integration test in `tests/player_view_leak.rs` is the safety net.
pub fn player_view(state: &GameState, player_id: u32) -> PlayerView {
    let player = state.players.iter().find(|p| p.id == player_id);
    let race = player.and_then(|p| p.race.as_ref());

    let mut planet_ids: Vec<u32> = state.universe.planets.keys().copied().collect();
    planet_ids.sort();

    let planets: Vec<PlanetIntel> = planet_ids
        .into_iter()
        .filter_map(|id| {
            let static_ = state.universe.planets.get(&id)?;
            let pstate = state.planet_states.get(&id);
            Some(intel_for(static_, pstate, player_id, player, race))
        })
        .collect();

    PlayerView {
        year: state.year,
        game_id: state.id.clone(),
        game_name: state.name.clone(),
        player_id,
        homeworld_id: player.and_then(|p| p.homeworld_id),
        planets,
        // The viewing player's OWN fleets, in full, sorted by id. Fog-of-war
        // mirrors the planet observed/unobserved split: a player sees its own
        // fleets completely; other players' fleets appear only within scanner
        // coverage, as partial `scanned_fleets`. See `fleet_view`.
        fleets: own_fleets(state, player_id),
        // Other players' fleets this player has scanned. The engine does not
        // model fleet scanning yet, so there is no foreign-fleet intel to
        // project; emit an empty list. The wire shape is defined
        // (schemas/response-turn-file.json scanned-fleet) so the client's map
        // overlays have a stable field to read. This is the growth point that
        // mirrors a planet becoming Observed. See docs/mechanics/scanning.rst.
        scanned_fleets: vec![],
        // The viewing player's own ship/starbase designs, edited via
        // design.upsert / design.delete orders. A ship design's built-count is
        // the number of ships of it across the player's fleets (0 for a design
        // with no ships, so its slot stays editable). See
        // docs/mechanics/ship_design.rst and `orders::design_built_count`.
        ship_designs: player
            .map(|p| {
                p.designs
                    .iter()
                    .map(|d| WireShipDesign {
                        slot: d.slot,
                        kind: match d.kind {
                            ShipDesignKind::Ship => WireShipDesignKind::Ship,
                            ShipDesignKind::Starbase => WireShipDesignKind::Starbase,
                        },
                        name: d.name.clone(),
                        hull_id: d.hull_id,
                        slot_assignments: d
                            .slot_assignments
                            .iter()
                            .map(|s| WireSlotAssignment {
                                slot_index: s.slot_index,
                                part_id: s.part_id,
                                count: s.count,
                            })
                            .collect(),
                        built_count: design_built_count(state, player_id, d.kind, d.slot),
                    })
                    .collect()
            })
            .unwrap_or_default(),
        // Other players' designs the viewer has scanned. The engine models
        // neither fleets nor scanning yet, so there is no enemy-design
        // intel to project; emit an empty list. The wire shape is defined
        // (schemas/response-turn-file.json scanned-design) so the client's
        // Enemy Hulls view has a stable field to read. See
        // docs/mechanics/scanning.rst 'Enemy Design Intel'.
        scanned_designs: vec![],
        messages: turn_messages(state, player_id),
        score: compute_score(state, player_id),
        // The viewing player's own race (None for a phantom/unknown player id).
        race: race.cloned(),
    }
}

/// Compute the viewing player's F10 score breakdown for the turn file.
///
/// Uses the confirmed formula in `game::score` (docs/mechanics/victory.rst).
/// Own score only — opponents' scores and ranks are gated on the
/// public-player-scores game flag, which `GameState` does not model yet. The
/// categories the engine can measure today are planets (owned populations),
/// tech (the player's six tech levels), and resources (the sum of each owned
/// planet's resources/year). Starbase and ship categories read 0 until
/// starbase score-counting and ship combat-power classification land, so
/// `total` grows automatically as they do.
fn compute_score(state: &GameState, player_id: u32) -> TurnScore {
    let player = state.players.iter().find(|p| p.id == player_id);

    let populations: Vec<u32> = state
        .planet_states
        .values()
        .filter(|s| s.owner == Some(player_id))
        .map(|s| s.population)
        .collect();
    let planet_count = populations.len() as u32;
    let planet_points: u32 = populations.iter().copied().map(score::planet_points).sum();

    // Annual resources: the sum of each owned planet's resources/year. A planet
    // the engine cannot compute resources for (an AR race) contributes 0.
    let race = player.and_then(|p| p.race.as_ref());
    let resource_amount: u32 = state
        .planet_states
        .values()
        .filter(|s| s.owner == Some(player_id))
        .filter_map(|s| compute_resources_per_year(s, race))
        .sum();
    let resource_points = score::resource_points(resource_amount);

    let tech = player.map(|p| &p.tech);
    let tech_levels = tech.map_or([0; 6], |t| {
        [
            t.energy,
            t.weapons,
            t.propulsion,
            t.construction,
            t.electronics,
            t.biotechnology,
        ]
    });
    let tech_level_sum: u32 = tech_levels.iter().sum();
    let tech_points: u32 = tech_levels
        .iter()
        .copied()
        .map(score::tech_field_points)
        .sum();

    // Not counted yet: starbase score-counting, and ship combat-power
    // classification (unarmed/escort/capital). The fleet model exists, but a
    // ship's power rating is a combat-model concern. Counts and points are 0.
    let (starbase_count, unarmed_count, escort_count, capital_count) = (0, 0, 0, 0);
    let starbase_points = score::starbase_points(starbase_count);
    let unarmed_points = score::unarmed_points(unarmed_count, planet_count);
    let escort_points = score::escort_points(escort_count, planet_count);
    let capital_points = score::capital_points(capital_count, planet_count);

    TurnScore {
        total: planet_points
            + starbase_points
            + unarmed_points
            + escort_points
            + capital_points
            + tech_points
            + resource_points,
        planet_count,
        planet_points,
        starbase_count,
        starbase_points,
        unarmed_count,
        unarmed_points,
        escort_count,
        escort_points,
        capital_count,
        capital_points,
        tech_level_sum,
        tech_points,
        resource_amount,
        resource_points,
    }
}

/// Build this player's messages for the current turn.
///
/// Messages are per-turn — recomputed on every turn file, never accumulated.
/// They come from two places, merged here in this order:
///
///   1. Resolution-time events, read from the host-side per-player store on
///      `GameState` that each turn-resolution step appends to (see
///      `turn::push_message` / `turn::resolve_turn`). The bulk of the message
///      catalogue (combat, bombing, colonisation, growth, mining, research,
///      minefields, packets, random events) lands here as its mechanic is
///      built; today no built step emits one.
///   2. View-time messages, derived fresh from the current state on every
///      projection — the production-queue-empty nudge is the only one so far.
///
/// `id` is assigned last as the 0-based position in the merged list, so it is
/// contiguous across both sources and stable within this turn file.
fn turn_messages(state: &GameState, player_id: u32) -> Vec<TurnMessage> {
    let mut messages: Vec<TurnMessage> = Vec::new();

    // (1) Resolution-time events recorded for this player during the last
    //     turn resolution. `id` is overwritten below.
    if let Some(stored) = state.player_messages.get(&player_id) {
        for m in stored {
            messages.push(TurnMessage {
                id: 0,
                message: m.message.clone(),
                message_type: m.message_type.clone(),
                related_object: m.related_object,
                related_battle: m.related_battle,
                important: m.important,
            });
        }
    }

    // (2) Production-queue-empty: for each world this player owns whose build
    //     queue is empty, nudge the player to queue production (message 063 in
    //     the original catalogue, "The production queue on <planet> is
    //     empty."). A freshly founded homeworld starts with an empty queue, so
    //     this is the first message a new game shows.
    let mut owned: Vec<(&u32, &PlanetState)> = state
        .planet_states
        .iter()
        .filter(|(_, s)| s.owner == Some(player_id) && s.build_queue.is_empty())
        .collect();
    owned.sort_by_key(|(id, _)| **id);

    for (id, _) in owned {
        let name = state
            .universe
            .planets
            .get(id)
            .map(|p| p.name.as_str())
            .unwrap_or("this planet");
        messages.push(TurnMessage {
            id: 0,
            message: format!("The production queue on {name} is empty."),
            message_type: "PlanetProductionQueueEmpty".to_string(),
            related_object: Some(*id),
            related_battle: None,
            important: true,
        });
    }

    // Contiguous 0-based ids across both sources, in final order.
    for (i, m) in messages.iter_mut().enumerate() {
        m.id = i as u16;
    }

    messages
}

/// Compute planet value (0..100 habitable, negative red) for a planet against
/// the given race. Returns 0 when the race is unknown — the safer default for
/// pre-existing saves missing the optional Race field on Player.
fn compute_value(s: &PlanetState, race: Option<&Race>) -> i32 {
    let Some(race) = race else {
        return 0;
    };
    let is_immune = [
        race.hab.gravity.immune,
        race.hab.temperature.immune,
        race.hab.radiation.immune,
    ];
    let (glo, ghi) = axis_to_idx(&race.hab.gravity, 0);
    let (tlo, thi) = axis_to_idx(&race.hab.temperature, 1);
    let (rlo, rhi) = axis_to_idx(&race.hab.radiation, 2);
    let hab_low = [glo, tlo, rlo];
    let hab_high = [ghi, thi, rhi];
    let hab_center = [(glo + ghi) / 2, (tlo + thi) / 2, (rlo + rhi) / 2];
    let planet_hab = [
        grav_to_idx(s.gravity as f64),
        temp_to_idx(s.temperature as f64),
        rad_to_idx(s.radiation as f64),
    ];
    planet_habitability(&is_immune, &hab_low, &hab_high, &hab_center, &planet_hab) as i32
}

/// Resources this planet generates per year, or `None` when the engine cannot
/// compute it for the owning race.
///
/// `floor(population / resource_production) + operated_factories *
/// factory_production`, where operated factories are capped at the planet's
/// factory capacity `population * colonists_operate_factories / 10000` — a
/// freshly founded homeworld sits well under that cap (see
/// docs/mechanics/production.rst). A derived value recomputed every turn, not
/// stored on the planet.
///
/// Returns `None` for an Alternate Reality race (its resources come from a
/// different, not-yet-modelled economy, so emitting the standard formula would
/// be wrong) and when the race is unknown.
fn compute_resources_per_year(s: &PlanetState, race: Option<&Race>) -> Option<u32> {
    let race = race?;
    if race.prt == Prt::Ar {
        return None;
    }
    let colonist = s.population / race.economy.resource_production.max(1);
    let capacity = s
        .population
        .saturating_mul(race.economy.colonists_operate_factories)
        / 10_000;
    let operated = s.factories.min(capacity);
    Some(colonist + operated * race.economy.factory_production)
}

/// Project the host-side production queue into the turn-file `BuildItem`
/// wire shape. Emitted only for owned planets (production is private); the
/// `estimated-years-to-complete` projection is deferred until the cost/output
/// model lands, so it is left absent here.
fn build_queue_view(s: &PlanetState) -> Vec<BuildItem> {
    s.build_queue
        .iter()
        .map(|bi| BuildItem {
            build_object_id: bi.build_object_id,
            build_quantity: bi.build_quantity,
            build_progress: Some(bi.build_progress),
            estimated_years_to_complete: None,
        })
        .collect()
}

/// Aggregate a planet's starbase design into the display stats the client's
/// Starbase section consumes, or `None` if the planet has no starbase. Only an
/// owned planet reaches here, so the design is the owning player's own.
///
/// Derived from the starbase hull (dock capacity, base armor) plus the
/// installed components (armor and shield damage-points, mass-driver warp).
/// Battle damage and packet targeting are not modelled yet, so `damage-percent`
/// is 0 and `packet-target` is null. A hull-only starting starbase therefore
/// reports just the hull's armor and unlimited/finite dock capacity, with zero
/// shields and no mass driver, until its component loadout is filled in.
fn starbase_status(player: Option<&Player>, s: &PlanetState) -> Option<StarbaseStatus> {
    let slot = s.starbase_design_slot?;
    let player = player?;
    let design = player
        .designs
        .iter()
        .find(|d| d.kind == ShipDesignKind::Starbase && d.slot == slot)?;
    let hull = starbase_hull_catalog()
        .into_iter()
        .find(|h| u32::from(h.id) == design.hull_id)?;

    let catalog = technology_catalog();
    let mut armor = hull.armor;
    let mut shields: u32 = 0;
    let mut mass_driver: Option<u32> = None;
    for sa in &design.slot_assignments {
        let Some(item) = catalog.iter().find(|t| u32::from(t.id) == sa.part_id) else {
            continue;
        };
        let count = sa.count.get();
        match &item.props {
            Props::Armor {
                armor_value,
                shield_value,
                ..
            } => {
                armor += armor_value * count;
                shields += shield_value * count;
            }
            Props::Shield {
                shield_value,
                armor_value,
                ..
            } => {
                shields += shield_value * count;
                armor += armor_value * count;
            }
            // The displayed rating is the driver tier's rated warp. A starbase
            // may hold at most two IDENTICAL drivers, so the max across
            // installed drivers is that shared rating — correct for display.
            // (Dual drivers' benefits — catch +1 warp, gentler overfling decay
            // — and the player-selected launch warp are packet-flight
            // behaviors, not this rating; see the mass-driver/packet finding.)
            Props::MassDriver { warp } => {
                let w = u32::from(*warp);
                mass_driver = Some(mass_driver.map_or(w, |cur| cur.max(w)));
            }
            _ => {}
        }
    }

    Some(StarbaseStatus {
        dock_capacity: hull.dock_capacity,
        armor,
        shields,
        damage_percent: 0,
        mass_driver,
        packet_target: s.packet_target,
    })
}

/// True when researched tech levels meet a planetary tech's requirement in
/// every field. (Mirrors `orders::tech_requirements_met`, kept local so the
/// view does not depend on an orders-module private.)
fn tech_met(req: &TechRequirements, tech: &TechLevels) -> bool {
    u32::from(req.energy) <= tech.energy
        && u32::from(req.weapons) <= tech.weapons
        && u32::from(req.propulsion) <= tech.propulsion
        && u32::from(req.construction) <= tech.construction
        && u32::from(req.electronics) <= tech.electronics
        && u32::from(req.bio) <= tech.biotechnology
}

/// Whether a race may field a planetary scanner (docs/reference/planetary_tech.rst
/// "Access"): Alternate Reality has no planetary scanners at all, and the
/// penetrating Snooper series is removed for No-Advanced-Scanners races.
fn scanner_available(race: &Race, penetrating: bool) -> bool {
    if race.prt == Prt::Ar {
        return false;
    }
    !(penetrating && race.lrts.contains(&Lrt::Nas))
}

/// Whether a race may field a planetary defense (docs/reference/planetary_tech.rst
/// "Access"): SDI and Missile Battery are universal; Laser Battery and the two
/// shields are excluded for War Monger and Alternate Reality.
fn defense_available(race: &Race, slug: &str) -> bool {
    let restricted = matches!(
        slug,
        "laser_battery" | "planetary_shield" | "neutron_shield"
    );
    !(restricted && matches!(race.prt, Prt::Wm | Prt::Ar))
}

/// The owner's effective planetary scanner: the highest normal-range scanner it
/// has both researched and may access. Planetary scanners are empire-wide and
/// automatic (not built per planet), so this depends only on race + tech. Does
/// NOT yet union with an orbiting starbase's scanner (future work). Returns
/// `(display name, normal range ly)`, or `None` (e.g. an AR race).
fn best_planetary_scanner(race: &Race, tech: &TechLevels) -> Option<(&'static str, u32)> {
    technology_catalog()
        .into_iter()
        .filter_map(|item| match &item.props {
            Props::Planetary(PlanetaryKind::Scanner {
                basic_range,
                penetrating_range,
            }) if scanner_available(race, *penetrating_range > 0)
                && tech_met(&item.tech_requirements, tech) =>
            {
                Some((item.name, *basic_range))
            }
            _ => None,
        })
        .max_by_key(|(_, range)| *range)
}

/// The owner's best planetary defense TYPE: the highest-coverage defense it has
/// both researched and may access. All of a planet's defenses are this type.
/// Returns `(display name, per-defense base coverage)`, or `None`.
fn best_planetary_defense(race: &Race, tech: &TechLevels) -> Option<(&'static str, f64)> {
    technology_catalog()
        .into_iter()
        .filter_map(|item| match &item.props {
            Props::Planetary(PlanetaryKind::Defense { base_coverage })
                if defense_available(race, item.slug)
                    && tech_met(&item.tech_requirements, tech) =>
            {
                Some((item.name, *base_coverage))
            }
            _ => None,
        })
        .max_by(|a, b| a.1.total_cmp(&b.1))
}

/// Overall colonist protection from `count` defenses, each with per-defense kill
/// probability `base_coverage`, as an integer percent (0..=100). Compounding
/// form from docs/reference/planetary_tech.rst: `1 − (1 − base_coverage)^count`.
/// Exact value pending oracle verification.
fn defense_coverage_percent(base_coverage: f64, count: u32) -> u32 {
    let protection = 1.0 - (1.0 - base_coverage).powi(count as i32);
    (protection * 100.0).round() as u32
}

/// The viewing player's own fleets, projected to the full turn-file wire
/// shape and sorted by id.
///
/// Own fleets are always fully visible to their owner — the fleet analogue of
/// an owned planet being Observed with current ground truth. A fleet owned by
/// another player is never emitted here; it reaches the player (partially) only
/// through `scanned_fleets` once fleet scanning is modelled.
fn own_fleets(state: &GameState, player_id: u32) -> Vec<WireFleet> {
    let mut fleets: Vec<&Fleet> = state
        .fleets
        .values()
        .filter(|f| f.owner == player_id)
        .collect();
    fleets.sort_by_key(|f| f.id);
    fleets.into_iter().map(fleet_view).collect()
}

/// Project one host-side `Fleet` into the turn-file wire `Fleet`. Used only for
/// a fleet the viewing player owns, so every field is exposed.
fn fleet_view(f: &Fleet) -> WireFleet {
    WireFleet {
        id: f.id,
        name: f.name.clone(),
        owner: f.owner,
        x: f.x,
        y: f.y,
        orbiting_planet_id: f.orbiting_planet_id,
        ship_stacks: f
            .ship_stacks
            .iter()
            .map(|s| WireShipStack {
                design_slot: s.design_slot,
                count: s.count,
            })
            .collect(),
        fuel: f.fuel,
        cargo: WireFleetCargo {
            ironium: f.cargo.ironium,
            boranium: f.cargo.boranium,
            germanium: f.cargo.germanium,
            colonists: f.cargo.colonists,
        },
        waypoints: f
            .waypoints
            .iter()
            .map(|w| WireFleetWaypoint {
                x: w.x,
                y: w.y,
                target_planet_id: w.target_planet_id,
                warp: w.warp,
                task: waypoint_task_view(&w.task),
            })
            .collect(),
        repeat_orders: f.repeat_orders,
    }
}

/// Map the host waypoint-task enum to the identical turn-file enum.
fn waypoint_task_view(task: &FleetWaypointTask) -> WireFleetWaypointTask {
    match task {
        FleetWaypointTask::None => WireFleetWaypointTask::None,
        FleetWaypointTask::Colonize => WireFleetWaypointTask::Colonize,
        FleetWaypointTask::RemoteMine => WireFleetWaypointTask::RemoteMine,
        FleetWaypointTask::UnloadCargo => WireFleetWaypointTask::UnloadCargo,
        FleetWaypointTask::LoadCargo => WireFleetWaypointTask::LoadCargo,
        FleetWaypointTask::LoadFuel => WireFleetWaypointTask::LoadFuel,
        FleetWaypointTask::Patrol => WireFleetWaypointTask::Patrol,
        FleetWaypointTask::TransferFleet => WireFleetWaypointTask::TransferFleet,
        FleetWaypointTask::MergeFleet => WireFleetWaypointTask::MergeFleet,
        FleetWaypointTask::ScrapFleet => WireFleetWaypointTask::ScrapFleet,
        FleetWaypointTask::LayMines => WireFleetWaypointTask::LayMines,
    }
}

/// Decide whether `player_id` can currently observe this planet, and emit
/// the matching `PlanetIntel` variant.
///
/// Today's rule: observable iff the player owns the planet. When scanner
/// mechanics land, this is the function that grows: union of fleet/planet
/// scanner coverage, with stale snapshots persisted across turns from a
/// future `PlayerIntel` store on `GameState`.
fn intel_for(
    static_: &PlanetStatic,
    pstate: Option<&PlanetState>,
    player_id: u32,
    player: Option<&Player>,
    race: Option<&Race>,
) -> PlanetIntel {
    let observable = matches!(pstate, Some(s) if s.owner == Some(player_id));

    match (observable, pstate) {
        (true, Some(s)) => {
            // Scanner/defense derive from the OWNER's race + tech. This planet
            // is observable iff the viewing player owns it, so `player`/`race`
            // are the owner's.
            let tech = player.map(|p| &p.tech);
            let (scanner_type, scanner_range) = match (race, tech) {
                (Some(r), Some(t)) => match best_planetary_scanner(r, t) {
                    Some((name, range)) => (Some(name.to_string()), Some(range)),
                    None => (None, None),
                },
                _ => (None, None),
            };
            let (defense_type, defense_coverage) = match (race, tech) {
                (Some(r), Some(t)) => match best_planetary_defense(r, t) {
                    Some((name, base)) => (
                        Some(name.to_string()),
                        Some(defense_coverage_percent(base, s.defenses)),
                    ),
                    None => (None, None),
                },
                _ => (None, None),
            };
            PlanetIntel::Observed(PlanetObserved {
                id: static_.id,
                name: static_.name.clone(),
                x: static_.x,
                y: static_.y,
                years_since_last_scan: 0,
                gravity: s.gravity,
                temperature: s.temperature,
                radiation: s.radiation,
                ironium_concentration: s.ironium_concentration,
                boranium_concentration: s.boranium_concentration,
                germanium_concentration: s.germanium_concentration,
                surface_ironium: s.surface_ironium,
                surface_boranium: s.surface_boranium,
                surface_germanium: s.surface_germanium,
                homeworld: s.homeworld,
                owner: s.owner,
                population: s.population,
                factories: s.factories,
                mines: s.mines,
                defenses: Some(s.defenses),
                value: compute_value(s, race),
                resources_per_year: compute_resources_per_year(s, race),
                scanner_type,
                scanner_range,
                defense_type,
                defense_coverage,
                build_queue: build_queue_view(s),
                route_target: s.route_target,
                starbase: starbase_status(player, s),
            })
        }
        _ => PlanetIntel::Unobserved(PlanetUnobserved {
            id: static_.id,
            name: static_.name.clone(),
            x: static_.x,
            y: static_.y,
        }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::objects::race_defaults::humanoid;

    fn tech(level: u32) -> TechLevels {
        TechLevels {
            energy: level,
            weapons: level,
            propulsion: level,
            construction: level,
            electronics: level,
            biotechnology: level,
        }
    }

    /// A JOAT (no LRTs) race with the given PRT/LRT overrides.
    fn race_with(prt: Prt, lrts: Vec<Lrt>) -> Race {
        let mut r = humanoid();
        r.prt = prt;
        r.lrts = lrts;
        r
    }

    #[test]
    fn scanner_at_zero_tech_is_the_basic_viewer() {
        let r = race_with(Prt::Joat, vec![]);
        assert_eq!(
            best_planetary_scanner(&r, &tech(0)),
            Some(("Viewer 50", 50))
        );
    }

    #[test]
    fn scanner_picks_the_best_researched_and_accessible() {
        let r = race_with(Prt::Joat, vec![]);
        // All fields high enough for the top Snooper (En7/El23/Bio9).
        assert_eq!(
            best_planetary_scanner(&r, &tech(30)),
            Some(("Snooper 620X", 620))
        );
    }

    #[test]
    fn nas_cannot_use_penetrating_snoopers() {
        let r = race_with(Prt::Joat, vec![Lrt::Nas]);
        // Snoopers (penetrating) are excluded; best normal scanner is Scoper 280.
        assert_eq!(
            best_planetary_scanner(&r, &tech(30)),
            Some(("Scoper 280", 280))
        );
    }

    #[test]
    fn ar_has_no_planetary_scanner() {
        let r = race_with(Prt::Ar, vec![]);
        assert_eq!(best_planetary_scanner(&r, &tech(30)), None);
    }

    #[test]
    fn defense_at_zero_tech_is_sdi() {
        let r = race_with(Prt::Joat, vec![]);
        assert_eq!(best_planetary_defense(&r, &tech(0)), Some(("SDI", 0.0099)));
    }

    #[test]
    fn defense_picks_the_best_researched_and_accessible() {
        let r = race_with(Prt::Joat, vec![]);
        assert_eq!(
            best_planetary_defense(&r, &tech(30)),
            Some(("Neutron Shield", 0.0379))
        );
    }

    #[test]
    fn war_monger_and_ar_are_capped_at_missile_battery() {
        // Laser Battery and the shields are excluded for WM and AR, so even at
        // high tech the best defense is the Missile Battery (En 5).
        for prt in [Prt::Wm, Prt::Ar] {
            let r = race_with(prt, vec![]);
            assert_eq!(
                best_planetary_defense(&r, &tech(30)),
                Some(("Missile Battery", 0.0199))
            );
        }
    }

    #[test]
    fn coverage_compounds_over_the_defense_count() {
        // No defenses => no protection.
        assert_eq!(defense_coverage_percent(0.0099, 0), 0);
        // 100 x SDI (0.0099): 1 - 0.9901^100 ~= 63.3% -> 63.
        assert_eq!(defense_coverage_percent(0.0099, 100), 63);
    }
}
