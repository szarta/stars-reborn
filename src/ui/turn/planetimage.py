"""
    ui.turn.planetimage

    The widget for displaying planet image.

    :copyright: (c) 2015 by Brandon Arrendondo.
    :license: MIT, see LICENSE.txt for more details.
"""
import glob

from PySide.QtGui import QWidget
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QLabel
from PySide.QtGui import QFrame
from PySide.QtCore import Qt
from PySide.QtGui import QPixmap
from PySide.QtGui import QPushButton
from PySide.QtGui import QSpinBox
from PySide.QtGui import QIcon

from objects.planet import PlanetDataHistory

Hide_Arrow_Path = "resources/hide_arrow.png"


class PlanetImage(QWidget):

    def __init__(self, current_planet):
        super(PlanetImage, self).__init__()

        self.details_hidden = False

        self.planet_list = glob.glob("resources/planets/*.png")
        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")

        self.hide_button = QPushButton()
        self.hide_button.clicked.connect(self.hide_details)
        arrow_pixmap = QPixmap(Hide_Arrow_Path)
        arrow_icon = QIcon(arrow_pixmap)
        self.hide_button.setIcon(arrow_icon)
        self.hide_button.setIconSize(arrow_pixmap.rect().size())

        hide_button_frame = QFrame()
        hide_button_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        hide_button_layout = QBoxLayout(QBoxLayout.LeftToRight)
        hide_button_layout.setContentsMargins(0, 0, 0, 0)
        hide_button_layout.setSpacing(0)
        hide_button_layout.addWidget(self.hide_button)
        hide_button_frame.setLayout(hide_button_layout)

        planet_name_layout = QBoxLayout(QBoxLayout.LeftToRight)

        self.planet_name = QLabel()
        self.planet_name.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.planet_name.setAlignment(Qt.AlignCenter)
        planet_name_layout.addWidget(self.planet_name, 1)
        planet_name_layout.addWidget(hide_button_frame)


        self.planet_picture = QLabel()
        self.planet_picture.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        self.hideable_widget = QFrame()
        self.hideable_widget.setFrameStyle(QFrame.Panel | QFrame.Raised)
        
        side_layout = QBoxLayout(QBoxLayout.LeftToRight)
        side_layout.addStretch(1)
        side_layout.addWidget(self.planet_picture)
        
        button_layout = QBoxLayout(QBoxLayout.TopToBottom)
        button_layout.addWidget(self.previous_button)
        button_layout.addWidget(self.next_button)
        button_layout.addStretch(1)
        side_layout.addLayout(button_layout)
        side_layout.addStretch(1)
        self.hideable_widget.setLayout(side_layout)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        main_layout.setSpacing(0)
        main_layout.addLayout(planet_name_layout)
        main_layout.addWidget(self.hideable_widget)
        main_layout.addStretch(1)

        self.update_planet(current_planet)
        self.setLayout(main_layout)

    def hide_details(self):
        if(self.details_hidden):
            self.hideable_widget.show()
            self.details_hidden = False
        else:
            self.hideable_widget.hide()
            self.details_hidden = True

    def update_planet(self, planet):
        self.planet_name.setText(planet.name)

        planet_image = self.planet_list[(planet.id % len(self.planet_list))]
        self.planet_picture.setPixmap(
            QPixmap(planet_image))
