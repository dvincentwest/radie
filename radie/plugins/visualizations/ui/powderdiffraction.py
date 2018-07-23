# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Coding\Python\PythonPackageLinks\radie\plugins\visualizations\ui\powderdiffraction.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PowderDiffraction(object):
    def setupUi(self, PowderDiffraction):
        PowderDiffraction.setObjectName("PowderDiffraction")
        PowderDiffraction.resize(1000, 561)
        self.verticalLayout = QtWidgets.QVBoxLayout(PowderDiffraction)
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(PowderDiffraction)
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
        self.comboBox_xValues = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_xValues.setObjectName("comboBox_xValues")
        self.formLayout_parameters.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.comboBox_xValues)
        self.checkBox_xStagger = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox_xStagger.setObjectName("checkBox_xStagger")
        self.formLayout_parameters.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.checkBox_xStagger)
        self.checkBox_yStagger = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox_yStagger.setObjectName("checkBox_yStagger")
        self.formLayout_parameters.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.checkBox_yStagger)
        self.checkBox_normalize = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox_normalize.setObjectName("checkBox_normalize")
        self.formLayout_parameters.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.checkBox_normalize)
        self.doubleSpinBox_xStagger = QtWidgets.QDoubleSpinBox(self.layoutWidget)
        self.doubleSpinBox_xStagger.setMaximum(1000.0)
        self.doubleSpinBox_xStagger.setSingleStep(5.0)
        self.doubleSpinBox_xStagger.setObjectName("doubleSpinBox_xStagger")
        self.formLayout_parameters.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_xStagger)
        self.doubleSpinBox_yStagger = QtWidgets.QDoubleSpinBox(self.layoutWidget)
        self.doubleSpinBox_yStagger.setMaximum(1000.0)
        self.doubleSpinBox_yStagger.setSingleStep(5.0)
        self.doubleSpinBox_yStagger.setObjectName("doubleSpinBox_yStagger")
        self.formLayout_parameters.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_yStagger)
        self.doubleSpinBox_wavelength = QtWidgets.QDoubleSpinBox(self.layoutWidget)
        self.doubleSpinBox_wavelength.setDecimals(6)
        self.doubleSpinBox_wavelength.setMinimum(0.01)
        self.doubleSpinBox_wavelength.setSingleStep(0.1)
        self.doubleSpinBox_wavelength.setProperty("value", 1.54)
        self.doubleSpinBox_wavelength.setObjectName("doubleSpinBox_wavelength")
        self.formLayout_parameters.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_wavelength)
        self.verticalLayout_left.addLayout(self.formLayout_parameters)
        self.plotWidget = PlotWidget(self.splitter)
        self.plotWidget.setObjectName("plotWidget")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(PowderDiffraction)
        QtCore.QMetaObject.connectSlotsByName(PowderDiffraction)

    def retranslateUi(self, PowderDiffraction):
        _translate = QtCore.QCoreApplication.translate
        PowderDiffraction.setWindowTitle(_translate("PowderDiffraction", "PowderDiffraction"))
        self.checkBox_xStagger.setText(_translate("PowderDiffraction", "X-Stagger (%)"))
        self.checkBox_yStagger.setText(_translate("PowderDiffraction", "Y-Stagger (%)"))
        self.checkBox_normalize.setText(_translate("PowderDiffraction", "Normalize intensity"))

from radie.qt.plotlist import DFListView
from radie.qt.plotwidget import PlotWidget
