# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Users\minorua\.qgis3\python\developing_plugins\Qgis2threejs\ui\widgetComboEdit.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ComboEditWidget(object):
    def setupUi(self, ComboEditWidget):
        ComboEditWidget.setObjectName("ComboEditWidget")
        ComboEditWidget.resize(235, 58)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ComboEditWidget.sizePolicy().hasHeightForWidth())
        ComboEditWidget.setSizePolicy(sizePolicy)
        ComboEditWidget.setMinimumSize(QtCore.QSize(50, 0))
        self.formLayout = QtWidgets.QFormLayout(ComboEditWidget)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 2, 0, 2)
        self.formLayout.setObjectName("formLayout")
        self.label_1 = QtWidgets.QLabel(ComboEditWidget)
        self.label_1.setMinimumSize(QtCore.QSize(50, 0))
        self.label_1.setObjectName("label_1")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox = QtWidgets.QComboBox(ComboEditWidget)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.checkBox = QtWidgets.QCheckBox(ComboEditWidget)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout.addWidget(self.checkBox)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_2 = QtWidgets.QLabel(ComboEditWidget)
        self.label_2.setMinimumSize(QtCore.QSize(50, 0))
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.expression = QgsFieldExpressionWidget(ComboEditWidget)
        self.expression.setObjectName("expression")
        self.horizontalLayout_2.addWidget(self.expression)
        self.toolButton = QtWidgets.QToolButton(ComboEditWidget)
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout_2.addWidget(self.toolButton)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_2)

        self.retranslateUi(ComboEditWidget)
        QtCore.QMetaObject.connectSlotsByName(ComboEditWidget)
        ComboEditWidget.setTabOrder(self.comboBox, self.checkBox)
        ComboEditWidget.setTabOrder(self.checkBox, self.toolButton)

    def retranslateUi(self, ComboEditWidget):
        _translate = QtCore.QCoreApplication.translate
        ComboEditWidget.setWindowTitle(_translate("ComboEditWidget", "Form"))
        self.toolButton.setText(_translate("ComboEditWidget", "..."))

from qgis.gui import QgsFieldExpressionWidget
