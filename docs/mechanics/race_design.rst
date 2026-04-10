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
- Starting tech bonus: receives a small spying bonus enabling easier technology
  acquisition from other races.

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

- Minefields act as **scanners** (SD can see through its own minefields).
- Own minefields decay **slower** than normal.
- Can **detonate** their own minefields at will (inflicts mine damage on all
  fleets in the field).
- Can **lay minefields while moving** (other races must be stationary to lay).
- Travel through **opposing** minefields at approximately **2 warp factors higher**
  than the normal safe speed (e.g., safe at Warp 7 where others are safe at Warp 5).
- Exclusive hulls: **Mini Mine Layer** and **Super Mine Layer** — lay mines twice
  as efficiently and are immune to detonation of their own minefields.
- Exclusive bomb type: **Retrovirus** bomb spreads a genetic payload that causes
  population loss over the following 3 years (decreasing effect).

.. note:: *Sources: Stars! Strategy Guide, Chapter 2 and Appendices A–D (reviewed
   by original authors). Numeric specifics need oracle verification.*

Lesser Racial Traits (LRT)
---------------------------

Any combination may be chosen (some have prerequisites or conflicts).

.. list-table::
   :header-rows: 1
   :widths: 35 45 20

   * - LRT
     - Effect
     - Cost
   * - No Ramscoop Engines (NRE)
     - Cannot use ramscoop engines
     - earns points
   * - Cheap Engines (CE)
     - Engines cost 75%
     - earns points
   * - Only Basic Remote Mining (OBRM)
     - Cannot use advanced mining hulls
     - earns points
   * - No Advanced Scanners (NAS)
     - No penetrating scanners
     - earns points
   * - Low Starting Population (LSP)
     - Start with 70% of normal pop (30% fewer colonists)
     - earns points
   * - Bleeding Edge Technology (BET)
     - New tech items cost ×2 at level+1
     - earns points
   * - Regenerating Shields (RS)
     - +IS-like shield regen (partial)
     - costs points
   * - Improved Fuel Efficiency (IFE)
     - Engines use 15% less fuel
     - costs points
   * - Total Terraforming (TT)
     - Can terraform any axis
     - costs points
   * - Advanced Remote Mining (ARM)
     - Better remote mining hulls
     - costs points
   * - Improved Starbases (ISB)
     - Starbases get bonus armor/shields
     - costs points
   * - Generalized Research (GR)
     - Research benefits all fields equally
     - costs points
   * - Ultimate Recycling (UR)
     - Scrap ships returns 90% minerals
     - costs points
   * - Mineral Alchemy (MA)
     - Can convert resources to minerals
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
- Cheap germanium option: factories cost 1 germanium instead of 4 germanium

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
- Accelerated BBS: 4× normal
- Low Starting Population LRT: 17.5% of normal

.. todo::

   Verify exact starting pop formula — some sources suggest
   ``5,000 × growth_rate`` (so 10% GR → 75,000) rather than a flat 25,000.

Advantage Points
----------------

The race designer enforces a point budget. Each trait has a cost/benefit that
adds or subtracts from the budget. The values below are sourced from the
Python reference engine (``parameters/race.py``, ``objects/race.py``); all
require oracle verification against ``stars.exe``.

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
   * - No Ramscoop Engines (NRE)
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

Non-immune habitat ranges contribute points based on range width and
position; the formula is complex and requires oracle verification.

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

- 2: −190, others: ``22 × (cost − 5)``  (e.g. 5 → 0, 2 → −66, 15 → +220)

**Colonists per mine** (colonists that operate one mine ÷10k, 5–25):

- ≤10: ``13 × (10 − value)``
- >10: ``−12 × (value − 10)``

.. todo::

   Oracle-verify all advantage point values above. The Python reference
   engine notes "slight deviations" in some mine cost values (21 vs. 22)
   and used an approximation.

LRT Interaction Notes
~~~~~~~~~~~~~~~~~~~~~

- **OBRM + ARM conflict:** Only Basic Remote Mining and Advanced Remote Mining
  cancel each other out. If both are selected, OBRM wins and ARM has no effect,
  wasting its cost. Never select both.
- **LRT count penalty:** After 4 lesser traits are selected, each additional LRT
  chosen *costs* advantage points rather than earning or spending at face value.
  Limit selections to 4 unless a 5th is critically necessary.

.. note:: *Source: Stars! Strategy Guide, Chapter 3.*

Open Questions
--------------

.. todo:: Exact starting population formula (simple vs. growth_rate-dependent)

.. todo:: CA terraforming rate and cost vs. normal terraforming

.. todo:: HE maximum population cap — strategy guide confirms it is 50% of
   normal (half max planet size); exact cap per planet size needs oracle verification.

.. todo:: AR growth model (lives in starbases; pop count different)

.. todo:: WM ship cost reduction: exact percentage? Speed bonus?

.. todo:: IT secondary starting planet — confirm it is absent in Tiny universes.
