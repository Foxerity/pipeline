import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from callback.callback import Callback
from pipeline_abc import Pipeline
from pages.send.send_text_tab import TextTabWidget
from pages.send.send_img_tab import ImageTabWidget
from pages.send.send_static_vid_tab import StaticVidTab
from pages.send.send_stream_vid_tab import StreamVidTab


class MainPage(QtWidgets.QMainWindow):
    pages_path = [
        "ui/send/send_txt_tab.ui",
        "ui/send/send_img_tab.ui",
        "ui/send/send_static_vid_tab.ui",
        "ui/send/send_stream_vid_tab.ui",
    ]

    def __init__(self):
        super(MainPage, self).__init__(flags=Qt.WindowFlags())
        self.init_main_UI()
        # 加载并添加四个标签页, 分别对应文本、图像、静态视频、流式视频Tab
        self.tab_widget.addTab(TextTabWidget(self.pages_path[0]), "指令")
        self.tab_widget.addTab(ImageTabWidget(self.pages_path[1]), "图像")
        self.tab_widget.addTab(StaticVidTab(self.pages_path[2]), "静态视频")
        self.tab_widget.addTab(StreamVidTab(self.pages_path[3]), "流式视频")

    def init_main_UI(self):
        # 设置窗口位置和大小（x, y, width, height）
        self.setGeometry(800, 800, 1600, 1000)
        self.setWindowTitle('Set Geometry Example')

        # 创建主窗口的 QTabWidget
        setattr(self, 'tab_widget', QtWidgets.QTabWidget())
        self.setCentralWidget(self.tab_widget)


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
