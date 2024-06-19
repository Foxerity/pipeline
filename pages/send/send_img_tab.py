import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog


class ImageTabWidget(QtWidgets.QWidget):
    def __init__(self, path, img_queue):
        super(ImageTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.img_queue = img_queue
        self.img_path = None

        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame_2')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_2')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_2')

        browser_font = QtGui.QFont()
        browser_font.setPointSize(14)
        self.browserButton.setFont(browser_font)
        self.sendButton.setFont(browser_font)
        self.browserButton.setText('浏览')
        self.sendButton.setText('发送')

        self.browserButton.clicked.connect(self.open_file_dialog)
        self.sendButton.clicked.connect(self.send_image)

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            print("选择的文件路径：", file_path)
            self.img_path = file_path
            self.display_image(file_path)

    def send_image(self):
        if self.img_path:
            self.img_queue.put(self.img_path)

    def display_image(self, image_path):
        if isinstance(image_path, Image.Image):
            pixmap = ImageQt(image_path)
        # 创建 QPixmap 并从文件加载图片
        else:
            pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(self.show_frame.size())

        # 创建 QPalette 并设置 QFrame 的背景
        palette = self.show_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.show_frame.setPalette(palette)
        self.show_frame.setAutoFillBackground(True)
        self.show_frame.repaint()
