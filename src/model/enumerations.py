"""
    enumerations.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""


class ResourcePaths:
    IntroLogo = "resources/images/stars-reborn.png"
    TechnologyIcons = "resources/images/technology"
    SaveGamePath = "saved-games"
    LicenseFile = "LICENSE.txt"
    CreditsPath = "resources/generated_credits.html"
    UnknownPlanetPath = "resources/images/undiscovered_planet.png"
    HideArrowPath = "resources/images/hide_arrow.png"
    PlanetsPath = "resource/images/planets"
    EnglishLanguageMap = "resources/strings/english_strings.json"
    TechnologyData = "resources/data/technologies.dat"


TutorialGameName = "tutorial"


class TechnologyId:
    Viewer50 = 0
    Viewer90 = 1
    Scoper150 = 2
    Scoper220 = 3
    Scoper280 = 4
    Snooper320X = 5
    Snooper400X = 6
    Snooper500X = 7
    Snooper620X = 8
    SDI = 9
    MissileBattery = 10
    LaserBattery = 11
    PlanetaryShield = 12
    NeutronShield = 13
    Tritanium = 14
    Crobmnium = 15
    CarbonicArmor = 16
    Strobnium = 17
    OrganicArmor = 18
    Kelarium = 19
    FieldedKelarium = 20
    DepletedNeutronium = 21
    Neutronium = 22
    Valanium = 23
    Superlatanium = 24
    MoleskinShield = 25
    CowhideShield = 26
    WolverineDiffuseShield = 27
    CrobySharmor = 28
    ShadowShield = 29
    BearNeutrinoBarrier = 30
    GorillaDelagator = 31
    ElephantHideFortress = 32
    CompletePhaseShield = 33
    MineDispenser40 = 34
    MineDispenser50 = 35
    MineDispenser80 = 36
    MineDispenser130 = 37
    HeavyDispenser50 = 38
    HeavyDispenser110 = 39
    HeavyDispenser200 = 40
    SpeedTrap20 = 41
    SpeedTrap30 = 42
    SpeedTrap50 = 43
    BatScanner = 44
    RhinoScanner = 45
    MoleScanner = 46
    DNAScanner = 47
    PossumScanner = 48
    PickPocketScanner = 49
    ChameleonScanner = 50
    FerretScanner = 51
    DolphinScanner = 52
    GazelleScanner = 53
    RNAScanner = 54
    CheetahScanner = 55
    ElephantScanner = 56
    EagleEyeScanner = 57
    RobberBaronScanner = 58
    PeerlessScanner = 59
    ColonizationModule = 60
    OrbitalConstructionModule = 61
    CargoPod = 62
    SuperCargoPod = 63
    FuelTank = 64
    SuperFuelTank = 65
    ManeuveringJet = 66
    Overthruster = 67
    BeamDeflector = 68
    TransportCloaking = 69
    StealthCloak = 70
    SuperStealthCloak = 71
    UltraStealthCloak = 72
    BattleComputer = 73
    BattleSuperComputer = 74
    BattleNexus = 75
    Jammer10 = 76
    Jammer20 = 77
    Jammer30 = 78
    Jammer50 = 79
    EnergyCapacitor = 80
    FluxCapacitor = 81
    EnergyDampener = 82
    TachyonDetector = 83
    AntiMatterGenerator = 84
    TotalTerraform3 = 85
    TotalTerraform5 = 86
    TotalTerraform7 = 87
    TotalTerraform10 = 88
    TotalTerraform15 = 89
    TotalTerraform20 = 90
    TotalTerraform25 = 91
    TotalTerraform30 = 92
    GravityTerraform3 = 93
    GravityTerraform7 = 94
    GravityTerraform11 = 95
    GravityTerraform15 = 96
    TemperatureTerraform3 = 97
    TemperatureTerraform7 = 98
    TemperatureTerraform11 = 99
    TemperatureTerraform15 = 100
    RadiationTerraform3 = 101
    RadiationTerraform7 = 102
    RadiationTerraform11 = 103
    RadiationTerraform15 = 104
    RoboMidgetMiner = 105
    RoboMiniMiner = 106
    RoboMiner = 107
    RoboMaxiMiner = 108
    RoboSuperMiner = 109
    RoboUltraMiner = 110
    OrbitalAdjuster = 111
    SettlersDelight = 112
    QuickJump5 = 113
    FuelMizer = 114
    LongHump6 = 115
    DaddyLongLegs7 = 116
    AlphaDrive8 = 117
    TransGalacticDrive = 118
    Interspace10 = 119
    TransStar10 = 120
    RadiatingHydroRamScoop = 121
    SubGalacticFuelScoop = 122
    TransGalacticFuelScoop = 123
    TransGalacticSuperScoop = 124
    TransGalacticMizerScoop = 125
    GalaxyScoop = 126
    LadyFingerBomb = 127
    BlackCatBomb = 128
    M70Bomb = 129
    M80Bomb = 130
    CherryBomb = 131
    LBU17Bomb = 132
    LBU32Bomb = 133
    LBU74Bomb = 134
    RetroBomb = 135
    SmartBomb = 136
    NeutronBomb = 137
    EnrichedNeutronBomb = 138
    PeerlessBomb = 139
    AnnihilatorBomb = 140
    Stargate100_250 = 141
    StargateAny_300 = 142
    Stargate150_600 = 143
    Stargate300_500 = 144
    Stargate100_Any = 145
    StargateAny_800 = 146
    StargateAny_Any = 147
    MassDriver5 = 148
    MassDriver6 = 149
    MassDriver7 = 150
    SuperDriver8 = 151
    SuperDriver9 = 152
    UltraDriver10 = 153
    UltraDriver11 = 154
    UltraDriver12 = 155
    UltraDriver13 = 156
    OrbitalFort = 157
    SpaceDock = 158
    SpaceStation = 159
    UltraStation = 160
    DeathStar = 161
    SmallFreighter = 162
    MediumFreighter = 163
    LargeFreighter = 164
    SuperFreighter = 165
    Scout = 166
    Frigate = 167
    Destroyer = 168
    Cruiser = 169
    BattleCruiser = 170
    Battleship = 171
    Dreadnought = 172
    Privateer = 173
    Rogue = 174
    Galleon = 175
    MiniColonyShip = 176
    ColonyShip = 177
    MiniBomber = 178
    B17Bomber = 179
    StealthBomber = 180
    B52Bomber = 181
    MidgetMiner = 182
    MiniMiner = 183
    Miner = 184
    MaxiMiner = 185
    UltraMiner = 186
    FuelTransport = 187
    SuperFuelTransport = 188
    MiniMineLayer = 189
    SuperMineLayer = 190
    Nubian = 191
    MetaMorph = 192
    Laser = 193
    XrayLaser = 194
    MiniGun = 195
    YakimoraLightPhaser = 196
    Blackjack = 197
    PhaserBazooka = 198
    PulsedSapper = 199
    ColloidalPhaser = 200
    GatlingGun = 201
    MiniBlaster = 202
    Bludgeon = 203
    MarkIVBlaster = 204
    PhasedSapper = 205
    HeavyBlaster = 206
    GatlingNeutrinoCannon = 207
    MyopicDisruptor = 208
    Blunderbuss = 209
    Disruptor = 210
    SyncroSapper = 211
    MegaDisruptor = 212
    BigMuthaCannon = 213
    StreamingPulverizer = 214
    AntiMatterPulverizer = 215
    AlphaTorpedo = 216
    BetaTorpedo = 217
    DeltaTorpedo = 218
    EpsilonTorpedo = 219
    RhoTorpedo = 220
    UpsilonTorpedo = 221
    OmegaTorpedo = 222
    JihadMissile = 223
    JuggernautMissile = 224
    DoomsdayMissile = 225
    ArmageddonMissile = 226
    Hushaboom = 227
    EnigmaPulsar = 228
    MegaPolyShell = 229
    LangstonShell = 230
    MultiFunctionPod = 231
    AntiMatterTorpedo = 232
    JumpGate = 233
    GenesisDevice = 234
    MultiContainedMunition = 235
    AlienMiner = 236
    MultiCargoPod = 237
    MiniMorph = 238


class TechnologySlotType:
    BeamWeapons = 1
    Torpedoes = 2
    Armor = 4
    Shields = 8
    Electrical = 16
    Orbital = 32
    Mechanical = 64
    Bombs = 128
    MineLayers = 256
    MiningRobots = 512
    Scanners = 1024
    Orbital = 2048
    Engines = 4096
    GeneralPurpose = 8192
    Weapons = BeamWeapons | Torpedoes
    Protection = Armor | Shields
    OrbitalElect = Orbital | Electrical
    ScannerElectMech = Scanners | Electrical | Mechanical
    ShieldElectMech = Shields | Electrical | Mechanical
    MineElectMech = MineLayers | Electrical | Mechanical
    WeaponShield = Shields | Weapons
    ElectMech = Electrical | Mechanical
    ArmorScannerElectMech = Armor | Scanners | Electrical | Mechanical


class TechnologyCategory:
    All = 0
    Armor = 1
    BeamWeapons = 2
    Bombs = 3
    Electrical = 4
    Engines = 5
    Mechanical = 6
    MineLayers = 7
    MiningRobots = 8
    Orbital = 9
    Planetary = 10
    Scanners = 11
    Shields = 12
    ShipHulls = 13
    StarbaseHulls = 14
    Terraforming = 15
    Torpedoes = 16


TechnologyCategoryMapping = {
    0: [
        TechnologyId.Tritanium,
        TechnologyId.Crobmnium,
        TechnologyId.CarbonicArmor,
        TechnologyId.Strobnium,
        TechnologyId.OrganicArmor,
        TechnologyId.Kelarium,
        TechnologyId.FieldedKelarium,
        TechnologyId.DepletedNeutronium,
        TechnologyId.Neutronium,
        TechnologyId.Valanium,
        TechnologyId.Superlatanium,
        TechnologyId.Laser,
        TechnologyId.XrayLaser,
        TechnologyId.MiniGun,
        TechnologyId.YakimoraLightPhaser,
        TechnologyId.Blackjack,
        TechnologyId.PhaserBazooka,
        TechnologyId.PulsedSapper,
        TechnologyId.ColloidalPhaser,
        TechnologyId.GatlingGun,
        TechnologyId.MiniBlaster,
        TechnologyId.Bludgeon,
        TechnologyId.MarkIVBlaster,
        TechnologyId.PhasedSapper,
        TechnologyId.HeavyBlaster,
        TechnologyId.GatlingNeutrinoCannon,
        TechnologyId.MyopicDisruptor,
        TechnologyId.Blunderbuss,
        TechnologyId.Disruptor,
        TechnologyId.SyncroSapper,
        TechnologyId.MegaDisruptor,
        TechnologyId.BigMuthaCannon,
        TechnologyId.StreamingPulverizer,
        TechnologyId.AntiMatterPulverizer,
        TechnologyId.LadyFingerBomb,
        TechnologyId.BlackCatBomb,
        TechnologyId.M70Bomb,
        TechnologyId.M80Bomb,
        TechnologyId.CherryBomb,
        TechnologyId.LBU17Bomb,
        TechnologyId.LBU32Bomb,
        TechnologyId.LBU74Bomb,
        TechnologyId.RetroBomb,
        TechnologyId.SmartBomb,
        TechnologyId.NeutronBomb,
        TechnologyId.EnrichedNeutronBomb,
        TechnologyId.PeerlessBomb,
        TechnologyId.AnnihilatorBomb,
        TechnologyId.TransportCloaking,
        TechnologyId.StealthCloak,
        TechnologyId.SuperStealthCloak,
        TechnologyId.UltraStealthCloak,
        TechnologyId.BattleComputer,
        TechnologyId.BattleSuperComputer,
        TechnologyId.BattleNexus,
        TechnologyId.Jammer10,
        TechnologyId.Jammer20,
        TechnologyId.Jammer30,
        TechnologyId.Jammer50,
        TechnologyId.EnergyCapacitor,
        TechnologyId.FluxCapacitor,
        TechnologyId.EnergyDampener,
        TechnologyId.TachyonDetector,
        TechnologyId.AntiMatterGenerator,
        TechnologyId.SettlersDelight,
        TechnologyId.QuickJump5,
        TechnologyId.FuelMizer,
        TechnologyId.LongHump6,
        TechnologyId.DaddyLongLegs7,
        TechnologyId.AlphaDrive8,
        TechnologyId.TransGalacticDrive,
        TechnologyId.Interspace10,
        TechnologyId.TransStar10,
        TechnologyId.RadiatingHydroRamScoop,
        TechnologyId.SubGalacticFuelScoop,
        TechnologyId.TransGalacticFuelScoop,
        TechnologyId.TransGalacticSuperScoop,
        TechnologyId.TransGalacticMizerScoop,
        TechnologyId.GalaxyScoop,
        TechnologyId.ColonizationModule,
        TechnologyId.OrbitalConstructionModule,
        TechnologyId.CargoPod,
        TechnologyId.SuperCargoPod,
        TechnologyId.FuelTank,
        TechnologyId.SuperFuelTank,
        TechnologyId.ManeuveringJet,
        TechnologyId.Overthruster,
        TechnologyId.BeamDeflector,
        TechnologyId.MineDispenser40,
        TechnologyId.MineDispenser50,
        TechnologyId.MineDispenser80,
        TechnologyId.MineDispenser130,
        TechnologyId.HeavyDispenser50,
        TechnologyId.HeavyDispenser110,
        TechnologyId.HeavyDispenser200,
        TechnologyId.SpeedTrap20,
        TechnologyId.SpeedTrap30,
        TechnologyId.SpeedTrap50,
        TechnologyId.RoboMidgetMiner,
        TechnologyId.RoboMiniMiner,
        TechnologyId.RoboMiner,
        TechnologyId.RoboMaxiMiner,
        TechnologyId.RoboSuperMiner,
        TechnologyId.RoboUltraMiner,
        TechnologyId.Stargate100_250,
        TechnologyId.StargateAny_300,
        TechnologyId.Stargate150_600,
        TechnologyId.Stargate300_500,
        TechnologyId.Stargate100_Any,
        TechnologyId.StargateAny_800,
        TechnologyId.StargateAny_Any,
        TechnologyId.MassDriver5,
        TechnologyId.MassDriver6,
        TechnologyId.MassDriver7,
        TechnologyId.SuperDriver8,
        TechnologyId.SuperDriver9,
        TechnologyId.UltraDriver10,
        TechnologyId.UltraDriver11,
        TechnologyId.UltraDriver12,
        TechnologyId.UltraDriver13,
        TechnologyId.Viewer50,
        TechnologyId.Viewer90,
        TechnologyId.Scoper150,
        TechnologyId.Scoper220,
        TechnologyId.Scoper280,
        TechnologyId.Snooper320X,
        TechnologyId.Snooper400X,
        TechnologyId.Snooper500X,
        TechnologyId.Snooper620X,
        TechnologyId.SDI,
        TechnologyId.MissileBattery,
        TechnologyId.LaserBattery,
        TechnologyId.PlanetaryShield,
        TechnologyId.NeutronShield,
        TechnologyId.BatScanner,
        TechnologyId.RhinoScanner,
        TechnologyId.MoleScanner,
        TechnologyId.DNAScanner,
        TechnologyId.PossumScanner,
        TechnologyId.PickPocketScanner,
        TechnologyId.ChameleonScanner,
        TechnologyId.FerretScanner,
        TechnologyId.DolphinScanner,
        TechnologyId.GazelleScanner,
        TechnologyId.RNAScanner,
        TechnologyId.CheetahScanner,
        TechnologyId.ElephantScanner,
        TechnologyId.EagleEyeScanner,
        TechnologyId.RobberBaronScanner,
        TechnologyId.PeerlessScanner,
        TechnologyId.MoleskinShield,
        TechnologyId.CowhideShield,
        TechnologyId.WolverineDiffuseShield,
        TechnologyId.CrobySharmor,
        TechnologyId.ShadowShield,
        TechnologyId.BearNeutrinoBarrier,
        TechnologyId.GorillaDelagator,
        TechnologyId.ElephantHideFortress,
        TechnologyId.CompletePhaseShield,
        TechnologyId.SmallFreighter,
        TechnologyId.MediumFreighter,
        TechnologyId.LargeFreighter,
        TechnologyId.SuperFreighter,
        TechnologyId.Scout,
        TechnologyId.Frigate,
        TechnologyId.Destroyer,
        TechnologyId.Cruiser,
        TechnologyId.BattleCruiser,
        TechnologyId.Battleship,
        TechnologyId.Dreadnought,
        TechnologyId.Privateer,
        TechnologyId.Rogue,
        TechnologyId.Galleon,
        TechnologyId.MiniColonyShip,
        TechnologyId.ColonyShip,
        TechnologyId.MiniBomber,
        TechnologyId.B17Bomber,
        TechnologyId.StealthBomber,
        TechnologyId.B52Bomber,
        TechnologyId.MidgetMiner,
        TechnologyId.MiniMiner,
        TechnologyId.Miner,
        TechnologyId.MaxiMiner,
        TechnologyId.UltraMiner,
        TechnologyId.OrbitalFort,
        TechnologyId.SpaceDock,
        TechnologyId.SpaceStation,
        TechnologyId.UltraStation,
        TechnologyId.DeathStar,
        TechnologyId.TotalTerraform3,
        TechnologyId.TotalTerraform5,
        TechnologyId.TotalTerraform7,
        TechnologyId.TotalTerraform10,
        TechnologyId.TotalTerraform15,
        TechnologyId.TotalTerraform20,
        TechnologyId.TotalTerraform25,
        TechnologyId.TotalTerraform30,
        TechnologyId.GravityTerraform3,
        TechnologyId.GravityTerraform7,
        TechnologyId.GravityTerraform11,
        TechnologyId.GravityTerraform15,
        TechnologyId.TemperatureTerraform3,
        TechnologyId.TemperatureTerraform7,
        TechnologyId.TemperatureTerraform11,
        TechnologyId.TemperatureTerraform15,
        TechnologyId.RadiationTerraform3,
        TechnologyId.RadiationTerraform7,
        TechnologyId.RadiationTerraform11,
        TechnologyId.RadiationTerraform15,
        TechnologyId.AlphaTorpedo,
        TechnologyId.BetaTorpedo,
        TechnologyId.DeltaTorpedo,
        TechnologyId.EpsilonTorpedo,
        TechnologyId.RhoTorpedo,
        TechnologyId.UpsilonTorpedo,
        TechnologyId.OmegaTorpedo,
        TechnologyId.JihadMissile,
        TechnologyId.JuggernautMissile,
        TechnologyId.DoomsdayMissile,
        TechnologyId.ArmageddonMissile
    ],
    1: [
        TechnologyId.Tritanium,
        TechnologyId.Crobmnium,
        TechnologyId.CarbonicArmor,
        TechnologyId.Strobnium,
        TechnologyId.OrganicArmor,
        TechnologyId.Kelarium,
        TechnologyId.FieldedKelarium,
        TechnologyId.DepletedNeutronium,
        TechnologyId.Neutronium,
        TechnologyId.Valanium,
        TechnologyId.Superlatanium
    ],
    2: [
        TechnologyId.Laser,
        TechnologyId.XrayLaser,
        TechnologyId.MiniGun,
        TechnologyId.YakimoraLightPhaser,
        TechnologyId.Blackjack,
        TechnologyId.PhaserBazooka,
        TechnologyId.PulsedSapper,
        TechnologyId.ColloidalPhaser,
        TechnologyId.GatlingGun,
        TechnologyId.MiniBlaster,
        TechnologyId.Bludgeon,
        TechnologyId.MarkIVBlaster,
        TechnologyId.PhasedSapper,
        TechnologyId.HeavyBlaster,
        TechnologyId.GatlingNeutrinoCannon,
        TechnologyId.MyopicDisruptor,
        TechnologyId.Blunderbuss,
        TechnologyId.Disruptor,
        TechnologyId.SyncroSapper,
        TechnologyId.MegaDisruptor,
        TechnologyId.BigMuthaCannon,
        TechnologyId.StreamingPulverizer,
        TechnologyId.AntiMatterPulverizer
    ],
    3: [
        TechnologyId.LadyFingerBomb,
        TechnologyId.BlackCatBomb,
        TechnologyId.M70Bomb,
        TechnologyId.M80Bomb,
        TechnologyId.CherryBomb,
        TechnologyId.LBU17Bomb,
        TechnologyId.LBU32Bomb,
        TechnologyId.LBU74Bomb,
        TechnologyId.RetroBomb,
        TechnologyId.SmartBomb,
        TechnologyId.NeutronBomb,
        TechnologyId.EnrichedNeutronBomb,
        TechnologyId.PeerlessBomb,
        TechnologyId.AnnihilatorBomb
    ],
    4: [
        TechnologyId.TransportCloaking,
        TechnologyId.StealthCloak,
        TechnologyId.SuperStealthCloak,
        TechnologyId.UltraStealthCloak,
        TechnologyId.BattleComputer,
        TechnologyId.BattleSuperComputer,
        TechnologyId.BattleNexus,
        TechnologyId.Jammer10,
        TechnologyId.Jammer20,
        TechnologyId.Jammer30,
        TechnologyId.Jammer50,
        TechnologyId.EnergyCapacitor,
        TechnologyId.FluxCapacitor,
        TechnologyId.EnergyDampener,
        TechnologyId.TachyonDetector,
        TechnologyId.AntiMatterGenerator
    ],
    5: [
        TechnologyId.SettlersDelight,
        TechnologyId.QuickJump5,
        TechnologyId.FuelMizer,
        TechnologyId.LongHump6,
        TechnologyId.DaddyLongLegs7,
        TechnologyId.AlphaDrive8,
        TechnologyId.TransGalacticDrive,
        TechnologyId.Interspace10,
        TechnologyId.TransStar10,
        TechnologyId.RadiatingHydroRamScoop,
        TechnologyId.SubGalacticFuelScoop,
        TechnologyId.TransGalacticFuelScoop,
        TechnologyId.TransGalacticSuperScoop,
        TechnologyId.TransGalacticMizerScoop,
        TechnologyId.GalaxyScoop
    ],
    6: [
        TechnologyId.ColonizationModule,
        TechnologyId.OrbitalConstructionModule,
        TechnologyId.CargoPod,
        TechnologyId.SuperCargoPod,
        TechnologyId.FuelTank,
        TechnologyId.SuperFuelTank,
        TechnologyId.ManeuveringJet,
        TechnologyId.Overthruster,
        TechnologyId.BeamDeflector
    ],
    7: [
        TechnologyId.MineDispenser40,
        TechnologyId.MineDispenser50,
        TechnologyId.MineDispenser80,
        TechnologyId.MineDispenser130,
        TechnologyId.HeavyDispenser50,
        TechnologyId.HeavyDispenser110,
        TechnologyId.HeavyDispenser200,
        TechnologyId.SpeedTrap20,
        TechnologyId.SpeedTrap30,
        TechnologyId.SpeedTrap50
    ],
    8: [
        TechnologyId.RoboMidgetMiner,
        TechnologyId.RoboMiniMiner,
        TechnologyId.RoboMiner,
        TechnologyId.RoboMaxiMiner,
        TechnologyId.RoboSuperMiner,
        TechnologyId.RoboUltraMiner,
        TechnologyId.OrbitalAdjuster
    ],
    9: [
        TechnologyId.Stargate100_250,
        TechnologyId.StargateAny_300,
        TechnologyId.Stargate150_600,
        TechnologyId.Stargate300_500,
        TechnologyId.Stargate100_Any,
        TechnologyId.StargateAny_800,
        TechnologyId.StargateAny_Any,
        TechnologyId.MassDriver5,
        TechnologyId.MassDriver6,
        TechnologyId.MassDriver7,
        TechnologyId.SuperDriver8,
        TechnologyId.SuperDriver9,
        TechnologyId.UltraDriver10,
        TechnologyId.UltraDriver11,
        TechnologyId.UltraDriver12,
        TechnologyId.UltraDriver13
    ],
    10: [
        TechnologyId.Viewer50,
        TechnologyId.Viewer90,
        TechnologyId.Scoper150,
        TechnologyId.Scoper220,
        TechnologyId.Scoper280,
        TechnologyId.Snooper320X,
        TechnologyId.Snooper400X,
        TechnologyId.Snooper500X,
        TechnologyId.Snooper620X,
        TechnologyId.SDI,
        TechnologyId.MissileBattery,
        TechnologyId.LaserBattery,
        TechnologyId.PlanetaryShield,
        TechnologyId.NeutronShield
    ],
    11: [
        TechnologyId.BatScanner,
        TechnologyId.RhinoScanner,
        TechnologyId.MoleScanner,
        TechnologyId.DNAScanner,
        TechnologyId.PossumScanner,
        TechnologyId.PickPocketScanner,
        TechnologyId.ChameleonScanner,
        TechnologyId.FerretScanner,
        TechnologyId.DolphinScanner,
        TechnologyId.GazelleScanner,
        TechnologyId.RNAScanner,
        TechnologyId.CheetahScanner,
        TechnologyId.ElephantScanner,
        TechnologyId.EagleEyeScanner,
        TechnologyId.RobberBaronScanner,
        TechnologyId.PeerlessScanner
    ],
    12: [
        TechnologyId.MoleskinShield,
        TechnologyId.CowhideShield,
        TechnologyId.WolverineDiffuseShield,
        TechnologyId.CrobySharmor,
        TechnologyId.ShadowShield,
        TechnologyId.BearNeutrinoBarrier,
        TechnologyId.GorillaDelagator,
        TechnologyId.ElephantHideFortress,
        TechnologyId.CompletePhaseShield
    ],
    13: [
        TechnologyId.SmallFreighter,
        TechnologyId.MediumFreighter,
        TechnologyId.LargeFreighter,
        TechnologyId.SuperFreighter,
        TechnologyId.Scout,
        TechnologyId.Frigate,
        TechnologyId.Destroyer,
        TechnologyId.Cruiser,
        TechnologyId.BattleCruiser,
        TechnologyId.Battleship,
        TechnologyId.Dreadnought,
        TechnologyId.Privateer,
        TechnologyId.Rogue,
        TechnologyId.Galleon,
        TechnologyId.MiniColonyShip,
        TechnologyId.ColonyShip,
        TechnologyId.MiniBomber,
        TechnologyId.B17Bomber,
        TechnologyId.StealthBomber,
        TechnologyId.B52Bomber,
        TechnologyId.MidgetMiner,
        TechnologyId.MiniMiner,
        TechnologyId.Miner,
        TechnologyId.MaxiMiner,
        TechnologyId.UltraMiner,
        TechnologyId.MiniMineLayer,
        TechnologyId.SuperMineLayer,
        TechnologyId.Nubian,
        TechnologyId.MetaMorph
    ],
    14: [
        TechnologyId.OrbitalFort,
        TechnologyId.SpaceDock,
        TechnologyId.SpaceStation,
        TechnologyId.UltraStation,
        TechnologyId.DeathStar
    ],
    15: [
        TechnologyId.TotalTerraform3,
        TechnologyId.TotalTerraform5,
        TechnologyId.TotalTerraform7,
        TechnologyId.TotalTerraform10,
        TechnologyId.TotalTerraform15,
        TechnologyId.TotalTerraform20,
        TechnologyId.TotalTerraform25,
        TechnologyId.TotalTerraform30,
        TechnologyId.GravityTerraform3,
        TechnologyId.GravityTerraform7,
        TechnologyId.GravityTerraform11,
        TechnologyId.GravityTerraform15,
        TechnologyId.TemperatureTerraform3,
        TechnologyId.TemperatureTerraform7,
        TechnologyId.TemperatureTerraform11,
        TechnologyId.TemperatureTerraform15,
        TechnologyId.RadiationTerraform3,
        TechnologyId.RadiationTerraform7,
        TechnologyId.RadiationTerraform11,
        TechnologyId.RadiationTerraform15
    ],
    16: [
        TechnologyId.AlphaTorpedo,
        TechnologyId.BetaTorpedo,
        TechnologyId.DeltaTorpedo,
        TechnologyId.EpsilonTorpedo,
        TechnologyId.RhoTorpedo,
        TechnologyId.UpsilonTorpedo,
        TechnologyId.OmegaTorpedo,
        TechnologyId.JihadMissile,
        TechnologyId.JuggernautMissile,
        TechnologyId.DoomsdayMissile,
        TechnologyId.ArmageddonMissile
    ]
}


class VictoryConditionCategory:
    PercentPlanets = 0
    TechLevels = 1
    ExceedsSecondPlaceScore = 2
    ExceedsTotalScore = 3
    ProductionCapacity = 4
    CapitalShips = 5
    HighestScore = 6


class PlanetView:
    Normal = 0
    SurfaceMinerals = 1
    MineralConcentration = 2
    PercentPopulation = 3
    PopulationView = 4
    NoInfo = 5
    Default = Normal


class GameDifficulty:
    """
    The game difficulty determines the number of CPU players and their
    difficulty level.
    """
    Easy = 0
    Standard = 1
    Harder = 2
    Expert = 3
    Default = Standard


class GameplayOptions:
    RandomEvents = 0
    PublicPlayerScores = 1
    AcceleratedPlay = 2
    SlowTechnologyAdvances = 3
    ComputerPlayersFormAlliances = 4
    BeginnerMaximumMinerals = 5


class ResourceProductionParameter:
    Minimum = 700
    Maximum = 2500
    Step = 100


class FactoryProductionParameter:
    Minimum = 5
    Maximum = 15
    Step = 1


class FactoryCostParameter:
    Minimum = 5
    Maximum = 25
    Step = 1


class ColonistFactoryParameter:
    Minimum = 5
    Maximum = 25
    Step = 1


class MineProductionParameter:
    Minimum = 5
    Maximum = 25
    Step = 1


class MineCostParameter:
    Minimum = 2
    Maximum = 15
    Step = 1


class ColonistMineParameter:
    Minimum = 5
    Maximum = 25
    Step = 1


class GravityParameter:
    Minimum = 0.12
    Maximum = 8.0
    Step = 0.4


class TemperatureParameter:
    Minimum = -200
    Maximum = 200
    Step = 4
    MinimumRange = 80


class RadiationParameter:
    Minimum = 0
    Maximum = 100
    Step = 1


class GrowthRateParameter:
    Minimum = 1
    Maximum = 20
    Step = 1


class PrimaryRacialTrait:
    ClaimAdjuster = 0
    JackOfAllTrades = 1
    InterstellarTraveler = 2
    InnerStrength = 3
    SpaceDemolition = 4
    WarMonger = 5
    PacketPhysics = 6
    SuperStealth = 7
    HyperExpansion = 8
    AlternateReality = 9


class LesserRacialTrait:
    NoRamscoopEngines = 0
    ImprovedFuelEfficiency = 1
    CheapEngines = 2
    TotalTerraforming = 3
    OnlyBasicRemoteMining = 4
    AdvancedRemoteMining = 5
    NoAdvancedScanners = 6
    ImprovedStarbases = 7
    LowStartingPopulation = 8
    GeneralizedResearch = 9
    BleedingEdgeTechnology = 10
    UltimateRecycling = 11
    RegeneratingShields = 12
    MineralAlchemy = 13


class LeftoverPointsOption:
    SurfaceMinerals = 0
    Mines = 1
    Factories = 2
    Defenses = 3
    MineralConcentration = 4
    Default = SurfaceMinerals


class ZoomLevel:
    Level25 = 0
    Level38 = 1
    Level50 = 2
    Level100 = 3
    Level125 = 4
    Level150 = 5
    Level200 = 6
    Level400 = 7
    Lowest = Level25
    Highest = Level400
    Default = Level200

    @staticmethod
    def multipliers():
        return [
            .25,
            .38,
            .5,
            1.0,
            1.25,
            1.5,
            2.0,
            4.0
        ]

    @staticmethod
    def names():
        return [
            "25%",
            "38%",
            "50%",
            "100%",
            "125%",
            "150%",
            "200%",
            "400%"
        ]


class UniverseSize:
    Tiny = 0
    Small = 1
    Medium = 2
    Large = 3
    Huge = 4
    Default = Small


class WormholeStabilityLevel:
    RockSolid = 0
    Stable = 1
    MostlyStable = 2
    Average = 3
    SlightlyVolatile = 4
    Volatile = 5
    ExtremelyVolatile = 6


class DensityLevel:
    Sparse = 0
    Normal = 1
    Dense = 2
    Packed = 3
    Default = Normal


class ShipType:
    Unarmed = 0
    Armed = 1
    Bomber = 2
    Freighter = 3
    FuelTransport = 4


class Minerals:
    Ironium = 0
    Boranium = 1
    Germanium = 2


class Cargo:
    Ironium = 0,
    Boranium = 1
    Germanium = 2
    Colonists = 3


class ProductionCost:
    Ironium = 0
    Boranium = 1
    Germanium = 2
    Resources = 3


class ResearchAreas:
    Energy = 0,
    Weapons = 1,
    Propulsion = 2,
    Construction = 3,
    Electronics = 4,
    Biotechnology = 5
    Total = 6


class BombType:
    Normal = 0
    Smart = 1


NeverSeenPlanet = -1


class MineType:
    Normal = 0
    Heavy = 2
    Speed = 3


class PredefinedRaces:
    Antethereal = 0
    Humanoid = 1
    Insectoid = 2
    Nucleotid = 3
    Rabbitoid = 4
    Silicanoid = 5
    Default = Humanoid


class ComputerArchetypes:
    Robotoids = 0
    Turindrones = 1
    Automitrons = 2
    Rototils = 3
    Cybertrons = 4
    Macinti = 5


class ComputerRaces:
    RobotoidEasy = 0
    RobotoidNormal = 1
    RobotoidTough = 2
    RobotoidExpert = 3
    TurindroneEasy = 4
    TurindroneNormal = 5
    TurindroneTough = 6
    TurindroneExpert = 7
    AutomitronEasy = 8
    AutomitronNormal = 9
    AutomitronTough = 10
    AutomitronExpert = 11
    RototilsEasy = 12
    RototilsNormal = 13
    RototilsTough = 14
    RototilsExpert = 15
    CybertronsEasy = 16
    CybertronsNormal = 17
    CybertronsTough = 18
    CybertronsExpert = 19
    MacintiEasy = 20
    MacintiNormal = 21
    MacintiTough = 22
    MacintiExpert = 23


class CPUDifficulties:
    Easy = 0
    Normal = 1
    Tough = 2
    Expert = 3


class ResearchCostOption:
    Expensive = 0
    Normal = 1
    Cheap = 2


class PrebuiltShipDesign:
    SmaugarianPeepingTom = 0
    ArmedProbe = 1
    LongRangeScout = 2
    SantaMaria = 3
    Teamster = 4
    StalwartDefender = 5
    CottonPicker = 6


BasePopulation = 25000

StartingYear = 2400

TechnologyLevelBaseCosts = [
    0, 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770, 6100, 9870, 13850,
    18040, 22440, 27050, 31870, 36900, 42140, 47590, 53250, 59120, 65200,
    71490, 77990, 84700
]
