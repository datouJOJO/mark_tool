from PyQt5.QtWidgets import QMainWindow

from premaking import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent=parent)
        ui = Ui_MainWindow()
        ui.setupUi(self)

    def auto(self):
        pass
    def man(self):
        pass