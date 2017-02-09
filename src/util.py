"""
    utils.py

    Helper functions.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import logging


def get_bounded_value(param_name, val, min, max):
    if val < min:
        logging.debug("Bounded val {0}: {1} is < {2}.  Choosing {2}.".format(
            param_name, val, min))
        return min
    elif val > max:
        logging.debug("Bounded val {0}: {1} is > {2}.  Choosing {2}.".format(
            param_name, val, max))
        return max
    else:
        return val
