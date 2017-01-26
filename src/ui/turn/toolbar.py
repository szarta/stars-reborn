"""
    ui.turn.toolbar

    Defines helpers functions to build up the toolbar.

    :copyright: (c) 2015 by Brandon Arrendondo.
    :license: MIT, see LICENSE.txt for more details.
"""
from PySide.QtGui import QPushButton
from PySide.QtGui import QButtonGroup
from PySide.QtGui import QIcon
from PySide.QtCore import QSize

NORMAL_VIEW_ICON = "resources/toolbar/normal_view.png"
SURFACE_MINERALS_ICON = "resources/toolbar/surface_minerals.png"
MINERAL_CONCENTRATIONS_ICON = "resources/toolbar/mineral_concentration.png"
PERCENT_ICON = "resources/toolbar/percent.png"
ZOOM_ICON = "resources/toolbar/magnifying_glass.png"
POPULATION_ICON = "resources/toolbar/population_view.png"
NO_PLAYER_INFO_ICON = "resources/toolbar/no_player_info.png"
ADD_WAYPOINT_ICON = "resources/toolbar/add_waypoint.png"
SHOW_ROUTES_ICON = "resources/toolbar/show_routes.png"
IDLE_FLEETS_ICON = "resources/toolbar/idle_fleets.png"
SHIP_DESIGN_FILTER_ICON = "resources/toolbar/ship_design_filter.png"
ENEMY_DESIGN_FILTER_ICON = "resources/toolbar/enemy_ship_filter.png"
PLANET_NAMES_ICON = "resources/toolbar/planet_names.png"

TOOLBAR_ICON_SIZE = QSize(24, 24)


def build_toolbar_button(main_window, icon_path, tooltip):

    created_button = QPushButton(main_window)
    created_button.setIcon(QIcon(icon_path))
    created_button.setIconSize(TOOLBAR_ICON_SIZE)
    created_button.setToolTip(tooltip)
    return created_button


def build_main_toolbar(main_window):

    toolbar_map = {}
    toolbar_table = [
        {
            "name": "normal_view",
            "icon_path": NORMAL_VIEW_ICON,
            "handler": main_window.handle_normal_view,
            "tooltip": "Normal View",
            "checkable": True
        },
        {
            "name": "surface_minerals_view",
            "icon_path": SURFACE_MINERALS_ICON,
            "handler": main_window.handle_surface_minerals,
            "tooltip": "Surface Mineral View",
            "checkable": True
        },
        {
            "name": "mineral_concentration_view",
            "icon_path": MINERAL_CONCENTRATIONS_ICON,
            "handler": main_window.handle_mineral_concentrations,
            "tooltip": "Mineral Concentration View",
            "checkable": True
        },
        {
            "name": "value_view",
            "icon_path": PERCENT_ICON,
            "handler": main_window.handle_percent_population,
            "tooltip": "Planet Value View",
            "checkable": True
        },
        {
            "name": "population_view",
            "icon_path": POPULATION_ICON,
            "handler": main_window.handle_population_view,
            "tooltip": "Population View",
            "checkable": True
        },
        {
            "name": "no_info_view",
            "icon_path": NO_PLAYER_INFO_ICON,
            "handler": main_window.handle_no_player_info,
            "tooltip": "No Player Info View",
            "separator_after": True,
            "checkable": True
        },
        {
            "name": "add_waypoints_mode",
            "icon_path": ADD_WAYPOINT_ICON,
            "handler": main_window.handle_add_waypoints,
            "tooltip": "Add Waypoints Mode",
            "separator_after": True
        },
        {
            "name": "fleet_paths_overlay",
            "icon_path": SHOW_ROUTES_ICON,
            "handler": main_window.handle_fleet_paths,
            "tooltip": "Fleet Paths Overlay",
            "separator_after": True,
            "checkable": True
        },
        {
            "name": "planet_names_overlay",
            "icon_path": PLANET_NAMES_ICON,
            "handler": main_window.handle_planet_names_toggle,
            "tooltip": "Planet Names Overlay",
            "checkable": True
        },
        {
            "name": "idle_fleets_overlay",
            "icon_path": IDLE_FLEETS_ICON,
            "handler": main_window.handle_idle_fleets_filter,
            "tooltip": "Idle Fleets Filter",
        },
        {
            "name": "ship_design_filter",
            "icon_path": SHIP_DESIGN_FILTER_ICON,
            "handler": main_window.handle_ship_design_filter,
            "tooltip": "Ship Design Filter",
        },
        {
            "name": "enemy_ship_design_filter",
            "icon_path": ENEMY_DESIGN_FILTER_ICON,
            "handler": main_window.handle_enemy_design_filter,
            "tooltip": "Enemy Ship Class Filter",
            "separator_after": True
        },
        {
            "name": "zoom_button",
            "icon_path": ZOOM_ICON,
            "menu": main_window.menu_map["zoom"],
            "tooltip": "Zoom Menu",
        },
    ]

    toolbar = main_window.toolbar

    for item in toolbar_table:
        created_button = build_toolbar_button(main_window,
                                              item["icon_path"],
                                              item["tooltip"])
        toolbar.addWidget(created_button)

        if("handler" in item):
            created_button.clicked.connect(item["handler"])

        if("menu" in item):
            created_button.setMenu(item["menu"])

        if("checkable" in item and item["checkable"]):
            created_button.setCheckable(True)

        if("separator_after" in item and item["separator_after"]):
            toolbar.addSeparator()

        toolbar_map.update({item["name"]: created_button})

    toolbar.visibilityChanged.connect(main_window.update_toolbar_status)

    toolbar_map["planet_names_overlay"].setChecked(
        main_window.view_options.planet_names_overlay)

    space_planet_views = QButtonGroup()
    space_planet_views.addButton(toolbar_map["normal_view"])
    space_planet_views.addButton(toolbar_map["surface_minerals_view"])
    space_planet_views.addButton(toolbar_map["mineral_concentration_view"])
    space_planet_views.addButton(toolbar_map["value_view"])
    space_planet_views.addButton(toolbar_map["population_view"])
    space_planet_views.addButton(toolbar_map["no_info_view"])

    planet_view_option = main_window.view_options.planet_view
    space_planet_views.buttons()[planet_view_option].setChecked(True)

    toolbar_map.update({"space_planet_views": space_planet_views})
    return toolbar_map
