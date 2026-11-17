// engine/src/game/objects/ship_cost.rs
//
// Server-side build cost of a stored ship/starbase design: the hull's cost plus
// each installed component's cost times its count. Mirrors the client's additive
// `DesignModel.total_cost`, computed here from the engine's own catalogs so the
// production queue spends the right minerals and resources. The caller supplies
// the catalogs (built once per turn) so this stays a pure sum.

use super::player::{ShipDesign, ShipDesignKind};
use super::technology::{ShipHull, StarbaseHull, TechCost};
use super::technology_catalog::TechItem;

const ZERO: TechCost = TechCost {
    ironium: 0,
    boranium: 0,
    germanium: 0,
    resources: 0,
};

/// `acc + unit * times`, saturating (a design cost never realistically overflows
/// u32, but a stray catalog value should not panic turn resolution).
fn add_scaled(acc: TechCost, unit: TechCost, times: u32) -> TechCost {
    TechCost {
        ironium: acc
            .ironium
            .saturating_add(unit.ironium.saturating_mul(times)),
        boranium: acc
            .boranium
            .saturating_add(unit.boranium.saturating_mul(times)),
        germanium: acc
            .germanium
            .saturating_add(unit.germanium.saturating_mul(times)),
        resources: acc
            .resources
            .saturating_add(unit.resources.saturating_mul(times)),
    }
}

/// BASE build cost of one unit of `design`: hull cost plus every installed
/// part's cost times its count. Returns `None` when the design's hull is not in
/// the catalog (an unknown/invalid design the caller must not build). An
/// installed part absent from the catalog contributes nothing — it cannot occur
/// for a design the engine validated.
///
/// NOT YET APPLIED — this is the unmodified catalog cost. The original game
/// adjusts a design's cost by the race's traits and tech level, none of which
/// this function sees yet (it takes neither the race nor its tech levels):
///   * components on a STARBASE hull cost 50% less than on a ship hull;
///   * WM weapons −25%, IS weapons +25%; CE engines −50%; IT stargates −25%;
///   * AR / ISB starbases −20% (non-cumulative);
///   * miniaturisation: −4%/level of tech above an item's requirement, cap
///     −75% (−5%/−80% with the Bleeding Edge trait, which also doubles a
///     not-yet-fully-researched item's cost).
///
/// Until a trait/tech-aware cost lands, production spends this base cost, which
/// over-charges most races. See the cost-modifier follow-up task.
pub fn design_cost(
    design: &ShipDesign,
    ship_hulls: &[ShipHull],
    starbase_hulls: &[StarbaseHull],
    parts: &[TechItem],
) -> Option<TechCost> {
    let hull_cost = match design.kind {
        ShipDesignKind::Ship => ship_hulls
            .iter()
            .find(|h| u32::from(h.id) == design.hull_id)
            .map(|h| h.cost),
        ShipDesignKind::Starbase => starbase_hulls
            .iter()
            .find(|h| u32::from(h.id) == design.hull_id)
            .map(|h| h.cost),
    }?;

    let mut total = add_scaled(ZERO, hull_cost, 1);
    for sa in &design.slot_assignments {
        if let Some(part) = parts.iter().find(|t| u32::from(t.id) == sa.part_id) {
            total = add_scaled(total, part.cost, sa.count.get());
        }
    }
    Some(total)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::objects::player::SlotAssignment;
    use crate::game::objects::ship_hull_catalog::ship_hull_catalog;
    use crate::game::objects::starbase_hull_catalog::starbase_hull_catalog;
    use crate::game::objects::technology_catalog::technology_catalog;
    use std::num::NonZeroU32;

    fn design(kind: ShipDesignKind, hull_id: u32, parts: Vec<(u32, u32)>) -> ShipDesign {
        ShipDesign {
            slot: 0,
            kind,
            name: "D".into(),
            hull_id,
            slot_assignments: parts
                .into_iter()
                .enumerate()
                .map(|(i, (part_id, count))| SlotAssignment {
                    slot_index: i as u32,
                    part_id,
                    count: NonZeroU32::new(count).unwrap(),
                })
                .collect(),
        }
    }

    #[test]
    fn empty_ship_design_costs_exactly_its_hull() {
        let hulls = ship_hull_catalog();
        let hull = &hulls[0];
        let d = design(ShipDesignKind::Ship, u32::from(hull.id), vec![]);
        let cost = design_cost(&d, &hulls, &starbase_hull_catalog(), &technology_catalog())
            .expect("known hull");
        assert_eq!(cost, hull.cost);
    }

    #[test]
    fn components_add_their_cost_times_count() {
        let hulls = ship_hull_catalog();
        let parts = technology_catalog();
        let hull = &hulls[0];
        let part = &parts[0];
        // Two of the first component on the first hull.
        let d = design(
            ShipDesignKind::Ship,
            u32::from(hull.id),
            vec![(u32::from(part.id), 2)],
        );
        let cost = design_cost(&d, &hulls, &starbase_hull_catalog(), &parts).expect("known hull");
        assert_eq!(cost.ironium, hull.cost.ironium + part.cost.ironium * 2);
        assert_eq!(cost.boranium, hull.cost.boranium + part.cost.boranium * 2);
        assert_eq!(
            cost.germanium,
            hull.cost.germanium + part.cost.germanium * 2
        );
        assert_eq!(
            cost.resources,
            hull.cost.resources + part.cost.resources * 2
        );
    }

    #[test]
    fn unknown_hull_has_no_cost() {
        let d = design(ShipDesignKind::Ship, 9999, vec![]);
        assert!(design_cost(
            &d,
            &ship_hull_catalog(),
            &starbase_hull_catalog(),
            &technology_catalog()
        )
        .is_none());
    }
}
