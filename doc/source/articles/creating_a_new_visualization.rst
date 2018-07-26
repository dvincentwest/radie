Creating A New Visualization
============================

*a quick note*: DF stands for :doc:`StructuredDataFrame </api/dataframe>`

This article will demonstrate the creation of a new QWidget based visualization
for dataframes, that can be included into the Radie Viewer, written in
PyQt. It will be a simple version of the included xy scatter plot
(:code:`radie.qt.visualizations.xyscatter`)

The code for this article can be found as a plugin module that can be used as a
starting template for creating new visualizations. See
`radie.plugins.visualizations.xyscatter_demo
<https://github.com/dvincentwest/radie/blob/master/radie/plugins/visualizations/xyscatter_demo.py>`_.

It should be noted that a lot of this is GUI programming and can be a real
grind.  The widget below is quite simple.  The complex functionality provided in
some of the other available visualizations will illustrate the PyQt code
necessary to expand interesting functionality.

The Basic Idea
--------------

Schematically our visualization will look something like this:

.. figure:: /_images/example_plot.svg
    :width: 50%

    figure 1: a basic visualization in Radie, consisting of an interactive
    List of datasets and an xy graph of the datasets on the right.

The list on the left is particularly important for the intended workflow.  It
allows drag and drop control of the datasets, adding and removing datasets to
the visualization rapidly, in addition to quickly reordering and unchecking the
datasets in the visualization, and also selecting the columns of data from the
dataset. Radie provides some built-in widgets that can be used for this list
of datasets (:doc:`/api/plotlist`)

List of DataItems
-----------------

first we setup the imports:

.. code:: python

    import os

    from PyQt5 import QtCore, QtWidgets
    import pyqtgraph as pg

    from radie.qt.visualizations import base, register_visualizations
    from radie.qt import dpi, cfg, colors, plotlist
    from radie.qt.plotlist import DFXYListView
    from radie.qt.plotwidget import PlotWidget
    from radie.qt import functions as fn

The plotting library used is pyqtgraph_.  This is not required, but recommended.
You can of course use matplotlib_, but you should also consider other options
such as vispy_, or any visualization library that plays nicely with PyQt.

.. _pyqtgraph: http://www.pyqtgraph.org
.. _matplotlib: https://matplotlib.org/
.. _vispy: http://vispy.org/

:code:`PlotWidget` is a simple `pyqtgraph.PlotWidget` subclass with some minor
formatting and conveniences thrown in.

More important are the imports from the :doc:`plotlist module</api/plotlist>`.
:code:`DFXYListView` is a subclass of :code:`DFListView`.  The class is a
`QTreeView` built to use the custom model :code:`DFListModel`.  All of these
are used for the list of datasets on the left in figure 1 above.  The code is
quite complex, and it is highly recommended to use these widgets either directly
or through subclassing when creating your own visualizations

In order for the list to be fully functional, it needs a container object for
each item in the list.  A base :code:`DFItem` class is defined in the
:code:`plotlist` module.  However it must be subclassed in each visualization
module to accomodate the specific handles needed for each item in the plot.  In
this case:

.. code:: python

    class DFItem(plotlist.DFItem):
        """an item class with pyqtgraph xy curve handles of type PlotDataItem"""
        def __init__(self, ref, item_list, name=None):
            super(DFItem, self).__init__(ref, item_list, name)
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

See the api reference for more detail, but as quick overview, the `DFItem` is a
bookeeping object that keeps track of:

  * the dataframe containing the data, and references to active columns
  * visualization handles for the data, in this case, :code:`pg.PlotDataItem`
  * visualization states of the items (checked or not, etc.)

The class can be extended to accomodate whatever is necessary for a custom
visualization

The QWidget Visualization
-------------------------

Having setup the necessary bits we define the visualizaton widget as a subclass
of the base visualization.

.. code:: python

    class XYScatterDemo(base.Visualization):
        """A generic XY scatter visualization"""
        name = "XY Scatter Demo"
        description = "Generic visualization of XY curves from StructuredDataFrame Series"
        _icon_image = os.path.join(cfg.icon_path, "xyscatter.svg")

As per the usual, we modify the relevant class variables, tailored to our
visualization.  Next we define the constructor:

.. code:: python

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setupUi()

            # required before the list will accept any drops
            self.treeView_datasets.setItemClass(DFItem)

            self.treeView_datasets.model().itemsAdded.connect(self.addCurves)
            self.treeView_datasets.model().itemAccessorChanged.connect(
                self.itemDataChanged)
            self.treeView_datasets.model().itemsDeleted.connect(
                self.processNewLayout)
            self.treeView_datasets.model().rowsMoved.connect(
                self.processNewLayout)
            self.treeView_datasets.model().itemToggled.connect(self.itemToggled)
            self.treeView_datasets.model().itemTextUpdated.connect(
                self.plotWidget.plotItem.resetLegend)

            self.lineEdit_xlabel.textChanged.connect(self.setXLabel)
            self.lineEdit_ylabel.textChanged.connect(self.setYLabel)

            self._colors = None
            self.resetColors()

In the :code:`__init__` methdod, there are a few points important to note.

First is that :code:`self.setupUi` is responsible for building all the elements
of the widgets.  It is in this method that the `TreeView` and `PlotWidget`
elements discussed above are instantiated for the visualization.  Beyond that,
the rest is just PyQt gui programming.

Second is all the code related to the TreeView, namely
:code:`self.treeView_datasets`.  The only essential line is the call to
:code:`DFTreeView.setItemClass`.  Before the TreeView can accept any
DataFrames dropped onto it, it must know which object class it is using to
contain the references.  It will not allow any drops until this function has
been called.

Next is the connecting of all the signals emitted when data in the list are
changed in some fashion.  The signals are all fairly self-explanatory, and are
all emitted by the `DFTreeModel` attached to the TreeView.

The remaining code is specific to the elements of this visualization, as is the
:code:`setupUi` method documented below:

.. code:: python

        def setupUi(self):
            self.setWindowTitle("XY Scatter Plot")
            self.resize(800, 450)

            self.verticalLayout_main = QtWidgets.QVBoxLayout(self)
            self.verticalLayout_main.setContentsMargins(3, 3, 3, 3)
            self.splitter = QtWidgets.QSplitter(self)
            self.splitter.setOrientation(QtCore.Qt.Horizontal)
            self.layoutWidget = QtWidgets.QWidget(self.splitter)  # left half
            self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
            self.verticalLayout.setContentsMargins(0, 0, 0, 0)
            self.treeView_datasets = DFXYListView(self.layoutWidget)
            self.verticalLayout.addWidget(self.treeView_datasets)
            self.formLayout_plotOptions = QtWidgets.QFormLayout()
            self.label_xlabel = QtWidgets.QLabel("X-Label", self.layoutWidget)
            self.formLayout_plotOptions.setWidget(
                0, QtWidgets.QFormLayout.LabelRole, self.label_xlabel)
            self.lineEdit_xlabel = QtWidgets.QLineEdit(self.layoutWidget)
            self.formLayout_plotOptions.setWidget(
                0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_xlabel)
            self.lineEdit_ylabel = QtWidgets.QLineEdit(self.layoutWidget)
            self.formLayout_plotOptions.setWidget(
                1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_ylabel)
            self.label_ylabel = QtWidgets.QLabel("Y-Label", self.layoutWidget)
            self.formLayout_plotOptions.setWidget(
                1, QtWidgets.QFormLayout.LabelRole, self.label_ylabel)
            self.verticalLayout.addLayout(self.formLayout_plotOptions)
            self.plotWidget = PlotWidget(self.splitter)
            self.verticalLayout_main.addWidget(self.splitter)

            self.splitter.setStretchFactor(0, 0)
            self.splitter.setStretchFactor(1, 1)
            self.splitter.setSizes(dpi.width_by_height(280, 720))

The rest of the methods of the Visualization class relate to the specifics of
this particular visualization, rather than any general requirements or
convenience classes of the radie viewer, from here on out it is an exercise
of gui programming. As long as it stays within the widget and plays nice with
the rest of the Viewer program it can be as simple or as complex as the designer
wishes.

.. code:: python

        def setAxisLabel(self, axis: str, text: str):
            if not text:
                self.plotWidget.plotItem.showLabel(axis, False)
                return
            self.plotWidget.setLabel(axis=axis, text=text)

        def setXLabel(self, text: str):
            self.setAxisLabel("bottom", text)

        def setYLabel(self, text: str):
            self.setAxisLabel("left", text)

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

        def itemToggled(self, item):
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

        def processNewLayout(self):
            self.plotWidget.plotItem.clear()
            self.plotWidget.plotItem.resetLegend()
            for item in self.treeView_datasets.iterItems():
                self.plotWidget.addItem(item.plotDataItem)

        def addCurves(self, items):
            """main function for adding new curves to the plot

            Parameters
            ----------
            items : list of DFItem
            """
            for item in items:
                item.color = self.nextColor()
                item.plotDataItem.setData(pen=item.color)
                item.plotDataItem.updateItems() 
                self.plotWidget.plotItem.addItem(item.plotDataItem)

Wrapping it up
--------------

The last remaining item required is registering the visualization class with the
main module.  This is done by a call to
:code:`radie.qt.visualizations.register_visualizations`

.. code:: python

    register_visualizations(XYScatterDemo)

This call will create a menu entry that the user can use to create a new
visualization window and add dataframes to it.

Testing the widget
------------------

below is some example code that can be used to create this widget as a
standalone window and add some example dataframes to it.  Note that this code
will fail if any of the imports are relative.  Note that in the code below we
do not add DataFrames directly to the Visualizations, but rather first we
wrap them in a reference object called a :code:`DFReference`.  See the
:doc:`relevant api documentation</api/masterdftree>` for more details.

.. code:: python

    if __name__ == "__main__":
        import sys
        from radie.plugins import examples
        from radie.qt.masterdftree import DFReference
        app = fn.instantiate_app()
        fn.reset_excepthook()  # PyQt5 exists silently, sucks for debugging

        df1 = examples.example_powderdiffraction()
        df1.metadata["name"] = "xrd1"
        df2 = examples.example_powderdiffraction()
        df2.metadata["name"] = "xrd2"
        df2["intensity"] += 10
        df2["intensity"] *= 1.1
        ref1 = DFReference(df1, None)
        ref2 = DFReference(df2, None)

        plot = XYScatterDemo()
        plot.treeView_datasets.addDataFrames(ref1, ref2)
        plot.show()

        sys.exit(app.exec_())

The final result looks like this:

.. image:: /_images/example_visualization.png
