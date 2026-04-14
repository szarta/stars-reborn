Starbase Components
===================

Components that fill the ``OrbitalElect`` slot on starbases.  They cannot
be installed on ships.

**Source:** Python engine ``factory.py``.  All values need oracle verification.

Tech requirements: ``En/We/Pr/Co/El/Bio``.  Costs: ``[Ir, Bo, Ge, Resources]``.

Access: see :doc:`technology_access` for per-PRT availability.
See :doc:`starbase_hulls` for hull slot counts.

.. _stargates-ref:

Stargates
---------

Stargates allow instantaneous fleet teleportation between two connected
gates.  Fleets that exceed ``safe_mass`` or transit farther than
``safe_range`` take proportional damage; far-exceeding either limit can
destroy the fleet.  ``any`` indicates no limit.

Cost for all stargates: ``[50, 20, 20, N]`` (resources vary by type).

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
   ``PRT_Technologies`` list.  HE races expand via mass drivers and high
   growth rate rather than gate networks.

.. _mass-drivers-ref:

Mass Drivers
------------

Mass drivers accelerate mineral packets toward a target planet at
``warp_speed``.  A receiving driver at warp N safely catches packets fired at
warp ≤ N; packets arriving faster lose minerals; packets arriving at an
undefended planet cause proportional damage.

MassDriver7 and UltraDriver10 are in the base research pool (all races).
The odd-tier drivers (5, 6, 8, 9, 11, 12, 13) are PP-exclusive.

.. note::
   MassDriver7 and UltraDriver10 carry disproportionately high resource costs
   compared to the PP-exclusive adjacent tiers — likely a deliberate balance
   penalty for non-PP races.

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
