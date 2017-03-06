"""
    ui.turn.hideablepane

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from PySide.QtGui import QWidget
from PySide.QtGui import QPushButton
from PySide.QtGui import QPixmap
from PySide.QtGui import QIcon
from PySide.QtGui import QFrame
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QLabel
from PySide.QtCore import Qt

from src.model.enumerations import ResourcePaths


class HideablePane(QWidget):

    def __init__(self):
        super(HideablePane, self).__init__()

        self.details_hidden = False

        self.hide_button = QPushButton()
        self.hide_button.clicked.connect(self.hide_details)
        arrow_pixmap = QPixmap(ResourcePaths.HideArrowPath)
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

        title_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.title_label = QLabel()
        self.title_label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.title_label, 1)
        title_layout.addWidget(hide_button_frame)

        self.hideable_widget = QFrame()
        self.hideable_widget.setFrameStyle(QFrame.Panel | QFrame.Raised)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        main_layout.setSpacing(0)
        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.hideable_widget)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def hide_details(self):
        if(self.details_hidden):
            self.hideable_widget.show()
            self.details_hidden = False
        else:
            self.hideable_widget.hide()
            self.details_hidden = True

    def set_title(self, new_title):
        self.title_label.setText(new_title)

    def update_hideable_pane(self, new_layout):
        if self.hideable_widget.layout():
            dummy_widget = QLabel()
            old_layout = self.hideable_widget.layout()
            dummy_widget.setLayout(old_layout)

        self.hideable_widget.setLayout(new_layout)
