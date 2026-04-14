Universe Parameters
===================

The host configures universe generation parameters when creating a new game.
These become the ``universe_params`` block in the ``POST /games`` request.
For the generation algorithms that consume these parameters, see
:doc:`../mechanics/universe_generation`.

Size
----

Controls the universe's rectangular extent and therefore the number of planets
at a given density.

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 40

   * - Value
     - Field name
     - Dimension (ly)
     - Notes
   * - ``tiny``
     - ``size``
     - 400 × 400
     - 2–3 players; early contact
   * - ``small``
     - ``size``
     - 800 × 800
     - Up to 4 players
   * - ``medium``
     - ``size``
     - 1200 × 1200
     - 4–16 players
   * - ``large``
     - ``size``
     - 1600 × 1600
     - Up to 16 players
   * - ``huge``
     - ``size``
     - 2000 × 2000
     - Up to 16 players

Density
-------

Controls how many planets exist within the universe.

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Value
     - Density value
     - Notes
   * - ``sparse``
     - 1.5
     - \
   * - ``normal``
     - 2.0
     - Default
   * - ``dense``
     - 2.5
     - \
   * - ``packed``
     - 3.75
     - Large/Packed, Huge/Dense, Huge/Packed are capped by engine limits

Planet count: ``floor((dim / 10)² × density / 100)`` — always at least
``num_players``.

Player Positions
----------------

Controls how far homeworlds are spread relative to each other.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Value
     - Behaviour
   * - ``close``
     - Homeworlds placed near each other; early conflict
   * - ``random``
     - No homeworld placement constraint beyond minimum distance
   * - ``distant``
     - Homeworlds maximally spread; most common competitive choice

.. todo::

   Confirm the exact homeworld placement algorithm for each ``player_positions``
   option (are sectors/quadrants used, or is it a rejection-sampling min-distance
   from other homeworlds?).

Game Options
------------

Boolean flags that modify generation or gameplay.

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Field
     - Default
     - Effect
   * - ``beginner_max_minerals``
     - false
     - All mineral concentrations set to 100.  Removes mineral scarcity.
   * - ``accelerated_bbs``
     - false
     - Starting population = ``25,000 + 5,000 × GR%`` (scales with growth
       rate; ≈ 100,000 for a 15% race); all planets +20% minerals; poor
       mineral worlds improved.  See :doc:`initial_state` for full formula.
   * - ``slower_tech_advances``
     - false
     - Research costs doubled universe-wide.
   * - ``no_random_events``
     - false
     - Disables mineral discoveries, artifact discoveries, comets, and
       habitability shifts.
   * - ``computer_players_form_alliances``
     - false
     - AI players target human players preferentially.
   * - ``public_player_scores``
     - false
     - Score sheet (F10) visible to all players after year 20.
   * - ``galaxy_clumping``
     - false
     - Star systems are placed in clusters; faster initial expansion.
       See :doc:`../mechanics/universe_generation`.

Random Seed
-----------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Field
     - Description
   * - ``random_seed``
     - Optional 64-bit unsigned integer.  If omitted the engine generates one
       and returns it in the creation response.  Providing the same seed with
       the same parameters must reproduce the identical universe.

The seed is stored in the game state and included in the
``response-create-new-game.json`` payload so it can be recorded.

Full Parameter Object
---------------------

.. code-block:: json

   {
     "size":                           "medium",
     "density":                        "normal",
     "player_positions":               "distant",
     "beginner_max_minerals":          false,
     "accelerated_bbs":                false,
     "slower_tech_advances":           false,
     "no_random_events":               false,
     "computer_players_form_alliances": false,
     "public_player_scores":           false,
     "galaxy_clumping":                false,
     "random_seed":                    null
   }
