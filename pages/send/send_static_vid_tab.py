from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt


class StaticVidTab(QtWidgets.QWidget):
    def __init__(self, path):
        super(StaticVidTab, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)
