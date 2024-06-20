import sys
from multiprocessing import Queue, Manager
from typing import Any, Union

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

    def __init__(self, queue_dict):
        super(MainPage, self).__init__(flags=Qt.WindowFlags())
        self.queue_dict = queue_dict
        # 创建主窗口的 QTabWidget
        self.tab_widget = QtWidgets.QTabWidget()
        self.init_main_UI()
        # 加载并添加四个标签页, 分别对应文本、图像、静态视频、流式视频Tab
        self.tab_widget.addTab(TextTabWidget(self.pages_path[0], queue_dict['txt_queue']), "指令")
        self.tab_widget.addTab(ImageTabWidget(self.pages_path[1], queue_dict['img_queue']), "图像")
        self.tab_widget.addTab(StaticVidTab(self.pages_path[2], queue_dict['static_vid_queue']), "静态视频")
        self.tab_widget.addTab(StreamVidTab(self.pages_path[3], queue_dict['stream_vid_queue']), "流式视频")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.on_tab_changed(0)

    def init_main_UI(self):
        # 设置窗口位置和大小（x, y, width, height）
        self.setGeometry(800, 800, 1600, 1000)
        self.setWindowTitle('水下通信演示系统——发送端')

        self.setCentralWidget(self.tab_widget)
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

    def run(self):
        self.show()

    def on_tab_changed(self, index):
        print(f"Current tab index: {index}")
        current_widget = self.tab_widget.currentWidget()
        print(f"Current tab widget: {current_widget}")

        # 执行不同的操作，根据当前选中的标签页
        if index == 0:
            print("Text Tab is selected")
            queue_tuple = self.queue_dict['txt_socket_queue']
            self.queue_dict['control_queue'].put(queue_tuple)
            print("putting txt_socket_queue")
        elif index == 1:
            queue_tuple = self.queue_dict['img_socket_queue']
            self.queue_dict['control_queue'].put(queue_tuple)
            print("Image Tab is selected")
        elif index == 2:
            print("Static Video Tab is selected")
            queue_tuple = self.queue_dict['static_socket_queue']
            self.queue_dict['control_queue'].put(queue_tuple)
        elif index == 3:
            print("Stream Video Tab is selected")


class MainWindow(Pipeline):
    queue_dict = {
        "control_queue": Union[Queue, Any],

        "txt_queue": Union[Queue, Any],
        "txt_socket_queue": Union[Queue, Any],

        "img_queue": Union[Queue, Any],
        "img_socket_queue": Union[Queue, Any],

        "static_vid_queue": Union[Queue, Any],
        "static_socket_queue": Union[Queue, Any],

        "stream_vid_queue": Union[Queue, Any],
        "stream_socket_queue": Union[Queue, Any],
    }

    def __init__(self):
        super(MainWindow, self).__init__()
        manager = Manager()
        self.control_queue = manager.Queue()                # 控制socket传输哪个队列的数据

        self.txt_queue = manager.Queue()                    # 文本：UI与进程通信，选择的文本
        self.txt_socket_queue = manager.Queue()             # 文本：进程与socket通信，传输具体的文本

        self.img_queue = manager.Queue()                    # 图像：UI与进程通信，选择的图片
        self.img_socket_queue = manager.Queue()             # 图像：进程与socket通信，传输具体的图片patch

        self.video_queue = manager.Queue()                  # 静态视频：UI与进程通信，选择的视频
        self.static_socket_queue = manager.Queue()          # 静态视频：进程与socket通信，传输具体的视频帧

        self.camera_queue = manager.Queue()                 # 动态视频：UI与进程通信，摄像头传来的图片
        self.stream_socket_queue = manager.Queue()          # 动态视频：进程与socket通信，传输具体的图片

        self.init_queue_dict()                              # 将全部队列管理为字典

        self.main_page = MainPage(self.queue_dict)

        self.process_control = ProcessesControl()

    def setup(self, **kwargs):
        self.modules = [
            self.main_page,
            self.process_control,
        ]

        self.process_control.setup(self.queue_dict)

    def run(self, callbacks: Callback = None, **kwargs):
        for module in self.modules:
            module.run()

    def init_queue_dict(self):
        self.queue_dict['control_queue'] = self.control_queue

        self.queue_dict['txt_queue'] = self.txt_queue
        self.queue_dict['txt_socket_queue'] = self.txt_socket_queue

        self.queue_dict['img_queue'] = self.img_queue
        self.queue_dict['img_socket_queue'] = self.img_socket_queue

        self.queue_dict['static_vid_queue'] = self.video_queue
        self.queue_dict['static_socket_queue'] = self.static_socket_queue

        self.queue_dict['stream_vid_queue'] = self.camera_queue
        self.queue_dict['stream_socket_queue'] = self.stream_socket_queue


if __name__ == "__main__":
    import torch
    torch.multiprocessing.set_start_method('spawn')
    app = QApplication(sys.argv)
    main = MainWindow()
    main.setup()
    main.run()
    sys.exit(app.exec_())
