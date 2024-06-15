from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt


class ImageTabWidget(QtWidgets.QWidget):
    def __init__(self, path):
        super(ImageTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame_2')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_2')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_2')

        self.browserButton.setText('浏览')
        self.sendButton.setText('发送')