Stars Reborn — Design
=====================

The authoritative developer reference for the |project| project.

**Read this repository before writing engine or UI code.**

|original| (1995, Jeff Johnson & Jeff McBride) is a complex 4X strategy game
with many interlocking systems. Much of its behavior has been reverse-engineered
by the community over 30 years. This repository collects that knowledge,
validates it against the original executable, and defines how each system will
be implemented in the clone.

Research, tooling, and open questions live in ``stars-reborn-research``.
JSON Schema definitions live in ``stars-reborn-schemas``.

.. toctree::
   :maxdepth: 1
   :caption: Architecture

   architecture
   validation

.. toctree::
   :maxdepth: 2
   :caption: New Game Creation

   new_game/index

.. toctree::
   :maxdepth: 2
   :caption: Game Mechanics

   mechanics/index

.. toctree::
   :maxdepth: 2
   :caption: Schemas

   schemas/index

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/index
