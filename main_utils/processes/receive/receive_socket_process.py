import queue
import socket
import time

from pipeline_abc import Pipeline


class ReceiveSocketProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.host = None
        self.port = None
        self.socket = None
        self.conn = None
        self.addr = None
        self.queue_dict = None
        self.current_queue = None

    def setup(self, host, port, queue_dict, **kwargs):
        self.host = host
        self.port = port
        self.socket = None
        self.queue_dict = queue_dict
        self.current_queue = None

    def connect(self):
        self.conn, self.addr = None, None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        print(f'bind{self.host}:{self.port}')
        self.socket.listen(1)
        self.conn, self.addr = self.socket.accept()
        print("accept.")

    def run(self, **kwargs):
        self.connect()
        while True:
            if not self.queue_dict['control_queue'].empty():
                new_queue = self.queue_dict['control_queue'].get()
                self.current_queue = new_queue
                self.clear_queue()
                self.clean_channel()
                print(f"start putting data to {new_queue}")
            data = self.receive_message()

            if data and self.current_queue:
                self.current_queue.put(data)
            time.sleep(0.2)

    def receive_message(self):
        try:
            data = self.conn.recv(1047)
            if not data:
                return None
            return data
        except socket.error as e:
            print(f"Socket error: {e}")
            return None

    def clean_channel(self):
        self.conn.setblocking(False)
        while True:
            try:
                data = self.conn.recv(1024)
            except socket.error as e:
                break
        self.conn.setblocking(True)

    def clear_queue(self):
        try:
            while True:
                self.current_queue.get_nowait()
        except queue.Empty:
            pass
