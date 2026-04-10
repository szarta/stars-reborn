Data Schemas
============

JSON schemas for all |project| game objects. These are the ground truth for
all data models shared between the engine and UI.

Schema files live in the ``stars-reborn-schemas`` repository — a standalone
artifact depended on by both the engine and UI, and bundled into the
application by the ``stars-reborn-game`` integration repo. This page is the
descriptive catalog; the files themselves are authoritative in that repo.

.. list-table::
   :header-rows: 1
   :widths: 30 60

   * - Schema
     - Description
   * - ``battle.json``
     - Battle report: rounds, events, surviving/destroyed ships
   * - ``planet.json``
     - Planet state: hab values, minerals, population, infrastructure, owner
   * - ``player.json``
     - Player state: race, known planets, fleets, tech levels
   * - ``race.json``
     - Race definition: PRT, LRTs, economy parameters, hab ranges, tech costs
   * - ``tech.json``
     - Technology item catalog: all 180+ items with costs, stats, and requirements
   * - ``turn.json``
     - Turn input/output wrapper: player orders in, game state out
   * - ``universe.json``
     - Universe snapshot: all planets, all fleets, all players
   * - ``request-create-new-game.json``
     - API request to create a new game; see :doc:`../new_game/new_game_request`
   * - ``request-create-tutorial-game.json``
     - API request to create a tutorial game
   * - ``request-validate-race.json``
     - API request to validate a race design
   * - ``response-create-new-game.json``
     - API response for new game creation; see :doc:`../new_game/new_game_request`
   * - ``response-create-tutorial-game.json``
     - API response for tutorial game creation
   * - ``response-validate-race.json``
     - API response for race validation
