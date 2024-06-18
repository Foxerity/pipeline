import multiprocessing

from pipeline_abc import Pipeline
from main_utils.processes.send.send_txt_process import TxtProcess
from main_utils.processes.send.send_img_process import ImgProcess
from main_utils.processes.send.send_static_vid_process import StaticVidProcess
from main_utils.processes.send.send_stream_vid_process import StreamVidProcess


class ProcessesControl(Pipeline):
    def __init__(self):
        super().__init__()
        self.queue_dict = None

    def setup(self, queue_dict, **kwargs):
        self.config = {
            'name': "Object Detection"
        }
        self.queue_dict = queue_dict

        self.modules = [
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]

        self.modules[0].setup(self.queue_dict['txt_proc'])
        # self.modules[2].setup(self.queue_dict['static_vid_pro'])
        # self.modules[3].setup(self.queue_dict['stream_vid_pro'])

    def run(self, **kwargs):
        txt_process = multiprocessing.Process(target=self.modules[0].run)
        txt_process.start()

        # img_process = multiprocessing.process(self.modules[1].run(), args=(kwargs,))
        # img_process.start()

        # static_vid_process = multiprocessing.Process(target=self.modules[2].run)
        # static_vid_process.start()

        # stream_vid_process = multiprocessing.Process(target=self.modules[3].run)
        # stream_vid_process.start()


