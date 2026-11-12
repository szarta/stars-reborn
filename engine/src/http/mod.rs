// engine/src/http/mod.rs
//
// Axum router and request handlers.
//
// This layer is intentionally thin: parse the request, call into game/,
// serialize the response. No game logic lives here.
//
// API surfaces (see stars-reborn-design/docs/architecture.rst):
//
//   GET /model/version                              — engine version + API schema version
//   GET /model/technologies                         — full technology tree
//   GET /model/technologies/{id}                    — single technology item
//   GET /model/race/traits                          — PRT/LRT definitions and point costs
//   GET /model/ships/hulls                          — all ship hull definitions
//   GET /model/starbase/hulls                       — all starbase hull definitions
//   GET /model/buildables                           — production-queue buildable registry
//   GET /model/schemas                              — JSON schemas for all request/response types
//
//   POST   /games                                   — create new game
//   GET    /games/{game_id}                         — game metadata
//   DELETE /games/{game_id}                         — remove game (memory + disk)
//   GET  /games/{game_id}/turns/{year}/status       — per-player submission status
//   GET  /games/{game_id}/turns/{year}/players/{pid}— turn file for player
//   PUT  /games/{game_id}/turns/{year}/orders/{pid} — submit player orders (idempotent)
//   POST /games/{game_id}/turns/{year}/skip/{pid}   — generate AI orders, mark skipped
//   GET  /games/{game_id}/turns/{year}/ai-orders/{pid} — AI-suggested orders (not submitted)

use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post, put},
    Json, Router,
};
use serde::Deserialize;
use serde_json::{json, Value};

use crate::game::objects::buildable::{
    design_build_object_id, Category, DESIGN_SLOTS, FIXED_BUILDABLES,
};
use crate::game::objects::generated::buildables as bld_wire;
use crate::game::objects::generated::ship_hulls as wire;
use crate::game::objects::generated::starbase_hulls as sb_wire;
use crate::game::objects::{
    advantage_points::advantage_points,
    planet::PlanetState,
    player::{Player, ShipDesign, ShipDesignKind},
    race::Race,
    race_defaults::default_race_by_name,
    ship_hull_catalog::{
        hull_category_slug, hull_requirement_slug, ship_hull_catalog, slot_type_slug,
    },
    starbase_hull_catalog::{starbase_hull_catalog, HOMEWORLD_STARBASE_HULL_ID},
    starting_tech::starting_tech_levels,
    technology::{ShipHull, StarbaseHull, TechSlot},
    technology_catalog::{technology_catalog, PlanetaryKind, Props, TechItem, TraitReq},
};
use crate::game::orders::{
    apply_design_delete, apply_design_upsert, apply_set_packet_target, apply_set_production_queue,
    apply_set_route_target, OrderError, ProductionItemInput,
};
use crate::game::state::GameState;
use crate::game::universe::generate_universe;
use crate::game::universe::scenario::{load_tutorial, scenario_universe};
use crate::game::view::player_view;

// ---------------------------------------------------------------------------
// Shared application state
// ---------------------------------------------------------------------------

#[derive(Clone)]
pub struct AppState {
    /// All active games, keyed by UUID string.
    games: Arc<RwLock<HashMap<String, GameState>>>,
}

impl Default for AppState {
    fn default() -> Self {
        Self::new()
    }
}

impl AppState {
    pub fn new() -> Self {
        let loaded = crate::store::load_all_games();
        let map: HashMap<String, GameState> =
            loaded.into_iter().map(|g| (g.id.clone(), g)).collect();
        log::info!("{} game(s) loaded from disk", map.len());
        Self {
            games: Arc::new(RwLock::new(map)),
        }
    }
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

/// Build and return the axum Router with all routes registered.
pub fn router(state: AppState) -> Router {
    Router::new()
        // Data model endpoints (read-only, static)
        .route("/model/version", get(model_version))
        .route("/model/technologies", get(model_technologies))
        .route("/model/technologies/:id", get(model_technology_by_id))
        .route("/model/race/traits", get(model_race_traits))
        .route("/model/ships/hulls", get(model_ship_hulls))
        .route("/model/starbase/hulls", get(model_starbase_hulls))
        .route("/model/buildables", get(model_buildables))
        .route("/model/schemas", get(model_schemas))
        // Race design utilities
        .route("/race/validate", post(race_validate))
        // Game endpoints (stateful)
        .route("/games", post(create_game))
        .route("/games/tutorial", post(create_tutorial_game))
        .route("/games/:game_id", get(get_game).delete(delete_game))
        .route("/games/:game_id/turns/:year/status", get(turn_status))
        .route(
            "/games/:game_id/turns/:year/players/:pid",
            get(get_turn_file),
        )
        .route(
            "/games/:game_id/turns/:year/orders/:pid",
            put(submit_orders),
        )
        .route("/games/:game_id/turns/:year/skip/:pid", post(skip_player))
        .route(
            "/games/:game_id/turns/:year/ai-orders/:pid",
            get(get_ai_orders),
        )
        .route("/games/:game_id/turns/:year/advance", post(advance_turn))
        .with_state(state)
}

// ---------------------------------------------------------------------------
// Data model handlers
// ---------------------------------------------------------------------------

async fn model_version() -> Json<Value> {
    Json(json!({
        "engine_version": crate::VERSION,
        "api_version": 1,
    }))
}

/// GET /model/technologies — the component technology catalog.
///
/// Response shape: schemas/response-model-technologies.json. The catalog is a
/// growing slice (task #144): engines, armor, shields, and orbital components
/// today; other categories land as follow-ups. Built with `json!` (no typed
/// producer yet, like `/model/buildables`); the `technologies_schema_contract`
/// test validates the output against the schema.
async fn model_technologies() -> impl IntoResponse {
    Json(technologies_response())
}

/// GET /model/technologies/{id} — a single component by numeric id or slug.
async fn model_technology_by_id(Path(id): Path<String>) -> impl IntoResponse {
    let found = technology_catalog()
        .into_iter()
        .find(|t| t.slug == id || id.parse::<u16>().map(|n| n == t.id).unwrap_or(false));
    match found {
        Some(item) => (StatusCode::OK, Json(tech_item_to_json(&item))).into_response(),
        None => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": format!("no technology with id or slug '{id}'")})),
        )
            .into_response(),
    }
}

/// Build the `GET /model/technologies` response body.
pub fn technologies_response() -> Value {
    let technologies: Vec<Value> = technology_catalog().iter().map(tech_item_to_json).collect();
    json!({ "technologies": technologies })
}

/// Map one catalog `TechItem` to its wire `tech-item` JSON. `mass` is emitted
/// only for installable parts; `requirement` is null or a trait gate; and
/// `properties` carries the category-specific `props-*` shape.
fn tech_item_to_json(t: &TechItem) -> Value {
    let mut obj = json!({
        "id": t.id,
        "slug": t.slug,
        "name": t.name,
        "category": t.props.category(),
        "requirement": trait_req_to_json(t.requirement),
        "cost": {
            "ironium": t.cost.ironium,
            "boranium": t.cost.boranium,
            "germanium": t.cost.germanium,
            "resources": t.cost.resources,
        },
        "tech-requirements": {
            "energy": t.tech_requirements.energy,
            "weapons": t.tech_requirements.weapons,
            "propulsion": t.tech_requirements.propulsion,
            "construction": t.tech_requirements.construction,
            "electronics": t.tech_requirements.electronics,
            "biotechnology": t.tech_requirements.bio,
        },
        "properties": props_to_json(&t.props),
    });
    if let Some(mass) = t.mass {
        obj["mass"] = json!(mass);
    }
    obj
}

/// Trait gate → wire `trait-requirement` (null, `{ "prt": [slug] }`, or
/// `{ "lrt": [slug] }`).
fn trait_req_to_json(req: Option<TraitReq>) -> Value {
    match req {
        None => Value::Null,
        Some(TraitReq::Prt(prt)) => json!({ "prt": [prt] }),
        Some(TraitReq::Lrt(lrt)) => json!({ "lrt": [lrt] }),
    }
}

/// Category stats → the matching wire `props-*` object.
fn props_to_json(props: &Props) -> Value {
    match props {
        Props::Engine {
            fuel_usage,
            battle_speed,
            warp10_travel,
            last_free_warp,
            cloaking,
            battle_speed_modifier,
        } => {
            let mut p = json!({
                "fuel-usage": fuel_usage.to_vec(),
                "battle-speed": battle_speed,
                "warp10-travel": warp10_travel,
                "last-free-warp": last_free_warp,
            });
            if *cloaking != 0 {
                p["cloaking"] = json!(cloaking);
            }
            if *battle_speed_modifier != 0.0 {
                p["battle-speed-modifier"] = json!(battle_speed_modifier);
            }
            p
        }
        Props::Armor {
            armor_value,
            shield_value,
            cloaking,
        } => {
            let mut p = json!({ "armor-value": armor_value });
            if *shield_value != 0 {
                p["shield-value"] = json!(shield_value);
            }
            if *cloaking != 0 {
                p["cloaking"] = json!(cloaking);
            }
            p
        }
        Props::Shield {
            shield_value,
            armor_value,
            cloaking,
            jamming,
            scanner_basic_range,
            scanner_penetrating_range,
        } => {
            let mut p = json!({ "shield-value": shield_value });
            if *armor_value != 0 {
                p["armor-value"] = json!(armor_value);
            }
            if *cloaking != 0 {
                p["cloaking"] = json!(cloaking);
            }
            if *jamming != 0 {
                p["jamming"] = json!(jamming);
            }
            if *scanner_basic_range != 0 {
                p["scanner-basic-range"] = json!(scanner_basic_range);
            }
            if *scanner_penetrating_range != 0 {
                p["scanner-penetrating-range"] = json!(scanner_penetrating_range);
            }
            p
        }
        Props::Stargate {
            safe_mass,
            safe_range,
        } => json!({
            "kind": "stargate",
            "safe-mass": safe_mass,
            "safe-range": safe_range,
        }),
        Props::MassDriver { warp } => json!({
            "kind": "mass-driver",
            "warp": warp,
        }),
        Props::Planetary(kind) => match kind {
            PlanetaryKind::Scanner {
                basic_range,
                penetrating_range,
            } => json!({
                "kind": "scanner",
                "basic-range": basic_range,
                "penetrating-range": penetrating_range,
            }),
            PlanetaryKind::Defense { base_coverage } => json!({
                "kind": "defense",
                "base-coverage": base_coverage,
            }),
            PlanetaryKind::Terraforming {
                gravity,
                temperature,
                radiation,
            } => json!({
                "kind": "terraforming",
                "gravity": gravity,
                "temperature": temperature,
                "radiation": radiation,
            }),
        },
    }
}

async fn model_race_traits() -> impl IntoResponse {
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(json!({"error": "not yet implemented"})),
    )
}

/// GET /model/ships/hulls — full ship-hull catalog.
///
/// Response shape: stars-reborn-schemas/response-model-ship-hulls.json.
async fn model_ship_hulls() -> impl IntoResponse {
    Json(ship_hulls_response())
}

/// Build the `GET /model/ships/hulls` response. The shape is GENERATED from the
/// single source of truth `schemas/response-model-ship-hulls.json` (see
/// `build.rs`); this maps the internal catalog into that wire type, and the
/// `ship_hulls_schema_contract` test validates the serialized output against the
/// schema. The slug helpers bridge the internal domain enums to the generated
/// wire enums through their canonical slug (the generated enums' `TryFrom<&str>`
/// accepts exactly those slugs), keeping the domain→wire mapping defined once.
pub fn ship_hulls_response() -> wire::ShipHullsResponse {
    wire::ShipHullsResponse {
        hulls: ship_hull_catalog().into_iter().map(hull_to_wire).collect(),
    }
}

/// Map one internal `ShipHull` to its generated wire shape.
fn hull_to_wire(h: ShipHull) -> wire::ShipHull {
    wire::ShipHull {
        id: h.id.into(),
        slug: h.slug.to_string(),
        name: h.name.to_string(),
        category: wire::HullCategory::try_from(hull_category_slug(h.category))
            .expect("catalog hull category is a canonical slug"),
        requirement: h.requirement.map(|r| {
            wire::HullRequirement::try_from(hull_requirement_slug(r))
                .expect("catalog hull requirement is a canonical slug")
        }),
        mass: h.mass.into(),
        armor: h.armor.into(),
        initiative: h.initiative,
        fuel_capacity: h.fuel_capacity.into(),
        cargo_capacity: h.cargo_capacity.into(),
        cost: wire::MineralCost {
            ironium: h.cost.ironium.into(),
            boranium: h.cost.boranium.into(),
            germanium: h.cost.germanium.into(),
            resources: h.cost.resources.into(),
        },
        tech_requirements: wire::TechRequirements {
            energy: i64::from(h.requirements.energy).into(),
            weapons: i64::from(h.requirements.weapons).into(),
            propulsion: i64::from(h.requirements.propulsion).into(),
            construction: i64::from(h.requirements.construction).into(),
            electronics: i64::from(h.requirements.electronics).into(),
            biotechnology: i64::from(h.requirements.bio).into(),
        },
        slots: h.slots.iter().map(slot_to_wire).collect(),
        // Both fuel-regen fields are set together on Fuel Transport hulls and
        // absent (skipped) elsewhere — see the schema.
        fuel_regen_per_year: h.fuel_regen_per_year.map(u64::from),
        fuel_regen_percent: h.fuel_regen_percent.map(i64::from),
    }
}

/// Map one internal hull slot to its generated wire shape.
fn slot_to_wire(s: &TechSlot) -> wire::HullSlot {
    let slug = slot_type_slug(s.slot_type).expect("catalog slots use only canonical slot types");
    wire::HullSlot {
        slot_type: wire::SlotType::try_from(slug)
            .expect("slot-type slug is a canonical wire value"),
        max_count: std::num::NonZeroU64::new(u64::from(s.max_count))
            .expect("hull slot max_count is >= 1"),
        position: wire::SlotPosition {
            row: s.position.row.into(),
            col: s.position.col.into(),
        },
    }
}

/// GET /model/starbase/hulls — full starbase-hull catalog.
///
/// Response shape: schemas/response-model-starbase-hulls.json.
async fn model_starbase_hulls() -> impl IntoResponse {
    Json(starbase_hulls_response())
}

/// Build the `GET /model/starbase/hulls` response. The shape is GENERATED from
/// the single source of truth `schemas/response-model-starbase-hulls.json` (see
/// `build.rs`); this maps the internal catalog into that wire type, and the
/// `starbase_hulls_schema_contract` test validates the serialized output against
/// the schema. Mirrors `ship_hulls_response`; `slot_to_wire`'s slug is reused
/// via `slot_type_slug`.
pub fn starbase_hulls_response() -> sb_wire::StarbaseHullsResponse {
    sb_wire::StarbaseHullsResponse {
        hulls: starbase_hull_catalog()
            .into_iter()
            .map(starbase_hull_to_wire)
            .collect(),
    }
}

/// Map one internal `StarbaseHull` to its generated wire shape.
fn starbase_hull_to_wire(h: StarbaseHull) -> sb_wire::StarbaseHull {
    sb_wire::StarbaseHull {
        id: h.id.into(),
        slug: h.slug.to_string(),
        name: h.name.to_string(),
        requirement: h.requirement.map(|r| {
            sb_wire::HullRequirement::try_from(hull_requirement_slug(r))
                .expect("catalog starbase hull requirement is a canonical slug")
        }),
        armor: h.armor.into(),
        initiative: h.initiative,
        dock_capacity: h.dock_capacity.map(u64::from),
        cost: sb_wire::MineralCost {
            ironium: h.cost.ironium.into(),
            boranium: h.cost.boranium.into(),
            germanium: h.cost.germanium.into(),
            resources: h.cost.resources.into(),
        },
        tech_requirements: sb_wire::TechRequirements {
            energy: i64::from(h.requirements.energy).into(),
            weapons: i64::from(h.requirements.weapons).into(),
            propulsion: i64::from(h.requirements.propulsion).into(),
            construction: i64::from(h.requirements.construction).into(),
            electronics: i64::from(h.requirements.electronics).into(),
            biotechnology: i64::from(h.requirements.bio).into(),
        },
        slots: h.slots.iter().map(starbase_slot_to_wire).collect(),
    }
}

/// Map one internal starbase hull slot to its generated wire shape.
fn starbase_slot_to_wire(s: &TechSlot) -> sb_wire::HullSlot {
    let slug = slot_type_slug(s.slot_type).expect("catalog slots use only canonical slot types");
    sb_wire::HullSlot {
        slot_type: sb_wire::SlotType::try_from(slug)
            .expect("slot-type slug is a canonical wire value"),
        max_count: std::num::NonZeroU64::new(u64::from(s.max_count))
            .expect("hull slot max_count is >= 1"),
        position: sb_wire::SlotPosition {
            row: s.position.row.into(),
            col: s.position.col.into(),
        },
    }
}

/// GET /model/buildables — the production-queue buildable registry.
///
/// Maps every `build-object-id` a planet queue can hold to its semantic kind,
/// display name, and category. Clients resolve queue ids (and offer the add-item
/// picker) from this instead of hardcoding the mapping. The id scheme is the
/// single source of truth in `game::objects::buildable`; see
/// `docs/mechanics/production.rst` (Buildable Registry).
async fn model_buildables() -> impl IntoResponse {
    Json(buildables_response())
}

/// Build the `GET /model/buildables` response. Fixed installation/auto
/// buildables first (in registry order), then the per-player design slots. The
/// shape is the single source of truth schemas/response-model-buildables.json;
/// the `buildables_schema_contract` test validates this output against it.
pub fn buildables_response() -> bld_wire::BuildablesResponse {
    let mut buildables: Vec<bld_wire::Buildable> = FIXED_BUILDABLES
        .iter()
        .map(|b| bld_wire::Buildable {
            build_object_id: b.id,
            kind: b.kind.to_string(),
            name: b.name.to_string(),
            category: category_to_wire(b.category),
            design_slot: None,
        })
        .collect();
    for slot in 0..DESIGN_SLOTS {
        buildables.push(bld_wire::Buildable {
            build_object_id: design_build_object_id(slot).expect("slot in range"),
            kind: "design".to_string(),
            name: format!("Design Slot {slot}"),
            category: category_to_wire(Category::ShipDesign),
            design_slot: Some(slot),
        });
    }
    bld_wire::BuildablesResponse { buildables }
}

/// Map an internal buildable `Category` to its generated wire enum.
fn category_to_wire(c: Category) -> bld_wire::BuildableCategory {
    bld_wire::BuildableCategory::try_from(c.slug()).expect("buildable category is a canonical slug")
}

async fn model_schemas() -> impl IntoResponse {
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(json!({"error": "not yet implemented"})),
    )
}

// ---------------------------------------------------------------------------
// Race design handlers
// ---------------------------------------------------------------------------

/// POST /race/validate
///
/// Request body is a bare `Race` (schemas/request-validate-race.json). Response
/// is GENERATED from schemas/response-validate-race.json; the
/// `validate_race_schema_contract` test validates this output against it.
async fn race_validate(Json(race): Json<Race>) -> impl IntoResponse {
    Json(validate_race_response(&race))
}

/// Build the POST /race/validate response for a race. Shape is the single
/// source of truth schemas/response-validate-race.json.
pub fn validate_race_response(race: &Race) -> RaceValidateResponse {
    let points = advantage_points(race);
    let valid = points >= 0;
    RaceValidateResponse {
        advantage_points: points,
        valid,
        failure_reason: if valid {
            None
        } else {
            Some(format!(
                "race overspends its advantage-point budget by {}",
                -points
            ))
        },
    }
}

// ---------------------------------------------------------------------------
// Request / response types for game creation
// ---------------------------------------------------------------------------

#[derive(Deserialize)]
#[serde(rename_all = "kebab-case")]
struct HumanPlayerRequest {
    id: u32,
    #[allow(dead_code)]
    name: Option<String>,
    race: Value, // string (predefined name) or full race object
}

#[derive(Deserialize)]
struct AiPlayerRequest {
    #[allow(dead_code)]
    difficulty: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "kebab-case")]
struct UniverseParams {
    size: String,
    density: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "kebab-case")]
struct GameParams {
    name: String,
    human_players: Vec<HumanPlayerRequest>,
    ai_players: Option<Vec<AiPlayerRequest>>,
    universe: UniverseParams,
}

#[derive(Deserialize)]
struct CreateGameRequest {
    game: GameParams,
}

// `CreateGameResponse` / `CreatedGame` are GENERATED from
// `schemas/response-create-new-game.json` at build time (see `build.rs`).
use crate::game::objects::generated::create_game::{CreateGameResponse, CreatedGame};
use crate::game::objects::generated::validate_race::RaceValidateResponse;

// ---------------------------------------------------------------------------
// Universe file response types  (.xy equivalent — public, same for all players)
// ---------------------------------------------------------------------------

// `UniverseResponse` / `UniversePlanet` are GENERATED from
// `schemas/response-game.json` at build time (see `build.rs`); change the shape
// by editing that schema. See `docs/adr/0003`.
use crate::game::objects::generated::universe_file::{UniversePlanet, UniverseResponse};

// ---------------------------------------------------------------------------
// Turn file response types  (.m equivalent — private, per-player)
// ---------------------------------------------------------------------------

// The per-player turn-file response shape lives in `game::view::PlayerView`,
// produced by the single `player_view()` choke point. The handler below
// serialises it directly — there is no http-layer intermediate type.

// ---------------------------------------------------------------------------
// Game handlers
// ---------------------------------------------------------------------------

fn parse_universe_size(s: &str) -> Option<u32> {
    match s {
        "tiny" => Some(0),
        "small" => Some(1),
        "medium" => Some(2),
        "large" => Some(3),
        "huge" => Some(4),
        _ => None,
    }
}

fn parse_density(s: &str) -> Option<u32> {
    match s {
        "sparse" => Some(0),
        "normal" => Some(1),
        "dense" => Some(2),
        "packed" => Some(3),
        _ => None,
    }
}

/// Resolve a `race` field from a CreateGameRequest into a full `Race`.
///
/// String → look up in the predefined registry (Humanoid, Insectoid, …).
/// Object → deserialize directly (race wizard / custom races).
/// On failure, returns `None`; the caller should reject the request.
fn resolve_race(v: &Value) -> Option<Race> {
    match v {
        Value::String(name) => default_race_by_name(name),
        obj => serde_json::from_value::<Race>(obj.clone()).ok(),
    }
}

/// The starbase-design slot every race's starting homeworld starbase occupies.
/// Slot 0 of the player's 10-slot starbase design pool (see
/// docs/mechanics/starbase_design.rst).
const STARTING_STARBASE_SLOT: u32 = 0;

/// Give a freshly placed homeworld its starting starbase.
///
/// Every race begins with a Space Station "Starbase" in orbit over its
/// homeworld (docs/new_game/initial_state.rst). The design is written into the
/// player's first starbase design slot and the planet records that slot — a
/// planet holds at most one starbase (docs/mechanics/starbase_design.rst). The
/// design is hull-only for now; the faithful weapon/shield loadout (and the
/// IT/PP stargate / mass-driver variants) wait on the component catalog. This
/// is host-only ground truth — the starbase's derived combat stats are
/// projected into the turn file separately.
fn place_homeworld_starbase(designs: &mut Vec<ShipDesign>, homeworld: &mut PlanetState) {
    designs.push(ShipDesign {
        slot: STARTING_STARBASE_SLOT,
        kind: ShipDesignKind::Starbase,
        name: "Starbase".to_string(),
        hull_id: HOMEWORLD_STARBASE_HULL_ID,
        slot_assignments: Vec::new(),
    });
    homeworld.starbase_design_slot = Some(STARTING_STARBASE_SLOT);
}

/// Homeworld starting population, in colonists — the engine's standard fresh
/// homeworld (shared with `create_game`). The captured tutorial `.hst` records
/// a different raw figure whose unit relative to this colonist count is not yet
/// reconciled; that is a faithfulness-diff item, not a thin-slice blocker.
const HOMEWORLD_POPULATION: u32 = 25_000;

/// Build the deterministic Tutorial Game from the embedded scenario: the fixed
/// Tiny universe, both fixed players (human Humanoid/JOAT, AI Berserker/SS),
/// their homeworlds (owned, populated, with the starting starbase), and their
/// starting tech. The homeworld's hab is left exactly as the scenario carries
/// it — the captured homeworld hab is already the race-fitted 100%-value world,
/// so it is not re-randomized the way a procedural game's homeworld is.
///
/// Thin slice: starting fleets, the faithful starbase/ship component loadout,
/// and the AI player's CPU/difficulty modelling are not set here (they accrete
/// as the fleet model, component catalog and settings model land). Game
/// settings (victory/play flags) are not persisted — `GameState` has no
/// settings field yet; that is the game-settings-persistence task.
fn build_tutorial_game() -> GameState {
    let scenario = load_tutorial();
    let generated = scenario_universe(&scenario);
    let mut planet_states = generated.planet_states;

    let mut players: Vec<Player> = Vec::with_capacity(scenario.players.len());
    for sp in &scenario.players {
        let hw = sp.homeworld_planet_id;
        let mut designs: Vec<ShipDesign> = Vec::new();
        if let Some(state) = planet_states.get_mut(&hw) {
            state.homeworld = true;
            state.owner = Some(sp.id);
            state.population = HOMEWORLD_POPULATION;
            state.factories = 10;
            state.mines = 10;
            // Hab intentionally left as loaded (captured race-fit); see above.
            place_homeworld_starbase(&mut designs, state);
        }
        players.push(Player {
            id: sp.id,
            race_name: sp.race.name.clone(),
            homeworld_id: Some(hw),
            tech: sp.starting_tech.clone(),
            race: Some(sp.race.clone()),
            designs,
        });
    }

    GameState {
        id: uuid::Uuid::new_v4().to_string(),
        name: scenario.name.clone(),
        universe: generated.universe,
        planet_states,
        players,
        year: scenario.year,
        player_messages: Default::default(),
        fleets: Default::default(),
    }
}

/// POST /games/tutorial — create the deterministic Tutorial Game.
///
/// Takes no body: the tutorial is a fixed scenario. Persists and registers the
/// new game and returns its id, mirroring `POST /games`.
async fn create_tutorial_game(State(state): State<AppState>) -> impl IntoResponse {
    let game = build_tutorial_game();
    let game_id = game.id.clone();

    if let Err(e) = crate::store::save_game(&game) {
        log::error!("Failed to persist tutorial game {}: {}", game_id, e);
    }
    state.games.write().unwrap().insert(game_id.clone(), game);

    (
        StatusCode::CREATED,
        Json(CreateGameResponse {
            request_is_valid: true,
            created_game: Some(CreatedGame { id: game_id }),
            failure_reason: None,
        }),
    )
        .into_response()
}

/// POST /games — create a new game
async fn create_game(
    State(state): State<AppState>,
    Json(req): Json<CreateGameRequest>,
) -> impl IntoResponse {
    let gp = req.game;

    let size_idx = match parse_universe_size(&gp.universe.size) {
        Some(v) => v,
        None => {
            return (
                StatusCode::BAD_REQUEST,
                Json(json!({"error": "invalid universe size"})),
            )
                .into_response()
        }
    };

    let density_idx = match parse_density(&gp.universe.density) {
        Some(v) => v,
        None => {
            return (
                StatusCode::BAD_REQUEST,
                Json(json!({"error": "invalid density"})),
            )
                .into_response()
        }
    };

    let num_human = gp.human_players.len() as u32;
    let num_ai = gp.ai_players.as_ref().map(|v| v.len()).unwrap_or(0) as u32;
    let num_players = num_human + num_ai;

    let generated = generate_universe(size_idx, density_idx, num_players, None);
    let universe = generated.universe;
    let mut planet_states = generated.planet_states;

    // Sort planet ids so homeworld assignment is deterministic
    let mut planet_ids: Vec<u32> = universe.planets.keys().copied().collect();
    planet_ids.sort();

    let mut players: Vec<Player> = Vec::with_capacity(num_players as usize);

    // Assign homeworlds to human players
    for (slot, hp) in gp.human_players.iter().enumerate() {
        let race = match resolve_race(&hp.race) {
            Some(r) => r,
            None => {
                return (
                    StatusCode::BAD_REQUEST,
                    Json(json!({
                        "error": format!(
                            "could not resolve race for player {}: not in predefined registry and not a valid Race object",
                            hp.id,
                        ),
                    })),
                )
                    .into_response();
            }
        };
        let homeworld_id = planet_ids.get(slot).copied();
        let mut designs: Vec<ShipDesign> = Vec::new();
        if let Some(hw_id) = homeworld_id {
            if let Some(state) = planet_states.get_mut(&hw_id) {
                state.homeworld = true;
                state.owner = Some(hp.id);
                state.population = 25_000;
                state.factories = 10;
                state.mines = 10;
                state.set_homeworld_hab(&race);
                place_homeworld_starbase(&mut designs, state);
            }
        }
        players.push(Player {
            id: hp.id,
            race_name: race.name.clone(),
            homeworld_id,
            tech: starting_tech_levels(&race),
            race: Some(race),
            designs,
        });
    }

    // Assign homeworlds to AI players. AI races default to Humanoid until the
    // AI difficulty selector is wired through to a race choice.
    let human_count = gp.human_players.len();
    for (ai_slot, _ai) in gp.ai_players.as_ref().unwrap_or(&vec![]).iter().enumerate() {
        let slot = human_count + ai_slot;
        let ai_id = slot as u32;
        let race =
            default_race_by_name("Humanoid").expect("Humanoid is always in the default registry");
        let homeworld_id = planet_ids.get(slot).copied();
        let mut designs: Vec<ShipDesign> = Vec::new();
        if let Some(hw_id) = homeworld_id {
            if let Some(state) = planet_states.get_mut(&hw_id) {
                state.homeworld = true;
                state.owner = Some(ai_id);
                state.population = 25_000;
                state.factories = 10;
                state.mines = 10;
                state.set_homeworld_hab(&race);
                place_homeworld_starbase(&mut designs, state);
            }
        }
        players.push(Player {
            id: ai_id,
            race_name: "AI".to_string(),
            homeworld_id,
            tech: starting_tech_levels(&race),
            race: Some(race),
            designs,
        });
    }

    let game_id = uuid::Uuid::new_v4().to_string();
    let game = GameState {
        id: game_id.clone(),
        name: gp.name,
        universe,
        planet_states,
        players,
        year: 2400,
        player_messages: Default::default(),
        fleets: Default::default(),
    };

    if let Err(e) = crate::store::save_game(&game) {
        log::error!("Failed to persist game {}: {}", game_id, e);
    }

    state.games.write().unwrap().insert(game_id.clone(), game);

    let response = CreateGameResponse {
        request_is_valid: true,
        created_game: Some(CreatedGame { id: game_id }),
        failure_reason: None,
    };
    (StatusCode::CREATED, Json(response)).into_response()
}

/// GET /games/{game_id} — universe file (.xy equivalent)
///
/// Returns the public universe state: all planet positions and names.
/// This resource is the same for every player in the game.
async fn get_game(State(state): State<AppState>, Path(game_id): Path<String>) -> impl IntoResponse {
    let games = state.games.read().unwrap();
    match games.get(&game_id) {
        Some(g) => {
            let mut planets: Vec<UniversePlanet> = g
                .universe
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
                game_id: g.id.clone(),
                game_name: g.name.clone(),
                year: g.year,
                universe_width: g.universe.width,
                universe_height: g.universe.height,
                planet_count: g.universe.planet_count() as u32,
                planets,
            };
            Json(response).into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "game not found"})),
        )
            .into_response(),
    }
}

/// DELETE /games/{game_id} — remove a game from memory and disk.
///
/// Returns 204 if anything was removed (in-memory or on-disk), 404 if neither
/// existed. Idempotent on the gone-state — a second DELETE returns 404.
///
/// Rejects request paths that are not valid UUIDs to prevent path traversal
/// against the data dir.
async fn delete_game(
    State(state): State<AppState>,
    Path(game_id): Path<String>,
) -> impl IntoResponse {
    if uuid::Uuid::parse_str(&game_id).is_err() {
        return (
            StatusCode::BAD_REQUEST,
            Json(json!({"error": "invalid game_id"})),
        )
            .into_response();
    }

    let in_memory = state.games.write().unwrap().remove(&game_id).is_some();

    let on_disk = match crate::store::delete_game(&game_id) {
        Ok(removed) => removed,
        Err(e) => {
            log::error!("Failed to delete game dir for {}: {}", game_id, e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "failed to delete game directory"})),
            )
                .into_response();
        }
    };

    if in_memory || on_disk {
        StatusCode::NO_CONTENT.into_response()
    } else {
        (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "game not found"})),
        )
            .into_response()
    }
}

/// GET /games/{game_id}/turns/{year}/status
async fn turn_status(
    State(state): State<AppState>,
    Path((game_id, year)): Path<(String, u32)>,
) -> impl IntoResponse {
    let games = state.games.read().unwrap();
    match games.get(&game_id) {
        Some(g) => {
            let slots: Vec<Value> = g
                .players
                .iter()
                .map(|p| {
                    json!({
                        "slot_index": p.id,
                        "player_type": if p.race_name == "AI" { "ai" } else { "human" },
                        "status": if p.race_name == "AI" { "ready" } else { "pending" },
                    })
                })
                .collect();
            Json(json!({
                "game_id": game_id,
                "year": year,
                "slots": slots,
                "turn_processed": false,
            }))
            .into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "game not found"})),
        )
            .into_response(),
    }
}

/// GET /games/{game_id}/turns/{year}/players/{pid} — turn file for player
async fn get_turn_file(
    State(state): State<AppState>,
    Path((game_id, _year, pid)): Path<(String, u32, u32)>,
) -> impl IntoResponse {
    let games = state.games.read().unwrap();
    let game = match games.get(&game_id) {
        Some(g) => g,
        None => {
            return (
                StatusCode::NOT_FOUND,
                Json(json!({"error": "game not found"})),
            )
                .into_response()
        }
    };

    if !game.players.iter().any(|p| p.id == pid) {
        return (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "player not found"})),
        )
            .into_response();
    }

    let view = player_view(game, pid);
    Json(view).into_response()
}

/// POST /games/{game_id}/turns/{year}/advance — resolve the turn, advance year.
///
/// Host-driven turn generation: runs `resolve_turn` (every implemented
/// turn-resolution step, then bumps the year) and persists the result. This is
/// the single-player / hotseat "Generate" action; orders are already applied to
/// the ground-truth state as they are submitted, so there is nothing to collect
/// here. Gating multiplayer generation on all-players-submitted waits on
/// per-player submission tracking (`turn_status` is still a stub) — a follow-up.
///
/// The `{year}` in the path must be the game's current year, or the request is
/// rejected as stale (CONFLICT) — this keeps a double-submit or a client on an
/// old turn from silently resolving the turn twice.
async fn advance_turn(
    State(state): State<AppState>,
    Path((game_id, year)): Path<(String, u32)>,
) -> impl IntoResponse {
    let mut games = state.games.write().unwrap();
    let game = match games.get_mut(&game_id) {
        Some(g) => g,
        None => {
            return (
                StatusCode::NOT_FOUND,
                Json(json!({"error": "game not found"})),
            )
                .into_response()
        }
    };

    if game.year != year {
        return (
            StatusCode::CONFLICT,
            Json(json!({
                "error": format!(
                    "year {year} is not the current turn ({})",
                    game.year
                ),
            })),
        )
            .into_response();
    }

    crate::game::turn::resolve_turn(game);
    let new_year = game.year;

    if let Err(e) = crate::store::save_game(game) {
        log::error!("Failed to persist game {game_id} after advance: {e}");
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({"error": "failed to persist game"})),
        )
            .into_response();
    }

    (
        StatusCode::OK,
        Json(json!({ "game_id": game_id, "year": new_year, "turn_processed": true })),
    )
        .into_response()
}

/// Submit-orders request body (schemas/request-submit-orders.json). Orders are
/// kept as raw JSON and dispatched per `kind` below, since only a subset of the
/// schema's order kinds is applied today.
#[derive(Deserialize)]
struct SubmitOrdersBody {
    #[serde(default)]
    #[allow(dead_code)]
    schema_version: Option<u32>,
    player_id: u32,
    turn_year: u32,
    orders: Vec<Value>,
}

/// The `planet.set_production_queue` order payload (minus its `kind` tag).
#[derive(Deserialize)]
struct SetProductionQueueOrder {
    planet_id: u32,
    items: Vec<ProductionItemInput>,
}

/// The `planet.set_route_target` order payload (minus its `kind` tag). A null or
/// absent `target_planet_id` clears the route.
#[derive(Deserialize)]
struct SetRouteTargetOrder {
    planet_id: u32,
    #[serde(default)]
    target_planet_id: Option<u32>,
}

/// The `planet.set_packet_target` order payload (minus its `kind` tag). Unlike
/// a route target, `target_planet_id` is required — the order only sets a
/// destination (schemas/request-submit-orders.json).
#[derive(Deserialize)]
struct SetPacketTargetOrder {
    planet_id: u32,
    target_planet_id: u32,
}

/// The `design.upsert` order payload (minus its `kind` tag): the target slot
/// plus the design body. The body carries everything but the slot (which comes
/// from `design_slot`), matching the stored `ShipDesign` shape.
#[derive(Deserialize)]
struct DesignUpsertOrder {
    design_slot: u32,
    design: DesignPayload,
}

#[derive(Deserialize)]
struct DesignPayload {
    kind: crate::game::objects::player::ShipDesignKind,
    name: String,
    #[serde(rename = "hull-id")]
    hull_id: u32,
    #[serde(rename = "slot-assignments", default)]
    slot_assignments: Vec<crate::game::objects::player::SlotAssignment>,
}

/// The `design.delete` order payload (minus its `kind` tag): the (kind, slot)
/// identifying which design to remove.
#[derive(Deserialize)]
struct DesignDeleteOrder {
    design_slot: u32,
    #[serde(rename = "design_kind")]
    kind: crate::game::objects::player::ShipDesignKind,
}

/// Map an `OrderError` from the game layer to an HTTP response.
fn order_error_response(e: OrderError) -> axum::response::Response {
    let (status, msg) = match e {
        OrderError::PlanetNotFound(id) => (StatusCode::NOT_FOUND, format!("planet {id} not found")),
        OrderError::PlanetNotOwned(id) => (
            StatusCode::FORBIDDEN,
            format!("planet {id} is not owned by the submitting player"),
        ),
        OrderError::UnknownBuildable => (
            StatusCode::BAD_REQUEST,
            "order names an unknown buildable".to_string(),
        ),
        OrderError::RouteTargetNotFound(id) => (
            StatusCode::NOT_FOUND,
            format!("route target planet {id} not found"),
        ),
        OrderError::PlayerNotFound(id) => (StatusCode::NOT_FOUND, format!("player {id} not found")),
        OrderError::DesignSlotOutOfRange { kind, slot } => (
            StatusCode::BAD_REQUEST,
            format!("design slot {slot} is out of range for a {kind:?} design"),
        ),
        OrderError::DesignHullNotFound { kind, hull_id } => (
            StatusCode::BAD_REQUEST,
            format!("no {kind:?} hull with id {hull_id}"),
        ),
        OrderError::DesignHullNotAvailable { kind, hull_id } => (
            StatusCode::BAD_REQUEST,
            format!("{kind:?} hull {hull_id} is not available to this player (tech or PRT/LRT)"),
        ),
        OrderError::DesignSlotAssignmentInvalid { slot_index } => (
            StatusCode::BAD_REQUEST,
            format!("invalid slot assignment at slot index {slot_index}"),
        ),
        OrderError::DesignSlotLocked { kind, slot } => (
            StatusCode::CONFLICT,
            format!("{kind:?} design slot {slot} is locked (built-count > 0)"),
        ),
        OrderError::DesignNotFound { kind, slot } => (
            StatusCode::NOT_FOUND,
            format!("no {kind:?} design in slot {slot}"),
        ),
        OrderError::BuildDesignSlotEmpty { slot } => (
            StatusCode::BAD_REQUEST,
            format!("cannot build design slot {slot}: the player has no design there"),
        ),
        OrderError::PacketTargetNotFound(id) => (
            StatusCode::NOT_FOUND,
            format!("packet target planet {id} not found"),
        ),
        OrderError::StarbaseHasNoMassDriver(id) => (
            StatusCode::BAD_REQUEST,
            format!("planet {id} cannot launch mineral packets: its starbase has no mass driver"),
        ),
    };
    (status, Json(json!({"error": msg}))).into_response()
}

/// PUT /games/{game_id}/turns/{year}/orders/{pid} — submit player orders.
///
/// The single orders choke point (docs/orders/engine_api.rst). This slice
/// applies `planet.set_production_queue`; any other order kind is rejected with
/// 501 rather than silently accepted, so the client is never told an
/// unimplemented order succeeded. The engine is the gatekeeper: body/path
/// consistency and planet ownership are enforced here regardless of the client.
async fn submit_orders(
    State(state): State<AppState>,
    Path((game_id, year, pid)): Path<(String, u32, u32)>,
    Json(body): Json<SubmitOrdersBody>,
) -> impl IntoResponse {
    if body.player_id != pid {
        return (
            StatusCode::BAD_REQUEST,
            Json(json!({"error": "player_id in body does not match path"})),
        )
            .into_response();
    }
    if body.turn_year != year {
        return (
            StatusCode::BAD_REQUEST,
            Json(json!({"error": "turn_year in body does not match path"})),
        )
            .into_response();
    }

    let mut games = state.games.write().unwrap();
    let game = match games.get_mut(&game_id) {
        Some(g) => g,
        None => {
            return (
                StatusCode::NOT_FOUND,
                Json(json!({"error": "game not found"})),
            )
                .into_response()
        }
    };
    if !game.players.iter().any(|p| p.id == pid) {
        return (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "player not found"})),
        )
            .into_response();
    }

    let mut orders_applied = 0u32;
    for order in &body.orders {
        let kind = order.get("kind").and_then(Value::as_str).unwrap_or("");
        match kind {
            "planet.set_production_queue" => {
                let parsed: SetProductionQueueOrder = match serde_json::from_value(order.clone()) {
                    Ok(p) => p,
                    Err(e) => {
                        return (
                            StatusCode::BAD_REQUEST,
                            Json(json!({
                                "error": format!("invalid planet.set_production_queue order: {e}"),
                            })),
                        )
                            .into_response()
                    }
                };
                if let Err(e) =
                    apply_set_production_queue(game, pid, parsed.planet_id, &parsed.items)
                {
                    return order_error_response(e);
                }
                orders_applied += 1;
            }
            "planet.set_route_target" => {
                let parsed: SetRouteTargetOrder = match serde_json::from_value(order.clone()) {
                    Ok(p) => p,
                    Err(e) => {
                        return (
                            StatusCode::BAD_REQUEST,
                            Json(json!({
                                "error": format!("invalid planet.set_route_target order: {e}"),
                            })),
                        )
                            .into_response()
                    }
                };
                if let Err(e) =
                    apply_set_route_target(game, pid, parsed.planet_id, parsed.target_planet_id)
                {
                    return order_error_response(e);
                }
                orders_applied += 1;
            }
            "planet.set_packet_target" => {
                let parsed: SetPacketTargetOrder = match serde_json::from_value(order.clone()) {
                    Ok(p) => p,
                    Err(e) => {
                        return (
                            StatusCode::BAD_REQUEST,
                            Json(json!({
                                "error": format!("invalid planet.set_packet_target order: {e}"),
                            })),
                        )
                            .into_response()
                    }
                };
                if let Err(e) =
                    apply_set_packet_target(game, pid, parsed.planet_id, parsed.target_planet_id)
                {
                    return order_error_response(e);
                }
                orders_applied += 1;
            }
            "design.upsert" => {
                let parsed: DesignUpsertOrder = match serde_json::from_value(order.clone()) {
                    Ok(p) => p,
                    Err(e) => {
                        return (
                            StatusCode::BAD_REQUEST,
                            Json(json!({"error": format!("invalid design.upsert order: {e}")})),
                        )
                            .into_response()
                    }
                };
                let design = crate::game::objects::player::ShipDesign {
                    slot: parsed.design_slot,
                    kind: parsed.design.kind,
                    name: parsed.design.name,
                    hull_id: parsed.design.hull_id,
                    slot_assignments: parsed.design.slot_assignments,
                };
                if let Err(e) = apply_design_upsert(game, pid, design) {
                    return order_error_response(e);
                }
                orders_applied += 1;
            }
            "design.delete" => {
                let parsed: DesignDeleteOrder = match serde_json::from_value(order.clone()) {
                    Ok(p) => p,
                    Err(e) => {
                        return (
                            StatusCode::BAD_REQUEST,
                            Json(json!({"error": format!("invalid design.delete order: {e}")})),
                        )
                            .into_response()
                    }
                };
                if let Err(e) = apply_design_delete(game, pid, parsed.kind, parsed.design_slot) {
                    return order_error_response(e);
                }
                orders_applied += 1;
            }
            other => {
                return (
                    StatusCode::NOT_IMPLEMENTED,
                    Json(json!({
                        "error": format!("order kind '{other}' is not yet supported by this engine build"),
                    })),
                )
                    .into_response()
            }
        }
    }

    if let Err(e) = crate::store::save_game(game) {
        log::error!("Failed to persist game {game_id}: {e}");
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({"error": "failed to persist game"})),
        )
            .into_response();
    }

    (
        StatusCode::OK,
        Json(json!({ "accepted": true, "orders_applied": orders_applied })),
    )
        .into_response()
}

/// POST /games/{game_id}/turns/{year}/skip/{pid}
async fn skip_player(Path((game_id, year, pid)): Path<(String, u32, u32)>) -> impl IntoResponse {
    let (_, _, _) = (game_id, year, pid);
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(json!({"error": "not yet implemented"})),
    )
}

/// GET /games/{game_id}/turns/{year}/ai-orders/{pid}
async fn get_ai_orders(Path((game_id, year, pid)): Path<(String, u32, u32)>) -> impl IntoResponse {
    let (_, _, _) = (game_id, year, pid);
    (
        StatusCode::NOT_IMPLEMENTED,
        Json(json!({"error": "not yet implemented"})),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn buildables_registry_is_well_formed() {
        let body = serde_json::to_value(buildables_response()).expect("serialize buildables");
        let list = body["buildables"].as_array().expect("buildables array");

        // 12 fixed buildables + one entry per design slot.
        assert_eq!(list.len(), FIXED_BUILDABLES.len() + DESIGN_SLOTS as usize);

        // Core installations keep the original Type-29 item ids.
        let by_kind = |k: &str| {
            list.iter()
                .find(|b| b["kind"] == k)
                .and_then(|b| b["build-object-id"].as_u64())
        };
        assert_eq!(by_kind("factory"), Some(7));
        assert_eq!(by_kind("mine"), Some(8));
        assert_eq!(by_kind("defenses"), Some(9));

        // Every id is unique across fixed + design entries.
        let mut ids: Vec<u64> = list
            .iter()
            .map(|b| b["build-object-id"].as_u64().expect("id"))
            .collect();
        let n = ids.len();
        ids.sort_unstable();
        ids.dedup();
        assert_eq!(ids.len(), n, "build-object-ids must be unique");
    }

    #[test]
    fn homeworld_gets_a_space_station_starbase() {
        let generated = generate_universe(0, 1, 1, Some(7));
        let mut planet_states = generated.planet_states;
        let hw_id = *planet_states.keys().min().expect("at least one planet");

        let mut designs: Vec<ShipDesign> = Vec::new();
        {
            let hw = planet_states.get_mut(&hw_id).expect("homeworld state");
            assert_eq!(
                hw.starbase_design_slot, None,
                "no starbase before placement"
            );
            place_homeworld_starbase(&mut designs, hw);
            assert_eq!(hw.starbase_design_slot, Some(STARTING_STARBASE_SLOT));
        }

        assert_eq!(designs.len(), 1, "exactly one starting starbase design");
        let sb = &designs[0];
        assert_eq!(sb.kind, ShipDesignKind::Starbase);
        assert_eq!(sb.slot, STARTING_STARBASE_SLOT);
        assert_eq!(sb.name, "Starbase");
        assert_eq!(sb.hull_id, HOMEWORLD_STARBASE_HULL_ID);
        assert!(
            sb.slot_assignments.is_empty(),
            "hull-only until the component catalog lands"
        );

        // The hull id resolves to a real, gate-free starbase hull (Space Station):
        // every race can hold it from turn 1.
        let hull = starbase_hull_catalog()
            .into_iter()
            .find(|h| u32::from(h.id) == sb.hull_id)
            .expect("starting starbase hull is in the catalog");
        assert_eq!(hull.slug, "space_station");
        assert!(hull.requirement.is_none(), "no PRT/LRT gate");
    }

    #[test]
    fn tutorial_game_has_both_fixed_players_and_owned_homeworlds() {
        let game = build_tutorial_game();
        assert_eq!(game.name, "Tutorial Game");
        assert_eq!(game.year, 2400);
        assert_eq!(game.universe.planet_count(), 24);
        assert_eq!(game.players.len(), 2);

        // P0: human Humanoid/JOAT, homeworld planet 13.
        let p0 = game.players.iter().find(|p| p.id == 0).expect("player 0");
        assert_eq!(p0.race_name, "Humanoid");
        assert_eq!(p0.homeworld_id, Some(13));
        assert_eq!(p0.tech.energy, 3);
        // P1: AI Berserker/SS, homeworld planet 10.
        let p1 = game.players.iter().find(|p| p.id == 1).expect("player 1");
        assert_eq!(p1.race_name, "Berserker");
        assert_eq!(p1.homeworld_id, Some(10));
        assert_eq!(p1.tech.electronics, 5);

        // Both homeworlds are owned, populated, and carry a starting starbase.
        for (pid, hw) in [(0u32, 13u32), (1u32, 10u32)] {
            let st = &game.planet_states[&hw];
            assert_eq!(st.owner, Some(pid));
            assert!(st.homeworld);
            assert_eq!(st.population, HOMEWORLD_POPULATION);
            assert_eq!((st.factories, st.mines), (10, 10));
            assert_eq!(st.starbase_design_slot, Some(0));
        }
        // Each player has the starting Space Station starbase design.
        for p in &game.players {
            assert!(p
                .designs
                .iter()
                .any(|d| d.kind == ShipDesignKind::Starbase && d.slot == 0));
        }

        // The homeworld hab is the captured race-fit, NOT re-randomized: P0's
        // Stove Top stays a dead-centre 1.00 g / 0 C / 50 mR world.
        let hw0 = &game.planet_states[&13];
        assert!((hw0.gravity - 1.00).abs() < 1e-6);
        assert_eq!((hw0.temperature, hw0.radiation), (0, 50));

        // Every non-homeworld planet is unowned.
        let owned = game
            .planet_states
            .values()
            .filter(|s| s.owner.is_some())
            .count();
        assert_eq!(owned, 2);
    }

    #[test]
    fn tutorial_p0_turn_file_carries_the_homeworld_starbase_stats() {
        let game = build_tutorial_game();
        let view = crate::game::view::player_view(&game, 0);
        let hw = view
            .planets
            .iter()
            .find_map(|p| match p {
                crate::game::view::PlanetIntel::Observed(o) if o.id == 13 => Some(o),
                _ => None,
            })
            .expect("P0 observes its homeworld");
        let sb = hw.starbase.as_ref().expect("homeworld has a starbase");
        // Hull-only Space Station: base hull armor, no shields/driver yet.
        assert_eq!(sb.dock_capacity, None, "Space Station dock is unlimited");
        assert_eq!(sb.shields, 0);
        assert_eq!(sb.mass_driver, None);
        assert_eq!(sb.damage_percent, 0);
        assert!(sb.armor > 0, "at least the hull's base armor");
    }
}
