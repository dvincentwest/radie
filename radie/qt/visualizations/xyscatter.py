"""module for the visualizations of generic datastructures"""
import os

from PyQt5 import QtGui
import pyqtgraph as pg

from . import base
from .. import dpi
from .. import cfg, colors
from .. import plotlist
from ..ui.xyscatter import Ui_XYScatter
from .. import functions as fn


class DFItem(plotlist.DFItem):
    """an item class with pyqtgraph xy curve handles of type PlotDataItem"""
    def __init__(self, ref, item_list, name=None):
        super(DFItem, self).__init__(ref, item_list, name)
        self.plotDataItem = pg.PlotDataItem()
        self.color = None

        self.legend_name = True
        self.legend_label = False
        self.legend_ycol = True

        self.plotDataItem.setData(
            x=self.x_data(),
            y=self.y_data(),
            name=self.text
        )

    def setLegend(self, legend_name=None, legend_label=None, legend_ycol=None):
        legend = list()

        if type(legend_name) is bool:
            self.legend_name = legend_name
            if legend_name:
                legend.append(self.ref.df.metadata["name"])
        if type(legend_label) is bool:
            self.legend_label = legend_label
            if legend_label:
                legend.append(self.text)
        if type(legend_ycol) is bool:
            self.legend_ycol = legend_ycol
            if legend_ycol:
                legend.append(str(self.y_accessor))

        self.plotDataItem.setData(name=" - ".join(legend))

    def setText(self, value):
        self.text = value
        if self.legend_label:  # only update if the legend is showing this data
            self.setLegend()


class XYScatter(base.Visualization, Ui_XYScatter):
    """A generic XY scatter visualization

    This visualization is meant to accomodate all possible data-frames.  It provides a combo-box in the list widget
    to select which columns of data will be used for the X and Y values, which will be non-sensical in some cases

    """
    name = "XY Scatter"
    description = "A generic visualization of XY curves from StructuredDataFrame Series"
    _icon_image = os.path.join(cfg.icon_path, "xyscatter.svg")

    def __init__(self, parent=None):
        super(XYScatter, self).__init__(parent)
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.splitter.setSizes(dpi.width_by_height(280, 720))

        self.comboBox_lineStyle.setItemIcon(0, QtGui.QIcon(os.path.join(cfg.icon_path, "xyline.svg")))
        self.comboBox_lineStyle.setItemIcon(1, QtGui.QIcon(os.path.join(cfg.icon_path, "xypoints.svg")))

        self.treeView_datasets.setItemClass(DFItem)
        self.treeView_datasets.supportedClasses = self.supportedClasses

        self.treeView_datasets.model().itemsAdded.connect(self.addCurves)
        self.treeView_datasets.model().itemAccessorChanged.connect(self.itemDataChanged)
        self.treeView_datasets.model().itemAccessorChanged.connect(self.legendSelectionChanged)
        self.treeView_datasets.model().itemsDeleted.connect(self.processNewLayout)
        self.treeView_datasets.model().rowsMoved.connect(self.processNewLayout)
        self.treeView_datasets.model().itemToggled.connect(self.itemToggled)
        self.treeView_datasets.model().itemTextUpdated.connect(self.legendSelectionChanged)
        self.comboBox_lineStyle.currentIndexChanged.connect(self.setLineStyle)
        self.lineEdit_xlabel.textChanged.connect(self.setXLabel)
        self.lineEdit_ylabel.textChanged.connect(self.setYLabel)

        for checkBox in (self.checkBox_legend_dfname, self.checkBox_legend_label, self.checkBox_legend_ycolumn):
            checkBox.stateChanged.connect(self.legendSelectionChanged)
        self.groupBox_Legend.toggled.connect(self.toggleLegend)

        self._colors = None
        self.resetColors()

        self.alphaChanged = pg.SignalProxy(self.slider_alpha.valueChanged, slot=self.setAlpha, delay=0.05)
        self.slider_alpha.valueChanged.connect(self.label_alphaValue.setNum)

    def legendSelectionChanged(self):
        for item in self.treeView_datasets.model().dflist:  # type: DFItem
            item.setLegend(
                self.checkBox_legend_dfname.isChecked(),
                self.checkBox_legend_label.isChecked(),
                self.checkBox_legend_ycolumn.isChecked(),
            )
            self.plotWidget.plotItem.resetLegend()

    def toggleLegend(self, on: bool):
        if on:
            self.plotWidget.plotItem.resetLegend()
        else:
            self.plotWidget.plotItem.removeLegend()

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
            for item in self.treeView_datasets.iterItems():  # type: DFItem
                color = "{:s}{:02x}".format(item.color, self.slider_alpha.value())
                item.plotDataItem.setData(symbolPen=color, symbol='o', symbolSize=5)
                item.plotDataItem.setPen(None)
        else:
            for item in self.treeView_datasets.iterItems():  # type: DFItem
                item.plotDataItem.setData(symbolPen=None, symbol=None)
                item.plotDataItem.setPen(item.color)

    def nextColor(self):
        return next(self._colors)

    def resetColors(self):
        self._colors = colors.colors()

    def itemDataChanged(self, item: DFItem):
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
        """process checking/unchecking of a StructuredDataFrame in the plot

        Parameters
        ----------
        item : DFItem

        """
        if item.checkState:
            item.plotDataItem.setData(
                x=item.x_data(),
                y=item.y_data(),
            )
            item.setLegend(self.checkBox_legend_dfname.isChecked(), self.checkBox_legend_label.isChecked(),
                           self.checkBox_legend_ycolumn.isChecked())
        else:
            item.plotDataItem.setData(name=None)
            item.plotDataItem.clear()
        self.plotWidget.plotItem.resetLegend()

    def addCurves(self, items):
        """
        Parameters
        ----------
        items : list of DFItem
        """
        if self.useSymbols():
            for item in items:  # type: DFItem
                item.color = self.nextColor()
                item.plotDataItem.setData(pen=None, symbol='o', symbolPen=item.color, symbolBrush=None)
                item.setLegend(self.checkBox_legend_dfname.isChecked(), self.checkBox_legend_label.isChecked(),
                               self.checkBox_legend_ycolumn.isChecked())
                item.plotDataItem.updateItems()
                self.plotWidget.plotItem.addItem(item.plotDataItem)
        else:
            alpha = self.slider_alpha.value()
            for item in items:
                item.color = self.nextColor()
                color = "{:s}{:02x}".format(item.color, alpha)
                item.plotDataItem.setData(pen=color, symbol=None, symbolPen=None, symbolBrush=None)
                item.setLegend(self.checkBox_legend_dfname.isChecked(), self.checkBox_legend_label.isChecked(),
                               self.checkBox_legend_ycolumn.isChecked())
                item.plotDataItem.updateItems()
                self.plotWidget.plotItem.addItem(item.plotDataItem)


def test():
    import sys
    from ...plugins import examples
    from ..masterdftree import DFReference
    app = fn.instantiate_app()
    fn.reset_excepthook()
    cfg.set_dpi_scaling()

    df = examples.example_powderdiffraction()
    ref1 = DFReference(df, None)

    plot = XYScatter()
    plot.treeView_datasets.addDataFrames(ref1, ref1, ref1)
    plot.show()

    sys.exit(app.exec_())
