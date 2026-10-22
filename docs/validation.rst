Validation Strategy
===================

Overview
--------

The primary correctness criterion for |project| is **behavioral equivalence
with the original** |original| **game engine**. The original ``stars.exe``
executable is the ground truth — an oracle. For any given game state and set
of player orders, our engine must produce the same outcome.

The validation effort is a first-class part of the project, not an afterthought.
Without it, we cannot know whether an implementation is faithful or merely
plausible.

**Scope of equivalence:** We target full equivalence for all deterministic game
mechanics — movement, combat, production, research, scanning, population growth,
planet value — and accept intentional divergence only for CPU player AI behavior,
which is explicitly out of scope.

The Oracle Model
----------------

The original ``stars.exe`` is treated as a black box oracle::

  same inputs → stars.exe  →  outputs A
  same inputs → our engine →  outputs B

  diff(A, B) == ∅   →   engine is correct
  diff(A, B) ≠ ∅   →   engine has a bug

Every divergence is a bug in our engine until proven otherwise. The oracle is
always right.

The oracle runs under Wine on Linux (``sr-old/original/stars.exe``). The
immediate engineering goal is to drive it **without a human operating a GUI** —
headless or near-headless, scriptable, repeatable.

Source Hierarchy and Trust Levels
----------------------------------

Not all reference material is equally trustworthy. This hierarchy governs which
sources can be used for what decisions.

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Source
     - Trust level
     - Use for
   * - ``stars.exe`` (original executable)
     - **Oracle**
     - All correctness decisions. Ground truth.
       Local: ``sr-old/original/stars.exe``
   * - Jeff McBride email on turn order
     - **Primary source**
     - Turn event ordering. Written by a Stars! co-creator.
       Local: ``reference/freestars/Docs/EventOrder2.txt``
   * - Posey's spreadsheet (fuel tables)
     - High — community-validated data
     - Fuel consumption per engine per warp per mass.
       Already extracted to ``data/fuel_tables/``.
       Source: http://wiki.starsautohost.org/files/posey.zip
   * - m.a@stars planet value formula
     - High — spot-checked against observed game data
     - Planet value calculation. Validated against
       ``data/planet_samples/`` CSVs.
       Source: starsautohost.org forum archives
   * - FreeStars community-tested facts (``Notes.txt``)
     - High — labeled by tester per fact
     - Specific behavior facts with attributed testing.
       Local: ``reference/freestars/Docs/Notes.txt``
   * - FreeStars C++ implementation
     - Medium — high-fidelity where complete; incomplete overall
     - Mechanics reference for implemented systems.
       Only 3 documented intentional deviations from Stars!
       Many major systems were never implemented.
       Local: ``reference/freestars/Server/``
       Source: https://github.com/vkholodkov/freestars
   * - starsautohost.org wiki
     - Medium — community documentation, unverified
     - Starting point for mechanics research.
       Source: http://wiki.starsautohost.org
   * - Official Stars! strategy guide
     - Medium — official but player-facing; omits internal formulas
     - Player-visible rules and UI behavior.
       Local: ``sr-old/original/strategy_guide/``

Circular Validation Risk
~~~~~~~~~~~~~~~~~~~~~~~~

A critical pitfall: if our engine and FreeStars both implement the same
community-documented formula, they will agree with each other — but both may
diverge from ``stars.exe`` if the community formula is wrong.

**Agreement between two secondary sources is not validation.** Only agreement
with the oracle counts.

This risk is highest for mechanics where:

- The formula is complex and community documentation is the primary available source
- FreeStars' implementation is the only available reference implementation

In these cases, oracle validation (Layer 2/3) is mandatory before treating the
formula as confirmed.

FreeStars Assessment
~~~~~~~~~~~~~~~~~~~~~

FreeStars warrants a detailed assessment given its scope and stated goals.

**What FreeStars got right:**

- Stated goal was faithful replication of Stars!, not innovation
- ``Docs/Differences.txt`` documents only 3 intentional deviations from the original:

  1. AR + ISB starbase cost stacking (FreeStars: 64%, original: 80%)
  2. Ship designs revealed when transferring fleets (FreeStars reveals them; original does not)
  3. Added "drop and load" transfer order (not in original)

- Where implemented, the C++ code is a useful mechanics reference
- ``Docs/growpop.txt`` contains a community-tested population growth implementation
- ``Docs/Notes.txt`` contains community-tested facts with named testers and test counts

**What FreeStars did not complete** (from ``Docs/EventOrder.txt``):

- Fleet battles
- Bombing
- Production (research, packet launch, ship/starbase construction)
- Mystery Traders
- Fleet transfer and merge
- Starbase and fleet repair
- Mine sweeping and detonation
- Remote terraforming
- CA instaforming
- Inner Strength fleet population growth
- Random events (comets, wormhole jiggle)
- SS spy bonus
- Scanning and patrol orders

**File format note:** FreeStars uses XML for its ``.m``, ``.x``, and ``.hst``
files — not the original Stars! binary format. The format documentation in
``Docs/m_form.txt``, ``x_form.txt``, and ``hst_form.txt`` describes FreeStars'
own schema, not the original binary layout. These files are useful for
understanding the data model (what fields exist) but provide no help for
binary reverse engineering of the original file format.

Test Harness Architecture
--------------------------

The validation test harness is the foundation of all Layer 2 and Layer 3
work. It must be fully automated — no human in the loop — so that assertions
about game behavior can be generated, run, and verified systematically and
repeatably. This is the critical path item for the entire validation effort.

The target workflow for a single test::

  [sandbox .hst]  +  [crafted .x files]
          ↓
    oracle executes (headless)
          ↓
    output .m files
          ↓
    parse specific fields
          ↓
    assert against expected values

Every step must be scripted. A human should never need to touch a mouse to
run a test.

Sandbox Universes
~~~~~~~~~~~~~~~~~

A sandbox universe is a committed ``.hst`` file representing a known, stable
game state designed to isolate a specific mechanic for testing. Each sandbox
is purpose-built:

.. list-table::
   :header-rows: 1
   :widths: 30 55

   * - Sandbox
     - What it isolates
   * - ``sandbox_production_01``
     - 1 player, 1 planet, specific race params. Tests factory/mine output,
       resource calculation, research advancement.
   * - ``sandbox_movement_01``
     - 1 player, fleet at known position, planet at known distance. Tests
       fuel burn, arrival calculation, waypoint resolution.
   * - ``sandbox_combat_01``
     - 2 players, opposing fleets at the same location. Tests battle rounds,
       damage, salvage.
   * - ``sandbox_population_01``
     - 1 player, planet at known hab value and population level. Tests growth
       formula, overcrowding onset.
   * - ``sandbox_scanning_01``
     - 2 players, fleet scanner ranges, cloaked ships. Tests fog of war
       in turn file output.

Sandbox universes live in ``data/test_scenarios/``. Each is a directory
containing the ``.hst`` file, a ``README.rst`` describing the game state and
what it tests, and subdirectories of recorded oracle outputs for each test
case run against it.

Creating sandbox universes initially requires running Stars! to produce the
``.hst`` file for a game configured to match the desired parameters. Once the
``.hst`` binary format is understood, sandboxes can be crafted directly.

Headless Oracle Execution
~~~~~~~~~~~~~~~~~~~~~~~~~

Stars! requires a display — it is a Windows GUI application with no
documented headless mode. Under Linux, ``Xvfb`` (virtual framebuffer) provides
a synthetic X11 display that Wine can target, making Stars! "headless" from the
system's perspective while the application itself runs normally.

The existing ``research/stars_automater.py`` is the seed of this work. It
already launches Stars! under Wine and drives it via ``xdotool``. However, it
has two significant limitations that must be resolved:

1. **Hardcoded pixel coordinates.** Every click is expressed as an absolute
   screen position (e.g., ``xdotool mousemove 306 1536 click 1``). These
   coordinates are valid only for one specific display resolution and window
   geometry. Moving to a different machine or resolution breaks everything.

2. **Game creation only.** The script automates new game creation, not turn
   processing. The critical missing piece is reliably triggering the host
   "Generate Turn" action.

The path forward for reliable headless execution:

**Step 1: Pin the display geometry.**
Run Xvfb at a fixed resolution that matches the hardcoded coordinates in
``stars_automater.py``. This makes the coordinates stable and reproducible on
any machine without changing the script::

  Xvfb :99 -screen 0 2560x1600x24 &
  DISPLAY=:99 wine stars.exe

**Step 2: Investigate auto-processing.**
Determine whether Stars! auto-detects and processes a turn when launched with
a complete set of ``.x`` files in place — i.e., does it process without any
GUI interaction at all? If yes, this eliminates all UI automation complexity
for the turn processing step.

.. todo::

   Test whether Stars! auto-processes when all ``.x`` files are present on
   launch. Run with ``DISPLAY=:99`` (Xvfb), copy ``.hst`` + all ``.x`` files
   to the game directory, launch Stars!, wait for new ``.m`` files to appear.
   This is the first thing to test — if it works, the GUI problem is solved.

**Step 3: If auto-processing fails, automate the single "Generate Turn" action.**
The host turn-processing action in Stars! is a single menu item or button. If
it cannot be triggered automatically, a minimal ``xdotool`` sequence (find
window → click menu item by position) is sufficient. This is far more robust
than automating the full game UI because it targets exactly one, always-present
UI element.

For robustness, target the window by **title and class** (using
``xdotool search --name`` or ``--class``) rather than by geometry, and find
the "Generate Turn" menu item by navigating the menu hierarchy rather than
clicking an absolute coordinate.

.. todo::

   Identify the exact menu path or button that triggers host turn processing
   in Stars!. Record its window title, menu path, and keyboard shortcut if
   any (keyboard shortcuts are more reliable than pixel clicks).

**Step 4: Detect completion by output file appearance.**
Replace all ``time.sleep()`` calls in ``stars_automater.py`` with file-watch
loops: poll for the expected output ``.m`` files to appear rather than
sleeping a fixed number of seconds. This makes the harness reliable across
machines with different Wine/CPU performance.

Harness Script Structure
~~~~~~~~~~~~~~~~~~~~~~~~

The test harness will live in ``research/harness/``:

.. code-block:: text

   research/harness/
     run_turn.py          orchestrator: copy sandbox, write .x files,
                          invoke oracle, wait for output, return .m paths
     oracle.py            Wine + Xvfb management, Stars! launch, turn
                          trigger, output detection
     write_x.py           .x file writer (builds binary orders file)
     parse_m.py           .m file parser (reads binary turn file)
     sandbox.py           sandbox management: load, reset, snapshot
     assertions.py        field comparison helpers and assertion library

**Immediate constraint:** ``write_x.py`` and ``parse_m.py`` require binary
format knowledge. Until the ``.x`` and ``.m`` formats are understood,
the harness can only run with manually-prepared ``.x`` files and cannot
programmatically inspect ``.m`` output. Binary format work (see above)
directly unblocks harness capability.

.. todo::

   Build ``oracle.py``: reliable Xvfb + Wine launch, turn processing trigger,
   output file detection. This is the unblocking task — nothing else in
   the harness can be exercised until oracle execution is reliable.

.. todo::

   Build ``parse_m.py`` incrementally as binary format fields are reverse-
   engineered. Start with the fields needed for the first test scenarios:
   planet population, resource output, fleet position, tech levels.

.. todo::

   Build ``write_x.py`` for the minimal order set needed for early tests:
   no-op turn (empty orders), set research field, set fleet waypoint.

Binary File Formats and Reverse Engineering
--------------------------------------------

**This is the highest-leverage unresolved technical problem.** The sooner the
original binary formats and executable are reverse-engineered, the sooner
validation can be made precise, targeted, and automated. All other validation
work is limited without it.

The oracle communicates via binary files. Understanding them is required
for full validation coverage.

.. list-table::
   :header-rows: 1
   :widths: 15 55 30

   * - File
     - Contents
     - Access needed
   * - ``.hst``
     - Master game state (server-side). Contains the full universe: all
       planets, all fleets, all player states. Never shared with players.
     - Read + write (to craft arbitrary game states)
   * - ``.m``
     - Player turn file. Fog-of-war filtered view of the universe for one
       player. Delivered to the player each turn.
     - Read (to inspect oracle outputs)
   * - ``.x``
     - Player orders file. Written by the client, consumed by the host.
     - Read + write (to supply orders to the oracle)

Approach 1: Fixed-seed play-forward (lowest cost, start here)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create games with known parameters (specific universe seed, specific race,
fixed settings). Run the oracle forward for N turns, capturing ``.m`` files
at each step via Wine automation. Feed the same initial conditions and orders
to our engine, compare outputs at each turn.

**No binary format writing required** — the oracle sets up all game states.
This approach is limited: you can only test states reachable by playing forward
from the initial configuration, which restricts test coverage of edge cases.

Approach 2: Binary format reverse engineering (high cost, high payoff)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fully document the ``.m`` and ``.hst`` binary formats, enabling arbitrary game
state construction and direct inspection of oracle outputs.

**Note:** FreeStars uses XML — its format documentation is not applicable to
the original binary layout. Independent reverse engineering is required.

Tools: `Ghidra <https://ghidra-sre.org/>`_ (NSA open-source reverse engineering
suite), `IDA Pro <https://hex-rays.com/>`_ (commercial), ``010 Editor`` (binary
template editor useful for format exploration).

``stars.exe`` is a 16-bit Windows 3.x NE (New Executable) format binary.
Standard 64-bit disassemblers require configuration or a dedicated NE-format
loader to handle it correctly.

.. todo::

     Determine whether Ghidra's NE loader handles 16-bit Stars! correctly,
     or whether a custom loader/preprocessor is needed.

Known File Structure
^^^^^^^^^^^^^^^^^^^^^

Initial inspection of a real Stars! game (``~/data/stars/test/``, 3-player
Tiny universe, year 1) reveals the following.

**File inventory:**

.. list-table::
   :header-rows: 1
   :widths: 15 12 55

   * - File
     - Size
     - Notes
   * - ``.hst``
     - 3660 B
     - Host master state; largest file
   * - ``.m1``
     - 844 B
     - Human player turn file; richer than CPU files
   * - ``.m2``, ``.m3``
     - ~580 B
     - CPU player turn files; leaner
   * - ``.x1``
     - 47 B
     - Player 1 orders with one change (add Armed Scout to production)
   * - ``.h1``
     - 125 B
     - Unknown — not documented in FreeStars
   * - ``.xy``
     - 600 B
     - Universe coordinate data — not documented in FreeStars

The ``.h1`` and ``.xy`` file types were never implemented by FreeStars (which
used XML and skipped files it didn't need). They require independent reverse
engineering.

**Common file header (12 bytes, identical across all file types):**

.. code-block:: text

   10 20 4A 33 4A 33 82 1B 3F 46 60 2A

``4A 33 4A 33`` is ``"J3J3"`` in ASCII — the Stars! file magic. The remaining
bytes in the header are yet to be identified (version, timestamp, or encryption
parameters).

**The files are encrypted.** Body content after the header shows uniformly
high entropy — no visible ASCII strings, no repeated structures, no alignment
patterns consistent with plain binary. Stars! deliberately encrypts file
content (anti-cheat for multiplayer). This is the primary obstacle to reading
the files and must be resolved before any field-level parsing is possible.

**The ``.x1`` orders file is only 47 bytes for one change.** This confirms
the orders format is delta/sparse — only changed fields are present, not a
full state snapshot. This informs our own orders file design.

Encryption is the first concrete blocker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All parsing work is blocked until the cipher is understood. The common header
is the anchor for finding the cipher routine in Ghidra: the decryption function
will almost certainly read, validate, or use those 12 header bytes. Once the
cipher is identified and the key derivation is understood, all file types
become readable simultaneously.

.. todo::

   Use Ghidra to locate the file read/decrypt routine in ``stars.exe``.
   The common 12-byte header ``10 20 4A 33 4A 33 82 1B 3F 46 60 2A`` is
   the search anchor. Find all references to this byte sequence in the
   disassembly and trace the surrounding decryption logic.

.. todo::

   Once the cipher is known, implement a Python decryptor and apply it to
   each file type to reveal the plaintext binary structure for further mapping.

.. todo::

   Determine whether existing Stars! community tools (Stars! Data Manager,
   starsautohost.org utilities) read ``.m`` files and whether their source
   code is available to bootstrap format knowledge.

Approach 3: Executable reverse engineering (high cost, high payoff)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Disassemble ``stars.exe`` directly to extract implementations of specific
mechanics — particularly formulas where community documentation is incomplete
or contradictory (beam attenuation, exact combat accuracy, overcrowding,
concentration decay).

This is the most authoritative approach for formula extraction: it reads the
formula directly from the code rather than inferring it from observed behavior.
It is not necessary to reverse-engineer the entire executable — targeted
extraction of specific routines is sufficient and tractable.

Modern Reverse Engineering Capabilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is an area where |project| has a genuine advantage over the FreeStars
developers (early 2000s). The tools and techniques available now are
significantly more capable:

**Ghidra** (`ghidra-sre.org <https://ghidra-sre.org/>`_, released 2019 by the
NSA, free and open-source) — includes a full decompiler that produces pseudo-C
from x86 assembly. The FreeStars team had no free decompiler; IDA Pro was
expensive and its Hex-Rays decompiler did not exist until 2007. Ghidra has a
loader for the NE (New Executable) format that ``stars.exe`` uses.

**LLM-assisted interpretation** — decompiled 16-bit pseudo-C is full of
compiler artifacts: register-width integers, segment arithmetic, mangled
variable names, and repeated address calculations that obscure intent. An LLM
can pattern-match algorithmic intent from this noise considerably faster than a
human reading raw assembly. When the decompiled output of a suspected planet
value routine contains a ``sqrt`` call and three accumulator variables, an LLM
can immediately correlate this with the m.a@stars formula and confirm or
refute the match. This capability simply did not exist for the FreeStars team.

**Accumulated community knowledge** — 30 years of play and analysis means we
know roughly what each routine should do before we look at it. This allows
targeted search: locate the routine by its known outputs (e.g., find code
paths that produce values in the −45 to +100 range for planet value) rather
than tracing from entry points.

The Clean-Room Workflow for Executable RE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Disassembly is permitted under the clean-room requirement provided it is used
to extract *specifications*, not *code*. The workflow:

.. code-block:: text

   stars.exe
      ↓  Ghidra disassembly + decompilation
   pseudo-C output  (never committed to repo)
      ↓  LLM + human analysis
   mathematical formula / pseudocode spec
   written in natural language or math notation
      ↓  written into docs/mechanics/*.rst as the authoritative spec
   independent Rust implementation
      ↓  oracle test cases validate behavioral equivalence

The disassembly and pseudo-C are working material, not artifacts. Only the
extracted mathematical specification enters the design documents. The
implementation is then written from that specification, and oracle test cases
provide the evidentiary trail that the implementation matches the original.

The 16-bit NE Format Challenge
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``stars.exe`` is a 16-bit Windows 3.x **NE (New Executable)** format binary.
This is a legitimate technical challenge:

- Code uses 16-bit x86 (real or protected mode segments)
- Segment registers and far pointers make decompiled output messier than
  modern 32/64-bit code
- Ghidra's NE support is less mature than its PE (32-bit Windows) support
- 64 KB segment limit means large data structures span multiple segments

However, these are obstacles to whole-program analysis, not to targeted
formula extraction. A specific routine (e.g., the planet value calculator) fits
within a single segment and can be extracted and analyzed in isolation.

.. todo::

   Verify Ghidra's NE loader handles ``stars.exe`` correctly. Determine
   whether a custom segment map or preprocessor step is needed for the
   16-bit x86 code.

.. todo::

   First target: locate and extract the planet value calculation routine.
   We have the m.a@stars community formula and ``data/planet_samples/``
   validation data — this makes it the ideal first target to calibrate
   the disassembly workflow before tackling unknown formulas.

.. todo::

   Priority formula targets after planet value: overcrowding penalty,
   mineral concentration decay, beam attenuation, missile accuracy with
   computers and jammers. These are the open questions where community
   documentation is weakest and oracle behavioral testing is most difficult
   to make precise.

Validation Layers
-----------------

Validation is organized into four layers of increasing scope and cost.

Layer 1: Formula Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pure mathematical calculations with no dependency on the oracle or Wine.

Covered formulas:

- Planet value (m.a@stars algorithm) — partially validated via ``data/planet_samples/``
- Research cost (``50 × (N+1)²`` and modifiers)
- Miniaturization cost (4% per level above requirement, 25% floor)
- Fuel consumption (per-engine tables in ``data/fuel_tables/``)
- Population growth (growth rate × capacity factor)
- Combat damage (shields, armor, beam attenuation, missile accuracy)
- Score calculation

These are **unit tests** runnable in CI with no Wine dependency. For each
formula, the test asserts that our implementation matches either:

- Community-documented expected values, or
- Values observed in ``data/planet_samples/`` CSVs

Layer 2: Component Validation (oracle required)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Targeted single-mechanic tests. Set up a known game state, apply specific
orders, run exactly one turn through the oracle, compare the specific output
field under test.

Examples:

- Fleet at position X, orders to move at warp W toward planet Y — assert
  position after one turn matches oracle
- Planet with N factories, M colonists, research set to Weapons — assert
  tech level and resource output match oracle
- Two fleets meet in combat — assert both players' battle reports match oracle

These tests isolate one mechanic at a time. Failures have a narrow search
space.

Running component tests requires the headless Wine harness. The oracle is
invoked offline to generate expected outputs; those expected outputs are
committed to the test scenario library and used in CI without Wine.

Layer 3: Full-Game Integration (oracle required)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

End-to-end game runs over many turns. A fixed-seed game with fixed race
parameters is played forward simultaneously through both the oracle and our
engine. Every turn file is compared field by field.

Purpose: catches emergent divergences that component tests miss. A formula
may be correct in isolation but applied in the wrong turn-order phase, or
combined with another formula incorrectly.

The fixed-seed approach is sufficient here. A library of 3–5 standard game
configurations (covering different universe sizes, race combinations, and
player counts) run to year 50–100 provides high confidence.

Layer 4: Regression Suite
~~~~~~~~~~~~~~~~~~~~~~~~~

A committed library of ``(game_state, orders) → expected_outputs`` tuples.
Generated offline using the oracle; no Wine dependency at runtime.

Every commit runs the full regression suite against our engine. Failures
immediately identify which mechanic regressed and in which test scenario.

The regression suite grows over time:

- Layer 1 formula tests are added as formulas are implemented
- Layer 2 component tests are added as mechanics are implemented
- Layer 3 integration snapshots are added after each new mechanic is stable
- Any bug found in production becomes a new regression test before being fixed

Test Scenario Library
---------------------

The test scenario library lives in ``data/test_scenarios/`` (to be created).
Each scenario is a directory containing:

.. code-block:: text

   scenario_name/
     README.rst          what this scenario tests and why
     setup.json          initial game parameters (seed, settings, races)
     turns/
       year_0/
         player_1.m.json   oracle turn file, converted to JSON
         ...
       year_1/
         player_1.orders.json   orders applied this turn
         player_1.m.json        oracle turn file after processing
         ...

Turn files are stored in our JSON format (not the original binary), converted
from the oracle's ``.m`` output using a one-time conversion tool.

.. todo::

   Build the ``.m`` → JSON converter. Requires sufficient binary format
   knowledge to read player turn files.

Known Intentional Divergences
------------------------------

Not all divergences are bugs. This log records intentional deviations from
the original so validation tooling can exclude them from failure reports.

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Area
     - Divergence
     - Status
   * - CPU player AI
     - AI move selection intentionally differs from original. All CPU player
       behavior is excluded from equivalence testing.
     - Accepted
   * - Planet names
     - Name pool extended from 999 to 2852. Name assignment order will differ
       for any game with more than 999 planets.
     - Accepted
   * - RNG behavior
     - If the original uses a specific PRNG sequence, our engine may use a
       different algorithm. Games with the same seed may diverge in random
       outcomes unless we replicate the exact PRNG.
     - Open question — see below

.. todo::

   Determine the original PRNG algorithm and seed interpretation. If we cannot
   replicate it, fixed-seed tests must compare structural properties (e.g.,
   planet count, hab distribution shape) rather than exact values.

Open Questions
--------------

.. todo::

   Establish the headless Wine + Xvfb harness for oracle execution.
   This is the critical path item — no Layer 2 or Layer 3 testing is possible
   without it.

.. todo::

   Survey FreeStars and starsautohost.org tools for existing binary format
   documentation and parsers.

.. todo::

   Determine the original Stars! PRNG algorithm. Fixed-seed reproducibility
   requires matching the original's random number sequence exactly, or
   decoupling test scenarios from RNG-dependent outcomes.

.. todo::

   Build the ``.m`` binary → JSON converter for reading oracle turn files.

.. todo::

   Determine whether ``stars.exe`` host processing can be triggered by a
   command-line flag or requires a scripted GUI interaction (click "Run Turn").

.. todo::

   Define the field-level comparison format for turn file diffing — which
   fields must match exactly, which may differ (e.g., display strings vs.
   computed values), and how to report divergences clearly.
