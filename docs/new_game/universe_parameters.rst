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
   :widths: 20 22 58

   * - Value
     - Density factor
     - Notes
   * - ``sparse``
     - 2.0
     - Oracle-confirmed 2026-04-22
   * - ``normal``
     - 2.5
     - Oracle-confirmed 2026-04-22; default
   * - ``dense``
     - 3.75
     - Oracle-confirmed 2026-04-22; **maximum effective density** (see note)

Planet count: ``floor((dim / 10)² × density_factor / 100)`` — always at least
``num_players``.

.. note::

   ``dense`` is the highest density selectable through the Stars! game UI and the
   highest code observed in ``.xy`` files (internal code 3).  A ``packed`` token
   (internal code 4) exists in the ``game.def`` file format but is invalid — Stars!
   exits silently with no output when given ``density=4`` in headless mode.  The
   original game UI's top density option (sometimes labeled "Packed" in community
   guides) stores as code 3 and is equivalent to ``dense``.

   Combinations where the formula target exceeds ~960 produce stochastic planet
   counts in the 908–965 range; see :doc:`../mechanics/universe_generation`.

Player Positions
----------------

Controls how far homeworlds are spread relative to each other.  There are four
settings; the two middle values correspond to the Stars! UI options labelled
"Random" (moderate) and "Farther Apart" (farther).

.. list-table::
   :header-rows: 1
   :widths: 20 25 55

   * - Value
     - Min separation (ly)
     - Behaviour
   * - ``close``
     - ≈ 60–62 ly
     - Homeworlds tightly clustered; early conflict
   * - ``moderate``
     - ≈ 178–180 ly
     - Moderate spread; labelled "Random" in Stars! UI
   * - ``farther``
     - ≈ 245–250 ly
     - Larger spread; labelled "Farther Apart" in Stars! UI
   * - ``distant``
     - ≈ 289–295 ly
     - Homeworlds maximally spread; most common competitive choice

**Minimum-separation constraint (oracle-confirmed 2026-04-22):**

Each setting enforces a hard minimum Euclidean separation between any two
homeworlds.  The values above are empirical upper bounds measured on a
Small / Normal map with 6 players across 10 seeds each.  The placement
algorithm is consistent with minimum-distance rejection sampling: a candidate
homeworld position is rejected if it falls within the threshold distance of any
already-placed homeworld.

Separation thresholds may scale with map size; the values quoted apply to Small
(800 × 800 ly) maps.  On very small maps with many players and ``distant``
spacing, Stars! may silently reduce the actual player count if it cannot place
all homeworlds at the required separation.

.. note::

   Whether thresholds are absolute constants or scale with map dimension is
   unconfirmed (tested on Small maps only).  The qualitative shape of each
   setting is faithfully reproduced by the values above; exact scaling is
   deferred as low-priority (P4).

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
     - All mineral concentrations set to exactly 100 (oracle-confirmed 2026-04-22).
       Removes mineral scarcity entirely.
   * - ``accelerated_bbs``
     - false
     - Starting population = ``25,000 + 5,000 × GR%`` (scales with growth
       rate; ≈ 100,000 for a 15% race); homeworld surface minerals ×1.25
       (oracle-confirmed; community "+20%" claim is wrong — it is +25%);
       non-homeworld surface minerals assumed ×1.25 (untestable without
       ownership).  See :doc:`initial_state` for full formula.
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
