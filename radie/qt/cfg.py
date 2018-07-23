import sys
import os

from PyQt5 import QtWidgets, QtGui
import pyqtgraph as pg

dpi = None
dpi_scaling = 1.0
dpi_100percent = 96


def set_dpi_scaling():
    app = QtWidgets.QApplication.instance()
    screen = app.screens()[0]  # type QtGui.QScreen
    dpi = screen.logicalDotsPerInch()
    global dpi_scaling
    dpi_scaling = dpi / dpi_100percent


preferred_styles = ['plastique', 'Fusion', 'cleanlooks', 'motif', 'cde']
preferred_style = 'Fusion'

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('antialias', True)

resource_manager = None

user_path = os.path.expanduser("~")
executable_dir = os.path.dirname(sys.executable)

qt_dir = os.path.dirname(os.path.abspath(__file__))
radie_dir = os.path.join(qt_dir, "..")
resources_dir = os.path.join(qt_dir, "resources")
icon_path = os.path.join(resources_dir, "icons")

radie_icon = os.path.join(icon_path, "radie.svg")
