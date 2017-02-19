"""
    space.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import math

from src.model.enumerations import NeverSeenPlanet
from src.model.enumerations import PlanetView


class SpaceObject(object):
    def __init__(self, id, location):
        self.id = id
        self.location = location

    def to_svg(self):
        return ""

    def distance_from(self, other):

        (x1, y1) = self.location
        (x2, y2) = other.location

        d = round(math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)), 2)
        return d


class Planet(SpaceObject):
    def __init__(self, id, location, name):
        """
        Creates a planet object.  Note that some of this data will not
        necessarily be known or populated for given players, given their
        information level and relationship (owned vs. not) on the planet.
        """
        SpaceObject.__init__(self, id, location)

        self.name = name
        self.reset_to_unknown()

    def reset_to_unknown(self):
        self.owner = None
        self.homeworld = False
        self.population = 0
        self.mines = 0
        self.factories = 0
        self.defenses = 0
        self.fleet_waypoint_location = None
        self.packet_waypoint_location = None
        self.packet_warp_speed = 0
        self.production_queue = []
        self.related_starbase = None
        self.all_fleets = {}
        self.friendly_fleets = []
        self.enemy_fleets = []

        # Minerals
        self.ironium_concentration = 0
        self.boranium_concentration = 0
        self.germanium_concentration = 0
        self.surface_ironium = 0
        self.surface_boranium = 0
        self.surface_germanium = 0

        # Habitat
        self.gravity_level = 0
        self.temperature_level = 0
        self.radiation_level = 0

        self.has_been_colonized = False
        self.planetary_defense = 0
        self.years_since = NeverSeenPlanet

    def calculate_value(self, race):
        return 100

    def to_svg(self, view_options, current_player):
        zoom_multiplier = view_options.zoom_multiplier()
        planet_view = view_options.planet_view

        ret_svg = ""

        show_name = (zoom_multiplier > .5) and view_options.planet_names_overlay
        x, y = self.location
        x *= zoom_multiplier
        y *= zoom_multiplier
        ret_svg = '<g class="node" transform="translate({0!s},{1!s})" onmouseup="planetClick(evt, {3!s})">'.format(x, y, self.id, self.id)

        ret_svg += '<rect pointer-events="visible" width="30" height="30" fill="none" transform="translate(-15, -15)" />'

        if(self.years_since == NeverSeenPlanet):
            ret_svg += "<rect width=\"5\" height=\"5\" fill=\"grey\" />"
            if(show_name):
                font_size = get_font_size(zoom_multiplier)
                ret_svg += "<text style=\"fill: #ffffff; stroke: none; font-size:{0!s}px; font-weight: bold; font-family: Arial; text-anchor:middle;\" transform=\"translate(0, 20)\">".format(font_size)
                ret_svg += self.name
                ret_svg += "</text>"

        else:
            # use data - will be historical or current
            if(planet_view == PlanetView.Normal):
                friendly_ships = len(self.friendly_fleets) > 0
                enemy_ships = len(self.enemy_fleets) > 0
                starbase = not(self.related_starbase is None)

                outline = ""
                if (friendly_ships and enemy_ships):
                    outline = '<circle r="10" stroke="purple" stroke-width="1" fill="none"/>'
                elif(friendly_ships):
                    outline = '<circle r="10" stroke="white" stroke-width="1" fill="none"/>'
                elif(enemy_ships):
                    outline = '<circle r="10" stroke="red" stroke-width="1" fill="none"/>'

                ret_svg += outline

                if(current_player.id == self.owner):
                    ret_svg += ' <circle r="5" stroke="#366b01" stroke-width="2" fill="#05ff00"/>'
                else:
                    ret_svg += ' <circle r="5" stroke="#366b01" stroke-width="2" fill="red"/>'
                    # TODO - deal with allies, assumes enemy for now

                if(starbase):
                    ret_svg += '<circle cx="6" cy="-4" r="3" fill="white"/>'

                if(show_name):
                    font_size = get_font_size(zoom_multiplier)
                    ret_svg += "<text style=\"fill: #ffffff; stroke: none; font-size:{0!s}px; font-weight: bold; font-family: Arial; text-anchor:middle;\" transform=\"translate(0, 20)\">".format(font_size)
                    ret_svg += self.name
                    ret_svg += "</text>"
            elif(planet_view == PlanetView.NoInfo):
                ret_svg += "<rect width=\"5\" height=\"5\" fill=\"grey\" />"
                if(show_name):
                    font_size = get_font_size(zoom_multiplier)
                    ret_svg += "<text style=\"fill: #ffffff; stroke: none; font-size:{0!s}px; font-weight: bold; font-family: Arial; text-anchor:middle;\" transform=\"translate(0, 20)\">".format(font_size)
                    ret_svg += self.name
                    ret_svg += "</text>"

        ret_svg += "</g>"

        """
            elif(planet_view == PlanetView.SurfaceMinerals):

            elif(planet_view == PlanetView.MineralConcentration):

            elif(planet_view == PlanetView.PercentPopulation):

            elif(planet_view == PlanetView.PopulationView):
        """
        return ret_svg


def get_font_size(zoom_multiplier):
    if(zoom_multiplier < 1.0):
        return 11

    if(zoom_multiplier == 4.0):
        return 14

    return 12




class MineField(SpaceObject):
    def __init__(self, id, location, owner):
        SpaceObject.__init__(self, id, location)

        self.owner = owner


class MineralPacket(SpaceObject):
    def __init__(self, id, location, owner, cargo, destination, speed):
        SpaceObject.__init__(self, id, location)

        self.owner = owner
        self.cargo = cargo
        self.destination = destination
        self.speed = speed


class Wormhole(SpaceObject):
    def __init__(self, id, location, stability, other_side):
        SpaceObject.__init__(self, id, location)

        self.stability = stability
        self.other_side = other_side


class Fleet(SpaceObject):
    def __init__(self, id, location, owner):
        SpaceObject.__init__(self, id, location)

        self.owner = owner
        self.ships = []

        self.orbitingPlanet = None


class Ship(SpaceObject):
    def __init__(self, id, location, owner, design, fuel, speed, cargo):
        SpaceObject.__init__(self, id, location)

        self.owner = owner
        self.design = design
        self.fuel = fuel
        self.speed = speed
        self.cargo = cargo

        self.orbitingPlanet = None

    def is_capital(self):
        return False

    def is_unarmed(self):
        return False

    def is_bomber(self):
        return False

    def is_freighter(self):
        return False

    def is_fuel_transport(self):
        return False

    def is_escort(self):
        return False


def set_player_homeworld(player, planet):
    planet.homeworld = True
    planet.owner = player.id
    planet.has_been_colonized = True

    player.homeworld = planet.id
