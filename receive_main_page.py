import multiprocessing
import sys
from multiprocessing import Queue

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

from callback.callback import Callback
from pipeline_abc import Pipeline
from pages.receive.receive_text_tab import TextTabWidget
from pages.receive.receive_img_tab import ImageTabWidget
from pages.receive.receive_static_vid_tab import StaticVidTab
from pages.receive.receive_stream_vid_tab import StreamVidTab

from main_utils.processes.receive.receive_processes_control import ProcessesControl


class MainPage(QtWidgets.QMainWindow):
    pages_path = [
        "ui/receive/receive_txt_tab.ui",
        "ui/receive/receive_img_tab.ui",
        "ui/receive/receive_static_vid_tab.ui",
        "ui/receive/receive_stream_vid_tab.ui",
    ]

    def __init__(self, skeleton_queue, generation_queue):
        super(MainPage, self).__init__(flags=Qt.WindowFlags())
        self.initUI()
        # 加载并添加四个标签页, 分别对应文本、图像、静态视频、流式视频Tab
        self.tab_widget.addTab(TextTabWidget(self.pages_path[0]), "指令")
        self.tab_widget.addTab(ImageTabWidget(self.pages_path[1]), "图像")
        self.tab_widget.addTab(StaticVidTab(self.pages_path[2]), "静态视频")
        self.tab_widget.addTab(StreamVidTab(self.pages_path[3], skeleton_queue, generation_queue), "流式视频")
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.tab_widget.setStyleSheet("""
        QTabBar::tab {
            font-size: 18px;      /* 设置字体大小为18px */
            height: 40px;         /* 设置标签高度为40px */
            width: 120px;         /* 设置标签宽度为120px */
            min-width: 100px;     /* 设置标签最小宽度为100px */
            min-height: 30px;     /* 设置标签最小高度为30px */
            max-width: 150px;     /* 设置标签最大宽度为150px */
            max-height: 50px;     /* 设置标签最大高度为50px */
        }
        """)

    def initUI(self):
        # 设置窗口位置和大小(x, y, width, height)
        self.setGeometry(800, 800, 1600, 1000)
        self.setWindowTitle('水下通信演示系统')

        # 创建主窗口的 QTabWidget
        setattr(self, 'tab_widget', QtWidgets.QTabWidget())
        self.setCentralWidget(self.tab_widget)


class MainWindow(Pipeline):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.skeleton_queue = Queue()
        self.generation_queue = Queue()

        self.main_page = MainPage(self.skeleton_queue, self.generation_queue)

    def setup(self, **kwargs):
        self.modules = [
            self.main_page,
            ProcessesControl()
        ]

        self.modules[1].setup(self.skeleton_queue, self.generation_queue)

    def run(self, callbacks: Callback = None, **kwargs):
        processes_control_process = multiprocessing.Process(target=self.modules[1].run)
        processes_control_process.start()
        self.main_page.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.setup()
    main.run()
    sys.exit(app.exec_())

