"""
    research.py

    Allows the user to look at current research status and select the current
    field of study.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.TXT for more details.
"""
from PySide.QtGui import QDialog
from PySide.QtGui import QLabel
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QButtonGroup
from PySide.QtGui import QComboBox
from PySide.QtGui import QRadioButton
from PySide.QtGui import QGroupBox

from PySide.QtGui import QFrame
from PySide.QtGui import QPixmap
from PySide.QtCore import Qt

from src.data import Language_Map
from src.data import Technologies

from src.model.technology import calculate_next_n_techs


class ResearchDialog(QDialog):
    def __init__(self, player, slow_tech, parent=None):
        super(ResearchDialog, self).__init__(parent)

        self.player = player
        self.slow_tech = slow_tech

        self.current_field = player.current_research_field
        self.next_field = player.next_research_field
        self.budgeted_resources = player.research_budget

        self.next_field_selection_array = [
            Language_Map["ui"]["research"]["same-field"]
        ]

        self.next_field_selection_array.extend(
            [x.title() for x in Language_Map["research-areas"]]
        )

        self.next_field_selection_array.append(
            Language_Map["ui"]["research"]["lowest-field"]
        )

        self.init_user_controls()
        self.init_ui()
        self.bind_user_controls()

    def init_user_controls(self):
        self.done_button = QPushButton(Language_Map["ui"]["general"]["done"])
        self.help_button = QPushButton(Language_Map["ui"]["general"]["help"])

        self.next_field_combo = QComboBox()
        self.next_field_combo.addItems(self.next_field_selection_array)

        self.research_area = QButtonGroup()

        self.current_research_label = QLabel()
        self.resources_needed_label = QLabel()

        button_id = 0
        for ra in Language_Map["research-areas"]:
            rb = QRadioButton(ra.title())
            self.research_area.addButton(rb, button_id)
            button_id += 1

    def bind_user_controls(self):
        self.done_button.clicked.connect(self.close_window)
        self.help_button.clicked.connect(self.do_help)
        self.research_area.buttonClicked.connect(self.handle_research_area_clicked)

    def init_ui(self):
        self.setWindowTitle(
            Language_Map["ui"]["research"]["title"])

        self.setGeometry(200, 200, 525, 460)

        tech_status = QGroupBox(
            Language_Map["ui"]["research"]["technology-status"])

        tech_status_layout = QBoxLayout(QBoxLayout.TopToBottom)
        header_layout = QBoxLayout(QBoxLayout.LeftToRight)
        header_layout.addWidget(
            QLabel("{0}".format(
                Language_Map["ui"]["research"]["field-of-study"])))

        header_layout.addStretch(1)

        current_level_label = QLabel()
        current_level_label.setText(
            Language_Map["ui"]["research"]["current-level"].replace(" ", "\n"))
        current_level_label.setWordWrap(True)
        current_level_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(current_level_label)

        header_line = QFrame()
        header_line.setFrameStyle(QFrame.HLine)

        research_areas_layout = QBoxLayout(QBoxLayout.TopToBottom)

        rl = self.player.get_tech_level_array()

        for i in xrange(len(self.research_area.buttons())):
            l = QBoxLayout(QBoxLayout.LeftToRight)
            l.addWidget(self.research_area.buttons()[i])
            l.addStretch()
            l.addWidget(QLabel("  {0!s}  ".format(rl[i])))
            research_areas_layout.addLayout(l)

        self.research_area.buttons()[self.current_field].setChecked(True)

        tech_status_layout.addLayout(header_layout)
        tech_status_layout.addWidget(header_line)
        tech_status_layout.addStretch(1)
        tech_status_layout.addLayout(research_areas_layout)
        tech_status.setLayout(tech_status_layout)

        self.expected_benefits = QGroupBox(
            Language_Map["ui"]["research"]["expected-benefits"])

        left_layout = QBoxLayout(QBoxLayout.TopToBottom)
        left_layout.addWidget(tech_status)
        left_layout.addStretch(1)
        left_layout.addWidget(self.expected_benefits)

        currently_researching = QGroupBox(
            Language_Map["ui"]["research"]["currently-researching"])

        researching_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.current_research_label.setAlignment(Qt.AlignCenter)
        self.resources_needed_label.setAlignment(Qt.AlignCenter)

        researching_layout.addWidget(self.current_research_label)
        researching_layout.addWidget(self.resources_needed_label)

        currently_researching.setLayout(researching_layout)

        right_layout = QBoxLayout(QBoxLayout.TopToBottom)
        right_layout.addWidget(currently_researching)

        center_layout = QBoxLayout(QBoxLayout.LeftToRight)
        center_layout.addLayout(left_layout)
        center_layout.addStretch(1)
        center_layout.addLayout(right_layout)

        bottom_layout = QBoxLayout(QBoxLayout.LeftToRight)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.done_button)
        bottom_layout.addWidget(self.help_button)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)
        main_layout.addLayout(center_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(bottom_layout)

        self.handle_research_area_clicked(
            self.research_area.buttons()[self.current_field])

    def handle_research_area_clicked(self, radio_button):
        index = self.research_area.buttons().index(radio_button)
        self.current_field = index

        rl = self.player.get_tech_level_array()

        self.current_research_label.setText("{0}, {1} {2!s}".format(
            Language_Map["research-areas"][self.current_field].title(),
            Language_Map["ui"]["research"]["tech-level"],
            rl[self.current_field]))

        self.resources_needed_label.setText("{0}:  {1}".format(
            Language_Map["ui"]["research"]["resources-needed"],
            self.player.research_resources_needed[self.current_field]))

        if self.expected_benefits.layout():
            dummy_widget = QLabel()
            old_layout = self.expected_benefits.layout()
            dummy_widget.setLayout(old_layout)

        expected_benefits_layout = QBoxLayout(QBoxLayout.TopToBottom)

        next_benefits = calculate_next_n_techs(
            self.player, self.current_field, 6, 7)

        for tech_id in next_benefits:
            tech = Technologies[tech_id]
            tech_name = Language_Map["technology-names"][tech_id]

            l = QLabel()
            l.setText(tech_name)

            diff = tech.requirements[self.current_field] - rl[self.current_field]
            if diff == 1:
                l.setStyleSheet("QLabel { color: #008000 }")
            elif diff < 5:
                l.setStyleSheet("QLabel { color: #000081 }")

            expected_benefits_layout.addWidget(l)

        self.expected_benefits.setLayout(expected_benefits_layout)

    def close_window(self):
        self.accept()

    def do_help(self):
        print "Help!"
