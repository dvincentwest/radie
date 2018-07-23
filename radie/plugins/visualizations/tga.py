"""Module for the Visualizations of Thermogravimetric Analysis Datasets"""

import os

import pyqtgraph as pg
import numpy as np

from radie.qt import cfg, colors, uchars
from radie.qt import plotlist
from radie.qt.visualizations import base, register_visualizations
from radie.plugins.structures import tga
from radie.plugins.visualizations.ui.tga import Ui_TGA


class DFItem(plotlist.DFItem):
    """an item class with pyqtgraph xy curve handles of type PlotDataItem"""

    def __init__(self, ref, item_list, name=None):
        super(DFItem, self).__init__(ref, item_list, name)
        self.plotDataItemY1 = pg.PlotDataItem()
        self.plotDataItemY1.setData(name=self.text)
        self.plotDataItemY2 = pg.PlotDataItem()
        self.plotDataItemY2.setData(name=self.text)

    def setText(self, value):
        self.text = value
        self.plotDataItemY1.setData(name=value)
        self.plotDataItemY2.setData(name=value)


class VisTGA(base.Visualization, Ui_TGA):
    name = "TGA"
    description = "A Visualization to compare thermogravimetric analysis results"
    _icon_image = os.path.join(os.path.dirname(__file__), "icons/tga_chart_curve.png")

    supportedClasses = (
        tga.TGA,
    )

    X_COMBO = ['Temperature', 'Time']
    Y1_COMBO = ['Weight', 'Deriv. Weight', 'Temperature']
    Y2_COMBO = ['None', 'Deriv. Weight', 'Temperature']

    def __init__(self, parent=None):
        super(VisTGA, self).__init__(parent)
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 100)

        self._colors = colors.colors()
        self.xmin = None
        self.xmax = None
        self.y1min = None
        self.y1max = None
        self.y2min = None
        self.y2max = None

        self.xlabel = None
        self.y1label = None
        self.y2label = None

        self._xFunc = None
        self._y1Func = None
        self._y2Func = None

        # setup class-types, and plotting-curve types for the list
        self.listView_datasets.supportedClasses = self.supportedClasses
        self.listView_datasets.setItemClass(DFItem)

        # Setup plotting choices
        for x_key in self.X_COMBO:
            self.comboBox_x.addItem(x_key)
        for y_key in self.Y1_COMBO:
            self.comboBox_y1.addItem(y_key)
        for y_key in self.Y2_COMBO:
            self.comboBox_y2.addItem(y_key)

        self.comboBox_x.setCurrentIndex(0)
        self.comboBox_y1.setCurrentIndex(0)
        self.comboBox_y2.setCurrentIndex(1)

        self.plotWidget.plotItem.setLabel("left", "Weight (mg)")
        self.plotWidget.plotItem.setLabel("bottom", "Temperature (°C)")

        # Setup secondary y axis
        # pyqtgraph does not have this really built in
        # A new viewbox must be created which will hold its own plotDataItems
        # That viewbox must be linked to the existing plotItem
        # Adapted from : https://stackoverflow.com/questions/23679159/two-y-scales-in-pyqtgraph-twinx-like
        # PlotDataItems (or PlotCurveItems etc..) can now be added to
        # the self.y2ViewBox via its addItem function
        self.plotWidget.plotItem.showAxis("right")
        self.plotWidget.plotItem.setLabel("right", "Deriv. Weight (mg/°C)")
        self.y2ViewBox = pg.ViewBox()
        self.plotWidget.plotItem.scene().addItem(self.y2ViewBox)
        self.plotWidget.plotItem.getAxis('right').linkToView(self.y2ViewBox)
        self.y2ViewBox.setXLink(self.plotWidget.plotItem)
        self.updateViews()
        self.plotWidget.plotItem.getViewBox().sigResized.connect(self.updateViews)

        # --- signal connections --- #
        # Taking the lazy approach with a complete redraw every time something changes
        # as opposed to changing only what is required
        self.listView_datasets.model().itemsAdded.connect(self.processNewLayout)
        self.listView_datasets.model().itemTextUpdated.connect(self.processNewLayout)
        self.listView_datasets.model().itemToggled.connect(self.processNewLayout)
        self.listView_datasets.model().rowsMoved.connect(self.processNewLayout)
        self.listView_datasets.model().itemsDeleted.connect(self.processNewLayout)
        self.checkBox_normalizeWeight.stateChanged.connect(self.processNewLayout)
        self.comboBox_x.currentIndexChanged.connect(self.processNewLayout)
        self.comboBox_y1.currentIndexChanged.connect(self.processNewLayout)
        self.comboBox_y2.currentIndexChanged.connect(self.processNewLayout)
        # --- end signal connections --- #

        self.setXDataFunction()
        self.setY1DataFunction()
        self.setY2DataFunction()

    def updateViews(self):
        """Needed for the y2 axis"""
        self.y2ViewBox.setGeometry(self.plotWidget.plotItem.getViewBox().sceneBoundingRect())
        self.y2ViewBox.linkedViewChanged(self.plotWidget.plotItem.getViewBox(), self.y2ViewBox.XAxis)

    def processNewLayout(self):
        self.plotWidget.plotItem.clear()
        self.plotWidget.plotItem.resetLegend()
        self.y2ViewBox.clear()

        self.setXDataFunction()
        self.setY1DataFunction()
        self.setY2DataFunction()

        self.setAxisLabels()

        self.addCurves([item for item in self.listView_datasets.iterItems() if item.checkState])

    def setAxisLabels(self):
        """
        Set the left, bottom and right axis labels based on the selection in the combo boxes
        Returns
        -------

        """
        # get and set the bottom axis label
        index = self.comboBox_x.currentIndex()
        if index == 0:
            self.xlabel = "Temperature (°C)"
        elif index == 1:
            self.xlabel = "Time (min)"
        self.plotWidget.plotItem.setLabel("bottom", self.xlabel)

        # get and set the left axis label
        index = self.comboBox_y1.currentIndex()
        norm = self.checkBox_normalizeWeight.isChecked()
        if index == 0:
            self.y1label = 'Weight ({})'.format('%' if norm else 'mg')
        elif index == 1:
            self.y1label = 'Deriv. Weight ({}/°C)'.format('%' if norm else 'mg')
        elif index == 2:
            self.y1label = 'Temperature (°C)'
        self.plotWidget.plotItem.setLabel("left", self.y1label)

        # get and set the right axis label
        index = self.comboBox_y2.currentIndex()
        norm = self.checkBox_normalizeWeight.isChecked()
        if index == 0:
            # is this really he best way to do control values on axis??
            self.plotWidget.plotItem.getAxis('right').style['showValues'] = False
            self.plotWidget.plotItem.getAxis('right').setGrid(False)
            self.y2label = ''
        elif index == 1:
            # is this really he best way to do control values on axis??
            self.plotWidget.plotItem.getAxis('right').style['showValues'] = True
            self.plotWidget.plotItem.getAxis('right').setGrid(True)
            self.y2label = 'Deriv. Weight ({}/°C)'.format('%' if norm else 'mg')
        elif index == 2:
            # is this really he best way to do control values on axis??
            self.plotWidget.plotItem.getAxis('right').style['showValues'] = True
            self.plotWidget.plotItem.getAxis('right').setGrid(True)
            self.y2label = 'Temperature (°C)'
        self.plotWidget.plotItem.showAxis("right")
        self.plotWidget.plotItem.setLabel("right", self.y2label)

    def hasY2(self):
        return self.comboBox_y2.currentIndex() > 0

    def setXDataFunction(self):
        index = self.comboBox_x.currentIndex()
        if index == 0:
            self._xFunc = lambda df: df.temperature.values
        elif index == 1:
            self._xFunc = lambda df: df.time.values

    def setY1DataFunction(self):
        index = self.comboBox_y1.currentIndex()
        norm = self.checkBox_normalizeWeight.isChecked()
        if index == 0:
            if norm:
                self._y1Func = lambda df: df.norm_weight.values
            else:
                self._y1Func = lambda df: df.weight.values
        elif index == 1:
            if norm:
                self._y1Func = lambda df: df.deriv_norm_weight.values
            else:
                self._y1Func = lambda df: df.deriv_weight.values
        elif index == 2:
            self._y1Func = lambda df: df.temperature.values

    def setY2DataFunction(self):
        index = self.comboBox_y2.currentIndex()
        norm = self.checkBox_normalizeWeight.isChecked()
        if index == 0:
            self._y2Func = lambda df: np.array([])
        elif index == 1:
            if norm:
                self._y2Func = lambda df: df.deriv_norm_weight.values
            else:
                self._y2Func = lambda df: df.deriv_weight.values
        elif index == 2:
            self._y2Func = lambda df: df.temperature.values

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

    def y1Data(self, df):
        """

        Parameters
        ----------
        df : structures.PowderDiffraction

        Returns
        -------
        yVals : np.ndarray
            the data to be used for y-axis plotting
        """
        return self._y1Func(df)

    def y2Data(self, df):
        return self._y2Func(df)

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

    def y1Values(self, item):
        """

        Parameters
        ----------
        item : DFItem

        Returns
        -------
        yVals : np.ndarray

        """
        y1Vals = self.y1Data(item.df)
        return y1Vals

    def y2Values(self, item):
        """

        Parameters
        ----------
        item : DFItem

        Returns
        -------
        yVals : np.ndarray

        """
        y2Vals = self.y2Data(item.df)
        return y2Vals

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

        self.resetColors()

        for item in listItems:  # type: DFItem

            # Color attribution before checkState allows constant colors during toggling
            color1 = self.nextColor
            color2 = self.nextColor

            if item.checkState:
                item.plotDataItemY1.setData(
                    x=self.xValues(item),
                    y=self.y1Values(item),
                    pen=color1
                )
                self.plotWidget.addItem(item.plotDataItemY1)

                if self.hasY2():
                    item.plotDataItemY2.setData(
                        x=self.xValues(item),
                        y=self.y2Values(item),
                        pen=color2
                    )
                    self.y2ViewBox.addItem(item.plotDataItemY2)
                    # Need to manually add the item to the legend since it is in a different viewbox
                    self.plotWidget.plotItem.legend.addItem(item.plotDataItemY2,
                                                            '{} y2'.format(item.plotDataItemY2.name()))



register_visualizations(VisTGA)
