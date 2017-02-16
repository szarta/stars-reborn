"""
    race.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from enumerations import ResearchCostOption
from enumerations import ResourceProductionParameter
from enumerations import FactoryProductionParameter
from enumerations import FactoryCostParameter
from enumerations import ColonistFactoryParameter
from enumerations import PrimaryRacialTrait
from enumerations import MineProductionParameter
from enumerations import MineCostParameter
from enumerations import ColonistMineParameter
from enumerations import GrowthRateParameter
from enumerations import BasePopulation
from enumerations import LesserRacialTrait
from enumerations import LeftoverPointsOption

from src.util import get_bounded_value

from universe import universe_is_tiny


class Race(object):
    def __init__(self):
        self.name = ""
        self.plural_name = ""
        self.description = ""

        self.primary_racial_trait = PrimaryRacialTrait.JackOfAllTrades
        self.lesser_racial_traits = []

        self.radiation_immune = False
        self.radiation_min = 0
        self.radiation_max = 0

        self.temperature_immune = False
        self.temperature_min = 0
        self.temperature_max = 0

        self.gravity_immune = False
        self.gravity_min = 0.0
        self.gravity_max = 0.0

        self._growth_rate = GrowthRateParameter.Minimum

        self._resource_production = ResourceProductionParameter.Minimum
        self._factory_production = FactoryProductionParameter.Minimum
        self._factory_cost = FactoryCostParameter.Minimum
        self._colonists_operate_factories = ColonistFactoryParameter.Minimum
        self._mine_production = MineProductionParameter.Minimum
        self._mine_cost = MineCostParameter.Minimum
        self._colonists_operate_mines = ColonistMineParameter.Minimum

        self.factory_cheap_germanium = False

        self.energy_cost = ResearchCostOption.Normal
        self.propulsion_cost = ResearchCostOption.Normal
        self.biotechnology_cost = ResearchCostOption.Normal
        self.electronics_cost = ResearchCostOption.Normal
        self.weapons_cost = ResearchCostOption.Normal
        self.construction_cost = ResearchCostOption.Normal
        self.expensive_tech_boost = False

        self.leftover_points = LeftoverPointsOption.SurfaceMinerals

        self.icon = 0

        self.advantage_points = 0
        self.recalculate_points()

    @property
    def resource_production(self):
        return self._resource_production

    @resource_production.setter
    def resource_production(self, value):
        val = int(value)
        assert(val % ResourceProductionParameter.Step == 0)

        min = ResourceProductionParameter.Minimum
        max = ResourceProductionParameter.Maximum
        self._resource_production = get_bounded_value(
            "resource_production", val, min, max)

    @property
    def factory_production(self):
        return self._factory_production

    @factory_production.setter
    def factory_production(self, value):
        val = int(value)

        min = FactoryProductionParameter.Minimum
        max = FactoryProductionParameter.Maximum
        self._factory_production = get_bounded_value(
            "factory_production", val, min, max)

    @property
    def factory_cost(self):
        return self._factory_cost

    @factory_cost.setter
    def factory_cost(self, value):
        val = int(value)

        min = FactoryCostParameter.Minimum
        max = FactoryCostParameter.Maximum
        self._factory_cost = get_bounded_value(
            "factory_cost", val, min, max)

    @property
    def colonists_operate_factories(self):
        return self._colonists_operate_factories

    @colonists_operate_factories.setter
    def colonists_operate_factories(self, value):
        val = int(value)

        min = ColonistFactoryParameter.Minimum
        max = ColonistFactoryParameter.Maximum
        self._colonists_operate_factories = get_bounded_value(
            "colonists_operate_factories", val, min, max)

    @property
    def mine_production(self):
        return self._mine_production

    @mine_production.setter
    def mine_production(self, value):
        val = int(value)

        min = MineProductionParameter.Minimum
        max = MineProductionParameter.Maximum
        self._mine_production = get_bounded_value(
            "mine_production", val, min, max)

    @property
    def mine_cost(self):
        return self._mine_cost

    @mine_cost.setter
    def mine_cost(self, value):
        val = int(value)

        min = MineCostParameter.Minimum
        max = MineCostParameter.Maximum
        self._mine_production = get_bounded_value(
            "mine_cost", val, min, max)

    @property
    def colonists_operate_mines(self):
        return self._colonists_operate_mines

    @colonists_operate_mines.setter
    def colonists_operate_mines(self, value):
        val = int(value)

        min = ColonistMineParameter.Minimum
        max = ColonistMineParameter.Maximum
        self._mine_production = get_bounded_value(
            "colonists_operate_mines", val, min, max)

    @property
    def growth_rate(self):
        return self._growth_rate

    @growth_rate.setter
    def growth_rate(self, value):
        val = int(value)

        min = GrowthRateParameter.Minimum
        max = GrowthRateParameter.Maximum
        self._mine_production = get_bounded_value(
            "growth_rate", val, min, max)

    def habitable_world_estimation(self):
        return 0.0

    def recalculate_points(self):
        points = 0

        points += calculate_prt_advantange_points(self.primary_racial_trait)

        for trait in self.lesser_racial_traits:
            points += calculate_lrt_advantage_points(trait)

        points += calculate_resource_production_advantage_points(
            self.resource_production)

        points += calculate_factory_production_advantage_points(
            self.factory_production)

        points += calculate_factory_cost_advantage_points(self.factory_cost)

        points += calculate_colonist_factory_advantage_points(
            self.colonists_operate_factories)

        points += calculate_mine_production_advantage_points(
            self.mine_production)

        points += calculate_mine_cost_advantage_points(self.mine_cost)
        points += calculate_colonist_mine_advantage_points(
            self.colonists_operate_mines)

        points += calculate_research_advantage_points(self.energy_cost)
        points += calculate_research_advantage_points(self.propulsion_cost)
        points += calculate_research_advantage_points(self.biotechnology_cost)
        points += calculate_research_advantage_points(self.electronics_cost)
        points += calculate_research_advantage_points(self.weapons_cost)
        points += calculate_research_advantage_points(self.construction_cost)
        points += calculate_growth_rate_advantage_points(self.growth_rate)

        points += calculate_habitat_advantage_points(
            self.radiation_immune, self.radiation_min, self.radiation_max,
            self.temperature_immune, self.temperature_min,
            self.temperature_max, self.gravity_immune, self.gravity_min,
            self.gravity_max)

        if(self.factory_cheap_germanium):
            points -= 58

        if(self.expensive_tech_boost):
            points += 60

        self.advantage_points = points


def calculate_prt_advantange_points(primary_racial_trait):
    prt = int(primary_racial_trait)
    advantage_point_table = [
        0, 25, -57, 36, 53, -12, -37, -28, -10, -27
    ]

    return advantage_point_table[prt]


def calculate_lrt_advantage_points(lesser_racial_trait):
    lrt = int(lesser_racial_trait)
    advantage_point_table = [
        53, -78, 80, -140, 85, -53, 95, -67, 60, 13, 23, -80, 10, -51
    ]

    return advantage_point_table[lrt]


def calculate_research_advantage_points(research_cost):
    rc = int(research_cost)
    advantage_point_table = [
        50, 0, -43
    ]

    return advantage_point_table[rc]


def calculate_colonist_mine_advantage_points(colonists):
    c = int(colonists)
    if c <= 10:
        return (13 * (10 - c))
    else:
        return (-12 * (c - 10))


def calculate_mine_cost_advantage_points(mine_cost):
    mc = int(mine_cost)
    if mc <= 2:
        return -190
    else:
        return (22 * (mc - 5))


def calculate_colonist_factory_advantage_points(factories):
    f = int(factories)
    assert(f >= ColonistFactoryParameter.Minimum)
    assert(f <= ColonistFactoryParameter.Maximum)

    return (-13 * (f - 10))


def calculate_factory_cost_advantage_points(factory_cost):
    fc = int(factory_cost)
    assert(fc >= FactoryCostParameter.Minimum)
    assert(fc <= FactoryCostParameter.Maximum)

    factory_cost_table = [
        0, 0, 0, 0, 0, -500, -320, -180, -80, -20
    ]

    if fc <= 9:
        return factory_cost_table[fc]
    else:
        return (18 * (fc - 10))


def calculate_resource_production_advantage_points(colonists_per_resource):
    cpr = int(colonists_per_resource)
    assert(cpr % 100 == 0)
    assert(cpr >= ResourceProductionParameter.Minimum)
    assert(cpr <= ResourceProductionParameter.Maximum)

    if cpr <= 700:
        result = -800
    elif cpr == 800:
        result = -420
    elif cpr == 900:
        result = -200
    else:
        result = int((0.4 * cpr) - 400)

    return result


def calculate_factory_production_advantage_points(factory_production):
    fp = int(factory_production)
    assert(fp >= FactoryProductionParameter.Minimum)
    assert(fp <= FactoryProductionParameter.Maximum)

    advantage_point_table = [
        0, 0, 0, 0, 0, 166, 133, 99, 66, 33, 0, -42, -84, -145, -207, -268
    ]

    return advantage_point_table[fp]


def calculate_mine_production_advantage_points(mine_production):
    mp = int(mine_production)
    assert(mp >= MineProductionParameter.Minimum)
    assert(mp <= MineProductionParameter.Maximum)

    if mp <= 10:
        return (33 * (10 - mp))
    else:
        return (-56 * (mp - 10))


def calculate_growth_rate_advantage_points(growth_rate):
    gr = int(growth_rate)
    assert(gr >= GrowthRateParameter.Minimum)
    assert(gr <= GrowthRateParameter.Maximum)

    advantage_points_table = [
        0, 7594, 6171, 4748, 3325, 1902, 1656, 1161, 565, 394, 274,
        228, 182, 136, 68, 0, -69, -137, -206, -274, -412
    ]

    return advantage_points_table[gr]


def calculate_habitat_advantage_points(radiation_immune, radiation_min,
                                       radiation_max, temperature_immune,
                                       temperature_min, temperature_max,
                                       gravity_immune, gravity_min,
                                       gravity_max):

    if temperature_immune and gravity_immune and radiation_immune:
        return -3925

    total_points = 0

    if ((temperature_immune and gravity_immune) or
       (temperature_immune and radiation_immune) or
       (gravity_immune and radiation_immune)):
        total_points -= 586

    # TODO: temperature calculation
    # TODO: gravity calculation
    # TODO: radiation calculation

    return total_points


def get_starting_population(race, universe):
    population = BasePopulation

    if (race.primary_racial_trait == PrimaryRacialTrait.InterstellarTraveler
       and universe_is_tiny(universe)):
        population -= 5000

    if LesserRacialTrait.LowStartingPopulation in race.lesser_racial_traits:
        population *= 0.7

    return population
