Starbase Design
===============

Starbases are orbital platforms built above planets. Unlike ships they have no
engines, cannot move, and are not subject to fuel constraints. A planet may
have at most one starbase at a time.

Design Limits
-------------

- Each player may have at most **10 active starbase designs** (separate pool
  from the 16-design ship limit).
- A starbase is upgraded by scrapping the existing one and building a new design
  in its place, or by directly upgrading via the production queue if the hull
  supports it.
- Starbase hull parts (weapons, shields, etc.) cost **50% less** to build than
  the same parts on a ship hull.

*Source: Stars! in-game help, Starbases section.*

Starbase vs. Ship Design Differences
-------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Property
     - Ship
     - Starbase
   * - Engines
     - Required (at least 1)
     - None — no engine slots
   * - Movement
     - Yes
     - Stationary
   * - Fuel
     - Carried in hull / fuel tank parts
     - N/A
   * - Cargo
     - Hull-dependent
     - N/A
   * - Dock capacity
     - N/A
     - Hull-dependent (ships built/repaired here)
   * - Orbital slot
     - No
     - Yes — ``OrbitalElect`` accepts stargates, mass drivers, electrical parts
   * - Can be attacked
     - Yes
     - Yes (counts as a combat participant)

Slot Types
----------

Starbases use the same slot type bitmask system as ships (see :doc:`ship_design`),
with one additional slot type exclusive to starbases:

**OrbitalElect** — accepts:

- Stargates (``Stargate100_250`` through ``StargateAny_Any``)
- Mass Drivers (``MassDriver5`` through ``UltraDriver13``)
- Electrical parts (cloaks, jammers, battle computers, etc.)

Only one stargate and one mass driver may be active per starbase at a time
(placing a second overwrites the first in that orbital slot).

.. todo::

   Confirm whether placing two stargates of different types in two OrbitalElect
   slots is valid or whether the engine enforces a single-stargate limit per
   starbase.

Dock Capacity
-------------

``dock_capacity`` is the maximum ship mass (kT) that can be built or repaired
at this starbase. A value of ``∞`` means no mass limit.

Ships heavier than the dock capacity cannot be built at this starbase. They
also cannot be repaired here (partial repairs up to dock capacity are allowed
by some community sources — needs oracle confirmation).

.. todo::

   Confirm partial repair rule for ships exceeding dock capacity.

Hull Reference
--------------

See :doc:`../reference/starbase_hulls` for the complete hull table.
