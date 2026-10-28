"""
ui/dialogs/find.py

Find dialog (Ctrl+F) — jump the map to a planet by name.

Type to filter the planet list (case-insensitive substring); pick a planet and
the dialog emits ``planet_activated`` so the host can centre the map and select
it (MainWindow._on_planet_nav). Searches all planets, observed or not — names
come from the shared .xy data. Fleet search is added when the fleet model lands
(#155).

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from ...data.defaults import find_planet_matches


class FindDialog(QDialog):
    """Modal Find dialog: filter planets by name and jump to one."""

    # Planet id of the chosen planet.
    planet_activated = Signal(int)

    def __init__(self, planets, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find")
        self.resize(280, 360)
        self._planets = planets

        layout = QVBoxLayout(self)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Planet name")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._refilter)
        self._search.returnPressed.connect(self._activate_current)
        layout.addWidget(self._search)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(lambda _item: self._activate_current())
        layout.addWidget(self._list)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._activate_current)
        self._buttons.rejected.connect(self.reject)
        layout.addWidget(self._buttons)

        self._refilter("")
        self._search.setFocus()

    def _refilter(self, text: str):
        """Repopulate the list from the current query and select the first row,
        so Enter/OK jumps to the top match without extra clicks."""
        self._list.clear()
        for pid, name in find_planet_matches(self._planets, text):
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, pid)
            self._list.addItem(item)
        if self._list.count():
            self._list.setCurrentRow(0)
        ok = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok.setEnabled(self._list.count() > 0)

    def _activate_current(self):
        item = self._list.currentItem()
        if item is None:
            return
        self.planet_activated.emit(int(item.data(Qt.ItemDataRole.UserRole)))
        self.accept()
