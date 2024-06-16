from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt


class TextTabWidget(QtWidgets.QWidget):
    def __init__(self, path=None):
        super(TextTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.tradition_frame = self.findChild(QtWidgets.QFrame, 'tradition_frame_1')
        self.semantic_frame = self.findChild(QtWidgets.QFrame, 'semantic_frame_1')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_1')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_1')

        receive_calculate_font = QtGui.QFont()
        receive_calculate_font.setPointSize(14)
        self.receiveButton.setFont(receive_calculate_font)
        self.calculateButton.setFont(receive_calculate_font)
        self.receiveButton.setText('接收')
        self.calculateButton.setText('计算')

