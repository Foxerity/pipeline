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
        self.test_queue = None

    def setup(self, txt_queue, **kwargs):
        self.test_queue = Queue()
        self.txt_queue = txt_queue
        self.modules = [
            Receiver()
        ]

    def run(self, callbacks: Callback = None, **kwargs):
        self.test_block(self.test_queue)
        while True:
            if not self.test_queue.empty():
                self.modules[0].run(self.test_queue, self.txt_queue)
            time.sleep(1)

    @staticmethod
    def test_block(q1):
        test_send = Sender()
        txt_pth = r"D:\project\pipeline\main_utils\processes\send\send_text_utils\data\input\1.txt"
        q1.put(txt_pth)
        test_send.run(q1)

