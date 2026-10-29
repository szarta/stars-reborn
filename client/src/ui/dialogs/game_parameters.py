"""
ui/dialogs/game_parameters.py

Game Parameters — a read-only summary of this game's settings.

Shows the parameters the client can see today (game name, year, universe size,
planet count). The rest of the original dialog's settings — victory conditions,
play flags, the player roster, and difficulty — are not persisted by the engine
yet, so they are omitted until it serializes game settings (engine follow-up).

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)

from ...data.defaults import game_parameters_rows


class GameParametersDialog(QDialog):
    """Modal read-only Game Parameters dialog."""

    def __init__(self, game_name, year, universe_w, universe_h, planet_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Parameters")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        for label, value in game_parameters_rows(
            game_name, year, universe_w, universe_h, planet_count
        ):
            form.addRow(f"{label}:", QLabel(value))
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
