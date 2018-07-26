"""module to define dflistview, using the QAbstractListModel"""
import typing

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from ..structures import StructuredDataFrame
from .indexabledict import IndexableDict
from .errors import DFTypeError
from .masterdftree import DFReference
from . import functions as fn


class DFItem(object):
    def __init__(self, ref, item_list, name=None):
        """
        Parameters
        ----------
        ref : DFReference
        item_list : DFItemList
        name : str
        """
        self.ref = ref
        self.list = item_list
        self.checkState = QtCore.Qt.Checked
        self.text = name if name else self.ref.df.metadata["name"]
        self.accessors = IndexableDict(self.ref.df.column_accessors())
        self.x_accessor = self.accessors.getKey(self.ref.df.x_col)
        y_idx = self.ref.df.y_col
        if y_idx is None:
            self.y_accessor = None
        else:
            self.y_accessor = self.accessors.getKey(y_idx)
        z_idx = self.ref.df.z_col
        if z_idx is None:
            self.z_accessor = None
        else:
            self.z_accessor = self.accessors.getKey(z_idx)

    @property
    def df(self):
        return self.ref.df

    def x_data(self) -> np.ndarray:
        data = self.accessors[self.x_accessor]().values
        return data

    def y_data(self) -> np.ndarray:
        return self.accessors[self.y_accessor]().values

    def z_data(self) -> np.ndarray:
        return self.accessors[self.z_accessor]().values

    def setText(self, value):
        self.text = value

    def setCheckState(self, value):
        self.checkState = value

    def isChecked(self):
        return bool(self.checkState)


class DFItemList(list):
    def __init__(self, iterable=None):
        super(DFItemList, self).__init__()
        if not iterable:
            return

        for item in iterable:
            if not isinstance(object, DFItem):
                raise TypeError("Only DFReference objects are allowed")
            self.append(item)

        self._itemClass = None

    @property
    def itemClass(self):
        if not self._itemClass:
            raise AttributeError("itemClass attribute not yet assigned")
        return self._itemClass

    @itemClass.setter
    def itemClass(self, cls):
        if not issubclass(cls, DFItem):
            raise TypeError("cls must be a DFItem subclass not {:}".format(cls.__name__))
        self._itemClass = cls

    def append(self, ref):
        """append a new StructuredDataFrame to the List

        Parameters
        ----------
        ref : DFReference
        """
        if not isinstance(ref, DFReference):
            raise TypeError("Only DFReference objects are allowed, not type: {:}".format(type(DFReference)))
        item = self.itemClass(ref, self)
        super(DFItemList, self).append(item)

    def __setitem__(self, key, value):
        if not isinstance(value, DFReference):
            raise TypeError("Only DFReference objects are allowed")
        super(DFItemList, self).__setitem__(key, value)


class DFListModel(QtCore.QAbstractItemModel):
    """
    Define a generic Model for use with lists of DataFrames to be plotted.  This model is a QAbstractItemModel
    meant to define the behavior for a QListView.  It can however also be used with a QTreeView, but will probably
    require some custom behavior via a sub-class
    """

    itemsAdded = QtCore.pyqtSignal(object)
    itemToggled = QtCore.pyqtSignal(object)
    itemTextUpdated = QtCore.pyqtSignal(object)
    itemAccessorChanged = QtCore.pyqtSignal(object)
    itemsDeleted = QtCore.pyqtSignal()

    def __init__(self, dflist: DFItemList):
        super(DFListModel, self).__init__()
        if not isinstance(dflist, DFItemList):
            raise TypeError("DFListModel only supports DFItemLists")
        self.dflist = dflist  # type: DFItemList
        self._headers = ["Name", "x-data", "y-data"]
        self._columnCount = len(self._headers)

    def setColumnCount(self, value):
        self._columnCount = int(value)

    def columnCount(self, parent: QtCore.QModelIndex = None):
        return self._columnCount

    def setHeaders(self, headers: list):
        headers = [str(header) for header in headers]
        self._headers = headers
        self._columnCount = len(self._headers)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._headers[section]
        else:
            return None

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = None) -> QtCore.QModelIndex:
        if not parent:
            parent = QtCore.QModelIndex()

        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        index = self.createIndex(row, column, self.dflist)
        return index

    def parent(self, child: QtCore.QModelIndex):
        return QtCore.QModelIndex()

    def hasChildren(self, parent: QtCore.QModelIndex = None):
        if parent.row() == -1:
            return True
        else:
            return False

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.dflist)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        col = index.column()
        if col == 0:
            if role == QtCore.Qt.CheckStateRole:
                item = self.dflist[index.row()]  # type: DFItem
                return item.checkState
            elif role in (QtCore.Qt.EditRole, QtCore.Qt.DisplayRole):
                item = self.dflist[index.row()]  # type: DFItem
                return item.text

        elif col > 0 and role in (QtCore.Qt.EditRole, QtCore.Qt.DisplayRole):
            if col == 1:
                return str(self.dflist[index.row()].x_accessor)
            if col == 2:
                return str(self.dflist[index.row()].y_accessor)
            if col == 3:
                return str(self.dflist[index.row()].z_accessor)

        return QtCore.QVariant()

    def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int):
        item = self.dflist[index.row()]  # type: DFItem
        col = index.column()
        if role == QtCore.Qt.CheckStateRole:
            item.setCheckState(value)
            self.itemToggled.emit(item)
            return True
        elif role == QtCore.Qt.EditRole:
            if col == 0:
                item.setText(str(value))
                self.itemTextUpdated.emit(item)
                return True

            else:
                if col == 1:
                    item.x_accessor = value
                elif col == 2:
                    item.y_accessor = value
                elif col == 3:
                    item.z_accessor = value
                else:
                    return False
                self.itemAccessorChanged.emit(item)
                return True
        return False

    def flags(self, index: QtCore.QModelIndex):
        col = index.column()
        if col == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | \
                   QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | \
                   QtCore.Qt.ItemIsDropEnabled

    def removeRow(self, row: int, parent: QtCore.QModelIndex=None):
        if not parent:
            parent = QtCore.QModelIndex()
        self.beginRemoveRows(parent, row, row)
        del self.dflist[row]
        self.endRemoveRows()

    def removeRows(self, row: int, count: int, parent: QtCore.QModelIndex=None):
        if not parent:
            parent = QtCore.QModelIndex()
        first = row
        last = row + count - 1
        self.beginRemoveRows(parent, first, last)  # last row inclusive
        del self.dflist[row:last + 1]  # last row not inclusive
        self.endRemoveRows()

    def internalMove(self, dropIndex: QtCore.QModelIndex, movingIndexes: list):
        indexes = sorted(movingIndexes, key=lambda index: index.row())
        parent = QtCore.QModelIndex()

        first_row = indexes[0].row()
        last_row = indexes[-1].row()

        insert_row = dropIndex.row()
        if insert_row < 0:  # dragging to the end yields `insert_row = -1`
            insert_row = len(self.dflist)

        if first_row <= insert_row <= last_row + 1:
            return  # drop spot is in-between somewhere, no purpose in moving
            # and in fact and exception will occur if you try to move
            # and there is no change in the list

        if first_row > insert_row:
            self.beginMoveRows(parent, indexes[0].row(), insert_row, parent, insert_row)
            for index in indexes:  # type: QtCore.QModelIndex
                row = index.row()
                self.dflist.insert(insert_row, self.dflist.pop(row))
                insert_row += 1
        else:
            self.beginMoveRows(parent, insert_row, indexes[-1].row(), parent, insert_row)
            for index in indexes[::-1]:  # type: QtCore.QModelIndex
                row = index.row()
                self.dflist.insert(insert_row - 1, self.dflist.pop(row))
                insert_row -= 1
        self.endMoveRows()

    def addDataFrames(self, *refs):
        first = len(self.dflist)
        last = len(refs) - 1
        self.beginInsertRows(QtCore.QModelIndex(), first, last)
        for ref in refs:
            self.dflist.append(ref)
            ref.dfDeleted.connect(self.referencesDeleted)
        self.endInsertRows()
        self.itemsAdded.emit(self.dflist[first:])

    def referencesDeleted(self, ref: DFReference):
        """This method is called with DFReference objects are about to be deleted globally"""
        for i in reversed(range(len(self.dflist))):
            item = self.dflist[i]  # type: DFItem
            if item.ref is ref:
                self.removeRow(i)
                # do not break out of this loop as a plot-list may contain multiple references to the same DF
        self.itemsDeleted.emit()

    def deleteSelectedRows(self, indexes: list):
        selected = sorted(indexes, key=lambda index: index.row())
        rows = [index.row() for index in selected]
        differences = [rows[i + 1] - rows[i] for i in range(len(rows) - 1)]
        sections = list()
        sections.append([rows[0]])
        for diff, row in zip(differences, rows[1:]):
            if diff == 1:  # rows are contiguous:
                sections[-1].append(row)
            else:  # rows are not contiguous
                sections.append([row])
        for section in sections[::-1]:
            self.removeRows(section[0], len(section))
        self.itemsDeleted.emit()


class DFListView(QtWidgets.QTreeView):
    modelClass = DFListModel

    def __init__(self, parent=None):
        super(DFListView, self).__init__(parent)
        self.setSelectionMode(self.ExtendedSelection)
        self.setDragDropMode(self.DragDrop)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClicked)
        self.supportedClasses = (StructuredDataFrame,)  # support all StructuredDataFrame classes by default

        # normally this will be instantiated with no data, so let's set it up, but can be overridden by the user
        self.setRootIsDecorated(False)
        self.initializeModel()
        self.setHeaders(["Datasets"])

    def initializeModel(self):
        self.setModel(
            self.modelClass(
                DFItemList()
            )
        )

    def model(self) -> DFListModel:
        return super(DFListView, self).model()

    def setColumnCount(self, val):
        self.model().setColumnCount(val)

    def setHeaders(self, headers: list):
        self.model().setHeaders(headers)

    def setItemClass(self, cls):
        """
        Set the List-item class that holds the plotting data classes necessary for visualization

        Parameters
        ----------
        cls : type
        """
        self.model().dflist.itemClass = cls

    def setModel(self, model: DFListModel):
        if not isinstance(model, DFListModel):
            raise TypeError("This View only supports models of type {:}".format(DFListModel.__name__))
        super(DFListView, self).setModel(model)

    def isSupported(self, ref: DFReference):
        supported = isinstance(ref.df, self.supportedClasses)
        return supported

    def addDataFrames(self, *refs: DFReference):
        for ref in refs:
            cls = ref.df.__class__
            if not issubclass(cls, self.supportedClasses):
                raise DFTypeError("This List does not support classes of type: {:}".format(cls))
        self.model().addDataFrames(*refs)

    def iterItems(self):
        """
        provide a convenient API to iterate over all the items presented in this view

        Yields
        -------
        DFItem

        """
        for item in self.model().dflist:  # type DFItem
            yield item

    def deleteSelected(self):
        self.model().deleteSelectedRows(self.selectionModel().selectedRows(0))

    def rightClicked(self, pos: QtCore.QPoint):
        menu = QtWidgets.QMenu()

        selected_rows = self.selectionModel().selectedRows(column=0)
        num_dataframes = len(selected_rows)

        if num_dataframes > 0:
            if num_dataframes == 1:
                deleteItem = QtWidgets.QAction("Delete StructuredDataFrame")
            else:
                deleteItem = QtWidgets.QAction("Delete DataFrames")
            deleteItem.triggered.connect(self.deleteSelected)
            menu.addAction(deleteItem)

        menu.exec_(self.mapToGlobal(pos))  # QtWidgets.QAction

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        else:
            super(DFListView, self).dragEnterEvent(event)

    def row(self, item):
        """

        Parameters
        ----------
        item : DFItem

        Returns
        -------
        int
        """
        return self.model().dflist.index(item)

    def dropEvent(self, event: QtGui.QDropEvent):
        source = event.source()  # type: QtWidgets.QAbstractItemView
        if source is self:  # internal move operation
            super(DFListView, self).dropEvent(event)
            pos = event.pos()
            dropIndex = source.indexAt(pos)
            source.model().internalMove(dropIndex, source.selectionModel().selectedRows(0))
        else:
            if isinstance(source, QtWidgets.QTreeView):
                invalid_drops = []
                valid_drops = []
                for index in source.selectionModel().selectedRows(column=0):  # type: QtCore.QModelIndex
                    pointer = index.internalPointer()  # type: DFReference
                    if self.isSupported(pointer):
                        valid_drops.append(pointer)
                    elif isinstance(pointer, DFReference):
                        invalid_drops.append(pointer.df.__class__.__name__)
                    else:
                        continue

                if valid_drops:
                    self.addDataFrames(*valid_drops)

                if invalid_drops:
                    fn.error_popup(
                        "Invalid StructuredDataFrame types: \n\t" + "\n\t".join(invalid_drops) +
                        "\n\nOnly DataFrames of the following types are allowed:\n\t" +
                        "\n\t".join(cls.__name__ for cls in self.supportedClasses)
                    )


class DFAccessorDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(DFAccessorDelegate, self).__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        comboBox = QtWidgets.QComboBox(parent)
        dflist = index.internalPointer()  # type: DFItemList
        item = dflist[index.row()]  # type: DFItem
        comboBox.addItems(list(map(str, item.accessors.keys())))
        comboBox.currentIndexChanged.connect(self.currentIndexChanged)
        return comboBox

    def setEditorData(self, editor: QtWidgets.QComboBox, index: QtCore.QModelIndex):
        editor.blockSignals(True)
        dflist = index.internalPointer()  # type: DFItemList
        item = dflist[index.row()]  # type: DFItem
        column = index.column()
        if column == 1:
            editor.setCurrentIndex(editor.findText(str(item.x_accessor)))
        elif column == 2:
            editor.setCurrentIndex(editor.findText(str(item.y_accessor)))
        elif column == 3:
            editor.setCurrentIndex(editor.findText(str(item.z_accessor)))
        editor.blockSignals(False)

    def setModelData(self, editor: QtWidgets.QComboBox, model: DFListModel, index: QtCore.QModelIndex):
        item = index.internalPointer()[index.row()]
        model.setData(index, item.accessors.getKey(editor.currentIndex()), QtCore.Qt.EditRole)

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


class DFSeriesListView(DFListView):
    def __init__(self, parent=None):
        super(DFSeriesListView, self).__init__(parent)
        self.setHeaders(["Name", "Series"])
        self.setItemDelegateForColumn(1, DFAccessorDelegate(self))


class DFXYListView(DFListView):
    def __init__(self, parent=None):
        super(DFXYListView, self).__init__(parent)
        self.setHeaders(["Label", "x-data", "y-data"])
        self.setItemDelegateForColumn(1, DFAccessorDelegate(self))
        self.setItemDelegateForColumn(2, DFAccessorDelegate(self))


def test(tree=False):
    """
    Instantiate a DFTreeView, add in some data and test the drag and drop
    features.
    """
    from ..plugins.examples import example_powderdiffraction, example_vsm
    from .masterdftree import DFTreeView
    import sys
    df1 = example_powderdiffraction(); df1.name = "Ferrite 1"
    df2 = example_powderdiffraction(); df2.name = "Ferrite 2"
    df3 = example_powderdiffraction(); df3.name = "Ferrite 3"
    df4 = example_vsm(); df4.name = "VSM 1"
    df5 = example_vsm(); df5.name = "VSM 2"
    app = QtWidgets.QApplication([])

    def excepthook_(val, type, tb):
        return sys.__excepthook__(val, type, tb)
    sys.excepthook = excepthook_

    widget = QtWidgets.QWidget()
    hlay = QtWidgets.QHBoxLayout(widget)

    tv = DFTreeView()
    tv.addDataFrame(df1)
    tv.addDataFrame(df2)
    tv.addDataFrame(df3)
    tv.addDataFrame(df4)
    tv.addDataFrame(df5)

    if not tree:
        lv = DFListView()
    else:
        lv = DFXYListView()
    lv.setItemClass(DFItem)  # cannot add items to the list before calling this
    hlay.addWidget(tv)
    hlay.addWidget(lv)

    widget.show()
    sys.exit(app.exec_())
