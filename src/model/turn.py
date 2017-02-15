"""
    turn.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import logging

from src.data import Language_Map
from src.model.enumerations import GameStrings


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


def generate_turn_zero(game):
    for pid in game.players.keys():
        player = game.players[pid]

        turn = Turn()
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

            print game.universe
            homeworld_name = game.universe.planets[player.homeworld].name

            turn.messages.append(TurnMessage(
                TurnMessageType.Intro,
                Language_Map["original-game-strings"][GameStrings.Homeworld].format(
                    homeworld_name),
                { "location": game.universe.planets[player.homeworld].location }))


            p.apply_trait_adjustments()

            """

    for pid in new_game.universe.planets:
        planet = new_game.universe.planets[pid]

        for player_id in new_game.universe.players:
            planet.players_scan_data[player_id] = SnapshotData()

        if(planet.owner_id != -1):
            owner_player = new_game.universe.players[planet.owner_id]
            if(planet.homeworld):
                planet.population = owner_player.get_starting_population(new_game.universe.size)
            else:
                planet.population = owner_player.get_starting_population(new_game.universe.size) / 2

    # prepare the turn files
    for pid in new_game.universe.players:
        player_game = generate_player_game(new_game, pid)

        # finally add scanning
        apply_scanning(new_game.universe, player_game.universe)

        write_game(player_game)

    new_game.save_name = "{0}.xy".format(new_game.save_name)
    write_game(new_game)
            """
