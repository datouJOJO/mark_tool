# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'analysis_window.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_welcome_window = QtWidgets.QAction(MainWindow)
        self.action_welcome_window.setObjectName("action_welcome_window")
        self.actionmanual_marking = QtWidgets.QAction(MainWindow)
        self.actionmanual_marking.setObjectName("actionmanual_marking")
        self.actionmachine_marking = QtWidgets.QAction(MainWindow)
        self.actionmachine_marking.setObjectName("actionmachine_marking")
        self.actionpre_making = QtWidgets.QAction(MainWindow)
        self.actionpre_making.setObjectName("actionpre_making")
        self.menu.addAction(self.action_welcome_window)
        self.menu.addAction(self.actionmanual_marking)
        self.menu.addAction(self.actionmachine_marking)
        self.menu.addAction(self.actionpre_making)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "&菜单"))
        self.menu_2.setTitle(_translate("MainWindow", "&说明"))
        self.action_welcome_window.setText(_translate("MainWindow", "&welcome_window"))
        self.actionmanual_marking.setText(_translate("MainWindow", "manual_marking"))
        self.actionmachine_marking.setText(_translate("MainWindow", "machine_marking"))
        self.actionpre_making.setText(_translate("MainWindow", "pre_making"))

