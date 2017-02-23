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
from enumerations import ResearchAreas

from src.data import Technologies


class Player(object):
    def __init__(self, id):
        self.race = None
        self.id = id
        self.cpu = False
        self.homeworld = 0

        self.energy_tech_level = 0
        self.energy_tech_progress = 0

        self.propulsion_tech_level = 0
        self.propulsion_tech_progress = 0

        self.biotechnology_tech_level = 0
        self.biotechnology_tech_progress = 0

        self.electronics_tech_level = 0
        self.electronics_tech_progress = 0

        self.weapons_tech_level = 0
        self.weapons_tech_progress = 0

        self.construction_tech_level = 0
        self.construction_tech_progress = 0

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

        for trait in self.race.lesser_racial_traits:
            self.discoverable_technologies.extend(
                list(LRT_Technologies[trait]))

        if LesserRacialTrait.NoRamscoopEngines in self.race.lesser_racial_traits:
            if LesserRacialTrait.ImprovedFuelEfficiency in self.race.lesser_racial_traits:
                self.discoverable_technologies.remove(TechnologyId.GalaxyScoop)
        else:
            self.discoverable_technologies.extend(list(RamScoopEngines))

        if not LesserRacialTrait.OnlyBasicRemoteMining in self.race.lesser_racial_traits:
            self.discoverable_technologies.extend(list(NormalRemoteMiners))

        if not (self.race.primary_racial_trait == PrimaryRacialTrait.AlternateReality or
                LesserRacialTrait.NoAdvancedScanners in self.race.lesser_racial_traits):
            self.discoverable_technologies.extend(list(AdvancedPlanetaryScanners))

        if(self.race.expensive_tech_boost):
            if(self.race.energy_cost == ResearchCostOption.Expensive):
                self.energy_tech_level = max(self.energy_tech_level, 3)
            if(self.race.propulsion_cost == ResearchCostOption.Expensive):
                self.propulsion_tech_level = max(self.propulsion_tech_level, 3)
            if(self.race.biotechnology_cost == ResearchCostOption.Expensive):
                self.biotechnology_tech_level = max(self.biotechnology_tech_level, 3)
            if(self.race.electronics_cost == ResearchCostOption.Expensive):
                self.electronics_tech_level = max(self.electronics_tech_level, 3)
            if(self.race.weapons_cost == ResearchCostOption.Expensive):
                self.weapons_tech_level = max(self.weapons_tech_level, 3)
            if(self.race.construction_cost == ResearchCostOption.Expensive):
                self.construction_tech_level = max(self.construction_tech_level, 3)

        if(self.race.primary_racial_trait == PrimaryRacialTrait.InterstellarTraveler):
            self.propulsion_tech_level = max(self.propulsion_tech_level, 5)
            self.construction_tech_level = max(self.construction_tech_level, 5)
        elif(self.race.primary_racial_trait == PrimaryRacialTrait.SpaceDemolition):
            self.propulsion_tech_level = max(self.propulsion_tech_level, 2)
            self.biotechnology_tech_level = max(self.biotechnology_tech_level, 2)
        elif(self.race.primary_racial_trait == PrimaryRacialTrait.WarMonger):
            self.propulsion_tech_level = max(self.propulsion_tech_level, 1)
            self.energy_tech_level = max(self.energy_tech_level, 1)
            self.weapons_tech_level = max(self.weapons_tech_level, 6)
        elif(self.race.primary_racial_trait == PrimaryRacialTrait.PacketPhysics):
            self.energy_tech_level = max(self.energy_tech_level, 4)
        elif(self.race.primary_racial_trait == PrimaryRacialTrait.JackOfAllTrades):
            self.energy_tech_level = max(self.energy_tech_level, 3)
            self.propulsion_tech_level = max(self.propulsion_tech_level, 3)
            self.biotechnology_tech_level = max(self.biotechnology_tech_level, 3)
            self.electronics_tech_level = max(self.electronics_tech_level, 3)
            self.weapons_tech_level = max(self.weapons_tech_level, 3)
            self.construction_tech_level = max(self.construction_tech_level, 3)
        elif(self.race.primary_racial_trait == PrimaryRacialTrait.ClaimAdjuster):
            self.biotechnology_tech_level = max(self.biotechnology_tech_level, 6)

        if(LesserRacialTrait.ImprovedFuelEfficiency in self.race.lesser_racial_traits or
           LesserRacialTrait.CheapEngines in self.race.lesser_racial_traits):
            self.propulsion_tech_level += 1

        other_techs = self.find_new_technologies()
        for t in other_techs:
            self.available_technologies.append(t)
            self.discoverable_technologies.remove(t)

    def total_tech_levels(self):
        return (self.energy_tech_level + self.propulsion_tech_level +
                self.biotechnology_tech_level + self.electronics_tech_level +
                self.weapons_tech_level + self.construction_tech_level)

    def find_new_technologies(self):
        new_technologies = []

        for tech_id in self.discoverable_technologies:
            tech = Technologies[tech_id]
            if player_meets_tech_requirements(self, tech.requirements):
                new_technologies.append(tech_id)

        return new_technologies


class CPU(Player):
    def __init__(self, id, difficulty_level, strategy):
        Player.__init__(self, id)
        self.difficulty_level = difficulty_level
        self.strategy = strategy
        self.cpu = True


def player_meets_tech_requirements(player, requirements):
    """
    Returns True if the given player has met the given research requirements.
    """
    p = player
    r = requirements
    ra = ResearchAreas

    if (p.energy_tech_level >= r[ra.Energy] and
       p.weapons_tech_level >= r[ra.Weapons] and
       p.propulsion_tech_level >= r[ra.Propulsion] and
       p.construction_tech_level >= r[ra.Construction] and
       p.electronics_tech_level >= r[ra.Electronics] and
       p.biotechnology_tech_level >= r[ra.Biotechnology]):
        return True
    else:
        return False


def total_cost_to_requirement_level(player, requirements, slow_tech_advance):
    """
    Calculates the total cost (could be 0) for the given player to reach the
    given requirement level.
    """
    if player_meets_tech_requirements(player, requirements):
        return 0

    deficits = []
    levels = [
        player.energy_tech_level,
        player.weapons_tech_level,
        player.propulsion_tech_level,
        player.construction_tech_level,
        player.electronics_tech_level,
        player.biotechnology_tech_level
    ]

    cost_percents = [
        player.race.energy_cost,
        player.race.weapons_cost,
        player.race.propulsion_cost,
        player.race.construction_cost,
        player.race.electronics_cost,
        player.race.biotechnology_cost
    ]

    for i in xrange(len(cost_percents)):
        cost_enum = cost_percents[i]
        if cost_enum == ResearchCostOption.Expensive:
            cost_percents[i] = 175
        elif cost_enum == ResearchCostOption.Normal:
            cost_percents[i] = 100
        else:
            cost_percents[i] = 50

    for i in xrange(len(levels)):
        plevel = levels[i]
        rlevel = requirements[i]
        if plevel >= rlevel:
            deficits.append(0)
        else:
            deficits.append(rlevel - plevel)

    running_cost = 0
    current_total_levels = player.total_tech_levels()
    for i in xrange(len(deficits)):
        deficit = deficits[i]
        if deficit != 0:
            for i in xrange(deficit):
                running_cost += total_cost_to_next_level(
                    levels[i], current_total_levels, cost_percents[i], slow_tech_advance)
                levels[i] += 1
                current_total_levels += 1

    return int(running_cost)


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
