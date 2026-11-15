"""
ui/dialogs/fleet_report.py

Fleets report (F3) — sortable tables of fleets from the current turn snapshot.

Two reports share one base: the player's **own** fleets (full detail) and
**Others' Fleets** — foreign fleets the player has detected by scanning
(partial, scan-depth gated, so name/ship-count may be unknown). Both are built
from the turn file (client/src/data/defaults); no engine call. Double-clicking a
row that orbits a known planet jumps the map there via ``fleet_goto`` (a fleet
in deep space has no map marker yet, so its row is informational only).

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

from ...data.defaults import fleet_report_rows, scanned_fleet_report_rows


def _cell(value, numeric: bool, *, placeholder: str = "n/a") -> QTableWidgetItem:
    """A read-only table cell. Numeric cells store the number so the column
    sorts numerically and right-aligns; a ``None`` numeric value shows
    ``placeholder`` and sorts low."""
    item = QTableWidgetItem()
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    if numeric:
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if value is None:
            item.setData(Qt.ItemDataRole.DisplayRole, placeholder)
        else:
            item.setData(Qt.ItemDataRole.DisplayRole, int(value))
    else:
        item.setData(Qt.ItemDataRole.DisplayRole, str(value))
    return item


class _FleetReportBase(QDialog):
    """A fleet table with jump-to-planet on double-click.

    Subclasses supply the window title, the ``(header, row-key, numeric)``
    column spec, the rows, and the empty-state message.
    """

    # Planet id to jump the map to (the orbited planet of a double-clicked row).
    fleet_goto = Signal(int)

    _COLUMNS: list[tuple[str, str, bool]] = []

    def __init__(self, title: str, rows: list[dict], empty_msg: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(640, 400)

        layout = QVBoxLayout(self)

        if not rows:
            layout.addWidget(QLabel(empty_msg))
            self._add_buttons(layout)
            return

        table = QTableWidget(len(rows), len(self._COLUMNS))
        table.setHorizontalHeaderLabels([c[0] for c in self._COLUMNS])
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setSortingEnabled(False)  # fill first, then enable (Qt guidance)
        for r, row in enumerate(rows):
            for c, (_, key, numeric) in enumerate(self._COLUMNS):
                item = _cell(row[key], numeric)
                if c == 0:
                    # Stash the orbited planet id (or None) for jump-to-planet.
                    item.setData(Qt.ItemDataRole.UserRole, row.get("orbiting_planet_id"))
                table.setItem(r, c, item)
        table.setSortingEnabled(True)
        table.sortItems(0, Qt.SortOrder.AscendingOrder)
        table.resizeColumnsToContents()
        table.itemDoubleClicked.connect(self._on_activate)
        self._table = table
        layout.addWidget(table)

        self._add_buttons(layout)

    def _on_activate(self, item):
        planet_id = self._table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        if planet_id is not None:
            self.fleet_goto.emit(int(planet_id))
            self.accept()

    def _add_buttons(self, layout):
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class FleetReportDialog(_FleetReportBase):
    """F3 Fleets report — the player's own fleets."""

    _COLUMNS = [
        ("Name", "name", False),
        ("Location", "location", False),
        ("Ships", "ships", True),
        ("Fuel", "fuel", True),
        ("Cargo", "cargo", True),
        ("Orders", "orders", False),
    ]

    def __init__(self, fleets, planets, parent=None):
        super().__init__(
            "Fleets",
            fleet_report_rows(fleets, planets),
            "You have no fleets.",
            parent,
        )


class OthersFleetReportDialog(_FleetReportBase):
    """F3 Others' Fleets report — detected foreign fleets (partial intel)."""

    _COLUMNS = [
        ("Name", "name", False),
        ("Owner", "owner", False),
        ("Location", "location", False),
        ("Ships", "ships", True),
        ("Last Seen", "age", True),
    ]

    def __init__(self, scanned_fleets, planets, parent=None):
        super().__init__(
            "Others' Fleets",
            scanned_fleet_report_rows(scanned_fleets, planets),
            "No foreign fleets have been detected.",
            parent,
        )
