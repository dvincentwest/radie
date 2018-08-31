"""package for QtWidgets used to visualize StructuredDataFrame objects"""

import warnings
import typing
from collections import OrderedDict

from . import base, xyscatter, histogram, series

__all__ = []
visualizations = OrderedDict()


def register_visualizations(*sub_classes):
    """
    Parameters
    ----------
    sub_classes : typing.Type(base.Visualization)
        base.Visualization sub-classes passed in as arguments

    """
    for cls in sub_classes:
        if cls.__name__ in visualizations.keys():
            warnings.warn("overwriting visualization class {:}".format(cls.__name__))
        visualizations[cls.__name__] = cls

        if not cls.__name__ in __all__:
            globals()[cls.__name__] = cls  # put the class into this scope
            __all__.append(cls.__name__)


register_visualizations(
    xyscatter.XYScatter,
    series.SeriesVisualization,
    histogram.Histogram,
)
