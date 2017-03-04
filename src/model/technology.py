"""
    technology.py

    This module contains all of the technology classes and helpers.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from enumerations import BombType
from enumerations import MineType
from enumerations import ResearchAreas

from src.data import Technologies


class ShipDesign(object):
    def __init__(self, name, base_hull_id, tech):
        self.name = name
        self.base_hull_id = base_hull_id
        self.tech = dict(tech)


class Technology(object):
    def __init__(self, requirements, cost):
        self.requirements = list(requirements)
        self.cost = list(cost)


class Part(Technology):
    def __init__(self, requirements, cost, mass):
        Technology.__init__(self, requirements, cost)

        self.mass = mass


class PlanetaryScanner(Technology):
    def __init__(self, requirements, cost, basic_range, penetrating_range):
        Technology.__init__(self, requirements, cost)

        self.basic_range = basic_range
        self.penetrating_range = penetrating_range


class PlanetaryDefense(Technology):
    """
    Planetary defense calculations courtesy of:

    http://wiki.starsautohost.org/wiki/Guts_of_bombing
    Author:  Leonard Dickens
    Date:  1998/07/17
    Forums:  rec.games.computer.stars
    """
    def __init__(self, requirements, cost, base_coverage):
        Technology.__init__(self, requirements, cost)

        self.base_coverage = base_coverage

    def colonist_protection(self, number_of_defenses, bomb_type):
        p = 0

        if bomb_type == BombType.Normal:
            p = 1.0 - ((1.0 - self.base_coverage) ** number_of_defenses)
        elif bomb_type == BombType.Smart:
            p = 1.0 - ((1.0 - (self.base_coverage)/2.0) ** number_of_defenses)

        return p

    def building_protection(self, number_of_defenses, bomb_type):
        return (self.colonist_protection(number_of_defenses, bomb_type) * 0.5)

    def invasion_protection(self, number_of_defenses, bomb_type):
        return (self.colonist_protection(number_of_defenses, bomb_type) * 0.75)


class Terraforming(Technology):
    def __init__(self, requirements, cost, gravity, temperature, radiation):
        Technology.__init__(self, requirements, cost)

        self.gravity = gravity
        self.temperature = temperature
        self.radiation = radiation


class Armor(Part):
    def __init__(self, requirements, cost, mass, armor_value):
        Part.__init__(self, requirements, cost, mass)

        self.armor_value = armor_value


class Shield(Part):
    def __init__(self, requirements, cost, mass, shield_value):
        Part.__init__(self, requirements, cost, mass)

        self.shield_value = shield_value


class MineLayer(Part):
    def __init__(self, requirements, cost, mass, mines_per_year, mine_type):
        Part.__init__(self, requirements, cost, mass)

        self.mines_per_year = mines_per_year
        self.mine_type = mine_type

        if(self.mine_type == MineType.Normal):
            self.min_safe_warp = 4
            self.hit_chance_per_ly = 0.3
            self.dmg_ship_no_ram_scoop = 100
            self.dmg_ship_ram_scoop = 125
            self.min_dmg_fleet_no_ram_scoop = 500
            self.min_dmg_fleet_ram_scoop = 600
        elif(self.mine_type == MineType.Heavy):
            self.min_safe_warp = 6
            self.hit_chance_per_ly = 1.0
            self.dmg_ship_no_ram_scoop = 500
            self.dmg_ship_ram_scoop = 600
            self.min_dmg_fleet_no_ram_scoop = 2000
            self.min_dmg_fleet_ram_scoop = 2500
        elif(self.mine_type == MineType.Speed):
            self.min_safe_warp = 5
            self.hit_chance_per_ly = 3.5
            self.dmg_ship_no_ram_scoop = 0
            self.dmg_ship_ram_scoop = 0
            self.min_dmg_fleet_no_ram_scoop = 0
            self.min_dmg_fleet_ram_scoop = 0


class Scanner(Part):
    def __init__(self, requirements, cost, mass, basic_range,
                 penetrating_range):
        Part.__init__(self, requirements, cost, mass)

        self.basic_range = basic_range
        self.penetrating_range = penetrating_range


class Mechanical(Part):
    def __init__(self, requirements, cost, mass):
        Part.__init__(self, requirements, cost, mass)


class Electrical(Part):
    def __init__(self, requirements, cost, mass):
        Part.__init__(self, requirements, cost, mass)


class MiningRobot(Part):
    def __init__(self, requirements, cost, mass, mining_value):
        Part.__init__(self, requirements, cost, mass)

        self.mining_value = mining_value


class Engine(Part):
    """
        Fuel gain table courtesy Posey's spreadsheet:

            http://wiki.starsautohost.org/files/posey.zip

        The matrix is the amount gained if the engine has free Warp X,
        if ship travels completely at Warp Speed Y
    """
    Fuel_Gain_Matrix = {
        1: [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        4: [0, 10, 24, 27, 16, 0, 0, 0, 0, 0],
        5: [0, 10, 40, 54, 48, 25, 0, 0, 0, 0],
        6: [0, 10, 40, 90, 96, 75, 36, 0, 0, 0],
        7: [0, 10, 40, 90, 160, 150, 108, 49, 0, 0],
        8: [0, 10, 40, 90, 160, 250, 216, 147, 64, 0],
        9: [0, 10, 40, 90, 160, 250, 360, 294, 192, 81]
    }

    def __init__(self, requirements, cost, mass, fuel_usage_table,
                 battle_speed, warp10_travel):
        Part.__init__(self, requirements, cost, mass)

        self.fuel_usage_table = list(fuel_usage_table)
        self.battle_speed = battle_speed
        self.warp10_travel = warp10_travel

        self.last_free_warp = calculate_last_free_warp(fuel_usage_table)


def calculate_last_free_warp(fuel_usage_table):
    previous_cost = 1
    for i in xrange(1, len(fuel_usage_table)):
        cost = fuel_usage_table[i]
        if cost != 0:
            if previous_cost == 0:
                return i - 1

        previous_cost = cost
    return 10


class Bomb(Part):
    def __init__(self, requirements, cost, mass, colonist_kill_percent,
                 minimum_colonists_killed, buildings_destroyed, smart):
        Part.__init__(self, requirements, cost, mass)

        self.colonist_kill_percent = colonist_kill_percent
        self.minimum_colonists_killed = minimum_colonists_killed
        self.buildings_destroyed = buildings_destroyed
        self.smart = smart


class BeamWeapon(Part):
    def __init__(self, requirements, cost, mass, power, range, initiative,
                 spread=False, shields_only=False):
        Part.__init__(self, requirements, cost, mass)

        self.power = power
        self.range = range
        self.initiative = initiative
        self.spread = spread
        self.shields_only = shields_only


class Torpedo(Part):
    def __init__(self, requirements, cost, mass, power, range, initiative,
                 accuracy):
        Part.__init__(self, requirements, cost, mass)
        self.power = power
        self.range = range
        self.initiative = initiative
        self.accuracy = accuracy


class Stargate(Technology):
    def __init__(self, requirements, cost, safe_mass, safe_range):
        Technology.__init__(self, requirements, cost)

        self.safe_mass = safe_mass
        self.safe_range = safe_range


class MassDriver(Technology):
    def __init__(self, requirements, cost, warp):
        Technology.__init__(self, requirements, cost)

        self.warp = warp


class Hull(Technology):
    def __init__(self, requirements, cost, tech_slots, armor_strength,
                 initiative):
        Technology.__init__(self, requirements, cost)
        self.armor_strength = armor_strength
        self.initiative = initiative
        self.tech_slots = dict(tech_slots)


class ShipHull(Hull):
    def __init__(self, requirements, cost, tech_slots, armor_strength,
                 initiative, mass, fuel_capacity, cargo_capacity):
        Hull.__init__(self, requirements, cost, tech_slots, armor_strength,
                      initiative)
        self.mass = mass
        self.fuel_capacity = fuel_capacity
        self.cargo_capacity = cargo_capacity


class StarbaseHull(Hull):
    def __init__(self, requirements, cost, tech_slots, armor_strength,
                 initiative, dock_capacity):
        Hull.__init__(self, requirements, cost, tech_slots, armor_strength,
                      initiative)

        self.dock_capacity = dock_capacity


def tech_requirements_met(tech, tech_levels):
    assert(len(tech_levels) == ResearchAreas.Total)

    for i in xrange(len(tech.requirements)):
        req = tech.requirements[i]
        current_level = tech_levels[i]

        if current_level < req:
            return False

    return True


def tech_is_bleeding_edge(tech, tech_levels, bleeding_edge=False):
    """
    Returns if the given technology is currently bleeding edge.
    Obviously if bleeding edge is not selected, it will not be.

    Notably the starting technologies (those with no requirements) are not
    subject to the bleeding edge technology restriction.

    Also, technically, technologies which have not been researched yet are not
    bleeding edge.
    """
    if not bleeding_edge:
        return False

    assert(len(tech_levels) == ResearchAreas.Total)

    if(sum(tech.requirements) == 0):
        return False

    if not tech_requirements_met(tech, tech_levels):
        return False

    overlevel_arr = []
    for i in xrange(len(tech.requirements)):
        req = tech.requirements[i]
        current_level = tech_levels[i]
        if req != 0:
            if current_level >= req:
                overlevel_arr.append(current_level - req)

    if len(overlevel_arr) == 0:
        overlevel = 0
    else:
        overlevel = min(overlevel_arr)

    if overlevel == 0:
        return True
    else:
        return False


def calculate_next_n_techs(player, research_field, n, threshold):
    """
    Given the research field, determines the next N technologies (in order)
    that the given player could discover via researching solely that field.

    This is mostly used by the research window, in which the next 6 techs are
    selected, which is threshold 7?
    """
    current_levels = list(player.tech_level)
    ret_techs = []

    starting_level = current_levels[research_field]
    ending_level = starting_level + threshold

    for i in xrange(starting_level, ending_level + 1):
        current_levels[research_field] = i
        for tech_id in player.discoverable_technologies:
            tech = Technologies[tech_id]

            if tech_requirements_met(tech, current_levels):
                if tech_id not in ret_techs:
                    ret_techs.append(tech_id)
                    if len(ret_techs) >= n:
                        return ret_techs

    return ret_techs


def calculate_costs_after_miniaturization(tech, tech_levels,
                                          bleeding_edge=False):
    """
    Miniaturization is the cost reduction of older technologies.
    It occurs as 4% cost reduction for each level over the tech requirement
    level up to 75% total.

    If Bleeding Edge Technology is taken, it occurs as 5% cost reduction for
    each level, up to 80%, but the technology on the current level costs twice
    as much.

    Miniaturization affects mineral costs and resource costs.

    Miniaturization rounds to the nearest whole number.

    If there are multiple requirements, the overleveling is defined as the
    minimum level difference:  e.g. if requirement is Energy 5 and Propulsion
    6, and the player's current levels are Energy 6 and Propulsion 8, the
    overlevel is 1 (Energy) despite Propulsion being over by 2.

    If there are no requirements for a given tech, the original game treats the
    tech as having requirements 0 for all types.
    """
    assert(len(tech_levels) == ResearchAreas.Total)

    overlevel = 0
    if(sum(tech.requirements) == 0):
        overlevel_arr = []
        for i in xrange(len(tech.requirements)):
            req = tech.requirements[i]
            current_level = tech_levels[i]
            overlevel_arr.append(current_level - req)

        if len(overlevel_arr) == 0:
            overlevel = 0
        else:
            overlevel = min(overlevel_arr)
    else:
        overlevel_arr = []
        for i in xrange(len(tech.requirements)):
            req = tech.requirements[i]
            current_level = tech_levels[i]
            if req != 0:
                if current_level >= req:
                    overlevel_arr.append(current_level - req)

        if len(overlevel_arr) == 0:
            overlevel = 0
        else:
            overlevel = min(overlevel_arr)

    if overlevel == 0:
        if bleeding_edge:
            return [2 * x for x in tech.cost]
        else:
            return tech.cost
    else:
        if bleeding_edge:
            reduction = 100 - (overlevel * 5)
            if reduction < 20:
                reduction = 20

            actual_reduction = reduction / 100.0
            return [actual_reduction * x for x in tech.cost]

        else:
            reduction = 100 - (overlevel * 4)
            if reduction < 25:
                reduction = 25

            actual_reduction = reduction / 100.0
            return [int(round(actual_reduction * x)) for x in tech.cost]
