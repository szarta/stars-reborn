#!/usr/bin/python
"""
    build_data.py

    :author: Brandon Arrendondo
    :license: MIT
"""
import sys
import argparse
import logging
import jsonpickle
import gzip
import time

from src.factory import build_technology
from src.factory import build_tutorial_game
from src.factory import build_computer_races

from src.data import load_language_map

__version__ = "%(prog)s 1.0.0 (Rel: 09 Jan 2017)"
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

    load_language_map("resources/strings/english_strings.json")

    start_time = time.time()
    tech = build_technology()
    build_time = time.time() - start_time

    f = gzip.open("technologies.dat", "wb")
    f.write(jsonpickle.encode(tech, keys=True))
    f.close()

    start_time = time.time()
    f = gzip.open("technologies.dat", "rb")
    contents = f.read()
    f.close()
    new_tech = jsonpickle.decode(contents, keys=True)
    load_time = time.time() - start_time

    print "Build time {0!s}, Load time {1!s}".format(build_time, load_time)
    print "Built {0!s}, Loaded {1!s} technologies.".format(
        len(tech), len(new_tech))

    tutorial = build_tutorial_game()
    f = gzip.open("tutorial.dat", "wb")
    f.write(jsonpickle.encode(tutorial, keys=True))
    f.close()

    computer_races = build_computer_races()
    f = gzip.open("ai_races.dat", "wb")
    f.write(jsonpickle.encode(computer_races, keys=True))
    f.close()



if __name__ == "__main__":
    main(sys.argv[1:])
