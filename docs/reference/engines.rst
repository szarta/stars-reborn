Engine Reference
================

All engine data sourced from the Python engine ``factory.py`` implementation.
Needs oracle verification against ``stars.exe``.

Tech requirements format: ``E/W/P/C/El/B`` (Energy, Weapons, Propulsion,
Construction, Electronics, Biotechnology). Costs: ``[Ir, Bo, Ge, Resources]``.

.. warning::

   Fuel table values (mg/ly) are from the Python engine implementation and
   require oracle verification. See
   ``stars-reborn-research/docs/open_questions/`` for research tasks.

Engine Summary
--------------

.. list-table::
   :header-rows: 1
   :widths: 28 18 8 18 8 8 8

   * - Engine
     - Tech Req
     - Mass
     - Cost [Ir,Bo,Ge,R]
     - Battle Speed
     - Warp 10
     - Free Warp
   * - Settlers Delight
     - —
     - 2
     - [1,0,1,2]
     - 6
     - No
     - 6
   * - Quick Jump 5
     - —
     - 4
     - [3,0,1,3]
     - 5
     - No
     - 1
   * - Fuel Mizer
     - P2
     - 6
     - [8,0,0,11]
     - 6
     - No
     - 4
   * - Long Hump 6
     - P3
     - 9
     - [5,0,1,6]
     - 6
     - No
     - 1
   * - Daddy Long Legs 7
     - P5
     - 13
     - [11,0,3,12]
     - 7
     - No
     - 1
   * - Alpha Drive 8
     - P7
     - 17
     - [16,0,3,28]
     - 8
     - No
     - 1
   * - Trans-Galactic Drive
     - P9
     - 25
     - [20,20,9,50]
     - 9
     - No
     - 1
   * - Interspace-10
     - P11
     - 25
     - [18,25,10,60]
     - 10
     - **Yes**
     - 1
   * - Trans-Star 10
     - P23
     - 5
     - [3,0,3,10]
     - 10
     - **Yes**
     - 1
   * - Radiating Hydro-Ram Scoop
     - E2, P6
     - 10
     - [3,2,9,8]
     - 6
     - No
     - 6
   * - Sub-Galactic Fuel Scoop
     - E2, P8
     - 20
     - [4,4,7,12]
     - 7
     - No
     - 5
   * - Trans-Galactic Fuel Scoop
     - E3, P9
     - 19
     - [5,4,12,18]
     - 8
     - No
     - 6
   * - Trans-Galactic Super Scoop
     - E4, P12
     - 18
     - [6,4,16,24]
     - 9
     - No
     - 7
   * - Trans-Galactic Mizer Scoop
     - E4, P16
     - 11
     - [5,2,13,20]
     - 10
     - **Yes**
     - 8
   * - Galaxy Scoop
     - E5, P20
     - 8
     - [4,2,9,12]
     - 10
     - **Yes**
     - 9
   * - Enigma Pulsar
     - E7, P13, C5, El9
     - 20
     - [12,15,11,40]
     - 10 (+0.25)
     - **Yes**
     - 9

**Free Warp** = highest warp speed with zero fuel cost (ram scoop or near-free
design). ``1`` means only warp 0–1 are free (standard non-ram engine).

Enigma Pulsar also grants +10% cloaking and a +0.25 battle speed modifier
stacked on its base battle speed of 10.

Fuel Tables (mg per light-year)
--------------------------------

Values at warp 0 and 1 are always 0 (stationary or negligible). Listed from
warp 2 onward.

.. list-table::
   :header-rows: 1
   :widths: 28 8 8 8 8 8 8 8 8 8

   * - Engine
     - W2
     - W3
     - W4
     - W5
     - W6
     - W7
     - W8
     - W9
     - W10
   * - Settlers Delight
     - 0
     - 0
     - 0
     - 0
     - 0
     - 140
     - 275
     - 480
     - 576
   * - Quick Jump 5
     - 25
     - 100
     - 100
     - 100
     - 180
     - 500
     - 800
     - 900
     - 1080
   * - Fuel Mizer
     - 0
     - 0
     - 0
     - 35
     - 120
     - 175
     - 235
     - 360
     - 420
   * - Long Hump 6
     - 20
     - 60
     - 100
     - 100
     - 105
     - 450
     - 750
     - 900
     - 1080
   * - Daddy Long Legs 7
     - 20
     - 60
     - 70
     - 100
     - 100
     - 110
     - 600
     - 750
     - 900
   * - Alpha Drive 8
     - 15
     - 50
     - 60
     - 70
     - 100
     - 100
     - 115
     - 700
     - 840
   * - Trans-Galactic Drive
     - 15
     - 35
     - 45
     - 55
     - 70
     - 80
     - 90
     - 100
     - 120
   * - Interspace-10
     - 10
     - 30
     - 40
     - 50
     - 60
     - 70
     - 80
     - 90
     - 100
   * - Trans-Star 10
     - 5
     - 15
     - 20
     - 25
     - 30
     - 35
     - 40
     - 45
     - 50
   * - Radiating Hydro-Ram Scoop
     - 0
     - 0
     - 0
     - 0
     - 0
     - 165
     - 375
     - 600
     - 720
   * - Sub-Galactic Fuel Scoop
     - 0
     - 0
     - 0
     - 0
     - 85
     - 105
     - 210
     - 380
     - 456
   * - Trans-Galactic Fuel Scoop
     - 0
     - 0
     - 0
     - 0
     - 0
     - 88
     - 100
     - 145
     - 174
   * - Trans-Galactic Super Scoop
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 65
     - 90
     - 108
   * - Trans-Galactic Mizer Scoop
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 70
     - 84
   * - Galaxy Scoop
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 60
   * - Enigma Pulsar
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 60

The per-engine fuel chart visualization (for display in the ship designer UI)
is generated from ``stars-reborn-ui/assets/fuel_tables/``.

Ram Scoop Fuel Gain Matrix
--------------------------

Ram scoop engines generate fuel passively while traveling. The gain is indexed
by the engine's free warp and the travel warp speed. Values are mg of fuel
gained per light-year.

.. list-table::
   :header-rows: 1
   :widths: 18 8 8 8 8 8 8 8 8 8 8

   * - Free Warp \\ Travel Warp
     - W1
     - W2
     - W3
     - W4
     - W5
     - W6
     - W7
     - W8
     - W9
     - W10
   * - 1 (non-ram)
     - 0
     - 1
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
     - 0
   * - 4 (Fuel Mizer)
     - 0
     - 10
     - 24
     - 27
     - 16
     - 0
     - 0
     - 0
     - 0
     - 0
   * - 5
     - 0
     - 10
     - 40
     - 54
     - 48
     - 25
     - 0
     - 0
     - 0
     - 0
   * - 6 (Settlers Delight, RHRP, TGFS)
     - 0
     - 10
     - 40
     - 90
     - 96
     - 75
     - 36
     - 0
     - 0
     - 0
   * - 7 (SGFS)
     - 0
     - 10
     - 40
     - 90
     - 160
     - 150
     - 108
     - 49
     - 0
     - 0
   * - 8 (TGSS)
     - 0
     - 10
     - 40
     - 90
     - 160
     - 250
     - 216
     - 147
     - 64
     - 0
   * - 9 (TGMS, Galaxy Scoop, Enigma Pulsar)
     - 0
     - 10
     - 40
     - 90
     - 160
     - 250
     - 360
     - 294
     - 192
     - 81

Source: Posey's spreadsheet (starsautohost.org). Needs oracle verification.

Net fuel cost = ``fuel_usage_table[warp] - fuel_gain_matrix[free_warp][warp]``
per light-year (cannot go negative — excess gain is discarded).

.. todo::

   Oracle-verify fuel gain matrix values. Specifically: confirm gain at warp
   speeds below free warp (should be 0), and the exact formula used for
   non-tabulated free warp values (e.g., free warp 5 Sub-Galactic uses table
   row 5, not 6).
