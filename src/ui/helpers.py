"""
    ui.helpers

    Contains methods commonly used across multiple UIs.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
from PySide.QtGui import QButtonGroup
from PySide.QtGui import QRadioButton
from PySide.QtGui import QCheckBox
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QGroupBox
from PySide.QtGui import QPushButton


def build_radio_group(array):
    radio_group = QButtonGroup()
    button_id = 0
    for item in array:
        rb = QRadioButton(item)
        radio_group.addButton(rb, button_id)
        button_id += 1

    return radio_group


def build_checkbox_group(array):
    check_group = QButtonGroup()
    button_id = 0
    for item in array:
        cb = QCheckBox(item)
        check_group.addButton(cb, button_id)
        button_id += 1

    return check_group


def build_push_button_group(array):
    button_group = QButtonGroup()
    button_id = 0

    for item in array:
        pb = QPushButton(item)
        button_group.addButton(pb, button_id)
        button_id += 1

    return button_group


def build_button_group_box(button_group, title, columns=1):

    horizontal_box = QBoxLayout(QBoxLayout.LeftToRight)

    column_array = []

    for i in xrange(columns):
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        column_array.append(layout)
        horizontal_box.addLayout(layout)

    i = 1
    for button in button_group.buttons():
        column_array[i % columns].addWidget(button)
        i += 1

    button_group_box = QGroupBox(title)
    button_group_box.setLayout(horizontal_box)
    return button_group_box
