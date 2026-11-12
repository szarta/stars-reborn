Fleets
======

A **fleet** is a named group of ships at a single map location, moving together
along an ordered list of waypoints. Fleets are how every ship in the game is
tracked: a ship always belongs to exactly one fleet, and a fleet of zero ships
does not exist (it is removed at turn resolution). This page describes the
fleet **data model** and its **per-player visibility**; the movement, fuel, and
waypoint-order rules live in :doc:`/mechanics/fleet_movement`.

Fleet model
-----------

A fleet is host-side ground truth, stored in ``GameState.fleets`` (keyed by
fleet id) and defined by ``schemas/game-state.json``. Its fields:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Field
     - Meaning
   * - ``id``
     - Universe-wide space-object id, unique across **every planet and fleet**
       in the game. A planet id and a fleet id are never equal, so a turn
       message's ``related-object`` and a client "Goto" address either kind by
       the one id (see :doc:`/architecture`).
   * - ``name``
     - Player-assigned fleet name.
   * - ``owner``
     - Owning player id.
   * - ``x``, ``y``
     - Current position in light years. When the fleet is in orbit these equal
       the orbited planet's coordinates.
   * - ``orbiting_planet_id``
     - Planet the fleet orbits, or null in deep space.
   * - ``ship_stacks``
     - Ship composition: one entry per ship design the fleet carries, as a
       ``(design_slot, count)`` pair. A fleet holds only **ship** designs
       (``kind = ship``); starbases live on planets, never in fleets.
   * - ``fuel``
     - Fuel on board (mg), shared across the whole fleet.
   * - ``cargo``
     - Ironium, boranium, germanium, and colonists carried (kT).
   * - ``waypoints``
     - Ordered list of future destinations, each with a travel warp and an
       order to run on arrival (see :doc:`/mechanics/fleet_movement`). The
       current position is ``(x, y)``, **not** a waypoint; an idle fleet has an
       empty waypoint list.
   * - ``repeat_orders``
     - When set, the waypoint chain loops back to the first waypoint after the
       last order runs (automated freighter routes).

A ship's **design** is referenced by slot, not copied into the fleet: a stack
names the owner's ship-design slot (0–15), and the design itself is looked up
from the player's stored designs. This is also how a design learns its
*built-count* — the number of ships of it in existence, summed across the
owner's fleets — which locks a design slot against editing while any ship of it
survives (``orders::design_built_count``).

Per-player visibility (fog of war)
----------------------------------

Like planets, fleets are filtered per player through the single projection
choke point ``game::view::player_view`` before they reach a client. The rule
mirrors the planet observed/unobserved split:

- **Own fleets** — projected in full into the turn file's ``fleets`` array
  (``schemas/response-turn-file.json``), sorted by id. This is the fleet
  analogue of an owned planet being *Observed* with current ground truth.
- **Other players' fleets** — exposed only within scanner coverage, and then
  only partially (position and owner always; fleet name and an aggregate ship
  count when the scan is close enough; never the per-design composition). These
  land in the separate ``scanned-fleets`` array.

Fleet **scanning is not modelled yet**, so ``scanned-fleets`` is currently
always empty — exactly as a planet the player has never scanned stays
*Unobserved*. The growth point is the same predicate that will promote a planet
to *Observed*: when scanner coverage lands, ``player_view`` gains the logic to
populate ``scanned-fleets`` from fleets inside a player's scan range. A fleet a
player cannot see never appears in that player's turn file at all, and the
``player_view_leak`` integration test guards against an opponent's fleet
leaking through.
