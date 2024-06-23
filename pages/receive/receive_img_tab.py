import time

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer
from main_utils.processes.receive.receive_img_utils.image_calculate import ImageCalculator


class ImageTabWidget(QtWidgets.QWidget):
    def __init__(self, path, img_queue, img_tra_queue, img_value_queue, socket_value):
        super(ImageTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)
        self.sema_img = None
        self.tral_img = None
        self.img_queue = img_queue
        self.img_tra_queue = img_tra_queue
        self.img_value_queue = img_value_queue
        self.socket_value = socket_value

        self.image_calculator = ImageCalculator()
        self.image_calculator.setup()

        self.tradition_frame = self.findChild(QtWidgets.QFrame, 'tradition_frame_2')
        self.semantic_frame = self.findChild(QtWidgets.QFrame, 'semantic_frame_2')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_2')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_2')
        self.sc_value = self.findChild(QtWidgets.QLabel, 'img_fidelity_sc_value')
        self.tc_value = self.findChild(QtWidgets.QLabel, 'img_fidelity_tc_value')
        self.sc_compress_value = self.findChild(QtWidgets.QLabel, 'img_compress_sc_value')
        self.tc_compress_value = self.findChild(QtWidgets.QLabel, 'img_compress_tc_value')

        self.bit_value = self.findChild(QtWidgets.QLabel, 'value_2')
        self.ber_value = self.findChild(QtWidgets.QLabel, 'value_3')
        self.mean_ber_value = self.findChild(QtWidgets.QLabel, 'value_4')
        self.loss_packet_value = self.findChild(QtWidgets.QLabel, 'value_5')

        receive_calculate_font = QtGui.QFont()
        receive_calculate_font.setPointSize(14)
        self.receiveButton.setFont(receive_calculate_font)
        self.calculateButton.setFont(receive_calculate_font)
        self.receiveButton.setText('接收')
        self.calculateButton.setText('计算')
        self.sc_value.setFont(receive_calculate_font)
        self.tc_value.setFont(receive_calculate_font)
        self.bit_value.setFont(receive_calculate_font)
        self.ber_value.setFont(receive_calculate_font)
        self.mean_ber_value.setFont(receive_calculate_font)
        self.loss_packet_value.setFont(receive_calculate_font)
        self.sc_compress_value.setFont(receive_calculate_font)
        self.tc_compress_value.setFont(receive_calculate_font)

        self.receiveButton.clicked.connect(self.get_img)
        self.calculateButton.clicked.connect(self.calculate_img)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.emit_calculation)
        self.timer.start(10)  # 10ms秒触发一次计算

    def get_img(self):
        self.get_semantic_img()
        self.get_tradition_img()

    def get_semantic_img(self):
        if not self.img_queue.empty():
            img = self.img_queue.get()
            self.sema_img = img
            print("ImageTabWidget: get_semantic_img")
            self.display_semantic_image(img)
        QTimer().singleShot(60, lambda: self.get_semantic_img())

    def get_tradition_img(self):
        if not self.img_tra_queue.empty():
            img = self.img_tra_queue.get()
            self.tral_img = img
            print("ImageTabWidget: get_tradition_img")
            self.display_tradition_image(img)
        QTimer().singleShot(60, lambda: self.get_tradition_img())

    def display_semantic_image(self, image_path):
        if isinstance(image_path, Image.Image):
            pixmap = ImageQt(image_path)
        else:
            pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(self.semantic_frame.size())

        # 创建 QPalette 并设置 QFrame 的背景
        palette = self.semantic_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.semantic_frame.setPalette(palette)
        self.semantic_frame.setAutoFillBackground(True)
        self.semantic_frame.repaint()

    def display_tradition_image(self, image_path):
        if isinstance(image_path, Image.Image):
            pixmap = ImageQt(image_path)
        else:
            pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(self.tradition_frame.size())

        # 创建 QPalette 并设置 QFrame 的背景
        palette = self.tradition_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        self.tradition_frame.setPalette(palette)
        self.tradition_frame.setAutoFillBackground(True)
        self.tradition_frame.repaint()

    def calculate_img(self):
        true_img_path = "/home/samaritan/Desktop/pipeline_final/pipeline/receive_img.jpg"
        true_img = Image.open(true_img_path).convert('RGB')

        semantic_evaluation_with_sema = self.image_calculator.overall_semantic_evaluation(self.sema_img, true_img)
        semantic_evaluation_wiht_tral = self.image_calculator.overall_semantic_evaluation(self.tral_img, true_img)
        self.sc_value.setText(f"{semantic_evaluation_with_sema * 100:.2f} %")
        self.tc_value.setText(f"{semantic_evaluation_wiht_tral * 100:.2f}%")
        self.sc_compress_value.setText(f"{1024 :.2f}")
        self.tc_compress_value.setText(f"{541:.2f}")

    def emit_calculation(self):
        if not self.img_value_queue.empty():
            value = self.img_value_queue.get()
            time_value = self.socket_value.get()
            self.bit_value.setText(f"{time_value['time'] / 1024:.2f} Kbps")
            self.loss_packet_value.setText(f"{value['loss_packet'] * 100:.2f}%")
            self.ber_value.setText(f"{value['ber_ratio'] * 100:.2f}%")
            self.mean_ber_value.setText(f"{value['mean_ber_ratio'] * 100:.2f}%")

