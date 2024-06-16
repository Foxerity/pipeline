import multiprocessing
import sys
from multiprocessing import Queue

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from callback.callback import Callback
from pipeline_abc import Pipeline
from pages.send.send_text_tab import TextTabWidget
from pages.send.send_img_tab import ImageTabWidget
from pages.send.send_static_vid_tab import StaticVidTab
from pages.send.send_stream_vid_tab import StreamVidTab

from main_utils.processes.send.send_processes_control import ProcessesControl


# 主界面
class MainPage(QtWidgets.QMainWindow):
    # 子界面的配置文件, 分别对应文本、图像、静态视频、流式视频Tab
    pages_path = [
        "ui/send/send_txt_tab.ui",
        "ui/send/send_img_tab.ui",
        "ui/send/send_static_vid_tab.ui",
        "ui/send/send_stream_vid_tab.ui",
    ]

    def __init__(self, cameraQueue):
        super(MainPage, self).__init__(flags=Qt.WindowFlags())
        self.init_main_UI()
        # 加载并添加四个标签页, 分别对应文本、图像、静态视频、流式视频Tab
        self.tab_widget.addTab(TextTabWidget(self.pages_path[0]), "指令")
        self.tab_widget.addTab(ImageTabWidget(self.pages_path[1]), "图像")
        self.tab_widget.addTab(StaticVidTab(self.pages_path[2]), "静态视频")
        self.tab_widget.addTab(StreamVidTab(self.pages_path[3], cameraQueue), "流式视频")

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
        self.camera_queue = Queue()
        self.main_page = MainPage(self.camera_queue)

    def setup(self, **kwargs):
        self.modules = [
            self.main_page,
            ProcessesControl(self.camera_queue)
        ]

        self.modules[1].setup()

    def run(self, callbacks: Callback = None, **kwargs):
        processes_control_process = multiprocessing.Process(target=self.modules[1].run)
        processes_control_process.start()
        # PyQt的主界面不建议在子进程运行，会出现不稳定的情况。
        self.main_page.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.setup()
    main.run()
    sys.exit(app.exec_())
