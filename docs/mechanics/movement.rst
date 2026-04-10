Fleet Movement
==============

Speed
-----

Fleet speed is measured in warp factors (Warp 1–10). Distance traveled per turn:

.. code-block:: text

    light_years_per_turn = warp^2

So Warp 5 = 25 ly/turn, Warp 9 = 81 ly/turn.

Fuel Consumption
----------------

Fuel consumed per light-year depends on engine type, warp, and fleet mass:

.. code-block:: text

    fuel_per_ly = engine_fuel_table[warp] * fleet_mass / engine_efficiency

Each engine has its own fuel table (mg fuel per kT per ly at each warp level).
Fleet mass = sum of all ship masses (hull + all installed parts + cargo).

Reference: ``stars-research/fuel_table_graphs/`` — extracted fuel table data.

Ram Scoop Engines
-----------------

Ram scoop engines (propulsion tech 6+) collect hydrogen fuel from space at Warp 5+.
No fuel tank needed for travel at or below the engine's free warp speed.

IFE (Improved Fuel Efficiency) LRT improves ramscoop performance.
NRSE LRT disables ramscoop engines.

Stargates
---------

Starbases with stargate tech allow instant fleet teleportation:

* Range: limited by stargate tech level (e.g., 100 ly, 300 ly, any range)
* Mass limit: limited by stargate tech level
* Fuel cost: none (instantaneous)
* Both source and destination must have compatible stargates

IS (Interstellar Traveler) PRT gets better stargate range/mass limits.

Waypoint Orders
---------------

At each waypoint a fleet can execute one order:

* **None** — just pass through or stop
* **Colonize** — if carrying colonists and planet is uninhabited
* **Remote Mine** — mine the planet without colonizing (robot miners required)
* **Unload/Load All Cargo** — transfer minerals and colonists
* **Unload/Load Optimally** — transfer up to capacity
* **Patrol** — attack any enemy fleet entering scanner range
* **Merge with Fleet** — combine with another fleet at the same location
* **Scrap Fleet** — destroy the fleet and recover minerals
* **Transfer Colonists** — specific colonist transfer
* **Lay Mine Field** — begin laying mines in the area
