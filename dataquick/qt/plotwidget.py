"""Customize the Basic PyQtGraph PlotWidget with styles and helpful functions"""

import types

import pyqtgraph as pg


class PlotWidget(pg.PlotWidget):
    def __init__(self, parent=None, background="default", **kwargs):
        super(PlotWidget, self).__init__(parent, background, **kwargs)

        # bolt on my PlotItem additions, for some reason all attempts to subclass don't really work
        self.plotItem.setupPlot = types.MethodType(PlotItem.setupPlot, self.plotItem)
        self.plotItem.resetLegend = types.MethodType(PlotItem.resetLegend, self.plotItem)
        self.plotItem.removeLegend = types.MethodType(PlotItem.removeLegend, self.plotItem)
        self.plotItem.setupPlot()


class PlotItem(pg.PlotItem):
    def __init__(self, *args, **kwargs):
        super(PlotItem, self).__init__(*args, **kwargs)
        self.setupPlot()

    def setupPlot(self):
        """
        A universal style for datauick plots

        Parameters
        ----------
        self : pg.PlotItem

        """
        self.addLegend()
        self.showAxis('top')
        self.showAxis('right')
        self.showGrid(True, True, 0.1)
        self.getAxis('top').setStyle(showValues=False)
        self.getAxis('right').setStyle(showValues=False)
        self.vb.setMouseMode(pg.ViewBox.RectMode)

    def removeLegend(self):
        """remove the legend"""
        legend = self.legend
        try:
            legend.scene().removeItem(legend)
            self.legend = None
        except AttributeError:
            pass

    def resetLegend(self):
        """
        clear out the old legend, add a new one and repopulate

        Parameters
        ----------
        self : pg.PlotItem

        Returns
        -------

        """
        self.removeLegend()
        self.addLegend()

        for item in self.listDataItems():
            if item.name() is not None:
                self.legend.addItem(item, item.name())
