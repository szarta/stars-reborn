"""
ui/dialogs/_components_common.py

Small Qt helpers shared by the Technology Browser and the Ship Designer's
component views: resolving a component's icon pixmap. Kept separate so both
dialogs render component icons the same way.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

import os

from PySide6.QtGui import QColor, QPixmap

from ...data.technologies import icon_filename
from ...rendering.enumerations import ResourcePaths


def component_icon(category: str, name: str) -> QPixmap:
    """Resolve a component's icon pixmap.

    Icons live under ``assets/png/components/<category>/<Name-With-Dashes>.png``
    (e.g. ``engines/Quick-Jump-5.png``). Only a few categories ship icons today;
    a miss returns a neutral placeholder tile. When the engine starts emitting an
    ``icon`` field on tech items (schema reserves it; see icon-convention task
    #88) this name heuristic can be replaced by a direct path.
    """
    path = os.path.join(ResourcePaths.ComponentsPath, category, icon_filename(name))
    pix = QPixmap(path)
    if not pix.isNull():
        return pix
    placeholder = QPixmap(64, 64)
    placeholder.fill(QColor("#2b2b2b"))
    return placeholder
