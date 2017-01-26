"""
    player.py

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from enumerations import TechnologyLevelBaseCosts


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
