# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'seaddialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog

class Ui_seedDialog(QDialog):

    def __init__(self, parent=None):
        super(Ui_Dialog, self).__init__(parent)
        self.setupUis(self)


    def setupUis(self, seedDialog):
        seedDialog.setObjectName("seedDialog")
        seedDialog.resize(260, 168)
        self.buttonBox = QtWidgets.QDialogButtonBox(seedDialog)
        self.buttonBox.setGeometry(QtCore.QRect(0, 110, 231, 61))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setMinimumSize(QtCore.QSize(231, 61))
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.spinBox = QtWidgets.QSpinBox(seedDialog)
        self.spinBox.setGeometry(QtCore.QRect(60, 60, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.spinBox.setFont(font)
        self.spinBox.setWrapping(False)
        self.spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.spinBox.setMaximum(1400)
        self.spinBox.setSingleStep(50)
        self.spinBox.setDisplayIntegerBase(10)
        self.spinBox.setObjectName("spinBox")
        self.label_2 = QtWidgets.QLabel(seedDialog)
        self.label_2.setGeometry(QtCore.QRect(180, 60, 41, 31))
        font = QtGui.QFont()
        font.setPointSize(23)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.retranslateUis(seedDialog)
        self.buttonBox.accepted.connect(seedDialog.accept)
        self.buttonBox.rejected.connect(seedDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(seedDialog)

    def retranslateUis(self, seedDialog):
        _translate = QtCore.QCoreApplication.translate
        seedDialog.setWindowTitle(_translate("seedDialog", "Dialog"))
        self.label_2.setText(_translate("seedDialog", "V"))
