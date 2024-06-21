from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QFileDialog


class TextTabWidget(QtWidgets.QWidget):
    def __init__(self, path=None, txt_queue=None, txt_tral_queue=None, txt_value_queue=None):
        super(TextTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)
        self.txt_queue = txt_queue
        self.txt_tral_queue = txt_tral_queue
        self.txt_value_queue = txt_value_queue
        self.txt = ''
        self.raw_content_list = []
        self.sema_content_list = []
        self.tral_content_list = []


        self.tradition_frame = self.findChild(QtWidgets.QFrame, 'tradition_frame_1')
        self.semantic_frame = self.findChild(QtWidgets.QFrame, 'semantic_frame_1')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_1')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_1')
        self.sc_value = self.findChild(QtWidgets.QLabel, 'txt_fidelity_sc_value')
        self.tc_value = self.findChild(QtWidgets.QLabel, 'txt_fidelity_tc_value')

        self.bit_value = self.findChild(QtWidgets.QLabel, 'value_2')
        self.ber_value = self.findChild(QtWidgets.QLabel, 'value_3')
        self.distant = self.findChild(QtWidgets.QLabel, 'value_4')
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
        self.distant.setFont(receive_calculate_font)
        self.loss_packet_value.setFont(receive_calculate_font)

        gt_txt_font = QFont("Arial", 12)  # 使用Arial字体，大小为12
        self.gt_frame_layout = QVBoxLayout(self.tradition_frame)
        self.gt_text_edit = QTextEdit(self.tradition_frame)
        self.gt_text_edit.setFont(gt_txt_font)
        self.gt_text_edit.setReadOnly(True)  # 设置为只读
        self.gt_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gt_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.gt_frame_layout.addWidget(self.gt_text_edit)

        ge_txt_font = QFont("Arial", 12)
        self.ge_frame_layout = QVBoxLayout(self.semantic_frame)
        self.ge_text_edit = QTextEdit(self.semantic_frame)
        self.ge_text_edit.setFont(ge_txt_font)
        self.ge_text_edit.setReadOnly(True)  # 设置为只读
        self.ge_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ge_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ge_frame_layout.addWidget(self.ge_text_edit)

        self.receiveButton.clicked.connect(self.show_txt)
        self.calculateButton.clicked.connect(self.calculate_txt)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.emit_calculation)
        self.timer.start(10)  # 每秒触发一次计算


    def show_txt(self):
        self.ge_text_edit.setPlainText('')
        self.gt_text_edit.setPlainText('')
        self.show_tra_gen_txt()
        self.show_gen_txt()

    def show_gen_txt(self):
        if not self.txt_queue.empty():
            content = self.txt_queue.get()
            self.sema_content_list.append(content)
            content = "".join(content)
            self.ge_text_edit.append(content)
        QTimer().singleShot(80, lambda: self.show_gen_txt())

    def show_tra_gen_txt(self):
        if not self.txt_tral_queue.empty():
            content = self.txt_tral_queue.get()
            self.tral_content_list.append(content)
            content = "".join(content)
            content = content.replace('\n', '\n\n') + "\n"
            self.gt_text_edit.append(content)
        QTimer().singleShot(80, lambda: self.show_tra_gen_txt())


    def true_text(self, text_path):
        with open(text_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        self.raw_content_list = lines
    def gen_txt(self, gen_path):
        fop = open(gen_path, 'r', encoding='utf8')
        gen_data = fop.read()
        gen_data = str(gen_data).replace(' ', '')
        sentences = gen_data.strip().split('\n')
        fop.close()
        return sentences

    def tra_gen_txt(self, tra_gen_path):
        fop = open(tra_gen_path, 'r', encoding='utf8')
        gen_data = fop.read()
        gen_data = str(gen_data).replace(' ', '')
        sentences = gen_data.strip().split('\n')
        fop.close()
        return sentences

    def calculate_txt(self):
        sc_same_count = 0
        tc_same_count = 0
        raw_data_path = r"/home/samaritan/Desktop/pipeline_final/pipeline/test_10.txt"
        self.true_text(raw_data_path)
        self.raw_content_list = [element.strip() for element in self.raw_content_list]
        self.sema_content_list = [element.strip() for element in self.sema_content_list]
        self.tral_content_list = [element.strip() for element in self.tral_content_list]
        for char1, char2 in zip(self.raw_content_list, self.sema_content_list):
            if char1 == char2:
                sc_same_count += 1
        for char1, char2 in zip(self.raw_content_list, self.tral_content_list):
            if char1 == char2:
                tc_same_count += 1
        total_count = len(self.raw_content_list)
        sc_ratio = sc_same_count / total_count if total_count > 0 else 0
        tc_ratio = tc_same_count / total_count if total_count > 0 else 0
        self.sc_value.setText(f"{sc_ratio * 100:.2f}%")
        self.tc_value.setText(f"{tc_ratio * 100:.2f}%")

    def emit_calculation(self):
        if not self.txt_value_queue.empty():
            value = self.txt_value_queue.get()
            self.bit_value.setText(f"{value['bit_ratio']/1024:.2f} Kbps")
            self.loss_packet_value.setText(f"{value['loss_packet'] * 100:.2f}%")

