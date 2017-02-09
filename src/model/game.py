"""
    game.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import logging
from enumerations import StartingYear

from turn import Turn

from src.util import get_bounded_value


class VictoryConditionArray:
    Min = 0
    Max = 1
    Step = 2
    Default = 3


class VictoryConditionParameters:
    MinimumYears = 0
    Planets = 1
    TechLevel = 2
    TechFields = 3
    ExceedsScore = 4
    ExceedsSecondPlaceScore = 5
    ProductionCapacity = 6
    CapitalShips = 7
    HighestScoreYears = 8


VictoryConditionParameterArray = [
    [30, 500, 10, 50],
    [20, 100, 5, 60],
    [8, 26, 1, 22],
    [2, 6, 1, 4],
    [1000, 20000, 1000, 11000],
    [20, 300, 10, 100],
    [10, 500, 10, 100],
    [10, 300, 10, 100],
    [30, 900, 10, 100]
]


class VictoryConditions:
    Planets = 0
    Tech = 1
    ExceedsScore = 2
    ExceedsSecondPlaceScore = 3
    ProductionCapacity = 4
    CapitalShips = 5
    HighestScoreYears = 6

    def __init__(self):
        self.condition_enabled = []
        for i in xrange(7):
            self.condition_enabled.append(False)

        self.conditions_needed = 0

        self._victory_parameter = []

        arr = VictoryConditionParameterArray
        default = VictoryConditionArray.Default

        for i in xrange(len(arr)):
            self._victory_parameter.append(arr[i][default])

    def get_victory_parameter(self, parameter):
        if parameter > (len(self._victory_parameter) - 1):
            logging.error(
                "Trying to access invalid Victory Condition parameter.")
            return None

        return self._victory_parameter[parameter]

    def set_victory_parameter(self, parameter, value):
        if parameter > (len(self._victory_parameter) - 1):
            logging.error(
                "Trying to access invalid Victory Condition parameter.")
            return

        arr = VictoryConditionParameterArray
        t_min = VictoryConditionArray.Min
        t_max = VictoryConditionArray.Max
        t_step = VictoryConditionArray.Step

        step = arr[parameter][t_step]
        min = arr[parameter][t_min]
        max = arr[parameter][t_max]

        val = int(value)
        assert(value % step == 0)
        self._victory_parameter[parameter] = get_bounded_value(
            str(parameter), val, min, max)


class Game:
    def __init__(self):
        self.name = ""
        self.save_name = "Game"

        self.universe = None
        self.year = StartingYear
        self.players = {}

        self.public_player_scores = False
        self.random_events = True
        self.accelerated_play = False
        self.slower_tech_advances = False
        self.cpu_players_form_alliances = False

        self.victory_conditions = None
        self.history = {}
        self.turn = None


def read_game(filepath):
    g = Game()
    g.turn = Turn()
    return g
