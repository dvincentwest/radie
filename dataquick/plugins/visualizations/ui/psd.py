# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Coding\Python\PythonPackageLinks\dataquick\plugins\visualizations\ui\psd.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PSD(object):
    def setupUi(self, PSD):
        PSD.setObjectName("PSD")
        PSD.resize(1000, 561)
        self.verticalLayout = QtWidgets.QVBoxLayout(PSD)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(PSD)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_left = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_left.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_left.setObjectName("verticalLayout_left")
        self.listView_datasets = DQFListView(self.layoutWidget)
        self.listView_datasets.setObjectName("listView_datasets")
        self.verticalLayout_left.addWidget(self.listView_datasets)
        self.plotWidget = PlotWidget(self.splitter)
        self.plotWidget.setObjectName("plotWidget")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(PSD)
        QtCore.QMetaObject.connectSlotsByName(PSD)

    def retranslateUi(self, PSD):
        _translate = QtCore.QCoreApplication.translate
        PSD.setWindowTitle(_translate("PSD", "Particle Size Distribution"))

from dataquick.qt.plotlist import DQFListView
from dataquick.qt.plotwidget import PlotWidget
