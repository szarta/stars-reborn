Turn Resolution Order
=====================

.. warning::

   The sequence below is **unverified**. It is a best-effort reconstruction
   from community sources and prior research. Several steps — particularly
   the relative ordering of packet movement, mine-laying, mine-field sweeping,
   fleet movement, bombing, and population growth — have been subjects of
   competitive debate because the order creates exploitable strategic
   differences. Every step must be confirmed by oracle testing before the
   engine implements it.

   See ``stars-reborn-research/docs/open_questions/turn_resolution_order.rst``
   for the research task.

Each year, the |original| engine processes events in the following order. |project| must
reproduce this sequence exactly for behavioral fidelity.

Sequence
--------

1. **Wormhole jiggles**
   Wormholes drift slightly each year. Endpoints shift by a small random amount.

2. **Random events**
   Comet strikes, mystery trader appearances, etc. (low probability per year).

3. **Packets and salvage move**
   Mineral packets fired from mass drivers advance toward their targets. Salvage
   drifts and decays (each year reduces mineral content).

4. **Fleets move**
   All fleets advance along their waypoints at their ordered speed. When a fleet
   arrives at a waypoint, it executes the waypoint order (colonize, mine, transfer
   cargo, etc.) and advances to the next waypoint. Mine-laying occurs during movement.

5. **Mine fields sweep**
   After all fleets have moved, mine fields check for fleets that entered or crossed
   through them. Mine-sweeping by fleets with mine-sweep weapons is also resolved here.

6. **Bombing**
   Fleets with bomb orders attack undefended planets. Normal and smart bombs apply
   population and defense kill percentages. Retroviruses (SD trait) spread genetic
   damage.

7. **Population growth**
   Each owned planet grows by ``growth_rate × planet_value / 100``. Overcrowding
   applies a penalty when population exceeds 25% over planet capacity.

8. **Factories and mines built**
   Production queues are processed for factory and mine construction items.

9. **Minerals mined**
   Each planet mines ``mine_count × mine_output × concentration / 100`` kT per mineral.
   Concentration decreases by a small amount each year.

10. **Resources generated; production queues run**
    Total resources = colonists × (resource_production / 10000) + factories × factory_output.
    Resources are applied to production queue items (ships, defenses, terraforming, etc.).

11. **Research applied**
    Resources allocated to research are credited to the appropriate tech fields.
    When a field accumulates enough resources, the tech level increases and new
    technologies become available.

12. **Battles**
    At any location where fleets from opposing players meet (and at least one is armed),
    a battle is resolved. The battle engine runs up to 16 rounds. Surviving ships remain;
    destroyed ships become salvage.

13. **Fleet merge/split**
    Player orders to merge or split fleets are executed.

14. **Messages generated**
    Turn messages are compiled for each player: discoveries, battle results, tech advances,
    random events, victory/defeat notifications.

Notes
-----

* Steps 4–5 are critical for mine field interactions. A fleet that is moving through a mine
  field has a chance of hitting a mine at each ly of travel.
* Research (step 11) happens *after* production (step 10), so resources spent on production
  queues are not available for research in the same turn.
* Battle (step 12) happens *after* population growth, meaning bombing survivors may still
  grow before combat.

.. todo::

   Confirm the exact turn resolution order via oracle testing. The following
   sub-questions are the highest-priority targets because each has known
   competitive implications:

   - **Packets vs. fleet movement**: do mineral packets resolve before or after
     fleets move? A packet arriving at a planet with a defending fleet in the
     same turn could interact differently depending on order.
   - **Mine-laying vs. mine-field sweep**: does a fleet laying mines in a field
     it is currently traversing affect the sweep calculation for that same turn?
   - **Mine-field sweep vs. fleet arrival**: if a fleet enters a mine field and
     hits a mine, does it still execute its waypoint order that turn?
   - **Bombing vs. population growth**: confirmed post-growth above, but needs
     oracle verification (a bombed population that grew first is a different
     result than one bombed before growth).
   - **Battle vs. bombing**: can a fleet bomb a planet and then also fight a
     battle at the same location in the same turn?
   - **Packet arrival damage vs. colonization**: if a packet hits a planet the
     same turn a fleet colonizes it, which resolves first?

   Community competitive play identified at least some of these as strategically
   significant. Check the starsautohost.org article library for any documented
   community findings before running oracle tests.
