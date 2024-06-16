import os

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFileDialog
from moviepy.editor import VideoFileClip


class StaticVidTab(QtWidgets.QWidget):
    def __init__(self, path, video_queue):
        super(StaticVidTab, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)
        self.video_queue = video_queue

        self.frame_rate = 15
        self.clip = None
        self.frame_count = None
        self.current_frame = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.display_next_frame)

        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame_4')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_4')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_4')

        browser_font = QtGui.QFont()
        browser_font.setPointSize(14)
        self.browserButton.setFont(browser_font)
        self.sendButton.setFont(browser_font)
        self.browserButton.setText('浏览')
        self.sendButton.setText('发送')

        self.browserButton.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            print("选择的文件路径：", file_path)
            self.start_playing(file_path)

    def start_playing(self, video_path):
        self.clip = VideoFileClip(video_path)
        self.frame_count = int(self.clip.duration * self.frame_rate)
        self.current_frame = 0
        print(1000 / self.frame_rate)
        self.timer.start(int(1000 / self.frame_rate))

    def display_next_frame(self):
        if self.current_frame < self.frame_count:
            img = self.clip.get_frame(self.current_frame / self.frame_rate)
            self.display_image(img)
            self.current_frame += 1
        else:
            self.timer.stop()

    def display_image(self, image):
        pixmap = QtGui.QPixmap.fromImage(
            QtGui.QImage(image.tobytes(), image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888))
        pixmap = pixmap.scaled(self.show_frame.size())
        palette = self.show_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.show_frame.setPalette(palette)
        self.show_frame.setAutoFillBackground(True)
