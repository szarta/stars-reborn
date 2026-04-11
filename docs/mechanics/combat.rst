Combat
======

When Combat Occurs
------------------

Battle occurs when **all four** of the following conditions hold simultaneously:

1. Fleets from two or more players are at the same location (planet or deep space).
2. At least one fleet is armed.
3. At least one fleet of the opposing player matches the armed fleet's target specification.
4. The opposing race is set as an enemy (attackable) in the armed fleet's battle orders.

Even declared enemies will not fight if their battle orders forbid it.

.. note:: *Source: Stars! Strategy Guide, Chapter 8 (reviewed by original authors).*

Starbases and Battle Initiation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An armed starbase counts as an armed fleet for the purpose of defending against
attack, but **cannot initiate a battle**. Only a fleet of ships can start a battle.
If an enemy fleet with no battle orders arrives at a planet, the starbase will not
fight even if it is armed — the attacking fleet must have orders that trigger combat.

Intercept Mechanics
~~~~~~~~~~~~~~~~~~~

A fleet can be sent on an intercept course toward a moving enemy fleet. The resolution
order is:

1. The **targeted fleet** moves to its new location first.
2. The **pursuing fleet** then moves toward that new location.
3. If the pursuer's speed is sufficient to reach the target's new location, the
   intercept is successful and combat is resolved there.

This means a slow pursuer can fail an intercept even if the target is heading
toward the pursuer; the target gets its move first.

Battle Orders
-------------

Players set **battle orders** per ship design. The default order is to attack all
races specified as enemies or neutral, targeting **armed ships first**, then anything
else second.

Custom orders allow:

- Primary target (armed enemies / all / none / starbases)
- Secondary target
- Move strategy (maximize damage / minimize losses / maximize net damage)
- Tactic (attack / hold position / disengage)

Battle Grid
-----------

Combat takes place on a **10×10 grid** of squares.  Ships are placed at their
starting positions, which are determined by player number (the lowest-numbered
player in the battle is assigned position 1, the next lowest position 2, etc.).
These positions are **deterministic and fixed** — they do not vary by fleet
composition.

The exact starting squares for 2–16 players are well-documented in the community
(SAH Forum, thread on battle board positioning).  Example (2-player battle):
player 1 starts at row 4 col 1; player 2 at row 5 col 8 (0-indexed).

Players can attempt to manipulate their effective player number (e.g., by
transferring a single ship to an ally the turn before a battle) to influence
starting position.

.. note::

   The design doc previously stated "32×32 grid" — this appears to be an
   implementation artifact.  Community data and FreeStars source consistently
   describe a 10×10 visible board.  See
   ``stars-reborn-research/docs/open_questions/battle_board_dimensions.rst``.

.. todo::

   Confirm board dimensions and starting square table via oracle test or Ghidra.
   Document how many tokens can share one square.

Battle Rounds
-------------

A battle runs for a maximum of **16 rounds**. If ships remain on both sides
after 16 rounds, the attacker is repelled (defender wins by default).

Each round:

1. Ships move (based on battle speed, determined by engine)
2. Beams fire
3. Missiles/torpedoes fire
4. Shields regenerate

Ship Battle Speed
-----------------

Battle movement is separate from warp speed. A ship's battle speed determines
how many squares it can move per round.

Battle movement formula (in ¼-square units):

.. code-block:: text

   movement = (ideal_engine_speed − 4) / 4
             − (ship_mass / 70 / 4 / num_engines)
             + (0.25 × num_maneuvering_jets)
             + (0.5 × num_overthrusters)

Movement is capped in the range **½ to 2½ squares per round**.
WM (War Monger) race gets an additional **+½ square** bonus.

Each round has 3 movement phases:

1. Tokens that can move ≥3 squares this round move 1 square
2. Tokens that can move ≥2 squares this round move 1 square
3. All remaining tokens move 1 square

Within each phase, tokens move heaviest-to-lightest (±15% margin for ties).

*Source: Stars! in-game help, Battle Board section.*

Per-engine battle speeds are also in the fuel tables (``data/fuel_tables/``).

Weapons
-------

Beams
~~~~~

- Fire first in each round
- Deal damage to the nearest enemy ship within range
- **Attenuation:** damage decreases with distance. At maximum range, beams
  deal significantly less damage than at close range
- Beam weapons: Laser, X-Ray Laser, Mini Gun, Yakimora Light Phaser, Blackjack,
  Phaser Bazooka, Pulsed Sapper, Disruptor, Syncro Sapper, Mega Disruptor,
  Big Mutha Cannon, Streaming Pulverizer, Anti-Matter Pulverizer

Beam Decay Formula
^^^^^^^^^^^^^^^^^^

Beam damage decays linearly from full power (range 0) to 90% power (max range):

.. code-block:: text

   effective_damage = base_damage × (1 − 0.1 × d / R)

Where ``d`` = distance to target, ``R`` = weapon max range.

Example: 100 dp weapon, max range 3, target at distance 2:
``100 × (1 − 0.1 × 2/3) = 94 dp``

*Source: Stars! in-game help, Beam Weapons section.*

Missiles & Torpedoes
~~~~~~~~~~~~~~~~~~~~~

- Fire second each round
- Travel to target; can miss (affected by accuracy and jammers)
- Hit: deals damage (50% to shields, 50% direct to armor)
- Miss: **collateral damage** = 1/8 normal damage to shields only
- Overflow if target token destroyed: applied to other tokens in same square
- **One missile = one kill (per round):** the game caps missile kills at the
  number of missiles fired in a round.  Each missile destroys at most one ship
  (excess damage is not applied to the next ship in the stack).  Beam weapons do
  not share this limit — a single beam hit can kill multiple ships.

*Source: SAH Forum, Chaff article (Art Lathrop) / community consensus.*

Targeting Algorithm
^^^^^^^^^^^^^^^^^^^

Missiles and torpedoes select targets by **attractiveness**, which combines cost
and vulnerability.  Cheaply-built, lightly-armored ships are the most attractive
targets.  Attractiveness is roughly proportional to:

.. code-block:: text

   attractiveness ∝ (armor + shields) / (resource_cost + boranium_cost)

Practical effects:

- Scouts/frigates with cheap engines and minimal armor are chosen first, soaking
  missiles before capital ships are targeted ("chaff" strategy).
- Adding shields to a cheap ship reduces its attractiveness as a missile target
  (more durability per cost → less attractive).
- Adding armor to capital ships decreases their attractiveness relative to chaff.

.. todo::

   Verify exact targeting attractiveness formula via Ghidra.  See
   ``stars-reborn-research/docs/open_questions/targeting_attractiveness_formula.rst``.

Battle Computers
^^^^^^^^^^^^^^^^

Three types, reducing torpedo **inaccuracy** by 20%, 30%, or 50%:

.. code-block:: text

   new_accuracy = 100 − ((100 − old_accuracy) × (1 − BC_factor))

Multiple battle computers apply sequentially (multiplicative on inaccuracy):

.. code-block:: text

   Example: 75% base + two 30% BCs:
   100 − (25 × 0.70 × 0.70) = 87.75% ≈ 88%

*Source: Stars! in-game help, Battle Computers section.*

Jammers
^^^^^^^

Jammer values are additive percentage reductions, applied multiplicatively:

.. code-block:: text

   Example: three 20% jammers:
   75% × 0.8 × 0.8 × 0.8 = 38% accuracy

BC vs Jammer interaction: 1% BC decrease in inaccuracy cancels 1% jammer
decrease in accuracy; net effect applies to remaining difference.

*Source: Stars! in-game help, Jammers section.*

Bombs
~~~~~

Bombs are not used in ship-to-ship combat. They are dropped on planets during
the bombing phase (separate from combat).

Damage Model
------------

Each ship has:

- **Shields:** absorbed first; regenerate 10% per round (25% for IS race with RS LRT)
- **Armor:** absorbed second; does not regenerate

When armor reaches 0, the ship is destroyed. Partial armor damage carries over
between rounds.

**Minimum damage resolution:** Armor damage is stored in **1/512th increments**
of the token's total armor.  Any hit that would deal armor damage rounds up to
the nearest 1/512th of total armor (≈ 0.2%).  In normal play this is negligible,
but a large number of individually-weak salvos (e.g., 900 separate torpedo shots)
can collectively destroy a token via accumulated 0.2% hits.

*Source: SAH Forum Known Bugs thread; also confirmed in FreeStars source.*

Shield regeneration per round:

.. code-block:: text

   new_shields = min(max_shields, current_shields + floor(max_shields × 0.10))

IS race (or RS LRT): 25% regeneration rate.

**RS (Regenerating Shields) LRT specifics:**

- Shields are **40% stronger** than their listed rating (e.g., a 100-rating shield
  provides 140 shield points)
- Armor is **50% of rated strength** (penalty)
- Regeneration: **10% of max shield value per round** (not base rated value)

*Source: Stars! in-game help, Regenerating Shields section.*

Capacitors & Jammers
--------------------

Capacitors
~~~~~~~~~~

Two types of beam capacitors: +10% or +20% beam damage per capacitor.
Stacking is **multiplicative**:

.. code-block:: text

   Example: three 10% capacitors: ×1.1 × 1.1 × 1.1 = ×1.331

**Hard cap:** capacitors may not contribute more than **250% additional damage**
(= ×3.5 total multiplier).

*Source: Stars! in-game help, Capacitors section.*

Energy Dampener
~~~~~~~~~~~~~~~

The Energy Dampener (SD PRT exclusive) slows **all ships in the battle** by
−1 square per round for the entire battle. Notable properties:

- Effect persists even if the ship carrying it is destroyed
- Multiple dampeners in one battle provide **no additional effect** (not stacked)

*Source: Stars! in-game help, Energy Dampener section.*

Movement Strategy
-----------------

Each ship follows its battle movement strategy:

- **Maximize damage:** move toward the enemy; fire every available weapon
- **Minimize losses:** maintain range with beams; withdraw if shields are low
- **Maximize net damage:** balance offense and defense

.. todo:: Reverse-engineer the exact AI movement heuristics.

Battle Results
--------------

After combat:

- Surviving ships remain at the battle location
- Destroyed ships produce **salvage** (a fraction of their mineral cost)
  that can be picked up by any fleet
- Battle report is generated for all players involved

Damage Repair
-------------

Damaged ships repair a percentage of damage each year based on location:

.. list-table::
   :header-rows: 1
   :widths: 55 20

   * - Location
     - Annual repair rate
   * - Moving through space
     - 1%
   * - Stopped in space
     - 2%
   * - Orbiting enemy planet (not bombing)
     - 3%
   * - Orbiting own planet, no starbase
     - 5%
   * - Orbiting own planet, starbase (no space dock)
     - 8%
   * - Orbiting own planet, space dock
     - 20%
   * - + Fuel Transport hull in fleet (bonus)
     - +5%
   * - + Super Fuel Xport hull in fleet (bonus)
     - +10%

- Fuel Transport/Xport bonuses are not stacked; only the best hull in the fleet applies
- No repair when using a stargate
- No repair when fleet has Attack orders while orbiting an enemy planet

*Source: Stars! in-game help, Damage Repair section.*

Open Questions
--------------

.. todo:: Starting formation placement rules on the 32×32 grid

.. todo:: Exact beam attenuation formula (confirmed linear from help; verify with oracle)

.. todo:: Exact missile accuracy formula with computers and jammers (BC formula confirmed above; needs oracle verification)

.. todo:: Capacitor damage multiplier table (10%/20% confirmed; oracle verify exact values)

.. todo:: Reverse-engineer the exact AI movement heuristics for each strategy

.. todo:: Salvage fraction of destroyed ship cost

.. todo:: What happens when a starbase is involved (it cannot move)

.. todo:: SD (Space Demolition) mine explosion mechanics in combat


.. _stars-reborn-impl:

Implementation Notes (from stars-reborn)
----------------------------------------

When fleets from opposing players occupy the same location and at least one fleet is
armed, a battle is resolved at end of turn (after movement, before messages).
Battle Setup
------------
Ships from all fleets at the location are placed on a 32×32 grid. Placement depends
on the fleet's battle orders (approach/retreat strategy).
Battle Sequence
---------------
Up to 16 rounds are fought. Each round:
1. **Move** — each ship moves toward or away from targets per its strategy
2. **Fire beams** — beam weapons fire; damage attenuates with distance
3. **Fire torpedoes/missiles** — fired at target; miss chance per jammer/computer
Ships move in speed order (fastest first). Within same speed, order is random.
Damage Resolution
**Shields** absorb damage first. Remaining damage hits armor.
Shields regenerate 10% of max capacity each round (base). RS (Regenerating Shields) LRT
doubles regeneration. IS PRT gets enhanced shields.
**Beam weapons** deal damage to the first ship in range. Beams attenuate (lose power)
with distance:
    effective_power = power * (1 - distance / (range + 1))
**Torpedoes** target a single ship. Miss chance:
.. code-block:: text
    hit_chance = 0.85 + (computers - jammers) * 0.05
    # clamped to [0.25, 0.99]
Miss means torpedo explodes near the target for reduced splash damage.
**Missiles** are like torpedoes but use different damage/miss formulas.
Battle Orders
-------------
Each ship design has:
* **Primary target** — who to attack first (armed ships, all, starbases, etc.)
* **Secondary target** — fallback if no primary in range
* **Move strategy** — maximize damage (close range), minimize losses (hold range),
  disengage (run away)
Salvage
-------
Destroyed ships leave salvage: a percentage of their hull + parts mineral cost.
Salvage drifts in space and decays each year.
Bombing
-------
When a fleet with bomb weapons is at a planet with no defending fleet:
**Normal bombs** — each bomb kills a percentage of population and defenses:
.. code-block:: text
    pop_killed = colonists * kill_percent / 100
    defenses_killed = floor(defenses * defense_kill_percent / 100)
**Smart bombs** — kill only colonists, not defenses.
**Retroviruses** (SD PRT only) — spread a retrovirus that causes population loss in
subsequent years (decreasing effect over 3 years).
Reference: Leonard Dickens 1998 bombing formula (``sr-old/reference/research/``).
