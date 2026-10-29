"""
ui/dialogs/ship_designer.py

Ship Designer dialog.

Reproduces the layout of the original Stars! Ship Designer (see
stars-reborn-research/experiments/screencaps/ship_designer/):

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

What is wired here:

- **Components view** — the live component catalog from ``GET
  /model/technologies`` (shared helpers with the Technology Browser: category
  grouping, availability filtering, icon resolution).
- **Available Hull Types** — the live hull catalogs (``GET /model/ships/hulls``,
  ``GET /model/starbase/hulls``), filtered to the player's buildable hulls.
- **Slot-fill editing** — a new design is created from an available hull and
  edited by clicking components into compatible slots; slot-type compatibility
  is validated and the cost/mass preview updates live
  (``src.data.ship_design``).

What is NOT wired yet (blocked on the engine host-side design model, task
#145): persisting an edited design back to the engine, engine-computed combat
stats (armor/shield totals, rating, cloak/jam), and the player's real
*Existing Designs* (those remain illustrative placeholders until the turn file
carries them). The editor therefore operates on an in-memory design; closing
the editor discards it.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

import logging

import requests
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
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

from ...data.ship_design import DesignModel, slot_accepts
from ...data.technologies import CATEGORY_LABELS, component_available, group_by_category
from ._components_common import component_icon

log = logging.getLogger(__name__)

# ── View keys ────────────────────────────────────────────────────────────────

_VIEW_EXISTING = "existing"
_VIEW_AVAILABLE = "available"
_VIEW_ENEMY = "enemy"
_VIEW_COMPONENTS = "components"

# ── Slot-type display labels (what the empty-slot tile shows) ─────────────────

_SLOT_LABELS = {
    "engines": "Engine",
    "weapons": "Weapon",
    "beam-weapons": "Beam Weapon",
    "torpedoes": "Torpedo",
    "armor": "Armor",
    "shields": "Shield",
    "protection": "Shield or Armor",
    "electrical": "Electrical",
    "mechanical": "Mechanical",
    "elect-mech": "Elect or Mech",
    "bombs": "Bomb",
    "mine-layers": "Mine Layer",
    "mine-elect-mech": "Mine, Elect or Mech",
    "mining-robots": "Mining Robot",
    "scanners": "Scanner",
    "scanner-elect-mech": "Scanner, Elect or Mech",
    "shield-elect-mech": "Shield, Elect or Mech",
    "armor-scanner-elect-mech": "Armor, Scan, Elect/Mech",
    "weapon-shield": "Weapon or Shield",
    "orbital": "Orbital",
    "orbital-elect": "Orbital or Elect",
    "general-purpose": "General Purpose",
}


def _slot_label(slot_type: str) -> str:
    return _SLOT_LABELS.get(slot_type, slot_type.replace("-", " ").title())


# ── Slot tile ────────────────────────────────────────────────────────────────


class _SlotTile(QFrame):
    """One slot in a hull's slot layout.

    Rendered fresh on each refresh. ``index`` is the slot's position in the
    hull's ``slots`` list (``-1`` for non-interactive decoration). When clicked
    it emits :attr:`clicked` with its index so the editor can place/remove a
    part. ``state`` tints the border during editing: ``compatible`` (a pending
    part fits here), ``incompatible`` (it does not), or ``normal``.
    """

    clicked = Signal(int)

    _BORDER = {
        "normal": "#808080",
        "compatible": "#1f8f1f",
        "incompatible": "#b03030",
    }

    def __init__(
        self,
        index: int,
        title: str,
        count_text: str = "",
        filled: bool = False,
        state: str = "normal",
        interactive: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._index = index
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Sunken if filled else QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setFixedSize(72, 72)
        self.setAutoFillBackground(True)
        border = self._BORDER.get(state, self._BORDER["normal"])
        bg = "#d8d8d8" if filled else "#f0f0f0"
        if state == "incompatible":
            bg = "#efe4e4"
        elif state == "compatible":
            bg = "#e4efe4"
        self.setStyleSheet(f"_SlotTile {{ border: 2px solid {border}; background: {bg}; }}")
        if interactive:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)

        label = QLabel(title, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 10px; border: none; background: transparent;")
        lay.addWidget(label)
        lay.addStretch(1)

        if count_text:
            count = QLabel(count_text, self)
            count.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
            count.setStyleSheet("font-size: 9px; border: none; background: transparent;")
            lay.addWidget(count)

    def mousePressEvent(self, event):  # noqa: N802 (Qt override)
        if self._index >= 0:
            self.clicked.emit(self._index)
        super().mousePressEvent(event)


# ── Component palette (shared by Components view + editor) ─────────────────────


class _ComponentPalette(QWidget):
    """Category-filtered list of components with icons.

    Emits :attr:`componentChanged` with the selected component dict (or
    ``None``). Used read-only in the Components view and as the part picker in
    the editor.
    """

    componentChanged = Signal(object)

    def __init__(self, by_category, categories, race, parent=None) -> None:
        super().__init__(parent)
        self._by_category = by_category
        self._categories = categories
        self._race = race

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self._cat_combo = QComboBox(self)
        for slug in self._categories:
            self._cat_combo.addItem(CATEGORY_LABELS.get(slug, slug.title()), slug)
        self._cat_combo.currentIndexChanged.connect(self._reload_list)
        lay.addWidget(self._cat_combo)

        self._avail_check = QCheckBox("Show Only Available", self)
        self._avail_check.stateChanged.connect(self._reload_list)
        lay.addWidget(self._avail_check)

        self._list = QListWidget(self)
        self._list.setIconSize(_icon_size())
        self._list.currentItemChanged.connect(self._on_item_changed)
        lay.addWidget(self._list, 1)

        if self._categories:
            self._reload_list()

    def _is_available(self, item) -> bool:
        return component_available(
            item,
            getattr(self._race, "prt", ""),
            getattr(self._race, "lrts", []),
        )

    def _reload_list(self, *_args) -> None:
        self._list.clear()
        if not self._categories:
            self.componentChanged.emit(None)
            return
        slug = self._cat_combo.currentData()
        items = self._by_category.get(slug, [])
        if self._avail_check.isChecked():
            items = [it for it in items if self._is_available(it)]
        for it in items:
            entry = QListWidgetItem(it.get("name", "?"))
            pix = component_icon(it.get("category", ""), it.get("name", ""))
            entry.setIcon(_pixmap_icon(pix))
            entry.setData(Qt.ItemDataRole.UserRole, it)
            if not self._is_available(it):
                entry.setForeground(Qt.GlobalColor.gray)
            self._list.addItem(entry)
        if self._list.count():
            self._list.setCurrentRow(0)
        else:
            self.componentChanged.emit(None)

    def _on_item_changed(self, current, _previous) -> None:
        self.componentChanged.emit(
            current.data(Qt.ItemDataRole.UserRole) if current is not None else None
        )

    def current_component(self):
        item = self._list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item is not None else None


def _icon_size():
    from PySide6.QtCore import QSize

    return QSize(32, 32)


def _pixmap_icon(pix):
    from PySide6.QtGui import QIcon

    return QIcon(pix)


# ── Placeholder Existing Designs (illustrative until the turn file carries them)

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


# ── Dialog ───────────────────────────────────────────────────────────────────


class ShipDesignerDialog(QDialog):
    """Top-level Ship Designer window.

    Parameters
    ----------
    player:
        The player object (parsed .m turn file). May be ``None``.
    engine_url:
        Base URL of the running engine; the component and hull catalogs are
        fetched from it. ``None`` leaves the catalog-backed views in an
        unavailable state.
    """

    def __init__(self, player=None, engine_url=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._player = player
        self._race = getattr(player, "race", None) if player else None
        self._engine_url = engine_url.rstrip("/") if engine_url else None

        self._design_kind: str = "ships"  # "ships" | "starbases"
        self._view_mode: str = _VIEW_EXISTING
        self._current_design_index: int = 0
        self._current_hull_index: int = 0
        self._editing: DesignModel | None = None
        self._pending_component: dict | None = None
        self._ready: bool = False

        # Catalogs (populated from the engine; empty if unavailable).
        self._tech_by_cat: dict[str, list[dict]] = {}
        self._tech_cats: list[str] = []
        self._ship_hulls: list[dict] = []
        self._starbase_hulls: list[dict] = []
        self._load_catalogs()

        self._init_ui()
        self._ready = True
        self._refresh_right_pane()

    # ── catalog loading ─────────────────────────────────────────────────────

    def _load_catalogs(self) -> None:
        if not self._engine_url:
            log.info("Ship Designer: no engine URL; catalog-backed views unavailable.")
            return
        items = self._get_json("/model/technologies", "technologies")
        self._tech_by_cat, self._tech_cats = group_by_category(items)
        self._ship_hulls = self._get_json("/model/ships/hulls", "hulls")
        self._starbase_hulls = self._get_json("/model/starbase/hulls", "hulls")

    def _get_json(self, path: str, key: str) -> list:
        try:
            resp = requests.get(f"{self._engine_url}{path}", timeout=15)
            resp.raise_for_status()
            return resp.json().get(key, [])
        except (requests.exceptions.RequestException, ValueError) as exc:
            log.warning("Could not load %s: %s", path, exc)
            return []

    @property
    def _has_catalog(self) -> bool:
        return bool(self._tech_cats or self._ship_hulls or self._starbase_hulls)

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _init_ui(self) -> None:
        self.setWindowTitle("Ship Designer")
        self.resize(680, 500)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Build right pane first so its widgets exist when the left-rail radios
        # fire their initial `toggled` signals during construction.
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
        self._view_box = view_group
        lay.addWidget(view_group)

        self._copy_btn = QPushButton("&Copy Selected Design")
        self._copy_btn.clicked.connect(self._on_copy_or_create)
        lay.addWidget(self._copy_btn)

        self._delete_btn = QPushButton("&Delete Selected Design")
        self._delete_btn.clicked.connect(self._on_delete_design)
        lay.addWidget(self._delete_btn)

        self._edit_btn = QPushButton("&Edit Selected Design")
        self._edit_btn.clicked.connect(self._on_edit_design)
        lay.addWidget(self._edit_btn)

        lay.addStretch(1)
        rail.setFixedWidth(200)
        return rail

    def _build_right_pane(self) -> QWidget:
        wrap = QWidget(self)
        wlay = QVBoxLayout(wrap)
        wlay.setContentsMargins(0, 0, 0, 0)
        wlay.setSpacing(6)

        # Header: hull thumbnail + name dropdown (hidden for Components/editor).
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
        self._header_row = header
        wlay.addLayout(header)

        self._body_stack = QStackedWidget(wrap)
        self._page_existing = self._build_design_page()
        self._page_available = self._build_design_page()
        self._page_enemy = self._build_enemy_page()
        self._page_components = self._build_components_page()
        self._page_edit = self._build_edit_page()
        for p in (
            self._page_existing,
            self._page_available,
            self._page_enemy,
            self._page_components,
            self._page_edit,
        ):
            self._body_stack.addWidget(p)
        wlay.addWidget(self._body_stack, 1)
        return wrap

    def _build_design_page(self) -> QWidget:
        """A read-only slot-grid + cost/stats page (Existing / Available)."""
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        slot_host = QWidget(page)
        slot_lay = QGridLayout(slot_host)
        slot_lay.setSpacing(4)
        slot_lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(slot_host, 0, Qt.AlignmentFlag.AlignHCenter)

        badge_row = QHBoxLayout()
        badge_row.addStretch(1)
        badge = QLabel("", page)
        badge.setStyleSheet("background: #c0c0c0; border: 1px solid #808080; padding: 2px 8px;")
        badge_row.addWidget(badge)
        lay.addLayout(badge_row)
        lay.addStretch(1)

        footer_host = QWidget(page)
        footer_lay = QGridLayout(footer_host)
        footer_lay.setContentsMargins(0, 0, 0, 0)
        footer_lay.setHorizontalSpacing(20)
        footer_lay.setVerticalSpacing(2)
        lay.addWidget(footer_host)

        page._slot_layout = slot_lay  # type: ignore[attr-defined]
        page._badge = badge  # type: ignore[attr-defined]
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
        return page

    def _build_components_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        if not self._tech_cats:
            lay.addWidget(self._catalog_unavailable_label())
            return page

        palette = _ComponentPalette(self._tech_by_cat, self._tech_cats, self._race, page)
        palette.componentChanged.connect(self._on_components_view_selection)
        lay.addWidget(palette, 1)

        detail = QLabel("", page)
        detail.setWordWrap(True)
        detail.setStyleSheet("color: #444;")
        detail.setMinimumHeight(70)
        detail.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.addWidget(detail)

        page._palette = palette  # type: ignore[attr-defined]
        page._detail = detail  # type: ignore[attr-defined]
        return page

    def _build_edit_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        banner = QLabel("", page)
        banner.setWordWrap(True)
        banner.setStyleSheet(
            "background: #fff3c0; border: 1px solid #d0b000; padding: 4px 6px; color: #604000;"
        )
        outer.addWidget(banner)

        body = QHBoxLayout()
        body.setSpacing(8)

        # Left: part palette (only shown once a catalog is present).
        self._edit_palette: _ComponentPalette | None = None
        if self._tech_cats:
            palette = _ComponentPalette(self._tech_by_cat, self._tech_cats, self._race, page)
            palette.componentChanged.connect(self._on_edit_component_selected)
            palette.setFixedWidth(230)
            self._edit_palette = palette
            body.addWidget(palette, 0)

        # Right: slot grid + live cost/mass.
        right = QWidget(page)
        rlay = QVBoxLayout(right)
        rlay.setContentsMargins(0, 0, 0, 0)
        rlay.setSpacing(6)

        hint = QLabel("", right)
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #336; font-style: italic;")
        rlay.addWidget(hint)

        slot_host = QWidget(right)
        slot_lay = QGridLayout(slot_host)
        slot_lay.setSpacing(4)
        slot_lay.setContentsMargins(0, 0, 0, 0)
        rlay.addWidget(slot_host, 0, Qt.AlignmentFlag.AlignHCenter)
        rlay.addStretch(1)

        footer_host = QWidget(right)
        footer_lay = QGridLayout(footer_host)
        footer_lay.setContentsMargins(0, 0, 0, 0)
        footer_lay.setHorizontalSpacing(20)
        footer_lay.setVerticalSpacing(2)
        rlay.addWidget(footer_host)

        body.addWidget(right, 1)
        outer.addLayout(body, 1)

        stop = QPushButton("&Stop Editing", page)
        stop.clicked.connect(self._stop_editing)
        stop_row = QHBoxLayout()
        stop_row.addStretch(1)
        stop_row.addWidget(stop)
        outer.addLayout(stop_row)

        page._banner = banner  # type: ignore[attr-defined]
        page._hint = hint  # type: ignore[attr-defined]
        page._slot_layout = slot_lay  # type: ignore[attr-defined]
        page._footer_layout = footer_lay  # type: ignore[attr-defined]
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

    def _catalog_unavailable_label(self) -> QLabel:
        msg = QLabel(
            "The component catalog is unavailable.\n\n"
            "Start the game against a running engine to browse components."
        )
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("color: #888; font-style: italic;")
        return msg

    # ── Data accessors ────────────────────────────────────────────────────────

    def _existing_designs(self) -> list[dict]:
        if self._design_kind == "ships":
            return list(_PLACEHOLDER_SHIP_DESIGNS)
        return list(_PLACEHOLDER_STARBASE_DESIGNS)

    def _available_hulls(self) -> list[dict]:
        """Live hull catalog for the current kind, filtered to buildable hulls."""
        hulls = self._ship_hulls if self._design_kind == "ships" else self._starbase_hulls
        return [h for h in hulls if self._hull_available(h)]

    def _hull_available(self, hull: dict) -> bool:
        """Whether the player's race can build ``hull`` (trait gate only).

        Hull ``requirement`` is a single trait code: ``AR`` (PRT), ``ARM`` (LRT),
        or ``MT`` (Mystery Trader — not buildable without a trade). A per-field
        tech-level check would make this exact once the client player carries
        tech levels.
        """
        req = hull.get("requirement")
        if not req:
            return True
        req = str(req).upper()
        prt = (getattr(self._race, "prt", "") or "").upper()
        lrts = {str(s).upper() for s in (getattr(self._race, "lrts", []) or [])}
        if req == "MT":
            return False
        if req == "AR":
            return prt == "AR"
        if req == "ARM":
            return "ARM" in lrts
        return True

    # ── Refresh ───────────────────────────────────────────────────────────────

    def _refresh_right_pane(self) -> None:
        if self._editing is not None:
            self._body_stack.setCurrentWidget(self._page_edit)
            self._hull_thumb.setVisible(False)
            self._name_combo.setVisible(False)
            return

        page = {
            _VIEW_EXISTING: self._page_existing,
            _VIEW_AVAILABLE: self._page_available,
            _VIEW_ENEMY: self._page_enemy,
            _VIEW_COMPONENTS: self._page_components,
        }[self._view_mode]
        self._body_stack.setCurrentWidget(page)

        header_visible = self._view_mode in (_VIEW_EXISTING, _VIEW_AVAILABLE, _VIEW_ENEMY)
        self._hull_thumb.setVisible(header_visible)
        self._name_combo.setVisible(header_visible)

        self._refresh_name_combo()
        self._refresh_action_buttons()

        if self._view_mode == _VIEW_EXISTING:
            self._populate_existing_page()
        elif self._view_mode == _VIEW_AVAILABLE:
            self._populate_available_page()

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
                self._name_combo.addItem(h.get("name", "?"))
            if self._name_combo.count():
                self._name_combo.setCurrentIndex(
                    min(self._current_hull_index, self._name_combo.count() - 1)
                )
        self._name_combo.blockSignals(False)

    def _refresh_action_buttons(self) -> None:
        is_existing = self._view_mode == _VIEW_EXISTING
        is_available = self._view_mode == _VIEW_AVAILABLE
        has_existing = is_existing and self._name_combo.count() > 0
        has_hull = is_available and self._name_combo.count() > 0

        # Copy doubles as "Create New Design" when browsing available hulls.
        self._copy_btn.setText("&Create New Design" if is_available else "&Copy Selected Design")
        self._copy_btn.setEnabled(has_existing or has_hull)
        self._delete_btn.setEnabled(has_existing)

        edit_enabled = False
        if has_existing:
            d = self._existing_designs()[self._name_combo.currentIndex()]
            edit_enabled = d.get("fleet_count", 0) == 0
        self._edit_btn.setEnabled(edit_enabled)

    def _populate_existing_page(self) -> None:
        page = self._page_existing
        _clear_layout(page._slot_layout)  # type: ignore[attr-defined]
        _clear_layout(page._footer_layout)  # type: ignore[attr-defined]
        items = self._existing_designs()
        idx = self._name_combo.currentIndex()
        if idx < 0 or idx >= len(items):
            page._badge.setText("")  # type: ignore[attr-defined]
            return
        entry = items[idx]
        page._badge.setText(  # type: ignore[attr-defined]
            f"{entry['fleet_count']} of {entry['fleet_count']}"
        )
        for row, col, label, max_count in entry["slots"]:
            tile = _SlotTile(-1, label, count_text=f"{max_count} of {max_count}", filled=True)
            page._slot_layout.addWidget(tile, row, col)  # type: ignore[attr-defined]
        self._fill_cost_stats(
            page._footer_layout,  # type: ignore[attr-defined]
            f"Cost of one {entry['name']}",
            entry["cost"],
            entry["stats"],
        )

    def _populate_available_page(self) -> None:
        page = self._page_available
        _clear_layout(page._slot_layout)  # type: ignore[attr-defined]
        _clear_layout(page._footer_layout)  # type: ignore[attr-defined]
        page._badge.setText("")  # type: ignore[attr-defined]
        hulls = self._available_hulls()
        idx = self._name_combo.currentIndex()
        if idx < 0 or idx >= len(hulls):
            if not self._has_catalog:
                page._footer_layout.addWidget(  # type: ignore[attr-defined]
                    self._catalog_unavailable_label(), 0, 0
                )
            return
        hull = hulls[idx]
        for i, slot in enumerate(hull.get("slots", [])):
            pos = slot.get("position", {})
            max_count = int(slot.get("max-count", 1) or 1)
            tile = _SlotTile(
                -1,
                _slot_label(slot.get("slot-type", "")),
                count_text=f"up to {max_count}" if max_count > 1 else "",
                filled=False,
            )
            page._slot_layout.addWidget(  # type: ignore[attr-defined]
                tile, int(pos.get("row", 0)), int(pos.get("col", i))
            )
        cost = _wire_cost_to_display(hull.get("cost", {}))
        stats = {"Mass": f"{hull.get('mass', 0)}kT", "Armor": f"{hull.get('armor', 0)}dp"}
        self._fill_cost_stats(
            page._footer_layout,  # type: ignore[attr-defined]
            f"Cost of one {hull.get('name', '?')} Hull",
            cost,
            stats,
        )

    def _fill_cost_stats(self, grid: QGridLayout, title: str, cost: dict, stats: dict) -> None:
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #008080; font-weight: bold;")
        grid.addWidget(title_label, 0, 0, 1, 2)

        cost_color = {"Ironium": "#0040c0", "Boranium": "#00a000", "Germanium": "#b08000"}
        row = 1
        for key, val in cost.items():
            lbl = QLabel(f"{key}:")
            if key in cost_color:
                lbl.setStyleSheet(f"color: {cost_color[key]};")
            grid.addWidget(lbl, row, 0)
            v = QLabel(val)
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            grid.addWidget(v, row, 1)
            row += 1

        row = 1
        for key, val in stats.items():
            grid.addWidget(QLabel(f"{key}:"), row, 2)
            v = QLabel(val)
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            grid.addWidget(v, row, 3)
            row += 1

    # ── Editor ──────────────────────────────────────────────────────────────

    def _start_editing(self, hull: dict, name: str) -> None:
        self._editing = DesignModel(hull=hull, name=name)
        self._pending_component = None
        if self._edit_palette is not None:
            self._pending_component = self._edit_palette.current_component()
        # Left rail is inert while editing.
        self._set_rail_enabled(False)
        self._refresh_right_pane()
        self._render_editor()

    def _stop_editing(self) -> None:
        self._editing = None
        self._pending_component = None
        self._set_rail_enabled(True)
        self._refresh_right_pane()

    def _set_rail_enabled(self, enabled: bool) -> None:
        self._view_box.setEnabled(enabled)
        for btn in self._design_group.buttons():
            btn.setEnabled(enabled)
        self._copy_btn.setEnabled(enabled)
        self._delete_btn.setEnabled(enabled)
        self._edit_btn.setEnabled(enabled)

    def _on_edit_component_selected(self, component) -> None:
        self._pending_component = component
        if self._editing is not None:
            self._render_editor()

    def _on_edit_slot_clicked(self, index: int) -> None:
        if self._editing is None:
            return
        assignment = self._editing.assignments[index]
        if self._pending_component is None:
            # No part selected: a click removes one from a filled slot.
            if assignment is not None:
                self._editing.remove_one(index)
                self._render_editor()
            return
        if not self._editing.place(index, self._pending_component):
            # Incompatible or full; flash nothing destructive — just re-render.
            self.statusBar_message_incompatible(index)
        self._render_editor()

    def statusBar_message_incompatible(self, index: int) -> None:
        # The dialog has no status bar; the red slot tint already signals a bad
        # fit, so this is a no-op hook kept for clarity/testability.
        pass

    def _render_editor(self) -> None:
        page = self._page_edit
        design = self._editing
        if design is None:
            return

        name = design.name or design.hull.get("name", "Design")
        page._banner.setText(  # type: ignore[attr-defined]
            f"Editing “{name}” on the {design.hull.get('name', '?')} hull. "
            "Changes are previewed here but not yet saved — persisting designs "
            "and engine-computed combat stats arrive with the host design model."
        )

        if self._pending_component is not None:
            page._hint.setText(  # type: ignore[attr-defined]
                f"Placing: {self._pending_component.get('name', '?')} — click a green "
                "(compatible) slot to install, a filled slot to remove."
            )
        else:
            page._hint.setText(  # type: ignore[attr-defined]
                "Select a component on the left, then click a compatible slot. "
                "With no component selected, clicking a filled slot removes one."
            )

        _clear_layout(page._slot_layout)  # type: ignore[attr-defined]
        pending_cat = (self._pending_component or {}).get("category", "")
        for i, slot in enumerate(design.slots):
            pos = slot.get("position", {})
            slot_type = slot.get("slot-type", "")
            assignment = design.assignments[i]
            if assignment is not None:
                comp = assignment["component"]
                title = comp.get("name", "?")
                count_text = f"{assignment['count']} of {design.slot_max(i)}"
                filled = True
                state = "normal"
            else:
                title = _slot_label(slot_type)
                mx = design.slot_max(i)
                count_text = f"up to {mx}" if mx > 1 else ""
                filled = False
                state = "normal"
                if self._pending_component is not None:
                    state = "compatible" if slot_accepts(slot_type, pending_cat) else "incompatible"
            tile = _SlotTile(
                i, title, count_text=count_text, filled=filled, state=state, interactive=True
            )
            tile.clicked.connect(self._on_edit_slot_clicked)
            page._slot_layout.addWidget(  # type: ignore[attr-defined]
                tile, int(pos.get("row", 0)), int(pos.get("col", i))
            )

        _clear_layout(page._footer_layout)  # type: ignore[attr-defined]
        cost = _wire_cost_to_display(design.total_cost())
        stats = {
            "Mass": f"{design.total_mass()}kT",
            "Slots filled": f"{design.filled_slot_count()} of {len(design.slots)}",
        }
        self._fill_cost_stats(
            page._footer_layout,  # type: ignore[attr-defined]
            f"Cost of one {name}",
            cost,
            stats,
        )

    # ── Components view selection ─────────────────────────────────────────────

    def _on_components_view_selection(self, component) -> None:
        page = self._page_components
        detail = getattr(page, "_detail", None)
        if detail is None:
            return
        if component is None:
            detail.setText("")
            return
        cost = component.get("cost", {}) or {}
        mass = component.get("mass")
        avail = (
            "Available"
            if component_available(
                component,
                getattr(self._race, "prt", ""),
                getattr(self._race, "lrts", []),
            )
            else "Not available to your race"
        )
        parts = [
            f"<b>{component.get('name', '?')}</b>",
            "Cost: {ironium}kT Ir, {boranium}kT Bo, {germanium}kT Ge, {resources} res".format(
                ironium=cost.get("ironium", 0),
                boranium=cost.get("boranium", 0),
                germanium=cost.get("germanium", 0),
                resources=cost.get("resources", 0),
            ),
        ]
        if mass is not None:
            parts.append(f"Mass: {mass}kT")
        parts.append(avail)
        desc = component.get("description")
        if desc:
            parts.append(f"<i>{desc}</i>")
        detail.setText("<br>".join(parts))

    # ── Left-rail handlers ─────────────────────────────────────────────────────

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

    def _on_copy_or_create(self) -> None:
        if self._view_mode == _VIEW_AVAILABLE:
            hulls = self._available_hulls()
            idx = self._name_combo.currentIndex()
            if 0 <= idx < len(hulls):
                hull = hulls[idx]
                self._start_editing(hull, f"New {hull.get('name', 'Design')}")
            return
        # Copying an existing (placeholder) design needs the host design model.
        QMessageBox.information(
            self,
            "Copy Design",
            "Copying an existing design will be available once the engine serves "
            "your designs (host design model). For now, choose Available Hull "
            "Types and Create New Design to try the slot editor.",
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
        QMessageBox.information(
            self,
            "Delete Design",
            "Design deletion is not yet wired to the engine (host design model).",
        )

    def _on_edit_design(self) -> None:
        QMessageBox.information(
            self,
            "Edit Design",
            "Editing an existing design will be available once the engine serves "
            "your designs (host design model). For now, choose Available Hull "
            "Types and Create New Design to try the slot editor.",
        )

    def _on_help(self) -> None:
        QMessageBox.information(
            self,
            "Ship Designer Help",
            "Ship Designer help — to be wired up to the Player's Guide.",
        )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _wire_cost_to_display(cost: dict) -> dict:
    """Map a wire mineral-cost dict to the footer's display labels."""
    return {
        "Ironium": f"{int(cost.get('ironium', 0) or 0)}kT",
        "Boranium": f"{int(cost.get('boranium', 0) or 0)}kT",
        "Germanium": f"{int(cost.get('germanium', 0) or 0)}kT",
        "Resources": f"{int(cost.get('resources', 0) or 0)}",
    }


def _clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
