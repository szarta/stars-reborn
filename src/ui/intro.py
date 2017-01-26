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
from PySide.QtGui import QLabel
from PySide.QtGui import QPixmap
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QMessageBox
from PySide.QtGui import QPalette
from PySide.QtCore import Qt

from dialogs import about
from dialogs import technology_browser

from src.model.enumerations import ResourcePaths
#from dialogs import game
#from dialogs import race

#from turn import editor

#from generators.game import generate_tutorial
#from parameters.game import Tutorial_Game_Name
#from parameters.game import Save_Game_Path


class IntroUI(QDialog):
    def __init__(self):
        super(IntroUI, self).__init__()

        self.init_user_controls()
        self.init_ui()
        self.bind_user_controls()
        self.main_editor = None

    def init_user_controls(self):
        self.new_game_button = QPushButton("&New Game")
        self.load_game_button = QPushButton("&Load Game")
        self.universe_button = QPushButton("&Universe Editor")
        self.race_editor_button = QPushButton("&Race Editor")
        self.about_button = QPushButton("&About")
        self.exit_button = QPushButton("E&xit")

    def bind_user_controls(self):
        self.new_game_button.clicked.connect(self.new_game_handler)
        self.load_game_button.clicked.connect(self.load_game_handler)
        self.universe_button.clicked.connect(self.universe_handler)
        self.race_editor_button.clicked.connect(self.race_editor_handler)
        self.about_button.clicked.connect(self.about_handler)
        self.exit_button.clicked.connect(self.exit_handler)

    def init_ui(self):
        self.setWindowTitle("Stars Reborn")
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
        player = None
        tech_browser = technology_browser.TechnologyBrowser(player)
        tech_browser.exec_()
        """
        new_game_dialog = game.NewBasicGameDialog(self)
        success = new_game_dialog.exec_()
        if(success):
            if(new_game_dialog.begin_tutorial):
                tutorial_path = "{0}/{1}.xy".format(
                    Save_Game_Path, Tutorial_Game_Name)

                if(os.path.exists(tutorial_path)):
                    msgbox = QMessageBox()
                    msgbox.setText("The tutorial has been run before.")
                    msgbox.setInformativeText("Would you like to destroy that game and start at the beginning?")
                    msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msgbox.setDefaultButton(QMessageBox.Yes)
                    ret = msgbox.exec_()

                    if(ret == QMessageBox.No):
                        return

                generate_tutorial()

                player_turn_file = "{0}/{1}.m0".format(
                    Save_Game_Path, Tutorial_Game_Name)

                self.main_editor = editor.CoreUI(player_turn_file)
                self.main_editor.show()
                self.hide()

            elif(new_game_dialog.launch_advanced_game):
                advanced_game_dialog = game.NewAdvancedGameDialog(self)
                success = advanced_game_dialog.exec_()
                if(success):
                    print "Launch advanced game!"

            else:
        """

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
