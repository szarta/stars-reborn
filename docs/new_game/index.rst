New Game Creation
=================

Everything required before turn 1 begins.  This section documents the full
pipeline from host configuration through to the first per-player turn files
being available from the engine.  It is the primary reference for implementing
the engine's ``POST /games`` endpoint and the UI's new-game wizard.

Pipeline
--------

.. list-table::
   :header-rows: 1
   :widths: 5 35 40 20

   * - Phase
     - What the host configures
     - Data model / output
     - Document
   * - 1
     - Player slots: names, human vs. AI, difficulty; race selection or design
     - :doc:`race.json <../schemas/index>` per slot
     - :doc:`race_design_workflow`
   * - 2
     - Universe size, density, player positions, game options
     - ``universe_params`` block in create-game request
     - :doc:`universe_parameters`
   * - 3
     - Victory conditions and thresholds
     - ``victory_conditions`` block in create-game request
     - :doc:`victory_parameters`
   * - 4
     - (Phases 1–3 assembled) → ``POST /games``
     - ``request-create-new-game.json``
     - :doc:`new_game_request`
   * - 5
     - Engine generates universe, assigns homeworlds, creates starting fleets
     - Persisted game state; turn 0 → turn 1
     - :doc:`initial_state`
   * - 6
     - Engine exposes per-player turn and universe views
     - ``GET /games/{id}/turns/1/players/{pid}``
     - :doc:`turn1_api`

Design Constraints
------------------

- **Seed reproducibility.** Providing an explicit ``random_seed`` in the
  creation request must produce an identical universe.  This is required for
  integration tests that compare our output against oracle games.

- **At least one human player.** The engine may accept an all-AI game (useful
  for testing) but this should be clearly flagged in the request schema.

- **Race file isolation.** A race definition submitted with the creation
  request is a snapshot; subsequent changes to a saved race file do not affect
  a game already created.

- **Original race import.** The UI must be able to import a ``.r`` file from
  the original |original| and convert it to a ``race.json`` for submission.
  See :doc:`race_file_format`.

.. toctree::
   :maxdepth: 1
   :hidden:

   race_design_workflow
   race_file_format
   universe_parameters
   victory_parameters
   new_game_request
   initial_state
   turn1_api
