import os
import time

from PIL import Image

from callback.callback import Callback
from pipeline_abc import Pipeline


class StaticVidProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.path = None
        self.video_queue = None

    def setup(self, video_queue, **kwargs):
        self.path = r'C:\Users\16070\Desktop'
        self.video_queue = video_queue

    def run(self, callbacks: Callback = None, **kwargs):
        while True:
            video_name = self.video_queue.get()
            print('put success.')
            time.sleep(2)
