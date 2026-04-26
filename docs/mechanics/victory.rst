Victory Conditions
==================

.. note::

   This document covers **in-game scoring and win detection** — the formulae,
   the year-50 minimum, and announcement behaviour.

   For the host-configurable parameters (which conditions are active and their
   thresholds) see :doc:`../new_game/victory_parameters`.

Overview
--------

Victory is determined at the end of each turn after the configured
minimum-years threshold has elapsed.  A player may win by meeting the
host-configured number of active victory conditions.  If Public Player
Scores is enabled, scores are visible after year 20.

Victory Condition Options
--------------------------

The host configures victory conditions when creating the game.  Any
subset of the seven conditions below may be checked, and the host
separately specifies how many of the checked conditions a player must
meet for victory to be declared.

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - Condition
     - Description
     - Range
   * - Owns X% of all planets
     - Colonise a percentage of every planet in the universe
       ("owned" = colonised by this player)
     - 20–100%
   * - Attains tech level N in X fields
     - Reach level N in X different fields
     - L8–26 / 2–6 fields
   * - Exceeds a score of N
     - Total score above a threshold
     - 1 000–20 000
   * - Exceeds second-place score by X%
     - Lead the runner-up by a margin
     - 20–300%
   * - Has production capacity of X thousand
     - Annual resources at or above a threshold
     - 10–500 (thousand)
   * - Owns N capital ships
     - Fleet of ships with power rating ≥ 2000
     - 10–300
   * - Has highest score after year N
     - Be top-ranked at the configured year
     - year 30–900

For full parameter ranges, field names, and the JSON request shape see
:doc:`../new_game/victory_parameters`.

Combining Conditions
~~~~~~~~~~~~~~~~~~~~

In addition to the seven checkboxes, the host sets *Winner must meet N of
the above selected criteria* (range 0–7).  At N = 1 any one enabled
condition suffices (the OR semantics documented by the help file); at
N > 1 the combinator acts as "any N of M".  Thus a host can demand e.g.
"own 30 % of planets AND score 11 000+" by checking both and setting
must-meet = 2.

Minimum Years
-------------

Victory cannot occur before ``min_years`` (configurable, 30–500, default
50) regardless of score or conditions met.  This prevents trivially fast
wins in small universes.

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
     - ``floor(8 × N_cap × N_planets / (N_cap + N_planets))`` pts total;
       N_cap capped at planets owned before the formula is applied
   * - Tech levels
     - 1 pt per level for levels 1–3; 2 pt for 4–6; 3 pt for 7–9; 4 pt for 10+
   * - Resources
     - 1 pt per 30 annual resources

Capital ship scoring uses a harmonic-mean formula that rewards balanced
fleet-to-planet ratios.  The formula gives **total** points for all capital
ships, not per-ship, and the total is truncated to an integer.  Example:
20 capital ships, 30 planets →
``floor(8 × 20 × 30 / (20 + 30)) = 96 pts`` total (4.8 pts per capital ship).

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

Capital-ship harmonic mean (confirmed year 2504)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A fourth snapshot at year 2504 (``stars-reborn-research/original/try2``,
6-player game) closed the last open cell.  Two players held capital ships:

* **P1 Timmune (AR)** — 1 capital ship, 5 planets →
  ``floor(8 × 1 × 5 / (1 + 5)) = floor(6.667) = 6 pts``.
  Total expected score 318 = F10 ✓
* **P4 Hicardi (HE)** — 26 capital ships, 212 planets →
  ``floor(8 × 26 × 212 / (26 + 212)) = floor(185.345) = 185 pts``.
  Total expected score 5116 = F10 ✓

All 6 players matched F10 exactly at year 2504 once exact resource totals
(summed from each player's ``.pN`` dump) were used in place of the
rounded values F10 displays (e.g. F10 shows "12k" for 11509 actual).

Confirmed behaviors:

- The harmonic-mean result is **floor-truncated** to an integer, not
  rounded.  P4's 185.345 scored 185 pts.
- The cap ``min(N_cap, N_planets)`` is applied to ``N_cap`` *before*
  substituting into the formula.  (Neither validation case hit the cap:
  1 ≤ 5 and 26 ≤ 212.)
- Points are awarded as a single total across the fleet, not per-ship.

At N=1 capital ship the marginal rate is 6 pts per ship; at N=26 against
212 planets it drops to ~7.1 pts/ship average.  The per-ship rate
approaches 8 as ``N_cap → N_planets`` and falls toward 0 as capital ships
pile up without matching planet count.

The full score table is now empirically validated end-to-end with
**zero residual** across 22 player-snapshots (16 at year 2448 + 6 at
year 2504), covering PRTs JOAT / HE / SS / PP / IS / AR / CA, planet
counts 1–212, escort counts up to 1 209, capital ship counts 0–26, and
tech levels up to 24.

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

Whether a player has won is determined by the ``must_meet_count``
combinator: they must satisfy at least ``must_meet_count`` of the
currently-enabled conditions.  The help file confirms that *multiple
players may win on the same turn* ("more than one player can be declared
the winner" / "Multiple players can achieve victory at the same time
(with the same or different conditions)") — the engine does not pick a
single winner from simultaneous qualifiers.

Simultaneous winners (confirmed R5.2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verified with a 2-human-player game
(``stars-reborn-research/original/long-2p-game``) configured with a
single condition (Tech L8 in 2 fields), ``min_years = 100``, and both
players given JOAT + Generalized Research so they would both cross the
threshold on the same turn.  The two players never met in-game.

When both qualified on the same turn, each player received **one** win
message naming the other qualifier.  The message is filled from the
canonical string at ``original-game-strings[183]`` in the extracted
English string table:

.. code-block:: text

   You, along with {0} have been declared the winners of this game.
   You may continue to play though, if you wish to attempt to improve
   your standing among your fellow dictators.

Player 1 saw ``{0}`` = ``Player 2`` and vice versa, because the two had
never met.  For reference, the three win-announcement templates in the
table are:

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - ID
     - Case
     - Template
   * - 181
     - Another empire won (recipient is not a winner)
     - "The forces of {0} have been declared the winner of this game.
       You are advised to accept their supremacy, though you may
       continue the fight."
   * - 182
     - Sole winner (recipient is the only one)
     - "You have been declared the winner of this game.  You may
       continue to play though, if you wish to really rub everyone's
       nose in your grand victory."
   * - 183
     - Joint winners (recipient is one of multiple)
     - "You, along with {0} have been declared the winners of this
       game.  You may continue to play though, if you wish to attempt
       to improve your standing among your fellow dictators."

Confirmed behaviours:

- Win-announcement is **per-recipient**: each winner receives a single
  message that enumerates every *other* qualifier for that turn
  (the reader is always the implicit "You").
- When the recipient has **not** discovered the other qualifier(s),
  they are referred to by the generic label "Player N" where N is the
  player-ID.  (Presumably the race/empire name is used once discovered;
  not yet confirmed.)
- The message explicitly invites continued play ("You may continue to
  play though…"), matching the help-file statement that the game does
  not force-end at victory.

.. todo:: Confirm the wording when the recipient *has* discovered the
   other qualifier(s) — expected to substitute the race short name for
   "Player N" but not yet observed.

Diplomatic Victory (multiplayer)
---------------------------------

In multiplayer, human players may agree to a diplomatic victory — all
remaining players declare a joint winner. This is purely a social convention;
the game engine does not enforce it.

Year-N condition (confirmed R5.2)
---------------------------------

The "Has highest score after N years" condition was tested in
``stars-reborn-research/original/900_turns`` (2-human game,
``highest_score_year = 900``, all other conditions disabled,
``min_years = 100``).  The host was advanced to turn 898 (year 3298),
then individual turns were generated via ``stars.exe -gN``.

* **Turn 900 (year 3300)** — Player 1 was declared winner; both players
  received win-announcement messages on this turn.
* **Turn 901 (year 3301)** — generated normally with no error; the game
  did **not** force-end at year-N.

Each player received one of the standard non-joint templates rather than
template 183:

.. code-block:: text

   [P1, template 182, sole winner]
   You have been declared the winner of this game. You may continue to
   play though, if you wish to really rub everyone's nose in your grand
   victory.

   [P2, template 181, another empire won]
   The forces of Player 1 have been declared the winner of this game.
   You are advised to accept their supremacy, though you may continue
   to fight.

Confirmed:

- The year-N condition is evaluated and the winner declared on the
  *exact* turn N is reached, not the turn after.
- Play continues afterwards exactly as for other victory conditions
  (the help-file invitation "you may continue to play" is honoured).
- Templates **181 and 182** are used for the single-winner case
  (recipient is the winner / recipient is anyone else); template **183**
  is used only for joint winners.  In both 181 and 183 the ``{0}``
  placeholder falls back to ``Player N`` when the recipient has not
  discovered the named player.

The turn counter (``.hst`` / ``.mN`` type-8 payload bytes 10–11) is a
little-endian u16, so the largest representable turn is 65 535 (year
67 935).  Whether the engine clamps before then, rolls over, or carries
into another byte is **untested** — but in practice the year-900
condition triggers long before this matters.
