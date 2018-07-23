from os import path
from PyQt5 import uic

uic_dir = path.dirname(__file__)
uic.compileUiDir(uic_dir)
