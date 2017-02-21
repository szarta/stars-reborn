"""
    factory.py

    The factory functions that generate many of the preconfigured data files
    used by the game.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from polygon import Polygon
from model.technology import Technology
from model.technology import Armor
from model.technology import BeamWeapon
from model.technology import Bomb
from model.technology import Electrical
from model.technology import Engine
from model.technology import MassDriver
from model.technology import Mechanical
from model.technology import MineLayer
from model.technology import MiningRobot
from model.technology import PlanetaryScanner
from model.technology import PlanetaryDefense
from model.technology import Scanner
from model.technology import Shield
from model.technology import Stargate
from model.technology import Terraforming
from model.technology import StarbaseHull
from model.technology import ShipHull
from model.technology import Torpedo
from model.technology import ShipDesign

from model.enumerations import TechnologyId
from model.enumerations import TechnologySlotType
from model.enumerations import MineType
from model.enumerations import TutorialGameSaveName

from model.enumerations import PrebuiltShipDesign

from model.universe import Universe
from model.space import Planet
from model.game import Game
from model.game import VictoryConditions
from model.game import VictoryConditionParameters

from model.race import Race
from model.player import Player
from model.player import CPU
from model.space import set_player_homeworld
from model.enumerations import PredefinedRaces
from model.enumerations import ComputerRaces
from model.enumerations import LesserRacialTrait
from model.enumerations import PrimaryRacialTrait
from model.enumerations import LeftoverPointsOption
from model.enumerations import ResearchCostOption
from model.enumerations import CPUDifficulties

from data import Language_Map


def build_tutorial_game():
    tut = Game()
    tut.name = Language_Map["tutorial-name"]
    tut.save_name = TutorialGameSaveName

    tut.universe = build_tutorial_universe()

    tut.slower_tech_advances = False
    tut.accelerated_play = True
    tut.random_events = False
    tut.cpu_players_form_alliances = False
    tut.public_player_scores = True

    vc = VictoryConditions()
    vc.conditions_needed = 1
    vc.condition_enabled[VictoryConditions.HighestScoreYears] = True
    vc.set_victory_parameter(VictoryConditionParameters.HighestScoreYears, 30)
    vc.set_victory_parameter(VictoryConditionParameters.MinimumYears, 30)
    tut.victory_conditions = vc

    p1 = Player(0)
    p1.race = createHumanoid()
    tut.players[p1.id] = p1
    set_player_homeworld(p1, tut.universe.planets[14])

    p2 = CPU(1, CPUDifficulties.Expert, None)
    p2.race = createRobotoidExpert()
    set_player_homeworld(p2, tut.universe.planets[11])
    tut.players[p2.id] = p2
    return tut


def build_tutorial_universe():
    playable_area = Polygon([(0, 0), (0, 400), (400, 400), (400, 0)])

    tutorial_universe = Universe(playable_area)

    p = Planet(8, (130, 28), "Mohlodi")
    p.ironium_concentration = 25
    p.boranium_concentration = 26
    p.germanium_concentration = 18
    p.gravity = 5.84
    p.temperature = -36
    p.radiation = 44
    tutorial_universe.planets[p.id] = p

    p = Planet(21, (366, 15), "Castle")
    p.ironium_concentration = 70
    p.boranium_concentration = 92
    p.germanium_concentration = 21
    p.gravity = 0.13
    p.temperature = 172
    p.radiation = 39
    tutorial_universe.planets[p.id] = p

    p = Planet(20, (366, 53), "Mobius")
    p.ironium_concentration = 85
    p.boranium_concentration = 72
    p.germanium_concentration = 97
    p.gravity = 0.17
    p.temperature = 68
    p.radiation = 86
    tutorial_universe.planets[p.id] = p

    p = Planet(22, (382, 98), "Dwarte")
    p.ironium_concentration = 98
    p.boranium_concentration = 61
    p.germanium_concentration = 53
    p.gravity = 3.68
    p.temperature = 104
    p.radiation = 98
    tutorial_universe.planets[p.id] = p

    p = Planet(17, (295, 131), "90210")
    p.ironium_concentration = 85
    p.boranium_concentration = 82
    p.germanium_concentration = 62
    p.gravity = 1.76
    p.temperature = -120
    p.radiation = 44
    tutorial_universe.planets[p.id] = p

    p = Planet(14, (237, 127), "Stove Top")
    p.boranium_concentration = 70
    p.germanium_concentration = 84
    p.ironium_concentration = 25
    p.gravity = 1.0
    p.temperature = 0
    p.radiation = 50
    p.boranium_on_surface = 477
    p.germanium_on_surface = 622
    p.ironium_on_surface = 424
    tutorial_universe.planets[p.id] = p

    p = Planet(13, (190, 112), "Prune")
    p.ironium_concentration = 87
    p.boranium_concentration = 41
    p.germanium_concentration = 109
    p.gravity = 1.08
    p.temperature = 160
    p.radiation = 62
    tutorial_universe.planets[p.id] = p

    p = Planet(10, (148, 104), "Hiho")
    p.ironium_concentration = 68
    p.boranium_concentration = 77
    p.germanium_concentration = 23
    p.gravity = 1.68
    p.temperature = 72
    p.radiation = 9
    tutorial_universe.planets[p.id] = p

    p = Planet(4, (105, 129), "No Vacancy")
    p.ironium_concentration = 85
    p.boranium_concentration = 46
    p.germanium_concentration = 43
    p.gravity = 3.20
    p.temperature = 28
    p.radiation = 98
    tutorial_universe.planets[p.id] = p

    p = Planet(3, (85, 187), "Oxygen")
    p.ironium_concentration = 89
    p.boranium_concentration = 92
    p.germanium_concentration = 88
    p.gravity = 0.60
    p.temperature = 104
    p.radiation = 13
    tutorial_universe.planets[p.id] = p

    p = Planet(9, (131, 184), "Slime")
    p.ironium_concentration = 4
    p.boranium_concentration = 2
    p.germanium_concentration = 6
    p.gravity = 0.51
    p.temperature = -60
    p.radiation = 13
    tutorial_universe.planets[p.id] = p

    p = Planet(6, (121, 203), "Wallaby")
    p.ironium_concentration = 80
    p.boranium_concentration = 100
    p.germanium_concentration = 61
    p.gravity = 3.44
    p.temperature = 16
    p.radiation = 92
    tutorial_universe.planets[p.id] = p

    p = Planet(16, (263, 186), "Alexander")
    p.ironium_concentration = 95
    p.boranium_concentration = 11
    p.germanium_concentration = 8
    p.gravity = 0.13
    p.temperature = -76
    p.radiation = 7
    tutorial_universe.planets[p.id] = p

    # This is the AI home planet (Expert Berserker)
    p = Planet(11, (149, 265), "Hacker")
    p.ironium_concentration = 25
    p.boranium_concentration = 64
    p.germanium_concentration = 75
    p.gravity = 1.32
    p.temperature = -60
    p.radiation = 65
    tutorial_universe.planets[p.id] = p

    p = Planet(12, (157, 255), "Neil")
    p.ironium_concentration = 4
    p.boranium_concentration = 84
    p.germanium_concentration = 103
    p.gravity = 0.56
    p.temperature = -160
    p.radiation = 82
    tutorial_universe.planets[p.id] = p

    p = Planet(5, (118, 257), "Mozart")
    p.ironium_concentration = 83
    p.boranium_concentration = 22
    p.germanium_concentration = 13
    p.gravity = 1.44
    p.temperature = 112
    p.radiation = 27
    tutorial_universe.planets[p.id] = p

    p = Planet(15, (263, 270), "Shaggy Dog")
    p.ironium_concentration = 82
    p.boranium_concentration = 44
    p.germanium_concentration = 91
    p.gravity = 1.56
    p.temperature = 20
    p.radiation = 74
    tutorial_universe.planets[p.id] = p

    p = Planet(18, (320, 294), "Sea Squared")
    p.ironium_concentration = 107
    p.boranium_concentration = 96
    p.germanium_concentration = 47
    p.gravity = 0.33
    p.temperature = -124
    p.radiation = 19
    tutorial_universe.planets[p.id] = p

    p = Planet(19, (352, 254), "Red Storm")
    p.ironium_concentration = 96
    p.boranium_concentration = 71
    p.germanium_concentration = 76
    p.gravity = 1.56
    p.temperature = -84
    p.radiation = 48
    tutorial_universe.planets[p.id] = p

    p = Planet(24, (386, 218), "Bloop")
    p.ironium_concentration = 102
    p.boranium_concentration = 20
    p.germanium_concentration = 62
    p.gravity = 1.44
    p.temperature = 136
    p.radiation = 34
    tutorial_universe.planets[p.id] = p

    p = Planet(23, (385, 196), "Kalamazoo")
    p.ironium_concentration = 4
    p.boranium_concentration = 93
    p.germanium_concentration = 50
    p.gravity = 0.24
    p.temperature = -96
    p.radiation = 79
    tutorial_universe.planets[p.id] = p

    p = Planet(7, (127, 369), "La Te Da")
    p.ironium_concentration = 20
    p.boranium_concentration = 72
    p.germanium_concentration = 2
    p.gravity = 0.21
    p.temperature = 48
    p.radiation = 32
    tutorial_universe.planets[p.id] = p

    p = Planet(2, (74, 369), "Speed Bump")
    p.ironium_concentration = 57
    p.boranium_concentration = 72
    p.germanium_concentration = 64
    p.gravity = 2.00
    p.temperature = -116
    p.radiation = 59
    tutorial_universe.planets[p.id] = p

    p = Planet(1, (26, 345), "Lever")
    p.ironium_concentration = 24
    p.boranium_concentration = 70
    p.germanium_concentration = 84
    p.gravity = 0.67
    p.temperature = -44
    p.radiation = 46
    tutorial_universe.planets[p.id] = p

    return tutorial_universe


def build_technology():
    technologies = {}

    cost = [10, 10, 70, 100]
    requirements = [0, 0, 0, 0, 0, 0]
    basic_range = 50
    penetrating_range = 0
    technologies[TechnologyId.Viewer50] = PlanetaryScanner(
        requirements, cost, basic_range, penetrating_range)

    requirements = [0, 0, 0, 0, 1, 0]
    basic_range = 90
    penetrating_range = 0
    technologies[TechnologyId.Viewer90] = PlanetaryScanner(
        requirements, cost, basic_range, penetrating_range)

    requirements = [0, 0, 0, 0, 3, 0]
    basic_range = 150
    penetrating_range = 0
    technologies[TechnologyId.Scoper150] = PlanetaryScanner(
        requirements, cost, basic_range, penetrating_range)

    requirements = [0, 0, 0, 0, 6, 0]
    technologies[TechnologyId.Scoper220] = PlanetaryScanner(
        requirements, cost, 220, 0)

    requirements = [0, 0, 0, 0, 8, 0]
    technologies[TechnologyId.Scoper280] = PlanetaryScanner(
        requirements, cost, 280, 0)

    requirements = [3, 0, 0, 0, 10, 3]
    technologies[TechnologyId.Snooper320X] = PlanetaryScanner(
        requirements, cost, 320, 160)

    requirements = [4, 0, 0, 0, 13, 6]
    technologies[TechnologyId.Snooper400X] = PlanetaryScanner(
        requirements, cost, 400, 200)

    requirements = [5, 0, 0, 0, 16, 7]
    technologies[TechnologyId.Snooper500X] = PlanetaryScanner(
        requirements, cost, 500, 250)

    requirements = [7, 0, 0, 0, 23, 9]
    technologies[TechnologyId.Snooper620X] = PlanetaryScanner(
        requirements, cost, 620, 310)

    cost = [5, 5, 5, 15]
    requirements = [0, 0, 0, 0, 0, 0]
    technologies[TechnologyId.SDI] = PlanetaryDefense(
        requirements, cost, 0.0099)

    cost = [5, 5, 5, 15]
    requirements = [5, 0, 0, 0, 0, 0]
    technologies[TechnologyId.MissileBattery] = PlanetaryDefense(
        requirements, cost, 0.0199)

    cost = [5, 5, 5, 15]
    requirements = [10, 0, 0, 0, 0, 0]
    technologies[TechnologyId.LaserBattery] = PlanetaryDefense(
        requirements, cost, 0.0239)

    cost = [5, 5, 5, 15]
    requirements = [16, 0, 0, 0, 0, 0]
    technologies[TechnologyId.PlanetaryShield] = PlanetaryDefense(
        requirements, cost, 0.0299)

    cost = [5, 5, 5, 15]
    requirements = [23, 0, 0, 0, 0, 0]
    technologies[TechnologyId.NeutronShield] = PlanetaryDefense(
        requirements, cost, 0.0379)

    cost = [5, 0, 0, 10]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 60
    armor = 50
    technologies[TechnologyId.Tritanium] = Armor(
        requirements, cost, mass, armor)

    cost = [6, 0, 0, 13]
    requirements = [0, 0, 0, 3, 0, 0]
    mass = 56
    armor = 75
    technologies[TechnologyId.Crobmnium] = Armor(
        requirements, cost, mass, armor)

    cost = [0, 0, 5, 15]
    requirements = [0, 0, 0, 0, 0, 4]
    mass = 25
    armor = 100
    technologies[TechnologyId.CarbonicArmor] = Armor(
        requirements, cost, mass, armor)

    cost = [8, 0, 0, 18]
    requirements = [0, 0, 0, 6, 0, 0]
    mass = 54
    armor = 120
    technologies[TechnologyId.Strobnium] = Armor(
        requirements, cost, mass, armor)

    cost = [0, 0, 6, 20]
    requirements = [0, 0, 0, 0, 0, 7]
    mass = 15
    armor = 175
    technologies[TechnologyId.OrganicArmor] = Armor(
        requirements, cost, mass, armor)

    cost = [9, 1, 0, 25]
    requirements = [0, 0, 0, 9, 0, 0]
    mass = 50
    armor = 180
    technologies[TechnologyId.Kelarium] = Armor(
        requirements, cost, mass, armor)

    cost = [10, 0, 2, 28]
    requirements = [4, 0, 0, 10, 0, 0]
    mass = 50
    armor = 175
    technologies[TechnologyId.FieldedKelarium] = Armor(
        requirements, cost, mass, armor)

    technologies[TechnologyId.FieldedKelarium].shield_value = 50

    cost = [10, 0, 2, 28]
    requirements = [0, 0, 0, 10, 3, 0]
    mass = 50
    armor = 200
    technologies[TechnologyId.DepletedNeutronium] = Armor(
        requirements, cost, mass, armor)

    technologies[TechnologyId.DepletedNeutronium].cloaking = 25

    cost = [11, 2, 1, 30]
    requirements = [0, 0, 0, 12, 0, 0]
    mass = 45
    armor = 275
    technologies[TechnologyId.Neutronium] = Armor(
        requirements, cost, mass, armor)

    cost = [15, 0, 0, 50]
    requirements = [0, 0, 0, 16, 0, 0]
    mass = 40
    armor = 500
    technologies[TechnologyId.Valanium] = Armor(
        requirements, cost, mass, armor)

    cost = [25, 0, 0, 100]
    requirements = [0, 0, 0, 24, 0, 0]
    mass = 30
    armor = 1500
    technologies[TechnologyId.Superlatanium] = Armor(
        requirements, cost, mass, armor)

    cost = [1, 0, 1, 4]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 1
    shields = 25
    technologies[TechnologyId.MoleskinShield] = Shield(
        requirements, cost, mass, shields)

    cost = [2, 0, 2, 5]
    requirements = [3, 0, 0, 0, 0, 0]
    mass = 1
    shields = 40
    technologies[TechnologyId.CowhideShield] = Shield(
        requirements, cost, mass, shields)

    cost = [3, 0, 3, 6]
    requirements = [6, 0, 0, 0, 0, 0]
    mass = 1
    shields = 60
    technologies[TechnologyId.WolverineDiffuseShield] = Shield(
        requirements, cost, mass, shields)

    cost = [7, 0, 4, 15]
    requirements = [7, 0, 0, 4, 0, 0]
    mass = 10
    shields = 60
    technologies[TechnologyId.CrobySharmor] = Shield(
        requirements, cost, mass, shields)

    technologies[TechnologyId.CrobySharmor].armor_value = 65

    cost = [3, 0, 3, 7]
    requirements = [7, 0, 0, 0, 3, 0]
    mass = 2
    shields = 75
    technologies[TechnologyId.ShadowShield] = Shield(
        requirements, cost, mass, shields)

    technologies[TechnologyId.ShadowShield].cloaking = 35

    cost = [4, 0, 4, 8]
    requirements = [10, 0, 0, 0, 0, 0]
    mass = 1
    shields = 100
    technologies[TechnologyId.BearNeutrinoBarrier] = Shield(
        requirements, cost, mass, shields)

    cost = [5, 0, 6, 11]
    requirements = [14, 0, 0, 0, 0, 0]
    mass = 1
    shields = 175
    technologies[TechnologyId.GorillaDelagator] = Shield(
        requirements, cost, mass, shields)

    cost = [8, 0, 10, 15]
    requirements = [18, 0, 0, 0, 0, 0]
    mass = 1
    shields = 300
    technologies[TechnologyId.ElephantHideFortress] = Shield(
        requirements, cost, mass, shields)

    cost = [12, 0, 15, 20]
    requirements = [22, 0, 0, 0, 0, 0]
    mass = 1
    shields = 500
    technologies[TechnologyId.CompletePhaseShield] = Shield(
        requirements, cost, mass, shields)

    cost = [2, 10, 8, 45]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 25
    mines_per_year = 40
    mine_type = MineType.Normal
    technologies[TechnologyId.MineDispenser40] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [2, 12, 10, 55]
    requirements = [2, 0, 0, 0, 0, 4]
    mass = 30
    mines_per_year = 50
    mine_type = MineType.Normal
    technologies[TechnologyId.MineDispenser50] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [2, 14, 10, 65]
    requirements = [3, 0, 0, 0, 0, 7]
    mass = 30
    mines_per_year = 80
    mine_type = MineType.Normal
    technologies[TechnologyId.MineDispenser80] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [2, 18, 10, 80]
    requirements = [6, 0, 0, 0, 0, 12]
    mass = 30
    mines_per_year = 130
    mine_type = MineType.Normal
    technologies[TechnologyId.MineDispenser130] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [2, 20, 5, 50]
    requirements = [5, 0, 0, 0, 0, 3]
    mass = 10
    mines_per_year = 50
    mine_type = MineType.Heavy
    technologies[TechnologyId.HeavyDispenser50] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [2, 30, 5, 70]
    requirements = [9, 0, 0, 0, 0, 5]
    mass = 15
    mines_per_year = 110
    mine_type = MineType.Heavy
    technologies[TechnologyId.HeavyDispenser110] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [2, 45, 5, 90]
    requirements = [14, 0, 0, 0, 0, 7]
    mass = 20
    mines_per_year = 200
    mine_type = MineType.Heavy
    technologies[TechnologyId.HeavyDispenser200] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [29, 0, 12, 58]
    requirements = [0, 0, 2, 0, 0, 2]
    mass = 100
    mines_per_year = 20
    mine_type = MineType.Speed
    technologies[TechnologyId.SpeedTrap20] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [32, 0, 14, 72]
    requirements = [0, 0, 3, 0, 0, 6]
    mass = 135
    mines_per_year = 30
    mine_type = MineType.Speed
    technologies[TechnologyId.SpeedTrap30] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [32, 0, 14, 72]
    requirements = [0, 0, 5, 0, 0, 11]
    mass = 140
    mines_per_year = 50
    mine_type = MineType.Speed
    technologies[TechnologyId.SpeedTrap50] = MineLayer(
        requirements, cost, mass, mines_per_year, mine_type)

    cost = [1, 0, 1, 1]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 2
    basic_range = 0
    penetrating_range = 0
    technologies[TechnologyId.BatScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [3, 0, 2, 3]
    requirements = [0, 0, 0, 0, 1, 0]
    mass = 5
    basic_range = 50
    penetrating_range = 0
    technologies[TechnologyId.RhinoScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [2, 0, 2, 9]
    requirements = [0, 0, 0, 0, 4, 0]
    mass = 2
    basic_range = 100
    penetrating_range = 0
    technologies[TechnologyId.MoleScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [1, 1, 1, 5]
    requirements = [0, 0, 3, 0, 0, 6]
    mass = 2
    basic_range = 125
    penetrating_range = 0
    technologies[TechnologyId.DNAScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [3, 0, 3, 18]
    requirements = [0, 0, 0, 0, 5, 0]
    mass = 3
    basic_range = 150
    penetrating_range = 0
    technologies[TechnologyId.PossumScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [8, 10, 6, 35]
    requirements = [4, 0, 0, 0, 4, 4]
    mass = 15
    basic_range = 80
    penetrating_range = 0
    technologies[TechnologyId.PickPocketScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [4, 6, 4, 25]
    requirements = [3, 0, 0, 0, 6, 0]
    mass = 6
    basic_range = 160
    penetrating_range = 45
    technologies[TechnologyId.ChameleonScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    technologies[TechnologyId.ChameleonScanner].cloaking = 20

    cost = [2, 0, 8, 36]
    requirements = [3, 0, 0, 0, 7, 2]
    mass = 2
    basic_range = 185
    penetrating_range = 50
    technologies[TechnologyId.FerretScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [5, 5, 10, 40]
    requirements = [5, 0, 0, 0, 10, 4]
    mass = 4
    basic_range = 220
    penetrating_range = 100
    technologies[TechnologyId.DolphinScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [4, 0, 5, 24]
    requirements = [4, 0, 0, 0, 8, 0]
    mass = 4
    basic_range = 225
    penetrating_range = 0
    technologies[TechnologyId.GazelleScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [1, 1, 2, 20]
    requirements = [0, 0, 5, 0, 0, 10]
    mass = 2
    basic_range = 230
    penetrating_range = 0
    technologies[TechnologyId.RNAScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [3, 1, 13, 50]
    requirements = [5, 0, 0, 0, 11, 0]
    mass = 4
    basic_range = 275
    penetrating_range = 0
    technologies[TechnologyId.CheetahScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [8, 5, 14, 70]
    requirements = [6, 0, 0, 0, 16, 7]
    mass = 6
    basic_range = 300
    penetrating_range = 200
    technologies[TechnologyId.ElephantScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [3, 2, 21, 64]
    requirements = [6, 0, 0, 0, 14, 0]
    mass = 3
    basic_range = 335
    penetrating_range = 0
    technologies[TechnologyId.EagleEyeScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [10, 10, 10, 90]
    requirements = [10, 0, 0, 0, 15, 10]
    mass = 20
    basic_range = 220
    penetrating_range = 120
    technologies[TechnologyId.RobberBaronScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [3, 2, 30, 90]
    requirements = [7, 0, 0, 0, 24, 0]
    mass = 4
    basic_range = 500
    penetrating_range = 0
    technologies[TechnologyId.PeerlessScanner] = Scanner(
        requirements, cost, mass, basic_range, penetrating_range)

    cost = [12, 10, 10, 10]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 32
    technologies[TechnologyId.ColonizationModule] = Mechanical(
        requirements, cost, mass)

    cost = [20, 15, 15, 20]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 50
    technologies[TechnologyId.OrbitalConstructionModule] = Mechanical(
        requirements, cost, mass)

    cost = [5, 0, 2, 10]
    requirements = [0, 0, 0, 3, 0, 0]
    mass = 5
    technologies[TechnologyId.CargoPod] = Mechanical(
        requirements, cost, mass)

    technologies[TechnologyId.CargoPod].cargo = 50

    cost = [8, 0, 2, 15]
    requirements = [3, 0, 0, 9, 0, 0]
    mass = 7
    technologies[TechnologyId.SuperCargoPod] = Mechanical(
        requirements, cost, mass)

    technologies[TechnologyId.SuperCargoPod].cargo = 100

    cost = [5, 0, 0, 4]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 3
    technologies[TechnologyId.FuelTank] = Mechanical(
        requirements, cost, mass)

    technologies[TechnologyId.FuelTank].fuel = 250

    cost = [8, 0, 0, 8]
    requirements = [6, 0, 4, 14, 0, 0]
    mass = 8
    technologies[TechnologyId.SuperFuelTank] = Mechanical(
        requirements, cost, mass)

    technologies[TechnologyId.SuperFuelTank].fuel = 500

    cost = [5, 0, 5, 10]
    requirements = [2, 0, 3, 0, 0, 0]
    mass = 5
    technologies[TechnologyId.ManeuveringJet] = Mechanical(
        requirements, cost, mass)

    technologies[TechnologyId.ManeuveringJet].battle_speed_modifier = 0.25

    cost = [10, 0, 8, 20]
    requirements = [5, 0, 12, 0, 0, 0]
    mass = 5
    technologies[TechnologyId.Overthruster] = Mechanical(
        requirements, cost, mass)

    technologies[TechnologyId.Overthruster].battle_speed_modifier = 0.5

    cost = [0, 0, 10, 8]
    requirements = [6, 6, 0, 6, 6, 0]
    mass = 1
    technologies[TechnologyId.BeamDeflector] = Mechanical(
        requirements, cost, mass)

    technologies[TechnologyId.BeamDeflector].beam_reduction = 10

    cost = [2, 0, 2, 3]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 1
    technologies[TechnologyId.TransportCloaking] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.TransportCloaking].cloaking = 75

    cost = [2, 0, 2, 5]
    requirements = [2, 0, 0, 0, 5, 0]
    mass = 2
    technologies[TechnologyId.StealthCloak] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.StealthCloak].cloaking = 35

    cost = [8, 0, 8, 15]
    requirements = [4, 0, 0, 0, 10, 0]
    mass = 3
    technologies[TechnologyId.SuperStealthCloak] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.SuperStealthCloak].cloaking = 55

    cost = [10, 0, 10, 25]
    requirements = [10, 0, 0, 0, 12, 0]
    mass = 5
    technologies[TechnologyId.UltraStealthCloak] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.UltraStealthCloak].cloaking = 85

    cost = [0, 0, 13, 5]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 1
    technologies[TechnologyId.BattleComputer] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.BattleComputer].initiative = 1
    technologies[TechnologyId.BattleComputer].torpedo_accuracy = 20

    cost = [0, 0, 25, 14]
    requirements = [5, 0, 0, 0, 11, 0]
    mass = 1
    technologies[TechnologyId.BattleSuperComputer] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.BattleSuperComputer].initiative = 2
    technologies[TechnologyId.BattleSuperComputer].torpedo_accuracy = 30

    cost = [0, 0, 30, 15]
    requirements = [10, 0, 0, 0, 19, 0]
    mass = 1
    technologies[TechnologyId.BattleNexus] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.BattleNexus].initiative = 3
    technologies[TechnologyId.BattleNexus].torpedo_accuracy = 50

    cost = [0, 0, 2, 6]
    requirements = [2, 0, 0, 0, 6, 0]
    mass = 1
    technologies[TechnologyId.Jammer10] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.Jammer10].jamming = 10

    cost = [1, 0, 5, 20]
    requirements = [4, 0, 0, 0, 10, 0]
    mass = 1
    technologies[TechnologyId.Jammer20] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.Jammer20].jamming = 20

    cost = [1, 0, 6, 20]
    requirements = [8, 0, 0, 0, 16, 0]
    mass = 1
    technologies[TechnologyId.Jammer30] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.Jammer30].jamming = 30

    cost = [2, 0, 7, 20]
    requirements = [16, 0, 0, 0, 22, 0]
    mass = 1
    technologies[TechnologyId.Jammer50] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.Jammer50].jamming = 50

    cost = [0, 0, 8, 5]
    requirements = [7, 0, 0, 0, 4, 0]
    mass = 1
    technologies[TechnologyId.EnergyCapacitor] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.EnergyCapacitor].beam_damage = 10

    cost = [0, 0, 8, 5]
    requirements = [14, 0, 0, 0, 8, 0]
    mass = 1
    technologies[TechnologyId.FluxCapacitor] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.FluxCapacitor].beam_damage = 20

    cost = [5, 10, 0, 50]
    requirements = [14, 0, 0, 0, 8, 0]
    mass = 2
    technologies[TechnologyId.EnergyDampener] = Electrical(
        requirements, cost, mass)

    cost = [1, 5, 0, 70]
    requirements = [8, 0, 0, 0, 14, 0]
    mass = 1
    technologies[TechnologyId.TachyonDetector] = Electrical(
        requirements, cost, mass)

    cost = [8, 3, 3, 10]
    requirements = [0, 12, 0, 0, 0, 7]
    mass = 10
    technologies[TechnologyId.AntiMatterGenerator] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.AntiMatterGenerator].fuel = 200
    technologies[TechnologyId.AntiMatterGenerator].fuel_per_year = 50

    cost = [0, 0, 0, 70]
    requirements = [0, 0, 0, 0, 0, 0]
    technologies[TechnologyId.TotalTerraform3] = Terraforming(
        requirements, cost, 3, 3, 3)

    requirements = [0, 0, 0, 0, 0, 3]
    technologies[TechnologyId.TotalTerraform5] = Terraforming(
        requirements, cost, 5, 5, 5)

    requirements = [0, 0, 0, 0, 0, 6]
    technologies[TechnologyId.TotalTerraform7] = Terraforming(
        requirements, cost, 7, 7, 7)

    requirements = [0, 0, 0, 0, 0, 9]
    technologies[TechnologyId.TotalTerraform10] = Terraforming(
        requirements, cost, 10, 10, 10)

    requirements = [0, 0, 0, 0, 0, 13]
    technologies[TechnologyId.TotalTerraform15] = Terraforming(
        requirements, cost, 15, 15, 15)

    requirements = [0, 0, 0, 0, 0, 17]
    technologies[TechnologyId.TotalTerraform20] = Terraforming(
        requirements, cost, 20, 20, 20)

    requirements = [0, 0, 0, 0, 0, 22]
    technologies[TechnologyId.TotalTerraform25] = Terraforming(
        requirements, cost, 25, 25, 25)

    requirements = [0, 0, 0, 0, 0, 25]
    technologies[TechnologyId.TotalTerraform30] = Terraforming(
        requirements, cost, 30, 30, 30)

    cost = [0, 0, 0, 100]
    requirements = [0, 0, 1, 0, 0, 1]
    technologies[TechnologyId.GravityTerraform3] = Terraforming(
        requirements, cost, 3, 0, 0)

    requirements = [0, 0, 5, 0, 0, 2]
    technologies[TechnologyId.GravityTerraform7] = Terraforming(
        requirements, cost, 7, 0, 0)

    requirements = [0, 0, 10, 0, 0, 3]
    technologies[TechnologyId.GravityTerraform11] = Terraforming(
        requirements, cost, 11, 0, 0)

    requirements = [0, 0, 16, 0, 0, 4]
    technologies[TechnologyId.GravityTerraform15] = Terraforming(
        requirements, cost, 15, 0, 0)

    requirements = [1, 0, 0, 0, 0, 1]
    technologies[TechnologyId.TemperatureTerraform3] = Terraforming(
        requirements, cost, 0, 3, 0)

    requirements = [5, 0, 0, 0, 0, 2]
    technologies[TechnologyId.TemperatureTerraform7] = Terraforming(
        requirements, cost, 0, 7, 0)

    requirements = [10, 0, 0, 0, 0, 3]
    technologies[TechnologyId.TemperatureTerraform11] = Terraforming(
        requirements, cost, 0, 11, 0)

    requirements = [16, 0, 0, 0, 0, 4]
    technologies[TechnologyId.TemperatureTerraform15] = Terraforming(
        requirements, cost, 0, 15, 0)

    requirements = [0, 1, 0, 0, 0, 1]
    technologies[TechnologyId.RadiationTerraform3] = Terraforming(
        requirements, cost, 0, 0, 3)

    requirements = [0, 5, 0, 0, 0, 2]
    technologies[TechnologyId.RadiationTerraform7] = Terraforming(
        requirements, cost, 0, 0, 7)

    requirements = [0, 10, 0, 0, 0, 3]
    technologies[TechnologyId.RadiationTerraform11] = Terraforming(
        requirements, cost, 0, 0, 11)

    requirements = [0, 16, 0, 0, 0, 4]
    technologies[TechnologyId.RadiationTerraform15] = Terraforming(
        requirements, cost, 0, 0, 15)

    cost = [12, 0, 4, 44]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 80
    mining_value = 5
    technologies[TechnologyId.RoboMidgetMiner] = MiningRobot(
        requirements, cost, mass, mining_value)

    cost = [29, 0, 7, 96]
    requirements = [0, 0, 0, 2, 1, 0]
    mass = 240
    mining_value = 4
    technologies[TechnologyId.RoboMiniMiner] = MiningRobot(
        requirements, cost, mass, mining_value)

    cost = [30, 0, 7, 100]
    requirements = [0, 0, 0, 4, 2, 0]
    mass = 240
    mining_value = 12
    technologies[TechnologyId.RoboMiner] = MiningRobot(
        requirements, cost, mass, mining_value)

    cost = [30, 0, 7, 100]
    requirements = [0, 0, 0, 7, 4, 0]
    mass = 240
    mining_value = 18
    technologies[TechnologyId.RoboMaxiMiner] = MiningRobot(
        requirements, cost, mass, mining_value)

    cost = [30, 0, 7, 100]
    requirements = [0, 0, 0, 12, 6, 0]
    mass = 240
    mining_value = 27
    technologies[TechnologyId.RoboSuperMiner] = MiningRobot(
        requirements, cost, mass, mining_value)

    cost = [14, 0, 4, 50]
    requirements = [0, 0, 0, 15, 8, 0]
    mass = 80
    mining_value = 25
    technologies[TechnologyId.RoboUltraMiner] = MiningRobot(
        requirements, cost, mass, mining_value)

    cost = [25, 25, 25, 50]
    requirements = [0, 0, 0, 0, 0, 6]
    mass = 80
    technologies[TechnologyId.OrbitalAdjuster] = MiningRobot(
        requirements, cost, mass, mining_value)

    technologies[TechnologyId.OrbitalAdjuster].cloaking = 25

    #
    # Fuel cost tables and battle movement courtesy Posey's spreadsheet:
    #   http://wiki.starsautohost.org/files/posey.zip
    #

    cost = [1, 0, 1, 2]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 2
    fuel_table = [0, 0, 0, 0, 0, 0, 0, 140, 275, 480, 576]
    battle_speed = 6
    warp_10_travel = False
    technologies[TechnologyId.SettlersDelight] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [3, 0, 1, 3]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 4
    fuel_table = [0, 0, 25, 100, 100, 100, 180, 500, 800, 900, 1080]
    battle_speed = 5
    warp_10_travel = False
    technologies[TechnologyId.QuickJump5] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [8, 0, 0, 11]
    requirements = [0, 0, 2, 0, 0, 0]
    mass = 6
    fuel_table = [0, 0, 0, 0, 0, 35, 120, 175, 235, 360, 420]
    battle_speed = 6
    warp_10_travel = False
    technologies[TechnologyId.FuelMizer] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [5, 0, 1, 6]
    requirements = [0, 0, 3, 0, 0, 0]
    mass = 9
    fuel_table = [0, 0, 20, 60, 100, 100, 105, 450, 750, 900, 1080]
    battle_speed = 6
    warp_10_travel = False
    technologies[TechnologyId.LongHump6] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [11, 0, 3, 12]
    requirements = [0, 0, 5, 0, 0, 0]
    mass = 13
    fuel_table = [0, 0, 20, 60, 70, 100, 100, 110, 600, 750, 900]
    battle_speed = 7
    warp_10_travel = False
    technologies[TechnologyId.DaddyLongLegs7] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [16, 0, 3, 28]
    requirements = [0, 0, 7, 0, 0, 0]
    mass = 17
    fuel_table = [0, 0, 15, 50, 60, 70, 100, 100, 115, 700, 840]
    battle_speed = 8
    warp_10_travel = False
    technologies[TechnologyId.AlphaDrive8] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [20, 20, 9, 50]
    requirements = [0, 0, 9, 0, 0, 0]
    mass = 25
    fuel_table = [0, 0, 15, 35, 45, 55, 70, 80, 90, 100, 120]
    battle_speed = 9
    warp_10_travel = False
    technologies[TechnologyId.TransGalacticDrive] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [18, 25, 10, 60]
    requirements = [0, 0, 11, 0, 0, 0]
    mass = 25
    fuel_table = [0, 0, 10, 30, 40, 50, 60, 70, 80, 90, 100]
    battle_speed = 10
    warp_10_travel = True
    technologies[TechnologyId.Interspace10] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [3, 0, 3, 10]
    requirements = [0, 0, 23, 0, 0, 0]
    mass = 5
    fuel_table = [0, 0, 5, 15, 20, 25, 30, 35, 40, 45, 50]
    battle_speed = 10
    warp_10_travel = True
    technologies[TechnologyId.TransStar10] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [3, 2, 9, 8]
    requirements = [2, 0, 6, 0, 0, 0]
    mass = 10
    fuel_table = [0, 0, 0, 0, 0, 0, 0, 165, 375, 600, 720]
    battle_speed = 6
    warp_10_travel = False
    technologies[TechnologyId.RadiatingHydroRamScoop] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [4, 4, 7, 12]
    requirements = [2, 0, 8, 0, 0, 0]
    mass = 20
    fuel_table = [0, 0, 0, 0, 0, 0, 85, 105, 210, 380, 456]
    battle_speed = 7
    warp_10_travel = False
    technologies[TechnologyId.SubGalacticFuelScoop] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [5, 4, 12, 18]
    requirements = [3, 0, 9, 0, 0, 0]
    mass = 19
    fuel_table = [0, 0, 0, 0, 0, 0, 0, 88, 100, 145, 174]
    battle_speed = 8
    warp_10_travel = False
    technologies[TechnologyId.TransGalacticFuelScoop] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [6, 4, 16, 24]
    requirements = [4, 0, 12, 0, 0, 0]
    mass = 18
    fuel_table = [0, 0, 0, 0, 0, 0, 0, 0, 65, 90, 108]
    battle_speed = 9
    warp_10_travel = False
    technologies[TechnologyId.TransGalacticSuperScoop] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [5, 2, 13, 20]
    requirements = [4, 0, 16, 0, 0, 0]
    mass = 11
    fuel_table = [0, 0, 0, 0, 0, 0, 0, 0, 0, 70, 84]
    battle_speed = 10
    warp_10_travel = True
    technologies[TechnologyId.TransGalacticMizerScoop] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [4, 2, 9, 12]
    requirements = [5, 0, 20, 0, 0, 0]
    mass = 8
    fuel_table = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60]
    battle_speed = 10
    warp_10_travel = True
    technologies[TechnologyId.GalaxyScoop] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    cost = [12, 15, 11, 40]
    requirements = [7, 0, 13, 5, 9, 0]
    mass = 20
    fuel_table = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60]
    battle_speed = 10
    warp_10_travel = True
    technologies[TechnologyId.EnigmaPulsar] = Engine(
        requirements, cost, mass, fuel_table, battle_speed,
        warp_10_travel)

    technologies[TechnologyId.EnigmaPulsar].cloaking = 10
    technologies[TechnologyId.EnigmaPulsar].battle_speed_modifier = 0.25

    cost = [1, 20, 0, 5]
    requirements = [0, 2, 0, 0, 0, 0]
    mass = 40
    colonist_kill_percent = 0.6
    minimum_colonists_killed = 300
    buildings_destroyed = 2
    smart = False
    technologies[TechnologyId.LadyFingerBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 22, 0, 7]
    requirements = [0, 5, 0, 0, 0, 0]
    mass = 45
    colonist_kill_percent = 0.9
    minimum_colonists_killed = 300
    buildings_destroyed = 4
    smart = False
    technologies[TechnologyId.BlackCatBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 24, 0, 9]
    requirements = [0, 8, 0, 0, 0, 0]
    mass = 50
    colonist_kill_percent = 1.2
    minimum_colonists_killed = 300
    buildings_destroyed = 6
    smart = False
    technologies[TechnologyId.M70Bomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 25, 0, 12]
    requirements = [0, 11, 0, 0, 0, 0]
    mass = 55
    colonist_kill_percent = 1.7
    minimum_colonists_killed = 300
    buildings_destroyed = 7
    smart = False
    technologies[TechnologyId.M80Bomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 25, 0, 11]
    requirements = [0, 14, 0, 0, 0, 0]
    mass = 52
    colonist_kill_percent = 2.5
    minimum_colonists_killed = 300
    buildings_destroyed = 10
    smart = False
    technologies[TechnologyId.CherryBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 15, 15, 7]
    requirements = [0, 5, 0, 0, 8, 0]
    mass = 30
    colonist_kill_percent = 0.2
    minimum_colonists_killed = 0
    buildings_destroyed = 16
    smart = False
    technologies[TechnologyId.LBU17Bomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 24, 15, 10]
    requirements = [0, 10, 0, 0, 10, 0]
    mass = 35
    colonist_kill_percent = 0.3
    minimum_colonists_killed = 0
    buildings_destroyed = 28
    smart = False
    technologies[TechnologyId.LBU32Bomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 33, 12, 14]
    requirements = [0, 15, 0, 0, 12, 0]
    mass = 45
    colonist_kill_percent = 0.4
    minimum_colonists_killed = 0
    buildings_destroyed = 45
    smart = False
    technologies[TechnologyId.LBU74Bomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [15, 15, 10, 50]
    requirements = [0, 10, 0, 0, 0, 12]
    mass = 45
    colonist_kill_percent = 0
    minimum_colonists_killed = 0
    buildings_destroyed = 0
    smart = False
    technologies[TechnologyId.RetroBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 22, 0, 27]
    requirements = [0, 5, 0, 0, 0, 7]
    mass = 50
    colonist_kill_percent = 1.3
    minimum_colonists_killed = 0
    buildings_destroyed = 0
    smart = True
    technologies[TechnologyId.SmartBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 30, 0, 30]
    requirements = [0, 10, 0, 0, 0, 10]
    mass = 57
    colonist_kill_percent = 2.2
    minimum_colonists_killed = 0
    buildings_destroyed = 0
    smart = True
    technologies[TechnologyId.NeutronBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 36, 0, 25]
    requirements = [0, 15, 0, 0, 0, 12]
    mass = 64
    colonist_kill_percent = 3.5
    minimum_colonists_killed = 0
    buildings_destroyed = 0
    smart = True
    technologies[TechnologyId.EnrichedNeutronBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 33, 0, 32]
    requirements = [0, 22, 0, 0, 0, 15]
    mass = 55
    colonist_kill_percent = 5.0
    minimum_colonists_killed = 0
    buildings_destroyed = 0
    smart = True
    technologies[TechnologyId.PeerlessBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [1, 30, 0, 28]
    requirements = [0, 26, 0, 0, 0, 17]
    mass = 50
    colonist_kill_percent = 7.0
    minimum_colonists_killed = 0
    buildings_destroyed = 0
    smart = True
    technologies[TechnologyId.AnnihilatorBomb] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [0, 6, 0, 5]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 1
    power = 10
    range = 1
    initiative = 9
    technologies[TechnologyId.Laser] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 6, 0, 6]
    requirements = [0, 3, 0, 0, 0, 0]
    mass = 1
    power = 16
    range = 1
    initiative = 9
    technologies[TechnologyId.XrayLaser] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 16, 0, 10]
    requirements = [0, 5, 0, 0, 0, 0]
    mass = 3
    power = 13
    range = 2
    initiative = 12
    spread = True
    technologies[TechnologyId.MiniGun] = BeamWeapon(
        requirements, cost, mass, power, range, initiative, spread)

    cost = [0, 8, 0, 7]
    requirements = [0, 6, 0, 0, 0, 0]
    mass = 1
    power = 26
    range = 1
    initiative = 9
    technologies[TechnologyId.YakimoraLightPhaser] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 16, 0, 7]
    requirements = [0, 7, 0, 0, 0, 0]
    mass = 10
    power = 90
    range = 0
    initiative = 10
    technologies[TechnologyId.Blackjack] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 8, 0, 11]
    requirements = [0, 8, 0, 0, 0, 0]
    mass = 2
    power = 26
    range = 2
    initiative = 7
    technologies[TechnologyId.PhaserBazooka] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 0, 4, 12]
    requirements = [5, 9, 0, 0, 0, 0]
    mass = 1
    power = 82
    range = 3
    initiative = 14
    spread = False
    shields_only = True
    technologies[TechnologyId.PulsedSapper] = BeamWeapon(
        requirements, cost, mass, power, range, initiative, spread,
        shields_only)

    cost = [0, 14, 0, 18]
    requirements = [0, 10, 0, 0, 0, 0]
    mass = 2
    power = 26
    range = 3
    initiative = 5
    technologies[TechnologyId.ColloidalPhaser] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 20, 0, 13]
    requirements = [0, 11, 0, 0, 0, 0]
    mass = 3
    power = 31
    range = 2
    initiative = 12
    spread = True
    technologies[TechnologyId.GatlingGun] = BeamWeapon(
        requirements, cost, mass, power, range, initiative, spread)

    cost = [0, 10, 0, 9]
    requirements = [0, 12, 0, 0, 0, 0]
    mass = 1
    power = 66
    range = 1
    initiative = 9
    technologies[TechnologyId.MiniBlaster] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 22, 0, 9]
    requirements = [0, 13, 0, 0, 0, 0]
    mass = 10
    power = 231
    range = 0
    initiative = 10
    technologies[TechnologyId.Bludgeon] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 12, 0, 15]
    requirements = [0, 14, 0, 0, 0, 0]
    mass = 2
    power = 66
    range = 2
    initiative = 7
    technologies[TechnologyId.MarkIVBlaster] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 0, 6, 16]
    requirements = [8, 15, 0, 0, 0, 0]
    mass = 1
    power = 211
    range = 3
    initiative = 14
    spread = False
    shields_only = True
    technologies[TechnologyId.PhasedSapper] = BeamWeapon(
        requirements, cost, mass, power, range, initiative, spread,
        shields_only)

    cost = [0, 20, 0, 25]
    requirements = [8, 15, 0, 0, 0, 0]
    mass = 2
    power = 66
    range = 3
    initiative = 5
    technologies[TechnologyId.HeavyBlaster] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 28, 0, 17]
    requirements = [0, 17, 0, 0, 0, 0]
    mass = 3
    power = 80
    range = 2
    initiative = 13
    spread = True
    technologies[TechnologyId.GatlingNeutrinoCannon] = BeamWeapon(
        requirements, cost, mass, power, range, initiative, spread)

    cost = [0, 14, 0, 12]
    requirements = [0, 18, 0, 0, 0, 0]
    mass = 1
    power = 169
    range = 1
    initiative = 9
    technologies[TechnologyId.MyopicDisruptor] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 30, 0, 13]
    requirements = [0, 19, 0, 0, 0, 0]
    mass = 10
    power = 592
    range = 0
    initiative = 11
    technologies[TechnologyId.Blunderbuss] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 16, 0, 20]
    requirements = [0, 20, 0, 0, 0, 0]
    mass = 2
    power = 169
    range = 2
    initiative = 8
    technologies[TechnologyId.Disruptor] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 0, 8, 21]
    requirements = [11, 21, 0, 0, 0, 0]
    mass = 1
    power = 541
    range = 3
    initiative = 14
    spread = False
    shields_only = True
    technologies[TechnologyId.SyncroSapper] = BeamWeapon(
        requirements, cost, mass, power, range, initiative, spread,
        shields_only)

    cost = [0, 30, 0, 33]
    requirements = [0, 22, 0, 0, 0, 0]
    mass = 2
    power = 169
    range = 3
    initiative = 6
    technologies[TechnologyId.MegaDisruptor] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 36, 0, 23]
    requirements = [0, 23, 0, 0, 0, 0]
    mass = 3
    power = 204
    range = 2
    initiative = 13
    spread = True
    technologies[TechnologyId.BigMuthaCannon] = BeamWeapon(
        requirements, cost, mass, power, range, initiative, spread)

    cost = [0, 20, 0, 16]
    requirements = [0, 24, 0, 0, 0, 0]
    mass = 1
    power = 433
    range = 1
    initiative = 9
    technologies[TechnologyId.StreamingPulverizer] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [0, 22, 0, 27]
    requirements = [0, 26, 0, 0, 0, 0]
    mass = 2
    power = 433
    range = 2
    initiative = 8
    technologies[TechnologyId.AntiMatterPulverizer] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    cost = [50, 20, 20, 200]
    requirements = [0, 0, 5, 5, 0, 0]
    safe_mass = 100
    safe_range = 250
    technologies[TechnologyId.Stargate100_250] = Stargate(
        requirements, cost, safe_mass, safe_range)

    cost = [50, 20, 20, 250]
    requirements = [0, 0, 6, 10, 0, 0]
    safe_mass = float("inf")
    safe_range = 300
    technologies[TechnologyId.StargateAny_300] = Stargate(
        requirements, cost, safe_mass, safe_range)

    cost = [50, 20, 20, 500]
    requirements = [0, 0, 11, 7, 0, 0]
    safe_mass = 150
    safe_range = 600
    technologies[TechnologyId.Stargate150_600] = Stargate(
        requirements, cost, safe_mass, safe_range)

    cost = [50, 20, 20, 600]
    requirements = [0, 0, 9, 13, 0, 0]
    safe_mass = 300
    safe_range = 500
    technologies[TechnologyId.Stargate300_500] = Stargate(
        requirements, cost, safe_mass, safe_range)

    cost = [50, 20, 20, 700]
    requirements = [0, 0, 16, 12, 0, 0]
    safe_mass = 100
    safe_range = float("inf")
    technologies[TechnologyId.Stargate100_Any] = Stargate(
        requirements, cost, safe_mass, safe_range)

    cost = [50, 20, 20, 700]
    requirements = [0, 0, 12, 18, 0, 0]
    safe_mass = float("inf")
    safe_range = 800
    technologies[TechnologyId.StargateAny_800] = Stargate(
        requirements, cost, safe_mass, safe_range)

    cost = [50, 20, 20, 800]
    requirements = [0, 0, 19, 24, 0, 0]
    safe_mass = float("inf")
    safe_range = float("inf")
    technologies[TechnologyId.StargateAny_Any] = Stargate(
        requirements, cost, safe_mass, safe_range)

    cost = [24, 20, 20, 70]
    requirements = [4, 0, 0, 0, 0, 0]
    warp = 5
    technologies[TechnologyId.MassDriver5] = MassDriver(
        requirements, cost, warp)

    cost = [24, 20, 20, 144]
    requirements = [7, 0, 0, 0, 0, 0]
    warp = 6
    technologies[TechnologyId.MassDriver6] = MassDriver(
        requirements, cost, warp)

    cost = [100, 100, 100, 512]
    requirements = [9, 0, 0, 0, 0, 0]
    warp = 7
    technologies[TechnologyId.MassDriver7] = MassDriver(
        requirements, cost, warp)

    cost = [24, 20, 20, 256]
    requirements = [11, 0, 0, 0, 0, 0]
    warp = 8
    technologies[TechnologyId.SuperDriver8] = MassDriver(
        requirements, cost, warp)

    cost = [24, 20, 20, 324]
    requirements = [13, 0, 0, 0, 0, 0]
    warp = 9
    technologies[TechnologyId.SuperDriver9] = MassDriver(
        requirements, cost, warp)

    cost = [100, 100, 100, 968]
    requirements = [15, 0, 0, 0, 0, 0]
    warp = 10
    technologies[TechnologyId.UltraDriver10] = MassDriver(
        requirements, cost, warp)

    cost = [24, 20, 20, 484]
    requirements = [17, 0, 0, 0, 0, 0]
    warp = 11
    technologies[TechnologyId.UltraDriver11] = MassDriver(
        requirements, cost, warp)

    cost = [24, 20, 20, 576]
    requirements = [20, 0, 0, 0, 0, 0]
    warp = 12
    technologies[TechnologyId.UltraDriver12] = MassDriver(
        requirements, cost, warp)

    cost = [24, 20, 20, 676]
    requirements = [24, 0, 0, 0, 0, 0]
    warp = 13
    technologies[TechnologyId.UltraDriver13] = MassDriver(
        requirements, cost, warp)

    cost = [12, 0, 17, 40]
    requirements = [0, 0, 0, 0, 0, 0]
    armor = 100
    initiative = 10
    dock_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Weapons, 12)
    tech_slots[1] = (TechnologySlotType.Weapons, 12)
    tech_slots[2] = (TechnologySlotType.Protection, 12)
    tech_slots[3] = (TechnologySlotType.Protection, 12)
    tech_slots[4] = (TechnologySlotType.OrbitalElect, 1)
    technologies[TechnologyId.OrbitalFort] = StarbaseHull(
        requirements, cost, tech_slots, armor, initiative, dock_capacity)

    cost = [20, 5, 25, 100]
    requirements = [0, 0, 0, 4, 0, 0]
    armor = 250
    initiative = 12
    dock_capacity = 200
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Weapons, 16)
    tech_slots[1] = (TechnologySlotType.Weapons, 16)
    tech_slots[2] = (TechnologySlotType.Weapons, 16)
    tech_slots[3] = (TechnologySlotType.Electrical, 2)
    tech_slots[4] = (TechnologySlotType.Electrical, 2)
    tech_slots[5] = (TechnologySlotType.Shields, 24)
    tech_slots[6] = (TechnologySlotType.Protection, 24)
    tech_slots[7] = (TechnologySlotType.OrbitalElect, 1)
    technologies[TechnologyId.SpaceDock] = StarbaseHull(
        requirements, cost, tech_slots, armor, initiative, dock_capacity)

    cost = [120, 80, 250, 600]
    requirements = [0, 0, 0, 0, 0, 0]
    armor = 500
    initiative = 14
    dock_capacity = float("inf")
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Weapons, 16)
    tech_slots[1] = (TechnologySlotType.Weapons, 16)
    tech_slots[2] = (TechnologySlotType.Weapons, 16)
    tech_slots[3] = (TechnologySlotType.Weapons, 16)
    tech_slots[4] = (TechnologySlotType.Shields, 16)
    tech_slots[5] = (TechnologySlotType.Shields, 16)
    tech_slots[6] = (TechnologySlotType.Protection, 16)
    tech_slots[7] = (TechnologySlotType.Protection, 16)
    tech_slots[8] = (TechnologySlotType.Electrical, 3)
    tech_slots[9] = (TechnologySlotType.Electrical, 3)
    tech_slots[10] = (TechnologySlotType.OrbitalElect, 1)
    tech_slots[11] = (TechnologySlotType.OrbitalElect, 1)
    technologies[TechnologyId.SpaceStation] = StarbaseHull(
        requirements, cost, tech_slots, armor, initiative, dock_capacity)

    cost = [120, 80, 300, 600]
    requirements = [0, 0, 0, 12, 0, 0]
    armor = 1000
    initiative = 16
    dock_capacity = float("inf")
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Weapons, 16)
    tech_slots[1] = (TechnologySlotType.Weapons, 16)
    tech_slots[2] = (TechnologySlotType.Weapons, 16)
    tech_slots[3] = (TechnologySlotType.Weapons, 16)
    tech_slots[4] = (TechnologySlotType.Weapons, 16)
    tech_slots[5] = (TechnologySlotType.Weapons, 16)
    tech_slots[6] = (TechnologySlotType.Electrical, 3)
    tech_slots[7] = (TechnologySlotType.Electrical, 3)
    tech_slots[8] = (TechnologySlotType.Electrical, 3)
    tech_slots[9] = (TechnologySlotType.Electrical, 3)
    tech_slots[10] = (TechnologySlotType.Shields, 20)
    tech_slots[11] = (TechnologySlotType.Shields, 20)
    tech_slots[12] = (TechnologySlotType.Protection, 20)
    tech_slots[13] = (TechnologySlotType.Protection, 20)
    tech_slots[14] = (TechnologySlotType.OrbitalElect, 1)
    tech_slots[15] = (TechnologySlotType.OrbitalElect, 1)
    technologies[TechnologyId.UltraStation] = StarbaseHull(
        requirements, cost, tech_slots, armor, initiative, dock_capacity)

    cost = [120, 80, 350, 750]
    requirements = [0, 0, 0, 17, 0, 0]
    armor = 1500
    initiative = 18
    dock_capacity = float("inf")
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Weapons, 32)
    tech_slots[1] = (TechnologySlotType.Weapons, 32)
    tech_slots[2] = (TechnologySlotType.Weapons, 32)
    tech_slots[3] = (TechnologySlotType.Weapons, 32)
    tech_slots[4] = (TechnologySlotType.Electrical, 4)
    tech_slots[5] = (TechnologySlotType.Electrical, 4)
    tech_slots[6] = (TechnologySlotType.Electrical, 4)
    tech_slots[7] = (TechnologySlotType.Electrical, 4)
    tech_slots[8] = (TechnologySlotType.Electrical, 4)
    tech_slots[9] = (TechnologySlotType.Electrical, 4)
    tech_slots[10] = (TechnologySlotType.Shields, 30)
    tech_slots[11] = (TechnologySlotType.Shields, 30)
    tech_slots[12] = (TechnologySlotType.Protection, 20)
    tech_slots[13] = (TechnologySlotType.Protection, 20)
    tech_slots[14] = (TechnologySlotType.OrbitalElect, 1)
    tech_slots[15] = (TechnologySlotType.OrbitalElect, 1)
    technologies[TechnologyId.DeathStar] = StarbaseHull(
        requirements, cost, tech_slots, armor, initiative, dock_capacity)

    cost = [12, 0, 17, 20]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 25
    armor = 25
    initiative = 0
    fuel_capacity = 130
    cargo_capacity = 70
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Protection, 1)
    tech_slots[2] = (TechnologySlotType.ScannerElectMech, 1)
    technologies[TechnologyId.SmallFreighter] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [20, 0, 19, 40]
    requirements = [0, 0, 0, 3, 0, 0]
    mass = 60
    armor = 50
    initiative = 0
    fuel_capacity = 450
    cargo_capacity = 210
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Protection, 1)
    tech_slots[2] = (TechnologySlotType.ScannerElectMech, 1)
    technologies[TechnologyId.MediumFreighter] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [35, 0, 21, 100]
    requirements = [0, 0, 0, 8, 0, 0]
    mass = 125
    armor = 150
    initiative = 0
    fuel_capacity = 2600
    cargo_capacity = 1200
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.Protection, 2)
    tech_slots[2] = (TechnologySlotType.ScannerElectMech, 2)
    technologies[TechnologyId.LargeFreighter] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [45, 0, 21, 125]
    requirements = [0, 0, 0, 13, 0, 0]
    mass = 175
    armor = 400
    initiative = 0
    fuel_capacity = 8000
    cargo_capacity = 3000
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 3)
    tech_slots[1] = (TechnologySlotType.Protection, 5)
    tech_slots[2] = (TechnologySlotType.ScannerElectMech, 3)
    tech_slots[3] = (TechnologySlotType.Electrical, 2)
    technologies[TechnologyId.SuperFreighter] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [4, 2, 4, 10]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 8
    armor = 20
    initiative = 1
    fuel_capacity = 50
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.GeneralPurpose, 1)
    tech_slots[2] = (TechnologySlotType.Scanners, 1)
    technologies[TechnologyId.Scout] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [4, 2, 4, 12]
    requirements = [0, 0, 0, 6, 0, 0]
    mass = 8
    armor = 45
    initiative = 4
    fuel_capacity = 125
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Protection, 2)
    tech_slots[2] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[3] = (TechnologySlotType.Scanners, 2)
    technologies[TechnologyId.Frigate] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [15, 3, 5, 35]
    requirements = [0, 0, 0, 3, 0, 0]
    mass = 30
    armor = 200
    initiative = 3
    fuel_capacity = 280
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Weapons, 1)
    tech_slots[2] = (TechnologySlotType.Weapons, 1)
    tech_slots[3] = (TechnologySlotType.Armor, 2)
    tech_slots[4] = (TechnologySlotType.GeneralPurpose, 1)
    tech_slots[5] = (TechnologySlotType.Electrical, 1)
    tech_slots[6] = (TechnologySlotType.Mechanical, 1)
    technologies[TechnologyId.Destroyer] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [40, 5, 8, 85]
    requirements = [0, 0, 0, 9, 0, 0]
    mass = 90
    armor = 700
    initiative = 5
    fuel_capacity = 600
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.Weapons, 2)
    tech_slots[2] = (TechnologySlotType.Weapons, 2)
    tech_slots[3] = (TechnologySlotType.Protection, 2)
    tech_slots[4] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[5] = (TechnologySlotType.ShieldElectMech, 1)
    tech_slots[6] = (TechnologySlotType.ShieldElectMech, 1)
    technologies[TechnologyId.Cruiser] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [55, 8, 12, 120]
    requirements = [0, 0, 0, 10, 0, 0]
    mass = 120
    armor = 1000
    initiative = 5
    fuel_capacity = 1400
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.Weapons, 3)
    tech_slots[2] = (TechnologySlotType.Weapons, 3)
    tech_slots[3] = (TechnologySlotType.Protection, 4)
    tech_slots[4] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[5] = (TechnologySlotType.ShieldElectMech, 2)
    tech_slots[6] = (TechnologySlotType.ShieldElectMech, 2)
    technologies[TechnologyId.BattleCruiser] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [120, 25, 20, 225]
    requirements = [0, 0, 0, 13, 0, 0]
    mass = 222
    armor = 2000
    initiative = 10
    fuel_capacity = 2800
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 4)
    tech_slots[1] = (TechnologySlotType.Weapons, 2)
    tech_slots[2] = (TechnologySlotType.Weapons, 2)
    tech_slots[3] = (TechnologySlotType.Weapons, 6)
    tech_slots[4] = (TechnologySlotType.Weapons, 6)
    tech_slots[5] = (TechnologySlotType.Weapons, 4)
    tech_slots[6] = (TechnologySlotType.Armor, 6)
    tech_slots[7] = (TechnologySlotType.Electrical, 3)
    tech_slots[8] = (TechnologySlotType.Electrical, 3)
    tech_slots[9] = (TechnologySlotType.Shields, 8)
    tech_slots[10] = (TechnologySlotType.ScannerElectMech, 1)
    technologies[TechnologyId.Battleship] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [140, 30, 25, 275]
    requirements = [0, 0, 0, 16, 0, 0]
    mass = 250
    armor = 4500
    initiative = 10
    fuel_capacity = 4500
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 5)
    tech_slots[1] = (TechnologySlotType.Weapons, 6)
    tech_slots[2] = (TechnologySlotType.Weapons, 6)
    tech_slots[3] = (TechnologySlotType.Weapons, 8)
    tech_slots[4] = (TechnologySlotType.Weapons, 8)
    tech_slots[6] = (TechnologySlotType.Armor, 8)
    tech_slots[7] = (TechnologySlotType.Electrical, 4)
    tech_slots[8] = (TechnologySlotType.Electrical, 4)
    tech_slots[9] = (TechnologySlotType.Protection, 4)
    tech_slots[10] = (TechnologySlotType.Protection, 4)
    tech_slots[11] = (TechnologySlotType.GeneralPurpose, 1)
    tech_slots[12] = (TechnologySlotType.WeaponShield, 5)
    tech_slots[13] = (TechnologySlotType.WeaponShield, 5)
    technologies[TechnologyId.Dreadnought] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [50, 3, 2, 50]
    requirements = [0, 0, 0, 4, 0, 0]
    mass = 65
    armor = 150
    initiative = 3
    fuel_capacity = 650
    cargo_capacity = 250
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Protection, 2)
    tech_slots[2] = (TechnologySlotType.GeneralPurpose, 1)
    tech_slots[3] = (TechnologySlotType.GeneralPurpose, 1)
    tech_slots[4] = (TechnologySlotType.ScannerElectMech, 1)
    technologies[TechnologyId.Privateer] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [80, 5, 5, 60]
    requirements = [0, 0, 0, 8, 0, 0]
    mass = 75
    armor = 450
    initiative = 4
    fuel_capacity = 2250
    cargo_capacity = 500
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.Electrical, 1)
    tech_slots[2] = (TechnologySlotType.Electrical, 1)
    tech_slots[3] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[4] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[5] = (TechnologySlotType.Protection, 3)
    tech_slots[6] = (TechnologySlotType.MineElectMech, 2)
    tech_slots[7] = (TechnologySlotType.MineElectMech, 2)
    tech_slots[8] = (TechnologySlotType.Scanners, 1)
    technologies[TechnologyId.Rogue] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [70, 5, 5, 105]
    requirements = [0, 0, 0, 11, 0, 0]
    mass = 125
    armor = 900
    initiative = 4
    fuel_capacity = 2500
    cargo_capacity = 1000
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 4)
    tech_slots[1] = (TechnologySlotType.Protection, 2)
    tech_slots[2] = (TechnologySlotType.Protection, 2)
    tech_slots[3] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[4] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[5] = (TechnologySlotType.Electrical, 1)
    tech_slots[6] = (TechnologySlotType.MineElectMech, 2)
    tech_slots[7] = (TechnologySlotType.ElectMech, 2)
    tech_slots[8] = (TechnologySlotType.Scanners, 2)
    technologies[TechnologyId.Galleon] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [2, 0, 2, 3]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 8
    armor = 10
    initiative = 0
    fuel_capacity = 150
    cargo_capacity = 10
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Mechanical, 1)
    technologies[TechnologyId.MiniColonyShip] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [10, 0, 15, 20]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 20
    armor = 20
    initiative = 0
    fuel_capacity = 200
    cargo_capacity = 25
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Mechanical, 1)
    technologies[TechnologyId.ColonyShip] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [20, 5, 10, 35]
    requirements = [0, 0, 0, 1, 0, 0]
    mass = 28
    armor = 50
    initiative = 0
    fuel_capacity = 120
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Bombs, 2)
    technologies[TechnologyId.MiniBomber] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [55, 10, 10, 150]
    requirements = [0, 0, 0, 6, 0, 0]
    mass = 69
    armor = 175
    initiative = 0
    fuel_capacity = 400
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.Bombs, 4)
    tech_slots[2] = (TechnologySlotType.Bombs, 4)
    tech_slots[3] = (TechnologySlotType.ScannerElectMech, 1)
    technologies[TechnologyId.B17Bomber] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [55, 10, 15, 175]
    requirements = [0, 0, 0, 8, 0, 0]
    mass = 70
    armor = 225
    initiative = 0
    fuel_capacity = 750
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.Bombs, 4)
    tech_slots[2] = (TechnologySlotType.Bombs, 4)
    tech_slots[3] = (TechnologySlotType.ScannerElectMech, 1)
    tech_slots[4] = (TechnologySlotType.Electrical, 3)
    technologies[TechnologyId.StealthBomber] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [90, 15, 10, 280]
    requirements = [0, 0, 0, 15, 0, 0]
    mass = 110
    armor = 450
    initiative = 0
    fuel_capacity = 750
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 3)
    tech_slots[1] = (TechnologySlotType.Bombs, 4)
    tech_slots[2] = (TechnologySlotType.Bombs, 4)
    tech_slots[3] = (TechnologySlotType.Bombs, 4)
    tech_slots[4] = (TechnologySlotType.Bombs, 4)
    tech_slots[5] = (TechnologySlotType.Shields, 2)
    tech_slots[6] = (TechnologySlotType.ScannerElectMech, 2)
    technologies[TechnologyId.B52Bomber] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [10, 0, 3, 20]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 10
    armor = 100
    initiative = 0
    fuel_capacity = 210
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.MiningRobots, 2)
    technologies[TechnologyId.MidgetMiner] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [25, 0, 6, 50]
    requirements = [0, 0, 0, 2, 0, 0]
    mass = 80
    armor = 130
    initiative = 0
    fuel_capacity = 210
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.MiningRobots, 1)
    tech_slots[2] = (TechnologySlotType.MiningRobots, 1)
    tech_slots[3] = (TechnologySlotType.ScannerElectMech, 1)
    technologies[TechnologyId.MiniMiner] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [32, 0, 6, 110]
    requirements = [0, 0, 0, 6, 0, 0]
    mass = 110
    armor = 475
    initiative = 0
    fuel_capacity = 500
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.MiningRobots, 2)
    tech_slots[2] = (TechnologySlotType.MiningRobots, 2)
    tech_slots[3] = (TechnologySlotType.MiningRobots, 1)
    tech_slots[4] = (TechnologySlotType.MiningRobots, 1)
    tech_slots[5] = (TechnologySlotType.ArmorScannerElectMech, 2)
    technologies[TechnologyId.Miner] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [32, 0, 6, 140]
    requirements = [0, 0, 0, 11, 0, 0]
    mass = 110
    armor = 1400
    initiative = 0
    fuel_capacity = 850
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.MiningRobots, 4)
    tech_slots[2] = (TechnologySlotType.MiningRobots, 4)
    tech_slots[3] = (TechnologySlotType.MiningRobots, 1)
    tech_slots[4] = (TechnologySlotType.MiningRobots, 1)
    tech_slots[5] = (TechnologySlotType.ArmorScannerElectMech, 2)
    technologies[TechnologyId.MaxiMiner] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)


    cost = [30, 0, 6, 130]
    requirements = [0, 0, 0, 14, 0, 0]
    mass = 100
    armor = 1500
    initiative = 0
    fuel_capacity = 1300
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.MiningRobots, 4)
    tech_slots[2] = (TechnologySlotType.MiningRobots, 4)
    tech_slots[3] = (TechnologySlotType.MiningRobots, 2)
    tech_slots[4] = (TechnologySlotType.MiningRobots, 2)
    tech_slots[5] = (TechnologySlotType.ArmorScannerElectMech, 3)
    technologies[TechnologyId.UltraMiner] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [10, 0, 5, 50]
    requirements = [0, 0, 0, 4, 0, 0]
    mass = 12
    armor = 5
    initiative = 0
    fuel_capacity = 750
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.Shields, 1)
    technologies[TechnologyId.FuelTransport] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    technologies[TechnologyId.FuelTransport].fuel_regen = 200
    technologies[TechnologyId.FuelTransport].percent_regen_bonus = 5

    cost = [20, 0, 8, 70]
    requirements = [0, 0, 0, 7, 0, 0]
    mass = 111
    armor = 12
    initiative = 0
    fuel_capacity = 2250
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.Shields, 2)
    tech_slots[2] = (TechnologySlotType.Scanners, 1)
    technologies[TechnologyId.SuperFuelTransport] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    technologies[TechnologyId.FuelTransport].fuel_regen = 200
    technologies[TechnologyId.FuelTransport].percent_regen_bonus = 10

    cost = [8, 2, 5, 20]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 10
    armor = 60
    initiative = 0
    fuel_capacity = 400
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 1)
    tech_slots[1] = (TechnologySlotType.MineLayers, 2)
    tech_slots[2] = (TechnologySlotType.MineLayers, 2)
    tech_slots[3] = (TechnologySlotType.ScannerElectMech, 1)
    technologies[TechnologyId.MiniMineLayer] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [20, 3, 9, 30]
    requirements = [0, 0, 0, 15, 0, 0]
    mass = 30
    armor = 1200
    initiative = 0
    fuel_capacity = 2200
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 3)
    tech_slots[1] = (TechnologySlotType.MineLayers, 8)
    tech_slots[2] = (TechnologySlotType.MineLayers, 8)
    tech_slots[3] = (TechnologySlotType.ScannerElectMech, 3)
    tech_slots[4] = (TechnologySlotType.Protection, 3)
    tech_slots[5] = (TechnologySlotType.MineElectMech, 3)
    technologies[TechnologyId.SuperMineLayer] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [75, 12, 12, 150]
    requirements = [0, 0, 0, 26, 0, 0]
    mass = 100
    armor = 5000
    initiative = 2
    fuel_capacity = 5000
    cargo_capacity = 0
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 3)
    tech_slots[1] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[2] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[3] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[4] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[5] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[6] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[7] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[8] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[9] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[10] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[11] = (TechnologySlotType.GeneralPurpose, 3)
    tech_slots[12] = (TechnologySlotType.GeneralPurpose, 3)
    technologies[TechnologyId.Nubian] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [50, 12, 12, 120]
    requirements = [0, 0, 0, 8, 0, 0]
    mass = 85
    armor = 500
    initiative = 2
    fuel_capacity = 700
    cargo_capacity = 300
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 3)
    tech_slots[1] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[2] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[3] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[4] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[5] = (TechnologySlotType.GeneralPurpose, 8)
    tech_slots[6] = (TechnologySlotType.GeneralPurpose, 1)
    technologies[TechnologyId.MetaMorph] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    cost = [9, 3, 3, 5]
    requirements = [0, 0, 0, 0, 0, 0]
    mass = 25
    power = 5
    range = 4
    initiative = 0
    accuracy = 35
    technologies[TechnologyId.AlphaTorpedo] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [18, 6, 4, 6]
    requirements = [0, 5, 1, 0, 0, 0]
    mass = 25
    power = 12
    range = 4
    initiative = 1
    accuracy = 45
    technologies[TechnologyId.BetaTorpedo] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [22, 8, 5, 8]
    requirements = [0, 10, 2, 0, 0, 0]
    mass = 25
    power = 26
    range = 4
    initiative = 1
    accuracy = 60
    technologies[TechnologyId.DeltaTorpedo] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [30, 10, 6, 10]
    requirements = [0, 14, 3, 0, 0, 0]
    mass = 25
    power = 48
    range = 5
    initiative = 2
    accuracy = 65
    technologies[TechnologyId.EpsilonTorpedo] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [34, 12, 8, 12]
    requirements = [0, 18, 4, 0, 0, 0]
    mass = 25
    power = 90
    range = 5
    initiative = 2
    accuracy = 75
    technologies[TechnologyId.RhoTorpedo] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [40, 14, 9, 15]
    requirements = [0, 22, 5, 0, 0, 0]
    mass = 25
    power = 169
    range = 5
    initiative = 3
    accuracy = 75
    technologies[TechnologyId.UpsilonTorpedo] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [52, 18, 12, 18]
    requirements = [0, 26, 6, 0, 0, 0]
    mass = 25
    power = 316
    range = 5
    initiative = 4
    accuracy = 80
    technologies[TechnologyId.OmegaTorpedo] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [37, 13, 9, 13]
    requirements = [0, 12, 6, 0, 0, 0]
    mass = 35
    power = 85
    range = 5
    initiative = 0
    accuracy = 20
    technologies[TechnologyId.JihadMissile] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [48, 16, 11, 16]
    requirements = [0, 16, 8, 0, 0, 0]
    mass = 35
    power = 150
    range = 5
    initiative = 1
    accuracy = 20
    technologies[TechnologyId.JuggernautMissile] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [60, 20, 13, 20]
    requirements = [0, 20, 10, 0, 0, 0]
    mass = 35
    power = 280
    range = 6
    initiative = 2
    accuracy = 25
    technologies[TechnologyId.DoomsdayMissile] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [67, 23, 16, 24]
    requirements = [0, 24, 10, 0, 0, 0]
    mass = 35
    power = 525
    range = 6
    initiative = 3
    accuracy = 30
    technologies[TechnologyId.ArmageddonMissile] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    #
    # MT part values courtesy of:
    #   http://wiki.starsautohost.org/wiki/Mystery_Trader
    #

    cost = [1, 2, 0, 2]
    requirements = [0, 12, 0, 0, 12, 12]
    mass = 5
    colonist_kill_percent = 3.0
    minimum_colonists_killed = 300
    buildings_destroyed = 2
    smart = False
    technologies[TechnologyId.Hushaboom] = Bomb(
        requirements, cost, mass, colonist_kill_percent,
        minimum_colonists_killed, buildings_destroyed, smart)

    cost = [14, 5, 5, 52]
    requirements = [14, 0, 0, 14, 14, 6]
    mass = 20
    armor = 400
    technologies[TechnologyId.MegaPolyShell] = Armor(
        requirements, cost, mass, armor)

    technologies[TechnologyId.MegaPolyShell].cloaking = 20
    technologies[TechnologyId.MegaPolyShell].jamming = 20
    technologies[TechnologyId.MegaPolyShell].shield_value = 100
    technologies[TechnologyId.MegaPolyShell].basic_range = 80
    technologies[TechnologyId.MegaPolyShell].penetrating_range = 40

    cost = [6, 1, 4, 12]
    requirements = [12, 0, 9, 0, 9, 0]
    mass = 10
    shields = 125
    technologies[TechnologyId.LangstonShell] = Shield(
        requirements, cost, mass, shields)

    technologies[TechnologyId.LangstonShell].cloaking = 10
    technologies[TechnologyId.LangstonShell].armor_value = 65
    technologies[TechnologyId.LangstonShell].jamming = 5
    technologies[TechnologyId.LangstonShell].basic_range = 50
    technologies[TechnologyId.LangstonShell].penetrating_range = 25

    cost = [4, 0, 4, 13]
    requirements = [11, 0, 11, 0, 11, 0]
    mass = 2
    technologies[TechnologyId.MultiFunctionPod] = Electrical(
        requirements, cost, mass)

    technologies[TechnologyId.MultiFunctionPod].cloaking = 30
    technologies[TechnologyId.MultiFunctionPod].jamming = 10
    technologies[TechnologyId.MultiFunctionPod].battle_speed_modifier = 0.25

    cost = [3, 8, 1, 50]
    requirements = [0, 11, 12, 0, 0, 21]
    mass = 8
    power = 60
    range = 6
    initiative = 0
    accuracy = 85
    technologies[TechnologyId.AntiMatterTorpedo] = Torpedo(
        requirements, cost, mass, power, range, initiative, accuracy)

    cost = [0, 0, 38, 30]
    requirements = [16, 0, 20, 20, 16, 0]
    mass = 10
    technologies[TechnologyId.JumpGate] = Mechanical(
        requirements, cost, mass)

    cost = [0, 0, 0, 5000]
    requirements = [20, 10, 10, 20, 10, 20]
    technologies[TechnologyId.GenesisDevice] = Technology(
        requirements, cost)

    cost = [0, 6, 0, 5]
    requirements = [21, 21, 0, 0, 16, 12]
    mass = 8
    power = 140
    range = 3
    initiative = 6
    technologies[TechnologyId.MultiContainedMunition] = BeamWeapon(
        requirements, cost, mass, power, range, initiative)

    technologies[TechnologyId.MultiContainedMunition].cloaking = 10
    technologies[TechnologyId.MultiContainedMunition].torpedo_accuracy = 10
    technologies[TechnologyId.MultiContainedMunition].basic_range = 150
    technologies[TechnologyId.MultiContainedMunition].penetrating_range = 75
    technologies[TechnologyId.MultiContainedMunition].mines_per_year = 40
    technologies[TechnologyId.MultiContainedMunition].colonist_kill_percent = 2
    technologies[TechnologyId.MultiContainedMunition].minimum_colonists_killed = 300
    technologies[TechnologyId.MultiContainedMunition].smart = False
    technologies[TechnologyId.MultiContainedMunition].buildings_destroyed = 5

    cost = [4, 0, 1, 10]
    requirements = [5, 0, 0, 10, 5, 5]
    mass = 20
    mining_value = 10
    technologies[TechnologyId.AlienMiner] = MiningRobot(
        requirements, cost, mass, mining_value)

    technologies[TechnologyId.AlienMiner].cloaking = 30
    technologies[TechnologyId.AlienMiner].jamming = 30
    technologies[TechnologyId.AlienMiner].battle_speed_modifier = 1 / 8.0

    cost = [12, 0, 3, 25]
    requirements = [5, 0, 0, 11, 5, 0]
    mass = 9
    technologies[TechnologyId.MultiCargoPod] = Mechanical(
        requirements, cost, mass)

    technologies[TechnologyId.MultiCargoPod].cargo = 250
    technologies[TechnologyId.MultiCargoPod].cloaking = 10
    technologies[TechnologyId.MultiCargoPod].armor_value = 50

    cost = [30, 8, 8, 100]
    requirements = [0, 0, 0, 8, 0, 0]
    mass = 70
    armor = 25
    initiative = 2
    fuel_capacity = 400
    cargo_capacity = 150
    tech_slots = {}
    tech_slots[0] = (TechnologySlotType.Engines, 2)
    tech_slots[1] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[2] = (TechnologySlotType.GeneralPurpose, 2)
    tech_slots[3] = (TechnologySlotType.GeneralPurpose, 1)
    tech_slots[4] = (TechnologySlotType.GeneralPurpose, 1)
    tech_slots[5] = (TechnologySlotType.GeneralPurpose, 1)
    tech_slots[6] = (TechnologySlotType.GeneralPurpose, 3)
    technologies[TechnologyId.MiniMorph] = ShipHull(
        requirements, cost, tech_slots, armor, initiative, mass, fuel_capacity,
        cargo_capacity)

    return technologies


def build_predefined_races():
    races = {}
    races[PredefinedRaces.Antethereal] = createAntethereal()
    races[PredefinedRaces.Humanoid] = createHumanoid()
    races[PredefinedRaces.Insectoid] = createInsectoid()
    races[PredefinedRaces.Nucleotid] = createNucleotid()
    races[PredefinedRaces.Rabbitoid] = createRabbitoid()
    races[PredefinedRaces.Silicanoid] = createSilicanoid()
    return races


def build_computer_races():
    """
    Computer race data based on data by:

    AI Race Specs by Wumpus - 27 Feb 2007
    http://wiki.starsautohost.org/wiki/AI_Race_Specs_by_Wumpus_-_27_Feb_2007_v2.6/7

    Robotoid - HE
    Turindrone - SS
    Automitron - IS
    Rototil - CA
    Cybertron - PP
    Macinti - AR

    These settings can also be verified by examining the race files directly
    using the AI password: viewai
    """
    races = {}
    races[ComputerRaces.RobotoidEasy] = createRobotoidEasy()
    races[ComputerRaces.RobotoidNormal] = createRobotoidNormal()
    races[ComputerRaces.RobotoidTough] = createRobotoidTough()
    races[ComputerRaces.RobotoidExpert] = createRobotoidExpert()

    races[ComputerRaces.TurindroneEasy] = createTurindroneEasy()
    races[ComputerRaces.TurindroneNormal] = createTurindroneNormal()
    races[ComputerRaces.TurindroneTough] = createTurindroneTough()
    races[ComputerRaces.TurindroneExpert] = createTurindroneExpert()

    races[ComputerRaces.AutomitronEasy] = createAutomitronEasy()
    races[ComputerRaces.AutomitronNormal] = createAutomitronNormal()
    races[ComputerRaces.AutomitronTough] = createAutomitronTough()
    races[ComputerRaces.AutomitronExpert] = createAutomitronExpert()

    races[ComputerRaces.RototilEasy] = createRototilEasy()
    races[ComputerRaces.RototilNormal] = createRototilNormal()
    races[ComputerRaces.RototilTough] = createRototilTough()
    races[ComputerRaces.RototilExpert] = createRototilExpert()

    races[ComputerRaces.CybertronEasy] = createCybertronEasy()
    races[ComputerRaces.CybertronNormal] = createCybertronNormal()
    races[ComputerRaces.CybertronTough] = createCybertronTough()
    races[ComputerRaces.CybertronExpert] = createCybertronExpert()

    races[ComputerRaces.MacintiEasy] = createMacintiEasy()
    races[ComputerRaces.MacintiNormal] = createMacintiNormal()
    races[ComputerRaces.MacintiTough] = createMacintiTough()
    races[ComputerRaces.MacintiExpert] = createMacintiExpert()

    return races


def createAntethereal():
    r = Race()
    r.name = Language_Map[
        "predefined-race-singular-names"][PredefinedRaces.Antethereal]

    r.plural_name = Language_Map[
        "predefined-race-plural-names"][PredefinedRaces.Antethereal]

    r.description = Language_Map[
        "predefined-race-descriptions"][PredefinedRaces.Antethereal]

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals
    r.icon = 12
    r.primary_racial_trait = PrimaryRacialTrait.SpaceDemolition
    r.lesser_racial_traits = [
        LesserRacialTrait.NoRamscoopEngines,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.AdvancedRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.MineralAlchemy
    ]

    r.gravity_immune = False
    r.gravity_min = 0.12
    r.gravity_max = 0.55

    r.temperature_immune = False
    r.temperature_min = -200
    r.temperature_max = 200

    r.radiation_immune = False
    r.radiation_min = 70
    r.radiation_max = 100

    r.growth_rate = 7

    r.resource_production = 700
    r.factory_production = 11
    r.factory_cost = 10
    r.colonists_operate_factories = 18
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 10
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Cheap
    r.propulsion_cost = ResearchCostOption.Cheap
    r.biotechnology_cost = ResearchCostOption.Cheap
    r.electronics_cost = ResearchCostOption.Cheap
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Cheap
    r.expensive_tech_boost = False

    return r


def createHumanoid():
    r = Race()
    r.name = Language_Map[
        "predefined-race-singular-names"][PredefinedRaces.Humanoid]

    r.plural_name = Language_Map[
        "predefined-race-plural-names"][PredefinedRaces.Humanoid]

    r.description = Language_Map[
        "predefined-race-descriptions"][PredefinedRaces.Humanoid]

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals
    r.icon = 15

    r.primary_racial_trait = PrimaryRacialTrait.JackOfAllTrades

    r.gravity_immune = False
    r.gravity_min = .22
    r.gravity_max = 4.4

    r.temperature_immune = False
    r.temperature_min = -140
    r.temperature_max = 140

    r.radiation_immune = False
    r.radiation_min = 15
    r.radiation_max = 85

    r.growth_rate = 15

    r.resource_production = 1000
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False

    return r


def createInsectoid():
    r = Race()
    r.name = Language_Map[
        "predefined-race-singular-names"][PredefinedRaces.Insectoid]

    r.plural_name = Language_Map[
        "predefined-race-plural-names"][PredefinedRaces.Insectoid]

    r.description = Language_Map[
        "predefined-race-descriptions"][PredefinedRaces.Insectoid]

    r.icon = 7
    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.WarMonger
    r.lesser_racial_traits = [
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.ImprovedStarbases,
        LesserRacialTrait.RegeneratingShields
    ]

    r.gravity_immune = True

    r.temperature_immune = False
    r.temperature_min = -200
    r.temperature_max = 200

    r.radiation_immune = False
    r.radiation_min = 70
    r.radiation_max = 100

    r.growth_rate = 10

    r.resource_production = 1000
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = False
    r.mine_production = 9
    r.mine_cost = 10
    r.colonists_operate_mines = 6

    r.energy_cost = ResearchCostOption.Cheap
    r.propulsion_cost = ResearchCostOption.Cheap
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Cheap
    r.construction_cost = ResearchCostOption.Cheap
    r.expensive_tech_boost = False

    return r


def createNucleotid():
    r = Race()

    r.name = Language_Map[
        "predefined-race-singular-names"][PredefinedRaces.Nucleotid]

    r.plural_name = Language_Map[
        "predefined-race-plural-names"][PredefinedRaces.Nucleotid]

    r.description = Language_Map[
        "predefined-race-descriptions"][PredefinedRaces.Nucleotid]

    r.icon = 0
    r.leftover_points = LeftoverPointsOption.Factories
    r.primary_racial_trait = PrimaryRacialTrait.SuperStealth

    r.lesser_racial_traits = [
        LesserRacialTrait.AdvancedRemoteMining,
        LesserRacialTrait.ImprovedStarbases
    ]

    r.gravity_immune = True

    r.temperature_immune = False
    r.temperature_min = -152
    r.temperature_max = 152

    r.radiation_immune = False
    r.radiation_min = 0
    r.radiation_max = 100

    r.growth_rate = 10

    r.resource_production = 900
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 15
    r.colonists_operate_mines = 5

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True

    return r


def createRabbitoid():
    r = Race()
    r.name = Language_Map[
        "predefined-race-singular-names"][PredefinedRaces.Rabbitoid]

    r.plural_name = Language_Map[
        "predefined-race-plural-names"][PredefinedRaces.Rabbitoid]

    r.description = Language_Map[
        "predefined-race-descriptions"][PredefinedRaces.Rabbitoid]

    r.icon = 1

    r.leftover_points = LeftoverPointsOption.Defenses
    r.primary_racial_trait = PrimaryRacialTrait.InterstellarTraveler

    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.NoAdvancedScanners
    ]

    r.gravity_immune = False
    r.gravity_min = .17
    r.gravity_max = 1.24

    r.temperature_immune = False
    r.temperature_min = -60
    r.temperature_max = 124

    r.radiation_immune = False
    r.radiation_min = 13
    r.radiation_max = 53

    r.growth_rate = 20

    r.resource_production = 1000
    r.factory_production = 10
    r.factory_cost = 9
    r.colonists_operate_factories = 17
    r.factory_cheap_germanium = True
    r.mine_production = 10
    r.mine_cost = 9
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Cheap
    r.biotechnology_cost = ResearchCostOption.Cheap
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False

    return r


def createSilicanoid():
    r = Race()
    r.name = Language_Map[
        "predefined-race-singular-names"][PredefinedRaces.Silicanoid]

    r.plural_name = Language_Map[
        "predefined-race-plural-names"][PredefinedRaces.Silicanoid]

    r.description = Language_Map[
        "predefined-race-descriptions"][PredefinedRaces.Silicanoid]

    r.icon = 3
    r.leftover_points = LeftoverPointsOption.Factories
    r.primary_racial_trait = PrimaryRacialTrait.HyperExpansion

    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.UltimateRecycling,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.BleedingEdgeTechnology
    ]

    r.gravity_immune = True
    r.temperature_immune = True
    r.radiation_immune = True

    r.growth_rate = 6

    r.resource_production = 800
    r.factory_production = 12
    r.factory_cost = 12
    r.colonists_operate_factories = 15
    r.factory_cheap_germanium = True
    r.mine_production = 10
    r.mine_cost = 9
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Cheap
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Cheap
    r.expensive_tech_boost = False

    return r


def createRobotoidEasy():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.RobotoidEasy]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.RobotoidEasy]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.HyperExpansion
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.BleedingEdgeTechnology
    ]

    r.gravity_immune = True
    r.temperature_immune = True
    r.radiation_immune = True

    r.growth_rate = 5

    r.resource_production = 1000
    r.factory_production = 12
    r.factory_cost = 10
    r.colonists_operate_factories = 16
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Cheap
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createRobotoidNormal():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.RobotoidNormal]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.RobotoidNormal]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.HyperExpansion
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.OnlyBasicRemoteMining,
    ]

    r.gravity_immune = True
    r.temperature_immune = True
    r.radiation_immune = True

    r.growth_rate = 6

    r.resource_production = 900
    r.factory_production = 13
    r.factory_cost = 9
    r.colonists_operate_factories = 16
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 4
    r.colonists_operate_mines = 11

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Cheap
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createRobotoidTough():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.RobotoidTough]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.RobotoidTough]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.HyperExpansion
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.UltimateRecycling,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.OnlyBasicRemoteMining,
    ]

    r.gravity_immune = True
    r.temperature_immune = True
    r.radiation_immune = True

    r.growth_rate = 6

    r.resource_production = 800
    r.factory_production = 13
    r.factory_cost = 9
    r.colonists_operate_factories = 18
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 4
    r.colonists_operate_mines = 12

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Cheap
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Cheap
    r.construction_cost = ResearchCostOption.Cheap
    r.expensive_tech_boost = False
    return r


def createRobotoidExpert():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.RobotoidExpert]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.RobotoidExpert]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.HyperExpansion
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.UltimateRecycling,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.OnlyBasicRemoteMining,
    ]

    r.gravity_immune = True
    r.temperature_immune = True
    r.radiation_immune = True

    r.growth_rate = 7

    r.resource_production = 800
    r.factory_production = 13
    r.factory_cost = 9
    r.colonists_operate_factories = 16
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 4
    r.colonists_operate_mines = 8

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Cheap
    r.construction_cost = ResearchCostOption.Cheap
    r.expensive_tech_boost = False
    return r


def createTurindroneEasy():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.TurindroneEasy]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.TurindroneEasy]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.SuperStealth
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.AdvancedRemoteMining,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.RegeneratingShields
    ]

    r.gravity_min = 0.52
    r.gravity_max = 5.36
    r.gravity_immune = False

    r.temperature_min = -172
    r.temperature_max = 52
    r.temperature_immune = False

    r.radiation_min = 35
    r.radiation_max = 95
    r.radiation_immune = False

    r.growth_rate = 14

    r.resource_production = 1000
    r.factory_production = 9
    r.factory_cost = 10
    r.colonists_operate_factories = 9
    r.factory_cheap_germanium = False
    r.mine_production = 9
    r.mine_cost = 5
    r.colonists_operate_mines = 8

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createTurindroneNormal():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.TurindroneNormal]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.TurindroneNormal]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.SuperStealth
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.AdvancedRemoteMining,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.RegeneratingShields
    ]

    r.gravity_min = 0.58
    r.gravity_max = 6.08
    r.gravity_immune = False

    r.temperature_min = -176
    r.temperature_max = 40
    r.temperature_immune = False

    r.radiation_min = 26
    r.radiation_max = 96
    r.radiation_immune = False

    r.growth_rate = 14

    r.resource_production = 1000
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = True
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 9

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createTurindroneTough():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.TurindroneTough]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.TurindroneTough]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.SuperStealth
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.AdvancedRemoteMining,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.RegeneratingShields
    ]

    r.gravity_min = 0.56
    r.gravity_max = 6.80
    r.gravity_immune = False

    r.temperature_min = -184
    r.temperature_max = 8
    r.temperature_immune = False

    r.radiation_min = 30
    r.radiation_max = 94
    r.radiation_immune = False

    r.growth_rate = 14

    r.resource_production = 900
    r.factory_production = 11
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = True
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 9

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createTurindroneExpert():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.TurindroneExpert]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.TurindroneExpert]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.SuperStealth
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.AdvancedRemoteMining,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.RegeneratingShields
    ]

    r.gravity_min = 0.56
    r.gravity_max = 6.32
    r.gravity_immune = False

    r.temperature_min = -180
    r.temperature_max = 12
    r.temperature_immune = False

    r.radiation_immune = True

    r.growth_rate = 15

    r.resource_production = 800
    r.factory_production = 15
    r.factory_cost = 10
    r.colonists_operate_factories = 25
    r.factory_cheap_germanium = True
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 9

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createAutomitronEasy():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.AutomitronEasy]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.AutomitronEasy]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.InterstellarTraveler
    r.lesser_racial_traits = [
        LesserRacialTrait.GeneralizedResearch,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation
    ]

    r.gravity_min = 0.15
    r.gravity_max = 1.52
    r.gravity_immune = False

    r.temperature_min = -96
    r.temperature_max = 176
    r.temperature_immune = False

    r.radiation_min = 5
    r.radiation_max = 71
    r.radiation_immune = False

    r.growth_rate = 15

    r.resource_production = 900
    r.factory_production = 11
    r.factory_cost = 10
    r.colonists_operate_factories = 14
    r.factory_cheap_germanium = False
    r.mine_production = 11
    r.mine_cost = 6
    r.colonists_operate_mines = 14

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createAutomitronNormal():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.AutomitronNormal]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.AutomitronNormal]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.InterstellarTraveler
    r.lesser_racial_traits = [
        LesserRacialTrait.GeneralizedResearch,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation
    ]

    r.gravity_min = 0.15
    r.gravity_max = 1.52
    r.gravity_immune = False

    r.temperature_min = -96
    r.temperature_max = 176
    r.temperature_immune = False

    r.radiation_min = 5
    r.radiation_max = 71
    r.radiation_immune = False

    r.growth_rate = 15

    r.resource_production = 800
    r.factory_production = 13
    r.factory_cost = 9
    r.colonists_operate_factories = 14
    r.factory_cheap_germanium = True
    r.mine_production = 10
    r.mine_cost = 6
    r.colonists_operate_mines = 14

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createAutomitronTough():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.AutomitronTough]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.AutomitronTough]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.InterstellarTraveler
    r.lesser_racial_traits = [
        LesserRacialTrait.GeneralizedResearch,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation
    ]

    r.gravity_min = 0.15
    r.gravity_max = 1.52
    r.gravity_immune = False

    r.temperature_min = -96
    r.temperature_max = 176
    r.temperature_immune = False

    r.radiation_min = 5
    r.radiation_max = 71
    r.radiation_immune = False

    r.growth_rate = 15

    r.resource_production = 800
    r.factory_production = 14
    r.factory_cost = 9
    r.colonists_operate_factories = 15
    r.factory_cheap_germanium = True
    r.mine_production = 14
    r.mine_cost = 5
    r.colonists_operate_mines = 15

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createAutomitronExpert():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.AutomitronExpert]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.AutomitronExpert]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.InterstellarTraveler
    r.lesser_racial_traits = [
        LesserRacialTrait.GeneralizedResearch,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation
    ]

    r.gravity_min = 0.15
    r.gravity_max = 1.52
    r.gravity_immune = False

    r.temperature_immune = True

    r.radiation_min = 0
    r.radiation_max = 100
    r.radiation_immune = False

    r.growth_rate = 16

    r.resource_production = 800
    r.factory_production = 14
    r.factory_cost = 9
    r.colonists_operate_factories = 14
    r.factory_cheap_germanium = True
    r.mine_production = 14
    r.mine_cost = 5
    r.colonists_operate_mines = 14

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createRototilEasy():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.RototilEasy]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.RototilEasy]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.ClaimAdjuster
    r.lesser_racial_traits = [
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.CheapEngines,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation,
        LesserRacialTrait.BleedingEdgeTechnology
    ]

    r.gravity_min = 0.58
    r.gravity_max = 1.72
    r.gravity_immune = False

    r.temperature_min = -76
    r.temperature_max = 76
    r.temperature_immune = False

    r.radiation_min = 31
    r.radiation_max = 69
    r.radiation_immune = False

    r.growth_rate = 15

    r.resource_production = 1000
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = False
    r.mine_production = 14
    r.mine_cost = 5
    r.colonists_operate_mines = 14

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createRototilNormal():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.RototilNormal]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.RototilNormal]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.ClaimAdjuster
    r.lesser_racial_traits = [
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation,
        LesserRacialTrait.BleedingEdgeTechnology
    ]

    r.gravity_min = 0.58
    r.gravity_max = 1.72
    r.gravity_immune = False

    r.temperature_min = -76
    r.temperature_max = 76
    r.temperature_immune = False

    r.radiation_min = 31
    r.radiation_max = 69
    r.radiation_immune = False

    r.growth_rate = 15

    r.resource_production = 800
    r.factory_production = 12
    r.factory_cost = 10
    r.colonists_operate_factories = 12
    r.factory_cheap_germanium = False
    r.mine_production = 14
    r.mine_cost = 5
    r.colonists_operate_mines = 12

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Cheap
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createRototilTough():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.RototilTough]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.RototilTough]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.ClaimAdjuster
    r.lesser_racial_traits = [
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation,
        LesserRacialTrait.BleedingEdgeTechnology
    ]

    r.gravity_min = 0.40
    r.gravity_max = 2.48
    r.gravity_immune = False

    r.temperature_min = -104
    r.temperature_max = 104
    r.temperature_immune = False

    r.radiation_min = 25
    r.radiation_max = 75
    r.radiation_immune = False

    r.growth_rate = 15

    r.resource_production = 800
    r.factory_production = 12
    r.factory_cost = 10
    r.colonists_operate_factories = 12
    r.factory_cheap_germanium = False
    r.mine_production = 14
    r.mine_cost = 5
    r.colonists_operate_mines = 12

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Cheap
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createRototilExpert():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.RototilExpert]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.RototilExpert]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.ClaimAdjuster
    r.lesser_racial_traits = [
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation,
        LesserRacialTrait.BleedingEdgeTechnology
    ]

    r.gravity_immune = True

    r.temperature_min = -104
    r.temperature_max = 104
    r.temperature_immune = False

    r.radiation_min = 25
    r.radiation_max = 75
    r.radiation_immune = False

    r.growth_rate = 15

    r.resource_production = 800
    r.factory_production = 15
    r.factory_cost = 10
    r.colonists_operate_factories = 15
    r.factory_cheap_germanium = False
    r.mine_production = 15
    r.mine_cost = 5
    r.colonists_operate_mines = 15

    r.energy_cost = ResearchCostOption.Expensive
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Cheap
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Expensive
    r.expensive_tech_boost = True
    return r


def createCybertronEasy():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.CybertronEasy]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.CybertronEasy]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.PacketPhysics
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.LowStartingPopulation
    ]

    r.gravity_min = 0.36
    r.gravity_max = 2.72
    r.gravity_immune = False

    r.temperature_min = -112
    r.temperature_max = 112
    r.temperature_immune = False

    r.radiation_min = 22
    r.radiation_max = 78
    r.radiation_immune = False

    r.growth_rate = 12

    r.resource_production = 1000
    r.factory_production = 9
    r.factory_cost = 18
    r.colonists_operate_factories = 9
    r.factory_cheap_germanium = False
    r.mine_production = 9
    r.mine_cost = 18
    r.colonists_operate_mines = 9

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Expensive
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = True
    return r


def createCybertronNormal():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.CybertronNormal]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.CybertronNormal]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.PacketPhysics
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation
    ]

    r.gravity_min = 0.29
    r.gravity_max = 3.44
    r.gravity_immune = False

    r.temperature_min = -124
    r.temperature_max = 124
    r.temperature_immune = False

    r.radiation_min = 19
    r.radiation_max = 81
    r.radiation_immune = False

    r.growth_rate = 17

    r.resource_production = 1000
    r.factory_production = 10
    r.factory_cost = 13
    r.colonists_operate_factories = 19
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 10
    r.colonists_operate_mines = 7

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Expensive
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = True
    return r


def createCybertronTough():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.CybertronTough]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.CybertronTough]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.PacketPhysics
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation
    ]

    r.gravity_min = 0.27
    r.gravity_max = 3.68
    r.gravity_immune = False

    r.temperature_min = -128
    r.temperature_max = 128
    r.temperature_immune = False

    r.radiation_min = 18
    r.radiation_max = 82
    r.radiation_immune = False

    r.growth_rate = 17

    r.resource_production = 1000
    r.factory_production = 14
    r.factory_cost = 10
    r.colonists_operate_factories = 20
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 10
    r.colonists_operate_mines = 6

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Cheap
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createCybertronExpert():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.CybertronExpert]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.CybertronExpert]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.MineralConcentration

    r.primary_racial_trait = PrimaryRacialTrait.PacketPhysics
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.MineralAlchemy,
        LesserRacialTrait.OnlyBasicRemoteMining,
        LesserRacialTrait.NoAdvancedScanners,
        LesserRacialTrait.LowStartingPopulation
    ]

    r.gravity_min = 0.25
    r.gravity_max = 3.92
    r.gravity_immune = False

    r.temperature_min = -132
    r.temperature_max = 132
    r.temperature_immune = False

    r.radiation_min = 17
    r.radiation_max = 83
    r.radiation_immune = False

    r.growth_rate = 19

    r.resource_production = 1000
    r.factory_production = 15
    r.factory_cost = 9
    r.colonists_operate_factories = 25
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 10
    r.colonists_operate_mines = 5

    r.energy_cost = ResearchCostOption.Cheap
    r.propulsion_cost = ResearchCostOption.Expensive
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Cheap
    r.construction_cost = ResearchCostOption.Cheap
    r.expensive_tech_boost = False
    return r


def createMacintiEasy():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.MacintiEasy]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.MacintiEasy]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.AlternateReality
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.ImprovedStarbases,
        LesserRacialTrait.GeneralizedResearch,
        LesserRacialTrait.CheapEngines
    ]

    r.gravity_min = 0.31
    r.gravity_max = 3.20
    r.gravity_immune = False

    r.temperature_min = -120
    r.temperature_max = 120
    r.temperature_immune = False

    r.radiation_min = 20
    r.radiation_max = 80
    r.radiation_immune = False

    r.growth_rate = 10

    r.resource_production = 1600
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createMacintiNormal():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.MacintiNormal]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.MacintiNormal]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.AlternateReality
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.ImprovedStarbases,
        LesserRacialTrait.GeneralizedResearch,
        LesserRacialTrait.CheapEngines
    ]

    r.gravity_min = 0.31
    r.gravity_max = 3.20
    r.gravity_immune = False

    r.temperature_min = -120
    r.temperature_max = 120
    r.temperature_immune = False

    r.radiation_min = 20
    r.radiation_max = 80
    r.radiation_immune = False

    r.growth_rate = 10

    r.resource_production = 1600
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Normal
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Expensive
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createMacintiTough():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.MacintiTough]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.MacintiTough]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.AlternateReality
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.AdvancedRemoteMining,
        LesserRacialTrait.ImprovedStarbases,
        LesserRacialTrait.GeneralizedResearch,
        LesserRacialTrait.UltimateRecycling,
        LesserRacialTrait.MineralAlchemy
    ]

    r.gravity_min = 0.22
    r.gravity_max = 4.40
    r.gravity_immune = False

    r.temperature_min = -140
    r.temperature_max = 140
    r.temperature_immune = False

    r.radiation_min = 15
    r.radiation_max = 85
    r.radiation_immune = False

    r.growth_rate = 17

    r.resource_production = 1000
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Cheap
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Normal
    r.expensive_tech_boost = False
    return r


def createMacintiExpert():
    r = Race()

    r.name = Language_Map[
        "computer-race-singular-names"][ComputerRaces.MacintiExpert]

    r.plural_name = Language_Map[
        "computer-race-plural-names"][ComputerRaces.MacintiExpert]

    r.icon = 27

    r.leftover_points = LeftoverPointsOption.SurfaceMinerals

    r.primary_racial_trait = PrimaryRacialTrait.AlternateReality
    r.lesser_racial_traits = [
        LesserRacialTrait.ImprovedFuelEfficiency,
        LesserRacialTrait.TotalTerraforming,
        LesserRacialTrait.AdvancedRemoteMining,
        LesserRacialTrait.ImprovedStarbases,
        LesserRacialTrait.GeneralizedResearch,
        LesserRacialTrait.UltimateRecycling,
        LesserRacialTrait.MineralAlchemy
    ]

    r.gravity_min = 0.22
    r.gravity_max = 4.40
    r.gravity_immune = False

    r.temperature_min = -140
    r.temperature_max = 140
    r.temperature_immune = False

    r.radiation_min = 15
    r.radiation_max = 85
    r.radiation_immune = False

    r.growth_rate = 20

    r.resource_production = 1000
    r.factory_production = 10
    r.factory_cost = 10
    r.colonists_operate_factories = 10
    r.factory_cheap_germanium = False
    r.mine_production = 10
    r.mine_cost = 5
    r.colonists_operate_mines = 10

    r.energy_cost = ResearchCostOption.Cheap
    r.propulsion_cost = ResearchCostOption.Normal
    r.biotechnology_cost = ResearchCostOption.Normal
    r.electronics_cost = ResearchCostOption.Normal
    r.weapons_cost = ResearchCostOption.Normal
    r.construction_cost = ResearchCostOption.Cheap
    r.expensive_tech_boost = False
    return r
