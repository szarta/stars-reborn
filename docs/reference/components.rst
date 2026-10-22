Ship Components
===============

All ship-installable components except engines (see :doc:`engines`) and hulls
(see :doc:`ship_hulls`, :doc:`starbase_hulls`).

**Source:** Python engine ``factory.py``.  All values need oracle verification.

Tech requirements: ``En/We/Pr/Co/El/Bio``.  Costs: ``[Ir, Bo, Ge, Resources]``.

Miniaturization: 4% cost reduction per tech level above requirement (non-BET),
minimum 25% of base cost.  BET races: 5% per level, minimum 20%, but ×2 cost
at exactly meeting requirements.  See :doc:`../mechanics/research`.

Access: see :doc:`technology_access` for PRT/LRT-specific items.

.. _armor-ref:

Armor
-----

.. list-table::
   :header-rows: 1
   :widths: 26 16 19 6 8 25

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - dp
     - Notes
   * - Tritanium
     - —
     - [5,0,0,10]
     - 60
     - 50
     - Initial tech; all races
   * - Crobmnium
     - Co 3
     - [6,0,0,13]
     - 56
     - 75
     -
   * - CarbonicArmor
     - Bio 4
     - [0,0,5,15]
     - 25
     - 100
     -
   * - Strobnium
     - Co 6
     - [8,0,0,18]
     - 54
     - 120
     -
   * - OrganicArmor
     - Bio 7
     - [0,0,6,20]
     - 15
     - 175
     -
   * - Kelarium
     - Co 9
     - [9,1,0,25]
     - 50
     - 180
     -
   * - FieldedKelarium
     - En 4 / Co 10
     - [10,0,2,28]
     - 50
     - 175
     - IS exclusive; also +50 shield dp
   * - DepletedNeutronium
     - Co 10 / El 3
     - [10,0,2,28]
     - 50
     - 200
     - SS exclusive; 25% cloaking
   * - Neutronium
     - Co 12
     - [11,2,1,30]
     - 45
     - 275
     -
   * - Valanium
     - Co 16
     - [15,0,0,50]
     - 40
     - 500
     -
   * - Superlatanium
     - Co 24
     - [25,0,0,100]
     - 30
     - 1500
     -
   * - MegaPolyShell *(MT)*
     - En 14 / Co 14 / El 14 / Bio 6
     - [14,5,5,52]
     - 20
     - 400
     - MT item; +100 shield dp; 20% cloak; 20% jammer; scan 80/40

.. _shields-ref:

Shields
-------

.. list-table::
   :header-rows: 1
   :widths: 26 16 19 6 8 25

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - dp
     - Notes
   * - MoleskinShield
     - —
     - [1,0,1,4]
     - 1
     - 25
     - Initial tech; all races
   * - CowhideShield
     - En 3
     - [2,0,2,5]
     - 1
     - 40
     -
   * - WolverineDiffuseShield
     - En 6
     - [3,0,3,6]
     - 1
     - 60
     -
   * - CrobySharmor
     - En 7 / Co 4
     - [7,0,4,15]
     - 10
     - 60
     - IS exclusive; +65 armor dp
   * - ShadowShield
     - En 7 / El 3
     - [3,0,3,7]
     - 2
     - 75
     - SS exclusive; 35% cloaking
   * - BearNeutrinoBarrier
     - En 10
     - [4,0,4,8]
     - 1
     - 100
     -
   * - GorillaDelagator
     - En 14
     - [5,0,6,11]
     - 1
     - 175
     -
   * - ElephantHideFortress
     - En 18
     - [8,0,10,15]
     - 1
     - 300
     -
   * - CompletePhaseShield
     - En 22
     - [12,0,15,20]
     - 1
     - 500
     -
   * - LangstonShell *(MT)*
     - En 12 / Pr 9 / El 9
     - [6,1,4,12]
     - 10
     - 125
     - MT item; +65 armor dp; 10% cloak; 5% jammer; scan 50/25

.. _beam-weapons-ref:

Beam Weapons
------------

``Spread`` = fires in a cone (reduced per-target damage, hits multiple ships).
``Shields only`` = damages shields; ignores armor.

.. list-table::
   :header-rows: 1
   :widths: 26 16 14 5 5 5 5 19

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - Pwr
     - Rng
     - Init
     - Notes
   * - Laser
     - —
     - [0,6,0,5]
     - 1
     - 10
     - 1
     - 9
     - Initial tech
   * - XrayLaser
     - We 3
     - [0,6,0,6]
     - 1
     - 16
     - 1
     - 9
     -
   * - MiniGun
     - We 5
     - [0,16,0,10]
     - 3
     - 13
     - 2
     - 12
     - IS exclusive; spread
   * - YakimoraLightPhaser
     - We 6
     - [0,8,0,7]
     - 1
     - 26
     - 1
     - 9
     -
   * - Blackjack
     - We 7
     - [0,16,0,7]
     - 10
     - 90
     - 0
     - 10
     - Range 0 (point-blank only)
   * - PhaserBazooka
     - We 8
     - [0,8,0,11]
     - 2
     - 26
     - 2
     - 7
     -
   * - PulsedSapper
     - En 5 / We 9
     - [0,0,4,12]
     - 1
     - 82
     - 3
     - 14
     - Shields only
   * - ColloidalPhaser
     - We 10
     - [0,14,0,18]
     - 2
     - 26
     - 3
     - 5
     -
   * - GatlingGun
     - We 11
     - [0,20,0,13]
     - 3
     - 31
     - 2
     - 12
     - Spread
   * - MiniBlaster
     - We 12
     - [0,10,0,9]
     - 1
     - 66
     - 1
     - 9
     -
   * - Bludgeon
     - We 13
     - [0,22,0,9]
     - 10
     - 231
     - 0
     - 10
     - Range 0 (point-blank only)
   * - MarkIVBlaster
     - We 14
     - [0,12,0,15]
     - 2
     - 66
     - 2
     - 7
     -
   * - PhasedSapper
     - En 8 / We 15
     - [0,0,6,16]
     - 1
     - 211
     - 3
     - 14
     - Shields only
   * - HeavyBlaster
     - En 8 / We 15
     - [0,20,0,25]
     - 2
     - 66
     - 3
     - 5
     -
   * - GatlingNeutrinoCannon
     - We 17
     - [0,28,0,17]
     - 3
     - 80
     - 2
     - 13
     - WM exclusive; spread
   * - MyopicDisruptor
     - We 18
     - [0,14,0,12]
     - 1
     - 169
     - 1
     - 9
     -
   * - Blunderbuss
     - We 19
     - [0,30,0,13]
     - 10
     - 592
     - 0
     - 11
     - WM exclusive; range 0
   * - Disruptor
     - We 20
     - [0,16,0,20]
     - 2
     - 169
     - 2
     - 8
     -
   * - SyncroSapper
     - En 11 / We 21
     - [0,0,8,21]
     - 1
     - 541
     - 3
     - 14
     - Shields only
   * - MegaDisruptor
     - We 22
     - [0,30,0,33]
     - 2
     - 169
     - 3
     - 6
     -
   * - BigMuthaCannon
     - We 23
     - [0,36,0,23]
     - 3
     - 204
     - 2
     - 13
     - Spread
   * - StreamingPulverizer
     - We 24
     - [0,20,0,16]
     - 1
     - 433
     - 1
     - 9
     -
   * - AntiMatterPulverizer
     - We 26
     - [0,22,0,27]
     - 2
     - 433
     - 2
     - 8
     -
   * - MultiContainedMunition *(MT)*
     - En 21 / We 21 / El 16 / Bio 12
     - [0,6,0,5]
     - 8
     - 140
     - 3
     - 6
     - MT item; also: +10% torpedo accuracy, 10% cloak, scan 150/75 pen,
       40 mines/yr, 2% colonist kill (300 min), 5 buildings/run

.. _torpedoes-ref:

Torpedoes
---------

Base accuracy before jammers/computers.  Computers add a bonus percentage;
jammers subtract.

.. list-table::
   :header-rows: 1
   :widths: 28 16 16 5 5 5 5 8 12

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - Pwr
     - Rng
     - Init
     - Acc%
     - Notes
   * - AlphaTorpedo
     - —
     - [9,3,3,5]
     - 25
     - 5
     - 4
     - 0
     - 35
     - Initial tech
   * - BetaTorpedo
     - We 5 / Pr 1
     - [18,6,4,6]
     - 25
     - 12
     - 4
     - 1
     - 45
     -
   * - DeltaTorpedo
     - We 10 / Pr 2
     - [22,8,5,8]
     - 25
     - 26
     - 4
     - 1
     - 60
     -
   * - EpsilonTorpedo
     - We 14 / Pr 3
     - [30,10,6,10]
     - 25
     - 48
     - 5
     - 2
     - 65
     -
   * - RhoTorpedo
     - We 18 / Pr 4
     - [34,12,8,12]
     - 25
     - 90
     - 5
     - 2
     - 75
     -
   * - UpsilonTorpedo
     - We 22 / Pr 5
     - [40,14,9,15]
     - 25
     - 169
     - 5
     - 3
     - 75
     -
   * - OmegaTorpedo
     - We 26 / Pr 6
     - [52,18,12,18]
     - 25
     - 316
     - 5
     - 4
     - 80
     -
   * - JihadMissile
     - We 12 / Pr 6
     - [37,13,9,13]
     - 35
     - 85
     - 5
     - 0
     - 20
     - High power; low accuracy
   * - JuggernautMissile
     - We 16 / Pr 8
     - [48,16,11,16]
     - 35
     - 150
     - 5
     - 1
     - 20
     -
   * - DoomsdayMissile
     - We 20 / Pr 10
     - [60,20,13,20]
     - 35
     - 280
     - 6
     - 2
     - 25
     -
   * - ArmageddonMissile
     - We 24 / Pr 10
     - [67,23,16,24]
     - 35
     - 525
     - 6
     - 3
     - 30
     -
   * - AntiMatterTorpedo *(MT)*
     - We 11 / Pr 12 / Bio 21
     - [3,8,1,50]
     - 8
     - 60
     - 6
     - 0
     - 85
     - MT item; highest accuracy of any torpedo

.. _bombs-ref:

Bombs
-----

**Normal bombs:** each bombing run kills ``kill%`` of colonists (minimum
``min_kill`` if > 0) and destroys ``bldgs`` planetary installations.

**Smart bombs:** colonists only (no building damage); defense effectiveness
halved (``P_smart = 1 − (1 − base_coverage/2)^n``).

**RetroBomb:** reverses terraforming; no colonist or building damage.  CA only.

.. list-table::
   :header-rows: 1
   :widths: 26 16 14 5 6 6 5 20

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - Kill%
     - Min kill
     - Bldgs
     - Notes
   * - LadyFingerBomb
     - We 2
     - [1,20,0,5]
     - 40
     - 0.6%
     - 300
     - 2
     -
   * - BlackCatBomb
     - We 5
     - [1,22,0,7]
     - 45
     - 0.9%
     - 300
     - 4
     -
   * - M70Bomb
     - We 8
     - [1,24,0,9]
     - 50
     - 1.2%
     - 300
     - 6
     -
   * - M80Bomb
     - We 11
     - [1,25,0,12]
     - 55
     - 1.7%
     - 300
     - 7
     -
   * - CherryBomb
     - We 14
     - [1,25,0,11]
     - 52
     - 2.5%
     - 300
     - 10
     -
   * - LBU-17 Bomb
     - We 5 / El 8
     - [1,15,15,7]
     - 30
     - 0.2%
     - 0
     - 16
     - Building-focused
   * - LBU-32 Bomb
     - We 10 / El 10
     - [1,24,15,10]
     - 35
     - 0.3%
     - 0
     - 28
     - Building-focused
   * - LBU-74 Bomb
     - We 15 / El 12
     - [1,33,12,14]
     - 45
     - 0.4%
     - 0
     - 45
     - Building-focused
   * - RetroBomb
     - We 10 / Bio 12
     - [15,15,10,50]
     - 45
     - 0%
     - 0
     - 0
     - CA exclusive; reverses terraforming; no kills
   * - SmartBomb
     - We 5 / Bio 7
     - [1,22,0,27]
     - 50
     - 1.3%
     - 0
     - 0
     - Smart; all PRTs except IS
   * - NeutronBomb
     - We 10 / Bio 10
     - [1,30,0,30]
     - 57
     - 2.2%
     - 0
     - 0
     - Smart; all PRTs except IS
   * - EnrichedNeutronBomb
     - We 15 / Bio 12
     - [1,36,0,25]
     - 64
     - 3.5%
     - 0
     - 0
     - Smart; all PRTs except IS
   * - PeerlessBomb
     - We 22 / Bio 15
     - [1,33,0,32]
     - 55
     - 5.0%
     - 0
     - 0
     - Smart; all PRTs except IS
   * - AnnihilatorBomb
     - We 26 / Bio 17
     - [1,30,0,28]
     - 50
     - 7.0%
     - 0
     - 0
     - Smart; highest kill rate; all PRTs except IS
   * - Hushaboom *(MT)*
     - We 12 / El 12 / Bio 12
     - [1,2,0,2]
     - 5
     - 3.0%
     - 300
     - 2
     - MT item; normal bomb; very light mass

.. _ship-scanners-ref:

Ship Scanners
-------------

Ranges in light-years.  Penetrating range = range at which colonists/minerals
on enemy planets are visible (non-zero only for pen scanners).

.. list-table::
   :header-rows: 1
   :widths: 28 16 16 5 8 8 19

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - Range
     - Pen
     - Notes
   * - BatScanner
     - —
     - [1,0,1,1]
     - 2
     - 0
     - 0
     - Initial tech; no scan capability
   * - RhinoScanner
     - El 1
     - [3,0,2,3]
     - 5
     - 50
     - 0
     -
   * - MoleScanner
     - El 4
     - [2,0,2,9]
     - 2
     - 100
     - 0
     -
   * - DNAScanner
     - Pr 3 / Bio 6
     - [1,1,1,5]
     - 2
     - 125
     - 0
     -
   * - PossumScanner
     - El 5
     - [3,0,3,18]
     - 3
     - 150
     - 0
     -
   * - PickPocketScanner
     - En 4 / El 4 / Bio 4
     - [8,10,6,35]
     - 15
     - 80
     - 0
     - SS exclusive; steals minerals from enemy fleets
   * - ChameleonScanner
     - En 3 / El 6
     - [4,6,4,25]
     - 6
     - 160
     - 45
     - SS exclusive; 20% cloaking
   * - FerretScanner
     - En 3 / El 7 / Bio 2
     - [2,0,8,36]
     - 2
     - 185
     - 50
     - Removed if NAS
   * - DolphinScanner
     - En 5 / El 10 / Bio 4
     - [5,5,10,40]
     - 4
     - 220
     - 100
     - Removed if NAS
   * - GazelleScanner
     - El 8
     - [4,0,5,24]
     - 4
     - 225
     - 0
     -
   * - RNAScanner
     - Pr 5 / Bio 10
     - [1,1,2,20]
     - 2
     - 230
     - 0
     -
   * - CheetahScanner
     - El 11
     - [3,1,13,50]
     - 4
     - 275
     - 0
     -
   * - ElephantScanner
     - En 6 / El 16 / Bio 7
     - [8,5,14,70]
     - 6
     - 300
     - 200
     - Removed if NAS
   * - EagleEyeScanner
     - El 14
     - [3,2,21,64]
     - 3
     - 335
     - 0
     -
   * - RobberBaronScanner
     - En 10 / El 15 / Bio 10
     - [10,10,10,90]
     - 20
     - 220
     - 120
     - SS exclusive; steals minerals from enemy planets
   * - PeerlessScanner
     - El 24
     - [3,2,30,90]
     - 4
     - 500
     - 0
     -

.. _mine-layers-ref:

Mine Layers
-----------

All mine fields: hit chance per light-year traveled through the field.
**Normal:** min safe warp 4, 0.3%/ly hit, 100 dmg/engine (125 vs. ram scoops),
500 min fleet dmg (600 vs. ram scoops).
**Heavy:** min safe warp 6, 1.0%/ly, 500 dmg/engine (600 vs. ram scoops),
2000 min fleet dmg (2500 vs. ram scoops).
**Speed trap:** min safe warp 5, 3.5%/ly, 0 dmg — drops fleet to safe speed.

.. list-table::
   :header-rows: 1
   :widths: 26 16 16 5 12 12 12

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - Mine type
     - Mines/yr
     - Access
   * - MineDispenser40
     - —
     - [2,10,8,45]
     - 25
     - Normal
     - 40
     - SD only
   * - MineDispenser50
     - En 2 / Bio 4
     - [2,12,10,55]
     - 30
     - Normal
     - 50
     - All PRTs (universal)
   * - MineDispenser80
     - En 3 / Bio 7
     - [2,14,10,65]
     - 30
     - Normal
     - 80
     - SD only
   * - MineDispenser130
     - En 6 / Bio 12
     - [2,18,10,80]
     - 30
     - Normal
     - 130
     - SD only
   * - HeavyDispenser50
     - En 5 / Bio 3
     - [2,20,5,50]
     - 10
     - Heavy
     - 50
     - SD only
   * - HeavyDispenser110
     - En 9 / Bio 5
     - [2,30,5,70]
     - 15
     - Heavy
     - 110
     - SD only
   * - HeavyDispenser200
     - En 14 / Bio 7
     - [2,45,5,90]
     - 20
     - Heavy
     - 200
     - SD only
   * - SpeedTrap20
     - Pr 2 / Bio 2
     - [29,0,12,58]
     - 100
     - Speed
     - 20
     - IS and SD
   * - SpeedTrap30
     - Pr 3 / Bio 6
     - [32,0,14,72]
     - 135
     - Speed
     - 30
     - SD only
   * - SpeedTrap50
     - Pr 5 / Bio 11
     - [32,0,14,72]
     - 140
     - Speed
     - 50
     - SD only

.. _mining-robots-ref:

Mining Robots
-------------

``mining_value`` = kT of minerals mined per robot per year from a planet.

.. list-table::
   :header-rows: 1
   :widths: 26 16 16 5 10 16

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - Mining
     - Access
   * - RoboMidgetMiner
     - —
     - [12,0,4,44]
     - 80
     - 5
     - ARM only
   * - RoboMiniMiner
     - Co 2 / El 1
     - [29,0,7,96]
     - 240
     - 4
     - Base pool (all races)
   * - RoboMiner
     - Co 4 / El 2
     - [30,0,7,100]
     - 240
     - 12
     - Base pool; removed if OBRM
   * - RoboMaxiMiner
     - Co 7 / El 4
     - [30,0,7,100]
     - 240
     - 18
     - Base pool; removed if OBRM
   * - RoboSuperMiner
     - Co 12 / El 6
     - [30,0,7,100]
     - 240
     - 27
     - Base pool; removed if OBRM
   * - RoboUltraMiner
     - Co 15 / El 8
     - [14,0,4,50]
     - 80
     - 25
     - ARM only
   * - OrbitalAdjuster
     - Bio 6
     - [25,25,25,50]
     - 80
     - —
     - CA exclusive; adjusts planetary hab (not a mining robot despite occupying
       that slot type); 25% cloaking
   * - AlienMiner *(MT)*
     - En 5 / Co 10 / El 5 / Bio 5
     - [4,0,1,10]
     - 20
     - 10
     - MT item; 30% cloak; 30% jammer; +1/8 battle speed

.. _mechanical-ref:

Mechanical Components
---------------------

.. list-table::
   :header-rows: 1
   :widths: 26 16 16 5 37

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - Function
   * - ColonizationModule
     - —
     - [12,10,10,10]
     - 32
     - Enables colonization (required in colony ship designs); all PRTs via PRT lists
   * - OrbitalConstructionModule
     - —
     - [20,15,15,20]
     - 50
     - Enables starbase construction; AR exclusive
   * - CargoPod
     - Co 3
     - [5,0,2,10]
     - 5
     - +50 cargo capacity
   * - SuperCargoPod
     - En 3 / Co 9
     - [8,0,2,15]
     - 7
     - +100 cargo capacity
   * - FuelTank
     - —
     - [5,0,0,4]
     - 3
     - +250 fuel capacity; initial tech
   * - SuperFuelTank
     - En 6 / Pr 4 / Co 14
     - [8,0,0,8]
     - 8
     - +500 fuel capacity
   * - ManeuveringJet
     - En 2 / Pr 3
     - [5,0,5,10]
     - 5
     - +0.25 battle speed
   * - Overthruster
     - En 5 / Pr 12
     - [10,0,8,20]
     - 5
     - +0.50 battle speed
   * - BeamDeflector
     - En 6 / We 6 / Co 6 / El 6
     - [0,0,10,8]
     - 1
     - Reduces incoming beam weapon damage by 10%
   * - JumpGate *(MT)*
     - En 16 / Pr 20 / Co 20 / El 16
     - [0,0,38,30]
     - 10
     - MT item; allows fleet teleportation via stargate network
   * - MultiCargoPod *(MT)*
     - En 5 / Co 11 / El 5
     - [12,0,3,25]
     - 9
     - MT item; +250 cargo; 10% cloak; +50 armor dp
   * - GenesisDevice *(MT)*
     - En 20 / We 10 / Pr 10 / Co 20 / El 10 / Bio 20
     - [0,0,0,5000]
     - 0
     - MT item; one-use; sets all three hab axes to race ideal (100% value) on any planet

.. _electrical-ref:

Electrical Components
---------------------

Cloak percentages stack multiplicatively in the engine.  Jammer percentages
reduce incoming torpedo hit chance.

.. list-table::
   :header-rows: 1
   :widths: 26 16 14 5 39

   * - Item
     - Tech Req
     - Cost [Ir,Bo,Ge,R]
     - Mass
     - Function
   * - TransportCloaking
     - —
     - [2,0,2,3]
     - 1
     - 75% cloaking; SS exclusive
   * - StealthCloak
     - En 2 / El 5
     - [2,0,2,5]
     - 2
     - 35% cloaking
   * - SuperStealthCloak
     - En 4 / El 10
     - [8,0,8,15]
     - 3
     - 55% cloaking
   * - UltraStealthCloak
     - En 10 / El 12
     - [10,0,10,25]
     - 5
     - 85% cloaking; SS exclusive
   * - BattleComputer
     - —
     - [0,0,13,5]
     - 1
     - +1 initiative; +20% torpedo accuracy; initial tech
   * - BattleSuperComputer
     - En 5 / El 11
     - [0,0,25,14]
     - 1
     - +2 initiative; +30% torpedo accuracy
   * - BattleNexus
     - En 10 / El 19
     - [0,0,30,15]
     - 1
     - +3 initiative; +50% torpedo accuracy
   * - Jammer10
     - En 2 / El 6
     - [0,0,2,6]
     - 1
     - 10% torpedo jamming; IS exclusive
   * - Jammer20
     - En 4 / El 10
     - [1,0,5,20]
     - 1
     - 20% torpedo jamming
   * - Jammer30
     - En 8 / El 16
     - [1,0,6,20]
     - 1
     - 30% torpedo jamming
   * - Jammer50
     - En 16 / El 22
     - [2,0,7,20]
     - 1
     - 50% torpedo jamming; IS exclusive
   * - EnergyCapacitor
     - En 7 / El 4
     - [0,0,8,5]
     - 1
     - +10% beam weapon damage
   * - FluxCapacitor
     - En 14 / El 8
     - [0,0,8,5]
     - 1
     - +20% beam weapon damage; HE exclusive
   * - EnergyDampener
     - En 14 / El 8
     - [5,10,0,50]
     - 2
     - Reduces enemy fleet battle speed during combat; SD exclusive
   * - TachyonDetector
     - En 8 / El 14
     - [1,5,0,70]
     - 1
     - Reveals cloaked ships; IS exclusive
   * - AntiMatterGenerator
     - We 12 / Bio 7
     - [8,3,3,10]
     - 10
     - +200 fuel capacity; generates 50 fuel/year passively; IT exclusive
   * - MultiFunctionPod *(MT)*
     - En 11 / Pr 11 / El 11
     - [4,0,4,13]
     - 2
     - MT item; 30% cloak; 10% jammer; +0.25 battle speed
