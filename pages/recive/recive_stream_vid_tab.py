import os
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import QTimer, Qt


class StreamVidTab(QtWidgets.QWidget):
    def __init__(self, path):
        super(StreamVidTab, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.skeleton_frame = self.findChild(QtWidgets.QFrame, 'skeleton_frame')
        self.gener_frame = self.findChild(QtWidgets.QFrame, 'gener_frame')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_3')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_3')
        self.browserButton.setText('Browser Skeleton')
        self.sendButton.setText('Browser Generation')
        self.browserButton.clicked.connect(lambda: self.open_file_dialog('skeleton_frame'))
        self.sendButton.clicked.connect(lambda: self.open_file_dialog('gener_frame'))

    def open_file_dialog(self, show_frame=None):
        # 打开文件对话框选择目录
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, '选择目录')
        if show_frame == 'skeleton_frame':
            setattr(self, 'skeleton_directory', directory)
        elif show_frame == 'gener_frame':
            setattr(self, 'gener_directory', directory)
        else:
            raise ValueError
        if directory:
            print(f"监视目录：{directory}")
            self.check_for_new_image(directory, show_frame)

    def check_for_new_image(self, directory, show_frame=None):
        # 获取目录中的所有文件
        if show_frame == 'skeleton_frame':
            if not directory == self.skeleton_directory:
                return
            show_frames = self.skeleton_frame
        elif show_frame == 'gener_frame':
            if not directory == self.gener_directory:
                return
            show_frames = self.gener_frame
        else:
            raise ValueError

        files = os.listdir(directory)
        # 过滤图片文件
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

        if image_files:
            # 如果找到图片，显示第一张图片
            image_path = os.path.join(directory, image_files[0])
            self.display_image(image_path, show_frames)
            os.remove(image_path)
            QTimer().singleShot(1, lambda: self.check_for_new_image(directory, show_frame))
        else:
            # 如果没有图片，定时器每隔一段时间检查一次
            QTimer().singleShot(1000, lambda: self.check_for_new_image(directory, show_frame))

    @staticmethod
    def display_image(image_path, show_frame=None):
        # 创建 QPixmap 并从文件加载图片
        pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(show_frame.size())
        # 创建 QPalette 并设置 QFrame 的背景
        palette = show_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        show_frame.setPalette(palette)
        show_frame.setAutoFillBackground(True)
        show_frame.repaint()
