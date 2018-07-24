from . import structures, loaders, plugins
from .structures import DataStructure
from .loaders import load_file, load_csv
from pandas import *

with open('VERSION') as fid:
    __version__ = fid.read().strip()

plugins.import_structures()
plugins.import_loaders()
