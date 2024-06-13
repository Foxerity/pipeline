from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt


class TextTabWidget(QtWidgets.QWidget):
    def __init__(self, path=None):
        super(TextTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)
