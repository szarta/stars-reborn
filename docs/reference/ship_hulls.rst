Ship Hull Reference
===================

All hull data sourced from the Python engine ``factory.py``.
Needs oracle verification against ``stars.exe``.

Tech requirements: ``C`` = Construction. Costs: ``[Ir, Bo, Ge, R]``.
Slot notation: ``Engines(n)`` = up to *n* engine parts per slot.
See :doc:`../mechanics/ship_design` for slot type definitions.

.. note::

   ``fuel_regen`` and ``percent_regen_bonus`` on Fuel Transport hulls indicate
   the base fuel regenerated per year and a percentage of current fuel added
   per year, respectively. These are hull-intrinsic properties, not from parts.

Scouts and Light Combat
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 20 8 8 8 8 8 8 42

   * - Hull
     - C Req
     - Mass
     - Armor
     - Init
     - Fuel
     - Cargo
     - Slots
   * - Scout
     - —
     - 8
     - 20
     - 1
     - 50
     - 0
     - Engines(1), GeneralPurpose(1), Scanners(1)
   * - Frigate
     - C6
     - 8
     - 45
     - 4
     - 125
     - 0
     - Engines(1), Protection(2), GeneralPurpose(3), Scanners(2)
   * - Destroyer
     - C3
     - 30
     - 200
     - 3
     - 280
     - 0
     - Engines(1), Weapons(1), Weapons(1), Armor(2), GeneralPurpose(1), Electrical(1), Mechanical(1)
   * - Cruiser
     - C9
     - 90
     - 700
     - 5
     - 600
     - 0
     - Engines(2), Weapons(2), Weapons(2), Protection(2), GeneralPurpose(2), ShieldElectMech(1), ShieldElectMech(1)
   * - BattleCruiser
     - C10
     - 120
     - 1000
     - 5
     - 1400
     - 0
     - Engines(2), Weapons(3), Weapons(3), Protection(4), GeneralPurpose(3), ShieldElectMech(2), ShieldElectMech(2)
   * - Battleship
     - C13
     - 222
     - 2000
     - 10
     - 2800
     - 0
     - Engines(4), Weapons(2), Weapons(2), Weapons(6), Weapons(6), Weapons(4), Armor(6), Electrical(3), Electrical(3), Shields(8), ScannerElectMech(1)
   * - Dreadnought
     - C16
     - 250
     - 4500
     - 10
     - 4500
     - 0
     - Engines(5), Weapons(6), Weapons(6), Weapons(8), Weapons(8), Armor(8), Electrical(4), Electrical(4), Protection(4), Protection(4), GeneralPurpose(1), WeaponShield(5), WeaponShield(5)

Freighters
----------

.. list-table::
   :header-rows: 1
   :widths: 20 8 8 8 8 8 8 42

   * - Hull
     - C Req
     - Mass
     - Armor
     - Init
     - Fuel
     - Cargo
     - Slots
   * - Small Freighter
     - —
     - 25
     - 25
     - 0
     - 130
     - 70
     - Engines(1), Protection(1), ScannerElectMech(1)
   * - Medium Freighter
     - C3
     - 60
     - 50
     - 0
     - 450
     - 210
     - Engines(1), Protection(1), ScannerElectMech(1)
   * - Large Freighter
     - C8
     - 125
     - 150
     - 0
     - 2600
     - 1200
     - Engines(2), Protection(2), ScannerElectMech(2)
   * - Super Freighter
     - C13
     - 175
     - 400
     - 0
     - 8000
     - 3000
     - Engines(3), Protection(5), ScannerElectMech(3), Electrical(2)

Multi-Purpose / Armed Freighters
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 8 8 8 8 8 8 42

   * - Hull
     - C Req
     - Mass
     - Armor
     - Init
     - Fuel
     - Cargo
     - Slots
   * - Privateer
     - C4
     - 65
     - 150
     - 3
     - 650
     - 250
     - Engines(1), Protection(2), GeneralPurpose(1), GeneralPurpose(1), ScannerElectMech(1)
   * - Rogue
     - C8
     - 75
     - 450
     - 4
     - 2250
     - 500
     - Engines(2), Electrical(1), Electrical(1), GeneralPurpose(2), GeneralPurpose(2), Protection(3), MineElectMech(2), MineElectMech(2), Scanners(1)
   * - Galleon
     - C11
     - 125
     - 900
     - 4
     - 2500
     - 1000
     - Engines(4), Protection(2), Protection(2), GeneralPurpose(3), GeneralPurpose(3), Electrical(1), MineElectMech(2), ElectMech(2), Scanners(2)

Colony Ships
------------

.. list-table::
   :header-rows: 1
   :widths: 22 8 8 8 8 8 8 38

   * - Hull
     - C Req
     - Mass
     - Armor
     - Init
     - Fuel
     - Cargo
     - Slots
   * - Mini Colony Ship
     - —
     - 8
     - 10
     - 0
     - 150
     - 10
     - Engines(1), Mechanical(1)
   * - Colony Ship
     - —
     - 20
     - 20
     - 0
     - 200
     - 25
     - Engines(1), Mechanical(1)

The ``Mechanical`` slot on colony ships accepts a Colonization Module, which is
required to establish a colony on an uninhabited planet.

Bombers
-------

.. list-table::
   :header-rows: 1
   :widths: 22 8 8 8 8 8 8 38

   * - Hull
     - C Req
     - Mass
     - Armor
     - Init
     - Fuel
     - Cargo
     - Slots
   * - Mini Bomber
     - C1
     - 28
     - 50
     - 0
     - 120
     - 0
     - Engines(1), Bombs(2)
   * - B-17 Bomber
     - C6
     - 69
     - 175
     - 0
     - 400
     - 0
     - Engines(2), Bombs(4), Bombs(4), ScannerElectMech(1)
   * - Stealth Bomber
     - C8
     - 70
     - 225
     - 0
     - 750
     - 0
     - Engines(2), Bombs(4), Bombs(4), ScannerElectMech(1), Electrical(3)
   * - B-52 Bomber
     - C15
     - 110
     - 450
     - 0
     - 750
     - 0
     - Engines(3), Bombs(4), Bombs(4), Bombs(4), Bombs(4), Shields(2), ScannerElectMech(2)

Remote Miners
-------------

.. list-table::
   :header-rows: 1
   :widths: 22 8 8 8 8 8 8 38

   * - Hull
     - C Req
     - Mass
     - Armor
     - Init
     - Fuel
     - Cargo
     - Slots
   * - Midget Miner
     - —
     - 10
     - 100
     - 0
     - 210
     - 0
     - Engines(1), MiningRobots(2)
   * - Mini Miner
     - C2
     - 80
     - 130
     - 0
     - 210
     - 0
     - Engines(1), MiningRobots(1), MiningRobots(1), ScannerElectMech(1)
   * - Miner
     - C6
     - 110
     - 475
     - 0
     - 500
     - 0
     - Engines(2), MiningRobots(2), MiningRobots(2), MiningRobots(1), MiningRobots(1), ArmorScannerElectMech(2)
   * - Maxi Miner
     - C11
     - 110
     - 1400
     - 0
     - 850
     - 0
     - Engines(1), MiningRobots(4), MiningRobots(4), MiningRobots(1), MiningRobots(1), ArmorScannerElectMech(2)
   * - Ultra Miner
     - C14
     - 100
     - 1500
     - 0
     - 1300
     - 0
     - Engines(2), MiningRobots(4), MiningRobots(4), MiningRobots(2), MiningRobots(2), ArmorScannerElectMech(3)

Fuel Transports
---------------

Fuel Transport hulls have hull-intrinsic fuel regeneration in addition to their
carried fuel capacity.

.. list-table::
   :header-rows: 1
   :widths: 22 8 8 8 8 8 8 8 8 30

   * - Hull
     - C Req
     - Mass
     - Armor
     - Fuel
     - Regen/yr
     - % Bonus
     - Cargo
     - Init
     - Slots
   * - Fuel Transport
     - C4
     - 12
     - 5
     - 750
     - 200
     - 5%
     - 0
     - 0
     - Engines(1), Shields(1)
   * - Super Fuel Transport
     - C7
     - 111
     - 12
     - 2250
     - 200
     - 10%
     - 0
     - 0
     - Engines(2), Shields(2), Scanners(1)

Mine Layers
-----------

.. list-table::
   :header-rows: 1
   :widths: 22 8 8 8 8 8 8 38

   * - Hull
     - C Req
     - Mass
     - Armor
     - Init
     - Fuel
     - Cargo
     - Slots
   * - Mini Mine Layer
     - —
     - 10
     - 60
     - 0
     - 400
     - 0
     - Engines(1), MineLayers(2), MineLayers(2), ScannerElectMech(1)
   * - Super Mine Layer
     - C15
     - 30
     - 1200
     - 0
     - 2200
     - 0
     - Engines(3), MineLayers(8), MineLayers(8), ScannerElectMech(3), Protection(3), MineElectMech(3)

Ultra-Hulls
-----------

These hulls require very high Construction tech and serve specialized roles.

.. list-table::
   :header-rows: 1
   :widths: 22 8 8 8 8 8 8 38

   * - Hull
     - C Req
     - Mass
     - Armor
     - Init
     - Fuel
     - Cargo
     - Slots
   * - Nubian
     - C26
     - 100
     - 5000
     - 2
     - 5000
     - 0
     - Engines(3), GeneralPurpose(3)×10
   * - MetaMorph *(AR only)*
     - C8
     - 85
     - 500
     - 2
     - 700
     - 300
     - Engines(3), GeneralPurpose(2)×4, GeneralPurpose(8), GeneralPurpose(1)
   * - MiniMorph *(AR only)*
     - C8
     - 70
     - 25
     - 2
     - 400
     - 150
     - Engines(2), GeneralPurpose(2)×4, GeneralPurpose(1)×3, GeneralPurpose(3)

Nubian has 13 GeneralPurpose slots of 3 each (total 39 possible part slots).
MetaMorph and MiniMorph are Alternate Reality (AR) PRT-only hulls.

.. todo::

   Confirm exact slot counts for Nubian (factory.py shows 13 × GP(3)).
   Confirm MetaMorph/MiniMorph availability is strictly gated to AR PRT.
