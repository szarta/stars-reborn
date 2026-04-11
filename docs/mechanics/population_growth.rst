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

The table implies a ``capacity_factor`` function applied to the growth formula:

.. code-block:: text

   annual_growth = floor(population × growth_rate × planet_value_fraction × capacity_factor)

Where ``capacity_factor`` falls from 1.0 at ≤20% capacity to 0 at 100% capacity.
The exact mathematical form of ``capacity_factor`` is not given in the strategy
guide; the table provides ground-truth calibration points.

.. note:: *Source: Stars! Strategy Guide, Chapter 6. Requires oracle verification
   of the exact capacity_factor formula (see research open question).*

.. todo:: Reverse-engineer ``capacity_factor`` formula from original. Research
   open question tracked in ``stars-reborn-research/docs/open_questions/population_growth_capacity_factor.rst``.

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
     - 4 × normal (100,000)
   * - Low Starting Population (LRT)
     - 17,500 (70% of normal; LSP gives 30% fewer colonists)

Some sources suggest starting population scales with growth rate::

   starting_pop = 5,000 × growth_rate   (so 10% GR → 50,000)

.. todo:: Validate via Wine automation.

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

.. todo:: Exact overcrowding formula

.. todo:: Starting population formula (flat 25k vs. growth_rate dependent)

.. todo:: HE maximum population cap (believed to be 50% of normal)

.. todo:: AR growth rate formula

.. todo:: Confirm max population table for planet sizes (help gives 1,000,000 on a 100%
   value planet; the "planet size" enumeration in universe_generation may map to this)
