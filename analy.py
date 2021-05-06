from PyQt5.QtWidgets import QMainWindow
from analysis_window import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        ui = analysis_window.Ui_MainWindow()
        ui.setupUi(self)
