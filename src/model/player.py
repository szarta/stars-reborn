"""
    player.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from enumerations import TechnologyLevelBaseCosts
from enumerations import ResearchCostOption
from enumerations import PrimaryRacialTrait
from enumerations import LesserRacialTrait


class Player(object):
    def __init__(self, id, race):
        self.race = race
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

    def apply_trait_adjustments(self):
        self.adjust_starbase_prototypes_for_racial_traits()
        self.adjust_ship_prototypes_for_racial_traits()
        self.adjust_technology_levels_for_racial_traits()

    def adjust_starbase_prototypes_for_racial_traits(self):
        print "adjust_starbase_prototypes_for_racial_traits"

    def adjust_ship_prototypes_for_racial_traits(self):
        print "adjust_ship_prototypes_for_racial_traits"

    def get_normal_visibility_regions(self):
        return []

    def get_penetrating_visibility_regions(self):
        return []

    def adjust_technology_levels_for_racial_traits(self):

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

    def total_tech_levels(self):

        return (self.energy_tech_level + self.propulsion_tech_level +
                self.biotechnology_tech_level + self.electronics_tech_level +
                self.weapons_tech_level + self.construction_tech_level)


class CPU(Player):
    def __init__(self, id, race, difficulty_level, strategy):
        Player.__init__(self, id, race)
        self.difficulty_level = difficulty_level
        self.strategy = strategy
        self.cpu = True


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
