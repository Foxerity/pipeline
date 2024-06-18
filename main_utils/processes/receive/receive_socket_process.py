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
        self.socket.listen(1)

        self.conn, self.addr = self.socket.accept()
        print(f'bind{self.host}:{self.port}')

    def run(self, **kwargs):
        self.connect()
        data_length = None
        while True:
            if not self.queue_dict['control_queue'].empty():
                data_length, new_queue = self.queue_dict['control_queue'].get()
                self.current_queue = new_queue
                self.clear_queue()
                self.clean_channel(data_length)

            data = self.receive_message(data_length)
            print(f"start getting {len(data)} data from {new_queue}")

            if data and self.current_queue:
                self.current_queue.put(data)
            time.sleep(0.2)

    def receive_message(self, data_length):
        try:
            data = self.conn.recv(data_length)
            if not data:
                return None
            return data
        except socket.error as e:
            print(f"receive_message: Socket error: {e}")
            return None

    def clean_channel(self, data_length):
        self.conn.setblocking(False)
        while True:
            try:
                self.conn.recv(data_length)
            except socket.error as e:
                print(f"clean_channel: Socket error: {e}")
                break
        self.conn.setblocking(True)

    def clear_queue(self):
        try:
            while True:
                self.current_queue.get_nowait()
        except queue.Empty:
            pass
