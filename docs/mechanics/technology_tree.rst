Technology Tree
===============

Technologies are unlocked when a player's tech level in the required field reaches
the specified level. Each technology has resource costs, mineral costs, and mass.

Tech Fields
-----------

* **Energy (E)**
* **Weapons (W)**
* **Propulsion (P)**
* **Construction (C)**
* **Electronics (El)**
* **Biotechnology (B)**

Class Hierarchy
---------------

All technology items share a common base with costs and tech requirements.
Ship-installable items are ``Part`` subclasses. Planetary items (scanners,
defenses, stargates, mass drivers, terraforming) are direct ``Technology``
subclasses.

.. uml::

   @startuml
   abstract class Technology {
       id : int
       ironiumCost : int
       boraniumCost : int
       germaniumCost : int
       resourceCost : int
       techRequirements : int[6]
   }

   abstract class Part {
       mass : int
   }

   class Armor {
       armorValue : int
   }

   class Shield {
       shieldValue : int
   }

   class Scanner {
       basicRange : int
       penetratingRange : int
   }

   class Engine {
       warpTenTravel : boolean
       battleSpeed : float
       fuelUsage : int[10]
       lastFreeWarp : int
   }

   class BeamWeapon {
       power : int
       range : int
       initiative : int
       spread : boolean
       shieldsOnly : boolean
   }

   class Torpedo {
       power : int
       range : int
       initiative : int
       accuracy : float
   }

   class Bomb {
       colonistKillPercent : float
       minimumColonistsKilled : int
       buildingsDestroyed : int
       smart : boolean
   }

   class MineLayer {
       minesPerYear : int
       mineType : MineType
       minSafeWarpSpeed : int
       hitChancePerLightYear : float
       shipDamageNoRamScoop : int
       shipDamageRamScoop : int
       fleetDamageNoRamScoop : int
       fleetDamageRamScoop : int
   }

   class MiningRobot {
       miningValue : int
   }

   class Mechanical {
   }

   class Electrical {
   }

   class ShipHull {
       mass : int
       fuelCapacity : int
       cargoCapacity : int
       armorStrength : int
       initiative : int
       minimumEngineSlots : int
       maximumEngineSlots : int
       minimumArmorSlots : int
       maximumArmorSlots : int
   }

   class StarbaseHull {
       armorStrength : int
       initiative : int
       dockCapacity : int
       minimumArmorSlots : int
       maximumArmorSlots : int
   }

   class PlanetaryScanner {
       basicRange : int
       penetratingRange : int
   }

   class PlanetaryDefense {
       baseCoverage : float
   }

   class Stargate {
       safeMass : int
       safeDistance : int
   }

   class MassDriver {
       warp : int
   }

   class Terraforming {
       gravity : int
       temperature : int
       radiation : int
   }

   enum MineType {
       NORMAL
       HEAVY
       SPEED
   }

   Technology <|-- Part
   Technology <|-- ShipHull
   Technology <|-- StarbaseHull
   Technology <|-- PlanetaryScanner
   Technology <|-- PlanetaryDefense
   Technology <|-- Stargate
   Technology <|-- MassDriver
   Technology <|-- Terraforming

   Part <|-- Armor
   Part <|-- Shield
   Part <|-- Scanner
   Part <|-- Engine
   Part <|-- BeamWeapon
   Part <|-- Torpedo
   Part <|-- Bomb
   Part <|-- MineLayer
   Part <|-- MiningRobot
   Part <|-- Mechanical
   Part <|-- Electrical

   MineLayer --> MineType
   @enduml

Technology Categories
---------------------

Scanners (ship-mounted)
~~~~~~~~~~~~~~~~~~~~~~~

Basic range and penetrating range. Higher tech = longer range and penetrating ability.
First scanner: Bat Scanner (E0, W0, P0, C0, El1, B0).

Planetary Scanners
~~~~~~~~~~~~~~~~~~

Cover a radius around the planet where built. Higher tech = larger radius and
penetrating capability.

Planetary Defenses
~~~~~~~~~~~~~~~~~~

``baseCoverage`` is the per-defense kill probability against a single bomb.
Stacks as ``1 - (1 - baseCoverage)^n`` for ``n`` defenses. Applies to both normal
and smart bombs; smart bombs halve effective coverage per defense.
Defenses also reduce remote mining yield.

Defense coverage values (per unit, per population unit — unverified):

.. list-table::
   :header-rows: 1
   :widths: 30 20

   * - Defense type
     - Coverage per unit
   * - SDI
     - 0.99%
   * - Missile Battery
     - 1.99%
   * - Laser Battery
     - 2.39%
   * - Planetary Shield
     - 2.99%
   * - Neutron Bomb
     - 3.79%

.. todo::

   Oracle-verify defense coverage values. Source: Python reference engine
   ``objects/planet.py`` ``DefenseQuality`` dict. Confirm units (is this
   "per unit per 10k pop" or per unit total?).

Armor
~~~~~

``armorValue`` adds directly to a ship's total armor strength. Multiple armor
pieces stack additively.

Shields
~~~~~~~

``shieldValue`` absorbs incoming damage before armor. Shields regenerate each
combat round (IS race: 25%; RS LRT: partial; all others: 0%).

Engines
~~~~~~~

``fuelUsage[w]`` is the fuel consumed per light-year at warp ``w`` (index 0–9,
where index 9 = warp 10). ``lastFreeWarp`` is the highest warp speed the engine
can sustain with zero fuel (ram scoop engines only; 0 for non-ram engines).
``warpTenTravel`` indicates whether the engine can safely travel at warp 10.
``battleSpeed`` is the combat speed rating (fractional).

Beam Weapons
~~~~~~~~~~~~

``spread`` weapons hit all targets in range simultaneously. ``shieldsOnly``
weapons (sappers) deal damage exclusively to shields and cannot damage armor.

Missiles / Torpedoes
~~~~~~~~~~~~~~~~~~~~

``accuracy`` is the base hit probability before ECM/jammers are applied. Initiative
determines firing order within a combat round.

Bombs (normal and smart)
~~~~~~~~~~~~~~~~~~~~~~~~

Normal bombs: ``colonistKillPercent`` fraction of colonists killed per bomb,
minimum ``minimumColonistsKilled``. ``buildingsDestroyed`` buildings destroyed per bomb.
Smart bombs: same formula but skips defenses more effectively (see Planetary Defenses).

Mine Layers
~~~~~~~~~~~

``minesPerYear`` mines laid per fleet per year at any waypoint task. Three mine types:

.. list-table::
   :header-rows: 1
   :widths: 15 20 65

   * - MineType
     - minSafeWarpSpeed
     - Collision effect
   * - NORMAL
     - warp 4
     - ``hitChancePerLightYear`` per l-y traversed; on hit: ``shipDamageNoRamScoop``
       damage to ship, ``fleetDamageNoRamScoop`` damage spread to fleet. Ram-scoop
       hulls use the ``RamScoop`` variants.
   * - HEAVY
     - warp 6
     - Higher damage, lower hit probability than normal.
   * - SPEED
     - warp 5 (stops fleet)
     - Reduces fleet to minimum safe warp on collision.

Mining Robots (remote)
~~~~~~~~~~~~~~~~~~~~~~

``miningValue`` kT of each mineral extracted per year per robot (proportional
to concentration). No colonists required.

Mechanical / Electrical Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Mechanical`` and ``Electrical`` are catch-all part categories for components
that don't fit the above specializations (e.g., cargo pods, fuel tanks,
maneuvering jets, battle computers, cloaking devices). They share the base
``Part`` fields (mass, costs, tech requirements) but have no additional
type-specific fields — capabilities are implicit in the specific item data.

Mass Drivers
~~~~~~~~~~~~

``warp`` is the packet velocity. Packets arriving at a planet without a matching
driver of equal or higher warp deal damage. See :doc:`../new_game/universe_parameters`
for mass driver packet mechanics.

Stargates
~~~~~~~~~

``safeMass`` (kT) and ``safeDistance`` (l-y) are the per-gate limits. The effective
limit for a transfer is the minimum of both endpoints. Exceeding either limit
causes hull damage or destruction.

Terraforming
~~~~~~~~~~~~

``gravity``, ``temperature``, ``radiation`` are the maximum hab units shiftable
per year per axis with this item equipped. Total annual shift = sum across all
terraforming items on the planet's fleet.

Hulls
-----

Ship hulls and starbase hulls are both ``Technology`` subclasses but are never
ship-installable parts.

``ShipHull.minimumEngineSlots`` / ``maximumEngineSlots`` constrain the valid
engine count in the ship designer. ``minimumArmorSlots`` is the number of
armor slots pre-filled by the hull design. ``fuelCapacity`` is the base fuel
tank; additional fuel pods (``Mechanical`` parts) may increase it.

``StarbaseHull.dockCapacity`` is the maximum ship mass (kT) that can be built
or repaired at this starbase; 0 = no docking.

Full Data Reference
-------------------

Numeric values for all technology items are in ``stars-reborn-research/data/technologies.dat``
(original game data) and will be encoded in the engine's data model.

.. todo::

   Port technologies.dat values into a structured reference table here once
   the race file format research (R1) is complete and the engine data model
   is defined.
