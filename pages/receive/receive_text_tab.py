from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QFileDialog


class TextTabWidget(QtWidgets.QWidget):
    def __init__(self, path=None, txt_queue=None):
        super(TextTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)
        self.txt_queue = txt_queue
        self.txt = ''

        self.tradition_frame = self.findChild(QtWidgets.QFrame, 'tradition_frame_1')
        self.semantic_frame = self.findChild(QtWidgets.QFrame, 'semantic_frame_1')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_1')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_1')

        receive_calculate_font = QtGui.QFont()
        receive_calculate_font.setPointSize(14)
        self.receiveButton.setFont(receive_calculate_font)
        self.calculateButton.setFont(receive_calculate_font)
        self.receiveButton.setText('展示')
        self.calculateButton.setText('接收')

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

        self.receiveButton.clicked.connect(self.open_file_dialog)
        self.calculateButton.clicked.connect(self.show_gen_txt)

    def open_file_dialog(self):
        self.ge_text_edit.clear()
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.txt = file_path
            print("选择的文件路径：", file_path)
            self.show_txt(file_path)

    def show_txt(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()[:-1].replace('\n', '\n\n') + "\n"
                self.gt_text_edit.setPlainText(content)  # 将文件内容设置到QTextEdit中
        except Exception as e:
            print(f"Error reading file: {e}")

    def send_txt(self):
        if not self.txt == '':
            self.txt_queue.put(self.txt)
            self.txt = ''

    def show_gen_txt(self):
        if not self.txt_queue.empty():
            content = self.txt_queue.get()
            content = "".join(content)
            self.ge_text_edit.append(content)
        QTimer().singleShot(80, lambda: self.show_gen_txt())



