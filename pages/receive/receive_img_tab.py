from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt


class ImageTabWidget(QtWidgets.QWidget):
    def __init__(self, path):
        super(ImageTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.tradition_frame = self.findChild(QtWidgets.QFrame, 'tradition_frame_2')
        self.semantic_frame = self.findChild(QtWidgets.QFrame, 'semantic_frame_2')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_2')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_2')

        receive_calculate_font = QtGui.QFont()
        receive_calculate_font.setPointSize(14)
        self.receiveButton.setFont(receive_calculate_font)
        self.calculateButton.setFont(receive_calculate_font)
        self.receiveButton.setText('接收')
        self.calculateButton.setText('计算')
