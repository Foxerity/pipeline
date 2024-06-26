import os
import time

from PIL import Image
from PIL.ImageQt import ImageQt
from moviepy.editor import VideoFileClip
from PyQt5 import uic, QtWidgets, QtGui, QtMultimediaWidgets, QtMultimedia, QtCore
from PyQt5.QtCore import Qt, QTimer
# from main_utils.processes.receive.utils.calculate_video import compute_true_sematic, compute_sc_fps

class StaticVidTab(QtWidgets.QWidget):
    def __init__(self, path, vid_obj_queue, rece_vid_queue, static_value_queue, socket_value):
        super(StaticVidTab, self).__init__(flags=Qt.WindowFlags())
        self.gt_path = r'/home/samaritan/Desktop/videos'
        self.rece_vid_queue = rece_vid_queue
        self.vid_obj_queue = vid_obj_queue
        self.static_value_queue = static_value_queue
        self.socket_value = socket_value

        self.frame_rate = 15
        self.clip = None
        self.frame_count = None
        self.current_frame = 0

        self.trad_timer = QtCore.QTimer(self)
        self.trad_timer.timeout.connect(self.display_next_frame)

        self.sema_timer = QtCore.QTimer(self)
        self.sema_timer.timeout.connect(self.receive_clicked)

        uic.loadUi(path, self)

        self.tradition_frame = self.findChild(QtWidgets.QFrame, 'tradition_frame_4')
        self.semantic_frame = self.findChild(QtWidgets.QFrame, 'semantic_frame_4')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_4')
        self.comboBox = self.findChild(QtWidgets.QComboBox, 'comboBox_4')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_4')
        self.sc_value = self.findChild(QtWidgets.QLabel, 'static_fidelity_sc_value')
        self.tc_value = self.findChild(QtWidgets.QLabel, 'static_fidelity_tc_value')
        self.sc_frame_value = self.findChild(QtWidgets.QLabel, 'static_frame_sc_value')
        self.tc_frame_value = self.findChild(QtWidgets.QLabel, 'static_frame_tc_value')
        self.bit_value = self.findChild(QtWidgets.QLabel, 'value_2')
        self.ber_value = self.findChild(QtWidgets.QLabel, 'value_3')
        self.mean_ber_value = self.findChild(QtWidgets.QLabel, 'value_4')
        self.loss_packet_value = self.findChild(QtWidgets.QLabel, 'value_5')

        receive_calculate_font = QtGui.QFont()
        receive_calculate_font.setPointSize(14)
        self.comboBox.setFont(receive_calculate_font)
        self.receiveButton.setFont(receive_calculate_font)
        self.calculateButton.setFont(receive_calculate_font)
        self.receiveButton.setText('接收')
        self.calculateButton.setText('计算')
        self.sc_value.setFont(receive_calculate_font)
        self.tc_value.setFont(receive_calculate_font)
        self.sc_frame_value.setFont(receive_calculate_font)
        self.tc_frame_value.setFont(receive_calculate_font)
        self.bit_value.setFont(receive_calculate_font)
        self.ber_value.setFont(receive_calculate_font)
        self.mean_ber_value.setFont(receive_calculate_font)
        self.loss_packet_value.setFont(receive_calculate_font)

        self.choice = {"fish": 1, "two_box": 2, "视频3": 3, "视频4": 4}
        self.comboBox.addItems(self.choice.keys())

        self.comboBox.currentIndexChanged.connect(self.combo_changed)
        self.receiveButton.clicked.connect(self.receive_clicked)
        # self.calculateButton.clicked.connect(self.calculate_static)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.emit_calculation)
        self.timer.start(70)  # 10ms秒触发一次计算

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
        self.sema_timer.start(70)

    def start_playing(self, video_path):
        video_path = os.path.join(self.gt_path, video_path + '.mp4')
        self.clip = VideoFileClip(video_path)
        self.frame_count = int(self.clip.duration * self.frame_rate)
        self.current_frame = 0
        self.trad_timer.start(int(1000 / self.frame_rate))

    def display_next_frame(self):
        if self.current_frame < self.frame_count:
            img = self.clip.get_frame(self.current_frame / self.frame_rate)
            self.display_image(img)
            self.current_frame += 1
        else:
            self.trad_timer.stop()

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

    def calculate_static(self):
        pass

    def emit_calculation(self):
        if not self.socket_value.empty():
            # value = self.static_value_queue.get()
            time_value = self.socket_value.get()
            print(f"speed: {time_value}")
            self.bit_value.setText(f"{time_value['time']/1024:.2f} Kbps")
            # self.loss_packet_value.setText(f"{value['loss_packet'] * 100:.2f}%")
