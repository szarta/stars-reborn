// Technology (component) catalog
//
// Static data for installable components, served at GET /model/technologies.
// Values come from the design reference docs/reference/{engines,components,
// starbase_components}.rst (sourced from Posey's spreadsheet / the legacy
// factory.py). Engine fuel tables are oracle-validated (see engines.rst); the
// other component numbers carry the docs' "needs oracle verification" caveat
// and are reproduced as-is from that authoritative community source.
//
// The first catalog slice landed engines, armor, shields, and orbital
// components (stargates + mass drivers) — the categories the starbase stats and
// the design system need first. This slice adds the non-installable planetary
// technologies (planetary scanners, planetary defenses, terraforming). The
// remaining installable ship categories (weapons, bombs, scanners, electrical,
// mechanical, mine-layers, mining-robots) and the two Mystery-Trader items
// (MegaPolyShell, LangstonShell) are tracked follow-ups; the catalog grows as
// they land.
//
// Ids match the original game's technology ids (model/enumerations.py).

use super::technology::{FuelTable, TechCost, TechRequirements};

// ---------------------------------------------------------------------------
// Component id allocation
// ---------------------------------------------------------------------------
//
// Component ids are Stars Reborn's OWN stable scheme, not the original game's
// (ADR-0005: we are faithful to mechanics, not binary files; the original
// identifies a design part by (category, sub-index), so there is no original
// "global id" to match). A part's id is referenced only inside a design's
// slot-assignments — a namespace separate from hull ids — so a component id may
// numerically coincide with a hull id without ambiguity. Ids are `u16`.
//
// Each category gets a contiguous block so an id is legible at a glance (block
// = id / 50 for the new categories). The four landed blocks keep the values the
// first catalog slice assigned; the remaining categories are reserved here and
// filled in by their own slices.
//
//   Landed (defined in this file):
//     armor          14– 24      shields        25– 33
//     engines       112–127      orbital       141–156   (stargates + drivers)
//
//   Hulls, for reference only (separate catalogs, separate namespace):
//     starbase hulls 157–161      ship hulls    162–299 (reserved headroom)
//
//   Remaining ship components (one block each; filled by later slices):
pub const BEAM_WEAPON_ID_BASE: u16 = 300; // 300–349
pub const TORPEDO_ID_BASE: u16 = 350; // 350–399
pub const BOMB_ID_BASE: u16 = 400; // 400–449
pub const SCANNER_ID_BASE: u16 = 450; // 450–499
pub const ELECTRICAL_ID_BASE: u16 = 500; // 500–549
pub const MECHANICAL_ID_BASE: u16 = 550; // 550–599
pub const MINE_LAYER_ID_BASE: u16 = 600; // 600–649
pub const MINING_ROBOT_ID_BASE: u16 = 650; // 650–699
                                           //     Mystery-Trader items   800–899   (reserved)
                                           //
                                           //   Planetary technologies (non-installable, no mass) — this slice. Each kind
                                           //   gets a sub-range inside the 700–799 planetary reservation:
pub const PLANETARY_SCANNER_ID_BASE: u16 = 700; // 700–719
pub const PLANETARY_DEFENSE_ID_BASE: u16 = 720; // 720–739
pub const TERRAFORMING_ID_BASE: u16 = 740; // 740–799
                                           //
                                           // Width per block is 50 — generous headroom over the category's item count; the
                                           // guard test below holds each landed category inside its range and keeps every
                                           // id unique, so a later slice that overflows a block fails a test rather than
                                           // colliding silently.
pub const COMPONENT_BLOCK_WIDTH: u16 = 50;

/// Trait gate restricting which races may research a component. Mirrors the
/// `requirement` field of the wire `tech-item` (a null gate = available to any
/// race with the tech levels). Only the single-PRT gate is used by this slice;
/// Mystery-Trader items are deferred with the rest.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TraitReq {
    /// Restricted to races with this Primary Racial Trait (slug, e.g. "IT").
    Prt(&'static str),
    /// Restricted to races with this Lesser Racial Trait (slug, e.g. "TT" for
    /// Total Terraforming). Maps to the wire `{ "lrt": [slug] }` gate.
    Lrt(&'static str),
}

/// Category-specific stats, selecting which wire `props-*` shape applies.
#[derive(Debug, Clone)]
pub enum Props {
    Engine {
        /// mg of fuel consumed per light-year at warp 0..=10 (index = warp).
        fuel_usage: FuelTable,
        /// Battle-speed rating as shown in the tech browser (engines.rst).
        battle_speed: u8,
        /// Whether the engine can safely travel at warp 10.
        warp10_travel: bool,
        /// Highest warp with zero fuel cost (ram-scoop characteristic).
        last_free_warp: u8,
        /// Cloaking bonus percent (Enigma Pulsar only).
        cloaking: u8,
        /// Additive battle-speed modifier (Enigma Pulsar: +0.25).
        battle_speed_modifier: f32,
    },
    Armor {
        armor_value: u32,
        /// Shield points this piece also provides (e.g. Fielded Kelarium).
        shield_value: u32,
        cloaking: u8,
    },
    Shield {
        shield_value: u32,
        /// Armor points this shield also provides (e.g. Croby Sharmor).
        armor_value: u32,
        cloaking: u8,
        jamming: u8,
        scanner_basic_range: u32,
        scanner_penetrating_range: u32,
    },
    /// Orbital structure (starbase-only). Stargate carries safe mass/range
    /// (None = unlimited / "any"); MassDriver carries its launch warp.
    Stargate {
        safe_mass: Option<u32>,
        safe_range: Option<u32>,
    },
    MassDriver {
        warp: u8,
    },
    /// Planetary technology (planet-only: not ship/starbase-installable and
    /// carries no mass). `kind` selects the stat shape.
    Planetary(PlanetaryKind),
}

/// The three planetary-technology kinds, each with its own stats. Mirrors the
/// wire `props-planetary` `kind` discriminator (scanner | defense |
/// terraforming).
#[derive(Debug, Clone)]
pub enum PlanetaryKind {
    /// Planetary scanner: normal scan range and (Snooper series) penetrating
    /// range, in light-years. A pen range of 0 = no penetrating coverage.
    Scanner {
        basic_range: u32,
        penetrating_range: u32,
    },
    /// Planetary defense: per-defense kill probability against a single bomb
    /// (0.0–1.0); overall protection compounds over the planet's defense count.
    Defense { base_coverage: f64 },
    /// Terraforming: max habitability units shiftable per year on each axis.
    /// Axis-specific items touch one axis (the others are 0); Total Terraform
    /// shifts all three by the same rate.
    Terraforming {
        gravity: u8,
        temperature: u8,
        radiation: u8,
    },
}

impl Props {
    /// The wire `tech-category` slug for this component.
    pub fn category(&self) -> &'static str {
        match self {
            Props::Engine { .. } => "engines",
            Props::Armor { .. } => "armor",
            Props::Shield { .. } => "shields",
            Props::Stargate { .. } | Props::MassDriver { .. } => "orbital",
            Props::Planetary(_) => "planetary",
        }
    }

    /// Whether this component is installable on a ship/starbase (carries mass).
    /// Orbital structures and planetary technologies are not installable on
    /// ships and carry no mass.
    pub fn is_installable(&self) -> bool {
        !matches!(
            self,
            Props::Stargate { .. } | Props::MassDriver { .. } | Props::Planetary(_)
        )
    }
}

/// One catalog entry: identity + gating + cost/tech levels + category stats.
#[derive(Debug, Clone)]
pub struct TechItem {
    pub id: u16,
    pub slug: &'static str,
    pub name: &'static str,
    pub requirement: Option<TraitReq>,
    /// Mass in kT for installable parts; `None` for orbital structures.
    pub mass: Option<u32>,
    pub cost: TechCost,
    pub tech_requirements: TechRequirements,
    pub props: Props,
}

fn cost(ironium: u32, boranium: u32, germanium: u32, resources: u32) -> TechCost {
    TechCost {
        ironium,
        boranium,
        germanium,
        resources,
    }
}

/// Tech-level requirement by branch: Energy, Weapons, Propulsion, Construction,
/// Electronics, Biotechnology.
fn tr(
    energy: u8,
    weapons: u8,
    propulsion: u8,
    construction: u8,
    electronics: u8,
    bio: u8,
) -> TechRequirements {
    TechRequirements {
        energy,
        weapons,
        propulsion,
        construction,
        electronics,
        bio,
    }
}

/// Returns the (growing) technology-component catalog.
pub fn technology_catalog() -> Vec<TechItem> {
    let mut items = Vec::new();
    items.extend(engines());
    items.extend(armors());
    items.extend(shields());
    items.extend(orbitals());
    items.extend(planetaries());
    items
}

// ---------------------------------------------------------------------------
// Engines (docs/reference/engines.rst — fuel tables oracle-validated)
// ---------------------------------------------------------------------------

#[allow(clippy::too_many_arguments)]
fn engine(
    id: u16,
    slug: &'static str,
    name: &'static str,
    mass: u32,
    cost: TechCost,
    tech_requirements: TechRequirements,
    fuel_usage: FuelTable,
    battle_speed: u8,
    warp10_travel: bool,
    last_free_warp: u8,
) -> TechItem {
    TechItem {
        id,
        slug,
        name,
        requirement: None,
        mass: Some(mass),
        cost,
        tech_requirements,
        props: Props::Engine {
            fuel_usage,
            battle_speed,
            warp10_travel,
            last_free_warp,
            cloaking: 0,
            battle_speed_modifier: 0.0,
        },
    }
}

fn engines() -> Vec<TechItem> {
    let mut v = vec![
        engine(
            112,
            "settlers_delight",
            "Settlers Delight",
            2,
            cost(1, 0, 1, 2),
            tr(0, 0, 0, 0, 0, 0),
            [0, 0, 0, 0, 0, 0, 0, 140, 275, 480, 576],
            6,
            false,
            6,
        ),
        engine(
            113,
            "quick_jump_5",
            "Quick Jump 5",
            4,
            cost(3, 0, 1, 3),
            tr(0, 0, 0, 0, 0, 0),
            [0, 0, 25, 100, 100, 100, 180, 500, 800, 900, 1080],
            5,
            false,
            1,
        ),
        engine(
            114,
            "fuel_mizer",
            "Fuel Mizer",
            6,
            cost(8, 0, 0, 11),
            tr(0, 0, 2, 0, 0, 0),
            [0, 0, 0, 0, 0, 35, 120, 175, 235, 360, 420],
            6,
            false,
            4,
        ),
        engine(
            115,
            "long_hump_6",
            "Long Hump 6",
            9,
            cost(5, 0, 1, 6),
            tr(0, 0, 3, 0, 0, 0),
            [0, 0, 20, 60, 100, 100, 105, 450, 750, 900, 1080],
            6,
            false,
            1,
        ),
        engine(
            116,
            "daddy_long_legs_7",
            "Daddy Long Legs 7",
            13,
            cost(11, 0, 3, 12),
            tr(0, 0, 5, 0, 0, 0),
            [0, 0, 20, 60, 70, 100, 100, 110, 600, 750, 900],
            7,
            false,
            1,
        ),
        engine(
            117,
            "alpha_drive_8",
            "Alpha Drive 8",
            17,
            cost(16, 0, 3, 28),
            tr(0, 0, 7, 0, 0, 0),
            [0, 0, 15, 50, 60, 70, 100, 100, 115, 700, 840],
            8,
            false,
            1,
        ),
        engine(
            118,
            "trans_galactic_drive",
            "Trans-Galactic Drive",
            25,
            cost(20, 20, 9, 50),
            tr(0, 0, 9, 0, 0, 0),
            [0, 0, 15, 35, 45, 55, 70, 80, 90, 100, 120],
            9,
            false,
            1,
        ),
        engine(
            119,
            "interspace_10",
            "Interspace-10",
            25,
            cost(18, 25, 10, 60),
            tr(0, 0, 11, 0, 0, 0),
            [0, 0, 10, 30, 40, 50, 60, 70, 80, 90, 100],
            10,
            true,
            1,
        ),
        engine(
            120,
            "trans_star_10",
            "Trans-Star 10",
            5,
            cost(3, 0, 3, 10),
            tr(0, 0, 23, 0, 0, 0),
            [0, 0, 5, 15, 20, 25, 30, 35, 40, 45, 50],
            10,
            true,
            1,
        ),
        engine(
            121,
            "radiating_hydro_ram_scoop",
            "Radiating Hydro-Ram Scoop",
            10,
            cost(3, 2, 9, 8),
            tr(2, 0, 6, 0, 0, 0),
            [0, 0, 0, 0, 0, 0, 0, 165, 375, 600, 720],
            6,
            false,
            6,
        ),
        engine(
            122,
            "sub_galactic_fuel_scoop",
            "Sub-Galactic Fuel Scoop",
            20,
            cost(4, 4, 7, 12),
            tr(2, 0, 8, 0, 0, 0),
            [0, 0, 0, 0, 0, 0, 85, 105, 210, 380, 456],
            7,
            false,
            5,
        ),
        engine(
            123,
            "trans_galactic_fuel_scoop",
            "Trans-Galactic Fuel Scoop",
            19,
            cost(5, 4, 12, 18),
            tr(3, 0, 9, 0, 0, 0),
            [0, 0, 0, 0, 0, 0, 0, 88, 100, 145, 174],
            8,
            false,
            6,
        ),
        engine(
            124,
            "trans_galactic_super_scoop",
            "Trans-Galactic Super Scoop",
            18,
            cost(6, 4, 16, 24),
            tr(4, 0, 12, 0, 0, 0),
            [0, 0, 0, 0, 0, 0, 0, 0, 65, 90, 108],
            9,
            false,
            7,
        ),
        engine(
            125,
            "trans_galactic_mizer_scoop",
            "Trans-Galactic Mizer Scoop",
            11,
            cost(5, 2, 13, 20),
            tr(4, 0, 16, 0, 0, 0),
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 70, 84],
            10,
            true,
            8,
        ),
        engine(
            126,
            "galaxy_scoop",
            "Galaxy Scoop",
            8,
            cost(4, 2, 9, 12),
            tr(5, 0, 20, 0, 0, 0),
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60],
            10,
            true,
            9,
        ),
    ];
    // Enigma Pulsar: +10% cloaking and +0.25 battle-speed modifier.
    v.push(TechItem {
        id: 127,
        slug: "enigma_pulsar",
        name: "Enigma Pulsar",
        requirement: None,
        mass: Some(20),
        cost: cost(12, 15, 11, 40),
        tech_requirements: tr(7, 0, 13, 5, 9, 0),
        props: Props::Engine {
            fuel_usage: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60],
            battle_speed: 10,
            warp10_travel: true,
            last_free_warp: 9,
            cloaking: 10,
            battle_speed_modifier: 0.25,
        },
    });
    v
}

// ---------------------------------------------------------------------------
// Armor (docs/reference/components.rst)
// ---------------------------------------------------------------------------

#[allow(clippy::too_many_arguments)]
fn armor(
    id: u16,
    slug: &'static str,
    name: &'static str,
    requirement: Option<TraitReq>,
    mass: u32,
    cost: TechCost,
    tech_requirements: TechRequirements,
    armor_value: u32,
    shield_value: u32,
    cloaking: u8,
) -> TechItem {
    TechItem {
        id,
        slug,
        name,
        requirement,
        mass: Some(mass),
        cost,
        tech_requirements,
        props: Props::Armor {
            armor_value,
            shield_value,
            cloaking,
        },
    }
}

fn armors() -> Vec<TechItem> {
    vec![
        armor(
            14,
            "tritanium",
            "Tritanium",
            None,
            60,
            cost(5, 0, 0, 10),
            tr(0, 0, 0, 0, 0, 0),
            50,
            0,
            0,
        ),
        armor(
            15,
            "crobmnium",
            "Crobmnium",
            None,
            56,
            cost(6, 0, 0, 13),
            tr(0, 0, 0, 3, 0, 0),
            75,
            0,
            0,
        ),
        armor(
            16,
            "carbonic_armor",
            "Carbonic Armor",
            None,
            25,
            cost(0, 0, 5, 15),
            tr(0, 0, 0, 0, 0, 4),
            100,
            0,
            0,
        ),
        armor(
            17,
            "strobnium",
            "Strobnium",
            None,
            54,
            cost(8, 0, 0, 18),
            tr(0, 0, 0, 6, 0, 0),
            120,
            0,
            0,
        ),
        armor(
            18,
            "organic_armor",
            "Organic Armor",
            None,
            15,
            cost(0, 0, 6, 20),
            tr(0, 0, 0, 0, 0, 7),
            175,
            0,
            0,
        ),
        armor(
            19,
            "kelarium",
            "Kelarium",
            None,
            50,
            cost(9, 1, 0, 25),
            tr(0, 0, 0, 9, 0, 0),
            180,
            0,
            0,
        ),
        // Fielded Kelarium: IS exclusive; also +50 shield dp.
        armor(
            20,
            "fielded_kelarium",
            "Fielded Kelarium",
            Some(TraitReq::Prt("IS")),
            50,
            cost(10, 0, 2, 28),
            tr(4, 0, 0, 10, 0, 0),
            175,
            50,
            0,
        ),
        // Depleted Neutronium: SS exclusive; 25% cloaking.
        armor(
            21,
            "depleted_neutronium",
            "Depleted Neutronium",
            Some(TraitReq::Prt("SS")),
            50,
            cost(10, 0, 2, 28),
            tr(0, 0, 0, 10, 3, 0),
            200,
            0,
            25,
        ),
        armor(
            22,
            "neutronium",
            "Neutronium",
            None,
            45,
            cost(11, 2, 1, 30),
            tr(0, 0, 0, 12, 0, 0),
            275,
            0,
            0,
        ),
        armor(
            23,
            "valanium",
            "Valanium",
            None,
            40,
            cost(15, 0, 0, 50),
            tr(0, 0, 0, 16, 0, 0),
            500,
            0,
            0,
        ),
        armor(
            24,
            "superlatanium",
            "Superlatanium",
            None,
            30,
            cost(25, 0, 0, 100),
            tr(0, 0, 0, 24, 0, 0),
            1500,
            0,
            0,
        ),
    ]
}

// ---------------------------------------------------------------------------
// Shields (docs/reference/components.rst)
// ---------------------------------------------------------------------------

#[allow(clippy::too_many_arguments)]
fn shield(
    id: u16,
    slug: &'static str,
    name: &'static str,
    requirement: Option<TraitReq>,
    mass: u32,
    cost: TechCost,
    tech_requirements: TechRequirements,
    shield_value: u32,
    armor_value: u32,
    cloaking: u8,
) -> TechItem {
    TechItem {
        id,
        slug,
        name,
        requirement,
        mass: Some(mass),
        cost,
        tech_requirements,
        props: Props::Shield {
            shield_value,
            armor_value,
            cloaking,
            jamming: 0,
            scanner_basic_range: 0,
            scanner_penetrating_range: 0,
        },
    }
}

fn shields() -> Vec<TechItem> {
    vec![
        shield(
            25,
            "moleskin_shield",
            "Moleskin Shield",
            None,
            1,
            cost(1, 0, 1, 4),
            tr(0, 0, 0, 0, 0, 0),
            25,
            0,
            0,
        ),
        shield(
            26,
            "cowhide_shield",
            "Cowhide Shield",
            None,
            1,
            cost(2, 0, 2, 5),
            tr(3, 0, 0, 0, 0, 0),
            40,
            0,
            0,
        ),
        shield(
            27,
            "wolverine_diffuse_shield",
            "Wolverine Diffuse Shield",
            None,
            1,
            cost(3, 0, 3, 6),
            tr(6, 0, 0, 0, 0, 0),
            60,
            0,
            0,
        ),
        // Croby Sharmor: IS exclusive; +65 armor dp.
        shield(
            28,
            "croby_sharmor",
            "Croby Sharmor",
            Some(TraitReq::Prt("IS")),
            10,
            cost(7, 0, 4, 15),
            tr(7, 0, 0, 4, 0, 0),
            60,
            65,
            0,
        ),
        // Shadow Shield: SS exclusive; 35% cloaking.
        shield(
            29,
            "shadow_shield",
            "Shadow Shield",
            Some(TraitReq::Prt("SS")),
            2,
            cost(3, 0, 3, 7),
            tr(7, 0, 0, 0, 3, 0),
            75,
            0,
            35,
        ),
        shield(
            30,
            "bear_neutrino_barrier",
            "Bear Neutrino Barrier",
            None,
            1,
            cost(4, 0, 4, 8),
            tr(10, 0, 0, 0, 0, 0),
            100,
            0,
            0,
        ),
        shield(
            31,
            "gorilla_delagator",
            "Gorilla Delagator",
            None,
            1,
            cost(5, 0, 6, 11),
            tr(14, 0, 0, 0, 0, 0),
            175,
            0,
            0,
        ),
        shield(
            32,
            "elephant_hide_fortress",
            "Elephant Hide Fortress",
            None,
            1,
            cost(8, 0, 10, 15),
            tr(18, 0, 0, 0, 0, 0),
            300,
            0,
            0,
        ),
        shield(
            33,
            "complete_phase_shield",
            "Complete Phase Shield",
            None,
            1,
            cost(12, 0, 15, 20),
            tr(22, 0, 0, 0, 0, 0),
            500,
            0,
            0,
        ),
    ]
}

// ---------------------------------------------------------------------------
// Orbital: stargates + mass drivers (docs/reference/starbase_components.rst)
// ---------------------------------------------------------------------------

#[allow(clippy::too_many_arguments)]
fn stargate(
    id: u16,
    slug: &'static str,
    name: &'static str,
    requirement: Option<TraitReq>,
    cost: TechCost,
    tech_requirements: TechRequirements,
    safe_mass: Option<u32>,
    safe_range: Option<u32>,
) -> TechItem {
    TechItem {
        id,
        slug,
        name,
        requirement,
        mass: None,
        cost,
        tech_requirements,
        props: Props::Stargate {
            safe_mass,
            safe_range,
        },
    }
}

fn mass_driver(
    id: u16,
    slug: &'static str,
    name: &'static str,
    requirement: Option<TraitReq>,
    cost: TechCost,
    tech_requirements: TechRequirements,
    warp: u8,
) -> TechItem {
    TechItem {
        id,
        slug,
        name,
        requirement,
        mass: None,
        cost,
        tech_requirements,
        props: Props::MassDriver { warp },
    }
}

fn orbitals() -> Vec<TechItem> {
    // Stargates. "IT only" gates to the Interstellar Traveler PRT. The two
    // "all PRTs except CA and HE" gates (Stargate 150/600, Stargate 300/500)
    // are an exclusion the simple trait-requirement model cannot express, so
    // they are left ungated here; per-PRT research access (CA/HE lack these)
    // is governed by the technology-access system (docs/reference/
    // technology_access.rst), tracked separately.
    let it = Some(TraitReq::Prt("IT"));
    let pp = Some(TraitReq::Prt("PP"));
    vec![
        stargate(
            141,
            "stargate_100_250",
            "Stargate 100/250",
            None,
            cost(50, 20, 20, 200),
            tr(0, 0, 5, 5, 0, 0),
            Some(100),
            Some(250),
        ),
        stargate(
            142,
            "stargate_any_300",
            "Stargate any/300",
            it,
            cost(50, 20, 20, 250),
            tr(0, 0, 6, 10, 0, 0),
            None,
            Some(300),
        ),
        stargate(
            143,
            "stargate_150_600",
            "Stargate 150/600",
            None,
            cost(50, 20, 20, 500),
            tr(0, 0, 11, 7, 0, 0),
            Some(150),
            Some(600),
        ),
        stargate(
            144,
            "stargate_300_500",
            "Stargate 300/500",
            None,
            cost(50, 20, 20, 600),
            tr(0, 0, 9, 13, 0, 0),
            Some(300),
            Some(500),
        ),
        stargate(
            145,
            "stargate_100_any",
            "Stargate 100/any",
            it,
            cost(50, 20, 20, 700),
            tr(0, 0, 16, 12, 0, 0),
            Some(100),
            None,
        ),
        stargate(
            146,
            "stargate_any_800",
            "Stargate any/800",
            it,
            cost(50, 20, 20, 700),
            tr(0, 0, 12, 18, 0, 0),
            None,
            Some(800),
        ),
        stargate(
            147,
            "stargate_any_any",
            "Stargate any/any",
            it,
            cost(50, 20, 20, 800),
            tr(0, 0, 19, 24, 0, 0),
            None,
            None,
        ),
        // Mass drivers. 7 and 10 are in the base research pool; the odd tiers
        // (5, 6, 8, 9, 11, 12, 13) are PP (Packet Physics) exclusive.
        mass_driver(
            148,
            "mass_driver_5",
            "Mass Driver 5",
            pp,
            cost(24, 20, 20, 70),
            tr(4, 0, 0, 0, 0, 0),
            5,
        ),
        mass_driver(
            149,
            "mass_driver_6",
            "Mass Driver 6",
            pp,
            cost(24, 20, 20, 144),
            tr(7, 0, 0, 0, 0, 0),
            6,
        ),
        mass_driver(
            150,
            "mass_driver_7",
            "Mass Driver 7",
            None,
            cost(100, 100, 100, 512),
            tr(9, 0, 0, 0, 0, 0),
            7,
        ),
        mass_driver(
            151,
            "super_driver_8",
            "Super Driver 8",
            pp,
            cost(24, 20, 20, 256),
            tr(11, 0, 0, 0, 0, 0),
            8,
        ),
        mass_driver(
            152,
            "super_driver_9",
            "Super Driver 9",
            pp,
            cost(24, 20, 20, 324),
            tr(13, 0, 0, 0, 0, 0),
            9,
        ),
        mass_driver(
            153,
            "ultra_driver_10",
            "Ultra Driver 10",
            None,
            cost(100, 100, 100, 968),
            tr(15, 0, 0, 0, 0, 0),
            10,
        ),
        mass_driver(
            154,
            "ultra_driver_11",
            "Ultra Driver 11",
            pp,
            cost(24, 20, 20, 484),
            tr(17, 0, 0, 0, 0, 0),
            11,
        ),
        mass_driver(
            155,
            "ultra_driver_12",
            "Ultra Driver 12",
            pp,
            cost(24, 20, 20, 576),
            tr(20, 0, 0, 0, 0, 0),
            12,
        ),
        mass_driver(
            156,
            "ultra_driver_13",
            "Ultra Driver 13",
            pp,
            cost(24, 20, 20, 676),
            tr(24, 0, 0, 0, 0, 0),
            13,
        ),
    ]
}

// ---------------------------------------------------------------------------
// Planetary technologies (docs/reference/planetary_tech.rst)
// ---------------------------------------------------------------------------
//
// Non-installable, planet-only: planetary scanners, planetary defenses, and
// terraforming. None carry mass. Values are confirmed against the Player's
// Guide help images for scanners and defenses; full oracle verification of the
// terraforming rates against stars.exe is still recommended.
//
// Access gates: the simple TraitReq model expresses single-trait *inclusion*
// only, so the scanner/defense *exclusion* gates (scanners: all PRTs except AR,
// Snooper series also removed for NAS; defenses: Laser/Planetary/Neutron shield
// excluded from WM and AR) are left ungated here — per-race research access is
// governed by the technology-access system (docs/reference/technology_access
// .rst), tracked separately. Total Terraform is the one expressible gate: it is
// granted by the TT (Total Terraforming) Lesser Racial Trait.

fn planetary_scanner(
    id: u16,
    slug: &'static str,
    name: &'static str,
    tech_requirements: TechRequirements,
    basic_range: u32,
    penetrating_range: u32,
) -> TechItem {
    TechItem {
        id,
        slug,
        name,
        requirement: None,
        mass: None,
        // All planetary scanners share one cost (planetary_tech.rst).
        cost: cost(10, 10, 70, 100),
        tech_requirements,
        props: Props::Planetary(PlanetaryKind::Scanner {
            basic_range,
            penetrating_range,
        }),
    }
}

fn planetary_defense(
    id: u16,
    slug: &'static str,
    name: &'static str,
    tech_requirements: TechRequirements,
    base_coverage: f64,
) -> TechItem {
    TechItem {
        id,
        slug,
        name,
        requirement: None,
        mass: None,
        // All planetary defenses share one cost (planetary_tech.rst).
        cost: cost(5, 5, 5, 15),
        tech_requirements,
        props: Props::Planetary(PlanetaryKind::Defense { base_coverage }),
    }
}

#[allow(clippy::too_many_arguments)]
fn terraform(
    id: u16,
    slug: &'static str,
    name: &'static str,
    requirement: Option<TraitReq>,
    cost: TechCost,
    tech_requirements: TechRequirements,
    gravity: u8,
    temperature: u8,
    radiation: u8,
) -> TechItem {
    TechItem {
        id,
        slug,
        name,
        requirement,
        mass: None,
        cost,
        tech_requirements,
        props: Props::Planetary(PlanetaryKind::Terraforming {
            gravity,
            temperature,
            radiation,
        }),
    }
}

fn planetaries() -> Vec<TechItem> {
    let s = PLANETARY_SCANNER_ID_BASE;
    let d = PLANETARY_DEFENSE_ID_BASE;
    let t = TERRAFORMING_ID_BASE;
    // Axis-specific terraform cost; Total Terraform costs less (70 resources).
    let axis_cost = cost(0, 0, 0, 100);
    let total_cost = cost(0, 0, 0, 70);
    let tt = Some(TraitReq::Lrt("TT"));
    vec![
        // Planetary scanners (9): basic range, and pen range for Snoopers.
        planetary_scanner(s, "viewer_50", "Viewer 50", tr(0, 0, 0, 0, 0, 0), 50, 0),
        planetary_scanner(s + 1, "viewer_90", "Viewer 90", tr(0, 0, 0, 0, 1, 0), 90, 0),
        planetary_scanner(
            s + 2,
            "scoper_150",
            "Scoper 150",
            tr(0, 0, 0, 0, 3, 0),
            150,
            0,
        ),
        planetary_scanner(
            s + 3,
            "scoper_220",
            "Scoper 220",
            tr(0, 0, 0, 0, 6, 0),
            220,
            0,
        ),
        planetary_scanner(
            s + 4,
            "scoper_280",
            "Scoper 280",
            tr(0, 0, 0, 0, 8, 0),
            280,
            0,
        ),
        planetary_scanner(
            s + 5,
            "snooper_320x",
            "Snooper 320X",
            tr(3, 0, 0, 0, 10, 3),
            320,
            160,
        ),
        planetary_scanner(
            s + 6,
            "snooper_400x",
            "Snooper 400X",
            tr(4, 0, 0, 0, 13, 6),
            400,
            200,
        ),
        planetary_scanner(
            s + 7,
            "snooper_500x",
            "Snooper 500X",
            tr(5, 0, 0, 0, 16, 7),
            500,
            250,
        ),
        planetary_scanner(
            s + 8,
            "snooper_620x",
            "Snooper 620X",
            tr(7, 0, 0, 0, 23, 9),
            620,
            310,
        ),
        // Planetary defenses (5): per-defense kill probability vs one bomb.
        planetary_defense(d, "sdi", "SDI", tr(0, 0, 0, 0, 0, 0), 0.0099),
        planetary_defense(
            d + 1,
            "missile_battery",
            "Missile Battery",
            tr(5, 0, 0, 0, 0, 0),
            0.0199,
        ),
        planetary_defense(
            d + 2,
            "laser_battery",
            "Laser Battery",
            tr(10, 0, 0, 0, 0, 0),
            0.0239,
        ),
        planetary_defense(
            d + 3,
            "planetary_shield",
            "Planetary Shield",
            tr(16, 0, 0, 0, 0, 0),
            0.0299,
        ),
        planetary_defense(
            d + 4,
            "neutron_shield",
            "Neutron Shield",
            tr(23, 0, 0, 0, 0, 0),
            0.0379,
        ),
        // Terraforming — Total Terraform (8, TT LRT): all three axes together.
        terraform(
            t,
            "total_terraform_3",
            "Total Terraform ±3",
            tt,
            total_cost,
            tr(0, 0, 0, 0, 0, 0),
            3,
            3,
            3,
        ),
        terraform(
            t + 1,
            "total_terraform_5",
            "Total Terraform ±5",
            tt,
            total_cost,
            tr(0, 0, 0, 0, 0, 3),
            5,
            5,
            5,
        ),
        terraform(
            t + 2,
            "total_terraform_7",
            "Total Terraform ±7",
            tt,
            total_cost,
            tr(0, 0, 0, 0, 0, 6),
            7,
            7,
            7,
        ),
        terraform(
            t + 3,
            "total_terraform_10",
            "Total Terraform ±10",
            tt,
            total_cost,
            tr(0, 0, 0, 0, 0, 9),
            10,
            10,
            10,
        ),
        terraform(
            t + 4,
            "total_terraform_15",
            "Total Terraform ±15",
            tt,
            total_cost,
            tr(0, 0, 0, 0, 0, 13),
            15,
            15,
            15,
        ),
        terraform(
            t + 5,
            "total_terraform_20",
            "Total Terraform ±20",
            tt,
            total_cost,
            tr(0, 0, 0, 0, 0, 17),
            20,
            20,
            20,
        ),
        terraform(
            t + 6,
            "total_terraform_25",
            "Total Terraform ±25",
            tt,
            total_cost,
            tr(0, 0, 0, 0, 0, 22),
            25,
            25,
            25,
        ),
        terraform(
            t + 7,
            "total_terraform_30",
            "Total Terraform ±30",
            tt,
            total_cost,
            tr(0, 0, 0, 0, 0, 25),
            30,
            30,
            30,
        ),
        // Terraforming — axis-specific (12, base pool): gravity.
        terraform(
            t + 8,
            "gravity_terraform_3",
            "Gravity Terraform ±3",
            None,
            axis_cost,
            tr(0, 0, 1, 0, 0, 1),
            3,
            0,
            0,
        ),
        terraform(
            t + 9,
            "gravity_terraform_7",
            "Gravity Terraform ±7",
            None,
            axis_cost,
            tr(0, 0, 5, 0, 0, 2),
            7,
            0,
            0,
        ),
        terraform(
            t + 10,
            "gravity_terraform_11",
            "Gravity Terraform ±11",
            None,
            axis_cost,
            tr(0, 0, 10, 0, 0, 3),
            11,
            0,
            0,
        ),
        terraform(
            t + 11,
            "gravity_terraform_15",
            "Gravity Terraform ±15",
            None,
            axis_cost,
            tr(0, 0, 16, 0, 0, 4),
            15,
            0,
            0,
        ),
        // temperature.
        terraform(
            t + 12,
            "temperature_terraform_3",
            "Temperature Terraform ±3",
            None,
            axis_cost,
            tr(1, 0, 0, 0, 0, 1),
            0,
            3,
            0,
        ),
        terraform(
            t + 13,
            "temperature_terraform_7",
            "Temperature Terraform ±7",
            None,
            axis_cost,
            tr(5, 0, 0, 0, 0, 2),
            0,
            7,
            0,
        ),
        terraform(
            t + 14,
            "temperature_terraform_11",
            "Temperature Terraform ±11",
            None,
            axis_cost,
            tr(10, 0, 0, 0, 0, 3),
            0,
            11,
            0,
        ),
        terraform(
            t + 15,
            "temperature_terraform_15",
            "Temperature Terraform ±15",
            None,
            axis_cost,
            tr(16, 0, 0, 0, 0, 4),
            0,
            15,
            0,
        ),
        // radiation.
        terraform(
            t + 16,
            "radiation_terraform_3",
            "Radiation Terraform ±3",
            None,
            axis_cost,
            tr(0, 1, 0, 0, 0, 1),
            0,
            0,
            3,
        ),
        terraform(
            t + 17,
            "radiation_terraform_7",
            "Radiation Terraform ±7",
            None,
            axis_cost,
            tr(0, 5, 0, 0, 0, 2),
            0,
            0,
            7,
        ),
        terraform(
            t + 18,
            "radiation_terraform_11",
            "Radiation Terraform ±11",
            None,
            axis_cost,
            tr(0, 10, 0, 0, 0, 3),
            0,
            0,
            11,
        ),
        terraform(
            t + 19,
            "radiation_terraform_15",
            "Radiation Terraform ±15",
            None,
            axis_cost,
            tr(0, 16, 0, 0, 0, 4),
            0,
            0,
            15,
        ),
    ]
}

#[cfg(test)]
mod id_allocation_tests {
    use super::*;

    #[test]
    fn catalog_ids_are_unique() {
        let cat = technology_catalog();
        let mut ids: Vec<u16> = cat.iter().map(|t| t.id).collect();
        let n = ids.len();
        ids.sort_unstable();
        ids.dedup();
        assert_eq!(
            ids.len(),
            n,
            "component ids must be unique across the catalog"
        );
    }

    #[test]
    fn landed_categories_stay_in_their_declared_id_ranges() {
        // (category slug, inclusive id range) — the landed blocks.
        let ranges: &[(&str, u16, u16)] = &[
            ("armor", 14, 24),
            ("shields", 25, 33),
            ("engines", 112, 127),
            ("orbital", 141, 156),
            ("planetary", 700, 799),
        ];
        for item in technology_catalog() {
            let slug = item.props.category();
            let (_, lo, hi) = ranges
                .iter()
                .find(|(s, ..)| *s == slug)
                .unwrap_or_else(|| panic!("no declared id range for category {slug:?}"));
            assert!(
                (*lo..=*hi).contains(&item.id),
                "{} (id {}) is outside its {} block {}..={}",
                item.name,
                item.id,
                slug,
                lo,
                hi
            );
        }
    }

    #[test]
    fn reserved_component_blocks_are_ordered_and_non_overlapping() {
        let bases = [
            BEAM_WEAPON_ID_BASE,
            TORPEDO_ID_BASE,
            BOMB_ID_BASE,
            SCANNER_ID_BASE,
            ELECTRICAL_ID_BASE,
            MECHANICAL_ID_BASE,
            MINE_LAYER_ID_BASE,
            MINING_ROBOT_ID_BASE,
        ];
        // The first new block sits clear of the hull id reservation (157–299).
        assert!(
            bases[0] >= 300,
            "component blocks must start above hull ids"
        );
        for w in bases.windows(2) {
            assert!(
                w[1] >= w[0] + COMPONENT_BLOCK_WIDTH,
                "reserved blocks at {} and {} overlap (width {})",
                w[0],
                w[1],
                COMPONENT_BLOCK_WIDTH
            );
        }
    }
}
