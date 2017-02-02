"""
    ui.dialogs.game

    Contains all the data and capabilities needed for new game creation.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from PySide.QtGui import QDialog
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QStackedLayout
from PySide.QtGui import QGroupBox
from PySide.QtGui import QComboBox
from PySide.QtGui import QTextEdit
from PySide.QtGui import QLineEdit
from PySide.QtGui import QLabel
from PySide.QtGui import QFrame
from PySide.QtCore import Qt

from src.model.enumerations import GameDifficulty
from src.model.enumerations import UniverseSize
from src.model.enumerations import DensityLevel

from src.model.enumerations import PredefinedRaces
from src.ui import helpers

from src.data import Language_Map


class NewBasicGameButtons:
    CreateGame = 0
    Cancel = 1
    Help = 2
    AdvancedGame = 3
    BeginTutorial = 4


class NewBasicGameDialog(QDialog):
    """
        The main dialog for new game creation.

        New game creation is separated into two separate dialogs.  One is for
        basic game setup with many of the options fixed for beginning players.
        The other is an advanced game setup with many of the options
        configurable.

        This dialog is the basic game setup dialog and is capable of launching
        the advanced game setup dialog via button, which will close this
        dialog and open that one.

        The game tutorial can also be launched from this dialog.
    """
    def __init__(self, parent=None):
        super(NewBasicGameDialog, self).__init__(parent)

        self.launch_advanced_game = False
        self.begin_tutorial = False

        self.init_user_controls()
        self.init_ui()
        self.bind_user_controls()

    def init_user_controls(self):
        buttons = [
            Language_Map["ui"]["general"]["create-game"],
            Language_Map["ui"]["general"]["cancel"],
            Language_Map["ui"]["general"]["help"],
            Language_Map["ui"]["general"]["advanced-game"],
            Language_Map["ui"]["general"]["begin-tutorial"]
        ]

        self.push_buttons = helpers.build_push_button_group(buttons)

        self.race_desc = QTextEdit()
        self.race_desc.setFixedHeight(135)
        self.race_desc.setReadOnly(True)

        race_selection_arr = [
            x.title() for x in Language_Map["predefined-race-singular-names"]]

        race_selection_arr.append(
            Language_Map["random"].title())

        self.race_combo = QComboBox()
        self.race_combo.addItems(race_selection_arr)
        self.race_combo.setCurrentIndex(PredefinedRaces.Default)

        self.handle_race_combo()

        self.difficulties = helpers.build_radio_group(
            [x.title() for x in Language_Map["difficulty-levels"]])

        self.difficulties.button(
            GameDifficulty.Default).setChecked(True)

        self.universe_sizes = helpers.build_radio_group(
            [x.title() for x in Language_Map["universe-sizes"]])

        self.universe_sizes.button(UniverseSize.Default).setChecked(True)

    def bind_user_controls(self):
        self.push_buttons.buttonClicked.connect(self.handle_button_clicked)
        self.race_combo.currentIndexChanged.connect(self.handle_race_combo)

    def init_ui(self):
        self.setWindowTitle(
            Language_Map["ui"]["new-game"]["title"])

        difficulty_group = \
            helpers.build_button_group_box(
                self.difficulties,
                Language_Map["ui"]["new-game"]["difficulty-level-title"])

        universe_size_group = \
            helpers.build_button_group_box(
                self.universe_sizes,
                Language_Map["ui"]["new-game"]["universe-size-title"])

        left_layout = QBoxLayout(QBoxLayout.TopToBottom)
        left_layout.addWidget(difficulty_group)
        left_layout.addStretch(1)
        left_layout.addWidget(universe_size_group)

        player_race_box = QBoxLayout(QBoxLayout.TopToBottom)
        player_race_group = QGroupBox("Player Race")
        player_race_box.addWidget(self.race_combo)
        player_race_box.addWidget(self.race_desc)
        player_race_group.setLayout(player_race_box)

        advanced_game_box = QBoxLayout(QBoxLayout.TopToBottom)
        advanced_game_group = QGroupBox(
            Language_Map["ui"]["new-game"]["advanced-game-title"])

        advanced_game_description = "<p>{0}</p>".format(
            Language_Map["ui"]["new-game"]["advanced-game-description"])

        advanced_game_label = QTextEdit(advanced_game_description)
        advanced_game_label.setFixedHeight(75)
        advanced_game_label.setReadOnly(True)

        advanced_game_box.addWidget(advanced_game_label)
        advanced_game_box.addWidget(
            self.push_buttons.button(NewBasicGameButtons.AdvancedGame))

        advanced_game_group.setLayout(advanced_game_box)

        right_layout = QBoxLayout(QBoxLayout.TopToBottom)
        right_layout.addWidget(player_race_group)
        right_layout.addWidget(advanced_game_group)

        side_layouts = QBoxLayout(QBoxLayout.LeftToRight)
        side_layouts.addLayout(left_layout)
        side_layouts.addLayout(right_layout)

        button_layout = QBoxLayout(QBoxLayout.LeftToRight)
        button_layout.addWidget(
            self.push_buttons.button(NewBasicGameButtons.Help))

        button_layout.addWidget(
            self.push_buttons.button(NewBasicGameButtons.BeginTutorial))

        button_layout.addStretch(1)
        button_layout.addWidget(
            self.push_buttons.button(NewBasicGameButtons.CreateGame))

        button_layout.addWidget(
            self.push_buttons.button(NewBasicGameButtons.Cancel))

        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        main_layout.addLayout(side_layouts)
        main_layout.addLayout(button_layout)

    def handle_race_combo(self):
        selectedIndex = self.race_combo.currentIndex()

        if selectedIndex < len(Language_Map["predefined-race-singular-names"]):
            self.race_desc.setHtml(
                Language_Map["predefined-race-descriptions"][selectedIndex])
        else:
            self.race_desc.setHtml("<p />")

    def handle_button_clicked(self, button):
        button_id = self.push_buttons.id(button)
        if(button_id == NewBasicGameButtons.Help):
            print "help!"
        elif(button_id == NewBasicGameButtons.Cancel):
            self.reject()
        else:
            usize = self.universe_sizes.checkedId()
            difficulty = self.difficulties.checkedId()

            if(button_id == NewBasicGameButtons.AdvancedGame):
                self.launch_advanced_game = True
            elif(button_id == NewBasicGameButtons.BeginTutorial):
                self.begin_tutorial = True

            self.accept()


class NewAdvancedGameDialog(QDialog):
    """
        The advanced dialog for new game creation.

        New game creation is separated into two separate dialogs.  One is for
        basic game setup with many of the options fixed for beginning players.
        The other is an advanced game setup with many of the options
        configurable.

        This dialog is the advanced game setup dialog - a multi-page wizard.
        Advanced setup allows for configuration of the following game settings:

        Tab 1: Game Setup
            - Game name
            - Options for:
                - Slower tech advances
                - Accelerated play
                - Random events
                - Computer player alliances
                - Public player scores

        Tab 2: Player Setup
            Player setup - number and types of players

        Tab 3: Universe Setup
            - Custom universe via Universe import
            - Player positioning
            - Galaxy clumping
            - Universe density
            - Preview universe

        Tab 4: Victory Conditions
            Victory conditions
    """
    PREVIOUS_BUTTON_ID = 0
    NEXT_BUTTON_ID = 1
    CANCEL_BUTTON_ID = 2
    IMPORT_BUTTON_ID = 3
    EXPORT_BUTTON_ID = 4
    CREATE_BUTTON_ID = 5

    def __init__(self, parent=None):
        super(NewAdvancedGameDialog, self).__init__(parent)

        self.init_user_controls()
        self.init_ui()
        self.bind_user_controls()

    def init_user_controls(self):
        """
        Sets up all important user controls on this form.
        """
        self.game_name_field = QLineEdit()

        buttons = [
            "&Previous",
            "&Next",
            "&Cancel",
            "&Import",
            "&Export",
            "C&reate Game"
        ]

        self.nav_buttons = helpers.build_push_button_group(buttons)

        checks = list(Language_Map["gameplay-option-names"])
        self.game_options = helpers.build_checkbox_group(checks)
        self.game_options.setExclusive(False)
        self.setup_game_options_state()

        self.densities = helpers.build_radio_group(
            Language_Map["density-levels"])

        self.densities.button(DensityLevel.Default).setChecked(True)

        self.tabbed_layout = QStackedLayout()

    def bind_user_controls(self):
        """
        Binds all user controls used by this form to their handlers.
        """
        self.nav_buttons.buttonClicked.connect(self.handle_nav_button)

    def init_ui(self):
        """
        Builds up the user interface - laying out the user controls on this
        form, any relevant tabbed frames, titles, icons, etc.
        """
        self.setWindowTitle("Advanced Game Creation")

        self.tabbed_layout.addWidget(self.create_game_setup_page())
        self.tabbed_layout.addWidget(self.create_player_setup_page())
        self.manage_navigation_state(0)

        button_layout = QBoxLayout(QBoxLayout.LeftToRight)
        button_layout.addWidget(self.nav_buttons.button(self.IMPORT_BUTTON_ID))
        button_layout.addWidget(self.nav_buttons.button(self.EXPORT_BUTTON_ID))
        button_layout.addStretch(1)
        button_layout.addWidget(
            self.nav_buttons.button(self.PREVIOUS_BUTTON_ID))

        button_layout.addWidget(self.nav_buttons.button(self.NEXT_BUTTON_ID))
        button_layout.addStretch(1)
        button_layout.addWidget(self.nav_buttons.button(self.CANCEL_BUTTON_ID))
        button_layout.addWidget(self.nav_buttons.button(self.CREATE_BUTTON_ID))

        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        main_layout.addLayout(self.tabbed_layout)
        main_layout.addLayout(button_layout)

    def handle_nav_button(self, button):
        button_id = self.nav_buttons.id(button)

        if(button_id == self.NEXT_BUTTON_ID):
            new_index = self.tabbed_layout.currentIndex() + 1
            self.manage_navigation_state(new_index)
        elif(button_id == self.PREVIOUS_BUTTON_ID):
            new_index = self.tabbed_layout.currentIndex() - 1
            self.manage_navigation_state(new_index)
        elif(button_id == self.CANCEL_BUTTON_ID):
            self.reject()
        else:
            print "some other button"

    def manage_navigation_state(self, new_index):
        prev_button = self.nav_buttons.button(self.PREVIOUS_BUTTON_ID)
        next_button = self.nav_buttons.button(self.NEXT_BUTTON_ID)

        self.tabbed_layout.setCurrentIndex(new_index)

        if(new_index == 0):
            prev_button.setEnabled(False)
            next_button.setEnabled(True)
        elif(new_index == 2):
            prev_button.setEnabled(True)
            next_button.setEnabled(False)
        else:
            prev_button.setEnabled(True)
            next_button.setEnabled(True)

    def handle_create_game(self):
        """
        Return success on the dialog.
        """
        self.accept()

    def setup_game_options_state(self):

        settings = GameplayOptionsContainer
        check_boxes = self.game_options.buttons()

        action_map = [
            (settings.beginner_minerals,
                check_boxes[GameplayOptions.Beginner_Minerals]),

            (settings.accelerated_play,
                check_boxes[GameplayOptions.Accelerated_Play]),

            (settings.slow_tech,
                check_boxes[GameplayOptions.Slow_Tech]),

            (settings.random_events,
                check_boxes[GameplayOptions.Random_Events]),

            (settings.public_scores,
                check_boxes[GameplayOptions.Public_Scores]),

            (settings.cpu_alliances,
                check_boxes[GameplayOptions.Computer_Alliances])
        ]

        for (game_condition, check_box) in action_map:
            if game_condition:
                check_box.setCheckState(Qt.Checked)
            else:
                check_box.setCheckState(Qt.Unchecked)

    def create_game_setup_page(self):
        page = QFrame()

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        game_name_layout = QBoxLayout(QBoxLayout.LeftToRight)
        game_name_layout.addWidget(QLabel("Game Name:"))
        game_name_layout.addWidget(self.game_name_field)
        layout.addLayout(game_name_layout)

        options_group = \
            helpers.build_button_group_box(self.game_options, "Game Options:")

        layout.addWidget(options_group)

        page.setLayout(layout)
        return page

    def create_player_setup_page(self):
        page = QFrame()

        layout = QBoxLayout(QBoxLayout.TopToBottom)

        density_group = \
            helpers.build_button_group_box(self.densities, "Universe Density:")

        layout.addWidget(density_group)

        page.setLayout(layout)
        return page
