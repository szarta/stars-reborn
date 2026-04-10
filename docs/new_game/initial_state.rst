Initial Game State
==================

After the engine processes a ``POST /games`` request it generates the
universe and sets up each player's initial position.  This document
specifies what that initial state looks like: homeworld configuration,
starting technology, starting fleets, and the shape of the turn 1 output.

Homeworld Setup
---------------

Each player's homeworld is selected from the generated planet pool and
configured identically regardless of which planet was chosen.

Planet position follows the ``player_positions`` setting.  Once the planet is
selected:

1. **Hab values** are set to the midpoint of the race's preferred range on
   each axis.

   - Immune axis: gravity = 1.0 g, temperature = 0 °C, radiation = 50 mR/yr.
   - Values are snapped to the nearest discrete step (see
     :doc:`../mechanics/habitability`).

2. **Minerals** on the surface: 1 000 kT ironium, 1 000 kT boranium, 1 000 kT
   germanium.

3. **Mineral concentrations** are set to 50 for all three minerals on
   the homeworld (unaffected by ``beginner_max_minerals``).

4. **Population** set per race and game options.  See
   :doc:`../mechanics/race_design` for the formula.

5. **Factories and mines** are built up to the race's starting capacity
   from the starting population.

.. todo::

   Confirm homeworld mineral concentrations: is 50 the correct value or does
   the homeworld concentration match the surface amount (1 000 kT is unusual;
   verify against original game files).

.. todo::

   Confirm starting factories and mines formula: does the original game
   pre-build them, or does the player start with resources to build them
   in year 1?

Starting Technology
-------------------

All races start at tech level 3 in all six fields by default.

Modifiers applied in order:

1. **Expensive tech boost:** if a field is set to Expensive *and* the
   "Expensive Tech Boost" checkbox is enabled, that field starts at
   ``max(base, 3)`` — granting the level-3 boost at no extra cost.
   This is a flat +60 advantage-point trade for the starting levels.

2. **PRT tech boosts:** applied as ``max(current, minimum)``; they
   override the base-3 where the PRT minimum is higher.

.. list-table::
   :header-rows: 1
   :widths: 10 50 40

   * - PRT
     - Starting tech minimums
     - Notes
   * - IT
     - Propulsion 5, Construction 5
     - Gate capability requires C5; IT starts with stargates
   * - SD
     - Propulsion 2, Biotechnology 2
     - Mine layer tech focus
   * - WM
     - Energy 1, Propulsion 1, Weapons 6
     - Combat-ready from turn 1
   * - PP
     - Energy 4
     - Mass driver tech requires Energy
   * - CA
     - Biotechnology 6
     - Full terraforming capability from turn 1
   * - JOAT
     - All 6 fields at 3
     - Brings all fields to the base level explicitly
   * - HE, IS, SS, AR
     - No PRT tech boost
     - Start at base 3 (or Expensive-field modifiers only)

.. note::

   IFE (Improved Fuel Efficiency) and CE (Cheap Engines) LRTs each add
   +1 to Propulsion starting level, applied after PRT boosts.

.. todo::

   Oracle-verify starting tech levels. Values sourced from the Python
   reference engine (``objects/player.py``); may contain approximations.

Starting Fleets
---------------

Each player starts with a small fleet sufficient to begin exploration and
colonisation.  Fleet composition varies by PRT.

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - PRT
     - Starting fleet
     - Notes
   * - HE
     - 2× Long Range Scout, 1× Colony Ship
     - Extra scout compensates for small max pop / fast expansion need
   * - IT
     - 1× Long Range Scout, 1× Colony Ship, 1× Privateer (or equivalent
       freighter)
     - IT starts with gate technology; freighter primes the gate network
   * - WM
     - 1× Armed Scout (weapon-equipped), 1× Colony Ship
     - Early offensive capability
   * - SS
     - 1× Cloaked Scout, 1× Colony Ship
     - Stealth advantage from turn 1
   * - AR
     - Unique — lives in starbases; no conventional colony ships
     - See :doc:`../mechanics/race_design` AR section
   * - Others
     - 1× Long Range Scout, 1× Colony Ship
     - Standard complement

All starting ships use the baseline hull designs for the race's tech level.
Fuel tanks are full.  The fleet is orbiting the homeworld at game start.

.. todo::

   Verify per-PRT starting fleet composition against the original game.
   The above is best-guess from community knowledge.  Confirm:

   - Exact hull types (Long Range Scout vs. Scout)
   - Whether any PRT starts with an armed ship
   - IT's additional starting ship type
   - AR's starting state (no fleet at all? starts with an orbital fort?)
   - PP starting fleet (do they get a mass driver immediately?)
   - SD starting fleet (do they get a mine layer?)

.. todo::

   Confirm whether starting fleet ship designs are fixed (named designs the
   engine creates) or whether they are player-editable from the start.

Turn 1 Output Structure
-----------------------

After generation, the engine creates the turn 1 state.  The turn 1 player
file is a subset of the full universe: only what the player can observe from
their homeworld and starting scanner range.

The player file at turn 1 contains:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Section
     - Contents at turn 1
   * - ``player``
     - Race definition, tech levels, resource totals, research allocation
   * - ``planets``
     - Homeworld (fully detailed) + any planets within scanner range
       (hab values and name only — no owner, pop, or minerals)
   * - ``fleets``
     - Starting fleet(s) at homeworld
   * - ``designs``
     - Starting ship designs
   * - ``messages``
     - Welcome message; any game-option notifications
   * - ``scores``
     - If ``public_player_scores`` = true: placeholder row per player;
       otherwise empty until year 20.
   * - ``universe_meta``
     - Planet count, universe size, year number (= 1)

The turn file conforms to ``turn.json`` in ``stars-reborn-schemas``.
See :doc:`../architecture` for the turn/orders data model.

Initial Scanner Coverage
------------------------

Scanner range at turn 1 depends on the race's starting Electronics tech
level and whether it has penetrating scanners:

- Default scanner hull component at Electronics 3: range X ly (TBD).
- NAS (No Advanced Scanners) LRT: only conventional (non-penetrating) range.
- SS PRT: cloaked scout has enhanced scanner capability.

Planets within range are reported with name and hab values but no
infrastructure detail.  Planets outside range are absent from the file.

.. todo::

   Document default scanner range formula and the Electronics tech
   progression for scanner range.  This crosses into
   :doc:`../mechanics/scanning`.
