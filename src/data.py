"""
    data.py

    The loaders and cont

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
