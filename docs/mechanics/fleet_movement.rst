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

Fuel consumption is a function of **ship mass**, **warp**, and **engine type**.
The authoritative data is in Posey's spreadsheet; per-engine ``.dat`` files are
in ``data/fuel_tables/``.

Fuel table format
~~~~~~~~~~~~~~~~~

Each ``.dat`` file contains rows: ``mass_index fuel_cost_mg``

Where ``fuel_cost_mg`` is milligrams of fuel burned per light-year of travel for
a ship of that mass class at that warp.

.. todo::

   Document the exact formula that maps mass + warp + engine to fuel burn.
   The fuel tables give discrete values; the engine needs an interpolation/lookup approach.

Special engines
~~~~~~~~~~~~~~~

- **Ramscoop engines** (Fuel Mizer, Galaxy Scoop, etc.): can travel at warp 5 or
  warp 6 for free by scooping hydrogen from stars. Above that speed they burn fuel
  normally. The "free" speed varies by engine.
- **Settler's Delight:** warp 1 only, no fuel
- **Quick Jump 5:** cheap; warp 5 max; efficient at low warp

Engines are listed in ``data/fuel_tables/`` with one file per engine.

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

.. todo:: Confirm the "out of fuel" behavior — does it stop completely or crawl?

Open Questions
--------------

.. todo:: Exact fuel consumption formula (mass + warp → mg/ly for each engine)

.. todo:: Interpolation strategy for masses between discrete table entries

.. todo:: "Out of fuel" behavior: stop vs. warp 1

.. todo:: Galaxy Scoop free warp speed (warp 5? warp 6?)

.. todo:: Exact waypoint resolution when multiple arrivals at same planet

.. todo:: IT (Interstellar Traveler) gate travel mechanics

.. todo:: PP (Packet Physics) mass driver packet movement
