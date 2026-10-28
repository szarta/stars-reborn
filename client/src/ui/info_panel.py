"""
ui/info_panel.py

Left-side command panel: two columns of context-sensitive sections + messages pane.

Column 1: Planet header (name/icon/nav), Minerals On Hand, Status
Column 2: Fleets In Orbit, Production, Route To, Starbase
Bottom:   Messages pane
"""

from __future__ import annotations

import glob
import math

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QBoxLayout,
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QWidget,
)

from ..rendering.enumerations import NeverSeenPlanet, PrimaryRacialTrait, ResourcePaths


def _getattr_safe(obj, *attrs, default=None):
    for attr in attrs:
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return default


def _next_owned_id(planets, player_id, current_id, direction):
    """Return the id of the next planet owned by ``player_id`` relative to
    ``current_id``, stepping in ``direction`` (+1 forward, -1 back) and wrapping
    at both ends.

    Owned worlds are ordered by id so navigation is deterministic. If
    ``current_id`` is not among the owned worlds, navigation starts at the first
    owned world (forward) or the last (back). Returns ``None`` when the player
    owns no worlds.
    """
    ids = sorted(p.id for p in planets if getattr(p, "owner", None) == player_id)
    if not ids:
        return None
    if current_id in ids:
        idx = (ids.index(current_id) + direction) % len(ids)
    else:
        idx = 0 if direction > 0 else len(ids) - 1
    return ids[idx]


def build_buildables_map(response):
    """Index a ``GET /model/buildables`` response by numeric build-object-id.

    Returns ``{id: {"name", "kind", "category", "design_slot"}}``. Clients read
    this registry from the engine rather than hardcoding the id→name mapping.
    """
    out: dict[int, dict] = {}
    for b in (response or {}).get("buildables", []):
        try:
            oid = int(b["build-object-id"])
        except (KeyError, TypeError, ValueError):
            continue
        out[oid] = {
            "name": b.get("name", f"Buildable {oid}"),
            "kind": b.get("kind"),
            "category": b.get("category"),
            "design_slot": b.get("design-slot"),
        }
    return out


def _queue_row_label(entry, buildables):
    """Human-readable list row for one production-queue entry: quantity, name,
    and (for the item in progress) its percent-complete contribution."""
    oid = entry.get("build_object_id")
    qty = entry.get("build_quantity", 0)
    meta = buildables.get(oid) if buildables else None
    name = meta["name"] if meta else f"Buildable {oid}"
    label = f"{qty} {name}"
    progress = entry.get("build_progress") or 0
    if progress:
        label += f"  ({progress}%)"
    return label


def order_items_from_entries(entries, buildables):
    """Convert working queue entries into ``planet.set_production_queue`` order
    items (``{"item": {"kind"[, "design_slot"]}, "count"}``), resolving each
    build-object-id back to its semantic kind via the buildable registry.

    Entries whose id is unknown to the registry are dropped — the engine would
    reject them, and the registry is the authority on what is buildable.
    """
    items = []
    for e in entries:
        meta = buildables.get(e.get("build_object_id")) if buildables else None
        if not meta or not meta.get("kind"):
            continue
        item = {"kind": meta["kind"]}
        if meta.get("design_slot") is not None:
            item["design_slot"] = meta["design_slot"]
        items.append({"item": item, "count": e.get("build_quantity", 0)})
    return items


def starbase_field_rows(starbase, names=None):
    """Format a planet's starbase stats into the display strings shown by the
    Starbase section, or ``None`` when the planet has no starbase.

    ``starbase`` is the snake-keyed dict carried on ``PlanetData.starbase``
    (the engine's per-planet starbase stats). ``names`` maps planet id → name
    so a mass-driver packet destination can show by name. Returning ``None``
    for a missing/empty starbase lets the section collapse to a "No Starbase"
    placeholder. Individual absent fields render as "n/a", so the section
    degrades cleanly before the engine serializes every field (parallel to the
    Status section — see task #54).
    """
    if not starbase:
        return None
    names = names or {}

    def _dp(v):
        return f"{v} dp" if v is not None else "n/a"

    dock = starbase.get("dock_capacity")
    damage = starbase.get("damage_percent")
    driver = starbase.get("mass_driver")
    dest = starbase.get("packet_target")
    return {
        "dock": "n/a" if dock is None else f"{dock} kT",
        "armor": _dp(starbase.get("armor")),
        "shields": _dp(starbase.get("shields")),
        "damage": "none" if not damage else f"{damage}%",
        "mass_driver": str(driver) if driver else "None",
        "dest": names.get(dest, str(dest)) if dest is not None else "none",
    }


def starbase_has_mass_driver(starbase) -> bool:
    """True when the planet's starbase mounts a mass driver, so a packet
    destination can be set. A falsy or absent rating means no driver."""
    return bool(starbase) and bool(starbase.get("mass_driver"))


# ── Section title bar with collapse arrow ─────────────────────────────────


class _SectionPane(QWidget):
    """Collapsible titled section — common building block for both panel columns."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._hidden = False

        title_bar = QFrame()
        title_bar.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)

        self._title_label = QLabel(title)
        self._title_label.setAlignment(Qt.AlignCenter)

        arrow_pix = QPixmap(ResourcePaths.HideArrowPath)
        self._toggle_btn = QPushButton()
        if not arrow_pix.isNull():
            self._toggle_btn.setIcon(QIcon(arrow_pix))
            self._toggle_btn.setIconSize(arrow_pix.rect().size())
        else:
            self._toggle_btn.setText("▲")
        self._toggle_btn.setFixedSize(24, 24)
        self._toggle_btn.setFlat(True)
        self._toggle_btn.clicked.connect(self._toggle)

        bar_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        bar_layout.setContentsMargins(2, 0, 2, 0)
        bar_layout.addWidget(self._title_label, 1)
        bar_layout.addWidget(self._toggle_btn)
        title_bar.setLayout(bar_layout)

        self._content = QFrame()
        self._content.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)

        main = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(title_bar)
        main.addWidget(self._content)
        self.setLayout(main)

    def set_content_layout(self, layout):
        if self._content.layout():
            old = self._content.layout()
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            old.deleteLater()
        self._content.setLayout(layout)

    def set_title(self, title: str):
        self._title_label.setText(title)

    def _toggle(self):
        if self._hidden:
            self._content.show()
            self._hidden = False
        else:
            self._content.hide()
            self._hidden = True


# ── Column 1: Planet header ────────────────────────────────────────────────


class _PlanetHeaderSection(_SectionPane):
    """Planet name (title bar) + planet image + Prev/Next navigation."""

    # Emitted with +1 (Next) or -1 (Prev) when the player clicks a nav button.
    nav_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__("", parent)
        self._planet_files = sorted(glob.glob(f"{ResourcePaths.PlanetsPath}/*.png"))

        self._picture = QLabel()
        self._picture.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self._picture.setAlignment(Qt.AlignCenter)
        self._picture.setFixedSize(68, 68)
        self._picture.setAutoFillBackground(True)
        self._picture.setStyleSheet("background-color: black;")

        self._prev_btn = QPushButton("Prev")
        self._next_btn = QPushButton("Next")
        self._prev_btn.clicked.connect(lambda: self.nav_requested.emit(-1))
        self._next_btn.clicked.connect(lambda: self.nav_requested.emit(1))

        btn_col = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        btn_col.addWidget(self._prev_btn)
        btn_col.addWidget(self._next_btn)
        btn_col.addStretch(1)

        row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        row.setContentsMargins(4, 4, 4, 4)
        row.addStretch(1)
        row.addWidget(self._picture)
        row.addLayout(btn_col)
        row.addStretch(1)
        self.set_content_layout(row)

    def update_planet(self, planet):
        self.set_title(planet.name)
        if getattr(planet, "years_since", 0) == NeverSeenPlanet:
            path = ResourcePaths.UnknownPlanetIcon
        elif self._planet_files:
            path = self._planet_files[planet.id % len(self._planet_files)]
        else:
            self._picture.clear()
            return
        pix = QPixmap(path)
        if not pix.isNull():
            self._picture.setPixmap(pix.scaled(68, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self._picture.clear()


# ── Column 1: Minerals On Hand ─────────────────────────────────────────────


class _MineralsSection(_SectionPane):
    """Surface minerals (Ironium/Boranium/Germanium in kT) + mines and factories."""

    def __init__(self, parent=None):
        super().__init__("Minerals On Hand", parent)

        self._iron_val = QLabel("0 kT")
        self._bor_val = QLabel("0 kT")
        self._ger_val = QLabel("0 kT")
        self._mines_val = QLabel("0")
        self._factories_val = QLabel("0")

        iron_lbl = QLabel("<b>Ironium</b>")
        iron_lbl.setStyleSheet("color: #4488ff")
        bor_lbl = QLabel("<b>Boranium</b>")
        bor_lbl.setStyleSheet("color: #44cc44")
        ger_lbl = QLabel("<b>Germanium</b>")
        ger_lbl.setStyleSheet("color: #dddd00")

        def _row(label, value_label):
            r = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            r.addWidget(label)
            r.addStretch(1)
            r.addWidget(value_label)
            return r

        col = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        col.setContentsMargins(4, 4, 4, 4)
        col.setSpacing(2)
        col.addLayout(_row(iron_lbl, self._iron_val))
        col.addLayout(_row(bor_lbl, self._bor_val))
        col.addLayout(_row(ger_lbl, self._ger_val))

        divider = QFrame()
        divider.setFrameStyle(QFrame.Shape.HLine | QFrame.Shadow.Sunken)
        col.addWidget(divider)

        col.addLayout(_row(QLabel("<b>Mines</b>"), self._mines_val))
        col.addLayout(_row(QLabel("<b>Factories</b>"), self._factories_val))
        self.set_content_layout(col)

    def update_planet(self, planet, player=None):
        self._iron_val.setText(f"{getattr(planet, 'surface_ironium', 0)} kT")
        self._bor_val.setText(f"{getattr(planet, 'surface_boranium', 0)} kT")
        self._ger_val.setText(f"{getattr(planet, 'surface_germanium', 0)} kT")

        prt = None
        if player is not None:
            race = getattr(player, "race", None)
            if race is not None:
                prt = getattr(race, "primary_racial_trait", None)

        pop = getattr(planet, "population", 0)
        if prt == PrimaryRacialTrait.AlternateReality:
            self._mines_val.setText(f"{int(math.sqrt(max(0, pop)) / 10)}*")
            self._factories_val.setText("n/a")
        else:
            self._mines_val.setText(str(getattr(planet, "mines", 0)))
            self._factories_val.setText(str(getattr(planet, "factories", 0)))


# ── Column 1: Status ───────────────────────────────────────────────────────


class _StatusSection(_SectionPane):
    """Population, resources/year, scanner, defenses."""

    def __init__(self, parent=None):
        super().__init__("Status", parent)

        self._pop_val = QLabel("n/a")
        self._res_val = QLabel("n/a")
        self._scanner_type_val = QLabel("n/a")
        self._scanner_range_val = QLabel("n/a")
        self._defenses_val = QLabel("n/a")
        self._defense_type_val = QLabel("n/a")
        self._def_coverage_val = QLabel("n/a")

        rows = [
            ("Population", self._pop_val),
            ("Resources/Year", self._res_val),
            ("Scanner Type", self._scanner_type_val),
            ("Scanner Range", self._scanner_range_val),
            ("Defenses", self._defenses_val),
            ("Defense Type", self._defense_type_val),
            ("Def Coverage", self._def_coverage_val),
        ]

        col = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        col.setContentsMargins(4, 4, 4, 4)
        col.setSpacing(1)
        for lbl_text, val_lbl in rows:
            r = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            r.addWidget(QLabel(lbl_text))
            r.addStretch(1)
            r.addWidget(val_lbl)
            col.addLayout(r)
        self.set_content_layout(col)

    def update_planet(self, planet, player=None):
        pop = getattr(planet, "population", 0)
        self._pop_val.setText(f"{pop:,}" if pop else "0")

        res = getattr(planet, "resources_per_year", None)
        cap = getattr(planet, "resource_capacity", None)
        if res is not None and cap is not None:
            self._res_val.setText(f"{res} of {cap}")
        elif res is not None:
            self._res_val.setText(str(res))
        else:
            self._res_val.setText("n/a")

        scanner = getattr(planet, "scanner_type", None)
        self._scanner_type_val.setText(scanner or "n/a")

        sr = getattr(planet, "scanner_range", None)
        self._scanner_range_val.setText(f"{sr} light years" if sr is not None else "n/a")

        defenses = getattr(planet, "defenses", None)
        self._defenses_val.setText(str(defenses) if defenses is not None else "n/a")

        def_type = getattr(planet, "defense_type", None)
        self._defense_type_val.setText(def_type or "n/a")

        coverage = getattr(planet, "defense_coverage", None)
        self._def_coverage_val.setText(str(coverage) if coverage is not None else "n/a")


# ── Column 2: Fleets In Orbit ─────────────────────────────────────────────


class _FleetsInOrbitSection(_SectionPane):
    """Fleet selector dropdown + fuel/cargo bars + Goto/Cargo buttons."""

    def __init__(self, parent=None):
        super().__init__("Fleets in Orbit", parent)

        self._fleet_combo = QComboBox()
        self._fleet_combo.addItem("(No fleets in orbit)")

        def _bar_row(label_text):
            lbl = QLabel(label_text)
            lbl.setFixedWidth(38)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(14)
            r = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            r.addWidget(lbl)
            r.addWidget(bar, 1)
            return r, bar

        fuel_row, self._fuel_bar = _bar_row("Fuel")
        cargo_row, self._cargo_bar = _bar_row("Cargo")

        btn_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        btn_row.addWidget(QPushButton("Goto"))
        btn_row.addStretch(1)
        btn_row.addWidget(QPushButton("Cargo"))

        col = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        col.setContentsMargins(4, 4, 4, 4)
        col.setSpacing(3)
        col.addWidget(self._fleet_combo)
        col.addLayout(fuel_row)
        col.addLayout(cargo_row)
        col.addLayout(btn_row)
        self.set_content_layout(col)


# ── Column 2: Production ───────────────────────────────────────────────────


class _ProductionSection(_SectionPane):
    """Production queue for the selected planet.

    Shows the queue from the engine's per-player turn file (present only for
    owned planets) and lets the player remove/reorder entries. Each edit
    re-emits ``queue_changed(planet_id, order_items)`` so the host can submit
    the whole new queue to the engine. Adding an item needs the buildable
    picker, which is a separate task — ``add_item_requested`` is the hook for it.
    """

    # (planet_id, order-item list) — the full queue after an edit, ready to
    # PUT as a planet.set_production_queue order.
    queue_changed = Signal(int, list)
    # planet_id — the Add button; the item-picker dialog is a deferred child task.
    add_item_requested = Signal(int)

    _EMPTY_PLACEHOLDER = "--- Queue is Empty ---"

    def __init__(self, parent=None):
        super().__init__("Production", parent)

        self._buildables: dict[int, dict] = {}
        self._planet = None
        self._owned = False
        self._editable = False
        # Working copy of the queue; entries are the snake-keyed dicts carried
        # on PlanetData.build_queue.
        self._entries: list[dict] = []

        self._queue = QListWidget()
        self._queue.setMinimumHeight(70)
        self._queue.currentRowChanged.connect(lambda _: self._refresh_buttons())

        self._add_btn = QPushButton("Add")
        self._remove_btn = QPushButton("Remove")
        self._up_btn = QPushButton("Up")
        self._down_btn = QPushButton("Down")
        self._add_btn.clicked.connect(self._on_add)
        self._remove_btn.clicked.connect(self._on_remove)
        self._up_btn.clicked.connect(lambda: self._on_move(-1))
        self._down_btn.clicked.connect(lambda: self._on_move(1))

        btn_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(2)
        for b in (self._add_btn, self._remove_btn, self._up_btn, self._down_btn):
            btn_row.addWidget(b)

        col = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        col.setContentsMargins(4, 4, 4, 4)
        col.addWidget(self._queue)
        col.addLayout(btn_row)
        self.set_content_layout(col)

        self._render()

    def set_buildables(self, mapping):
        """Install the build-object-id → metadata map (see build_buildables_map).
        Re-renders so queue rows show real names once it arrives."""
        self._buildables = mapping or {}
        self._render()

    def set_editable(self, editable: bool):
        """Enable the edit controls. Off when there is no engine to submit to
        (e.g. a locally loaded turn file)."""
        self._editable = bool(editable)
        self._refresh_buttons()

    def update_planet(self, planet, player=None):
        self._planet = planet
        queue = getattr(planet, "build_queue", None) if planet is not None else None
        self._owned = queue is not None
        self._entries = [dict(e) for e in (queue or [])]
        self._render()

    # ── rendering / state ────────────────────────────────────────────────
    def _render(self):
        self._queue.clear()
        if self._entries:
            for e in self._entries:
                self._queue.addItem(_queue_row_label(e, self._buildables))
        else:
            self._queue.addItem(self._EMPTY_PLACEHOLDER)
        self._refresh_buttons()

    def _selected_index(self) -> int:
        """Current row, or -1 when nothing real is selected."""
        if not self._entries:
            return -1
        row = self._queue.currentRow()
        return row if 0 <= row < len(self._entries) else -1

    def _refresh_buttons(self):
        can_edit = self._editable and self._owned
        idx = self._selected_index()
        has_sel = idx >= 0
        self._add_btn.setEnabled(can_edit)
        self._remove_btn.setEnabled(can_edit and has_sel)
        self._up_btn.setEnabled(can_edit and has_sel and idx > 0)
        self._down_btn.setEnabled(can_edit and has_sel and idx < len(self._entries) - 1)

    # ── edit handlers ────────────────────────────────────────────────────
    def _on_add(self):
        if self._planet is not None:
            self.add_item_requested.emit(self._planet.id)

    def _on_remove(self):
        idx = self._selected_index()
        if idx < 0:
            return
        del self._entries[idx]
        self._commit(min(idx, len(self._entries) - 1))

    def _on_move(self, delta: int):
        idx = self._selected_index()
        if idx < 0:
            return
        new = idx + delta
        if not (0 <= new < len(self._entries)):
            return
        self._entries[idx], self._entries[new] = self._entries[new], self._entries[idx]
        self._commit(new)

    def _commit(self, select_row: int):
        """Re-render after an edit, restore the selection, mirror the change
        onto the planet model, and emit the new queue for submission."""
        self._render()
        if 0 <= select_row < len(self._entries):
            self._queue.setCurrentRow(select_row)
        if self._planet is not None:
            self._planet.build_queue = [dict(e) for e in self._entries]
            self.queue_changed.emit(
                self._planet.id, order_items_from_entries(self._entries, self._buildables)
            )


# ── Column 2: Route To ────────────────────────────────────────────────────


class _RouteSection(_SectionPane):
    """Planet "Route To" destination + Change/Clear/Route buttons.

    The route destination is always a planet (clicking empty space or any object
    snaps to the nearest planet — confirmed against the original game; see
    knowledge/findings/route_to.rst). Change/Clear emit requests that the host
    turns into a ``planet.set_route_target`` order. The Route button routes the
    selected fleet to this destination — a fleet order deferred to task #141.
    """

    change_requested = Signal(int)  # planet_id — begin picking a route target
    clear_requested = Signal(int)  # planet_id — clear the route
    route_requested = Signal(int)  # planet_id — route selected fleet (deferred)

    def __init__(self, parent=None):
        super().__init__("Route To", parent)

        self._planet = None
        self._owned = False
        self._editable = False
        self._names: dict[int, str] = {}
        self._player_id = None

        dest_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        dest_row.addWidget(QLabel("Route to"))
        dest_row.addStretch(1)
        self._dest_label = QLabel("none")
        dest_row.addWidget(self._dest_label)

        self._change_btn = QPushButton("Change")
        self._clear_btn = QPushButton("Clear")
        self._route_btn = QPushButton("Route")
        self._change_btn.clicked.connect(self._on_change)
        self._clear_btn.clicked.connect(self._on_clear)
        self._route_btn.clicked.connect(self._on_route)

        btn_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        btn_row.addWidget(self._change_btn)
        btn_row.addWidget(self._clear_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self._route_btn)

        col = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        col.setContentsMargins(4, 4, 4, 4)
        col.setSpacing(4)
        col.addLayout(dest_row)
        col.addLayout(btn_row)
        self.set_content_layout(col)

        self._refresh_buttons()

    def set_universe(self, planets, player_id):
        """Store an id → name map (to show a route target by name) and the
        active player id (to tell which planets the player can route)."""
        self._names = {p.id: getattr(p, "name", str(p.id)) for p in planets}
        self._player_id = player_id

    def set_editable(self, editable: bool):
        self._editable = bool(editable)
        self._refresh_buttons()

    def update_planet(self, planet, player=None):
        self._planet = planet
        target = getattr(planet, "route_target", None) if planet is not None else None
        self._owned = planet is not None and getattr(planet, "owner", None) == self._player_id
        self._dest_label.setText(self._names.get(target, "none") if target is not None else "none")
        self._refresh_buttons()

    def _refresh_buttons(self):
        can_edit = self._editable and self._owned
        self._change_btn.setEnabled(can_edit)
        has_route = (
            self._planet is not None and getattr(self._planet, "route_target", None) is not None
        )
        self._clear_btn.setEnabled(can_edit and has_route)
        self._route_btn.setEnabled(can_edit and has_route)

    def _on_change(self):
        if self._planet is not None:
            self.change_requested.emit(self._planet.id)

    def _on_clear(self):
        if self._planet is not None:
            self.clear_requested.emit(self._planet.id)

    def _on_route(self):
        if self._planet is not None:
            self.route_requested.emit(self._planet.id)


# ── Column 2: Starbase ────────────────────────────────────────────────────


class _StarbaseSection(_SectionPane):
    """Starbase stats for the selected planet, plus the mass-driver packet
    destination picker.

    Data-driven from ``PlanetData.starbase`` (the engine's per-planet starbase
    stats). A planet with no starbase collapses the stat rows to a "No
    Starbase" placeholder. ``Set Dest`` emits ``set_dest_requested(planet_id)``
    so the host can pick a destination planet and submit a
    ``planet.set_packet_target`` order; it enables only for an owned planet
    whose starbase mounts a mass driver, and only when order editing is on.

    The engine does not serialize starbase stats yet, nor dispatch the
    ``planet.set_packet_target`` order (engine work tracked in task #142,
    parallel to the Status section's #54); until it does, every planet reads as
    "No Starbase" and Set Dest stays disabled.
    """

    # planet_id — begin picking a mass-driver packet destination on the map.
    set_dest_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__("Starbase", parent)

        self._planet = None
        self._owned = False
        self._editable = False
        self._names: dict[int, str] = {}
        self._player_id = None
        # Display strings for the current planet's starbase, or None when the
        # planet has no starbase; and whether that starbase mounts a driver.
        self._display: dict | None = None
        self._has_driver = False

        self._dock_val = QLabel("n/a")
        self._armor_val = QLabel("n/a")
        self._shields_val = QLabel("n/a")
        self._damage_val = QLabel("n/a")
        self._mass_driver_val = QLabel("n/a")
        self._dest_val = QLabel("n/a")

        def _row(lbl_text, val_lbl):
            w = QWidget()
            r = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            r.setContentsMargins(0, 0, 0, 0)
            r.addWidget(QLabel(lbl_text))
            r.addStretch(1)
            r.addWidget(val_lbl)
            w.setLayout(r)
            return w

        self._stat_rows = [
            _row("Dock Capacity", self._dock_val),
            _row("Armor", self._armor_val),
            _row("Shields", self._shields_val),
            _row("Damage", self._damage_val),
            _row("Mass Driver", self._mass_driver_val),
            _row("Destination", self._dest_val),
        ]

        self._no_starbase = QLabel("No Starbase")
        self._no_starbase.setAlignment(Qt.AlignCenter)

        self._set_dest_btn = QPushButton("Set Dest")
        self._set_dest_btn.setEnabled(False)
        self._set_dest_btn.clicked.connect(self._on_set_dest)

        col = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        col.setContentsMargins(4, 4, 4, 4)
        col.setSpacing(1)
        col.addWidget(self._no_starbase)
        for w in self._stat_rows:
            col.addWidget(w)
        col.addWidget(self._set_dest_btn, 0, Qt.AlignLeft)
        self.set_content_layout(col)

        self._render()

    def set_universe(self, planets, player_id):
        """Store an id → name map (to show a packet destination by name) and
        the active player id (to tell which planets the player controls)."""
        self._names = {p.id: getattr(p, "name", str(p.id)) for p in planets}
        self._player_id = player_id

    def set_editable(self, editable: bool):
        """Enable the Set Dest control. Off when there is no engine to submit
        to (e.g. a locally loaded turn file)."""
        self._editable = bool(editable)
        self._refresh_buttons()

    def update_planet(self, planet, player=None):
        self._planet = planet
        starbase = getattr(planet, "starbase", None) if planet is not None else None
        self._owned = planet is not None and getattr(planet, "owner", None) == self._player_id
        self._display = starbase_field_rows(starbase, self._names)
        self._has_driver = starbase_has_mass_driver(starbase)
        self._render()

    def _render(self):
        has_starbase = self._display is not None
        self._no_starbase.setVisible(not has_starbase)
        for w in self._stat_rows:
            w.setVisible(has_starbase)
        self._set_dest_btn.setVisible(has_starbase)
        if has_starbase:
            self._dock_val.setText(self._display["dock"])
            self._armor_val.setText(self._display["armor"])
            self._shields_val.setText(self._display["shields"])
            self._damage_val.setText(self._display["damage"])
            self._mass_driver_val.setText(self._display["mass_driver"])
            self._dest_val.setText(self._display["dest"])
        self._refresh_buttons()

    def _refresh_buttons(self):
        self._set_dest_btn.setEnabled(
            self._editable and self._owned and self._display is not None and self._has_driver
        )

    def _on_set_dest(self):
        if self._planet is not None:
            self.set_dest_requested.emit(self._planet.id)


# ── Messages pane ──────────────────────────────────────────────────────────


class _MessagesPane(QWidget):
    """Year/message counter bar + message text area at the bottom of the left panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)

        top_bar = QFrame()
        top_bar.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)

        self._filter_check = QCheckBox()
        self._filter_check.setChecked(True)
        self._filter_check.setFixedSize(18, 18)
        self._filter_check.setToolTip("Hide unimportant messages")

        self._year_count_label = QLabel("Year: 2400   Messages: 0 of 0")

        self._prev_btn = QPushButton("Prev")
        self._prev_btn.setFixedWidth(36)
        self._goto_btn = QPushButton("Goto")
        self._goto_btn.setFixedWidth(36)
        self._next_btn = QPushButton("Next")
        self._next_btn.setFixedWidth(36)

        bar_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        bar_layout.setContentsMargins(2, 2, 2, 2)
        bar_layout.setSpacing(2)
        bar_layout.addWidget(self._filter_check)
        bar_layout.addWidget(self._year_count_label, 1)
        bar_layout.addWidget(self._prev_btn)
        bar_layout.addWidget(self._goto_btn)
        bar_layout.addWidget(self._next_btn)
        top_bar.setLayout(bar_layout)

        self._msg_text = QLabel("(No messages)")
        self._msg_text.setWordWrap(True)
        self._msg_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._msg_text.setContentsMargins(4, 4, 4, 4)
        self._msg_text.setStyleSheet("background: black; color: white;")

        main = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        main.addWidget(top_bar)
        main.addWidget(self._msg_text, 1)
        self.setLayout(main)

    def set_year(self, year: int):
        self._year_count_label.setText(f"Year: {year}   Messages: 0 of 0")


# ── Left panel (top-level assembly) ───────────────────────────────────────


class LeftPanel(QWidget):
    """
    The left-side command panel.

    Two adjacent section columns fill the top area; a messages pane sits below.
    Call update_planet(planet, player) whenever selection changes.

    Prev/Next in the planet header cycle through the active player's owned
    worlds; the resulting planet id is re-emitted via ``planet_nav_requested``
    so the host can update the map selection and the other panes in step.
    """

    # Emitted with a planet id when Prev/Next picks a new world to navigate to.
    planet_nav_requested = Signal(int)
    # Forwarded from the Production section: (planet_id, order-item list) after a
    # queue edit, and the planet_id of an Add request (picker is a child task).
    queue_changed = Signal(int, list)
    add_item_requested = Signal(int)
    # Forwarded from the Route To section.
    route_change_requested = Signal(int)
    route_clear_requested = Signal(int)
    route_fleet_requested = Signal(int)
    # Forwarded from the Starbase section: pick a mass-driver packet destination.
    packet_dest_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(360)
        self.setMaximumWidth(520)

        # Universe context for Prev/Next navigation; populated by set_universe().
        self._planets: list = []
        self._player_id = None
        self._current_planet = None

        # ── Column 1 ──────────────────────────────────────────────────────
        self._planet_header = _PlanetHeaderSection()
        self._planet_header.nav_requested.connect(self._on_nav)
        self._minerals = _MineralsSection()
        self._status = _StatusSection()

        col1 = QWidget()
        c1 = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        c1.setContentsMargins(0, 0, 0, 0)
        c1.setSpacing(0)
        c1.addWidget(self._planet_header)
        c1.addWidget(self._minerals)
        c1.addWidget(self._status)
        c1.addStretch(1)
        col1.setLayout(c1)

        # ── Column 2 ──────────────────────────────────────────────────────
        self._fleets = _FleetsInOrbitSection()
        self._production = _ProductionSection()
        self._production.queue_changed.connect(self.queue_changed)
        self._production.add_item_requested.connect(self.add_item_requested)
        self._route = _RouteSection()
        self._route.change_requested.connect(self.route_change_requested)
        self._route.clear_requested.connect(self.route_clear_requested)
        self._route.route_requested.connect(self.route_fleet_requested)
        self._starbase = _StarbaseSection()
        self._starbase.set_dest_requested.connect(self.packet_dest_requested)

        col2 = QWidget()
        c2 = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        c2.setContentsMargins(0, 0, 0, 0)
        c2.setSpacing(0)
        c2.addWidget(self._fleets)
        c2.addWidget(self._production)
        c2.addWidget(self._route)
        c2.addWidget(self._starbase)
        c2.addStretch(1)
        col2.setLayout(c2)

        # ── Two-column row ─────────────────────────────────────────────────
        columns = QWidget()
        cols = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        cols.setContentsMargins(0, 0, 0, 0)
        cols.setSpacing(0)
        cols.addWidget(col1)
        cols.addWidget(col2)
        columns.setLayout(cols)

        # ── Messages pane ──────────────────────────────────────────────────
        self._messages = _MessagesPane()

        # ── Vertical splitter: columns (top) / messages (bottom) ───────────
        # Original game anchors the messages pane to the bottom at a fixed
        # height; the section columns absorb vertical resize.
        self._splitter = QSplitter(Qt.Vertical)
        self._splitter.addWidget(columns)
        self._splitter.addWidget(self._messages)
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 0)

        main = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(self._splitter)
        self.setLayout(main)

    def set_universe(self, planets, player_id):
        """Give the panel the full planets list and the active player id so
        Prev/Next can cycle through that player's owned worlds and the Route
        section can resolve/own targets."""
        self._planets = list(planets)
        self._player_id = player_id
        self._route.set_universe(self._planets, player_id)
        self._starbase.set_universe(self._planets, player_id)

    def set_buildables(self, mapping):
        """Forward the buildable registry to the Production section."""
        self._production.set_buildables(mapping)

    def set_production_editable(self, editable: bool):
        """Enable production-queue editing (off when there is no engine)."""
        self._production.set_editable(editable)

    def set_route_editable(self, editable: bool):
        """Enable route editing (off when there is no engine to submit to)."""
        self._route.set_editable(editable)

    def set_starbase_editable(self, editable: bool):
        """Enable the Starbase Set Dest control (off with no engine to submit to)."""
        self._starbase.set_editable(editable)

    def update_planet(self, planet, player=None):
        self._current_planet = planet
        self._planet_header.update_planet(planet)
        self._minerals.update_planet(planet, player)
        self._status.update_planet(planet, player)
        self._production.update_planet(planet, player)
        self._route.update_planet(planet, player)
        self._starbase.update_planet(planet, player)

    def _on_nav(self, direction: int):
        """Prev/Next clicked: pick the adjacent owned world and ask the host to
        select it."""
        current_id = getattr(self._current_planet, "id", None)
        pid = _next_owned_id(self._planets, self._player_id, current_id, direction)
        if pid is not None:
            self.planet_nav_requested.emit(pid)

    def set_year(self, year: int):
        self._messages.set_year(year)


# ── Back-compat alias ──────────────────────────────────────────────────────
InfoPanel = LeftPanel
