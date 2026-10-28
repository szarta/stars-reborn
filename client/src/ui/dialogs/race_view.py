"""
ui/dialogs/race_view.py

Race view (F8) — a read-only summary of the viewing player's race.

Shows the race's identity (name, PRT, LRTs), habitability ranges, economy
parameters, and per-field research costs, grouped into sections. Reads the
race from the turn file (client/src/data/defaults.race_summary); the engine is
authoritative for the race definition.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
)

from ...data.defaults import race_summary


class RaceViewDialog(QDialog):
    """Modal read-only Race view."""

    def __init__(self, race: dict | None, parent=None):
        super().__init__(parent)
        name = (race or {}).get("name")
        self.setWindowTitle(f"Race — {name}" if name else "Race")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        sections = race_summary(race)

        if not sections:
            layout.addWidget(QLabel("No race data available."))
        else:
            for title, rows in sections:
                box = QGroupBox(title)
                form = QFormLayout(box)
                for label, value in rows:
                    form.addRow(f"{label}:", QLabel(value))
                layout.addWidget(box)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        buttons.setCenterButtons(True)
        layout.addWidget(buttons)
        layout.setAlignment(Qt.AlignTop)
