Scanning
========

Overview
--------

Scanning determines what information a player has about distant planets and
fleets. Without scanning, planets appear as "never visited" (grey dot). With
scanning, the player sees current planet data.

Scanner Types
-------------

Every scanner has two ranges: a **normal** range and a **penetrating** range.
Each range gates different categories of information.

Normal range
~~~~~~~~~~~~

What is revealed inside normal range:

- Fleets (subject to cloaking — see below)
- Wormholes
- Mineral packets in flight, salvage, mystery traders
- Minefields (subject to minefield cloak vs. non-penetrating scanners)
- The **existence** of a planet at a given coordinate (planet identity and
  position are common knowledge from the start; this is what is visible from
  the .xy data)

What is **not** revealed inside normal range:

- Planet contents — hab values (gravity/temperature/radiation), mineral
  concentrations, surface minerals, population, owner, installations.
  These require penetrating range.
- Cloaked fleets beyond their effective detection range.

Penetrating range
~~~~~~~~~~~~~~~~~

Penetrating range is typically much shorter than normal range. Inside it,
in addition to everything visible at normal range:

- **Planet contents** — hab values, mineral concentrations, surface minerals,
  population, owner, defense level. This is the only mechanism (apart from
  physically orbiting the planet) by which a player learns the contents of an
  enemy or unowned planet.
- Cloaked fleets within the penetrating-range envelope (subject to cloak
  reduction — see :ref:`cloaking-section`).
- Minefields are always detectable to penetrating scanners (0% cloak vs pen).

Penetrating-capable scanners are blocked by the **NAS** (No Advanced
Scanners) LRT; NAS races can only learn planet contents by visiting the
planet with one of their own fleets.

*References:* :ref:`planetary-scanners-ref` and :ref:`ship-scanners-ref` give
per-component normal and penetrating ranges.

Scanner Sources
---------------

Planetary scanners
~~~~~~~~~~~~~~~~~~

Installed via production queue. Auto-scan every planet within range each turn.
If no scanner is installed, the planet's own data is visible to its owner (range 0).

**Built-in scanner:** Every owned planet has a minimal built-in scanner.

.. list-table::
   :header-rows: 1
   :widths: 30 20 25 30

   * - Scanner
     - Basic range (ly)
     - Penetrating range (ly)
     - Tech req
   * - Bat Scanner
     - 50
     - 0
     - Energy 1
   * - Rhino Scanner
     - 100
     - 0
     - Energy 3
   * - Mole Scanner
     - 150
     - 0
     - Energy 4
   * - DNA Scanner
     - 125
     - 0
     - Biotech 6
   * - Possum Scanner
     - 150
     - 0
     - Energy 5
   * - Pick Pocket Scanner
     - 80
     - 35
     - Energy 4, Electronics 4
   * - Chameleon Scanner
     - 160
     - 45
     - Energy 6, Electronics 6
   * - Ferret Scanner
     - 185
     - 50
     - Energy 7, Electronics 7
   * - Dolphin Scanner
     - 220
     - 100
     - Energy 8, Electronics 8
   * - Gazelle Scanner
     - 225
     - 0
     - Energy 9
   * - RNA Scanner
     - 230
     - 0
     - Biotech 10
   * - Cheetah Scanner
     - 275
     - 110
     - Energy 10, Electronics 9
   * - Elephant Scanner
     - 300
     - 200
     - Energy 12, Electronics 10
   * - Eagle Eye Scanner
     - 335
     - 0
     - Energy 16
   * - Robber Baron Scanner
     - 220
     - 220
     - Energy 13, Electronics 13
   * - Peerless Scanner
     - 500
     - 350
     - Energy 24, Electronics 23

.. todo:: Validate all scanner ranges and tech requirements from the original.

Ship scanners
~~~~~~~~~~~~~

Ships with scanner components scan while in flight. The best scanner in a
fleet determines the fleet's scan radius.

Combined scanning
~~~~~~~~~~~~~~~~~

A player's total scan coverage is the union of all planetary scanner circles
and fleet scanner circles. Any planet within any scan circle is revealed.

Wormholes
~~~~~~~~~

Wormhole positions are revealed by **basic** scanner range from any source
(planetary or fleet); penetrating range is not required. Knowing a wormhole's
position is not the same as knowing where it leads — endpoint linkage is
gated on physical traversal. See :doc:`wormholes` for the full visibility
contract and the per-player intel record shape.

.. _cloaking-section:

Cloaking
--------

Ships can have cloaking devices installed. Super Stealth (SS) PRT ships have a
**75% built-in cloak** on every ship at no design slot cost.

Cloaking reduces the effective scanner range needed to detect the fleet:

- A fleet cloaked at **80%** is visible only within **20% of the scanner's rated range**.
- Cloaking at 75–95% provides marginal additional benefit over uncloaked detection.
- Cloaking at **98%+** is substantially stronger than 97%. A 98% cloaked fleet can
  sit within 25 ly of a planet and remain nearly undetectable regardless of tech level.
- The difference between 97% and 98% cloaking is larger than the difference between
  0% and 97%; practical cloaking strategy should target ≥98% or accept 75% (built-in SS).

Detection range for a cloaked fleet:

.. code-block:: text

   effective_range = scanner_range × (1 − cloak_percent / 100)

Where ``cloak_percent`` is the fleet's total cloaking percentage.

.. note:: *Sources: Stars! Strategy Guide, Chapter 9 and Appendix A (reviewed by
   original authors). The exact formula needs oracle verification — see research
   open question.*

.. todo:: Confirm cloaking detection formula via oracle test. See
   ``stars-reborn-research/docs/open_questions/cloaking_detection_formula.rst``.

Cloak Percentage Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ship's cloak percentage is derived from its **cloak units per kT** of ship mass.
The conversion is piecewise (from the in-game "Appendix of Cloaking"):

.. code-block:: text

   if units ≤ 100:    percent = units / 2
   elif units ≤ 300:  percent = 50 + (units − 100) / 8
   elif units ≤ 612:  percent = 75 + (units − 300) / 24
   elif units ≤ 1124: percent = 88 + (units − 612) / 64
   elif units < 1380: percent = 96
   elif units < 1612: percent = 97
   else:              percent = 98

Key checkpoints: 100 u/kT → 50%, 300 u/kT → 75%, 612 u/kT → 87.5%,
1124 u/kT → 96%, ≥1612 u/kT → 98%.

For a **loaded** ship: ``units/kT = device_units/kT × empty_mass / loaded_mass``.
Uncloaked ships in the fleet add to loaded_mass but contribute no cloak units.

**SS race exception:** cargo does NOT reduce cloaking for SS ships.

Multiple cloaking devices on the same ship: their combined cloak units/kT is
summed first, then the piecewise table is applied. Diminishing returns are
inherent to the table, not an explicit stacking penalty.

*Source: Stars! in-game help, Appendix of Cloaking.*

Tachyon Detector
~~~~~~~~~~~~~~~~~

Each Tachyon Detector in a fleet reduces enemy cloaking by 5%. Multiple
detectors stack with diminishing returns:

.. code-block:: text

   cloak_reduction_factor = 0.95 ^ sqrt(num_detectors)

Example: 4 detectors: ``0.95^2 = 0.9025`` → 9.75% total reduction.

*Source: Stars! in-game help, Tachyon Detector section.*

Cloaking in Minefields
~~~~~~~~~~~~~~~~~~~~~~~

Inside a minefield, cloaking is treated as an absolute hit-chance modifier:
a fleet cloaked at 90% has a **10% hit chance** per minefield detonation check,
regardless of field density. This differs from the scanner-range reduction model.

Against penetrating scanners: minefields have **0% cloak** (always detectable).
Against non-penetrating scanners: minefields have **82% cloak**.

*Source: Stars! in-game help, Minefields section.*

Information Staleness
---------------------

A player's view of a planet is in exactly one of three states:

1. **Never observed** — the player has never had a penetrating scanner on
   the planet and has never visited it. Planet contents are entirely
   unknown; identity (id, name, position) is still visible from the .xy
   data, but every contents field on ``DiscoverablePlanetData`` is absent
   (not zero, not null — literally not present).

2. **Observed before, not currently in penetrating-scan range** — the
   player has seen the planet at some prior turn. The contents fields
   hold the values **as they were at last observation**. Ground truth may
   have drifted since (terraforming changes hab; mining decays
   concentrations; population grows or declines), but the player's view
   is frozen until they re-scan. ``years_since_last_scan`` increments
   each turn the planet is not in penetrating-scan coverage.

3. **Currently in penetrating-scan range** — the contents fields hold
   the **current** ground-truth values, and ``years_since_last_scan = 0``.

Fields that follow this three-state rule on ``DiscoverablePlanetData``:
hab values (gravity, temperature, radiation), the three mineral
concentrations, the three surface mineral amounts, population, owner,
factories, mines, defense level, starbase presence/design.

Identity fields (id, name, position) are always present — they come from
the shared .xy data and never need scanning.

The original game uses ``NeverSeenPlanet`` (−1) as a sentinel for
``years_since_last_scan`` when the planet has never been observed; the
clone uses field absence instead, consistent with the
:ref:`architecture-discoverable-data` model.

Open Questions
--------------

.. todo:: Validate all scanner stats from the original game

.. todo:: Exact formula for combined cloaking vs. penetrating range detection

.. todo:: Whether the built-in homeworld scanner has a specific range

.. todo:: Pick Pocket Scanner (SS PRT ability) — steal technology mechanic

.. todo:: Whether non-penetrating scans of a planet refresh ``years_since_last_scan``
   at all, or only penetrating-range scans count as "observation". Original-game
   oracle test needed.
