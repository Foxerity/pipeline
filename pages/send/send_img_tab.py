from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt


class ImageTabWidget(QtWidgets.QWidget):
    def __init__(self, path):
        super(ImageTabWidget, self).__init__()
        uic.loadUi(path, self)
