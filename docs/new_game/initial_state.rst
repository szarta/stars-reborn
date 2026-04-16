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

   - All PRTs except AR: **10 factories, 10 mines, 10 defenses.**
   - AR (Alternate Reality): **no installations** — the Installations flag
     is not set on AR homeworlds; mines, factories, and defenses are absent.

   .. note::

      These counts are independent of the race's economy parameters
      (colonists-operate-factories, etc.).  The starting 10/10/10 appears
      to be a fixed game constant, not derived from the starting population.

Starting Population
-------------------

Normal (non-Accelerated BBS) starting population:

- **All PRTs except PP:** 25 000 colonists on the homeworld.  With LSP: 25 000 × 70% = 17 500.
- **PP (Packet Physics):** 30 000 colonists total across two starting planets:

  - Homeworld: 20 000 colonists.
  - Second planet: 10 000 colonists.
  - With LSP (70%): 21 000 total — 14 000 (homeworld) + 7 000 (second planet).

  Oracle-confirmed (human race, SamplePP.m1): homeworld (Cerebus) 20 000, second planet (Clay) 10 000.

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

   **PP (Packet Physics) starts with two planets** in non-tiny universes.
   Oracle corpus confirms ``PlanetCount = 2`` in the turn-1 type-6 block for
   PP in all map sizes except Tiny (where only one homeworld fits at the
   required minimum spacing).  The second planet is not a random colony —
   it appears to be a guaranteed second starting world specific to the PP PRT.

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
   * - PP
     - Both starting planets have a mass driver; fleet details otherwise unconfirmed
     - Oracle-confirmed (SamplePP.m1): both planets have mass driver installations.
       See "Starting Population" above for the 20 000 / 10 000 colonist split.
   * - Others
     - 1× Long Range Scout, 1× Colony Ship
     - Standard complement

All starting ships use the baseline hull designs for the race's tech level.
Fuel tanks are full.  The fleet is orbiting the homeworld at game start.

.. todo::

   Verify per-PRT starting fleet composition against the original game.
   The above is best-guess from community knowledge + oracle corpus notes.
   Confirm all of the following (R2.3):

   - Exact hull types (Long Range Scout vs. Scout)
   - Whether any PRT starts with an armed ship
   - IT's additional starting ship type and whether it arrives with a stargate
   - AR's starting state (no conventional fleet; does it start with an
     orbital fort / starbase already placed?)
   - PP starting fleet and second planet fleet/installations
   - SD starting fleet (mine layer hull confirmed by strategy guide; verify
     component loadout)

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
