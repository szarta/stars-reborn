Population Growth
=================

Annual Growth Formula
---------------------

.. code-block:: text

   growth_rate_actual = min(race.growth_rate, planet_value)   [if planet_value > 0]
   annual_growth      = floor(population × growth_rate_actual / 100 × capacity_factor)

Where ``capacity_factor`` accounts for overcrowding (see below).

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

Each planet has a maximum population based on its **planet size** (an enumerated
value assigned during universe generation).

.. list-table::
   :header-rows: 1
   :widths: 25 25

   * - Planet size
     - Max population
   * - Tiny
     - 300,000
   * - Small
     - 500,000
   * - Medium
     - 700,000
   * - Large
     - 800,000
   * - Huge
     - 1,000,000

.. todo::

   Verify these values from the original game. These are estimates from community
   sources. The original game assigns planet size during generation but the exact
   distribution and capacity table needs Wine validation.

**HE (Hyper Expansion):** max population is 500,000 on a 100% value planet
(half the normal cap of 1,000,000).

**OBRM (Only Basic Remote Mining):** +10% maximum population — 1,100,000 on a
100% planet (550,000 for HE).

Population above the planet cap continues to work but at 50% efficiency.

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

*Sources: FreeStars C++ source (Planet.cpp PopGrowth()); cross-confirmed against
Stars! Strategy Guide Chapter 6 (8/8 table values match). Pending final oracle
confirmation.*

**Overpopulation (population > max_population):**

.. code-block:: text

   annual_loss = round(population × (population / max_population) × 4)

At 110% capacity: annual loss ≈ 4.4% of population per year.

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

AR (Alternate Reality) Growth
------------------------------

AR races do not colonize planets in the normal sense. Their population grows
in starbases. The growth model is different:

- Population grows at the homeworld starbase
- Colonists "work" in orbit rather than on the surface
- Mining is done remotely

.. todo:: Research and document the AR growth model fully.

Open Questions
--------------

.. todo:: Confirm max population table for all planet sizes

.. todo:: Confirm planet size distribution during universe generation

.. todo:: HE maximum population cap (believed to be 50% of normal)

.. todo:: AR growth rate formula

.. todo:: Confirm max population table for planet sizes (help gives 1,000,000 on a 100%
   value planet; the "planet size" enumeration in universe_generation may map to this)
