import time

import numpy as np
from PIL import Image

from main_utils.processes.send.send_img_utils.tradition_send import JPEGCompression, array2bin
from pipeline_abc import Pipeline

from main_utils.processes.send.send_img_utils.tools import downsample_images, resize_2k_image, split_image


class ImgProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.img = None
        self.image_path = None
        self.downsample_image_path = None
        self.img_socket_queue = None
        self.img_queue = None

    def setup(self, img_queue, img_socket_queue, **kwargs):
        self.img_queue = img_queue
        self.img_socket_queue = img_socket_queue

    def run(self, **kwargs):
        while True:
            if not self.img_queue.empty():
                self.img = self.img_queue.get()
                print(f'ImgProcess: {self.img}')
                self.semantic_compress(self.img)
                self.tradition_compress(self.img)
            time.sleep(0.2)

    def semantic_compress(self, img_path):
        img = Image.open(img_path).convert('RGB')
        img_2k = resize_2k_image(img)
        img_64 = downsample_images(img_2k)
        image_chunks_list = split_image(img_64)

        # 第一包设置为100个数据包数
        send_packet_bit = np.array([len(image_chunks_list)] * 100, dtype="<u2")
        send_packet_bytes = send_packet_bit.tobytes("F")
        self.img_socket_queue.put(send_packet_bytes)

        for image_chunks in image_chunks_list:
            image_chunks = image_chunks.tobytes()
            while len(image_chunks) < 1044:
                image_chunks += b'\x00'
            image_chunks = b'\x24' + b'\x4d' + b'\x53' + image_chunks
            self.img_socket_queue.put(image_chunks)
            image_chunks = ''.join(format(byte, '08b') for byte in image_chunks)
            self.write_bits_to_file(image_chunks, r"resources/send/semantic_compress.txt")

    def tradition_compress(self, img_path):
        out_dir = 'temp'
        img = JPEGCompression(img_path, out_dir)
        data = array2bin(img)

        # 第一包设置为100个数据包数
        send_packet_bit = np.array([len(range(0, len(data), 1044))] * 100, dtype="<u2")
        send_packet_bytes = send_packet_bit.tobytes("F")
        self.img_socket_queue.put(send_packet_bytes)

        for i in range(0, len(data), 1044):
            chunk = data[i:i + 1044]
            chunk += b'\x00' * (1044 - len(chunk))
            chunk = b'\x24' + b'\x4d' + b'\x53' + bytes(chunk)
            assert len(chunk) == 1047
            self.img_socket_queue.put(chunk)
            chunk = ''.join(format(byte, '08b') for byte in chunk)
            self.write_bits_to_file(chunk, r"resources/send/tradition_compress.txt")

    @staticmethod
    def write_bits_to_file(bit_stream, file_path):
        with open(file_path, 'a') as file:
            file.write(bit_stream)

