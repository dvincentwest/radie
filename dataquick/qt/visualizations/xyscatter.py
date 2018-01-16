"""module for the visualizations of generic dataquickframes"""
import os

from PyQt5 import QtGui
import pyqtgraph as pg

from . import base
from .. import dpi
from .. import cfg, colors
from .. import plotlist
from ..ui.xyscatter import Ui_XYScatter
from .. import functions as fn


class DQFItem(plotlist.DQFItem):
    """an item class with pyqtgraph xy curve handles of type PlotDataItem"""
    def __init__(self, ref, item_list, name=None):
        super(DQFItem, self).__init__(ref, item_list, name)
        self.plotDataItem = pg.PlotDataItem()
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


class XYScatter(base.Visualization, Ui_XYScatter):
    """A generic XY scatter visualization

    This visualization is meant to accomodate all possible data-frames.  It provides a combo-box in the list widget
    to select which columns of data will be used for the X and Y values, which will be non-sensical in some cases

    """
    name = "XY Scatter"
    description = "A generic visualization of XY curves from DataFrame Series"
    _icon_image = os.path.join(cfg.icon_path, "xyscatter.svg")

    def __init__(self, parent=None):
        super(XYScatter, self).__init__(parent)
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.splitter.setSizes(dpi.width_by_height(280, 720))

        self.comboBox_lineStyle.setItemIcon(0, QtGui.QIcon(os.path.join(cfg.icon_path, "xyline.svg")))
        self.comboBox_lineStyle.setItemIcon(1, QtGui.QIcon(os.path.join(cfg.icon_path, "xypoints.svg")))

        self.treeView_datasets.setItemClass(DQFItem)
        self.treeView_datasets.supportedClasses = self.supportedClasses

        self.treeView_datasets.model().itemsAdded.connect(self.addCurves)
        self.treeView_datasets.model().itemAccessorChanged.connect(self.itemDataChanged)
        self.treeView_datasets.model().itemsDeleted.connect(self.processNewLayout)
        self.treeView_datasets.model().rowsMoved.connect(self.processNewLayout)
        self.treeView_datasets.model().itemToggled.connect(self.itemToggled)
        self.treeView_datasets.model().itemTextUpdated.connect(self.plotWidget.plotItem.resetLegend)
        self.comboBox_lineStyle.currentIndexChanged.connect(self.setLineStyle)
        self.lineEdit_xlabel.textChanged.connect(self.setXLabel)
        self.lineEdit_ylabel.textChanged.connect(self.setYLabel)

        self._colors = None
        self.resetColors()

        self.alphaChanged = pg.SignalProxy(self.slider_alpha.valueChanged, slot=self.setAlpha, delay=0.05)
        self.slider_alpha.valueChanged.connect(self.label_alphaValue.setNum)

    def setAlpha(self):
        if not self.useSymbols():
            return
        for item in self.treeView_datasets.iterItems():
            color = "{:s}{:02x}".format(item.color, self.slider_alpha.value())
            item.plotDataItem.setSymbolPen(color)

    def useSymbols(self):
        return bool(self.comboBox_lineStyle.currentIndex())

    def setAxisLabel(self, axis: str, text: str):
        if not text:
            self.plotWidget.plotItem.showLabel(axis, False)
            return
        self.plotWidget.setLabel(axis=axis, text=text)

    def setXLabel(self, text: str):
        self.setAxisLabel("bottom", text)

    def setYLabel(self, text: str):
        self.setAxisLabel("left", text)

    def setLineStyle(self, checkState: bool):
        if self.useSymbols():
            for item in self.treeView_datasets.iterItems():  # type: DQFItem
                color = "{:s}{:02x}".format(item.color, self.slider_alpha.value())
                item.plotDataItem.setData(symbolPen=color, symbol='o', symbolSize=5)
                item.plotDataItem.setPen(None)
        else:
            for item in self.treeView_datasets.iterItems():  # type: DQFItem
                item.plotDataItem.setData(symbolPen=None, symbol=None)
                item.plotDataItem.setPen(item.color)

    def nextColor(self):
        return next(self._colors)

    def resetColors(self):
        self._colors = colors.colors()

    def itemDataChanged(self, item: DQFItem):
        if not item.isChecked():
            return

        item.plotDataItem.setData(
            x=item.x_data(),
            y=item.y_data()
        )

    def processNewLayout(self):
        self.plotWidget.plotItem.clear()
        self.plotWidget.plotItem.resetLegend()
        for item in self.treeView_datasets.iterItems():
            self.plotWidget.addItem(item.plotDataItem)

    def itemToggled(self, item):
        """process checking/unchecking of a DataQuickFrame in the plot

        Parameters
        ----------
        item : DQFItem

        """
        if item.checkState:
            item.plotDataItem.setData(
                x=item.x_data(),
                y=item.y_data(),
                name=item.text
            )
        else:
            item.plotDataItem.setData(name=None)
            item.plotDataItem.clear()
        self.plotWidget.plotItem.resetLegend()

    def addCurves(self, items):
        """
        Parameters
        ----------
        items : list of DQFItem
        """
        if self.useSymbols():
            for item in items:  # type: DQFItem
                item.color = self.nextColor()
                item.plotDataItem.setData(pen=None, symbol='o', symbolPen=item.color, symbolBrush=None)
                item.plotDataItem.updateItems()
                self.plotWidget.plotItem.addItem(item.plotDataItem)
        else:
            alpha = self.slider_alpha.value()
            for item in items:
                item.color = self.nextColor()
                color = "{:s}{:02x}".format(item.color, alpha)
                item.plotDataItem.setData(pen=color, symbol=None, symbolPen=None, symbolBrush=None)
                item.plotDataItem.updateItems()
                self.plotWidget.plotItem.addItem(item.plotDataItem)


def test():
    import sys
    from ...plugins import examples
    from ..masterdqftree import DQFReference
    app = fn.instantiate_app()
    fn.reset_excepthook()
    cfg.set_dpi_scaling()

    df = examples.example_powderdiffraction()
    ref1 = DQFReference(df, None)

    plot = XYScatter()
    plot.treeView_datasets.addDataFrames(ref1, ref1, ref1)
    plot.show()

    sys.exit(app.exec_())
