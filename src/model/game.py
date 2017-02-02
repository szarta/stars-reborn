"""
    game.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from enumerations import StartingYear
from turn import Turn


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

        self.victory_conditions = []
        self.history = {}
        self.turn = None


def read_game(filepath):
    g = Game()
    g.turn = Turn()
    return g
