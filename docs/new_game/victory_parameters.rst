Victory Condition Parameters
============================

The host selects which victory conditions are active and sets their thresholds
when creating a new game.  These become the ``victory_conditions`` block in
the ``POST /games`` request.

For scoring formulae, year-50 minimum, and win-announcement behaviour, see
:doc:`../mechanics/victory`.

Available Conditions
--------------------

Multiple conditions may be enabled simultaneously.  Meeting **any one** wins
the game (subject to the year-50 minimum).

.. list-table::
   :header-rows: 1
   :widths: 30 20 20 30

   * - Condition
     - Enabled field
     - Threshold field
     - Default threshold
   * - Own N% of planets
     - ``own_planets``
     - ``own_planets_pct``
     - 30
   * - Attain tech level N in X fields
     - ``tech_levels``
     - ``tech_level`` / ``tech_fields``
     - level 22 in 6 fields
   * - Exceed score N
     - ``exceed_score``
     - ``score_threshold``
     - 11 000
   * - Score above second-place by N%
     - ``score_lead``
     - ``score_lead_pct``
     - 100
   * - Produce N resources per year
     - ``produce_resources``
     - ``resources_threshold``
     - 1 000
   * - Own N starbases
     - ``own_starbases``
     - ``starbases_threshold``
     - 100
   * - Highest score after year N
     - ``highest_score``
     - ``highest_score_year``
     - 900

All ``_pct`` fields are integers in [1, 100].  All other thresholds are
positive integers.

Full Parameter Object
---------------------

.. code-block:: json

   {
     "own_planets":          true,
     "own_planets_pct":      30,

     "tech_levels":          true,
     "tech_level":           22,
     "tech_fields":          6,

     "exceed_score":         true,
     "score_threshold":      11000,

     "score_lead":           true,
     "score_lead_pct":       100,

     "produce_resources":    true,
     "resources_threshold":  1000,

     "own_starbases":        true,
     "starbases_threshold":  100,

     "highest_score":        true,
     "highest_score_year":   900
   }

All conditions are enabled by default to match the original game's default
new-game setup.

Validation Rules
----------------

- At least one condition must be enabled.
- ``tech_fields`` must be in [1, 6].
- ``tech_level`` must be in [1, 26] (the valid range of tech levels).
- ``own_planets_pct`` must be in [1, 100].
- ``score_lead_pct`` must be ≥ 1.

.. todo::

   Confirm whether the original game enforces any of these validation rules
   at game creation time or simply behaves oddly if they are violated.

.. todo::

   Determine whether ``own_planets_pct`` is computed against total planets
   in the universe or total colonised planets.
