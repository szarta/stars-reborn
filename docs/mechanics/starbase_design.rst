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

**Two stargates in two OrbitalElect slots:** only one gate is active at a time.
The active gate is determined by slot position:

- **Starbase / Space Dock hull:** the **leftmost** gate slot is used.
- **Ultrastation / Death Star hull:** the **uppermost** gate slot is used.

This means a 100/Any gate and an Any/300 gate on the same starbase do **not**
combine into Any/Any capability. Players who accidentally place two gates only
get the capabilities of one.

The same slot-priority rule applies to IT gate scanning (see :ref:`it-gate-scanning`
below).

**Two Mass Drivers** on the same starbase do provide an additive advantage; see
the in-game help for details.

*Source: SAH Forum (starsautohost.org), Starbase FAQ thread.  Needs oracle
confirmation.*

.. _it-gate-scanning:

IT Gate Scanning
----------------

Interstellar Traveler (IT) races can use their stargates to scan remote
starbases.  Details:

- The gate used for scanning is the same slot-priority gate as for transit
  (leftmost for Starbase/Space Dock; uppermost for Ultrastation/Death Star).
- IT gate scanning reveals **planet stats only**: colonist count, habitability,
  mineral concentrations, and defense percentage.
- IT gate scanning does **not** reveal: the scanned starbase's design, or ships
  in orbit of that planet.
- A starbase with maximum cloaking (98%) is still visible to an IT gate whose
  range is "Any", because 2% of infinite range is still infinite.  Non-infinite
  gate ranges are reduced by cloaking in the normal way.

*Source: SAH Forum, Starbase FAQ thread.*

Starbase Battle Behaviour
--------------------------

- Starbases use **any/any** as their combat target (primary and secondary),
  regardless of the default battle plan's primary/secondary target settings.
- However, the starbase does respect the default battle plan's **"attack who"**
  (enemy/neutral/friend) setting.  Example: if a player's default plan is
  "attack everyone," the starbase will initiate battle against a friend who
  enters orbit even though no player ships are present.
- A stationary starbase has no move tactic, but it can still *initiate* a
  battle if its "attack who" setting triggers.
- Starbases **always sweep neutral minefields**, independent of the default
  battle plan's "attack who" setting.
- Specific slot firing order applies to starbases (community-documented;
  needs oracle confirmation).

*Source: SAH Forum, Starbase FAQ thread.*

Starbase Salvage and Tech
--------------------------

- Starbases leave **no salvage** when destroyed.
- Players cannot gain tech from destroying a starbase, even if the starbase
  carries higher-tech components than the attacking fleet.

*Source: SAH Forum, Starbase FAQ thread.*

Starbase Jamming and Cloaking
------------------------------

- Starbase jamming is **75% as effective** as equivalent ship jamming.
  The maximum jamming a starbase can achieve is 75% (= 0.75 × 99%),
  compared to the 95% ship cap.
- Starbase cloaking obeys the same **98% maximum** as ships.
- Cloaking a starbase reduces IT gate scan range (as with any scanner).
  Exception: an IT gate with "any" range still detects all gates in the
  universe even at maximum cloak (2% of ∞ = ∞).

*Source: SAH Forum, Starbase FAQ thread.*

Mystery Trader Items on Starbases
-----------------------------------

- **Langston Shell / Mega Poly Shell** mounted on a starbase provides
  jamming and cloaking, but **does not** provide the scanning bonus those
  items give on ships.
- Multi-Contained Munition in weapon slots cannot lay mines on a starbase
  (starbases cannot issue waypoint orders).

*Source: SAH Forum, Starbase FAQ thread.*

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
