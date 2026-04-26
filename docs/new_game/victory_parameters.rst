Victory Condition Parameters
============================

The host selects which victory conditions are active and sets their
thresholds when creating a new game.  These become the
``victory_conditions`` block in the ``POST /games`` request.

For scoring formulae, minimum-year behaviour, and win-announcement
semantics, see :doc:`../mechanics/victory`.

Available Conditions
--------------------

The host checks any subset of the seven conditions below, and separately
configures **how many** of the checked conditions a player must meet for
victory, plus the earliest game year at which victory may be declared.

Condition ranges and field names are drawn from the Step-3 *Winning
Conditions* page of the Advanced New Game wizard and from the
``stars!.exe -a game.def`` CLI reference in the help file.

.. list-table::
   :header-rows: 1
   :widths: 28 22 18 16 16

   * - Condition
     - Enabled field
     - Threshold field
     - Range
     - CLI name
   * - Has colonised N% of all planets in the universe
     - ``own_planets``
     - ``own_planets_pct``
     - 20–100
     - ``VC # of planets``
   * - Attains tech level N in X fields
     - ``tech_levels``
     - ``tech_level`` / ``tech_fields``
     - level 8–26 / 2–6 fields
     - ``VC Tech``
   * - Exceeds a score of N
     - ``exceed_score``
     - ``score_threshold``
     - 1 000–20 000
     - ``VC Score``
   * - Exceeds second-place score by N%
     - ``score_lead``
     - ``score_lead_pct``
     - 20–300
     - ``VC Exceeds nearest``
   * - Has a production capacity of N thousand
     - ``production_capacity``
     - ``production_capacity_k``
     - 10–500 (thousands of annual resources)
     - ``VC Production``
   * - Owns N capital ships
     - ``own_capital_ships``
     - ``capital_ships_threshold``
     - 10–300
     - ``VC Capital Ships``
   * - Has the highest score after N years
     - ``highest_score``
     - ``highest_score_year``
     - 30–900
     - ``VC Turns``

Two additional fields control *combination* and *timing*:

.. list-table::
   :header-rows: 1
   :widths: 28 22 18 32

   * - Parameter
     - Field
     - Range
     - CLI name
   * - Winner must meet N of the selected criteria
     - ``must_meet_count``
     - 0–7
     - ``VC Must Meet``
   * - Minimum years before a winner may be declared
     - ``min_years``
     - 30–500
     - ``Minimum Years``

Full Parameter Object
---------------------

.. code-block:: json

   {
     "own_planets":            true,
     "own_planets_pct":        60,

     "tech_levels":            true,
     "tech_level":             22,
     "tech_fields":            4,

     "exceed_score":           false,
     "score_threshold":        11000,

     "score_lead":             true,
     "score_lead_pct":         100,

     "production_capacity":    false,
     "production_capacity_k":  100,

     "own_capital_ships":      false,
     "capital_ships_threshold": 100,

     "highest_score":          false,
     "highest_score_year":     100,

     "must_meet_count":        1,
     "min_years":              50
   }

The example above matches the values shown on a freshly-opened *Step 3
Winning Conditions* page of the Advanced New Game wizard (captured from
the original game).  The host may toggle any checkbox and adjust any
spinner before clicking *Finish*.

Validation Rules
----------------

Engine-enforced at game creation:

- ``must_meet_count`` must be ≤ the number of enabled conditions.
- ``tech_level`` ∈ [8, 26], ``tech_fields`` ∈ [2, 6].
- ``own_planets_pct`` ∈ [20, 100].
- ``score_threshold`` ≥ 1 000.
- ``score_lead_pct`` ∈ [20, 300].
- ``production_capacity_k`` ∈ [10, 500].
- ``capital_ships_threshold`` ∈ [10, 300].
- ``highest_score_year`` ∈ [30, 900].
- ``min_years`` ∈ [30, 500].

.. _victory-params-open-questions:

Open Questions
--------------

.. todo:: Clarify the semantics of ``must_meet_count = 0``.  The Step-3
   wizard permits selecting 0 even when one or more conditions are
   checked; does this make victory unreachable, or does 0 have some other
   meaning (e.g. "ignore the must-meet combinator")?
