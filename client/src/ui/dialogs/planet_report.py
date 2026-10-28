"""
ui/dialogs/planet_report.py

Planets report (F3) — a sortable table of the planets the player can see.

Built entirely from the current turn snapshot (client/src/data/defaults
.PlanetData); no engine call. Columns cover the fields the turn file provides
today; double-clicking a row jumps the map to that planet via
``planet_activated``. Foreign (observed-but-unowned) planets appear once
scanning surfaces them — the row builder already includes any observed planet.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ...data.defaults import planet_report_rows

# (header, row-key, numeric?) in display order.
_COLUMNS = [
    ("Name", "name", False),
    ("Value", "value", True),
    ("Population", "population", True),
    ("Resources", "resources", True),
    ("Mines", "mines", True),
    ("Factories", "factories", True),
    ("Ironium", "ironium", True),
    ("Boranium", "boranium", True),
    ("Germanium", "germanium", True),
]


def _cell(value, numeric: bool) -> QTableWidgetItem:
    """A table cell. Numeric cells store the number as the display datum so the
    column sorts numerically (not lexically) and right-aligns; a missing numeric
    value shows 'n/a' and sorts as -1."""
    item = QTableWidgetItem()
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    if numeric:
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setData(Qt.ItemDataRole.DisplayRole, -1 if value is None else int(value))
        if value is None:
            item.setData(Qt.ItemDataRole.DisplayRole, "n/a")
    else:
        item.setData(Qt.ItemDataRole.DisplayRole, str(value))
    return item


class PlanetReportDialog(QDialog):
    """Modal F3 Planets report. Double-click a row to jump to that planet."""

    # Planet id of a double-clicked row.
    planet_activated = Signal(int)

    def __init__(self, planets, player_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Planets")
        self.resize(640, 400)

        rows = planet_report_rows(planets, player_id)
        layout = QVBoxLayout(self)

        if not rows:
            layout.addWidget(QLabel("No planets to report."))
            self._add_buttons(layout)
            return

        table = QTableWidget(len(rows), len(_COLUMNS))
        table.setHorizontalHeaderLabels([c[0] for c in _COLUMNS])
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setSortingEnabled(False)  # fill first, then enable (Qt guidance)
        for r, row in enumerate(rows):
            for c, (_, key, numeric) in enumerate(_COLUMNS):
                item = _cell(row[key], numeric)
                if c == 0:
                    # Stash the planet id on the name cell for activation.
                    item.setData(Qt.ItemDataRole.UserRole, row["id"])
                table.setItem(r, c, item)
        table.setSortingEnabled(True)
        table.sortItems(0, Qt.SortOrder.AscendingOrder)  # name A->Z by default
        table.resizeColumnsToContents()
        table.itemDoubleClicked.connect(self._on_activate)
        self._table = table
        layout.addWidget(table)

        self._add_buttons(layout)

    def _on_activate(self, item):
        pid = self._table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        if pid is not None:
            self.planet_activated.emit(int(pid))
            self.accept()

    def _add_buttons(self, layout):
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
