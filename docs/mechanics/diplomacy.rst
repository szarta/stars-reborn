Player Relations (Diplomacy)
============================

Each player holds a **relations vector** — one setting per other player, chosen
from **Friend**, **Neutral**, or **Enemy**. Relations are set in the Player
Relations dialog and gate several engine behaviours. This document is the
implementation contract for the relations model and every action it affects.

Relations are **one-directional**: *A*'s stance toward *B* is independent of
*B*'s stance toward *A*. A player may declare another a Friend without that
being reciprocated, and the engine always reads the specific direction each
mechanic requires.

The relations model
-------------------

For each ordered pair ``(source, target)`` of distinct players, store one
relation value:

.. list-table::
   :header-rows: 1
   :widths: 14 20 66

   * - Value
     - Relation
     - Notes
   * - ``0``
     - Neutral
     - Default at game start.
   * - ``1``
     - Friend
     - The privileged relation; unlocks the friendly behaviours below.
   * - ``2``
     - Enemy
     -

At new-game setup, all cross-player relations default to **Neutral**, except
when the game option that starts everyone hostile is set, in which case every
cross-player relation defaults to **Enemy**. A player's relation to itself is
unused.

.. note::

   This model matches the original game byte-for-byte. The in-memory array, the
   three radio-button encodings, and every behavioural gate below were
   confirmed by static analysis of the original executable (an exhaustive
   enumeration of all code that reads the relations array). See the research
   record *Player Relations — Permitted Actions* for addresses and the full
   reader list.

Combat (co-location and attacking)
----------------------------------

Relations gate combat through each fleet's battle-plan **"Attack Who"**
setting. For a candidate opposing player, a fleet will engage iff:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Attack Who
     - Engages the candidate when…
   * - Nobody
     - never
   * - Enemies
     - the candidate's relation is **Enemy** (``2``)
   * - Enemies and Neutrals
     - the candidate's relation is **not Friend** (``!= 1``)
   * - Everyone
     - always
   * - A specific player
     - the candidate is that player

Consequence: **mutually-Friendly players co-orbit and pass without fighting**
under the default plans ("Enemies", "Enemies and Neutrals"), because Friend is
excluded from both. Fighting a Friend requires deliberately setting the battle
plan to "Everyone" or naming that player. Friendly worlds and fleets also
render with the friendly colour on the map. See :doc:`combat`.

Stargate transit
----------------

A fleet may jump through a stargate only if the starbase at **each** end
(source **and** destination) is owned by **the fleet's owner** or by a player
who has set the **fleet's owner** as a **Friend**:

   ``allowed(gateOwner, fleetOwner) = (gateOwner == fleetOwner) or
   relations[gateOwner][fleetOwner] == Friend``

Note the direction: it is the **gate owner's** stance toward the travelling
player that matters, not the traveller's stance toward the gate owner. A
one-sided Friend declaration by the gate owner is sufficient. If either end
fails the test, the jump is refused (the original reports "the starbase … is
not owned by you or a friend of yours" for the source end, and "the planet at
each end must be owned by you or a friend of yours" for the destination). See
:doc:`fleet_movement`.

Minefields
----------

Relations exempt Friends from minefield interactions:

- A fleet **triggers** (is slowed or destroyed by) a minefield only if its
  owner is **not Friendly** to the field's owner.
- A fleet or starbase **sweeps** a minefield only if the field's owner is **not
  Friendly** to the sweeper.

Mutually-Friendly players therefore neither detonate nor sweep each other's
minefields.

Remote mining (NOT relation-gated)
----------------------------------

Remote mining is **independent of relations**. The sole gate is **planet
occupancy**:

- Remote miners add minerals **only on an unowned planet**.
- An **inhabited** planet — owned by anyone, including a Friend or yourself —
  rejects the order ("the planet is inhabited"). This is the same regardless of
  relation; you cannot remote-mine a friendly world any more than an enemy one.
- **AR** (Alternate Reality) is the sole exception: an inhabited planet does
  not produce the rejection message for an AR fleet, but no remote-mine yield
  is applied either — AR's extraction from its own worlds runs through normal
  planet production, not the remote-mine order.

Planetary defenses do **not** gate the remote-mine order. See
:doc:`fleet_movement` for the Remote Mine waypoint task.

Actions that are NOT relation-gated
-----------------------------------

For the avoidance of doubt (confirmed by the exhaustive reader enumeration):

- **Fleet merge** requires the *same owner*, never merely a Friend.
- **Remote mining** gates on planet occupancy only (above).
- **Production and economy** never consult relations.
