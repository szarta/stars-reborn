"""
    turn.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import jsonpickle
import gzip

from src.data import Language_Map
from src.model.enumerations import GameStrings
from src.race import get_starting_population


class TurnMessageType:
    Tip = 0
    Intro = 1


class TurnMessage:
    def __init__(self, type, message, action=None):
        self.message_type = type
        self.message = message
        self.action = action


class Turn:
    def __init__(self):
        self.active_player = 0
        self.visible_universe = None
        self.messages = []
        self.action_queue = []


def generate_visible_universe(universe, normal_visibility_regions,
                              penetrating_visibility_regions):
    pass


def generate_turn_zero(game, save_directory):

    planet_ids = game.universe.planets.keys()
    for planet_id in planet_ids:
        planet = game.universe.planets[planet_id]
        if(planet.owner is not None):
            owner_player = game.universe.players[planet.owner]
            starting_population = get_starting_population(
                owner_player.race, game.universe)

            if(planet.homeworld):
                planet.population = starting_population
            else:
                planet.population = starting_population / 2

    turns = [Turn() for i in xrange(len(game.players))]

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

    for pid in game.players.keys():
        turn = turns[pid]
        turn.visible_universe = generate_visible_universe(
            game.universe, player.get_normal_visibility_regions(),
            player.get_penetrating_visibility_regions())

    for pid in game.players.keys():
        f = gzip.open("{0}/{1}.m{2!s}".format(
            save_directory, game.save_name, pid))
        f.write(jsonpickle.encode(turn[pid], keys=True))
        f.close()

    f = gzip.open("{0}/{1}.xy".format(save_directory, game.save_name))
    f.write(jsonpickle.encode(game, keys=True))
    f.close()
