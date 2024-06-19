import time

from pipeline_abc import Pipeline
from main_utils.processes.send.send_text_utils.txt_send import Sender


class TxtProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.sender = Sender()
        self.txt_queue = None
        self.txt_socket_queue = None

    def setup(self, txt_queue, txt_socket_queue, **kwargs):
        self.txt_queue = txt_queue
        self.txt_socket_queue = txt_socket_queue

        self.modules = [
            Sender()
        ]

    def run(self, **kwargs):
        while True:
            if self.txt_queue and not self.txt_queue.empty():
                self.modules[0].run(self.txt_queue, self.txt_socket_queue)
            time.sleep(1)

