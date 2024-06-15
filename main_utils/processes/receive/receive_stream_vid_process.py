import os
import time

from PIL import Image

from callback.callback import Callback
from pipeline_abc import Pipeline


class StreamVidProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.camera_queue = None

    def setup(self, camera_queue, **kwargs):
        self.camera_queue = camera_queue

    def run(self, callbacks: Callback = None, **kwargs):
        image_list = os.listdir(r'C:\Users\fengx\Desktop')
        image_files = [f for f in image_list if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        while True:
            for image in image_files:
                img = Image.open(os.path.join(r'C:\Users\fengx\Desktop', image))
                self.camera_queue.put(img)
                print('put success.')
            time.sleep(2)
