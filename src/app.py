import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from root_window import MainWindow


basedir = os.path.abspath(os.path.dirname(__file__))

try:
    from ctypes import windll
    myappid = 'sigma-is.emulator.devices.2.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


def include_style(app):
    with open(os.path.join(basedir, "ui", "style.qss"), "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons", "logo.ico")))
    widget = MainWindow()
    include_style(app)
    widget.show()
    sys.exit(app.exec())