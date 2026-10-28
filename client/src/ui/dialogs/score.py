"""
ui/dialogs/score.py

Score dialog (F10) — the viewing player's F10 score breakdown.

Shows one row per scoring category (planets, starbases, ships, tech, resources)
with its raw count and the points it contributes, plus the total score. Points
come from the engine (client/src/data/defaults.ScoreData); the client never
recomputes the formula. See docs/mechanics/victory.rst.

Own score only — the multi-player scoreboard with ranks and opponents' scores is
gated on the public-player-scores game flag, which the engine does not model
yet. Starbase and ship rows read 0 until those models land in the engine.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ...data.defaults import ScoreData, score_rows


class ScoreDialog(QDialog):
    """Modal F10 Score window for a single player's breakdown."""

    def __init__(self, score: ScoreData | None, year: int | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Score" if year is None else f"Score — Year {year}")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)

        if score is None:
            layout.addWidget(QLabel("No score available for this turn."))
            self._add_buttons(layout)
            return

        rows = score_rows(score)
        table = QTableWidget(len(rows), 3)
        table.setHorizontalHeaderLabels(["Category", "Count", "Points"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        for r, (label, count, points) in enumerate(rows):
            table.setItem(r, 0, QTableWidgetItem(label))
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            points_item = QTableWidgetItem(str(points))
            points_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(r, 1, count_item)
            table.setItem(r, 2, points_item)
        table.resizeColumnsToContents()
        layout.addWidget(table)

        total = QLabel(f"<b>Total Score: {score.total}</b>")
        total.setAlignment(Qt.AlignRight)
        layout.addWidget(total)

        self._add_buttons(layout)

    def _add_buttons(self, layout):
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
