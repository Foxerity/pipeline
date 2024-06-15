import multiprocessing
import os
import time

from PIL import Image

from pipeline_abc import Pipeline
from main_utils.processes.send.send_txt_process import TxtProcess
from main_utils.processes.send.send_img_process import ImgProcess
from main_utils.processes.send.send_static_vid_process import StaticVidProcess
from main_utils.processes.send.send_stream_vid_process import StreamVidProcess


class ProcessesControl(Pipeline):
    def __init__(self, camera_queue):
        super().__init__()
        self.camera_queue = camera_queue

    def setup(self, **kwargs):
        self.config = {
            'name': "Object Detection"
        }
        self.modules = [
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]

        self.modules[3].setup(self.camera_queue)

    def run(self, **kwargs):
        # txt_process = multiprocessing.process(self.modules[0].run(), args=(kwargs,))
        # txt_process.start()

        # img_process = multiprocessing.process(self.modules[1].run(), args=(kwargs,))
        # img_process.start()

        # static_vid_process = multiprocessing.process(self.modules[2].run(), args=(kwargs,))
        # static_vid_process.start()

        stream_vid_process = multiprocessing.Process(self.modules[3].run())
        stream_vid_process.start()


