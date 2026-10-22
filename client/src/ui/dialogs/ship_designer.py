"""
ui/dialogs/ship_designer.py

Ship Designer dialog — top-level skeleton.

Reproduces the layout of the original Stars! Ship Designer (see
stars-reborn-research/original/screencaps/ship_designer/):

  ┌──── Ship Designer ──────────────────────────────────────────┐
  │ ┌─Design────┐                                                │
  │ │ ◉ Ships   │   [hull thumbnail] [design-name dropdown    ▾] │
  │ │ ○ Bases   │                                                │
  │ └───────────┘   ┌──────────── slot layout ───────────────┐   │
  │ ┌─View──────┐   │    (cruciform for bases, row for ships)│   │
  │ │ ◉ Existing│   │                                        │   │
  │ │ ○ Avail.  │   └────────────────────────────────────────┘   │
  │ │ ○ Enemy   │   ┌─ cost / stats ───────────────────────────┐ │
  │ │ ○ Comp.   │   │   Ironium  12kT     Max Fuel    50mg     │ │
  │ └───────────┘   │   Boranium  8kT     Armor       20dp     │ │
  │ [Copy]          │   ...                                    │ │
  │ [Delete]        └──────────────────────────────────────────┘ │
  │ [Edit]                                            [Done][Help]│
  └─────────────────────────────────────────────────────────────┘

This is a skeleton: hull/component data and design persistence are not
wired up yet. Existing-design/hull/enemy/component lists use placeholder
content to validate layout. The Components view is stubbed pending the
Technology Browser (todo #81), which provides component icons and
filter logic that the Ship Designer will reuse.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# ── View keys ────────────────────────────────────────────────────────────────

_VIEW_EXISTING = "existing"
_VIEW_AVAILABLE = "available"
_VIEW_ENEMY = "enemy"
_VIEW_COMPONENTS = "components"


# ── Slot tile ────────────────────────────────────────────────────────────────


class _SlotTile(QFrame):
    """One slot in a hull's slot layout.

    `label` is the slot type or component name; `count_text` is the small
    bottom-right text ("8 of 16", "up to 12", or empty).
    `filled` controls the bevel — empty (raised) vs. filled (sunken/grey).
    """

    def __init__(
        self,
        label: str,
        count_text: str = "",
        filled: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Sunken if filled else QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setFixedSize(72, 72)
        self.setAutoFillBackground(True)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)

        title = QLabel(label, self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 10px;")
        lay.addWidget(title)

        lay.addStretch(1)

        if count_text:
            count = QLabel(count_text, self)
            count.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
            count.setStyleSheet("font-size: 9px;")
            lay.addWidget(count)


# ── Placeholder data (stub until engine wires up hull / design data) ─────────

# Each hull entry: (name, slot-pattern, cost, stats)
# slot-pattern is a list of (row, col, label, max_count) — for the skeleton.
_PLACEHOLDER_SHIP_DESIGNS = [
    {
        "name": "Armed Probe",
        "hull": "Scout",
        "fleet_count": 1,
        "slots": [
            (0, 0, "Engine", 1),
            (0, 1, "Scanner", 1),
            (0, 2, "Gen.Elec", 1),
        ],
        "cost": {"Ironium": "12kT", "Boranium": "8kT", "Germanium": "7kT", "Resources": "24"},
        "stats": {
            "Mass": "23kT",
            "Max Fuel": "50mg",
            "Armor": "20dp",
            "Shields": "(none)",
            "Rating": "13",
            "Cloak/Jam": "0%/0%",
            "Initiative/Moves": "1 / 1",
            "Scanner Range": "66 / 30",
        },
    },
]

_PLACEHOLDER_STARBASE_DESIGNS = [
    {
        "name": "Starbase",
        "hull": "Space Station",
        "fleet_count": 1,
        "slots": [
            (0, 1, "Weapon", 16),
            (0, 2, "Weapon", 16),
            (1, 0, "Weapon", 16),
            (1, 1, "Orbital or Elect", 1),
            (1, 2, "Unlimited Space Dock", 1),
            (1, 3, "Orbital or Elect", 1),
            (1, 4, "Weapon", 16),
            (2, 1, "Weapon", 16),
            (2, 2, "Weapon", 16),
        ],
        "cost": {"Ironium": "122kT", "Boranium": "151kT", "Germanium": "236kT", "Resources": "656"},
        "stats": {
            "Armor": "500dp",
            "Shields": "800dp",
            "Rating": "192",
            "Cloak/Jam": "0%/0%",
            "Initiative/Moves": "14 / --",
        },
    },
]

_PLACEHOLDER_SHIP_HULLS = [
    {
        "name": "Scout",
        "slots": [(0, 0, "Engine", 1), (0, 1, "Scanner", 1), (0, 2, "Gen.Elec", 1)],
        "cost": {"Ironium": "4kT", "Boranium": "2kT", "Germanium": "4kT", "Resources": "8"},
        "stats": {"Armor": "20dp"},
    },
    {
        "name": "Orbital Fort",
        "slots": [
            (0, 1, "Weapon", 12),
            (1, 0, "Shield or Armor", 12),
            (1, 1, "Orbital or Elect", 1),
            (1, 2, "Shield or Armor", 12),
            (2, 1, "Weapon", 12),
        ],
        "cost": {"Ironium": "11kT", "Boranium": "0kT", "Germanium": "15kT", "Resources": "35"},
        "stats": {"Armor": "100dp"},
    },
]


# ── Dialog ───────────────────────────────────────────────────────────────────


class ShipDesignerDialog(QDialog):
    """Top-level Ship Designer window.

    Parameters
    ----------
    player:
        The player object (parsed .m turn file). May be ``None`` while the
        engine→client wiring for designs is still being built.
    """

    def __init__(self, player=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._player = player
        self._design_kind: str = "ships"  # "ships" | "starbases"
        self._view_mode: str = _VIEW_EXISTING
        self._current_design_index: int = 0
        self._current_hull_index: int = 0
        self._ready: bool = False  # suppress refresh during build
        self._init_ui()
        self._ready = True
        self._refresh_right_pane()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _init_ui(self) -> None:
        self.setWindowTitle("Wainwright")  # original window title; player-config name later
        self.resize(640, 480)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Build right pane first so its widgets exist when the left-rail
        # radios fire their initial `toggled` signals during construction.
        right = self._build_right_pane()
        left = self._build_left_rail()
        body = QHBoxLayout()
        body.setSpacing(10)
        body.addWidget(left, 0)
        body.addWidget(right, 1)
        root.addLayout(body, 1)

        root.addLayout(self._build_bottom_buttons())

    def _build_left_rail(self) -> QWidget:
        rail = QWidget(self)
        lay = QVBoxLayout(rail)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Design group
        design_group = QGroupBox("Design")
        dlay = QVBoxLayout(design_group)
        dlay.setSpacing(2)
        self._design_group = QButtonGroup(self)
        for label, value in (("Ships", "ships"), ("Starbases", "starbases")):
            btn = QRadioButton(label)
            btn.setProperty("value", value)
            btn.toggled.connect(self._on_design_kind_changed)
            self._design_group.addButton(btn)
            dlay.addWidget(btn)
            if value == "ships":
                btn.setChecked(True)
        lay.addWidget(design_group)

        # View group
        view_group = QGroupBox("View")
        vlay = QVBoxLayout(view_group)
        vlay.setSpacing(2)
        self._view_group = QButtonGroup(self)
        for label, value in (
            ("Existing Designs", _VIEW_EXISTING),
            ("Available Hull Types", _VIEW_AVAILABLE),
            ("Enemy Hulls", _VIEW_ENEMY),
            ("Components", _VIEW_COMPONENTS),
        ):
            btn = QRadioButton(label)
            btn.setProperty("value", value)
            btn.toggled.connect(self._on_view_changed)
            self._view_group.addButton(btn)
            vlay.addWidget(btn)
            if value == _VIEW_EXISTING:
                btn.setChecked(True)
        lay.addWidget(view_group)

        # Action buttons
        self._copy_btn = QPushButton("&Copy Selected Design")
        self._copy_btn.clicked.connect(self._on_copy_design)
        lay.addWidget(self._copy_btn)

        self._delete_btn = QPushButton("&Delete Selected Design")
        self._delete_btn.clicked.connect(self._on_delete_design)
        lay.addWidget(self._delete_btn)

        self._edit_btn = QPushButton("&Edit Selected Design")
        self._edit_btn.clicked.connect(self._on_edit_design)
        lay.addWidget(self._edit_btn)

        lay.addStretch(1)
        rail.setFixedWidth(190)
        return rail

    def _build_right_pane(self) -> QWidget:
        wrap = QWidget(self)
        wlay = QVBoxLayout(wrap)
        wlay.setContentsMargins(0, 0, 0, 0)
        wlay.setSpacing(6)

        # Header: hull thumbnail + name dropdown
        header = QHBoxLayout()
        header.setSpacing(8)
        self._hull_thumb = QLabel(wrap)
        self._hull_thumb.setFixedSize(80, 56)
        self._hull_thumb.setFrameShape(QFrame.Shape.Box)
        self._hull_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hull_thumb.setStyleSheet("background: black; color: #888;")
        self._hull_thumb.setText("(hull)")
        header.addWidget(self._hull_thumb)

        self._name_combo = QComboBox(wrap)
        self._name_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._name_combo.currentIndexChanged.connect(self._on_name_combo_changed)
        header.addWidget(self._name_combo, 1)

        wlay.addLayout(header)

        # Stacked body — switches by view mode
        self._body_stack = QStackedWidget(wrap)
        self._page_existing = self._build_design_page()
        self._page_available = self._build_design_page()
        self._page_enemy = self._build_enemy_page()
        self._page_components = self._build_components_page()
        self._body_stack.addWidget(self._page_existing)
        self._body_stack.addWidget(self._page_available)
        self._body_stack.addWidget(self._page_enemy)
        self._body_stack.addWidget(self._page_components)
        wlay.addWidget(self._body_stack, 1)

        return wrap

    def _build_design_page(self) -> QWidget:
        """A page used for both Existing Designs and Available Hull Types.

        Both views show the same anatomy: slot grid + cost/stats footer. The
        difference is whether slots are filled (existing) or empty placeholders
        (available).
        """
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        slot_host = QWidget(page)
        slot_lay = QGridLayout(slot_host)
        slot_lay.setSpacing(4)
        slot_lay.setContentsMargins(0, 0, 0, 0)
        slot_host.setLayout(slot_lay)
        lay.addWidget(slot_host, 0, Qt.AlignmentFlag.AlignHCenter)

        # Fleet-count badge (top-right of slot area)
        badge_row = QHBoxLayout()
        badge_row.addStretch(1)
        badge = QLabel("", page)
        badge.setStyleSheet("background: #c0c0c0; border: 1px solid #808080; padding: 2px 8px;")
        badge_row.addWidget(badge)
        lay.addLayout(badge_row)

        lay.addStretch(1)

        # Cost/stats footer
        footer_host = QWidget(page)
        footer_lay = QGridLayout(footer_host)
        footer_lay.setContentsMargins(0, 0, 0, 0)
        footer_lay.setHorizontalSpacing(20)
        footer_lay.setVerticalSpacing(2)
        lay.addWidget(footer_host)

        # Stash references for refresh
        page.setProperty("_is_design_page", True)
        page._slot_host = slot_host  # type: ignore[attr-defined]
        page._slot_layout = slot_lay  # type: ignore[attr-defined]
        page._badge = badge  # type: ignore[attr-defined]
        page._footer_host = footer_host  # type: ignore[attr-defined]
        page._footer_layout = footer_lay  # type: ignore[attr-defined]
        return page

    def _build_enemy_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        msg = QLabel(
            "No enemy hulls have been observed yet.\n\n"
            "Hulls discovered via scanning enemy fleets will appear here.",
            page,
        )
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("color: #555;")
        lay.addStretch(1)
        lay.addWidget(msg)
        lay.addStretch(2)
        page._empty_label = msg  # type: ignore[attr-defined]
        return page

    def _build_components_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        category = QComboBox(page)
        category.addItems(
            [
                "All",
                "Armor",
                "Shields",
                "Weapons",
                "Bombs",
                "Electrical",
                "Engines",
                "Mechanical",
                "Mine Layers",
                "Mine Robots",
                "Orbital",
                "Planetary",
                "Scanners",
            ]
        )
        category.setEnabled(False)  # stubbed pending Technology Browser
        lay.addWidget(category)

        lst = QListWidget(page)
        for placeholder in (
            "Mole-skin Shield",
            "Cow-hide Shield",
            "Tritanium",
            "Crobmnium",
        ):
            lst.addItem(QListWidgetItem(placeholder))
        lst.setEnabled(False)
        lay.addWidget(lst, 1)

        note = QLabel(
            "Components view depends on the Technology Browser (not yet built).",
            page,
        )
        note.setStyleSheet("color: #888; font-style: italic;")
        lay.addWidget(note)
        return page

    def _build_bottom_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch(1)
        self._done_btn = QPushButton("&Done")
        self._done_btn.setDefault(True)
        self._done_btn.clicked.connect(self.accept)
        row.addWidget(self._done_btn)
        self._help_btn = QPushButton("&Help")
        self._help_btn.clicked.connect(self._on_help)
        row.addWidget(self._help_btn)
        return row

    # ── Data accessors (stubbed) ─────────────────────────────────────────────

    def _existing_designs(self) -> list[dict]:
        # TODO: pull from self._player when schema lands
        if self._design_kind == "ships":
            return list(_PLACEHOLDER_SHIP_DESIGNS)
        return list(_PLACEHOLDER_STARBASE_DESIGNS)

    def _available_hulls(self) -> list[dict]:
        # TODO: filter master hull list by player PRT + tech level + Mystery
        # Trader gifts. For now just show one example per kind.
        if self._design_kind == "ships":
            return [_PLACEHOLDER_SHIP_HULLS[0]]
        return [_PLACEHOLDER_SHIP_HULLS[1]]

    # ── Refresh ───────────────────────────────────────────────────────────────

    def _refresh_right_pane(self) -> None:
        # Sync stack page
        page_index = {
            _VIEW_EXISTING: 0,
            _VIEW_AVAILABLE: 1,
            _VIEW_ENEMY: 2,
            _VIEW_COMPONENTS: 3,
        }[self._view_mode]
        self._body_stack.setCurrentIndex(page_index)

        # Header is shown only for design/hull/enemy pages
        header_visible = self._view_mode != _VIEW_COMPONENTS
        self._hull_thumb.setVisible(header_visible)
        self._name_combo.setVisible(header_visible)

        self._refresh_name_combo()
        self._refresh_action_buttons()

        if self._view_mode == _VIEW_EXISTING:
            self._populate_design_page(self._page_existing, mode="existing")
        elif self._view_mode == _VIEW_AVAILABLE:
            self._populate_design_page(self._page_available, mode="available")
        # Enemy + Components pages are static for the skeleton.

    def _refresh_name_combo(self) -> None:
        self._name_combo.blockSignals(True)
        self._name_combo.clear()
        if self._view_mode == _VIEW_EXISTING:
            for d in self._existing_designs():
                self._name_combo.addItem(d["name"])
            self._name_combo.setCurrentIndex(
                min(self._current_design_index, self._name_combo.count() - 1)
            )
        elif self._view_mode == _VIEW_AVAILABLE:
            for h in self._available_hulls():
                self._name_combo.addItem(h["name"])
            self._name_combo.setCurrentIndex(
                min(self._current_hull_index, self._name_combo.count() - 1)
            )
        elif self._view_mode == _VIEW_ENEMY:
            # No items — empty state
            pass
        self._name_combo.blockSignals(False)

    def _refresh_action_buttons(self) -> None:
        is_existing = self._view_mode == _VIEW_EXISTING
        has_designs = is_existing and self._name_combo.count() > 0

        self._copy_btn.setEnabled(has_designs or self._view_mode == _VIEW_AVAILABLE)
        self._delete_btn.setEnabled(has_designs)

        # Edit Selected Design is disabled when ships of that design exist —
        # match the screencap behavior. We don't yet have built-count info,
        # so for the placeholder data assume any design with fleet_count > 0
        # blocks editing.
        edit_enabled = False
        if has_designs:
            d = self._existing_designs()[self._name_combo.currentIndex()]
            edit_enabled = d.get("fleet_count", 0) == 0
        self._edit_btn.setEnabled(edit_enabled)

    def _populate_design_page(self, page: QWidget, mode: str) -> None:
        slot_layout: QGridLayout = page._slot_layout  # type: ignore[attr-defined]
        badge: QLabel = page._badge  # type: ignore[attr-defined]
        footer_layout: QGridLayout = page._footer_layout  # type: ignore[attr-defined]

        _clear_layout(slot_layout)
        _clear_layout(footer_layout)

        if mode == "existing":
            items = self._existing_designs()
            idx = self._name_combo.currentIndex()
            if idx < 0 or idx >= len(items):
                badge.setText("")
                return
            entry = items[idx]
            badge.setText(f"{entry['fleet_count']} of {entry['fleet_count']}")
            for row, col, label, max_count in entry["slots"]:
                tile = _SlotTile(label, count_text=f"{max_count} of {max_count}", filled=True)
                slot_layout.addWidget(tile, row, col)
            self._fill_footer(
                footer_layout, f"Cost of one {entry['name']}", entry["cost"], entry["stats"]
            )
        else:  # available
            items = self._available_hulls()
            idx = self._name_combo.currentIndex()
            if idx < 0 or idx >= len(items):
                badge.setText("")
                return
            entry = items[idx]
            badge.setText("")
            for row, col, label, max_count in entry["slots"]:
                count_text = f"up to {max_count}" if max_count > 0 else ""
                tile = _SlotTile(label, count_text=count_text, filled=False)
                slot_layout.addWidget(tile, row, col)
            self._fill_footer(
                footer_layout, f"Cost of one {entry['name']} Hull", entry["cost"], entry["stats"]
            )

    def _fill_footer(
        self,
        grid: QGridLayout,
        title: str,
        cost: dict,
        stats: dict,
    ) -> None:
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #008080; font-weight: bold;")
        grid.addWidget(title_label, 0, 0, 1, 2)

        # Left column: cost
        row = 1
        cost_color = {
            "Ironium": "#0040c0",
            "Boranium": "#00a000",
            "Germanium": "#b08000",
        }
        for key, val in cost.items():
            lbl = QLabel(f"{key}:")
            color = cost_color.get(key)
            if color:
                lbl.setStyleSheet(f"color: {color};")
            grid.addWidget(lbl, row, 0)
            v = QLabel(val)
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            grid.addWidget(v, row, 1)
            row += 1

        # Right column: stats
        row = 1
        for key, val in stats.items():
            grid.addWidget(QLabel(f"{key}:"), row, 2)
            v = QLabel(val)
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            grid.addWidget(v, row, 3)
            row += 1

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_design_kind_changed(self, checked: bool) -> None:
        if not checked or not self._ready:
            return
        btn = self._design_group.checkedButton()
        if btn is None:
            return
        self._design_kind = btn.property("value")
        self._current_design_index = 0
        self._current_hull_index = 0
        self._refresh_right_pane()

    def _on_view_changed(self, checked: bool) -> None:
        if not checked or not self._ready:
            return
        btn = self._view_group.checkedButton()
        if btn is None:
            return
        self._view_mode = btn.property("value")
        self._refresh_right_pane()

    def _on_name_combo_changed(self, index: int) -> None:
        if not self._ready:
            return
        if self._view_mode == _VIEW_EXISTING:
            self._current_design_index = max(0, index)
        elif self._view_mode == _VIEW_AVAILABLE:
            self._current_hull_index = max(0, index)
        self._refresh_right_pane()

    def _on_copy_design(self) -> None:
        QMessageBox.information(
            self,
            "Copy Design",
            "Copy Selected Design — opens the design editor seeded with a copy of "
            "the current selection. Not yet implemented.",
        )

    def _on_delete_design(self) -> None:
        designs = self._existing_designs()
        idx = self._name_combo.currentIndex()
        if idx < 0 or idx >= len(designs):
            return
        entry = designs[idx]
        n = entry.get("fleet_count", 0)
        if n > 0:
            answer = QMessageBox.question(
                self,
                "Delete Design",
                f"You currently have {n} {entry['name']}. If you delete this "
                f"design, these ships will be destroyed. Are you sure?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        # TODO: actually remove the design once persistence is wired up.
        QMessageBox.information(
            self,
            "Delete Design",
            "Design deletion is not yet wired to the engine.",
        )

    def _on_edit_design(self) -> None:
        QMessageBox.information(
            self,
            "Edit Design",
            "Edit Selected Design — opens the design editor. Not yet implemented.",
        )

    def _on_help(self) -> None:
        QMessageBox.information(
            self,
            "Ship Designer Help",
            "Ship Designer help — to be wired up to the Player's Guide.",
        )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
