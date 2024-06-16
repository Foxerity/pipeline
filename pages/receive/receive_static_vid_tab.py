from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt


class StaticVidTab(QtWidgets.QWidget):
    def __init__(self, path):
        super(StaticVidTab, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.tradition_frame = self.findChild(QtWidgets.QFrame, 'tradition_frame_4')
        self.semantic_frame = self.findChild(QtWidgets.QFrame, 'semantic_frame_4')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_4')
        self.comboBox = self.findChild(QtWidgets.QComboBox, 'comboBox_4')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_4')

        receive_calculate_font = QtGui.QFont()
        receive_calculate_font.setPointSize(14)
        self.comboBox.setFont(receive_calculate_font)
        self.receiveButton.setFont(receive_calculate_font)
        self.calculateButton.setFont(receive_calculate_font)
        self.receiveButton.setText('接收')
        self.calculateButton.setText('计算')

        self.choice = {"视频1": 1, "视频2": 2, "视频3": 3, "视频4": 4}
        self.comboBox.addItems(self.choice.keys())
