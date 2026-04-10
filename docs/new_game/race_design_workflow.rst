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

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Race name
     - PRT
     - Notes
   * - Humanoid
     - JOAT
     - Balanced all-rounder; the original game's default human race
   * - Rabbitoid
     - HE
     - Extreme growth, small max pop; aggressive expansion style
   * - Insectoid
     - WM
     - Combat-focused; high weapons start
   * - Nucleotid
     - PP
     - Packet physics specialist
   * - Antethereal
     - AR
     - Alternate Reality; unique growth model
   * - Silicanoid
     - CA
     - Claim Adjuster; broad habitability via cheap terraforming

.. todo::

   Confirm exact pre-built race stat values against original ``stars.exe``
   default race definitions.

.. todo::

   Define full set of pre-built races and their exact parameters (hab ranges,
   economy values, LRTs).

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
