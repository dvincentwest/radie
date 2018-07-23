import warnings
from collections import OrderedDict

from . import datastructure
from .datastructure import DataStructure

__all__ = [
    DataStructure.__name__
]

structures = OrderedDict()
structures[DataStructure.__name__] = DataStructure


def register_data_structures(*sub_classes):
    """
    register DataStructure structures from the plugins folder

    Parameters
    ----------
    sub_classes
        DataStructure sub-classes as arguments

    """
    for cls in sub_classes:  # type: DataStructure
        if cls.__name__ in structures.keys():
            warnings.warn("overwriting {:s} df_class".format(cls.__name__))
        structures[cls.__name__] = cls
        globals()[cls.__name__] = cls  # put the class into this scope

        if cls.__name__ not in __all__:
            __all__.append(cls.__name__)


def print_available_structures():
    for key in structures.keys():
        print(key)
