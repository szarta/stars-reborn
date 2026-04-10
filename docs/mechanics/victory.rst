Victory Conditions
==================

.. note::

   This document covers **in-game scoring and win detection** — the formulae,
   the year-50 minimum, and announcement behaviour.

   For the host-configurable parameters (which conditions are active and their
   thresholds) see :doc:`../new_game/victory_parameters`.

Overview
--------

Victory is determined at the end of each turn after year 50 (minimum). A
player may win by meeting any of the configured victory conditions. If Public
Player Scores is enabled, scores are visible after year 20.

Victory Condition Options
--------------------------

The host configures victory conditions when creating the game. Multiple
conditions can be active simultaneously; meeting **any one** wins the game.

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - Condition
     - Description
     - Default
   * - Own X% of planets
     - Control a percentage of all planets
     - 30%
   * - Attain tech level N in X fields
     - Reach level N in X different fields
     - level 22 in 6 fields
   * - Exceed score N
     - Achieve a total score above a threshold
     - 11,000
   * - Score above second-place by X%
     - Lead by a margin
     - 100%
   * - Produce N resources
     - Accumulate total annual resources
     - 1,000
   * - Own N starbases
     - Build a number of starbases
     - 100
   * - Highest score after year N
     - Survive until year N with top score
     - year 900

These can be combined (e.g., own 30% of planets AND score 11,000+).

Minimum Years
-------------

Victory cannot occur before year 50 regardless of score or conditions met.
This prevents trivially fast wins in small universes.

Score Calculation
-----------------

Score is a composite of several factors:

.. list-table::
   :header-rows: 1
   :widths: 30 40

   * - Component
     - Formula
   * - Planets owned
     - colonized planets × 1
   * - Starbases
     - starbases × 3
   * - Unarmed ships
     - ships (unarmed) × 0.5
   * - Armed ships
     - ships (armed) × 1
   * - Resources
     - annual resources × 1
   * - Tech levels
     - sum of all tech levels × 1
   * - Population
     - total population / 100,000
   * - Capital ships
     - capital ships × 3

.. todo:: Validate exact score formula components and multipliers.

Winner Announcement
-------------------

When a player meets victory conditions:

- All players are notified
- The game can continue (other players may have more turns)
- The winning player is shown in the score report (F10)

Diplomatic Victory (multiplayer)
---------------------------------

In multiplayer, human players may agree to a diplomatic victory — all
remaining players declare a joint winner. This is purely a social convention;
the game engine does not enforce it.

Open Questions
--------------

.. todo:: Exact score formula components and multipliers

.. todo:: Whether meeting any condition wins or all conditions must be met

.. todo:: Exact behavior when multiple players meet conditions simultaneously

.. todo:: Year 900 "time limit" behavior in practice
