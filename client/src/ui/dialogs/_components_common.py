"""
ui/dialogs/_components_common.py

Small Qt helpers shared by the Technology Browser and the Ship Designer:
resolving component and hull icon pixmaps from the engine's slugs. The path
convention is defined (Qt-free) in :mod:`src.data.assets`; this layer only wraps
it in ``QPixmap`` and supplies the on-disk root from ``ResourcePaths``.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

import os

from PySide6.QtGui import QColor, QPixmap

from ...data.assets import component_icon_relpath, hull_icon_filename, hull_variants
from ...rendering.enumerations import ResourcePaths


def _placeholder() -> QPixmap:
    pix = QPixmap(64, 64)
    pix.fill(QColor("#2b2b2b"))
    return pix


def component_icon(category: str, slug: str) -> QPixmap:
    """Resolve a component's icon pixmap by ``category`` + ``slug``.

    Icons live under ``assets/png/components/<category>/<slug>.png`` (e.g.
    ``engines/quick_jump_5.png``). Only a few categories ship icons today; a
    miss returns a neutral placeholder tile (see the icon-asset pipeline in
    docs/reference/assets.rst; missing artwork is filled by the icon-generation
    pass).
    """
    if not slug:
        return _placeholder()
    path = os.path.join(ResourcePaths.ComponentsPath, component_icon_relpath(category, slug))
    pix = QPixmap(path)
    return pix if not pix.isNull() else _placeholder()


def hull_icon(slug: str, variant: int = 1) -> QPixmap:
    """Resolve a hull's icon pixmap by ``slug`` and 1-based ``variant``.

    Icons live under ``assets/png/hulls/<slug>-<variant>.png`` (e.g.
    ``battle_cruiser-1.png``). A miss returns a neutral placeholder tile.
    """
    if not slug:
        return _placeholder()
    path = os.path.join(ResourcePaths.HullsPath, hull_icon_filename(slug, variant))
    pix = QPixmap(path)
    return pix if not pix.isNull() else _placeholder()


def available_hull_variants(slug: str) -> list[int]:
    """Variant numbers that have art for ``slug`` (ascending; empty if none)."""
    if not slug:
        return []
    return hull_variants(ResourcePaths.HullsPath, slug)
