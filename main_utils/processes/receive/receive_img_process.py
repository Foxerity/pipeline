import time

from callback.callback import Callback
from pipeline_abc import Pipeline

from main_utils.processes.receive.receive_img_utils.tools import super_resolution, reconstruct_image


class ImgProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.img_socket_queue = None
        self.img_queue = None

    def setup(self, img_queue, img_socket_queue, **kwargs):
        self.img_socket_queue = img_socket_queue
        self.img_queue = img_queue

    def run(self, callbacks: Callback = None, **kwargs):
        while True:
            received_chunks = []
            total_size = 0
            count = 0
            while True:
                chunk = self.img_socket_queue.get()
                count += 1
                received_chunks.append(chunk)
                total_size += len(chunk)
                print(f"ImgProcess: {len(received_chunks)}")
                if len(received_chunks) == 16:
                    print("ImgProcess: breaking")
                    break
                time.sleep(0.1)
            reconstructed_image = reconstruct_image(received_chunks)
            super_resolution_image = super_resolution(reconstructed_image)
            self.img_queue.put(super_resolution_image)

