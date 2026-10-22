Contributing
============

Development Setup
-----------------

::

    git clone <repo> stars-reborn
    cd stars-reborn
    pip install -e ".[dev,docs]"
    pytest tests/      # verify everything passes

Code Organization
-----------------

* Game logic goes in ``stars_reborn/engine/`` — no UI imports.
* UI code goes in ``stars_reborn/ui/`` — imports engine freely.
* Data loading/serialization goes in ``stars_reborn/data/``.
* Tests go in ``tests/`` — engine tests must not require a display (headless).

When adding a new mechanic:

1. Add the implementation to the appropriate ``engine/`` module.
2. Add tests in ``tests/``.
3. Document the formula in ``docs/mechanics/``.
4. If research validates a new value from the original game, note it in ``CHANGELOG.txt``.

Commit Messages
---------------

Follow conventional commits style:

* ``feat:`` — new feature
* ``fix:`` — bug fix
* ``refactor:`` — internal change, no behavior change
* ``test:`` — test additions or changes
* ``docs:`` — documentation only
* ``data:`` — changes to ``resources/`` data files

Branching
---------

* ``main`` — stable, always runs
* ``dev/phase-N`` — work in progress for a specific phase
* ``fix/description`` — bug fixes

Style
-----

* Python: PEP 8, 100-char line limit.
* Docstrings: one-line summary for simple functions; full docstring for anything involving
  a formula (include the formula and source).
* No type annotations required, but welcome where they clarify intent.
