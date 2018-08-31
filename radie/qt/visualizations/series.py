"""plot a line of a single pandas series"""

import os

import numpy as np
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg

from ...structures.structureddataframe import StructuredDataFrame
from .. import colors, cfg, dpi
from .. import plotwidget
from .. import plotlist
from .base import Visualization


class DFItem(plotlist.DFItem):
    """an item class with pyqtgraph xy curve handles of type PlotDataItem"""
    def __init__(self, ref, item_list, name=None):
        super(DFItem, self).__init__(ref, item_list, name)
        self.plotDataItem = pg.PlotDataItem()
        self.color = None
        self.values = None

    def setText(self, value):
        self.text = value
        self.plotDataItem.setData(name=value)
        self.plotDataItem.updateItems()

    def calculateValue(self):
        """calculate the histogram values, given the number of bins

        Parameters
        ----------
        bins : int
        density : bool

        """
        self.values = self.x_data()


class SeriesVisualization(Visualization):
    """A generic class providing the visualization of a column of data as evenly-spaced points"""

    name = "Series Line"
    description = "A generic visualization of Series of values"
    _icon_image = os.path.join(cfg.icon_path, "seriesvisualization.svg")

    def __init__(self, parent=None):
        super(SeriesVisualization, self).__init__(parent)

        # --- setupUi --- #
        self.resize(1000, 600)
        self.setWindowTitle("Series")
        self.vlay_main = QtWidgets.QVBoxLayout(self)
        self.vlay_main.setContentsMargins(3, 3, 3, 3)
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.dataListWidget = QtWidgets.QWidget(self.splitter)
        self.vlay_dataListWidget = QtWidgets.QVBoxLayout(self.dataListWidget)
        self.vlay_dataListWidget.setContentsMargins(0, 0, 0, 0)
        self.treeView_datasets = plotlist.DFSeriesListView(self.dataListWidget)
        self.vlay_dataListWidget.addWidget(self.treeView_datasets)
        self.hlay_parameters = QtWidgets.QHBoxLayout()
        self.vlay_dataListWidget.addLayout(self.hlay_parameters)
        self.plotWidget = plotwidget.PlotWidget(self.splitter)
        self.vlay_main.addWidget(self.splitter)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes(dpi.width_by_height(280, 720))
        # --- end setupUi --- #

        self.treeView_datasets.setItemClass(DFItem)
        self.treeView_datasets.supportedClasses = self.supportedClasses

        self.treeView_datasets.model().itemsAdded.connect(self.addCurves)
        self.treeView_datasets.model().itemAccessorChanged.connect(self.itemDataChanged)
        self.treeView_datasets.model().itemsDeleted.connect(self.processNewLayout)
        self.treeView_datasets.model().itemToggled.connect(self.itemToggled)
        self.treeView_datasets.model().itemTextUpdated.connect(self.plotWidget.plotItem.resetLegend)
        # self.checkBox_plotDensity.stateChanged.connect(self.recalculateValues)
        # self.spinBox_bins.editingFinished.connect(self.recalculateValues)

        self._colors = None
        self.resetColors()

    def nextColor(self):
        return next(self._colors)

    def resetColors(self):
        self._colors = colors.colors()

    def recalculateValues(self):
        for item in self.treeView_datasets.iterItems():
            item.calculateValue()
            item.plotDataItem.setData(x=np.arange(len(item.values)), y=item.values)

    def itemDataChanged(self, item: DFItem):
        if not item.isChecked():
            return
        item.calculateValue()
        item.plotDataItem.setData(x=np.arange(len(item.values)), y=item.values)

    def processNewLayout(self):
        self.plotWidget.plotItem.clear()
        self.plotWidget.plotItem.resetLegend()
        for item in self.treeView_datasets.iterItems():
            self.plotWidget.addItem(item.plotDataItem)

    def itemToggled(self, item):
        """
        process checking/unchecking of a StructuredDataFrame in the plot

        Parameters
        ----------
        item : DFItem
        """
        if item.checkState:
            item.plotDataItem.setData(x=np.arange(len(item.values)), y=item.values)
        else:
            item.plotDataItem.setData(name=None, stepMode=False)
            item.plotDataItem.clear()
        self.plotWidget.plotItem.resetLegend()

    def addCurves(self, items):
        """
        Parameters
        ----------
        items : list of DFItem
        """
        for item in items:  # type: DFItem
            item.color = self.nextColor()
            item.calculateValue()
            item.plotDataItem.setData(x=np.arange(len(item.values)), y=item.values, pen=item.color)
            self.plotWidget.plotItem.addItem(item.plotDataItem)


def test():
    import sys
    from ..masterdftree import DFReference
    from .. import cfg
    from .. import functions as fn
    app = fn.instantiate_app()
    fn.reset_excepthook()
    cfg.set_dpi_scaling()

    rng = np.random.RandomState(10)  # deterministic random data
    a = np.hstack((rng.normal(size=1000), rng.normal(loc=5, scale=2, size=1000)))
    b = np.hstack((rng.normal(size=1000, scale=2), rng.normal(loc=5, scale=1, size=1000)))
    data = np.vstack((a, b)).T
    df = StructuredDataFrame(data, columns=("a", "b"), name="Deterministic Random Data")
    ref1 = DFReference(df, None)

    plot = SeriesVisualization()
    plot.treeView_datasets.addDataFrames(ref1, ref1)
    plot.show()

    sys.exit(app.exec_())
