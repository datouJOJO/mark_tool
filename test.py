# coding=utf-8
from PyQt5 import QtWidgets

import welcome

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QFileDialog
import sys
import time
from PyQt5.QtGui import QPixmap

from analy import MainWindow as MainWindow4
from machine import MainWindow as MainWindow3
import analysis_window
from manual import MainWindow as MainWindow2
from pre import MainWindow as MainWindow5


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        ui = welcome.Ui_MainWindow()
        ui.setupUi(self)

    def help(self):
        msgBox = QMessageBox(QMessageBox.NoIcon, '帮助', '视频情感数据标注系统帮助文档')
        msgBox.exec_()

    def about_us(self):
        msgBox=QMessageBox(QMessageBox.NoIcon,'关于','视频情感数据标注系统')
        msgBox.setIconPixmap(QPixmap("./YYY.jpg"))
        msgBox.exec_()

    def jump_to_1(self):
        self.ui_1 = MainWindow2()
        self.ui_1.show()

    def jump_to_2(self):
        self.ui_2 = MainWindow3()
        self.ui_2.show()

    def jump_to_3(self):
        self.ui_3 = MainWindow4()
        self.ui_3.show()

    def jump_to_4(self):
        self.ui_4 = MainWindow5()
        self.ui_4.show()



if __name__ == '__main__':
    app=QtWidgets.QApplication(sys.argv)
    ui=MainWindow()
    ui.show()
    sys.exit(app.exec_())

