Race Design
===========

.. note::

   This document covers the **mathematical rules** governing race behaviour
   during play: PRT/LRT definitions, hab formulae, economy parameters, and
   point costs.

   For the new-game workflow — race file format, AI races, the race designer
   UI steps, and how races are submitted to the engine — see
   :doc:`../new_game/race_design_workflow` and
   :doc:`../new_game/race_file_format`.

Overview
--------

Every player controls a race they design before the game. The race designer
uses an **advantage point** budget: beneficial traits cost points, penalties
earn them. The final race must balance to zero (or within allowed range).

Primary Racial Traits (PRT)
----------------------------

Exactly one PRT must be chosen. Each fundamentally changes gameplay.

.. list-table::
   :header-rows: 1
   :widths: 5 30 50

   * - #
     - PRT
     - Key ability
   * - 0
     - Claim Adjuster (CA)
     - Terraforms cheaply; can total-terraform
   * - 1
     - Jack of All Trades (JOAT)
     - No special bonus; all-rounder
   * - 2
     - Interstellar Traveler (IT)
     - Builds cheap gates; gate without damage
   * - 3
     - Inner Strength (IS)
     - Shields regenerate 25%/round; bonus to colonist survival
   * - 4
     - Space Demolition (SD)
     - Minelayers; can detonate minefields
   * - 5
     - War Monger (WM)
     - Ships cost less; bonus to weapons
   * - 6
     - Packet Physics (PP)
     - Mineral packets as weapons; cheap mass drivers
   * - 7
     - Super Stealth (SS)
     - Cloaking; steal technology
   * - 8
     - Hyper Expansion (HE)
     - Double population growth rate; small maximum population
   * - 9
     - Alternate Reality (AR)
     - Lives in starbases; unique growth model

PRT Mechanical Details
~~~~~~~~~~~~~~~~~~~~~~

Key mechanical properties per PRT beyond the summary table above.

**Hyper Expansion (HE)**

- Growth rate in play is **double** the value set in the race designer (so a
  15% design rate → 30% effective maximum). The advantage points system prices
  this accordingly: a HE race at 15% costs the same as a non-HE race at 30%.
- Maximum planet population is **half** that of other races (planets are "small"
  for HE; effectively 50% of normal capacity).

**Super Stealth (SS)**

- Every ship has a **75% built-in cloak** (no design slot required).
- Unique scanners: **PickPocket** and **Robber Baron** can steal minerals from
  other players' planets or ships within scanner range.
- All ships and mineral packets have built-in cloaking.
- **Research bonus**: each turn, gains research equal to **½ the average spent
  in each tech field by all races** (including itself), as long as at least one
  other race exists.  This applies to whichever field SS is currently researching.
  (Community source: GameFAQs FAQ v1.11; oracle verification pending.)

**Interstellar Traveler (IT)**

- Starts with **tech level 5** in both **Propulsion** and **Construction** (all
  other PRTs start at level 3 in all fields, or level 4 for some).
- Builds stargates cheaply; can gate fleets without damage up to the gate's mass
  and distance limits.
- Stargates allow **scanning** of any enemy planet within gate range (reveals
  population and defenses).
- IT costs 57 advantage points — the most expensive PRT; 20 points more than
  the next most expensive.
- In Tiny universes, IT starts with only one planet despite normally receiving
  a secondary starting planet.

**War Monger (WM)**

- Exclusive ship hulls: **Battle Cruiser** and **Dreadnought** (stronger than
  any equivalently-available hull for other races).
- Exclusive weapons: **Gatling Neutrino Cannon** (effective minefield clearing)
  and **Blunderbuss** (highest-power beam weapon in the game, short range).
- Weapons cost less to build (cheap weapons).
- Ships are faster in combat (aggressive colonists, quicker engines?).

.. todo:: Confirm WM ship cost reduction and speed bonus exact values. See race_design.rst open questions.

**Space Demolition (SD)**

- Minefields act as **non-penetrating scanners**.  Cloaks work as an absolute
  percentage against mine scanning: a 75% cloaked ship has a 25% chance of
  detection per year inside a SD minefield.
- Own minefields decay at **1% per enclosed planet per year**; other races'
  minefields decay at **4% per enclosed planet per year**.  (Community source:
  GameFAQs FAQ v1.11; oracle verification pending.)
- Can **remotely detonate** their own standard minefields (damages all fleets
  in the field; SD mine layer hulls are immune to their own detonations).
- Learns the **exact design** of any enemy ship that hits a mine.
- Can **lay minefields while moving** (other races must be stationary to lay).
- Travel through **opposing** minefields at **2 warp factors higher** than the
  normal safe speed (e.g., safe at Warp 7 where others are safe at Warp 5).
- Exclusive hulls: **Mini Mine Layer** and **Super Mine Layer** — lay mines twice
  as efficiently and are immune to detonation of their own minefields.
- Exclusive bomb type: **Retrovirus** bomb spreads a genetic payload that causes
  population loss over the following 3 years (decreasing effect).

.. note:: *Sources: Stars! Strategy Guide, Chapter 2 and Appendices A–D (reviewed
   by original authors). Numeric specifics need oracle verification.*

Lesser Racial Traits (LRT)
---------------------------

Any combination may be chosen (some have prerequisites or conflicts).

.. note::

   Point costs shown here are for the default Humanoid race.  Actual costs vary
   slightly with growth rate and hab settings (TT's effective cost rises sharply
   with wider hab ranges; see Advantage Points section).

.. list-table::
   :header-rows: 1
   :widths: 35 45 20

   * - LRT
     - Effect
     - Cost
   * - No Ramscoop Engines (NRSE)
     - Cannot use ramscoop engines; gains IS-10 warp-10 engine (requires Prop 11)
     - earns points
   * - Cheap Engines (CE)
     - Engines cost 50% in resources and minerals; starting Propulsion +1; 10% chance fleet does not move each year at warp 7+
     - earns points
   * - Only Basic Remote Mining (OBRM)
     - Loses Robo-Miner, Robo-Maxi-Miner, Robo-Super-Miner robots and Maxi-Miner hull; maximum planet population +10%
     - earns points
   * - No Advanced Scanners (NAS)
     - Loses all penetrating scanners; standard scanner ranges doubled
     - earns points
   * - Low Starting Population (LSP)
     - Starting planets have 30% fewer colonists (70% of normal)
     - earns points
   * - Bleeding Edge Technology (BET)
     - Items cost ×2 until all tech requirements are exceeded by one level; miniaturization is 5%/level to 80% (vs. 4%/level to 75%)
     - earns points
   * - Regenerating Shields (RS)
     - Shields regenerate 10% of max strength per combat round; shield items 40% stronger; armor slabs 50% weaker
     - earns points
   * - Generalized Research (GR)
     - Only 50% of research resources apply to the current field; 15% goes to each of the five other fields (125% effective total)
     - earns points
   * - Improved Fuel Efficiency (IFE)
     - Grants Fuel Mizer engine (and Galaxy Scoop if not NRSE); all engines use 15% less fuel; starting Propulsion +1
     - costs points
   * - Total Terraforming (TT)
     - Terraforming costs only 70 resources per click (vs. 100); unlocks TT ±3, 5, 7, 10, 15, 20, 25, and 30 levels
     - costs points
   * - Advanced Remote Mining (ARM)
     - Grants Midget Miner, Miner, and Ultra-Miner hulls and Robo-Midget Miner and Robo-Ultra-Miner robots; starts with two Midget Miners
     - costs points
   * - Improved Starbases (ISB)
     - Grants Spacedock and Ultra Station hulls; all starbases cost 20% less and have built-in 20% cloak
     - costs points
   * - Ultimate Recycling (UR)
     - Ships scrapped at starbases yield 90% minerals and some resources; scrapping at planets yields 45% minerals
     - costs points
   * - Mineral Alchemy (MA)
     - Mineral Alchemy production costs only 25 resources per kT (vs. 100); converts resources into each mineral type
     - costs points

Habitat Ranges
--------------

Gravity
~~~~~~~

- Min: 0.12g, Max: 8.00g
- Step: 0.4 (in normalized 0–100 space: each click moves by ~1–2 positions)
- Immune: no gravity penalty ever; always counts as 10000 hab points

Temperature
~~~~~~~~~~~

- Min: −200°C, Max: +200°C, Step: 4°C
- **Minimum range width: 80°C** (enforced by race designer)
- Immune: always 10000 hab points

Radiation
~~~~~~~~~

- Min: 0 mR/yr, Max: 100 mR/yr, Step: 1
- Immune: always 10000 hab points

Economy Parameters
------------------

All parameters are set in the race designer and define the race's economic profile.

Resources per colonist
~~~~~~~~~~~~~~~~~~~~~~

- Parameter: ``resource_production`` (range 700–2500, step 100)
- Meaning: X colonists produce 1 resource per year
- Default: 1000
- Lower = more productive colonists

Factory production
~~~~~~~~~~~~~~~~~~

- Parameter: ``factory_production`` (range 5–15, step 1)
- Meaning: each factory produces X resources per year
- Default: 10

Factory cost
~~~~~~~~~~~~

- Parameter: ``factory_cost`` (range 5–25, step 1)
- Meaning: each factory costs X resources to build
- Default: 10
- Cheap germanium option: factories cost 3 germanium instead of 4 germanium ("costs one less")

Colonists that operate factories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Parameter: ``colonists_operate_factories`` (range 5–25, step 1)
- Meaning: X colonists per 10,000 can operate one factory
- Max factories on a planet = ``(population / 10,000) × colonists_operate_factories``

Mine production
~~~~~~~~~~~~~~~

- Parameter: ``mine_production`` (range 5–25, step 1)
- Meaning: each mine extracts X kT of each mineral per year (proportional to concentration)
- Default: 10

Mine cost
~~~~~~~~~

- Parameter: ``mine_cost`` (range 2–15, step 1)
- Meaning: each mine costs X resources to build
- Default: 5

Colonists that operate mines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Parameter: ``colonists_operate_mines`` (range 5–25, step 1)
- Meaning: X colonists per 10,000 can operate one mine
- Max mines on a planet = ``(population / 10,000) × colonists_operate_mines``

Growth rate
~~~~~~~~~~~

- Parameter: ``growth_rate`` (range 1–20%, step 1%)
- Meaning: maximum annual population growth rate
- Actual growth = ``min(growth_rate, planet_value) × capacity_factor``

Research Cost Options
---------------------

Each of the 6 tech fields can be set to Cheap, Normal, or Expensive.

- Cheap: 50% of base cost
- Normal: 100%
- Expensive: 175%

**Expensive Tech Boost:** If a field is set to Expensive, the race gets a
+1 starting level in that field (a slight headstart at the cost of ongoing expense).

.. note::

   Generalized Research (LRT) distributes excess research to other fields;
   this interacts with per-field cost settings.

Starting Population
-------------------

- Normal start: 25,000 colonists
- Accelerated BBS: ``25,000 + 5,000 × growth_rate_percent``
  — e.g., 15% GR → 100,000;  10% GR → 75,000;  20% GR → 125,000
- Low Starting Population LRT: 70% of the above (30% fewer colonists)

.. note::

   The base 25,000 is confirmed flat (``Consts.java`` from craigstars).
   The Accelerated BBS bonus scales with growth rate — confirmed by the Python
   engine (``turn.py``) and FreeStars source.  The shorthand "4× normal =
   100,000" is the 15%-growth-rate case, not a general multiplier.
   Oracle validation across multiple growth rates is pending (R2.1).

Advantage Points
----------------

The race designer enforces a point budget. Each trait has a cost/benefit that
adds or subtracts from the budget.

.. note::

   **Source:** The values below have been cross-verified against
   ``RacePointsCalculator.java`` from the `craigstars
   <https://github.com/nicholasolas/Stars->`_ open-source Stars! reimplementation.
   The internal algorithm accumulates **raw points** (starting at 1,650) from
   habitat range, growth rate, economy parameters, PRT flag, and LRT flags; the
   final result is integer-divided by 3.  Most LRT values in the table below
   match exactly to ``raw_value / 3``; exceptions are noted in the todo at the
   end of this section.

PRT point values
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 35 15

   * - Index
     - PRT
     - Points
   * - 0
     - Claim Adjuster (CA)
     - 0
   * - 1
     - Jack of All Trades (JOAT)
     - +25
   * - 2
     - Interstellar Traveler (IT)
     - −57
   * - 3
     - Inner Strength (IS)
     - +36
   * - 4
     - Space Demolition (SD)
     - +53
   * - 5
     - War Monger (WM)
     - −12
   * - 6
     - Packet Physics (PP)
     - −37
   * - 7
     - Super Stealth (SS)
     - −28
   * - 8
     - Hyper Expansion (HE)
     - −10
   * - 9
     - Alternate Reality (AR)
     - −27

LRT point values
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 20

   * - LRT
     - Points
   * - No Ramscoop Engines (NRSE)
     - +53
   * - Improved Fuel Efficiency (IFE)
     - −78
   * - Cheap Engines (CE)
     - +80
   * - Total Terraforming (TT)
     - −140
   * - Only Basic Remote Mining (OBRM)
     - +85
   * - Advanced Remote Mining (ARM)
     - −53
   * - No Advanced Scanners (NAS)
     - +95
   * - Improved Starbases (ISB)
     - −67
   * - Low Starting Population (LSP)
     - +60
   * - Generalized Research (GR)
     - +13
   * - Bleeding Edge Technology (BET)
     - +23
   * - Ultimate Recycling (UR)
     - −80
   * - Regenerating Shields (RS)
     - +10
   * - Mineral Alchemy (MA)
     - −51

Research cost modifier point values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Applied independently per tech field (6 fields × modifier):

- Expensive: +50 per field
- Normal: 0
- Cheap: −43 per field

**Expensive Tech Boost** (checkbox): +60 points flat (unlocks +1 starting
tech level in each Expensive field).

**Factory cheap germanium** (checkbox): −58 points flat.

Habitat point values
~~~~~~~~~~~~~~~~~~~~

Immune axes each cost points (beneficial):

- Each immune axis: −572 points
- Two immune axes (any combination): −586 additional modifier
- All three axes immune: −3925 total (not the sum of three individual
  immune values; tri-immunity is specially capped)

Non-immune habitat ranges contribute points through the following algorithm
(from ``RacePointsCalculator.java``, craigstars):

The calculation runs **3 outer loops** with a ``TTCorrectionFactor`` of
``{0, 5, 15}`` (or ``{0, 8, 17}`` if TT is selected).  Each loop samples
11 evenly-spaced points across the race's effective terraformable range for
each non-immune axis (1 point if immune).  For each sample combination the
**planet desirability** is the squared distance from the hab center (clamped
to 0–100), multiplied by a loop weight of ``{7, 5, 6}`` for the three outer
loops respectively.  Accumulated desirabilities are scaled by the effective
range width / 100 for non-immune axes, or × 11 for immune axes.  The final
``habPoints`` is the total divided by 10.

``habPoints`` then feeds the growth-rate penalty:
``points -= (habPoints × growthRateFactor) / 24``

This is why **TT's listed cost varies with hab range**: TT's raw flag cost
is only −25 raw (≈ −8 advantage points), but enabling TT expands the
effective terraformable range used in the hab sample loops, substantially
increasing ``habPoints`` and thus the growth-rate penalty.  The −140 value
shown for a Humanoid-range race is the NET effect; narrow-hab races pay
less for TT, wide-hab races pay more.

Economy parameter point values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Growth rate** (1–20%):

.. list-table::
   :header-rows: 1
   :widths: 15 15

   * - Growth %
     - Points
   * - 1
     - +7594
   * - 2
     - +6171
   * - 3
     - +4748
   * - 4
     - +3325
   * - 5
     - +1902
   * - 6
     - +1656
   * - 7
     - +1161
   * - 8
     - +565
   * - 9
     - +394
   * - 10
     - +274
   * - 11
     - +228
   * - 12
     - +182
   * - 13
     - +136
   * - 14
     - +68
   * - 15
     - 0
   * - 16
     - −69
   * - 17
     - −137
   * - 18
     - −206
   * - 19
     - −274
   * - 20
     - −412

**Resources per colonist** (colonists needed to produce 1 resource):

- 700: −800, 800: −420, 900: −200
- 1000+: ``floor(0.4 × cpr − 400)``  (e.g. 1000 → 0, 2500 → +600)

**Factory production** (resources per factory, 5–15):

.. list-table::
   :header-rows: 1
   :widths: 15 15

   * - Value
     - Points
   * - 5–9
     - +166 … +33 (step −33 approx)
   * - 10
     - 0
   * - 11
     - −42
   * - 12
     - −84
   * - 13
     - −145
   * - 14
     - −207
   * - 15
     - −268

**Factory cost** (resources to build one factory, 5–25):

- 5: −500, 6: −320, 7: −180, 8: −80, 9: −20
- 10+: ``18 × (cost − 10)``  (e.g. 10 → 0, 25 → +270)

**Colonists per factory** (colonists that operate one factory ÷10k, 5–25):
``−13 × (value − 10)``  (e.g. 10 → 0, 5 → +65, 25 → −195)

**Mine production** (kT extracted per mine per year, 5–25):

- ≤10: ``33 × (10 − value)``
- >10: ``−56 × (value − 10)``

**Mine cost** (resources per mine, 2–15):

Exact raw formula (``costPoints = 3 − mine_cost``, before the global ÷3):

- ``costPoints ≤ 0``: ``raw_contrib = costPoints × −65 + 80``
- ``costPoints > 0`` (mine_cost < 3): ``raw_contrib = −360``

Combined with the mine-production and colonists-per-mine terms before the
global ÷3 is applied; the doc's prior ``22 × (cost − 5)`` approximation was
close for mid-range values but diverges at the extremes.

**Colonists per mine** (colonists that operate one mine ÷10k, 5–25):

- ≤10: ``13 × (10 − value)``
- >10: ``−12 × (value − 10)``

.. note::

   **Verification status (cross-checked against craigstars source):**

   - **Most LRT costs confirmed** — IFE (−78), ARM (−53), ISB (−67), GR (+13),
     UR (−80), CE (+80), OBRM (+85), LSP (+60), BET (+23), RS (+10), MA (−51)
     all match ``raw / 3`` from the Java source within rounding.

   - **TT cost is range-dependent** — the raw TT flag cost is only −25 (≈ −8
     adv. pts.); the −140 figure is the net cost for a Humanoid-range race
     because TT's expanded terraforming window raises the hab-range component
     significantly.  See Habitat point values section above.

   - **NAS discrepancy** — the craigstars raw NAS cost is 325 (→ 108 adv.
     pts. after ÷3); this doc shows +95.  The source of the discrepancy is
     unresolved.  The craigstars code also applies *additional* NAS penalties
     for PP (−93 extra), SS (−67 extra), and JoaT (−13 extra) races.  Oracle
     test recommended to pin the baseline value.

   - **Mine cost formula** — the craigstars source uses exact coefficients
     (``costPoints × −65 + 80`` when ``costPoints ≤ 0``, ``−360`` otherwise)
     rather than the ``22 × (cost − 5)`` approximation used previously.
     For most values the approximation is within ±5 pts; mine cost = 2 has
     the largest deviation (−190 exact vs. −66 approximated).

LRT Interaction Notes
~~~~~~~~~~~~~~~~~~~~~

- **OBRM + ARM conflict:** Only Basic Remote Mining and Advanced Remote Mining
  cancel each other out. If both are selected, OBRM wins and ARM has no effect,
  wasting its cost. Never select both.
- **IFE + NRSE interaction:** IFE grants the Galaxy Scoop only when NRSE is *not*
  also selected.  Taking both is valid; you simply forgo the Galaxy Scoop.
- **CE + UR interaction:** If a CE player builds a mostly-engine ship and a UR
  player scraps it, the UR player can receive more minerals and resources than
  the CE player spent — a cooperative exploit in team games.
- **LRT count penalty:** After 4 lesser traits are selected, each additional LRT
  chosen *costs* advantage points rather than earning or spending at face value.
  Limit selections to 4 unless a 5th is critically necessary.

.. note:: *Sources: Stars! Strategy Guide Chapter 3; Walter D. Pullen,
   "Lesser Racial Traits" (1997, v2.6/7); Mahrin Skel, "Race Design, Step
   by Step" (1997, v2.6/7).*

Open Questions
--------------

.. todo:: CA terraforming rate and cost vs. normal terraforming

.. todo:: HE maximum population cap — strategy guide confirms it is 50% of
   normal (half max planet size); exact cap per planet size needs oracle verification.

.. todo:: AR growth model (lives in starbases; pop count different).
   GameFAQs FAQ v1.11 (plague006/Mars Jenkar, 2006) gives these formulas
   (community source; oracle verification needed):

   - **Scanner range**: ``sqrt(population / 10)`` light years (standard scan);
     Ultra Station / Death Star have penetrating scans at half this range.
   - **Resource generation**: ``hab_value × sqrt(pop × energy_TL / coeff)``
     where ``coeff`` is the single Page-5 efficiency slider (range 7–25, lower
     is better) and ``hab_value`` is 0.0–1.0.
   - **Mine generation** (auto-mining from orbit): ``sqrt(population) / 10``
     mines per year, which then mine the planet automatically.

   See ``stars-reborn-research/docs/findings/gamefaqs_faq_race_mechanics.rst``.

.. todo:: WM ship cost reduction: exact percentage? Speed bonus?
   GameFAQs FAQ v1.11 says: all **weapons** cost 25% less to build (not ships
   generally); battle movement bonus is **½ square per round**.  Community source
   only — oracle verification needed before closing this TODO.
   See ``stars-reborn-research/docs/findings/gamefaqs_faq_race_mechanics.rst``.

.. todo:: IT secondary starting planet — confirm it is absent in Tiny universes.
