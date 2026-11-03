"""
ui/dialogs/production_picker.py

Production add-item picker — choose a buildable (and quantity) to insert into a
planet's production queue.

Opened by the Production section's Add button. The list is populated from the
engine's ``GET /model/buildables`` registry (already indexed into the section
via ``set_buildables``), grouped under fixed category headers: Installations,
Auto Build, Ship Designs. Picking an item and a quantity and accepting hands
back ``(build_object_id, quantity)``; the section inserts it at the selected
queue position and submits through its existing ``queue_changed`` path.

Auto-build items are standing orders rather than counted builds, so the quantity
is locked to 1 while one is selected. Ship-design slots come straight from the
registry; narrowing them to the player's actual designs is the engine's job as
it serializes designs (tracked separately).

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QVBoxLayout,
)

from ..info_panel import grouped_buildables

# Qt item-data roles for a buildable row.
_ROLE_ID = Qt.ItemDataRole.UserRole  # build-object-id (int)
_ROLE_CATEGORY = Qt.ItemDataRole.UserRole + 1  # category slug (str)

_MAX_QUANTITY = 99999


class ProductionPickerDialog(QDialog):
    """Modal picker: select one buildable and a quantity to add to the queue."""

    # (build_object_id, quantity) for the chosen buildable.
    item_chosen = Signal(int, int)

    def __init__(self, buildables, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add to Production Queue")
        self.resize(300, 380)
        self._selected = None  # (oid, qty) once accepted

        layout = QVBoxLayout(self)

        self._list = QListWidget()
        self._list.currentItemChanged.connect(lambda *_: self._on_selection_changed())
        self._list.itemDoubleClicked.connect(lambda _item: self._accept_current())
        layout.addWidget(self._list)

        qty_row = QHBoxLayout()
        qty_row.addWidget(QLabel("Quantity:"))
        self._qty = QSpinBox()
        self._qty.setRange(1, _MAX_QUANTITY)
        self._qty.setValue(1)
        qty_row.addWidget(self._qty)
        qty_row.addStretch(1)
        layout.addLayout(qty_row)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._accept_current)
        self._buttons.rejected.connect(self.reject)
        layout.addWidget(self._buttons)

        self._populate(buildables)
        self._on_selection_changed()

    # ── population ───────────────────────────────────────────────────────────
    def _populate(self, buildables):
        """Fill the list with group-header rows and selectable buildable rows."""
        self._list.clear()
        first_item_row = None
        for label, items in grouped_buildables(buildables):
            self._list.addItem(self._make_header(label))
            for oid, name in items:
                row = QListWidgetItem(name)
                row.setData(_ROLE_ID, int(oid))
                cat = _category_for_label(label)
                if cat is not None:
                    row.setData(_ROLE_CATEGORY, cat)
                self._list.addItem(row)
                if first_item_row is None:
                    first_item_row = self._list.row(row)
        if first_item_row is not None:
            self._list.setCurrentRow(first_item_row)

    @staticmethod
    def _make_header(label: str) -> QListWidgetItem:
        """A non-selectable, bold group-header separator row."""
        item = QListWidgetItem(label)
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        return item

    # ── selection / accept ─────────────────────────────────────────────────
    def _current_oid(self):
        item = self._list.currentItem()
        if item is None:
            return None
        oid = item.data(_ROLE_ID)
        return int(oid) if oid is not None else None

    def _on_selection_changed(self):
        """Enable OK only for a real buildable row, and lock the quantity to 1
        for auto-build items (standing orders take no count)."""
        item = self._list.currentItem()
        oid = self._current_oid()
        is_item = oid is not None
        ok = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok.setEnabled(is_item)

        is_auto = is_item and item.data(_ROLE_CATEGORY) == "auto"
        if is_auto:
            self._qty.setValue(1)
        self._qty.setEnabled(is_item and not is_auto)

    def _accept_current(self):
        item = self._list.currentItem()
        oid = self._current_oid()
        if oid is None:
            return
        # Auto-build items are standing orders, not counted builds — force 1
        # regardless of the (locked) spin box.
        qty = 1 if item.data(_ROLE_CATEGORY) == "auto" else self._qty.value()
        self._selected = (oid, qty)
        self.item_chosen.emit(oid, qty)
        self.accept()

    def selected(self):
        """The accepted ``(build_object_id, quantity)``, or ``None`` if the
        dialog was cancelled."""
        return self._selected


def _category_for_label(label: str):
    """Reverse the picker group label back to its category slug (so a row can
    carry its category for the auto-quantity lock). Returns ``None`` for the
    'Other' catch-all group."""
    from ..info_panel import _PICKER_CATEGORY_LABELS

    for cat, lbl in _PICKER_CATEGORY_LABELS:
        if lbl == label:
            return cat
    return None
