from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QTextEdit, QVBoxLayout


class TextTabWidget(QtWidgets.QWidget):
    def __init__(self, path=None, txt_queue=None):
        super(TextTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)
        self.txt_queue = txt_queue
        self.txt = ''

        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame_1')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_1')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_1')

        browser_font = QtGui.QFont()
        browser_font.setPointSize(14)
        self.browserButton.setFont(browser_font)
        self.sendButton.setFont(browser_font)
        self.browserButton.setText('浏览')
        self.sendButton.setText('发送')

        txt_font = QFont("Arial", 12)  # 使用Arial字体，大小为12
        self.frame_layout = QVBoxLayout(self.show_frame)
        self.text_edit = QTextEdit(self.show_frame)
        self.text_edit.setFont(txt_font)
        self.text_edit.setReadOnly(True)  # 设置为只读
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.frame_layout.addWidget(self.text_edit)

        self.browserButton.clicked.connect(self.open_file_dialog)
        self.sendButton.clicked.connect(self.send_txt)

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.txt = file_path
            print("选择的文件路径：", file_path)
            self.show_txt(file_path)

    def show_txt(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                content = content[:-1].replace('\n', '\n\n') + '\n'
                self.text_edit.setPlainText(content)  # 将文件内容设置到QTextEdit中
        except Exception as e:
            print(f"Error reading file: {e}")

    def send_txt(self):
        if not self.txt == '':
            self.txt_queue.put(self.txt)
            self.txt = ''
