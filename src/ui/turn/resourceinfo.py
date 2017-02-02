"""
    resourceinfo.py

    The widget for displaying planet resource info.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QLabel
from PySide.QtGui import QFrame
from PySide.QtGui import QPixmap
from PySide.QtCore import Qt

from src.model.enumerations import ResourcePaths
from src.model.enumerations import NeverSeenPlanet


class PlanetInfo(QWidget):
    def __init__(self, planet, race):
        super(PlanetInfo, self).__init__()
        self.race = race
        main_layout = QBoxLayout(QBoxLayout.TopToBottom)

        self.planet_name = QLabel()
        self.planet_name.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.planet_name.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.planet_name)

        self.planet_details = QWidget()
        planet_details_layout = QBoxLayout(QBoxLayout.TopToBottom)
        first_pane = QBoxLayout(QBoxLayout.LeftToRight)

        self.planet_value = QLabel()
        self.report_age = QLabel()

        info_box = QBoxLayout(QBoxLayout.TopToBottom)
        info_box.addWidget(self.planet_value)
        info_box.addWidget(self.report_age)

        self.population = QLabel()

        first_pane.addLayout(info_box)
        first_pane.addStretch(1)
        first_pane.addWidget(self.population)

        planet_details_layout.addLayout(first_pane)
        self.planet_details.setLayout(planet_details_layout)

        main_layout.addWidget(self.planet_details)

        self.unknown_planet_label = QLabel()
        self.unknown_planet_label.setAlignment(Qt.AlignCenter)
        self.unknown_planet_label.setPixmap(
            QPixmap(ResourcePaths.UnknownPlanetPath))

        main_layout.addWidget(self.unknown_planet_label)

        self.update_planet(planet)
        self.setLayout(main_layout)

    def update_planet(self, planet):
        self.target_planet = planet
        summary_text = '<font size="10pt">{0} Summary</font>'.format(
            self.target_planet.name)

        self.planet_name.setText(summary_text)
        if(planet.years_since == NeverSeenPlanet):
            self.unknown_planet_label.show()
            self.planet_details.hide()
        else:
            value = self.target_planet.calculate_value(self.race)
            color = "red"
            if(value > 0):
                color = "green"

            val_txt = '<font size="8pt">Value:  </font>'
            val_txt += '<font size="8pt" color="{0}">{1!s}%</font>'.format(
                color, value)
            self.planet_value.setText(val_txt)

            since = ""
            if(self.target_planet.years_since > 0):
                since = '<font size="8pt" color="red">{0}</font>'.format(
                    'Report is {0} years old'.format(
                        self.target_planet.years_since))

            else:
                since = '<font size="8pt">{0}</font>'.format(
                    "Report is current")

            self.report_age.setText(since)

            pop = ""
            if(self.target_planet.population == 0):
                pop = '<font size="8pt">Uninhabited</font>'
            else:
                pop = '<font size="8pt">Population:  {0!s}</font>'.format(
                    self.target_planet.population)

            self.population.setText(pop)

            self.unknown_planet_label.hide()
            self.planet_details.show()
