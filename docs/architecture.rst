Architecture
============

|project| is a faithful open-source clone of |original| — the classic 16-bit
Windows 4X space strategy game by Jeff Johnson and Jeff McBride (1995/1996).

Project Tenets
--------------

1. **Open game** — freely distributable, modifiable, and playable
   (cross-platform, no licensing restrictions).
2. **Faithful reproduction** — all original mechanics must be
   reverse-engineered, documented, and implemented. A veteran |original| player
   must feel immediately at home.
3. **Respectful enhancement** — a "Legacy" mode preserves original behavior
   exactly; optional fixes address known bugs and micromanagement pain points.
4. **Collaborative** — acknowledge prior clone efforts, community research,
   and contributors.

Overview
--------

|project| is a **client/server game**. The engine and UI are fully decoupled
services that communicate exclusively over HTTP. There is no in-process
language interop between them.

.. code-block:: text

    ┌────────────────────────────┐        HTTP        ┌────────────────────────────┐
    │       Game Client (UI)     │ ◄────────────────► │    Game Engine (Rust)      │
    │                            │                    │                            │
    │  Renders universe state    │                    │  Universe generation       │
    │  Collects player orders    │                    │  Turn processing           │
    │  Submits orders to engine  │                    │  Victory detection         │
    │  Displays turn results     │                    │  Authoritative data model  │
    │  Enforces UI-level rules   │                    │  Validates all inputs      │
    └────────────────────────────┘                    └────────────────────────────┘

**Single-player:** a thin launcher starts the engine on ``localhost:PORT``
and opens the client. On exit the launcher shuts down the engine. The user
sees a single application.

**Multiplayer:** the client connects to a remote engine host. No code changes
required on either side — just a different host address.

This architecture enables third-party clients. Any HTTP-capable implementation
that conforms to the engine API contracts is a valid client.

Repository Structure
--------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Repository
     - Purpose
   * - ``stars-reborn-design``
     - This repo. Authoritative developer reference: mechanics, API contracts,
       architecture decisions. Read before writing engine or UI code.
   * - ``stars-reborn-engine``
     - Rust game engine. HTTP API server, turn processing, data model authority.
   * - ``stars-reborn-ui``
     - Python/PySide6 view layer. Pure HTTP client, no game logic.
   * - ``stars-reborn-schemas``
     - JSON Schema definitions for all shared game objects and API contracts.
       Depended on directly by both engine and UI; bundled into the app.
   * - ``stars-reborn-game``
     - Integration repo. CI/CD builds engine + UI + schemas into a single
       ``.exe`` (Windows) or ``AppImage`` (Linux). User-facing README and
       high-level integration tests.
   * - ``stars-reborn-research``
     - Local only (not on GitHub). Research workspace: original executable
       analysis, Wine automation, Ghidra reverse-engineering. Confirmed
       findings graduate to this repo.

Engine Responsibilities
-----------------------

The engine is a standalone Rust binary exposing an HTTP API. It has four core
jobs:

**1. Universe Generation**
  Generate the initial star map: planet placement, hab values, mineral
  concentrations, homeworld setup per race, starting fleets. Seeded for
  reproducibility.

**2. Turn Processing**
  Each year, resolve the full turn sequence across all player orders (see
  :doc:`mechanics/turn_resolution`). Generate per-player turn files containing
  only what that player can observe.

**3. Victory Detection**
  After each turn, evaluate all victory conditions and notify affected players.

**4. Data Model Authority**
  The engine is the single source of truth for all game rules and data
  structures: technology tree, race trait definitions, ship hull definitions,
  valid component data, habitat formulae, schema versions. Clients retrieve
  this data from the engine rather than hardcoding it.

Core Data Model
---------------

Game Object Model
~~~~~~~~~~~~~~~~~

The universe contains a set of ``SpaceObject`` instances, each at a
``SpaceCoordinate``. Every object a player can observe or interact with is
one of these subtypes:

.. uml::

   @startuml
   abstract class SpaceObject {
       id : int
       location : SpaceCoordinate
   }

   class Planet {
   }

   class Fleet {
       warpSpeed : int
       fuel : int
   }

   class MineralPacket {
   }

   class Salvage {
   }

   class Wormhole {
   }

   class Minefield {
   }

   class Starbase {
   }

   class Game {
   }

   class Universe {
   }

   class Player {
   }

   class Race {
   }

   SpaceObject <|-- Planet
   SpaceObject <|-- Fleet
   SpaceObject <|-- MineralPacket
   SpaceObject <|-- Salvage
   SpaceObject <|-- Wormhole
   SpaceObject <|-- Minefield

   Universe "1" *-- "0..*" SpaceObject

   Planet "1" o-- "0..1" Starbase
   Planet "1" o-- "0..*" Fleet : orbiting
   Planet "1" *-- "numPlayers" DiscoverablePlanetData

   Fleet "1" *-- "1..*" Ship

   Wormhole "1" -- "1" Wormhole : paired

   MineralPacket *-- Cargo
   Fleet *-- Cargo

   Game "1" *-- "1..*" Player
   Game "1" *-- "1" Universe

   Player "1" -- "1" Race
   Player "1" *-- "0..20" ShipDesign
   Player "1" *-- "0..20" StarbaseDesign
   Player <|-- NPC
   @enduml

.. _architecture-discoverable-data:

Per-Player Visibility (Discoverable Data)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``DiscoverablePlanetData`` is the per-player fog-of-war record for a planet.
Each planet carries one such record per player slot; a player's turn file
includes only the record for their own slot.

The record is in one of three states for a given player (see
:doc:`mechanics/scanning` for the full rules):

1. **Never observed** — every contents field absent. Identity fields (id,
   name, position) come from the shared .xy data and are always present.
2. **Observed before, not currently penetrating-scanned** — contents fields
   hold values **as they were at last observation**; ``years_since_last_scan``
   tells the client how stale they are. Ground truth may have drifted
   (terraforming, mining, population growth) — the player will not see the
   change until they re-scan.
3. **Currently penetrating-scanned** — contents fields hold current
   ground-truth values; ``years_since_last_scan = 0``.

Contents fields subject to the three-state rule: ``gravity``, ``temperature``,
``radiation``, the three mineral concentrations, the three surface mineral
amounts, ``population``, ``owner``, ``factories``, ``mines``, ``defense``,
starbase presence/design. **Fields the player has never observed are absent
(not zero, not null — literally not in the JSON.)** This is critical: a UI
that reads a "0" for population on an unobserved planet would be wrong.

The same per-player intel pattern applies to other ``SpaceObject`` types that
are scanner-gated. ``DiscoverableWormholeData`` records last-seen position,
``seen_this_turn``, and a sticky ``partner_id`` (set only on traversal); see
:doc:`mechanics/wormholes`. ``DiscoverableFleetData`` and ``DiscoverableMinefieldData``
follow the same convention — fields never observed are absent, and intel
about the most recent observation is retained across turns.

Engine ground truth (full planet state for every player slot, full wormhole
linkages, uncloaked fleet positions, AI internals) lives in the host-side
``GameState`` and is exposed only via host-token-gated endpoints. The single
choke point that derives a player's turn file from ``GameState`` is the place
to enforce — and test — that no host-only field can leak into a per-player
view.

Each ``Player`` may have at most **20 ship designs** and **20 starbase designs**
active simultaneously. Scrapping a ship frees its design slot only when no
ships of that design remain.

``NPC`` is a computer-controlled player; it uses the same data model as a
human ``Player`` and the same order format.

Ship Classification
~~~~~~~~~~~~~~~~~~~

Ships are classified at turn-resolution time by hull type and loadout. These
predicates are used by scoring, combat, and order validation:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Predicate
     - True when
   * - ``isCapital()``
     - Hull is a capital ship class (battleship, dreadnought, nubian, etc.)
   * - ``isUnarmed()``
     - Ship carries no weapons (beam weapons, torpedoes, or bombs)
   * - ``isBomber()``
     - Ship carries at least one bomb
   * - ``isFreighter()``
     - Hull has cargo capacity and no weapons
   * - ``isFuelTransport()``
     - Hull is a fuel transport hull type
   * - ``isEscort()``
     - Armed, non-capital, non-bomber ship

These map directly to scoring categories (capital ships ×3, unarmed ×0.5,
armed ×1) and to combat stack behavior. See :doc:`mechanics/combat` and
:doc:`mechanics/victory`.

.. todo::

   Confirm exact hull types that qualify as ``isCapital()`` against original
   game data.

Every game year produces two artifacts per player:

**Turn file** (engine → player)
  A fog-of-war filtered snapshot of the universe from that player's
  perspective. Read-only. Contains everything the player is allowed to see
  this year: planet states, visible fleets, messages, battle reports, scores.

**Orders file** (player → engine)
  The player's instructions for this year. Submitted once per year per
  player. Contains fleet waypoints, production queue changes, research
  allocation, ship design changes, messages to other players.

The engine is a pure function over these inputs::

    (universe_state, orders[all_players]) → (new_universe_state, turn_files[all_players])

Fog of war is applied by the engine at turn-file generation time. A player's
turn file does not contain data they cannot see — it is absent, not hidden.
This is essential for multiplayer integrity.

Orders as Desired State
~~~~~~~~~~~~~~~~~~~~~~~

Orders are expressed as **desired state**, not commands. The orders file for
a fleet says "fleet 12 waypoints: [Scorpius, Antares]", not "add Antares to
fleet 12's waypoint list". This makes orders idempotent and easy to display
as a diff against the previous turn's defaults.

Unset fields in the orders file carry forward from the previous year's
defaults — the same behavior as the original |original|. A player who never
touches research allocation does not lose their research settings.

File Format
-----------

All turn files and orders files are JSON. Requirements:

- A ``format_version`` field at the top level of every file (integer,
  increments on breaking schema changes). Allows engine and UI to detect
  mismatches.
- Pretty-printed JSON on disk (human-inspectable, diffable, debuggable).
- Minified + gzip for network transport in online play. This is a
  transport-layer concern; the application never sees compressed data.

Size at scale (Huge/Packed universe, ~750 planets worst case):

- Raw JSON turn file: ~500 KB
- After gzip: ~40 KB

Network size is not a practical concern.

Schemas for all file formats live in ``stars-reborn-schemas``.

Engine API
----------

The engine embeds an HTTP server (axum) and listens on a configured port.
The API has two distinct surfaces.

Data Model API
~~~~~~~~~~~~~~

Read-only endpoints exposing the authoritative game rules. Clients use these
to build the tech browser, populate the ship designer, understand race traits,
and know valid parameter ranges. The data model does not change during a game.

.. code-block:: text

    GET /model/version                  → engine version + API schema version
    GET /model/technologies             → full technology tree
    GET /model/technologies/{id}        → single technology item
    GET /model/race/traits              → PRT/LRT definitions and point costs
    GET /model/ships/hulls              → all hull definitions
    GET /model/schemas                  → JSON schemas for all request/response types

Game API
~~~~~~~~

Stateful endpoints for gameplay:

.. code-block:: text

    POST /games                                         → create new game
    GET  /games/{game_id}                               → game metadata
    GET  /games/{game_id}/turns/{year}/status           → per-player submission status
    GET  /games/{game_id}/turns/{year}/players/{pid}    → turn file for player
    PUT  /games/{game_id}/turns/{year}/orders/{pid}     → submit player orders (idempotent)
    POST /games/{game_id}/turns/{year}/skip/{pid}       → generate AI orders, mark skipped
    GET  /games/{game_id}/turns/{year}/ai-orders/{pid}  → AI-suggested orders (not submitted)

There is no explicit "process turn" endpoint. Processing is a side effect of
all player slots being either ``submitted`` or ``skipped``.

Skip, AI, and Computer Players
-------------------------------

These three cases share a single code path in the engine:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Case
     - What happens
   * - Computer player
     - AI generates orders for the slot; never exposed to a human.
   * - Skipped human player
     - AI generates orders for the slot; human had no opportunity to act.
   * - AI-assisted human
     - AI generates suggested orders (``GET .../ai-orders``); human modifies
       and submits.
   * - Full human
     - Human generates orders from scratch and submits.

Computer player and skipped human are identical from the engine's perspective.

Validation Philosophy
---------------------

The engine validates all inputs before acting on them. Clients may enforce
rules locally for immediate feedback (e.g., grey out a component the player
hasn't researched), but the engine never trusts that client-side validation
occurred.

Validation layers:

1. **Structural** — does the input conform to the JSON schema for this request
   type? (Schemas in ``stars-reborn-schemas``.)
2. **Rules-logical** — is this race design legal given the PRT/LRT combination
   and advantage point totals? Is this ship design valid for the player's tech
   level and hull type?
3. **Game-state** — does the player have authority to issue these orders? Is it
   this player's turn?

Engine Internal Structure
--------------------------

.. code-block:: text

    engine/
      http/    axum router and request handlers
               (thin layer: parse request → call game logic → serialize response)
      game/    all game logic: turn processing, fog of war, AI, scoring
      store/   game state persistence (JSON files on disk)

The ``http`` layer has no game logic. The ``game`` layer has no HTTP knowledge.
The core logic is independently testable without an HTTP server.

Client Architecture
-------------------

The client is a pure HTTP consumer. It:

- Retrieves the data model from ``/model/`` endpoints at startup
- Polls for turn readiness
- Retrieves its turn file (``GET .../players/{pid}``)
- Renders the universe from that data
- Collects player orders through the UI
- Submits orders (``PUT .../orders/{pid}``)

The client does **not**:

- Implement game logic (movement calculations, combat, research accumulation)
- Maintain authoritative copies of the tech tree or rule definitions
- Trust its own validation as sufficient — the engine always makes the final call

The reference client is Python/PySide6 (``stars-reborn-ui``), but any
HTTP-capable implementation is a valid client.

Authentication
--------------

- **Local play**: no authentication. Engine binds to ``127.0.0.1`` only.
- **Online play**: a join token per player slot, issued at game creation and
  shared out of band. Passed as ``Authorization: Bearer <token>`` on all
  requests. The engine enforces that player A cannot read player B's turn file
  or submit orders for player B.

The API shape does not change between local and online play.

Packaging
---------

.. code-block:: text

    stars-reborn/
    ├── launcher     ← thin binary: starts engine + client, manages lifecycle
    ├── engine       ← game engine binary
    ├── schemas/     ← bundled from stars-reborn-schemas
    └── client/      ← UI application files

The launcher is what becomes the ``.exe`` (Windows) or ``AppImage`` (Linux).
For multiplayer server deployments, the engine binary is run standalone.

Technology Stack
----------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Component
     - Choice
     - Rationale
   * - Game engine
     - Rust
     - Performance for large maps and parallel turn processing; safe
       concurrency; ships as a standalone binary.
   * - Engine HTTP layer
     - axum (Rust)
     - Native to the engine binary; no separate process needed.
   * - Reference client
     - Python 3 / PySide6
     - Cross-platform Qt6; QPainter space map; Win95 aesthetic reproducible
       via QStyle/QPalette.
   * - Client↔Engine transport
     - HTTP + JSON
     - Language-agnostic; enables third-party clients; identical interface
       for local and remote play.
   * - Schemas
     - JSON Schema (``stars-reborn-schemas``)
     - Structural validation enforced by engine; shared artifact for both
       engine and UI.
   * - Save files
     - JSON (gzip), ``.sr`` extension
     - Engine-side persistence; human-inspectable.
   * - Tests
     - pytest (client) + cargo test (engine)
     - Headless Python tests; Rust unit + integration tests.
   * - Packaging
     - Rust launcher + PyInstaller / appimage-builder
     - Single executable ships engine + client together.

Clean-Room Implementation Requirement
--------------------------------------

|project| must be a **clean-room independent implementation** of |original|'s
mechanics. This is a legal and architectural constraint, not merely a
preference.

**What this means in practice:**

- If the original ``stars.exe`` source code were ever discovered or made
  available, we cannot read it, incorporate it, or use it as a reference.
  Even accidental exposure creates IP contamination.
- No contributor may have read the original source while working on
  |project|. If this occurs, that contributor must be isolated from the
  affected systems.
- The implementation must be derived solely from: behavioral observation of
  the original executable (the oracle), community-documented specifications,
  and mathematical descriptions independently derived from those sources.

**What this does not prohibit:**

- Running ``stars.exe`` as a black-box oracle to observe outputs.
- Disassembling ``stars.exe`` to extract behavioral specifications —
  provided the extracted knowledge is written as mathematical formulas or
  prose, and the implementation is written independently from those
  descriptions (never from the disassembly itself). See
  ``stars-reborn-research`` for Ghidra tooling.
- Reading FreeStars C++ source, since FreeStars is an independent
  re-implementation under its own license.

**Why oracle test cases are our evidence:**

A library of structured test cases — specific inputs fed to ``stars.exe``
producing specific outputs, with our engine required to match them — serves
as the auditable record of design intent. Each test case is a traceable
citation. This evidentiary record protects the project.

Open Design Questions
---------------------

.. todo::

   Authentication scheme for online play — token issuance, rotation, and
   what happens when a player loses their token mid-game.

.. todo::

   Whether the engine manages multiple concurrent games (a "host" process)
   or is instantiated once per game. Multiple-game hosting changes the
   store layout and complicates port binding.

.. todo::

   Turn processing: synchronous (request blocks until done) or asynchronous
   (202 Accepted, poll status)? Processing may be slow for large universes
   with many AI players and combat resolutions.

.. todo::

   Computer player AI design — what information does the AI see, and how
   does it interface with the same order-generation code used for skip?

.. todo::

   Replay / spectator mode — can a non-player observe a game in progress?
   Requires a separate observer turn file with full or delayed visibility.

.. todo::

   Hot-reload of orders: can a player re-submit orders before the turn is
   processed (last write wins)? The UI should reflect whether resubmission
   is permitted.
