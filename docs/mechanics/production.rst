Production
==========

Overview
--------

Each colonized planet has a production queue that is processed every turn.
Resources (energy/labor) and minerals (ironium, boranium, germanium) are
consumed to build items. Leftover resources and minerals carry over.

Resources
---------

Resources represent colonist labor + factory output.

.. code-block:: text

   colonist_resources = floor(population / resource_production)
   factory_resources  = factories_built × factory_production
   total_resources    = colonist_resources + factory_resources

Where ``resource_production`` is the race parameter (700–2500 colonists per resource).

Example: 1,000,000 colonists, ``resource_production=1000``, 100 factories × 10 production:

.. code-block:: text

   colonist_resources = 1,000,000 / 1,000 = 1,000
   factory_resources  = 100 × 10 = 1,000
   total = 2,000 resources/year

Factories
---------

- Cost to build: ``factory_cost`` resources + 4 germanium (or 3 germanium with the "costs one less" race option)
- Production: ``factory_production`` resources/year when operated
- Capacity: max ``(population / 10,000) × colonists_operate_factories`` factories
- Factories beyond capacity sit idle (no production, no cost)

Mines
-----

- Cost to build: ``mine_cost`` resources
- Production: extracts ``mine_production`` kT of each mineral/year × (concentration/100)
- Capacity: max ``(population / 10,000) × colonists_operate_mines`` mines
- Mineral extraction formula:

  .. code-block:: text

     kT_extracted = mine_production × concentration / 100

- Concentration slowly depletes over time as minerals are extracted

Mineral Concentration Decay
----------------------------

Concentrations range from 0 to 200 (not 0–100 as colloquially described).

Each mine-year of extraction reduces concentration by:

.. code-block:: text

   mine_years_to_reduce_by_1 = 12,500 / current_concentration

So a concentration-100 mineral requires 125 mine-years to drop by 1 point.
A concentration-50 mineral requires 250 mine-years. At concentration 1 (the
floor), no further reduction occurs.

**Homeworld special rule:** concentration never drops below 30% on a homeworld
regardless of mining, for any race that owns it.

*Source: Stars! in-game help, Minerals section.*

Production Queue
----------------

Items in the production queue are built in order each turn:

.. list-table::
   :header-rows: 1
   :widths: 25 20 15 15 15

   * - Item
     - Resources
     - Ironium
     - Boranium
     - Germanium
   * - Mine
     - ``mine_cost``
     - 0
     - 0
     - 0
   * - Factory
     - ``factory_cost``
     - 0
     - 0
     - 4 (or 1)
   * - Defense
     - varies by tech
     - 0
     - 0
     - 0
   * - Ship (by design)
     - varies
     - varies
     - varies
     - varies
   * - Mineral alchemy (MA)
     - 100
     - −1 ea
     - −1 ea
     - −1 ea → +1 ea
   * - Terraform
     - varies
     - 0
     - 0
     - 0

**Partial production:** if insufficient resources to complete an item, progress is
banked. The item will be completed in a subsequent turn.

**Auto items:** Auto-mines and auto-factories continue building until the
colonist-capacity limit is reached, then stop automatically.

Ship Construction
-----------------

Ships are built from a design with a hull and installed parts. Cost:

.. code-block:: text

   total_resources = hull_cost + sum(part_cost for part in slots)
   total_ironium   = hull_iron + sum(part_iron for part in slots)
   ... etc.

Defenses
--------

Defenses protect the population from orbital bombing. Each defense installation
adds to the planet's kill rate (% of incoming bombers' bomb effectiveness blocked).

.. todo:: Document defense costs by tech level and the kill rate formula.

Starbases
---------

Starbases are a special production item — they orbit the planet rather than
landing on it. They can be upgraded by queuing a new starbase design.

.. todo:: Document starbase construction and upgrade costs.

Turn Resolution Order
---------------------

Production runs near the end of the turn, after movement but before end-of-turn
reporting. Full turn order is documented in ``mechanics/turn_resolution.md``.

Open Questions
--------------

.. todo:: Exact mineral concentration decay rate

.. todo:: Defense cost table by tech level

.. todo:: Defense kill rate formula

.. todo:: Starbase construction and upgrade rules

.. todo:: Exact partial production banking rules (does germanium also bank?)

.. todo:: Mineral alchemy exact exchange rates (MA LRT)

.. todo:: AR race: production runs in starbases, not planets


.. _stars-reborn-impl:

Implementation Notes (from stars-reborn)
----------------------------------------

Resource Generation
-------------------
Annual resources per planet:
    resources = floor(population / (10000 / resources_per_10k))
              + floor(factories * factory_output)
Where:
* ``population`` — current colonist count on the planet
* ``resources_per_10k`` — race parameter (5–25 resources per 10,000 colonists per year)
* ``factories`` — number of operational factories (capped by colonists: max = pop / colonists_per_factory)
* ``factory_output`` — race parameter (5–15 resources per factory per year)
The production queue is an ordered list of items. Each turn, resources are applied
from top to bottom. Partial completion banks resources toward the next turn.
Queue item types:
* **Factory** — costs (factory_cost) resources + 4 germanium; limited by colonists_per_factory
* **Mine** — costs (mine_cost) resources; limited by colonists_per_mine
* **Defense** — costs 5 resources; up to 100 defenses per planet
* **Ship** — costs vary by hull + installed parts (hull cost + sum of part costs)
* **Starbase** — same as ship but immobile; upgrades existing starbase
* **Mineral Alchemy** — converts resources to minerals:
  - With MA trait: **25 resources → 1 kT each** of Ironium, Boranium, Germanium
  - Without MA trait: **100 resources → 1 kT each** (much less efficient)
  *Source: Stars! in-game help.*
* **Terraforming** — 100 resources → 1 unit shift on one hab axis
Auto-items (infinite quantity):
* **Auto-factory** — keep building factories until max reached
* **Auto-mine** — keep building mines until max reached
* **Auto-defense** — keep building defenses until max reached
Mineral Consumption
-------------------
Minerals are consumed when building ships:
* Hull cost provides ironium/boranium/germanium base amounts
* Each installed part adds its own mineral costs
* Factories: 1 germanium each
* Mines: no minerals
* Defenses: no minerals
See ``docs/mechanics/technology_tree.rst`` for per-item mineral costs.
