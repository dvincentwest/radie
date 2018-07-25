from . import structures, loaders, plugins
from .structures import DataStructure
from .loaders import load_file, load_csv

__version__ = '0.1.2'

plugins.import_structures()
plugins.import_loaders()
