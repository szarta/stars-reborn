"""
    ui.turn.space

    The widget for displaying and interacting with space and the objects in it.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""
import json
from PySide.QtCore import Qt
from PySide.QtWebKit import QWebView
from PySide.QtWebKit import QWebPage
from PySide.QtGui import QPainter
from PySide.QtGui import QWidget
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QLabel
from PySide.QtGui import QFrame
from PySide.QtCore import Signal


class ButtonType:
    LeftClick = 0
    MiddleClick = 1
    RightClick = 2


class SpaceMap(QWidget):

    planet_selected = Signal(int)

    def __init__(self, svg=""):
        super(SpaceMap, self).__init__()

        main_layout = QBoxLayout(QBoxLayout.TopToBottom)

        self.web_view = QWebView()
        self.web_view.setRenderHints(QPainter.SmoothPixmapTransform)

        self.space_page = CommunicatingWebPage(self.handle_json_response)
        self.web_view.setPage(self.space_page)
        self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)

        self.update_view(svg)
        main_layout.addWidget(self.web_view, 1)

        info_panel = QBoxLayout(QBoxLayout.LeftToRight)
        self.id_label = QLabel()
        self.id_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        self.x_label = QLabel()
        self.x_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        self.y_label = QLabel()
        self.y_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        self.name_label = QLabel()
        self.name_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        info_panel.addWidget(self.id_label)
        info_panel.addWidget(self.x_label)
        info_panel.addWidget(self.y_label)
        info_panel.addWidget(self.name_label, 1)

        main_layout.addLayout(info_panel)

        self.light_year_label = QLabel()
        self.light_year_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        main_layout.addWidget(self.light_year_label)

        self.setLayout(main_layout)

    def update_view(self, svg):
        self.space_page.mainFrame().setHtml(space_html_from_svg(svg))

    def update_coords(self, pid, x, y, name):
        sb = '<font size="10pt">'
        se = '</font>'
        self.id_label.setText('{0}ID #{1!s}{2}'.format(sb, pid, se))
        self.x_label.setText("{0}X: {1!s}{2}".format(sb, x, se))
        self.y_label.setText("{0}Y: {1!s}{2}".format(sb, y, se))
        self.name_label.setText("{0}{1}{2}".format(sb, name, se))

    def update_light_years(self, distance, from_name):
        if(distance == 0):
            self.light_year_label.setText("")
        else:
            sb = '<font size="10pt">'
            se = '</font>'
            self.light_year_label.setText("{0}{1} light years from {2}{3}".format(
                sb, distance, from_name, se))

    def handle_json_response(self, json_data):
        button_clicked = json_data["evt-btn"]
        op = json_data["op"]

        if(button_clicked == ButtonType.LeftClick):

            if(op == "planet_click"):
                pid = json_data["pid"]
                self.planet_selected.emit(pid)
        elif(button_clicked == ButtonType.RightClick):
            print "Right Click"
        elif(button_clicked == ButtonType.MiddleClick):
            print "Middle click"
        else:
            print "Unrecognized button pressed."


class CommunicatingWebPage(QWebPage):
    """
    Class that defines a Web Page that is capable of sending and receiving
    JSON messages via Javascript on the web page to this class.
    """

    def __init__(self, json_receiver):
        """
        Inits this class.
        json_receiver - the function that implements the handler for received
                        JSON messages
        """
        super(CommunicatingWebPage, self).__init__()
        self.json_receiver = json_receiver

    def javaScriptAlert(self, originating_frame, message):
        """
        Overrides the base QWebPage function for JavaScript alerts.

        This is the hook by which this code can communicate with the JavaScript
        on the loaded web page (when it posts a Javascript alert)
        """
        self.receive_data(originating_frame, message)

    def receive_data(self, originating_frame, message):
        """
        Receives a JSON message from the Javascript on the frame.
        """
        data = json.loads(message)
        self.json_receiver(data)

    def send_data(self, frame, message):
        """
        Sends a JSON message to the Javascript on the frame.  Assumes it
        implements the function receiveJSON.
        """
        message.replace('"', '\\"')
        frame.evaluateJavaScript('receiveJSON("%s")' % message)


def space_html_from_svg(svg):
        html_content = """\
<html>
<head>
    <script language="javascript" type="text/javascript">
        function sendJSON(data) {
            alert(JSON.stringify(data));
        }

        function spaceCoord(x,y) {
            sendJSON({'op' : 'coord', 'coord' : {'x':x,'y':y}});
        }

        function spaceClick(evt) {
            sendJSON({'op' : 'space_click', 'coord' : {'x' : evt.clientX,'y' : evt.clientY}, 'shift-key' : evt.shiftKey, 'ctrl-key' : evt.ctrlKey});
        }

        function planetClick(evt, pid) {
            sendJSON({'op' : 'planet_click', 'coord' : {'x' : evt.clientX,'y' : evt.clientY}, 'shift-key' : evt.shiftKey, 'ctrl-key' : evt.ctrlKey, "pid" : pid, 'evt-btn' : evt.button});
        }

        function fleetClick(evt, pid) {
            sendJSON({'op' : 'fleet_click', 'coord' : {'x' : evt.clientX,'y' : evt.clientY}, 'shift-key' : evt.shiftKey, 'ctrl-key' : evt.ctrlKey, "pid" : pid});
        }

    </script>
</head>
<body style="-webkit-user-select: none; ondragstart='return false'; background-color:black">
<div align="left">
"""
        html_content += svg
        html_content += "</div></body></html>"
        return html_content
