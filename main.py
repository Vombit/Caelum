"""pass"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon

from bin.modules.CallHandler import CallHandler
from bin.modules.additional_functions import (
    resource_path,
)


class WebEngine(QWebEngineView):
    """pass"""
    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setWindowTitle("Caelum")
        self.setFixedSize(1000, 620)
        self.setWindowIcon(QIcon("./bin/icon.ico"))

    def close_event(self, evt):
        """Override close event to clear http cache before closing application
        """
        self.page().profile().clearHttpCache()
        super().closeEvent(evt)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = WebEngine()
    channel = QWebChannel()
    handler = CallHandler(view)
    channel.registerObject("PyHandler", handler)
    view.page().setWebChannel(channel)
    view.load(QUrl.fromLocalFile(resource_path("./bin/index.html")))
    view.show()
    app.exec_()
