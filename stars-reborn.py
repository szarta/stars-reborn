#!/usr/bin/python
"""
    stars-reborn.py

    :author: Brandon Arrendondo
    :license: MIT
"""
import sys
import argparse
import logging

from PySide.QtGui import QApplication
from src._version import __version__
from src.data import load_language_map
from src.data import load_technologies
from src.ui import intro

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
    load_technologies("resources/data/technologies.dat")

    app = QApplication(sys.argv)
    ex = intro.IntroUI()
    ex.show()

    # Qt application main loop
    app.exec_()
    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
