import time

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap


class ImageTabWidget(QtWidgets.QWidget):
    def __init__(self, path, img_queue):
        super(ImageTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.img_queue = img_queue

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

        self.receiveButton.clicked.connect(self.get_img)

    def get_img(self):
        if not self.img_queue.empty():
            img = self.img_queue.get()
            print("ImageTabWidget: get img")
            self.display_semantic_image(img)
        QTimer().singleShot(60, lambda: self.get_img())

    def display_semantic_image(self, image_path):
        if isinstance(image_path, Image.Image):
            pixmap = ImageQt(image_path)
            # pixmap = QPixmap.fromImage(pixmap)
        else:
            pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(self.semantic_frame.size())

        # 创建 QPalette 并设置 QFrame 的背景
        palette = self.semantic_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.semantic_frame.setPalette(palette)
        self.semantic_frame.repaint()

