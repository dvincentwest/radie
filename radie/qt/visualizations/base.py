"""define the generic Visualization class"""
import os

from PyQt5 import QtWidgets, QtGui
from ...structures.structureddataframe import StructuredDataFrame


class Visualization(QtWidgets.QWidget):
    """base class for QtWidget visualizations

    Very minimal skeleton defining the expected behavior a QWidget used to visualize a StructuredDataFrame.  Almost
    anything that will fit into a QtWidget is acceptable as a Visualization.  Most of the internals are defined in
    subclass.

    Attributes
    ----------
    name : str
        *cls var*, The name of the visualization to be displayed in menus
    description : str
        *cls var*, a short one line description
    supported_classes : list of Type(StructuredDataFrame)
        *cls var*, provide an easy mechanism to validate if the StructuredDataFrame objects in the visualization
        will play nice with the visualization

    Notes
    -----
    Private class variables for subclassing:

    _icon_image : str
        the path to the icon image used for this visualization
    _icon : QtGui.QIcon
        the Qt Icon constructed using `_icon_image` after an icon is requested from the application

    """

    name = 'Base'  # type: str
    description = None  # type: str
    _icon_image = None  # type: str
    _icon = None  # type: QtGui.QIcon

    supportedClasses = (  # must be a tuple
        StructuredDataFrame,
    )

    @classmethod
    def icon(cls):
        """return the icon specified in cls._icon_image, or a blank icon if no icon is specified

        Returns
        -------
        QtGui.QIcon

        Notes
        -----
        Certain versions of PyQt fail if a QIcon is constructed before the QApplication.  We specify the icon
        image file in cls._icon_image and then a QIcon is then constructed the first time this method is called.
        Subsequent calls return the previously constructed QIcon object

        """
        if isinstance(cls._icon, QtGui.QIcon):
            return cls._icon
        elif not cls._icon_image:
            return QtGui.QIcon()

        if os.path.isfile(cls._icon_image):
            try:
                cls._icon = QtGui.QIcon(cls._icon_image)
                return cls._icon
            except:
                cls._icon = None

        return QtGui.QIcon()

    def exportToExcel(self):
        """optional method to export the visualization to an excel file"""
        raise NotImplementedError

    def copyImage(self):
        """put an image of the visualization on the clipboard"""
        raise NotImplementedError
