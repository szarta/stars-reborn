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
  These are internal archetypes and never appear as in-game names.

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

Methodology
-----------

Confirmed empirically by generating 260 games (65 per difficulty × 4
difficulties, across all 5 universe sizes with 13 seeds each) and decoding
the type-6 Race/Player block from each ``.hst`` file.  Race names are stored
at the tail of that block using the "StarsText" nibble encoding, documented
in the decompiled community tooling (``StarsHostCreator``/``StarsHostEditor``
source).  Every AI player record in all 260 games was decoded and the name,
plural, and PRT fields were extracted and cross-tabulated.
