"""
ui/dialogs/technology_browser.py

Technology Browser dialog — browse the ship/starbase component catalog served
by the engine at ``GET /model/technologies``.

Reproduces the layout of the original Stars! Technology Browser (see
stars-reborn-research/experiments/screencaps/tech_browser/):

  ┌──── Technology Browser ─────────────────────────────────────┐
  │ [← Prev]  [ Engines              ▾]  [Next →]                │
  │                       Settler's Delight                     │
  │  ┌──────┐   Ironium    1kT    Mass: 2kT                     │
  │  │ icon │   Boranium   0kT                                  │
  │  └──────┘   Germanium  1kT                                  │
  │  Tech Req:  Resources  2                                     │
  │   None                                                       │
  │  UnAvail   ┌──── Fuel Usage vs. Warp Speed ───────────────┐ │
  │            │           (per-category detail)              │ │
  │            └──────────────────────────────────────────────┘ │
  │  This engine can only be mounted on ... (restriction line)  │
  │  [ ] Show Only Available Technology              [ Close ]  │
  └─────────────────────────────────────────────────────────────┘

The browser is data-driven: it renders whatever categories the endpoint
returns (the live catalog currently serves a subset; it fills in as the engine
component catalog grows — see engine task #149). Engines get a faithful
Fuel-Usage-vs-Warp graph; every other category gets a generic stats panel.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

import logging

import requests
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ...data.technologies import (
    CATEGORY_LABELS,
    component_available,
    group_by_category,
)
from ._components_common import component_icon

log = logging.getLogger(__name__)

# ── Presentation constants ───────────────────────────────────────────────────

# Mineral text colors (approximating the original's palette).
_IRONIUM_COLOR = "#8fa9ff"
_BORANIUM_COLOR = "#4fcf4f"
_GERMANIUM_COLOR = "#d8c838"
_RESOURCE_COLOR = "#4fcf4f"

_TECH_FIELDS = [
    ("energy", "Ene"),
    ("weapons", "Wea"),
    ("propulsion", "Pro"),
    ("construction", "Con"),
    ("electronics", "Ele"),
    ("biotechnology", "Bio"),
]

# Full names for PRT/LRT codes used in the restriction line.
_PRT_NAMES = {
    "HE": "Hyper-Expansion",
    "SS": "Super-Stealth",
    "WM": "War Monger",
    "CA": "Claim Adjuster",
    "IS": "Inner Strength",
    "SD": "Space Demolition",
    "PP": "Packet Physics",
    "IT": "Interstellar Traveler",
    "AR": "Alternate Reality",
    "JOAT": "Jack of All Trades",
}


# ── Engine fuel-usage graph ──────────────────────────────────────────────────


class _FuelGraph(QWidget):
    """Paints the original's "Fuel Usage vs. Warp Speed" chart.

    ``fuel-usage`` is an 11-element array (index = warp 0..10) of percentages
    (100 = standard cost). The Y axis is piecewise: 0..100% over the lower half
    (grid at 25/50/75/100) and 100..800% over the upper half (grid at
    200/400/600/800), matching the game. Warps 1..10 are plotted on X.
    """

    _LOW_GRID = [25, 50, 75, 100]
    _HIGH_GRID = [200, 400, 600, 800]
    _MAX = 800

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fuel: list[int] = []
        self._warp10_safe = True
        self.setMinimumSize(240, 150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_engine(self, fuel: list[int], warp10_safe: bool) -> None:
        self._fuel = list(fuel or [])
        self._warp10_safe = bool(warp10_safe)
        self.update()

    def _y_frac(self, value: float) -> float:
        """Map a fuel percentage to a 0..1 fraction up from the X axis."""
        v = max(0.0, min(float(value), self._MAX))
        if v <= 100.0:
            return (v / 100.0) * 0.5
        return 0.5 + ((v - 100.0) / (self._MAX - 100.0)) * 0.5

    def paintEvent(self, event):  # noqa: N802 (Qt override)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        left, right, top, bottom = 34, w - 8, 18, h - 18
        plot_w = max(1, right - left)
        plot_h = max(1, bottom - top)

        def px(warp: int) -> float:
            return left + (warp - 1) / 9.0 * plot_w

        def py(value: float) -> float:
            return bottom - self._y_frac(value) * plot_h

        # Background.
        p.fillRect(0, 0, w, h, QColor("#f4f4e8"))

        # Unsafe-warp band: warp 10 when the engine cannot safely travel it
        # (per message 223, "engines over-reacted trying to achieve Warp 10").
        # The original's exact band is approximate here; refine via oracle.
        if not self._warp10_safe:
            x0 = px(10) - (plot_w / 9.0) * 0.5
            p.fillRect(int(x0), top, int(right - x0), plot_h, QColor(240, 224, 80, 110))

        grid_pen = QPen(QColor("#b8b8a8"))
        grid_pen.setWidth(1)
        p.setPen(grid_pen)
        font = QFont()
        font.setPointSize(7)
        p.setFont(font)
        for val in self._LOW_GRID + self._HIGH_GRID:
            y = py(val)
            p.drawLine(left, int(y), right, int(y))
            p.drawText(2, int(y) + 3, f"{val}%")
        # X axis ticks.
        axis_pen = QPen(QColor("#888878"))
        p.setPen(axis_pen)
        p.drawLine(left, bottom, right, bottom)
        for warp in range(1, 11):
            x = px(warp)
            p.drawLine(int(x), bottom, int(x), bottom + 3)
            p.drawText(int(x) - 3, bottom + 14, str(warp))

        # Fuel curve (warps 1..10).
        if len(self._fuel) >= 11:
            poly = QPolygonF()
            for warp in range(1, 11):
                poly.append(QPointF(px(warp), py(self._fuel[warp])))
            curve_pen = QPen(QColor("#303060"))
            curve_pen.setWidth(2)
            p.setPen(curve_pen)
            p.drawPolyline(poly)

        p.end()


# ── Dialog ───────────────────────────────────────────────────────────────────


class TechnologyBrowser(QDialog):
    """Browse the component technology catalog from the engine."""

    def __init__(self, player, engine_url=None, show_only_available=False, parent=None):
        super().__init__(parent)
        self._player = player
        self._engine_url = engine_url.rstrip("/") if engine_url else None
        self._race = getattr(player, "race", None) if player else None

        self.setWindowTitle("Technology Browser")
        self.resize(420, 460)

        # category slug -> list of tech-item dicts (catalog order preserved)
        self._by_category: dict[str, list[dict]] = {}
        self._categories: list[str] = []  # slugs present, in dropdown order
        self._cat_index = 0
        self._item_index = 0

        self._load_catalog()
        self._build_ui(show_only_available)
        if self._categories:
            self._select_category(0)

    # ── data ────────────────────────────────────────────────────────────────

    def _load_catalog(self) -> None:
        if not self._engine_url:
            log.info("Technology Browser: no engine URL; catalog unavailable.")
            return
        try:
            resp = requests.get(f"{self._engine_url}/model/technologies", timeout=15)
            resp.raise_for_status()
            items = resp.json().get("technologies", [])
        except (requests.exceptions.RequestException, ValueError) as exc:
            log.warning("Could not load /model/technologies: %s", exc)
            return

        self._by_category, self._categories = group_by_category(items)

    # ── ui construction ───────────────────────────────────────────────────────

    def _build_ui(self, show_only_available: bool) -> None:
        root = QVBoxLayout(self)

        if not self._categories:
            msg = QLabel(
                "The technology catalog is unavailable.\n\n"
                "Start the game against a running engine to browse components."
            )
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("color: #888; font-style: italic;")
            root.addWidget(msg, 1)
            close = QPushButton("Close")
            close.clicked.connect(self.accept)
            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(close)
            root.addLayout(row)
            return

        # Header: Prev | category combo | Next
        header = QHBoxLayout()
        self._prev_btn = QPushButton("← Prev")
        self._prev_btn.clicked.connect(self._prev_item)
        self._cat_combo = QComboBox()
        for slug in self._categories:
            self._cat_combo.addItem(CATEGORY_LABELS.get(slug, slug.title()), slug)
        self._cat_combo.currentIndexChanged.connect(self._select_category)
        self._next_btn = QPushButton("Next →")
        self._next_btn.clicked.connect(self._next_item)
        header.addWidget(self._prev_btn)
        header.addWidget(self._cat_combo, 1)
        header.addWidget(self._next_btn)
        root.addLayout(header)

        # Name.
        self._name_label = QLabel("")
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(11)
        self._name_label.setFont(name_font)
        root.addWidget(self._name_label)

        # Icon + costs row.
        info = QHBoxLayout()
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(64, 64)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.addWidget(self._icon_label)

        cost_host = QWidget()
        self._cost_grid = QGridLayout(cost_host)
        self._cost_grid.setContentsMargins(8, 0, 0, 0)
        self._cost_grid.setHorizontalSpacing(10)
        self._cost_grid.setVerticalSpacing(1)
        info.addWidget(cost_host, 1)
        root.addLayout(info)

        # Tech requirement / availability line.
        self._techreq_label = QLabel("")
        self._techreq_label.setStyleSheet("color: #666;")
        root.addWidget(self._techreq_label)

        # Detail area (fuel graph for engines, generic grid otherwise).
        self._detail_host = QFrame()
        self._detail_host.setFrameShape(QFrame.Shape.StyledPanel)
        self._detail_layout = QVBoxLayout(self._detail_host)
        self._detail_layout.setContentsMargins(6, 6, 6, 6)
        self._fuel_graph = _FuelGraph()
        root.addWidget(self._detail_host, 1)

        # Restriction / description line.
        self._restriction_label = QLabel("")
        self._restriction_label.setWordWrap(True)
        self._restriction_label.setStyleSheet("color: #a05000; font-style: italic;")
        root.addWidget(self._restriction_label)

        # Footer: filter checkbox + Close.
        footer = QHBoxLayout()
        self._avail_check = QCheckBox("Show Only Available Technology")
        self._avail_check.setChecked(bool(show_only_available))
        self._avail_check.stateChanged.connect(self._on_filter_changed)
        footer.addWidget(self._avail_check)
        footer.addStretch(1)
        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        footer.addWidget(close)
        root.addLayout(footer)

    # ── navigation ────────────────────────────────────────────────────────────

    def _current_items(self) -> list[dict]:
        """Items in the selected category, honoring the availability filter."""
        if not self._categories:
            return []
        slug = self._categories[self._cat_index]
        items = self._by_category.get(slug, [])
        if self._avail_check.isChecked():
            items = [it for it in items if self._is_available(it)]
        return items

    def _select_category(self, index: int) -> None:
        if index < 0 or index >= len(self._categories):
            return
        self._cat_index = index
        if self._cat_combo.currentIndex() != index:
            self._cat_combo.setCurrentIndex(index)
        self._item_index = 0
        self._render_current()

    def _next_item(self) -> None:
        items = self._current_items()
        if not items:
            return
        self._item_index = (self._item_index + 1) % len(items)
        self._render_current()

    def _prev_item(self) -> None:
        items = self._current_items()
        if not items:
            return
        self._item_index = (self._item_index - 1) % len(items)
        self._render_current()

    def _on_filter_changed(self, _state) -> None:
        self._item_index = 0
        self._render_current()

    # ── availability ──────────────────────────────────────────────────────────

    def _is_available(self, item: dict) -> bool:
        """Whether the player's race can build this item (see ``component_available``)."""
        return component_available(
            item,
            getattr(self._race, "prt", ""),
            getattr(self._race, "lrts", []),
        )

    # ── rendering ─────────────────────────────────────────────────────────────

    def _render_current(self) -> None:
        items = self._current_items()
        has = bool(items)
        self._prev_btn.setEnabled(len(items) > 1)
        self._next_btn.setEnabled(len(items) > 1)
        if not has:
            self._name_label.setText("(no available technology)")
            self._icon_label.clear()
            self._clear_grid(self._cost_grid)
            self._techreq_label.setText("")
            self._restriction_label.setText("")
            self._clear_detail()
            return
        self._item_index %= len(items)
        self._render_item(items[self._item_index])

    def _render_item(self, item: dict) -> None:
        category = item.get("category", "")
        name = item.get("name", "")
        self._name_label.setText(name)

        # Icon.
        pix = component_icon(category, item.get("slug", ""))
        self._icon_label.setPixmap(
            pix.scaled(
                64,
                64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        # Costs.
        self._clear_grid(self._cost_grid)
        cost = item.get("cost", {}) or {}
        rows = [
            ("Ironium", f"{cost.get('ironium', 0)}kT", _IRONIUM_COLOR),
            ("Boranium", f"{cost.get('boranium', 0)}kT", _BORANIUM_COLOR),
            ("Germanium", f"{cost.get('germanium', 0)}kT", _GERMANIUM_COLOR),
            ("Resources", f"{cost.get('resources', 0)}", _RESOURCE_COLOR),
        ]
        for r, (label, value, color) in enumerate(rows):
            lab = QLabel(label)
            lab.setStyleSheet(f"color: {color};")
            val = QLabel(value)
            val.setStyleSheet(f"color: {color};")
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            self._cost_grid.addWidget(lab, r, 0)
            self._cost_grid.addWidget(val, r, 1)
        mass = item.get("mass")
        if mass is not None:
            mass_lab = QLabel(f"Mass: {mass}kT")
            self._cost_grid.addWidget(mass_lab, 0, 2)

        # Tech requirement + availability.
        reqs = item.get("tech-requirements", {}) or {}
        parts = [f"{short} {reqs[field]}" for field, short in _TECH_FIELDS if reqs.get(field)]
        techreq = ", ".join(parts) if parts else "None"
        avail = "Avail" if self._is_available(item) else "UnAvail"
        self._techreq_label.setText(f"Tech Req: {techreq}   —   {avail}")

        # Restriction line.
        self._restriction_label.setText(self._restriction_text(item))

        # Detail area.
        self._clear_detail()
        if category == "engines":
            props = item.get("properties", {}) or {}
            self._fuel_graph.set_engine(
                props.get("fuel-usage", []), props.get("warp10-travel", False)
            )
            title = QLabel("Fuel Usage vs. Warp Speed")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("color: #303060;")
            self._detail_layout.addWidget(title)
            self._detail_layout.addWidget(self._fuel_graph, 1)
        else:
            self._detail_layout.addWidget(self._build_stats_panel(item))

    def _restriction_text(self, item: dict) -> str:
        bits = []
        req = item.get("requirement")
        if req:
            if req.get("mystery-trader"):
                bits.append("Available only through the Mystery Trader.")
            prt_list = req.get("prt")
            if prt_list:
                names = ", ".join(_PRT_NAMES.get(p.upper(), p) for p in prt_list)
                bits.append(f"Requires the {names} primary racial trait.")
            lrt_list = req.get("lrt")
            if lrt_list:
                bits.append("Requires the Lesser Racial Trait(s): " + ", ".join(lrt_list) + ".")
        desc = item.get("description")
        if desc:
            bits.append(desc)
        return " ".join(bits)

    def _build_stats_panel(self, item: dict) -> QWidget:
        """Generic two-column stats table from the item's ``properties``."""
        host = QWidget()
        grid = QGridLayout(host)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(2)
        props = item.get("properties", {}) or {}
        row = 0
        for key, value in props.items():
            if value is None:
                continue
            label = QLabel(key.replace("-", " ").title())
            grid.addWidget(label, row, 0)
            grid.addWidget(QLabel(self._format_value(value)), row, 1)
            row += 1
        if row == 0:
            note = QLabel("No additional statistics.")
            note.setStyleSheet("color: #888; font-style: italic;")
            grid.addWidget(note, 0, 0)
        grid.setRowStretch(row, 1)
        return host

    @staticmethod
    def _format_value(value) -> str:
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return str(value)

    # ── small helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _clear_grid(grid: QGridLayout) -> None:
        while grid.count():
            child = grid.takeAt(0)
            w = child.widget()
            if w is not None:
                w.setParent(None)

    def _clear_detail(self) -> None:
        while self._detail_layout.count():
            child = self._detail_layout.takeAt(0)
            w = child.widget()
            if w is not None:
                # Keep the reusable fuel graph alive; just detach it.
                if w is self._fuel_graph:
                    w.setParent(None)
                else:
                    w.deleteLater()
