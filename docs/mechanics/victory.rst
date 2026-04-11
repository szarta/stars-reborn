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

Score is a composite of several factors.  Ship counts are capped at the number
of planets owned (excess ships beyond that count do not score).

.. list-table::
   :header-rows: 1
   :widths: 30 50

   * - Component
     - Formula
   * - Planets
     - 1–6 pts; 1 pt per 100,000 colonists (max 6 pts per planet)
   * - Starbases
     - 3 pts each (Orbital Forts do not count)
   * - Unarmed ships
     - 0.5 pt each (power rating = 0); capped at number of planets owned
   * - Escort ships
     - 2 pts each (power rating 1–1999); capped at number of planets owned
   * - Capital ships
     - ``8 × N_cap × N_planets / (N_cap + N_planets)`` pts each; capped at planets
   * - Tech levels
     - 1 pt per level for levels 1–3; 2 pt for 4–6; 3 pt for 7–9; 4 pt for 10+
   * - Resources
     - 1 pt per 30 annual resources

Capital ship scoring uses a harmonic-mean formula that rewards balanced
fleet-to-planet ratios.  Example: 20 capital ships, 30 planets →
``8 × 20 × 30 / (20 + 30) = 4.8 pts`` per capital ship.

*Source: Stars! Players Guide (via Stars! FAQ advfaq/guts2.htm §4.13).*
*Oracle validation of exact multipliers still recommended.*

.. todo:: Validate capital ship "power rating" threshold (> 1999 = capital).
   Confirm whether Orbital Forts are truly excluded from starbase scoring.
   Confirm capping behavior (ship count vs planets owned).

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
