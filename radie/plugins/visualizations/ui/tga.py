# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\a2nldzz\Documents\repos\radie\radie\plugins\visualizations\ui\tga.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TGA(object):
    def setupUi(self, TGA):
        TGA.setObjectName("TGA")
        TGA.resize(1000, 561)
        self.verticalLayout = QtWidgets.QVBoxLayout(TGA)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(TGA)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_left = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_left.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_left.setObjectName("verticalLayout_left")
        self.listView_datasets = DFListView(self.layoutWidget)
        self.listView_datasets.setObjectName("listView_datasets")
        self.verticalLayout_left.addWidget(self.listView_datasets)
        self.formLayout_parameters = QtWidgets.QFormLayout()
        self.formLayout_parameters.setObjectName("formLayout_parameters")
        self.comboBox_y1 = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_y1.setObjectName("comboBox_y1")
        self.formLayout_parameters.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.comboBox_y1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout_parameters.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.label_2)
        self.comboBox_y2 = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_y2.setObjectName("comboBox_y2")
        self.formLayout_parameters.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.comboBox_y2)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.formLayout_parameters.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_3)
        self.checkBox_normalizeWeight = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox_normalizeWeight.setObjectName("checkBox_normalizeWeight")
        self.formLayout_parameters.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.checkBox_normalizeWeight)
        self.comboBox_x = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_x.setObjectName("comboBox_x")
        self.formLayout_parameters.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.comboBox_x)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.formLayout_parameters.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.label)
        self.verticalLayout_left.addLayout(self.formLayout_parameters)
        self.plotWidget = PlotWidget(self.splitter)
        self.plotWidget.setObjectName("plotWidget")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(TGA)
        QtCore.QMetaObject.connectSlotsByName(TGA)

    def retranslateUi(self, TGA):
        _translate = QtCore.QCoreApplication.translate
        TGA.setWindowTitle(_translate("TGA", "TGA"))
        self.label_2.setText(_translate("TGA", "Primary Vertical Axis"))
        self.label_3.setText(_translate("TGA", "Secondary Vertical Axis"))
        self.checkBox_normalizeWeight.setText(_translate("TGA", "Normalize weight"))
        self.label.setText(_translate("TGA", "Horizontal Axis"))

from radie.qt.plotlist import DFListView
from radie.qt.plotwidget import PlotWidget
