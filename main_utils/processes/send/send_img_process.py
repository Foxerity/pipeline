import time

from PIL import Image

from callback.callback import Callback
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
                img = Image.open(self.img).convert('RGB')
                img_2k = resize_2k_image(img)
                img_64 = downsample_images(img_2k)
                img_64.save("img_64.jpg")
                image_chunks_list = split_image(img_64)
                print(image_chunks_list)
                for image_chunks in image_chunks_list:
                    image_chunks = image_chunks.tobytes()

                    while len(image_chunks) < 1044:
                        image_chunks += b'\x00'
                    image_chunks = b'\x24' + b'\x4d' + b'\x53' + image_chunks
                    self.img_socket_queue.put(image_chunks)
            time.sleep(0.2)

