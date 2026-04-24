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
     - ``max(1, min(6, ceil(pop / 100_000)))`` per owned planet — i.e.
       1 pt floor, +1 pt per started 100k colonists, capped at 6 pts
   * - Starbases
     - 3 pts each (Orbital Forts do not count)
   * - Unarmed ships
     - 0.5 pt each (power rating = 0); capped at number of planets owned
   * - Escort ships
     - 2 pts each (power rating 1–1999); capped at number of planets owned
   * - Capital ships
     - ``8 × N_cap × N_planets / (N_cap + N_planets)`` pts total; capped at planets
   * - Tech levels
     - 1 pt per level for levels 1–3; 2 pt for 4–6; 3 pt for 7–9; 4 pt for 10+
   * - Resources
     - 1 pt per 30 annual resources

Capital ship scoring uses a harmonic-mean formula that rewards balanced
fleet-to-planet ratios.  The formula gives **total** points for all capital
ships, not per-ship.  Example: 20 capital ships, 30 planets →
``8 × 20 × 30 / (20 + 30) = 96 pts`` total (4.8 pts per capital ship).

Power rating thresholds (confirmed from help file):

- Unarmed: power rating = 0
- Escort: power rating 1–1999
- Capital: power rating ≥ 2000

*Source: Stars! help file ctx_5f2efbaf (Score sheet topic, 1998).*

Empirical validation (R5.1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verified against an in-game F10 screen at year 2420 in a 16-player game
(``stars-reborn-research/original/normally_played_game``).  Player 1
(AR race "Timmune") with 4 planets, 1 starbase, 16 unarmed ships,
tech 6/0/1/4/3/3 (sum 17), and 311 annual resources scored exactly:

.. code-block:: text

   Planets        4 owned  →   4 pts   (1 pt floor; none above 100k pop)
   Starbases      1        →   3 pts
   Unarmed Ships 16 (cap 4) →  2 pts   (0.5 × min(16, 4 planets))
   Tech Levels   17 sum     → 21 pts   (E6=9 + W0=0 + P1=1 + C4=5 + El3=3 + B3=3)
   Resources    311        →  10 pts   (floor(311/30))
   ──────────────────────────────────
   EXPECTED               =  40 pts   ✓ matches F10

Confirmed multipliers and behaviors:

- Owned-planet floor is **1 pt minimum** for any colonized planet (the help
  file's "1–6 pts" range is correct: ``max(1, min(6, pop // 100_000))``).
- Starbase = 3 pts each; Starter Colony icons do **not** count.
- Unarmed ships are capped at ``min(n_ships, n_planets_owned)`` × 0.5.
- Tech-level breakpoints (1/2/3/4 pts at L1–3 / L4–6 / L7–9 / L10+) match
  the per-field totals exactly when applied to each of the six fields.
- Resources: integer-divided by 30 (truncate, do not round).

Cross-checked against Player 5 (10P, 16 unarmed, tech 9, res 376 → 37 pts)
and Player 2 (4P, 2 unarmed, tech 21, res 525 → 51 pts); both agree.

A second snapshot at year 2433 (same game) re-validates Player 1: 7P, 1SB,
23 unarmed (cap 7), tech 6/4/8/6/3/3 (sum 30), 724 res → 81 pts (matches
F10).  This snapshot **adds empirical confirmation of the L7-9 = 3 pt
breakpoint** via Propulsion = 8 (= 1+1+1+2+2+2+3+3 = 15 pts).

Multi-player cross-check at year 2433 — after fixing ``m1_to_json`` to
disambiguate multiple type-6 records by matching the player-ID byte at
offset 0 against the filename — confirmed the formula reproduces F10
*exactly* for **12 of 16 players**: P1 (AR), P2 (HE), P3, P4, P5, P6
(IS), P8, P11, P14, P15, P16 — every player whose only high-pop world is
the homeworld at 600k+ (which scores the cap of 6 pts).

A third snapshot at year 2448 added **three more confirmed cells**:

* **Per-planet bonus uses ``ceil``, not ``floor``** — a planet at 108k
  colonists scores 2 pts, not 1.  Empires with many medium-pop worlds
  (P9 Ferret 73 planets, P10 Crusher 52, P12 Bulushi 37) only matched
  F10 once the bonus formula was switched to ceiling division.  All four
  apparent "PRT-conditional" residuals at year 2433 (which we attributed
  to PP/HE special rules) collapsed to exact matches once this was fixed.
* **Escort multiplier = 2 pts each** — Player 1 (Timmune) had 4 escorts
  this turn; expected 4×2 = 8 pts; total score 128 matched F10 exactly.
  Cross-checked at scale by P3 (60 escorts → 120 pts ✓) and P4 (50 → 100 ✓).
* **Tech L10+ = 4 pts per level** — Player 1's Construction reached 10;
  C10 contributes 4 pts (in addition to the 1+1+1+2+2+2+3+3+3 = 18 from
  L1-9), giving 22 pts.  Total tech 75 pts matched F10's 41-level total.

Multiple-starbases-per-player works additively (P1 had 2 starbases →
6 pts).  Year-2448 multi-player run: **16/16 exact F10 matches**.  The
help-file formula reproduces every player's score with zero residual,
across PRTs JOAT/HE/SS/PP/IS/AR, planet counts from 1 to 73, escort
counts up to 60, and tech levels up to 10.

Per-class validation scripts:
``stars-reborn-research/reverse-engineering/scripts/score_calc.py`` (single
player) and ``validate_score.py`` (multi-player, takes an F10 ground-truth
JSON).

Still open
~~~~~~~~~~

The validation snapshot had no escort or capital ships and no player above
tech level 6, so these cells of the table remain unverified empirically:

.. note:: Escort multiplier (2 pts each, capped at planets) is confirmed
   year 2448 — verified across multiple players up to 60 escorts.

.. todo:: Verify the capital-ship harmonic-mean total formula
   ``8 × N_cap × N_planets / (N_cap + N_planets)`` and whether the cap
   applies before or after the harmonic mean.  No snapshot has any
   player with capital ships at year 2448 (Crusher's 9 from year 2433
   are gone).  Need a snapshot once any player builds ≥2000-power ships.

.. note:: Tech L10+ = 4 pts confirmed year 2448 via Player 1
   Construction=10.  Escort = 2 pts confirmed same snapshot via Player 1's
   4-escort fleet contributing 8 pts to a fully-balanced expected total.

.. note:: The "PRT-conditional" anomalies suspected at year 2433 (P7 PP,
   P9 HE, P10 PP, P12 PP, P13 SS) were all OCR transcription errors in
   the F10 reading combined with the wrong rounding direction in the
   per-planet bonus formula.  Once the planet bonus was switched to
   ``ceil`` and the column reads were corrected, **all PRT-suspected
   players now match F10 exactly** at year 2448.  The formula is not
   PRT-conditional for any of these cells.

Winner Announcement
-------------------

When a player meets victory conditions:

- All players are notified
- The game can continue (other players may have more turns)
- The winning player is shown in the score report (F10)

Meeting **any one** configured victory condition wins the game; conditions are
OR-combined (confirmed from help file: "more than one player can be declared
the winner").

Diplomatic Victory (multiplayer)
---------------------------------

In multiplayer, human players may agree to a diplomatic victory — all
remaining players declare a joint winner. This is purely a social convention;
the game engine does not enforce it.

Open Questions
--------------

.. todo:: Exact behavior when multiple players meet conditions simultaneously

.. todo:: Year 900 "time limit" behavior in practice
