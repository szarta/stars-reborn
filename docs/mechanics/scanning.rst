Scanning
========

Overview
--------

Scanning determines what information a player has about distant planets and
fleets. Without scanning, planets appear as "never visited" (grey dot). With
scanning, the player sees current planet data.

Scanner Types
-------------

Basic (non-penetrating)
~~~~~~~~~~~~~~~~~~~~~~~~

- Reveals planet hab values, minerals, population, and owner at the scanned range
- Does **not** reveal cloaked fleets
- Range: varies by scanner tech item

Penetrating
~~~~~~~~~~~

- Reveals all of the above AND cloaked ships within penetrating range
- Penetrating range is typically much shorter than basic range
- Advanced scanners (blocked by No Advanced Scanners LRT)

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

Information Staleness
---------------------

When a scanner is no longer covering a planet:

- The planet data freezes at the last observed state
- ``years_since`` increments each turn it is not scanned
- Value of ``NeverSeenPlanet`` (−1) means the planet has never been scanned

Open Questions
--------------

.. todo:: Validate all scanner stats from the original game

.. todo:: Exact formula for combined cloaking vs. penetrating range detection

.. todo:: Whether the built-in homeworld scanner has a specific range

.. todo:: Pick Pocket Scanner (SS PRT ability) — steal technology mechanic

.. todo:: Exactly what data is revealed at basic vs. penetrating range
