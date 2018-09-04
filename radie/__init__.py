from . import structures, loaders, plugins
from .structures import StructuredDataFrame
from .loaders import load_file, load_csv

__version__ = '0.1.4'

plugins.import_structures()
plugins.import_loaders()
