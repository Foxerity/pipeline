import os
import time

from PIL import Image

from callback.callback import Callback
from pipeline_abc import Pipeline


class StreamVidProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.skeleton_queue = None
        self.generation_queue = None

    def setup(self, skeleton_queue, generation_queue, **kwargs):
        self.skeleton_queue = skeleton_queue
        self.generation_queue = generation_queue

    def run(self, callbacks: Callback = None, **kwargs):
        image_list = os.listdir(r'C:\Users\fengx\Desktop')
        image_files = [f for f in image_list if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        while True:
            for image in image_files:
                img = Image.open(os.path.join(r'C:\Users\fengx\Desktop', image))
                self.skeleton_queue.put(img)
                print('put success skeleton')
                img = Image.open(os.path.join(r'C:\Users\fengx\Desktop', image))
                self.generation_queue.put(img)
                print('put success generation.')
            time.sleep(2)
