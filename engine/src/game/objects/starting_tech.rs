// engine/src/game/objects/starting_tech.rs
//
// A race's starting technology levels at year 2400 (turn 1), computed from its
// PRT, LRTs, and research costs. New players begin here instead of all-zeros —
// and every turn-1 ship design is the optimal loadout the engine can build from
// *this* tech, so these levels are what make the starting designs faithful.
//
// The algorithm is the one documented and oracle-confirmed (130+ turn-1 `.m`
// files) in `docs/new_game/initial_state.rst` ("Starting Technology"):
//
//   1. base 0 in all six fields;
//   2. PRT tech minimums raise specific fields (take the max);
//   3. Expensive Tech Boost: when the race has the EB flag, every field whose
//      research cost is Expensive is raised to at least 3;
//   4. LRT propulsion bonus: IFE and CE each add +1 to Propulsion, applied last.

use super::player::TechLevels;
use super::race::{Lrt, Prt, Race, TechCost};

/// The six tech fields in `TechLevels` order: energy, weapons, propulsion,
/// construction, electronics, biotechnology.
type Fields = [u32; 6];

/// Compute a race's starting tech levels. See the module docs for the source.
pub fn starting_tech_levels(race: &Race) -> TechLevels {
    // 1. + 2. Base zero, raised to the PRT minimums.
    let mut t = prt_minimums(race.prt);

    // 3. Expensive Tech Boost: each Expensive-cost field is raised to >= 3.
    if race.research_costs.expensive_tech_boost {
        let rc = &race.research_costs;
        for (field, cost) in t.iter_mut().zip([
            &rc.energy,
            &rc.weapons,
            &rc.propulsion,
            &rc.construction,
            &rc.electronics,
            &rc.biotechnology,
        ]) {
            if matches!(cost, TechCost::Expensive) {
                *field = (*field).max(3);
            }
        }
    }

    // 4. LRT propulsion bonus: IFE and CE each add +1 (additive, applied last).
    let prop_bonus = race
        .lrts
        .iter()
        .filter(|l| matches!(l, Lrt::Ife | Lrt::Ce))
        .count() as u32;
    t[2] += prop_bonus;

    TechLevels {
        energy: t[0],
        weapons: t[1],
        propulsion: t[2],
        construction: t[3],
        electronics: t[4],
        biotechnology: t[5],
    }
}

/// PRT starting-tech minimums (energy, weapons, propulsion, construction,
/// electronics, biotechnology), oracle-confirmed per
/// `docs/new_game/initial_state.rst`.
///
/// The doc's table lists the PRT's observed minimums. For PP and AR every
/// observed corpus race also carries IFE, so the *base* propulsion here is one
/// below the doc's observed value (PP 3, AR 0): base + the universal IFE/CE
/// bonus (step 4) reproduces the observed PP=4 / AR=1. The doc flags this split
/// as unresolved; this is the only split consistent with the observed turn-1
/// data given the unconditional IFE/CE propulsion bonus. (No predefined race is
/// PP or AR, so this only affects custom races.)
fn prt_minimums(prt: Prt) -> Fields {
    // [energy, weapons, propulsion, construction, electronics, biotechnology]
    match prt {
        Prt::Joat => [3, 3, 3, 3, 3, 3],
        Prt::Ca => [0, 0, 0, 0, 0, 6],
        Prt::Ss => [0, 0, 0, 0, 5, 0],
        Prt::Pp => [4, 0, 3, 0, 0, 0],
        Prt::Ar => [1, 0, 0, 0, 0, 0],
        Prt::It => [0, 0, 5, 5, 0, 0],
        Prt::Wm => [1, 6, 1, 0, 0, 0],
        Prt::Sd => [0, 0, 3, 0, 0, 2],
        Prt::He | Prt::Is => [0, 0, 0, 0, 0, 0],
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::objects::race_defaults::default_race_by_name;

    /// A race with a chosen PRT + LRTs, all research costs Normal and EB off
    /// (so only steps 2 and 4 apply) — isolates the PRT/LRT contribution.
    fn race_with(prt: Prt, lrts: Vec<Lrt>) -> Race {
        let mut r = default_race_by_name("Humanoid").expect("Humanoid default");
        r.prt = prt;
        r.lrts = lrts;
        r
    }

    #[test]
    fn default_humanoid_is_joat_all_threes() {
        let t = starting_tech_levels(&default_race_by_name("Humanoid").unwrap());
        assert_eq!(
            (
                t.energy,
                t.weapons,
                t.propulsion,
                t.construction,
                t.electronics,
                t.biotechnology
            ),
            (3, 3, 3, 3, 3, 3)
        );
    }

    #[test]
    fn prt_minimums_match_the_doc_table() {
        let get = |prt| {
            let t = starting_tech_levels(&race_with(prt, vec![]));
            [
                t.energy,
                t.weapons,
                t.propulsion,
                t.construction,
                t.electronics,
                t.biotechnology,
            ]
        };
        assert_eq!(get(Prt::Joat), [3, 3, 3, 3, 3, 3]);
        assert_eq!(get(Prt::Ca), [0, 0, 0, 0, 0, 6]); // Biotech >= 6
        assert_eq!(get(Prt::Ss), [0, 0, 0, 0, 5, 0]); // Electronics >= 5
        assert_eq!(get(Prt::It), [0, 0, 5, 5, 0, 0]); // Propulsion, Construction >= 5
        assert_eq!(get(Prt::Wm), [1, 6, 1, 0, 0, 0]); // Weapons >= 6, Energy/Prop >= 1
        assert_eq!(get(Prt::Sd), [0, 0, 3, 0, 0, 2]); // Propulsion >= 3, Biotech >= 2
        assert_eq!(get(Prt::He), [0, 0, 0, 0, 0, 0]); // none
        assert_eq!(get(Prt::Is), [0, 0, 0, 0, 0, 0]); // none
    }

    #[test]
    fn ife_and_ce_each_add_one_propulsion() {
        // JOAT base prop 3; +IFE = 4; +IFE+CE = 5.
        assert_eq!(
            starting_tech_levels(&race_with(Prt::Joat, vec![Lrt::Ife])).propulsion,
            4
        );
        assert_eq!(
            starting_tech_levels(&race_with(Prt::Joat, vec![Lrt::Ife, Lrt::Ce])).propulsion,
            5
        );
    }

    #[test]
    fn pp_and_ar_with_ife_reproduce_observed_propulsion() {
        // Every observed corpus PP/AR race carries IFE; observed PP prop = 4,
        // AR prop = 1 (base 3/0 + IFE +1).
        let pp = starting_tech_levels(&race_with(Prt::Pp, vec![Lrt::Ife]));
        assert_eq!((pp.energy, pp.propulsion), (4, 4));
        let ar = starting_tech_levels(&race_with(Prt::Ar, vec![Lrt::Ife]));
        assert_eq!((ar.energy, ar.propulsion), (1, 1));
    }

    #[test]
    fn expensive_tech_boost_raises_expensive_fields_to_three() {
        let mut r = race_with(Prt::He, vec![]); // HE has no PRT minimums
        r.research_costs.expensive_tech_boost = true;
        r.research_costs.weapons = TechCost::Expensive;
        r.research_costs.energy = TechCost::Normal;
        let t = starting_tech_levels(&r);
        assert_eq!(t.weapons, 3, "Expensive weapons raised to 3 by EB");
        assert_eq!(t.energy, 0, "non-Expensive field untouched by EB");
    }
}
