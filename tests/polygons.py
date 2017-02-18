#!/usr/bin/python
"""
    polygons.py

    :author: Brandon Arrendondo
    :license: MIT
"""
import sys
import argparse
import logging

from src.polygon import Polygon

__version__ = "%(prog)s 1.0.0 (Rel: 18 Feb 2017)"
default_log_format = "%(filename)s:%(levelname)s:%(asctime)s] %(message)s"


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    parser.add_argument("--version", action="version", version=__version__,
                        help="show the version and exit")

    args = parser.parse_args()

    logging.basicConfig(format=default_log_format)
    if(args.verbose):
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    p = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
    logging.info(p.area())
    logging.info(p.bounds())

    p = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
    logging.info(p.area())
    logging.info(p.bounds())


if __name__ == "__main__":
    main(sys.argv[1:])
