Turn Resolution Order
=====================

.. note::

   The sequence below is sourced from a **direct statement by Jeff McBride**
   (original Stars! developer, Mare Crisium), preserved in the FreeStars
   project documentation (``freestars/Docs/EventOrder2.txt``,
   rec.games.computer.stars 1996-06-27).  Sub-step details from the FreeStars
   community ``EventOrder.txt`` are also incorporated and are rated medium trust.
   Core ordering from McBride is treated as authoritative (equivalent to the
   strategy guide).  Individual steps still benefit from oracle confirmation —
   see ``stars-reborn-research/docs/open_questions/turn_resolution_order.rst``.

Each year, the |original| engine processes events in the following order. |project| must
reproduce this sequence exactly for behavioral fidelity.

Sequence
--------

**Phase 0 — Apply player orders**

  Load the ``.hst`` file, then apply each player's ``.x`` orders: split/merge
  fleet instructions, production queue changes, waypoint assignments, research
  setting, battle plans, and ship designs.  When two players' by-hand cargo
  transfers conflict (both grabbing the same salvage), a coin flip resolves it.

**Phase 1 — Waypoint 0 tasks** *(before any movement)*

  Each fleet executes its current-location waypoint order.  Unload operations
  are processed before load operations so that exchanges work.  Colonization
  and ground combat at waypoint 0 resolve here.

  W0 tasks cannot be blocked by enemy fleets arriving later — a colonizer
  already in orbit that is given a Colonize task at W0 will colonize before any
  attacker arrives.

**Phase 2 — MT and packet movement**

  Mystery Traders advance.  In-space mineral packets (already in flight) advance
  toward their targets.  PP packets terraform during this step.  All fleets
  chasing an MT or packet update their waypoints to the new location.

  **Sub-step:** Wormhole endpoints jiggle/degrade/shift (after packets, before
  fleet movement). The new position is visible to a player only if the wormhole
  is inside that player's basic scanner coverage this turn; otherwise the
  player retains the last observed position as stale intel until the wormhole
  is re-acquired. See :doc:`wormholes` for the full visibility model.

**Phase 3 — Fleet movement**

  All fleets move along their waypoints.  Fleet movement includes: minefield
  hits (damage/speed reduction), fuel exhaustion (fleet stops or slows), wormhole
  traversal, and stargate jumps.  Circular-chase fleets spiral in (1/10th
  movement × 10 iterations).

**Phase 4 — IS fleet growth; salvage and packet decay**

  Inner Strength colonists aboard freighters grow (conceptually simultaneous
  with movement).  In-space mass packets and salvage lose a fraction of their
  cargo each year.  SD minefield remote detonation occurs here (after movement,
  before mining).

**Phase 5 — Mining**

  Each planet extracts minerals: ``mines × rate × concentration / 100 / 10`` kT
  per mineral.  Concentration degrades slightly.

**Phase 6 — Production**

  All production queues run: factories, mines, defenses, ships, starbases,
  terraforming, alchemy, packets.  Research resources are credited.

  Minerals mined in Phase 5 are available for production this same year.
  Newly-launched packets (from packet launch production items) can reach their
  destination this turn if close enough.

  SS spy tech bonus is applied here (after the galaxy total of tech spent is
  known).

**Phase 7 — Population growth; research; random events**

  Population grows (or declines on red worlds).  Research fields advance if
  enough resources have accumulated.  Random events fire (comet strikes, MT
  appearances, wormhole spawning).

  Refueling at starbases occurs after random events, before battle.

**Phase 8 — Battles**

  At every location where opposing players' fleets meet and at least one is
  armed, a battle resolves.  Surviving fleets remain; destroyed ships become
  salvage.

  *Important:* destination waypoint tasks (W1) have NOT yet occurred.  A fleet
  ordered to colonize that arrives this turn will fight first — the colony is
  not yet established.

**Phase 9 — Bombing and invasion**

  Fleets with bombers attack undefended planets (no defending starbase).  Ground
  invasions are also resolved here.

**Phase 10 — Waypoint 1 tasks** *(destination tasks)*

  Fleets execute their destination waypoint orders: colonize, unload/load cargo,
  transfer minerals, scrap, etc.  Mine-laying occurs here (NOT during movement).
  CA instaforming occurs here.

**Phase 11 — Minesweeping**

  Fleets with mine-sweep weapons reduce enemy minefields.  Minefield decay
  (annual percentage loss) also occurs after mine-laying.

**Phase 12 — Repair**

  Starbases and fleets repair damaged ships.

**Phase 13 — Scanning; patrol**

  Scanner coverage is computed.  Patrol orders are assigned to fleets targeting
  in-range enemies.

**Phase 14 — Output**

  The updated ``.hst`` and per-player ``.m#`` files are written.

Notes
-----

* **Packets precede fleets** (Phase 2 before Phase 3).  A packet and a fleet
  sent to the same destination in the same turn: the packet arrives first
  (arrives in Phase 2); the fleet arrives in Phase 3 and battles in Phase 8.
  Colonization order: packet impact then fleet arrival.

* **Mine-laying is W1 (Phase 10)**, not during movement.  A fleet ordered to lay
  mines cannot mine the corridor it is flying through that same turn.  Enemy
  fleets moving through that corridor in Phase 3 will not hit those mines until
  the following year.

* **Battles are post-production, post-growth** (Phase 8 after Phase 6–7).
  Population growth has already occurred for the turn when battles fire.

* **W0 colonization is safe from interception.**  W1 colonization (arriving
  fleet) is not — the arriving fleet fights before it colonizes.

.. todo::

   Confirm each phase ordering with oracle tests.  Priority sub-questions
   (each is a distinct observable outcome):

   - **Packets vs. fleet movement**: Phase 2 before Phase 3 (McBride confirms;
     oracle test to verify).
   - **Mine-laying vs. fleet traversal**: Phase 10 vs. Phase 3 (McBride + FreeStars
     confirm mine-laying is W1; oracle to verify).
   - **Battle vs. bombing**: Phase 8 before Phase 9 (McBride confirms; oracle to verify).
   - **Bombing vs. population growth**: Phase 9 after Phase 7 (McBride confirms;
     oracle to verify).
   - **Newly-launched packets reaching destination same turn** (Phase 6 sub-step;
     needs oracle confirmation of exact range cutoff).

   See ``stars-reborn-research/docs/open_questions/turn_resolution_order.rst``.
