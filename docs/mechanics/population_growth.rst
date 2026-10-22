Population Growth
=================

Annual Growth Formula
---------------------

.. code-block:: text

   if planet_value > 0:
       annual_growth = round(population × race_growth_rate × planet_value / 100 × capacity_factor)

Growth is multiplicative across all three terms (race rate, hab, capacity
factor) — there is no ``min()`` cap. ``capacity_factor`` accounts for
overcrowding (see below); on lightly-populated planets it is ``1.0``.

Planets with a positive value below 5% are treated as 5% for population
calculations (floor to prevent near-zero growth from being zero).

If ``planet_value ≤ 0`` (red planet):

.. code-block:: text

   annual_loss = floor(population × abs(planet_value) / 10 / 100)
   new_pop     = population - annual_loss

The loss rate is ``|planet_value| / 10`` percent of colonists per year.
Example: a −10% planet kills 1% of colonists per year.

*Source: Stars! in-game help, Population section.*

Planet Capacity
---------------

There is no "planet size" enumeration. Maximum population scales linearly
with the race's habitability value of the planet:

.. code-block:: text

   max_pop = MaxPlanetPop × hab / 100 × PopulationFactor

Where:

- ``MaxPlanetPop = 1,000,000`` is a constant.
- ``hab`` is the race's planet value as a percentage. A planet with positive
  hab below 5 is treated as 5 for max-pop purposes (matching the growth
  floor).
- ``PopulationFactor`` is the product of all PRT/LRT pop multipliers
  (default 1.0).

Examples on a 100% planet (``PopulationFactor = 1.0``): 1,000,000 cap.
On a 50% planet: 500,000. On a 25% planet: 250,000. Terraforming a planet
toward 100% therefore raises both the growth-rate ceiling *and* the max-pop
ceiling.

PRT/LRT modifiers to ``PopulationFactor``:

.. list-table::
   :header-rows: 1
   :widths: 30 25 45

   * - Trait
     - Factor
     - Effect on a 100% planet
   * - HE (Hyper Expansion)
     - 0.5
     - 500,000 cap
   * - JOAT (Jack of All Trades)
     - 1.2
     - 1,200,000 cap
   * - OBRM (Only Basic Remote Mining)
     - 1.1
     - 1,100,000 cap (550,000 with HE; 1,320,000 with JOAT)

Population above the planet cap continues to work but at reduced efficiency
and triggers an overpopulation loss each turn (see below).

*Sources: Stars! in-game help ("max_pop = planet_value × 1,000,000");
FreeStars ``Server/Planet.cpp::GetMaxPop()``; ``rules/MyModRules.xml``
PRT/LRT ``PopulationFactor`` values.*

Overcrowding Penalty
--------------------

Growth slows as a planet fills up; the overcrowding penalty begins well before
the planet reaches capacity. The Stars! Strategy Guide (reviewed by original
authors) gives the following table for a 100% value world:

.. list-table::
   :header-rows: 1
   :widths: 30 40

   * - Population capacity
     - Effective growth rate (as if planet value were…)
   * - ≤20%
     - 100% (no penalty)
   * - 30%
     - 87%
   * - 40%
     - 64%
   * - 50%
     - 44%
   * - 60%
     - 28%
   * - 70%
     - 16%
   * - 80%
     - 7%
   * - 90%
     - 2%
   * - 100%
     - 0% (no growth)

"Capacity" here is ``population / max_population``. Growth begins to decline
above ~25% capacity. Absolute growth (population × rate) peaks at ~33% capacity
even though the rate is still at 100% there, because the rate is capped while
population is still increasing.

The formula for ``capacity_factor`` is:

.. code-block:: text

   if capacity ≤ 0.25:
       capacity_factor = 1.0   (no crowding penalty)
   else:
       capacity_factor = (16/9) × (1 − capacity)²

This formula reproduces all eight strategy guide calibration points exactly
(e.g. at 50% capacity: (16/9) × 0.5² = 0.444 ≈ 0.44 ✓).  The function is
continuous at the 25% breakpoint: (16/9) × (0.75)² = 1.0.

Applied in the growth formula:

.. code-block:: text

   annual_growth = round(population × growth_rate × planet_value_fraction × capacity_factor)

*Sources: Jeff McBride email (1997-02-19, posted to rec.games.computer.stars
1997-02-20 with permission, archived in research/excel/pop formula.txt) —
primary developer source giving the full pseudocode; FreeStars
``Server/Planet.cpp::PopGrowth()`` (matches McBride byte-for-byte);
advfaq §4.9 (Cawley/Butler); Stars! Strategy Guide Chapter 6 (8/8 table
values reproduced exactly).*

**Overpopulation (population > max_population):**

.. code-block:: text

   annual_loss = round(population × (population / max_population) × 4)

At 110% capacity: annual loss ≈ 4.4% of population per year. McBride's 1997
email gives an additional refinement that pegs loss to ~10% per year at and
above 200% cap (``Retard_Percent`` floor of −300, yielding an effective Grow
Percent of −1200). Overpopulation only occurs naturally for AR (whose cap is
hull-based, not hab-based) and for IS via fleet overflow into a non-owned
orbit.

**Edge case: exactly at cap.** If ``population ≥ max_pop`` and
``population < max_pop + 10``, growth is zeroed entirely (no negative growth,
no positive growth). Above ``max_pop + 10``, the overpopulation loss formula
applies.

Starting Population
-------------------

.. list-table::
   :header-rows: 1
   :widths: 40 30

   * - Condition
     - Starting population
   * - Normal game
     - 25,000
   * - Accelerated BBS
     - ``25,000 + 5,000 × GR%`` (e.g. 15% → 100,000; see below)
   * - Low Starting Population (LRT)
     - 70% of the above (30% fewer colonists)

FreeStars implements starting population as:

.. code-block:: text

   starting_pop = 25,000 + 500,000 × growth_rate_decimal

Examples: 1% GR → 30,000; 5% GR → 50,000; 10% GR → 75,000; 20% GR → 125,000.

The alternative formula sometimes cited ("5,000 × GR") matches the bonus
component only (500,000 × 0.10 = 50,000) and omits the 25,000 base.

.. todo:: Confirm starting population formula with oracle test (R2.1).

Homeworld Population
--------------------

Homeworlds start with the standard starting population above. Their hab values
are set to the midpoint of the race's preferred range, so ``planet_value = 100%``
and the race grows at exactly ``growth_rate%`` per year on its homeworld.

HE (Hyper Expansion)
--------------------

HE races multiply both the growth rate and the planet capacity by trait
factors:

- ``GrowthRateFactor = 2.0`` — the race's selected growth rate is doubled
  when applied. (The race-design slider still ranges from 1–20%; the cost is
  computed against the displayed value, not the doubled effective value.)
- ``PopulationFactor = 0.5`` — every planet's max pop is halved. A 100%
  planet caps at 500,000; a 50% planet at 250,000.

The capacity-factor formula uses the HE-adjusted max pop, so the ~25%
breakpoint and crowding penalty kick in at half the absolute population
they would for a non-HE race.

IS (Inner Strength) — Freighter Reproduction
--------------------------------------------

IS colonists grow while traveling on freighters. Each turn, every fleet with
IS-owned colonists aboard gains:

.. code-block:: text

   in_transit_growth = floor(fleet_pop × FreighterReproduction × race_growth_rate)

With ``FreighterReproduction = 0.5``, an IS fleet carrying 100 kT (10,000
colonists) at 15% race growth grows by ``10000 × 0.5 × 0.15 = 750`` colonists
per turn. There is no habitability or capacity factor in transit; growth
is uncapped by planet conditions.

If the new total exceeds the fleet's cargo capacity, the overflow is pushed
to a planet the fleet is orbiting if and only if that planet is owned by
the IS player; otherwise the overflow is lost. This is the source of the
classic IS "flying orgy" tactic: a freighter parked above an owned world
acts as a pop-overflow generator.

AR (Alternate Reality)
----------------------

AR races do not colonize planets in the normal sense — population lives in
starbases in orbit, not on the surface. The growth model differs from
non-AR races in three ways:

1. **Capacity comes from the starbase hull**, not the planet's hab value.
   Each starbase hull defines an ``ARMaxPop`` value (in 100-pop cargo
   units):

   .. list-table::
      :header-rows: 1
      :widths: 35 25 30

      * - Starbase hull
        - ARMaxPop (units)
        - Population cap
      * - Orbital Fort
        - 2,500
        - 250,000
      * - Space Dock
        - 5,000
        - 500,000
      * - Space Station
        - 10,000
        - 1,000,000
      * - Ultra Station
        - 20,000
        - 2,000,000
      * - Death Star
        - 30,000
        - 3,000,000

   These are then multiplied by ``PopulationFactor`` from any LRTs (e.g.
   OBRM gives a Death Star a 3,300,000 cap).

2. **Growth uses the same crowding formula** as non-AR races, with the
   capacity above substituted for the hab-scaled planet cap. An AR planet
   with a Space Station at 250k pop is at 25% capacity (no crowding
   penalty); the same population on an Orbital Fort is at 100% (no growth).
   Upgrading the starbase hull immediately re-opens growth headroom.

3. **No surface hab penalty for AR.** AR races still need a *colonizable*
   planet (positive hab) to land in the first place, but planet hab does
   not enter the cap calculation.

If an AR starbase is destroyed, the resident population becomes
overpopulation against an effective cap of zero, and dies off rapidly.

**Warp acceleration deaths (AR-specific).** AR colonists in transit suffer
losses each turn — message 193: "Due to the rigors of warp acceleration,
X of your colonists on Y have died." Confirmed AR-specific in
``research/original/transport_test`` (Wine save). Non-AR races do **not**
incur this loss when transporting colonists. The exact per-turn rate as
a function of warp speed is still open.

.. todo:: Document the exact AR warp-acceleration death rate (per-turn
   fraction as a function of warp speed).

Radiating Hydro-Ram Scoop
-------------------------

Independent of PRT, any fleet that contains **at least one ship using the
Radiating Hydro-Ram Scoop engine** subjects all colonists in the fleet to
radiation losses each turn, *unless* the midpoint of the race's
Radiation hab band is at or above 85 mR.

This is a fleet-wide property: it triggers if any single ship in the
shared fleet has the engine, even if the colonists are riding on a
different (non-radiating) ship in the same fleet. To carry pop with this
engine safely, either design the race with a radiation midpoint ≥85 mR
or keep colonist transports in a separate fleet.

*Source: in-game component help text on Radiating Hydro-Ram Scoop.*

.. todo:: Document the exact RHRS death rate when the radiation midpoint
   is below 85 mR.
