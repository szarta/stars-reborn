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
     - Built-in penetrating scanners on all ships; slightly larger planet capacity; no specialty bonus or penalty.
   * - HE
     - Hyper Expansion
     - Double population growth rate; maximum planet population is half that of other races.
   * - SS
     - Super Stealth
     - All ships 75% cloaked; PickPocket and Robber Baron scanners steal minerals; tech theft.
   * - WM
     - War Monger
     - Weapons cost less; exclusive Battle Cruiser and Dreadnought hulls; higher starting weapons tech.
   * - CA
     - Claim Adjuster
     - Auto-terraforms planets toward race hab preferences; can total-terraform any axis.
   * - IS
     - Inner Strength
     - Shields regenerate 25% per combat round; colonists grow while traveling in ships; bonus ground combat defense.
   * - SD
     - Space Demolition
     - Mine-laying specialists; minefields act as scanners; can detonate own minefields; retroviruses in bombing.
   * - PP
     - Packet Physics
     - Mass driver specialists; cheap mineral packets as weapons and scanners; auto-terraforming via packet bombardment.
   * - IT
     - Interstellar Traveler
     - Builds stargates cheaply; gates fleets without mass-limit damage; stargates scan enemy planets; starts Prop 5 / Construction 5.
   * - AR
     - Alternate Reality
     - Population lives in starbases; resource generation scales with orbital population; no planetary colonization.

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

Race Archetypes
---------------

Community-established design philosophies for competitive play.  Every race
should be designed around one of these themes rather than hedging between them.

**HP — Hyper-Production**
   Maximise long-term resource output. Narrow habitat (1-in-6 to 1-in-10),
   typically Total Terraforming, slower growth rate (16–17%), Advanced Remote
   Mining, and high factory settings. Needs time to ramp up; vulnerable early.
   Typical factory settings: 15 factories / cost 9 / 25 per 10k colonists.

**HG — Hyper-Growth**
   Maximise expansion speed. Wider habitat (1-in-4 to 1-in-6), Only Basic
   Remote Mining, high growth rate (18–19%), moderate factory settings. Target
   benchmark: 25 000 resources by year 2450 in a test bed (no AI, Accelerated
   BBS, maximum minerals, small packed universe).
   Typical factory settings: 11–13 factories / cost 8–9 / 14–17 per 10k colonists.

**Hybrid**
   Mix of HG and HP. Best hybrids use HG habitat and growth settings combined
   with HP resource (factory) settings; start slow, catch up to HG races by
   approximately 2430–2440.

**-F — Factoryless**
   Set factory parameters to their worst values and redirect the freed points
   to mines, ships, and tech. Fast early game; "low density" — needs many
   planets to compensate.  Usually paired with OBRM and a wide habitat; often
   CA to avoid terraforming costs.  Should target 20% growth rate; mine cost
   should still be set to 3.

**Monster**
   Any race achieving 25 000 resources by 2450 in the standard HG test bed.
   The gravity-immune CA is the easiest archetype; immunities significantly
   simplify play at the cost of advantage points that must be recouped elsewhere.

**QS — Quick Start**
   Cheap factory settings (7 or below) for a fast early surge. Best in small
   and tiny universes. Trades late-game potential for early-game pressure.

.. note:: *Archetypes documented by Art Lathrop, "Basic Race Design" (1999);
   corroborated by Mahrin Skel, "Race Design, Step by Step" (1997).*
