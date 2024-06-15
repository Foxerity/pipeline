from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt


class StaticVidTab(QtWidgets.QWidget):
    def __init__(self, path):
        super(StaticVidTab, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.tradition_frame = self.findChild(QtWidgets.QFrame, 'tradition_frame_4')
        self.semantic_frame = self.findChild(QtWidgets.QFrame, 'semantic_frame_4')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_4')
        self.showButton = self.findChild(QtWidgets.QPushButton, 'showButton_4')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_4')

        receive_show_calculate_font = QtGui.QFont()
        receive_show_calculate_font.setPointSize(14)
        self.receiveButton.setFont(receive_show_calculate_font)
        self.showButton.setFont(receive_show_calculate_font)
        self.calculateButton.setFont(receive_show_calculate_font)
        self.receiveButton.setText('接收')
        self.showButton.setText('显示')
        self.calculateButton.setText('计算')