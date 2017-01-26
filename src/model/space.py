"""
    space.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import math


class SpaceObject(object):
    def __init__(self, id, location):
        self.id = id
        self.location = location

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
        self.player_scan_data = {}
        self.years_since = 0


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
