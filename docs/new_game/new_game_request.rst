New Game API Request
====================

``POST /games`` is the single endpoint that creates a game.  The engine
validates the full request, generates the universe, and returns a game ID and
seed.

The JSON body must conform to ``request-create-new-game.json`` in
``stars-reborn-schemas``.

Request Schema
--------------

Top-level fields:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Field
     - Type
     - Description
   * - ``format_version``
     - integer
     - Schema version.  Clients must match the version reported by
       ``GET /model/version``.
   * - ``game_name``
     - string
     - Optional display name for the game.
   * - ``universe_params``
     - object
     - Universe generation parameters.  See :doc:`universe_parameters`.
   * - ``victory_conditions``
     - object
     - Win conditions and thresholds.  See :doc:`victory_parameters`.
   * - ``players``
     - array of player-slot objects
     - One entry per player slot (2–16).  See `Player Slot Object`_ below.

Player Slot Object
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Field
     - Type
     - Description
   * - ``slot_index``
     - integer
     - Zero-based slot number.  Must be unique and contiguous from 0.
   * - ``player_type``
     - string enum
     - ``"human"`` or ``"ai"``
   * - ``display_name``
     - string
     - Player's name as shown in the score sheet.
   * - ``ai_difficulty``
     - integer (1–5)
     - Required when ``player_type`` is ``"ai"``.  1 = hardest, 5 = easiest.
       Absent (or null) for human slots.
   * - ``race``
     - object
     - Inline ``race.json`` object.  The submitted snapshot is the definitive
       race for this game; changes to the saved file have no effect.

Response Schema
---------------

On success (``201 Created``) the engine returns a body conforming to
``response-create-new-game.json``.

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Field
     - Type
     - Description
   * - ``game_id``
     - string (UUID)
     - Unique identifier used in all subsequent game API calls.
   * - ``random_seed``
     - integer
     - The seed used for generation.  Equal to ``universe_params.random_seed``
       if that was provided; otherwise the engine-generated value.
   * - ``player_tokens``
     - array of objects
     - One entry per human slot.  Each has ``slot_index`` and ``token``
       (opaque string).  Used as ``Authorization: Bearer <token>`` for all
       requests against this game.  Never issued for AI slots.
   * - ``planet_count``
     - integer
     - How many planets were generated (after applying any density caps).
   * - ``turn``
     - integer
     - Always ``1``.  The first turn file is immediately available.

Error Responses
---------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Status
     - When
   * - ``400 Bad Request``
     - JSON is malformed, schema validation fails, or a race is invalid
       (illegal PRT/LRT combination, advantage points out of budget, bad
       hab ranges).
   * - ``409 Conflict``
     - A game with the same ``game_name`` already exists (if names are
       enforced as unique — TBD).
   * - ``422 Unprocessable Entity``
     - Request is structurally valid but logically invalid (e.g., fewer
       than 2 player slots, ``tech_fields`` out of range).

The error body follows a standard envelope:

.. code-block:: json

   {
     "error": "RACE_INVALID",
     "message": "Slot 2: LRT 'ARM' requires PRT 'JOAT' or remote mining capability",
     "field": "players[2].race.lrts"
   }

Complete Request Example
------------------------

.. code-block:: json

   {
     "format_version": 1,
     "game_name": "Friday Night Smash",
     "universe_params": {
       "size":                            "medium",
       "density":                         "normal",
       "player_positions":                "distant",
       "beginner_max_minerals":           false,
       "accelerated_bbs":                 false,
       "slower_tech_advances":            false,
       "no_random_events":                false,
       "computer_players_form_alliances": false,
       "public_player_scores":            false,
       "galaxy_clumping":                 false,
       "random_seed":                     null
     },
     "victory_conditions": {
       "own_planets":         true,
       "own_planets_pct":     30,
       "tech_levels":         true,
       "tech_level":          22,
       "tech_fields":         6,
       "exceed_score":        true,
       "score_threshold":     11000,
       "score_lead":          true,
       "score_lead_pct":      100,
       "produce_resources":   true,
       "resources_threshold": 1000,
       "own_starbases":       true,
       "starbases_threshold": 100,
       "highest_score":       true,
       "highest_score_year":  900
     },
     "players": [
       {
         "slot_index":    0,
         "player_type":   "human",
         "display_name":  "Alice",
         "ai_difficulty": null,
         "race": { "...": "full race.json object" }
       },
       {
         "slot_index":    1,
         "player_type":   "ai",
         "display_name":  "Rabbitoid",
         "ai_difficulty": 3,
         "race": { "...": "full race.json object" }
       }
     ]
   }

Validation Order
----------------

The engine validates in this order so that the most actionable error is
returned first:

1. ``format_version`` matches engine's current schema version.
2. Top-level structural conformance (JSON Schema).
3. ``universe_params`` values are in valid ranges.
4. ``victory_conditions`` values are in valid ranges and at least one is
   enabled.
5. Player slot count is between 2 and 16; slot indices are contiguous from 0.
6. Each race passes full race validation (schema → rules → advantage points).

.. todo::

   Decide whether ``game_name`` uniqueness is enforced.  Simplest: no
   enforcement (games are identified by UUID only).

.. todo::

   Decide whether ``POST /games`` blocks until universe generation completes
   or returns 202 and the client polls.  Generation of a Huge/Packed universe
   with 16 AI players may be non-trivial.  See the open question in
   :doc:`../architecture`.
