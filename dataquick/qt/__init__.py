try:
    import PyQt5
except ImportError:
    raise Exception("PyQt5 module note found, run `conda install pyqt` or `pip install PyQt5`")

from . import cfg
from .functions import *

from .. import plugins

plugins.import_visualizations()
