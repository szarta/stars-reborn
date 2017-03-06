"""
    ui.turn.statuspane

    Status pane widgets for the turn editor.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import glob
import math

from PySide.QtGui import QWidget
from PySide.QtGui import QPushButton
from PySide.QtGui import QPixmap
from PySide.QtGui import QFrame
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QLabel

from src.ui.turn.hideablepane import HideablePane

from src.model.enumerations import ResourcePaths
from src.model.enumerations import Minerals
from src.model.enumerations import Installations
from src.model.enumerations import PrimaryRacialTrait
from src.data import Language_Map


class PlanetImage(QWidget):

    def __init__(self):
        super(PlanetImage, self).__init__()

        self.hideable_pane = HideablePane()

        self.planet_list = glob.glob("{0}/*.png".format(
            ResourcePaths.PlanetsPath))

        self.previous_button = QPushButton(
            Language_Map["ui"]["general"]["previous"])

        self.next_button = QPushButton(
            Language_Map["ui"]["general"]["next"])

        self.planet_picture = QLabel()
        self.planet_picture.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        side_layout = QBoxLayout(QBoxLayout.LeftToRight)
        side_layout.addStretch(1)
        side_layout.addWidget(self.planet_picture)

        button_layout = QBoxLayout(QBoxLayout.TopToBottom)
        button_layout.addWidget(self.previous_button)
        button_layout.addWidget(self.next_button)
        button_layout.addStretch(1)
        side_layout.addLayout(button_layout)
        side_layout.addStretch(1)

        self.hideable_pane.update_hideable_pane(side_layout)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        main_layout.addWidget(self.hideable_pane)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

    def update_planet(self, planet):
        self.hideable_pane.set_title(planet.name)
        planet_image = self.planet_list[(planet.id % len(self.planet_list))]
        self.planet_picture.setPixmap(QPixmap(planet_image))


class MineralsOnHand(QWidget):

    def __init__(self, player):
        super(MineralsOnHand, self).__init__()

        self.player = player
        self.hideable_pane = HideablePane()

        overall_layout = QBoxLayout(QBoxLayout.TopToBottom)

        combined_layout = QBoxLayout(QBoxLayout.LeftToRight)

        label_layout = QBoxLayout(QBoxLayout.TopToBottom)
        ironium_label = QLabel("<b>{0}</b>".format(
            Language_Map["minerals"][Minerals.Ironium].title()))
        ironium_label.setStyleSheet("QLabel { color: #0000ff }")

        boranium_label = QLabel("<b>{0}</b>".format(
            Language_Map["minerals"][Minerals.Boranium].title()))
        boranium_label.setStyleSheet("QLabel { color: #008000 }")

        germanium_label = QLabel("<b>{0}</b>".format(
            Language_Map["minerals"][Minerals.Germanium].title()))
        germanium_label.setStyleSheet("QLabel { color: #ffff00 }")

        label_layout.addWidget(ironium_label)
        label_layout.addWidget(boranium_label)
        label_layout.addWidget(germanium_label)

        details_layout = QBoxLayout(QBoxLayout.TopToBottom)

        self.ironium_value = QLabel()
        self.boranium_value = QLabel()
        self.germanium_value = QLabel()

        details_layout.addWidget(self.ironium_value)
        details_layout.addWidget(self.boranium_value)
        details_layout.addWidget(self.germanium_value)

        combined_layout.addLayout(label_layout)
        combined_layout.addStretch(1)
        combined_layout.addLayout(details_layout)

        overall_layout.addLayout(combined_layout)

        header_line = QFrame()
        header_line.setFrameStyle(QFrame.HLine)
        overall_layout.addWidget(header_line)

        combined_layout2 = QBoxLayout(QBoxLayout.LeftToRight)

        label_layout2 = QBoxLayout(QBoxLayout.TopToBottom)
        label_layout2.addWidget(QLabel("<b>{0}</b>".format(
            Language_Map["installations"][Installations.Mines])))

        label_layout2.addWidget(QLabel("<b>{0}</b>".format(
            Language_Map["installations"][Installations.Factories])))

        self.mine_value = QLabel()
        self.factory_value = QLabel()

        details_layout2 = QBoxLayout(QBoxLayout.TopToBottom)
        details_layout2.addWidget(self.mine_value)
        details_layout2.addWidget(self.factory_value)

        combined_layout2.addLayout(label_layout2)
        combined_layout2.addStretch(1)
        combined_layout2.addLayout(details_layout2)

        overall_layout.addLayout(combined_layout2)

        self.hideable_pane.set_title(
            Language_Map["ui"]["editor"]["minerals-on-hand"])

        self.hideable_pane.update_hideable_pane(overall_layout)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        main_layout.addWidget(self.hideable_pane)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

    def update_planet(self, planet):
        self.ironium_value.setText("{0!s}kT".format(
            planet.surface_ironium))

        self.boranium_value.setText("{0!s}kT".format(
            planet.surface_boranium))

        self.germanium_value.setText("{0!s}kT".format(
            planet.surface_germanium))

        prt = self.player.race.primary_racial_trait
        if prt == PrimaryRacialTrait.AlternateReality:
            self.mine_value.setText("{0!s}*".format(
                int(math.sqrt(planet.population) / 10)))

            self.factory_value.setText("n/a")
        else:
            self.mine_value.setText("{0!s}".format(
                planet.mines))

            self.factory_value.setText("{0!s}".format(
                planet.factories))
