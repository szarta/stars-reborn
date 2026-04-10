Race File Format
================

Stars Reborn uses a JSON race file format (``*.race.json``) as its native
format.  The engine can also import the original |original| binary race
format (``*.r``) and convert it on the fly.

Stars Reborn JSON Format
------------------------

The file is a single JSON object conforming to ``race.json`` in
``stars-reborn-schemas``.  It is a direct serialisation of the race
definition submitted to the engine — the same structure passed in the
``race`` field of a ``POST /games`` request.

Top-level fields:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Field
     - Type
     - Description
   * - ``format_version``
     - integer
     - Schema version.  Increment on breaking changes.
   * - ``name``
     - string
     - Race display name (max 15 characters in original game; advised limit)
   * - ``plural_name``
     - string
     - Plural form (e.g., "Humanoids")
   * - ``prt``
     - string enum
     - Primary Racial Trait.  One of: ``CA``, ``JOAT``, ``IT``, ``IS``,
       ``SD``, ``WM``, ``PP``, ``SS``, ``HE``, ``AR``.  Internal byte
       values: HE=0, SS=1, WM=2, CA=3, IS=4, SD=5, PP=6, IT=7, AR=8,
       JOAT=9 (confirmed from ``analyze_r1.py``; CA=3 inferred, AR=8
       pending confirmation — see research task R1.1)
   * - ``lrts``
     - array of string enum
     - Lesser Racial Traits.  Any subset of the valid LRT identifiers.
   * - ``hab``
     - object
     - Habitat preferences.  See `Habitat Object`_ below.
   * - ``economy``
     - object
     - Economy parameters.  See `Economy Object`_ below.
   * - ``research_costs``
     - object
     - Per-field cost multiplier.  See `Research Costs Object`_ below.
   * - ``icon_index``
     - integer
     - Index into the race icon sprite sheet (0–based).

Habitat Object
~~~~~~~~~~~~~~

Each of the three axes (``gravity``, ``temperature``, ``radiation``) is
either an ``immune`` flag or a ``min``/``max`` preference range.

.. code-block:: json

   {
     "gravity":     { "immune": false, "min": 0.22, "max": 4.40 },
     "temperature": { "immune": false, "min": -60,  "max": 20   },
     "radiation":   { "immune": true                             }
   }

- Gravity values are from the ``Gravity_Map`` set (see
  :doc:`../mechanics/habitability`).
- Temperature is in °C, must be a multiple of 4, range [−200, 200].
- Radiation is an integer, range [0, 100].
- Range width for temperature must be ≥ 80°C when not immune.

Economy Object
~~~~~~~~~~~~~~

.. code-block:: json

   {
     "resource_production":        1000,
     "factory_production":         10,
     "factory_cost":               10,
     "factory_cheap_germanium":    false,
     "colonists_operate_factories": 10,
     "mine_production":            10,
     "mine_cost":                  5,
     "colonists_operate_mines":    10,
     "growth_rate":                15
   }

See :doc:`../mechanics/race_design` for valid ranges and defaults.

Research Costs Object
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "energy":        "normal",
     "weapons":       "cheap",
     "propulsion":    "normal",
     "construction":  "expensive",
     "electronics":   "normal",
     "biotechnology": "normal"
   }

Valid values: ``"cheap"``, ``"normal"``, ``"expensive"``.

Complete Example
~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "format_version": 1,
     "name": "Humanoid",
     "plural_name": "Humanoids",
     "prt": "JOAT",
     "lrts": ["IFE", "ISB"],
     "hab": {
       "gravity":     { "immune": false, "min": 0.22, "max": 4.40 },
       "temperature": { "immune": false, "min": -60,  "max": 20   },
       "radiation":   { "immune": false, "min": 15,   "max": 85   }
     },
     "economy": {
       "resource_production":        1000,
       "factory_production":         10,
       "factory_cost":               10,
       "factory_cheap_germanium":    false,
       "colonists_operate_factories": 10,
       "mine_production":            10,
       "mine_cost":                  5,
       "colonists_operate_mines":    10,
       "growth_rate":                15
     },
     "research_costs": {
       "energy":        "normal",
       "weapons":       "normal",
       "propulsion":    "normal",
       "construction":  "normal",
       "electronics":   "normal",
       "biotechnology": "normal"
     },
     "icon_index": 0
   }

Original ``.r`` File Import
----------------------------

The original |original| game saves race designs as binary ``.r`` files.
The engine (or a standalone import utility) must be able to read these and
produce an equivalent ``race.json``.

File Structure
~~~~~~~~~~~~~~

The ``.r`` file is a fixed-length binary record.  All multi-byte integers are
little-endian.

.. list-table::
   :header-rows: 1
   :widths: 10 15 75

   * - Offset
     - Size
     - Content
   * - 0
     - 2
     - Magic / version bytes.  Original game: ``0x0e 0x00`` (version 14).
   * - 2
     - 16
     - Race name, null-terminated ASCII.
   * - 18
     - 16
     - Plural name, null-terminated ASCII.
   * - 34
     - 1
     - PRT index (0–9; see :doc:`../mechanics/race_design` table)
   * - 35
     - 2
     - LRT bitmask (bit 0 = NRE, bit 1 = CE, … — see bit layout below)
   * - 37
     - 6
     - Habitat settings (3 × 2 bytes: each pair is ``min_index``/``max_index``
       into the discrete value tables; high bit set = immune)
   * - 43
     - 10
     - Economy parameters (5 × 2 bytes: resource_production, factory values ×
       3, mine values × 3, growth rate — exact byte layout TBD)
   * - 53
     - 1
     - Research cost flags (2 bits per field × 6 fields = 12 bits)
   * - 54
     - 1
     - Icon index
   * - 55
     - varies
     - Padding / trailing bytes (exact length TBD)

.. todo::

   Reverse-engineer the exact ``.r`` binary layout from the original
   executable.  Priority fields: LRT bitmask bit order, habitat byte layout,
   economy byte layout, research cost encoding.  Document in
   ``stars-reborn-research`` first, then promote confirmed layout here.

LRT Bitmask Bit Order
~~~~~~~~~~~~~~~~~~~~~

Confirmed via differential analysis of known-race ``.r1`` files
(``scripts/analyze_r1.py`` in ``stars-reborn-research``):

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - Bit
     - LRT
   * - 0
     - No Ramscoop Engines (NRE)
   * - 1
     - Improved Fuel Efficiency (IFE)
   * - 2
     - Cheap Engines (CE)
   * - 3
     - Total Terraforming (TT)
   * - 4
     - Only Basic Remote Mining (OBRM)
   * - 5
     - Advanced Remote Mining (ARM)
   * - 6
     - No Advanced Scanners (NAS)
   * - 7
     - Improved Starbases (ISB)
   * - 8
     - Low Starting Population (LSP)
   * - 9
     - Generalized Research (GR)
   * - 10
     - Bleeding Edge Technology (BET)
   * - 11
     - Ultimate Recycling (UR)
   * - 12
     - Regenerating Shields (RS)
   * - 13
     - Mineral Alchemy (MA)

.. note::

   Byte offset of the bitmask within the record payload is still TBD.
   See research task R1.2.

Import Validation
~~~~~~~~~~~~~~~~~

After converting a ``.r`` file to ``race.json`` the result must pass the same
validation as a hand-authored file:

1. PRT is in the valid set.
2. LRTs have no prerequisite violations.
3. Hab ranges are within allowed bounds; temperature range is ≥ 80°C if not
   immune.
4. Economy values are within allowed ranges.
5. Advantage point total is within the valid budget.

If the imported race fails validation (e.g., was created with a different
game version that allowed now-invalid combinations), the importer should
report specific errors rather than silently adjusting values.
