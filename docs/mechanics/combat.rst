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

Combat takes place on a **32×32 grid**. Ships are placed at their starting
positions based on their initial formation.

.. todo::

   Document starting formation rules (which squares are used, how many ships
   can stack in one square).

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
how many squares it can move per round. This is a property of the engine.

Battle speeds are in the fuel tables (``data/fuel_tables/``).

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

.. todo:: Document exact attenuation formula.

Missiles & Torpedoes
~~~~~~~~~~~~~~~~~~~~~

- Fire second each round
- Travel to target; can miss (affected by accuracy and jammers)
- Deal full damage if they hit; no damage if they miss
- Missiles spread damage across armor; torpedoes punch through shields
- Accuracy formula: ``base_accuracy × (1 + computers_bonus) × (1 - jammers_penalty)``

.. todo:: Document exact accuracy formula and computer/jammer interactions.

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

Shield regeneration per round:

.. code-block:: text

   new_shields = min(max_shields, current_shields + floor(max_shields × 0.10))

IS race (or RS LRT): 25% regeneration rate.

Capacitors & Jammers
--------------------

- **Beam capacitors:** multiply beam damage by a factor (e.g., ×1.1, ×1.5)
- **Deflectors:** reduce beam damage taken (the opposing effect)
- **Jammers:** reduce incoming missile accuracy (each jammer stacks multiplicatively)
- **Battle computers:** increase beam and missile accuracy

.. todo::

   Document exact capacitor damage multipliers and jammer accuracy reduction
   tables from Posey's spreadsheet.

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

Open Questions
--------------

.. todo:: Starting formation placement rules on the 32×32 grid

.. todo:: Exact beam attenuation formula (linear? logarithmic?)

.. todo:: Exact missile accuracy formula with computers and jammers

.. todo:: Capacitor damage multiplier table (from Posey's spreadsheet)

.. todo:: Jammer accuracy reduction table

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
