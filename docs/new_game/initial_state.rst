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

2. **Mineral concentrations** are random per homeworld — not fixed at any
   value.  Oracle corpus (130+ homeworlds across all map sizes and difficulty
   tiers) shows concentrations spanning roughly 30–126 for each mineral.
   ``beginner_max_minerals`` is believed to affect non-homeworld planets only.

3. **Minerals on the surface** vary with concentration and are not a fixed
   1 000 kT.  Observed homeworld surface minerals in the oracle corpus range
   from roughly 100 kT to 800+ kT per mineral; the exact formula relating
   concentration to initial surface amount is not yet determined.

4. **Population** set per race and game options.  See
   :ref:`accelerated-bbs-pop` below and :doc:`../mechanics/race_design`.

5. **Factories, mines, and defenses** are pre-built at game start — the
   player does not spend year-1 production to create them.

   Oracle-confirmed values (turn-1 ``.m`` files, 130+ games):

   - All PRTs except AR: **10 factories, 10 mines, 10 defenses** on the
     homeworld.
   - AR (Alternate Reality): **no installations** — the Installations flag
     is not set on AR homeworlds; mines, factories, and defenses are absent.
   - IT second planet (Molybdenum in oracle): **10 mines, 4 factories,
     0 defenses** — the second IT starting planet receives a reduced package.

   .. note::

      The homeworld 10/10/10 is independent of economy parameters and
      appears to be a fixed game constant.  However, choosing
      ``leftover_spend = mines``, ``factories``, or ``defenses`` in race
      design may increase the respective count beyond 10.  This has not yet
      been researched; see ``open_questions/leftover_spend_starting_values``.

Starting Population
-------------------

Normal (non-Accelerated BBS) starting population:

- **Most PRTs:** 25 000 colonists on the homeworld.  With LSP: 25 000 × 70% = 17 500.
- **PP (Packet Physics) and IT (Interstellar Traveler):** Both start with two
  colonised planets using the same 20 000 / 10 000 split:

  - Homeworld: 20 000 colonists.
  - Second planet: 10 000 colonists.
  - With LSP (70%): 21 000 total — 14 000 (homeworld) + 7 000 (second planet).

  Oracle-confirmed for PP (human race, SamplePP.m1): homeworld (Cerebus) 20 000,
  second planet (Clay) 10 000.

  Oracle-confirmed for IT (``race_fleet_permutation_games/IT/game_0001/IT0001.m1``):
  homeworld (Beethoven) 20 000, second planet (Molybdenum) 10 000.

Growth rate does **not** affect normal starting population — it determines year-over-year growth only,
not the initial colonist count.  (Oracle-confirmed across GR 1%–20% for non-PP PRTs; R2.1 closed.)

.. _accelerated-bbs-pop:

Accelerated BBS Starting Population
-------------------------------------

When the game option ``accelerated_bbs`` is enabled, each player's starting
population on their homeworld is boosted by an amount that scales with the
race's growth rate.

Formula (Python engine ``turn.py``, citing SAH wiki Accelerated_BBS_Play;
also confirmed by FreeStars open-source source):

.. code-block:: text

   ap_bonus     = 5 000 × growth_rate_percent   (growth_rate_percent as integer 1–20)
   homeworld    = base_pop + ap_bonus
   second_world = (base_pop + ap_bonus) / 4     [PP and any other multi-start PRT]

Where ``base_pop`` is the normal starting population: 25 000 for all PRTs except PP (see
above), or × 0.70 with LSP.

.. note::

   PP's ``base_pop`` in the Accelerated BBS formula is unconfirmed — it may be 30 000
   (the PP normal base) rather than 25 000.  The second-world formula and the AP bonus
   scaling for PP+BBS both need oracle verification.  (R2.1 partially open)

Examples:

.. list-table::
   :header-rows: 1
   :widths: 15 20 20 20 25

   * - GR%
     - Bonus
     - Homeworld (no LSP)
     - Homeworld (LSP)
     - Second world (no LSP)
   * - 5%
     - 25 000
     - 50 000
     - 35 000
     - 12 500
   * - 10%
     - 50 000
     - 75 000
     - 52 500
     - 18 750
   * - 15%
     - 75 000
     - 100 000
     - 70 000
     - 25 000
   * - 20%
     - 100 000
     - 125 000
     - 87 500
     - 31 250

The commonly cited figure "4× normal = 100,000" is the 15% growth rate case.
It is *not* a fixed multiplier — population scales linearly with growth rate.

.. todo::

   Oracle-validate the Accelerated BBS formula against multiple growth rates
   (e.g., 5%, 10%, 20%) to confirm the 5 000 × GR scaling.  PP+BBS starting
   population (both homeworld and second-planet amounts) also needs oracle
   confirmation; PP's ``base_pop`` in the BBS formula may differ from the
   standard 25 000.  (R2.1 partially open)

Starting Technology
-------------------

Starting tech is computed as follows (applied in order, taking the maximum
at each step):

1. **Base level: 0** in all six fields for all PRTs.

2. **PRT tech minimums** raise specific fields.  Oracle-confirmed values
   from turn-1 ``.m`` files (130+ games); unconfirmed PRTs marked:

   .. list-table::
      :header-rows: 1
      :widths: 10 50 40

      * - PRT
        - Starting tech minimums
        - Status
      * - JOAT
        - All 6 fields ≥ 3
        - Oracle-confirmed
      * - CA
        - Biotechnology ≥ 6
        - Oracle-confirmed
      * - SS
        - Electronics ≥ 5
        - Oracle-confirmed
      * - PP
        - Energy ≥ 4, Propulsion ≥ 4
        - Oracle-confirmed (all corpus PP designs include IFE; see note)
      * - AR
        - Energy ≥ 1, Propulsion ≥ 1
        - Oracle-confirmed (all corpus AR designs include IFE; see note)
      * - IT
        - Propulsion ≥ 5, Construction ≥ 5
        - Oracle-confirmed (human race, basic_it.r1)
      * - WM
        - Weapons ≥ 6, Energy ≥ 1, Propulsion ≥ 1
        - Oracle-confirmed (human race, basic_wm.r1)
      * - SD
        - Propulsion ≥ 3, Biotechnology ≥ 2
        - Oracle-confirmed (human race, SampleSD.m1)
      * - HE, IS
        - None
        - Oracle-confirmed

   .. note::

      PP and AR corpus designs all include the IFE LRT (see step 3 below).
      It is not yet confirmed from oracle data whether PP's Propulsion=4
      is a PRT minimum or IFE applied to a lower PRT base.  The table
      above reflects observed values; the split between PRT and IFE
      contribution is unresolved for these two PRTs.

3. **Expensive tech boost (EB):** if the race has the "Expensive Tech
   Boost" flag set, every field whose research cost is ``75% extra``
   is raised to ``max(current, 3)``.

4. **LRT Propulsion bonus:** IFE (Improved Fuel Efficiency) and CE
   (Cheap Engines) each add +1 to the Propulsion starting level.
   Applied after all other modifiers.

**Oracle examples** (harder/expert AI templates, turn-1 ``.m`` corpus):

.. list-table::
   :header-rows: 1
   :widths: 10 30 10 40

   * - PRT
     - Relevant LRTs
     - EB?
     - Observed starting tech (E/W/P/C/El/B)
   * - JOAT
     - (none)
     - No
     - 3 / 3 / 3 / 3 / 3 / 3
   * - HE
     - IFE
     - No
     - 0 / 0 / 1 / 0 / 0 / 0
   * - SS
     - IFE
     - No
     - 0 / 0 / 1 / 0 / 5 / 0
   * - CA
     - IFE + all-Expensive fields
     - Yes
     - 3 / 3 / 4 / 3 / 3 / 6
   * - IS
     - CE + all-Expensive fields
     - Yes
     - 3 / 3 / 4 / 3 / 3 / 3
   * - PP
     - IFE + mixed costs
     - Yes
     - 4 / 0 / 4 / 0 / 0 / 0
   * - AR
     - IFE
     - No
     - 1 / 0 / 2 / 0 / 0 / 0

Starting Fleets
---------------

Each player starts with a small fleet sufficient to begin exploration and
colonisation.  Fleet composition varies by PRT.

.. note::

   **PP and IT both start with two planets** in non-tiny universes.  Oracle
   corpus confirms ``PlanetCount = 2`` for both PRTs.  For PP both planets carry a
   Mass Driver 5 starbase (homeworld = Space Station; second planet = Orbital Fort
   "Accelerator Platform"); for IT both planets carry a Stargate 100/250
   (the IT PRT's defining game-start feature).

IT Starting Fleet (oracle-confirmed)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Confirmed from ``race_fleet_permutation_games/IT/game_0001/IT0001.m1`` and
client inspection (IT + ARM + CE + ISB, ``leftover_spend = surface_minerals``).

**Ship designs:**

.. list-table::
   :header-rows: 1
   :widths: 5 22 20 53

   * - Slot
     - Name
     - Hull
     - Components
   * - 0
     - Smaugarian Peeping Tom
     - Scout
     - Daddy Long Legs 7, Fuel Tank, Bat Scanner
   * - 1
     - Mayflower
     - Colony Ship
     - Daddy Long Legs 7, Colonization Module
   * - 2
     - Stalwart Defender
     - Destroyer
     - Daddy Long Legs 7, Fuel Tank, Battle Computer, 2× Crobmnium,
       Alpha Torpedo, Laser, Bat Scanner
   * - 3
     - Swashbuckler
     - Privateer
     - Daddy Long Legs 7, Laser, Alpha Torpedo, 2× Crobmnium, Bat Scanner
   * - 4
     - Potato Bug
     - Midget Miner
     - Daddy Long Legs 7, 2× Robo-Midget Miner

**Fleet positions at game start:**

- Beethoven (homeworld): 2× Scout, 1× Colony Ship, 2× Destroyer, 2× Privateer,
  1× Midget Miner (fleet 5), 1× Midget Miner (fleet 6)
- Molybdenum (second planet): 2× Scout

**Starbases:**

- Beethoven: design named **"Starbase"** (Space Station hull) — 4 weapon slots
  (8/16 Laser), 4 shield slots (8/16 Mole-skin Shield), Stargate 100/250.
- Molybdenum: **"Porthole to Beyond"** (Orbital Fort hull) — 2 shield slots
  (6/12 Mole-skin Shield), 2 weapon slots (6/12 Laser), Stargate 100/250.

Starting ship designs are **pre-named and pre-loaded** by the engine — the
player receives them at turn 1 as fixed designs, not a blank slate.

.. note::

   The above was confirmed with ``leftover_spend = surface_minerals``.  Fleet
   composition and design names are not expected to vary with leftover_spend,
   but this has not been systematically verified across all five options.  See
   ``open_questions/leftover_spend_starting_values`` for the open research item
   on how leftover_spend affects starting installations and surface minerals.

Summary table (all PRTs)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - PRT
     - Starting fleet
     - Notes
   * - IT
     - 2× Scout, 1× Colony Ship, 2× Destroyer, 2× Privateer, 2× Midget Miner
     - Oracle-confirmed (see above).  Scouts split 2/2 across both planets.
       Both planets have Stargate 100/250 starbases.
   * - HE
     - 2× Scout, 3× Mini-Colony Ship, 2× Midget Miner
     - Hull types confirmed from one LRT permutation (ARM+ISB+CE, game_0001).
       3 colony ships instead of 1.  Mini-Colony Ship uses Settler's Delight engine
       (the only engine available to HE colony ships).
       Starbase: Space Station "Starbase", no Stargate.
   * - CA
     - 2× Scout, 1× Colony Ship, 1× Mini-Miner (terraforming), 2× Midget Miner
     - Hull types confirmed from one LRT permutation.  Mini-Miner carries Orbital
       Adjusters; count may vary with starting Construction tech.
       Starbase: Space Station "Starbase", no Stargate.
   * - SS
     - 2× Scout, 1× Small Freighter (cloaked), 1× Colony Ship, 2× Midget Miner
     - Hull types confirmed from one LRT permutation.  Scout uses penetrating scanner.
       Small Freighter carries Transport Cloaking.
       Starbase: Space Station "Starbase", no Stargate.
   * - WM
     - 1× Scout (armed), 1× Colony Ship, 2× Midget Miner
     - Hull types confirmed from one LRT permutation.  Only 1 scout; it carries a
       beam weapon.  Weapon type depends on starting Weapons tech.
       Starbase: Space Station "Starbase", no Stargate.
   * - IS
     - 2× Scout, 1× Colony Ship, 2× Midget Miner
     - Hull types confirmed from one LRT permutation.  No PRT-unique design.
       Starbase: Space Station "Starbase", no Stargate.
   * - SD
     - 2× Scout, 1× Colony Ship, 2× Mine Layer (normal), 2× Mine Layer (speed),
       2× Midget Miner
     - Hull types confirmed from one LRT permutation.  Two mine layer designs:
       one lays normal mines, one lays speed mines.  Mine layer type and
       component loadout depend on starting Propulsion tech.
       Starbase: Space Station "Starbase", no Stargate.
   * - AR
     - 1× Scout, 1× Colony Ship (Orbital Construction Module), 2× Midget Miner
     - Oracle-confirmed (ARM+ISB+CE, game_0001).  AR colony ship deploys a copy
       of the non-deletable "Starter Colony" Orbital Fort design when given Colonize
       orders; AR population lives on that starbase (destroyed starbase = dead pop).
       No mass driver; Space Station starbase has 4×(8/16 Laser), 4×(8/16 Mole-skin Shield).
       No second planet.
   * - PP
     - 2× Scout + 1× Colony Ship + 2× Midget Miner at homeworld; 1× Scout at second planet
     - Oracle-confirmed (ARM+ISB+CE, game_0001).  Both starting planets have Mass Driver 5
       starbases: homeworld = Space Station "Starbase"; second planet = Orbital Fort
       "Accelerator Platform" (2× 6/12 Laser, 2× 6/12 Cow-hide Shield, Mass Driver 5).
       See "Starting Population" above for the 20 000 / 10 000 colonist split.
   * - JOAT
     - 1× Armed Probe, 1× Long Range Scout, 1× Colony Ship, 1× Medium Freighter,
       1× Destroyer, 1× Mini-Miner, 2× Midget Miner
     - Oracle-confirmed (ARM+ISB+CE, game_0001).  Richest starting fleet of any PRT.
       Armed Probe carries a beam weapon.  Destroyer carries beam + torpedo + armor.
       Space Station starbase, no Stargate or mass driver.  No second planet.

.. note::

   The hull and count observations in this table come from one LRT combination
   (ARM + ISB + CE, ``race_fleet_permutation_games/*/game_0001/``).
   **Hull types, component loadouts, design names, and ship counts are all dependent
   on PRT, LRT, and the resulting starting tech levels** and may differ for other
   combinations.  The permutation corpus (384 games × 16 players per PRT) covers all
   LRT+tech combinations; full analysis is pending corpus generation and bulk decode (R2.3).

.. todo::

   Complete R2.3 — Starting fleet generation rules per PRT:

   - Bulk-decode all permutation games once corpus generation completes
   - Determine which hull slots are PRT-fixed vs. tech-dependent
   - Map: (PRT, starting tech levels) → (component choices, design names)
   - Confirm whether AI-template design names differ from human-player design names
   - AR, PP, JOAT: generate dedicated oracle games and decode
   - Whether designs are player-editable from turn 1 or locked (all PRTs)

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
