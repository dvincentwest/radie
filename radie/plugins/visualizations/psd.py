"""Module for the Visualization of particle size distributions
Log plot"""

import os

import pyqtgraph as pg

from radie.qt import colors, uchars
from radie.qt import plotlist
from radie.qt.visualizations import base, register_visualizations
from radie.plugins.structures import psd
from radie.plugins.visualizations.ui.psd import Ui_PSD


class DFItem(plotlist.DFItem):
    """an item class with pyqtgraph xy curve handles of type PlotDataItem"""
    def __init__(self, ref, item_list, name=None):
        super(DFItem, self).__init__(ref, item_list, name)
        self.plotDataItem = pg.PlotDataItem()
        #self.plotDataItem.setLogMode(x=True) #?
        self.color = None
        self.plotDataItem.setData(
            x=self.x_data(),
            y=self.y_data(),
            name=self.text
        )

    def setText(self, value):
        self.text = value
        self.plotDataItem.setData(name=value)
        self.plotDataItem.updateItems()


class VisPSD(base.Visualization, Ui_PSD):
    """A Visualization to compare particle size distributions"""

    name = "Particle Size Distribution"
    description = "A Visualization to compare particle size distributions"
    _icon_image = os.path.join(os.path.dirname(__file__), "icons/particlesizedistribution.svg")

    supportedClasses = (
        psd.PSD,
    )

    X_VALUES = [
        ["Diameter ({}m)".format(uchars.mu), None],
    ]

    def __init__(self, parent=None):
        super(VisPSD, self).__init__(parent)
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 100)

        self._colors = colors.colors()
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self._xFunc = None

        # setup class-types, and plotting-curve types for the list
        self.listView_datasets.supportedClasses = self.supportedClasses
        self.listView_datasets.setItemClass(DFItem)

#        for xVal in self.X_VALUES:
#            self.comboBox_xValues.addItem(xVal[0])
#        self.doubleSpinBox_wavelength.setValue(powderdiffraction.CuKa)

        self.plotWidget.plotItem.setLabel("left", "Frequency")
        self.plotWidget.plotItem.setLabel("bottom", "Diameter ({}m)".format(uchars.mu))
        self.plotWidget.plotItem.setLogMode(x=True)


        # --- signal connections --- #
        self.listView_datasets.model().itemsAdded.connect(self.addCurves)
        self.listView_datasets.model().itemTextUpdated.connect(self.plotWidget.plotItem.resetLegend)
        self.listView_datasets.model().itemToggled.connect(self.itemToggled)
        self.listView_datasets.model().rowsMoved.connect(self.processNewLayout)
        self.listView_datasets.model().itemsDeleted.connect(self.processNewLayout)
        # self.listView_datasets.model().rowsRemoved.connect(self.processNewLayout)
#        self.doubleSpinBox_wavelength.editingFinished.connect(self.determineXBounds)
#        self.doubleSpinBox_wavelength.editingFinished.connect(self.setXDataFunction)
#        self.doubleSpinBox_wavelength.editingFinished.connect(self.recalculateXValues)
#        self.checkBox_normalize.stateChanged.connect(self.recalculateYValues)
#        self.checkBox_xStagger.stateChanged.connect(self.recalculateXValues)
#        self.checkBox_xStagger.stateChanged.connect(self.doubleSpinBox_xStagger.setEnabled)
#        self.checkBox_yStagger.stateChanged.connect(self.recalculateYValues)
#        self.checkBox_yStagger.stateChanged.connect(self.doubleSpinBox_yStagger.setEnabled)
#        self.doubleSpinBox_yStagger.valueChanged.connect(self.recalculateYValues)
#        self.doubleSpinBox_xStagger.valueChanged.connect(self.recalculateXValues)
#        self.comboBox_xValues.currentIndexChanged.connect(self.xSelectionChanged)
        # --- end signal connections --- #

 #       self.doubleSpinBox_yStagger.setEnabled(False)
 #       self.doubleSpinBox_xStagger.setEnabled(False)
 #       self.setXDataFunction()

    def itemToggled(self, item):
        """
        process checking/unchecking of a StructuredDataFrame in the plot

        Parameters
        ----------
        item : DFItem
        """
        if item.checkState:
            item.plotDataItem.setData(
                x=self.xValues(item),
                y=self.yValues(item),
                name=item.text
            )
        else:
            item.plotDataItem.setData(name=None)
            item.plotDataItem.clear()
        self.plotWidget.plotItem.resetLegend()

    def processNewLayout(self):
        self.plotWidget.plotItem.clear()
        self.plotWidget.plotItem.resetLegend()
        self.recalculateYValues()
        for item in self.listView_datasets.iterItems():
            self.plotWidget.addItem(item.plotDataItem)

#    def xSelectionChanged(self):
#        xIndex = self.comboBox_xValues.currentIndex()
#        self.setXDataFunction()
#        self.determineXBounds()
#
#        self.doubleSpinBox_wavelength.setEnabled(xIndex not in (1, 2))
#
#        if xIndex == 1:
#            xLabel = "Q"
#        elif xIndex == 2:
#            xLabel = "d-space ({:s})".format(uchars.angstrom)
#        else:
#            xLabel = "two-theta (deg)"
#
#        self.plotWidget.plotItem.setLabel("bottom", xLabel)
#
#        if xIndex > 2:
#            wavelength = self.X_VALUES[xIndex][1]
#            self.doubleSpinBox_wavelength.setValue(wavelength)
#
#        self.recalculateXValues()

    def determineXBounds(self):
        # first, where are the xValues coming from
        items = self.listView_datasets.iterItems()
        item1 = next(items)
        x = self.xValues(item1)
        self.xmax = x.max()
        self.xmin = x.min()

        for item in items:
            x = self.xValues(item)
            df_xmax = x.max()
            if df_xmax > self.xmax:
                self.xmax = df_xmax
            df_xmin = x.min()
            if df_xmin > self.xmin:
                self.xmin = df_xmin

    def determineYBounds(self):
        items = self.listView_datasets.iterItems()
        item1 = next(items)
        y = self.yValues(item1)
        self.ymax = y.max()
        self.ymin = y.min()

        for item in items:
            y = self.yValues(item)
            df_ymax = y.max()
            if df_ymax > self.ymax:
                self.ymax = df_ymax
            df_ymin = y.min()
            if df_ymin > self.ymin:
                self.ymin = df_ymin

    def determineXYBounds(self):
        self.determineXBounds()
        self.determineYBounds()

    def recalculateXValues(self):
        for item in self.listView_datasets.iterItems():  # type: DFItem
            if item.checkState:
                item.plotDataItem.setData(
                    x=self.xValues(item),
                    y=item.plotDataItem.yData
                )

    def recalculateYValues(self):
        for item in self.listView_datasets.iterItems():  # type: DFItem
            if item.isChecked():
                item.plotDataItem.setData(
                    x=item.plotDataItem.xData,
                    y=self.yValues(item)
                )


    def xData(self, df):
        """

        Parameters
        ----------
        df : structures.PSD

        Returns
        -------
        xVals : np.ndarray
            the data to be used for x-axis plotting

        """
        return df.diameter.values

    def yData(self, df):
        """

        Parameters
        ----------
        df : structures.PSD

        Returns
        -------
        yVals : np.ndarray
            the data to be used for y-axis plotting
        """
        return df.frequency.values

    def xValues(self, item):
        """

        Parameters
        ----------
        item : DFItem

        Returns
        -------
        xVals : np.ndarray

        """
        xVals = self.xData(item.df)  # get the appropriate xValues, and scale them accordingly
        return xVals

    def yValues(self, item):
        """

        Parameters
        ----------
        item : DFItem

        Returns
        -------
        yVals : np.ndarray

        """
        yVals = self.yData(item.df)
        return yVals

    @property
    def nextColor(self):
        return next(self._colors)

    def resetColors(self):
        self._colors = colors.colors()

    def addCurves(self, listItems):
        """
        Parameters
        ----------
        listItems : list of DFItem
        """
        if not listItems:
            return

        self.determineXYBounds()

        for item in listItems:  # type: DFItem
            item.plotDataItem.setData(
                x=self.xValues(item),
                y=self.yValues(item),
                pen=self.nextColor
            )
            self.plotWidget.addItem(item.plotDataItem)


register_visualizations(VisPSD)
