Wormholes
=========

Overview
--------

Wormholes are paired ``SpaceObject`` instances that allow fleets to traverse
between two points in the galaxy in a single turn, bypassing normal warp travel.
Each wormhole has a partner; entering one and selecting *traverse* moves a fleet
to its partner's location.

Wormhole positions are not static: their endpoints jiggle each turn (see
:doc:`turn_resolution` Phase 2 sub-step).

Visibility
----------

Wormhole visibility is **per-player** and follows the same fog-of-war model as
planets and fleets — see :ref:`architecture-discoverable-data` for the data shape.

Position visibility (entry point)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A wormhole's position is visible to a player this turn if and only if the
wormhole lies inside the union of that player's **basic scanner ranges**
(planetary or fleet). Penetrating scan is not required — wormholes are not
cloaked.

When a wormhole goes out of scanner range, the player retains the **last
observed position** as stale intel (mirroring planet last-seen behaviour).
The intel is annotated:

- ``seen_this_turn = false``
- ``last_seen_year`` is the most recent year the wormhole was inside the
  player's scan coverage

The next-turn jiggle is **not** visible to a player who is out of scanner
range — they continue to see the stale position until they re-acquire the
wormhole, at which point the new position replaces the old.

Endpoint linkage (where it leads)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Knowing a wormhole's *position* is distinct from knowing its *partner*.

A player learns the linkage between a wormhole and its partner only by
**physically traversing** the wormhole with one of their fleets. Scanning
both endpoints is **not** sufficient — the player will see two unconnected
wormhole entries until a traversal occurs.

Once learned, the linkage is **sticky**: the player retains knowledge of the
pairing across turns even if neither endpoint is currently in scanner range,
and even after subsequent jiggles. The player does not, however, see the
*current* position of the partner unless that endpoint is also in scanner
range — they only know "this wormhole pairs with the one I previously
observed at coordinates X".

.. todo:: Oracle-verify endpoint-known stickiness across:
   (a) jiggle of either endpoint after traversal,
   (b) loss of scanner coverage on one endpoint after traversal,
   (c) destruction/decay of a wormhole the player has traversed.

Per-player intel record
-----------------------

Each player's turn file (``.m`` equivalent) contains a
``DiscoverableWormholeData`` record per wormhole the player has ever observed:

.. code-block:: text

   DiscoverableWormholeData {
       wormhole_id           : int
       last_seen_position    : SpaceCoordinate    # absent if never seen
       last_seen_year        : int                 # absent if never seen
       seen_this_turn        : bool
       partner_id            : int                 # absent until traversed; sticky once set
       stability             : Stability           # absent until first observation; refreshed on each scan
   }

Wormholes the player has never observed do **not** appear in the turn file
at all (consistent with the "fields never observed are absent" rule for
``DiscoverablePlanetData``).

Engine ground-truth wormhole records, including current paired endpoint,
stability state, and jiggle RNG, live in the host-side ``GameState`` and are
exposed only via the host-token-gated endpoint.

Open Questions
--------------

.. todo:: Wormhole stability levels (rock-solid, stable, mostly stable,
   averagely stable, slightly volatile, volatile, extremely volatile) and
   how they affect jiggle magnitude and traversal damage.

.. todo:: Wormhole spawn/decay rules per turn (referenced in turn_resolution
   Phase 7 random events).

.. todo:: Whether traversal damage applies to all ships or only certain hull
   classes.
