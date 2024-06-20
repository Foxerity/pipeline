import multiprocessing
import queue
import random
import socket
import time

from pipeline_abc import Pipeline
from main_utils.processes.receive.receive_socket_utils.receive_chanel_effect import ReceiveChannelEffect
from main_utils.processes.receive.receive_socket_utils.receive_logger import ByteStreamSaver


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

        self.lock = None
        self.cache_list = None

        self.byte_saver = None

        self.raw_count = None
        self.noise_count = None

        self.effect_bytes = None
        self.put_data_queue = None
        self.get_data_queue = None

    def setup(self, host, port, queue_dict, **kwargs):
        self.host = host
        self.port = port
        self.socket = None

        self.queue_dict = queue_dict
        self.current_queue = None

        self.byte_saver = ByteStreamSaver()
        self.effect_bytes = ReceiveChannelEffect()
        self.put_data_queue = multiprocessing.Queue()
        self.get_data_queue = multiprocessing.Queue()

        self.cache_list = []

    def connect(self):
        self.conn, self.addr = None, None
        self.effect_bytes.setup()
        effect_socket = multiprocessing.Process(target=self.effect_bytes.fun, args=(self.put_data_queue,
                                                                                    self.get_data_queue))
        effect_socket.start()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((self.host, self.port))
        self.socket.listen(1)

        self.conn, self.addr = self.socket.accept()
        self.conn.setblocking(False)
        print(f'bind{self.host}:{self.port}')
        self.raw_count = 0
        self.noise_count = 0

    def run(self, **kwargs):
        self.connect()
        data_length = None
        self.clean_channel(1047)
        while True:

            if data_length is not None:
                data = self.receive_message(data_length)
            else:
                data = None

            if not self.queue_dict['control_queue'].empty():
                print("ReceiveSocketProcess: queue changed.")
                data_length, new_queue = self.queue_dict['control_queue'].get()
                self.current_queue = new_queue
                self.clear_queue()
                self.clean_channel(data_length)

            if data is not None and self.current_queue:
                print("ReceiveSocketProcess: effect data.")
                self.put_data_queue.put(data)
                self.raw_count += 1
                self.byte_saver.save_byte_stream(data, f"raw_{self.raw_count}.txt")

            if not self.get_data_queue.empty():
                data = self.get_data_queue.get()
                self.noise_count += 1
                self.byte_saver.save_byte_stream(data, f"noise_{self.noise_count}.txt")
                self.current_queue.put(data)
                print(f"ReceiveSocketProcess: put noise data {self.noise_count} to ui")
            time.sleep(0.1)

    def receive_message(self, data_length):
        try:
            data = self.conn.recv(data_length)
            print('ReceiveSocketProcess: get data')
            if not data:
                return None
            return data
        except socket.error as e:
            return None

    def clean_channel(self, data_length):
        self.conn.setblocking(False)
        while True:
            try:
                self.conn.recv(data_length)
            except socket.error as e:
                print(f"clean_channel: Socket error: {e}")
                break
        # self.conn.setblocking(True)

    def clear_queue(self):
        try:
            while True:
                self.current_queue.get_nowait()
        except queue.Empty:
            pass
