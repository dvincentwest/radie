from . import structures, loaders, plugins
from .structures import DataQuickFrame
from .loaders import load_file, load_csv
from pandas import *

__version__ = "2017.12.29"

plugins.import_structures()
plugins.import_loaders()
