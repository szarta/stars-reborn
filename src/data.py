"""
    data.py

    Contains and owns the loading and in-memory storage of all of the
    pre-defined game data.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import json
import jsonpickle
import gzip

Technologies = {}
Language_Map = {}


def load_language_map(filepath):
    f = open(filepath, "r")
    Language_Map.update(json.load(f))
    f.close()


def load_technologies(filepath):
    f = gzip.open(filepath, "rb")
    contents = f.read()
    f.close()
    Technologies.update(jsonpickle.decode(contents, keys=True))


def load_tutorial_game(tutorial_filepath):
    f = gzip.open(tutorial_filepath, "rb")
    contents = f.read()
    f.close()

    game = jsonpickle.decode(contents, keys=True)
    return game
