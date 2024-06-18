import socket
import time

from pipeline_abc import Pipeline


class ReceiveSocketProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.host = None
        self.port = None
        self.socket = None
        self.queue_dict = None
        self.current_queue = None

    def setup(self, host, port, queue_dict, **kwargs):
        self.host = host
        self.port = port
        self.socket = None
        self.queue_dict = queue_dict
        self.current_queue = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def run(self, **kwargs):
        self.connect()
        while True:
            if not self.queue_dict['control_queue'].empty():
                new_queue = self.queue_dict['control_queue'].get()
                self.current_queue = new_queue
            if self.current_queue and not self.current_queue.empty():
                msg = self.current_queue.get_nowait()
                self.send_message(msg)
            time.sleep(0.5)

    def send_message(self, message, func):
        self.socket.sendall(message.encode('utf-8'))
