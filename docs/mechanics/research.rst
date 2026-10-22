Research
========

Tech Fields
-----------

|original| has six technology fields. Each has independent levels (0–26).

.. list-table::
   :header-rows: 1
   :widths: 25 60

   * - Field
     - Controls
   * - Energy
     - Shields, capacitors, gates, terraforming, antimatter generators
   * - Weapons
     - Beams, missiles/torpedoes, bombs
   * - Propulsion
     - Engines, fuel efficiency, warp speed
   * - Construction
     - Hulls, armor, mine layers, mining hulls, starbases
   * - Electronics
     - Scanners, jammers, battle computers, cloaking
   * - Biotechnology
     - Terraforming, population growth, hab expansion

Research Allocation
-------------------

Each year, the player allocates a percentage of total planetary resources to
research. This percentage is then distributed across fields according to the
player's allocation sliders.

Only one field is the "current" primary research target. All resources allocated
to research go to that field. The remaining fields advance when the primary field
gains a level (see Generalized Research LRT).

Only one field receives research resources at a time. Switching fields at any
time is allowed; **accumulated progress is retained** when switching — points
already spent in a field are not lost. A "next field" queue entry can be set
to automatically switch when the current field levels up.

.. todo:: Confirm whether multiple simultaneous field research is ever possible.

Tech Level Costs
----------------

Research cost to advance from level N to level N+1:

.. code-block:: text

   cost = (BaseCost[N + 1] + total_all_levels × 10) × (cost_percent / 100)

   × 2 if the game option "Slower Tech Advances" is enabled

Where:

- ``BaseCost[N+1]`` — a fixed table of base costs (see below)
- ``total_all_levels`` — sum of the player's current levels in all 6 fields
- ``cost_percent`` — 50 (Cheap), 100 (Normal), or 175 (Expensive)

Base cost table (index = level being reached):

.. code-block:: text

   Reach  1:    50     Reach  2:    80     Reach  3:   130
   Reach  4:   210     Reach  5:   340     Reach  6:   550
   Reach  7:   890     Reach  8:  1440     Reach  9:  2330
   Reach 10:  3770     Reach 11:  6100     Reach 12:  9870
   Reach 13: 13850     Reach 14: 18040     Reach 15: 22440
   Reach 16: 27050     Reach 17: 31870     Reach 18: 36900
   Reach 19: 42140     Reach 20: 47590     Reach 21: 53250
   Reach 22: 59120     Reach 23: 65200     Reach 24: 71490
   Reach 25: 77990     Reach 26: 84700

Example: Advancing Weapons from level 5 to 6, total race tech currently at 15:

.. code-block:: text

   base = BaseCost[6] = 550
   penalty = 15 × 10 = 150
   Normal:    (550 + 150) × 1.00 =  700 resources
   Cheap:     (550 + 150) × 0.50 =  350 resources
   Expensive: (550 + 150) × 1.75 = 1225 resources

*Source: original Python engine (src/model/player.py), citing SAH wiki
"Guts of research costs" and Posey's Spreadsheet.*

.. todo:: Oracle-validate: confirm total_all_levels × 10 penalty by observing
   costs at different total tech levels in the original game.

Miniaturization
---------------

Tech items become cheaper to build as your tech level surpasses their
minimum tech requirement. This is called **miniaturization**.

Formula:

.. code-block:: text

   miniaturized_cost = base_cost × max(0.25, 1.0 - 0.04 × (tech_level - required_level))

- 4% cheaper per tech level above requirement
- Minimum cost: 25% of base cost (at 18+ levels above requirement)

.. todo:: Verify exact miniaturization formula and cap.

Bleeding Edge Technology (BET LRT)
------------------------------------

Races with BET pay ×2 to **build** any tech item at the moment it is first
unlocked (when the player's tech level exactly meets the item's requirements).

The penalty drops to normal once the player **exceeds all tech requirements**
for that item by at least 1 level.

BET races also get slightly better miniaturization overall:

- BET: **5% cost reduction per level above requirement**, minimum 20% of base cost
- Non-BET: 4% per level, minimum 25% of base cost

*Source: Stars! in-game help, Bleeding Edge Technology section.*

Generalized Research (GR LRT)
------------------------------

GR races distribute research resources as follows:

- **50%** of the research budget goes to the current primary field
- **15%** goes to each of the other 5 fields (= 75% total to other fields)
- Grand total: 125% of the budget (the game intentionally gives GR races a bonus)

This makes advancement more uniform; the primary field advances slower but
all others advance steadily without player attention.

*Source: Stars! in-game help, Generalized Research section.*

Starting Tech Levels
--------------------

All races start at level 0 in all fields, modified by:

- **PRT minimums** — see ``docs/new_game/initial_state.rst`` (IT: Prop/Con ≥ 5;
  JOAT: all ≥ 3; WM: Weapons ≥ 6; CA: Bio ≥ 6; etc.)
- **IFE or CE LRT** — each adds +1 to Propulsion after all PRT minimums are applied
- **Expensive Tech Boost flag** — raises every field set to Expensive to
  max(current, 3)

*Source: original Python engine (src/model/player.py).  IT/JOAT oracle-confirmed
2026-04-14; WM/SD/CA/PP need oracle.*

Technology Items
----------------

All technology items (engines, weapons, shields, scanners, etc.) have:

- A name and ID
- Minimum tech levels required (one per field; all must be met)
- Build cost (resources + minerals)
- Stats (depends on type)

The full technology tree is in ``schemas/tech.json``.

Open Questions
--------------

.. todo:: Oracle-validate the tech level cost formula — specifically the
   ``total_all_levels × 10`` penalty term (need to observe actual costs at
   varying total tech levels in the original game).

.. todo:: Exact miniaturization formula — current formula is from Python engine;
   confirm rounding, multi-field requirement overlevel logic, and BET 2× penalty
   via oracle.

.. todo:: GR distribution formula — 50%/15%/125% confirmed from Pullen web source;
   verify engine implementation matches (does GR actually give a 25% resource bonus?).

.. todo:: Maximum tech level — 26 in base cost table and item requirements;
   confirm no item requires level 27+ in any field.


.. _stars-reborn-impl:

Implementation Notes (from stars-reborn)
----------------------------------------

Six independent research fields:
* **Energy** — shields, stargates, scanners, capacitors
* **Weapons** — beam weapons, torpedoes, missiles, bombs
* **Propulsion** — engines, fuel efficiency
* **Construction** — hulls, armor, mass drivers
* **Electronics** — scanners, computers, jammers
* **Biotechnology** — terraforming, genetic tech
Annual Research Budget
----------------------
The player sets a research budget as a percentage of annual resources (0–100%).
Remaining resources go to production queues.
Budget is divided among tech fields per allocation weights (the player sets which
fields receive focus).
    research_resources_for_field = total_research_budget * field_weight / total_weight
Tech Level Costs
----------------
Base cost to advance from level N to level N+1:
    base_cost = TechnologyLevelBaseCosts[field][level]

Adjusted for race modifier:
* **Cheap**: ``adjusted = floor(base_cost * 0.5)``
* **Normal**: ``adjusted = base_cost``
* **Expensive**: ``adjusted = floor(base_cost * 1.75)``
GR (Generalized Research) LRT averages costs across all fields.
As tech levels advance, the cost to build technologies that require that tech
decreases (miniaturization):
    For a technology requiring level N in field F:
    current_level = player's tech level in F
    miniaturization = max(0, current_level - N) * 4%
    effective_cost = floor(base_cost * (1 - miniaturization))
Maximum miniaturization: 75% reduction.
BET (Bleeding Edge Technology) LRT allows using technologies one level before
they're normally available, but at 4× the normal cost.
