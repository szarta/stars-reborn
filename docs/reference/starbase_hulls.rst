Starbase Hull Reference
=======================

All data from the Python engine ``factory.py``. Needs oracle verification.

Costs: ``[Ir, Bo, Ge, R]``. ``Dock`` = max ship mass (kT) buildable/repairable;
``∞`` = unlimited. See :doc:`../mechanics/starbase_design` for design rules.

Slot types: ``Weapons`` = BeamWeapons|Torpedoes; ``Shields`` = shields only;
``Protection`` = Armor|Shields; ``Electrical`` = electrical parts;
``OrbitalElect`` = stargates, mass drivers, or electrical parts.

.. list-table::
   :header-rows: 1
   :widths: 20 8 8 8 8 8 52

   * - Hull
     - C Req
     - Armor
     - Init
     - Dock
     - Cost
     - Slots
   * - Orbital Fort
     - —
     - 100
     - 10
     - 0
     - [12,0,17,40]
     - Weapons(12), Weapons(12), Protection(12), Protection(12), OrbitalElect(1)
   * - Space Dock
     - C4
     - 250
     - 12
     - 200
     - [20,5,25,100]
     - Weapons(16), Weapons(16), Weapons(16), Electrical(2), Electrical(2), Shields(24), Protection(24), OrbitalElect(1)
   * - Space Station
     - —
     - 500
     - 14
     - ∞
     - [120,80,250,600]
     - Weapons(16)×4, Shields(16)×2, Protection(16)×2, Electrical(3)×2, OrbitalElect(1)×2
   * - Ultra Station
     - C12
     - 1000
     - 16
     - ∞
     - [120,80,300,600]
     - Weapons(16)×6, Electrical(3)×4, Shields(20)×2, Protection(20)×2, OrbitalElect(1)×2
   * - Death Star
     - C17
     - 1500
     - 18
     - ∞
     - [120,80,350,750]
     - Weapons(32)×4, Electrical(4)×6, Shields(30)×2, Protection(20)×2, OrbitalElect(1)×2

Slot counts use ``×N`` notation for multiple identical slots.

Dock Capacity Notes
-------------------

- **Orbital Fort** (dock 0): cannot build or repair ships. Functions as a
  weapons/defense platform only.
- **Space Dock** (dock 200 kT): can build and repair ships up to 200 kT hull
  mass. Limits early-game capital ship construction.
- **Space Station / Ultra Station / Death Star** (dock ∞): no mass limit.

.. todo::

   Confirm whether Space Station has zero tech requirements (factory.py shows
   ``[0,0,0,0,0,0]``). The original game may require some base tech to build
   it despite zero research requirements.

.. todo::

   Confirm exact slot counts for all hulls against oracle. The expanded slot
   notation (e.g., Weapons(16)×4 for Ultra Station's 6 weapon slots) needs
   verification.
