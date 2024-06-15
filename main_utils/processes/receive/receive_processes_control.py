import multiprocessing

from pipeline_abc import Pipeline
from main_utils.processes.receive.receive_txt_process import TxtProcess
from main_utils.processes.receive.receive_img_process import ImgProcess
from main_utils.processes.receive.receive_static_vid_process import StaticVidProcess
from main_utils.processes.receive.receive_stream_vid_process import StreamVidProcess


class ProcessesControl(Pipeline):
    def __init__(self):
        super().__init__()
        self.skeleton_queue = None
        self.generation_queue = None

    def setup(self, skeleton_queue, generation_queue, **kwargs):
        self.modules = [
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]
        self.skeleton_queue = skeleton_queue
        self.generation_queue = generation_queue
        self.modules[3].setup(self.skeleton_queue, self.generation_queue)

    def run(self, **kwargs):
        # txt_process = multiprocessing.process(self.modules[0].run(), args=(kwargs,))
        # txt_process.start()

        # img_process = multiprocessing.process(self.modules[1].run(), args=(kwargs,))
        # img_process.start()

        # static_vid_process = multiprocessing.process(self.modules[2].run(), args=(kwargs,))
        # static_vid_process.start()

        stream_vid_process = multiprocessing.Process(self.modules[3].run())
        stream_vid_process.start()


