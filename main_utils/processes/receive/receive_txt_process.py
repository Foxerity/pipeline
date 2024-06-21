import multiprocessing
import time
from multiprocessing import Queue

from callback.callback import Callback
from pipeline_abc import Pipeline
from main_utils.processes.send.send_text_utils.txt_receive import Receiver
from main_utils.processes.send.send_text_utils.txt_send import Sender


class TxtProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.receiver = Receiver()
        self.txt_queue = None
        self.txt_socket_queue = None
        self.txt_tral_queue = None

    def setup(self, txt_socket_queue, txt_queue, txt_tral_queue, txt_value_queue, **kwargs):
        self.txt_socket_queue = txt_socket_queue
        self.txt_queue = txt_queue
        self.txt_tral_queue = txt_tral_queue
        self.txt_value_queue = txt_value_queue
        self.modules = [
            Receiver()
        ]

    def run(self, callbacks: Callback = None, **kwargs):
        while True:
            if not self.txt_socket_queue.empty():
                self.modules[0].run(self.txt_socket_queue, self.txt_queue, self.txt_tral_queue, self.txt_value_queue)
            time.sleep(1)

