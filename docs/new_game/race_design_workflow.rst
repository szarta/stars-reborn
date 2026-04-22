Race Design Workflow
====================

This document covers the UI-facing workflow for configuring player slots and
designing races.  For the mathematical formulae that govern race behaviour in
play, see :doc:`../mechanics/race_design`.  For the on-disk file format and
import from the original game, see :doc:`race_file_format`.

Player Slots
------------

The host defines between 2 and 16 player slots when creating a game.  Each
slot has:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Field
     - Description
   * - ``name``
     - Display name shown in the score sheet.  Defaults to the race name.
   * - ``player_type``
     - ``human`` or ``ai``.  An ``ai`` slot is never exposed to a human player;
       the engine generates its orders every turn.
   * - ``ai_difficulty``
     - Only for ``ai`` slots.  See `AI Difficulty`_ below.
   * - ``race``
     - Inline ``race.json`` object (custom design) or a reference to a
       pre-built race (see `Pre-built Races`_ below).

Race Selection
--------------

When configuring a slot the host (or human player in a lobby) chooses one of:

1. **Load from file** — an existing ``race.json`` saved from the race designer.
2. **Import original** — an original |original| ``.r`` race file, converted on
   import.  See :doc:`race_file_format`.
3. **Pick pre-built** — one of the built-in races bundled with the engine.
   See `Pre-built Races`_ below.
4. **Design new** — opens the race designer to build from scratch.

Race Designer Steps
-------------------

The race designer enforces an **advantage point** budget (net zero or within
the allowed tolerance).  The steps match the original game's wizard pages:

1. **Primary Racial Trait (PRT)** — exactly one; see
   :doc:`../mechanics/race_design` for the full table.
2. **Lesser Racial Traits (LRTs)** — any combination without prerequisite
   violations.
3. **Habitat ranges** — gravity, temperature, radiation.  Each axis may be
   set to immune (always 10 000 hab points) or a min/max preference range.
   Minimum range width: 80°C for temperature.
4. **Economy** — resources per colonist, factory production/cost/operators,
   mine production/cost/operators, growth rate.
5. **Research costs** — Cheap / Normal / Expensive per field.  Expensive
   grants +1 starting level.
6. **Race name and icon.**

The designer must show a running point total and block submission if the
budget is out of range.

Leftover Advantage Points
~~~~~~~~~~~~~~~~~~~~~~~~~

When a race design has points remaining within the allowed tolerance, those
leftover points can be spent on starting bonuses.  The original game's rates
(community source: GameFAQs FAQ v1.11; oracle verification pending):

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Option
     - Rate
   * - Surface minerals
     - 10 kT per point; distributed toward the rarest mineral
   * - Mines
     - 1 mine per 2 points
   * - Factories
     - 1 factory per 5 points
   * - Defenses
     - 1 defense installation per 10 points
   * - Mineral concentration
     - +1% concentration on the rarest homeworld mineral per 3 points

The homeworld's mineral concentration is floored at 30 regardless of depletion,
so the mineral-concentration option has limited practical value.

Saving and Loading
------------------

- The race designer saves a ``race.json`` file to disk.
- The file may be loaded back into the designer for editing.
- Multiple saved races can be maintained; the player picks one when joining a
  game.
- The engine validates the submitted race against the full rules; UI-side
  validation is a convenience only.
- See :doc:`race_file_format` for the schema.

Pre-built Races
---------------

The engine ships with a set of pre-built race definitions used for AI slots
and as starting points for new players.  These are bundled from
``stars-reborn-schemas`` (file: ``builtin_races/``).

**Source:** Decoded from original ``stars.exe`` default ``.r1`` files
(2026-04-22).  Full details in
``stars-reborn-research/docs/findings/default_race_values.rst``.

Hab values: 0–100 index (``0xFF`` = immune).  Temperature: ``°C = (idx−50)×4``.
Radiation: direct mR/yr.  Research cost: ``N``\=Normal, ``E``\=Expensive,
``C``\=Cheap.  Costs: ``[Ir, Bo, Ge, Resources]``.

.. list-table::
   :header-rows: 1
   :widths: 12 7 14 14 14 6 42

   * - Race
     - PRT
     - Grav (0–100)
     - Temp (0–100)
     - Rad (0–100)
     - Grow
     - LRTs / Economy notes
   * - Humanoid
     - JOAT
     - 15–85
     - 15–85
     - 15–85
     - 15%
     - No LRTs; all research Normal; rp=1000 fp=10 fc=10 mp=10 mc=5
   * - Rabbitoid
     - HE (inf.)
     - 10–56
     - 35–81
     - 13–53
     - 20%
     - IFE+TT+CE+NAS; cheap_germ; En/We Exp, Pr Cheap, Bio Cheap; rp=1000 fc=9 cof=17k mc=9
   * - Insectoid
     - WM
     - immune
     - 0–100
     - 70–100
     - 10%
     - ISB+CE+RS; En/We/Pr/Co Cheap, Bio Exp; rp=1000 mp=9 mc=10 com=6k
   * - Nucleotid
     - ? (1)
     - immune
     - 12–88
     - immune
     - 10%
     - ARM+ISB+BET*; all research Expensive; rp=900 mc=15 com=5k. PRT unconfirmed (likely IT)
   * - Antetheral
     - AR (inf.)
     - 0–30
     - 0–100
     - 70–100
     - 7%
     - ARM+MA+NRE+CE+NAS; En/Pr/Co/El/Bio Cheap, We Exp; rp=700 fp=11 cof=18k
   * - Silicanoid
     - CA
     - immune
     - immune
     - immune
     - 6%
     - IFE+UR+OBRM+BET; Pr/Co Cheap, Bio Exp; rp=800 fp=12 fc=12 cof=15k mc=9

``*`` Nucleotid's BET is stored in the flags byte (``0x20``), not in the LRT
bitmask.  Silicanoid's BET IS in the LRT bitmask (bit 12).  The difference
requires further investigation.

.. todo::

   Oracle-confirm Nucleotid's PRT (byte value 1 — likely IT based on ISB+ARM LRTs).
   Oracle-confirm Antetheral's PRT (byte value 5 — likely AR from NRE+MA characteristics).
   Oracle-confirm PRT values 1, 3, 8 (remaining unknown: SS, SD, IT in some order).

AI Difficulty
-------------

AI difficulty controls two independent dimensions:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Dimension
     - Effect
   * - **Starting advantage**
     - Higher difficulty grants the AI boosted starting resources, tech levels,
       or population.  The original game used fixed per-difficulty multipliers.
   * - **Decision quality**
     - Higher difficulty enables more sophisticated order generation (fleet
       routing, production prioritisation, combat targeting).

Difficulty levels (names TBD; matching original game):

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Level
     - Original label
     - Notes
   * - 1
     - Expert
     - Hardest; full starting advantage + best AI logic
   * - 2
     - Good
     - \
   * - 3
     - Average
     - Default for new games
   * - 4
     - Mediocre
     - \
   * - 5
     - Dumb
     - Easiest; no starting advantage

.. todo::

   Verify original game difficulty names and exact starting-advantage
   multipliers per level (resources? tech? population?).

.. todo::

   Determine whether "Computer Players Form Alliances" (game option) changes
   AI targeting logic or just a global preference weight.
