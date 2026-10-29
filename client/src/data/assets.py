"""
data/assets.py

Pure (Qt-free) resolution of icon asset paths from the engine's stable slugs.
Icons are *client-derived* from the identity the engine already serves — no
``icon`` field on the wire — using one documented convention (see
docs/reference/assets.rst):

- Component icons: ``components/<category-slug>/<part-slug>.png``
  (e.g. ``engines/quick_jump_5.png``), keyed by the ``category`` and ``slug``
  from ``GET /model/technologies``.
- Hull icons: ``hulls/<hull-slug>-<variant>.png`` (e.g. ``battle_cruiser-1.png``),
  keyed by the ``slug`` from ``GET /model/ships/hulls`` or
  ``/model/starbase/hulls``, with a 1-based ``variant`` (a hull has one or more
  interchangeable icon variants, used by the Ship Designer and by AI fleets).

Slugs are lower_snake and filename-safe by construction, so no escaping is
needed and names with punctuation (e.g. "Settler's Delight" → ``settlers_delight``)
resolve losslessly. Keeping the path logic here (not in Qt code) makes it
unit-testable headless.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

import re
from pathlib import Path

_HULL_VARIANT_RE = re.compile(r"^(?P<slug>.+)-(?P<variant>\d+)$")


def component_icon_relpath(category: str, slug: str) -> str:
    """Relative icon path for a component: ``<category>/<slug>.png``."""
    return f"{category}/{slug}.png"


def hull_icon_filename(slug: str, variant: int = 1) -> str:
    """Icon filename for a hull variant: ``<slug>-<variant>.png``."""
    return f"{slug}-{variant}.png"


def parse_hull_icon(filename: str) -> tuple[str, int] | None:
    """Split a hull icon filename into ``(slug, variant)``, or ``None``.

    ``"battle_cruiser-1.png"`` → ``("battle_cruiser", 1)``. The variant is the
    trailing ``-<digits>``; a hull slug is lower_snake and never ends in
    ``-<digits>``, so the split is unambiguous.
    """
    stem = filename[:-4] if filename.endswith(".png") else filename
    m = _HULL_VARIANT_RE.match(stem)
    if not m:
        return None
    return m.group("slug"), int(m.group("variant"))


def hull_variants(hulls_dir: Path, slug: str) -> list[int]:
    """Variant numbers available for ``slug`` in ``hulls_dir``, ascending.

    Empty when the hull has no art yet (the caller falls back to a placeholder).
    """
    variants: list[int] = []
    for png in Path(hulls_dir).glob(f"{slug}-*.png"):
        parsed = parse_hull_icon(png.name)
        if parsed is not None and parsed[0] == slug:
            variants.append(parsed[1])
    return sorted(variants)
