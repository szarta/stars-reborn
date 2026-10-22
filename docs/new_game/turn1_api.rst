Turn 1 API
==========

After ``POST /games`` succeeds, the turn 1 player files are immediately
available.  This document specifies the endpoints used to retrieve them and
the validation approach for comparing engine output against the original game.

Endpoints
---------

All endpoints are under the game created by ``POST /games``.

.. code-block:: text

    GET /games/{game_id}/turns/1/status
        → Per-slot submission status for year 1.  At game start all human
          slots are "pending" (no orders submitted) and all AI slots are
          "ready" (engine will generate orders).

    GET /games/{game_id}/turns/1/players/{slot_index}
        → Turn 1 player file for the given slot.
          Requires Authorization: Bearer <token> matching that slot.
          Returns the player's fog-of-war filtered view of the universe.

    GET /games/{game_id}
        → Game metadata: name, seed, universe size, player list, current year.

Turn Status Object
------------------

.. code-block:: json

   {
     "game_id": "f47ac10b-...",
     "year": 1,
     "slots": [
       { "slot_index": 0, "player_type": "human", "status": "pending" },
       { "slot_index": 1, "player_type": "ai",    "status": "ready"   }
     ],
     "turn_processed": false
   }

Status values:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Status
     - Meaning
   * - ``pending``
     - Human player has not yet submitted orders.
   * - ``submitted``
     - Human player has submitted orders for this year.
   * - ``skipped``
     - Human player was skipped; engine generated orders on their behalf.
   * - ``ready``
     - AI slot; engine will generate orders when the turn is processed.
   * - ``processed``
     - Orders generated (AI or human); turn already processed for this slot.

Player File Response
--------------------

``Content-Type: application/json``

The body conforms to ``turn.json`` in ``stars-reborn-schemas``.  See
:doc:`initial_state` for the specific contents at turn 1.

On success: ``200 OK``.
If the requester's token does not match the slot: ``403 Forbidden``.
If the turn has not yet been generated: ``404 Not Found`` (should not
occur at turn 1 since generation is synchronous with ``POST /games``).

Validation Against the Original Game
-------------------------------------

To confirm the engine produces a faithful initial state, oracle test cases
compare engine output against observed original ``stars.exe`` behaviour.

Test case structure:

1. A known ``.r`` race file (or set of races) is converted to ``race.json``.
2. A ``POST /games`` request with a fixed ``random_seed`` and known parameters
   is submitted.
3. The engine's turn 1 player files are compared against turn 1 files
   extracted from a |original| game started with the same seed and parameters.

Key properties to validate at turn 1:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Property
     - Validation approach
   * - Planet count
     - Count planets in player file vs. original ``.xy`` file
   * - Homeworld hab values
     - Match midpoint calculation to race hab ranges
   * - Homeworld minerals
     - Fixed 1 000 kT each; compare surface amounts
   * - Starting fleet composition
     - Compare fleet/design list in player file
   * - Starting tech levels
     - Compare per-field tech levels in player file
   * - Visible planet list
     - Compare which planets are in scanner range (requires matching scanner
       range formula)

The ``stars-reborn-research`` repository contains tooling for extracting
turn files from original ``.m`` files (the per-player turn format).  Confirmed
test cases are promoted to the ``stars-reborn-engine`` integration test suite.

.. todo::

   Document the original ``.m`` / ``.xy`` / ``.x`` file formats sufficiently
   to extract turn 1 state for comparison.  This is a research task for
   ``stars-reborn-research``.

.. todo::

   Determine whether the original game's turn 1 is generated at game-creation
   time or deferred until the host "starts" the game (submits initial orders).
   If deferred, ``POST /games`` returns 201 but no turn files exist yet; a
   subsequent host action triggers generation.
