"""
ui/main_window.py

QMainWindow for the main game screen.

Layout
------
  [Menu bar]
  [Toolbar]
  ┌────────────────────────────────────────────────────┐
  │  LeftPanel (~400 px)  │  SpaceMap                  │
  │  col1  │  col2        │                            │
  │  ────── ──────        ├────────────────────────────┤
  │  Messages pane        │  PlanetSummaryWidget        │
  └────────────────────────────────────────────────────┘
  [Status bar]
"""

from __future__ import annotations

import logging

import requests
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QActionGroup, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QToolBar,
    QToolButton,
    QWidget,
)

from ..rendering.enumerations import NeverSeenPlanet, PlanetView, ResourcePaths, ZoomLevel
from .info_panel import LeftPanel, build_buildables_map
from .planet_summary import PlanetSummaryWidget
from .space_map import SpaceMap

log = logging.getLogger(__name__)

_TOOLBAR_ICON_SIZE = QSize(24, 24)


# ── view-options container ──────────────────────────────────────────────────


class _ViewOptions:
    def __init__(self):
        self.zoom_level: int = ZoomLevel.Default
        self.planet_view: int = PlanetView.Default
        self.planet_names_overlay: bool = True

    def zoom_multiplier(self) -> float:
        return ZoomLevel.multipliers()[self.zoom_level]


# ── main window ─────────────────────────────────────────────────────────────


class MainWindow(QMainWindow):
    """
    Primary game window.

    Parameters
    ----------
    planets:
        Iterable of planet objects (duck-typed; populated from engine HTTP API response).
    universe_w, universe_h:
        Universe dimensions in light-years.
    player_id:
        Active player's id, used to color own planets green.
    game_year:
        Starting year shown in the status bar.
    game_name:
        Title bar suffix.
    player:
        Full player object (optional, passed to panels for race-aware display).
    messages:
        This turn's messages (``MessageData``), shown in the Messages pane.
        Per-turn — replaced each year and cleared when a new turn is generated.
    score:
        The viewing player's F10 score breakdown (``ScoreData``) for this turn,
        shown by the F10 Score dialog; ``None`` when the turn file has no score.
    race:
        The viewing player's race (raw turn-file ``race`` dict), shown by the F8
        Race view; ``None`` when the turn file carries no race.
    """

    def __init__(
        self,
        planets=(),
        universe_w: float = 400.0,
        universe_h: float = 400.0,
        player_id: int | None = None,
        game_year: int = 2400,
        game_name: str = "New Game",
        player=None,
        engine_url: str | None = None,
        game_id: str | None = None,
        messages=(),
        score=None,
        race=None,
    ):
        super().__init__()
        self._planets = list(planets)
        # The viewing player's race (raw turn-file dict), shown by the F8 Race
        # view, or None when the turn file carries no race.
        self._race = race
        # This turn's messages (MessageData); per-turn, cleared on generate.
        self._messages_data = list(messages)
        # The viewing player's F10 score breakdown (ScoreData) for this turn,
        # or None when the turn file carries no score. Shown by the F10 dialog.
        self._score = score
        self._universe_w = universe_w
        self._universe_h = universe_h
        self._player_id = player_id
        self._game_year = game_year
        self._game_name = game_name
        self._player = player
        # Engine connection for order submission; None when a turn file was
        # loaded locally (offline) — production editing stays read-only then.
        self._engine_url = engine_url.rstrip("/") if engine_url else None
        self._game_id = game_id
        self._view_opts = _ViewOptions()
        # Two-slot target model — see SpaceMap docstring.
        # _selected_planet always tracks the primary target (used by the
        # zoom handler to keep that planet centred when the user changes
        # zoom levels).
        self._primary_id: int | None = None
        self._secondary_id: int | None = None
        self._selected_planet = None
        # When set, the next map click picks the route target for this planet id
        # (snapped to the nearest planet) instead of selecting a planet.
        self._awaiting_route_target: int | None = None
        # Same, for a starbase mass-driver packet destination.
        self._awaiting_packet_target: int | None = None

        self._init_ui()
        self._init_menu()
        self._init_toolbar()
        self._init_status_bar()
        self._load_universe()
        self._init_orders()

    # ── setup ───────────────────────────────────────────────────────────────

    def _init_ui(self):
        self.setWindowTitle(f"Stars Reborn — {self._game_name}")
        self.setGeometry(100, 100, 1280, 800)

        # Left command panel
        self._left_panel = LeftPanel()
        self._left_panel.set_year(self._game_year)
        self._left_panel.set_universe(self._planets, self._player_id)
        self._left_panel.set_messages(self._messages_data)
        self._left_panel.planet_nav_requested.connect(self._on_planet_nav)
        self._left_panel.message_goto_requested.connect(self._on_message_goto)
        self._left_panel.queue_changed.connect(self._on_production_queue_changed)
        self._left_panel.add_item_requested.connect(self._on_add_production_item)
        self._left_panel.route_change_requested.connect(self._on_route_change)
        self._left_panel.route_clear_requested.connect(self._on_route_clear)
        self._left_panel.route_fleet_requested.connect(self._on_route_fleet)
        self._left_panel.packet_dest_requested.connect(self._on_set_packet_dest)

        # Space map (absolute pixel-per-ly scale; scroll area provides panning).
        self._space_map = SpaceMap()
        self._space_map.planet_selected.connect(self._on_planet_selected)
        self._space_map.map_clicked.connect(self._on_map_clicked)
        self._space_map.hover_world.connect(self._on_hover_world)
        self._space_map.zoom_step.connect(self._on_wheel_zoom)

        self._space_scroll = QScrollArea()
        self._space_scroll.setWidget(self._space_map)
        self._space_scroll.setWidgetResizable(False)
        self._space_scroll.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._space_scroll.setFrameShape(QScrollArea.NoFrame)
        self._space_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._space_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._space_scroll.viewport().setStyleSheet("background-color: black;")

        # Planet summary (below space map)
        self._planet_summary = PlanetSummaryWidget()

        # Right pane: space map (top) + summary (bottom).  Original game
        # anchors the planet summary to the bottom at a fixed height; the
        # space map absorbs all vertical resize.
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self._space_scroll)
        right_splitter.addWidget(self._planet_summary)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 0)
        right_splitter.setSizes([560, 200])

        # Main horizontal split: left panel | space map + summary
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self._left_panel)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([420, 860])

        self.setCentralWidget(main_splitter)

    def _load_universe(self):
        self._space_map.set_universe(
            self._planets,
            self._universe_w,
            self._universe_h,
            self._player_id,
        )
        self._space_map.set_show_names(self._view_opts.planet_names_overlay)
        self._space_map.set_zoom(ZoomLevel.multipliers()[self._view_opts.zoom_level])
        self._select_initial_target()

    def _select_initial_target(self):
        """Default target on load: the active player's homeworld (both slots)."""
        home = next(
            (
                p
                for p in self._planets
                if getattr(p, "homeworld", False) and p.owner == self._player_id
            ),
            None,
        )
        if home is None:
            return
        self._primary_id = home.id
        self._secondary_id = home.id
        self._selected_planet = home
        self._space_map.set_primary_target(home.id)
        self._space_map.set_secondary_target(home.id)
        self._left_panel.update_planet(home, self._player)
        self._planet_summary.set_primary_target(home)
        self._planet_summary.update_planet(home, self._player)
        self._center_scroll_on_planet(home.id)

    def _center_scroll_on_planet(self, pid: int):
        """Scroll the space view so the given planet sits in the viewport center."""
        pos = self._space_map.planet_screen_pos(pid)
        if pos is None:
            return
        sx, sy = pos
        vp = self._space_scroll.viewport()
        # ensureVisible(x, y, xmargin, ymargin) — picking margins of half the
        # viewport effectively centers (x, y) when the content is large enough.
        self._space_scroll.ensureVisible(int(sx), int(sy), vp.width() // 2, vp.height() // 2)

    # ── menu bar ────────────────────────────────────────────────────────────

    def _init_menu(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("&File")
        file_menu.addAction(self._action("&New...", "Ctrl+N", self._handle_new))
        file_menu.addAction(
            self._action("&Custom Race Wizard...", None, self._handle_custom_race_wizard)
        )
        file_menu.addAction(self._action("&Open...", "Ctrl+O", self._handle_open))
        file_menu.addAction(self._action("&Close", None, self._handle_close))
        file_menu.addAction(self._action("&Save", "Ctrl+S", self._handle_save))
        file_menu.addAction(
            self._action("Save &And Submit", "Ctrl+A", self._handle_save_and_submit, enabled=False)
        )
        file_menu.addSeparator()
        file_menu.addAction(self._action("&Print Map", None, self._handle_print_map))
        file_menu.addSeparator()
        file_menu.addAction(self._action("E&xit", None, self.close))

        # View
        view_menu = mb.addMenu("&View")
        self._toolbar_action = self._action(
            "&Toolbar", None, self._handle_toggle_toolbar, checkable=True
        )
        self._toolbar_action.setChecked(True)
        view_menu.addAction(self._toolbar_action)
        view_menu.addSeparator()
        view_menu.addAction(self._action("&Find...", "Ctrl+F", self._handle_find))

        zoom_menu = view_menu.addMenu("&Zoom")
        zoom_group = QActionGroup(self)
        self._zoom_actions = []
        for i, name in enumerate(ZoomLevel.names()):
            a = self._action(
                name, None, lambda checked, idx=i: self._handle_zoom(idx), checkable=True
            )
            zoom_group.addAction(a)
            zoom_menu.addAction(a)
            self._zoom_actions.append(a)
        self._zoom_actions[self._view_opts.zoom_level].setChecked(True)

        layout_menu = view_menu.addMenu("&Window Layout")
        layout_menu.addAction(self._action("&Default", None, self._handle_window_layout_default))
        layout_menu.addAction(self._action("&Save Layout", None, self._handle_window_layout_save))
        layout_menu.addAction(
            self._action("&Restore Layout", None, self._handle_window_layout_restore)
        )

        view_menu.addAction(self._action("Player &Colors...", None, self._handle_player_colors))
        view_menu.addSeparator()
        view_menu.addAction(self._action("&Race...", "F8", self._handle_race))
        view_menu.addAction(self._action("&Game Parameters...", None, self._handle_game_params))

        # Turn
        turn_menu = mb.addMenu("&Turn")
        turn_menu.addAction(
            self._action("&Wait for New", None, self._handle_wait_for_new, enabled=False)
        )
        turn_menu.addAction(self._action("&Generate", "F9", self._handle_generate))

        # Commands
        cmd_menu = mb.addMenu("&Commands")
        cmd_menu.addAction(self._action("&Ship Design...", "F4", self._handle_ship_design))
        cmd_menu.addAction(self._action("&Research...", "F5", self._handle_research))
        cmd_menu.addAction(self._action("&Battle Plans...", "F6", self._handle_battle_plans))
        cmd_menu.addAction(
            self._action("&Player Relations...", "F7", self._handle_player_relations, enabled=False)
        )
        cmd_menu.addSeparator()
        cmd_menu.addAction(
            self._action("Change Pass&word...", None, self._handle_change_password, enabled=False)
        )

        # Report
        rep_menu = mb.addMenu("&Report")
        rep_menu.addAction(self._action("&Planets...", "F3", self._handle_planets_report))
        rep_menu.addAction(self._action("&Fleets...", "F3", self._handle_fleets_report))
        rep_menu.addAction(
            self._action("&Others' Fleets...", "F3", self._handle_others_fleets_report)
        )
        rep_menu.addSeparator()
        rep_menu.addAction(self._action("&Battles...", None, self._handle_battles_report))
        rep_menu.addSeparator()
        rep_menu.addAction(self._action("&Score...", "F10", self._handle_score))
        rep_menu.addSeparator()
        dump_menu = rep_menu.addMenu("&Dump to Text File")
        dump_menu.addAction(self._action("&Universe Definition", None, self._handle_dump_universe))
        dump_menu.addAction(self._action("&Planet Information", None, self._handle_dump_planets))
        dump_menu.addAction(self._action("&Fleet Information", None, self._handle_dump_fleets))

        # Help
        help_menu = mb.addMenu("&Help")
        help_menu.addAction(self._action("&Introduction", None, self._handle_intro))
        help_menu.addAction(self._action("&Player's Guide", "F1", self._handle_players_guide))
        help_menu.addSeparator()
        help_menu.addAction(self._action("Technology &Browser", "F2", self._handle_tech_browser))
        help_menu.addAction(self._action("&Tutorial", None, self._handle_tutorial))
        help_menu.addSeparator()
        help_menu.addAction(self._action("&About Stars Reborn...", None, self._handle_about))

    def _action(self, text, shortcut, slot, checkable=False, enabled=True) -> QAction:
        a = QAction(text, self)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        a.triggered.connect(slot)
        if checkable:
            a.setCheckable(True)
        if not enabled:
            a.setEnabled(False)
        return a

    # ── toolbar ─────────────────────────────────────────────────────────────

    def _init_toolbar(self):
        tb = QToolBar("Main Toolbar", self)
        tb.setIconSize(_TOOLBAR_ICON_SIZE)
        tb.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, tb)
        self._main_toolbar = tb

        view_buttons = []
        view_group = QButtonGroup(self)
        view_specs = [
            (
                "normal_view",
                ResourcePaths.NormalViewIcon,
                "Normal View",
                lambda: self._handle_view_mode(PlanetView.Normal),
            ),
            (
                "surface_minerals",
                ResourcePaths.SurfaceMineralsIcon,
                "Surface Mineral View",
                lambda: self._handle_view_mode(PlanetView.SurfaceMinerals),
            ),
            (
                "mineral_conc",
                ResourcePaths.MineralConcentrationsIcon,
                "Mineral Concentration View",
                lambda: self._handle_view_mode(PlanetView.MineralConcentration),
            ),
            (
                "value_view",
                ResourcePaths.PercentIcon,
                "Planet Value View",
                lambda: self._handle_view_mode(PlanetView.PercentPopulation),
            ),
            (
                "pop_view",
                ResourcePaths.PopulationIcon,
                "Population View",
                lambda: self._handle_view_mode(PlanetView.PopulationView),
            ),
            (
                "no_info",
                ResourcePaths.NoPlayerInfoIcon,
                "No Player Info View",
                lambda: self._handle_view_mode(PlanetView.NoInfo),
            ),
        ]
        for _name, icon_path, tip, handler in view_specs:
            btn = self._toolbar_btn(icon_path, tip, checkable=True)
            btn.clicked.connect(handler)
            tb.addWidget(btn)
            view_group.addButton(btn)
            view_buttons.append(btn)
        view_buttons[self._view_opts.planet_view].setChecked(True)
        self._view_buttons = view_buttons

        tb.addSeparator()

        self._waypoints_btn = self._toolbar_btn(ResourcePaths.AddWaypointIcon, "Add Waypoints Mode")
        self._waypoints_btn.clicked.connect(self._handle_add_waypoints)
        tb.addWidget(self._waypoints_btn)
        tb.addSeparator()

        self._routes_btn = self._toolbar_btn(
            ResourcePaths.ShowRoutesIcon, "Fleet Paths Overlay", checkable=True
        )
        self._routes_btn.clicked.connect(self._handle_fleet_paths)
        tb.addWidget(self._routes_btn)
        tb.addSeparator()

        self._names_btn = self._toolbar_btn(
            ResourcePaths.PlanetNamesIcon, "Toggle Planet Names", checkable=True
        )
        self._names_btn.setChecked(self._view_opts.planet_names_overlay)
        self._names_btn.clicked.connect(self._handle_names_toggle)
        tb.addWidget(self._names_btn)

        self._idle_fleets_btn = self._toolbar_btn(
            ResourcePaths.IdleFleetsIcon, "Idle Fleets Filter"
        )
        self._idle_fleets_btn.clicked.connect(self._handle_idle_fleets)
        tb.addWidget(self._idle_fleets_btn)

        self._enemy_filter_btn = self._toolbar_btn(
            ResourcePaths.EnemyShipFilterIcon, "Enemy Ship Filter", checkable=True
        )
        self._enemy_filter_btn.clicked.connect(self._handle_enemy_ship_filter)
        tb.addWidget(self._enemy_filter_btn)

        self._design_filter_btn = self._toolbar_btn(
            ResourcePaths.ShipDesignFilterIcon, "Ship Design Filter", checkable=True
        )
        self._design_filter_btn.clicked.connect(self._handle_ship_design_filter)
        tb.addWidget(self._design_filter_btn)

        self._zoom_btn = QToolButton()
        zoom_icon = QIcon(ResourcePaths.MagnifyingGlassIcon)
        if not zoom_icon.isNull():
            self._zoom_btn.setIcon(zoom_icon)
            self._zoom_btn.setIconSize(_TOOLBAR_ICON_SIZE)
        else:
            self._zoom_btn.setText("Zoom")
        self._zoom_btn.setToolTip("Zoom Level")
        self._zoom_btn.setFixedSize(28, 28)
        self._zoom_btn.setAutoRaise(True)
        self._zoom_btn.setPopupMode(QToolButton.InstantPopup)

        zoom_menu = QMenu(self._zoom_btn)
        self._toolbar_zoom_actions = []
        tb_zoom_group = QActionGroup(self)
        for i, name in enumerate(ZoomLevel.names()):
            a = QAction(name, self)
            a.setCheckable(True)
            a.triggered.connect(lambda checked, idx=i: self._handle_zoom(idx))
            tb_zoom_group.addAction(a)
            zoom_menu.addAction(a)
            self._toolbar_zoom_actions.append(a)
        self._toolbar_zoom_actions[self._view_opts.zoom_level].setChecked(True)
        self._zoom_btn.setMenu(zoom_menu)
        tb.addWidget(self._zoom_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        self._year_label = QLabel(f"Year {self._game_year}")
        self._year_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._year_label.setStyleSheet("font-weight: bold; padding: 0 8px;")
        tb.addWidget(self._year_label)

        self._next_turn_btn = QPushButton("Next Turn")
        self._next_turn_btn.setShortcut(QKeySequence("Space"))
        self._next_turn_btn.setToolTip("Generate next turn (Space)")
        self._next_turn_btn.clicked.connect(self._handle_generate)
        tb.addWidget(self._next_turn_btn)

    def _toolbar_btn(self, icon_path: str, tooltip: str, checkable: bool = False) -> QPushButton:
        btn = QPushButton()
        icon = QIcon(icon_path)
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(_TOOLBAR_ICON_SIZE)
        else:
            btn.setText(tooltip[:3])
        btn.setToolTip(tooltip)
        btn.setFixedSize(28, 28)
        btn.setFlat(True)
        if checkable:
            btn.setCheckable(True)
        return btn

    # ── status bar ───────────────────────────────────────────────────────────

    def _init_status_bar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._year_status_label = QLabel(f"Year {self._game_year}")
        self._year_status_label.setFrameStyle(1)
        sb.addPermanentWidget(self._year_status_label)

    # ── slots ───────────────────────────────────────────────────────────────

    @staticmethod
    def _is_promotable(target) -> bool:
        """Can this map object become the primary target?

        Surveyed planets (any ownership) and own fleets are promotable.
        Never-seen planets, enemy fleets, wormholes, mineral packets, space
        debris, and the mystery trader are secondary-only and never enter
        the left pane. Currently the space map only renders planets, so the
        only branch exercised is the never-seen check; the helper is kept
        so fleet support drops in cleanly.
        """
        if getattr(target, "years_since", 0) == NeverSeenPlanet:
            return False
        return True

    def _on_planet_selected(self, pid: int):
        """Single-click on a planet.

        Always sets the secondary target (drives the bottom-right pane and
        the small arrow). Promotes to primary when this planet was already
        the secondary target — i.e. the user has clicked it a second time.
        """
        # While picking a route or packet target, the click is consumed by
        # _on_map_clicked.
        if self._awaiting_route_target is not None or self._awaiting_packet_target is not None:
            return

        planet = next((p for p in self._planets if p.id == pid), None)
        if planet is None:
            return

        prior_secondary = self._secondary_id

        self._secondary_id = pid
        self._space_map.set_secondary_target(pid)
        self._planet_summary.update_planet(planet, self._player)

        if self._is_promotable(planet) and prior_secondary == pid and self._primary_id != pid:
            self._primary_id = pid
            self._space_map.set_primary_target(pid)
            self._left_panel.update_planet(planet, self._player)
            self._planet_summary.set_primary_target(planet)
            self._selected_planet = planet

    def _on_planet_nav(self, pid: int):
        """Prev/Next in the planet header: fully select the chosen owned world —
        both target slots, both panes, and recentre the map on it."""
        planet = next((p for p in self._planets if p.id == pid), None)
        if planet is None:
            return
        self._primary_id = pid
        self._secondary_id = pid
        self._selected_planet = planet
        self._space_map.set_primary_target(pid)
        self._space_map.set_secondary_target(pid)
        self._left_panel.update_planet(planet, self._player)
        self._planet_summary.set_primary_target(planet)
        self._planet_summary.update_planet(planet, self._player)
        self._center_scroll_on_planet(pid)

    def _on_message_goto(self, obj_id: int):
        """Goto in the Messages pane: navigate the map to the message's subject.

        The subject is a universe-wide space-object id. Today only planets are
        modeled and rendered, so a planet subject gets a full select + recentre
        (exactly as Prev/Next does via ``_on_planet_nav``); any other subject
        (e.g. a fleet) is a no-op with a hint until fleets are rendered."""
        if any(p.id == obj_id for p in self._planets):
            self._on_planet_nav(obj_id)
        else:
            self.statusBar().showMessage(
                "Message subject is not a planet — fleet/location navigation not yet implemented.",
                4000,
            )

    def _on_hover_world(self, wx: int, wy: int):
        self._planet_summary.update_hover_coords(wx, wy)

    # ── order submission (production + route) ────────────────────────────────
    def _init_orders(self):
        """Enable the order-editing sections and fetch any registries they need.

        Route editing only needs an engine to submit to; production editing also
        needs the buildable registry. Offline (a locally loaded turn file, no
        engine URL) both stay read-only, since there is nowhere to submit orders.
        """
        orders_ok = bool(self._engine_url and self._game_id)
        self._left_panel.set_route_editable(orders_ok)
        self._left_panel.set_starbase_editable(orders_ok)

        buildables_ok = False
        if self._engine_url:
            try:
                resp = requests.get(f"{self._engine_url}/model/buildables", timeout=15)
                resp.raise_for_status()
                self._left_panel.set_buildables(build_buildables_map(resp.json()))
                buildables_ok = True
            except requests.exceptions.RequestException as exc:
                log.warning("Could not load /model/buildables: %s", exc)
        self._left_panel.set_production_editable(orders_ok and buildables_ok)

    def _submit_orders(self, orders: list) -> bool:
        """PUT a list of orders to the engine's orders choke point. Returns True
        on success; logs and shows a status message on failure."""
        if not self._engine_url or self._game_id is None:
            return False
        body = {
            "player_id": self._player_id,
            "turn_year": self._game_year,
            "orders": orders,
        }
        url = (
            f"{self._engine_url}/games/{self._game_id}"
            f"/turns/{self._game_year}/orders/{self._player_id}"
        )
        try:
            resp = requests.put(url, json=body, timeout=15)
            resp.raise_for_status()
            return True
        except requests.exceptions.RequestException as exc:
            log.error("Order submission failed: %s", exc)
            self.statusBar().showMessage(f"Order submission failed: {exc}", 5000)
            return False

    def _on_production_queue_changed(self, planet_id: int, items: list):
        """A queue edit: submit the planet's whole new queue to the engine."""
        order = {"kind": "planet.set_production_queue", "planet_id": planet_id, "items": items}
        if self._submit_orders([order]):
            self.statusBar().showMessage("Production order submitted.", 3000)

    def _on_add_production_item(self, planet_id: int):
        """Add button — the buildable picker dialog is a separate task (#140)."""
        self.statusBar().showMessage(
            "Add to production — item picker dialog not yet implemented.", 4000
        )

    # ── route to ─────────────────────────────────────────────────────────────
    def _on_route_change(self, planet_id: int):
        """Change clicked: enter route-target mode. The next map click picks the
        destination, snapped to the nearest planet."""
        if not self._engine_url or self._game_id is None:
            return
        self._awaiting_route_target = planet_id
        self.setCursor(Qt.CrossCursor)
        self.statusBar().showMessage(
            "Click a destination on the map — the route snaps to the nearest planet."
        )

    def _on_route_clear(self, planet_id: int):
        self._submit_route_target(planet_id, None)

    def _on_route_fleet(self, planet_id: int):
        """Route button — routes the selected fleet; a fleet order deferred (#141)."""
        self.statusBar().showMessage("Route fleet — fleet routing not yet implemented.", 4000)

    # ── starbase: mass-driver packet destination ────────────────────────────
    def _on_set_packet_dest(self, planet_id: int):
        """Set Dest clicked: enter packet-target mode. The next map click picks
        the mass-driver destination, snapped to the nearest planet."""
        if not self._engine_url or self._game_id is None:
            return
        self._awaiting_packet_target = planet_id
        self.setCursor(Qt.CrossCursor)
        self.statusBar().showMessage(
            "Click a destination on the map — the packet target snaps to the nearest planet."
        )

    def _submit_packet_target(self, planet_id: int, target: int):
        """Submit a planet.set_packet_target order and refresh the Starbase
        display on success."""
        order = {
            "kind": "planet.set_packet_target",
            "planet_id": planet_id,
            "target_planet_id": target,
        }
        if not self._submit_orders([order]):
            return
        planet = next((p for p in self._planets if p.id == planet_id), None)
        if planet is not None and getattr(planet, "starbase", None) is not None:
            planet.starbase["packet_target"] = target
            if self._primary_id == planet_id:
                self._left_panel.update_planet(planet, self._player)
        name = next((p.name for p in self._planets if p.id == target), str(target))
        self.statusBar().showMessage(f"Packet destination set to {name}.", 3000)

    def _on_map_clicked(self, wx: float, wy: float):
        """Handle a raw map click while picking a route or packet target."""
        if self._awaiting_route_target is not None:
            planet_id = self._awaiting_route_target
            self._awaiting_route_target = None
            self.unsetCursor()
            nearest = self._nearest_planet(wx, wy)
            if nearest is not None:
                self._submit_route_target(planet_id, nearest.id)
            return
        if self._awaiting_packet_target is not None:
            planet_id = self._awaiting_packet_target
            self._awaiting_packet_target = None
            self.unsetCursor()
            nearest = self._nearest_planet(wx, wy)
            if nearest is not None:
                self._submit_packet_target(planet_id, nearest.id)
            return

    def _nearest_planet(self, wx: float, wy: float):
        """The planet nearest (Euclidean) to a world-space point, or None."""
        return min(
            self._planets,
            key=lambda p: (p.x - wx) ** 2 + (p.y - wy) ** 2,
            default=None,
        )

    def _submit_route_target(self, planet_id: int, target: int | None):
        """Submit a planet.set_route_target order (target None clears the route)
        and refresh the Route display on success."""
        order = {"kind": "planet.set_route_target", "planet_id": planet_id}
        if target is not None:
            order["target_planet_id"] = target
        if not self._submit_orders([order]):
            return
        planet = next((p for p in self._planets if p.id == planet_id), None)
        if planet is not None:
            planet.route_target = target
            # Refresh the panel if this planet is the one on display.
            if self._primary_id == planet_id:
                self._left_panel.update_planet(planet, self._player)
        if target is None:
            self.statusBar().showMessage("Route cleared.", 3000)
        else:
            name = next((p.name for p in self._planets if p.id == target), str(target))
            self.statusBar().showMessage(f"Route set to {name}.", 3000)

    # ── toolbar / menu handlers ─────────────────────────────────────────────

    def _handle_view_mode(self, mode: int):
        self._view_opts.planet_view = mode
        self._space_map.set_view_mode(mode)

    def _handle_names_toggle(self):
        enabled = self._names_btn.isChecked()
        self._view_opts.planet_names_overlay = enabled
        self._space_map.set_show_names(enabled)

    def _handle_zoom(self, level: int):
        self._view_opts.zoom_level = level
        self._space_map.set_zoom(ZoomLevel.multipliers()[level])
        self._zoom_actions[level].setChecked(True)
        self._toolbar_zoom_actions[level].setChecked(True)
        if self._selected_planet is not None:
            self._center_scroll_on_planet(self._selected_planet.id)

    def _on_wheel_zoom(self, direction: int):
        """Wheel-zoom: step one preset in the requested direction."""
        new_level = self._view_opts.zoom_level + direction
        new_level = max(ZoomLevel.Lowest, min(ZoomLevel.Highest, new_level))
        if new_level != self._view_opts.zoom_level:
            self._handle_zoom(new_level)

    def _handle_add_waypoints(self):
        self.statusBar().showMessage("Waypoint mode — not yet implemented.")

    def _handle_fleet_paths(self):
        self.statusBar().showMessage("Fleet paths overlay — not yet implemented.")

    def _handle_idle_fleets(self):
        self.statusBar().showMessage("Idle fleets filter — not yet implemented.")

    def _handle_enemy_ship_filter(self):
        self.statusBar().showMessage("Enemy ship filter — not yet implemented.")

    def _handle_ship_design_filter(self):
        self.statusBar().showMessage("Ship design filter — not yet implemented.")

    def _handle_toggle_toolbar(self):
        if self._main_toolbar.isVisible():
            self._main_toolbar.hide()
        else:
            self._main_toolbar.show()

    def _handle_new(self):
        self.statusBar().showMessage("New game — not yet implemented.")

    def _handle_custom_race_wizard(self):
        self.statusBar().showMessage("Custom Race Wizard — not yet implemented.")

    def _handle_open(self):
        self.statusBar().showMessage("Open game — not yet implemented.")

    def _handle_save(self):
        self.statusBar().showMessage("Save game — not yet implemented.")

    def _handle_save_and_submit(self):
        self.statusBar().showMessage("Save and Submit — not yet implemented.")

    def _handle_print_map(self):
        self.statusBar().showMessage("Print Map — not yet implemented.")

    def _handle_close(self):
        self.close()

    def _handle_find(self):
        from .dialogs.find import FindDialog

        dlg = FindDialog(self._planets, parent=self)
        dlg.planet_activated.connect(self._on_planet_nav)
        dlg.exec()

    def _handle_window_layout_default(self):
        self.statusBar().showMessage("Window Layout: Default — not yet implemented.")

    def _handle_window_layout_save(self):
        self.statusBar().showMessage("Window Layout: Save — not yet implemented.")

    def _handle_window_layout_restore(self):
        self.statusBar().showMessage("Window Layout: Restore — not yet implemented.")

    def _handle_player_colors(self):
        self.statusBar().showMessage("Player Colors — not yet implemented.")

    def _handle_race(self):
        from .dialogs.race_view import RaceViewDialog

        RaceViewDialog(self._race, parent=self).exec()

    def _handle_game_params(self):
        self.statusBar().showMessage("Game parameters — not yet implemented.")

    def _handle_wait_for_new(self):
        self.statusBar().showMessage("Wait for new turn — not yet implemented.")

    def _handle_player_relations(self):
        self.statusBar().showMessage("Player Relations — not yet implemented.")

    def _handle_change_password(self):
        self.statusBar().showMessage("Change Password — not yet implemented.")

    def _handle_generate(self):
        self._game_year += 1
        self._year_label.setText(f"Year {self._game_year}")
        self._year_status_label.setText(f"Year {self._game_year}")
        self._left_panel.set_year(self._game_year)
        # Messages are per-turn and cleared on next-turn. A real turn fetch will
        # replace them with the new year's messages; until the engine serializes
        # messages there are none to fetch, so clearing is the whole behavior.
        self._messages_data = []
        self._left_panel.set_messages(self._messages_data)
        self.statusBar().showMessage(f"Turn generated — Year {self._game_year}")

    def _handle_ship_design(self):
        try:
            from .dialogs.ship_designer import ShipDesignerDialog

            dlg = ShipDesignerDialog(self._player, self)
            dlg.exec()
            return
        except (ImportError, Exception):
            pass
        self.statusBar().showMessage("Ship design — not yet implemented.")

    def _handle_research(self):
        if self._player is not None:
            try:
                from .dialogs.research import ResearchDialog

                dlg = ResearchDialog(self._player, False)
                dlg.exec()
                return
            except (ImportError, Exception):
                pass
        self.statusBar().showMessage("Research — not yet implemented.")

    def _handle_battle_plans(self):
        self.statusBar().showMessage("Battle plans — not yet implemented.")

    def _handle_planets_report(self):
        from .dialogs.planet_report import PlanetReportDialog

        dlg = PlanetReportDialog(self._planets, self._player_id, parent=self)
        dlg.planet_activated.connect(self._on_planet_nav)
        dlg.exec()

    def _handle_fleets_report(self):
        self.statusBar().showMessage("Fleets report — not yet implemented.")

    def _handle_others_fleets_report(self):
        self.statusBar().showMessage("Others' Fleets report — not yet implemented.")

    def _handle_battles_report(self):
        self.statusBar().showMessage("Battles report — not yet implemented.")

    def _handle_score(self):
        from .dialogs.score import ScoreDialog

        ScoreDialog(self._score, year=self._game_year, parent=self).exec()

    def _handle_dump_universe(self):
        self.statusBar().showMessage("Dump universe — not yet implemented.")

    def _handle_dump_planets(self):
        self.statusBar().showMessage("Dump planets — not yet implemented.")

    def _handle_dump_fleets(self):
        self.statusBar().showMessage("Dump fleets — not yet implemented.")

    def _handle_intro(self):
        self.statusBar().showMessage("Introduction — not yet implemented.")

    def _handle_players_guide(self):
        self.statusBar().showMessage("Player's Guide — not yet implemented.")

    def _handle_tutorial(self):
        self.statusBar().showMessage("Tutorial — not yet implemented.")

    def _handle_tech_browser(self):
        if self._player is not None:
            try:
                from .dialogs.technology_browser import TechnologyBrowser

                dlg = TechnologyBrowser(self._player, False)
                dlg.exec()
                return
            except (ImportError, Exception):
                pass
        self.statusBar().showMessage("Technology browser — not yet implemented.")

    def _handle_about(self):
        try:
            from .dialogs import about

            dlg = about.AboutDialog()
            dlg.exec()
        except (ImportError, Exception):
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.about(
                self, "About Stars Reborn", "Stars Reborn — an open-source Stars! clone."
            )
