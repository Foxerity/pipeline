from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt


class StaticVidTab(QtWidgets.QWidget):
    def __init__(self, path):
        super(StaticVidTab, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame_4')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_4')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_4')

        browser_font = QtGui.QFont()
        browser_font.setPointSize(14)
        self.browserButton.setFont(browser_font)
        self.sendButton.setFont(browser_font)
        self.browserButton.setText('浏览')
        self.sendButton.setText('发送')