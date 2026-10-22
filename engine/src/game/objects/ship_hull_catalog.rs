// Ship hull catalog
//
// Static data for every ship hull in the game. Values mirror the legacy
// Python engine (stars-reborn-research/stars-reborn/src/factory.py) and the
// design reference at stars-reborn-design/docs/reference/ship_hulls.rst.
//
// Slot positions are placeholders (single row, col = slot index) until task
// #83 captures real per-hull layouts from the original Ship Designer.

use super::technology::{
    HullCategory, HullRequirement, ShipHull, SlotPosition, SlotType, TechCost, TechRequirements,
    TechSlot,
};

fn req(construction: u8) -> TechRequirements {
    TechRequirements {
        construction,
        ..TechRequirements::NONE
    }
}

fn cost(ironium: u32, boranium: u32, germanium: u32, resources: u32) -> TechCost {
    TechCost {
        ironium,
        boranium,
        germanium,
        resources,
    }
}

fn slots(specs: &[(SlotType, u8)]) -> Vec<TechSlot> {
    specs
        .iter()
        .enumerate()
        .map(|(i, &(slot_type, max_count))| TechSlot {
            slot_type,
            max_count,
            position: SlotPosition {
                row: 0,
                col: i as u8,
            },
        })
        .collect()
}

/// Returns the canonical, ordered ship-hull catalog.
///
/// Order matches the original game's Ship Designer hull-picker grouping:
/// scouts/light combat, freighters, armed freighters, colony ships, bombers,
/// miners, fuel transports, mine layers, ultra-hulls.
pub fn ship_hull_catalog() -> Vec<ShipHull> {
    use SlotType as S;
    vec![
        // ----- Scouts and light combat -----
        ShipHull {
            id: 166,
            slug: "scout",
            name: "Scout",
            category: HullCategory::Scout,
            requirement: None,
            requirements: TechRequirements::NONE,
            cost: cost(4, 2, 4, 10),
            slots: slots(&[(S::ENGINES, 1), (S::GENERAL_PURPOSE, 1), (S::SCANNERS, 1)]),
            armor: 20,
            initiative: 1,
            mass: 8,
            fuel_capacity: 50,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 167,
            slug: "frigate",
            name: "Frigate",
            category: HullCategory::Scout,
            requirement: None,
            requirements: req(6),
            cost: cost(4, 2, 4, 12),
            slots: slots(&[
                (S::ENGINES, 1),
                (S::PROTECTION, 2),
                (S::GENERAL_PURPOSE, 3),
                (S::SCANNERS, 2),
            ]),
            armor: 45,
            initiative: 4,
            mass: 8,
            fuel_capacity: 125,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 168,
            slug: "destroyer",
            name: "Destroyer",
            category: HullCategory::Scout,
            requirement: None,
            requirements: req(3),
            cost: cost(15, 3, 5, 35),
            slots: slots(&[
                (S::ENGINES, 1),
                (S::WEAPONS, 1),
                (S::WEAPONS, 1),
                (S::ARMOR, 2),
                (S::GENERAL_PURPOSE, 1),
                (S::ELECTRICAL, 1),
                (S::MECHANICAL, 1),
            ]),
            armor: 200,
            initiative: 3,
            mass: 30,
            fuel_capacity: 280,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 169,
            slug: "cruiser",
            name: "Cruiser",
            category: HullCategory::Scout,
            requirement: None,
            requirements: req(9),
            cost: cost(40, 5, 8, 85),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::WEAPONS, 2),
                (S::WEAPONS, 2),
                (S::PROTECTION, 2),
                (S::GENERAL_PURPOSE, 2),
                (S::SHIELD_ELECT_MECH, 1),
                (S::SHIELD_ELECT_MECH, 1),
            ]),
            armor: 700,
            initiative: 5,
            mass: 90,
            fuel_capacity: 600,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 170,
            slug: "battle_cruiser",
            name: "Battle Cruiser",
            category: HullCategory::Scout,
            requirement: None,
            requirements: req(10),
            cost: cost(55, 8, 12, 120),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::WEAPONS, 3),
                (S::WEAPONS, 3),
                (S::PROTECTION, 4),
                (S::GENERAL_PURPOSE, 3),
                (S::SHIELD_ELECT_MECH, 2),
                (S::SHIELD_ELECT_MECH, 2),
            ]),
            armor: 1000,
            initiative: 5,
            mass: 120,
            fuel_capacity: 1400,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 171,
            slug: "battleship",
            name: "Battleship",
            category: HullCategory::Scout,
            requirement: None,
            requirements: req(13),
            cost: cost(120, 25, 20, 225),
            slots: slots(&[
                (S::ENGINES, 4),
                (S::WEAPONS, 2),
                (S::WEAPONS, 2),
                (S::WEAPONS, 6),
                (S::WEAPONS, 6),
                (S::WEAPONS, 4),
                (S::ARMOR, 6),
                (S::ELECTRICAL, 3),
                (S::ELECTRICAL, 3),
                (S::SHIELDS, 8),
                (S::SCANNER_ELECT_MECH, 1),
            ]),
            armor: 2000,
            initiative: 10,
            mass: 222,
            fuel_capacity: 2800,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 172,
            slug: "dreadnought",
            name: "Dreadnought",
            category: HullCategory::Scout,
            requirement: None,
            requirements: req(16),
            cost: cost(140, 30, 25, 275),
            slots: slots(&[
                (S::ENGINES, 5),
                (S::WEAPONS, 6),
                (S::WEAPONS, 6),
                (S::WEAPONS, 8),
                (S::WEAPONS, 8),
                (S::ARMOR, 8),
                (S::ELECTRICAL, 4),
                (S::ELECTRICAL, 4),
                (S::PROTECTION, 4),
                (S::PROTECTION, 4),
                (S::GENERAL_PURPOSE, 1),
                (S::WEAPON_SHIELD, 5),
                (S::WEAPON_SHIELD, 5),
            ]),
            armor: 4500,
            initiative: 10,
            mass: 250,
            fuel_capacity: 4500,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        // ----- Freighters -----
        ShipHull {
            id: 162,
            slug: "small_freighter",
            name: "Small Freighter",
            category: HullCategory::Freighter,
            requirement: None,
            requirements: TechRequirements::NONE,
            cost: cost(12, 0, 17, 20),
            slots: slots(&[
                (S::ENGINES, 1),
                (S::PROTECTION, 1),
                (S::SCANNER_ELECT_MECH, 1),
            ]),
            armor: 25,
            initiative: 0,
            mass: 25,
            fuel_capacity: 130,
            cargo_capacity: 70,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 163,
            slug: "medium_freighter",
            name: "Medium Freighter",
            category: HullCategory::Freighter,
            requirement: None,
            requirements: req(3),
            cost: cost(20, 0, 19, 40),
            slots: slots(&[
                (S::ENGINES, 1),
                (S::PROTECTION, 1),
                (S::SCANNER_ELECT_MECH, 1),
            ]),
            armor: 50,
            initiative: 0,
            mass: 60,
            fuel_capacity: 450,
            cargo_capacity: 210,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 164,
            slug: "large_freighter",
            name: "Large Freighter",
            category: HullCategory::Freighter,
            requirement: None,
            requirements: req(8),
            cost: cost(35, 0, 21, 100),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::PROTECTION, 2),
                (S::SCANNER_ELECT_MECH, 2),
            ]),
            armor: 150,
            initiative: 0,
            mass: 125,
            fuel_capacity: 2600,
            cargo_capacity: 1200,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 165,
            slug: "super_freighter",
            name: "Super Freighter",
            category: HullCategory::Freighter,
            requirement: None,
            requirements: req(13),
            cost: cost(45, 0, 21, 125),
            slots: slots(&[
                (S::ENGINES, 3),
                (S::PROTECTION, 5),
                (S::SCANNER_ELECT_MECH, 3),
                (S::ELECTRICAL, 2),
            ]),
            armor: 400,
            initiative: 0,
            mass: 175,
            fuel_capacity: 8000,
            cargo_capacity: 3000,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        // ----- Armed freighters / multi-purpose -----
        ShipHull {
            id: 173,
            slug: "privateer",
            name: "Privateer",
            category: HullCategory::ArmedFreighter,
            requirement: None,
            requirements: req(4),
            cost: cost(50, 3, 2, 50),
            slots: slots(&[
                (S::ENGINES, 1),
                (S::PROTECTION, 2),
                (S::GENERAL_PURPOSE, 1),
                (S::GENERAL_PURPOSE, 1),
                (S::SCANNER_ELECT_MECH, 1),
            ]),
            armor: 150,
            initiative: 3,
            mass: 65,
            fuel_capacity: 650,
            cargo_capacity: 250,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 174,
            slug: "rogue",
            name: "Rogue",
            category: HullCategory::ArmedFreighter,
            requirement: None,
            requirements: req(8),
            cost: cost(80, 5, 5, 60),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::ELECTRICAL, 1),
                (S::ELECTRICAL, 1),
                (S::GENERAL_PURPOSE, 2),
                (S::GENERAL_PURPOSE, 2),
                (S::PROTECTION, 3),
                (S::MINE_ELECT_MECH, 2),
                (S::MINE_ELECT_MECH, 2),
                (S::SCANNERS, 1),
            ]),
            armor: 450,
            initiative: 4,
            mass: 75,
            fuel_capacity: 2250,
            cargo_capacity: 500,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 175,
            slug: "galleon",
            name: "Galleon",
            category: HullCategory::ArmedFreighter,
            requirement: None,
            requirements: req(11),
            cost: cost(70, 5, 5, 105),
            slots: slots(&[
                (S::ENGINES, 4),
                (S::PROTECTION, 2),
                (S::PROTECTION, 2),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::ELECTRICAL, 1),
                (S::MINE_ELECT_MECH, 2),
                (S::ELECT_MECH, 2),
                (S::SCANNERS, 2),
            ]),
            armor: 900,
            initiative: 4,
            mass: 125,
            fuel_capacity: 2500,
            cargo_capacity: 1000,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        // ----- Colony ships -----
        ShipHull {
            id: 176,
            slug: "mini_colony_ship",
            name: "Mini Colony Ship",
            category: HullCategory::Colony,
            requirement: None,
            requirements: TechRequirements::NONE,
            cost: cost(2, 0, 2, 3),
            slots: slots(&[(S::ENGINES, 1), (S::MECHANICAL, 1)]),
            armor: 10,
            initiative: 0,
            mass: 8,
            fuel_capacity: 150,
            cargo_capacity: 10,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 177,
            slug: "colony_ship",
            name: "Colony Ship",
            category: HullCategory::Colony,
            requirement: None,
            requirements: TechRequirements::NONE,
            cost: cost(10, 0, 15, 20),
            slots: slots(&[(S::ENGINES, 1), (S::MECHANICAL, 1)]),
            armor: 20,
            initiative: 0,
            mass: 20,
            fuel_capacity: 200,
            cargo_capacity: 25,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        // ----- Bombers -----
        ShipHull {
            id: 178,
            slug: "mini_bomber",
            name: "Mini Bomber",
            category: HullCategory::Bomber,
            requirement: None,
            requirements: req(1),
            cost: cost(20, 5, 10, 35),
            slots: slots(&[(S::ENGINES, 1), (S::BOMBS, 2)]),
            armor: 50,
            initiative: 0,
            mass: 28,
            fuel_capacity: 120,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 179,
            slug: "b17_bomber",
            name: "B-17 Bomber",
            category: HullCategory::Bomber,
            requirement: None,
            requirements: req(6),
            cost: cost(55, 10, 10, 150),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::BOMBS, 4),
                (S::BOMBS, 4),
                (S::SCANNER_ELECT_MECH, 1),
            ]),
            armor: 175,
            initiative: 0,
            mass: 69,
            fuel_capacity: 400,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 180,
            slug: "stealth_bomber",
            name: "Stealth Bomber",
            category: HullCategory::Bomber,
            requirement: None,
            requirements: req(8),
            cost: cost(55, 10, 15, 175),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::BOMBS, 4),
                (S::BOMBS, 4),
                (S::SCANNER_ELECT_MECH, 1),
                (S::ELECTRICAL, 3),
            ]),
            armor: 225,
            initiative: 0,
            mass: 70,
            fuel_capacity: 750,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 181,
            slug: "b52_bomber",
            name: "B-52 Bomber",
            category: HullCategory::Bomber,
            requirement: None,
            requirements: req(15),
            cost: cost(90, 15, 10, 280),
            slots: slots(&[
                (S::ENGINES, 3),
                (S::BOMBS, 4),
                (S::BOMBS, 4),
                (S::BOMBS, 4),
                (S::BOMBS, 4),
                (S::SHIELDS, 2),
                (S::SCANNER_ELECT_MECH, 2),
            ]),
            armor: 450,
            initiative: 0,
            mass: 110,
            fuel_capacity: 750,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        // ----- Miners -----
        ShipHull {
            id: 182,
            slug: "midget_miner",
            name: "Midget Miner",
            category: HullCategory::Miner,
            requirement: Some(HullRequirement::ARM),
            requirements: TechRequirements::NONE,
            cost: cost(10, 0, 3, 20),
            slots: slots(&[(S::ENGINES, 1), (S::MINING_ROBOTS, 2)]),
            armor: 100,
            initiative: 0,
            mass: 10,
            fuel_capacity: 210,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 183,
            slug: "mini_miner",
            name: "Mini Miner",
            category: HullCategory::Miner,
            requirement: None,
            requirements: req(2),
            cost: cost(25, 0, 6, 50),
            slots: slots(&[
                (S::ENGINES, 1),
                (S::MINING_ROBOTS, 1),
                (S::MINING_ROBOTS, 1),
                (S::SCANNER_ELECT_MECH, 1),
            ]),
            armor: 130,
            initiative: 0,
            mass: 80,
            fuel_capacity: 210,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 184,
            slug: "miner",
            name: "Miner",
            category: HullCategory::Miner,
            requirement: None,
            requirements: req(6),
            cost: cost(32, 0, 6, 110),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::MINING_ROBOTS, 2),
                (S::MINING_ROBOTS, 2),
                (S::MINING_ROBOTS, 1),
                (S::MINING_ROBOTS, 1),
                (S::ARMOR_SCANNER_ELECT_MECH, 2),
            ]),
            armor: 475,
            initiative: 0,
            mass: 110,
            fuel_capacity: 500,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 185,
            slug: "maxi_miner",
            name: "Maxi Miner",
            category: HullCategory::Miner,
            requirement: None,
            requirements: req(11),
            cost: cost(32, 0, 6, 140),
            slots: slots(&[
                (S::ENGINES, 1),
                (S::MINING_ROBOTS, 4),
                (S::MINING_ROBOTS, 4),
                (S::MINING_ROBOTS, 1),
                (S::MINING_ROBOTS, 1),
                (S::ARMOR_SCANNER_ELECT_MECH, 2),
            ]),
            armor: 1400,
            initiative: 0,
            mass: 110,
            fuel_capacity: 850,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 186,
            slug: "ultra_miner",
            name: "Ultra Miner",
            category: HullCategory::Miner,
            requirement: None,
            requirements: req(14),
            cost: cost(30, 0, 6, 130),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::MINING_ROBOTS, 4),
                (S::MINING_ROBOTS, 4),
                (S::MINING_ROBOTS, 2),
                (S::MINING_ROBOTS, 2),
                (S::ARMOR_SCANNER_ELECT_MECH, 3),
            ]),
            armor: 1500,
            initiative: 0,
            mass: 100,
            fuel_capacity: 1300,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        // ----- Fuel transports -----
        ShipHull {
            id: 187,
            slug: "fuel_transport",
            name: "Fuel Transport",
            category: HullCategory::FuelTransport,
            requirement: None,
            requirements: req(4),
            cost: cost(10, 0, 5, 50),
            slots: slots(&[(S::ENGINES, 1), (S::SHIELDS, 1)]),
            armor: 5,
            initiative: 0,
            mass: 12,
            fuel_capacity: 750,
            cargo_capacity: 0,
            fuel_regen_per_year: Some(200),
            fuel_regen_percent: Some(5),
        },
        ShipHull {
            id: 188,
            slug: "super_fuel_transport",
            name: "Super Fuel Transport",
            category: HullCategory::FuelTransport,
            requirement: None,
            requirements: req(7),
            cost: cost(20, 0, 8, 70),
            slots: slots(&[(S::ENGINES, 2), (S::SHIELDS, 2), (S::SCANNERS, 1)]),
            armor: 12,
            initiative: 0,
            mass: 111,
            fuel_capacity: 2250,
            cargo_capacity: 0,
            fuel_regen_per_year: Some(200),
            fuel_regen_percent: Some(10),
        },
        // ----- Mine layers -----
        ShipHull {
            id: 189,
            slug: "mini_mine_layer",
            name: "Mini Mine Layer",
            category: HullCategory::MineLayer,
            requirement: None,
            requirements: TechRequirements::NONE,
            cost: cost(8, 2, 5, 20),
            slots: slots(&[
                (S::ENGINES, 1),
                (S::MINE_LAYERS, 2),
                (S::MINE_LAYERS, 2),
                (S::SCANNER_ELECT_MECH, 1),
            ]),
            armor: 60,
            initiative: 0,
            mass: 10,
            fuel_capacity: 400,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 190,
            slug: "super_mine_layer",
            name: "Super Mine Layer",
            category: HullCategory::MineLayer,
            requirement: None,
            requirements: req(15),
            cost: cost(20, 3, 9, 30),
            slots: slots(&[
                (S::ENGINES, 3),
                (S::MINE_LAYERS, 8),
                (S::MINE_LAYERS, 8),
                (S::SCANNER_ELECT_MECH, 3),
                (S::PROTECTION, 3),
                (S::MINE_ELECT_MECH, 3),
            ]),
            armor: 1200,
            initiative: 0,
            mass: 30,
            fuel_capacity: 2200,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        // ----- Ultra-hulls -----
        ShipHull {
            id: 191,
            slug: "nubian",
            name: "Nubian",
            category: HullCategory::Ultra,
            requirement: None,
            requirements: req(26),
            cost: cost(75, 12, 12, 150),
            slots: slots(&[
                (S::ENGINES, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
                (S::GENERAL_PURPOSE, 3),
            ]),
            armor: 5000,
            initiative: 2,
            mass: 100,
            fuel_capacity: 5000,
            cargo_capacity: 0,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 192,
            slug: "metamorph",
            name: "MetaMorph",
            category: HullCategory::Ultra,
            requirement: Some(HullRequirement::AR),
            requirements: req(8),
            cost: cost(50, 12, 12, 120),
            slots: slots(&[
                (S::ENGINES, 3),
                (S::GENERAL_PURPOSE, 2),
                (S::GENERAL_PURPOSE, 2),
                (S::GENERAL_PURPOSE, 2),
                (S::GENERAL_PURPOSE, 2),
                (S::GENERAL_PURPOSE, 8),
                (S::GENERAL_PURPOSE, 1),
            ]),
            armor: 500,
            initiative: 2,
            mass: 85,
            fuel_capacity: 700,
            cargo_capacity: 300,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
        ShipHull {
            id: 238,
            slug: "minimorph",
            name: "MiniMorph",
            category: HullCategory::Ultra,
            requirement: Some(HullRequirement::AR),
            requirements: req(8),
            cost: cost(30, 8, 8, 100),
            slots: slots(&[
                (S::ENGINES, 2),
                (S::GENERAL_PURPOSE, 2),
                (S::GENERAL_PURPOSE, 2),
                (S::GENERAL_PURPOSE, 1),
                (S::GENERAL_PURPOSE, 1),
                (S::GENERAL_PURPOSE, 1),
                (S::GENERAL_PURPOSE, 3),
            ]),
            armor: 25,
            initiative: 2,
            mass: 70,
            fuel_capacity: 400,
            cargo_capacity: 150,
            fuel_regen_per_year: None,
            fuel_regen_percent: None,
        },
    ]
}

/// Map a `SlotType` bit pattern to its canonical kebab-case schema string.
/// Returns `None` if the pattern is not one of the 22 named slot types defined
/// in `stars-reborn-schemas/tech.json`.
pub fn slot_type_slug(t: SlotType) -> Option<&'static str> {
    Some(match t {
        s if s == SlotType::ENGINES => "engines",
        s if s == SlotType::WEAPONS => "weapons",
        s if s == SlotType::BEAM_WEAPONS => "beam-weapons",
        s if s == SlotType::TORPEDOES => "torpedoes",
        s if s == SlotType::ARMOR => "armor",
        s if s == SlotType::SHIELDS => "shields",
        s if s == SlotType::PROTECTION => "protection",
        s if s == SlotType::ELECTRICAL => "electrical",
        s if s == SlotType::MECHANICAL => "mechanical",
        s if s == SlotType::ELECT_MECH => "elect-mech",
        s if s == SlotType::BOMBS => "bombs",
        s if s == SlotType::MINE_LAYERS => "mine-layers",
        s if s == SlotType::MINE_ELECT_MECH => "mine-elect-mech",
        s if s == SlotType::MINING_ROBOTS => "mining-robots",
        s if s == SlotType::SCANNERS => "scanners",
        s if s == SlotType::SCANNER_ELECT_MECH => "scanner-elect-mech",
        s if s == SlotType::SHIELD_ELECT_MECH => "shield-elect-mech",
        s if s == SlotType::ARMOR_SCANNER_ELECT_MECH => "armor-scanner-elect-mech",
        s if s == SlotType::WEAPON_SHIELD => "weapon-shield",
        s if s == SlotType::ORBITAL => "orbital",
        s if s == SlotType::ORBITAL_ELECT => "orbital-elect",
        s if s == SlotType::GENERAL_PURPOSE => "general-purpose",
        _ => return None,
    })
}

pub fn hull_category_slug(c: HullCategory) -> &'static str {
    match c {
        HullCategory::Scout => "scout",
        HullCategory::Freighter => "freighter",
        HullCategory::ArmedFreighter => "armed-freighter",
        HullCategory::Colony => "colony",
        HullCategory::Bomber => "bomber",
        HullCategory::Miner => "miner",
        HullCategory::FuelTransport => "fuel-transport",
        HullCategory::MineLayer => "mine-layer",
        HullCategory::Ultra => "ultra",
    }
}

pub fn hull_requirement_slug(r: HullRequirement) -> &'static str {
    match r {
        HullRequirement::AR => "AR",
        HullRequirement::ARM => "ARM",
        HullRequirement::MT => "MT",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn catalog_has_32_ship_hulls() {
        // 7 scouts + 4 freighters + 3 armed-freighters + 2 colony + 4 bombers
        // + 5 miners + 2 fuel-transports + 2 mine-layers + 3 ultra-hulls.
        assert_eq!(ship_hull_catalog().len(), 32);
    }

    #[test]
    fn ids_and_slugs_are_unique() {
        let catalog = ship_hull_catalog();
        let mut ids: Vec<u8> = catalog.iter().map(|h| h.id).collect();
        ids.sort();
        ids.dedup();
        assert_eq!(ids.len(), catalog.len(), "duplicate hull id");

        let mut slugs: Vec<&str> = catalog.iter().map(|h| h.slug).collect();
        slugs.sort();
        slugs.dedup();
        assert_eq!(slugs.len(), catalog.len(), "duplicate hull slug");
    }

    #[test]
    fn fuel_transports_have_regen_others_dont() {
        for hull in ship_hull_catalog() {
            let is_ft = hull.category == HullCategory::FuelTransport;
            assert_eq!(
                hull.fuel_regen_per_year.is_some(),
                is_ft,
                "{} fuel_regen_per_year mismatch",
                hull.name
            );
            assert_eq!(
                hull.fuel_regen_percent.is_some(),
                is_ft,
                "{} fuel_regen_percent mismatch",
                hull.name
            );
        }
    }

    #[test]
    fn ar_hulls_are_metamorph_family() {
        let ar_hulls: Vec<&str> = ship_hull_catalog()
            .iter()
            .filter(|h| h.requirement == Some(HullRequirement::AR))
            .map(|h| h.slug)
            .collect();
        assert_eq!(ar_hulls, vec!["metamorph", "minimorph"]);
    }

    #[test]
    fn arm_hulls_are_midget_miner_only() {
        let arm_hulls: Vec<&str> = ship_hull_catalog()
            .iter()
            .filter(|h| h.requirement == Some(HullRequirement::ARM))
            .map(|h| h.slug)
            .collect();
        assert_eq!(arm_hulls, vec!["midget_miner"]);
    }

    #[test]
    fn every_slot_type_has_a_slug() {
        for hull in ship_hull_catalog() {
            for slot in &hull.slots {
                assert!(
                    slot_type_slug(slot.slot_type).is_some(),
                    "{} has slot with no slug: {:?}",
                    hull.name,
                    slot.slot_type
                );
            }
        }
    }
}
