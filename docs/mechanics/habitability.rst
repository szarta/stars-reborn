Habitability & Planet Value
===========================

Overview
--------

Every planet has three habitat axes. Every race has a preferred range on each
axis (or is immune to it). The **planet value** (−45% to +100%) summarizes how
hospitable the planet is for a given race. It directly controls population
growth rate and is the primary factor in colonization decisions.

Habitat Axes
------------

Gravity
~~~~~~~

- Displayed as: ``Xg`` (e.g., ``1.00g``, ``0.22g``, ``4.40g``)
- 101 discrete values: 0.12g to 8.00g (non-linear spacing)
- Normalized to 0–100 via the ``Gravity_Map`` lookup table (display value → index)

The mapping is **non-linear** and has a quirk at the low end: indices 1, 3, 5, 7,
and 10 are unreachable — no display value maps to them.  This double-increment
behavior appears to reflect logarithmic perception of gravity at low values.

This matters for **race file decoding**: if the stored value is a 0–100 index,
some index values will never appear in a valid race file.  See
:ref:`hab-race-file-encoding` below.

Complete Gravity_Map (display string → internal 0–100 index):

.. code-block:: text

   0.12g →   0    0.13g →   2    0.14g →   4    0.15g →   6    0.16g →   8
   0.17g →   9    0.18g →  11    0.19g →  12    0.20g →  13    0.21g →  14
   0.22g →  15    0.24g →  16    0.25g →  17    0.27g →  18    0.29g →  19
   0.31g →  20    0.33g →  21    0.36g →  22    0.40g →  23    0.44g →  24
   0.50g →  25    0.51g →  26    0.52g →  27    0.53g →  28    0.54g →  29
   0.55g →  30    0.56g →  31    0.58g →  32    0.59g →  33    0.60g →  34
   0.62g →  35    0.64g →  36    0.65g →  37    0.67g →  38    0.69g →  39
   0.71g →  40    0.73g →  41    0.75g →  42    0.78g →  43    0.80g →  44
   0.83g →  45    0.86g →  46    0.89g →  47    0.92g →  48    0.96g →  49
   1.00g →  50    1.04g →  51    1.08g →  52    1.12g →  53    1.16g →  54
   1.20g →  55    1.24g →  56    1.28g →  57    1.32g →  58    1.36g →  59
   1.40g →  60    1.44g →  61    1.48g →  62    1.52g →  63    1.56g →  64
   1.60g →  65    1.64g →  66    1.68g →  67    1.72g →  68    1.76g →  69
   1.80g →  70    1.84g →  71    1.88g →  72    1.92g →  73    1.96g →  74
   2.00g →  75    2.24g →  76    2.48g →  77    2.72g →  78    2.96g →  79
   3.20g →  80    3.44g →  81    3.68g →  82    3.92g →  83    4.16g →  84
   4.40g →  85    4.64g →  86    4.88g →  87    5.12g →  88    5.36g →  89
   5.60g →  90    5.84g →  91    6.08g →  92    6.32g →  93    6.56g →  94
   6.80g →  95    7.04g →  96    7.28g →  97    7.52g →  98    7.76g →  99
   8.00g → 100

   Unreachable indices (no display value maps to them): 1, 3, 5, 7, 10

Gravity display values have **ambiguous spots**: multiple click indices can
display the same g value (e.g. clicks 0–1 both show ``0.12g``, clicks 2–3 both
show ``0.13g``).  Converting from a displayed gravity string back to a click
index is therefore not always unambiguous without context.

**Inverse gravity function** (click index from float g value, after m.a@stars):

.. code-block:: javascript

   function getClicksFromGrav(grav) {
     grav *= 100;           // work in centigs
     var lowerHalf = 1;
     if (grav < 100) {
       grav = Math.floor(10000 / grav);   // invert sub-1g values
       lowerHalf = -1;
     }
     var result;
     if (grav < 200) {
       result = grav / 4 - 25;
     } else {
       result = (grav + 400) / 24;
     }
     result = Math.floor(50.9 + lowerHalf * result);
     if (result < 1) result = 1;   // one less ambiguity
     return result;
   }

**Source:** Validated against live Stars! game data in
``stars-reborn-research/maps/compare_formula_hab_to_actual.py``.

Temperature
~~~~~~~~~~~

- Displayed as: ``X°C`` (e.g., ``0°C``, ``−140°C``, ``200°C``)
- Range: −200°C to +200°C, step 4 (101 discrete values)
- Normalized to 0–100 via linear formula:

  .. code-block:: python

     normalized = floor(temp / 4.0 + 50)

  Example: 0°C → 50, −200°C → 0, +200°C → 100

Radiation
~~~~~~~~~

- Displayed as: ``X mR/yr``
- Range: 0 to 100 mR/yr (integer)
- No normalization needed — value IS the 0–100 position

Race Habitat Ranges
-------------------

Each race defines a minimum and maximum for each axis. The **midpoint** of this
range is the race's ideal value. A planet at the midpoint of all three axes
receives the maximum planet value for that race.

Race range constraints:

- Gravity: min 0.12g, max 8.00g; range must span at least some value
- Temperature: range must be at least 80°C wide
- Radiation: min 0, max 100

Planet Value Formula
--------------------

**Source:** m.a@stars, starsautohost.org forum (reverse-engineered).
`Thread #2299 <http://starsautohost.org/sahforum2/index.php?t=msg&th=2299&rid=625&S=ee625fe2bec617564d7c694e9c5379c5&pl_view=&start=0#msg_19643>`_

**Status:** Oracle-confirmed (R3 ``hab_proximity_growth_rate``).  A faithful
re-implementation of the integer-arithmetic formula below produces a
**byte-perfect match** on all 241 planets observed by 4 AI races at year 30
of a Small/Normal/Farther map (seed 42), spanning positive, negative, and
clamped value cases.  The same formula appears as ``Hab%`` in advfaq §4.11
(Bill Butler, "Race wizard - Hab studies", 1998-04-10) — algebraically
equivalent, with the floating-point form
``Hab% = √[(1−g)² + (1−t)² + (1−r)²] · (1−x)(1−y)(1−z) / √3``
where ``g, t, r`` are fractional distances from range center and
``x, y, z = max(0, frac − 0.5)``.  The advfaq presentation gives 100% at
center exactly: ``√3/√3 · 1·1·1 = 1.0``; an earlier worry that the formula
was inverted was a hand-calculation slip.

.. note::

   The community C implementation (``planet_hab.c``) required a correction to
   the ideality calculation: the original posted code had an incorrect double-cast
   in the ideality path; the integer math path
   ``ideality = ideality * (habRadius*2 - margin) / (habRadius*2)``
   produces correct results and is what this formula uses.

.. code-block:: python

   def calculate_planet_value(planet, race):
       # For each of the three axes:
       #   1. Compute distance from planet value to range center (normalized 0-100)
       #   2. If within range: contribute positive points + ideality correction
       #   3. If outside range by ≤15: contribute negative "red" points
       #   4. If outside range by >15: clamp negative at -15
       #
       # Final value:
       #   if any red_value > 0: return -(red_value)   [negative planet value]
       #   else: return floor(sqrt(planet_value_points / 3) + 0.9) × ideality / 10000

Positive value (per axis)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   ex_center = 100 * distance_to_center // hab_radius
   ex_center = 100 - ex_center
   planet_value_points += ex_center * ex_center      # max 10000 per axis

   margin = (distance_to_center * 2) - hab_radius
   if margin > 0:
       ideality *= ((hab_radius * 2) - margin) / (hab_radius * 2)

- Perfect center on all three axes: ``planet_value_points = 30000``, ``ideality = 10000``
- Final value = ``sqrt(30000/3 + 0.9) × 1.0 ≈ 100``

Negative value (per axis)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   negative = distance_to_center - hab_radius      # how far outside the range
   negative = min(negative, 15)                    # cap at 15 per axis
   red_value += negative

- Maximum negative: −45% (all three axes at 15+ units outside range)
- A single red axis makes the whole planet negative

Immune axes
~~~~~~~~~~~

An immune race receives the full 10000 points from that axis regardless of
planet value. Immunity to all three axes = planet value always 100%.

Planet Value Display
--------------------

.. list-table::
   :header-rows: 1
   :widths: 15 15 50

   * - Value
     - Color
     - Meaning
   * - > 0%
     - Green
     - Habitable; grow at ``min(growth_rate, value)%`` per year
   * - 0%
     - White
     - Zero growth (border of habitable range)
   * - < 0%
     - Red
     - Population dies at ``value%`` per year

Validation
----------

The formula has been validated against observed |original| games. See
``data/planet_samples/`` for CSV exports of planet hab values vs. calculated
planet values for known race configurations.

Example validation case (Tiny/Normal map, Humanoid race: grav 0.22–4.40g,
temp −140–140°C, rad 15–85 mR/yr):

- Planet ``Scorpius``: grav 2.96g, temp −32°C, rad 45 → observed 45%, formula gives 45% ✓
- Planet ``Planet 9``: grav 0.65g, temp 12°C, rad 46 → observed 83%, formula gives 83% ✓

.. _hab-race-file-encoding:

Race File Encoding — Hypothesis
---------------------------------

The race record (binary type-6, 131 bytes) stores hab range min/max for each axis.
The exact byte offsets within the type-6 payload are **not yet decoded**, but
``RACEWIZARDDLG1–6`` (``10e0:03ac``–``10e0:3bae``) is the confirmed Ghidra address
range for the race designer wizard, noted to contain "hab range encoding."

Two plausible encodings for the stored gravity value:

1. **Stored as 0–100 index** — the normalized internal value from ``Gravity_Map``.
   Display value is recovered by the inverse lookup.  This is the most likely
   encoding given that all three hab axes work on the same 0–100 scale internally.

2. **Stored as display value** — e.g., gravity as a fixed-point integer (e.g.,
   ``0.22g`` stored as ``22`` after multiplying by 100), temperature as a signed
   integer in °C, radiation as a raw 0–100 byte.

**Community evidence for encoding (1):** The starsautohost.org reference C
implementation (``planet_hab.c``, m.a@stars, 2299) defines:

.. code-block:: c

   struct playerDataStruct {
     BYTE lowerHab[3];  // from 0 to 100 "clicks", -1 for immunity
     BYTE upperHab[3];
   };

The explicit "0 to 100 clicks, -1 for immunity" comment strongly suggests the
author knew the race file stores hab ranges as 0–100 integers, not display values.

**Race file likely stores a third center byte per axis.** Forum discussion on the
same thread (Kotk, m.a@stars) identifies "3 bytes" of potential waste as
"Radiation, Gravity and Temperature" — one center byte per axis.  The hypothesis
is that the race file layout per axis is:

.. code-block:: text

   lowerHab  (1 byte, 0–100 or -1)
   upperHab  (1 byte, 0–100 or -1)
   centerHab (1 byte, 0–100 or -1)   ← always == (lower+upper)/2 in practice

**Bounds checker confirmed:** ConstB (forum thread) notes a bounds-checker inside
Stars! validates hab center correctness; PricklyPea confirms "it checks that it
is in the middle."  Encoding an off-center hab range would be detected and
rejected.  The formula code nonetheless handles arbitrary centers, suggesting the
design originally allowed them.

The unreachable gravity indices (1, 3, 5, 7, 10) remain the hard diagnostic: if
a decoded type-6 byte lands on one of those values, encoding (1) is ruled out.

.. todo:: Decode hab range bytes in type-6 record via ``RACEWIZARDDLG`` analysis
          and resolve which encoding is used. Confirm whether center byte is
          stored separately (9 hab bytes total) or derived. Cross-reference with
          ``binary_map.rst``.

Open Questions
--------------

.. todo:: Confirm exact rounding behavior at boundary cases (floor vs round)

.. todo:: Confirm behavior when ``hab_radius = 0`` (single-point hab range)

.. todo:: AR (Alternate Reality) race: does planet value work differently?

.. todo:: **Asymmetric hab ranges** — the formula code handles an explicit center
          byte that need not equal ``(min + max) / 2``, but a confirmed bounds
          checker in Stars! enforces centering in practice.  m.a@stars speculates
          this was an earlier design that was later locked down.  Confirm via
          ``RACEWIZARDDLG`` whether the center byte is stored separately and
          whether the bounds check is in the race wizard or the host engine.


.. _stars-reborn-impl:

Implementation Notes (from stars-reborn)
----------------------------------------

Planet Value Formula
--------------------
Each planet has three habitat readings: gravity (g), temperature (t), and radiation (r),
each on a 0–100 integer scale. Your race has a range [min, max] on each axis (or "immune").
Planet value is the product of three per-axis values, normalized to [-45, 100]:
For each axis:
.. code-block:: text
    If immune:
        axis_value = 100
    Else:
        mid = (min + max) / 2
        range_half = (max - min) / 2
        If planet_val is within [min, max]:
            distance_from_mid = abs(planet_val - mid)
            axis_value = 100 * (1 - distance_from_mid / range_half)
        Else (out of range):
            out_of_range = min(abs(planet_val - min), abs(planet_val - max))
            axis_value = -45 * out_of_range / 15   (capped at -45)
Overall planet_value = product formula combining three axis values.
**Reference:** ``sr-old/reference/research/`` — ``planet_hab.c`` (community C implementation),
validated against live Stars! game data in ``stars-research/planet_data/``.
Gravity Map
-----------
Gravity values are non-linear. The 0–100 integer scale maps to g values:
.. code-block:: text
    0  → 0.12g       25 → 0.50g       50 → 1.00g
    10 → 0.20g       30 → 0.55g       55 → 1.12g
    20 → 0.36g       40 → 0.71g       75 → 2.24g
                                       100 → 8.00g
Full mapping in ``stars_reborn/engine/space.py`` ``Gravity_Map``.
Temperature Map
---------------
Temperature maps linearly: ``temperature = (scale_value - 50) * 4``
Range: scale 0 = -200°C, scale 50 = 0°C, scale 100 = +200°C.
Radiation Map
-------------
Radiation maps linearly (1:1 with mR/yr): scale 0 = 0 mR/yr, scale 100 = 100 mR/yr.
Homeworld Initialization
------------------------
A player's homeworld is always set to a planet value of exactly 100% for that race:
* Gravity set to the midpoint of the race's gravity range (or 50 if immune)
* Temperature set to the midpoint of the race's temperature range (or 50 if immune)
* Radiation set to the midpoint of the race's radiation range (or 50 if immune)
Population Capacity
-------------------
Maximum population per planet is determined by planet size (set at universe generation):
   * - Planet Size
     - Max Population
   * - Tiny
     - 100,000
   * - Small
     - 200,000
   * - Medium
     - 500,000
   * - Large
     - 1,000,000
   * - Huge
     - 2,000,000
(These are approximate; exact values TBD from original game research.)
