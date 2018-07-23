"""plugins package, meant for custom data-structures and file-loaders and visualizations"""

import os
import pkgutil
import importlib

STRUCTURES_PKG_NAME = "structures"
STRUCTURES_PKG = __package__ + "." + STRUCTURES_PKG_NAME
LOADERS_PKG_NAME = "loaders"
LOADERS_PKG = __package__ + "." + LOADERS_PKG_NAME
VISUALIZATIONS_PKG_NAME = "visualizations"
VISUALZIATIONS_PKG = __package__ + "." + VISUALIZATIONS_PKG_NAME

this_dir = os.path.dirname(__file__)
structures_dir = os.path.join(this_dir, STRUCTURES_PKG_NAME)
loaders_dir = os.path.join(this_dir, LOADERS_PKG_NAME)
visualizations_dir = os.path.join(this_dir, VISUALIZATIONS_PKG_NAME)


disabled_plugins = (
    "powderdiffraction_siemensD500",
)


def import_structures():
    importlib.import_module(STRUCTURES_PKG)
    for finder, module_name, is_pkg in pkgutil.iter_modules([structures_dir]):
        if not is_pkg:
            importlib.import_module("." + module_name, STRUCTURES_PKG)


def import_loaders():
    importlib.import_module(LOADERS_PKG)
    for finder, module_name, is_pkg in pkgutil.iter_modules([loaders_dir]):
        if not is_pkg and module_name not in disabled_plugins:
            importlib.import_module("." + module_name, LOADERS_PKG)


def import_visualizations():
    importlib.import_module(VISUALZIATIONS_PKG)
    for finder, module_name, is_pkg in pkgutil.iter_modules([visualizations_dir]):
        if not is_pkg:
            importlib.import_module("." + module_name, VISUALZIATIONS_PKG)
