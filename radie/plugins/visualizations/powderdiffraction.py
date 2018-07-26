"""Module for the Visualizations of PowderDiffraction Datasets"""

import os

import pyqtgraph as pg

from radie.qt import colors, uchars
from radie.qt import plotlist
from radie.qt.visualizations import base, register_visualizations
from radie.plugins.structures import powderdiffraction
from radie.plugins.visualizations.ui.powderdiffraction import Ui_PowderDiffraction


class DFItem(plotlist.DFItem):
    """an item class with pyqtgraph xy curve handles of type PlotDataItem"""
    def __init__(self, ref, item_list, name=None):
        super(DFItem, self).__init__(ref, item_list, name)
        self.plotDataItem = pg.PlotDataItem()
        self.plotDataItem.setData(name=self.text)

    def setText(self, value):
        self.text = value
        self.plotDataItem.setData(name=value)


class VisPowderDiffraction(base.Visualization, Ui_PowderDiffraction):
    """Visualization to compare powder diffraction histograms

    Attributes
    ----------
    x_values : list
        a list of key, value pairs for the comboBox_xValues widget

    """
    name = "Powder Diffraction"
    description = "A Visualization to compare powder diffraction histograms"
    _icon_image = os.path.join(os.path.dirname(__file__), "icons/powderdiffraction.svg")

    supportedClasses = (
        powderdiffraction.PowderDiffraction,
    )

    x_values = [
        ["wavelength ({:})".format(uchars.angstrom), None],
        ["Q", None],
        ["d-spacing", None],
        ["CuKa", powderdiffraction.CuKa]
    ]

    def __init__(self, parent=None):
        super(VisPowderDiffraction, self).__init__(parent)
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
        self.listView_datasets.setItemClass(DFItem)
        self.listView_datasets.supportedClasses = self.supportedClasses

        for xVal in self.x_values:
            self.comboBox_xValues.addItem(xVal[0])
        self.doubleSpinBox_wavelength.setValue(powderdiffraction.CuKa)

        self.plotWidget.plotItem.setLabel("left", "intensity")
        self.plotWidget.plotItem.setLabel("bottom", "two-theta (deg)")

        # --- signal connections --- #
        self.listView_datasets.model().itemsAdded.connect(self.addCurves)
        self.listView_datasets.model().itemTextUpdated.connect(self.plotWidget.plotItem.resetLegend)
        self.listView_datasets.model().itemToggled.connect(self.itemToggled)
        self.listView_datasets.model().rowsMoved.connect(self.processNewLayout)
        self.listView_datasets.model().itemsDeleted.connect(self.processNewLayout)
        # self.listView_datasets.model().rowsRemoved.connect(self.processNewLayout)
        self.doubleSpinBox_wavelength.editingFinished.connect(self.determineXBounds)
        self.doubleSpinBox_wavelength.editingFinished.connect(self.setXDataFunction)
        self.doubleSpinBox_wavelength.editingFinished.connect(self.recalculateXValues)
        self.checkBox_normalize.stateChanged.connect(self.recalculateYValues)
        self.checkBox_xStagger.stateChanged.connect(self.recalculateXValues)
        self.checkBox_xStagger.stateChanged.connect(self.doubleSpinBox_xStagger.setEnabled)
        self.checkBox_yStagger.stateChanged.connect(self.recalculateYValues)
        self.checkBox_yStagger.stateChanged.connect(self.doubleSpinBox_yStagger.setEnabled)
        self.doubleSpinBox_yStagger.valueChanged.connect(self.recalculateYValues)
        self.doubleSpinBox_xStagger.valueChanged.connect(self.recalculateXValues)
        self.comboBox_xValues.currentIndexChanged.connect(self.xSelectionChanged)
        # --- end signal connections --- #

        self.doubleSpinBox_yStagger.setEnabled(False)
        self.doubleSpinBox_xStagger.setEnabled(False)
        self.setXDataFunction()

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

    def xSelectionChanged(self):
        xIndex = self.comboBox_xValues.currentIndex()
        self.setXDataFunction()
        self.determineXBounds()

        self.doubleSpinBox_wavelength.setEnabled(xIndex not in (1, 2))

        if xIndex == 1:
            xLabel = "Q"
        elif xIndex == 2:
            xLabel = "d-space ({:s})".format(uchars.angstrom)
        else:
            xLabel = "two-theta (deg)"

        self.plotWidget.plotItem.setLabel("bottom", xLabel)

        if xIndex > 2:
            wavelength = self.x_values[xIndex][1]
            self.doubleSpinBox_wavelength.setValue(wavelength)

        self.recalculateXValues()

    def determineXBounds(self):
        # first, where are the xValues coming from
        items = self.listView_datasets.iterItems()
        item1 = next(items)
        xVals = self.xData(item1.df)
        self.xmax = xVals.max()
        self.xmin = xVals.min()
        
        for item in items:
            xVals = self.xData(item.df)
            df_xmax = xVals.max()
            if df_xmax > self.xmax:
                self.xmax = df_xmax
            df_xmin = xVals.min()
            if df_xmin > self.xmin:
                self.xmin = df_xmin

    def determineYBounds(self):
        items = self.listView_datasets.iterItems()
        item1 = next(items)

        self.ymax = item1.df.intensity.max()
        self.ymin = item1.df.intensity.min()

        for item in items:
            df_ymax = item.df.intensity.max()
            if df_ymax > self.ymax:
                self.ymax = df_ymax
            df_ymin = item.df.intensity.min()
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

    def setXDataFunction(self):
        index = self.comboBox_xValues.currentIndex()
        if index == 1:
            self._xFunc = lambda df: df.Q.values
        elif index == 2:
            self._xFunc = lambda df: df.d_spacing.values
        else:
            wavelength = self.doubleSpinBox_wavelength.value()
            self._xFunc = lambda df: df.twotheta_at_wavelength(wavelength).values

    def xData(self, df):
        """

        Parameters
        ----------
        df : structures.PowderDiffraction

        Returns
        -------
        xVals : np.ndarray
            the data to be used for x-axis plotting

        """
        return self._xFunc(df)

    def yData(self, df):
        """

        Parameters
        ----------
        df : structures.PowderDiffraction

        Returns
        -------
        yVals : np.ndarray
            the data to be used for y-axis plotting
        """
        return df.intensity.values

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

        if self.checkBox_xStagger.isChecked():
            row = self.listView_datasets.row(item)
            stagger_by = row * self.doubleSpinBox_xStagger.value() / 100
            stagger_by *= self.xmax - self.xmin
            xVals += stagger_by

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
        row = self.listView_datasets.row(item)
        stagger = self.checkBox_yStagger.checkState()
        stagger_by = self.doubleSpinBox_yStagger.value() / 100
        yVals = self.yData(item.df)

        if self.checkBox_normalize.isChecked():
            yMin = yVals.min()
            yShift = yVals - yMin
            yVals = yShift / yShift.max()
            if stagger:
                yVals += stagger_by * row
        else:
            if stagger:
                stagger_by = (self.ymax - self.ymin) * stagger_by
                yVals = yVals + stagger_by * row

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


register_visualizations(VisPowderDiffraction)
