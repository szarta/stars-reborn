"""
    ui.turn.editor

    Contains all of the data and capabilities needed for the central GUI.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import os
import logging
from PySide.QtGui import QMainWindow
from PySide.QtGui import QLabel
from PySide.QtGui import QSplitter
from PySide.QtCore import Qt

from src.ui.dialogs import about
from space import SpaceMap
from resourceinfo import PlanetInfo
from planetimage import PlanetImage
import menu
import toolbar

from src.model.turn import read_turn_file

from src.model.enumerations import ZoomLevel
from src.model.enumerations import PlanetView

from src.data import Language_Map

#from src.ui.dialogs.race import RaceWizard


class ViewOptions:

    def __init__(self):
        self.zoom_level = ZoomLevel.Default
        self.planet_view = PlanetView.Default
        self.planet_names_overlay = True

    def zoom_multiplier(self):
        return ZoomLevel.multipliers()[self.zoom_level]


class CoreUI(QMainWindow):

    def __init__(self, turn_file):
        super(CoreUI, self).__init__()
        logging.debug("initializing UI")

        # TODO: will probably have to do this in the background
        self.focus_object = None
        self.interest_object = None

        self.turn = read_turn_file(turn_file)
        self.game = self.turn.visible_game
        self.universe = self.game.universe

        self.active_player = self.game.players[self.turn.active_player]

        self.title = "{0} - {1} - {2} - {3}".format(
            Language_Map["game-name"],
            self.game.name,
            self.active_player.race.name,
            os.path.basename(turn_file))

        # TODO: check for saved view options
        self.view_options = ViewOptions()
        logging.debug("loading view")
        self.init_ui()

    def init_ui(self, turn_file=None):

        self.setGeometry(150, 150, 1080, 720)
        self.setWindowTitle(self.title)

        self.action_map = menu.build_action_map(self)
        self.toolbar = self.addToolBar('Main Toolbar')
        self.menu_map = menu.build_main_menu(self)
        self.toolbar_map = toolbar.build_main_toolbar(self)

        main_layout = QSplitter(Qt.Horizontal)

        homeworld = self.universe.planets[self.active_player.homeworld]
        self.focus_object = homeworld
        self.planet_info = PlanetInfo(homeworld, self.active_player.race)

        generated_svg = self.universe.to_svg(
            self.view_options, self.active_player)

        self.space_map = SpaceMap(generated_svg)

        (x, y) = homeworld.location
        self.space_map.update_coords(homeworld.id, x, y, homeworld.name)

        left_pane = QSplitter(Qt.Vertical)
        self.planet_image = PlanetImage(homeworld)
        left_pane.addWidget(self.planet_image)
        left_pane.addWidget(QLabel(" Message box"))

        right_pane = QSplitter(Qt.Vertical)
        right_pane.addWidget(self.space_map)
        right_pane.addWidget(self.planet_info)
        self.space_map.planet_selected.connect(self.handle_planet_selected)

        main_layout.addWidget(left_pane)
        main_layout.addWidget(right_pane)

        self.setCentralWidget(main_layout)

        self.statusBar().showMessage('Ready')

    def handle_planet_selected(self, pid):
        planet = self.universe.planets[pid]

        if(self.interest_object == planet):
            # TODO: change the left pane to have planet information
            # if owned by current player

            # TODO: check if owned before making this assignment
            self.focus_object = planet

            # TODO: also, if focused already, will cycle through any ships
        else:
            self.interest_object = planet
            (x, y) = planet.location
            self.space_map.update_coords(pid, x, y, planet.name)

            distance = self.focus_object.distance_from(self.interest_object)
            self.space_map.update_light_years(distance, self.focus_object.name)

            self.planet_info.update_planet(planet)

    def handle_new_game(self):
        print "New game!"

    def handle_custom_race_wizard(self):

        print "Custom Race Wizard!"
        #dialog = CustomizeRaceWizard(self)
        #dialog.exec_()

    def handle_current_race_wizard(self):
        #race_view_dialog = RaceWizard(self, player.race, True)
        #race_view_dialog.exec_()
        print "Race wizard!"

    def handle_open_game(self):
        print "Open game!"

    def handle_close_game(self):
        print "Close game!"

    def handle_save_game(self):
        print "Save game!"

    def handle_exit_game(self):
        self.close()

    def update_toolbar_status(self):
        if(self.toolbar.isVisible()):
            self.action_map["toggle_toolbar"].setChecked(True)
        else:
            self.action_map["toggle_toolbar"].setChecked(False)

    def handle_toggle_toolbar(self):
        if(self.toolbar.isVisible()):
            self.toolbar.hide()
        else:
            self.toolbar.show()

    def handle_find(self):
        print "Find!"

    def handle_zoom_25(self):
        self.view_options.zoom_level = ZoomLevel.Level_25
        self.refresh_space()

    def handle_zoom_38(self):
        self.view_options.zoom_level = ZoomLevel.Level_38
        self.refresh_space()

    def handle_zoom_50(self):
        self.view_options.zoom_level = ZoomLevel.Level_50
        self.refresh_space()

    def handle_zoom_100(self):
        self.view_options.zoom_level = ZoomLevel.Level_100
        self.refresh_space()

    def handle_zoom_125(self):
        self.view_options.zoom_level = ZoomLevel.Level_125
        self.refresh_space()

    def handle_zoom_150(self):
        self.view_options.zoom_level = ZoomLevel.Level_150
        self.refresh_space()

    def handle_zoom_200(self):
        self.view_options.zoom_level = ZoomLevel.Level_200
        self.refresh_space()

    def handle_zoom_400(self):
        self.view_options.zoom_level = ZoomLevel.Level_400
        self.refresh_space()

    def handle_view_game_parameters(self):
        print "Game Parameters!"

    def handle_generate(self):
        print "Generate!"

    def handle_ship_design(self):
        print "Ship Design!"

    def handle_research(self):
        print "Research!"

    def handle_battle_plans(self):
        print "Battle Plans!"

    def handle_planets_report(self):
        print "Planets report!"

    def handle_fleets_report(self):
        print "Fleets report!"

    def handle_other_fleets_report(self):
        print "Other fleets report!"

    def handle_battle_report(self):
        print "Battle report!"

    def handle_score(self):
        print "Game score!"

    def handle_dump_universe(self):
        print "Dump Universe!"

    def handle_dump_fleets(self):
        print "Dump Fleets!"

    def handle_dump_planets(self):
        print "Dump Planets!"

    def handle_introduction(self):
        print "Introduction!"

    def handle_guide(self):
        print "Guide!"

    def handle_tech_browser(self):
        print "Tech Browser!"

    def handle_tutorial(self):
        print "Tutorial!"

    def handle_normal_view(self):
        self.view_options.planet_view = PlanetView.Normal
        self.refresh_space()

    def handle_surface_minerals(self):
        print "Surface Minerals!"

    def handle_mineral_concentrations(self):
        print "Mineral Concentrations!"

    def handle_percent_population(self):
        print "Percent Population!"

    def handle_population_view(self):
        print "Population view!"

    def handle_no_player_info(self):
        self.view_options.planet_view = PlanetView.No_Info
        self.refresh_space()

    def handle_add_waypoints(self):
        print "Add waypoints!"

    def handle_fleet_paths(self):
        print "Fleet paths!"

    def handle_ship_design_filter(self):
        print "Ship design filter!"

    def handle_enemy_design_filter(self):
        print "Enemy design filter!"

    def handle_idle_fleets_filter(self):
        print "Idle fleets filter!"

    def handle_planet_names_toggle(self):
        enabled = self.toolbar_map["planet_names_overlay"].isChecked()
        self.view_options.planet_names_overlay = enabled
        self.refresh_space()

    def handle_about(self):
        dialog = about.AboutDialog(self)
        dialog.exec_()

    def refresh_space(self):
        generated_svg = self.universe.to_svg(
            self.view_options, self.active_player)

        self.space_map.update_view(generated_svg)
