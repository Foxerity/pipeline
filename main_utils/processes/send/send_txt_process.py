import time

from pipeline_abc import Pipeline
from main_utils.processes.send.send_text_utils.txt_send import Sender


class TxtProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.sender = Sender()
        self.txt_queue = None
        self.txt_send_queue = None

    def setup(self, txt_queue, txt_send_queue, **kwargs):
        self.txt_queue = txt_queue
        self.txt_send_queue = txt_send_queue

        self.modules = [
            Sender()
        ]

    def run(self, **kwargs):
        while True:
            if not self.txt_queue.empty():
                self.modules[0].run(self.txt_queue, self.txt_send_queue)
            time.sleep(1)

