import multiprocessing
import sys
from multiprocessing import Queue, Manager
from typing import Union, Any

from PyQt5 import QtWidgets

from callback.callback import Callback
from pipeline_abc import Pipeline

from main_utils.processes.receive.receive_processes_control import ProcessesControl
from pages.receive.receive_main_page import MainPage


class MainWindow(Pipeline):
    queue_dict = {
        "control_queue": Union[Queue, Any],
        "socket_value": Union[Queue, Any],

        "txt_queue": Union[Queue, Any],
        "txt_trad_queue": Union[Queue, Any],
        "txt_socket_queue": Union[Queue, Any],
        "txt_value_queue": Union[Queue, Any],

        "img_queue": Union[Queue, Any],
        "img_tra_queue": Union[Queue, Any],
        "img_socket_queue": Union[Queue, Any],
        "img_value_queue": Union[Queue, Any],

        "vid_obj_queue": Union[Queue, Any],
        "rec_queue": Union[Queue, Any],
        "static_socket_queue": Union[Queue, Any],
        "static_value_queue": Union[Queue, Any],

        "skeleton_queue": Union[Queue, Any],
        "generation_queue": Union[Queue, Any],
        "stream_socket_queue": Union[Queue, Any],
        "stream_value_queue": Union[Queue, Any],

    }

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ProcessesControl = None
        self.MainPage = None

        manager = Manager()
        self.control_queue = manager.Queue()
        self.socket_value = manager.Queue()

        self.txt_queue = manager.Queue()
        self.txt_trad_queue = manager.Queue()
        self.txt_socket_queue = manager.Queue()
        self.txt_value_queue = manager.Queue()

        self.img_queue = manager.Queue()
        self.img_tra_queue = manager.Queue()
        self.img_socket_queue = manager.Queue()
        self.img_value_queue = manager.Queue()

        self.vid_obj_queue = manager.Queue()
        self.rec_queue = manager.Queue()
        self.static_socket_queue = manager.Queue()
        self.static_value_queue = manager.Queue()

        self.skeleton_queue = manager.Queue()
        self.generation_queue = manager.Queue()
        self.stream_socket_queue = manager.Queue()
        self.stream_value_queue = manager.Queue()

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
        self.queue_dict["socket_value"] = self.socket_value

        self.queue_dict["txt_queue"] = self.txt_queue
        self.queue_dict["txt_trad_queue"] = self.txt_trad_queue
        self.queue_dict['txt_socket_queue'] = self.txt_socket_queue
        self.queue_dict['txt_value_queue'] = self.txt_value_queue

        self.queue_dict["img_queue"] = self.img_queue
        self.queue_dict["img_tra_queue"] = self.img_tra_queue
        self.queue_dict["img_socket_queue"] = self.img_socket_queue
        self.queue_dict["img_value_queue"] = self.img_value_queue

        self.queue_dict["vid_obj_queue"] = self.vid_obj_queue
        self.queue_dict["rec_queue"] = self.rec_queue
        self.queue_dict["static_socket_queue"] = self.static_socket_queue
        self.queue_dict["static_value_queue"] = self.static_value_queue

        self.queue_dict["skeleton_queue"] = self.skeleton_queue
        self.queue_dict["generation_queue"] = self.generation_queue
        self.queue_dict["stream_socket_queue"] = self.stream_socket_queue
        self.queue_dict["stream_value_queue"] = self.stream_value_queue


if __name__ == "__main__":
    import torch

    torch.multiprocessing.set_start_method('spawn')
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.setup()
    main.run()
    sys.exit(app.exec_())
