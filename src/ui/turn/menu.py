"""
    ui.turn.menu

    Defines helper functions to build up the turn editor menu.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from PySide.QtGui import QAction
from PySide.QtGui import QActionGroup


def build_action_map(main_window):

    action_map = {}
    action_table = [
        {
            "action_name": '&New...',
            "shortcut": 'Ctrl+N',
            "status_tip": 'Create new game.',
            "trigger": main_window.handle_new_game,
            "map_name": 'new'
        },
        {
            "action_name": '&Open...',
            "shortcut": 'Ctrl+O',
            "status_tip": 'Open a previously saved game.',
            "trigger": main_window.handle_open_game,
            "map_name": 'open'
        },
        {
            "action_name": '&Save',
            "shortcut": 'Ctrl+S',
            "status_tip": 'Save the current game changes.',
            "trigger": main_window.handle_save_game,
            "map_name": 'save'
        },
        {
            "action_name": 'Custom &Race Wizard...',
            "shortcut": None,
            "status_tip": 'Build a custom race.',
            "trigger": main_window.handle_custom_race_wizard,
            "map_name": 'custom_race'
        },
        {
            "action_name": '&Close',
            "shortcut": None,
            "status_tip": 'Close the current game and return to the main \
                           screen.',
            "trigger": main_window.handle_close_game,
            "map_name": 'close'
        },
        {
            "action_name": 'E&xit',
            "shortcut": None,
            "status_tip": 'Exit the game.',
            "trigger": main_window.handle_exit_game,
            "map_name": 'exit'
        },
        {
            "action_name": '&Toolbar',
            "shortcut": None,
            "status_tip": 'Toggle the toolbar.',
            "trigger": main_window.handle_toggle_toolbar,
            "map_name": 'toggle_toolbar'
        },
        {
            "action_name": '&Find...',
            "shortcut": 'Ctrl+F',
            "status_tip": 'Find a planet or fleet.',
            "trigger": main_window.handle_find,
            "map_name": 'find'
        },
        {
            "action_name": '25%',
            "shortcut": None,
            "status_tip": 'Zoom the space window to 25%.',
            "trigger": main_window.handle_zoom_25,
            "map_name": 'zoom_25'
        },
        {
            "action_name": '38%',
            "shortcut": None,
            "status_tip": 'Zoom the space window to 38%.',
            "trigger": main_window.handle_zoom_38,
            "map_name": 'zoom_38'
        },
        {
            "action_name": '50%',
            "shortcut": None,
            "status_tip": 'Zoom the space window to 50%.',
            "trigger": main_window.handle_zoom_50,
            "map_name": 'zoom_50'
        },
        {
            "action_name": '100%',
            "shortcut": None,
            "status_tip": 'Zoom the space window to 100%.',
            "trigger": main_window.handle_zoom_100,
            "map_name": 'zoom_100'
        },
        {
            "action_name": '125%',
            "shortcut": None,
            "status_tip": 'Zoom the space window to 125%.',
            "trigger": main_window.handle_zoom_125,
            "map_name": 'zoom_125'
        },
        {
            "action_name": '150%',
            "shortcut": None,
            "status_tip": 'Zoom the space window to 150%.',
            "trigger": main_window.handle_zoom_150,
            "map_name": 'zoom_150'
        },
        {
            "action_name": '200%',
            "shortcut": None,
            "status_tip": 'Zoom the space window to 200%.',
            "trigger": main_window.handle_zoom_200,
            "map_name": 'zoom_200'
        },
        {
            "action_name": '400%',
            "shortcut": None,
            "status_tip": 'Zoom the space window to 400%.',
            "trigger": main_window.handle_zoom_400,
            "map_name": 'zoom_400'
        },
        {
            "action_name": "&Race...",
            "shortcut": 'F8',
            "status_tip": "View your current race.",
            "trigger": main_window.handle_current_race_wizard,
            "map_name": 'current_race'
        },
        {
            "action_name": "&Game Parameters...",
            "shortcut": None,
            "status_tip": "View the current game paramters.",
            "trigger": main_window.handle_view_game_parameters,
            "map_name": "game_parameters"
        },
        {
            "action_name": "&Generate",
            "shortcut": "F9",
            "status_tip": "Generate the next turn.",
            "trigger": main_window.handle_generate,
            "map_name": "generate"
        },
        {
            "action_name": "&Ship Design...",
            "shortcut": "F4",
            "status_tip": "Build custom ship designs.",
            "trigger": main_window.handle_ship_design,
            "map_name": "ship_design"
        },
        {
            "action_name": "&Research...",
            "shortcut": "F5",
            "status_tip": "Set research levels.",
            "trigger": main_window.handle_research,
            "map_name": "research"
        },
        {
            "action_name": "&Battle Plans...",
            "shortcut": "F6",
            "status_tip": "Create battle orders for ships and fleets.",
            "trigger": main_window.handle_battle_plans,
            "map_name": "battle_plans"
        },
        {
            "action_name": "&Planets...",
            "shortcut": None,
            "status_tip": "Show a report of colonized planets.",
            "trigger": main_window.handle_planets_report,
            "map_name": "planets"
        },
        {
            "action_name": "&Fleets...",
            "shortcut": "Show a report of your fleets.",
            "status_tip": None,
            "trigger": main_window.handle_fleets_report,
            "map_name": "fleets"
        },
        {
            "action_name": "&Other Fleets...",
            "shortcut": None,
            "status_tip": "Show a report of fleets that are not your own.",
            "trigger": main_window.handle_other_fleets_report,
            "map_name": "other_fleets"
        },
        {
            "action_name": "&Battles...",
            "shortcut": None,
            "status_tip": "Show a report of battles you have been involved in \
                          this turn",
            "trigger": main_window.handle_battle_report,
            "map_name": "battles"
        },
        {
            "action_name": "&Score...",
            "shortcut": "F10",
            "status_tip": "Show the current game score",
            "trigger": main_window.handle_score,
            "map_name": "score"
        },
        {
            "action_name": "&Universe Information",
            "shortcut": None,
            "status_tip": "Write all known universe information to a file.",
            "trigger": main_window.handle_dump_universe,
            "map_name": "dump_universe"
        },
        {
            "action_name": "&Planet Information",
            "shortcut": None,
            "status_tip": "Write all known planet information to a file.",
            "trigger": main_window.handle_dump_planets,
            "map_name": "dump_planets"
        },
        {
            "action_name": "&Fleet Information",
            "shortcut": None,
            "status_tip": "Write all known fleet information to a file.",
            "trigger": main_window.handle_dump_fleets,
            "map_name": "dump_fleets"
        },
        {
            "action_name": "&Introduction...",
            "shortcut": None,
            "status_tip": "Introduction to this game.",
            "trigger": main_window.handle_introduction,
            "map_name": "introduction"
        },
        {
            "action_name": "&Player's Guide...",
            "shortcut": "F1",
            "status_tip": "The player's reference manual for this game.",
            "trigger": main_window.handle_guide,
            "map_name": "guide"
        },
        {
            "action_name": "Technology &Browser...",
            "shortcut": "F2",
            "status_tip": "View components available via technology advances.",
            "trigger": main_window.handle_tech_browser,
            "map_name": "tech_browser"
        },
        {
            "action_name": "&Tutorial",
            "shortcut": None,
            "status_tip": "Begin the tutorial.",
            "trigger": main_window.handle_tutorial,
            "map_name": "tutorial"
        },
        {
            "action_name": "&About...",
            "shortcut": None,
            "status_tip": "View details of this game.",
            "trigger": main_window.handle_about,
            "map_name": "about"
        }
    ]

    for action in action_table:
        built_action = build_action(main_window,
                                    action["action_name"],
                                    action["shortcut"],
                                    action["status_tip"],
                                    action["trigger"])

        action_map.update({action["map_name"]: built_action})

    return action_map


def build_main_menu(main_window):

    menu_bar = main_window.menuBar()
    action_map = main_window.action_map

    menu_map = {}

    # File Menu
    file_menu = menu_bar.addMenu('&File')
    file_menu.addAction(action_map["new"])
    file_menu.addAction(action_map["open"])
    file_menu.addAction(action_map["save"])
    file_menu.addSeparator()
    file_menu.addAction(action_map["custom_race"])
    file_menu.addSeparator()
    file_menu.addAction(action_map["close"])
    file_menu.addAction(action_map["exit"])
    menu_map.update({"file": file_menu})

    # View Menu
    view_menu = menu_bar.addMenu('&View')
    view_menu.addAction(action_map["toggle_toolbar"])
    action_map["toggle_toolbar"].setCheckable(True)
    view_menu.addSeparator()
    view_menu.addAction(action_map["find"])

    zoom_menu = view_menu.addMenu("&Zoom")
    zoom_levels = QActionGroup(main_window)
    zoom_levels.addAction(action_map["zoom_25"])
    zoom_levels.addAction(action_map["zoom_38"])
    zoom_levels.addAction(action_map["zoom_50"])
    zoom_levels.addAction(action_map["zoom_100"])
    zoom_levels.addAction(action_map["zoom_125"])
    zoom_levels.addAction(action_map["zoom_150"])
    zoom_levels.addAction(action_map["zoom_200"])
    zoom_levels.addAction(action_map["zoom_400"])

    for action in zoom_levels.actions():
        action.setCheckable(True)
        zoom_menu.addAction(action)

    zoom_levels.actions()[main_window.view_options.zoom_level].setChecked(True)
    menu_map.update({"zoom": zoom_menu})

    view_menu.addSeparator()
    view_menu.addAction(action_map["current_race"])
    view_menu.addAction(action_map["game_parameters"])
    menu_map.update({"view": view_menu})

    # Turn Menu
    turn_menu = menu_bar.addMenu('&Turn')
    turn_menu.addAction(action_map["generate"])
    menu_map.update({"turn": turn_menu})

    # Commands Menu
    commands_menu = menu_bar.addMenu('&Commands')
    commands_menu.addAction(action_map["ship_design"])
    commands_menu.addAction(action_map["research"])
    commands_menu.addAction(action_map["battle_plans"])
    menu_map.update({"commands": commands_menu})

    # Report
    report_menu = menu_bar.addMenu('&Report')
    report_menu.addAction(action_map["planets"])
    report_menu.addAction(action_map["fleets"])
    report_menu.addAction(action_map["other_fleets"])
    report_menu.addSeparator()
    report_menu.addAction(action_map["battles"])
    report_menu.addSeparator()
    report_menu.addAction(action_map["score"])
    report_menu.addSeparator()
    dump_menu = report_menu.addMenu("&Dump to Text File")
    dump_menu.addAction(action_map["dump_universe"])
    dump_menu.addAction(action_map["dump_planets"])
    dump_menu.addAction(action_map["dump_fleets"])
    menu_map.update({"report": report_menu})
    menu_map.update({"dump": dump_menu})

    # Help Menu
    help_menu = menu_bar.addMenu('&Help')
    help_menu.addAction(action_map["introduction"])
    help_menu.addAction(action_map["guide"])
    help_menu.addSeparator()
    help_menu.addAction(action_map["tech_browser"])
    help_menu.addAction(action_map["tutorial"])
    help_menu.addSeparator()
    help_menu.addAction(action_map["about"])
    menu_map.update({"help": help_menu})
    return menu_map


def build_action(main_window, action_name, shortcut, status_tip, trigger):
    """
    Builds a QAction from its component parts.
    """
    built_action = QAction(action_name, main_window)
    if not shortcut is None:
        built_action.setShortcut(shortcut)
    built_action.setStatusTip(status_tip)
    built_action.triggered.connect(trigger)
    return built_action
