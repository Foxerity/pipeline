import time
from collections import Counter

import cv2
import numpy as np
from PIL import Image
from callback.callback import Callback
from main_utils.processes.receive.receive_img_utils.tradition_recevie import bin2array
from pipeline_abc import Pipeline

from main_utils.processes.receive.receive_img_utils.tools import super_resolution, reconstruct_image


class ImgProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.img_socket_queue = None
        self.img_queue = None
        self.img_tra_queue = None
        self.img_value_queue = None
        self.value_dict = {
            "send_packet_count": 0,
            "recevie_packet_count": 0,  # 接受端受到的包数
            "most_common_number": 0,  # 发送端发送的包数
            "loss_packet": 0.,  # 接收端丢包率
            "bit_ratio": 0.,  # 比特率
            "ber_ratio": 0.,  # 误码率
            "mean_ber_ratio": 0.  # 平均误码率
        }

    def setup(self, img_queue, img_tra_queue, img_socket_queue, img_value_queue, **kwargs):
        self.img_socket_queue = img_socket_queue
        self.img_queue = img_queue
        self.img_tra_queue = img_tra_queue
        self.img_value_queue = img_value_queue

    def run(self, callbacks: Callback = None, **kwargs):
        flag = 0
        while True:
            received_chunks = []
            received_tra_chunks = []
            total_size = 0

            bit_start = 0
            bit_end = 0
            ber_list = []
            send_bit = self.send_bits("semantic_compress.txt")
            while True:
                if not self.img_socket_queue.empty():
                    chunk = self.img_socket_queue.get()

                    bits_stream = ''.join(format(byte, '08b') for byte in chunk)
                    # 误码率
                    bit_end += len(bits_stream)
                    count = self.count_matching_bits(send_bit[bit_start:bit_end], bits_stream)
                    ber = (len(bits_stream) - count) / len(bits_stream)

                    bit_start = bit_end
                    if bit_start == bit_end:
                        bit_start = 0
                        bit_end = 0
                    self.value_dict["ber_ratio"] = float(ber)
                    ber_list.append(ber)
                    self.value_dict["mean_ber_ratio"] = sum(ber_list) / len(ber_list)

                    # 丢包率
                    if flag == 0:
                        chunk = np.frombuffer(chunk, dtype='<u2')
                        print(chunk.shape)
                        counter = Counter(chunk)
                        self.value_dict["send_packet_count"], _ = counter.most_common(1)[0]
                        flag = 1
                        continue
                    self.value_dict["recevie_packet_count"] += 1

                    received_chunks.append(chunk)
                    total_size += len(chunk)
                    print(f"ImgProcess: {len(received_chunks)}")
                    if len(received_chunks) == 16:
                        print("ImgProcess: finished 16 chunks")
                        break
                    self.img_value_queue.put(self.value_dict)
                    print(self.value_dict["bit_ratio"])
                    time.sleep(0.1)
            reconstructed_image = reconstruct_image(received_chunks)
            super_resolution_image = super_resolution(reconstructed_image)
            self.img_queue.put(super_resolution_image)
            self.value_dict["loss_packet"] = (self.value_dict["send_packet_count"] - self.value_dict[
                "recevie_packet_count"]) / self.value_dict["send_packet_count"]
            self.value_dict["recevie_packet_count"] = 0
            flag = 0
            bit_start = 0
            bit_end = 0
            ber_list = []
            send_bit = self.send_bits("tradition_compress.txt")
            while True:
                if not self.img_socket_queue.empty():
                    chunk = self.img_socket_queue.get()

                    bits_stream = ''.join(format(byte, '08b') for byte in chunk)

                    # 误码率
                    bit_end += len(bits_stream)
                    count = self.count_matching_bits(send_bit[bit_start:bit_end], bits_stream)
                    ber = (len(bits_stream) - count) / len(bits_stream)

                    bit_start = bit_end
                    if bit_start == bit_end:
                        bit_start = 0
                        bit_end = 0
                    self.value_dict["ber_ratio"] = float(ber)
                    ber_list.append(ber)
                    self.value_dict["mean_ber_ratio"] = sum(ber_list) / len(ber_list)

                    # 丢包率
                    if flag == 0:
                        chunk = np.frombuffer(chunk, dtype='<u2')
                        counter = Counter(chunk)
                        self.value_dict["send_packet_count"], _ = counter.most_common(1)[0]
                        flag = 1
                        continue
                    # 语义和传统总接受包数
                    self.value_dict["recevie_packet_count"] += 1

                    received_tra_chunks.append(chunk[3:])
                    total_size += len(chunk)
                    print(f"ImgProcess: {len(received_tra_chunks)}")
                    if len(received_tra_chunks) == 179:
                        print("ImgProcess: finished 179 chunks")
                        break
                    self.img_value_queue.put(self.value_dict)
                    time.sleep(0.1)
            flattened_list = [item for sublist in received_tra_chunks for item in sublist]
            data = bin2array(flattened_list[0: 185856], (88, 88, 3))
            restore = cv2.resize(data.astype("float"), (2048, 2048))
            restore = np.clip(restore, 0, 255)
            restore_uint8 = restore.astype('uint8')
            restore_rgb = cv2.cvtColor(restore_uint8, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(restore_rgb.astype('uint8'))
            self.img_tra_queue.put(pil_image)
            self.value_dict["loss_packet"] = ((self.value_dict["send_packet_count"] -
                                               self.value_dict["recevie_packet_count"]) /
                                              self.value_dict["send_packet_count"])

    @staticmethod
    def send_bits(path):
        with open("resources/send/" + path, 'r') as file:
            send_bit_stream = file.read()
        return send_bit_stream

    @staticmethod
    def count_matching_bits(str1, str2):
        # 确保两个字符串的长度相同
        if len(str1) != len(str2):
            print(ValueError("len of bits stream different"))
            return 0
        # 计算相同字符的个数
        matching_count = sum(1 for a, b in zip(str1, str2) if a == b)
        return matching_count
