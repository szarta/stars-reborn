Race Design
===========

The Race Designer is used to create a custom race before starting a new game. Each choice
costs or earns **advantage points**; your total must stay within a fixed budget (typically 0
or fewer remaining points at game start).

Habitability
------------

Three environmental axes define which planets your race can colonize:

* **Gravity** — 0.12g to 8.00g (maps to 0–100 scale; midpoint 1.00g = 50)
* **Temperature** — -200°C to +200°C (maps to 0–100 scale; midpoint 0°C = 50)
* **Radiation** — 0 mR/yr to 100 mR/yr (maps to 0–100 scale; midpoint 50 mR/yr = 50)

For each axis you set a minimum and maximum (or mark it as **Immune**, meaning the race
can inhabit any value). Narrower ranges cost fewer points; wider ranges or immunity cost more.

A planet's **value** to your race is calculated from how close each axis is to the center of
your range (100% at the midpoint, 0% at the edge of tolerance, negative beyond).

.. note::

   The race editor UI works in **display units** (g, °C, mR/yr).  Before any hab
   calculation — and almost certainly before values are written to the race file —
   display values are normalized to a 0–100 internal integer scale.  Gravity uses
   a non-linear lookup table; temperature uses a linear formula; radiation is 1:1.
   See :doc:`../mechanics/habitability` for the complete ``Gravity_Map`` and the
   discussion of race file encoding.

Primary Racial Trait (PRT)
--------------------------

Every race has exactly one PRT. The PRT defines fundamental abilities and tech access.

.. list-table::
   :header-rows: 1
   :widths: 10 20 70

   * - Code
     - Name
     - Description
   * - JOAT
     - Jack of All Trades
     - No specialty. Gets free tech bonuses across the board; can build any ship type.
   * - HE
     - Hyper Expansion
     - Double colonist growth rate; can colonize with pop packets fired from mass drivers.
   * - SS
     - Super Stealth
     - Cloaking devices; built-in scanner/cloak on ships; steal tech from enemies.
   * - WM
     - War Monger
     - Best weapons tech discounts; built-in battle computers; ramscoops.
   * - CA
     - Claim Adjuster
     - Terraforming technology; can terraform all axes regardless of race hab.
   * - IS
     - Interstellar Traveler
     - Stargates built-in; regenerating shields in combat.
   * - SD
     - Space Demolition
     - Mine-laying specialists; retroviruses in bombing.
   * - PP
     - Packet Physics
     - Mass driver specialists; auto-terraforming via packet bombardment.
   * - IT
     - Interstellar Traveler (alt)
     - Long-range stargates; can exceed normal stargate mass limits.
   * - AR
     - Artifact Reality
     - Population lives in starbases, not on planets; no conventional colonization.

Lesser Racial Traits (LRT)
--------------------------

LRTs are optional modifiers that stack on top of your PRT. Each costs (positive points)
or earns (negative points, i.e. a disadvantage) advantage points.

Key LRTs:

* **IFE** — Improved Fuel Efficiency: ramscoop engines more efficient.
* **TT** — Total Terraforming: terraform all axes regardless of race preferences.
* **ARM** — Advanced Remote Mining: better remote mining robots.
* **ISB** — Improved Starbases: cheaper and stronger starbases.
* **GR** — Generalized Research: research costs are averaged (no cheap/expensive fields).
* **UR** — Ultimate Recycling: recycle ships back into minerals efficiently.
* **NAS** — No Advanced Scanners: no access to penetrating scanners (saves points).
* **OBRM** — Only Basic Remote Mining: no advanced mining robots (saves points).
* **CE** — Cheap Engines: all engines cost less.
* **NRSE** — No Ram Scoop Engines: cannot use ramscoop engines (saves points).
* **BET** — Bleeding Edge Technology: can use tech one level above what's been researched.
* **RS** — Regenerating Shields: shields regenerate in combat.
* **MA** — Mineral Alchemy: convert resources into minerals.

Production Parameters
---------------------

Adjust your race's production efficiency:

* **Resources per colonist** (per 10,000): 5–25 resources/year per 10k pop
* **Factory output**: 5–15 resources per factory per year
* **Factory cost**: 7–25 resources to build a factory (lower is better)
* **Colonists per factory**: 5–25 (how many colonists operate one factory)
* **Mine output**: 5–25 kT minerals per mine per year
* **Mine cost**: 2–15 resources to build a mine
* **Colonists per mine**: 2–25 (how many colonists operate one mine)
* **Growth rate**: 1%–20% per year (rate at which population grows on ideal planets)

Research Costs
--------------

For each of the six tech fields, set cost to:

* **Normal** — baseline cost
* **Cheap** — 50% of normal cost
* **Expensive** — 175% of normal cost

One field may also be set to **Expensive** as a disadvantage to earn extra points.
