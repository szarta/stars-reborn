Data Files
==========

Compiled Data Files
-------------------

These files in ``resources/data/`` are generated from ``stars_reborn/data/factory.py``
and should not be edited directly:

``technologies.dat``
    Gzip-encoded jsonpickle of the complete technology tree. Built by
    ``factory.py::build_technology_data()``. Contains all Technology subclass instances
    keyed by ``TechnologyId``.

``tutorial.dat``
    Gzip-encoded jsonpickle of a pre-built tutorial game state (Turn object). Built by
    ``factory.py::build_tutorial_game()``.

``ai_races.dat``
    Pre-defined computer opponent races. Built by ``factory.py::build_ai_races()``.

Regenerating Data Files
-----------------------

After changing factory.py (e.g., correcting a tech stat), regenerate all data files::

    python -c "from stars_reborn.data.factory import regenerate_data_files; regenerate_data_files()"

Or run the factory module directly::

    python -m stars_reborn.data.factory

String Files
------------

``resources/strings/english_strings.json``
    Game UI text, indexed by integer key (matching ``GameStrings`` enum constants).
    To add strings, append to this file and add the key to ``GameStrings`` in
    ``stars_reborn/engine/enumerations.py``.

Race Files
----------

``resources/race/``
    Pre-defined player race definitions in JSON format. These are offered as starting
    points in the Race Designer dialog. The format mirrors the ``Race`` model object.

Planet Name Lists
-----------------

``resources/data/names.txt`` (to be created)
    One name per line. Used by universe generation to assign planet names.
    Source: ``stars-research/planet_name_generation/name_lists/``.
