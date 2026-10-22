Fleet Movement
==============

Warp Speeds
-----------

Fleets travel at warp 1 through warp 9, plus warp 10 (free fuel "safe speed"):

.. list-table::
   :header-rows: 1
   :widths: 15 25 40

   * - Warp
     - Distance/year (ly)
     - Notes
   * - 1
     - 1
     - Very slow
   * - 2
     - 4
     -
   * - 3
     - 9
     -
   * - 4
     - 16
     -
   * - 5
     - 25
     -
   * - 6
     - 36
     -
   * - 7
     - 49
     -
   * - 8
     - 64
     -
   * - 9
     - 81
     -
   * - 10
     - 100
     - Free for ramscoop engines only

Distance = warp² light years per year.

Fuel Consumption
----------------

Fuel consumption is a function of **total ship mass** (hull + components +
cargo), **warp** speed, and the engine's **Fuel Usage Number** (FUN). FUN is
expressed in percent units, where ``100`` is the chart's "100% efficiency"
line: at FUN = 100, **1 mg of fuel moves 200 kT of weight 1 light-year**
(Jason Cawley, advfaq §4.5.1).

Cawley fuel formula:

.. code-block:: text

   fuel_per_ly_mg = (mass_kT / 200) * (FUN / 100) * IFE_factor
                  = (mass_kT * FUN * IFE_factor) / 20000

   IFE_factor = 0.85   # if race has Improved Fuel Efficiency LRT
              = 1.00   # otherwise

Per-segment fuel cost is ``fuel_per_ly_mg * distance_ly``, accumulated across
the fleet's stacks. See FreeStars ``Server/Fleet.cpp::GetFuelUsage`` for the
cargo/free-speed accounting (free-speed stacks ignore cargo mass; fully-loaded
stacks bill ``mass + cargo_capacity``; partial loads bill empty mass and pay
for cargo at the cheapest available stack's rate).

Per-engine FUN tables (warp 1–10) and the ramscoop fuel-gain matrix are in
:doc:`/reference/engines`. FUN values are sourced from Posey's spreadsheet,
validated against in-game tech-browser graphs and cross-checked against
FreeStars's ``rules/MyModRules.xml``.

Free speed and fuel generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each engine has a **FreeSpeed** — the highest warp at which it consumes zero
fuel. Standard (non-ramscoop) engines have FreeSpeed = 1 (warp 1 is always
free; ``FUN[1] = 0``). Ramscoops have higher FreeSpeed values (Settler's
Delight = 6, Galaxy Scoop = 9, etc.) and additionally **generate** fuel at
warps below their FreeSpeed — see the Ram Scoop Fuel Gain Matrix in
:doc:`/reference/engines`. Excess generated fuel beyond tank capacity is
discarded.

Out of fuel
~~~~~~~~~~~

A fleet that exhausts its fuel mid-segment drops to warp 1 (free) for the
remainder of the journey. It does not stop completely.

Waypoints
---------

A fleet has an ordered list of waypoints. Each waypoint has:

- A destination (planet or absolute coordinates)
- Orders at arrival (see below)
- Repeat flag (cycle back to first waypoint after last)

Waypoint orders
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 60

   * - Order
     - Description
   * - None
     - Stop and wait
   * - Colonize
     - Land colony ship; transfer colonists; claim planet
   * - Remote Mine
     - Mine a planet remotely (requires mining hull)
   * - Unload Cargo
     - Transfer cargo to planet or another fleet
   * - Load Cargo
     - Load minerals or colonists
   * - Load Fuel
     - Fill fuel from planet
   * - Patrol
     - Orbit planet; engage enemy fleets
   * - Transfer Fleet
     - Move ships between fleets
   * - Merge Fleet
     - Combine with another fleet
   * - Scrap Fleet
     - Dismantle ships; return minerals
   * - Lay Mines
     - Lay mines at current location (requires mine-layer component)

Cargo Transfer Modes
~~~~~~~~~~~~~~~~~~~~

Load/Unload cargo orders support a **threshold** parameter:

- **Load all**: load as much of the named mineral/colonists as available.
- **Load to X kT**: load the mineral until the fleet carries X kT total.
- **Unload all**: drop everything of the named type to the planet.
- **Unload to X kT**: leave at least X kT on the source planet; only load
  what keeps the planet at or above X.  This is the primary tool for
  maintaining mineral reserves on source planets in repeat routes.

Repeat Orders
~~~~~~~~~~~~~

A waypoint chain with the **repeat** flag set cycles back to waypoint 0 after
the fleet executes the last waypoint's orders.  This enables fully automated
freighter loops.  Repeat orders are compatible with all cargo threshold modes;
a fleet can indefinitely run a route like "load Ironium at Pervo (leave 2000
kT), deliver to Earth" without per-turn player intervention.

Turn Resolution
---------------

Fleet movement runs in the movement phase of each turn:

1. All fleets move simultaneously along their waypoints
2. A fleet moves at most one waypoint per turn
3. If a fleet reaches a waypoint mid-year, it continues to the next waypoint
   with remaining distance
4. At each waypoint destination, orders execute after arrival

.. todo::

   Document the exact movement resolution order when multiple fleets
   arrive at the same planet simultaneously.

Distance Formula
----------------

.. code-block:: text

   distance = sqrt((x2 - x1)² + (y2 - y1)²)   [in light years]

A fleet traveling at warp W covers ``W²`` light years per year. If the destination
is within ``W²`` light years, the fleet arrives this turn.

Fuel Capacity
-------------

Each ship design has a fuel tank capacity (determined by hull). A fleet's total
fuel capacity is the sum of all ships' capacities. Fuel is shared within a fleet.

If a fleet runs out of fuel mid-journey, it drops to warp 1 for the remainder
of travel (consuming no additional fuel).


Fleet Routing
-------------

Each colonized planet with a starbase can have a **route destination** set.
When a ship is produced at a planet that has a route destination, the game
automatically assigns the ship waypoints toward that destination at the best
safe speed (conserving fuel; using stargates when available).

Route destinations chain: if planet A routes to planet B, and planet B routes
to planet C, ships built at A travel A → B → C, stopping at C (which has no
route set).

Route orders are set per planet and apply to all ships built there in that
turn.  They do not affect ships already in flight.

.. todo:: Confirm whether route chains resolve transitively at build time
   (full path pre-calculated) or hop-by-hop (each planet re-routes on arrival).

Stargate Overgating
-------------------

A stargate has two ratings: a **mass limit** (kT, possibly "infinite", encoded
as ``-1``) and a **range limit** (light years, possibly "infinite"). A fleet
that uses a stargate may exceed either limit by up to 5×; beyond 5× the
transit is hard-blocked. Overgated transit always succeeds in moving the
fleet, but inflicts damage and may destroy ships outright.

Rules summary (per the help file and the community "Guts of Overgating"
spec):

- Both mass and distance overgating cause ship damage. Damage is applied per
  ship and accumulates with prior damage; a ship at ≥100% total damage is
  destroyed.
- Overgating damage from a single transit is always strictly less than 100%.
- Distance overgating uses **only the sending gate's range**.
- Mass overgating uses **both gates' mass limits for damage**, but **only the
  sending gate** for the vanishing roll.
- Gates with an "infinite" cap on either axis contribute no damage on that
  axis (treat their ``safe`` factor as 1).
- IT (Interstellar Traveler) races never lose ships to the void from
  overgating, but their ships take the same damage as any other race's.

Per-ship damage formulas
~~~~~~~~~~~~~~~~~~~~~~~~

Let ``sendRange`` be the sending gate's range limit, ``sendMassCap`` and
``recvMassCap`` the sending and receiving gates' mass limits, ``mass`` the
ship-design mass, and ``distance`` the gate-to-gate distance.

**Range damage** (zero if ``distance ≤ sendRange``):

.. code-block:: text

   rdam = (distance - sendRange) / (4 * sendRange)

**Mass damage** (each gate contributes ``safe = 1`` if its cap is infinite or
``mass`` is at or below its cap):

.. code-block:: text

   safe_send = (5 * sendMassCap - mass) / (4 * sendMassCap)
   safe_recv = (5 * recvMassCap - mass) / (4 * recvMassCap)
   mdam      = 1 - safe_send * safe_recv

**Combined damage** (probabilistic combination, rounded down to 1%):

.. code-block:: text

   tdam = mdam + rdam - mdam * rdam

Each ship's damage on transit is ``tdam`` (as a fraction of its armor),
**added** to its existing damage. A ship whose total reaches 100% is
destroyed.

Vanishing probability
~~~~~~~~~~~~~~~~~~~~~

Each surviving ship rolls independently for loss to the void. The mass
component uses the sending gate only; the range component is proportional to
range damage:

.. code-block:: text

   vmass  = (1 - safe_send²) / 3
   vrange = rdam / 3
   vodds  = (1 - (1 - vmass) * (1 - vrange)) * OvergateLossFactor

``OvergateLossFactor`` is ``0`` for IT races and ``1`` otherwise. The result
is rounded down to the nearest 1%.

At the 5× mass limit, ``safe_send = 0`` and ``vmass = 1/3`` — confirming the
"kills 1/3 of your ships at the limit" rule of thumb. Surviving ships at
that limit have already taken ~98% damage.

.. todo:: Oracle-validate the exact rounding rules and confirm the
   sending-only-vs-both-gates question for the mass component of ``vodds``;
   the captured FreeStars snippet uses both gates but the help file and wiki
   say sending only.

Open Questions
--------------

.. todo:: Exact fuel consumption formula (mass + warp → mg/ly for each engine)

.. todo:: Interpolation strategy for masses between discrete table entries

.. todo:: "Out of fuel" behavior: stop vs. warp 1

.. todo:: Galaxy Scoop free warp speed (warp 5? warp 6?)

.. todo:: Exact waypoint resolution when multiple arrivals at same planet

.. todo:: IT (Interstellar Traveler) gate travel mechanics

.. todo:: PP (Packet Physics) mass driver packet movement
