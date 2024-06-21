import queue
import socket
import time

from pipeline_abc import Pipeline


class SendSocketProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.host = None
        self.port = None
        self.socket = None
        self.queue_dict = None
        self.current_queue = None
        self.count = None

    def setup(self, host, port, queue_dict, **kwargs):
        self.host = host
        self.port = port
        self.socket = None
        self.queue_dict = queue_dict
        self.current_queue = None

    def connect(self):
        self.count = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.connect((self.host, self.port))

    def run(self, **kwargs):
        self.connect()
        while True:
            if not self.queue_dict['control_queue'].empty():
                new_queue = self.queue_dict['control_queue'].get()
                print("socket: getting new queue.")
                self.current_queue = new_queue
                self.clear_queue()
                self.count = 0
            if self.current_queue and not self.current_queue.empty():
                msg = self.current_queue.get_nowait()
                self.send_message(msg)
                self.count += 1
                print(f"socket: sending message {len(msg)} {self.count}")
            time.sleep(0.2)

    def send_message(self, message):
        self.socket.sendall(message)

    def clear_queue(self):
        try:
            while True:
                self.current_queue.get_nowait()
        except queue.Empty:
            pass
