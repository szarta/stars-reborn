Planetary Technology
=====================

Planetary and orbital installations that are built on planets (not on ships
or starbases): planetary scanners, planetary defenses, and terraforming.

For starbase-mounted orbital items (stargates, mass drivers) see
:doc:`starbase_components`.  For the GenesisDevice (MT ship component that
terraforms an entire planet) see :doc:`components`.

**Source:** Python engine ``factory.py``.  All values need oracle verification.

Tech requirements: ``En/We/Pr/Co/El/Bio``.  Costs: ``[Ir, Bo, Ge, Resources]``.

Access: see :doc:`technology_access` — planetary scanners and defenses are not
in the base research pool; they are granted via ``PRT_Technologies`` lists.
Terraforming is in the base pool (axis-specific) or via TT LRT (total terraform).

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
