// engine/src/game/objects/buildable.rs
//
// The buildable registry: the engine's canonical, flat `build_object_id` space
// and the single source of truth that bridges the two representations of a
// production-queue item:
//
//   * the SEMANTIC order form a client submits — `production_item.item.kind`
//     in schemas/request-submit-orders.json (`factory`, `mine`, `design` + a
//     slot, …); and
//   * the NUMERIC `build_object_id` the host stores in the build queue
//     (schemas/game-state.json planet-state.build_queue) and surfaces in the
//     per-player turn file.
//
// Clients read this registry from `GET /model/buildables` so they never
// hardcode the mapping (ADR: clients read the data model from /model/).
//
// Ids 7/8/9 match the original game's Type-29 `item_id` for Factory/Mine/
// Defenses (docs/orders/x_file_format.rst, item_type 2). The remaining
// installation/auto ids are engine-assigned; ship/starbase designs live in a
// high block (`DESIGN_ID_BASE + slot`) mirroring the original's separate
// item_type 4 (custom design slot). The scheme is documented in
// docs/mechanics/production.rst (Buildable Registry).

/// Category of a buildable, as surfaced to clients.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Category {
    /// A one-off installation (factory, mine, defenses, alchemy).
    Installation,
    /// An auto-build item that repeats until a limit is reached.
    Auto,
    /// A ship or starbase built from one of the player's design slots.
    ShipDesign,
}

impl Category {
    /// Stable kebab-case slug used on the wire.
    pub fn slug(self) -> &'static str {
        match self {
            Category::Installation => "installation",
            Category::Auto => "auto",
            Category::ShipDesign => "ship-design",
        }
    }
}

/// A fixed (game-independent) buildable: everything except per-player designs.
#[derive(Debug, Clone, Copy)]
pub struct Buildable {
    /// Flat `build_object_id`.
    pub id: u32,
    /// Semantic kind slug — matches `production_item.item.kind` in the order
    /// schema (e.g. `factory`, `auto_max_mines`).
    pub kind: &'static str,
    /// Human-facing display name.
    pub name: &'static str,
    pub category: Category,
}

/// Base id for ship/starbase design slots: slot `N` builds as `DESIGN_ID_BASE + N`.
/// Well clear of the installation/auto block so the two never collide.
pub const DESIGN_ID_BASE: u32 = 1024;

/// Number of custom design slots a player has (original game: 16 ship + 10
/// starbase; the registry enumerates the 16-slot ship range the Ship Designer
/// exposes today — starbase slots fold in when the designer gains them).
pub const DESIGN_SLOTS: u32 = 16;

/// The fixed buildables, in canonical registry order. Ids 7/8/9 are faithful
/// to the original Type-29 item_id values; the rest are engine-assigned.
pub const FIXED_BUILDABLES: &[Buildable] = &[
    Buildable {
        id: 7,
        kind: "factory",
        name: "Factory",
        category: Category::Installation,
    },
    Buildable {
        id: 8,
        kind: "mine",
        name: "Mine",
        category: Category::Installation,
    },
    Buildable {
        id: 9,
        kind: "defenses",
        name: "Defenses",
        category: Category::Installation,
    },
    Buildable {
        id: 10,
        kind: "alchemy",
        name: "Mineral Alchemy",
        category: Category::Installation,
    },
    Buildable {
        id: 20,
        kind: "auto_factory",
        name: "Auto Factories",
        category: Category::Auto,
    },
    Buildable {
        id: 21,
        kind: "auto_mine",
        name: "Auto Mines",
        category: Category::Auto,
    },
    Buildable {
        id: 22,
        kind: "auto_defenses",
        name: "Auto Defenses",
        category: Category::Auto,
    },
    Buildable {
        id: 23,
        kind: "auto_alchemy",
        name: "Auto Mineral Alchemy",
        category: Category::Auto,
    },
    Buildable {
        id: 24,
        kind: "auto_min_terraform",
        name: "Auto Minimum Terraform",
        category: Category::Auto,
    },
    Buildable {
        id: 25,
        kind: "auto_max_terraform",
        name: "Auto Maximum Terraform",
        category: Category::Auto,
    },
    Buildable {
        id: 26,
        kind: "auto_max_factories",
        name: "Auto Maximum Factories",
        category: Category::Auto,
    },
    Buildable {
        id: 27,
        kind: "auto_max_mines",
        name: "Auto Maximum Mines",
        category: Category::Auto,
    },
];

/// Resolve a design slot to its `build_object_id`. Returns `None` if the slot
/// is outside the valid range.
pub fn design_build_object_id(slot: u32) -> Option<u32> {
    (slot < DESIGN_SLOTS).then_some(DESIGN_ID_BASE + slot)
}

/// If `id` is a design-slot buildable, return its slot index.
pub fn design_slot_of(id: u32) -> Option<u32> {
    if (DESIGN_ID_BASE..DESIGN_ID_BASE + DESIGN_SLOTS).contains(&id) {
        Some(id - DESIGN_ID_BASE)
    } else {
        None
    }
}

/// Look up a fixed buildable by its semantic kind slug.
pub fn fixed_by_kind(kind: &str) -> Option<&'static Buildable> {
    FIXED_BUILDABLES.iter().find(|b| b.kind == kind)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn core_installations_match_original_item_ids() {
        // Faithful to Stars! Type-29 item_type 2 (docs/orders/x_file_format.rst).
        assert_eq!(fixed_by_kind("factory").unwrap().id, 7);
        assert_eq!(fixed_by_kind("mine").unwrap().id, 8);
        assert_eq!(fixed_by_kind("defenses").unwrap().id, 9);
    }

    #[test]
    fn ids_are_unique_and_clear_of_the_design_block() {
        let mut ids: Vec<u32> = FIXED_BUILDABLES.iter().map(|b| b.id).collect();
        let n = ids.len();
        ids.sort_unstable();
        ids.dedup();
        assert_eq!(ids.len(), n, "fixed buildable ids must be unique");
        assert!(
            ids.iter().all(|&id| id < DESIGN_ID_BASE),
            "fixed ids must not collide with the design-slot block"
        );
    }

    #[test]
    fn design_ids_round_trip() {
        assert_eq!(design_build_object_id(0), Some(DESIGN_ID_BASE));
        assert_eq!(design_build_object_id(15), Some(DESIGN_ID_BASE + 15));
        assert_eq!(design_build_object_id(16), None);
        assert_eq!(design_slot_of(DESIGN_ID_BASE + 3), Some(3));
        assert_eq!(design_slot_of(9), None);
    }
}
