import os
import time

from PIL import Image
from PIL.ImageQt import ImageQt
from moviepy.editor import VideoFileClip
from PyQt5 import uic, QtWidgets, QtGui, QtMultimediaWidgets, QtMultimedia, QtCore
from PyQt5.QtCore import Qt, QTimer


class StaticVidTab(QtWidgets.QWidget):
    def __init__(self, path, vid_obj_queue, rece_vid_queue):
        super(StaticVidTab, self).__init__(flags=Qt.WindowFlags())
        self.gt_path = r'C:\Users\16070\Desktop\gt_videos'
        self.rece_vid_queue = rece_vid_queue
        self.vid_obj_queue = vid_obj_queue

        self.frame_rate = 15
        self.clip = None
        self.frame_count = None
        self.current_frame = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.display_next_frame)

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

        self.choice = {"fish": 1, "two_box": 2, "视频3": 3, "视频4": 4}
        self.comboBox.addItems(self.choice.keys())

        self.comboBox.currentIndexChanged.connect(self.combo_changed)
        self.receiveButton.clicked.connect(self.receive_clicked)

    def combo_changed(self):
        # 获取当前选中的文本
        current_text = self.comboBox.currentText()
        self.vid_obj_queue.put(current_text)

        # 打印选中的信息
        print(f"Selected Text: {current_text}")
        self.start_playing(current_text)

    def receive_clicked(self):
        if not self.rece_vid_queue.empty():
            img = self.rece_vid_queue.get()
            self.display_single_image(img)
        QTimer().singleShot(70, lambda: self.receive_clicked())

    def start_playing(self, video_path):
        video_path = os.path.join(self.gt_path, video_path + '.mp4')
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
        pixmap = pixmap.scaled(self.tradition_frame.size())
        palette = self.tradition_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.tradition_frame.setPalette(palette)
        self.tradition_frame.setAutoFillBackground(True)

    def display_single_image(self, image_path):
        if isinstance(image_path, Image.Image):
            pixmap = ImageQt(image_path)
        # 创建 QPixmap 并从文件加载图片
        else:
            pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(self.semantic_frame.size())

        # 创建 QPalette 并设置 QFrame 的背景
        palette = self.semantic_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.semantic_frame.setPalette(palette)
        self.semantic_frame.setAutoFillBackground(True)
        self.semantic_frame.repaint()

