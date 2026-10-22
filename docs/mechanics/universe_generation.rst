Universe Generation
===================

.. note::

   This document covers the **generation algorithms**: planet count formulae,
   placement, hab value distributions, and homeworld setup.

   For the host-configurable input parameters (size, density, player positions,
   game options) see :doc:`../new_game/universe_parameters`.

Universe Sizes
--------------

.. list-table::
   :header-rows: 1
   :widths: 20 25 30

   * - Name
     - Dimension (ly)
     - Typical players
   * - Tiny
     - 400 × 400
     - 2–3
   * - Small
     - 800 × 800
     - up to 4
   * - Medium
     - 1200 × 1200
     - 4–16
   * - Large
     - 1600 × 1600
     - up to 16
   * - Huge
     - 2000 × 2000
     - up to 16

Source: community wiki; see :doc:`../reference/universe_sizes`.

Planet Count Formula
--------------------

.. code-block:: text

   planet_count = floor((dim / 10)² × density_factor / 100)

Where ``dim`` is the universe dimension in light years and ``density_factor`` is:

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Setting
     - Density factor
     - Confidence
   * - Sparse
     - 2.0
     - Oracle-confirmed (Large/Sparse=512, Huge/Sparse=800)
   * - Normal
     - 2.5
     - Oracle-confirmed (Tiny=40, Small=160, Medium=360, Large=640)
   * - Dense
     - 3.75
     - Oracle-confirmed (Tiny/Dense=60, Small/Dense=240, Medium/Dense=540)
.. note::

   ``Packed`` is **not a distinct density** in Stars!.  The Stars! game UI's
   highest density option stores internally as code 3 (Dense), confirmed by
   reading the ``.xy`` type-7 record across 10 manually-created games.
   A ``packed`` token (internal code 4) exists in the ``game.def`` format but
   is invalid — Stars! exits silently with no output when given code 4 headlessly.

Examples (oracle-confirmed 2026-04-21/22):

- Tiny / Normal:  ``floor((400/10)² × 2.5 / 100) = floor(1600 × 0.025) = 40``
- Medium / Normal: ``floor((1200/10)² × 2.5 / 100) = floor(14400 × 0.025) = 360``
- Large / Dense:  ``floor((1600/10)² × 3.75 / 100) = floor(25600 × 0.0375) = 960``

Planet Count Cap
~~~~~~~~~~~~~~~~

Stars! shipped with exactly 999 unique planet names — by design, the maximum
achievable planet count in any configuration is below this limit.

For combinations where the formula target exceeds roughly **960 planets**, the
placement algorithm does not reliably reach the target.  Planet counts become
**stochastic** (vary per seed) rather than exact, as the algorithm exhausts its
iteration budget before placing every planet:

.. list-table::
   :header-rows: 1
   :widths: 22 18 20 40

   * - Combination
     - Formula Target
     - Observed Range
     - Notes
   * - Huge / Normal
     - 1 000
     - 939–946
     - Oracle-confirmed (2026-04-21, 3 seeds)
   * - Huge / Dense
     - 1 500
     - 939–959
     - Headless: 939–958 (10 seeds); UI: 939–959 (10 seeds, 2026-04-22)
   * - Large / Dense
     - 960
     - 908–928
     - Oracle-confirmed (2026-04-21, 10 seeds)

All other combinations produce **exact, deterministic** planet counts matching
the formula.  Examples: Large/Normal = 640, Huge/Sparse = 800, Medium/Dense = 540.

.. note::

   "Huge/Packed" is Huge/Dense under another name — the UI's top density option
   is Dense (code 3) regardless of its label in any given game version.
   "Large/Packed" is identically Large/Dense.

The planet count must always be at least ``num_players`` to guarantee a homeworld
for each player.

Planet Placement
----------------

- Planets are placed within a rectangular region of ``dim × dim`` light years.
- **Minimum inter-planet distance: 20 light years.**
- Placement algorithm: rejection sampling (attempt random position; retry if too close
  to any existing planet). After a fixed number of failed attempts, the constraint is
  relaxed and the planet is placed unconstrained (prevents infinite loops at high density).

.. todo:: Verify whether original |original| uses any clustering ("Galaxy Clumping" option).

Planet Names
------------

The original game has **999 unique planet names** (``engine/data/planet_names/original.txt``).
This imposes a design cap on universe size — each planet must have a distinct
name drawn from the pool without replacement. The largest supported universe
(Huge/Packed) generates 931–965 planets in practice, well within the 999-name
pool. The 999-name limit was set intentionally to accommodate all standard
configurations with headroom to spare.

For future extension beyond the original universe sizes, a curated supplemental
pool of ~2 000 additional names is kept in ``engine/data/planet_names/extended/``,
organized by thematic category (see below). The combined pool supports up to
~3 000 uniquely named planets.

**Naming rules observed in the original game:**

- Length: 2–18 characters (shortest: Io; longest: Wammalammadingdong)
- Up to 3 words per name (e.g. "Le Petit Jean", "Double Tall Skinny")
- Characters: A–Z, a–z, 0–9, hyphen, apostrophe
- Some names are pure numbers (007)
- Every name starting with a letter begins with a capital; secondary words
  also capitalized
- Predominantly English / Latin alphabet
- No overt profanity or obscenity

**Original name categories** (from the game's own pool):

- People: first names (Alexander), last names (Lincoln, Washington, Mozart)
- Mythology: Loki, Asgard
- Food: Maple Syrup, Flaming Poodle
- Earth places: America
- Astronomy: Mars, Milky Way, Ursa Major
- Fiction: Asgard
- Computing: Sed, Awk
- Chemistry: Gold, Silver, Neon, H2O, H2SO4
- Pop culture: 3M TA3
- Flora: Forget-Me-Not
- Mathematics / science: Cosine
- Miscellaneous: Flutter Valve

**Extended pool categories** (``engine/data/planet_names/extended/``):

basic_hand_tools, chemical_compounds, constellations, countries_of_earth,
days_of_week, defunct_states, elements, exoplanets, fruits, fun_symbology,
gemstones, greek_gods, greek_letters, greek_titans, mexican_food,
months_of_year, pop_culture, religion, scientific_terms, scientists, shapes,
shrubbery, snakes, solar_system, space_probes, swords, types_of_knots,
usa_presidents_last_names, usa_states, usa_territories, vegetables.

Name selection at universe generation: shuffle the combined pool, draw without
replacement in order. If the pool is exhausted before all planets are named,
fall back to "Planet N" for remaining planets.

Habitat Value Generation
------------------------

Each planet rolls three habitat axes independently.  All three axes are stored
internally as a click index 0–100 (101 discrete values).  Indices 0 and 100 are
**never produced** by universe generation — both extreme values have zero
probability of being rolled (verified with 40,614 sample planets across 52
Huge universes; see :ref:`hab-distribution-finding`).

Gravity
~~~~~~~

- Click index 0–100 maps via the ``Gravity_Map`` table to displayed values
  0.12g – 8.00g; see :doc:`habitability` for the lookup table.
- Distribution: **trapezoid centred on click index 50** (see formula below).

Temperature
~~~~~~~~~~~

- Click index 0–100 maps to °C as ``temp_c = (idx − 50) × 4``, giving
  −200°C to +200°C in 4°C steps.
- Distribution: **trapezoid centred on click index 50**, identical shape to
  gravity.

Radiation
~~~~~~~~~

- Click index 0–100 equals mR/yr directly (0–100 mR/yr).
- Distribution: **uniform across indices 1–99**; indices 0 and 100 have zero
  probability.

Trapezoid distribution (gravity and temperature)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Letting ``d = |idx − 50|`` be the distance from centre in clicks, the per-click
probability is:

.. code-block:: text

   d = 50            : 0%                       (idx 0 and idx 100)
   d ∈ [41, 49]      : ((50 − d) / 10) × (1/0.9)%      (linear ramp)
   d ∈ [0, 40]       : (1/0.9)% ≈ 1.1111%        (flat plateau, 81 indices)

Equivalent table form for the ramp:

================  ==================  ==============
``d`` from centre  Coefficient        Percent per index
================  ==================  ==============
41                 0.9                1.0000%
42                 0.8                0.8889%
43                 0.7                0.7778%
44                 0.6                0.6667%
45                 0.5                0.5556%
46                 0.4                0.4444%
47                 0.3                0.3333%
48                 0.2                0.2222%
49                 0.1                0.1111%
50                 0                  0%
================  ==================  ==============

Total mass: ``81 × (1/0.9) + 2 × (4.5/0.9) = 90 + 10 = 100%``.

Uniform distribution (radiation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   idx ∈ {0, 100}    : 0%
   idx ∈ [1, 99]     : (1/0.99)% ≈ 1.0101%      (99 equally-likely values)

Race-design implication
~~~~~~~~~~~~~~~~~~~~~~~

A race's hab window of width *w* on radiation captures the same expected
fraction of planets regardless of where the window is placed within 1–99.
A window of the same width on gravity or temperature captures the most
planets when centred on the plateau (indices 10–90) and progressively fewer
as the window slides toward the extremes.  This is why Art Lathrop's
*Basic Race Design* article recommends sliding only the radiation window for
free advantage points.

Source: Alan L. Kolaga's per-click distribution table (charts captured at
``stars-reborn-research/web_captures/arglos/charts/``), confirmed against
40,614 independently observed planets in
:ref:`hab-distribution-finding`.

Mineral Generation
------------------

Each planet independently rolls three mineral concentrations.  All three
minerals use the same algorithm and the same distribution shape.

**Range:** 1–119 (oracle-confirmed; the common community assumption of 1–100 is wrong).

**Distribution** (oracle-confirmed, 9,204 planets × 3 minerals = 27,612 readings
across 10 large/dense games; see research R3.4):

.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Range
     - Fraction
     - Shape
   * - 1–30
     - ~30%
     - Flat / uniform (≈1% per value)
   * - 31–32
     - <0.2%
     - Near-zero valley (not a hard cutoff, but extremely rare)
   * - 33–119
     - ~70%
     - Bell-shaped; peak at ~74–79; tails off to zero by 119

The bimodal structure (two clearly distinct pools) suggests that the game
uses two separate generation paths rather than a single continuous distribution.
The exact algorithm is not yet reverse-engineered.

**Radiation dependency:** When a planet's radiation value is ≥ 90 mR/yr, the
high-concentration pool (33+) is shifted upward by approximately 5–6 points
(mean ~81 vs ~75 for rad < 90).  The fraction of planets landing in the low
pool (1–30) is unaffected by radiation.  This correlation is the only confirmed
cross-axis dependency in mineral generation.

**Surface mineral amounts** are initialized to a function of concentration
(see :doc:`/new_game/initial_state`).

.. note::

   **"Beginner: Maximum Minerals"** sets every planet's concentration to exactly
   100 for all three minerals (oracle-confirmed 2026-04-22: 918 planets ×
   3 minerals, all = 100, Large/Dense game, seed 43100).  No exceptions.

.. todo:: Reverse-engineer the exact two-pool generation algorithm

Homeworld Setup
---------------

**Selection:** Homeworlds are selected from the existing planet pool after all
planets have been placed (confirmed oracle 2026-04-22: homeworld planet indices
span the full range, showing no early-index bias).  Candidate homeworlds are
placed by rejection sampling: a random planet is chosen; if it falls within the
``player_positions`` threshold distance of any already-assigned homeworld it is
rejected and a new candidate is drawn.  Planet indices 0–3 are never assigned
as homeworlds (possibly reserved for wormholes or other non-planet objects).

**Homeworld separation thresholds** scale proportionally with map dimension for
``moderate``, ``farther``, and ``distant``; see :doc:`../new_game/universe_parameters`.

**PP / IT second starting planet:** PP (Packet Physics) and IT (Interstellar
Traveler) races receive a second colonised planet in addition to their main
homeworld.  This second planet is:

- **Not generated on Tiny maps** — only Small and larger.
- **PRT-independent in placement:** PP and IT races receive identical second-planet
  assignments for the same seed, confirming the placement algorithm does not
  specialise by PRT.
- **Proportionally distant from the main homeworld:** 0.155–0.228 × map dimension
  (oracle-confirmed 2026-04-22 across Small/Medium/Large/Huge, 15 seeds each).
  The upper bound (0.228 × dim) coincides with the ``moderate`` homeworld
  threshold (0.221 × dim), suggesting the same rejection-sampling mechanism.

When a homeworld is assigned to a player's race:

1. **Hab values** are set to the midpoint of the race's preferred range on each axis.

   - Immune axis: gravity=1.0g, temperature=0°C, radiation=50 mR/yr
   - Gravity snapped to nearest ``Gravity_Map`` key
   - Temperature snapped to nearest step-4 value

2. **Starting minerals:** 1000 kT each (ironium, boranium, germanium)
3. **Starting population:** see :doc:`population_growth`
4. **Starting infrastructure:** factories and mines from race parameters

Open Questions
--------------

.. todo:: Packed density factor (cannot measure headlessly; Large/Packed count unknown)

.. todo:: Whether "Galaxy Clumping" uses a spatial Poisson process or simple clustering

.. todo:: Whether mineral concentrations have a minimum guaranteed per homeworld
