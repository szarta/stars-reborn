"""
    ui.dialogs.about

    Contains all the data and capabilities needed for the game's about dialog.

    :copyright: (c) 2015 by Brandon Arrendondo.
    :license: MIT, see LICENSE.txt for more details.
"""
from PySide.QtGui import QDialog
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QPushButton
from PySide.QtGui import QLabel
from PySide.QtGui import QPixmap
from PySide.QtGui import QTextEdit
from PySide.QtCore import Qt

from src._version import __version__

License_File = "LICENSE.txt"
Credits_File = "resources/generated_credits.html"


class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super(LicenseDialog, self).__init__(parent)
        self.close_button = QPushButton("&Close")

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Stars Reborn License")
        self.setGeometry(150, 150, 640, 480)

        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        license_string = ""
        with open(License_File) as f:
            license_string = "".join(f.readlines())

        license_string = '<pre>' + \
                         license_string + '</pre>'

        license_label = QTextEdit(license_string)
        license_label.setReadOnly(True)
        main_layout.addWidget(license_label)

        button_layout = QBoxLayout(QBoxLayout.LeftToRight)
        button_layout.addStretch(1)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

        self.close_button.clicked.connect(self.accept)


class CreditsDialog(QDialog):
    def __init__(self, parent=None):
        super(CreditsDialog, self).__init__(parent)

        self.setGeometry(150, 150, 640, 480)
        self.close_button = QPushButton("&Close")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Stars Reborn Credits")
        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        credits_string = ""
        with open(Credits_File) as f:
            credits_string = "".join(f.readlines())

        credits_label = QTextEdit(credits_string)
        credits_label.setReadOnly(True)
        main_layout.addWidget(credits_label)

        button_layout = QBoxLayout(QBoxLayout.LeftToRight)
        button_layout.addStretch(1)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

        self.close_button.clicked.connect(self.accept)


class AboutDialog(QDialog):
    """
    This is the about dialog for this application.  It is responsible for:

        * Identifying the application
        * Showing the version information
        * Showing copyright/license information
        * Providing author/contact information
        * Linking to the application webpage
    """
    def __init__(self, parent=None):
        """
        Builds all display components used for this UI.
        """
        super(AboutDialog, self).__init__(parent)
        self.setGeometry(200, 200, 300, 200)

        self.credits_button = QPushButton("C&redits")
        self.license_button = QPushButton("&License")
        self.close_button = QPushButton("&Close")

        self.init_ui()

    def init_ui(self):

        self.setWindowTitle("About Stars Reborn")
        main_layout = QBoxLayout(QBoxLayout.TopToBottom, self)

        about_logo = QLabel("Stars Reborn")
        about_logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(about_logo)

        description_label = QLabel('A turn-based space strategy game.')
        description_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description_label)

        prog = "Stars Reborn"
        version_string = __version__ % ({"prog": prog})
        version_label = QLabel("Version: {0!s}".format(version_string))
        version_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(version_label)

        copyright_label = QLabel('<font size="2">Copyright (c) 2017</font>')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label2 = QLabel('<font size="2">Brandon Arrendondo</font>')
        copyright_label2.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(copyright_label)
        main_layout.addWidget(copyright_label2)

        website_label = QLabel('<a href="http://www.stars-reborn.com">Visit \
                                the Stars-Reborn website</a>')
        website_label.setAlignment(Qt.AlignCenter)
        website_label.setOpenExternalLinks(True)
        main_layout.addWidget(website_label)

        button_layout = QBoxLayout(QBoxLayout.LeftToRight)
        button_layout.addWidget(self.credits_button)
        button_layout.addWidget(self.license_button)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

        self.close_button.clicked.connect(self.accept)
        self.license_button.clicked.connect(self.license_exec)
        self.credits_button.clicked.connect(self.credits_exec)

    def license_exec(self):
        dialog = LicenseDialog(self)
        dialog.exec_()

    def credits_exec(self):
        dialog = CreditsDialog(self)
        dialog.exec_()
