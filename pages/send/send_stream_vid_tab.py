import os
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer, Qt


class StreamVidTab(QtWidgets.QWidget):
    def __init__(self, path):
        super(StreamVidTab, self).__init__()
        uic.loadUi(path, self)

        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton')

        self.browserButton.setText('Browser')
        self.sendButton.setText('Send')

        self.browserButton.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        # 打开文件对话框选择目录
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, '选择目录')
        setattr(self, 'directory', directory)
        if directory:
            print(f"监视目录：{directory}")
            self.check_for_new_image(directory)

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
        # 创建 QPixmap 并从文件加载图片
        pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(self.show_frame.size())

        # 创建 QPalette 并设置 QFrame 的背景
        palette = self.show_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.show_frame.setPalette(palette)
        self.show_frame.setAutoFillBackground(True)
        self.show_frame.repaint()
