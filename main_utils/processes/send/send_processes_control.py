import multiprocessing

from pipeline_abc import Pipeline
from main_utils.processes.send.send_txt_process import TxtProcess
from main_utils.processes.send.send_img_process import ImgProcess
from main_utils.processes.send.send_static_vid_process import StaticVidProcess
from main_utils.processes.send.send_stream_vid_process import StreamVidProcess


class ProcessesControl(Pipeline):
    def __init__(self, camera_queue, video_queue):
        super().__init__()
        self.camera_queue = camera_queue
        self.video_queue = video_queue

    def setup(self, path, host, port, **kwargs):
        self.config = {
            'name': "Object Detection"
        }
        self.modules = [
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]

        self.modules[2].setup(self.video_queue, path, host, port)
        self.modules[3].setup(self.camera_queue)

    def run(self, **kwargs):
        # txt_process = multiprocessing.process(self.modules[0].run(), args=(kwargs,))
        # txt_process.start()

        # img_process = multiprocessing.process(self.modules[1].run(), args=(kwargs,))
        # img_process.start()

        static_vid_process = multiprocessing.Process(target=self.modules[2].run)
        static_vid_process.start()

        # stream_vid_process = multiprocessing.Process(target=self.modules[3].run)
        # stream_vid_process.start()






