import os
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer, Qt
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QFileDialog


class StreamVidTab(QtWidgets.QWidget):
    def __init__(self, path, cameraQueue):
        super(StreamVidTab, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame_3')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_3')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_3')

        browser_font = QtGui.QFont()
        browser_font.setPointSize(14)
        self.browserButton.setFont(browser_font)
        self.sendButton.setFont(browser_font)
        self.browserButton.setText('浏览')
        self.sendButton.setText('发送')

        self.cameraQueue = cameraQueue

        self.browserButton.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            print("选择的文件路径：", file_path)
            self.check_for_camera()

    def check_for_camera(self):
        if self.cameraQueue and not self.cameraQueue.empty():
            img = self.cameraQueue.get()
            print('get img.')
            if img and isinstance(img, Image.Image):
                self.display_image(img)
                QTimer().singleShot(80, lambda: self.check_for_camera())
            else:
                QTimer().singleShot(80, lambda: self.check_for_camera())
        else:
            QTimer().singleShot(80, lambda: self.check_for_camera())

    def check_for_new_image(self, directory):
        # 获取目录中的所有文件
        if not directory == self.directory:
            print("退出！")
            return
        files = os.listdir(directory)
        # 过滤图片文件
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

        if image_files:
            # 如果找到图片，显示第一张图片
            image_path = os.path.join(directory, image_files[0])
            self.display_image(image_path)
            os.remove(image_path)
            QTimer().singleShot(10, lambda: self.check_for_new_image(directory))
        else:
            # 如果没有图片，定时器每隔一段时间检查一次
            QTimer().singleShot(1000, lambda: self.check_for_new_image(directory))

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
