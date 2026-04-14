Planetary Technology
=====================

Orbital and planetary installations: planetary scanners, planetary defenses,
stargates, mass drivers, and terraforming.

**Source:** Python engine ``factory.py``.  All values need oracle verification.

Tech requirements: ``En/We/Pr/Co/El/Bio``.  Costs: ``[Ir, Bo, Ge, Resources]``.

Access: see :doc:`technology_access` — none of these items are in the base
research pool.  They are granted via ``PRT_Technologies`` and/or ``LRT_Technologies``
lists.

.. _planetary-scanners-ref:

Planetary Scanners
------------------

Planetary scanners are orbital installations (no mass).  They provide
normal scan coverage (normal range) and, for the Snooper series,
penetrating coverage (pen range) that reveals colonists and minerals on
enemy planets.

Cost for all planetary scanners: ``[10, 10, 70, 100]``.

Access: all PRTs except AR have Viewer50–Scoper280.  Snooper series
(320X, 400X, 620X) are removed for NAS races and AR races.
Snooper500X accessibility is a known source inconsistency — see
:doc:`technology_access`.

.. list-table::
   :header-rows: 1
   :widths: 20 20 12 12 36

   * - Item
     - Tech Req
     - Range (ly)
     - Pen (ly)
     - Notes
   * - Viewer50
     - —
     - 50
     - 0
     -
   * - Viewer90
     - El 1
     - 90
     - 0
     -
   * - Scoper150
     - El 3
     - 150
     - 0
     -
   * - Scoper220
     - El 6
     - 220
     - 0
     -
   * - Scoper280
     - El 8
     - 280
     - 0
     -
   * - Snooper320X
     - En 3 / El 10 / Bio 3
     - 320
     - 160
     - Removed if NAS or AR
   * - Snooper400X
     - En 4 / El 13 / Bio 6
     - 400
     - 200
     - Removed if NAS or AR
   * - Snooper500X
     - En 5 / El 16 / Bio 7
     - 500
     - 250
     - Absent from NAS/AR removal list (source inconsistency)
   * - Snooper620X
     - En 7 / El 23 / Bio 9
     - 620
     - 310
     - Removed if NAS or AR

.. _planetary-defenses-ref:

Planetary Defenses
------------------

Planetary defenses are orbital installations (no mass).  A planet can have
up to 100 defenses; each unit contributes independently to overall protection.

Cost for all planetary defenses: ``[5, 5, 5, 15]``.

Access: SDI and MissileBattery are in every PRT's list.  LaserBattery,
PlanetaryShield, and NeutronShield are excluded from WM and AR.

**Protection formulas** (from ``src/model/technology.py:PlanetaryDefense``;
source: Leonard Dickens "Guts of bombing", 1998):

.. code-block:: text

   # n = number of defenses; base_coverage per item listed below
   colonist_protection = 1 − (1 − base_coverage)^n
   smart_bomb_factor   = 1 − (1 − base_coverage/2)^n   [smart bombs halve coverage]
   building_protection = colonist_protection × 0.5
   invasion_protection = colonist_protection × 0.75

Example: 100× SDI (base_coverage = 0.0099):
colonist protection = 1 − (1 − 0.0099)^100 = 1 − 0.9901^100 ≈ 63.3%.

.. list-table::
   :header-rows: 1
   :widths: 22 14 14 50

   * - Item
     - Tech Req
     - base_coverage
     - Notes
   * - SDI
     - —
     - 0.99% (0.0099)
     - All PRTs
   * - MissileBattery
     - En 5
     - 1.99% (0.0199)
     - All PRTs
   * - LaserBattery
     - En 10
     - 2.39% (0.0239)
     - All PRTs except WM and AR
   * - PlanetaryShield
     - En 16
     - 2.99% (0.0299)
     - All PRTs except WM and AR
   * - NeutronShield
     - En 23
     - 3.79% (0.0379)
     - All PRTs except WM and AR

.. _stargates-ref:

Stargates
---------

Stargates are starbase-mounted orbital installations (no mass; built on
starbases only, not ships).  They allow instantaneous fleet teleportation
between two gates; fleets exceeding the safe limits take damage or may
be destroyed.

``safe_mass`` — maximum fleet mass (kT) that can transit without damage.
``safe_range`` — maximum gate-to-gate distance (ly) for safe transit.
``any`` indicates no limit.

Cost for all stargates: ``[50, 20, 20, N]`` (resources vary by type).

Access: see :doc:`technology_access` for per-PRT gate availability.

.. list-table::
   :header-rows: 1
   :widths: 22 20 18 12 12 16

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Safe mass (kT)
     - Safe range (ly)
     - Access
   * - Stargate 100/250
     - Pr 5 / Co 5
     - [50,20,20,200]
     - 100
     - 250
     - All PRTs
   * - StargateAny/300
     - Pr 6 / Co 10
     - [50,20,20,250]
     - any
     - 300
     - IT only
   * - Stargate 150/600
     - Pr 11 / Co 7
     - [50,20,20,500]
     - 150
     - 600
     - All PRTs except CA and HE
   * - Stargate 300/500
     - Pr 9 / Co 13
     - [50,20,20,600]
     - 300
     - 500
     - All PRTs except CA and HE
   * - Stargate100/Any
     - Pr 16 / Co 12
     - [50,20,20,700]
     - 100
     - any
     - IT only
   * - StargateAny/800
     - Pr 12 / Co 18
     - [50,20,20,700]
     - any
     - 800
     - IT only
   * - StargateAny/Any
     - Pr 19 / Co 24
     - [50,20,20,800]
     - any
     - any
     - IT only

.. note::
   HE has **no stargate access** — Stargate100/250 is absent from the HE
   ``PRT_Technologies`` list.  This appears intentional: HE races expand via
   mass drivers and high growth rate rather than gate networks.

.. _mass-drivers-ref:

Mass Drivers
------------

Mass drivers are starbase-mounted orbital installations (no mass; built on
starbases only).  They accelerate mineral packets to a target planet at
``warp_speed``.  Packets traveling faster than the receiving driver's speed
lose minerals on arrival; packets arriving at an undefended planet cause
damage.

Cost formula: varies by driver tier (see table).  Base access depends on PRT:
MassDriver7 and UltraDriver10 are in the base pool (all races).
Odd-tier drivers (5, 6, 8, 9, 11, 12, 13) are PP-exclusive.

.. list-table::
   :header-rows: 1
   :widths: 22 16 22 12 28

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Speed
     - Access
   * - MassDriver5
     - En 4
     - [24,20,20,70]
     - Warp 5
     - PP only
   * - MassDriver6
     - En 7
     - [24,20,20,144]
     - Warp 6
     - PP only
   * - MassDriver7
     - En 9
     - [100,100,100,512]
     - Warp 7
     - Base pool (all races)
   * - SuperDriver8
     - En 11
     - [24,20,20,256]
     - Warp 8
     - PP only
   * - SuperDriver9
     - En 13
     - [24,20,20,324]
     - Warp 9
     - PP only
   * - UltraDriver10
     - En 15
     - [100,100,100,968]
     - Warp 10
     - Base pool (all races)
   * - UltraDriver11
     - En 17
     - [24,20,20,484]
     - Warp 11
     - PP only
   * - UltraDriver12
     - En 20
     - [24,20,20,576]
     - Warp 12
     - PP only
   * - UltraDriver13
     - En 24
     - [24,20,20,676]
     - Warp 13
     - PP only

.. note::
   MassDriver7 and UltraDriver10 have disproportionately high resource costs
   (512 and 968 vs. the ~70–676 range of PP-exclusive drivers).  PP races can
   always build the cheaper tier-adjacent drivers; non-PP races pay the high
   cost for the two base-pool drivers.

.. _terraforming-ref:

Terraforming
------------

Terraforming items improve planetary habitability by adjusting gravity,
temperature, and/or radiation toward the race's ideal range.  Each
technology improves the target axis by ``rate`` steps per year.

All terraforming items occupy the orbital/mechanical slot on ships or
are built via the production queue at terraforming rate.

Cost for all axis-specific terraforming: ``[0, 0, 0, 100]``.
Cost for total terraforming: ``[0, 0, 0, 70]``.

Access: axis-specific terraforming (Gravity/Temperature/Radiation 3–15)
is in the base pool for all races.  TT (Total Terraforming) LRT grants
access to the TotalTerraform series; axis-specific items remain accessible
(TT does not remove them).

Total Terraforming (TT LRT only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 22 20 58

   * - Item
     - Tech Req
     - Rate (all 3 axes simultaneously)
   * - TotalTerraform3
     - —
     - 3 steps/yr each axis
   * - TotalTerraform5
     - Bio 3
     - 5 steps/yr each axis
   * - TotalTerraform7
     - Bio 6
     - 7 steps/yr each axis
   * - TotalTerraform10
     - Bio 9
     - 10 steps/yr each axis
   * - TotalTerraform15
     - Bio 13
     - 15 steps/yr each axis
   * - TotalTerraform20
     - Bio 17
     - 20 steps/yr each axis
   * - TotalTerraform25
     - Bio 22
     - 25 steps/yr each axis
   * - TotalTerraform30
     - Bio 25
     - 30 steps/yr each axis

Axis-Specific Terraforming (base pool — all races)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 22 24 54

   * - Item
     - Tech Req
     - Rate
   * - GravityTerraform3
     - Pr 1 / Bio 1
     - Gravity ±3 steps/yr
   * - GravityTerraform7
     - Pr 5 / Bio 2
     - Gravity ±7 steps/yr
   * - GravityTerraform11
     - Pr 10 / Bio 3
     - Gravity ±11 steps/yr
   * - GravityTerraform15
     - Pr 16 / Bio 4
     - Gravity ±15 steps/yr
   * - TemperatureTerraform3
     - En 1 / Bio 1
     - Temperature ±3 steps/yr
   * - TemperatureTerraform7
     - En 5 / Bio 2
     - Temperature ±7 steps/yr
   * - TemperatureTerraform11
     - En 10 / Bio 3
     - Temperature ±11 steps/yr
   * - TemperatureTerraform15
     - En 16 / Bio 4
     - Temperature ±15 steps/yr
   * - RadiationTerraform3
     - We 1 / Bio 1
     - Radiation ±3 steps/yr
   * - RadiationTerraform7
     - We 5 / Bio 2
     - Radiation ±7 steps/yr
   * - RadiationTerraform11
     - We 10 / Bio 3
     - Radiation ±11 steps/yr
   * - RadiationTerraform15
     - We 16 / Bio 4
     - Radiation ±15 steps/yr

GenesisDevice (MT)
~~~~~~~~~~~~~~~~~~~

The GenesisDevice is a Mystery Trader item that terraforms an entire planet
to ideal habitability in one use.

- **ID:** 234
- **Tech req:** En 20 / We 10 / Pr 10 / Co 20 / El 10 / Bio 20
- **Cost:** [0, 0, 0, 5000]
- **Effect:** Sets all three hab axes to the race's ideal values (100% value)
  on any planet.
