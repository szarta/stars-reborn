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

Original ``.r`` / ``.r1`` File Import
--------------------------------------

The original |original| game saves race designs as ``.r`` files (one per
player slot, numbered ``.r1``–``.r16``).  The engine ships an import utility
(``r1_to_json``, in ``stars-reborn-engine/engine/src/bin/``) that reads these
and emits the equivalent ``race.json``.

Container Format
~~~~~~~~~~~~~~~~

Each ``.r1`` file is a Stars! record container (the same format as ``.m``,
``.hst``, ``.xy`` files).  Record headers are 2-byte LE: high 6 bits = record
type, low 10 bits = payload length.  Payloads are XOR-encrypted with a
L'Ecuyer (1988) combined LCG seeded from the type-8 header record.

A race file contains exactly 3 records:
1. Type 8 (16-byte plaintext header — seeds the LCG)
2. Type 6 (race data payload — encrypted)
3. Type 0 (empty end-of-file marker)

Cipher
~~~~~~

L'Ecuyer combined LCG with two streams:

- s1: a=40014, m=2^31−85 (Schrage params q=53668, r=12211)
- s2: a=40692, m=2^31−249 (q=52774, r=3791)

Per 4-byte chunk: ``key = (new_s1 − new_s2) & 0xFFFFFFFF``.
Bytes are the 4 LE bytes of this 32-bit value.
Seeds are derived from bytes 12-13 of the type-8 payload; a small
pre-advance count is computed from other bytes in that payload.

Payload Field Map
~~~~~~~~~~~~~~~~~

The type-6 payload is a direct ``memcpy`` of a 192-byte in-memory struct
(confirmed via Ghidra decompilation of ``FUN_1070_551c``).

All multi-byte integers are little-endian.  All confirmed fields are 1 byte
unless noted.

.. list-table::
   :header-rows: 1
   :widths: 10 10 80

   * - Offset
     - Size
     - Content
   * - 0
     - 1
     - ``0xFF`` constant (magic/version marker)
   * - 16
     - 1
     - ``grav_center`` — gravity hab center (0–100 index; ``0xFF`` = immune)
   * - 17
     - 1
     - ``temp_center`` — temperature hab center
   * - 18
     - 1
     - ``rad_center`` — radiation hab center
   * - 19
     - 1
     - ``grav_min`` — gravity hab minimum index (0–100)
   * - 20
     - 1
     - ``temp_min`` — temperature hab minimum (0–100 scale)
   * - 21
     - 1
     - ``rad_min`` — radiation hab minimum (0–100 mR/yr)
   * - 22
     - 1
     - ``grav_max``
   * - 23
     - 1
     - ``temp_max``
   * - 24
     - 1
     - ``rad_max``
   * - 25
     - 1
     - ``growth_rate`` (raw integer %, e.g. 15 → 15%)
   * - 56
     - 1
     - ``0x0F`` constant (unknown purpose)
   * - 62
     - 1
     - ``resource_production / 100`` (multiply by 100 to get RP)
   * - 63
     - 1
     - ``factory_production``
   * - 64
     - 1
     - ``factory_cost``
   * - 65
     - 1
     - ``colonists_operate_factories`` (thousands, e.g. 10 → 10,000)
   * - 66
     - 1
     - ``mine_production``
   * - 67
     - 1
     - ``mine_cost``
   * - 68
     - 1
     - ``colonists_operate_mines``
   * - 69
     - 1
     - Leftover mines amount (meaning TBD)
   * - 70
     - 1
     - Energy research cost (0=Expensive, 1=Normal, 2=Cheap)
   * - 71
     - 1
     - Weapons research cost
   * - 72
     - 1
     - Propulsion research cost
   * - 73
     - 1
     - Construction research cost
   * - 74
     - 1
     - Electronics research cost
   * - 75
     - 1
     - Biotechnology research cost
   * - 76
     - 1
     - PRT index (HE=0, SS=1, WM=2, CA=3*, IS=4, SD=5, PP=6, IT=7, AR=8*, JOAT=9)
   * - 78
     - 2
     - LRT bitmask and icon_index — **encoding unconfirmed** (see R1.2)
   * - 81
     - 1
     - Flags: bit 7 = ``factory_cheap_germanium``, bit 5 = ``expensive_tech_boost``
   * - 112+
     - varies
     - Name section (see below)

``*`` CA=3 and AR=8 are inferred, not yet oracle-confirmed.

Habitat Encoding
~~~~~~~~~~~~~~~~

Immunity to an axis: all three bytes for that axis (center, min, max) = ``0xFF``.

Gravity index (0–100) maps to g values via the ``Gravity_Map`` lookup table
(see :doc:`../mechanics/habitability`).

Temperature scale: ``temp_°C = (index − 50) × 4``.
Range: index 0 = −200°C, index 50 = 0°C, index 100 = +200°C.

Radiation: direct 0–100 mR/yr.

Center byte is always ``floor((min + max) / 2)``; a bounds checker in Stars!
enforces this at save time.

Name Section
~~~~~~~~~~~~

The name section starts at payload offset 112 with a ``0x00`` constant byte,
followed by two name blocks (singular and plural).  Each block:

- **1-byte marker**: determines block type and size
  - 6 or 7 → preset name; ``marker`` data bytes follow (opaque lookup key)
  - 8, 9, … → user-typed name; ``marker`` data bytes follow, each encoding
    ``char = byte − 111`` (printable ASCII, base offset 111)
- **marker bytes of data**: the block body

Blocks are contiguous; plural block follows immediately after singular.
If plural marker is ``0``, no plural is stored and the importer defaults to
``singular + "s"``.

Preset name lookup keys (full data block, singular first):

.. code-block:: text

   Humanoid:   [183,222,219,22,116,214]     / [183,222,219,22,116,214,159]
   Antetheral: [176,106,42,50,129,95]       / [176,106,42,50,129,89]
   Insectoid:  [184,105,45,90,116,214]      / [184,105,45,90,116,214,159]
   Nucleotid:  [189,222,213,82,122,77,111]  / [189,222,213,82,122,77,105]
   Rabbitoid:  [193,29,77,68,167,77,111]    / [193,29,77,68,167,77,105]
   Silicanoid: [194,69,77,81,103,77,111]    / [194,69,77,81,103,77,105]

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
