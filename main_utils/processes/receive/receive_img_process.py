import time

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

    def setup(self, img_queue, img_tra_queue, img_socket_queue, **kwargs):
        self.img_socket_queue = img_socket_queue
        self.img_queue = img_queue
        self.img_tra_queue = img_tra_queue

    def run(self, callbacks: Callback = None, **kwargs):
        while True:
            received_chunks = []
            received_tra_chunks = []
            total_size = 0
            count = 0
            while True:
                chunk = self.img_socket_queue.get()
                count += 1
                received_chunks.append(chunk)
                total_size += len(chunk)
                print(f"ImgProcess: {len(received_chunks)}")
                if len(received_chunks) == 16:
                    print("ImgProcess: finished 16 chunks")
                    break
                time.sleep(0.1)
            reconstructed_image = reconstruct_image(received_chunks)
            super_resolution_image = super_resolution(reconstructed_image)
            self.img_queue.put(super_resolution_image)
            count = 0
            while True:
                chunk = self.img_socket_queue.get()
                count += 1
                received_tra_chunks.append(chunk[3:])
                total_size += len(chunk)
                print(f"ImgProcess: {len(received_tra_chunks)}")
                if len(received_tra_chunks) == 179:
                    print("ImgProcess: finished 179 chunks")
                    break
                time.sleep(0.1)
            flattened_list = [item for sublist in received_tra_chunks for item in sublist]
            data = bin2array(flattened_list[0: 185856], (88, 88, 3))
            restore = cv2.resize(data.astype("float"), (2048, 2048))
            restore = np.clip(restore, 0, 255)
            restore_uint8 = restore.astype('uint8')
            restore_rgb = cv2.cvtColor(restore_uint8, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(restore_rgb.astype('uint8'))
            self.img_tra_queue.put(pil_image)

