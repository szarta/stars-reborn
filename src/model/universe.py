"""
    universe.py

    The universe module contains the functions and classes needed to build and
    interact with a game universe.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""


class Universe(object):
    def __init__(self, playable_region):
        self.playable_region = playable_region

        self.planets = {}
        self.fleets = []
        self.ships = []
        self.mine_fields = []
        self.mineral_packets = []
        self.wormholes = []
        self.salvage = []

    def area(self):
        return self.playable_region.area()

    def svg_boundary(self, zoom_multiplier):
        """
        Boundary rectangle in which the universe exists.
        """
        (min_x, min_y, max_x, max_y) = self.playable_region.bounds()

        width_bound = (max_x * zoom_multiplier) + 25
        height_bound = (max_y * zoom_multiplier) + 25

        ret_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="{0}" height="{1}">'.format(
            width_bound, height_bound)

        #ret_svg += '<rect x="0" y="0" width="{0}" height="{1}" onmousemove="spaceCoord(evt.clientX, evt.clientY)" fill="black"/>'.format(width_bound, height_bound)
        ret_svg += '<rect x="0" y="0" width="{0}" height="{1}" fill="black"/>'.format(
            width_bound, height_bound)

        return ret_svg

    def to_svg(self, view_options, active_player):
        zoom_multiplier = view_options.zoom_multiplier()

        ret_svg = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>"
        ret_svg += self.svg_boundary(zoom_multiplier)

        # TODO: eventually put a purple zone around playable space, right now
        # all space is rectangular and connected, in the future it could
        # consist of many different polygons?

        for pid in self.planets.keys():
            ret_svg += self.planets[pid].to_svg(view_options, active_player)

        ret_svg += "</svg>"
        return ret_svg


def universe_is_tiny(universe):
    return universe.area < 400.0
