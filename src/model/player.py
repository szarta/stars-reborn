"""
    player.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from enumerations import TechnologyLevelBaseCosts
from enumerations import ResearchCostOption
from enumerations import PrimaryRacialTrait
from enumerations import LesserRacialTrait
from enumerations import InitialTechnologies
from enumerations import BaseDiscoverableTechnologies
from enumerations import PRT_Technologies
from enumerations import LRT_Technologies
from enumerations import TechnologyId
from enumerations import RamScoopEngines
from enumerations import NormalRemoteMiners
from enumerations import AdvancedPlanetaryScanners
from enumerations import AdvancedShipScanners
from enumerations import ResearchAreas

from src.data import Technologies


class Player(object):
    def __init__(self, id):
        self.race = None
        self.id = id
        self.cpu = False
        self.homeworld = 0

        self.current_research_field = 0
        self.next_research_field = 0
        self.research_budget = 15

        self.tech_level = [0, 0, 0, 0, 0, 0]
        self.research_progress = [0, 0, 0, 0, 0, 0]

        self.constructed_starbase_designs = []
        self.constructed_ship_designs = []

        self.starbase_prototypes = []
        self.ship_prototypes = []
        self.available_technologies = []
        self.discoverable_technologies = []

    def apply_trait_adjustments(self):
        self.adjust_starbase_prototypes_for_racial_traits()
        self.adjust_ship_prototypes_for_racial_traits()
        self.adjust_technology_for_racial_traits()

    def meets_tech_requirements(self, requirements):
        assert (len(requirements) == len(self.tech_level))

        for i in xrange(len(self.tech_level)):
            req = requirements[i]
            current_level = self.tech_level[i]

            if current_level < req:
                return False

        return True

    def get_cost_multipliers(self):
        cost_percents = [
            self.race.energy_cost,
            self.race.weapons_cost,
            self.race.propulsion_cost,
            self.race.construction_cost,
            self.race.electronics_cost,
            self.race.biotechnology_cost
        ]

        for i in xrange(len(cost_percents)):
            cost_enum = cost_percents[i]
            if cost_enum == ResearchCostOption.Expensive:
                cost_percents[i] = 175
            elif cost_enum == ResearchCostOption.Normal:
                cost_percents[i] = 100
            else:
                cost_percents[i] = 50

        return cost_percents

    def adjust_starbase_prototypes_for_racial_traits(self):
        print "adjust_starbase_prototypes_for_racial_traits"

    def adjust_ship_prototypes_for_racial_traits(self):
        print "adjust_ship_prototypes_for_racial_traits"

    def get_normal_visibility_regions(self):
        return []

    def get_penetrating_visibility_regions(self):
        return []

    def adjust_technology_for_racial_traits(self):
        self.available_technologies = list(InitialTechnologies)
        self.discoverable_technologies = list(BaseDiscoverableTechnologies)
        self.discoverable_technologies.extend(
            list(PRT_Technologies[self.race.primary_racial_trait]))

        prt = self.race.primary_racial_trait
        lrts = self.race.lesser_racial_traits

        for trait in lrts:
            self.discoverable_technologies.extend(
                list(LRT_Technologies[trait]))

        if LesserRacialTrait.NoRamscoopEngines in lrts:
            if LesserRacialTrait.ImprovedFuelEfficiency in lrts:
                self.discoverable_technologies.remove(TechnologyId.GalaxyScoop)
        else:
            self.discoverable_technologies.extend(list(RamScoopEngines))

        if not LesserRacialTrait.OnlyBasicRemoteMining in lrts:
            self.discoverable_technologies.extend(list(NormalRemoteMiners))

        if not (prt == PrimaryRacialTrait.AlternateReality or
                LesserRacialTrait.NoAdvancedScanners in lrts):
            self.discoverable_technologies.extend(
                list(AdvancedPlanetaryScanners))

        if LesserRacialTrait.NoAdvancedScanners not in lrts:
            self.discoverable_technologies.extend(list(AdvancedShipScanners))

        if(self.race.expensive_tech_boost):
            cost_percents = [
                self.race.energy_cost,
                self.race.weapons_cost,
                self.race.propulsion_cost,
                self.race.construction_cost,
                self.race.electronics_cost,
                self.race.biotechnology_cost
            ]

            for i in xrange(len(cost_percents)):
                if cost_percents[i] == ResearchCostOption.Expensive:
                    self.tech_level[i] = max(self.tech_level[i], 3)

        if(prt == PrimaryRacialTrait.InterstellarTraveler):
            self.tech_level[ResearchAreas.Propulsion] = max(
                self.tech_level[ResearchAreas.Propulsion], 5)

            self.tech_level[ResearchAreas.Construction] = max(
                self.tech_level[ResearchAreas.Construction], 5)

        elif(prt == PrimaryRacialTrait.SpaceDemolition):
            self.tech_level[ResearchAreas.Propulsion] = max(
                self.tech_level[ResearchAreas.Propulsion], 2)

            self.tech_level[ResearchAreas.Biotechnology] = max(
                self.tech_level[ResearchAreas.Biotechnology], 2)

        elif(prt == PrimaryRacialTrait.WarMonger):
            self.tech_level[ResearchAreas.Propulsion] = max(
                self.tech_level[ResearchAreas.Propulsion], 1)

            self.tech_level[ResearchAreas.Energy] = max(
                self.tech_level[ResearchAreas.Energy], 1)

            self.tech_level[ResearchAreas.Weapons] = max(
                self.tech_level[ResearchAreas.Weapons], 6)

        elif(prt == PrimaryRacialTrait.PacketPhysics):
            self.tech_level[ResearchAreas.Energy] = max(
                self.tech_level[ResearchAreas.Energy], 4)

        elif(prt == PrimaryRacialTrait.JackOfAllTrades):
            for i in xrange(ResearchAreas.Total):
                self.tech_level[i] = max(self.tech_level[i], 3)

        elif(prt == PrimaryRacialTrait.ClaimAdjuster):
            self.tech_level[ResearchAreas.Biotechnology] = max(
                self.tech_level[ResearchAreas.Biotechnology], 6)

        if ((LesserRacialTrait.ImprovedFuelEfficiency in lrts) or
           (LesserRacialTrait.CheapEngines in lrts)):
            self.tech_level[ResearchAreas.Propulsion] += 1

        other_techs = self.find_new_technologies()
        for t in other_techs:
            self.available_technologies.append(t)
            self.discoverable_technologies.remove(t)

    def find_new_technologies(self):
        new_technologies = []

        for tech_id in self.discoverable_technologies:
            tech = Technologies[tech_id]
            if self.meets_tech_requirements(tech.requirements):
                new_technologies.append(tech_id)

        return new_technologies


class CPU(Player):
    def __init__(self, id, difficulty_level, strategy):
        Player.__init__(self, id)
        self.difficulty_level = difficulty_level
        self.strategy = strategy
        self.cpu = True


def total_cost_to_requirement_level(player, requirements, slow_tech_advance):
    """
    Calculates the total cost (could be 0) for the given player to reach the
    given requirement level.
    """
    if player.meets_tech_requirements(requirements):
        return 0

    deficits = []
    levels = list(player.tech_level)
    cost_percents = player.get_cost_multipliers()

    for i in xrange(len(levels)):
        plevel = levels[i]
        rlevel = requirements[i]
        if plevel >= rlevel:
            deficits.append(0)
        else:
            deficits.append(rlevel - plevel)

    running_cost = 0
    current_total_levels = sum(levels)
    for i in xrange(len(deficits)):
        deficit = deficits[i]
        if deficit != 0:
            for j in xrange(deficit):
                running_cost += total_cost_to_next_level(
                    levels[i], current_total_levels, cost_percents[i],
                    slow_tech_advance)
                levels[i] += 1
                current_total_levels += 1

    return int(running_cost)


def player_cost_to_next_level(player, research_area, slow_tech_advance):
    """
    Calculates the cost in resources for the given player to achieve the next
    level in the given research category.
    """
    current_level = player.tech_level[research_area]
    current_progress = player.research_progress[research_area]
    cost_percents = player.get_cost_multipliers()
    cost_percent_for_area = cost_percents[research_area]

    total_cost = total_cost_to_next_level(
        current_level, sum(player.tech_level), cost_percent_for_area,
        slow_tech_advance)

    return int(total_cost - current_progress)


def total_cost_to_next_level(current_level, total_tech_levels, cost_percent,
                             slow_tech_advance):
    """
    Calculate the total cost for a technology to get to the next level.

    The base cost is provided in a table.

    The base cost is modified by 3 factors:

        slow_tech_advance - boolean - whether game parameter was selected to
                            slow the tech advances

        tech_levels - the number of total tech levels attained so far
        cost_percent - the cost selected in race edit for the technology

    total = (base + (tech_levels * 10)) * cost_percent

    Double the total if slow_tech_advance is True.

    Based on algorithm from:
    http://wiki.starsautohost.org/wiki/Guts_of_research_costs

    Credit to S.B. Posey's Spreadsheet used to double-check the numbers.
    """
    cost = (float((TechnologyLevelBaseCosts[current_level + 1]) +
            float(total_tech_levels) * 10.0) *
            (float(cost_percent) / 100.0))

    if(slow_tech_advance):
        cost *= 2

    return cost
