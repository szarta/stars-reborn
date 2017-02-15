"""
    intro.py

    This is the first UI screen the user sees.  It drives into:
        * Game creation
        * Game loading
        * About dialog

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import os

from PySide.QtGui import QDialog
from PySide.QtGui import QPixmap
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QMessageBox
from PySide.QtGui import QPalette

from dialogs import about

from src.model.enumerations import ResourcePaths
from src.model.enumerations import TutorialGameName
from dialogs import game
#from dialogs import race

from turn import editor

from src.data import load_tutorial_game
from src.data import Language_Map
from src.model.turn import generate_turn_zero


class IntroUI(QDialog):
    def __init__(self):
        super(IntroUI, self).__init__()

        self.init_user_controls()
        self.init_ui()
        self.bind_user_controls()
        self.main_editor = None

    def init_user_controls(self):
        self.new_game_button = QPushButton(
            Language_Map["ui"]["general"]["new-game"])

        self.load_game_button = QPushButton(
            Language_Map["ui"]["general"]["load-game"])

        self.universe_button = QPushButton("&Universe Editor")
        self.race_editor_button = QPushButton("&Race Editor")
        self.about_button = QPushButton(
            Language_Map["ui"]["general"]["about"])

        self.exit_button = QPushButton(
            Language_Map["ui"]["general"]["exit"])

    def bind_user_controls(self):
        self.new_game_button.clicked.connect(self.new_game_handler)
        self.load_game_button.clicked.connect(self.load_game_handler)
        self.universe_button.clicked.connect(self.universe_handler)
        self.race_editor_button.clicked.connect(self.race_editor_handler)
        self.about_button.clicked.connect(self.about_handler)
        self.exit_button.clicked.connect(self.exit_handler)

    def init_ui(self):
        self.setWindowTitle(
            Language_Map["game-name"])

        self.setGeometry(200, 200, 768, 768)
        self.setFixedSize(768, 768)

        palette = self.palette()
        bg = QPixmap(ResourcePaths.IntroLogo)
        palette.setBrush(QPalette.Background, bg)
        self.setPalette(palette)

        background_layout = QBoxLayout(QBoxLayout.LeftToRight)

        button_layout = QBoxLayout(QBoxLayout.TopToBottom)
        button_layout.addWidget(self.new_game_button)
        button_layout.addWidget(self.load_game_button)
        button_layout.addWidget(self.universe_button)
        button_layout.addWidget(self.race_editor_button)
        button_layout.addWidget(self.about_button)
        button_layout.addWidget(self.exit_button)

        background_layout.addLayout(button_layout)
        background_layout.addStretch(1)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        main_layout.addLayout(background_layout)

    def new_game_handler(self):
        #player = None
        #tech_browser = technology_browser.TechnologyBrowser(player)
        #tech_browser.exec_()
        new_game_dialog = game.NewBasicGameDialog(self)
        success = new_game_dialog.exec_()
        if(success):
            if(new_game_dialog.begin_tutorial):
                tutorial_path = "{0}/{1}.xy".format(
                    ResourcePaths.SaveGamePath, TutorialGameName)

                if(os.path.exists(tutorial_path)):
                    msgbox = QMessageBox()
                    msgbox.setText(
                        Language_Map["ui"]["intro"]["tutorial-run-before-text"])
                    msgbox.setInformativeText(
                        Language_Map["ui"]["intro"]["tutorial-run-before-informative"])
                    msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msgbox.setDefaultButton(QMessageBox.Yes)
                    ret = msgbox.exec_()

                    if(ret == QMessageBox.No):
                        return

                generate_turn_zero(
                    load_tutorial_game(ResourcePaths.TutorialData),
                    ResourcePaths.SaveGamePath)

                player_turn_file = "{0}/{1}.m0".format(
                    ResourcePaths.SaveGamePath, TutorialGameName)

                self.main_editor = editor.CoreUI(player_turn_file)
                self.main_editor.show()
                self.hide()

            elif(new_game_dialog.launch_advanced_game):
                print "Launch advanced game!"
                #advanced_game_dialog = game.NewAdvancedGameDialog(self)
                #success = advanced_game_dialog.exec_()
                #if(success):
                #    print "Launch advanced game!"

            else:
                print "New game!"

    def load_game_handler(self):
        print "Load game!"

    def universe_handler(self):
        print "Universe Editor!"

    def race_editor_handler(self):
        #race_edit_dialog = race.RaceWizard(self)
        #race_edit_dialog.exec_()
        print "Race dialog!"

    def about_handler(self):
        about_dialog = about.AboutDialog()
        about_dialog.exec_()

    def exit_handler(self):
        self.close()
