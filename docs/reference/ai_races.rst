AI Race Names
=============

When the engine creates AI players for a new game, each is assigned a name
drawn at random from a fixed pool of 24 names.  The name has no relationship
to the AI's PRT or the game difficulty.

The 24 names and their plural forms are:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Singular
     - Plural
   * - American
     - Americans
   * - Berserker
     - Berserkers
   * - Bulushi
     - Bulushis
   * - Cleaver
     - Cleavers
   * - Crusher
     - Crushers
   * - Eagle
     - Eagles
   * - Felite
     - Felites
   * - Ferret
     - Ferrets
   * - Golem
     - Golems
   * - Hawk
     - Hawks
   * - Hicardi
     - Hicardis
   * - Hooveron
     - Hooverons
   * - House Cat
     - House Cats
   * - Kurkonian
     - Kurkonians
   * - Loraxoid
     - Loraxoids
   * - Mensoid
     - Mensoids
   * - Nairnian
     - Nairnians
   * - Nee
     - Nees
   * - Nulon
     - Nulons
   * - Picardi
     - Picardis
   * - Rush'n
     - Rush'ns
   * - Tritizoid
     - Tritizoids
   * - Ubert
     - Uberts
   * - Valadiac
     - Valadiacs

Assignment rules:

- Each AI player in the game gets a unique name (no two AIs share a name in
  the same game).
- The name is independent of the AI's PRT, LRT set, difficulty tier, and
  universe size.
- The original game UI shows six AI template labels (Robotoids, Turindrones,
  Automitrons, Robotills, Cybertrons, Macinti) in the Custom Game dialog.
  These are internal archetypes and never appear as in-game names.  Even when
  all 16 player slots in a game share a single AI template, none of the 16
  retains the template name — confirmed 2026-04-25 via
  ``stars-reborn-research/original/all_ai_players_standard_robotill/`` (16
  Standard-tier Robotill AIs; all 16 received distinct pool names, "Robotill"
  never appeared).  This is the same mechanism the engine uses for human-player
  name collisions (see :ref:`name-collision-resolution` below); AI templates
  always trigger reassignment because their archetype labels are never valid
  in-game names.

Difficulty and PRT
------------------

Difficulty controls which PRT archetypes are weighted for selection, not
which names are used.  The observed distribution across 260 games:

.. list-table::
   :header-rows: 1
   :widths: 15 17 17 17 17 17

   * - PRT
     - Easy
     - Standard
     - Harder
     - Expert
     -
   * - HE
     - rare (~0%)
     - ~6%
     - ~16%
     - ~40%
     -
   * - SS
     - ~18%
     - ~47%
     - ~8%
     - ~2%
     -
   * - CA
     - ~40%
     - ~13%
     - ~4%
     - ~1%
     -
   * - IS
     - ~38%
     - ~15%
     - ~4%
     - ~2%
     -
   * - PP
     - ~1%
     - ~15%
     - ~47%
     - ~37%
     -
   * - AR
     - ~1%
     - ~1%
     - ~19%
     - ~17%
     -

Easy games prefer builder/defensive PRTs (CA, IS, SS).  Harder and Expert
games strongly favour aggressive PRTs (HE, PP, AR).

.. _name-collision-resolution:

Name collision resolution
-------------------------

The engine maintains one global rule across all player types: every player
in a game must have a unique race name, drawn from (or reassigned to) the
24-name pool above.  AI players always reassign (template labels like
"Robotill" are never valid in-game names — see assignment rules above).
Human players keep their loaded race name unless it collides with an
earlier slot, in which case the duplicate is reassigned from the same pool.

Confirmed for human collisions by two 16-human experiments under
``stars-reborn-research/original/``:
``all_human_players_humanoid/`` (R5.2) and
``all_human_players_rabbitoid/`` (added 2026-04-25).  In both runs
every player loaded the same race; Player 1 kept the loaded race name
("Humanoid" / "Rabbitoid") and the remaining 15 received distinct
names from the AI pool.

Observed assignment across the three 16-player runs (P1 column shows the
loaded source-race name in parentheses where it was preserved; the Robotill
run is all-AI, so P1 is reassigned):

.. list-table::
   :header-rows: 1
   :widths: 8 24 24 24

   * - Slot
     - Humanoid run (16 humans)
     - Rabbitoid run (16 humans)
     - Robotill run (16 AIs)
   * - P1
     - *Humanoid* (preserved)
     - *Rabbitoid* (preserved)
     - Ubert
   * - P2
     - Loraxoid
     - Hooveron
     - House Cat
   * - P3
     - House Cat
     - Ubert
     - Nee
   * - P4
     - Hicardi
     - Nulon
     - Tritizoid
   * - P5
     - Nee
     - Bulushi
     - Hicardi
   * - P6
     - Felite
     - Crusher
     - Nulon
   * - P7
     - Kurkonian
     - Picardi
     - Nairnian
   * - P8
     - Ferret
     - Rush'n
     - Cleaver
   * - P9
     - Mensoid
     - House Cat
     - Golem
   * - P10
     - Cleaver
     - Kurkonian
     - Eagle
   * - P11
     - Nairnian
     - Eagle
     - Mensoid
   * - P12
     - Nulon
     - Berserker
     - Rush'n
   * - P13
     - Hooveron
     - Nee
     - Crusher
   * - P14
     - Rush'n
     - Mensoid
     - Valadiac
   * - P15
     - Eagle
     - Golem
     - Hawk
   * - P16
     - Ubert
     - Nairnian
     - Felite

Confirmed behaviours:

- **P1 deterministically keeps the loaded race name when that name is a
  valid in-game name.**  Confirmed across 2,880 games (288 games × 10
  PRTs) in the ``race_fleet_permutation_games`` corpus.  No exceptions.
- The disambiguation pool is the **same 24-name AI race-name list** in
  the table above.  Across 43,200 corpus reassignments, all 24 pool
  names appear; no name outside the pool was ever observed.
- Player 1 is reassigned only when the loaded name is *not* itself a
  valid in-game name.  The all-AI Robotill run (template label
  "Robotill" — not a valid in-game name) confirms slot 0 is reassigned
  when the loaded name is unsuitable; the two human runs (loaded names
  "Humanoid", "Rabbitoid" — both valid) confirm slot 0 is preserved.

.. note:: Stars Reborn engine implementation

   The original Stars! game produces deterministic per-PRT name+icon
   reassignment tables (see :ref:`collision-determinism` below for the
   research-side investigation).  Stars Reborn intentionally does
   **not** replicate the original's exact algorithm — instead the
   engine performs a uniform-random draw from the unused-pool subset
   when reassigning a colliding slot.  This produces the same
   user-visible invariant (every player has a unique name from the
   24-pool) without depending on undocumented details of the original
   algorithm.

Icon collision resolution
-------------------------

Race **icons** also carry a per-game uniqueness invariant: no two players
in the same game may share an icon (out of the 32 icons indexed 0–31, see
``icon_index`` in :doc:`../new_game/race_file_format`).  When loaded races
collide on icon, the engine reassigns one of the conflicting slots.

Confirmed 2026-04-25 by four oracles under
``stars-reborn-research/original/``:

- ``same_icon_different_name/`` — 2-player game with two distinct race
  files (``androids.r1``, ``robots.r1``), both configured with
  ``icon_index = 0`` but otherwise different (different names, slightly
  different stats).
- ``all_human_players_humanoid/`` — 16 humans, same loaded race.
- ``all_human_players_rabbitoid/`` — 16 humans, same loaded race.
- ``all_ai_players_standard_robotill/`` — 16 AIs, same template.

Same-icon 2-player result:

.. list-table::
   :header-rows: 1
   :widths: 10 25 20 20

   * - Slot
     - Name
     - Source ``icon_index``
     - Resolved ``icon_index``
   * - P1
     - Android
     - 0
     - **10** (reassigned)
   * - P2
     - Robot
     - 0
     - 0 (preserved)

16-player resolved icons (no two players in any game share an icon):

.. list-table::
   :header-rows: 1
   :widths: 8 18 24 24 24

   * - Slot
     - Name (humanoid)
     - icon (humanoid)
     - icon (rabbitoid)
     - icon (robotill)
   * - P1
     - Humanoid / Rabbitoid / Ubert
     - 15
     - 13
     - 30
   * - P2
     -
     - 28
     - 24
     - 0
   * - P3
     -
     - 17
     - 9
     - 17
   * - P4
     -
     - 3
     - 23
     - 29
   * - P5
     -
     - 14
     - 14
     - 25
   * - P6
     -
     - 24
     - 12
     - 5
   * - P7
     -
     - 29
     - 15
     - 15
   * - P8
     -
     - 16
     - 17
     - 6
   * - P9
     -
     - 22
     - 19
     - 24
   * - P10
     -
     - 25
     - 26
     - 9
   * - P11
     -
     - 27
     - 8
     - 16
   * - P12
     -
     - 8
     - 6
     - 8
   * - P13
     -
     - 5
     - 16
     - 26
   * - P14
     -
     - 0
     - 21
     - 10
   * - P15
     -
     - 18
     - 10
     - 11
   * - P16
     -
     - 2
     - 11
     - 19

Confirmed behaviours:

- The icon pool has 32 entries (indices 0–31).  Within each game the
  resolved icons are pairwise unique, drawn from this pool.
- **On collision, exactly one slot keeps the source icon and the rest
  get reassigned** — confirmed in 2,880/2,880 corpus games and all
  four small oracles.
- All 32 icons appear in the corpus reassignments (43,200 draws); no
  icons are excluded.

.. note:: Stars Reborn engine implementation

   As with names, Stars Reborn does not replicate the original's
   exact icon-reassignment algorithm.  The engine preserves one
   slot's source icon and uniformly draws random unused icons for
   the colliding slots.  Choice of which slot keeps the source icon
   is implementation-defined (a reasonable default: the lowest slot
   index that has the source icon — i.e., let slot N keep it and
   reassign slots N+1 through M).

.. _collision-determinism:

Resolution determinism (research note)
--------------------------------------

The ``race_fleet_permutation_games`` corpus
(``stars-reborn-research/original/race_fleet_permutation_games/``,
2,880 games) confirms that the original Stars! game produces fully
deterministic per-PRT ``slot → (name, icon)`` reassignment tables —
no RNG is involved.  The full canonical tables and analysis are in
``stars-reborn-research/docs/findings/race_collision_canonical_mappings.rst``.

Stars Reborn intentionally diverges from this behavior in favour of
a simpler random-draw implementation (see notes above), so the
specifics of the original algorithm — including the per-PRT keeper
slot, the IS/SS coincidence, and the content-based ordering function
that distinguishes corpus runs from identical-clone runs — are
recorded in research as historical findings rather than as engine
requirements.

Methodology
-----------

AI race-name pool and PRT distribution: 260 games (65 per difficulty × 4
difficulties, across all 5 universe sizes with 13 seeds each) decoded from
the type-6 Race/Player block of each ``.hst`` file.  Race names are stored
at the tail of that block using the nibble-packed encoding (see
:doc:`../new_game/race_file_format`).  Every AI player record in all 260
games was decoded and cross-tabulated.

Collision-resolution determinism: 2,880 games (288 games × 10 PRTs) from
``stars-reborn-research/original/race_fleet_permutation_games/``.  Each
game has 16 ``.r1`` source races sharing PRT, name ("Humanoid"), and icon
(0) but with varying tech permutations.  Resolved ``slot → (name, icon)``
mappings extracted from each ``.mN`` file via
``stars_file_parser::name::decode_names`` plus the byte-6 icon decode.
Comparison against per-PRT canonical mappings: zero variation across 288
games per PRT.
