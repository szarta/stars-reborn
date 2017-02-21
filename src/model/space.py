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


# The gravity values are not linear, but still map to (0, 100) step 1
# Although the bottom-most values are a little strange in that they double
# increment
Gravity_Map = {
    "-1": "-1",
    "0.12": 0,
    "0.13": 2,
    "0.14": 4,
    "0.15": 6,
    "0.16": 8,
    "0.17": 9,
    "0.18": 11,
    "0.19": 12,
    "0.20": 13,
    "0.21": 14,
    "0.22": 15,
    "0.24": 16,
    "0.25": 17,
    "0.27": 18,
    "0.29": 19,
    "0.31": 20,
    "0.33": 21,
    "0.36": 22,
    "0.40": 23,
    "0.44": 24,
    "0.50": 25,
    "0.51": 26,
    "0.52": 27,
    "0.53": 28,
    "0.54": 29,
    "0.55": 30,
    "0.56": 31,
    "0.58": 32,
    "0.59": 33,
    "0.60": 34,
    "0.62": 35,
    "0.64": 36,
    "0.65": 37,
    "0.67": 38,
    "0.69": 39,
    "0.71": 40,
    "0.73": 41,
    "0.75": 42,
    "0.78": 43,
    "0.80": 44,
    "0.83": 45,
    "0.86": 46,
    "0.89": 47,
    "0.92": 48,
    "0.96": 49,
    "1.0": 50,
    "1.00": 50,
    "1.04": 51,
    "1.08": 52,
    "1.12": 53,
    "1.16": 54,
    "1.20": 55,
    "1.24": 56,
    "1.28": 57,
    "1.32": 58,
    "1.36": 59,
    "1.40": 60,
    "1.44": 61,
    "1.48": 62,
    "1.52": 63,
    "1.56": 64,
    "1.60": 65,
    "1.64": 66,
    "1.68": 67,
    "1.72": 68,
    "1.76": 69,
    "1.80": 70,
    "1.84": 71,
    "1.88": 72,
    "1.92": 73,
    "1.96": 74,
    "2.00": 75,
    "2.24": 76,
    "2.48": 77,
    "2.72": 78,
    "2.96": 79,
    "3.20": 80,
    "3.44": 81,
    "3.68": 82,
    "3.92": 83,
    "4.16": 84,
    "4.4": 85,
    "4.64": 86,
    "4.88": 87,
    "5.12": 88,
    "5.36": 89,
    "5.60": 90,
    "5.84": 91,
    "6.08": 92,
    "6.32": 93,
    "6.56": 94,
    "6.80": 95,
    "7.04": 96,
    "7.28": 97,
    "7.52": 98,
    "7.76": 99,
    "8.00": 100
}


def normalize_gravity(grav):
    return Gravity_Map[str(grav)]


def normalize_temperature(temp):
    if(int(temp) == -1):
        return -1

    actual_temp = int(temp)
    # maps temperature from range (-200, 200) step 4 onto range (0, 100) step 1
    # y = mx + b
    # m = 1 / 4
    # b = 50
    return int((actual_temp / 4.0) + 50)


def _calculate_hab_points(hab_radius, distance_to_center):
    """
    These calculations courtesy:

    m.a@stars
    http://starsautohost.org/sahforum2/index.php?t=msg&th=2299&rid=625&S=ee625fe2bec617564d7c694e9c5379c5&pl_view=&start=0#msg_19643
    """
    planet_value_points = 0
    red_value = 0
    ideality_correction = 1.0

    if distance_to_center <= hab_radius:
        ex_center = 100 * distance_to_center // hab_radius
        ex_center = 100 - ex_center
        planet_value_points += ex_center * ex_center

        margin = (distance_to_center * 2) - hab_radius
        if margin > 0:
            ideality_correction *= (hab_radius * 2) - margin
            ideality_correction /= (hab_radius * 2)
    else:
        negative = distance_to_center - hab_radius
        if negative > 15:
            negative = 15
        red_value += negative

    return (planet_value_points, red_value, ideality_correction)


def _calculate_planet_value(p_grav, p_temp, p_rad,
                            r_grav_immune, r_grav_min, r_grav_max,
                            r_temp_immune, r_temp_min, r_temp_max,
                            r_rad_immune, r_rad_min, r_rad_max):

    """
    These calculations courtsey:

    m.a@stars
    http://starsautohost.org/sahforum2/index.php?t=msg&th=2299&rid=625&S=ee625fe2bec617564d7c694e9c5379c5&pl_view=&start=0#msg_19643
    """
    planet_value_points = 0
    red_value = 0
    ideality = 10000

    if(r_grav_immune):
        planet_value_points += 10000
    else:
        normalized_grav_min = normalize_gravity(r_grav_min)
        normalized_grav_max = normalize_gravity(r_grav_max)
        normalized_grav_mid = (normalized_grav_max + normalized_grav_min) / 2

        normalized_p_grav = normalize_gravity(p_grav)

        distance_to_center = abs(normalized_p_grav - normalized_grav_mid)
        hab_radius = normalized_grav_mid - normalized_grav_min
        (pv, r, ic) = _calculate_hab_points(hab_radius, distance_to_center)

        planet_value_points += pv
        red_value += r
        ideality = int(ideality * ic)

    if(r_temp_immune):
        planet_value_points += 10000
    else:
        normalized_temp_min = normalize_temperature(r_temp_min)
        normalized_temp_max = normalize_temperature(r_temp_max)
        normalized_temp_mid = (normalized_temp_max + normalized_temp_min) / 2

        normalized_p_temp = normalize_temperature(p_temp)

        distance_to_center = abs(normalized_p_temp - normalized_temp_mid)
        hab_radius = normalized_temp_mid - normalized_temp_min

        (pv, r, ic) = _calculate_hab_points(hab_radius, distance_to_center)
        planet_value_points += pv
        red_value += r
        ideality = int(ideality * ic)

    if(r_rad_immune):
        planet_value_points += 10000
    else:
        r_rad_mid = (int(r_rad_min) + int(r_rad_max)) / 2
        distance_to_center = abs(int(p_rad) - r_rad_mid)
        hab_radius = int(r_rad_mid) - int(r_rad_min)
        (pv, r, ic) = _calculate_hab_points(hab_radius, distance_to_center)
        planet_value_points += pv
        red_value += r
        ideality = int(ideality * ic)

    if red_value != 0:
        return -1 * red_value

    planet_value_points = int(math.sqrt(planet_value_points / 3.0) + 0.9)
    planet_value_points = (planet_value_points * ideality) // 10000
    return planet_value_points


def calculate_planet_value(planet, race):
    """
    Calculates a planet value for a given race.

    I have tested this extensively in the stars-research project to ensure the
    calculation matches with the original game.

    The algorithm/code for this is largely from:

    m.a@stars
    http://starsautohost.org/sahforum2/index.php?t=msg&th=2299&rid=625&S=ee625fe2bec617564d7c694e9c5379c5&pl_view=&start=0#msg_19643
    """

    val = _calculate_planet_value(planet.gravity, planet.temperature,
                                  planet.radiation, race.gravity_immune,
                                  race.gravity_min, race.gravity_max,
                                  race.temperature_immune, race.temperature_min,
                                  race.temperature_max, race.radiation_immune,
                                  race.radiation_min, race.radiation_max)

    return val


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
        self.gravity = 0
        self.temperature = 0
        self.radiation = 0

        # if the planet is visible, this value will be precalculated
        self.value = 0

        self.has_been_colonized = False
        self.planetary_defense = 0
        self.years_since = NeverSeenPlanet

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
