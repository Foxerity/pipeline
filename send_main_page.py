import os
import sys
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QFileDialog, QSizePolicy
from PyQt5.QtCore import Qt, QFileSystemWatcher, QTimer

from callback.callback import Callback
from pipeline_abc import Pipeline


class MainPage(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainPage, self).__init__()
        self.init_main_UI()
        # 加载并添加各个标签页
        self.initTabs_txt()
        self.initTabs_img()
        self.initTabs_static_vid()
        self.initTabs_stream_vid()

    def init_main_UI(self):
        # 设置窗口位置和大小（x, y, width, height）
        self.setGeometry(800, 800, 800, 800)
        self.setWindowTitle('Set Geometry Example')
        # 创建主窗口的 QTabWidget
        self.tab_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_widget)

    def initTabs_txt(self):
        self.add_tab("ui/send/txt_tab.ui", "指令")

    def initTabs_img(self):
        self.add_tab("ui/send/img_tab.ui", "图片")

    def initTabs_static_vid(self):
        self.add_tab("ui/send/static_vid_tab.ui", "静态视频")

    def initTabs_stream_vid(self):
        self.add_tab("ui/send/stream_vid_tab.ui", "流式视频")
        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame')

        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton')

        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton')

        self.browserButton.clicked.connect(self.open_file_dialog)

    def add_tab(self, ui_file, tab_name):
        # 加载 .ui 文件并创建相应的 QWidget
        tab = uic.loadUi(ui_file)
        self.tab_widget.addTab(tab, tab_name)

    def open_file_dialog(self):
        # 打开文件对话框选择目录
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, '选择目录')
        self.directory = directory
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
            QTimer.singleShot(10, lambda: self.check_for_new_image(directory))
        else:
            # 如果没有图片，定时器每隔一段时间检查一次
            QTimer.singleShot(1000, lambda: self.check_for_new_image(directory))

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


class MainWindow(Pipeline):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_page = MainPage()

    def setup(self, **kwargs):
        pass

    def run(self, callbacks: Callback = None, **kwargs):
        self.main_page.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.run()
    sys.exit(app.exec_())
