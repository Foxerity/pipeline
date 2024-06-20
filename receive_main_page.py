import multiprocessing
import sys
from multiprocessing import Queue, Manager
from typing import Union, Any

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

    def __init__(self, queue_dict):
        super(MainPage, self).__init__(flags=Qt.WindowFlags())
        # 创建主窗口的 QTabWidget
        self.queue_dict = queue_dict
        self.tab_widget = QtWidgets.QTabWidget()
        self.initUI()
        # 加载并添加四个标签页, 分别对应文本、图像、静态视频、流式视频Tab
        self.tab_widget.addTab(TextTabWidget(self.pages_path[0],
                                             queue_dict['txt_queue'], queue_dict['txt_trad_queue']),
                               "指令")

        self.tab_widget.addTab(ImageTabWidget(self.pages_path[1], queue_dict['img_queue'], queue_dict["img_tra_queue"]),
                               "图像")

        self.tab_widget.addTab(StaticVidTab(self.pages_path[2],
                                            queue_dict['vid_obj_queue'], queue_dict['rec_queue']),
                               "静态视频")

        self.tab_widget.addTab(StreamVidTab(self.pages_path[3],
                                            queue_dict['skeleton_queue'], queue_dict['generation_queue']),
                               "流式视频")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)

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

        self.on_tab_changed(0)

    def initUI(self):
        # 设置窗口位置和大小(x, y, width, height)
        self.setGeometry(800, 800, 1600, 1000)
        self.setWindowTitle('水下通信演示系统——接收端')

        self.setCentralWidget(self.tab_widget)

    def on_tab_changed(self, index):
        print(f"Current tab index: {index}")
        current_widget = self.tab_widget.currentWidget()
        print(f"Current tab widget: {current_widget}")

        # 执行不同的操作，根据当前选中的标签页
        if index == 0:
            print("Text Tab is selected")
            queue_tuple = (1047, self.queue_dict['txt_socket_queue'])
            self.queue_dict['control_queue'].put(queue_tuple)
        elif index == 1:
            print("Image Tab is selected")
            queue_tuple = (1047, self.queue_dict['img_socket_queue'])
            self.queue_dict['control_queue'].put(queue_tuple)
        elif index == 2:
            print("Static Video Tab is selected")
            queue_tuple = (1047, self.queue_dict['static_socket_queue'])
            self.queue_dict['control_queue'].put(queue_tuple)
        elif index == 3:
            print("Stream Video Tab is selected")


class MainWindow(Pipeline):
    queue_dict = {
        "txt_queue": Union[Queue, Any],
        "txt_trad_queue": Union[Queue, Any],
        "txt_socket_queue": Union[Queue, Any],

        "img_queue": Union[Queue, Any],

        "static_vid_pro": Union[Queue, Any],

        "stream_vid_pro": Union[Queue, Any],
    }

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ProcessesControl = None
        self.MainPage = None

        manager = Manager()
        self.control_queue = manager.Queue()

        self.txt_queue = manager.Queue()
        self.txt_trad_queue = manager.Queue()
        self.txt_socket_queue = manager.Queue()

        self.img_queue = manager.Queue()
        self.img_tra_queue = manager.Queue()
        self.img_socket_queue = manager.Queue()

        self.vid_obj_queue = manager.Queue()
        self.rec_queue = manager.Queue()
        self.static_socket_queue = manager.Queue()

        self.skeleton_queue = manager.Queue()
        self.generation_queue = manager.Queue()
        self.stream_socket_queue = manager.Queue()

        self.init_queue_dict()

    def setup(self, **kwargs):
        self.modules = [
            MainPage(self.queue_dict),
            ProcessesControl()
        ]
        self.initialize_modules()
        self.ProcessesControl.setup(self.queue_dict)

    def run(self, callbacks: Callback = None, **kwargs):
        processes_control_process = multiprocessing.Process(target=self.ProcessesControl.run)
        processes_control_process.start()
        self.MainPage.show()

    def init_queue_dict(self):
        self.queue_dict["control_queue"] = self.control_queue

        self.queue_dict["txt_queue"] = self.txt_queue
        self.queue_dict["txt_trad_queue"] = self.txt_trad_queue
        self.queue_dict['txt_socket_queue'] = self.txt_socket_queue

        self.queue_dict["img_queue"] = self.img_queue
        self.queue_dict["img_tra_queue"] = self.img_tra_queue
        self.queue_dict["img_socket_queue"] = self.img_socket_queue

        self.queue_dict["vid_obj_queue"] = self.vid_obj_queue
        self.queue_dict["rec_queue"] = self.rec_queue
        self.queue_dict["static_socket_queue"] = self.static_socket_queue

        self.queue_dict["skeleton_queue"] = self.skeleton_queue
        self.queue_dict["generation_queue"] = self.generation_queue
        self.queue_dict["stream_socket_queue"] = self.stream_socket_queue


if __name__ == "__main__":
    import torch

    torch.multiprocessing.set_start_method('spawn')
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.setup()
    main.run()
    sys.exit(app.exec_())
