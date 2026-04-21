Ship Design
===========

Players design custom ships by selecting a hull and filling its slots with
components. A design is then built through the production queue.

Design Limits
-------------

- Each player may have at most **16 active ship designs** simultaneously.
- Starbases have a separate limit of **10 active starbase designs**.
- Additional fleet/ship limits: **512 fleets per player**; **32,000 ships of
  one design in a single fleet**.
- A design slot is freed only when **no ships of that design remain** in the
  game (all scrapped or destroyed). Scrapping a ship does not free the slot
  until the last ship of that design is gone.
- The ship designer is available from turn 1; however, building ships requires
  production queue capacity, which is unlocked through the colony development
  phase. Designs themselves cost nothing to create.

*Source: Stars! in-game help, Ship Design section.*

.. uml::

   @startuml
   class ShipDesign {
       name : string
       hull : ShipHull
       slots : Map<int, Part>
   }

   class ShipHull {
       techSlots : List<TechSlot>
       mass : int
       armor : int
       initiative : int
       fuelCapacity : int
       cargoCapacity : int
   }

   class TechSlot {
       slotType : SlotType
       maxCount : int
   }

   class Part {
       mass : int
   }

   ShipDesign "1" --> "1" ShipHull
   ShipDesign "1" *-- "0..*" Part : slotFill
   ShipHull "1" *-- "1..*" TechSlot
   @enduml

Slot Type System
----------------

Each hull slot has a **SlotType** bitmask specifying which component categories
may be placed in it. A part is compatible with a slot if the part's category
bit is set in the slot's bitmask.

.. list-table:: Atomic Slot Types
   :header-rows: 1
   :widths: 25 10 65

   * - Name
     - Bit
     - Accepts
   * - ``Engines``
     - 4096
     - Engine parts only. Required slot — every ship needs at least one.
   * - ``BeamWeapons``
     - 1
     - Beam weapon parts only.
   * - ``Torpedoes``
     - 2
     - Torpedo/missile parts only.
   * - ``Armor``
     - 4
     - Armor parts only.
   * - ``Shields``
     - 8
     - Shield parts only.
   * - ``Electrical``
     - 16
     - Electrical parts (cloaks, jammers, battle computers, capacitors, etc.).
   * - ``Mechanical``
     - 64
     - Mechanical parts (cargo pods, fuel tanks, maneuvering jets, etc.).
   * - ``Bombs``
     - 128
     - Bomb parts only.
   * - ``MineLayers``
     - 256
     - Mine layer parts only.
   * - ``MiningRobots``
     - 512
     - Mining robot parts only.
   * - ``Scanners``
     - 1024
     - Ship scanner parts only.
   * - ``GeneralPurpose``
     - 8192
     - Any non-orbital part (beam weapons, torpedoes, armor, shields,
       electrical, mechanical, bombs, mine layers, mining robots, scanners,
       engines).

.. list-table:: Composite Slot Types (bitmask combinations)
   :header-rows: 1
   :widths: 30 70

   * - Name
     - Accepts
   * - ``Weapons``
     - Beam weapons or torpedoes.
   * - ``Protection``
     - Armor or shields.
   * - ``ShieldElectMech``
     - Shields, electrical, or mechanical parts.
   * - ``ScannerElectMech``
     - Scanners, electrical, or mechanical parts.
   * - ``MineElectMech``
     - Mine layers, electrical, or mechanical parts.
   * - ``ElectMech``
     - Electrical or mechanical parts.
   * - ``WeaponShield``
     - Beam weapons, torpedoes, or shields.
   * - ``ArmorScannerElectMech``
     - Armor, scanners, electrical, or mechanical parts.
   * - ``OrbitalElect``
     - Orbital items (stargates, mass drivers) or electrical parts. *Starbase-only.*

Design Validation Rules
-----------------------

The engine enforces these rules when a design is submitted:

1. **Engine slot must be filled.** Every ship hull has at least one ``Engines``
   slot; it must contain at least one engine to be a valid design. (Exception:
   starbases have no engine slots.)
2. **Part fits slot.** Each installed part's category bit must appear in the
   slot's ``SlotType`` bitmask.
3. **Stack count ≤ slot max.** The number of identical parts placed in a single
   slot cannot exceed the slot's ``maxCount``.
4. **Tech requirements met.** The player's current tech levels must satisfy
   every requirement of each installed part. Parts that don't meet requirements
   cannot be placed.
5. **Bleeding Edge Technology.** If the BET LRT is active, any part exactly at
   the player's current tech threshold costs double resources to build (not to
   design).

Miniaturization
---------------

Components become cheaper as tech levels exceed their requirements:

- Normal: 4% cost reduction per level above requirement, minimum 25% of base cost.
- BET LRT: 5% per level, minimum 20%, but items at the exact unlock level
  cost 2× base.

Miniaturization applies to mineral and resource costs equally. It does not
affect mass.

When multiple tech fields are required, the overlevel is the **minimum** gap
across all required fields.

Ship Classification
-------------------

Classification is determined at turn resolution time from hull type and loadout.
These predicates affect scoring, combat stacking, and order validation.
See :doc:`../architecture` for the full predicate table.

Component Access Restrictions
-----------------------------

- **Mine-laying pods** require **Biotech level 4** unless the race has the
  **Space Demolition (SD) PRT**, which grants access without research.
- **Only Basic Remote Mining (OBRM) LRT**: limits a ship to at most **one
  mining robot** in its design, regardless of hull slot count.
- **Advanced Remote Mining (ARM) LRT**: grants the Midget Miner hull and
  Robo-Midget Miner robot at tech level 0.  If using ARM, always prefer the
  Robo-Midget Miner over the Robo-Mini Miner — it extracts more at half the
  cost.

*Source: Stars! Strategy Guide, Chapter 5.*

Design Role Notes
-----------------

These notes summarise validated role conventions from the original strategy
guide; they are design intent, not engine-enforced constraints.

Scouts
~~~~~~

Effective scouts need scanning power, range, speed, and low cost.  The Long
Range Scout pre-made design (engine + fuel pod + scanner) fulfils all four.  A
**fuel pod quadruples** the hull's base fuel capacity, dramatically extending
range.  Penetrating scanners require Electronics 7 (and the absence of the No
Advanced Scanners LRT); a non-penetrating scanner suffices for exploration.

Freighters
~~~~~~~~~~

The Privateer hull (Construction 4) offers 650 mg fuel, 250 kT base cargo,
and three ``GeneralPurpose`` slots that accept fuel or cargo pods, with only
2 kT Germanium hull cost — far less than Small Freighters (17 kT) or Medium
Freighters (19 kT).  Its 50 kT Ironium cost is the main drawback on
Ironium-scarce maps.

Remote Miners
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Situation
     - Best design
   * - OBRM LRT *or* cannot reach C4 + E2, with ARM
     - Midget Miner + Robo-Midget Miner
   * - OBRM LRT *or* cannot reach C4 + E2, without ARM
     - Mini Miner + 2× Robo-Mini Miner
   * - Standard or ARM, can reach Construction 4 + Electronics 2
     - Midget Miner (ARM) or Mini Miner + 2× Robo-Miner

Include a fuel pod in the spare slot (not a scanner — send a cheap scout with
the mining fleet instead).

Minelayers
~~~~~~~~~~

A Scout-hull minelayer (engine + mine pod + scanner) is the cheapest option
and buildable early.  A Frigate-hull minelayer (Construction 6) outputs three
times the mines per turn at similar cost-per-mine and accommodates two
scanners.  Use the longest-range scanner available; penetrating is preferred
for border patrol but not required.

Warships
~~~~~~~~

For beam warships, aim for battle speed **≥ 1¾** squares/round (target 2 or
2½).  The Frigate hull has no Mechanical or Electrical slots, so it cannot
carry Maneuvering Jets or Battle Computers — this limits its effectiveness as
a beam platform.  See :doc:`combat` for the battle speed formula.

Hull Reference
--------------

See :doc:`../reference/ship_hulls` for the complete hull table with all slot
layouts, mass, armor, fuel capacity, and cargo capacity.

Engine Reference
----------------

See :doc:`../reference/engines` for the full engine table including fuel
consumption at each warp speed, ram scoop free warp, and battle speed.

The fuel consumption visualization (chart per engine) is generated from
``stars-reborn-ui/assets/fuel_tables/``.
