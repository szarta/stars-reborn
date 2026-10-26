// Ship hull catalog
//
// Static data for every ship hull in the game. Values mirror the legacy
// Python engine (stars-reborn-research/stars-reborn/src/factory.py) and the
// design reference at stars-reborn-design/docs/reference/ship_hulls.rst.
//
// Slot positions are the real per-hull Ship Designer layout, verified against
// the original game's Tech Browser hull view. Grid unit = half a slot box;
// (row, col) origin at the top-left of each hull's box cluster.

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

fn slots(specs: &[(SlotType, u8, u8, u8)]) -> Vec<TechSlot> {
    specs
        .iter()
        .map(|&(slot_type, max_count, row, col)| TechSlot {
            slot_type,
            max_count,
            position: SlotPosition { row, col },
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
            slots: slots(&[
                (S::ENGINES, 1, 0, 0),
                (S::GENERAL_PURPOSE, 1, 0, 2),
                (S::SCANNERS, 1, 0, 4),
            ]),
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
                (S::ENGINES, 1, 0, 0),
                (S::PROTECTION, 2, 0, 2),
                (S::GENERAL_PURPOSE, 3, 0, 4),
                (S::SCANNERS, 2, 0, 6),
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
                (S::ENGINES, 1, 3, 0),
                (S::WEAPONS, 1, 0, 3),
                (S::WEAPONS, 1, 6, 3),
                (S::ARMOR, 2, 3, 2),
                (S::GENERAL_PURPOSE, 1, 3, 4),
                (S::ELECTRICAL, 1, 5, 1),
                (S::MECHANICAL, 1, 1, 1),
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
                (S::ENGINES, 2, 2, 0),
                (S::WEAPONS, 2, 4, 4),
                (S::WEAPONS, 2, 0, 4),
                (S::PROTECTION, 2, 2, 4),
                (S::GENERAL_PURPOSE, 2, 2, 6),
                (S::SHIELD_ELECT_MECH, 1, 3, 2),
                (S::SHIELD_ELECT_MECH, 1, 1, 2),
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
                (S::ENGINES, 2, 2, 0),
                (S::WEAPONS, 3, 4, 4),
                (S::WEAPONS, 3, 0, 4),
                (S::PROTECTION, 4, 2, 4),
                (S::GENERAL_PURPOSE, 3, 2, 6),
                (S::SHIELD_ELECT_MECH, 2, 3, 2),
                (S::SHIELD_ELECT_MECH, 2, 1, 2),
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
                (S::ENGINES, 4, 3, 0),
                (S::WEAPONS, 2, 6, 2),
                (S::WEAPONS, 2, 0, 2),
                (S::WEAPONS, 6, 5, 4),
                (S::WEAPONS, 6, 1, 4),
                (S::WEAPONS, 4, 4, 6),
                (S::ARMOR, 6, 3, 4),
                (S::ELECTRICAL, 3, 4, 2),
                (S::ELECTRICAL, 3, 2, 2),
                (S::SHIELDS, 8, 2, 6),
                (S::SCANNER_ELECT_MECH, 1, 3, 8),
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
                (S::ENGINES, 5, 3, 0),
                (S::WEAPONS, 6, 6, 2),
                (S::WEAPONS, 6, 0, 2),
                (S::WEAPONS, 8, 5, 4),
                (S::WEAPONS, 8, 1, 4),
                (S::ARMOR, 8, 3, 4),
                (S::ELECTRICAL, 4, 4, 2),
                (S::ELECTRICAL, 4, 2, 2),
                (S::PROTECTION, 4, 5, 0),
                (S::PROTECTION, 4, 1, 0),
                (S::GENERAL_PURPOSE, 2, 3, 8),
                (S::WEAPON_SHIELD, 5, 4, 6),
                (S::WEAPON_SHIELD, 5, 2, 6),
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
                (S::ENGINES, 1, 0, 0),
                (S::PROTECTION, 1, 0, 4),
                (S::SCANNER_ELECT_MECH, 1, 0, 6),
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
                (S::ENGINES, 1, 0, 0),
                (S::PROTECTION, 1, 0, 6),
                (S::SCANNER_ELECT_MECH, 1, 0, 8),
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
                (S::ENGINES, 2, 1, 0),
                (S::PROTECTION, 2, 2, 6),
                (S::SCANNER_ELECT_MECH, 2, 0, 6),
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
                (S::ENGINES, 3, 2, 0),
                (S::PROTECTION, 5, 2, 8),
                (S::SCANNER_ELECT_MECH, 3, 0, 8),
                (S::ELECTRICAL, 2, 4, 8),
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
                (S::ENGINES, 1, 2, 0),
                (S::PROTECTION, 2, 1, 6),
                (S::GENERAL_PURPOSE, 1, 4, 4),
                (S::GENERAL_PURPOSE, 1, 0, 4),
                (S::SCANNER_ELECT_MECH, 1, 3, 6),
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
                (S::ENGINES, 2, 3, 0),
                (S::ELECTRICAL, 1, 6, 1),
                (S::ELECTRICAL, 1, 0, 1),
                (S::GENERAL_PURPOSE, 2, 6, 3),
                (S::GENERAL_PURPOSE, 2, 0, 3),
                (S::PROTECTION, 3, 3, 5),
                (S::MINE_ELECT_MECH, 2, 5, 5),
                (S::MINE_ELECT_MECH, 2, 1, 5),
                (S::SCANNERS, 1, 3, 7),
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
                (S::ENGINES, 4, 3, 0),
                (S::PROTECTION, 2, 6, 3),
                (S::PROTECTION, 2, 0, 3),
                (S::GENERAL_PURPOSE, 3, 6, 5),
                (S::GENERAL_PURPOSE, 3, 0, 5),
                (S::MINE_ELECT_MECH, 2, 2, 6),
                (S::ELECT_MECH, 2, 4, 6),
                (S::SCANNERS, 2, 3, 8),
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
            slots: slots(&[(S::ENGINES, 1, 0, 0), (S::MECHANICAL, 1, 0, 4)]),
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
            slots: slots(&[(S::ENGINES, 1, 0, 0), (S::MECHANICAL, 1, 0, 4)]),
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
            slots: slots(&[(S::ENGINES, 1, 0, 0), (S::BOMBS, 2, 0, 2)]),
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
                (S::ENGINES, 2, 0, 0),
                (S::BOMBS, 4, 0, 2),
                (S::BOMBS, 4, 0, 4),
                (S::SCANNER_ELECT_MECH, 1, 0, 6),
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
                (S::ENGINES, 2, 1, 0),
                (S::BOMBS, 4, 2, 2),
                (S::BOMBS, 4, 0, 2),
                (S::SCANNER_ELECT_MECH, 1, 0, 4),
                (S::ELECTRICAL, 3, 2, 4),
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
                (S::ENGINES, 3, 2, 0),
                (S::BOMBS, 4, 4, 2),
                (S::BOMBS, 4, 0, 2),
                (S::BOMBS, 4, 3, 4),
                (S::BOMBS, 4, 1, 4),
                (S::SHIELDS, 2, 2, 2),
                (S::SCANNER_ELECT_MECH, 2, 2, 6),
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
            slots: slots(&[(S::ENGINES, 1, 0, 0), (S::MINING_ROBOTS, 2, 0, 2)]),
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
                (S::ENGINES, 1, 1, 0),
                (S::MINING_ROBOTS, 1, 2, 2),
                (S::MINING_ROBOTS, 1, 0, 2),
                (S::SCANNER_ELECT_MECH, 1, 1, 4),
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
                (S::ENGINES, 2, 1, 0),
                (S::MINING_ROBOTS, 2, 2, 2),
                (S::MINING_ROBOTS, 2, 0, 2),
                (S::MINING_ROBOTS, 1, 2, 4),
                (S::MINING_ROBOTS, 1, 0, 4),
                (S::ARMOR_SCANNER_ELECT_MECH, 2, 1, 6),
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
                (S::ENGINES, 3, 1, 0),
                (S::MINING_ROBOTS, 4, 2, 2),
                (S::MINING_ROBOTS, 4, 0, 2),
                (S::MINING_ROBOTS, 1, 2, 4),
                (S::MINING_ROBOTS, 1, 0, 4),
                (S::ARMOR_SCANNER_ELECT_MECH, 2, 1, 6),
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
                (S::ENGINES, 2, 1, 0),
                (S::MINING_ROBOTS, 4, 2, 2),
                (S::MINING_ROBOTS, 4, 0, 2),
                (S::MINING_ROBOTS, 2, 2, 4),
                (S::MINING_ROBOTS, 2, 0, 4),
                (S::ARMOR_SCANNER_ELECT_MECH, 3, 1, 6),
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
            slots: slots(&[(S::ENGINES, 1, 0, 0), (S::SHIELDS, 1, 0, 2)]),
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
            slots: slots(&[
                (S::ENGINES, 2, 0, 0),
                (S::SHIELDS, 2, 0, 2),
                (S::SCANNERS, 1, 0, 4),
            ]),
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
                (S::ENGINES, 1, 1, 0),
                (S::MINE_LAYERS, 2, 2, 2),
                (S::MINE_LAYERS, 2, 0, 2),
                (S::SCANNER_ELECT_MECH, 1, 1, 4),
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
                (S::ENGINES, 3, 1, 0),
                (S::MINE_LAYERS, 8, 2, 2),
                (S::MINE_LAYERS, 8, 0, 2),
                (S::SCANNER_ELECT_MECH, 3, 0, 6),
                (S::PROTECTION, 3, 1, 4),
                (S::MINE_ELECT_MECH, 3, 2, 6),
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
                (S::ENGINES, 3, 3, 0),
                (S::GENERAL_PURPOSE, 3, 5, 0),
                (S::GENERAL_PURPOSE, 3, 1, 0),
                (S::GENERAL_PURPOSE, 3, 6, 2),
                (S::GENERAL_PURPOSE, 3, 4, 2),
                (S::GENERAL_PURPOSE, 3, 2, 2),
                (S::GENERAL_PURPOSE, 3, 0, 2),
                (S::GENERAL_PURPOSE, 3, 5, 4),
                (S::GENERAL_PURPOSE, 3, 3, 4),
                (S::GENERAL_PURPOSE, 3, 1, 4),
                (S::GENERAL_PURPOSE, 3, 4, 6),
                (S::GENERAL_PURPOSE, 3, 2, 6),
                (S::GENERAL_PURPOSE, 3, 3, 8),
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
                (S::ENGINES, 3, 2, 0),
                (S::GENERAL_PURPOSE, 2, 4, 2),
                (S::GENERAL_PURPOSE, 2, 0, 2),
                (S::GENERAL_PURPOSE, 2, 3, 6),
                (S::GENERAL_PURPOSE, 2, 1, 6),
                (S::GENERAL_PURPOSE, 8, 2, 2),
                (S::GENERAL_PURPOSE, 1, 2, 8),
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
                (S::ENGINES, 2, 2, 0),
                (S::GENERAL_PURPOSE, 2, 4, 2),
                (S::GENERAL_PURPOSE, 2, 0, 2),
                (S::GENERAL_PURPOSE, 1, 3, 6),
                (S::GENERAL_PURPOSE, 1, 1, 6),
                (S::GENERAL_PURPOSE, 1, 2, 8),
                (S::GENERAL_PURPOSE, 3, 2, 2),
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

    fn hull(slug: &str) -> ShipHull {
        ship_hull_catalog()
            .into_iter()
            .find(|h| h.slug == slug)
            .unwrap()
    }

    #[test]
    fn slot_positions_are_unique_within_each_hull() {
        // Two slots sharing a grid cell would overlap in the designer render.
        for h in ship_hull_catalog() {
            let mut seen = std::collections::HashSet::new();
            for s in &h.slots {
                assert!(
                    seen.insert((s.position.row, s.position.col)),
                    "{} has two slots at ({}, {})",
                    h.name,
                    s.position.row,
                    s.position.col
                );
            }
        }
    }

    #[test]
    fn scout_slots_sit_in_one_row() {
        // Verified against the original Ship Designer: engine, general, scanner
        // in a horizontal row (half-box grid, so cols 0/2/4).
        let s = hull("scout");
        let pos: Vec<(u8, u8)> = s
            .slots
            .iter()
            .map(|s| (s.position.row, s.position.col))
            .collect();
        assert_eq!(pos, vec![(0, 0), (0, 2), (0, 4)]);
    }

    #[test]
    fn dreadnought_general_purpose_holds_two() {
        // Verified from the Tech Browser: "General Purpose up to 2", far right.
        let d = hull("dreadnought");
        assert_eq!(d.slots.len(), 13);
        let gp = d
            .slots
            .iter()
            .find(|s| s.slot_type == SlotType::GENERAL_PURPOSE)
            .unwrap();
        assert_eq!(gp.max_count, 2);
        assert_eq!((gp.position.row, gp.position.col), (3, 8));
    }

    #[test]
    fn maxi_miner_engine_holds_three() {
        // Verified from the Tech Browser: "Engine needs 3".
        let m = hull("maxi_miner");
        let eng = m
            .slots
            .iter()
            .find(|s| s.slot_type == SlotType::ENGINES)
            .unwrap();
        assert_eq!(eng.max_count, 3);
    }

    #[test]
    fn galleon_has_eight_slots_no_stray_electrical() {
        // Verified from the Tech Browser: 8 slots (the centre is a cargo hold,
        // not a slot); the real hull has no standalone Electrical slot.
        let g = hull("galleon");
        assert_eq!(g.slots.len(), 8);
        assert!(g.slots.iter().all(|s| s.slot_type != SlotType::ELECTRICAL));
        assert!(g
            .slots
            .iter()
            .any(|s| s.slot_type == SlotType::MINE_ELECT_MECH));
        assert!(g.slots.iter().any(|s| s.slot_type == SlotType::ELECT_MECH));
    }

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
