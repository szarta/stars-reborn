// Starbase hull catalog
//
// Static data for every starbase hull in the game. Values mirror the legacy
// Python engine (reference factory.py) and the design reference at
// docs/reference/starbase_hulls.rst, which is the authoritative source for the
// slot layouts (verified against the original game's Tech Browser hull view).
//
// Ids match the original game's technology ids (OrbitalFort=157 .. DeathStar=161),
// which sit just below the ship-hull ids (162+) in the shared tech-id space.
// Starbase hull ids are a parallel space to ship-hull ids (a design's `kind`
// disambiguates which catalog a hull-id indexes); keeping the canonical values
// avoids surprises when cross-referencing the original data.
//
// Slot order follows the legacy per-hull slot index (0..n) — the canonical
// slot-index a design references — and each slot carries its Ship Designer grid
// position from the reference doc. Grid unit = half a slot box; (row, col)
// origin at the top-left of each hull's box cluster, as for ship hulls. The
// central dock disc (max buildable ship mass) is not a slot.

use super::technology::{
    HullRequirement, SlotPosition, SlotType, StarbaseHull, TechCost, TechRequirements, TechSlot,
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

/// Returns the canonical, ordered starbase-hull catalog.
///
/// Order matches the original game's Ship Designer starbase picker: Orbital
/// Fort, Space Dock, Space Station, Ultra Station, Death Star. `dock_capacity`
/// `None` means unlimited (∞); `Some(0)` means the hull cannot build or repair
/// ships (Orbital Fort). Trait gates: Space Dock and Ultra Station need the ISB
/// LRT; Death Star needs the AR PRT.
pub fn starbase_hull_catalog() -> Vec<StarbaseHull> {
    use SlotType as S;
    vec![
        // ----- Orbital Fort — a cross; the centre is a slot -----
        StarbaseHull {
            id: 157,
            slug: "orbital_fort",
            name: "Orbital Fort",
            requirement: None,
            requirements: TechRequirements::NONE,
            cost: cost(12, 0, 17, 40),
            slots: slots(&[
                (S::WEAPONS, 12, 0, 2),
                (S::WEAPONS, 12, 4, 2),
                (S::PROTECTION, 12, 2, 0),
                (S::PROTECTION, 12, 2, 4),
                (S::ORBITAL_ELECT, 1, 2, 2),
            ]),
            armor: 100,
            initiative: 10,
            dock_capacity: Some(0),
        },
        // ----- Space Dock — an octagonal ring around the dock (ISB) -----
        StarbaseHull {
            id: 158,
            slug: "space_dock",
            name: "Space Dock",
            requirement: Some(HullRequirement::ISB),
            requirements: req(4),
            cost: cost(20, 5, 25, 100),
            slots: slots(&[
                (S::WEAPONS, 16, 0, 3),
                (S::WEAPONS, 16, 3, 6),
                (S::WEAPONS, 16, 5, 1),
                (S::ELECTRICAL, 2, 1, 5),
                (S::ELECTRICAL, 2, 5, 5),
                (S::SHIELDS, 24, 6, 3),
                (S::PROTECTION, 24, 3, 0),
                (S::ORBITAL_ELECT, 1, 1, 1),
            ]),
            armor: 250,
            initiative: 12,
            dock_capacity: Some(200),
        },
        // ----- Space Station — a staggered cross (∞ dock) -----
        StarbaseHull {
            id: 159,
            slug: "space_station",
            name: "Space Station",
            requirement: None,
            requirements: TechRequirements::NONE,
            cost: cost(120, 80, 250, 600),
            slots: slots(&[
                (S::WEAPONS, 16, 0, 5),
                (S::WEAPONS, 16, 3, 0),
                (S::WEAPONS, 16, 5, 8),
                (S::WEAPONS, 16, 8, 3),
                (S::SHIELDS, 16, 0, 3),
                (S::SHIELDS, 16, 8, 5),
                (S::PROTECTION, 16, 3, 8),
                (S::PROTECTION, 16, 5, 0),
                (S::ELECTRICAL, 3, 2, 4),
                (S::ELECTRICAL, 3, 6, 4),
                (S::ORBITAL_ELECT, 1, 4, 2),
                (S::ORBITAL_ELECT, 1, 4, 6),
            ]),
            armor: 500,
            initiative: 14,
            dock_capacity: None,
        },
        // ----- Ultra Station — a staggered cross (∞ dock, ISB) -----
        StarbaseHull {
            id: 160,
            slug: "ultra_station",
            name: "Ultra Station",
            requirement: Some(HullRequirement::ISB),
            requirements: req(12),
            cost: cost(120, 80, 300, 600),
            slots: slots(&[
                (S::WEAPONS, 16, 0, 3),
                (S::WEAPONS, 16, 3, 0),
                (S::WEAPONS, 16, 3, 8),
                (S::WEAPONS, 16, 5, 0),
                (S::WEAPONS, 16, 5, 8),
                (S::WEAPONS, 16, 8, 5),
                (S::ELECTRICAL, 3, 0, 5),
                (S::ELECTRICAL, 3, 4, 2),
                (S::ELECTRICAL, 3, 4, 6),
                (S::ELECTRICAL, 3, 8, 3),
                (S::SHIELDS, 20, 2, 6),
                (S::SHIELDS, 20, 6, 2),
                (S::PROTECTION, 20, 2, 2),
                (S::PROTECTION, 20, 6, 6),
                (S::ORBITAL_ELECT, 1, 2, 4),
                (S::ORBITAL_ELECT, 1, 6, 4),
            ]),
            armor: 1000,
            initiative: 16,
            dock_capacity: None,
        },
        // ----- Death Star — a pinwheel (∞ dock, AR) -----
        StarbaseHull {
            id: 161,
            slug: "death_star",
            name: "Death Star",
            requirement: Some(HullRequirement::AR),
            requirements: req(17),
            cost: cost(120, 80, 350, 750),
            slots: slots(&[
                (S::WEAPONS, 32, 0, 2),
                (S::WEAPONS, 32, 2, 8),
                (S::WEAPONS, 32, 6, 0),
                (S::WEAPONS, 32, 8, 6),
                (S::ELECTRICAL, 4, 0, 6),
                (S::ELECTRICAL, 4, 2, 0),
                (S::ELECTRICAL, 4, 4, 1),
                (S::ELECTRICAL, 4, 4, 7),
                (S::ELECTRICAL, 4, 6, 8),
                (S::ELECTRICAL, 4, 8, 2),
                (S::SHIELDS, 30, 2, 6),
                (S::SHIELDS, 30, 6, 2),
                (S::PROTECTION, 20, 2, 2),
                (S::PROTECTION, 20, 6, 6),
                (S::ORBITAL_ELECT, 1, 1, 4),
                (S::ORBITAL_ELECT, 1, 7, 4),
            ]),
            armor: 1500,
            initiative: 18,
            dock_capacity: None,
        },
    ]
}
