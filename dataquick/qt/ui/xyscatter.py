# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Coding\Python\PythonPackageLinks\dataquick\qt\ui\xyscatter.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_XYScatter(object):
    def setupUi(self, XYScatter):
        XYScatter.setObjectName("XYScatter")
        XYScatter.resize(1000, 561)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(XYScatter)
        self.verticalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(XYScatter)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView_datasets = DQFXYListView(self.layoutWidget)
        self.treeView_datasets.setObjectName("treeView_datasets")
        self.verticalLayout.addWidget(self.treeView_datasets)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_lineStyle = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_lineStyle.setObjectName("comboBox_lineStyle")
        self.comboBox_lineStyle.addItem("")
        self.comboBox_lineStyle.addItem("")
        self.horizontalLayout.addWidget(self.comboBox_lineStyle)
        self.label_alpha = QtWidgets.QLabel(self.layoutWidget)
        self.label_alpha.setObjectName("label_alpha")
        self.horizontalLayout.addWidget(self.label_alpha)
        self.slider_alpha = QtWidgets.QSlider(self.layoutWidget)
        self.slider_alpha.setMaximum(255)
        self.slider_alpha.setProperty("value", 255)
        self.slider_alpha.setOrientation(QtCore.Qt.Horizontal)
        self.slider_alpha.setObjectName("slider_alpha")
        self.horizontalLayout.addWidget(self.slider_alpha)
        self.label_alphaValue = QtWidgets.QLabel(self.layoutWidget)
        self.label_alphaValue.setObjectName("label_alphaValue")
        self.horizontalLayout.addWidget(self.label_alphaValue)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.formLayout_plotOptions = QtWidgets.QFormLayout()
        self.formLayout_plotOptions.setObjectName("formLayout_plotOptions")
        self.label_xlabel = QtWidgets.QLabel(self.layoutWidget)
        self.label_xlabel.setObjectName("label_xlabel")
        self.formLayout_plotOptions.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_xlabel)
        self.lineEdit_xlabel = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_xlabel.setObjectName("lineEdit_xlabel")
        self.formLayout_plotOptions.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_xlabel)
        self.lineEdit_ylabel = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_ylabel.setObjectName("lineEdit_ylabel")
        self.formLayout_plotOptions.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_ylabel)
        self.label_ylabel = QtWidgets.QLabel(self.layoutWidget)
        self.label_ylabel.setObjectName("label_ylabel")
        self.formLayout_plotOptions.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_ylabel)
        self.verticalLayout.addLayout(self.formLayout_plotOptions)
        self.plotWidget = PlotWidget(self.splitter)
        self.plotWidget.setObjectName("plotWidget")
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(XYScatter)
        QtCore.QMetaObject.connectSlotsByName(XYScatter)

    def retranslateUi(self, XYScatter):
        _translate = QtCore.QCoreApplication.translate
        XYScatter.setWindowTitle(_translate("XYScatter", "DataFrames"))
        self.comboBox_lineStyle.setItemText(0, _translate("XYScatter", "line"))
        self.comboBox_lineStyle.setItemText(1, _translate("XYScatter", "points"))
        self.label_alpha.setText(_translate("XYScatter", "Scatter Alpha"))
        self.label_alphaValue.setText(_translate("XYScatter", "255"))
        self.label_xlabel.setText(_translate("XYScatter", "X-Label"))
        self.label_ylabel.setText(_translate("XYScatter", "Y-Label"))

from dataquick.qt.plotlist import DQFXYListView
from dataquick.qt.plotwidget import PlotWidget
