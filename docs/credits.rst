.. _credits:

Credits & Acknowledgements
===========================

.. note::
   This file is the authoritative source for all credits and attributions in the
   Stars Reborn project. ``stars-reborn-game/README.md`` and the in-game About
   dialog both derive from here.

Original Game
-------------

Stars Reborn is a clone of **Stars!**, created by **Jeff Johnson** and **Jeff McBride**
and published by Empire Interactive Entertainment (1996). This project is not endorsed
or sponsored in any way by the original authors or copyright holders.

Jeff McBride additionally contributed authoritative design documentation to the Stars!
community via the ``rec.games.computer.stars`` newsgroup and the FreeStars project,
including the canonical turn resolution order (``EventOrder2.txt``) and scrap-tech
algorithm (``ScrapTech.txt``). These documents directly inform this implementation.

Community Researchers
----------------------

The following individuals reverse-engineered, documented, and published Stars! game
mechanics over nearly 30 years. This project stands on their accumulated work.

**Art Lathrop** (stars.arglos.net)
   Published in-depth articles on battle targeting and attractiveness formulae,
   race design strategy, chaff mechanics, and mineral concentration statistics.
   His site is the primary source for several unconfirmed formulas under
   active verification.

**Bill Butler**
   Reverse-engineered the ground combat formula, planet value formula, and
   torpedo/missile accuracy rounding calculations. His published results are
   a primary reference for those mechanics.

**James McGuigan**
   Author of the *Stars! FAQ v1.9.6* (2002), the most comprehensive community
   reference for Stars! mechanics, consolidating research from the
   ``rec.games.computer.stars`` newsgroup.

**Dave Johnston**
   Author of the *Advanced & Technical FAQ*, consolidated into McGuigan's FAQ.
   Primary source for many deep-mechanics entries.

**Jason Cawley**
   Community contributor; published the population growth capacity factor formula
   and other growth-related mechanics.

**Alan L. Kolaga**
   Published mineral concentration distribution charts derived from a
   100M+ planet statistical sample, used to validate universe generation.

**S.B. Posey** (SBPosey)
   Contributed turn resolution observations and formula details via the
   SAH Forum.

**XyliGUN**
   Documented the binary file block type registry (2011), a primary reference
   for ``.m``/``.hst``/``.x`` file format reverse-engineering.

Prior Clone Efforts
-------------------

**FreeStars** (`github.com/vkholodkov/freestars <https://github.com/vkholodkov/freestars>`_)
   C++ re-implementation of the Stars! game engine. Its source code and the
   canonical game documents it preserves (``EventOrder2.txt``, ``ScrapTech.txt``)
   are a primary research reference.

**stars-4x organization** (`github.com/stars-4x <https://github.com/stars-4x>`_)
   Maintained decompiled Stars! utilities (``StarsHostCreator``,
   ``StarsHostEditor``, ``StarsSupremacyHost``), the ``starsapi`` Java API with
   technology item data, and the ``Structure XML`` field-level binary block
   definitions. These are key references for file format and data model work.

Community Resources
-------------------

**Stars! Auto Host (SAH) Forum** (starsautohost.org)
   The primary active community forum. The Academy section hosts authoritative
   threads on file formats, known bugs, turn order, and battle board mechanics.

**Stars! Auto Host Wiki** (wiki.starsautohost.org)
   File format definitions and community tool downloads.

**rec.games.computer.stars** (Usenet newsgroup, 1995–2001)
   Original developer posts and early community research. Archived posts are
   a primary source for pre-FAQ mechanic documentation.

Technology
----------

Stars Reborn is built on the following open-source technologies:

- `Rust <https://www.rust-lang.org/>`_ and the Rust ecosystem
  (axum, tokio, serde, rayon, and related crates)
- `Python <https://www.python.org/>`_ and
  `PySide6 <https://wiki.qt.io/Qt_for_Python>`_ (Qt6)
- `JSON Schema <https://json-schema.org/>`_

Asset Attributions
------------------

.. TODO: populate as assets are created or sourced. Each entry should include
   the asset name/type, source URL, author, and license.
