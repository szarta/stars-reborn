"""
    turn.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import jsonpickle
import gzip
import logging

from src.data import Language_Map
from src.model.enumerations import GameStrings
from src.model.race import get_starting_population
from src.model.game import Game
from src.model.player import Player
from src.model.universe import Universe
from src.model.space import Planet


class TurnMessageType:
    Tip = 0
    Intro = 1


class TurnMessage:
    def __init__(self, type, message, action=None):
        self.message_type = type
        self.message = message
        self.action = action


class Turn(object):
    def __init__(self):
        self.active_player = 0
        self.messages = []

        self.visible_game = None
        self.action_queue = []


def generate_visible_game(player, game):
    visible_game = Game()
    visible_game.name = game.name
    visible_game.save_name = game.save_name

    visible_game.year = game.year

    visible_game.public_player_scores = game.public_player_scores
    visible_game.random_events = game.random_events
    visible_game.accelerated_play = game.accelerated_play
    visible_game.slower_tech_advances = game.slower_tech_advances
    visible_game.cpu_players_form_alliances = game.cpu_players_form_alliances

    visible_game.victory_conditions = game.victory_conditions
    visible_game.history = None

    visible_game.players = {}
    visible_game.players[player.id] = player

    for i in game.players.keys():
        if i != player.id:
            p = Player(i)
            visible_game.players[i] = p

    visible_game.universe = generate_visible_universe(player, game.universe)
    return visible_game


def generate_visible_universe(player, universe):
    visible_universe = Universe(universe.playable_region)

    for pid in universe.planets.keys():
        p = universe.planets[pid]
        if p.owner == player.id:
            p.years_since = 0
            visible_universe.planets[pid] = p
        else:
            visible_planet = Planet(p.id, p.location, p.name)
            visible_universe.planets[pid] = visible_planet

    apply_scanning(player, universe, visible_universe)
    return visible_universe


def apply_scanning(player, actual_universe, visible_universe):
    """
    Based on scanning, update universe information
    """
    pass


def generate_turn_zero(game, save_directory):

    logging.debug("generating turn zero")
    logging.debug("setting up homeworlds")
    planet_ids = game.universe.planets.keys()
    for planet_id in planet_ids:
        planet = game.universe.planets[planet_id]
        if(planet.owner is not None):
            owner_player = game.players[planet.owner]
            starting_population = get_starting_population(
                owner_player.race, game.universe)

            if(planet.homeworld):
                planet.population = starting_population
            else:
                planet.population = starting_population / 2

    turns = [Turn() for i in xrange(len(game.players))]
    game.turns = turns

    logging.debug("building player messages")
    for pid in game.players.keys():
        player = game.players[pid]
        turn = turns[pid]
        turn.active_player = pid

        if(not player.cpu):
            turn.messages.append(TurnMessage(
                TurnMessageType.Tip,
                Language_Map["original-game-strings"][GameStrings.HidingMessages]))

            turn.messages.append(TurnMessage(
                TurnMessageType.Tip,
                Language_Map["original-game-strings"][GameStrings.AddingWaypoints]))

            turn.messages.append(TurnMessage(
                TurnMessageType.Tip,
                Language_Map["original-game-strings"][GameStrings.DesigningShips]))

            turn.messages.append(TurnMessage(
                TurnMessageType.Tip,
                Language_Map["original-game-strings"][GameStrings.PopupHelp]))

            homeworld_name = game.universe.planets[player.homeworld].name

            turn.messages.append(TurnMessage(
                TurnMessageType.Intro,
                Language_Map["original-game-strings"][GameStrings.Homeworld].format(
                    homeworld_name),
                {"location": game.universe.planets[player.homeworld].location}))

        player.apply_trait_adjustments()

    logging.debug("generating player universes")
    for pid in game.players.keys():
        player = game.players[pid]
        turn = turns[pid]
        turn.visible_game = generate_visible_game(player, game)

    logging.debug("writing out player files")
    for pid in game.players.keys():
        turn = turns[pid]
        f = gzip.open("{0}/{1}.m{2!s}".format(
            save_directory, game.save_name, pid), "wb")
        f.write(jsonpickle.encode(turn, keys=True))
        f.close()

    logging.debug("writing out master game file")
    f = gzip.open("{0}/{1}.xy".format(
        save_directory, game.save_name), "wb")
    f.write(jsonpickle.encode(game, keys=True))
    f.close()

    logging.debug("done generating turn zero")


def read_turn_file(filepath):
    f = gzip.open(filepath, "rb")
    contents = f.read()
    f.close()

    turn = jsonpickle.decode(contents, keys=True)
    return turn
