"""
    ui.dialogs.race

    Contains all the data and capabilities needed for race creation.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from PySide.QtGui import QDialog
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QLineEdit
from PySide.QtGui import QComboBox
from PySide.QtGui import QStackedLayout
from PySide.QtGui import QFormLayout
from PySide.QtGui import QLabel
from PySide.QtGui import QFrame
from PySide.QtGui import QToolButton
from PySide.QtGui import QCheckBox
from PySide.QtGui import QPixmap
from PySide.QtGui import QTextEdit
from PySide.QtGui import QGroupBox
from PySide.QtGui import QWidget
from PySide.QtGui import QPushButton
from PySide.QtGui import QPainter
from PySide.QtCore import Qt
from PySide.QtCore import QRect

from objects.race import Race
from parameters.race import TemperatureParameters
from parameters.race import LesserRacialTrait
from parameters.race import PrimaryRacialTrait
from parameters.race import LeftoverPointsOption
from parameters.race import TechnologyCostOption
from parameters.races import PredefinedRaces

import glob
import math

from ui import helpers

PREVIOUS_ICON = "resources/previous.png"
RACE_ICON_LOCATION = "resources/race"


class RaceIconResources():
    """
        This is a temporary placeholder until a full resource manager is
        developed.
    """
    def __init__(self):
        self.icons = []
        self.discover_icons(RACE_ICON_LOCATION)

    def discover_icons(self, location):
        glob_search = location + "/*.png"
        self.icons = glob.glob(glob_search)

    def index_of(self, image_path):
        index = 0
        if(image_path in self.icons):
            index = self.icons.index(image_path)

        return index


class ColorSlider(QWidget):

    def __init__(self, puck_color, min_value, max_value, start_min, start_max,
                 parent=None):

        super(ColorSlider, self).__init__(parent)

        self.slider_height = 30
        self.slider_width = 250
        self.puck_color = puck_color
        self.setFixedHeight(self.slider_height)
        self.setFixedWidth(self.slider_width)

        self.slope = float(self.slider_width) / float(max_value - min_value)
        self.offset = -1.0 * (float(min_value) * self.slope)

        self.update_value(start_min, start_max)

    def update_value(self, current_low, current_high, ignore_values=False):

        self.low_point = math.floor(self.slope * current_low + self.offset)
        self.high_point = math.floor(self.slope * current_high + self.offset)
        self.ignore_values = ignore_values

        self.repaint()

    def paintEvent(self, event):

        painter = QPainter(self)
        bg_rect = self.rect()
        painter.fillRect(bg_rect, Qt.black)

        if(not self.ignore_values):
            width = self.high_point - self.low_point
            puck_rect = QRect(self.low_point, 0, width, self.slider_height)
            painter.fillRect(puck_rect, self.puck_color)


class ArrowControl(QWidget):

    def __init__(self, text_before, text_after,
                 increment_callback, decrement_callback, parent=None):
        super(ArrowControl, self).__init__(parent)

        self.increment_callback = increment_callback
        self.decrement_callback = decrement_callback

        main_layout = QBoxLayout(QBoxLayout.LeftToRight)
        main_layout.addWidget(QLabel(text_before))

        self.value_label = QLabel()
        main_layout.addWidget(self.value_label)

        self.increment_arrow = QToolButton()
        self.increment_arrow.setArrowType(Qt.UpArrow)
        self.increment_arrow.setMaximumHeight(10)

        self.decrement_arrow = QToolButton()
        self.decrement_arrow.setArrowType(Qt.DownArrow)
        self.decrement_arrow.setMaximumHeight(10)

        arrow_container = QBoxLayout(QBoxLayout.TopToBottom)
        arrow_container.addWidget(self.increment_arrow)
        arrow_container.addWidget(self.decrement_arrow)
        main_layout.addLayout(arrow_container)

        main_layout.addWidget(QLabel(text_after))
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def update_value(self, new_value):
        self.value_label.setText(str(new_value))

    def bind_callbacks(self):
        self.increment_arrow.clicked.connect(self.increment_callback)
        self.decrement_arrow.clicked.connect(self.decrement_callback)


class RaceWizard(QDialog):
    """
        The race wizard for race creation/editing/viewing.

        In view-only (self.read_only) mode, the race will be presented, but all
        controls that allow modification will be disabled.

        The primary output object of this dialog in creation/edit mode, if
        accepted, is:

            self.race

        The UI will enforce a legal race upon dialog exit, where a legal race
        is one that returns True from self.race.is_legal()
    """
    HELP_BUTTON_ID = 0
    CANCEL_BUTTON_ID = 1
    PREVIOUS_BUTTON_ID = 2
    NEXT_BUTTON_ID = 3
    FINISH_BUTTON_ID = 4

    def __init__(self, parent=None, race=None, readonly=False):
        super(RaceWizard, self).__init__(parent)

        if(race):
            self.race = race
        else:
            self.race = Race()

        self.icon_resources = RaceIconResources()

        self.read_only = readonly

        self.init_user_controls()
        self.init_ui()
        self.bind_user_controls()

        if not race:
            self.base_races.button(PredefinedRaces.Default).setChecked(True)
            self.handle_base_race_change()

    def init_user_controls(self):
        """
        Sets up all important user controls on this form.
        """

        self.advantage_points = QLabel()

        self.race_name = QLineEdit()
        self.plural_race_name = QLineEdit()
        self.password = QLineEdit()

        self.leftover_points = QComboBox()
        self.leftover_points.addItems(LeftoverPointsOption.names())

        buttons = [
            "&Help",
            "&Cancel",
            "&Previous",
            "&Next"
        ]

        if(self.read_only):
            buttons.append("&Ok")
        else:
            buttons.append("&Finish")

        self.nav_buttons = helpers.build_push_button_group(buttons)

        self.primary_racials = helpers.build_radio_group(
            PrimaryRacialTrait.names())

        self.lesser_racials = helpers.build_checkbox_group(
            LesserRacialTrait.names())

        self.lesser_racials.setExclusive(False)

        self.base_races = helpers.build_radio_group(PredefinedRaces.names())

        self.previous_icon_button = QToolButton()
        self.previous_icon_button.setArrowType(Qt.LeftArrow)
        self.next_icon_button = QToolButton()
        self.next_icon_button.setArrowType(Qt.RightArrow)
        self.current_race_icon = self.race.icon
        self.race_icon_label = QLabel()
        self.race_icon_label.setAlignment(Qt.AlignCenter)

        self.prt_desc = QTextEdit()
        self.prt_desc.setFixedHeight(160)
        self.prt_desc.setReadOnly(True)

        self.lrt_desc = QTextEdit()
        self.lrt_desc.setFixedHeight(110)
        self.lrt_desc.setReadOnly(True)

        self.temperature_max = QLabel()
        self.temperature_max.setAlignment(Qt.AlignCenter)

        self.increment_temperature_range = QPushButton("<<  >>")

        self.increment_temperature_midpoint = QToolButton()
        self.increment_temperature_midpoint.setArrowType(Qt.RightArrow)

        self.decrement_temperature_range = QPushButton(">>  <<")

        self.decrement_temperature_midpoint = QToolButton()
        self.decrement_temperature_midpoint.setArrowType(Qt.LeftArrow)

        self.temperature_slider = ColorSlider(Qt.darkRed,
                                              TemperatureParameters.Minimum,
                                              TemperatureParameters.Maximum,
                                              self.race.temperature_min,
                                              self.race.temperature_max)

        self.temperature_min = QLabel()
        self.temperature_min.setAlignment(Qt.AlignCenter)

        self.temperature_immune = QCheckBox("Immune to Temperature")

        self.growth_rate = ArrowControl(
            "Maximum colonist growth rate percentage per year: ",
            " ",
            self.handle_increment_growth_rate,
            self.handle_decrement_growth_rate)

        self.resource_production = ArrowControl(
            "One resource is generated each year for every ",
            " colonists.",
            self.handle_increment_colonist_resource,
            self.handle_decrement_colonist_resource)

        self.factory_production = ArrowControl(
            "Every 10 factories produce ", " resources each year.",
            self.handle_increment_factory_production,
            self.handle_decrement_factory_production)

        self.factory_cost = ArrowControl(
            "Factories require ", "resources to build.",
            self.handle_increment_factory_cost,
            self.handle_decrement_factory_cost)

        self.colonists_operate_factories = ArrowControl(
            "Every 10,000 colonists may operate up to ",
            "factories.", self.handle_increment_colonists_operate_factories,
            self.handle_decrement_colonists_operate_factories)

        self.factory_cheap_germanium = QCheckBox(
            "Factories cost 1kT less Germanium to build.")

        self.mine_production = ArrowControl(
            "Every 10 mines produce up to ",
            " kT of each mineral each year.",
            self.handle_increment_mine_production,
            self.handle_decrement_mine_production)

        self.mine_cost = ArrowControl(
            "Mines require ", "resources to build.",
            self.handle_increment_mine_cost,
            self.handle_decrement_mine_cost)

        self.colonists_operate_mines = ArrowControl(
            "Every 10,000 colonists may operate up to ",
            "mines.", self.handle_increment_colonists_operate_mines,
            self.handle_decrement_colonists_operate_mines)

        tech_cost_names = TechnologyCostOption.names()

        self.energy_research_cost = helpers.build_radio_group(
            tech_cost_names)

        self.electronics_research_cost = helpers.build_radio_group(
            tech_cost_names)

        self.construction_research_cost = helpers.build_radio_group(
            tech_cost_names)

        self.biotech_research_cost = helpers.build_radio_group(
            tech_cost_names)

        self.weapons_research_cost = helpers.build_radio_group(
            tech_cost_names)

        self.propulsion_research_cost = helpers.build_radio_group(
            tech_cost_names)

        self.expensive_tech = QCheckBox(
            "All 'Costs 75% extra' research fields start at Tech 4.")

        if(self.read_only):
            self.nav_buttons.button(self.CANCEL_BUTTON_ID).setVisible(False)
            self.previous_icon_button.setEnabled(False)
            self.next_icon_button.setEnabled(False)

        self.tabbed_layout = QStackedLayout()

    def bind_user_controls(self):
        """
        Binds all user controls used by this form to their handlers.
        """
        self.nav_buttons.buttonClicked.connect(self.handle_nav_button)
        self.previous_icon_button.clicked.connect(self.handle_previous_icon)
        self.next_icon_button.clicked.connect(self.handle_next_icon)
        self.primary_racials.buttonClicked.connect(
            self.handle_primary_racial_change)

        self.lesser_racials.buttonClicked.connect(
            self.handle_lesser_racial_change)

        self.base_races.buttonClicked.connect(
            self.handle_base_race_change)

        self.increment_temperature_midpoint.clicked.connect(
            self.handle_increment_temperature_midpoint)

        self.decrement_temperature_midpoint.clicked.connect(
            self.handle_decrement_temperature_midpoint)

        self.increment_temperature_range.clicked.connect(
            self.handle_increment_temperature_range)

        self.decrement_temperature_range.clicked.connect(
            self.handle_decrement_temperature_range)

        self.temperature_immune.clicked.connect(
            self.handle_temperature_immune_change)

        self.growth_rate.bind_callbacks()

        self.energy_research_cost.buttonClicked.connect(
            self.handle_energy_cost_change)

        self.weapons_research_cost.buttonClicked.connect(
            self.handle_weapons_cost_change)

        self.biotech_research_cost.buttonClicked.connect(
            self.handle_biotech_cost_change)

        self.electronics_research_cost.buttonClicked.connect(
            self.handle_electronics_cost_change)

        self.propulsion_research_cost.buttonClicked.connect(
            self.handle_propulsion_cost_change)

        self.construction_research_cost.buttonClicked.connect(
            self.handle_construction_cost_change)
        self.expensive_tech.clicked.connect(self.handle_expensive_tech)

        self.resource_production.bind_callbacks()
        self.factory_production.bind_callbacks()
        self.factory_cost.bind_callbacks()
        self.colonists_operate_factories.bind_callbacks()

        self.factory_cheap_germanium.clicked.connect(
            self.handle_factory_cheap_germanium_change)

        self.mine_production.bind_callbacks()
        self.mine_cost.bind_callbacks()
        self.colonists_operate_mines.bind_callbacks()

    def init_ui(self):
        """
        Builds up the user interface - laying out the user controls on this
        form, any relevant tabbed frames, titles, icons, etc.
        """
        if(self.read_only):
            self.setWindowTitle('View Race Details')
        else:
            self.setWindowTitle('Custom Race Wizard')

        self.tabbed_layout.addWidget(self.create_race_general_details_page())
        self.tabbed_layout.addWidget(self.create_primary_trait_page())
        self.tabbed_layout.addWidget(self.create_lesser_trait_page())
        self.tabbed_layout.addWidget(self.create_environmental_habitat_page())
        self.tabbed_layout.addWidget(self.create_economy_page())
        self.tabbed_layout.addWidget(self.create_research_cost_page())
        self.manage_navigation_state(0)

        button_box = QBoxLayout(QBoxLayout.LeftToRight)
        button_box.addWidget(self.nav_buttons.button(self.HELP_BUTTON_ID))
        button_box.addWidget(self.nav_buttons.button(self.CANCEL_BUTTON_ID))
        button_box.addWidget(self.nav_buttons.button(self.PREVIOUS_BUTTON_ID))
        button_box.addWidget(self.nav_buttons.button(self.NEXT_BUTTON_ID))
        button_box.addWidget(self.nav_buttons.button(self.FINISH_BUTTON_ID))

        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.advantage_points.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.advantage_points)
        main_layout.addLayout(self.tabbed_layout)
        main_layout.addLayout(button_box)

        self.update_advantage_points()

    def handle_base_race_change(self):
        selected_race = self.base_races.checkedId()
        if(selected_race != -1):
            self.race = PredefinedRaces.race(selected_race)
            self.apply_race_settings()

    def apply_race_settings(self):

        self.race_name.setText(self.race.name)
        self.plural_race_name.setText(self.race.plural_name)
        self.manage_icon_state(self.race.icon)
        self.leftover_points.setCurrentIndex(self.race.leftover_points)

        self.primary_racials.button(
            self.race.primary_racial_trait).setChecked(True)
        self.handle_primary_racial_change()

        for button in self.lesser_racials.buttons():
            button.setChecked(False)

        for trait in self.race.lesser_racial_traits:
            self.lesser_racials.button(trait).setChecked(True)

        self.update_temperature_labels()
        self.temperature_immune.setChecked(self.race.temperature_immune)

        self.growth_rate.update_value(self.race.growth_rate)

        self.resource_production.update_value(
            self.race.resource_production)

        self.factory_production.update_value(
            self.race.factory_production)

        self.factory_cost.update_value(self.race.factory_cost)
        self.colonists_operate_factories.update_value(
            self.race.colonists_operate_factories)

        self.factory_cheap_germanium.setChecked(
            self.race.factory_cheap_germanium)

        self.mine_production.update_value(self.race.mine_production)
        self.mine_cost.update_value(self.race.mine_cost)

        self.colonists_operate_mines.update_value(
            self.race.colonists_operate_mines)

        self.energy_research_cost.button(
            self.race.energy_cost).setChecked(True)

        self.propulsion_research_cost.button(
            self.race.propulsion_cost).setChecked(True)

        self.electronics_research_cost.button(
            self.race.electronics_cost).setChecked(True)

        self.construction_research_cost.button(
            self.race.construction_cost).setChecked(True)

        self.biotech_research_cost.button(
            self.race.biotechnology_cost).setChecked(True)

        self.weapons_research_cost.button(
            self.race.weapons_cost).setChecked(True)

        self.expensive_tech.setChecked(self.race.expensive_tech_boost)

        self.temperature_slider.update_value(self.race.temperature_min,
                                             self.race.temperature_max,
                                             self.race.temperature_immune)

        self.update_advantage_points()

    def update_advantage_points(self):
        self.race.recalculate_points()
        advantage_points = self.race.advantage_points
        self.advantage_points.setText('<b>Race Advantage Points: ' +
                                      str(advantage_points) + '</b>')

    def handle_primary_racial_change(self):
        selected_prt = self.primary_racials.checkedId()
        self.prt_desc.setText(PrimaryRacialTrait.descriptions()[selected_prt])
        self.race.primary_racial_trait = selected_prt
        self.update_advantage_points()

    def handle_lesser_racial_change(self, button):
        lrt_id = self.lesser_racials.id(button)

        if(lrt_id == LesserRacialTrait.Only_Basic_Remote_Mining):
            self.lesser_racials.button(
                LesserRacialTrait.Advanced_Remote_Mining).setChecked(False)

        if(lrt_id == LesserRacialTrait.Advanced_Remote_Mining):
            self.lesser_racials.button(
                LesserRacialTrait.Only_Basic_Remote_Mining).setChecked(False)

        self.lrt_desc.setText(LesserRacialTrait.descriptions()[lrt_id])
        self.update_lesser_racial_state()

    def update_lesser_racial_state(self):

        self.race.lesser_racial_traits = []

        for button in self.lesser_racials.buttons():
            if(button.isChecked()):
                lrt_id = self.lesser_racials.id(button)
                self.race.lesser_racial_traits.append(lrt_id)

        self.update_advantage_points()

    def handle_previous_icon(self):
        print self.current_race_icon
        self.manage_icon_state(self.current_race_icon - 1)

    def handle_next_icon(self):
        self.manage_icon_state(self.current_race_icon + 1)

    def manage_icon_state(self, new_index):
        self.current_race_icon = new_index % len(self.icon_resources.icons)
        self.race_icon_label.setPixmap(
            QPixmap(self.icon_resources.icons[self.current_race_icon]))

    def handle_nav_button(self, button):
        button_id = self.nav_buttons.id(button)

        if(button_id == self.CANCEL_BUTTON_ID):
            self.reject()
        elif(button_id == self.NEXT_BUTTON_ID):
            new_index = self.tabbed_layout.currentIndex() + 1
            self.manage_navigation_state(new_index)
        elif(button_id == self.PREVIOUS_BUTTON_ID):
            new_index = self.tabbed_layout.currentIndex() - 1
            self.manage_navigation_state(new_index)
        else:
            print "some other button"

    def handle_energy_cost_change(self):
        self.race.energy_cost = self.energy_research_cost.checkedId()
        self.update_advantage_points()

    def handle_weapons_cost_change(self):
        self.race.weapons_cost = self.weapons_research_cost.checkedId()
        self.update_advantage_points()

    def handle_biotech_cost_change(self):
        self.race.biotechnology_cost = self.biotech_research_cost.checkedId()
        self.update_advantage_points()

    def handle_electronics_cost_change(self):
        self.race.electronics_cost = self.electronics_research_cost.checkedId()
        self.update_advantage_points()

    def handle_propulsion_cost_change(self):
        self.race.propulsion_cost = self.propulsion_research_cost.checkedId()
        self.update_advantage_points()

    def handle_construction_cost_change(self):
        self.race.construction_cost = \
            self.construction_research_cost.checkedId()

        self.update_advantage_points()

    def handle_expensive_tech(self):
        if(self.expensive_tech.isChecked()):
            self.race.expensive_tech_boost = True
        else:
            self.race.expensive_tech_boost = False

        self.update_advantage_points()

    def update_temperature_labels(self):
        self.temperature_min.setText(str(self.race.temperature_min))
        self.temperature_max.setText(str(self.race.temperature_max))

    def handle_increment_temperature_range(self):
        self.race.increment_temperature_range()
        self.update_temperature_labels()
        self.update_advantage_points()

        self.temperature_slider.update_value(self.race.temperature_min,
                                             self.race.temperature_max)

    def handle_increment_temperature_midpoint(self):
        self.race.increment_temperature_midpoint()
        self.update_temperature_labels()
        self.update_advantage_points()

        self.temperature_slider.update_value(self.race.temperature_min,
                                             self.race.temperature_max)

    def handle_decrement_temperature_range(self):
        self.race.decrement_temperature_range()
        self.update_temperature_labels()
        self.update_advantage_points()

        self.temperature_slider.update_value(self.race.temperature_min,
                                             self.race.temperature_max)

    def handle_decrement_temperature_midpoint(self):
        self.race.decrement_temperature_midpoint()
        self.update_temperature_labels()
        self.update_advantage_points()

        self.temperature_slider.update_value(self.race.temperature_min,
                                             self.race.temperature_max)

    def handle_temperature_immune_change(self):
        if(self.temperature_immune.isChecked()):
            self.race.temperature_immune = True
        else:
            self.race.temperature_immune = False

        self.update_advantage_points()

        self.temperature_slider.update_value(self.race.temperature_min,
                                             self.race.temperature_max,
                                             self.race.temperature_immune)

    def handle_increment_growth_rate(self):
        self.race.increment_growth_rate()
        self.growth_rate.update_value(self.race.growth_rate)
        self.update_advantage_points()

    def handle_decrement_growth_rate(self):
        self.race.decrement_growth_rate()
        self.growth_rate.update_value(self.race.growth_rate)
        self.update_advantage_points()

    def handle_increment_colonist_resource(self):
        self.race.increment_resource_production()
        self.resource_production.update_value(
            self.race.resource_production)

        self.update_advantage_points()

    def handle_decrement_colonist_resource(self):
        self.race.decrement_resource_production()
        self.resource_production.update_value(
            self.race.resource_production)

        self.update_advantage_points()

    def handle_increment_factory_production(self):
        self.race.increment_factory_production()
        self.factory_production.update_value(
            self.race.factory_production)

        self.update_advantage_points()

    def handle_decrement_factory_production(self):
        self.race.decrement_factory_production()
        self.factory_production.update_value(
            self.race.factory_production)

        self.update_advantage_points()

    def handle_increment_factory_cost(self):
        self.race.increment_factory_cost()
        self.factory_cost.update_value(self.race.factory_cost)
        self.update_advantage_points()

    def handle_decrement_factory_cost(self):
        self.race.decrement_factory_cost()
        self.factory_cost.update_value(self.race.factory_cost)
        self.update_advantage_points()

    def handle_increment_colonists_operate_factories(self):
        self.race.increment_colonists_operate_factories()
        self.colonists_operate_factories.update_value(
            self.race.colonists_operate_factories)
        self.update_advantage_points()

    def handle_decrement_colonists_operate_factories(self):
        self.race.decrement_colonists_operate_factories()
        self.colonists_operate_factories.update_value(
            self.race.colonists_operate_factories)
        self.update_advantage_points()

    def handle_factory_cheap_germanium_change(self):
        if(self.factory_cheap_germanium.isChecked()):
            self.race.factory_cheap_germanium = True
        else:
            self.race.factory_cheap_germanium = False

        self.update_advantage_points()

    def handle_increment_mine_production(self):
        self.race.increment_mine_production()
        self.mine_production.update_value(self.race.mine_production)
        self.update_advantage_points()

    def handle_decrement_mine_production(self):
        self.race.decrement_mine_production()
        self.mine_production.update_value(self.race.mine_production)
        self.update_advantage_points()

    def handle_increment_mine_cost(self):
        self.race.increment_mine_cost()
        self.mine_cost.update_value(self.race.mine_cost)
        self.update_advantage_points()

    def handle_decrement_mine_cost(self):
        self.race.decrement_mine_cost()
        self.mine_cost.update_value(self.race.mine_cost)
        self.update_advantage_points()

    def handle_increment_colonists_operate_mines(self):
        self.race.increment_colonists_operate_mines()
        self.colonists_operate_mines.update_value(
            self.race.colonists_operate_mines)
        self.update_advantage_points()

    def handle_decrement_colonists_operate_mines(self):
        self.race.decrement_colonists_operate_mines()
        self.colonists_operate_mines.update_value(
            self.race.colonists_operate_mines)
        self.update_advantage_points()

    def manage_navigation_state(self, new_index):
        prev_button = self.nav_buttons.button(self.PREVIOUS_BUTTON_ID)
        next_button = self.nav_buttons.button(self.NEXT_BUTTON_ID)

        self.tabbed_layout.setCurrentIndex(new_index)

        if(new_index == 0):
            prev_button.setEnabled(False)
            next_button.setEnabled(True)
        elif(new_index == 5):
            prev_button.setEnabled(True)
            next_button.setEnabled(False)
        else:
            prev_button.setEnabled(True)
            next_button.setEnabled(True)

    def create_race_general_details_page(self):
        page = QFrame()

        formLayout = QFormLayout()
        formLayout.addRow("Race Name:", self.race_name)
        formLayout.addRow("Plural Race Name:", self.plural_race_name)
        formLayout.addRow("Password:", self.password)

        base_race_group = helpers.build_button_group_box(
            self.base_races, "Predefined Race Templates", 2)

        leftover_box = QBoxLayout(QBoxLayout.TopToBottom)
        leftover_label = QLabel("Spend up to 50 leftover advantage points on:")
        leftover_box.addWidget(leftover_label)
        leftover_box.addWidget(self.leftover_points)

        arrow_container = QBoxLayout(QBoxLayout.LeftToRight)
        arrow_container.addWidget(self.previous_icon_button)
        arrow_container.addWidget(self.next_icon_button)

        race_icon_box = QBoxLayout(QBoxLayout.TopToBottom)
        self.manage_icon_state(self.current_race_icon)
        race_icon_box.addWidget(self.race_icon_label)
        race_icon_box.addLayout(arrow_container)

        bottom_container = QBoxLayout(QBoxLayout.LeftToRight)
        bottom_container.addLayout(leftover_box)
        bottom_container.addLayout(race_icon_box)

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addLayout(formLayout)
        layout.addStretch(1)
        layout.addWidget(base_race_group)
        layout.addStretch(1)
        layout.addLayout(bottom_container)

        page.setLayout(layout)
        return page

    def create_primary_trait_page(self):
        page = QFrame()

        prt_group = helpers.build_button_group_box(
            self.primary_racials, "Primary Racial Trait", 2)

        description_layout = QBoxLayout(QBoxLayout.TopToBottom)
        description_layout.addWidget(self.prt_desc)

        description_box = QGroupBox("Description of Trait")
        description_box.setLayout(description_layout)

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(prt_group)
        layout.addStretch(1)
        layout.addWidget(description_box)

        page.setLayout(layout)
        return page

    def create_lesser_trait_page(self):
        page = QFrame()

        lrt_group = helpers.build_button_group_box(
            self.lesser_racials, "Lesser Racial Trait", 2)

        description_layout = QBoxLayout(QBoxLayout.TopToBottom)
        description_layout.addWidget(self.lrt_desc)

        description_box = QGroupBox("Description of Trait")
        description_box.setLayout(description_layout)

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(lrt_group)
        layout.addStretch(1)
        layout.addWidget(description_box)

        page.setLayout(layout)
        return page

    def create_environmental_habitat_page(self):
        page = QFrame()
        layout = QBoxLayout(QBoxLayout.TopToBottom)

        temperature_layout = QBoxLayout(QBoxLayout.LeftToRight)
        lbl_0 = QLabel()
        lbl_0.setTextFormat(Qt.RichText)
        lbl_0.setText("<b>Temperature</b>")
        temperature_layout.addWidget(lbl_0)

        temp_panels = QBoxLayout(QBoxLayout.TopToBottom)
        top_temp_panel = QBoxLayout(QBoxLayout.LeftToRight)
        top_temp_panel.addWidget(self.decrement_temperature_midpoint)
        top_temp_panel.addWidget(self.temperature_slider)
        top_temp_panel.addWidget(self.increment_temperature_midpoint)

        bottom_temp_panel = QBoxLayout(QBoxLayout.LeftToRight)
        bottom_temp_panel.addWidget(self.increment_temperature_range)
        bottom_temp_panel.addWidget(self.temperature_immune)
        bottom_temp_panel.addWidget(self.decrement_temperature_range)

        temp_panels.addLayout(top_temp_panel)
        temp_panels.addLayout(bottom_temp_panel)
        temperature_layout.addLayout(temp_panels)

        temp_labels = QBoxLayout(QBoxLayout.TopToBottom)
        temp_labels.addWidget(self.temperature_min)
        lbl_1 = QLabel("to")
        lbl_1.setAlignment(Qt.AlignCenter)
        temp_labels.addWidget(lbl_1)
        temp_labels.addWidget(self.temperature_max)
        temp_labels.addStretch(1)

        temperature_layout.addLayout(temp_labels)

        layout.addLayout(temperature_layout)
        layout.addWidget(self.growth_rate)
        layout.addStretch(1)

        page.setLayout(layout)
        return page

    def create_economy_page(self):
        page = QFrame()

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(self.resource_production)
        layout.addWidget(self.factory_production)
        layout.addWidget(self.factory_cost)
        layout.addWidget(self.colonists_operate_factories)
        layout.addWidget(self.factory_cheap_germanium)
        layout.addWidget(self.mine_production)
        layout.addWidget(self.mine_cost)
        layout.addWidget(self.colonists_operate_mines)
        layout.addStretch(1)

        page.setLayout(layout)
        return page

    def create_research_cost_page(self):
        page = QFrame()

        energy_box = helpers.build_button_group_box(
            self.energy_research_cost, "Energy Research")

        weapons_box = helpers.build_button_group_box(
            self.weapons_research_cost, "Weapons Research")

        propulsion_box = helpers.build_button_group_box(
            self.propulsion_research_cost, "Propulsion Research")

        left_layout = QBoxLayout(QBoxLayout.TopToBottom)
        left_layout.addWidget(energy_box)
        left_layout.addWidget(weapons_box)
        left_layout.addWidget(propulsion_box)

        construction_box = helpers.build_button_group_box(
            self.construction_research_cost, "Construction Research")

        electronics_box = helpers.build_button_group_box(
            self.electronics_research_cost, "Electronics Research")

        biotech_box = helpers.build_button_group_box(
            self.biotech_research_cost, "Biotechnology Research")

        right_layout = QBoxLayout(QBoxLayout.TopToBottom)
        right_layout.addWidget(construction_box)
        right_layout.addWidget(electronics_box)
        right_layout.addWidget(biotech_box)

        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        full_layout = QBoxLayout(QBoxLayout.TopToBottom)
        full_layout.addLayout(layout)
        full_layout.addWidget(self.expensive_tech)

        page.setLayout(full_layout)
        return page
