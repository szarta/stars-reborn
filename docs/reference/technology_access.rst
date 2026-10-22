Technology Access
=================

Defines which technology items each race can discover and build, based on
PRT and selected LRTs.

**Source:** ``stars-reborn-research/stars-reborn/src/model/enumerations.py``
(``InitialTechnologies``, ``BaseDiscoverableTechnologies``,
``PRT_Technologies``, ``LRT_Technologies``) and
``src/model/player.py`` (removal logic).

.. todo::
   Oracle-validate PRT-exclusive access rules.  The Python engine may be
   incomplete for some PRTs (confirmed incomplete for PP starting pop;
   IS smart-bomb exclusion needs oracle confirmation).

.. todo::
   Confirm that FerretScanner / DolphinScanner / ElephantScanner and the
   Snooper planetary scanner series are in the base discoverable pool.
   They appear in the removal lists (NAS, AR) but are absent from the
   102-item ``BaseDiscoverableTechnologies`` constant and from all
   ``PRT_Technologies`` lists.  Likely a Python engine omission — the
   stars-reborn engine should treat them as universally discoverable
   (subject to NAS/AR removal).  (R-tech-access-1)

Computing Accessible Technologies
-----------------------------------

The engine computes each race's full technology pool as follows:

.. code-block:: text

   pool  = set(InitialTechnologies)
   pool |= set(BaseDiscoverableTechnologies)
   pool |= set(PRT_Technologies[race.prt])
   for lrt in race.lrts:
       pool |= set(LRT_Technologies[lrt])

   # Removals — applied in order:
   if OBRM in race.lrts:
       pool -= {RoboMiner, RoboMaxiMiner, RoboSuperMiner, MaxiMiner}
   if NAS in race.lrts:
       pool -= {FerretScanner, DolphinScanner, ElephantScanner}
       pool -= {Snooper320X, Snooper400X, Snooper620X}
   if race.prt == AR:
       pool -= {Snooper320X, Snooper400X, Snooper620X}
   if NRSE in race.lrts and IFE in race.lrts:
       pool -= {GalaxyScoop}

MT items (IDs 227–238) are not in any research pool — obtained exclusively
from the Mystery Trader encounter.

Initial Technologies
---------------------

All races start with these 13 items fully known (no research required):

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Item
     - Category
     - Notes
   * - Tritanium
     - Armor
     - Starting armor
   * - MoleskinShield
     - Shield
     - Starting shield
   * - BatScanner
     - Scanner
     - Range 0/pen 0; no scanner capability
   * - Laser
     - Beam Weapon
     - Starting beam weapon
   * - AlphaTorpedo
     - Torpedo
     - Starting torpedo; 35% base accuracy
   * - BattleComputer
     - Electrical
     - +20% torpedo accuracy, +1 initiative
   * - FuelTank
     - Mechanical
     - +250 fuel capacity
   * - QuickJump5
     - Engine
     - Battle speed 5; free at warp 1
   * - Scout
     - Ship Hull
     - Scout hull
   * - ColonyShip
     - Ship Hull
     - Colony hull
   * - SmallFreighter
     - Ship Hull
     - Smallest freighter hull
   * - OrbitalFort
     - Starbase Hull
     - Weakest starbase hull
   * - SpaceStation
     - Starbase Hull
     - Standard space station hull

Base Discoverable Technologies
---------------------------------

All races may research these 102 items, subject to removal rules.
(For full stats see :doc:`components` and :doc:`planetary_tech`.)

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Category
     - Items
   * - Armor
     - Crobmnium, CarbonicArmor, Strobnium, OrganicArmor, Kelarium,
       Neutronium, Valanium, Superlatanium
   * - Shields
     - CowhideShield, WolverineDiffuseShield, BearNeutrinoBarrier,
       GorillaDelagator, ElephantHideFortress, CompletePhaseShield
   * - Beam Weapons
     - XrayLaser, YakimoraLightPhaser, Blackjack, PhaserBazooka,
       PulsedSapper, ColloidalPhaser, GatlingGun, MiniBlaster, Bludgeon,
       MarkIVBlaster, PhasedSapper, HeavyBlaster, MyopicDisruptor, Disruptor,
       SyncroSapper, MegaDisruptor, BigMuthaCannon, StreamingPulverizer,
       AntiMatterPulverizer
   * - Torpedoes
     - BetaTorpedo, DeltaTorpedo, EpsilonTorpedo, RhoTorpedo,
       UpsilonTorpedo, OmegaTorpedo, JihadMissile, JuggernautMissile,
       DoomsdayMissile, ArmageddonMissile
   * - Bombs (normal)
     - LadyFingerBomb, BlackCatBomb, M70Bomb, M80Bomb, CherryBomb,
       LBU17Bomb, LBU32Bomb, LBU74Bomb
   * - Ship Scanners
     - RhinoScanner, MoleScanner, DNAScanner, PossumScanner, GazelleScanner,
       RNAScanner, CheetahScanner, EagleEyeScanner, PeerlessScanner
   * - Ship Scanners (penetrating)
     - FerretScanner, DolphinScanner, ElephantScanner *(see todo above)*
   * - Mining Robots
     - RoboMiniMiner; also RoboMiner, RoboMaxiMiner, RoboSuperMiner
       *(removed if OBRM)*
   * - Electrical
     - StealthCloak, SuperStealthCloak, BattleSuperComputer, BattleNexus,
       Jammer20, Jammer30, EnergyCapacitor
   * - Engines
     - LongHump6, DaddyLongLegs7, AlphaDrive8, TransGalacticDrive,
       TransStar10, RadiatingHydroRamScoop
   * - Mechanical
     - CargoPod, SuperCargoPod, SuperFuelTank, ManeuveringJet,
       Overthruster, BeamDeflector
   * - Orbital (mass drivers)
     - MassDriver7, UltraDriver10
   * - Ship Hulls
     - MediumFreighter, LargeFreighter, Frigate, Destroyer, Cruiser,
       Battleship, Privateer, Galleon, MiniBomber, B17Bomber, MiniMiner,
       SuperFuelTransport, Nubian;
       also MaxiMiner *(removed if OBRM)*
   * - Terraforming
     - GravityTerraform3/7/11/15, TemperatureTerraform3/7/11/15,
       RadiationTerraform3/7/11/15

**Not in the base pool** (PRT or LRT exclusive): all planetary scanners,
all planetary defenses, stargates, PP-exclusive mass drivers, smart/retro bombs,
ColonizationModule, MineDispenser50, most ram-scoop engines, FuelMizer,
Interspace10, GalaxyScoop, and all PRT-specific hulls and components.

PRT-Exclusive Technology Access
----------------------------------

Each PRT adds a specific set of items to its pool beyond the base.  Items
noted as *shared* appear in multiple PRT lists.

.. list-table::
   :header-rows: 1
   :widths: 8 92

   * - PRT
     - Items added to pool (beyond base)
   * - CA
     - **Planetary scanners:** Viewer50, Viewer90, Scoper150, Scoper220, Scoper280

       **Planetary defenses:** SDI, MissileBattery, LaserBattery, PlanetaryShield, NeutronShield

       **Stargate:** Stargate100_250

       **Universal:** MineDispenser50, ColonizationModule

       **Smart/special bombs:** SmartBomb, NeutronBomb, EnrichedNeutronBomb, PeerlessBomb, AnnihilatorBomb

       **CA-exclusive:** RetroBomb, OrbitalAdjuster
   * - JOAT
     - Same as CA except: **no** RetroBomb, **no** OrbitalAdjuster

       **Adds:** Stargate150_600, Stargate300_500
   * - IT
     - Same as JOAT plus:

       **IT-exclusive:** StargateAny_300, Stargate100_Any, StargateAny_800, StargateAny_Any, AntiMatterGenerator
   * - IS
     - **Planetary scanners:** Viewer50–Scoper280

       **Planetary defenses:** SDI, MissileBattery, LaserBattery, PlanetaryShield, NeutronShield

       **Stargates:** Stargate100_250, Stargate150_600, Stargate300_500

       **Universal:** MineDispenser50, ColonizationModule, SpeedTrap20

       **IS-exclusive:** FuelTransport (hull), SuperFreighter (hull), CrobySharmor,
       FieldedKelarium, TachyonDetector, MiniGun, Jammer10, Jammer50

       **No smart bombs** — IS is the only PRT without access to smart/retro bombs
   * - SD
     - **Planetary scanners:** Viewer50–Scoper280

       **Planetary defenses:** SDI, MissileBattery, LaserBattery, PlanetaryShield, NeutronShield

       **Stargates:** Stargate100_250, Stargate150_600, Stargate300_500

       **Universal:** MineDispenser50, ColonizationModule

       **Smart bombs:** SmartBomb–AnnihilatorBomb

       **SD-exclusive:** SuperMineLayer (hull), MiniMineLayer (hull), MineDispenser40,
       MineDispenser80, MineDispenser130, HeavyDispenser50, HeavyDispenser110,
       HeavyDispenser200, SpeedTrap20, SpeedTrap30, SpeedTrap50, EnergyDampener
   * - WM
     - **Planetary scanners:** Viewer50–Scoper280

       **Planetary defenses:** SDI, MissileBattery only — **no** LaserBattery,
       PlanetaryShield, or NeutronShield

       **Stargates:** Stargate100_250, Stargate150_600, Stargate300_500

       **Universal:** ColonizationModule

       **Smart bombs:** SmartBomb–AnnihilatorBomb

       **WM-exclusive:** BattleCruiser (hull), Dreadnought (hull),
       GatlingNeutrinoCannon, Blunderbuss

       **No MineDispenser50**
   * - PP
     - **Planetary scanners:** Viewer50–Scoper280

       **Planetary defenses:** SDI, MissileBattery, LaserBattery, PlanetaryShield, NeutronShield

       **Stargates:** Stargate100_250, Stargate150_600, Stargate300_500

       **Universal:** MineDispenser50, ColonizationModule

       **Smart bombs:** SmartBomb–AnnihilatorBomb

       **PP-exclusive:** MassDriver5, MassDriver6, SuperDriver8, SuperDriver9,
       UltraDriver11, UltraDriver12, UltraDriver13

       *(MassDriver7 and UltraDriver10 are in the base pool for all races)*
   * - SS
     - **Planetary scanners:** Viewer50–Scoper280

       **Planetary defenses:** SDI, MissileBattery, LaserBattery, PlanetaryShield, NeutronShield

       **Stargates:** Stargate100_250, Stargate150_600, Stargate300_500

       **Universal:** MineDispenser50, ColonizationModule

       **Smart bombs:** SmartBomb–AnnihilatorBomb

       **SS-exclusive:** StealthBomber (hull), Rogue (hull), ShadowShield,
       ChameleonScanner, PickPocketScanner, RobberBaronScanner,
       DepletedNeutronium, TransportCloaking, UltraStealthCloak
   * - HE
     - **Planetary scanners:** Viewer50–Scoper280

       **Planetary defenses:** SDI, MissileBattery, LaserBattery, PlanetaryShield, NeutronShield

       **No stargates** — HE has no stargate access (only Stargate100_250 is absent)

       **Universal:** MineDispenser50, ColonizationModule

       **Smart bombs:** SmartBomb–AnnihilatorBomb

       **HE-exclusive:** MetaMorph (hull), MiniColonyShip (hull),
       SettlersDelight (engine), FluxCapacitor

       .. note::
          HE gets SDI and MissileBattery but no stargates at all.
          Stargate100_250 is absent from the HE PRT list.
   * - AR
     - **No planetary scanners** — AR cannot research any Viewer/Scoper/Snooper

       **Planetary defenses:** SDI, MissileBattery only (no higher defenses)

       **Stargates:** Stargate100_250, Stargate150_600, Stargate300_500

       **Smart bombs:** SmartBomb–AnnihilatorBomb

       **AR-exclusive:** DeathStar (starbase hull), OrbitalConstructionModule

       **Also:** MineDispenser50

       AR does **not** get: ColonizationModule, any planetary scanners,
       LaserBattery / PlanetaryShield / NeutronShield, standard combat/freight hulls
       from PRT list (but does have them from base pool + InitialTech)

PRT Access Matrix — Selected Items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Items that vary across PRTs (✓ = accessible, — = not accessible).
Items in the base pool (accessible to all) are excluded from this table.

.. list-table::
   :header-rows: 1
   :widths: 32 7 7 7 7 7 7 7 7 7 7

   * - Item
     - CA
     - JOAT
     - IT
     - IS
     - SD
     - WM
     - PP
     - SS
     - HE
     - AR
   * - Planetary scanners (Viewer50–280)
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - —
   * - Snooper 320X / 400X / 620X
     - ?
     - ?
     - ?
     - ?
     - ?
     - ?
     - ?
     - ?
     - ?
     - —
   * - LaserBattery / PlanetaryShield / NeutronShield
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - —
     - ✓
     - ✓
     - ✓
     - —
   * - Stargate 100/250
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - —
     - ✓
   * - Stargate 150/600, 300/500
     - —
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - —
     - ✓
   * - Stargates Any/300, 100/Any, Any/800, Any/Any
     - —
     - —
     - ✓
     - —
     - —
     - —
     - —
     - —
     - —
     - —
   * - Smart/retro bombs
     - ✓
     - ✓
     - ✓
     - —
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
   * - ColonizationModule
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - —
   * - MineDispenser50
     - ✓
     - ✓
     - ✓
     - ✓
     - ✓
     - —
     - ✓
     - ✓
     - ✓
     - ✓

.. note::
   Snooper 320X / 400X / 620X show ``?`` because the Python engine source
   omits them from both ``BaseDiscoverableTechnologies`` and all
   ``PRT_Technologies`` lists, yet includes them in the NAS/AR removal list.
   The stars-reborn engine should make them universally discoverable (minus
   NAS/AR removals).  Oracle confirmation required.  (R-tech-access-1)

LRT-Exclusive Technology Access
----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - LRT
     - Items granted
     - Notes
   * - NRSE
     - Interspace10
     - Warp-10 non-ram-scoop engine with good fuel efficiency
   * - IFE
     - FuelMizer, GalaxyScoop
     - GalaxyScoop removed if race also has NRSE (see removals below)
   * - CE
     - *(none)*
     - Effect is a cost discount on engines, not a new item
   * - TT
     - TotalTerraform3, 5, 7, 10, 15, 20, 25, 30
     - All-axis terraforming; replaces axis-specific from base pool
   * - OBRM
     - *(none)*
     - Removes items (see removals); no additions
   * - ARM
     - RoboMidgetMiner, RoboUltraMiner (robots);
       MidgetMiner, Miner, UltraMiner (hulls)
     - Advanced mining capability; partially offsets OBRM if combined
   * - NAS
     - *(none)*
     - Removes items (see removals); doubles normal scanner ranges
   * - ISB
     - SpaceDock (starbase hull), UltraStation (starbase hull)
     - Improved starbase tiers; ISB also improves existing starbases' stats
   * - LSP
     - *(none)*
     - Effect is reduced starting pop only
   * - GR
     - *(none)*
     - Effect is research distribution change only
   * - BET
     - *(none)*
     - Effect is build-cost modifier; better miniaturization scaling
   * - UR
     - *(none)*
     - Effect is salvage/recycling mechanic only
   * - RS
     - *(none)*
     - Effect is shield regeneration in combat only
   * - MA
     - *(none)*
     - Effect is mineral conversion mechanic only

Technology Removals
--------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Trigger
     - Items removed from pool
   * - OBRM
     - RoboMiner, RoboMaxiMiner, RoboSuperMiner (robot components);
       MaxiMiner (ship hull)
   * - NAS
     - FerretScanner, DolphinScanner, ElephantScanner (penetrating ship scanners);
       Snooper320X, Snooper400X, Snooper620X (penetrating planetary scanners)

       Standard scanner ranges are doubled as compensation.

       Snooper500X is **not** in the removal list (apparent source bug — NAS
       races may inadvertently retain access to Snooper500X).
   * - AR (PRT)
     - Snooper320X, Snooper400X, Snooper620X

       AR cannot build any planetary scanner at all (Viewer50–Scoper280 are
       also absent from AR's ``PRT_Technologies`` list).
   * - NRSE + IFE (both)
     - GalaxyScoop

       SubGalacticFuelScoop, TransGalacticFuelScoop, and
       TransGalacticMizerScoop are listed in ``RamScoopEngines`` but the
       Python engine removal code only removes them conditionally — see
       ``player.py`` for exact trigger.  TransGalacticSuperScoop is **not**
       in the ``RamScoopEngines`` list (apparent source omission).

Source Notes
--------------

**Python engine omissions (bugs to fix in stars-reborn):**

1. ``Snooper500X`` is absent from ``AdvancedPlanetaryScanners``, so NAS/AR races
   can still research it.  Likely unintentional.

2. ``FerretScanner``, ``DolphinScanner``, ``ElephantScanner``, ``Snooper320X``,
   ``Snooper400X``, ``Snooper620X`` appear in removal lists but are absent from
   both ``BaseDiscoverableTechnologies`` and all ``PRT_Technologies`` entries.
   The stars-reborn engine should add them to the base pool.

3. ``TransGalacticSuperScoop`` is absent from ``RamScoopEngines``, so it cannot
   be removed even if NRSE+IFE is set.

4. ``TotalTerraform7`` appears twice in the TT ``LRT_Technologies`` list
   (duplicate entry; deduplication in set-union is harmless).

5. ``IS`` has no smart bombs — the only PRT without them.  Likely intentional
   (IS is a peaceful/defensive PRT) but needs oracle confirmation.

6. ``WM`` has no LaserBattery, PlanetaryShield, or NeutronShield.  Likely
   intentional (WM specialises in offense, not planetary defense).
