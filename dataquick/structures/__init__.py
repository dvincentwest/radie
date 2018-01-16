import warnings
from collections import OrderedDict

from . import dataquickframe
from .dataquickframe import DataQuickFrame

__all__ = [
    DataQuickFrame.__name__
]

structures = OrderedDict()
structures[DataQuickFrame.__name__] = DataQuickFrame


def register_data_structures(*sub_classes):
    """
    register DataQuickFrame structures from the plugins folder

    Parameters
    ----------
    sub_classes
        DataQuickFrame sub-classes as arguments

    """
    for cls in sub_classes:  # type: DataQuickFrame
        if cls.__name__ in structures.keys():
            warnings.warn("overwriting {:s} dqf_class".format(cls.__name__))
        structures[cls.__name__] = cls
        globals()[cls.__name__] = cls  # put the class into this scope

        if cls.__name__ not in __all__:
            __all__.append(cls.__name__)


def print_available_structures():
    for key in structures.keys():
        print(key)
