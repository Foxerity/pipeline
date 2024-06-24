import sys
from multiprocessing import Queue, Manager
from typing import Any, Union
from PyQt5.QtWidgets import QApplication

from pipeline_abc import Pipeline

from main_utils.processes.send.send_processes_control import ProcessesControl
from pages.send.send_main_page import MainPage
from callback.send.send_main_callback import SendMainCallback


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
        self.SendMainCallback = None
        self.ProcessesControl = None

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

        self.process_control = ProcessesControl()

    def setup(self, **kwargs):
        self.modules = [
            SendMainCallback(),
            MainPage(self.queue_dict),
            ProcessesControl()
        ]
        self.initialize_modules()
        self.ProcessesControl.setup(self.queue_dict)
        self.SendMainCallback.setup(self.__class__.__name__)
        self.SendMainCallback.init_run(self.modules, self.queue_dict)

    def run(self,  **kwargs):
        for module in self.modules:
            self.SendMainCallback.before_run(module)
            module.run()
            self.SendMainCallback.after_run(module)

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
    main.save_configfile("send_main.yaml")
    main.run()
    sys.exit(app.exec_())
