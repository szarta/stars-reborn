"""
    universe.py

    The universe module contains the functions and classes needed to build and
    interact with a game universe.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""


class Universe:
    def __init__(self, playable_area):
        self.playable_area = playable_area

        self.planets = {}
        self.fleets = []
        self.ships = []
        self.mine_fields = []
        self.mineral_packets = []
        self.wormholes = []
        self.salvage = []

    def area(self):
        return 0.0


def universe_is_tiny(universe):
    return universe.area < 400.0
